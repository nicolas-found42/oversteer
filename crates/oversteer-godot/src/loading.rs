//! Native ResourceLoader progress; scene instantiation stays on the main thread.
use crate::diagnostics;
use godot::classes::resource_loader::ThreadLoadStatus;
use godot::classes::{Resource, ResourceLoader};
use godot::prelude::*;
use serde_json::json;
pub struct SceneLoad {
    pub paths: Vec<String>,
    done: Vec<bool>,
    resources: Vec<Gd<Resource>>,
    pub samples: Vec<serde_json::Value>,
    start: std::time::Instant,
    operation: u64,
    terminal: bool,
    last_progress: std::time::Instant,
    samples_dropped: u64,
}
impl SceneLoad {
    pub fn new(paths: Vec<String>) -> Result<Self, String> {
        let paths: Vec<_> = paths
            .into_iter()
            .filter(|p| !p.is_empty())
            .collect::<std::collections::BTreeSet<_>>()
            .into_iter()
            .collect();
        let operation = diagnostics::event("loading.start", json!({"resource_count":paths.len()}));
        let mut loader = ResourceLoader::singleton();
        let mut done = vec![];
        let mut resources = vec![];
        for path in &paths {
            if loader.has_cached(path)
                && let Some(resource) = loader.load(path)
            {
                resources.push(resource);
                done.push(true);
                continue;
            }
            let error = loader.load_threaded_request(path);
            if error != godot::global::Error::OK {
                diagnostics::event(
                    "loading.end",
                    json!({"operation":operation,"outcome":"error","category":"request_rejected","resource_count":paths.len()}),
                );
                return Err(format!("Cannot load {path}: {error:?}"));
            }
            done.push(false);
        }
        Ok(Self {
            paths,
            done,
            resources,
            samples: vec![],
            start: std::time::Instant::now(),
            operation,
            terminal: false,
            last_progress: std::time::Instant::now(),
            samples_dropped: 0,
        })
    }
    pub fn poll(&mut self) -> Result<(f64, bool), String> {
        let result = self.poll_inner();
        if matches!(result, Ok((_, true)) | Err(_)) {
            self.terminal = true;
            diagnostics::event(
                "loading.end",
                json!({"operation":self.operation,"outcome":if result.is_ok(){"ok"}else{"error"},"category":if result.is_ok(){"none"}else{"resource_unavailable"},"duration_ms":self.start.elapsed().as_millis(),"samples_dropped":self.samples_dropped}),
            );
        } else if self.last_progress.elapsed().as_secs() >= 1 {
            self.last_progress = std::time::Instant::now();
            diagnostics::event(
                "loading.progress",
                json!({"operation":self.operation,"progress":result.as_ref().ok().map(|r|r.0),"duration_ms":self.start.elapsed().as_millis()}),
            );
        }
        result
    }
    fn poll_inner(&mut self) -> Result<(f64, bool), String> {
        let mut loader = ResourceLoader::singleton();
        let mut total = 0.;
        for (i, path) in self.paths.iter().enumerate() {
            if self.done[i] {
                total += 1.;
                continue;
            }
            let progress = VarArray::new();
            let status = loader
                .load_threaded_get_status_ex(path)
                .progress(&progress)
                .done();
            if status == ThreadLoadStatus::LOADED {
                let resource = loader
                    .load_threaded_get(path)
                    .ok_or_else(|| format!("Loaded resource unavailable: {path}"))?;
                self.resources.push(resource);
                self.done[i] = true;
                total += 1.;
            } else if status == ThreadLoadStatus::FAILED
                || status == ThreadLoadStatus::INVALID_RESOURCE
            {
                let _ = loader.load_threaded_get(path);
                return Err(format!("Resource failed to load: {path}"));
            } else {
                total += progress
                    .get(0)
                    .and_then(|v| v.try_to::<f64>().ok())
                    .unwrap_or(0.)
                    .clamp(0., 1.);
            }
        }
        let progress = if self.paths.is_empty() {
            1.
        } else {
            total / self.paths.len() as f64
        };
        self.samples_dropped += u64::from(record_progress(
            &mut self.samples,
            progress,
            self.start.elapsed().as_secs_f64(),
        ));
        Ok((progress, self.done.iter().all(|d| *d)))
    }
    pub fn finish(mut self) -> (Vec<Gd<Resource>>, serde_json::Value) {
        let summary = json!({"paths":self.paths,"seconds":self.start.elapsed().as_secs_f64(),"samples":self.samples,"samples_dropped":self.samples_dropped});
        (std::mem::take(&mut self.resources), summary)
    }
}

fn record_progress(samples: &mut Vec<serde_json::Value>, progress: f64, seconds: f64) -> bool {
    if let Some(last) = samples.last_mut()
        && last["progress"].as_f64() == Some(progress)
    {
        last["poll_count"] = (last["poll_count"].as_u64().unwrap_or(1) + 1).into();
        last["stall_duration_s"] = (seconds - last["seconds"].as_f64().unwrap_or(seconds)).into();
        last["last_seconds"] = seconds.into();
        false
    } else {
        let dropped = samples.len() == 128;
        if dropped {
            samples.remove(0);
        }
        samples.push(
            json!({"seconds":seconds,"last_seconds":seconds,"progress":progress,
            "poll_count":1,"stall_duration_s":0.0}),
        );
        dropped
    }
}

impl Drop for SceneLoad {
    fn drop(&mut self) {
        if !self.terminal {
            diagnostics::event(
                "loading.end",
                json!({"operation":self.operation,"outcome":"cancelled","duration_ms":self.start.elapsed().as_millis()}),
            );
        }
    }
}

#[cfg(test)]
mod tests {
    use super::record_progress;

    #[test]
    fn changing_progress_is_bounded_and_reports_loss() {
        let mut samples = vec![];
        let mut dropped = 0;
        for poll in 0..1000 {
            dropped += u64::from(record_progress(
                &mut samples,
                poll as f64 / 1000.,
                poll as f64,
            ));
        }
        assert_eq!(samples.len(), 128);
        assert_eq!(dropped, 872);
        assert_eq!(samples.last().unwrap()["progress"], 0.999);
    }
    #[test]
    fn repeated_loading_polls_keep_stall_evidence_without_duplicate_samples() {
        let mut samples = vec![];
        record_progress(&mut samples, 0.9375, 0.210);
        for poll in 1..=130 {
            record_progress(&mut samples, 0.9375, 0.210 + poll as f64 * 0.02);
        }
        record_progress(&mut samples, 1.0, 3.883);
        assert_eq!(samples.len(), 2);
        assert_eq!(samples[0]["poll_count"], 131);
        assert!((samples[0]["stall_duration_s"].as_f64().unwrap() - 2.6).abs() < 1e-9);
        assert_eq!(samples[1]["progress"], 1.0);
    }
}

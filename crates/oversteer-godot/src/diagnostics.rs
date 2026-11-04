//! Bounded, best-effort local evidence. Never serialize player text or error messages.
use serde_json::{Value, json};
use std::{
    cell::{Cell, RefCell},
    fs::{self, OpenOptions},
    io::Write,
    os::unix::fs::{DirBuilderExt, OpenOptionsExt},
    path::{Path, PathBuf},
    time::{Instant, SystemTime, UNIX_EPOCH},
};

const FILE_BYTES: u64 = 4 * 1024 * 1024;
const EVENT_BYTES: usize = 2048;
const EVENTS_PER_SECOND: u32 = 64;
thread_local! { static CURRENT: Cell<u64> = const { Cell::new(0) }; static JOURNAL: RefCell<Option<Journal>> = const { RefCell::new(None) }; }

pub struct Journal {
    directory: PathBuf,
    session: String,
    sequence: u64,
    dropped: u64,
    warned: bool,
    started: Instant,
    window: Instant,
    count: u32,
    source: String,
    parent: String,
}

fn stamp() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis()
}
pub fn token(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 96
        && value
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"_.:-".contains(&c))
}

impl Journal {
    pub fn new(directory: PathBuf) -> Self {
        let now = Instant::now();
        Self {
            directory,
            session: format!(
                "{:x}-{}-{:x}",
                stamp(),
                std::process::id(),
                SystemTime::now()
                    .duration_since(UNIX_EPOCH)
                    .unwrap_or_default()
                    .subsec_nanos()
            ),
            sequence: 0,
            dropped: 0,
            warned: false,
            started: now,
            window: now,
            count: 0,
            source: env!("OVERSTEER_SOURCE_ID").into(),
            parent: std::env::var("OVERSTEER_PARENT_OPERATION")
                .ok()
                .filter(|v| token(v))
                .unwrap_or_default(),
        }
    }
    pub fn record(&mut self, event: &str, fields: Value) -> u64 {
        self.sequence += 1;
        let sequence = self.sequence;
        if self.window.elapsed().as_secs() >= 1 {
            self.window = Instant::now();
            self.count = 0;
        }
        self.count += 1;
        let mut row = json!({"schema":1,"timestamp_ms":stamp(),"session":self.session,
            "sequence":sequence,"elapsed_ms":self.started.elapsed().as_millis(),
            "component":"game","source_id":self.source,"commit":env!("OVERSTEER_COMMIT"),"build_profile":if cfg!(debug_assertions){"debug"}else{"release"},"event":event,
            "dropped_before":self.dropped});
        if !self.parent.is_empty() {
            row["parent_operation"] = self.parent.clone().into();
        }
        // Caller-owned constants/tokens only; no paths, profile, command payload or raw errors.
        for (key, value) in fields.as_object().into_iter().flatten() {
            let allowed = match key.as_str() {
                "progress" | "operation" | "parent" | "attempt" | "duration_ms" | "frame"
                | "cash_before" | "cash_after" | "transactions" | "resource_count"
                | "samples_dropped" | "recovered_race" | "preserved" | "quality" | "difficulty" => {
                    value.is_number() || value.is_boolean()
                }
                "outcome" | "category" | "stage" | "command" | "screen_before" | "screen_after"
                | "state_id" | "content_id" | "mode" | "target" | "source" | "asset_id"
                | "event_id" | "car_id" => value.as_str().is_some_and(token),
                _ => false,
            };
            if allowed {
                row[key] = value.clone();
            }
        }
        let mut bytes = serde_json::to_vec(&row).unwrap_or_default();
        bytes.push(b'\n');
        if !token(event)
            || bytes.len() > EVENT_BYTES
            || self.count > EVENTS_PER_SECOND
            || self.append(&bytes).is_err()
        {
            self.dropped += 1;
            if !self.warned {
                let _ = writeln!(
                    std::io::stderr(),
                    "Oversteer diagnostics incomplete: write, contention, size or rate limit"
                );
                self.warned = true;
            }
        } else {
            self.dropped = 0;
        }
        sequence
    }
    fn append(&self, bytes: &[u8]) -> std::io::Result<()> {
        fs::DirBuilder::new()
            .recursive(true)
            .mode(0o700)
            .create(&self.directory)?;
        let lock = OpenOptions::new()
            .create(true)
            .truncate(false)
            .write(true)
            .mode(0o600)
            .open(self.directory.join("journal.lock"))?;
        lock.try_lock().map_err(std::io::Error::other)?;
        let path = self.directory.join("journal.jsonl");
        if path.metadata().map(|m| m.len()).unwrap_or(0) + bytes.len() as u64 > FILE_BYTES {
            fs::rename(&path, self.directory.join("journal.previous.jsonl"))?;
        }
        OpenOptions::new()
            .create(true)
            .append(true)
            .mode(0o600)
            .open(path)?
            .write_all(bytes)
        // Kernel write, not fsync: process exit survives; power loss is not guaranteed.
    }
}

pub fn initialize(directory: &Path) {
    JOURNAL.with(|cell| *cell.borrow_mut() = Some(Journal::new(directory.to_owned())));
    event("session.start", json!({}));
}
pub fn event(name: &str, mut fields: Value) -> u64 {
    CURRENT.with(|current| {
        if current.get() != 0 {
            fields["parent"] = current.get().into();
        }
    });
    JOURNAL.with(|cell| {
        cell.borrow_mut()
            .as_mut()
            .map(|j| j.record(name, fields))
            .unwrap_or(0)
    })
}

pub fn operation<T>(
    kind: &str,
    action: impl FnOnce(u64) -> Result<T, String>,
) -> Result<T, String> {
    let operation = event("operation.start", json!({"stage":kind}));
    let started = Instant::now();
    let previous = CURRENT.with(|current| current.replace(operation));
    let result = action(operation);
    CURRENT.with(|current| current.set(previous));
    event(
        "operation.end",
        json!({"operation":operation,"stage":kind,
        "duration_ms":started.elapsed().as_millis(),"outcome":if result.is_ok(){"ok"}else{"error"}}),
    );
    result
}

pub fn rejection(error: Option<&str>) -> &'static str {
    match error {
        None => "none",
        Some(
            "Insufficient cash" | "Insufficient driver stake" | "Insufficient spectator stake",
        ) => "insufficient_cash",
        Some(
            "Keep one career vehicle" | "Pink slips require a rival and a spare owned vehicle",
        ) => "spare_vehicle_required",
        Some(
            "Driver bet already escrowed"
            | "Offer is already closed"
            | "Race has already launched"
            | "Vehicle already owned",
        ) => "already_applied",
        Some(
            "No race grid"
            | "No grid to launch"
            | "Screen requires a game transition"
            | "No race to restart",
        ) => "invalid_transition",
        Some(_) => "other_rejection",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn bounds_redaction_rotation_and_failure() {
        let dir = std::env::temp_dir().join(format!(
            "oversteer-journal-{}-{}",
            std::process::id(),
            stamp()
        ));
        let mut journal = Journal::new(dir.clone());
        journal.record(
            "test",
            json!({"profile":"SECRET","category":"Bad/Input","stage":"backup","operation":7}),
        );
        let path = dir.join("journal.jsonl");
        let text = fs::read_to_string(&path).unwrap();
        assert!(!text.contains("SECRET"));
        assert!(!text.contains("Bad/Input"));
        let row: Value = serde_json::from_str(text.trim()).unwrap();
        assert_eq!(row["operation"], 7);
        OpenOptions::new()
            .write(true)
            .open(&path)
            .unwrap()
            .set_len(FILE_BYTES)
            .unwrap();
        journal.record("rotate", json!({}));
        assert!(dir.join("journal.previous.jsonl").exists());
        for _ in 0..100 {
            journal.record("burst", json!({}));
        }
        assert!(journal.dropped > 0);
        journal.window = Instant::now() - std::time::Duration::from_secs(2);
        journal.record("recovered", json!({}));
        let text = fs::read_to_string(&path).unwrap();
        let last: Value = serde_json::from_str(text.lines().last().unwrap()).unwrap();
        assert!(last["dropped_before"].as_u64().unwrap() > 0);
        journal.directory = path;
        journal.record("unwritable", json!({}));
        assert_eq!(journal.dropped, 1);
        fs::remove_dir_all(dir).unwrap();
    }
}

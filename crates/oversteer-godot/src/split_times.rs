//! Presentation-only splits at checkpoints accepted by the simulation.
//! Times are observed intervals, not distance/speed estimates or exact crossings.
use std::collections::BTreeMap;

use oversteer_core::RaceSnapshot;

#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Split {
    /// Rival crossing time minus player crossing time at the same checkpoint.
    pub seconds: f32,
    /// Maximum timing error from observing only the enclosing frame intervals.
    pub uncertainty: f32,
}

impl Split {
    pub fn label(self) -> String {
        format!("~{:+.1}s", self.seconds)
    }
}

#[derive(Clone, Copy, Debug)]
struct Crossing {
    earliest: f32,
    latest: f32,
}

#[derive(PartialEq)]
struct RaceIdentity {
    event: String,
    track: String,
    round: u32,
    checkpoint_count: usize,
    racers: Vec<(String, String)>,
}

#[derive(Default)]
pub struct SplitTimes {
    identity: Option<RaceIdentity>,
    previous: Option<(f32, Vec<u64>)>,
    crossings: Vec<BTreeMap<u64, Crossing>>,
}

impl SplitTimes {
    /// Call when leaving/restarting a race, including a same-event restart.
    pub fn reset(&mut self) {
        *self = Self::default();
    }

    pub fn update(&mut self, race: &RaceSnapshot, checkpoint_count: usize) {
        let identity = RaceIdentity {
            event: race.event_id.clone(),
            track: race.track_id.clone(),
            round: race.round,
            checkpoint_count,
            racers: race
                .racers
                .iter()
                .map(|r| (r.car_id.clone(), r.name.clone()))
                .collect(),
        };
        if checkpoint_count < 2
            || !race.elapsed.is_finite()
            || race.elapsed < 0.
            || race.racers.iter().any(|r| r.checkpoint >= checkpoint_count)
        {
            self.reset();
            return;
        }
        let keys: Vec<_> = race
            .racers
            .iter()
            .map(|r| checkpoint_ordinal(r.lap, r.checkpoint, checkpoint_count))
            .collect();
        if self.identity.as_ref() != Some(&identity) {
            self.reset();
            self.identity = Some(identity);
        }
        self.observe(race.elapsed, keys);
    }

    fn observe(&mut self, elapsed: f32, keys: Vec<u64>) {
        if let Some((before, old)) = &self.previous
            && (elapsed < *before
                || keys.len() != old.len()
                || keys.iter().zip(old).any(|(new, old)| new < old)
                || (elapsed == *before && &keys != old))
        {
            self.previous = None;
            self.crossings.clear();
        }
        self.crossings.resize_with(keys.len(), BTreeMap::new);
        if let Some((before, old)) = &self.previous {
            for (index, (&new, &old)) in keys.iter().zip(old).enumerate() {
                if new > old {
                    // On a skipped frame only the newest accepted crossing is
                    // observed. Never manufacture timestamps for intervening gates.
                    self.crossings[index].insert(
                        new,
                        Crossing {
                            earliest: *before,
                            latest: elapsed,
                        },
                    );
                }
            }
        }
        self.previous = Some((elapsed, keys));
    }

    /// Latest checkpoint observed for both racers. This is a last split, not a
    /// continuously predicted live gap. No shared observation means no reading.
    pub fn relative_to(&self, player: usize, rival: usize) -> Option<Split> {
        if player == rival {
            return None;
        }
        let player = self.crossings.get(player)?;
        let rival = self.crossings.get(rival)?;
        let (_, (a, b)) = player
            .iter()
            .rev()
            .find_map(|(key, a)| rival.get(key).map(|b| (key, (a, b))))?;
        let low = b.earliest - a.latest;
        let high = b.latest - a.earliest;
        Some(Split {
            seconds: (low + high) * 0.5,
            uncertainty: (high - low) * 0.5,
        })
    }
}

fn checkpoint_ordinal(lap: u32, next: usize, count: usize) -> u64 {
    u64::from(lap) * count as u64 + ((next + count - 1) % count) as u64
}

#[cfg(test)]
mod tests {
    use super::*;

    fn snapshot() -> RaceSnapshot {
        let racer = |name: &str| {
            serde_json::json!({
                "wheel_omega": [0., 0., 0., 0.], "wheel_angles": [0., 0., 0., 0.],
                "wheel_steer_angles": [0., 0., 0., 0.],
                "surface_contacts": vec![oversteer_core::SurfaceContact::default(); 4],
                "is_player": name == "You", "team": 0, "role": "Rival", "lives": 1,
                "chain_score": 0., "best_lap_time": 0., "clean_lap": true,
                "car_id": name, "name": name, "position": [0., 0., 0.],
                "rotation": [0., 0., 0., 1.], "velocity": [0., 0., 0.],
                "speed_kph": 0., "rpm": 1000., "gear": 1, "steering": 0.,
                "nitrous": 0., "nitrous_active": false, "nitrous_pressure_band": 0,
                "lap": 0, "checkpoint": 1, "progress": 0., "drift_score": 0.,
                "spook": 0., "finished": false, "eliminated": false, "customization": {}
            })
        };
        serde_json::from_value(serde_json::json!({
            "native_discipline": null, "bet_offer": null, "wager": 0,
            "bet_racer": 1, "spectating": false, "spectator_bets": [],
            "spectator_odds": [], "speed_challenge": "Pending", "round": 1,
            "total_rounds": 1, "lives": 1, "target": 0., "team_scores": [],
            "tournament_points": [], "event_id": "circuit", "track_id": "london",
            "mode": "Circuit", "elapsed": 0., "countdown": 3., "position": 1,
            "laps": 2, "racers": [racer("You"), racer("Rival")],
            "standings": [0, 1], "drift_combo": 0., "message": ""
        }))
        .unwrap()
    }

    fn recorded() -> (SplitTimes, RaceSnapshot) {
        let mut race = snapshot();
        let mut splits = SplitTimes::default();
        splits.update(&race, 4);
        race.elapsed = 1.;
        race.countdown = 0.;
        race.racers.iter_mut().for_each(|r| r.checkpoint = 2);
        splits.update(&race, 4);
        assert!(splits.relative_to(0, 1).is_some());
        (splits, race)
    }

    #[test]
    fn actual_snapshot_update_resets_event_track_round_roster_and_count() {
        for change in 0..6 {
            let (mut splits, mut race) = recorded();
            let mut count = 4;
            match change {
                0 => race.event_id = "other".into(),
                1 => race.track_id = "other".into(),
                2 => race.round += 1,
                3 => race.racers[1].car_id = "other".into(),
                4 => {
                    race.racers.pop();
                }
                _ => count = 5,
            }
            splits.update(&race, count);
            assert_eq!(splits.relative_to(0, 1), None);
        }
    }

    #[test]
    fn actual_snapshot_update_tracks_lap_wrap_and_rejects_invalid_inputs() {
        let (mut splits, mut race) = recorded();
        race.elapsed = 2.;
        race.racers.iter_mut().for_each(|r| r.checkpoint = 0);
        splits.update(&race, 4);
        race.elapsed = 3.;
        race.racers.iter_mut().for_each(|r| {
            r.lap = 1;
            r.checkpoint = 1;
        });
        splits.update(&race, 4);
        assert_eq!(splits.crossings[0].get(&4).unwrap().latest, 3.);
        race.elapsed = 0.;
        splits.update(&race, 4);
        assert_eq!(splits.relative_to(0, 1), None);
        race.elapsed = f32::NAN;
        splits.update(&race, 4);
        assert!(splits.previous.is_none());
        race.elapsed = 4.;
        race.racers[0].checkpoint = 4;
        splits.update(&race, 4);
        assert!(splits.previous.is_none());
        race.racers[0].checkpoint = 1;
        splits.update(&race, 0);
        assert!(splits.previous.is_none());
    }

    #[test]
    fn lap_wrap_has_distinct_monotonic_checkpoint_identity() {
        assert_eq!(checkpoint_ordinal(0, 1, 4), 0);
        assert_eq!(checkpoint_ordinal(0, 0, 4), 3);
        assert_eq!(checkpoint_ordinal(1, 1, 4), 4);
        assert_eq!(checkpoint_ordinal(1, 2, 4), 5);
    }

    #[test]
    fn paused_time_creates_no_crossings_and_same_time_teleport_clears_history() {
        let mut splits = SplitTimes::default();
        splits.observe(1., vec![0, 0]);
        splits.observe(2., vec![1, 1]);
        let before = splits.relative_to(0, 1);
        splits.observe(2., vec![1, 1]);
        assert_eq!(splits.relative_to(0, 1), before);
        splits.observe(2., vec![2, 1]);
        assert_eq!(splits.relative_to(0, 1), None);
    }

    #[test]
    fn no_grid_or_unshared_crossing_is_invented() {
        let mut splits = SplitTimes::default();
        splits.observe(0., vec![0, 0]);
        assert_eq!(splits.relative_to(0, 1), None);
        splits.observe(10., vec![1, 0]);
        assert_eq!(splits.relative_to(0, 1), None);
    }

    #[test]
    fn same_checkpoint_uses_elapsed_intervals_and_signed_delta() {
        let mut splits = SplitTimes::default();
        splits.observe(9.9, vec![0, 0]);
        splits.observe(10., vec![1, 0]);
        splits.observe(11.1, vec![1, 0]);
        splits.observe(11.2, vec![1, 1]);
        let split = splits.relative_to(0, 1).unwrap();
        assert!((split.seconds - 1.2).abs() < 0.001);
        assert!((split.uncertainty - 0.1).abs() < 0.001);
        assert_eq!(split.label(), "~+1.2s");
        assert_eq!(splits.relative_to(1, 0).unwrap().label(), "~-1.2s");
        // A later unshared checkpoint retains the most recent shared split.
        splits.observe(12., vec![2, 1]);
        assert_eq!(splits.relative_to(0, 1).unwrap().label(), "~+1.2s");
    }

    #[test]
    fn elapsed_rollback_or_checkpoint_regression_discards_history() {
        let mut splits = SplitTimes::default();
        splits.observe(1., vec![0, 0]);
        splits.observe(2., vec![1, 1]);
        assert!(splits.relative_to(0, 1).is_some());
        splits.observe(0., vec![0, 0]);
        assert_eq!(splits.relative_to(0, 1), None);
        splits.observe(1., vec![1, 1]);
        splits.observe(2., vec![0, 1]);
        assert_eq!(splits.relative_to(0, 1), None);
    }

    #[test]
    fn skipping_crossings_does_not_fill_unobserved_checkpoints() {
        let mut splits = SplitTimes::default();
        splits.observe(0., vec![0, 0]);
        splits.observe(1., vec![3, 1]);
        assert_eq!(splits.relative_to(0, 1), None);
        splits.observe(2., vec![3, 3]);
        assert!(splits.relative_to(0, 1).is_some());
        splits.reset();
        assert_eq!(splits.relative_to(0, 1), None);
    }
}

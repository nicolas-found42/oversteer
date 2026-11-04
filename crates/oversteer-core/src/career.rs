use crate::{
    EventContestant, EventDefinition, GameContent, GoalDefinition, LeagueDefinition, RaceMode,
};

const CIRCUIT: &str = "london_circuit1";
const DRIFT: &str = "london_drift_drift1";
const CARS: [&str; 3] = ["GT4_HOND0018", "GT4_MAZD0012", "GT4_MITS0001"];

impl GameContent {
    /// Select the independent career without rewriting recovered source catalogs.
    pub fn apply_oversteer_career(&mut self) -> Result<(), String> {
        for id in [CIRCUIT, DRIFT] {
            if !self.tracks.iter().any(|track| track.id == id) {
                return Err(format!("Career requires course {id}"));
            }
        }
        for id in CARS {
            if !self.cars.iter().any(|car| car.id == id) {
                return Err(format!("Career requires vehicle {id}"));
            }
        }
        self.tracks
            .retain(|track| [CIRCUIT, DRIFT].contains(&track.id.as_str()));
        for track in &mut self.tracks {
            track.name = if track.id == CIRCUIT {
                "London Circuit"
            } else {
                "London Drift"
            }
            .into();
        }
        for car in &mut self.cars {
            car.league = car.league.min(5);
            match car.id.as_str() {
                "GT4_HOND0018" => {
                    car.league = 0;
                    car.price = 15000;
                }
                "GT4_MAZD0012" => {
                    car.league = 0;
                    car.price = 18000;
                }
                "GT4_MITS0001" => {
                    car.league = 1;
                    car.price = 32000;
                }
                _ => {}
            }
        }
        // A stable starter is independent of recovered catalog ordering.
        let starter = self.cars.iter().position(|car| car.id == CARS[0]).unwrap();
        self.cars.swap(0, starter);
        self.events.clear();
        self.leagues.clear();
        for (tier, name) in ["Local", "Club", "Street", "Regional", "Pro", "Masters"]
            .into_iter()
            .enumerate()
        {
            let tier = tier as u8;
            let reward = 2500 * (u32::from(tier) + 1);
            let mut goals = Vec::new();
            for (kind, mode, track, qualifier) in [
                ("circuit", RaceMode::Circuit, CIRCUIT, false),
                ("drift", RaceMode::Drift, DRIFT, false),
                ("promotion", RaceMode::Circuit, CIRCUIT, true),
            ] {
                let prize = if qualifier { reward * 2 } else { reward };
                let event_name = format!(
                    "{name} {}",
                    if qualifier {
                        if tier == 5 {
                            "Final"
                        } else {
                            "Promotion"
                        }
                    } else if mode.is_drift() {
                        "Drift"
                    } else {
                        "Circuit"
                    }
                );
                goals.push(GoalDefinition {
                    id: format!("oversteer-{tier}-{kind}-win"),
                    description: format!("Win {event_name}"),
                    kind: "WinRace".into(),
                    discipline: if mode.is_drift() { "Drift" } else { "Circuit" }.into(),
                    qualifier,
                    ..Default::default()
                });
                self.events.push(EventDefinition {
                    id: format!("oversteer-{tier}-{kind}"),
                    name: event_name,
                    track_id: track.into(),
                    mode,
                    league: tier,
                    laps: if qualifier { 2 } else { 1 },
                    reward: prize,
                    prizes: vec![prize, prize * 3 / 5, prize * 2 / 5, prize / 5],
                    target: if mode.is_drift() {
                        1000. * (f32::from(tier) + 1.)
                    } else {
                        0.
                    },
                    opponents: 3,
                    time_limit: if mode.is_drift() { 180. } else { 0. },
                    qualifier,
                    contestants: std::iter::once(EventContestant {
                        tag: "Player".into(),
                        ..Default::default()
                    })
                    .chain((0..3).map(|index| EventContestant {
                        tag: format!("oversteer-rival-{index}"),
                        car_id: CARS[if tier == 0 { index % 2 } else { index }].into(),
                        team: index as u8 + 1,
                    }))
                    .collect(),
                    ..Default::default()
                });
            }
            self.leagues.push(LeagueDefinition {
                league: tier,
                name: format!("Tier {} · {name}", tier + 1),
                optional_goals_required: 2,
                goals,
            });
        }
        Ok(())
    }
}

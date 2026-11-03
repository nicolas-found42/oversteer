use oversteer_core::*;
fn main() {
    let original: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let car = original
        .cars
        .iter()
        .find(|c| c.id == "MCLA_VP_SLN_S7_06")
        .unwrap()
        .clone();
    let mut c = original.clone();
    c.leagues.clear();
    c.cars = vec![car.clone()];
    c.events = vec![EventDefinition {
        id: "search".into(),
        track_id: "alps_drift1_drift1".into(),
        mode: RaceMode::DriftEndurance,
        target: 1000000.,
        opponents: 0,
        ..Default::default()
    }];
    let mut best = 0f32;
    for entry in [1.5, 2.5, 4.] {
        for steer in [0.3, 0.5, 0.7, 1.] {
            for hand in [0., 0.01, 0.03, 0.1, 0.3, 0.8] {
                for desired_speed in [11., 13., 16.] {
                    let mut game = Game::new(c.clone());
                    game.command(GameCommand::Navigate {
                        screen: GameScreen::QuickRace,
                    })
                    .unwrap();
                    game.command(GameCommand::Customize {
                        car_id: car.id.clone(),
                        customization: Customization {
                            engine: 3,
                            ..Default::default()
                        },
                    })
                    .unwrap();
                    game.command(GameCommand::StartRace {
                        event_id: "search".into(),
                        career: false,
                        wager: 0,
                        pink_slip: false,
                    })
                    .unwrap();
                    let mut peak = 0f32;
                    let mut elapsed = 0f32;
                    let mut clean = true;
                    for _ in 0..15000 {
                        let r = game.frame_snapshot().race.unwrap();
                        let v = &r.racers[0];
                        elapsed = r.elapsed;
                        let input = PlayerInput {
                            throttle: if r.elapsed < entry {
                                1.
                            } else {
                                ((desired_speed - v.speed_kph / 3.6) * 0.8).clamp(0., 1.)
                            },
                            steering: if r.elapsed < entry { 0. } else { steer },
                            handbrake: if r.elapsed < entry { 0. } else { hand },
                            ..Default::default()
                        };
                        game.advance(1. / 60., input);
                        let snap = game.frame_snapshot();
                        let r = snap.race.unwrap();
                        peak = peak.max(r.racers[0].chain_score);
                        clean = r.racers[0].clean_lap;
                        if snap.screen == GameScreen::Results {
                            break;
                        }
                    }
                    if peak > best {
                        best = peak;
                        println!("best{best} entry{entry} steer{steer} hand{hand} speed{desired_speed} time{elapsed} clean{clean}");
                    }
                }
            }
        }
    }
}

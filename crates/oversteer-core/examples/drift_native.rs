use oversteer_core::*;
fn main() {
    let original: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let starts: serde_json::Value = serde_json::from_str(
        &std::fs::read_to_string("artifacts/juiced2-build/native-ai/starts/all33.json").unwrap(),
    )
    .unwrap();
    let car = original
        .cars
        .iter()
        .find(|c| c.handling.layout == DriveLayout::Awd)
        .unwrap()
        .clone();
    for track in original.tracks.iter().filter(|t| t.id.contains("drift")) {
        let mut best = (0f32, 0f32, 0f32, 0f32);
        for steering in [-0.65, -0.6, -0.55, -0.5, 0.5, 0.55, 0.6, 0.65] {
            for hand in [0.7, 0.8, 0.85] {
                let mut c = original.clone();
                c.cars = vec![car.clone()];
                let path = format!(
                    "artifacts/juiced2-build/collision/track-local/{}.json",
                    track.id
                );
                let collision: NativeCollisionDefinition =
                    serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
                let runtime_track = c.tracks.iter_mut().find(|t| t.id == track.id).unwrap();
                runtime_track.collision = Some(collision);
                let native_start = starts["tracks"]
                    .as_array()
                    .unwrap()
                    .iter()
                    .find(|t| t["id"].as_str() == Some(&track.id))
                    .unwrap();
                runtime_track.start_grid =
                    serde_json::from_value(native_start["start_grid"].clone()).unwrap();

                c.events = vec![EventDefinition {
                    id: "diagnostic".into(),
                    mode: RaceMode::DriftEndurance,
                    target: 1000000.,
                    track_id: track.id.clone(),
                    opponents: 0,
                    ..Default::default()
                }];
                let mut game = Game::new(c);
                game.command(GameCommand::StartRace {
                    event_id: "diagnostic".into(),
                    career: false,
                    wager: 0,
                    pink_slip: false,
                })
                .unwrap();
                let mut peak = 0f32;
                let mut unsupported = 0u32;
                for _ in 0..14400 {
                    let snapshot = game.frame_snapshot();
                    let player = &snapshot.race.as_ref().unwrap().racers[0];
                    let active = player.speed_kph >= 36.;
                    let input = if peak >= 1_000_000. {
                        PlayerInput {
                            brake: 1.,
                            ..Default::default()
                        }
                    } else {
                        PlayerInput {
                            throttle: 1.,
                            steering: if active { steering } else { 0. },
                            handbrake: if active { hand } else { 0. },
                            ..Default::default()
                        }
                    };
                    game.advance(1. / 60., input);
                    let snapshot = game.frame_snapshot();
                    peak = peak.max(snapshot.race.as_ref().unwrap().racers[0].chain_score);
                    let r = &snapshot.race.as_ref().unwrap().racers[0];
                    if snapshot.race.as_ref().unwrap().elapsed > 0.
                        && r.surface_contacts.iter().filter(|c| c.active).count() < 2
                    {
                        unsupported += 1;
                    }
                    if peak > best.0 {
                        best = (
                            peak,
                            steering,
                            hand,
                            snapshot.race.as_ref().unwrap().elapsed,
                        );
                    }

                    if unsupported > 30 {
                        break;
                    }
                    if snapshot.screen == GameScreen::Results {
                        if peak > best.0 {
                            best = (peak, steering, hand, snapshot.result.as_ref().unwrap().time);
                        }
                        if peak > 500000. {
                            println!(
                                "FOUND {} peak{} steer{} hand{} result{:?}",
                                track.id, peak, steering, hand, snapshot.result
                            );
                        }
                        break;
                    }
                }
            }
        }
        println!("BEST {} {:?}", track.id, best);
    }
}

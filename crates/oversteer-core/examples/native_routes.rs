use oversteer_core::*;
fn main() {
    let mut content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let audit: serde_json::Value = serde_json::from_str(
        &std::fs::read_to_string("artifacts/juiced2-build/body-geometry-audit.json").unwrap(),
    )
    .unwrap();
    for car in &mut content.cars {
        let record = audit["cars"]
            .as_array()
            .unwrap()
            .iter()
            .find(|r| r["code"] == car.id)
            .unwrap();
        car.handling.body_min_y = record["body_bounds"]["min"][1].as_f64().unwrap() as f32;
    }
    for track in content.tracks.clone() {
        content.events = vec![EventDefinition {
            id: "scenario".into(),
            track_id: track.id.clone(),
            opponents: 0,
            laps: 1,
            ..Default::default()
        }];
        let mut game = Game::new(content.clone());
        game.command(GameCommand::StartRace {
            event_id: "scenario".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..216000 {
            let input = game.scenario_player_ai_input();
            game.advance(1. / 60., input);
            if game.frame_snapshot().screen == GameScreen::Results {
                break;
            }
        }
        let snapshot = game.frame_snapshot();
        let race = snapshot.race.as_ref().unwrap();
        let racer = &race.racers[0];
        println!(
            "{} {:?} t{} cp{} pos{:?} result{:?}",
            track.id,
            snapshot.screen,
            race.elapsed,
            racer.checkpoint,
            racer.position,
            snapshot.result
        );
    }
}

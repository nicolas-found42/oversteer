use oversteer_core::*;
fn main() {
    let original: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for track in original
        .tracks
        .iter()
        .filter(|t| t.id.contains("rome_drift"))
    {
        let mut content = original.clone();
        content.cars = vec![original
            .cars
            .iter()
            .find(|c| c.handling.layout == DriveLayout::Awd)
            .unwrap()
            .clone()];
        content.events = vec![original
            .events
            .iter()
            .find(|e| e.id == "native_ca32970d_010")
            .unwrap()
            .clone()];
        let mut game = Game::new(content);
        let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
        save.career.league = 2;
        game =
            Game::load_json(game.content.clone(), &serde_json::to_string(&save).unwrap()).unwrap();
        game.command(GameCommand::StartRace {
            event_id: "native_ca32970d_010".into(),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        let started = std::time::Instant::now();
        let mut controls = Vec::new();
        let mut peak = 0f32;
        let mut unsupported = 0u32;
        for tick in 0..14400 {
            let input = game.scenario_endurance_predictive_input();
            controls.push(serde_json::json!({"tick":tick,"input":input}));
            if tick % 600 == 0 {
                let s = game.frame_snapshot();
                let r = s.race.as_ref().unwrap();
                let p = &r.racers[0];
                println!(
                    "TRACE {tick} v{} angle{} in{:?} pos{:?}",
                    p.speed_kph, p.chain_score, input, p.position
                );
            }
            game.advance(1. / 60., input);
            let snapshot = game.frame_snapshot();
            let race = snapshot.race.as_ref().unwrap();
            let player = &race.racers[0];
            peak = peak.max(player.chain_score);
            if race.elapsed > 0. && player.surface_contacts.iter().filter(|c| c.active).count() < 2
            {
                unsupported += 1;
            }
            if snapshot.screen == GameScreen::Results || unsupported > 30 || tick == 14399 {
                std::fs::write(
                    "artifacts/juiced2-build/rome-drift-500k-binary-controls.json",
                    serde_json::to_vec(&controls).unwrap(),
                )
                .unwrap();
                std::fs::write(
                    "artifacts/juiced2-build/rome-drift-500k-binary-save.json",
                    game.save_json().unwrap(),
                )
                .unwrap();
                println!(
                    "{} ticks{} peak{} time{} unsupported{} cpu{:?} result{:?} pos{:?}",
                    track.id,
                    tick,
                    peak,
                    race.elapsed,
                    unsupported,
                    started.elapsed(),
                    snapshot.result,
                    player.position
                );
                break;
            }
        }
    }
}

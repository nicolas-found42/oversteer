use oversteer_core::*;
fn main() {
    let mut c: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for track in ["tokyo_circuit5", "tokyo_drift2_drift2"] {
        c.events = vec![EventDefinition {
            id: "cost".into(),
            track_id: track.into(),
            opponents: 7,
            laps: 10,
            ..Default::default()
        }];
        let mut game = Game::new(c.clone());
        let begin = std::time::Instant::now();
        game.command(GameCommand::StartRace {
            event_id: "cost".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        let build = begin.elapsed();
        let mut samples = Vec::new();
        for tick in 0..2400 {
            let input = game.scenario_player_ai_input();
            let start = std::time::Instant::now();
            game.advance(1. / 60., input);
            if tick >= 240 {
                samples.push(start.elapsed().as_secs_f64() * 1000.);
            }
        }
        samples.sort_by(f64::total_cmp);
        let n = samples.len();
        println!(
            "{track} build{build:?} advance_ms median{} p95{} max{}",
            samples[n / 2],
            samples[n * 95 / 100],
            samples[n - 1]
        );
    }
}

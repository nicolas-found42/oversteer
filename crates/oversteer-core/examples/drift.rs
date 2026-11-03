use oversteer_core::*;
fn main() {
    let original: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for layout in [DriveLayout::Fwd, DriveLayout::Rwd, DriveLayout::Awd] {
        let car = original
            .cars
            .iter()
            .find(|c| c.handling.layout == layout)
            .unwrap()
            .clone();
        let mut c = original.clone();
        c.cars = vec![car.clone()];
        c.events = vec![EventDefinition {
            id: "drift".into(),
            mode: RaceMode::DriftEndurance,
            target: 1000000.,
            track_id: "alps_drift1_drift1".into(),
            opponents: 0,
            ..Default::default()
        }];
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: "drift".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        let mut max_points = 0f32;
        let mut max_angle = 0f32;
        for i in 0..18000 {
            let input = game.scenario_player_ai_input();
            game.advance(1. / 60., input);
            let snap = game.frame_snapshot();
            let race = snap.race.unwrap();
            let player = &race.racers[0];
            max_points = max_points.max(player.chain_score);
            let yaw = 2. * player.rotation[1].atan2(player.rotation[3]);
            let angle = ((player.velocity[0] * yaw.cos() - player.velocity[2] * yaw.sin())
                .atan2(player.velocity[0] * yaw.sin() + player.velocity[2] * yaw.cos()))
            .to_degrees()
            .abs();
            max_angle = max_angle.max(angle);
            if i % 60 == 0 {
                println!(
                    "{} t{:.1} speed{:.1} angle{:.1} chain{} total{} clean{} input{:?}",
                    car.id,
                    race.elapsed,
                    player.speed_kph,
                    angle,
                    player.chain_score,
                    player.drift_score,
                    player.clean_lap,
                    input
                );
            }
            if snap.screen == GameScreen::Results {
                println!(
                    "RESULT {} {:?} maxchain{} maxangle{} clean{}",
                    car.id, snap.result, max_points, max_angle, player.clean_lap
                );
                break;
            }
        }
    }
}

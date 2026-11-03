use oversteer_core::*;
fn main() {
    let mut c = GameContent {
        leagues: vec![],
        drivers: vec![],
        cars: vec![CarDefinition {
            id: "a".into(),
            ..Default::default()
        }],
        tracks: vec![TrackDefinition::default()],
        events: vec![EventDefinition {
            laps: 1,
            opponents: 0,
            ..Default::default()
        }],
    };
    c.tracks[0].points = (0..80)
        .map(|i| {
            let a = i as f32 * std::f32::consts::TAU / 80.;
            [80. * (1. - a.cos()), 0., 80. * a.sin()]
        })
        .collect();
    let mut g = Game::new(c);
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for i in 0..60 * 60 {
        let input = g.scenario_player_ai_input();
        g.advance(1. / 60., input);
        if i % 120 == 0 {
            let s = g.frame_snapshot();
            let p = &s.race.unwrap().racers[0];
            println!(
                "{i} p{:?} yaw{} speed{} steer{} throttle{} check{}",
                p.position,
                2. * p.rotation[1].atan2(p.rotation[3]),
                p.speed_kph,
                input.steering,
                input.throttle,
                p.checkpoint
            );
        }
    }
}

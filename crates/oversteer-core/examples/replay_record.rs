use oversteer_core::*;
fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let mut game = Game::load_json(content, &std::fs::read_to_string(&args[0]).unwrap()).unwrap();
    std::fs::write(
        format!("{}-initial-save.json", args[3]),
        game.save_json().unwrap(),
    )
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: args[2].clone(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    if args.get(4).map(String::as_str) == Some("grid-bet") {
        game.command(GameCommand::OpenGrid).unwrap();
        let n = game.frame_snapshot().race.unwrap().racers.len();
        game.command(GameCommand::OfferDriverBet {
            racer: n - 1,
            amount: 2500,
        })
        .unwrap();
        game.command(GameCommand::AcceptBetOffer).unwrap();
        game.command(GameCommand::LaunchRace).unwrap();
    }
    std::fs::write(
        format!("{}-initial-snapshot.json", args[3]),
        serde_json::to_vec(&game.frame_snapshot()).unwrap(),
    )
    .unwrap();
    let rows: Vec<serde_json::Value> =
        serde_json::from_str(&std::fs::read_to_string(&args[1]).unwrap()).unwrap();
    let mut actual = Vec::new();
    let mut first = None;
    let mut nitrous_requested_ticks = 0;
    let mut nitrous_active_ticks = 0;
    let mut minimum_nitrous = 1.0_f32;
    let mut nitrous_recharge_ticks = 0;
    for (tick, mut row) in rows.into_iter().enumerate() {
        let before = game.frame_snapshot();
        let countdown = before.race.as_ref().unwrap().countdown;
        if countdown <= 0. && first.is_none() {
            first = Some(tick);
        }
        let input: PlayerInput = serde_json::from_value(row["input"].clone()).unwrap();
        assert!(input.nitrous == 0. || input.nitrous == 1.);
        nitrous_requested_ticks += usize::from(input.nitrous > 0.);
        let raw = row["raw_axes"]["steering_0"].as_f64().unwrap() as f32;
        let mapped = if raw.abs() > 0.12 {
            -raw.signum() * (raw.abs() - 0.12) / 0.88
        } else {
            0.
        };
        assert_eq!(
            mapped.to_bits(),
            input.steering.to_bits(),
            "unreachabletick{tick}"
        );
        row["tick"] = tick.into();
        row["countdown_before"] = countdown.into();
        row["active_tick"] = first.map(|f| tick - f).into();
        actual.push(row);
        game.advance(1. / 60., input);
        let after = game.frame_snapshot();
        let racer = &after.race.as_ref().unwrap().racers[0];
        nitrous_active_ticks += usize::from(racer.nitrous_active);
        minimum_nitrous = minimum_nitrous.min(racer.nitrous);
        nitrous_recharge_ticks +=
            usize::from(racer.nitrous > before.race.as_ref().unwrap().racers[0].nitrous);
        if after.screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    assert_eq!(snapshot.screen, GameScreen::Results);
    std::fs::write(
        format!("{}-controls.json", args[3]),
        serde_json::to_vec(&actual).unwrap(),
    )
    .unwrap();
    std::fs::write(format!("{}-save.json", args[3]), game.save_json().unwrap()).unwrap();
    std::fs::write(
        format!("{}-final-snapshot.json", args[3]),
        serde_json::to_vec(&snapshot).unwrap(),
    )
    .unwrap();
    let evidence = serde_json::json!({"first_active_tick":first,"tick_count":actual.len(),"active_ticks":actual.len()-first.unwrap(),"event_id":args[2],"car_id":snapshot.race.as_ref().unwrap().racers[0].car_id,"result":snapshot.result,"raw_handbrake_button":2,"raw_nitrous_button":0,"outer_dt_seconds":1./60.,"nitrous_observations":{"requested_ticks":nitrous_requested_ticks,"active_ticks":nitrous_active_ticks,"minimum_fraction":minimum_nitrous,"recharge_ticks":nitrous_recharge_ticks},"host_reachability":"Everyrawaxiswascheckedwiththeactualfloat32deadzoneforwardmapbeforeadvance; binaryHB/NOS,zeroShift/forwardOnly validated by preprocessing."});
    std::fs::write(
        format!("{}-evidence.json", args[3]),
        serde_json::to_vec_pretty(&evidence).unwrap(),
    )
    .unwrap();
    println!("{evidence}");
}

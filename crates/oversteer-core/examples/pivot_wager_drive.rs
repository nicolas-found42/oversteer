//! Record host-reachable controls from an earned save; never inject race state.
//! Usage: pivot_wager_drive SAVE cash|pink DELAY_SECONDS OUTPUT_DIRECTORY
use oversteer_core::*;
use std::path::PathBuf;

fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    assert_eq!(
        args.len(),
        4,
        "Expected SAVE cash|pink DELAY_SECONDS OUTPUT_DIRECTORY"
    );
    assert!(matches!(args[1].as_str(), "cash" | "pink"));
    let delay: f32 = args[2].parse().unwrap();
    let output = PathBuf::from(&args[3]);
    std::fs::create_dir(&output).unwrap();
    let mut content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("godot/assets/game-content.json").unwrap())
            .unwrap();
    content.apply_oversteer_vehicle_corrections();
    content.apply_oversteer_career().unwrap();
    std::fs::write(
        output.join("content.json"),
        serde_json::to_string(&content).unwrap(),
    )
    .unwrap();
    let initial = std::fs::read_to_string(&args[0]).unwrap();
    let mut game = Game::load_json(content, &initial).unwrap();
    std::fs::write(output.join("initial-save.json"), &initial).unwrap();
    game.command(GameCommand::StartRace {
        event_id: "oversteer-0-circuit".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    game.command(if args[1] == "cash" {
        GameCommand::OfferDriverBet {
            racer: 2,
            amount: 1000,
        }
    } else {
        GameCommand::OfferPinkSlip { racer: 2 }
    })
    .unwrap();
    game.command(GameCommand::AcceptBetOffer).unwrap();
    let offer = game.frame_snapshot().race.unwrap().bet_offer.unwrap();
    game.command(GameCommand::LaunchRace).unwrap();
    let mut controls = Vec::new();
    let mut first = None;
    for tick in 0..60 * 600 {
        let snapshot = game.frame_snapshot();
        let race = snapshot.race.as_ref().unwrap();
        if race.countdown <= 0. && first.is_none() {
            first = Some(tick);
        }
        let mut input = if race.elapsed < delay {
            PlayerInput {
                brake: 1.,
                ..Default::default()
            }
        } else {
            game.scenario_player_ai_input()
        };
        let raw = if input.steering == 0. {
            0.
        } else {
            -input.steering.signum() * (0.12_f32 + 0.88_f32 * input.steering.abs())
        };
        input.steering = if raw.abs() > 0.12 {
            -raw.signum() * (raw.abs() - 0.12) / 0.88
        } else {
            0.
        };
        assert_eq!(input.shift, 0);
        assert!([0., 1.].contains(&input.handbrake) && [0., 1.].contains(&input.nitrous));
        controls.push(serde_json::json!({"tick":tick,"active_tick":first.map(|f|tick-f),
            "countdown_before":race.countdown,"raw_axes":{"steering_0":raw,"throttle_5":input.throttle,"brake_4":input.brake},"input":input}));
        game.advance(1. / 60., input);
        if game.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    let finished = snapshot.screen == GameScreen::Results;
    let race = snapshot.race.as_ref().unwrap();
    let evidence = serde_json::json!({"event_id":race.event_id,"car_id":race.racers[0].car_id,
        "first_active_tick":first,"tick_count":controls.len(),"active_ticks":controls.len()-first.unwrap(),
        "raw_handbrake_button":2,"raw_nitrous_button":0,"raw_reverse_button":3,"result":snapshot.result,
        "grid_driver_bet":{"racer":2,"offer_amount":1000,"accepted_counter":offer.counter_amount,"kind":offer.kind},
        "method":"Normal difficulty; ordinary host-reachable controls only. No pose, score, ownership or progression injection.",
        "held_brake_seconds":delay,"finished":finished});
    for (name, value) in [
        ("controls.json", serde_json::to_value(controls).unwrap()),
        ("snapshot.json", serde_json::to_value(snapshot).unwrap()),
        ("evidence.json", evidence.clone()),
    ] {
        std::fs::write(
            output.join(name),
            serde_json::to_vec_pretty(&value).unwrap(),
        )
        .unwrap();
    }
    std::fs::write(output.join("save.json"), game.save_json().unwrap()).unwrap();
    println!("{evidence}");
    assert!(
        finished,
        "Race did not finish within ten minutes; diagnostic recording retained"
    );
}

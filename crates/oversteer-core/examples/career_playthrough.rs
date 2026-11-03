use oversteer_core::*;
fn main() {
    let mut args = std::env::args().skip(1).collect::<Vec<_>>();
    let content_path = if args.first().map(String::as_str) == Some("--content") {
        let path = args.remove(1);
        args.remove(0);
        path
    } else {
        "data/juiced2/content.json".into()
    };
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string(&content_path).unwrap()).unwrap();
    println!("CONTENT {content_path}");
    let mut game = if args.first().map(String::as_str) == Some("--load") {
        let path = args.remove(1);
        args.remove(0);
        Game::load_json(content.clone(), &std::fs::read_to_string(path).unwrap()).unwrap()
    } else {
        Game::new(content.clone())
    };
    if args.first().map(String::as_str) == Some("--easy") {
        args.remove(0);
        game.command(GameCommand::SetDifficulty { level: 0 })
            .unwrap();
    }
    if args.first().map(String::as_str) == Some("--buy") {
        let car_id = args.remove(1);
        args.remove(0);
        game.command(GameCommand::BuyCar {
            car_id: car_id.clone(),
        })
        .unwrap();
        game.command(GameCommand::SelectCar { car_id }).unwrap();
    }
    if args.first().map(String::as_str) == Some("--upgrade") {
        args.remove(0);
        game.command(GameCommand::Navigate {
            screen: GameScreen::Garage,
        })
        .unwrap();
        let snapshot = game.frame_snapshot();
        let mut customization = snapshot.selected_customization;
        customization.engine = 3;
        customization.transmission = 3;
        customization.tyres = 3;
        customization.nitrous = 3;
        game.command(GameCommand::Customize {
            car_id: snapshot.selected_car,
            customization,
        })
        .unwrap();
        game.command(GameCommand::Checkout).unwrap();
    }
    let mut wager_amount = 2500;
    let mut stock_nos = false;
    loop {
        match args.first().map(String::as_str) {
            Some("--stock-nos") => {
                args.remove(0);
                stock_nos = true;
            }
            Some("--select") => {
                let car_id = args.remove(1);
                args.remove(0);
                game.command(GameCommand::SelectCar { car_id }).unwrap();
            }
            Some("--wager") => {
                wager_amount = args.remove(1).parse::<u32>().unwrap();
                args.remove(0);
            }
            _ => break,
        }
    }
    let predictive = args.first().map(String::as_str) == Some("--predict");
    if predictive {
        args.remove(0);
    }
    if args.is_empty() {
        args = [
            "native_28956449_001",
            "native_28956449_003",
            "native_28956449_007",
            "native_28956449_002",
            "native_28956449_000",
        ]
        .map(str::to_owned)
        .to_vec();
    }
    for event in args {
        if matches!(
            game.frame_snapshot().screen,
            GameScreen::Results | GameScreen::Complete
        ) {
            game.command(GameCommand::Continue).unwrap();
        }
        game.command(GameCommand::Navigate {
            screen: GameScreen::Career,
        })
        .unwrap();
        let initial = game.save_json().unwrap();
        if let Err(error) = game.command(GameCommand::StartRace {
            event_id: event.clone(),
            career: true,
            wager: 0,
            pink_slip: false,
        }) {
            println!("BLOCKED {event}: {error}");
            break;
        }
        if game.frame_snapshot().race.as_ref().unwrap().racers.len() > 1 {
            game.command(GameCommand::OpenGrid).unwrap();
        }
        if game.frame_snapshot().screen == GameScreen::Grid {
            let n = game.frame_snapshot().race.unwrap().racers.len();
            if n > 1 && game.frame_snapshot().career.cash >= 5000 {
                if game
                    .command(GameCommand::OfferDriverBet {
                        racer: n - 1,
                        amount: wager_amount,
                    })
                    .is_ok()
                {
                    println!(
                        "Offer{:?}",
                        game.frame_snapshot().race.as_ref().unwrap().bet_offer
                    );
                    game.command(GameCommand::AcceptBetOffer).unwrap();
                }
            }
            game.command(GameCommand::LaunchRace).unwrap();
        }
        let started = std::time::Instant::now();
        let mut controls = Vec::new();
        let mut held = PlayerInput::default();
        for tick in 0..216000 {
            let mut input =
                if predictive && game.frame_snapshot().race.as_ref().unwrap().mode.is_drift() {
                    if tick % 12 == 0 {
                        held = game.scenario_drift_predictive_input();
                    }
                    held
                } else {
                    game.scenario_player_ai_input()
                };
            let raw = if input.steering == 0. {
                0.
            } else {
                -input.steering.signum() * (0.12 + 0.88 * input.steering.abs())
            };
            input.steering = if raw.abs() > 0.12 {
                -raw.signum() * (raw.abs() - 0.12) / 0.88
            } else {
                0.
            };
            input.handbrake =
                if game.frame_snapshot().race.as_ref().unwrap().racers[0].speed_kph < 21.6 {
                    0.
                } else if input.handbrake > 0. {
                    1.
                } else {
                    0.
                };
            if stock_nos
                && tick % 600 < 120
                && game.frame_snapshot().race.as_ref().unwrap().racers[0].speed_kph > 60.
                && input.steering.abs() < 0.1
                && input.throttle > 0.1
            {
                input.nitrous = 1.;
            }
            controls.push(input);
            game.advance(1. / 60., input);
            if tick % 1800 == 0 {
                let snapshot = game.frame_snapshot();
                let race = snapshot.race.as_ref().unwrap();
                println!(
                    "{event} tick{tick} time{} position{} lap{} cp{}",
                    race.elapsed, race.position, race.racers[0].lap, race.racers[0].checkpoint
                );
                println!(
                    "playerpos{:?} v{:?} finished{} eliminated{}",
                    race.racers[0].position,
                    race.racers[0].velocity,
                    race.racers[0].finished,
                    race.racers[0].eliminated
                );
            }
            if tick % 60 == 0 {
                let screen = game.frame_snapshot().screen;
                if screen == GameScreen::RoundResults {
                    game.command(GameCommand::Continue).unwrap();
                } else if screen != GameScreen::Race {
                    break;
                }
            }
        }
        let snapshot = game.frame_snapshot();
        println!(
            "EVENT{event} cpu{:?} screen{:?} result{:?} cash{} league{} goals{}/{} open{}",
            started.elapsed(),
            snapshot.screen,
            snapshot.result,
            snapshot.career.cash,
            snapshot.career.league,
            snapshot.league_progress.optional_completed,
            snapshot.league_progress.optional_required,
            snapshot.league_progress.promotion_open
        );
        let prefix = format!(
            "artifacts/juiced2-build/career-{event}{}",
            if stock_nos {
                "-stock-nos"
            } else if predictive {
                "-predict"
            } else {
                ""
            }
        );
        std::fs::write(format!("{prefix}-initial-save.json"), initial).unwrap();
        std::fs::write(
            format!("{prefix}-controls.json"),
            serde_json::to_vec(&controls).unwrap(),
        )
        .unwrap();
        std::fs::write(
            format!("{prefix}-final-snapshot.json"),
            serde_json::to_vec(&snapshot).unwrap(),
        )
        .unwrap();
        let saved = game.save_json().unwrap();
        std::fs::write(format!("{prefix}-save.json"), &saved).unwrap();
        game = Game::load_json(content.clone(), &saved).unwrap();
    }
}

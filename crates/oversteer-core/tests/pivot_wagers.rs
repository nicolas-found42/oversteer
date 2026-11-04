use oversteer_core::*;

fn content() -> GameContent {
    GameContent {
        cars: (0..3)
            .map(|i| CarDefinition {
                id: format!("car{i}"),
                price: 1000,
                ..Default::default()
            })
            .collect(),
        tracks: vec![TrackDefinition::default()],
        events: vec![EventDefinition::default()],
        ..Default::default()
    }
}

fn staked_race(pink_slip: bool) -> Game {
    let mut c = content();
    c.events[0].contestants = vec![
        EventContestant {
            tag: "Player".into(),
            ..Default::default()
        },
        EventContestant {
            tag: "rival".into(),
            car_id: "car2".into(),
            ..Default::default()
        },
    ];
    let mut game = Game::new(c);
    game.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 1000,
        pink_slip,
    })
    .unwrap();
    game
}

#[test]
fn restart_forfeits_original_stake_without_automatically_placing_another_bet() {
    let mut game = staked_race(true);
    game.command(GameCommand::Restart).unwrap();
    let state = game.frame_snapshot();
    assert_eq!(state.career.cash, 23000);
    assert_eq!(state.career.losses, 1);
    assert!(!state.career.garage.contains_key("car1"));
    assert_eq!(state.selected_car, "car0");
    let race = state.race.unwrap();
    assert_eq!(race.racers[0].car_id, "car0");
    assert_eq!(race.wager, 0);
    assert!(!race.pink_slip);
    assert_eq!(state.career.vehicle_history["car1"].pink_slip_losses, 1);
}

#[test]
fn leaving_an_unfinished_race_forfeits_once_and_cannot_resume_it() {
    let mut game = staked_race(true);
    game.command(GameCommand::Pause).unwrap();
    game.command(GameCommand::Navigate {
        screen: GameScreen::Career,
    })
    .unwrap();
    game.command(GameCommand::Navigate {
        screen: GameScreen::MainMenu,
    })
    .unwrap();
    let state = game.frame_snapshot();
    assert_eq!(state.career.cash, 23000);
    assert_eq!(state.career.losses, 1);
    assert_eq!(state.career.garage.len(), 1);
    assert!(!state.career.garage.contains_key("car1"));
    assert!(state.race.is_none());
    let reloaded = Game::load_json(content(), &game.save_json().unwrap()).unwrap();
    assert_eq!(reloaded.frame_snapshot().career.garage.len(), 1);
    assert_eq!(reloaded.frame_snapshot().career.losses, 1);
}

#[test]
fn pausing_and_resuming_does_not_forfeit_a_stake() {
    let mut game = staked_race(true);
    game.command(GameCommand::Pause).unwrap();
    game.command(GameCommand::Resume).unwrap();
    let state = game.frame_snapshot();
    assert_eq!(state.career.losses, 0);
    assert_eq!(state.career.garage.len(), 2);
    assert_eq!(state.career.cash, 23000);
}

#[test]
fn cash_only_restart_keeps_the_car_and_does_not_double_charge_the_wager() {
    let mut game = staked_race(false);
    game.command(GameCommand::Restart).unwrap();
    let state = game.frame_snapshot();
    assert_eq!(state.career.cash, 23000);
    assert_eq!(state.career.garage.len(), 2);
    assert_eq!(state.selected_car, "car1");
}

#[test]
fn a_new_race_or_continue_cannot_discard_an_unsettled_stake() {
    let mut game = staked_race(true);
    assert!(game
        .command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .is_err());
    assert!(game.command(GameCommand::Continue).is_err());
    assert_eq!(game.frame_snapshot().career.garage.len(), 2);
    game.command(GameCommand::Navigate {
        screen: GameScreen::MainMenu,
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().career.garage.len(), 1);
}

#[test]
fn interrupted_race_returns_unsettled_cash_and_preserves_the_staked_car_once() {
    let game = staked_race(true);
    assert_eq!(game.frame_snapshot().career.cash, 23000);
    let recovered = Game::load_json(content(), &game.save_json().unwrap()).unwrap();
    let state = recovered.frame_snapshot();
    assert_eq!(state.career.cash, 24000);
    assert_eq!(state.career.losses, 0);
    assert_eq!(state.career.garage.len(), 2);
    assert!(state.race.is_none());
    let saved = recovered.save_json().unwrap();
    let again = Game::load_json(content(), &saved).unwrap();
    assert_eq!(again.save_json().unwrap(), saved);
    assert_eq!(again.frame_snapshot().career.cash, 24000);
}

#[test]
fn settled_reward_and_wager_are_not_refunded_again_on_reload() {
    let mut game = staked_race(false);
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_player([0., 0., 250.], [0.; 3], 2, 1)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    assert!(game.frame_snapshot().result.unwrap().won);
    assert_eq!(game.frame_snapshot().career.cash, 30000);
    let saved = game.save_json().unwrap();
    assert_eq!(
        Game::load_json(content(), &saved)
            .unwrap()
            .save_json()
            .unwrap(),
        saved
    );
}

#[test]
fn pink_slips_cannot_stake_against_a_vehicle_already_in_the_garage() {
    let mut game = Game::new(content());
    game.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    assert!(game
        .command(GameCommand::OfferPinkSlip { racer: 1 })
        .is_err());
}

#[test]
fn a_pink_slip_win_initializes_the_awarded_cars_parts_before_saving() {
    let mut game = staked_race(true);
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    // Isolate settlement and persistence, separately from the recorded driving tests.
    game.scenario_place_player([0., 0., 250.], [0.; 3], 2, 1)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let snapshot = game.frame_snapshot();
    assert_eq!(snapshot.result.unwrap().pink_slip.as_deref(), Some("car2"));
    let saved = game.save_json().unwrap();
    assert_eq!(
        Game::load_json(content(), &saved)
            .unwrap()
            .save_json()
            .unwrap(),
        saved
    );
    assert!(snapshot.career.parts_inventory["car2"].contains(&"engine:0".into()));
}

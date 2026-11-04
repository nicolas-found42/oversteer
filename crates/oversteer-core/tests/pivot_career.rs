use oversteer_core::*;

fn recovered() -> GameContent {
    GameContent {
        cars: ["GT4_HOND0018", "GT4_MAZD0012", "GT4_MITS0001"]
            .into_iter()
            .map(|id| CarDefinition {
                id: id.into(),
                league: 9,
                ..Default::default()
            })
            .chain((3..30).map(|i| CarDefinition {
                id: format!("car{i}"),
                league: 9,
                ..Default::default()
            }))
            .collect(),
        tracks: ["london_circuit1", "london_drift_drift1", "deferred"]
            .into_iter()
            .map(|id| TrackDefinition {
                id: id.into(),
                ..Default::default()
            })
            .collect(),
        events: vec![EventDefinition {
            is_sponsor: true,
            ..Default::default()
        }],
        ..Default::default()
    }
}

fn content() -> GameContent {
    let mut c = recovered();
    c.apply_oversteer_career().unwrap();
    c
}

fn start(game: &mut Game, event: &str) -> Result<(), String> {
    game.command(GameCommand::StartRace {
        event_id: event.into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
}

#[test]
fn independent_catalog_retains_roster_and_has_only_reachable_racing_tiers() {
    let mut c = content();
    assert_eq!(c.cars.len(), 30);
    assert_eq!(c.tracks.len(), 2);
    assert_eq!(c.leagues.len(), 6);
    assert_eq!(c.events.len(), 18);
    assert!(c.cars.iter().all(|c| c.league < 6));
    for tier in &c.leagues {
        assert_eq!(tier.optional_goals_required, 2);
        assert_eq!(tier.goals.len(), 3);
        assert!(tier.goals.iter().all(|g| g.kind == "WinRace"));
        let events: Vec<_> = c
            .events
            .iter()
            .filter(|e| e.league == tier.league)
            .collect();
        assert_eq!(events.len(), 3);
        assert!(events
            .iter()
            .all(|e| !e.is_sponsor && e.entrance_fee == 0 && e.car_class.is_empty()));
        assert_eq!(events.iter().filter(|e| e.qualifier).count(), 1);
    }
    let before = serde_json::to_string(&c).unwrap();
    c.apply_oversteer_career().unwrap();
    assert_eq!(before, serde_json::to_string(&c).unwrap());
}

#[test]
fn career_requires_both_disciplines_and_saved_progress_unlocks_promotion() {
    let c = content();
    let mut game = Game::new(c.clone());
    assert!(start(&mut game, "oversteer-0-promotion").is_err());
    assert!(start(&mut game, "oversteer-1-circuit").is_err());
    start(&mut game, "oversteer-0-circuit").unwrap();
    assert!(game
        .frame_snapshot()
        .race
        .unwrap()
        .racers
        .iter()
        .all(|racer| ["GT4_HOND0018", "GT4_MAZD0012"].contains(&racer.car_id.as_str())));
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    // Isolate finish/reward/progression observation; this is not a driving proof.
    game.scenario_place_player([0., 0., 250.], [0.; 3], 1, 1)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    assert!(game.frame_snapshot().result.unwrap().won);
    assert!(game.frame_snapshot().career.cash > 25000);
    assert!(!game.league_progress().promotion_open);
    game.command(GameCommand::Continue).unwrap();
    assert!(start(&mut game, "oversteer-0-promotion").is_err());
    // Seed an earned drift win to test the save/unlock boundary independently.
    let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    save.career.goal_progress.insert(
        "oversteer-0-drift-win".into(),
        GoalProgress {
            complete: true,
            value: 1.,
        },
    );
    let mut resumed = Game::load_json(c, &serde_json::to_string(&save).unwrap()).unwrap();
    assert!(resumed.league_progress().promotion_open);
    start(&mut resumed, "oversteer-0-promotion").unwrap();
    for _ in 0..190 {
        resumed.advance(1. / 60., PlayerInput::default());
    }
    resumed
        .scenario_place_player([0., 0., 250.], [0.; 3], 2, 1)
        .unwrap();
    resumed.advance(1. / 60., PlayerInput::default());
    assert_eq!(resumed.frame_snapshot().career.league, 1);
    resumed.command(GameCommand::Continue).unwrap();
    // A cleared tier stays replayable even before the next tier's goals are met.
    start(&mut resumed, "oversteer-0-promotion").unwrap();
}

#[test]
fn starter_can_buy_rwd_car_and_enter_without_a_stake_even_at_zero_cash() {
    let c = content();
    let mut game = Game::new(c.clone());
    game.command(GameCommand::BuyCar {
        car_id: "GT4_MAZD0012".into(),
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().career.cash, 7000);
    let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    save.career.cash = 0;
    let mut game = Game::load_json(c, &serde_json::to_string(&save).unwrap()).unwrap();
    start(&mut game, "oversteer-0-circuit").unwrap();
    assert_eq!(game.frame_snapshot().race.unwrap().wager, 0);
}

#[test]
fn missing_required_course_is_an_error_and_does_not_partially_modify_content() {
    let mut c = recovered();
    c.tracks.retain(|t| t.id != "london_drift_drift1");
    let before = serde_json::to_string(&c).unwrap();
    assert!(c.apply_oversteer_career().is_err());
    assert_eq!(before, serde_json::to_string(&c).unwrap());
}

#[test]
fn deferred_crew_and_spooking_commands_cannot_change_a_new_career() {
    let mut game = Game::new(content());
    let before = game.save_json().unwrap();
    assert!(game
        .command(GameCommand::Navigate {
            screen: GameScreen::Crew
        })
        .is_err());
    assert!(game
        .command(GameCommand::Recruit {
            driver: DriverDna::default()
        })
        .is_err());
    assert!(game
        .command(GameCommand::SpectatorCheer {
            racer: 1,
            positive: false
        })
        .is_err());
    assert_eq!(game.save_json().unwrap(), before);
    start(&mut game, "oversteer-0-circuit").unwrap();
    for _ in 0..480 {
        game.advance(
            1. / 60.,
            PlayerInput {
                throttle: 1.,
                ..Default::default()
            },
        );
    }
    assert!(game
        .frame_snapshot()
        .race
        .unwrap()
        .racers
        .iter()
        .all(|r| r.spook == 0.));
}

#[test]
fn first_tier_is_winnable_with_driving_inputs_and_persists_earned_promotion() {
    // Replaces the retired Eliminator/Obliterator career-win replays. Uses the
    // actual selected courses and normal physics/scoring, with no state injection.
    let mut content: GameContent = serde_json::from_str(
        &std::fs::read_to_string("../../godot/assets/game-content.json").unwrap(),
    )
    .unwrap();
    content.apply_oversteer_vehicle_corrections();
    content.apply_oversteer_career().unwrap();
    let mut game = Game::new(content.clone());
    game.command(GameCommand::SetDifficulty { level: 0 })
        .unwrap();
    game.command(GameCommand::BuyCar {
        car_id: "GT4_MAZD0012".into(),
    })
    .unwrap();
    for kind in ["circuit", "drift", "promotion"] {
        let drift = kind == "drift";
        game.command(GameCommand::SelectCar {
            car_id: if drift {
                "GT4_MAZD0012"
            } else {
                "GT4_HOND0018"
            }
            .into(),
        })
        .unwrap();
        start(&mut game, &format!("oversteer-0-{kind}")).unwrap();
        let mut input = PlayerInput::default();
        for tick in 0..60 * 600 {
            if !drift || tick % 12 == 0 {
                input = if drift {
                    game.scenario_drift_predictive_input()
                } else {
                    game.scenario_player_ai_input()
                };
            }
            game.advance(1. / 60., input);
            if game.frame_snapshot().screen == GameScreen::Results {
                break;
            }
        }
        let snapshot = game.frame_snapshot();
        let result = snapshot
            .result
            .expect("Race must settle within ten minutes");
        assert!(result.won, "{kind}: {result:?}");
        if drift {
            assert!(result.score >= 1000.);
        }
        assert!(snapshot.career.goal_progress[&format!("oversteer-0-{kind}-win")].complete);
        assert_eq!(snapshot.career.league, u8::from(kind == "promotion"));
        game.command(GameCommand::Continue).unwrap();
        let save = game.save_json().unwrap();
        game = Game::load_json(content.clone(), &save).unwrap();
        assert_eq!(save, game.save_json().unwrap());
    }
    assert_eq!(game.frame_snapshot().career.cash, 17000);
    assert_eq!(game.frame_snapshot().career.completed_events.len(), 3);
    start(&mut game, "oversteer-1-circuit").unwrap();
}

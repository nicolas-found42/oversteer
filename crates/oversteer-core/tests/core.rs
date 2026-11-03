use oversteer_core::*;
fn content() -> GameContent {
    GameContent {
        leagues: vec![],
        drivers: vec![],
        cars: (0..30)
            .map(|i| CarDefinition {
                id: format!("car{i}"),
                name: format!("Vehicle {i}"),
                price: 1000,
                ..Default::default()
            })
            .collect(),
        tracks: vec![TrackDefinition::default()],
        events: vec![EventDefinition {
            laps: 1,
            opponents: 2,
            ..Default::default()
        }],
    }
}
#[test]
fn native_prototype_currency_migrates_only_absent_fields_without_installing_parts() {
    let mut data = content();
    data.leagues.push(LeagueDefinition {
        goals: vec![
            GoalDefinition {
                id: "earned".into(),
                prot_unlock: true,
                ..Default::default()
            },
            GoalDefinition {
                id: "unfinished".into(),
                prot_unlock: true,
                ..Default::default()
            },
        ],
        ..Default::default()
    });
    let game = Game::new(data.clone());
    let mut old: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    old.career.league = 3;
    old.career.goal_progress.insert(
        "earned".into(),
        GoalProgress {
            value: 1.,
            complete: true,
        },
    );
    old.career.native_performance = None;
    let mut migrated =
        Game::load_json(data.clone(), &serde_json::to_string(&old).unwrap()).unwrap();
    let saved = migrated.save_json().unwrap();
    let state = migrated.frame_snapshot().career;
    let native = state.native_performance.unwrap();
    assert_eq!(native.prototype_tokens, 2);
    assert!(native.prototype_unlocks.is_empty());
    assert_eq!(native.ordinary_licenses.len(), 30);
    assert!(native
        .ordinary_licenses
        .iter()
        .all(|license| license.item == 0));
    assert!(state
        .garage
        .values()
        .all(|car| car.native_performance_parts.is_none()));
    assert_eq!(
        Game::load_json(data.clone(), &saved)
            .unwrap()
            .save_json()
            .unwrap(),
        saved
    );
    assert!(migrated
        .command(GameCommand::UnlockPrototype {
            league: 4,
            category: PrototypeCategory::Power
        })
        .is_err());
    migrated
        .command(GameCommand::UnlockPrototype {
            league: 3,
            category: PrototypeCategory::Nitrous,
        })
        .unwrap();
    assert!(migrated
        .command(GameCommand::UnlockPrototype {
            league: 3,
            category: PrototypeCategory::Nitrous
        })
        .is_err());
    let chosen = migrated.frame_snapshot().career.native_performance.unwrap();
    assert_eq!(chosen.prototype_tokens, 1);
    assert_eq!(
        chosen.prototype_unlocks,
        vec![(3, PrototypeCategory::Nitrous)]
    );
    let chosen_save = migrated.save_json().unwrap();
    assert_eq!(
        Game::load_json(data.clone(), &chosen_save)
            .unwrap()
            .save_json()
            .unwrap(),
        chosen_save
    );
    old.career.native_performance = Some(NativePerformanceCareer::default());
    let present = Game::load_json(data, &serde_json::to_string(&old).unwrap()).unwrap();
    assert_eq!(
        present
            .frame_snapshot()
            .career
            .native_performance
            .unwrap()
            .prototype_tokens,
        0
    );
}

#[test]
fn all_thirty_raw_endpoint_algorithms_match_independent_f32_fixtures() {
    let read = |path: &str| std::fs::read_to_string(format!("../../{path}")).unwrap();
    let production: GameContent = serde_json::from_str(&read("data/juiced2/content.json")).unwrap();
    let mapping: serde_json::Value = serde_json::from_str(&read(
        "artifacts/juiced2-build/native-performance/donor-mapping.json",
    ))
    .unwrap();
    let fixture: serde_json::Value = serde_json::from_str(&read(
        "artifacts/juiced2-build/native-performance/relative-endpoint-fixtures.json",
    ))
    .unwrap();
    let catalog = NativePerformanceCatalog::default();
    let rows = fixture["cars"].as_array().unwrap();
    assert_eq!(rows.len(), 30);
    for row in rows {
        let id = row["car_id"].as_str().unwrap();
        let baseline = &production
            .cars
            .iter()
            .find(|car| car.id == id)
            .unwrap()
            .handling;
        let raw = mapping["cars"]
            .as_array()
            .unwrap()
            .iter()
            .find(|car| car["car_id"] == id)
            .unwrap();
        let mut definition: NativePerformanceDefinition =
            serde_json::from_value(raw.clone()).unwrap();
        // This retained RAW counterpart fixture checks instruction arithmetic only,
        // not the separately audited ADR0007 gameplay capacity mapping.
        definition.authoritative_base.peak_bhp = definition.native_fields.stock_power;
        definition.authoritative_base.mass = definition.native_fields.stock_weight;
        definition.adapted_endpoints.maximum_power = definition.native_fields.max_power;
        definition.adapted_endpoints.minimum_mass = definition.native_fields.min_weight;
        let league = catalog.maximum_potential_league(&definition.native_fields);
        assert_eq!(
            u64::from(league),
            row["max_potential_league"].as_u64().unwrap()
        );
        let prototype = catalog.installed_package(league, 3).unwrap();
        for case in row["cases"].as_array().unwrap() {
            let parts = match case["case"].as_str().unwrap() {
                "stock" => [0; 3],
                "power_prototype" => [prototype, 0, 0],
                "weight_prototype" => [0, 0, prototype],
                "combined_prototype" => [prototype, 0, prototype],
                _ => unreachable!(),
            };
            let tuned = catalog
                .apply_relative(&definition, parts, baseline, false)
                .unwrap();
            let expected = &case["endpoints"];
            for (field, value) in [
                ("peak_torque", tuned.peak_torque),
                ("peak_torque_rpm", tuned.peak_torque_rpm),
                ("peak_bhp", tuned.peak_bhp),
                ("peak_bhp_rpm", tuned.peak_bhp_rpm),
                ("redline", tuned.redline),
                ("mass", tuned.mass),
            ] {
                let wanted = expected[field]["adapted_tuned"].as_f64().unwrap() as f32;
                assert_eq!(
                    value.to_bits(),
                    wanted.to_bits(),
                    "{id} {} {field}",
                    case["case"]
                );
            }
            assert_eq!(tuned.layout, baseline.layout);
            assert_eq!(tuned.gears, baseline.gears);
            assert_eq!(tuned.wheelbase, baseline.wheelbase);
            assert_eq!(tuned.body_length, baseline.body_length);
            assert_eq!(tuned.body_width, baseline.body_width);
            assert_eq!(tuned.body_height, baseline.body_height);
            assert_eq!(tuned.body_min_y, baseline.body_min_y);
            assert_eq!(
                tuned.nitrous_power_factor.to_bits(),
                (case["power_factor"].as_f64().unwrap() as f32).to_bits()
            );
            if parts == [0; 3] {
                assert_eq!(
                    serde_json::to_value(&tuned).unwrap(),
                    serde_json::to_value(baseline).unwrap()
                );
            }
            if parts[0] == 0 && parts[2] != 0 {
                assert_eq!(tuned.nitrous_power_factor, 1.);
                assert!(tuned.peak_bhp > baseline.peak_bhp);
            }
        }
        let handling_parts = [0, prototype, 0];
        let circuit = catalog
            .apply_relative(&definition, handling_parts, baseline, false)
            .unwrap();
        let drift = catalog
            .apply_relative(&definition, handling_parts, baseline, true)
            .unwrap();
        assert!(circuit.footbrake_mu > baseline.footbrake_mu);
        assert_eq!(drift.footbrake_mu, circuit.footbrake_mu);
        assert!(circuit.damping_ratio > baseline.damping_ratio);
        assert_eq!(drift.damping_ratio, circuit.damping_ratio);
        assert_eq!(circuit.rear_damping_ratio, baseline.rear_damping_ratio);
        assert_eq!(drift.tyre_mu, baseline.tyre_mu);
        assert_eq!(drift.rear_tyre_mu, baseline.rear_tyre_mu);
        assert!(circuit.tyre_mu > baseline.tyre_mu);
    }
}
#[test]
fn native_scheduler_strict_thresholds() {
    assert_eq!(substeps(0.05), (1, 0.05));
    assert_eq!(substeps(0.1), (2, 0.05));
    assert_eq!(substeps(1.), (3, 0.2 / 3.));
}
#[test]
fn steering_reversal_resets_and_slews() {
    assert_eq!(steering_slew(0.8, -1., 0.1, 3.), -0.3);
    assert_eq!(steering_slew(0.8, 0.2, 0.1, 3.), 0.2);
}
#[test]
fn source_torque_knots() {
    let h = Handling::default();
    assert!((torque_curve(&h, 1000.) - 0.7).abs() < 1e-6);
    assert!((torque_curve(&h, h.peak_torque_rpm) - 1.).abs() < 1e-6);
    assert!((torque_curve(&h, 1.12 * h.redline) + 0.1).abs() < 1e-5);
}
#[test]
fn source_curve_initialization_scans_peak() {
    let g = PhysicsGlobals::default();
    assert_eq!(g.response_curve.len(), 24);
    assert!(g.abs_threshold > 0.);
    assert!(g
        .response_curve
        .iter()
        .all(|p| p[1] <= curve(&g.response_curve, g.abs_threshold)));
}
#[test]
fn driving_finite_and_repeatable() {
    let h = Handling::default();
    let g = PhysicsGlobals::default();
    let mut a = VehicleState::default();
    let mut b = a.clone();
    for _ in 0..1200 {
        let u = PlayerInput {
            throttle: 1.,
            ..Default::default()
        };
        a.step(&h, &g, u, 1. / 120.);
        b.step(&h, &g, u, 1. / 120.);
    }
    assert_eq!(a.position, b.position);
    assert!(a.position.iter().all(|v| v.is_finite()));
    assert!(a.position[2] > 10., "{:?}", a);
    assert!(a.speed() > 3.);
}
#[test]
fn all_thirty_customizations_quick_race() {
    let mut g = Game::new(content());
    g.command(GameCommand::Navigate {
        screen: GameScreen::QuickRace,
    })
    .unwrap();
    for i in 0..30 {
        let id = format!("car{i}");
        g.command(GameCommand::SelectCar { car_id: id.clone() })
            .unwrap();
        g.command(GameCommand::Customize {
            car_id: id,
            customization: Customization {
                wheels: "five-spoke".into(),
                engine: 3,
                vinyls: vec![Vinyl::default()],
                ..Default::default()
            },
        })
        .unwrap();
        g.command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        assert_eq!(g.snapshot().race.unwrap().racers[0].customization.engine, 3);
        g.command(GameCommand::Navigate {
            screen: GameScreen::QuickRace,
        })
        .unwrap();
    }
}
#[test]
fn wager_settles_once_and_save_relaunch() {
    let c = content();
    let mut g = Game::new(c.clone());
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 1000,
        pink_slip: false,
    })
    .unwrap();
    assert_eq!(g.snapshot().career.cash, 24000);
    g.scenario_place_player([0., 0., 250.], [0.; 3], 1, 1)
        .unwrap();
    for _ in 0..400 {
        g.advance(1. / 60., PlayerInput::default());
    }
    let s = g.snapshot();
    assert_eq!(s.screen, GameScreen::Results);
    assert!(s.result.unwrap().won);
    assert_eq!(s.career.cash, 31000);
    for _ in 0..60 {
        g.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(g.snapshot().career.cash, 31000);
    let loaded = Game::load_json(c, &g.save_json().unwrap()).unwrap();
    assert_eq!(
        loaded.snapshot().career.completed_events,
        vec!["harbor-circuit"]
    );
    assert_eq!(loaded.snapshot().career.cash, 31000);
}
#[test]
fn pink_slip_last_car_is_protected() {
    let mut g = Game::new(content());
    assert!(g
        .command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: true,
            wager: 0,
            pink_slip: true
        })
        .is_err());
    g.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 0,
        pink_slip: true,
    })
    .unwrap();
}
#[test]
fn unknown_save_version_rejected() {
    let g = Game::new(content());
    let json = g
        .save_json()
        .unwrap()
        .replace("\"schema_version\": 1", "\"schema_version\": 2");
    assert!(Game::load_json(content(), &json).is_err());
}
#[test]
fn suspension_reacts_to_independent_3d_contacts() {
    let mut car = VehicleState::default();
    let h = Handling::default();
    let g = PhysicsGlobals::default();
    car.contacts[0].height = 0.1;
    car.contacts[2].height = 0.1;
    for _ in 0..60 {
        car.step(&h, &g, PlayerInput::default(), 1. / 120.);
    }
    assert!(car.position[1] > 0.01);
    assert!(car.orientation[2].abs() > 0.005);
    assert!(car.orientation.iter().all(|v| v.is_finite()));
}
#[test]
fn frame_rate_driving_is_stable() {
    for hz in [30, 60, 120] {
        let mut car = VehicleState::default();
        let p = Handling::default();
        let g = PhysicsGlobals::default();
        for i in 0..hz * 60 {
            car.step(
                &p,
                &g,
                PlayerInput {
                    throttle: 1.,
                    steering: if i > hz * 10 { 0.2 } else { 0. },
                    ..Default::default()
                },
                1. / hz as f32,
            );
            assert!(
                car.position
                    .iter()
                    .chain(car.velocity.iter())
                    .all(|x| x.is_finite()),
                "hz={hz},step={i}"
            );
        }
        assert!(car.speed() < 200.);
    }
}
#[test]
fn quick_customization_relaunch_includes_unowned_and_editor_navigation() {
    let c = content();
    let mut game = Game::new(c.clone());
    game.command(GameCommand::Navigate {
        screen: GameScreen::QuickRace,
    })
    .unwrap();
    for i in 0..30 {
        let id = format!("car{i}");
        game.command(GameCommand::SelectCar { car_id: id.clone() })
            .unwrap();
        game.command(GameCommand::Navigate {
            screen: GameScreen::Customization,
        })
        .unwrap();
        game.command(GameCommand::Customize {
            car_id: id,
            customization: Customization {
                paint: [0.1, 0.2, 0.3, 1.],
                wheels: "mesh".into(),
                vinyls: vec![Vinyl {
                    rotation: 0.8,
                    ..Default::default()
                }],
                ..Default::default()
            },
        })
        .unwrap();
    }
    let mut loaded = Game::load_json(c, &game.save_json().unwrap()).unwrap();
    loaded
        .command(GameCommand::Navigate {
            screen: GameScreen::QuickRace,
        })
        .unwrap();
    for i in 0..30 {
        loaded
            .command(GameCommand::SelectCar {
                car_id: format!("car{i}"),
            })
            .unwrap();
        let s = loaded.frame_snapshot();
        assert_eq!(s.selected_customization.wheels, "mesh");
        assert_eq!(s.selected_customization.vinyls[0].rotation, 0.8);
        assert!(s.tracks.is_empty());
    }
}
#[test]
fn accepted_content_all_cars_drive_with_native_elevated_routes() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string(path).expect("prepared game content"))
            .unwrap();
    assert_eq!(content.cars.len(), 30);
    assert_eq!(content.tracks.len(), 33);
    for car in &content.cars {
        let mut g = Game::new(content.clone());
        g.command(GameCommand::SelectCar {
            car_id: car.id.clone(),
        })
        .unwrap();
        g.command(GameCommand::StartRace {
            event_id: content.events[0].id.clone(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..600 {
            g.advance(
                1. / 60.,
                PlayerInput {
                    throttle: 1.,
                    ..Default::default()
                },
            );
            let p = &g.frame_snapshot().race.unwrap().racers[0];
            assert!(
                p.position
                    .iter()
                    .chain(p.rotation.iter())
                    .all(|x| x.is_finite()),
                "{} pose invalid",
                car.id
            );
            assert!(p.speed_kph.is_finite(), "{} speed invalid", car.id);
        }
    }
}
#[test]
fn ai_can_drive_a_complete_circuit_without_teleporting() {
    let mut c = content();
    c.events[0].opponents = 0;
    let mut g = Game::new(c);
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 1000,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..60 * 360 {
        let input = g.scenario_player_ai_input();
        g.advance(1. / 60., input);
        if g.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let s = g.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results, "{:?}", s.race);
    assert!(s.result.unwrap().won);
}

#[test]
fn ai_drives_smooth_circuit_without_teleporting() {
    let mut c = content();
    c.events[0].opponents = 0;
    c.tracks[0].points = (0..80)
        .map(|i| {
            let a = i as f32 * std::f32::consts::TAU / 80.;
            [80. * (1. - a.cos()), 0., 80. * a.sin()]
        })
        .collect();
    let mut g = Game::new(c);
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..60 * 240 {
        let input = g.scenario_player_ai_input();
        g.advance(1. / 60., input);
        if g.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let s = g.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results, "{:?}", s.race);
    assert!(s.result.unwrap().won);
}
#[test]
fn native_course_ai_finishes_without_pose_injection() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let mut content: GameContent =
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    for track in content.tracks.clone().into_iter() {
        content.events = vec![EventDefinition {
            id: "scenario".into(),
            track_id: track.id.clone(),
            opponents: 0,
            laps: 1,
            ..Default::default()
        }];
        let mut g = Game::new(content.clone());
        g.command(GameCommand::StartRace {
            event_id: "scenario".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..60 * 3600 {
            let input = g.scenario_player_ai_input();
            g.advance(1. / 60., input);
            if g.frame_snapshot().screen == GameScreen::Results {
                break;
            }
        }
        let s = g.frame_snapshot();
        assert_eq!(
            s.screen,
            GameScreen::Results,
            "route {}: {:?}",
            track.id,
            s.race
        );
        assert!(s.result.unwrap().won, "{}", track.id);
    }
}
#[test]
fn all_donor_layouts_complete_a_native_course_with_driving_inputs() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    for car in &content.cars {
        let mut c = content.clone();
        c.events = vec![EventDefinition {
            id: "scenario".into(),
            track_id: c.tracks[0].id.clone(),
            opponents: 0,
            laps: 1,
            ..Default::default()
        }];
        let mut g = Game::new(c);
        g.command(GameCommand::SelectCar {
            car_id: car.id.clone(),
        })
        .unwrap();
        g.command(GameCommand::StartRace {
            event_id: "scenario".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..60 * 3600 {
            let input = g.scenario_player_ai_input();
            g.advance(1. / 60., input);
            if g.frame_snapshot().screen == GameScreen::Results {
                break;
            }
        }
        let s = g.frame_snapshot();
        assert_eq!(s.screen, GameScreen::Results, "{} {:?}", car.id, s.race);
        assert!(s.result.unwrap().won, "{}", car.id);
    }
}
#[test]
fn drift_scores_motion_and_challenge_settles_without_cash_in_quick_race() {
    let mut c = content();
    c.events[0].mode = RaceMode::Drift;
    c.events[0].opponents = 0;
    c.events[0].target = 1.;
    let mut g = Game::new(c);
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: false,
        wager: 9000,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..190 {
        g.advance(1. / 60., PlayerInput::default());
    }
    g.scenario_place_player([0., 0., 80.], [50., 0., 50.], 0, 1)
        .unwrap();
    for _ in 0..11 {
        g.advance(1. / 60., PlayerInput::default());
    }
    assert!(g.frame_snapshot().race.unwrap().racers[0].drift_score > 0.);
    g.scenario_place_player([0., 0., 250.], [15., 0., 20.], 1, 1)
        .unwrap();
    g.advance(1. / 60., PlayerInput::default());
    let s = g.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results);
    assert!(s.result.unwrap().won);
    assert_eq!(s.career.cash, 25000);
}
#[test]
fn pink_slip_loss_transfers_selected_car_and_restart_forfeits_escrow() {
    let mut c = content();
    c.events[0].mode = RaceMode::TimeAttack;
    c.events[0].target = 0.1;
    c.events[0].opponents = 1;
    let mut g = Game::new(c);
    g.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    g.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: true,
        wager: 1000,
        pink_slip: true,
    })
    .unwrap();
    g.command(GameCommand::Restart).unwrap();
    assert_eq!(g.frame_snapshot().career.cash, 22000);
    for _ in 0..60 * 40 {
        g.advance(1. / 60., PlayerInput::default());
    }
    let s = g.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results);
    assert!(!s.result.unwrap().won);
    assert_eq!(s.career.garage.len(), 1);
    assert!(!s.career.garage.contains_key("car1"));
    assert_eq!(s.selected_car, "car0");
    assert_eq!(s.career.cash, 22000);
}
#[test]
fn reverse_drives_backwards_and_brakes() {
    let p = Handling::default();
    let g = PhysicsGlobals::recovered_script_settings();
    let mut car = VehicleState::default();
    for _ in 0..600 {
        car.step(
            &p,
            &g,
            PlayerInput {
                throttle: 0.5,
                reverse: true,
                ..Default::default()
            },
            1. / 60.,
        );
    }
    assert!(car.position[2] < -5., "{:?}", car);
    assert!(car.wheel_omega.iter().all(|v| *v <= 0.));
    let speed = car.speed();
    for _ in 0..600 {
        car.step(
            &p,
            &g,
            PlayerInput {
                brake: 1.,
                reverse: true,
                ..Default::default()
            },
            1. / 60.,
        );
    }
    assert!(car.speed() < speed * 0.5, "{} -> {}", speed, car.speed());
}
#[test]
fn career_unlocks_leagues_and_reaches_final_completion() {
    let mut c = content();
    c.events = (0..3)
        .map(|league| EventDefinition {
            id: format!("league-{league}"),
            league,
            opponents: 0,
            laps: 1,
            ..Default::default()
        })
        .collect();
    let mut game = Game::new(c.clone());
    assert!(game
        .command(GameCommand::StartRace {
            event_id: "league-1".into(),
            career: true,
            wager: 0,
            pink_slip: false
        })
        .is_err());
    for league in 0..3 {
        game.command(GameCommand::StartRace {
            event_id: format!("league-{league}"),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        game.scenario_place_player([0., 0., 250.], [0.; 3], 1, 1)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        assert!(game.frame_snapshot().result.unwrap().won);
        game.command(GameCommand::Continue).unwrap();
        let save = game.save_json().unwrap();
        game = Game::load_json(c.clone(), &save).unwrap();
        assert_eq!(
            game.frame_snapshot().career.completed_events.len(),
            league as usize + 1
        );
    }
    game.command(GameCommand::Continue).unwrap();
    assert_eq!(game.frame_snapshot().screen, GameScreen::Complete);
}
#[test]
fn recovered_wheel_inertia_is_independent_of_chassis_mass() {
    let g = PhysicsGlobals::default();
    assert!((g.wheel_inertia() - 1.094).abs() < 0.003);
    let mut changed = g.clone();
    changed.wheel_rim_inches = 20.;
    assert!(changed.wheel_inertia() > g.wheel_inertia());
}
#[test]
fn chassis_contacts_cover_bumpers_and_allow_bridges() {
    let half = [1., 2.2];
    let a = [0., 0., 0.];
    let b = [0., 0., 3.5];
    let push = chassis_overlap(a, 0., half, b, 0., half).unwrap();
    assert!((push[2] + 0.9).abs() < 1e-5);
    assert!(chassis_overlap([push[0], 0., push[2]], 0., half, b, 0., half).is_none());
    assert!(chassis_overlap(a, 0., half, [0., 5., 0.], 0., half).is_none());
    assert!(
        chassis_overlap(a, 0., half, [2., 0., 1.], std::f32::consts::FRAC_PI_2, half).is_some()
    );
}
#[test]
fn six_car_native_race_contacts_preserve_playable_completion() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let mut c: GameContent = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    c.events[0].laps = 1;
    c.events[0].stages.clear();
    c.events[0].mode = RaceMode::Circuit;
    c.events[0].opponents = 5;
    let id = c.events[0].id.clone();
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..60 * 3600 {
        let u = game.scenario_player_ai_input();
        game.advance(1. / 60., u);
        if game.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let s = game.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results, "{:?}", s.race);
    assert!(s.race.unwrap().racers[0].finished);
}
#[test]
fn native_drift_equation_banks_and_preserves_collision_rules() {
    let mut state = NativeDriftState::default();
    state.duration = 2.;
    state.points = 1000;
    state.accumulate(30., 20., 0.05, 1., 1.);
    assert_eq!(state.points, 1076);
    state.points = 1_000_001;
    state.accumulate(30., 20., 0.05, 1., 1.);
    assert_eq!(state.points, 1_001_126);
    state.collide(0., false);
    assert_eq!(state.points, 0);
    assert_eq!(state.banked, 0);
    assert_eq!(state.lost, 1_001_126);
    state.recovery = 1.;
    state.points = 10_000;
    state.collide(0., true);
    assert_eq!(state.banked, 10_000);
    assert_eq!(state.points, 0);
}
#[test]
fn recovered_drift_equation_exposes_native_clock_cadence_dependence() {
    let totals: Vec<_> = [30, 60, 120]
        .into_iter()
        .map(|hz| {
            let mut s = NativeDriftState::default();
            for _ in 0..hz * 20 {
                s.advance(30., 40f32.to_radians(), 1. / hz as f32, false, 1., 1.);
            }
            s.total() as f32
        })
        .collect();
    assert!(totals[1] > 10_000.);
    assert!((1.95..2.05).contains(&(totals[0] / totals[1])));
    assert!((0.45..0.55).contains(&(totals[2] / totals[1])));
}
#[test]
fn avatar_customization_roundtrips_and_podium_requires_result() {
    let c = content();
    let mut game = Game::new(c.clone());
    assert!(game.command(GameCommand::ShowPodium).is_err());
    let profile = PlayerProfile {
        native_components: std::collections::BTreeMap::from([("top".into(), "MHoodedtop".into())]),
        native_attributes: std::collections::BTreeMap::from([("FaceFlat".into(), 123.)]),
        name: "Test Driver".into(),
        preset: "Char04".into(),
        gender: "F".into(),
        top: "jacket".into(),
        accessories: vec!["earrings".into()],
        ..Default::default()
    };
    game.command(GameCommand::CustomizeAvatar {
        profile: profile.clone(),
    })
    .unwrap();
    let loaded = Game::load_json(c, &game.save_json().unwrap()).unwrap();
    assert_eq!(loaded.frame_snapshot().profile, profile);
    let legacy: PlayerProfile = serde_json::from_str(r#"{"name":"Legacy"}"#).unwrap();
    assert!(legacy.native_components.is_empty() && legacy.native_attributes.is_empty());
}
#[test]
fn paid_garage_cart_previews_removes_checks_out_and_persists() {
    let c = content();
    let mut game = Game::new(c.clone());
    game.command(GameCommand::Navigate {
        screen: GameScreen::Garage,
    })
    .unwrap();
    let custom = Customization {
        engine: 2,
        wheels: "mesh".into(),
        plate_text: "JUICED2".into(),
        wheel_paint: [0.8, 0.1, 0.1, 1.],
        ..Default::default()
    };
    let quoted = game.quote_customization(&custom);
    assert_eq!(quoted.len(), 4);
    assert!(game.frame_snapshot().cart.is_empty());
    assert_eq!(game.frame_snapshot().career.cash, 25000);
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization: custom,
    })
    .unwrap();
    let s = game.frame_snapshot();
    assert_eq!(s.career.cash, 25000);
    assert_eq!(s.career.garage["car0"].engine, 0);
    assert_eq!(s.selected_customization.engine, 2);
    assert_eq!(s.cart.len(), 4);
    assert_eq!(s.cart, quoted);
    let unsaved = Game::load_json(c.clone(), &game.save_json().unwrap()).unwrap();
    assert!(unsaved.frame_snapshot().cart.is_empty());
    assert_eq!(
        unsaved.frame_snapshot().career.garage["car0"].wheels,
        "stock"
    );
    let engine = s
        .cart
        .iter()
        .find(|i| i.field == "engine")
        .unwrap()
        .id
        .clone();
    game.command(GameCommand::RemoveCartItem { item_id: engine })
        .unwrap();
    assert_eq!(game.frame_snapshot().selected_customization.engine, 0);
    game.command(GameCommand::Checkout).unwrap();
    let loaded = Game::load_json(c, &game.save_json().unwrap()).unwrap();
    let s = loaded.frame_snapshot();
    assert_eq!(s.career.cash, 23500);
    assert_eq!(s.career.garage["car0"].wheels, "mesh");
    assert_eq!(s.career.garage["car0"].plate_text, "JUICED2");
    assert_eq!(s.career.vehicle_history["car0"].total_spent, 1500);
    assert_eq!(
        s.career.transactions.last().unwrap().kind,
        TransactionKind::Customization
    );
}
#[test]
fn checkout_is_atomic_and_owned_parts_can_be_refitted_without_repurchase() {
    let mut c = content();
    c.cars[1].price = 2000;
    let mut game = Game::new(c);
    game.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    for id in ["car0", "car1"] {
        game.command(GameCommand::Customize {
            car_id: id.into(),
            customization: Customization {
                engine: 3,
                transmission: 3,
                suspension: 3,
                tyres: 3,
                nitrous: 3,
                ..Default::default()
            },
        })
        .unwrap();
    }
    assert!(game.command(GameCommand::Checkout).is_err());
    let s = game.frame_snapshot();
    assert_eq!(s.career.cash, 23000);
    assert_eq!(s.career.garage["car0"].engine, 0);
    assert_eq!(s.career.garage["car1"].engine, 0);
    game.command(GameCommand::DiscardCart {
        car_id: Some("car1".into()),
    })
    .unwrap();
    game.command(GameCommand::Checkout).unwrap();
    assert_eq!(game.frame_snapshot().career.cash, 11000);
    for level in [1, 3] {
        game.command(GameCommand::Customize {
            car_id: "car0".into(),
            customization: Customization {
                engine: level,
                transmission: 3,
                suspension: 3,
                tyres: 3,
                nitrous: 3,
                ..Default::default()
            },
        })
        .unwrap();
        assert!(game.frame_snapshot().cart.iter().all(|i| i.cost == 0));
        game.command(GameCommand::Checkout).unwrap();
    }
    assert_eq!(game.frame_snapshot().career.cash, 11000);
}
#[test]
fn native_eight_driver_tournament_uses_three_duels_and_actual_stage_path() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let c: GameContent = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    let event = c
        .events
        .iter()
        .find(|e| e.id == "native_ca32970d_021")
        .unwrap()
        .clone();
    assert_eq!(event.stages.len(), 7);
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: event.id.clone(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for (round, (stage_index, rival)) in [
        (0, "Tyrone Albercete"),
        (4, "Leon Tyrrell"),
        (6, "Keiko Miyama"),
    ]
    .into_iter()
    .enumerate()
    {
        let snap = game.frame_snapshot().race.unwrap();
        assert_eq!(snap.round, round as u32 + 1);
        assert_eq!(snap.total_rounds, 3);
        assert_eq!(snap.racers.len(), 2);
        assert_eq!(snap.track_id, event.stages[stage_index].track_id);
        assert_eq!(snap.racers[1].name, rival);
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        let points = game
            .content
            .tracks
            .iter()
            .find(|t| t.id == snap.track_id)
            .unwrap()
            .points
            .clone();
        game.scenario_place_player(points[1], [0.; 3], snap.laps, 1)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        let snap = game.frame_snapshot();
        if round < 2 {
            assert_eq!(snap.screen, GameScreen::RoundResults);
            assert!(!snap.result.unwrap().is_final);
            game.command(GameCommand::Continue).unwrap();
        } else {
            assert_eq!(snap.screen, GameScreen::Results);
            assert!(snap.result.unwrap().won);
        }
    }
}
#[test]
fn obliterator_requires_target_each_lap_instead_of_finishing_at_first_target() {
    let mut c = content();
    c.events[0].mode = RaceMode::DriftObliterator;
    c.events[0].target = 1.;
    c.events[0].laps = 2;
    c.events[0].opponents = 0;
    c.events[0].lives = 1;
    c.tracks[0].road_width = 100.;
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_player([0., 0., 80.], [50., 0., 50.], 0, 1)
        .unwrap();
    for _ in 0..12 {
        game.advance(1. / 30., PlayerInput::default());
    }
    let s = game.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Race);
    assert!(s.race.unwrap().racers[0].drift_score > 1.);
    game.scenario_place_player([0., 0., 0.], [0.; 3], 0, 0)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let r = game.frame_snapshot().race.unwrap();
    assert_eq!(r.racers[0].lap, 1);
    assert_eq!(r.racers[0].drift_score, 0.);
    assert!(!r.racers[0].eliminated);
    game.scenario_place_player([0., 0., 0.], [0.; 3], 1, 0)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let s = game.frame_snapshot();
    assert_eq!(s.screen, GameScreen::Results);
    assert!(!s.result.unwrap().won);
    assert!(s.race.unwrap().racers[0].eliminated);
}
#[test]
fn drift_king_uses_native_countdown_and_does_not_end_on_lap_completion() {
    let mut c = content();
    c.events[0].mode = RaceMode::DriftKing;
    c.events[0].target = 1.;
    c.events[0].laps = 1;
    c.events[0].opponents = 0;
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: "harbor-circuit".into(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_player([0., 0., 250.], [0.; 3], 1, 1)
        .unwrap();
    game.advance(1. / 60., PlayerInput::default());
    assert_eq!(game.frame_snapshot().screen, GameScreen::Race);
    for _ in 0..60 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(game.frame_snapshot().screen, GameScreen::Results);
}

#[test]
fn recovered_body_drag_is_quadratic_and_opposes_full_velocity() {
    let drag = body_drag([3., 4., 0.], 0.4, 1.);
    assert!((drag[0] + 6.).abs() < 1e-5);
    assert!((drag[1] + 8.).abs() < 1e-5);
    assert_eq!(drag[2], 0.);
    let doubled = body_drag([6., 8., 0.], 0.4, 1.);
    assert!((doubled[0] / drag[0] - 4.).abs() < 1e-5);
    assert_eq!(body_drag([0.; 3], 0.4, 1.), [0.; 3]);
}

#[test]
fn team_winner_receives_first_prize_when_player_finishes_second() {
    let mut c = content();
    c.events[0].mode = RaceMode::TeamRace;
    c.events[0].prizes = vec![16000];
    c.events[0].contestants = vec![
        EventContestant {
            tag: "Player0".into(),
            team: 0,
            ..Default::default()
        },
        EventContestant {
            tag: "Char01".into(),
            team: 0,
            ..Default::default()
        },
        EventContestant {
            tag: "Char02".into(),
            team: 1,
            ..Default::default()
        },
    ];
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_racer(1, point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let result = game.frame_snapshot().result.unwrap();
    assert!(result.won);
    assert_eq!(result.position, 1);
    assert_eq!(result.reward, 16000);
}

#[test]
fn native_goal_count_opens_qualifier_then_promotes_without_clearing_all_events() {
    let mut c = content();
    let base = c.events[0].clone();
    c.events[0].id = "optional".into();
    c.events[0].opponents = 0;
    c.events.push(EventDefinition {
        id: "promotion".into(),
        qualifier: true,
        opponents: 0,
        ..base.clone()
    });
    c.events.push(EventDefinition {
        id: "remaining".into(),
        ..base.clone()
    });
    c.events.push(EventDefinition {
        id: "nextleague".into(),
        league: 1,
        ..base
    });
    c.leagues.push(LeagueDefinition {
        league: 0,
        name: "Rookie".into(),
        optional_goals_required: 1,
        goals: vec![
            GoalDefinition {
                id: "rookie-win".into(),
                kind: "WinRace".into(),
                ..Default::default()
            },
            GoalDefinition {
                id: "rookie-promotion".into(),
                qualifier: true,
                kind: "WinRace".into(),
                ..Default::default()
            },
        ],
    });
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c.clone());
    let start = |id: &str| GameCommand::StartRace {
        event_id: id.into(),
        career: true,
        wager: 0,
        pink_slip: false,
    };
    assert!(game
        .command(start("promotion"))
        .unwrap_err()
        .contains("league goals"));
    game.command(start("optional")).unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    assert!(game.league_progress().promotion_open);
    assert_eq!(game.frame_snapshot().career.league, 0);
    let json = game.save_json().unwrap();
    let mut game = Game::load_json(c, &json).unwrap();
    assert!(game.league_progress().promotion_open);
    game.command(start("promotion")).unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let career = game.frame_snapshot().career;
    assert_eq!(career.league, 1);
    assert!(!career.completed_events.contains(&"remaining".into()));
}

#[test]
fn speed_challenge_uses_si_target_and_waits_for_full_lap() {
    let mut c = content();
    c.events[0].mode = RaceMode::SpeedChallenge;
    c.events[0].target = 5.;
    c.events[0].opponents = 0;
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    for drops_below in [false, true] {
        let mut game = Game::new(c.clone());
        game.command(GameCommand::StartRace {
            event_id: id.clone(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        // This is 21.6km/h, above the native5m/s target.
        game.scenario_place_player([0., 0.55, 0.], [0., 0., 6.], 0, 1)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        for _ in 0..360 {
            game.scenario_place_player([0., 0.55, 0.], [0., 0., 6.], 0, 1)
                .unwrap();
            game.advance(1. / 60., PlayerInput::default());
        }
        assert_eq!(game.frame_snapshot().screen, GameScreen::Race);
        if drops_below {
            game.scenario_place_player([0., 0.55, 0.], [0.; 3], 0, 1)
                .unwrap();
            game.advance(1. / 60., PlayerInput::default());
        }
        if !drops_below {
            game.scenario_place_player(point, [0., 0., 6.], 1, 1)
                .unwrap();
            game.advance(1. / 60., PlayerInput::default());
        }
        assert_eq!(game.frame_snapshot().result.unwrap().won, !drops_below);
    }
}

#[test]
fn native_speed_monitor_preserves_deadline_and_equality_boundaries() {
    use SpeedChallengeState::*;
    assert_eq!(Pending.update(10., 10., 9.), Pending);
    assert_eq!(Pending.update(10.001, 10., 10.), Armed);
    assert_eq!(Pending.update(20., 10., 10.001), FailedReach);
    assert_eq!(Armed.update(10., 10., 30.), Armed);
    assert_eq!(Armed.update(9.999, 10., 30.), FailedMaintain);
    assert_eq!(FailedMaintain.update(20., 10., 31.), FailedMaintain);
}

#[test]
fn spectator_bets_lock_dynamic_odds_escrow_settle_once_and_unlock_native_goal() {
    let mut c = content();
    c.leagues.push(LeagueDefinition {
        league: 0,
        optional_goals_required: 1,
        goals: vec![GoalDefinition {
            id: "spectator-win".into(),
            kind: "WinSpectatorBet".into(),
            args: vec![serde_json::json!(1)],
            ..Default::default()
        }],
        ..Default::default()
    });
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c.clone());
    let initial = game.frame_snapshot().career.cash;
    game.command(GameCommand::StartSpectating { event_id: id })
        .unwrap();
    let race = game.frame_snapshot().race.unwrap();
    assert!(race.spectating);
    assert!(race.racers.iter().all(|r| !r.is_player));
    game.command(GameCommand::PlaceSpectatorBet {
        racer: 1,
        amount: 100,
    })
    .unwrap();
    let odds = game.frame_snapshot().race.unwrap().spectator_bets[0].odds;
    assert_eq!(game.frame_snapshot().career.cash, initial - 100);
    assert!(game.command(GameCommand::Restart).is_err());
    assert!(game.command(GameCommand::ResetCar).is_err());
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_racer(1, point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let snap = game.frame_snapshot();
    let payout = (100. * odds as f64).floor() as i64;
    assert_eq!(snap.career.cash, initial - 100 + payout);
    assert_eq!(snap.race.unwrap().spectator_bets[0].payout, payout);
    assert!(snap.league_progress.promotion_open);
    assert!(game
        .command(GameCommand::PlaceSpectatorBet {
            racer: 1,
            amount: 100
        })
        .is_err());
    for _ in 0..10 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(game.frame_snapshot().career.cash, initial - 100 + payout);
    let loaded = Game::load_json(c, &game.save_json().unwrap()).unwrap();
    assert_eq!(loaded.frame_snapshot().career.cash, initial - 100 + payout);
    assert!(loaded.league_progress().promotion_open);
}

#[test]
fn native_beat_car_head_start_delays_rival_and_adapted_roster_can_win() {
    let mut c = content();
    c.events[0].mode = RaceMode::BeatCar;
    c.events[0].target = 7.;
    c.events[0].target_car = Some("UNAVAILABLE_NATIVE_CAR".into());
    c.events[0].opponents = 1;
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    let origin = game.frame_snapshot().race.unwrap().racers[1].position;
    for _ in 0..300 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(
        game.frame_snapshot().race.unwrap().racers[1].position,
        origin
    );
    for _ in 0..180 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_ne!(
        game.frame_snapshot().race.unwrap().racers[1].position,
        origin
    );
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    assert!(game.frame_snapshot().result.unwrap().won);
}

#[test]
fn native_lms_eliminates_on_barrier() {
    for mode in [RaceMode::LastManStanding] {
        let mut c = content();
        c.events[0].mode = mode;
        c.events[0].laps = 4;
        let id = c.events[0].id.clone();
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: id,
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        assert!(game
            .frame_snapshot()
            .race
            .unwrap()
            .racers
            .iter()
            .all(|r| !r.eliminated));
        {
            game.scenario_place_player([100., 0.55, 100.], [0.; 3], 0, 1)
                .unwrap();
            game.advance(1. / 60., PlayerInput::default());
            assert!(game.frame_snapshot().race.unwrap().racers[0].eliminated);
            assert!(!game.frame_snapshot().result.unwrap().won);
        }
    }
}

#[test]
fn selected_driver_bet_can_win_and_complete_named_goal_without_winning_race() {
    let mut c = content();
    c.events[0].contestants = vec![
        EventContestant {
            tag: "Player0".into(),
            ..Default::default()
        },
        EventContestant {
            tag: "Char01".into(),
            ..Default::default()
        },
        EventContestant {
            tag: "Char03".into(),
            ..Default::default()
        },
    ];
    c.leagues.push(LeagueDefinition {
        league: 0,
        optional_goals_required: 1,
        goals: vec![GoalDefinition {
            id: "named-bet".into(),
            kind: "WinDriverBet".into(),
            args: vec![serde_json::json!(1000), serde_json::json!("Char03")],
            ..Default::default()
        }],
        ..Default::default()
    });
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c);
    let initial = game.frame_snapshot().career.cash;
    game.command(GameCommand::StartRace {
        event_id: id,
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    for _ in 0..300 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(game.frame_snapshot().race.unwrap().countdown, 3.);
    game.command(GameCommand::PlaceDriverBet {
        racer: 2,
        amount: 1000,
    })
    .unwrap();
    assert!(game
        .command(GameCommand::PlaceDriverBet {
            racer: 1,
            amount: 1000
        })
        .is_err());
    game.command(GameCommand::LaunchRace).unwrap();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_racer(1, point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let snap = game.frame_snapshot();
    assert!(!snap.result.as_ref().unwrap().won);
    assert_eq!(snap.result.unwrap().wager, 1000);
    assert_eq!(snap.career.cash, initial + 1000);
    assert!(snap.league_progress.promotion_open);
}

#[test]
fn finish_margin_goals_observe_rival_finish_or_a_proven_time_lower_bound() {
    for (kind, target, rival_finishes) in [("CloseFinish", 1., true), ("VictoryMargin", 2., false)]
    {
        let mut c = content();
        c.events[0].opponents = 1;
        c.leagues.push(LeagueDefinition {
            league: 0,
            optional_goals_required: 1,
            goals: vec![GoalDefinition {
                id: "margin".into(),
                kind: kind.into(),
                args: vec![serde_json::json!(target)],
                ..Default::default()
            }],
            ..Default::default()
        });
        let id = c.events[0].id.clone();
        let point = c.tracks[0].points[1];
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: id,
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
        game.advance(1. / 60., PlayerInput::default());
        assert_eq!(game.frame_snapshot().screen, GameScreen::Race);
        for _ in 0..25 {
            game.advance(1. / 60., PlayerInput::default());
        }
        if rival_finishes {
            game.scenario_place_racer(1, point, [0.; 3], 1, 1).unwrap();
            game.advance(1. / 60., PlayerInput::default());
        } else {
            for _ in 0..120 {
                game.advance(1. / 60., PlayerInput::default());
            }
        }
        assert!(game.frame_snapshot().result.unwrap().won);
        assert!(game.league_progress().promotion_open, "{kind}");
    }
}

#[test]
fn native_london_traffic_does_not_leave_interpenetrating_chassis_after_a_frame() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let mut c: GameContent = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    let track_id = c
        .tracks
        .iter()
        .find(|t| t.id == "london_circuit1")
        .unwrap()
        .id
        .clone();
    c.events = vec![EventDefinition {
        id: "traffic".into(),
        track_id,
        opponents: 6,
        laps: 3,
        ..Default::default()
    }];
    let cars = c.cars.clone();
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: "traffic".into(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    let mut deepest = 0f32;
    for _ in 0..600 {
        game.advance(
            1. / 60.,
            PlayerInput {
                throttle: 0.5,
                ..Default::default()
            },
        );
        let race = game.frame_snapshot().race.unwrap();
        for (i, a) in race.racers.iter().enumerate() {
            for b in race.racers.iter().skip(i + 1) {
                let dimensions = |id: &str| {
                    let c = cars.iter().find(|c| c.id == id).unwrap();
                    [c.width_m / 2., c.length_m / 2.]
                };
                let yaw = |q: [f32; 4]| 2. * q[1].atan2(q[3]);
                if let Some(push) = chassis_overlap(
                    a.position,
                    yaw(a.rotation),
                    dimensions(&a.car_id),
                    b.position,
                    yaw(b.rotation),
                    dimensions(&b.car_id),
                ) {
                    deepest = deepest.max((push[0] * push[0] + push[2] * push[2]).sqrt());
                }
            }
        }
    }
    assert!(deepest < 0.05, "post-frame chassis penetration {deepest}m");
}

#[test]
fn legal_drift_inputs_initiate_sustain_and_bank_on_native_course_for_each_layout() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let original: GameContent =
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
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
            id: "legal-drift".into(),
            track_id: "alps_drift1_drift1".into(),
            mode: RaceMode::DriftEndurance,
            target: 30.,
            opponents: 0,
            ..Default::default()
        }];
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: "legal-drift".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        let mut peak = 0f32;
        for _ in 0..12000 {
            let input = game.scenario_player_ai_input();
            game.advance(1. / 60., input);
            let snap = game.frame_snapshot();
            let race = snap.race.unwrap();
            peak = peak.max(race.racers[0].chain_score);
            if snap.screen == GameScreen::Results {
                break;
            }
        }
        let snap = game.frame_snapshot();
        assert!(
            peak >= 30.,
            "{} {:?}: legal inputs never sustained a scoring drift; peak{peak}",
            car.id,
            layout
        );
        assert!(
            snap.result.as_ref().map(|r| r.won).unwrap_or(false),
            "{} failed to bank actual drift: {:?}",
            car.id,
            snap.result
        );
    }
}

#[test]
fn native_open_differential_splits_and_coupled_stage_constraints() {
    let split = differential_split(2., 6., 0.5, 10.);
    assert!((split.0[0] - 7.5).abs() < 1e-6 && (split.0[1] - 12.5).abs() < 1e-6);
    assert!((split.1[0] - 0.75).abs() < 1e-6 && (split.1[1] - 1.25).abs() < 1e-6);
    assert_eq!(differential_split(2., 6., 0., 10.), ([10., 10.], [1., 1.]));
    for layout in [DriveLayout::Fwd, DriveLayout::Rwd, DriveLayout::Awd] {
        let p = Handling {
            layout,
            ..Default::default()
        };
        let mut v = VehicleState::default();
        let g = PhysicsGlobals::recovered_script_settings();
        let mut observed = false;
        for _ in 0..180 {
            v.step(
                &p,
                &g,
                PlayerInput {
                    throttle: 1.,
                    ..Default::default()
                },
                1. / 60.,
            );
            if v.clutch_engaged {
                observed = true;
                let average = match layout {
                    DriveLayout::Fwd => (v.wheel_omega[0] + v.wheel_omega[1]) * 0.5,
                    DriveLayout::Rwd => (v.wheel_omega[2] + v.wheel_omega[3]) * 0.5,
                    DriveLayout::Awd => v.wheel_omega.iter().sum::<f32>() * 0.25,
                };
                let target = v.engine_omega / (p.gears[v.gear - 1] * p.final_drive);
                assert!((average - target).abs() < 1e-3);
            }
        }
        assert!(observed);
        v.step(
            &p,
            &g,
            PlayerInput {
                throttle: 1.,
                handbrake: 1.,
                ..Default::default()
            },
            1. / 60.,
        );
        assert!(!v.clutch_engaged);
    }
}

#[test]
fn native_wheel_reaction_stops_at_rolling_and_locked_targets() {
    assert_eq!(wheel_reaction(100., -20., 0., 10., 0.1, 1.), 0.);
    // A strong brake cannot reverse a forward wheel in one outer step.
    assert!((wheel_reaction(100., 0., 5., 10., 0.1, 1.) + 50.).abs() < 1e-6);
    // Contact reaction similarly stops at the rolling velocity.
    assert!((wheel_reaction(0., 100., 5., 8., 0.1, 1.) - 30.).abs() < 1e-5);
}

#[test]
fn game_clock_keeps_legal_drift_driving_and_settlement_identical_at_30_60_120_render_hz() {
    let path =
        std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../../data/juiced2/content.json");
    let mut c: GameContent = serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    c.cars = vec![c
        .cars
        .iter()
        .find(|c| c.handling.layout == DriveLayout::Awd)
        .unwrap()
        .clone()];
    c.leagues.clear();
    c.events = vec![EventDefinition {
        id: "clock-drift".into(),
        track_id: "alps_drift1_drift1".into(),
        mode: RaceMode::DriftEndurance,
        target: 30.,
        opponents: 0,
        ..Default::default()
    }];
    let mut outputs = vec![];
    for rate in [30, 60, 120] {
        let mut game = Game::new(c.clone());
        game.command(GameCommand::StartRace {
            event_id: "clock-drift".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        // The same causal controller is sampled at30Hz, with its legal input held across render calls.
        for _ in 0..1800 {
            let input = game.scenario_player_ai_input();
            for _ in 0..rate / 30 {
                game.advance(1. / rate as f32, input);
            }
            if game.frame_snapshot().screen == GameScreen::Results {
                break;
            }
        }
        let snap = game.frame_snapshot();
        assert!(snap.result.as_ref().map(|r| r.score > 0.).unwrap_or(false));
        outputs.push(serde_json::to_string(&snap).unwrap());
    }
    assert_eq!(outputs[0], outputs[1]);
    assert_eq!(outputs[1], outputs[2]);
}

#[test]
fn native_clutch_coasting_uses_body_forward_velocity_at_all_world_headings() {
    let p = Handling::default();
    let g = PhysicsGlobals::recovered_script_settings();
    for heading in [0., std::f32::consts::FRAC_PI_2, std::f32::consts::PI] {
        let mut v = VehicleState::default();
        v.set_yaw(heading);
        v.velocity = [12. * heading.sin(), 0., 12. * heading.cos()];
        v.clutch_engaged = true;
        assert!((v.body_velocity()[2] - 12.).abs() < 1e-5);
        v.step(&p, &g, PlayerInput::default(), 1. / 60.);
        assert!(
            v.clutch_engaged,
            "coast at heading{heading} incorrectly disengaged"
        );
    }
}

#[test]
fn bet_negotiation_defers_escrow_until_counter_is_accepted() {
    let c = content();
    let id = c.events[0].id.clone();
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    let initial = game.frame_snapshot().career.cash;
    game.command(GameCommand::OfferDriverBet {
        racer: 1,
        amount: 1,
    })
    .unwrap();
    let offer = game.frame_snapshot().race.unwrap().bet_offer.unwrap();
    assert_eq!(offer.status, BetOfferStatus::Countered);
    assert!(offer.counter_amount > 1);
    assert_eq!(game.frame_snapshot().career.cash, initial);
    game.command(GameCommand::DeclineBetOffer).unwrap();
    assert_eq!(game.frame_snapshot().career.cash, initial);
    game.command(GameCommand::OfferDriverBet {
        racer: 1,
        amount: 1,
    })
    .unwrap();
    game.command(GameCommand::AcceptBetOffer).unwrap();
    assert_eq!(
        game.frame_snapshot().career.cash,
        initial - i64::from(offer.counter_amount)
    );
    assert_eq!(
        game.frame_snapshot()
            .race
            .unwrap()
            .bet_offer
            .unwrap()
            .status,
        BetOfferStatus::Accepted
    );
    assert!(game.command(GameCommand::AcceptBetOffer).is_err());
    assert!(game.command(GameCommand::DeclineBetOffer).is_err());
}

#[test]
fn pink_slip_negotiation_transfers_the_selected_rivals_car_even_if_race_is_lost() {
    let c = content();
    let id = c.events[0].id.clone();
    let point = c.tracks[0].points[1];
    let mut game = Game::new(c);
    game.command(GameCommand::BuyCar {
        car_id: "car29".into(),
    })
    .unwrap();
    game.command(GameCommand::SelectCar {
        car_id: "car0".into(),
    })
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: id,
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    game.command(GameCommand::OfferPinkSlip { racer: 2 })
        .unwrap();
    assert_eq!(
        game.frame_snapshot()
            .race
            .as_ref()
            .unwrap()
            .bet_offer
            .as_ref()
            .unwrap()
            .kind,
        BetKind::PinkSlip
    );
    game.command(GameCommand::AcceptBetOffer).unwrap();
    game.command(GameCommand::LaunchRace).unwrap();
    let rival = game.frame_snapshot().race.unwrap().racers[2].car_id.clone();
    for _ in 0..190 {
        game.advance(1. / 60., PlayerInput::default());
    }
    game.scenario_place_racer(1, point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    game.scenario_place_player(point, [0.; 3], 1, 1).unwrap();
    game.advance(1. / 60., PlayerInput::default());
    let snap = game.frame_snapshot();
    assert!(!snap.result.as_ref().unwrap().won);
    assert_eq!(snap.result.unwrap().pink_slip, Some(rival.clone()));
    assert!(snap.career.garage.contains_key(&rival));
    assert!(snap.career.garage.contains_key("car0"));
    assert_eq!(snap.career.vehicle_history[&rival].pink_slip_wins, 1);
}

#[test]
fn compatible_per_slot_parts_checkout_independently_and_save() {
    let mut c = content();
    c.cars[0].parts = std::collections::BTreeMap::from([
        ("spoiler".into(), vec!["native-wing".into()]),
        ("hood".into(), vec!["native-hood".into()]),
    ]);
    let mut game = Game::new(c.clone());
    let mut custom = Customization::default();
    custom.parts.insert("spoiler".into(), "wrong-car".into());
    assert!(game
        .command(GameCommand::Customize {
            car_id: "car0".into(),
            customization: custom.clone()
        })
        .is_err());
    custom.parts.insert("spoiler".into(), "native-wing".into());
    custom.parts.insert("hood".into(), "native-hood".into());
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization: custom,
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().cart.len(), 2);
    game.command(GameCommand::RemoveCartItem {
        item_id: "car0:part:hood".into(),
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().cart.len(), 1);
    assert!(!game
        .frame_snapshot()
        .selected_customization
        .parts
        .contains_key("hood"));
    game.command(GameCommand::Checkout).unwrap();
    let loaded = Game::load_json(c, &game.save_json().unwrap()).unwrap();
    assert_eq!(
        loaded.frame_snapshot().career.garage["car0"].parts["spoiler"],
        "native-wing"
    );
}

#[test]
fn native_eliminator_five_drivers_penultimate_crossing_eliminates_last() {
    let mut c = content();
    c.events[0].mode = RaceMode::Eliminator;
    c.events[0].laps = 99;
    c.events[0].opponents = 4;
    let points = c.tracks[0].points.clone();
    let id = c.events[0].id.clone();
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    for _ in 0..181 {
        game.advance(1. / 60., PlayerInput::default());
    }
    assert_eq!(game.frame_snapshot().race.unwrap().laps, 4);
    for lap in 0..4 {
        let last = 4 - lap as usize;
        for i in 1..=last {
            let mut p = points[1];
            p[0] += i as f32 * 2.5;
            game.scenario_place_racer(i, p, [0.; 3], lap, 2).unwrap();
        }
        game.scenario_place_player(points[0], [0.; 3], lap, 0)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        let snapshot = game.frame_snapshot();
        if last == 1 {
            // Leader is now the penultimate participant and completes configured lap four.
            assert!(snapshot.race.as_ref().unwrap().racers[1].eliminated);
            assert!(snapshot.result.unwrap().won);
            break;
        }
        assert_eq!(
            snapshot
                .race
                .unwrap()
                .racers
                .iter()
                .filter(|r| r.eliminated)
                .count(),
            lap as usize
        );
        // Earlier drivers have crossed. Rank N−1 crosses before rank N does.
        for i in 0..last - 1 {
            let mut p = points[1];
            p[0] += i as f32 * 2.5;
            game.scenario_place_racer(i, p, [0.; 3], lap + 1, 2)
                .unwrap();
        }
        game.scenario_place_racer(last - 1, points[0], [0.; 3], lap, 0)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        let snapshot = game.frame_snapshot();
        let race = snapshot.race.unwrap();
        assert!(race.racers[last].eliminated);
        assert_eq!(
            race.racers[last].lap, lap,
            "last driver is eliminated BEFORE crossing"
        );
        assert!(!race.racers[last - 1].eliminated);
        assert_eq!(
            race.racers.iter().filter(|r| r.eliminated).count(),
            lap as usize + 1
        );
    }
}

#[test]
fn difficulty_persists_and_changes_actual_opponent_driving() {
    let mut c = content();
    c.events[0].opponents = 1;
    let mut easy = Game::new(c.clone());
    easy.command(GameCommand::SetDifficulty { level: 0 })
        .unwrap();
    let json = easy.save_json().unwrap();
    let mut easy = Game::load_json(c.clone(), &json).unwrap();
    assert_eq!(easy.frame_snapshot().difficulty, 0);
    let mut normal = Game::new(c);
    assert_eq!(normal.frame_snapshot().difficulty, 1);
    assert!(normal
        .command(GameCommand::SetDifficulty { level: 3 })
        .is_err());
    for game in [&mut easy, &mut normal] {
        let id = game.snapshot().events[0].id.clone();
        game.command(GameCommand::StartRace {
            event_id: id,
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        game.scenario_place_player([120., 0., 350.], [0.; 3], 0, 3)
            .unwrap();
        for _ in 0..300 {
            game.advance(1. / 60., PlayerInput::default());
        }
    }
    let easy_car = easy.frame_snapshot().race.unwrap().racers[1].clone();
    let normal_car = normal.frame_snapshot().race.unwrap().racers[1].clone();
    assert!(
        (normal_car.speed_kph - easy_car.speed_kph).abs() > 0.1,
        "normal={} easy={}",
        normal_car.speed_kph,
        easy_car.speed_kph
    );
    assert_ne!(normal_car.position, easy_car.position);
}

#[test]
fn native_ai_speed_demand_preserves_deadband_slopes_and_reverse_predicate() {
    assert_eq!(native_ai_speed_demand(19., 20., 0), 0.);
    assert_eq!(native_ai_speed_demand(21., 20., 0), 0.);
    assert!((native_ai_speed_demand(5., 20., 0) - 1.).abs() < 1e-6);
    assert!((native_ai_speed_demand(17., 20., 0) - 0.2).abs() < 1e-6);
    assert!((native_ai_speed_demand(23., 20., 0) + 0.3).abs() < 1e-6);
    assert_eq!(native_ai_speed_demand(-2., 20., 0), -1.);
    assert_eq!(native_ai_speed_demand(-2., 20., 1), 1.);
}

#[test]
fn native_human_drift_assist_changes_motion_by_recovered_equations() {
    let mut state = HumanDriftState::default();
    let mut globals = HumanDriftGlobals::default();
    let motion = HumanDriftMotion {
        world_velocity: [0., 0., 20.],
        body_angular_velocity: [0.1, 0., 0.2],
        forward_axis: [0., 0., 1.],
        right_axis: [1., 0., 0.],
        score_angle: 0.5,
        airborne_time: 0.,
    };
    let result = state.advance(
        &mut globals,
        PlayerInput {
            throttle: 1.,
            steering: 0.3,
            ..Default::default()
        },
        1. / 60.,
        true,
        motion,
    );
    // 82114BD8: blend=(.5-.02)*2=.96; forward delta=.96*45*.02*25/60.
    assert!((state.blend - 0.96).abs() < 1e-6);
    assert!((result.world_velocity[2] - 20.36).abs() < 1e-5);
    assert!((state.yaw_control - 0.6088381).abs() < 1e-5);
    assert!((result.body_angular_velocity[1] - 0.01168969).abs() < 1e-6);
    assert_eq!(result.body_angular_velocity[0], 0.1);
    assert_eq!(result.body_angular_velocity[2], 0.2);
    assert_eq!(globals.shared_damping, 1.); // Native mutable global write survives this call.
    assert!((state.visual_steering - 0.06).abs() < 1e-6);
    let stopped = HumanDriftMotion {
        world_velocity: [0.; 3],
        score_angle: 0.,
        ..motion
    };
    let mut state = HumanDriftState::default();
    let mut globals = HumanDriftGlobals::default();
    let result = state.advance(
        &mut globals,
        PlayerInput {
            throttle: 1.,
            ..Default::default()
        },
        1. / 60.,
        false,
        stopped,
    );
    assert_eq!(result.world_velocity, [0.; 3]); // Zero-initialized native throttle gate; no invented launch force.
    assert_eq!(state.blend, 0.);
}

#[test]
fn native_drift_grip_switch_preserves_layout_and_speed_boundaries() {
    let base = [1.2, 1.4];
    assert_eq!(
        native_drift_tyre_mu(base, DriveLayout::Rwd, 9.999, true, true),
        base
    );
    assert_eq!(
        native_drift_tyre_mu(base, DriveLayout::Awd, 20., false, true),
        base
    );
    assert_eq!(
        native_drift_tyre_mu(base, DriveLayout::Fwd, 20., true, false),
        base
    );
    let rear = native_drift_tyre_mu(base, DriveLayout::Rwd, 10., true, true);
    assert!((rear[0] - 0.66).abs() < 1e-6 && (rear[1] - 0.77).abs() < 1e-6);
    for layout in [DriveLayout::Fwd, DriveLayout::Awd] {
        let mu = native_drift_tyre_mu(base, layout, 10., true, true);
        assert!((mu[0] - 1.08).abs() < 1e-6 && (mu[1] - 0.77).abs() < 1e-6);
    }
}

#[test]
fn native_human_assist_is_equivariant_under_world_yaw_and_damps_airborne_rotation() {
    let motion = HumanDriftMotion {
        world_velocity: [4., 0., 20.],
        body_angular_velocity: [0.1, 0.2, 0.3],
        forward_axis: [0., 0., 1.],
        right_axis: [1., 0., 0.],
        score_angle: 0.3,
        airborne_time: 0.,
    };
    let input = PlayerInput {
        throttle: 1.,
        steering: 0.2,
        ..Default::default()
    };
    let mut first = HumanDriftState::default();
    let mut globals = HumanDriftGlobals::default();
    let expected = first.advance(&mut globals, input, 1. / 60., true, motion);
    let rotated = HumanDriftMotion {
        world_velocity: [20., 0., -4.],
        forward_axis: [1., 0., 0.],
        right_axis: [0., 0., -1.],
        ..motion
    };
    let mut second = HumanDriftState::default();
    let mut globals = HumanDriftGlobals::default();
    let actual = second.advance(&mut globals, input, 1. / 60., true, rotated);
    assert!((actual.world_velocity[0] - expected.world_velocity[2]).abs() < 1e-6);
    assert!((actual.world_velocity[2] + expected.world_velocity[0]).abs() < 1e-6);
    assert_eq!(actual.body_angular_velocity, expected.body_angular_velocity);
    let mut state = HumanDriftState::default();
    let mut globals = HumanDriftGlobals::default();
    let airborne = state.advance(
        &mut globals,
        input,
        1. / 60.,
        true,
        HumanDriftMotion {
            airborne_time: 0.1,
            ..motion
        },
    );
    assert!(
        (airborne.body_angular_velocity[1] - expected.body_angular_velocity[1] * (1. - 10. / 60.))
            .abs()
            < 1e-6
    );
    assert!((airborne.body_angular_velocity[2] - 0.25).abs() < 1e-6);
    assert_eq!(airborne.body_angular_velocity[0], 0.1);
}

#[test]
fn native_collision_queries_preserve_concave_floor_holes_bridges_and_wall_sweeps() {
    let mut def = NativeCollisionDefinition {
        points: vec![
            [0., 0., 0.],
            [4., 0., 0.],
            [4., 0., 1.],
            [1., 0., 1.],
            [1., 0., 4.],
            [0., 0., 4.],
        ],
        polygons: vec![NativePolygon {
            indices: vec![0, 1, 2, 3, 4, 5],
            surface_id: 7,
        }],
        ..Default::default()
    };
    let world = NativeCollisionWorld::new(&def).unwrap();
    assert_eq!(world.ground([0.5, 0., 3.], 0.5, 1.).unwrap().surface_id, 7);
    assert!(world.ground([3., 0., 3.], 0.5, 1.).is_none());
    def.points
        .extend([[0., 5., 0.], [4., 5., 0.], [4., 5., 4.], [0., 5., 4.]]);
    def.polygons.push(NativePolygon {
        indices: vec![6, 7, 8, 9],
        surface_id: 8,
    });
    let world = NativeCollisionWorld::new(&def).unwrap();
    assert_eq!(world.ground([3., 5., 3.], 0.5, 1.).unwrap().height, 5.);
    assert_eq!(world.ground([0.5, 0., 3.], 0.5, 1.).unwrap().height, 0.);
    let def = NativeCollisionDefinition {
        points: vec![[2., 0., -10.], [2., 4., -10.], [2., 4., 10.], [2., 0., 10.]],
        polygons: vec![NativePolygon {
            indices: vec![0, 1, 2, 3],
            surface_id: 1,
        }],
        ..Default::default()
    };
    let world = NativeCollisionWorld::new(&def).unwrap();
    let mut state = VehicleState::default();
    state.position = [4., 0., 2.];
    state.velocity = [20., 0., 0.];
    assert!(world.resolve_chassis(&mut state, &Handling::default(), [0., 0., 2.]));
    assert!(
        state.position[0] < 1.16 && state.velocity[0] < 0.,
        "{:?} {:?}",
        state.position,
        state.velocity
    );
}

#[test]
fn native_bicubic_patch_basis_and_all_eight_original_collision_files_build() {
    let mut def = NativeCollisionDefinition::default();
    for j in 0..4 {
        for i in 0..4 {
            def.points
                .push([i as f32 / 3., i as f32 * j as f32 / 9., j as f32 / 3.]);
        }
    }
    let patch = NativePatch {
        indices: std::array::from_fn(|i| i as u32),
        subdivisions: [4, 4],
        ..Default::default()
    };
    let p = def.patch_point(&patch, 0.25, 0.75);
    assert!(
        (p[0] - 0.75).abs() < 1e-6 && (p[1] - 0.1875).abs() < 1e-6 && (p[2] - 0.25).abs() < 1e-6
    );
    def.patches.push(patch);
    let world = NativeCollisionWorld::new(&def).unwrap();
    assert!((world.ground(p, 1., 1.).unwrap().height - p[1]).abs() < 0.03);
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../artifacts/juiced2-build/collision/track-local");
    let mut count = 0;
    for entry in std::fs::read_dir(root).unwrap() {
        let path = entry.unwrap().path();
        if !path
            .file_name()
            .unwrap()
            .to_string_lossy()
            .contains("drift")
        {
            continue;
        }
        let def: NativeCollisionDefinition =
            serde_json::from_str(&std::fs::read_to_string(&path).unwrap()).unwrap();
        let world =
            NativeCollisionWorld::new(&def).unwrap_or_else(|e| panic!("{}: {e}", path.display()));
        assert!(world.triangle_count > 100);
        count += 1;
    }
    assert_eq!(count, 8);
}

#[test]
fn native_cubic_spline_wall_uses_recovered_four_metre_top_and_minus_one_bottom() {
    let def = NativeCollisionDefinition {
        points: vec![[2., 0., -10.], [2., 0., -3.], [2., 0., 3.], [2., 0., 10.]],
        splines: vec![NativeSpline {
            indices: [0, 1, 2, 3],
            surface_id: 9,
        }],
        ..Default::default()
    };
    let world = NativeCollisionWorld::new(&def).unwrap();
    assert_eq!(world.unresolved_spline_count, 0);
    for (height, expected) in [(0., true), (4.1, false), (-2.6, false)] {
        let mut state = VehicleState::default();
        state.position = [4., height, 0.];
        state.velocity = [20., 0., 0.];
        assert_eq!(
            world.resolve_chassis(&mut state, &Handling::default(), [0., height, 0.]),
            expected,
            "height {height}"
        );
    }
}

#[test]
fn ui_snapshots_keep_minimap_data_without_copying_native_physics_geometry() {
    let mut c = content();
    let points = c.tracks[0].points.clone();
    c.tracks[0].collision = Some(NativeCollisionDefinition {
        points: vec![[1., 2., 3.]; 10000],
        ..Default::default()
    });
    let game = Game::new(c);
    let snapshot = game.snapshot();
    assert_eq!(snapshot.tracks[0].points, points);
    assert!(snapshot.tracks[0].collision.is_none());
    assert_eq!(
        game.content.tracks[0]
            .collision
            .as_ref()
            .unwrap()
            .points
            .len(),
        10000
    );
    assert!(game.frame_snapshot().tracks.is_empty());
}

#[test]
fn uphill_tangent_motion_is_not_mistaken_for_suspension_compression_velocity() {
    let p = Handling::default();
    let g = PhysicsGlobals::default();
    let slope = 0.15f32;
    let angle = slope.atan();
    let mut state = VehicleState::default();
    state.orientation = [(-angle * 0.5).sin(), 0., 0., (-angle * 0.5).cos()];
    state.velocity = [0., 3., 20.];
    state.wheel_omega = [state.speed() / p.wheel_radius; 4];
    for i in 0..4 {
        let z = if i < 2 {
            p.wheelbase * (1. - p.front_weight)
        } else {
            -p.wheelbase * p.front_weight
        };
        state.contacts[i] = SurfaceContact {
            anchor_xz: [
                if i % 2 == 0 {
                    -p.track_width * 0.5
                } else {
                    p.track_width * 0.5
                },
                angle.cos() * z,
            ],
            height: slope * angle.cos() * z,
            normal: [0., angle.cos(), -angle.sin()],
            grip: 1.,
            active: true,
        };
    }
    assert!(state.body_velocity()[1].abs() < 1e-6);
    state.step(&p, &g, PlayerInput::default(), 1. / 60.);
    assert!(
        state.velocity[1] > 2.98,
        "tangent motion incorrectly damped: {:?}",
        state.velocity
    );
}

#[test]
fn selected_goal_events_share_context_and_respect_qualifier_unlock() {
    let mut c = content();
    c.tracks[0].location = "USA".into();
    let goal = GoalDefinition {
        id: "g".into(),
        kind: "WinRace".into(),
        discipline: "Circuit".into(),
        subtype: "Eliminator".into(),
        location: "USA".into(),
        contest_type: "Championship".into(),
        car_class: "C1".into(),
        prototype: true,
        extreme_nos: true,
        endurance: true,
        prize_type: "PinkSlip".into(),
        ..Default::default()
    };
    let mut qualifier = goal.clone();
    qualifier.id = "q".into();
    qualifier.qualifier = true;
    c.leagues = vec![LeagueDefinition {
        league: 0,
        optional_goals_required: 1,
        goals: vec![goal, qualifier],
        ..Default::default()
    }];
    let mut event = c.events[0].clone();
    event.id = "matching".into();
    event.mode = RaceMode::Eliminator;
    event.contest_type = "Championship".into();
    event.car_class = "c1".into();
    event.prototype = true;
    event.extreme_nos = true;
    event.endurance = 25;
    event.prize_type = "PinkSlip".into();
    c.events = vec![event.clone()];
    for i in 0..8 {
        let mut other = event.clone();
        other.id = format!("excluded{i}");
        match i {
            0 => other.mode = RaceMode::DriftKing,
            1 => other.contest_type = "Tournament".into(),
            2 => other.car_class = "C2".into(),
            3 => other.prototype = false,
            4 => other.extreme_nos = false,
            5 => other.endurance = 0,
            6 => other.prize_type = "Cash".into(),
            _ => other.league = 1,
        };
        c.events.push(other);
    }
    event.id = "qualifier".into();
    event.qualifier = true;
    c.events.push(event);
    let mut game = Game::new(c);
    assert_eq!(game.events_for_goal("g"), vec!["matching"]);
    assert!(game.events_for_goal("q").is_empty());
    assert!(game.events_for_goal("unknown").is_empty());
    let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    save.career.goal_progress.insert(
        "g".into(),
        GoalProgress {
            value: 1.,
            complete: true,
        },
    );
    game = Game::load_json(game.content.clone(), &serde_json::to_string(&save).unwrap()).unwrap();
    assert_eq!(game.events_for_goal("q"), vec!["qualifier"]);
}

#[test]
fn native_start_records_reflect_yaw_clamp_slot_and_snap_to_collision_plane() {
    let mut c = content();
    c.events[0].opponents = 2;
    c.tracks[0].start_grid = vec![
        TrackStart {
            position: [2., 0.5, 4.],
            native_yaw_radians: std::f32::consts::FRAC_PI_2,
            source_record_index: 0,
        },
        TrackStart {
            position: [-3., 0.5, 1.],
            native_yaw_radians: 0.,
            source_record_index: 1,
        },
    ];
    c.tracks[0].collision = Some(NativeCollisionDefinition {
        points: vec![
            [-100., 0., -100.],
            [100., 0., -100.],
            [100., 0., 100.],
            [-100., 0., 100.],
        ],
        polygons: vec![NativePolygon {
            indices: vec![0, 1, 2, 3],
            surface_id: 0,
        }],
        ..Default::default()
    });
    let id = c.events[0].id.clone();
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: id,
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    let race = game.frame_snapshot().race.unwrap();
    assert_eq!(race.racers[0].position, [2., 0., 4.]);
    let q = race.racers[0].rotation;
    assert!((2. * (q[0] * q[2] + q[3] * q[1]) + 1.).abs() < 1e-6);
    assert!((1. - 2. * (q[0] * q[0] + q[1] * q[1])).abs() < 1e-6);
    assert_eq!(race.racers[1].position, [-3., 0., 1.]);
    assert_eq!(race.racers[2].position, race.racers[1].position);
}

#[test]
fn recorded_binary_controls_complete_native_endurance_targets_and_persist_rewards() {
    for (event_id, league, target, label, goal_id) in [
        (
            "native_ca32970d_010",
            2,
            500_000.,
            "1m-host-3d-v1",
            "goal_0a2b0440_03",
        ),
        (
            "native_c8c48fc7_035",
            3,
            1_000_000.,
            "1m-host-3d-v1",
            "goal_08b3ccff_12",
        ),
    ] {
        let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
        let mut content: GameContent = serde_json::from_str(
            &std::fs::read_to_string(root.join("data/juiced2/content.json")).unwrap(),
        )
        .unwrap();
        let car = content
            .cars
            .iter()
            .find(|c| c.handling.layout == DriveLayout::Awd)
            .unwrap()
            .clone();
        content.cars = vec![car];
        content.events.retain(|event| event.id == event_id);
        assert_eq!(content.events[0].target, target);
        let controls: Vec<serde_json::Value> = serde_json::from_str(
            &std::fs::read_to_string(root.join(format!(
                "artifacts/juiced2-build/rome-drift-{label}-controls.json"
            )))
            .unwrap(),
        )
        .unwrap();
        let mut game = Game::new(content);
        let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
        save.career.league = league; // Fixture precondition, not a bypass during the event.
        game =
            Game::load_json(game.content.clone(), &serde_json::to_string(&save).unwrap()).unwrap();
        let cash = game.snapshot().career.cash;
        game.command(GameCommand::StartRace {
            event_id: event_id.into(),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for (tick, row) in controls.iter().enumerate() {
            assert_eq!(row["tick"].as_u64(), Some(tick as u64));
            let input: PlayerInput = serde_json::from_value(row["input"].clone()).unwrap();
            assert!(input.handbrake == 0. || input.handbrake == 1.);
            assert!((-1. ..=1.).contains(&input.steering));
            assert!((0. ..=1.).contains(&input.throttle) && (0. ..=1.).contains(&input.brake));
            game.advance(1. / 60., input);
            let snapshot = game.frame_snapshot();
            let race = snapshot.race.unwrap();
            if race.elapsed > 0. {
                assert!(
                    race.racers[0]
                        .surface_contacts
                        .iter()
                        .filter(|c| c.active)
                        .count()
                        >= 2,
                    "unsupported tick{tick}"
                );
            }
        }
        let result = game.frame_snapshot().result.unwrap();
        assert!(result.won && result.score >= target, "{result:?}");
        let reloaded = Game::load_json(game.content.clone(), &game.save_json().unwrap()).unwrap();
        let career = reloaded.snapshot().career;
        assert_eq!(career.cash, cash + result.reward);
        assert!(career.completed_events.contains(&event_id.into()));
        assert!(career.goal_progress[goal_id].complete);
    }
}

#[test]
fn measured_body_underside_clears_native_london_curb_without_removing_barriers() {
    let root = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../..");
    let content: GameContent = serde_json::from_str(
        &std::fs::read_to_string(root.join("data/juiced2/content.json")).unwrap(),
    )
    .unwrap();
    let audit: serde_json::Value = serde_json::from_str(
        &std::fs::read_to_string(root.join("artifacts/juiced2-build/body-geometry-audit.json"))
            .unwrap(),
    )
    .unwrap();
    let measured = audit["cars"]
        .as_array()
        .unwrap()
        .iter()
        .find(|car| car["code"] == "GT4_HOND0018")
        .unwrap()["body_bounds"]["min"][1]
        .as_f64()
        .unwrap() as f32;
    let mut handling = content
        .cars
        .iter()
        .find(|car| car.id == "GT4_HOND0018")
        .unwrap()
        .handling
        .clone();
    let track = content
        .tracks
        .iter()
        .find(|track| track.id == "london_circuit2")
        .unwrap();
    let world = NativeCollisionWorld::new(track.collision.as_ref().unwrap()).unwrap();
    let mut initial = VehicleState::default();
    initial.position = [38.5, -0.010503486, -25.];
    initial.set_yaw(2.234);
    initial.velocity = [8.3, 0., -5.5];
    let old = [
        initial.position[0] - 8.3 / 60.,
        initial.position[1],
        initial.position[2] + 5.5 / 60.,
    ];
    handling.body_min_y = 0.;
    assert!(world.resolve_chassis(&mut initial.clone(), &handling, old));
    handling.body_min_y = measured;
    let mut cleared = initial.clone();
    assert!(!world.resolve_chassis(&mut cleared, &handling, old));
    assert_eq!(cleared.position, initial.position);
    let wall = NativeCollisionWorld::new(&NativeCollisionDefinition {
        points: vec![[-10., 0., 0.], [10., 0., 0.], [10., 3., 0.], [-10., 3., 0.]],
        polygons: vec![NativePolygon {
            indices: vec![0, 1, 2, 3],
            surface_id: 0,
        }],
        ..Default::default()
    })
    .unwrap();
    cleared.position = [0., 0., 5.];
    cleared.set_yaw(0.);
    cleared.velocity = [0., 0., 10.];
    assert!(wall.resolve_chassis(&mut cleared, &handling, [0., 0., -5.]));
}

#[test]
fn native_curved_tokyo_patch_retains_continuous_source_midpoint() {
    let path = std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
        .join("../../artifacts/juiced2-build/collision/track-local/tokyo_circuit1.json");
    let def: NativeCollisionDefinition =
        serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
    let point = def.patch_point(&def.patches[397], 0.5, 0.5);
    let world = NativeCollisionWorld::new(&def).unwrap();
    let hit = world
        .ground(point, 0.5, 0.5)
        .expect("source patch397 midpoint was flattened out of the query mesh");
    assert!((hit.height - point[1]).abs() < 0.03, "{hit:?} vs{point:?}");
}

#[test]
fn native_king_catchup_uses_human_reference_rank_league_and_source_clamps() {
    assert_eq!(native_king_multiplier(None, 100, 2, 9, true), 1.);
    assert_eq!(native_king_multiplier(Some(100), 0, 1, 0, false), 0.2);
    assert_eq!(native_king_multiplier(Some(1000), 100, 1, 0, false), 10.);
    assert!((native_king_multiplier(Some(200), 100, 1, 1, false) - 2.3).abs() < 1e-6);
    assert_eq!(native_king_multiplier(Some(200), 100, 6, 1, false), 0.2);
    assert_eq!(native_king_multiplier(Some(100), 200, 1, 9, false), 0.4);
    assert_eq!(native_king_multiplier(Some(200), 100, 1, 0, true), 5.);
}

#[test]
fn native_contact_frame_preserves_fast_path_plane_projection_and_reverse_sign() {
    let n = [0.2f32, 0.96, (1f32 - 0.2 * 0.2 - 0.96 * 0.96).sqrt()];
    let frame = native_wheel_frame(n, [3., 4., 15.], 0.3, 30.);
    for axis in [
        frame.lateral_axis,
        frame.longitudinal_axis,
        frame.tangent_velocity,
    ] {
        assert!((axis[0] * n[0] + axis[1] * n[1] + axis[2] * n[2]).abs() < 2e-6);
    }
    assert_eq!(frame.camber, n[0]);
    let fast = native_wheel_frame(n, [3., 4., 15.], 0., 30.);
    assert_eq!(fast.lateral_axis, [1., 0., 0.]);
    assert_eq!(fast.longitudinal_axis, [0., 0., 1.]);
    let forward = native_wheel_frame([0., 1., 0.], [2., 0., 10.], 0.2, 30.);
    let reverse = native_wheel_frame([0., 1., 0.], [-2., 0., -10.], 0.2, -30.);
    assert!((forward.angle - reverse.angle).abs() < 1e-6);
    assert!((forward.forward_speed + reverse.forward_speed).abs() < 1e-6);
    assert_eq!(reverse.camber, 0.);
    assert_eq!(
        native_wheel_frame([0.35, 0.9367497, 0.], [0., 0., 10.], 0.2, 30.).camber,
        0.
    );
}

#[test]
fn native_negative_camber_reflects_before_positive_saturation_clamp() {
    let g = PhysicsGlobals::default();
    let a = combined_tyre_force(3000., 1., 0.2, 0.15, -0.3, &g);
    let b = combined_tyre_force(3000., 1., 0.2, -0.15, 0.3, &g);
    assert_eq!(a[0], b[0]);
    assert_eq!(a[1], -b[1]);
    assert_eq!(a[2], b[2]);
}

#[test]
fn solo_drift_has_no_unsourced_timeout_and_failed_challenges_pay_no_winner_prize() {
    for explicit_limit in [0., 0.1] {
        let mut c = content();
        c.events[0].mode = RaceMode::SoloDrift;
        c.events[0].opponents = 0;
        c.events[0].target = 30000.;
        c.events[0].time_limit = explicit_limit;
        c.events[0].prizes = vec![5000];
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..60 * 185 {
            game.advance(1. / 60., PlayerInput::default());
        }
        let snapshot = game.frame_snapshot();
        if explicit_limit == 0. {
            assert_eq!(snapshot.screen, GameScreen::Race);
            // Configured lap completion must still end the challenge.
            game.scenario_place_player([0., 0., 250.], [0., 0., 0.], 1, 1)
                .unwrap();
            game.advance(1. / 60., PlayerInput::default());
        }
        let snapshot = game.frame_snapshot();
        assert_eq!(snapshot.screen, GameScreen::Results);
        let result = snapshot.result.unwrap();
        assert!(!result.won);
        assert_eq!(result.reward, 0);
        assert_eq!(snapshot.career.cash, 25000);
    }
}

#[test]
fn native_paint_family_and_color_are_one_priced_record() {
    for (family, price) in [
        ("gloss", 3000),
        ("metallic", 5000),
        ("flake", 12000),
        ("pearl", 12000),
        ("matt", 7500),
        ("thinfilm", 20000),
    ] {
        let mut game = Game::new(content());
        game.command(GameCommand::Navigate {
            screen: GameScreen::Garage,
        })
        .unwrap();
        let custom = Customization {
            finish: family.into(),
            paint: [0.1, 0.2, 0.3, 1.],
            ..Default::default()
        };
        game.command(GameCommand::Customize {
            car_id: "car0".into(),
            customization: custom.clone(),
        })
        .unwrap();
        let cart = game.frame_snapshot().cart;
        assert_eq!(
            cart.len(),
            1,
            "{family} must not charge separately for RGB and family"
        );
        assert_eq!(cart[0].cost, price);
        game.command(GameCommand::RemoveCartItem {
            item_id: cart[0].id.clone(),
        })
        .unwrap();
        assert_eq!(
            game.frame_snapshot().selected_customization,
            Customization::default()
        );
        game.command(GameCommand::Customize {
            car_id: "car0".into(),
            customization: custom,
        })
        .unwrap();
        game.command(GameCommand::Checkout).unwrap();
        assert_eq!(game.frame_snapshot().career.cash, 25000 - i64::from(price));
        let saved = game.save_json().unwrap();
        let loaded = Game::load_json(content(), &saved).unwrap();
        assert_eq!(loaded.frame_snapshot().career.garage["car0"].finish, family);
    }
}

#[test]
fn earned_rookie_qualifier_drives_around_eliminated_contestants_and_promotes() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("../../data/juiced2/content.json").unwrap())
            .unwrap();
    let initial=std::fs::read_to_string("../../artifacts/juiced2-build/career-rookie-earned/career-native_28956449_000-initial-save.json").unwrap();
    let mut game = Game::load_json(content, &initial).unwrap();
    assert_eq!(game.frame_snapshot().career.league, 0);
    assert!(game.frame_snapshot().league_progress.promotion_open);
    game.command(GameCommand::StartRace {
        event_id: "native_28956449_000".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game.command(GameCommand::OpenGrid).unwrap();
    let n = game.frame_snapshot().race.unwrap().racers.len();
    game.command(GameCommand::OfferDriverBet {
        racer: n - 1,
        amount: 2500,
    })
    .unwrap();
    game.command(GameCommand::AcceptBetOffer).unwrap();
    game.command(GameCommand::LaunchRace).unwrap();
    for _ in 0..60 * 900 {
        let mut input = game.scenario_player_ai_input();
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
        game.advance(1. / 60., input);
        if game.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    assert_eq!(snapshot.screen, GameScreen::Results);
    assert!(snapshot.result.unwrap().won);
    assert_eq!(snapshot.career.league, 1);
}

#[test]
fn native_paint_record_preserves_channels_and_single_cart_purchase() {
    // Synthetic byte-layout fixture, not a fabricated native material preset.
    let mut bytes = [0u8; 72];
    bytes[..4].copy_from_slice(&5u32.to_be_bytes());
    for (index, value) in [
        0.2f32, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1., 2., 3., 4., 5., 6., 7., 0.375, 9.,
    ]
    .into_iter()
    .enumerate()
    {
        bytes[4 + index * 4..8 + index * 4].copy_from_slice(&value.to_be_bytes());
    }
    let record = NativePaintRecord::from_be_bytes(&bytes).unwrap();
    assert_eq!(record.base_rgb, [0.2, 0.3, 0.4]);
    assert_eq!(record.fleck_rgb, [0.5, 0.6, 0.7]);
    assert_eq!(record.secondary_rgb, [0.8, 0.9, 1.]);
    assert_eq!(record.try_thin_film, 0.375); // Source uniform uses FLOAT, not bool.
    assert_eq!(record.finish_id(), Some("thinfilm"));
    assert_eq!(record.to_be_bytes(), bytes);
    assert!(NativePaintRecord::from_be_bytes(&bytes[..71]).is_err());
    let mut game = Game::new(content());
    game.command(GameCommand::Navigate {
        screen: GameScreen::Garage,
    })
    .unwrap();
    let custom = Customization {
        native_paint: Some(record),
        ..Default::default()
    };
    assert_eq!(game.quote_customization(&custom)[0].cost, 20000);
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: custom.native_paint.clone().unwrap(),
    })
    .unwrap();
    let cart = game.frame_snapshot().cart;
    assert_eq!(cart.len(), 1);
    game.command(GameCommand::RemoveCartItem {
        item_id: cart[0].id.clone(),
    })
    .unwrap();
    assert_eq!(
        game.frame_snapshot().selected_customization,
        Customization::default()
    );
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: custom.native_paint.unwrap(),
    })
    .unwrap();
    game.command(GameCommand::Checkout).unwrap();
    let loaded = Game::load_json(content(), &game.save_json().unwrap()).unwrap();
    let custom = &loaded.frame_snapshot().career.garage["car0"];
    assert_eq!(custom.paint, [0.2, 0.3, 0.4, 1.]);
    assert_eq!(custom.finish, "thinfilm");
    assert_eq!(custom.native_paint.as_ref().unwrap().raw_be_bytes, bytes);
    let mut same_typed = custom.clone();
    same_typed
        .native_paint
        .as_mut()
        .unwrap()
        .raw_be_bytes
        .clear();
    assert!(loaded.quote_customization(&same_typed).is_empty());
    let old: Customization = serde_json::from_str("{}").unwrap();
    assert!(old.native_paint.is_none());
}

#[test]
fn accepted_native_paint_requeues_identical_paid_record() {
    let record = NativePaintRecord::from_be_bytes(&[0; 72]).unwrap();
    let mut game = Game::new(content());
    let customization = Customization {
        native_paint: Some(record.clone()),
        ..Default::default()
    };
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization: customization.clone(),
    })
    .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    for _ in 0..2 {
        game.command(GameCommand::AcceptNativePaint {
            car_id: "car0".into(),
            paint: record.clone(),
        })
        .unwrap();
    }
    assert_eq!(game.frame_snapshot().cart.len(), 1);
    game.command(GameCommand::Checkout).unwrap();
    assert_eq!(game.frame_snapshot().career.cash, 22000);
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization,
    })
    .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    assert_eq!(game.quote_native_paint(&record).unwrap().cost, 3000);
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: record.clone(),
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().cart.len(), 1);
    assert_eq!(game.frame_snapshot().cart[0].cost, 3000);
    game.command(GameCommand::RemoveCartItem {
        item_id: "car0:paint".into(),
    })
    .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    let mut metallic = record.clone();
    metallic.native_type = 1;
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: metallic.clone(),
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().cart[0].cost, 5000);
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: record.clone(),
    })
    .unwrap();
    let mut unaccepted_preview = game.frame_snapshot().selected_customization;
    unaccepted_preview.native_paint = Some(metallic);
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization: unaccepted_preview,
    })
    .unwrap();
    assert_eq!(game.frame_snapshot().cart[0].cost, 3000);
    assert_eq!(
        game.frame_snapshot()
            .selected_customization
            .native_paint
            .as_ref()
            .unwrap()
            .native_type,
        0
    );
    game.command(GameCommand::DiscardCart { car_id: None })
        .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    assert_eq!(game.frame_snapshot().career.cash, 22000);
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car0".into(),
        paint: record.clone(),
    })
    .unwrap();
    game.command(GameCommand::Checkout).unwrap();
    assert_eq!(game.frame_snapshot().career.cash, 19000);
    assert!(game.frame_snapshot().cart.is_empty());
    let saved = game.save_json().unwrap();
    assert_eq!(
        Game::load_json(content(), &saved)
            .unwrap()
            .save_json()
            .unwrap(),
        saved
    );
    game.command(GameCommand::Navigate {
        screen: GameScreen::QuickRace,
    })
    .unwrap();
    game.command(GameCommand::SelectCar {
        car_id: "car29".into(),
    })
    .unwrap();
    assert_eq!(game.quote_native_paint(&record).unwrap().cost, 0);
    game.command(GameCommand::AcceptNativePaint {
        car_id: "car29".into(),
        paint: record,
    })
    .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    assert!(game
        .frame_snapshot()
        .selected_customization
        .native_paint
        .is_some());
}

#[test]
fn native_obliterator_qualifier_drives_and_meets_every_lap_quota() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("../../data/juiced2/content.json").unwrap())
            .unwrap();
    let initial = std::fs::read_to_string(
        "../../artifacts/juiced2-build/career-oblit-earned/initial-save.json",
    )
    .unwrap();
    let mut game = Game::load_json(content, &initial).unwrap();
    game.command(GameCommand::StartRace {
        event_id: "native_ca32970d_000".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    let mut held = PlayerInput::default();
    let mut completed_laps = 0;
    for tick in 0..60 * 900 {
        if tick % 12 == 0 {
            held = game.scenario_drift_predictive_input();
        }
        let raw = if held.steering == 0. {
            0.
        } else {
            -held.steering.signum() * (0.12 + 0.88 * held.steering.abs())
        };
        let mut input = held;
        input.steering = if raw.abs() > 0.12 {
            -raw.signum() * (raw.abs() - 0.12) / 0.88
        } else {
            0.
        };
        let before = game.frame_snapshot().race.unwrap().racers[0].clone();
        game.advance(1. / 60., input);
        let snapshot = game.frame_snapshot();
        let after = &snapshot.race.as_ref().unwrap().racers[0];
        if after.lap > before.lap {
            assert!(before.drift_score >= 20000.);
            completed_laps += 1;
        }
        if snapshot.screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    assert_eq!(completed_laps, 4);
    let result = snapshot.result.unwrap();
    assert!(result.won);
    assert!(
        result.score >= 20000.,
        "Final lap score must survive settlement"
    );
    assert_eq!(snapshot.career.league, 3);
}

#[test]
fn restricted_events_require_a_legally_purchased_matching_car() {
    let mut c = content();
    c.events[0].car_class = "Musclecar".into();
    c.cars[1].classes = vec!["MuscleCar".into()];
    let mut game = Game::new(c.clone());
    for career in [false, true] {
        assert!(game
            .command(GameCommand::StartRace {
                event_id: "harbor-circuit".into(),
                career,
                wager: 0,
                pink_slip: false
            })
            .unwrap_err()
            .contains("requires class"));
    }
    assert_eq!(game.frame_snapshot().career.cash, 25000);
    game.command(GameCommand::BuyCar {
        car_id: "car1".into(),
    })
    .unwrap();
    game.command(GameCommand::SelectCar {
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
    let snapshot = game.frame_snapshot();
    assert_eq!(snapshot.career.cash, 24000);
    assert!(snapshot
        .race
        .unwrap()
        .racers
        .iter()
        .all(|r| r.car_id == "car1"));
    for _ in 0..60 * 20 {
        let input = game.scenario_player_ai_input();
        game.advance(1. / 60., input);
    }
    assert!(game.frame_snapshot().race.unwrap().racers[0].position[2].abs() > 10.);
    let saved = game.save_json().unwrap();
    assert!(Game::load_json(c, &saved)
        .unwrap()
        .frame_snapshot()
        .career
        .garage
        .contains_key("car1"));
}

#[test]
fn earned_profile_buys_a_muscle_car_and_wins_the_restricted_qualifier() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("../../data/juiced2/content.json").unwrap())
            .unwrap();
    let initial = std::fs::read_to_string(
        "../../artifacts/juiced2-build/career-muscle-earned/initial-unowned-save.json",
    )
    .unwrap();
    let mut game = Game::load_json(content, &initial).unwrap();
    assert!(!game
        .frame_snapshot()
        .career
        .garage
        .contains_key("MUSTANG_68"));
    game.command(GameCommand::BuyCar {
        car_id: "MUSTANG_68".into(),
    })
    .unwrap();
    game.command(GameCommand::SelectCar {
        car_id: "MUSTANG_68".into(),
    })
    .unwrap();
    game.command(GameCommand::StartRace {
        event_id: "native_c75c8b79_000".into(),
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    let mut held = PlayerInput::default();
    for tick in 0..60 * 90 {
        if tick % 12 == 0 {
            held = game.scenario_drift_predictive_input();
        }
        let raw = if held.steering == 0. {
            0.
        } else {
            -held.steering.signum() * (0.12 + 0.88 * held.steering.abs())
        };
        let mut input = held;
        input.steering = if raw.abs() > 0.12 {
            -raw.signum() * (raw.abs() - 0.12) / 0.88
        } else {
            0.
        };
        game.advance(1. / 60., input);
        if game.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    let result = snapshot.result.unwrap();
    assert!(result.won);
    assert!(result.score >= 100000.);
    assert_eq!(snapshot.career.league, 5);
    assert!(snapshot
        .career
        .transactions
        .iter()
        .any(|t| t.kind == TransactionKind::BuyCar && t.car_id.as_deref() == Some("MUSTANG_68")));
}

#[test]
fn native_route_goals_filter_selection_and_observation_by_exact_course() {
    let mut c = content();
    c.tracks[0].native_route = "RouteA".into();
    c.tracks.push(TrackDefinition {
        id: "other".into(),
        native_route: "RouteB".into(),
        ..Default::default()
    });
    c.events[0].opponents = 0;
    let mut other = c.events[0].clone();
    other.id = "other-event".into();
    other.track_id = "other".into();
    c.events.push(other);
    c.leagues = vec![LeagueDefinition {
        league: 0,
        goals: vec![
            GoalDefinition {
                id: "route-a".into(),
                kind: "WinRace".into(),
                route: "RouteA".into(),
                ..Default::default()
            },
            GoalDefinition {
                id: "route-b".into(),
                kind: "WinRace".into(),
                native_rows: vec![vec!["Route".into(), "RouteB".into()]],
                ..Default::default()
            },
        ],
        ..Default::default()
    }];
    for (event, wanted, unwanted) in [
        ("harbor-circuit", "route-a", "route-b"),
        ("other-event", "route-b", "route-a"),
    ] {
        let mut game = Game::new(c.clone());
        assert_eq!(game.events_for_goal("route-a"), vec!["harbor-circuit"]);
        assert_eq!(game.events_for_goal("route-b"), vec!["other-event"]);
        game.command(GameCommand::StartRace {
            event_id: event.into(),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..190 {
            game.advance(1. / 60., PlayerInput::default());
        }
        // Isolate the observer branch; real career replay proofs never use this hook.
        game.scenario_place_player([0., 0., 250.], [0.; 3], 1, 1)
            .unwrap();
        game.advance(1. / 60., PlayerInput::default());
        let snapshot = game.frame_snapshot();
        assert!(snapshot.result.unwrap().won);
        assert!(snapshot.career.goal_progress[wanted].complete);
        assert!(!snapshot
            .career
            .goal_progress
            .get(unwanted)
            .map(|p| p.complete)
            .unwrap_or(false));
    }
}

#[test]
// Keep staged setup explicit so fixture overrides and input sampling order remain visible.
#[allow(clippy::field_reassign_with_default)]
fn native_nitrous_pressure_capacity_and_activation_snapshot() {
    assert_eq!(native_nitrous_capacity(-2.), 5.);
    assert_eq!(native_nitrous_capacity(0.5), 3.5);
    assert_eq!(native_nitrous_capacity(0.), 2.);
    assert_eq!(native_nitrous_capacity(1.), 5.);
    for (fraction, band, power) in [
        (1., 4, 1.4),
        (0.66, 2, 0.7),
        (f32::from_bits(0.66f32.to_bits() + 1), 3, 1.),
        (0.33, 1, 0.3),
        (f32::from_bits(0.33f32.to_bits() + 1), 2, 0.7),
        (1.1, 3, 1.),
    ] {
        assert_eq!(native_nitrous_pressure(fraction), (band, power));
    }
    let mut state = NativeNitrousState::default();
    state.tank = 1.75;
    state.request(true);
    state.drain(0.5);
    assert_eq!(state.force(1., 1., 4, true), 9520.);
    state.drain(2.);
    assert_eq!(state.force(1., 1., 4, true), 9520.);
    state.request(false);
    state.request(true);
    assert_eq!(state.force(1., 1., 4, true), f32::from_bits(0x457f0001));
    state.drain(20.);
    assert_eq!(state.tank, 0.);
    assert!(!state.active);
}
#[test]
// Keep staged setup explicit so fixture overrides and input sampling order remain visible.
#[allow(clippy::field_reassign_with_default)]
fn native_nitrous_contact_gear_double_metric_and_refill_gates() {
    let mut state = NativeNitrousState::default();
    state.request(true);
    for contacts in [0, 1] {
        assert_eq!(state.force(1., 1., contacts, true), 0.);
    }
    assert_eq!(state.force(1., 1., 4, false), 0.);
    assert_eq!(state.force(0., 1., 4, true), 0.);
    assert_eq!(state.force(1., 1., 2, true), 19040.);
    assert_eq!(native_nitrous_wheel_ratio([4., 0., 0.], 4., true), 0.);
    assert_eq!(native_nitrous_wheel_ratio([3., 4., 0.], 2., true), 0.4);
    assert_eq!(native_nitrous_wheel_ratio([3., 4., 0.], 2., false), 0.);
    assert_eq!(native_nitrous_metric([0.25; 4]), 0.5);
    state.request(false);
    state.tank = 1.;
    for _ in 0..3 {
        state.refill(0.5, 1, false, 0.1);
        assert_eq!(state.tank, 1.);
    }
    state.refill(0.5, 1, false, 0.1);
    assert!((state.tank - 1.024).abs() < 1e-7);
    let mut ai = state.clone();
    ai.tank = 1.;
    ai.refill(0.5, 2, false, 0.1);
    assert!((ai.tank - 1.05).abs() < 1e-7);
    let mut extra = NativeNitrousState::default();
    extra.tank = 1.;
    extra.refill(0., 1, true, 1.);
    assert_eq!(extra.tank, 1.02);
    extra.request(true);
    let before = extra.tank;
    extra.refill(2., 1, true, 1.);
    assert_eq!(extra.tank, before);
}
#[test]
fn stock_nitrous_adds_forward_force_and_uses_original_discipline_gate() {
    fn drive(discipline: NativeDiscipline, nitrous: f32) -> RacerSnapshot {
        let mut c = content();
        c.events[0].opponents = 0;
        c.events[0].native_discipline = Some(discipline);
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for _ in 0..241 {
            game.advance(
                1. / 60.,
                PlayerInput {
                    throttle: 1.,
                    nitrous,
                    ..Default::default()
                },
            );
        }
        game.frame_snapshot().race.unwrap().racers.remove(0)
    }
    let normal = drive(NativeDiscipline::Circuit, 0.);
    let boost = drive(NativeDiscipline::Circuit, 1.);
    assert!(boost.speed_kph > normal.speed_kph + 18.);
    assert!(boost.nitrous < 1.);
    assert!(boost.nitrous_active);
    let disabled = drive(NativeDiscipline::Drift, 1.);
    assert_eq!(disabled.position, normal.position);
    assert_eq!(disabled.nitrous, 1.);
    assert!(!disabled.nitrous_active);
    let solo = drive(NativeDiscipline::Solo, 1.);
    assert_eq!(solo.position, boost.position);
}

#[test]
fn native_nitrous_does_not_add_force_in_air_reverse_or_neutral() {
    let p = Handling::default();
    let g = PhysicsGlobals::recovered_script_settings();
    for mode in 0..3 {
        let mut plain = VehicleState::default();
        if mode == 0 {
            for contact in &mut plain.contacts {
                contact.active = false;
            }
        }
        if mode == 1 {
            plain.reversing = true;
        }
        if mode == 2 {
            plain.gear = 0;
        }
        let mut boost = plain.clone();
        for _ in 0..60 {
            let input = PlayerInput {
                throttle: 1.,
                reverse: mode == 1,
                ..Default::default()
            };
            plain.step(&p, &g, input, 1. / 60.);
            boost.step(
                &p,
                &g,
                PlayerInput {
                    nitrous: 1.,
                    ..input
                },
                1. / 60.,
            );
        }
        assert_eq!(plain.velocity, boost.velocity, "mode{mode}");
        assert_eq!(
            plain.engine_omega, boost.engine_omega,
            "stockP416mustnotbe1.5"
        );
    }
    let mut plain = VehicleState::default();
    plain.set_yaw(std::f32::consts::FRAC_PI_2);
    let mut boost = plain.clone();
    for _ in 0..60 {
        let input = PlayerInput {
            throttle: 1.,
            ..Default::default()
        };
        plain.step(&p, &g, input, 1. / 60.);
        boost.step(
            &p,
            &g,
            PlayerInput {
                nitrous: 1.,
                ..input
            },
            1. / 60.,
        );
    }
    assert!(boost.velocity[0] > plain.velocity[0] + 5.);
    assert!((boost.velocity[2] - plain.velocity[2]).abs() < 0.001);
}

#[test]
fn native_nitrous_gameplay_is_render_cadence_independent() {
    fn run(fps: usize) -> serde_json::Value {
        let mut c = content();
        c.events[0].opponents = 0;
        c.events[0].native_discipline = Some(NativeDiscipline::Circuit);
        let mut game = Game::new(c);
        game.command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        for frame in 0..fps * 6 {
            let seconds = frame / fps;
            game.advance(
                1. / fps as f32,
                PlayerInput {
                    throttle: 1.,
                    steering: if seconds >= 4 { 0.1 } else { 0. },
                    nitrous: if seconds == 3 { 1. } else { 0. },
                    ..Default::default()
                },
            );
        }
        serde_json::to_value(game.frame_snapshot()).unwrap()
    }
    let expected = run(60);
    assert_eq!(run(30), expected);
    assert_eq!(run(120), expected);
}

#[test]
fn save_roundtrip_preserves_real_accumulated_mileage_bits() {
    let c = content();
    let fresh = Game::new(c.clone());
    let game = Game::load_json(c.clone(), &fresh.save_json().unwrap()).unwrap();
    // Actual earned four-lap native viewport save, not an approximate decimal.
    let mileage = f64::from_bits(0x40fd71d4f69fffff);
    let mut fixture: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    fixture
        .career
        .vehicle_history
        .get_mut("car0")
        .unwrap()
        .mileage_m = mileage;
    let saved = serde_json::to_string_pretty(&fixture).unwrap();
    let loaded = Game::load_json(c, &saved).unwrap();
    assert_eq!(
        loaded.frame_snapshot().career.vehicle_history["car0"]
            .mileage_m
            .to_bits(),
        mileage.to_bits()
    );
    assert_eq!(loaded.save_json().unwrap(), saved);
}

#[test]
// Keep staged setup explicit so fixture overrides and input sampling order remain visible.
#[allow(clippy::field_reassign_with_default)]
fn native_nitrous_uses_mutable_force_refill_and_drain_parameters() {
    let p = Handling::default();
    let g = PhysicsGlobals::recovered_script_settings();
    let mut zero = g.clone();
    zero.nitrous_force_gain = 0.;
    let mut plain = VehicleState::default();
    let mut held = plain.clone();
    for _ in 0..60 {
        let input = PlayerInput {
            throttle: 1.,
            ..Default::default()
        };
        plain.step(&p, &g, input, 1. / 60.);
        held.step(
            &p,
            &zero,
            PlayerInput {
                nitrous: 1.,
                ..input
            },
            1. / 60.,
        );
    }
    assert_eq!(plain.velocity, held.velocity);
    assert_eq!(plain.engine_omega, held.engine_omega);
    assert!(held.native_nitrous.tank < held.native_nitrous.capacity);
    let mut state = NativeNitrousState::default();
    state.tank = 1.;
    state.refill_timer = 1.;
    state.refill_scale = 0.;
    state.refill(1., 1, false, 0.1);
    assert_eq!(state.tank, 1.);
    state.refill(0., 1, true, 1.);
    assert_eq!(state.tank, 1.02);
    state.tank = 3.5;
    state.drain_rate = 0.8;
    state.request(true);
    state.drain(1.);
    assert_eq!(state.tank, 2.7);
}

#[test]
fn retired_legacy_nitrous_stage_is_preserved_without_a_fake_purchase() {
    let c = content();
    let mut game = Game::new(c.clone());
    let custom = Customization {
        nitrous: 3,
        ..Default::default()
    };
    assert!(game.quote_customization(&custom).is_empty());
    game.command(GameCommand::Customize {
        car_id: "car0".into(),
        customization: custom,
    })
    .unwrap();
    assert!(game.frame_snapshot().cart.is_empty());
    assert_eq!(game.frame_snapshot().career.cash, 25000);
    assert_eq!(game.frame_snapshot().selected_customization.nitrous, 0);
    let mut legacy: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
    legacy.career.garage.get_mut("car0").unwrap().nitrous = 3;
    let loaded = Game::load_json(c, &serde_json::to_string(&legacy).unwrap()).unwrap();
    assert_eq!(loaded.frame_snapshot().career.garage["car0"].nitrous, 3);
}

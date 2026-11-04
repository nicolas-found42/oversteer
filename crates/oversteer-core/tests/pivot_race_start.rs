use oversteer_core::*;

fn grid_game() -> Game {
    let content = GameContent {
        cars: (0..7)
            .map(|i| CarDefinition {
                id: format!("car{i}"),
                ..Default::default()
            })
            .collect(),
        tracks: vec![TrackDefinition {
            points: vec![
                [0., 0., 0.],
                [0., 0., 250.],
                [200., 0., 250.],
                [200., 0., 0.],
            ],
            ..Default::default()
        }],
        events: vec![EventDefinition {
            opponents: 6,
            ..Default::default()
        }],
        ..Default::default()
    };
    let event = content.events[0].id.clone();
    let mut game = Game::new(content);
    game.command(GameCommand::StartRace {
        event_id: event,
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    game
}

#[test]
fn countdown_locks_every_racer_and_race_clock_despite_full_controls() {
    let mut game = grid_game();
    let initial = game.frame_snapshot().race.unwrap();
    for _ in 0..179 {
        game.advance(
            1. / 60.,
            PlayerInput {
                throttle: 1.,
                steering: 1.,
                nitrous: 1.,
                ..Default::default()
            },
        );
        let race = game.frame_snapshot().race.unwrap();
        assert!(race.countdown > 0.);
        assert_eq!(race.elapsed, 0.);
        for (racer, grid) in race.racers.iter().zip(&initial.racers) {
            assert_eq!(racer.position, grid.position);
            assert_eq!(racer.speed_kph, 0.);
        }
    }
}

#[test]
fn each_rival_has_its_own_presentation_without_player_upgrades() {
    let game = grid_game();
    let race = game.frame_snapshot().race.unwrap();
    let paints: std::collections::BTreeSet<_> = race.racers[1..]
        .iter()
        .map(|r| r.customization.paint.map(f32::to_bits))
        .collect();
    let plates: std::collections::BTreeSet<_> = race.racers[1..]
        .iter()
        .map(|r| r.customization.plate_text.as_str())
        .collect();
    assert_eq!(paints.len(), race.racers.len() - 1);
    assert_eq!(plates.len(), race.racers.len() - 1);
    assert!(!plates.contains(race.racers[0].customization.plate_text.as_str()));
    assert!(race.racers[1..].iter().all(|r| r.customization.engine == 0));
}

#[test]
fn all_rivals_launch_from_a_clear_straight_grid() {
    let mut game = grid_game();
    for _ in 0..360 {
        game.advance(
            1. / 60.,
            PlayerInput {
                throttle: 1.,
                ..Default::default()
            },
        );
    }
    let race = game.frame_snapshot().race.unwrap();
    for racer in &race.racers[1..] {
        assert!(
            racer.speed_kph > 15.,
            "{} stalled at {:.2} kph / {:.0} rpm",
            racer.name,
            racer.speed_kph,
            racer.rpm
        );
    }
}

#[test]
fn finished_rivals_clear_the_finish_line_while_the_player_is_still_racing() {
    let mut game = grid_game();
    let held = PlayerInput {
        brake: 1.,
        ..Default::default()
    };
    let mut first_finisher = None;
    for _ in 0..60 * 180 {
        game.advance(1. / 60., held);
        let race = game.frame_snapshot().race.unwrap();
        if let Some(index) = race.racers.iter().position(|r| r.finished) {
            first_finisher = Some((index, race.racers[index].clone()));
            break;
        }
    }
    let (index, classified) = first_finisher.expect("A rival must finish the circuit");
    assert_ne!(index, 0);
    for _ in 0..60 {
        game.advance(1. / 60., held);
    }
    let snapshot = game.frame_snapshot();
    assert_eq!(snapshot.screen, GameScreen::Race);
    let racer = &snapshot.race.as_ref().unwrap().racers[index];
    let moved = ((racer.position[0] - classified.position[0]).powi(2)
        + (racer.position[2] - classified.position[2]).powi(2))
    .sqrt();
    assert!(racer.finished);
    assert_eq!(racer.finish_time, classified.finish_time);
    assert_eq!(racer.drift_score, classified.drift_score);
    assert!(
        moved > 5.,
        "Finished rival moved only {moved} m in a second"
    );
}

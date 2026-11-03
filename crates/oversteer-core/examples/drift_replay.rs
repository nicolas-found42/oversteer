use oversteer_core::*;
fn main() {
    let source: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let controls: Vec<serde_json::Value> = serde_json::from_str(
        &std::fs::read_to_string("artifacts/juiced2-build/rome-drift-1m-host-3d-v1-controls.json")
            .unwrap(),
    )
    .unwrap();
    for (label, event, league) in [
        ("500k", "native_ca32970d_010", 2),
        ("1m", "native_c8c48fc7_035", 3),
    ] {
        let mut starter = source.clone();
        starter.cars.retain(|car| car.id == "GT4_SUBR0017");
        let game = Game::new(starter);
        let mut save: GameSave = serde_json::from_str(&game.save_json().unwrap()).unwrap();
        save.career.league = league;
        let mut game =
            Game::load_json(source.clone(), &serde_json::to_string(&save).unwrap()).unwrap();
        let prefix = format!("artifacts/juiced2-build/rome-drift-{label}-3d-v1-replay");
        std::fs::write(
            format!("{prefix}-initial-save.json"),
            game.save_json().unwrap(),
        )
        .unwrap();
        game.command(GameCommand::StartRace {
            event_id: event.into(),
            career: true,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        std::fs::write(
            format!("{prefix}-initial-snapshot.json"),
            serde_json::to_vec(&game.frame_snapshot()).unwrap(),
        )
        .unwrap();
        for row in &controls {
            game.advance(
                1. / 60.,
                serde_json::from_value(row["input"].clone()).unwrap(),
            );
        }
        let snapshot = game.frame_snapshot();
        assert!(snapshot.result.as_ref().unwrap().won);
        std::fs::write(format!("{prefix}-save.json"), game.save_json().unwrap()).unwrap();
        std::fs::write(
            format!("{prefix}-final-snapshot.json"),
            serde_json::to_vec(&snapshot).unwrap(),
        )
        .unwrap();
        println!("{label}: {:?}", snapshot.result);
    }
}

use oversteer_core::*;

fn main() {
    let event = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "oversteer-0-circuit".into());
    let mut content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("godot/assets/game-content.json").unwrap())
            .unwrap();
    content.apply_oversteer_vehicle_corrections();
    content.apply_oversteer_career().unwrap();
    let mut game = Game::new(content);
    game.command(GameCommand::SetDifficulty { level: 0 })
        .unwrap();
    if event.ends_with("drift") {
        game.command(GameCommand::BuyCar {
            car_id: "GT4_MAZD0012".into(),
        })
        .unwrap();
    }
    let drift = event.ends_with("drift");
    game.command(GameCommand::StartRace {
        event_id: event,
        career: true,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
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
    println!("{}", serde_json::to_string_pretty(&serde_json::json!({
        "screen": snapshot.screen, "result": snapshot.result,
        "career": snapshot.career, "race": snapshot.race,
        "method": "Regular player inputs only; no pose, score or progress injection. Easy difficulty."
    })).unwrap());
}

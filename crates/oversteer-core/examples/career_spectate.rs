use oversteer_core::*;
fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let initial = std::fs::read_to_string(&args[0]).unwrap();
    let event = content.events.iter().find(|e| e.id == args[1]).unwrap();
    let length = content
        .tracks
        .iter()
        .find(|t| t.id == event.track_id)
        .unwrap()
        .points
        .len();
    let laps = event.laps;
    let event_id = event.id.clone();
    let mut game = Game::load_json(content, &initial).unwrap();
    game.command(GameCommand::Navigate {
        screen: GameScreen::Career,
    })
    .unwrap();
    game.command(GameCommand::StartSpectating {
        event_id: event_id.clone(),
    })
    .unwrap();
    let mut bet = false;
    for _ in 0..60 * 1800 {
        let snapshot = game.frame_snapshot();
        let race = snapshot.race.unwrap();
        if !bet && race.countdown <= 0. {
            let (index, leader) = race
                .racers
                .iter()
                .enumerate()
                .filter(|(_, r)| !r.eliminated)
                .max_by(|(_, a), (_, b)| a.progress.total_cmp(&b.progress))
                .unwrap();
            if leader.lap >= laps.saturating_sub(1) && leader.checkpoint + 15 >= length {
                let amount = args
                    .get(2)
                    .and_then(|value| value.parse::<u32>().ok())
                    .unwrap_or(50000)
                    .min(snapshot.career.cash as u32);
                game.command(GameCommand::PlaceSpectatorBet {
                    racer: index,
                    amount,
                })
                .unwrap();
                println!(
                    "BET racer{index} amount{amount} time{} odds{}",
                    race.elapsed, race.spectator_odds[index]
                );
                bet = true;
            }
        }
        game.advance(1. / 60., PlayerInput::default());
        if game.frame_snapshot().screen == GameScreen::Results {
            break;
        }
    }
    let snapshot = game.frame_snapshot();
    println!(
        "RESULT {:?} cash{} goals{}/{} open{}",
        snapshot.result,
        snapshot.career.cash,
        snapshot.league_progress.optional_completed,
        snapshot.league_progress.optional_required,
        snapshot.league_progress.promotion_open
    );
    let prefix = format!("artifacts/juiced2-build/career-spectator-{event_id}");
    std::fs::write(format!("{prefix}-initial-save.json"), initial).unwrap();
    std::fs::write(format!("{prefix}-save.json"), game.save_json().unwrap()).unwrap();
    std::fs::write(
        format!("{prefix}-final-snapshot.json"),
        serde_json::to_vec(&snapshot).unwrap(),
    )
    .unwrap();
}

use oversteer_core::*;
use std::collections::VecDeque;
fn main() {
    let mut c: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let track_id = std::env::args()
        .nth(1)
        .unwrap_or("alps_alps_masterworld1".into());
    let track = c.tracks.iter().find(|t| t.id == track_id).unwrap().clone();
    let world = NativeCollisionWorld::new(track.collision.as_ref().unwrap()).unwrap();
    c.events = vec![EventDefinition {
        id: "trace".into(),
        track_id: track.id.clone(),
        opponents: 0,
        ..Default::default()
    }];
    let mut game = Game::new(c);
    game.command(GameCommand::StartRace {
        event_id: "trace".into(),
        career: false,
        wager: 0,
        pink_slip: false,
    })
    .unwrap();
    let mut history = VecDeque::new();
    let mut unsupported = 0;
    for frame in 0..60 * 600 {
        let input = game.scenario_player_ai_input();
        game.advance(1. / 60., input);
        let s = game.frame_snapshot();
        let race = s.race.unwrap();
        let p = &race.racers[0];
        let contacts = p.surface_contacts.iter().filter(|c| c.active).count();
        let line = format!(
            "t{:.3} cp{} pos{:?} v{:?} q{:?} contacts{} ground{:?} input{:?}",
            race.elapsed,
            p.checkpoint,
            p.position,
            p.velocity,
            p.rotation,
            contacts,
            world.ground(p.position, 10., 30.),
            input
        );
        if frame % 600 == 0 && p.checkpoint > 155 && p.checkpoint < 180 {
            println!("PERIODIC {line}");
        }
        history.push_back(line);
        if history.len() > 12 {
            history.pop_front();
        }
        if contacts < 2 {
            unsupported += 1;
        } else {
            unsupported = 0;
        }
        if unsupported == 1 {
            println!("FIRSTLOSS {}", history.back().unwrap());
        }
        if unsupported > 30 {
            for line in history {
                println!("{line}");
            }
            break;
        }
        if s.screen == GameScreen::Results {
            println!("RESULT {:?}", s.result);
            break;
        }
    }
}

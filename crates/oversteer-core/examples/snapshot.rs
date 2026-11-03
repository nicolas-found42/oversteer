use oversteer_core::*;
use std::time::Instant;
fn main() {
    let mut content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for track in &mut content.tracks {
        let path = format!(
            "artifacts/juiced2-build/collision/track-local/{}.json",
            track.id
        );
        track.collision =
            Some(serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap());
    }
    let game = Game::new(content);
    for frame in [false, true] {
        let start = Instant::now();
        let mut length = 0;
        for _ in 0..5 {
            let snap = if frame {
                game.frame_snapshot()
            } else {
                game.snapshot()
            };
            length = serde_json::to_string(&snap).unwrap().len();
        }
        println!(
            "{} bytes={} mean_ms={:.3}",
            if frame { "frame" } else { "full" },
            length,
            start.elapsed().as_secs_f64() * 200.
        );
    }
}

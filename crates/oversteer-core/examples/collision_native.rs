use oversteer_core::*;
fn main() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for track in content.tracks.iter() {
        let path = format!(
            "artifacts/juiced2-build/collision/track-local/{}.json",
            track.id
        );
        let def: NativeCollisionDefinition =
            serde_json::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();
        let world = NativeCollisionWorld::new(&def).unwrap();
        let mut hit = 0;
        let mut delta = 0.;
        for (p, surface) in track.points.iter().zip(&track.surface_points) {
            if let Some(ground) = world.ground(*p, 3., 3.) {
                hit += 1;
                delta += ground.height - surface[1];
            }
        }
        println!(
            "{} tris{} spline{} centerlinehits{}/{} meanVisualDelta{:.4} start{:?}",
            track.id,
            world.triangle_count,
            world.unresolved_spline_count,
            hit,
            track.points.len(),
            delta / hit.max(1) as f32,
            world.ground(track.points[0], 3., 3.)
        );
    }
}

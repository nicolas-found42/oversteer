use oversteer_core::*;
fn main() {
    let content: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    let track = content
        .tracks
        .iter()
        .find(|t| t.id == "rome_rome_masterworld_route2")
        .unwrap();
    let world = NativeCollisionWorld::new(track.collision.as_ref().unwrap()).unwrap();
    let car = &content.cars[0];
    let snapshot: GameSnapshot = serde_json::from_str(
        &std::fs::read_to_string(
            "artifacts/juiced2-build/career-native_28956449_000-final-snapshot.json",
        )
        .unwrap(),
    )
    .unwrap();
    let racer = &snapshot.race.as_ref().unwrap().racers[0];
    let speed =
        (racer.velocity[0] * racer.velocity[0] + racer.velocity[2] * racer.velocity[2]).sqrt();
    let forward = [racer.velocity[0] / speed, 0., racer.velocity[2] / speed];
    let left = [-forward[2], 0., forward[0]];
    for offset in [-8., -6., -4., -2., 0., 2., 4., 6., 8.] {
        let mut state = VehicleState::default();
        let old = [
            racer.position[0] + left[0] * offset,
            racer.position[1],
            racer.position[2] + left[2] * offset,
        ];
        state.position = [old[0] + forward[0] * 0.3, old[1], old[2] + forward[2] * 0.3];
        state.orientation = racer.rotation;
        state.velocity = forward.map(|v| v * 20.);
        let hit = world.resolve_chassis(&mut state, &car.handling, old);
        println!(
            "offset{offset} hit{hit} pos{:?} velocity{:?}",
            state.position, state.velocity
        );
    }
}

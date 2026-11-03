use oversteer_core::*;
fn main() {
    let c: GameContent =
        serde_json::from_str(&std::fs::read_to_string("data/juiced2/content.json").unwrap())
            .unwrap();
    for car in c
        .cars
        .iter()
        .filter(|c| ["GT4_HOND0018", "GT4_MAZD0012", "GT4_SUBR0017"].contains(&c.id.as_str()))
    {
        let mut v = VehicleState::default();
        for i in 0..1200 {
            v.step(
                &car.handling,
                &PhysicsGlobals::recovered_script_settings(),
                PlayerInput {
                    throttle: 1.,
                    ..Default::default()
                },
                1. / 60.,
            );
            if i % 60 == 0 {
                println!(
                    "{} t{} kph{:.2} gear{} rpm{:.0} clutch{} pending{} ω{:?}",
                    car.id,
                    i / 60,
                    v.speed() * 3.6,
                    v.gear,
                    v.engine_omega * 9.549296,
                    v.clutch_engaged,
                    v.clutch_pending,
                    v.wheel_omega
                );
            }
        }
    }
}

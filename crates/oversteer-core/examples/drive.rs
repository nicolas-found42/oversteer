use oversteer_core::*;
fn main() {
    let mut v = VehicleState::default();
    for i in 0..1800 {
        v.step(
            &Handling::default(),
            &PhysicsGlobals::default(),
            PlayerInput {
                throttle: 0.8,
                steering: if i > 300 { 0.5 } else { 0. },
                ..Default::default()
            },
            1. / 60.,
        );
        if i % 300 == 0 {
            println!(
                "{i} {} {} {:?} yawrate{} wheels{:?}",
                v.speed(),
                v.yaw(),
                v.position,
                v.yaw_rate,
                v.wheel_omega
            );
        }
    }
}

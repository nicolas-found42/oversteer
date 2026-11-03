use crate::PlayerInput;
use serde::{Deserialize, Serialize};

/// Native 82114BD8 globals. Mutable shared_damping is written by drift-mode calls.
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct HumanDriftGlobals {
    pub shared_damping: f32,
    pub throttle_acceleration: f32,
    pub speed_floor: f32,
}
impl Default for HumanDriftGlobals {
    fn default() -> Self {
        Self {
            shared_damping: 2.,
            throttle_acceleration: 0.,
            speed_floor: 0.,
        }
    }
}

/// Actor fields 796/800/804/816 in the recovered human-control routine.
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct HumanDriftState {
    pub yaw_control: f32,
    pub visual_steering: f32,
    pub blend: f32,
    pub handbrake_timer: f32,
}
#[derive(Clone, Copy, Debug)]
pub struct HumanDriftMotion {
    pub world_velocity: [f32; 3],
    pub body_angular_velocity: [f32; 3],
    /// The normalized-forward source transform axis, before normalization here.
    pub forward_axis: [f32; 3],
    pub right_axis: [f32; 3],
    /// 820F7F18's clamped angle, not an unbounded backwards-facing slip angle.
    pub score_angle: f32,
    /// Actor680: time with fewer than two supporting wheels (820F5480/82111E50).
    pub airborne_time: f32,
}
impl HumanDriftState {
    /// Exact scalar/vector sequence from 82114BD8; caller owns the native motion setters.
    pub fn advance(
        &mut self,
        globals: &mut HumanDriftGlobals,
        input: PlayerInput,
        dt: f32,
        drift_mode: bool,
        mut motion: HumanDriftMotion,
    ) -> HumanDriftMotion {
        let speed = motion
            .world_velocity
            .iter()
            .map(|v| v * v)
            .sum::<f32>()
            .sqrt();
        let excess = (speed - globals.speed_floor).max(0.);
        let gain = if drift_mode {
            globals.shared_damping = 1.;
            2.
        } else {
            if input.handbrake == 1. {
                self.handbrake_timer = 0.75;
            } else if self.handbrake_timer > 0. {
                self.handbrake_timer = (self.handbrake_timer - dt).max(0.);
            }
            0.75 + self.handbrake_timer
        };
        self.blend =
            ((motion.score_angle.abs() - 0.02) * gain * (excess * 0.06666667014360428).min(1.))
                .clamp(0., 1.);
        let mut acceleration = [0.; 3];
        if input.throttle > 0. {
            let norm = motion
                .forward_axis
                .iter()
                .map(|v| v * v)
                .sum::<f32>()
                .sqrt()
                + f32::EPSILON;
            let force = globals
                .throttle_acceleration
                .mul_add(input.throttle, self.blend * 45.);
            for i in 0..3 {
                acceleration[i] = motion.forward_axis[i] / norm * 0.02 * force;
            }
            if input.throttle >= 0.9900000095367432 {
                self.yaw_control =
                    (dt * self.blend * motion.score_angle.signum()).mul_add(-15., self.yaw_control);
            }
        }
        let limit = (1. - self.blend).mul_add(90., 45.);
        if excess > limit {
            for v in &mut motion.world_velocity {
                *v = *v / (speed + f32::EPSILON) * limit;
            }
        }
        for i in 0..3 {
            motion.world_velocity[i] += acceleration[i] * dt * 25.;
        }
        if !drift_mode {
            self.blend *= self.blend;
        }
        let high_speed = if !drift_mode && excess > 40. {
            let x = (excess - 40.) * 0.025;
            0.5 / x.mul_add(x, 0.5)
        } else {
            1.
        };
        self.yaw_control = ((input.handbrake + 1.) * input.steering * dt * high_speed)
            .mul_add(170., self.yaw_control);
        let damping = (globals.shared_damping / (globals.shared_damping + excess))
            .mul_add(-(1. - self.blend), 1.);
        self.yaw_control = (self.yaw_control * damping).clamp(-100., 100.);
        let yaw_target = self.yaw_control * 0.02;
        motion.body_angular_velocity[1] =
            (1. - self.blend).mul_add(motion.body_angular_velocity[1], self.blend * yaw_target);
        let angular_decay = if motion.airborne_time > 0. {
            10.
        } else if input.steering == 0. && !drift_mode {
            4.
        } else {
            0.
        };
        let angular_damping = (1. - dt * angular_decay).clamp(0., 1.);
        motion.body_angular_velocity[1] *= angular_damping;
        motion.body_angular_velocity[2] *= angular_damping;
        if drift_mode {
            // The caller refreshes local slip after the world-velocity setter.
            let steering = if input.steering != 0. {
                input.steering
            } else {
                self.blend * {
                    let lateral = motion
                        .right_axis
                        .iter()
                        .zip(motion.world_velocity)
                        .map(|(a, b)| a * b)
                        .sum::<f32>();
                    let forward = motion
                        .forward_axis
                        .iter()
                        .zip(motion.world_velocity)
                        .map(|(a, b)| a * b)
                        .sum::<f32>();
                    lateral.atan2(forward).clamp(-0.8, 0.8)
                }
            };
            self.visual_steering = steering.mul_add(0.2, self.visual_steering * 0.8);
        }
        motion
    }
}

/// Native 820F7290: mode-specific TyreMu replacement, independent of handbrake.
pub fn native_drift_tyre_mu(
    base: [f32; 2],
    layout: crate::DriveLayout,
    speed: f32,
    drift_mode: bool,
    forward_gear: bool,
) -> [f32; 2] {
    if !drift_mode || speed < 10. || !forward_gear {
        return base;
    }
    [
        base[0]
            * if layout == crate::DriveLayout::Rwd {
                0.550000011920929
            } else {
                0.8999999761581421
            },
        base[1] * 0.550000011920929,
    ]
}

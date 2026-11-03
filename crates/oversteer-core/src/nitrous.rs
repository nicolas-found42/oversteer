use serde::{Deserialize, Serialize};

pub fn native_nitrous_capacity(control: f32) -> f32 {
    if control == -2. {
        5.
    } else {
        control.mul_add(3., 2.)
    }
}
pub fn native_nitrous_pressure(fraction: f32) -> (u8, f32) {
    if fraction == 1. {
        (4, 1.4)
    } else if fraction > 0.66 {
        (3, 1.)
    } else if fraction > 0.33 {
        (2, 0.7)
    } else {
        (1, 0.3)
    }
}
pub fn native_nitrous_wheel_ratio(point_velocity: [f32; 3], residual_x: f32, contact: bool) -> f32 {
    let speed = point_velocity[2]
        .mul_add(
            point_velocity[2],
            point_velocity[0].mul_add(point_velocity[0], point_velocity[1] * point_velocity[1]),
        )
        .sqrt();
    if contact && speed > 4. {
        (residual_x * (1. / speed)).abs().clamp(0., 1.)
    } else {
        0.
    }
}
pub fn native_nitrous_metric(ratios: [f32; 4]) -> f32 {
    let mut total = 0.;
    for ratio in ratios {
        total += ratio;
        total += ratio;
    }
    total * 0.25
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct NativeNitrousState {
    pub drain_rate: f32,
    pub force_gain: f32,
    pub refill_scale: f32,
    pub tank: f32,
    pub capacity: f32,
    pub activation_tank: f32,
    pub active: bool,
    pub pressure_band: u8,
    pub refill_timer: f32,
}
impl Default for NativeNitrousState {
    fn default() -> Self {
        Self {
            drain_rate: 0.4,
            force_gain: 13600.,
            refill_scale: 0.04,
            tank: 3.5,
            capacity: 3.5,
            activation_tank: 3.5,
            active: false,
            pressure_band: 1,
            refill_timer: 0.,
        }
    }
}
impl NativeNitrousState {
    pub fn configure(&mut self, control: f32) {
        let capacity = native_nitrous_capacity(control);
        if capacity != self.capacity {
            *self = Self {
                tank: capacity,
                capacity,
                activation_tank: capacity,
                ..Self::default()
            };
        }
    }
    pub fn fraction(&self) -> f32 {
        self.tank / self.capacity
    }
    pub fn request(&mut self, active: bool) {
        if active && !self.active {
            self.activation_tank = self.tank;
            self.pressure_band = 1;
        }
        self.active = active;
    }
    /// 82260108: once per local physics interval, before RK force evaluations.
    pub fn drain(&mut self, h: f32) {
        if self.active {
            self.tank = -self.drain_rate.mul_add(h, -self.tank);
            if self.tank < 0. {
                self.tank = 0.;
            }
            // 820F82D0 stops the gameplay activation when the tank is empty.
            if self.tank <= 0. {
                self.tank = 0.;
                self.active = false;
            }
        }
    }
    pub fn force(
        &mut self,
        throttle: f32,
        power: f32,
        contact_count: usize,
        forward_gear: bool,
    ) -> f32 {
        if !self.active || self.tank <= 0. || contact_count <= 1 {
            return 0.;
        }
        let (band, pressure) = native_nitrous_pressure(self.activation_tank / self.capacity);
        self.pressure_band = band;
        if !forward_gear {
            return 0.;
        }
        ((throttle * pressure) * power) * self.force_gain
    }
    /// 820F82D0 gameplay refill; caller invokes once after the object's world step.
    pub fn refill(&mut self, metric: f32, mode: u8, extreme: bool, h: f32) {
        if metric > 0.2 && !self.active && self.tank < self.capacity {
            self.refill_timer += h;
            if self.refill_timer > 0.3 {
                let coefficient = if mode == 2 { 25. } else { 12. };
                let rate = (metric * coefficient) * h;
                self.tank = rate
                    .mul_add(self.refill_scale, self.tank)
                    .min(self.capacity);
            }
        } else {
            self.refill_timer = 0.;
        }
        if extreme && !self.active {
            self.tank = h.min(0.06666667).mul_add(0.3, self.tank).min(self.capacity);
        }
    }
}

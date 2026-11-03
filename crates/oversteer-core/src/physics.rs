use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct PlayerInput {
    pub throttle: f32,
    pub brake: f32,
    pub steering: f32,
    pub handbrake: f32,
    pub nitrous: f32,
    pub shift: i8,
    pub reverse: bool,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default, Serialize, Deserialize)]
pub enum DriveLayout {
    Fwd,
    #[default]
    Rwd,
    Awd,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct Handling {
    pub nitrous_capacity_control: f32,
    pub nitrous_engine_multiplier: f32,
    pub nitrous_power_factor: f32,
    pub max_spring_compression: f32,
    pub rear_max_spring_compression: Option<f32>,
    pub rear_spring_rate: Option<f32>,
    pub rear_damping_ratio: Option<f32>,
    pub rear_tyre_mu: Option<f32>,
    pub rear_wheel_radius: Option<f32>,
    pub body_length: f32,
    pub body_width: f32,
    pub body_height: f32,
    /// Measured donor body underside above the wheel-ground origin; query proxy only.
    pub body_min_y: f32,
    pub inertia_scalar: f32,
    pub footbrake_mu: f32,
    pub handbrake_mu: f32,
    pub axle_mu: f32,
    pub clutch_time: f32,
    pub front_diff_slip: f32,
    pub rear_diff_slip: f32,
    pub centre_diff_slip: f32,
    pub mass: f32,
    pub wheelbase: f32,
    pub track_width: f32,
    pub wheel_radius: f32,
    pub front_weight: f32,
    pub peak_torque: f32,
    pub peak_torque_rpm: f32,
    pub peak_bhp: f32,
    pub peak_bhp_rpm: f32,
    pub redline: f32,
    pub engine_size: f32,
    pub gears: Vec<f32>,
    pub final_drive: f32,
    pub layout: DriveLayout,
    pub max_steer: f32,
    pub tyre_mu: f32,
    pub spring_rate: f32,
    pub damping_ratio: f32,
    pub drag: f32,
    pub abs: bool,
    pub shift_duration: f32,
    pub provenance: String,
}
impl Default for Handling {
    fn default() -> Self {
        Self {
            nitrous_capacity_control: 0.5,
            nitrous_engine_multiplier: 1.,
            nitrous_power_factor: 1.,
            max_spring_compression: 0.4,
            rear_max_spring_compression: None,
            rear_spring_rate: None,
            rear_damping_ratio: None,
            rear_tyre_mu: None,
            rear_wheel_radius: None,
            body_length: 4.2,
            body_width: 1.7,
            body_height: 1.45,
            body_min_y: 0.,
            inertia_scalar: 1.,
            footbrake_mu: 10000.,
            handbrake_mu: 10000.,
            axle_mu: 10.,
            clutch_time: 0.3,
            front_diff_slip: 1.,
            rear_diff_slip: 1.,
            centre_diff_slip: 1.,
            mass: 1250.,
            wheelbase: 2.6,
            track_width: 1.5,
            wheel_radius: 0.32,
            front_weight: 0.55,
            peak_torque: 250.,
            peak_torque_rpm: 4000.,
            peak_bhp: 220.,
            peak_bhp_rpm: 6000.,
            redline: 7000.,
            engine_size: 2000.,
            gears: vec![3.2, 2.1, 1.5, 1.15, 0.9, 0.75],
            final_drive: 4.1,
            layout: DriveLayout::Rwd,
            max_steer: 0.7799999713897705,
            tyre_mu: 1.1,
            spring_rate: 35000.,
            damping_ratio: 0.6,
            drag: 0.4,
            abs: true,
            shift_duration: 0.18,
            provenance: "Adapted default; not an original vehicle tune".into(),
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct PhysicsGlobals {
    pub nitrous_force_gain: f32,
    pub nitrous_refill_scale: f32,
    pub skid_mu_scalar: f32,
    pub slip_mu_scalar: f32,
    pub slip_point: f32,
    pub gravity: f32,
    pub steering_speed: f32,
    pub engine_torque_scalar: f32,
    pub engine_inertia_scalar: f32,
    pub engine_braking_scalar: f32,
    pub tyre_mu_scalar: f32,
    pub cornering_mu_scalar: f32,
    pub tyre_stiffness: f32,
    pub cornering_stiffness: f32,
    pub camber_stiffness: f32,
    pub tyre_shape: f32,
    pub response_curve: Vec<[f32; 2]>,
    pub abs_threshold: f32,
    pub wheel_radius_base: f32,
    pub wheel_rim_inches: f32,
}
impl Default for PhysicsGlobals {
    fn default() -> Self {
        let mut g = Self {
            nitrous_force_gain: 13600.,
            nitrous_refill_scale: 0.04,
            skid_mu_scalar: 1.,
            slip_mu_scalar: 0.4000000059604645,
            slip_point: 5.,
            gravity: -9.8,
            steering_speed: 3.,
            engine_torque_scalar: 1.,
            engine_inertia_scalar: 0.00025,
            engine_braking_scalar: 0.1,
            tyre_mu_scalar: 1.,
            cornering_mu_scalar: 1.,
            tyre_stiffness: 30000.,
            cornering_stiffness: 30000.,
            camber_stiffness: 60000.,
            tyre_shape: 0.,
            response_curve: vec![],
            abs_threshold: 0.,
            wheel_radius_base: 0.12300000339746475,
            wheel_rim_inches: 16.,
        };
        g.initialize_tyre_curve();
        g
    }
}
impl PhysicsGlobals {
    /// Extracted global settings record a86bbf42 (SHA a202f542a80cdcd0bbe9032824adfcaa9a44771357aa064391a84809b87f3256).
    /// Runtime load/override order is unobserved; this selects the recovered script rather than constructor priors.
    pub fn recovered_script_settings() -> Self {
        Self {
            slip_point: 6.400000095367432,
            tyre_mu_scalar: 2.5,
            cornering_mu_scalar: 2.,
            tyre_stiffness: 120000.,
            cornering_stiffness: 270000.,
            camber_stiffness: 80000.,
            engine_torque_scalar: 1.75,
            engine_inertia_scalar: 0.0003499999875202775,
            engine_braking_scalar: 0.07000000029802322,
            ..Self::default()
        }
    }
    /// 8226CC28: inertia derived from mutable radius-like globals, not chassis mass.
    pub fn wheel_inertia(&self) -> f32 {
        let radius = self
            .wheel_rim_inches
            .abs()
            .mul_add(0.01269999984651804, self.wheel_radius_base);
        let mass = (radius * radius * 0.644026517868042) * 300.;
        ((mass * radius) * radius) * 0.5
    }
    /// 8226D028: shared, mutable curve; callers may reinitialize it per object.
    pub fn initialize_tyre_curve(&mut self) {
        self.response_curve.clear();
        self.response_curve.push([0., tyre_response(0.)]);
        let mut x = 0.3f32;
        while x < 3.0999999 {
            self.response_curve.push([x, tyre_response(x)]);
            x += 0.3;
        }
        for i in 4..=15 {
            self.response_curve
                .push([i as f32, tyre_response(i as f32)]);
        }
        self.response_curve.push([1000., tyre_response(1000.)]);
        let mut best = 0.;
        self.abs_threshold = 0.;
        for [x, y] in &self.response_curve {
            if *y > best {
                best = *y;
                self.abs_threshold = *x;
            }
        }
    }
}
/// 82272040. Local interval subdivision, not a claim about the upstream native clock.
pub fn substeps(delta: f32) -> (usize, f32) {
    let dt = delta.min(0.2);
    let n = if dt > 0.1 {
        3
    } else if dt > 0.05 {
        2
    } else {
        1
    };
    (n, dt / n as f32)
}
/// 8225B550, with ordered knots supplied by the native construction path.
pub fn curve(knots: &[[f32; 2]], x: f32) -> f32 {
    if knots.is_empty() || x < knots[0][0] {
        return 0.;
    }
    for w in knots.windows(2) {
        if x < w[1][0] {
            return w[0][1] + (w[1][1] - w[0][1]) * (x - w[0][0]) / (w[1][0] - w[0][0]);
        }
    }
    knots.last().unwrap()[1]
}
/// 8226C920. Rust libm helper identities remain an explicitly documented adaptation.
pub fn tyre_response(x: f32) -> f32 {
    (1.39999998 * (0.713999987 * (1.20000005 * x - 0.280112058 * (0.713999987 * x).atan())).atan())
        .sin()
}
pub fn damping_coefficient(mass_channel: f32, spring_rate: f32, ratio: f32) -> f32 {
    2. * ratio * (mass_channel * spring_rate).sqrt()
}
pub fn suspension_load(
    load: f32,
    damping: f32,
    velocity: f32,
    max_compression: f32,
    spring_rate: f32,
) -> f32 {
    (load - damping * velocity).clamp(0., 1.2000000476837158 * max_compression * spring_rate)
}
pub fn steering_slew(current: f32, target: f32, h: f32, speed: f32) -> f32 {
    let mut c = current;
    if c * target < 0. {
        c = 0.;
    }
    if c.abs() < target.abs() {
        let step = speed * h;
        if target > c {
            c = (c + step).min(target)
        } else {
            c = (c - step).max(target)
        }
    } else {
        c = target
    }
    c
}
pub fn torque_curve(p: &Handling, rpm: f32) -> f32 {
    let fourth = if p.peak_torque == 0. || p.peak_bhp_rpm == 0. {
        0.
    } else {
        7120.75586 * p.peak_bhp / (p.peak_bhp_rpm * p.peak_torque)
    };
    let mut knots = vec![
        [0., 0.],
        [1000., 0.699999988],
        [p.peak_torque_rpm, 1.],
        [p.peak_bhp_rpm, fourth],
        [1.12 * p.redline, -0.100000001],
    ];
    knots.sort_by(|a, b| a[0].total_cmp(&b[0]));
    curve(&knots, rpm)
}
pub fn engine_inertia(p: &Handling, g: &PhysicsGlobals) -> f32 {
    p.engine_size.min(3500.) * g.engine_inertia_scalar
}
pub fn longitudinal_slip(omega: f32, radius: f32, speed: f32, angle: f32) -> f32 {
    if angle.abs() < 1.57079637 {
        radius * omega.abs() / (speed * angle.cos() + f32::EPSILON) - 1.
    } else {
        100.
    }
}
/// 8226D6F8's combined tyre core. Zero-load contacts must be filtered by the caller.
pub fn combined_tyre_force(
    load: f32,
    mu: f32,
    slip: f32,
    angle: f32,
    camber: f32,
    g: &PhysicsGlobals,
) -> [f32; 3] {
    // D6F8 reflects negative camber/angle before the positive camber clamp,
    // then reflects only lateral force back on return.
    let reflected = camber < 0.;
    let angle = if reflected { -angle } else { angle };
    let t = angle.tan();
    let b =
        (g.camber_stiffness * camber.abs() / (load * mu * g.cornering_mu_scalar)).min(0.949999988);
    let a =
        g.cornering_stiffness * t / (load * mu * g.cornering_mu_scalar) / (1. - angle.signum() * b);
    let q = g.tyre_stiffness * slip / (load * mu * g.tyre_mu_scalar);
    let r = (a * a + q * q).sqrt();
    let shape = if r <= 6.2831854820251465 {
        (1. + g.tyre_shape) / 2. - (1. - g.tyre_shape) * (r / 2.).cos() / 2.
    } else {
        1.
    };
    let response = curve(&g.response_curve, r);
    let denom = (shape * shape * t * t + slip * slip).sqrt() + f32::EPSILON;
    [
        load * mu * g.tyre_mu_scalar * slip * response / denom,
        load * mu
            * g.cornering_mu_scalar
            * ((response * shape * t / denom - b) / (1. - angle.signum() * b))
            * if reflected { -1. } else { 1. },
        r,
    ]
}
/// Recovered BODY-space contact channels from8226D560/8226DE08/8226DF90.
#[derive(Clone, Copy, Debug)]
pub struct NativeWheelFrame {
    pub lateral_axis: [f32; 3],
    pub longitudinal_axis: [f32; 3],
    pub tangent_velocity: [f32; 3],
    pub speed: f32,
    pub angle: f32,
    pub forward_speed: f32,
    pub camber: f32,
}

pub fn native_wheel_frame(
    normal: [f32; 3],
    point_velocity: [f32; 3],
    steer: f32,
    omega: f32,
) -> NativeWheelFrame {
    let (lateral_axis, longitudinal_axis) = if steer == 0. {
        // Literal native fast path: unlike the nonzero branch, these are NOT projected.
        ([1., 0., 0.], [0., 0., 1.])
    } else {
        let c = f64::from(steer).cos() as f32;
        let s = f64::from(steer).sin() as f32;
        let project_axis = |axis: [f32; 3], longitudinal: bool| {
            let xz = if longitudinal {
                normal[0].mul_add(axis[0], normal[2] * axis[2])
            } else {
                normal[2].mul_add(axis[2], normal[0] * axis[0])
            };
            let dot = normal[1].mul_add(axis[1], xz);
            let projected = std::array::from_fn::<_, 3, _>(|i| axis[i] - normal[i] * dot);
            let norm = projected[2]
                .mul_add(
                    projected[2],
                    projected[0].mul_add(projected[0], projected[1] * projected[1]),
                )
                .sqrt()
                + f32::EPSILON;
            let inverse = 1. / norm;
            projected.map(|component| component * inverse)
        };
        (
            project_axis([c, 0., -s], false),
            project_axis([s, 0., c], true),
        )
    };
    let normal_speed = point_velocity[2].mul_add(
        normal[2],
        point_velocity[0].mul_add(normal[0], point_velocity[1] * normal[1]),
    );
    let tangent_velocity =
        std::array::from_fn::<_, 3, _>(|i| point_velocity[i] - normal[i] * normal_speed);
    let speed = tangent_velocity[2]
        .mul_add(
            tangent_velocity[2],
            tangent_velocity[0].mul_add(
                tangent_velocity[0],
                tangent_velocity[1] * tangent_velocity[1],
            ),
        )
        .sqrt();
    let sign = if omega < 0. { -1. } else { 1. };
    let heading =
        f64::from(tangent_velocity[0] * sign).atan2(f64::from(tangent_velocity[2] * sign)) as f32;
    let angle = if steer == 0. {
        -heading
    } else {
        (f64::from(longitudinal_axis[0]).atan2(f64::from(longitudinal_axis[2])) as f32) - heading
    };
    let forward_speed = speed * (f64::from(angle).cos() as f32) * sign;
    let camber = if omega < 0. || normal[0].abs() > 0.3400000035762787 {
        0.
    } else {
        normal[0]
    };
    NativeWheelFrame {
        lateral_axis,
        longitudinal_axis,
        tangent_velocity,
        speed,
        angle,
        forward_speed,
        camber,
    }
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct SurfaceContact {
    /// Sampled world-plane origin X/Z; height supplies its Y coordinate.
    #[serde(default)]
    pub anchor_xz: [f32; 2],
    pub height: f32,
    pub normal: [f32; 3],
    pub grip: f32,
    pub active: bool,
}
impl Default for SurfaceContact {
    fn default() -> Self {
        Self {
            anchor_xz: [0.; 2],
            height: 0.,
            normal: [0., 1., 0.],
            grip: 1.,
            active: true,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VehicleState {
    #[serde(default)]
    pub native_nitrous: crate::NativeNitrousState,
    #[serde(default)]
    pub nitrous_allowed: bool,
    #[serde(default)]
    pub extreme_nos: bool,
    #[serde(default)]
    pub nitrous_control_mode: u8,
    #[serde(default)]
    nitrous_refill_metric: f32,
    #[serde(default)]
    nitrous_body_force: f32,
    pub wheel_angles: [f32; 4],
    pub wheel_steer_angles: [f32; 4],
    pub handbrake: f32,
    pub clutch_engaged: bool,
    pub clutch_timer: f32,
    pub clutch_pending: bool,
    pub clutch_launch: bool,
    pub position: [f32; 3],
    pub velocity: [f32; 3],
    pub orientation: [f32; 4],
    pub yaw_rate: f32,
    pub engine_omega: f32,
    pub wheel_omega: [f32; 4],
    pub gear: usize,
    pub steering: f32,
    pub nitrous: f32,
    pub slip_angle: f32,
    pub distance: f32,
    pub shift_timer: f32,
    pub reversing: bool,
    pub roll_rate: f32,
    pub pitch_rate: f32,
    pub contacts: [SurfaceContact; 4],
}
impl Default for VehicleState {
    fn default() -> Self {
        Self {
            native_nitrous: crate::NativeNitrousState::default(),
            nitrous_allowed: true,
            extreme_nos: false,
            nitrous_control_mode: 1,
            nitrous_refill_metric: 0.,
            nitrous_body_force: 0.,
            wheel_angles: [0.; 4],
            wheel_steer_angles: [0.; 4],
            handbrake: 0.,
            clutch_engaged: false,
            clutch_timer: 0.,
            clutch_pending: false,
            clutch_launch: false,
            position: [0.; 3],
            velocity: [0.; 3],
            orientation: [0., 0., 0., 1.],
            yaw_rate: 0.,
            engine_omega: 104.719757,
            wheel_omega: [0.; 4],
            gear: 1,
            steering: 0.,
            nitrous: 1.,
            slip_angle: 0.,
            distance: 0.,
            shift_timer: 0.,
            reversing: false,
            roll_rate: 0.,
            pitch_rate: 0.,
            contacts: [SurfaceContact::default(); 4],
        }
    }
}
impl VehicleState {
    pub fn yaw(&self) -> f32 {
        2. * self.orientation[1].atan2(self.orientation[3])
    }
    pub fn body_velocity(&self) -> [f32; 3] {
        let [x, y, z, w] = self.orientation;
        let v = self.velocity;
        [
            (1. - 2. * (y * y + z * z)) * v[0]
                + 2. * (x * y + w * z) * v[1]
                + 2. * (x * z - w * y) * v[2],
            2. * (x * y - w * z) * v[0]
                + (1. - 2. * (x * x + z * z)) * v[1]
                + 2. * (y * z + w * x) * v[2],
            2. * (x * z + w * y) * v[0]
                + 2. * (y * z - w * x) * v[1]
                + (1. - 2. * (x * x + y * y)) * v[2],
        ]
    }
    pub fn speed(&self) -> f32 {
        (self.velocity[0].mul_add(
            self.velocity[0],
            self.velocity[2].mul_add(self.velocity[2], self.velocity[1] * self.velocity[1]),
        ))
        .sqrt()
    }
    pub fn set_yaw(&mut self, yaw: f32) {
        self.orientation = [0., (yaw / 2.).sin(), 0., (yaw / 2.).cos()];
    }
    pub fn step(&mut self, p: &Handling, g: &PhysicsGlobals, input: PlayerInput, h: f32) {
        self.handbrake = input.handbrake.clamp(0., 1.);
        if self.speed() < 1. {
            self.reversing = input.reverse;
        }
        if self.reversing {
            self.gear = 1;
        }
        self.steering = steering_slew(
            self.steering,
            input.steering.clamp(-1., 1.),
            h,
            g.steering_speed,
        );
        self.wheel_steer_angles = [
            self.steering * p.max_steer,
            self.steering * p.max_steer,
            0.,
            0.,
        ];
        self.shift_timer = (self.shift_timer - h).max(0.);
        let rpm = self.engine_omega * 9.54929638;
        if self.shift_timer == 0. && !self.reversing {
            let shift = if input.shift != 0 {
                input.shift
            } else if self.clutch_engaged
                && input.brake <= 0.9
                && input.handbrake <= 0.9
                && rpm > p.redline * 0.93
                && self.gear < p.gears.len()
            {
                1
            } else if self.clutch_engaged
                && input.brake <= 0.9
                && input.handbrake <= 0.9
                && rpm < 2100.
                && self.gear > 1
            {
                -1
            } else {
                0
            };
            if shift != 0 {
                self.gear = (self.gear as i32 + shift as i32).clamp(1, p.gears.len().max(1) as i32)
                    as usize;
                self.shift_timer = p.shift_duration;
                self.clutch_engaged = false;
                self.clutch_pending = false;
                self.clutch_timer = 0.;
            }
        }
        let forward_velocity = self.body_velocity()[2];
        if input.brake > 0.9 || input.handbrake > 0.9 {
            self.clutch_engaged = false;
            self.clutch_pending = false;
            self.clutch_timer = 0.;
        } else if self.shift_timer == 0. {
            if !self.clutch_engaged
                && !self.clutch_pending
                && (input.throttle > 0. || forward_velocity > 10.)
            {
                self.clutch_pending = true;
                self.clutch_timer = 0.;
                self.clutch_launch = self.gear == 1
                    && self.driven_omega(p).abs() * self.gear_ratio(p).abs() < 104.719757;
            } else if input.throttle <= 0.
                && forward_velocity <= 10.
                && self.engine_omega < 104.719757 * 1.01
            {
                self.clutch_engaged = false;
                self.clutch_pending = false;
                self.clutch_timer = 0.;
            }
            if self.clutch_pending {
                self.clutch_timer += h;
                if self.clutch_timer > p.clutch_time {
                    if !self.clutch_launch {
                        self.engine_omega = self.driven_omega(p).abs() * self.gear_ratio(p).abs();
                    }
                    self.clutch_engaged = true;
                    self.clutch_pending = false;
                    self.clutch_timer = 0.;
                }
            }
        }
        self.native_nitrous.configure(p.nitrous_capacity_control);
        self.native_nitrous.force_gain = g.nitrous_force_gain;
        self.native_nitrous.refill_scale = g.nitrous_refill_scale;
        self.native_nitrous
            .request(input.nitrous > 0. && self.nitrous_allowed);
        self.native_nitrous.drain(h);
        let contacts = if self.native_nitrous.active {
            self.nitrous_contact_metrics(p, g).0
        } else {
            0
        };
        self.nitrous_body_force = self.native_nitrous.force(
            input.throttle.clamp(0., 1.),
            p.nitrous_power_factor,
            contacts,
            !self.reversing && self.gear > 0,
        );
        self.nitrous = self.native_nitrous.fraction();
        let boosted = self.native_nitrous.active && self.native_nitrous.tank > 0.;
        let mut u = input;
        u.throttle = u.throttle.clamp(0., 1.);
        u.brake = u.brake.clamp(0., 1.);
        if self.shift_timer > 0. {
            u.throttle = 0.;
        }
        u.nitrous = if boosted { 1. } else { 0. };
        // Dedicated RK4 includes each intermediate commit; engine clamp and driven axle constraints are nonlinear.
        let initial = self.channels(p);
        let k1 = self.derivative(p, g, u, h);
        self.commit(add(initial, k1, h * 0.5), p);
        let k2 = self.derivative(p, g, u, h);
        self.commit(add(initial, k2, h * 0.5), p);
        let k3 = self.derivative(p, g, u, h);
        self.commit(add(initial, k3, h), p);
        let k4 = self.derivative(p, g, u, h);
        // Preserve the last force-stage readout for the following gameplay update.
        self.nitrous_refill_metric = if self.nitrous_allowed
            && !self.native_nitrous.active
            && self.native_nitrous.tank < self.native_nitrous.capacity
        {
            self.nitrous_contact_metrics(p, g).1
        } else {
            0.
        };
        let mut final_state = initial;
        for i in 0..18 {
            final_state[i] += h * (k1[i] + 2. * k2[i] + 2. * k3[i] + k4[i]) * 0.1666666716337204;
        }
        self.commit(final_state, p);
        for i in 0..4 {
            self.wheel_angles[i] =
                (self.wheel_angles[i] + self.wheel_omega[i] * h).rem_euclid(std::f32::consts::TAU);
        }
        self.distance += self.speed() * h;
        let local_velocity = self.body_velocity();
        self.slip_angle = local_velocity[0].atan2(local_velocity[2]);
    }
    /// Source820F5480/82111E50 read the last force-stage wheel registers.
    pub fn update_nitrous_gameplay(&mut self, h: f32) {
        if self.nitrous_allowed {
            self.native_nitrous.refill(
                self.nitrous_refill_metric,
                self.nitrous_control_mode,
                self.extreme_nos,
                h,
            );
        }
        self.nitrous = self.native_nitrous.fraction();
    }
    fn nitrous_contact_metrics(&self, p: &Handling, g: &PhysicsGlobals) -> (usize, f32) {
        let body = self.body_velocity();
        let mut contacts = 0;
        let ratios = std::array::from_fn(|i| {
            let contact = self.contacts[i];
            if !contact.active {
                return 0.;
            }
            let front = i < 2;
            let weight = if front {
                p.front_weight * 0.5
            } else {
                (1. - p.front_weight) * 0.5
            };
            let x = if i % 2 == 0 {
                -p.track_width / 2.
            } else {
                p.track_width / 2.
            };
            let z = if front {
                p.wheelbase * (1. - p.front_weight)
            } else {
                -p.wheelbase * p.front_weight
            };
            let point = [
                body[0] + self.yaw_rate * z,
                body[1] + x * self.roll_rate - z * self.pitch_rate,
                body[2] - self.yaw_rate * x,
            ];
            let normal = inverse_rotate(self.orientation, contact.normal);
            let q = self.orientation;
            let arm = inverse_rotate([-q[0], -q[1], -q[2], q[3]], [x, 0., z]);
            let world_point =
                std::array::from_fn::<_, 3, _>(|axis| self.position[axis] + arm[axis]);
            let delta = [
                contact.anchor_xz[0] - world_point[0],
                contact.height - world_point[1],
                contact.anchor_xz[1] - world_point[2],
            ];
            let penetration = contact.normal[0].mul_add(
                delta[0],
                contact.normal[1].mul_add(delta[1], contact.normal[2] * delta[2]),
            );
            let spring = if front {
                p.spring_rate
            } else {
                p.rear_spring_rate.unwrap_or(p.spring_rate)
            };
            let damping = if front {
                p.damping_ratio
            } else {
                p.rear_damping_ratio.unwrap_or(p.damping_ratio)
            };
            let compression = if front {
                p.max_spring_compression
            } else {
                p.rear_max_spring_compression
                    .unwrap_or(p.max_spring_compression)
            };
            let vy = normal[0].mul_add(point[0], normal[1].mul_add(point[1], normal[2] * point[2]));
            let load = suspension_load(
                p.mass * (-g.gravity) * weight + penetration * spring,
                damping_coefficient(p.mass * weight, spring, damping),
                vy,
                compression,
                spring,
            );
            if load <= 0. {
                return 0.;
            }
            contacts += 1;
            if normal[1] <= 0. || contact.normal[1] < 0.1 {
                return 0.;
            }
            let steer = if front {
                self.steering * p.max_steer
            } else {
                0.
            };
            let frame = native_wheel_frame(normal, point, steer, self.wheel_omega[i]);
            let residual = frame.tangent_velocity[0]
                - frame.longitudinal_axis[0] * (self.wheel_omega[i] * wheel_radius(p, i));
            crate::native_nitrous_wheel_ratio(point, residual, true)
        });
        (contacts, crate::native_nitrous_metric(ratios))
    }
    fn channels(&self, p: &Handling) -> [f32; 18] {
        let inertia = body_inertia(p);
        let q = self.orientation;
        let momentum = inverse_rotate(
            [-q[0], -q[1], -q[2], q[3]],
            [
                inertia[0] * self.pitch_rate,
                inertia[1] * self.yaw_rate,
                inertia[2] * self.roll_rate,
            ],
        );
        [
            self.position[0],
            self.position[1],
            self.position[2],
            self.velocity[0],
            self.velocity[1],
            self.velocity[2],
            self.orientation[0],
            self.orientation[1],
            self.orientation[2],
            self.orientation[3],
            momentum[1],
            self.engine_omega,
            self.wheel_omega[0],
            self.wheel_omega[1],
            self.wheel_omega[2],
            self.wheel_omega[3],
            momentum[2],
            momentum[0],
        ]
    }
    fn commit(&mut self, s: [f32; 18], p: &Handling) {
        self.position = [s[0], s[1], s[2]];
        self.velocity = [s[3], s[4], s[5]];
        let norm = (s[6] * s[6] + s[7] * s[7] + s[8] * s[8] + s[9] * s[9]).sqrt();
        self.orientation = [s[6] / norm, s[7] / norm, s[8] / norm, s[9] / norm];
        let inertia = body_inertia(p);
        let momentum = inverse_rotate(self.orientation, [s[17], s[10], s[16]]);
        self.pitch_rate = momentum[0] * (1. / inertia[0]);
        self.yaw_rate = momentum[1] * (1. / inertia[1]);
        self.roll_rate = momentum[2] * (1. / inertia[2]);
        self.engine_omega = s[11].clamp(104.719757, 0.104719758 * 1.12 * p.redline);
        self.wheel_omega = std::array::from_fn(|i| {
            if self.reversing {
                s[12 + i].min(0.)
            } else {
                s[12 + i].max(0.)
            }
        });
        if self.clutch_engaged {
            let (omegas, _) = self.drivetrain(p);
            for i in 0..4 {
                if is_driven(self.effective_layout(p), i) {
                    self.wheel_omega[i] = omegas[i];
                }
            }
        }
    }
    fn effective_layout(&self, p: &Handling) -> DriveLayout {
        // Native82260108 disconnects the rear axle of an AWD car for any handbrake input.
        if p.layout == DriveLayout::Awd && self.handbrake > 0. {
            DriveLayout::Fwd
        } else {
            p.layout
        }
    }
    fn gear_ratio(&self, p: &Handling) -> f32 {
        p.gears
            .get(self.gear.saturating_sub(1))
            .copied()
            .unwrap_or(1.)
            * p.final_drive
            * if self.reversing { -1. } else { 1. }
    }
    fn driven_omega(&self, p: &Handling) -> f32 {
        match self.effective_layout(p) {
            DriveLayout::Fwd => (self.wheel_omega[0] + self.wheel_omega[1]) * 0.5,
            DriveLayout::Rwd => (self.wheel_omega[2] + self.wheel_omega[3]) * 0.5,
            DriveLayout::Awd => self.wheel_omega.iter().sum::<f32>() * 0.25,
        }
    }
    fn drivetrain(&self, p: &Handling) -> ([f32; 4], [f32; 4]) {
        let velocity = self.body_velocity();
        let rolling: [f32; 4] = std::array::from_fn(|i| {
            let x = if i % 2 == 0 {
                -p.track_width * 0.5
            } else {
                p.track_width * 0.5
            };
            let z = if i < 2 {
                p.wheelbase * (1. - p.front_weight)
            } else {
                -p.wheelbase * p.front_weight
            };
            let point_velocity = [
                velocity[0] + self.yaw_rate * z,
                velocity[1] + self.roll_rate * x - self.pitch_rate * z,
                velocity[2] - self.yaw_rate * x,
            ];
            let normal = inverse_rotate(self.orientation, self.contacts[i].normal);
            let steer = if i < 2 {
                self.steering * p.max_steer
            } else {
                0.
            };
            (native_wheel_frame(normal, point_velocity, steer, self.wheel_omega[i]).forward_speed
                / wheel_radius(p, i))
            .abs()
        });
        let target = self.engine_omega / self.gear_ratio(p);
        let (front_target, rear_target, centre) = if self.effective_layout(p) == DriveLayout::Awd {
            let d = differential_split(
                (rolling[0] + rolling[1]) * 0.5,
                (rolling[2] + rolling[3]) * 0.5,
                p.centre_diff_slip,
                target,
            );
            (d.0[0], d.0[1], d.1)
        } else {
            (target, target, [1.; 2])
        };
        let f = differential_split(rolling[0], rolling[1], p.front_diff_slip, front_target);
        let r = differential_split(rolling[2], rolling[3], p.rear_diff_slip, rear_target);
        (
            [f.0[0], f.0[1], r.0[0], r.0[1]],
            [
                f.1[0] * centre[0],
                f.1[1] * centre[0],
                r.1[0] * centre[1],
                r.1[1] * centre[1],
            ],
        )
    }
    fn derivative(&self, p: &Handling, g: &PhysicsGlobals, u: PlayerInput, h: f32) -> [f32; 18] {
        let body_velocity = self.body_velocity();
        let ratio = self.gear_ratio(p);
        let engine_torque = torque_curve(p, self.engine_omega * 9.54929638)
            * p.peak_torque
            * g.engine_torque_scalar
            * u.throttle
            * if u.nitrous > 0. {
                p.nitrous_engine_multiplier
            } else {
                1.
            }
            - (1. - u.throttle) * p.engine_size * g.engine_braking_scalar;
        let (_, fractions) = self.drivetrain(p);
        let mut reflected_reaction = 0.;
        let mut inertia = engine_inertia(p, g);
        let mut body_force = [0f32; 3];
        let mut body_torque = [0f32; 3];
        let mut wheel_acc = [0.; 4];
        for i in 0..4 {
            let front = i < 2;
            let radius = wheel_radius(p, i);
            let spring_rate = if front {
                p.spring_rate
            } else {
                p.rear_spring_rate.unwrap_or(p.spring_rate)
            };
            let damping = if front {
                p.damping_ratio
            } else {
                p.rear_damping_ratio.unwrap_or(p.damping_ratio)
            };
            let compression = if front {
                p.max_spring_compression
            } else {
                p.rear_max_spring_compression
                    .unwrap_or(p.max_spring_compression)
            };
            let z = if front {
                p.wheelbase * (1. - p.front_weight)
            } else {
                -p.wheelbase * p.front_weight
            };
            let x = if i % 2 == 0 {
                -p.track_width / 2.
            } else {
                p.track_width / 2.
            };
            let steer = if front {
                self.steering * p.max_steer
            } else {
                0.
            };
            let static_load = p.mass
                * (-g.gravity)
                * if front {
                    p.front_weight * 0.5
                } else {
                    (1. - p.front_weight) * 0.5
                };
            let q = self.orientation;
            let contact = self.contacts[i];
            let arm_world = inverse_rotate([-q[0], -q[1], -q[2], q[3]], [x, 0., z]);
            let wheel_point =
                std::array::from_fn::<_, 3, _>(|axis| self.position[axis] + arm_world[axis]);
            // 82260970 -> 8225BFF0: wheel172 is contact-normal point velocity,
            // not absolute world-Y velocity. A tangent uphill motion has zero damping.
            let normal_body = inverse_rotate(self.orientation, contact.normal);
            let point_velocity = [
                body_velocity[0] + self.yaw_rate * z,
                body_velocity[1] + x * self.roll_rate - z * self.pitch_rate,
                body_velocity[2] - self.yaw_rate * x,
            ];
            let wheel_vy = normal_body[0].mul_add(
                point_velocity[0],
                normal_body[1].mul_add(point_velocity[1], normal_body[2] * point_velocity[2]),
            );
            // 82260970 advances penetration along the sampled normal while the
            // contact plane stays fixed across this object's RK stages.
            let to_plane = [
                contact.anchor_xz[0] - wheel_point[0],
                contact.height - wheel_point[1],
                contact.anchor_xz[1] - wheel_point[2],
            ];
            let penetration = contact.normal[0].mul_add(
                to_plane[0],
                contact.normal[1].mul_add(to_plane[1], contact.normal[2] * to_plane[2]),
            );
            let spring_load = static_load + penetration * spring_rate;
            let load = if contact.active {
                suspension_load(
                    spring_load,
                    damping_coefficient(
                        p.mass
                            * if front {
                                p.front_weight * 0.5
                            } else {
                                (1. - p.front_weight) * 0.5
                            },
                        spring_rate,
                        damping,
                    ),
                    wheel_vy,
                    compression,
                    spring_rate,
                )
            } else {
                0.
            };
            let frame = native_wheel_frame(normal_body, point_velocity, steer, self.wheel_omega[i]);
            let mut tyre_force = [0f32; 3];
            let mut slip = 0.;
            let mut saturation = 0.;
            let wheel_throttle = if is_driven(p.layout, i) {
                u.throttle
            } else {
                0.
            };
            // DA48 gates tire force on WORLD normalY76 and BODY normalY92.
            if load > 0. && contact.normal[1] >= 0.1 && normal_body[1] > 0. {
                slip = longitudinal_slip(self.wheel_omega[i], radius, frame.speed, frame.angle);
                let mu = if front {
                    p.tyre_mu
                } else {
                    p.rear_tyre_mu.unwrap_or(p.tyre_mu)
                } * contact.grip;
                let alpha = contact_blend(frame.speed, frame.angle, slip, contact.normal[1], 0.);
                let force = if alpha > 0. {
                    combined_tyre_force(load, mu, slip, frame.angle, frame.camber, g)
                } else {
                    [0.; 3]
                };
                let residual = std::array::from_fn::<_, 3, _>(|axis| {
                    frame.tangent_velocity[axis]
                        - frame.longitudinal_axis[axis] * (self.wheel_omega[i] * radius)
                });
                let residual_length = (residual[0] * residual[0]
                    + residual[1] * residual[1]
                    + residual[2] * residual[2])
                    .sqrt();
                saturation = if alpha == 0. {
                    residual_length * 0.5
                } else {
                    force[2]
                };
                let residual_force = load
                    * mu
                    * g.skid_mu_scalar
                    * curve(&g.response_curve, saturation)
                    * (1. - alpha)
                    / (residual_length + f32::EPSILON);
                let attenuation = if saturation > g.slip_point {
                    1. - (1. - g.slip_mu_scalar) * wheel_throttle
                } else {
                    1.
                };
                let direction = if self.wheel_omega[i] < 0. { -1. } else { 1. };
                for axis in 0..3 {
                    tyre_force[axis] += alpha
                        * direction
                        * (frame.longitudinal_axis[axis] * force[0] * attenuation
                            + frame.lateral_axis[axis] * force[1])
                        - residual[axis] * residual_force;
                }
            }
            let brake = if p.abs && slip < 0. && saturation > g.abs_threshold {
                0.
            } else {
                u.brake * p.footbrake_mu
            };
            let hand = if !front {
                u.handbrake * p.handbrake_mu
            } else {
                0.
            };
            // D940 writes suspension force204; DA48 clears/writes TIRE force220.
            // DF90 rotates220 by-steer, so suspension is excluded from wheel reaction.
            let (sn, cs) = steer.sin_cos();
            let mut road_force = tyre_force[0] * sn + tyre_force[2] * cs;
            if saturation > g.slip_point && wheel_throttle > 0.8 {
                road_force -= (wheel_throttle - 0.8) * 2.;
            }
            let reaction = wheel_reaction(
                brake + hand + p.axle_mu,
                -road_force * radius,
                self.wheel_omega[i],
                frame.forward_speed / radius,
                h,
                1. / g.wheel_inertia(),
            );
            wheel_acc[i] = reaction / g.wheel_inertia();
            let driven_wheel = match self.effective_layout(p) {
                DriveLayout::Fwd => front,
                DriveLayout::Rwd => !front,
                DriveLayout::Awd => true,
            };
            if driven_wheel && self.clutch_engaged {
                reflected_reaction += reaction * fractions[i] / ratio * 1.5;
                inertia += g.wheel_inertia() * fractions[i] * (1. / ratio).abs();
            }
            let wheel_force =
                std::array::from_fn::<_, 3, _>(|axis| normal_body[axis] * load + tyre_force[axis]);
            for axis in 0..3 {
                body_force[axis] += wheel_force[axis];
            }
            body_torque[0] -= z * wheel_force[1];
            body_torque[1] += z * wheel_force[0] - x * wheel_force[2];
            body_torque[2] += x * wheel_force[1];
        }
        if self.nitrous_body_force != 0. {
            body_force[2] += self.nitrous_body_force;
        }
        let engine_acc = (engine_torque + reflected_reaction) / inertia;
        let drag = body_drag(self.velocity, p.drag, 1.);
        let q = self.orientation;
        let world_force = inverse_rotate([-q[0], -q[1], -q[2], q[3]], body_force);
        let acceleration =
            std::array::from_fn::<_, 3, _>(|axis| (world_force[axis] + drag[axis]) / p.mass);
        let world_torque = inverse_rotate([-q[0], -q[1], -q[2], q[3]], body_torque);
        let omega = inverse_rotate(
            [-q[0], -q[1], -q[2], q[3]],
            [self.pitch_rate, self.yaw_rate, self.roll_rate],
        );
        // 82265FF8: WORLD omega premultiplies the orientation; angular RK channels
        // are WORLD momentum and its derivative is R*BODY torque.
        [
            self.velocity[0],
            self.velocity[1],
            self.velocity[2],
            acceleration[0],
            acceleration[1] + g.gravity,
            acceleration[2],
            0.5 * (q[3] * omega[0] + q[2] * omega[1] - q[1] * omega[2]),
            0.5 * (q[3] * omega[1] + q[0] * omega[2] - q[2] * omega[0]),
            0.5 * (q[3] * omega[2] + q[1] * omega[0] - q[0] * omega[1]),
            -0.5 * (q[0] * omega[0] + q[1] * omega[1] + q[2] * omega[2]),
            world_torque[1],
            engine_acc,
            wheel_acc[0],
            wheel_acc[1],
            wheel_acc[2],
            wheel_acc[3],
            world_torque[2],
            world_torque[0],
        ]
    }
}
fn body_inertia(p: &Handling) -> [f32; 3] {
    let per_unit = [
        p.body_height * p.body_height + p.body_length * p.body_length,
        p.body_length * p.body_length + p.body_width * p.body_width,
        p.body_height * p.body_height + p.body_width * p.body_width,
    ]
    .map(|sum| sum * 0.0833333358168602);
    per_unit.map(|inertia| p.mass * inertia * p.inertia_scalar)
}

fn inverse_rotate(q: [f32; 4], v: [f32; 3]) -> [f32; 3] {
    let [x, y, z, w] = q;
    [
        (1. - 2. * (y * y + z * z)) * v[0]
            + 2. * (x * y + w * z) * v[1]
            + 2. * (x * z - w * y) * v[2],
        2. * (x * y - w * z) * v[0]
            + (1. - 2. * (x * x + z * z)) * v[1]
            + 2. * (y * z + w * x) * v[2],
        2. * (x * z + w * y) * v[0]
            + 2. * (y * z - w * x) * v[1]
            + (1. - 2. * (x * x + y * y)) * v[2],
    ]
}

fn add(s: [f32; 18], k: [f32; 18], h: f32) -> [f32; 18] {
    let mut o = s;
    for i in 0..18 {
        o[i] += k[i] * h;
    }
    o
}
/// Minimum translation from B into A for intersecting oriented chassis footprints.
/// Geometric SAT query only; ordered response belongs to the game scheduler.
pub fn chassis_overlap(
    a: [f32; 3],
    ayaw: f32,
    ahalf: [f32; 2],
    b: [f32; 3],
    byaw: f32,
    bhalf: [f32; 2],
) -> Option<[f32; 3]> {
    if (a[1] - b[1]).abs() > 1.8 {
        return None;
    }
    let ax = [[ayaw.cos(), -ayaw.sin()], [ayaw.sin(), ayaw.cos()]];
    let bx = [[byaw.cos(), -byaw.sin()], [byaw.sin(), byaw.cos()]];
    let d = [a[0] - b[0], a[2] - b[2]];
    let mut best = f32::MAX;
    let mut normal = [0.; 2];
    for axis in ax.into_iter().chain(bx) {
        let dot = |v: [f32; 2]| v[0] * axis[0] + v[1] * axis[1];
        let ra = ahalf[0] * dot(ax[0]).abs() + ahalf[1] * dot(ax[1]).abs();
        let rb = bhalf[0] * dot(bx[0]).abs() + bhalf[1] * dot(bx[1]).abs();
        let separation = dot(d);
        let depth = ra + rb - separation.abs();
        if depth <= 0. {
            return None;
        }
        if depth < best {
            best = depth;
            let sign = if separation >= 0. { 1. } else { -1. };
            normal = [axis[0] * sign, axis[1] * sign];
        }
    }
    Some([normal[0] * best, 0., normal[1] * best])
}

/// Native 82266218: quadratic drag projected along the full velocity vector.
/// body+3924 is initialized to one by 82267670; runtime writers remain unknown.
pub fn body_drag(velocity: [f32; 3], coefficient: f32, multiplier: f32) -> [f32; 3] {
    let speed_squared = velocity[0].mul_add(
        velocity[0],
        velocity[2].mul_add(velocity[2], velocity[1] * velocity[1]),
    );
    let magnitude = -(speed_squared * coefficient * multiplier);
    let inverse_length = 1. / (speed_squared.sqrt() + f32::EPSILON);
    velocity.map(|component| (component * inverse_length) * magnitude)
}

fn is_driven(layout: DriveLayout, i: usize) -> bool {
    layout == DriveLayout::Awd
        || (layout == DriveLayout::Fwd && i < 2)
        || (layout == DriveLayout::Rwd && i >= 2)
}
/// Native8225C950 plus E4D8 rolling-velocity initialization; returns speeds and direct fractions.
pub fn differential_split(a: f32, b: f32, slip: f32, target: f32) -> ([f32; 2], [f32; 2]) {
    let mean = (a + b) * 0.5;
    let mut left = slip.clamp(0., 1.).mul_add(a - mean, mean);
    let mut right = mean - (left - mean);
    if slip == 0. || (right < 0.0001 && left < 0.0001) {
        left = target;
        right = target;
    } else if right < 0.0001 {
        left = target * 2.;
        right = 0.;
    } else {
        let relative = left / right;
        right = target * 2. / (relative + 1.);
        left = right * relative;
    }
    let fractions = if slip == 0. || target < 0.0001 {
        [1.; 2]
    } else {
        [left / target, right / target]
    };
    ([left, right], fractions)
}

/// Native8226DF90 brake/contact reaction with rolling/locked target crossing prevention.
pub fn wheel_reaction(
    brake_magnitude: f32,
    road: f32,
    omega: f32,
    rolling_omega: f32,
    h: f32,
    inverse_inertia: f32,
) -> f32 {
    let brake = if omega == 0. {
        -road.clamp(-brake_magnitude, brake_magnitude)
    } else {
        -brake_magnitude * omega.signum()
    };
    let mut total = brake + road;
    let target = if road.abs() > brake.abs() {
        rolling_omega
    } else {
        0.
    };
    let delta = inverse_inertia * total * h;
    if delta == 0. {
        return 0.;
    }
    let alpha = (target - omega) / delta;
    if (0. ..1e-7).contains(&alpha) {
        return 0.;
    }
    if alpha > 0. && alpha < 1. {
        total *= alpha;
    }
    total
}

/// Native8226DA48 contact-force blend; ordinary suspension-axis localY defaults to one.
pub fn contact_blend(speed: f32, angle: f32, slip: f32, axis_y: f32, override404: f32) -> f32 {
    let a = (speed.clamp(3., 5.) - 3.) * 0.5;
    let b = 1. - (angle.abs().clamp(1., 1.2000000476837158) - 1.) * 4.999999046325684;
    let c = (slip.clamp(-0.8999999761581421, -0.6000000238418579) + 0.8999999761581421)
        * 3.333333969116211;
    let mut alpha = if override404 > 0. { 1. } else { a * b * c };
    if alpha > 0. {
        alpha = if axis_y > 0.800000011920929 {
            alpha * (axis_y - 0.800000011920929) * 5.
        } else {
            0.
        };
    }
    alpha
}

fn wheel_radius(p: &Handling, i: usize) -> f32 {
    if i < 2 {
        p.wheel_radius
    } else {
        p.rear_wheel_radius.unwrap_or(p.wheel_radius)
    }
}

#[cfg(test)]
mod contact_frame_regressions {
    use super::*;
    #[test]
    fn bank_normal_contributes_all_three_suspension_force_components() {
        let p = Handling {
            drag: 0.,
            ..Default::default()
        };
        let g = PhysicsGlobals::default();
        let mut state = VehicleState::default();
        let normal = [0.2f32, 0.96, (1f32 - 0.2 * 0.2 - 0.96 * 0.96).sqrt()];
        for i in 0..4 {
            let x = if i % 2 == 0 {
                -p.track_width / 2.
            } else {
                p.track_width / 2.
            };
            let z = if i < 2 {
                p.wheelbase * (1. - p.front_weight)
            } else {
                -p.wheelbase * p.front_weight
            };
            state.contacts[i] = SurfaceContact {
                anchor_xz: [x, z],
                height: 0.,
                normal,
                grip: 1.,
                active: true,
            };
        }
        let derivative = state.derivative(&p, &g, PlayerInput::default(), 1. / 60.);
        assert!(
            (derivative[3] + g.gravity * normal[0]).abs() < 1e-4,
            "{derivative:?}"
        );
        assert!((derivative[5] + g.gravity * normal[2]).abs() < 1e-4);
    }
    #[test]
    fn low_speed_contact_force_rotates_with_full_body_and_plane_frame() {
        let p = Handling {
            drag: 0.,
            ..Default::default()
        };
        let g = PhysicsGlobals::default();
        let mut a = VehicleState::default();
        a.velocity = [0.5, 0., 1.];
        a.wheel_omega = [4.; 4];
        a.steering = 0.2;
        for i in 0..4 {
            let x = if i % 2 == 0 {
                -p.track_width / 2.
            } else {
                p.track_width / 2.
            };
            let z = if i < 2 {
                p.wheelbase * (1. - p.front_weight)
            } else {
                -p.wheelbase * p.front_weight
            };
            a.contacts[i].anchor_xz = [x, z];
        }
        let mut b = a.clone();
        let half = 0.15f32;
        b.orientation = [half.sin(), 0., 0., half.cos()];
        let rotation = [-b.orientation[0], 0., 0., b.orientation[3]];
        b.velocity = inverse_rotate(rotation, a.velocity);
        let normal = inverse_rotate(rotation, [0., 1., 0.]);
        for i in 0..4 {
            let arm = inverse_rotate(
                rotation,
                [a.contacts[i].anchor_xz[0], 0., a.contacts[i].anchor_xz[1]],
            );
            b.contacts[i] = SurfaceContact {
                anchor_xz: [arm[0], arm[2]],
                height: arm[1],
                normal,
                grip: 1.,
                active: true,
            };
        }
        let da = a.derivative(&p, &g, PlayerInput::default(), 1. / 60.);
        let db = b.derivative(&p, &g, PlayerInput::default(), 1. / 60.);
        let expected = inverse_rotate(rotation, [da[3], da[4] - g.gravity, da[5]]);
        let actual = [db[3], db[4] - g.gravity, db[5]];
        for axis in 0..3 {
            assert!(
                (expected[axis] - actual[axis]).abs() < 0.001,
                "expected{expected:?} actual{actual:?}"
            );
        }
    }
}

#[cfg(test)]
mod angular_momentum_regressions {
    use super::*;
    fn world_momentum(state: &VehicleState, p: &Handling) -> [f32; 3] {
        let inertia = body_inertia(p);
        let q = state.orientation;
        inverse_rotate(
            [-q[0], -q[1], -q[2], q[3]],
            [
                inertia[0] * state.pitch_rate,
                inertia[1] * state.yaw_rate,
                inertia[2] * state.roll_rate,
            ],
        )
    }
    #[test]
    fn torque_free_anisotropic_body_preserves_world_momentum_and_precesses() {
        let p = Handling {
            drag: 0.,
            ..Default::default()
        };
        let g = PhysicsGlobals {
            gravity: 0.,
            ..Default::default()
        };
        let mut state = VehicleState::default();
        state.pitch_rate = 0.3;
        state.yaw_rate = 0.7;
        state.roll_rate = 0.4;
        for contact in &mut state.contacts {
            contact.active = false;
        }
        let before = world_momentum(&state, &p);
        for _ in 0..600 {
            state.step(&p, &g, PlayerInput::default(), 1. / 120.);
        }
        let after = world_momentum(&state, &p);
        let scale = before.iter().map(|v| v * v).sum::<f32>().sqrt();
        let error = before
            .iter()
            .zip(after)
            .map(|(a, b)| (a - b) * (a - b))
            .sum::<f32>()
            .sqrt()
            / scale;
        assert!(
            error < 0.0001,
            "WorldL error{error} before{before:?} after{after:?}"
        );
        assert!(
            (state.pitch_rate - 0.3).abs()
                + (state.yaw_rate - 0.7).abs()
                + (state.roll_rate - 0.4).abs()
                > 0.01
        );
    }
}

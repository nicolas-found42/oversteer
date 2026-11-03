//! Static PPC drift recovery: 82113648 / 82113CF8 / 82113FA8 / 82113B58 / 82113398.
//! Native upstream clock, bonus inputs and remaining mode/context bindings remain explicit gaps.
use serde::{Deserialize, Serialize};
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum DriftPhase {
    Idle,
    Active,
    Coasting,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativeDriftState {
    pub phase: DriftPhase,
    pub points: u32,
    pub banked: u32,
    pub lost: u32,
    pub duration: f32,
    pub activation: f32,
    pub coast: f32,
    pub recovery: f32,
    pub chains: u32,
    last_sign: f32,
    waiting_for_chain: bool,
    chain_hold: f32,
}
impl Default for NativeDriftState {
    fn default() -> Self {
        Self {
            phase: DriftPhase::Idle,
            points: 0,
            banked: 0,
            lost: 0,
            duration: 0.,
            activation: 0.,
            coast: 0.,
            recovery: 1.,
            chains: 0,
            last_sign: 0.,
            waiting_for_chain: false,
            chain_hold: 0.,
        }
    }
}
impl NativeDriftState {
    pub fn total(&self) -> u32 {
        self.banked.wrapping_add(self.points)
    }
    /// 82113CF8. The frame interval enters twice; this is not a dt-linear score rate.
    pub fn accumulate(
        &mut self,
        angle_degrees: f32,
        speed: f32,
        clock_step: f32,
        multiplier: f32,
        bonus: f32,
    ) {
        if self.recovery < 1. {
            return;
        }
        let dt = clock_step.min(0.06666667014360428);
        self.duration += dt;
        let angle = angle_degrees.abs() as u32 as f32;
        let product = multiplier * angle * speed;
        if self.points > 1_000_000 {
            let gain = product * dt * dt * bonus;
            self.points = gain.mul_add(750., self.points as f32) as u32;
        } else {
            let gain = product * self.duration * dt * dt * bonus;
            self.points = gain.mul_add(25., self.points as f32) as u32;
        }
    }
    /// Returns true when a chain is banked this frame. Native mode9 uses a longer chain-direction hold.
    pub fn advance(
        &mut self,
        speed: f32,
        angle_radians: f32,
        clock_step: f32,
        endurance: bool,
        multiplier: f32,
        bonus: f32,
    ) -> bool {
        let dt = clock_step.min(0.06666667014360428);
        let angle = if !(-2.0..=2.0).contains(&angle_radians) {
            0.
        } else {
            angle_radians.clamp(-1.5707963705062866, 1.5707963705062866)
        };
        let degrees = angle * 57.2957763671875;
        let eligible = speed > 10. && degrees.abs() > 10.;
        let mut banked = false;
        if eligible {
            self.activation += dt;
        } else if self.phase == DriftPhase::Idle {
            self.activation = 0.;
            self.duration = 0.;
        }
        if eligible && self.activation > 0.10000000149011612 {
            self.phase = DriftPhase::Active;
            self.coast = 0.;
            self.accumulate(degrees, speed, dt, multiplier, bonus);
            self.recovery += dt;
        } else {
            match self.phase {
                DriftPhase::Active => self.phase = DriftPhase::Coasting,
                DriftPhase::Coasting => {
                    self.coast += dt;
                    if self.coast > 0.75 {
                        banked = self.points > 0;
                        self.bank();
                        self.phase = DriftPhase::Idle;
                        self.duration = 0.;
                        self.activation = 0.;
                    }
                }
                DriftPhase::Idle => {}
            }
        }
        if matches!(self.phase, DriftPhase::Active | DriftPhase::Coasting) {
            let sign = degrees.signum();
            if self.waiting_for_chain {
                if sign != self.last_sign {
                    self.waiting_for_chain = false;
                } else {
                    self.chain_hold += dt;
                    if self.chain_hold > if endurance { 2. } else { 1. } {
                        self.chains = self.chains.wrapping_add(1);
                        self.waiting_for_chain = false;
                    }
                }
            } else if self.last_sign != 0. && sign != self.last_sign {
                self.waiting_for_chain = true;
                self.chain_hold = 0.;
            }
            self.last_sign = sign;
        } else {
            self.last_sign = 0.;
            self.waiting_for_chain = false;
        }
        banked
    }
    pub fn bank(&mut self) {
        self.banked = self.banked.wrapping_add(self.points);
        self.points = 0;
    }
    /// 82113B58: endurance banks before collision loss; other modes retain a damage-scaled fraction.
    pub fn collide(&mut self, retained_fraction: f32, endurance: bool) {
        if endurance {
            self.bank();
        }
        let before = self.points;
        let retained = (before as f32 * retained_fraction.clamp(0., 1.)) as u32;
        self.lost = self.lost.wrapping_add(before.wrapping_sub(retained));
        self.points = retained;
        self.duration = 0.;
        self.activation = 0.;
        self.recovery = 0.;
        self.phase = DriftPhase::Idle;
        self.coast = 0.;
        self.chains = 0;
    }
    pub fn reset_lap(&mut self) {
        let recovery = self.recovery;
        *self = Self::default();
        self.recovery = recovery;
    }
}

/// 821143C0 mode12 AI catch-up. Rank380 is one-based;821DD510 supplies the
/// first HUMAN participant, not whichever AI currently leads the scoreboard.
/// The caller must bind the native alternate-context condition separately.
pub fn native_king_multiplier(
    human_total: Option<u32>,
    own_total: u32,
    rank: i32,
    profile_league: u32,
    alternate_context: bool,
) -> f32 {
    let Some(human_total) = human_total else {
        return 1.;
    };
    let ratio = if own_total == 0 {
        1.
    } else {
        let factor = (rank as f32 - 1.).mul_add(0.2, 1.);
        (human_total as f32 / factor) / own_total as f32
    };
    let base = if alternate_context {
        2.5
    } else if ratio > 1. {
        match profile_league {
            1 => 1.15,
            2 => 1.2,
            3 => 1.25,
            4..=7 => 1.3,
            8 | 9 => 1.35,
            _ => 1.1,
        }
    } else {
        match profile_league {
            1 => 0.2,
            2 => 0.3,
            3 => 0.4,
            4 => 0.5,
            5 => 0.6,
            6 => 0.7,
            7..=9 => 0.8,
            _ => 0.1,
        }
    };
    (base * ratio).clamp(0.2, 10.)
}

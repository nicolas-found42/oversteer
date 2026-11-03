//! Original packed package decoding and 821064C8 factors. Donor endpoint binding is separate.
use serde::{Deserialize, Serialize};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum PerformanceCategory {
    Power,
    Handling,
    Weight,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum PrototypeCategory {
    Power,
    Handling,
    Weight,
    Nitrous,
}
#[derive(Clone, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub struct PerformanceLicense {
    pub league: u8,
    pub category: PerformanceCategory,
    pub item: u32,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePerformanceCareer {
    pub prototype_tokens: u8,
    pub prototype_unlocks: Vec<(u8, PrototypeCategory)>,
    pub ordinary_licenses: Vec<PerformanceLicense>,
}
impl Default for NativePerformanceCareer {
    fn default() -> Self {
        // 82217870 sets every third ordinary-license bit after clearing90bits.
        let ordinary_licenses = (0..10)
            .flat_map(|league| {
                [
                    PerformanceCategory::Power,
                    PerformanceCategory::Handling,
                    PerformanceCategory::Weight,
                ]
                .into_iter()
                .map(move |category| PerformanceLicense {
                    league,
                    category,
                    item: 0,
                })
            })
            .collect();
        Self {
            prototype_tokens: 0,
            prototype_unlocks: vec![],
            ordinary_licenses,
        }
    }
}
impl PerformanceCategory {
    pub fn index(self) -> usize {
        match self {
            Self::Power => 0,
            Self::Handling => 1,
            Self::Weight => 2,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePackageLeague {
    pub league: String,
    pub threshold: f32,
    pub steps: u32,
    pub native_price_operands: [u32; 6],
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePerformanceCatalog {
    pub packages: Vec<NativePackageLeague>,
    pub engine_endpoints: Vec<NativePerformanceEndpoint>,
    pub handling_increment: f32,
    pub handling_scale: f32,
    pub human_handling_scale: f32,
    pub front_tyre_scale: f32,
    pub rear_tyre_scale: f32,
    pub suspension_gain: f32,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePerformanceEndpoint {
    pub catalog_base_offset: u32,
    pub catalog_max_offset: u32,
    pub base: f32,
    pub maximum: f32,
}
impl NativePerformanceEndpoint {
    pub fn interpolate(&self, ratio: f32) -> f32 {
        (1. - ratio).mul_add(self.base, self.maximum * ratio)
    }
}
impl Default for NativePerformanceCatalog {
    fn default() -> Self {
        serde_json::from_str(include_str!("../data/native-performance.json"))
            .expect("validated original performance catalog")
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePerformanceFields {
    pub stock_power: f32,
    pub stock_weight: f32,
    pub max_power: f32,
    pub min_weight: f32,
    pub brake_factor: f32,
    pub tyre_factor: f32,
    pub suspension_factor: f32,
    pub turbo_factor: f32,
    pub cost_modifier: f32,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NativePerformanceDefinition {
    pub native_id: String,
    pub binding_kind: String,
    pub rationale: String,
    pub native_fields: NativePerformanceFields,
    pub authoritative_base: DonorPerformanceBase,
    pub adapted_endpoints: DonorPerformanceEndpoints,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DonorPerformanceBase {
    pub peak_bhp: f32,
    pub mass: f32,
    pub layout: crate::DriveLayout,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DonorPerformanceEndpoints {
    pub maximum_power: f32,
    pub minimum_mass: f32,
}
impl NativePerformanceDefinition {
    /// ADR0007 operands: donor stock and declared adapted maximum endpoints.
    /// Raw counterpart values remain provenance and supply the other five factors.
    pub fn adapted_fields(&self) -> NativePerformanceFields {
        let mut fields = self.native_fields.clone();
        fields.stock_power = self.authoritative_base.peak_bhp;
        fields.stock_weight = self.authoritative_base.mass;
        fields.max_power = self.adapted_endpoints.maximum_power;
        fields.min_weight = self.adapted_endpoints.minimum_mass;
        fields
    }
}

/// Original top-two-bit installation marker, signed five-bit league, low25 item.
pub fn native_package_decode(raw: u32) -> Option<(i32, u32)> {
    (raw & 0xc0000000 != 0).then_some((((raw << 2) as i32) >> 27, raw & 0x01ffffff))
}

/// 821C9E28's literal state244 values. State2 routes challenge/unlock UI, not purchase.
pub fn native_package_selection_state(
    installed: u32,
    league: u8,
    item: u32,
    player_league: u8,
    licensed: bool,
    previous_licensed: bool,
    prototype: bool,
) -> u8 {
    if native_package_decode(installed) == Some((i32::from(league), item)) {
        return 3;
    }
    if league <= player_league && licensed {
        let current = ((((installed << 2) as i32) >> 27), installed & 0x01ffffff);
        return if (i32::from(league), item) >= current {
            1
        } else {
            4
        };
    }
    if league <= player_league && (previous_licensed || item == 0 || prototype) {
        2
    } else {
        0
    }
}

impl NativePerformanceCatalog {
    pub fn tuned_ratio(&self, car: &NativePerformanceFields, parts: [u32; 3]) -> Result<f32, String> {
        let power = self.factor(car, PerformanceCategory::Power, parts[0])?;
        let weight = self.factor(car, PerformanceCategory::Weight, parts[2])?;
        Ok((car.stock_power * power) / (car.stock_weight / weight))
    }
    /// 82202B10 candidate list uses inclusive class bounds, unlike min/max lookup.
    pub fn eligible_for_league(&self, car: &NativePerformanceFields, parts: [u32; 3], league: u8) -> Result<bool, String> {
        let pack = self.packages.get(usize::from(league)).ok_or("Invalid race league")?;
        let lower = if league == 0 { 0.01 } else { self.packages[league as usize - 1].threshold };
        let ratio = self.tuned_ratio(car, parts)?;
        Ok(ratio >= lower && ratio <= pack.threshold)
    }
    /// Donor-relative adapter around the original HUMAN C558 raw-P/W endpoint producer.
    /// This preserves donor stock values; it is not an original per-donor live tune.
    pub fn apply_relative(&self, definition: &NativePerformanceDefinition, parts: [u32; 3], baseline: &crate::Handling, drift_discipline: bool) -> Result<crate::Handling, String> {
        let adapted = definition.adapted_fields();
        let car = &adapted;
        let stock_ratio = car.stock_power / car.stock_weight;
        let tuned_ratio = self.tuned_ratio(car, parts)?;
        let endpoint_ratio = |index: usize| -> Result<f32, String> {
            let endpoint = self.engine_endpoints.get(index).ok_or("Missing native endpoint")?;
            Ok(endpoint.interpolate(tuned_ratio) / endpoint.interpolate(stock_ratio))
        };
        let mut result = baseline.clone();
        result.peak_torque *= endpoint_ratio(0)?;
        result.peak_torque_rpm *= endpoint_ratio(1)?;
        result.peak_bhp *= endpoint_ratio(2)?;
        result.peak_bhp_rpm *= endpoint_ratio(3)?;
        result.redline *= endpoint_ratio(4)?;
        result.mass *= endpoint_ratio(7)?;
        result.nitrous_power_factor = self.factor(car, PerformanceCategory::Power, parts[0])?;
        let handling = self.factor(car, PerformanceCategory::Handling, parts[1])?;
        if handling != 1. {
            let stock = self.human_handling_scale;
            let tuned = handling * stock;
            let stock_brakes = car.brake_factor * stock;
            let tuned_brakes = car.brake_factor * tuned;
            result.footbrake_mu *= tuned_brakes / stock_brakes;
            // Source rear coefficient comes from original FRONT baseline in both
            // paths, so the normalized rear upgrade delta is zero.
            let delta = car.suspension_factor.mul_add(tuned, -1.) * self.suspension_gain;
            let stock_delta = car.suspension_factor.mul_add(stock, -1.) * self.suspension_gain;
            result.damping_ratio += delta - stock_delta;
            if !drift_discipline {
                let gain = |value: f32| -> f32 { (value - 1.) * self.suspension_gain + 1. };
                let stock_gain = car.tyre_factor * gain(stock);
                let tuned_gain = car.tyre_factor * gain(tuned);
                result.tyre_mu *= (tuned_gain * self.front_tyre_scale) / (stock_gain * self.front_tyre_scale);
                result.rear_tyre_mu = baseline.rear_tyre_mu.map(|mu| mu * ((tuned_gain * self.rear_tyre_scale) / (stock_gain * self.rear_tyre_scale)));
                if baseline.rear_tyre_mu.is_none() {
                    result.rear_tyre_mu = Some(baseline.tyre_mu * ((tuned_gain * self.rear_tyre_scale) / (stock_gain * self.rear_tyre_scale)));
                }
            }
        }
        Ok(result)
    }
    /// 8210AAA8 uses the stock ratio; its fallback differs from8210A968.
    pub fn minimum_potential_league(&self, car: &NativePerformanceFields) -> u8 {
        let ratio = car.stock_power / car.stock_weight;
        for (index, league) in self.packages.iter().enumerate() {
            let lower = if index == 0 {
                0.01
            } else {
                self.packages[index - 1].threshold
            };
            if ratio < league.threshold && ratio > lower {
                return index as u8;
            }
        }
        0
    }
    /// 821CB9D0 normal item quote: signed integer division by steps, not steps-1.
    pub fn package_price(
        &self,
        league: u8,
        category: PerformanceCategory,
        item: u32,
        prototype: bool,
    ) -> Result<u32, String> {
        let pack = self
            .packages
            .get(usize::from(league))
            .ok_or("Invalid package league")?;
        if prototype {
            return Ok(match league {
                4 => 20000,
                5 => 26000,
                6 => 40000,
                7 => 56000,
                8 => 82000,
                9 => 150000,
                _ => 12000,
            });
        }
        if pack.steps == 0 || item >= pack.steps {
            return Err("Invalid package item".into());
        }
        let offset = category.index() * 2;
        let minimum = pack.native_price_operands[offset] as i32;
        let maximum = pack.native_price_operands[offset + 1] as i32;
        let delta = maximum.wrapping_sub(minimum).wrapping_mul(item as i32) / pack.steps as i32;
        Ok((minimum as f32 + delta as f32).trunc() as u32)
    }
    /// 8210CFA0 clears at-1; otherwise caps the item to this league's last step.
    pub fn installed_package(&self, league: u8, item: i32) -> Result<u32, String> {
        let pack = self
            .packages
            .get(usize::from(league))
            .ok_or("Invalid package league")?;
        if item == -1 {
            return Ok(0);
        }
        if item < -1 || pack.steps == 0 {
            return Err("Invalid package item".into());
        }
        let item = (item as u32).min(pack.steps - 1);
        Ok(0x40000000 | ((u32::from(league) << 25) & 0x3e000000) | (item & 0x01ffffff))
    }
    /// 8210A968 uses maximum potential, and BOTH range comparisons are strict.
    pub fn maximum_potential_league(&self, car: &NativePerformanceFields) -> u8 {
        let ratio = car.max_power / car.min_weight;
        for (index, league) in self.packages.iter().enumerate() {
            let lower = if index == 0 {
                0.01
            } else {
                self.packages[index - 1].threshold
            };
            if ratio < league.threshold && ratio > lower {
                return index as u8;
            }
        }
        9
    }

    /// 8210AB70: ANY installed category at max-potential league, item index3.
    pub fn prototype_eligible(&self, car: &NativePerformanceFields, parts: [u32; 3]) -> bool {
        let league = i32::from(self.maximum_potential_league(car));
        parts
            .into_iter()
            .any(|raw| native_package_decode(raw) == Some((league, 3)))
    }

    /// The source searches in .001 steps and can return -.001; do not clamp it.
    pub fn factor(
        &self,
        car: &NativePerformanceFields,
        category: PerformanceCategory,
        raw: u32,
    ) -> Result<f32, String> {
        let Some((league, item)) = native_package_decode(raw) else {
            return Ok(1.);
        };
        let pack = self
            .packages
            .get(usize::try_from(league).map_err(|_| "Invalid package league")?)
            .ok_or("Invalid package league")?;
        if category == PerformanceCategory::Handling {
            return Ok(
                ((league * 4 + item as i32) as f32 * self.handling_increment)
                    .mul_add(self.handling_scale, 1.),
            );
        }
        let stock_ratio = car.stock_power / car.stock_weight;
        let max_ratio = car.max_power / car.min_weight;
        let lower = if league <= 0 {
            0.01
        } else {
            self.packages[league as usize - 1].threshold
        };
        let lower = lower.max(stock_ratio).min(max_ratio);
        let upper = pack.threshold.max(stock_ratio).min(max_ratio);
        let fraction = (1. / pack.steps as f32) * (item + 1) as f32;
        let target = (1. - fraction).mul_add(lower, fraction * upper);
        let mut scan = 0.0_f32;
        let mut blend = 1.0_f32;
        while scan <= 1. {
            let power = (1. - scan).mul_add(car.stock_power, car.max_power * scan);
            let weight = (1. - scan).mul_add(car.stock_weight, car.min_weight * scan);
            if power / weight >= target {
                blend = scan - 0.001;
                break;
            }
            scan += 0.001;
        }
        Ok(match category {
            PerformanceCategory::Power => {
                (car.max_power - car.stock_power).mul_add(blend, car.stock_power) / car.stock_power
            }
            PerformanceCategory::Weight => {
                car.stock_weight
                    / (-(car.stock_weight - car.min_weight)).mul_add(blend, car.stock_weight)
            }
            PerformanceCategory::Handling => unreachable!(),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn civic() -> NativePerformanceFields {
        NativePerformanceFields {
            stock_power: 250.,
            stock_weight: 1090.,
            max_power: 405.,
            min_weight: 965.,
            brake_factor: 1.,
            tyre_factor: 1.,
            suspension_factor: 1.,
            turbo_factor: 1.,
            cost_modifier: 1.5,
        }
    }
    #[test]
    fn source_packed_prototype_is_max_potential_and_any_category() {
        let catalog = NativePerformanceCatalog::default();
        let car = civic();
        assert_eq!(catalog.maximum_potential_league(&car), 4);
        assert!(catalog.prototype_eligible(&car, [0, 0x48000003, 0]));
        assert!(!catalog.prototype_eligible(&car, [0x46000003, 0, 0]));
        assert!(!catalog.prototype_eligible(&car, [0x48000002, 0, 0]));
        assert!(!catalog.prototype_eligible(&car, [0x08000003, 0, 0]));
        assert_eq!(native_package_decode(0x7e000003), Some((-1, 3)));
        assert_eq!(catalog.installed_package(0, 10).unwrap(), 0x40000002);
        assert_eq!(catalog.installed_package(4, 3).unwrap(), 0x48000003);
        assert_eq!(catalog.installed_package(4, -1).unwrap(), 0);
        let mut boundary = civic();
        boundary.min_weight = 1.;
        boundary.max_power = catalog.packages[4].threshold;
        assert_eq!(catalog.maximum_potential_league(&boundary), 9);
        assert_eq!(
            catalog
                .package_price(0, PerformanceCategory::Power, 0, false)
                .unwrap(),
            7500
        );
        assert_eq!(
            catalog
                .package_price(0, PerformanceCategory::Power, 1, false)
                .unwrap(),
            8166
        );
        assert_eq!(
            catalog
                .package_price(0, PerformanceCategory::Power, 2, false)
                .unwrap(),
            8833
        );
        assert_eq!(
            catalog
                .package_price(0, PerformanceCategory::Handling, 0, false)
                .unwrap(),
            3000
        );
        assert_eq!(
            catalog
                .package_price(0, PerformanceCategory::Weight, 0, false)
                .unwrap(),
            5500
        );
        assert_eq!(
            catalog
                .package_price(4, PerformanceCategory::Power, 3, true)
                .unwrap(),
            20000
        );
    }
    #[test]
    fn source_scan_preserves_negative_first_step_and_handling_operand_order() {
        let catalog = NativePerformanceCatalog::default();
        let car = civic();
        assert_eq!(
            catalog.factor(&car, PerformanceCategory::Power, 0).unwrap(),
            1.
        );
        // Rookie target is clamped up to the car's stock ratio; first scan succeeds at0.
        assert_eq!(
            catalog
                .factor(&car, PerformanceCategory::Power, 0x40000000)
                .unwrap(),
            155.0_f32.mul_add(-0.001, 250.) / 250.
        );
        assert_eq!(
            catalog
                .factor(&car, PerformanceCategory::Handling, 0x48000003)
                .unwrap(),
            (19.0_f32 * 0.025).mul_add(0.75, 1.)
        );
        assert!(catalog
            .factor(&car, PerformanceCategory::Weight, 0x7e000003)
            .is_err());
        assert_eq!(
            native_package_selection_state(0, 0, 0, 0, true, false, false),
            1
        );
        assert_eq!(
            native_package_selection_state(0, 0, 1, 0, false, true, false),
            2
        );
        assert_eq!(
            native_package_selection_state(0, 0, 2, 0, false, false, false),
            0
        );
        assert_eq!(
            native_package_selection_state(0x48000003, 0, 0, 4, true, false, false),
            4
        );
        assert_eq!(
            native_package_selection_state(0x48000003, 4, 3, 4, true, true, true),
            3
        );
    }
}

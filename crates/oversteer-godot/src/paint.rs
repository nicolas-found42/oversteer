//! Source material-record edits. Disc-initial globals are an explicit donor seed
//! adapter, not a claim about the original game's initialized runtime globals.
use oversteer_core::{Customization, NativePaintRecord};
use serde_json::Value;

fn data() -> Value {
    serde_json::from_str(include_str!("native-paint.json")).expect("verified source paint writer")
}

pub fn provenance() -> Value {
    serde_json::json!({
        "record_writer": "820F8F78/820F9428; typed72-byte source material",
        "missing_record_seed": "820F8DB8 constructor plus retained disc-global snapshot; initialized runtime globals remain partly unbound",
        "unbound_global_writes": "Explicit native_global expressions use retained disc snapshots as a frontend adapter, not proven initialized coefficients; offsets not written by the source path remain unchanged",
        "pearl_balance": "820F9428 default x*span+bias, with CRT82474BB0 initialized span1/bias0; later indirect writes not excluded",
        "rendering": "Godot PBR translation; original GPU BRDF not recovered",
        "workflow": "821C5E20 ordered color/scalar stages; one final draft and whole-session cancel. Scalar widget layout remains adapted"
    })
}

pub fn donor_seed(custom: &Customization) -> NativePaintRecord {
    if let Some(record) = &custom.native_paint {
        return record.clone();
    }
    // 820F8DB8 plus the retained image's initialized-data snapshot. RGB is
    // subsequently replaced by the donor's selected color through channel0.
    let mut raw = [0; 72];
    for (offset, value) in [
        (4, 1_f32),
        (28, 1.),
        (44, 0.05),
        (48, 0.25),
        (52, 0.5199999809265137),
        (56, 100.),
    ] {
        raw[offset..offset + 4].copy_from_slice(&value.to_be_bytes());
    }
    NativePaintRecord::from_be_bytes(&raw).expect("source constructor record layout")
}

pub fn color(
    record: &mut NativePaintRecord,
    family: &str,
    channel: u32,
    rgb: [f32; 3],
) -> Result<(), String> {
    let table = data();
    let family = table["families"]
        .as_array()
        .unwrap()
        .iter()
        .find(|item| item["id"].as_str() == Some(family))
        .ok_or("Unknown native paint family")?;
    let channel = channel.to_string();
    let values = family["material_state_by_channel"][&channel]
        .as_object()
        .ok_or("This paint family has no such color channel")?;
    let before = record.to_be_bytes();
    let mut after = before;
    after[0..4].copy_from_slice(&(family["native_enum"].as_u64().unwrap() as u32).to_be_bytes());
    for (offset, expression) in values {
        let offset: usize = offset.parse().map_err(|_| "Invalid source paint offset")?;
        let value = evaluate(expression, rgb, &before)?;
        after[offset..offset + 4].copy_from_slice(&value.to_be_bytes());
    }
    *record = NativePaintRecord::from_be_bytes(&after)?;
    Ok(())
}

fn evaluate(expression: &Value, input: [f32; 3], previous: &[u8; 72]) -> Result<f32, String> {
    if let Some(value) = expression.as_f64() {
        return Ok(value as f32);
    }
    if let Some(token) = expression.as_str() {
        if let Some(index) = ["input.r", "input.g", "input.b"]
            .iter()
            .position(|t| *t == token)
        {
            return Ok(input[index]);
        }
        if let Some(offset) = token
            .strip_prefix("previous.material[")
            .and_then(|v| v.strip_suffix(']'))
            .and_then(|v| v.parse::<usize>().ok())
        {
            let bytes = previous
                .get(offset..offset + 4)
                .ok_or("Invalid previous material offset")?;
            return Ok(f32::from_be_bytes(bytes.try_into().unwrap()));
        }
        return Err(format!("Unbound native paint expression {token}"));
    }
    for operator in ["subtract", "multiply"] {
        if let Some(args) = expression[operator].as_array() {
            let a = evaluate(&args[0], input, previous)?;
            let b = evaluate(&args[1], input, previous)?;
            return Ok(if operator == "subtract" { a - b } else { a * b });
        }
    }
    if expression["native_global"].is_string() {
        return expression["disc_initial"]
            .as_f64()
            .map(|v| v as f32)
            .ok_or_else(|| "No disc snapshot for paint runtime global".into());
    }
    if let Some(call) = expression["source_call"].as_str() {
        let args = expression["inputs"]
            .as_array()
            .ok_or("Missing paint function arguments")?;
        let values = [
            evaluate(&args[0], input, previous)?,
            evaluate(&args[1], input, previous)?,
            evaluate(&args[2], input, previous)?,
        ];
        let result = match call {
            "8207ac80" => rgb_to_hsv(values),
            "8207adc0" => hsv_to_rgb(values),
            _ => return Err(format!("Unbound paint function {call}")),
        };
        return result
            .get(
                expression["component"]
                    .as_u64()
                    .ok_or("Missing result component")? as usize,
            )
            .copied()
            .ok_or_else(|| "Invalid paint result component".into());
    }
    Err("Unsupported native paint expression".into())
}

// 8207AC80: explicit f32 epsilon and branch order retained.
fn rgb_to_hsv([r, g, b]: [f32; 3]) -> [f32; 3] {
    let min = r.min(g).min(b);
    let max = r.max(g).max(b);
    let chroma = max - min;
    if max == 0. {
        return [-1., 0., max];
    }
    let saturation = chroma / max;
    let divisor = chroma + f32::EPSILON;
    let sector = if r == max {
        (g - b) / divisor
    } else if g == max {
        (b - r) / divisor + 2.
    } else {
        (r - g) / divisor + 4.
    };
    let mut hue = sector * 60.;
    if hue < 0. {
        hue += 360.;
    }
    [hue, saturation, max]
}
// 8207ADC0: normalized sector arithmetic, f32 FMADD and original sector cases.
fn hsv_to_rgb([h, s, v]: [f32; 3]) -> [f32; 3] {
    if s == 0. {
        return [v; 3];
    }
    let s = s.min(1.);
    let h = h * 0.01666666753590107_f32;
    let sector = h.floor();
    let f = h - sector;
    let p = (1. - s) * v;
    let q = (-s).mul_add(f, 1.) * v;
    let t = (-(1. - f)).mul_add(s, 1.) * v;
    match sector as i32 {
        0 => [v, t, p],
        1 => [q, v, p],
        2 => [p, v, t],
        3 => [p, q, v],
        4 => [t, p, v],
        _ => [v, p, q],
    }
}

/// Ordered accept stages recovered from 821C5E20. Color channels and scalar
/// channels are kept distinct so accepting an intermediate stage cannot create
/// a partial purchased paint item.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stage {
    Color(u32),
    Scalar(u32),
}

pub struct Session {
    pub original: Customization,
    pub family: String,
    pub cursor: usize,
}
impl Session {
    pub fn stage(&self) -> Option<Stage> {
        stages(&self.family).get(self.cursor).copied()
    }
}

pub fn stages(family: &str) -> &'static [Stage] {
    use Stage::{Color, Scalar};
    match family {
        "pearl" => &[Color(0), Color(1), Scalar(2)],
        "flake" => &[Color(0), Color(3), Scalar(4), Scalar(5)],
        "thinfilm" => &[Color(0), Scalar(6)],
        "gloss" | "metallic" | "matt" => &[Color(0)],
        _ => &[],
    }
}

pub fn scalar(record: &mut NativePaintRecord, channel: u32, value: f32) -> Result<(), String> {
    match (record.native_type, channel) {
        (2, 4) => record.flakie = value.mul_add(0.699999988079071, 0.30000001192092896),
        (2, 5) => record.fleck_power = value.mul_add(48., 100.),
        (5, 6) => record.film_thickness = value.mul_add(0.019999999552965164, 0.005499999970197678),
        // xstart ->823D8398 invokes initializer82474BB0: span=f32(1-bias).
        // Retained bias0 gives initialized span1. This is the source default,
        // not a claim that every later indirect global write is excluded.
        (3, 2) => record.two_tone_exp = value.mul_add(1., 0.),
        _ => return Err("This paint family has no such scalar channel".into()),
    }
    record.raw_be_bytes = record.to_be_bytes().to_vec();
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn workflow_retains_all_required_accept_stages() {
        assert_eq!(
            stages("pearl"),
            &[Stage::Color(0), Stage::Color(1), Stage::Scalar(2)]
        );
        assert_eq!(
            stages("flake"),
            &[
                Stage::Color(0),
                Stage::Color(3),
                Stage::Scalar(4),
                Stage::Scalar(5)
            ]
        );
        assert_eq!(stages("thinfilm"), &[Stage::Color(0), Stage::Scalar(6)]);
        assert!(stages("chrome").is_empty());
    }
    #[test]
    fn actual_color_paths_preserve_other_fields_and_roundtrip() {
        let custom = Customization::default();
        let mut record = donor_seed(&custom);
        record.fleck_locality = 0.375;
        color(&mut record, "flake", 0, [0.2, 0.4, 0.7]).unwrap();
        let base = record.base_rgb;
        let secondary = record.secondary_rgb;
        color(&mut record, "flake", 3, [0.8, 0.3, 0.1]).unwrap();
        assert_eq!(record.base_rgb, base);
        assert_eq!(record.secondary_rgb, secondary);
        assert_eq!(record.fleck_rgb, [0.8, 0.3, 0.1]);
        assert_eq!(record.fleck_locality, 0.375);
        assert_eq!(
            NativePaintRecord::from_be_bytes(&record.to_be_bytes()).unwrap(),
            record
        );
    }
    #[test]
    fn source_hsv_shift_and_scalar_boundaries_have_expected_values() {
        let mut hsv = rgb_to_hsv([0.8, 0.3, 0.1]);
        hsv[0] += 30.;
        hsv[1] *= 0.8;
        hsv[2] *= 1.2;
        let output = hsv_to_rgb(hsv);
        for (value, expected) in output.into_iter().zip([0.96, 0.816, 0.288]) {
            assert!((value - expected).abs() < 0.000002);
        }
        let mut record = donor_seed(&Customization::default());
        record.native_type = 2;
        scalar(&mut record, 4, 0.).unwrap();
        assert_eq!(record.flakie, 0.3);
        scalar(&mut record, 5, 1.).unwrap();
        assert_eq!(record.fleck_power, 148.);
        record.native_type = 3;
        scalar(&mut record, 2, 0.5).unwrap();
        assert_eq!(record.two_tone_exp, 0.5);
    }
}

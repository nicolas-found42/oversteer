//! Presentation-only formatting shared by menus, confirmations and instruments.
pub fn money(value: i64) -> String {
    format!(
        "{}${}",
        if value < 0 { "-" } else { "" },
        grouped_integer(value.unsigned_abs())
    )
}

pub fn grouped_integer(value: u64) -> String {
    let digits = value.to_string();
    let mut grouped = String::new();
    for (index, digit) in digits.chars().enumerate() {
        if index > 0 && (digits.len() - index).is_multiple_of(3) {
            grouped.push(',');
        }
        grouped.push(digit);
    }
    grouped
}

pub fn vehicle_name(value: &str) -> String {
    let mut words: Vec<_> = value.split_whitespace().collect();
    if words.len() > 1 && words[0].eq_ignore_ascii_case(words[1]) {
        words.remove(1);
    }
    words.join(" ")
}

pub fn map_heading(forward_x: f32, forward_z: f32) -> f32 {
    forward_x.atan2(-forward_z)
}

/// Fine concrete variation and expansion joints, limited to the menu showroom.
pub const WORKSHOP_FLOOR_SHADER: &str = r#"
shader_type spatial;
varying vec3 world_position;
void vertex() {
    world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}
void fragment() {
    vec2 p = world_position.xz;
    float grain = fract(sin(dot(floor(p * 180.0), vec2(12.9898, 78.233))) * 43758.5453);
    vec2 joint = abs(fract(p / 3.5 + 0.5) - 0.5) * 2.0;
    vec2 aa = max(fwidth(p), vec2(0.003));
    float seam = 1.0 - min(smoothstep(0.006, 0.006 + aa.x, joint.x),
                           smoothstep(0.006, 0.006 + aa.y, joint.y));
    ALBEDO = mix(vec3(0.028, 0.029, 0.030) + grain * 0.007, vec3(0.012), seam * 0.3);
    ROUGHNESS = 0.78;
    SPECULAR = 0.15;
}
"#;

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn minimap_chevron_follows_projected_world_forward() {
        for (x, z) in [(0., 1.), (1., 0.), (0., -1.), (-1., 0.)] {
            let angle = map_heading(x, z);
            // The unrotated glyph points up; route X/Z project to screen X/Y.
            assert!((angle.sin() - x).abs() < 0.00001);
            assert!((-angle.cos() - z).abs() < 0.00001);
        }
    }

    #[test]
    fn purchase_balance_is_explicit_and_grouped() {
        assert_eq!(money(25_000), "$25,000");
        assert_eq!(money(25_000 - 19_500), "$5,500");
        assert_eq!(money(-1_000), "-$1,000");
        assert_eq!(money(0), "$0");
    }

    #[test]
    fn vehicle_display_removes_only_duplicate_manufacturer() {
        assert_eq!(vehicle_name("Honda HONDA S2000 ’03"), "Honda S2000 ’03");
        assert_eq!(vehicle_name("MINI Cooper S"), "MINI Cooper S");
        assert_eq!(vehicle_name("Mazda MX-5"), "Mazda MX-5");
    }
}

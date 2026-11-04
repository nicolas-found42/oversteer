//! Code-only typography, metal instrument faces and live transparent dial overlays.
use godot::classes::{ColorRect, Control, Font, FontFile, FontVariation, Shader, ShaderMaterial};
use godot::prelude::*;

pub const START_DEGREES: f32 = 140.;
// Keep the engine-limit band above the overlapping speedometer.
pub const SWEEP_DEGREES: f32 = 190.;

pub fn font() -> Gd<Font> {
    let mut source = godot::tools::load::<FontFile>("res://ui/fonts/Exo2-Italic-Variable.ttf");
    source.set_multichannel_signed_distance_field(true);
    let mut font = FontVariation::new_gd();
    font.set_base_font(&source.upcast::<Font>());
    let text_server = godot::classes::TextServerManager::singleton()
        .get_primary_interface()
        .expect("Godot text server");
    let weight = text_server.name_to_tag("wght");
    font.set_variation_opentype(&vdict! { weight => 800. }.upcast_any_dictionary());
    let tabular_numbers = text_server.name_to_tag("tnum");
    font.set_opentype_features(&vdict! { tabular_numbers => 1 }.upcast_any_dictionary());
    font.upcast()
}

pub fn bezel(parent: &mut Gd<Control>, center: Vector2, radius: f32, amber: bool, cyan_ring: bool) {
    let mut shader = Shader::new_gd();
    shader.set_code(BEZEL_SHADER);
    let mut material = ShaderMaterial::new_gd();
    material.set_shader(&shader);
    material.set_shader_parameter("amber", &amber.to_variant());
    material.set_shader_parameter("cyan_ring", &cyan_ring.to_variant());
    let mut face = ColorRect::new_alloc();
    face.set_position(center - Vector2::ONE * radius);
    face.set_size(Vector2::ONE * radius * 2.);
    face.set_material(&material);
    face.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
    parent.add_child(&face);
}

pub fn plaque(parent: &mut Gd<Control>, rect: Rect2) {
    for (inset, color) in [
        (0., Color::from_rgb(0.025, 0.032, 0.04)),
        (1.5, Color::from_rgb(0.56, 0.60, 0.64)),
        (4., Color::from_rgb(0.055, 0.065, 0.08)),
    ] {
        let position = rect.position + Vector2::ONE * inset;
        let size = rect.size - Vector2::ONE * inset * 2.;
        let cut = (size.y * 0.28).min(14.);
        let mut plate = godot::classes::Polygon2D::new_alloc();
        plate.set_polygon(&PackedVector2Array::from(&[
            position + Vector2::new(cut, 0.),
            position + Vector2::new(size.x, 0.),
            position + Vector2::new(size.x - cut, size.y),
            position + Vector2::new(0., size.y),
        ]));
        plate.set_color(color);
        parent.add_child(&plate);
    }
}

/// `steps` is the number of major intervals, e.g. RPM limit / 1000 or 240 / 20.
/// Update the returned material's `value` uniform with the actual normalized reading.
/// Optional `cover_center` and `cover_radius` use dial-radius units relative to its center.
pub fn dial(
    parent: &mut Gd<Control>,
    center: Vector2,
    radius: f32,
    steps: f32,
    dark_ink: bool,
) -> Gd<ShaderMaterial> {
    let mut shader = Shader::new_gd();
    shader.set_code(DIAL_SHADER);
    let mut material = ShaderMaterial::new_gd();
    material.set_shader(&shader);
    material.set_shader_parameter("steps", &steps.to_variant());
    material.set_shader_parameter("dark_ink", &dark_ink.to_variant());
    material.set_shader_parameter("start_angle", &START_DEGREES.to_radians().to_variant());
    material.set_shader_parameter("sweep_angle", &SWEEP_DEGREES.to_radians().to_variant());
    let mut overlay = ColorRect::new_alloc();
    overlay.set_position(center - Vector2::ONE * radius);
    overlay.set_size(Vector2::ONE * radius * 2.);
    overlay.set_material(&material);
    overlay.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
    parent.add_child(&overlay);
    material
}

const DIAL_SHADER: &str = r#"
shader_type canvas_item;
render_mode unshaded;
uniform float value : hint_range(0.0, 1.0) = 0.0;
uniform float steps = 12.0;
uniform bool dark_ink = true;
uniform float start_angle = 2.443461;
uniform float sweep_angle = 3.316126;
uniform vec2 cover_center = vec2(0.0);
uniform float cover_radius = 0.0;

void fragment() {
    vec2 p = (UV - vec2(0.5)) * 2.0;
    float radius = length(p);
    float aa = max(fwidth(radius), 0.001);
    float angle = atan(p.y, p.x);
    if (angle < start_angle) { angle += TAU; }
    float progress = (angle - start_angle) / sweep_angle;
    float minor_count = max(steps * 5.0, 1.0);
    float tick_index = floor(progress * minor_count + 0.5);
    float tick_angle = start_angle + tick_index * sweep_angle / minor_count;
    float angular_distance = abs(angle - tick_angle) * radius;
    bool major = mod(tick_index, 5.0) < 0.5;
    // Marks stay outside the numeral ring, leaving the dial face visible.
    float inner = major ? 0.82 : 0.88;
    float width = major ? 0.009 : 0.004;
    float ticks = (1.0 - smoothstep(width, width + aa, angular_distance))
        * smoothstep(inner - aa, inner, radius)
        * (1.0 - smoothstep(0.95, 0.95 + aa, radius))
        * step(0.0, progress) * step(progress, 1.0);
    vec3 ink = dark_ink ? vec3(0.045, 0.035, 0.025) : vec3(0.96, 0.97, 0.95);
    vec4 color = vec4(ink, ticks);
    if (!dark_ink) {
        float redline = smoothstep(0.85, 0.855, progress) * step(progress, 1.0)
            * smoothstep(0.96 - aa, 0.96, radius)
            * (1.0 - smoothstep(0.985, 0.985 + aa, radius));
        color.rgb = mix(color.rgb, vec3(0.96, 0.12, 0.055), redline);
        color.a = max(color.a, redline);
    }

    float needle_angle = start_angle + clamp(value, 0.0, 1.0) * sweep_angle;
    vec2 direction = vec2(cos(needle_angle), sin(needle_angle));
    float along = dot(p, direction);
    float across = dot(p, vec2(-direction.y, direction.x));
    float taper = mix(0.035, 0.005, clamp((along + 0.12) / 0.92, 0.0, 1.0));
    float needle = (1.0 - smoothstep(taper, taper + aa, abs(across)))
        * smoothstep(-0.17 - aa, -0.17, along)
        * (1.0 - smoothstep(0.80, 0.80 + aa, along));
    vec3 needle_color = mix(vec3(1.0, 0.71, 0.08), vec3(0.86, 0.10, 0.035),
        smoothstep(-0.006, 0.016, across));
    color.rgb = mix(color.rgb, needle_color, needle);
    color.a = max(color.a, needle);

    float hub = 1.0 - smoothstep(0.095, 0.095 + aa, radius);
    vec3 hub_color = mix(vec3(0.025), vec3(0.18),
        clamp(0.5 - p.y * 4.0 - p.x * 2.0, 0.0, 1.0));
    color.rgb = mix(color.rgb, hub_color, hub);
    color.a = max(color.a, hub);
    if (cover_radius > 0.0) {
        color.a *= smoothstep(cover_radius, cover_radius + aa, length(p - cover_center));
    }
    COLOR = color;
}
"#;

const BEZEL_SHADER: &str = r#"
shader_type canvas_item;
render_mode unshaded;
uniform bool amber = false;
uniform bool cyan_ring = false;

void fragment() {
    vec2 p = (UV - vec2(0.5)) * 2.0;
    float radius = length(p);
    float aa = max(fwidth(radius), 0.001);
    vec2 normal = p / max(radius, 0.001);
    float light = dot(normal, normalize(vec2(-0.45, -0.9)));
    // Broad reflected light bands and a narrow bevel; no texture or procedural noise.
    float reflection = pow(abs(light), 6.0);
    vec3 steel = mix(vec3(0.15, 0.18, 0.21), vec3(0.65, 0.70, 0.75), reflection);
    float bevel = sin(clamp((radius - 0.885) / 0.10, 0.0, 1.0) * PI);
    steel *= 0.50 + 0.65 * bevel;
    float outer = smoothstep(0.975, 0.992, radius);
    steel = mix(steel, vec3(0.035, 0.043, 0.052), outer);
    float inner_lip = 1.0 - smoothstep(0.895, 0.915, radius);
    steel = mix(steel, vec3(0.035, 0.045, 0.055), inner_lip);

    float vertical = clamp(p.y * 0.5 + 0.5, 0.0, 1.0);
    vec3 face = amber
        ? mix(vec3(1.0, 0.67, 0.08), vec3(0.76, 0.34, 0.025), vertical)
        : mix(vec3(0.055, 0.085, 0.11), vec3(0.012, 0.02, 0.03), vertical);
    face *= 1.0 - 0.20 * smoothstep(0.60, 0.89, radius);
    float face_mask = 1.0 - smoothstep(0.88, 0.89, radius);
    vec3 color = mix(steel, face, face_mask);
    if (cyan_ring) {
        float ring = smoothstep(0.866 - aa, 0.866, radius)
            * (1.0 - smoothstep(0.875, 0.875 + aa, radius));
        color = mix(color, vec3(0.02, 0.86, 0.92), ring);
    }
    COLOR = vec4(color, 1.0 - smoothstep(0.99, 0.99 + aa, radius));
}
"#;

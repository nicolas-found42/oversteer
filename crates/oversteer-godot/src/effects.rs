//! Reconstructed tyre/nitrous particles and lamps; the donor body meshes remain unchanged.
use godot::classes::{
    GpuParticles3D, Gradient, GradientTexture2D, Node3D, OmniLight3D, ParticleProcessMaterial,
    QuadMesh, SpotLight3D, StandardMaterial3D,
};
use godot::prelude::*;
use oversteer_core::{PlayerInput, RacerSnapshot};
pub struct CarEffects {
    smoke: Vec<Gd<GpuParticles3D>>,
    flame: Gd<GpuParticles3D>,
    nitro_light: Gd<OmniLight3D>,
    brakes: Vec<Gd<OmniLight3D>>,
    previous_speed: f32,
}
impl CarEffects {
    pub fn new(car: &mut Gd<Node3D>, length: f32, width: f32) -> Self {
        let mut smoke = vec![];
        for sign in [-1., 1.] {
            let mut emitter = particles(Color::from_rgba(0.7, 0.72, 0.74, 0.25), 1.15, 48, false);
            emitter.set_position(Vector3::new(sign * width * 0.39, 0.16, length * 0.30));
            car.add_child(&emitter);
            smoke.push(emitter);
        }
        let mut flame = particles(Color::from_rgba(0.08, 0.4, 1., 0.7), 0.20, 24, true);
        flame.set_position(Vector3::new(-width * 0.3, 0.3, length * 0.48));
        car.add_child(&flame);
        let mut nitro_light = OmniLight3D::new_alloc();
        nitro_light.set_position(Vector3::new(-width * 0.3, 0.3, length * 0.5));
        nitro_light.set_color(Color::from_rgb(0.08, 0.35, 1.));
        nitro_light.set_param(godot::classes::light_3d::Param::RANGE, 2.5);
        nitro_light.set_visible(false);
        car.add_child(&nitro_light);
        let mut brakes = vec![];
        for sign in [-1., 1.] {
            let mut lamp = OmniLight3D::new_alloc();
            lamp.set_position(Vector3::new(sign * width * 0.32, 0.5, length * 0.43));
            lamp.set_color(Color::from_rgb(1., 0.015, 0.005));
            lamp.set_param(godot::classes::light_3d::Param::RANGE, 2.);
            lamp.set_param(godot::classes::light_3d::Param::ENERGY, 0.15);
            car.add_child(&lamp);
            brakes.push(lamp);
            let mut head = SpotLight3D::new_alloc();
            head.set_position(Vector3::new(sign * width * 0.32, 0.5, -length * 0.43));
            head.set_rotation_degrees(Vector3::new(-7., 0., 0.));
            head.set_color(Color::from_rgb(0.78, 0.88, 1.));
            head.set_param(godot::classes::light_3d::Param::ENERGY, 3.);
            head.set_param(godot::classes::light_3d::Param::RANGE, 32.);
            car.add_child(&head);
        }
        Self {
            smoke,
            flame,
            nitro_light,
            brakes,
            previous_speed: 0.,
        }
    }
    pub fn update(&mut self, racer: &RacerSnapshot, input: Option<PlayerInput>, paused: bool) {
        let q = Quaternion::new(
            racer.rotation[0],
            racer.rotation[1],
            racer.rotation[2],
            racer.rotation[3],
        );
        let velocity =
            q.inverse() * Vector3::new(racer.velocity[0], racer.velocity[1], racer.velocity[2]);
        let sliding = racer.speed_kph > 22.
            && (velocity.x.abs() > 2. || input.is_some_and(|i| i.handbrake > 0.4));
        let nitrous = racer.nitrous_active && !paused;
        for smoke in &mut self.smoke {
            smoke.set_emitting(sliding && !paused);
            smoke.set_speed_scale(if paused { 0. } else { 1. });
        }
        self.flame.set_emitting(nitrous);
        self.flame.set_speed_scale(if paused { 0. } else { 1. });
        self.nitro_light.set_visible(nitrous);
        let braking =
            input.is_some_and(|i| i.brake > 0.1) || racer.speed_kph < self.previous_speed - 0.1;
        for lamp in &mut self.brakes {
            lamp.set_param(
                godot::classes::light_3d::Param::ENERGY,
                if braking { 2.5 } else { 0.15 },
            );
        }
        self.previous_speed = racer.speed_kph;
    }
    pub fn summary(&self) -> serde_json::Value {
        serde_json::json!({"tyre_smoke":self.smoke.iter().any(|s|s.is_emitting()),"nitrous_flame":self.flame.is_emitting(),"presentation":"reconstructed particles and lights"})
    }
}
fn particles(color: Color, lifetime: f64, amount: i32, flame: bool) -> Gd<GpuParticles3D> {
    use godot::classes::particle_process_material::{EmissionShape, Parameter};
    let mut gradient = Gradient::new_gd();
    gradient.set_colors(&PackedColorArray::from(
        &[color, Color::from_rgba(color.r, color.g, color.b, 0.)][..],
    ));
    let mut texture = GradientTexture2D::new_gd();
    texture.set_gradient(&gradient);
    texture.set_fill(godot::classes::gradient_texture_2d::Fill::RADIAL);
    texture.set_fill_from(Vector2::new(0.5, 0.5));
    texture.set_fill_to(Vector2::new(0.5, 0.));
    let mut material = StandardMaterial3D::new_gd();
    material.set_texture(
        godot::classes::base_material_3d::TextureParam::ALBEDO,
        &texture,
    );
    material.set_transparency(godot::classes::base_material_3d::Transparency::ALPHA);
    material.set_shading_mode(godot::classes::base_material_3d::ShadingMode::UNSHADED);
    material.set_billboard_mode(godot::classes::base_material_3d::BillboardMode::ENABLED);
    let mut mesh = QuadMesh::new_gd();
    mesh.set_size(Vector2::ONE);
    mesh.set_material(&material);
    let mut process = ParticleProcessMaterial::new_gd();
    process.set_emission_shape(EmissionShape::SPHERE);
    process.set_emission_sphere_radius(0.1);
    process.set_direction(if flame {
        Vector3::new(0., 0., 1.)
    } else {
        Vector3::UP
    });
    process.set_spread(if flame { 10. } else { 65. });
    process.set_gravity(if flame {
        Vector3::ZERO
    } else {
        Vector3::UP * 0.2
    });
    process.set_param_min(
        Parameter::INITIAL_LINEAR_VELOCITY,
        if flame { 3. } else { 0.4 },
    );
    process.set_param_max(
        Parameter::INITIAL_LINEAR_VELOCITY,
        if flame { 5. } else { 0.8 },
    );
    process.set_param_min(Parameter::SCALE, if flame { 0.12 } else { 0.4 });
    process.set_param_max(Parameter::SCALE, if flame { 0.25 } else { 1.1 });
    let mut emitter = GpuParticles3D::new_alloc();
    emitter.set_amount(amount);
    emitter.set_lifetime(lifetime);
    emitter.set_use_local_coordinates(false);
    emitter.set_visibility_aabb(Aabb::new(
        Vector3::new(-8., -2., -8.),
        Vector3::new(16., 8., 16.),
    ));
    emitter.set_process_material(&process);
    emitter.set_draw_pass_mesh(0, &mesh);
    emitter.set_emitting(false);
    emitter
}

//! Read actual rendered material instances for the native all-roster scenario.
use godot::classes::{MeshInstance3D, Node3D, ShaderMaterial, StandardMaterial3D, Texture2D};
use godot::prelude::*;
use serde_json::{Value, json};
pub fn materials(node: &Gd<Node3D>, definition: &Value) -> Value {
    let targets = definition["paint_materials"]
        .as_array()
        .map(|m| {
            m.iter()
                .filter_map(|m| m["name"].as_str())
                .collect::<std::collections::BTreeSet<_>>()
        })
        .unwrap_or_default();
    let mut rows = vec![];
    walk(node, "", false, &targets, &mut rows);
    let unexpected = rows
        .iter()
        .filter(|r| {
            r["override"].as_bool() == Some(true)
                && r["paint_target"].as_bool() != Some(true)
                && r["wheel"].as_bool() != Some(true)
        })
        .count();
    json!({"surfaces":rows,"unexpected_unpainted_overrides":unexpected})
}
fn walk(
    node: &Gd<Node3D>,
    path: &str,
    wheel: bool,
    targets: &std::collections::BTreeSet<&str>,
    rows: &mut Vec<Value>,
) {
    let name = node.get_name().to_string();
    let path = format!("{path}/{name}");
    let wheel = wheel || name.starts_with("wheel_") || name.starts_with("tire_");
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>() {
        if let Some(resource) = mesh.get_mesh() {
            for i in 0..resource.get_surface_count() {
                let Some(base) = resource.surface_get_material(i) else {
                    continue;
                };
                let base_name = base.get_name().to_string();
                let active = mesh.get_active_material(i).unwrap_or(base.clone());
                let mut row = json!({"node":path,"surface":i,"base_name":base_name,"paint_target":targets.contains(base_name.as_str()),"wheel":wheel,"override":mesh.get_surface_override_material(i).is_some(),"instance_id":active.instance_id().to_i64()});
                if let Ok(base) = base.try_cast::<StandardMaterial3D>() {
                    let c = base.get_albedo();
                    row["factory_state"] = json!({"rgba":[c.r,c.g,c.b,c.a],"roughness":base.get_roughness(),"metallic":base.get_metallic(),"transparency":base.get_transparency().ord()});
                }
                if let Ok(standard) = active.clone().try_cast::<StandardMaterial3D>() {
                    let color = standard.get_albedo();
                    row["runtime_standard_rgba"] = json!([color.r, color.g, color.b, color.a]);
                }
                if let Ok(shader) = active.try_cast::<ShaderMaterial>() {
                    let paint = shader
                        .get_shader_parameter("paint")
                        .try_to::<Color>()
                        .ok()
                        .map(|c| [c.r, c.g, c.b, c.a]);
                    let mask = shader
                        .get_shader_parameter("paint_mask")
                        .try_to::<Gd<Texture2D>>()
                        .ok()
                        .map(|t| t.get_path().to_string());
                    let code = shader
                        .get_shader()
                        .map(|shader| shader.get_code().to_string())
                        .unwrap_or_default();
                    row["runtime_render_state"] = json!({"alpha_scissor":code.contains("ALPHA_SCISSOR_THRESHOLD"),"cull_front":code.contains("cull_front"),"cull_disabled":code.contains("cull_disabled"),"factory_luma_linear":shader.get_shader_parameter("factory_luma").try_to::<f32>().ok(),"use_vertex_color":shader.get_shader_parameter("use_vertex_color").try_to::<bool>().ok()});
                    row["native_decal_textures"] = json!(
                        (0..16)
                            .filter_map(|index| shader
                                .get_shader_parameter(&format!("decal_{index}"))
                                .try_to::<Gd<Texture2D>>()
                                .ok()
                                .map(|texture| texture.get_path().to_string()))
                            .collect::<Vec<_>>()
                    );
                    row["native_decal_color_modes"] = json!((0..16).filter_map(|index| {
                        shader.get_shader_parameter(&format!("decal_{index}")).try_to::<Gd<Texture2D>>().ok().map(|texture| json!({"layer":index,"texture":texture.get_path().to_string(),"alpha_mask":shader.get_shader_parameter(&format!("decal_{index}_alpha_mask")).try_to::<bool>().unwrap_or(false)}))
                    }).collect::<Vec<_>>());
                    row["runtime_paint"] = json!({"rgba":paint,"has_mask":shader.get_shader_parameter("has_mask").try_to::<bool>().unwrap_or(false),"decal_repeat_uv":shader.get_shader_parameter("decal_repeat_uv").try_to::<bool>().unwrap_or(false),"mask":mask,"unpainted_finish_preserved":"roughness and metallic lerp by paint-mask coverage"});
                }
                rows.push(row);
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(spatial) = child.try_cast::<Node3D>() {
            walk(&spatial, &path, wheel, targets, rows);
        }
    }
}
pub fn trim_unchanged(before: &Value, after: &Value) -> bool {
    let a = before["surfaces"].as_array().cloned().unwrap_or_default();
    let b = after["surfaces"].as_array().cloned().unwrap_or_default();
    a.iter()
        .filter(|r| r["paint_target"] != true && r["wheel"] != true)
        .all(|r| {
            b.iter()
                .find(|s| s["base_name"] == r["base_name"] && s["surface"] == r["surface"])
                .is_some_and(|s| {
                    s["factory_state"] == r["factory_state"]
                        && !s["override"].as_bool().unwrap_or(false)
                })
        })
}

/// Read-only observer on the same post-advance clock as native input samples.
/// Recharging is defined identically to replay_record: fraction increased since
/// the preceding tick. No input or simulation state is modified.
pub fn nitrous_observations(samples: &[Value], initial: Option<f32>) -> Value {
    let mut previous = initial;
    let mut minimum = initial.unwrap_or(1.);
    let mut requested = 0usize;
    let mut active = 0usize;
    let mut recharge = 0usize;
    let mut recharged_fraction = 0_f64;
    let mut observed = 0usize;
    for sample in samples {
        let Some(fraction) = sample["nitrous"]["fraction"].as_f64().map(|v| v as f32) else {
            continue;
        };
        observed += 1;
        requested += usize::from(sample["controls"]["nitrous"].as_f64().unwrap_or(0.) > 0.);
        active += usize::from(sample["nitrous"]["active"].as_bool() == Some(true));
        minimum = minimum.min(fraction);
        if let Some(before) = previous {
            if fraction > before {
                recharge += 1;
                recharged_fraction += (fraction - before) as f64;
            }
        }
        previous = Some(fraction);
    }
    json!({"sampled_ticks":observed,"initial_fraction":initial,"requested_ticks":requested,"active_ticks":active,"minimum_fraction":minimum,"recharge_ticks":recharge,"recharged_fraction_f64_sum":recharged_fraction,"clock":"Post-Game.advance, same sample as polled controls; recharge iff fraction increased from preceding tick; f64 sum of positive f32 fraction deltas"})
}

#[cfg(test)]
mod observer_tests {
    use super::*;
    #[test]
    fn nitrous_counts_post_tick_state_including_first_delta() {
        let sample = |fraction: f32, active: bool, request: f32| json!({"nitrous":{"fraction":fraction,"active":active},"controls":{"nitrous":request}});
        let report = nitrous_observations(
            &[
                sample(0.5, true, 1.),
                sample(0.6, false, 1.),
                sample(0.7, false, 0.),
            ],
            Some(1.),
        );
        assert_eq!(report["active_ticks"], 1);
        assert_eq!(report["requested_ticks"], 2);
        assert_eq!(report["recharge_ticks"], 2);
        assert_eq!(report["minimum_fraction"], 0.5);
        assert!((report["recharged_fraction_f64_sum"].as_f64().unwrap() - 0.2).abs() < 1e-6);
        assert_eq!(
            nitrous_observations(&[sample(0.6, false, 0.)], Some(0.5))["recharge_ticks"],
            1
        );
    }
}

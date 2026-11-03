//! Native component selection and shared-rig attachment. Source HSV and skeletal
//! profile attributes are retained by the game, but are not interpreted here.
use godot::classes::{
    FileAccess, MeshInstance3D, Node, Node3D, PackedScene, ResourceLoader, Skeleton3D, Skin,
    StandardMaterial3D, Texture2D,
};
use godot::prelude::*;
use oversteer_core::PlayerProfile;
use serde_json::{Value, json};
use std::collections::BTreeSet;

const CATEGORY_ITEMS: [(&str, &str, &str); 12] = [
    ("done", "79187623", "DONE"),
    ("face", "2c652168", "EDIT FACE"),
    ("nose", "9d09cf58", "EDIT NOSE"),
    ("eyes", "a3dadd7c", "EDIT EYES"),
    ("mouth", "630e8a81", "EDIT MOUTH"),
    ("head", "34bb726c", "EDIT HEAD"),
    ("hair", "6a641eac", "EDIT HAIR"),
    ("skin", "9c42ba44", "EDIT SKIN HUE"),
    ("lips", "a5ead6ae", "EDIT LIP COLOR"),
    ("facial", "04e3ea77", "EDIT FACIAL HAIR"),
    ("brow", "660fa9af", "EDIT BROWS"),
    ("clothes", "7878a002", "EDIT CLOTHES"),
];
pub fn next_category(current: &str, direction: i32) -> String {
    let current = CATEGORY_ITEMS
        .iter()
        .position(|(id, _, _)| *id == current)
        .unwrap_or(0) as i32;
    CATEGORY_ITEMS[(current + direction).clamp(0, CATEGORY_ITEMS.len() as i32 - 1) as usize]
        .0
        .into()
}

pub fn catalog() -> Result<Value, String> {
    serde_json::from_str(
        &FileAccess::get_file_as_string("res://assets/characters/components.json").to_string(),
    )
    .map_err(|e| format!("Native character catalog: {e}"))
}

pub fn select_preset(data: &Value, profile: &mut PlayerProfile, id: &str) -> Result<(), String> {
    let preset = data["native_presets"]["presets"]
        .as_array()
        .and_then(|presets| presets.iter().find(|p| p["id"].as_str() == Some(id)))
        .ok_or_else(|| format!("Unknown native character preset {id}"))?;
    profile.gender = preset["gender"].as_str().unwrap_or("M").into();
    profile.preset = id.into();
    profile.native_components =
        serde_json::from_value(preset["native_components"].clone()).map_err(|e| e.to_string())?;
    profile.native_attributes =
        serde_json::from_value(preset["native_attributes"].clone()).map_err(|e| e.to_string())?;
    Ok(())
}

pub fn select_component(data: &Value, profile: &mut PlayerProfile, id: &str) -> Result<(), String> {
    let component = data["components"]
        .as_array()
        .and_then(|items| items.iter().find(|c| c["id"].as_str() == Some(id)))
        .ok_or_else(|| format!("Unknown native component {id}"))?;
    if !component["gender_tags"]
        .as_array()
        .is_some_and(|genders| genders.iter().any(|g| g.as_str() == Some(&profile.gender)))
    {
        return Err("This component belongs to the other character gender".into());
    }
    let category = component["category"]
        .as_str()
        .ok_or("Native component has no category")?;
    profile.native_components.insert(category.into(), id.into());
    Ok(())
}

pub fn apply_control(
    data: &Value,
    profile: &mut PlayerProfile,
    id: &str,
    input: f32,
) -> Result<(), String> {
    let action = data["creator_controls"]["actions"]
        .as_array()
        .and_then(|actions| actions.iter().find(|a| a["id"].as_str() == Some(id)))
        .ok_or_else(|| format!("Unknown native appearance control {id}"))?;
    if let Some(channels) = action["morph_channels"][&profile.gender].as_array() {
        for channel in channels {
            let start = channel["control_start"].as_f64().unwrap_or(0.) as f32;
            let finish = channel["control_finish"].as_f64().unwrap_or(1.) as f32;
            if input < start || input > finish || finish == start {
                continue;
            }
            let t = (input - start) / (finish - start);
            // 821A3120 retains the channel's partial interval in this second interpolation.
            let p = (1. - t) * start + t * finish;
            let a = channel["native_ramp_start"].as_f64().unwrap_or(0.) as f32;
            let b = channel["native_ramp_finish"].as_f64().unwrap_or(0.) as f32;
            if let Some(name) = channel["name"].as_str() {
                profile
                    .native_attributes
                    .insert(name.into(), a + p * (b - a));
            }
        }
    }
    Ok(())
}

fn descendants<T: GodotClass + Inherits<Node>>(node: &Gd<Node>) -> Vec<Gd<T>> {
    let mut result = vec![];
    if let Ok(value) = node.clone().try_cast::<T>() {
        result.push(value);
    }
    for child in node.get_children().iter_shared() {
        result.extend(descendants::<T>(&child));
    }
    result
}

fn relative_transform(node: &Gd<Node3D>, root: &Gd<Node3D>) -> Transform3D {
    let mut transform = node.get_transform();
    let mut parent = node.get_parent();
    while let Some(node) = parent {
        if node == root.clone().upcast::<Node>() {
            break;
        }
        if let Ok(spatial) = node.clone().try_cast::<Node3D>() {
            transform = spatial.get_transform() * transform;
        }
        parent = node.get_parent();
    }
    transform
}

/// Replace the prepared actor's meshes while keeping its original skeleton and
/// animation player. Every source component chunk is attached in the same root basis.
pub fn attach(
    actor: &mut Gd<Node3D>,
    data: &Value,
    profile: &PlayerProfile,
) -> Result<Value, String> {
    let mut actor_root = descendants::<Node3D>(&actor.clone().upcast())
        .into_iter()
        .find(|node| node.get_name().to_string() == "NativeAvatar")
        .ok_or("Native actor normalization root is missing")?;
    let base_skeleton = descendants::<Skeleton3D>(&actor.clone().upcast())
        .into_iter()
        .next()
        .ok_or("Native actor has no skeleton")?;
    let components = data["components"]
        .as_array()
        .ok_or("Missing native components")?;
    let skins = data["skins"].as_array().ok_or("Missing native skins")?;
    let selected: Vec<_> = profile
        .native_components
        .values()
        .map(|id| {
            components
                .iter()
                .find(|c| c["id"].as_str() == Some(id))
                .ok_or_else(|| format!("Missing selected native component {id}"))
        })
        .collect::<Result<_, _>>()?;
    let mut skin_ids = BTreeSet::new();
    for component in &selected {
        for id in component["skin_ids"]
            .as_array()
            .into_iter()
            .flatten()
            .filter_map(Value::as_str)
        {
            let skin = skins
                .iter()
                .find(|s| s["id"].as_str() == Some(id))
                .ok_or_else(|| format!("Missing native skin {id}"))?;
            if skin["gender_tag"].as_str() == Some(&profile.gender) {
                skin_ids.insert(id.to_string());
            }
        }
    }
    if skin_ids.is_empty() {
        return Err("Native preset has no drawable components".into());
    }
    for mut mesh in descendants::<MeshInstance3D>(&actor.clone().upcast()) {
        mesh.set_visible(false);
    }
    let mut reports = vec![];
    for id in skin_ids {
        let definition = skins
            .iter()
            .find(|s| s["id"].as_str() == Some(&id))
            .unwrap();
        let path = definition["model_path"]
            .as_str()
            .ok_or("Missing native component path")?;
        let scene = ResourceLoader::singleton()
            .load(path)
            .and_then(|r| r.try_cast::<PackedScene>().ok())
            .ok_or_else(|| format!("Unable to load native component {path}"))?;
        let root = scene
            .instantiate()
            .and_then(|n| n.try_cast::<Node3D>().ok())
            .ok_or_else(|| format!("Unable to instantiate native component {path}"))?;
        let result = (|| -> Result<(), String> {
            let component_root = descendants::<Node3D>(&root.clone().upcast())
                .into_iter()
                .find(|node| node.get_name().to_string() == "NativeAvatar")
                .ok_or("Native component normalization root is missing")?;
            let source_skeleton = descendants::<Skeleton3D>(&root.clone().upcast())
                .into_iter()
                .next()
                .ok_or("Component has no skeleton")?;
            for mut mesh in descendants::<MeshInstance3D>(&root.clone().upcast()) {
                let relative = relative_transform(&mesh.clone().upcast(), &component_root);
                let source_skin = mesh.get_skin().ok_or("Component mesh has no skin")?;
                let mut skin = Skin::new_gd();
                for bind in 0..source_skin.get_bind_count() {
                    let mut name = source_skin.get_bind_name(bind).to_string();
                    if name.is_empty() {
                        name = source_skeleton
                            .get_bone_name(source_skin.get_bind_bone(bind))
                            .to_string();
                    }
                    if base_skeleton.find_bone(&name) < 0 {
                        return Err(format!("Native common rig lacks bone {name}"));
                    }
                    skin.add_named_bind(&name, source_skin.get_bind_pose(bind));
                }
                mesh.set_owner(Gd::<Node>::null_arg());
                if let Some(mut parent) = mesh.get_parent() {
                    parent.remove_child(&mesh);
                }
                actor_root.add_child(&mesh);
                mesh.set_transform(relative);
                mesh.set_skin(&skin);
                let skeleton_path = mesh.get_path_to(&base_skeleton);
                mesh.set_skeleton_path(&skeleton_path);
                let enabled = selected
                    .iter()
                    .filter(|c| {
                        c["skin_ids"]
                            .as_array()
                            .is_some_and(|ids| ids.iter().any(|v| v.as_str() == Some(&id)))
                    })
                    .any(|c| c["native_initial_mesh_enabled"].as_bool().unwrap_or(true));
                mesh.set_visible(enabled);
                for attribute in definition["morph_attributes"]
                    .as_array()
                    .into_iter()
                    .flatten()
                {
                    if let Some(name) = attribute["name"].as_str() {
                        let index = attribute["target_index"].as_i64().unwrap_or(-1) as i32;
                        if index >= 0 && index < mesh.get_blend_shape_count() {
                            let level = profile.native_attributes.get(name).copied().unwrap_or(0.);
                            let scale = attribute["native_level_to_render_weight"]
                                .as_f64()
                                .unwrap_or(0.01) as f32;
                            mesh.set_blend_shape_value(index, level * scale);
                        }
                    }
                }
                let key = definition["source"]["key"].as_str().unwrap_or("");
                if let Some(resource) = mesh.get_mesh() {
                    for surface in 0..resource.get_surface_count() {
                        let Some(material) = mesh.get_active_material(surface) else {
                            continue;
                        };
                        let material_name = material.get_name().to_string();
                        let Some(slot) = definition["materials"].as_array().and_then(|slots| {
                            slots
                                .iter()
                                .find(|s| s["name"].as_str() == Some(&material_name))
                        }) else {
                            continue;
                        };
                        let replacement = selected
                            .iter()
                            .flat_map(|c| c["replacement_slots"].as_array().into_iter().flatten())
                            .filter(|r| {
                                r["skin_key"].as_str() == Some(key)
                                    && r["native_jtd"] == slot["native_jtd"]
                            })
                            .last();
                        if let Some(path) = replacement.and_then(|r| r["texture_path"].as_str()) {
                            if let Some(texture) = ResourceLoader::singleton()
                                .load(path)
                                .and_then(|r| r.try_cast::<Texture2D>().ok())
                            {
                                if let Ok(mut copy) = material
                                    .duplicate_resource()
                                    .try_cast::<StandardMaterial3D>()
                                {
                                    copy.set_texture(
                                        godot::classes::base_material_3d::TextureParam::ALBEDO,
                                        &texture,
                                    );
                                    mesh.set_surface_override_material(surface, &copy);
                                }
                            } else {
                                return Err(format!("Missing native clothing artwork {path}"));
                            }
                        }
                    }
                }
                let morphs: Vec<_> = definition["morph_attributes"].as_array().into_iter().flatten().filter_map(|attribute| {
                    let index=attribute["target_index"].as_i64()? as i32;
                    (index>=0 && index<mesh.get_blend_shape_count()).then(|| json!({"name":attribute["name"],"target_index":index,"render_weight":mesh.get_blend_shape_value(index)}))
                }).collect();
                let actual_skin = mesh
                    .get_skin()
                    .ok_or("Attached native mesh lost its Skin")?;
                reports.push(json!({"skin":id,"mesh":mesh.get_name().to_string(),"bind_count":actual_skin.get_bind_count(),"skeleton_path":mesh.get_skeleton_path().to_string(),"enabled":enabled,"morphs":morphs}));
            }
            Ok(())
        })();
        root.free();
        result?;
    }
    Ok(
        json!({"meshes":reports,"limits":"Original head geometry, clothing textures, joint bindings and source ramps; skeletal-scale/HSV attributes and unlock semantics remain unresolved"}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    fn source_catalog() -> Value {
        serde_json::from_str(
            &std::fs::read_to_string(concat!(
                env!("CARGO_MANIFEST_DIR"),
                "/../../godot/assets/characters/components.json"
            ))
            .unwrap(),
        )
        .unwrap()
    }
    #[test]
    fn native_preset_keeps_all_raw_attributes_and_exact_components() {
        let data = source_catalog();
        let mut profile = PlayerProfile::default();
        select_preset(&data, &mut profile, "MPreset2").unwrap();
        assert_eq!(profile.native_attributes.len(), 56);
        assert_eq!(
            profile.native_components["top"],
            "componentdefs-8d11c330_47"
        );
        assert_eq!(profile.native_attributes["FaceFlat"], -23.27);
        assert_eq!(profile.native_attributes["SKIN_DARK"], 100.);
    }
    #[test]
    fn source_partial_ramp_does_not_normalize_or_modify_inactive_channel() {
        let data = source_catalog();
        let mut profile = PlayerProfile::default();
        profile.gender = "M".into();
        profile.native_attributes.insert("FaceHeavy".into(), 17.);
        apply_control(&data, &mut profile, "FACEHEAVYSLIDER", 0.25).unwrap();
        assert_eq!(profile.native_attributes["FaceHeavy"], 17.);
        apply_control(&data, &mut profile, "FACEHEAVYSLIDER", 0.5).unwrap();
        assert_eq!(profile.native_attributes["FaceHeavy"], -50.);
        apply_control(&data, &mut profile, "FACEHEAVYSLIDER", 0.75).unwrap();
        assert_eq!(profile.native_attributes["FaceHeavy"], -25.);
    }
    #[test]
    fn visible_slider_actions_follow_original_menu_insertions_and_english_captions() {
        let captions: Value =
            serde_json::from_str(include_str!("avatar-ui-captions.json")).unwrap();
        let groups = captions["groups"].as_array().unwrap();
        assert_eq!(
            groups
                .iter()
                .map(|group| group["controls"].as_array().unwrap().len())
                .sum::<usize>(),
            34
        );
        let nose = groups.iter().find(|group| group["id"] == "nose").unwrap();
        assert_eq!(nose["controls"][0]["id"], "NOSEBIGSLIDER");
        assert_eq!(nose["controls"][0]["caption"], "Size");
        assert!(
            !nose["controls"]
                .as_array()
                .unwrap()
                .iter()
                .any(|control| control["id"] == "NOSEFLATSLIDER")
        );
        let layout = super::super::native_layout::NativeLayout::parse(include_str!(
            "layouts/avatar-nose.json"
        ))
        .unwrap();
        let slot = layout.slot("NOSEBIGSLIDER").unwrap();
        assert!((slot.rect[0] - 0.0932).abs() < 0.000001);
        assert!((slot.rect[1] - 0.38978).abs() < 0.000001);
    }
}

impl super::OversteerApp {
    fn native_avatar_sliders(
        &mut self,
        menu: &mut Gd<godot::classes::Control>,
        snap: &oversteer_core::GameSnapshot,
        data: &Value,
        group: &Value,
    ) {
        use super::native_layout::NativeLayout;
        use godot::classes::{HSlider, StyleBoxTexture};
        let rows = match group["id"].as_str() {
            Some("face") => include_str!("layouts/avatar-face.json"),
            Some("nose") => include_str!("layouts/avatar-nose.json"),
            Some("eyes") => include_str!("layouts/avatar-eyes.json"),
            Some("mouth") => include_str!("layouts/avatar-mouth.json"),
            _ => include_str!("layouts/avatar-head.json"),
        };
        let layout = NativeLayout::parse(rows).expect("verified native avatar slider rows");
        if let Err(error) = layout.render(
            menu,
            &[("TITLE", group["title"].as_str().unwrap_or("").into())],
        ) {
            self.notice = error;
        }
        let controls = group["controls"].as_array().unwrap();
        let source_rows: Value = serde_json::from_str(rows).unwrap();
        let menu_name = source_rows["fields"]
            .as_array()
            .unwrap()
            .iter()
            .find(|row| {
                row[0].as_str() == Some("BeginMenu")
                    && row[1].as_str().is_some_and(|n| n != "BG_HIGHLIGHTER")
            })
            .and_then(|row| row[1].as_str())
            .unwrap();
        let menu_slot = layout.slot(menu_name).unwrap();
        let first = layout.slot(controls[0]["id"].as_str().unwrap()).unwrap();
        let label_offset_y = first.rect[1] - menu_slot.rect[1];
        let (font, font_size) = menu_slot.font_resource().unwrap();
        for control in controls {
            let id = control["id"].as_str().unwrap();
            let Some(action) = data["creator_controls"]["actions"]
                .as_array()
                .unwrap()
                .iter()
                .find(|a| a["id"].as_str() == Some(id))
            else {
                continue;
            };
            let slot = layout.slot(id).unwrap();
            let (position, size) = slot.pixels();
            let mut label = Self::text(
                menu,
                control["caption"].as_str().unwrap_or(""),
                menu_slot.rect[0] * 1920.,
                (slot.rect[1] - label_offset_y) * 1080.,
                font_size,
                Color::WHITE,
            );
            label.add_theme_font_override("font", &font);
            let mut slider = HSlider::new_alloc();
            slider.set_min(0.);
            slider.set_max(1.);
            slider.set_step(0.001);
            slider.set_position(position);
            slider.set_size(size);
            slider.set_value(control_position(action, &snap.profile) as f64);
            let mut track = StyleBoxTexture::new_gd();
            track.set_texture(&godot::tools::load::<Texture2D>(
                "res://assets/ui/native/ui_frontend/893e7974.png",
            ));
            slider.add_theme_stylebox_override("slider", &track);
            slider.add_theme_icon_override(
                "grabber",
                &godot::tools::load::<Texture2D>("res://assets/ui/native/ui_frontend/51a60f34.png"),
            );
            slider.add_theme_icon_override(
                "grabber_highlight",
                &godot::tools::load::<Texture2D>("res://assets/ui/native/ui_frontend/ee276db6.png"),
            );
            slider.set_meta("ui_action", &format!("avatar_control:{id}").to_variant());
            slider.set_meta("native_layout_slot", &id.to_variant());
            slider.set_meta(
                "native_caption",
                &control["caption"].as_str().unwrap_or("").to_variant(),
            );
            slider.connect(
                "value_changed",
                &self
                    .base()
                    .callable("avatar_control_changed")
                    .bindv(&varray![id]),
            );
            menu.add_child(&slider);
        }
    }
    pub(super) fn native_avatar_menu(
        &mut self,
        menu: &mut Gd<godot::classes::Control>,
        snap: &oversteer_core::GameSnapshot,
    ) {
        use godot::classes::LineEdit;
        let data = match catalog() {
            Ok(data) => data,
            Err(error) => {
                self.notice = error;
                return;
            }
        };
        let gender_view = self.avatar_category == "gender" || self.avatar_category == "preset";
        let layout = super::native_layout::NativeLayout::parse(if gender_view {
            include_str!("layouts/avatar-gender.json")
        } else {
            include_str!("layouts/avatar-categories.json")
        });
        let title = if self.avatar_category == "gender" {
            "SELECT GENDER"
        } else if self.avatar_category == "preset" && snap.profile.gender == "F" {
            "SELECT FEMALE CHARACTER"
        } else if self.avatar_category == "preset" {
            "SELECT MALE CHARACTER"
        } else {
            "EDIT CHARACTER"
        };
        if let Err(error) =
            layout.and_then(|layout| layout.render(menu, &[("MENUTITLE", title.into())]))
        {
            self.notice = error;
        }
        let mut name = LineEdit::new_alloc();
        name.set_text(&snap.profile.name);
        name.set_position(Vector2::new(1420., 125.));
        name.set_size(Vector2::new(350., 50.));
        name.add_theme_font_size_override("font_size", 24);
        name.connect("text_submitted", &self.base().callable("avatar_name"));
        menu.add_child(&name);
        if gender_view {
            for (i, (label, key, hash)) in [("MALE", "M", "5abf5d6a"), ("FEMALE", "F", "70785b6a")]
                .iter()
                .enumerate()
            {
                icon(
                    menu,
                    hash,
                    Vector2::new(730. + i as f32 * 230., 775.),
                    Vector2::new(140., 140.),
                );
                self.button(
                    menu,
                    label,
                    &format!("avatar:gender:{key}"),
                    710. + i as f32 * 230.,
                    925.,
                    190.,
                    50.,
                );
            }
            if self.avatar_category == "preset" {
                let presets: Vec<_> = data["native_presets"]["presets"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter(|p| p["gender"].as_str() == Some(&snap.profile.gender))
                    .collect();
                for (i, preset) in presets.iter().enumerate() {
                    let id = preset["id"].as_str().unwrap_or("");
                    self.button(
                        menu,
                        &format!(
                            "{}{} / {}",
                            if snap.profile.preset == id { "> " } else { "" },
                            i + 1,
                            presets.len()
                        ),
                        &format!("avatar:native:{id}"),
                        1350.,
                        280. + i as f32 * 65.,
                        420.,
                        55.,
                    );
                }
                self.button(
                    menu,
                    "CUSTOMIZE",
                    "avatar:page:face",
                    1360.,
                    690.,
                    400.,
                    60.,
                );
            }
        } else {
            let caption_data: Value = serde_json::from_str(include_str!("avatar-ui-captions.json"))
                .expect("verified native captions");
            if let Some(group) = caption_data["groups"].as_array().and_then(|groups| {
                groups.iter().find(|group| {
                    self.avatar_editing && group["id"].as_str() == Some(&self.avatar_category)
                })
            }) {
                self.native_avatar_sliders(menu, snap, &data, group);
                self.button(menu, "BACK", "avatar:back", 130., 990., 280., 60.);
                self.button(menu, "DONE", "nav:main", 1510., 990., 260., 60.);
                Self::text(menu, &self.notice, 650., 1015., 23, Color::WHITE);
                if let Some(mut slider) = menu
                    .get_children()
                    .iter_shared()
                    .find_map(|child| child.try_cast::<godot::classes::HSlider>().ok())
                {
                    slider.grab_focus();
                }
                return;
            }
            let selected = CATEGORY_ITEMS
                .iter()
                .position(|(id, _, _)| *id == self.avatar_category)
                .unwrap_or(0);
            for offset in -2_i32..=2 {
                let index = selected as i32 + offset;
                if index < 0 || index >= CATEGORY_ITEMS.len() as i32 {
                    continue;
                }
                let (category, hash, _) = CATEGORY_ITEMS[index as usize];
                let size = match offset.abs() {
                    0 => 240.,
                    1 => 128.,
                    _ => 96.,
                };
                let position = Vector2::new(
                    960. + offset as f32 * 195. - size * 0.5,
                    876.15 - size * 0.5,
                );
                icon(menu, hash, position, Vector2::ONE * size);
                let action = if category == "done" {
                    "nav:main".into()
                } else {
                    format!("avatar:page:{category}")
                };
                self.button(menu, "", &action, position.x, position.y, size, size);
            }
            let mut help = Self::text(
                menu,
                CATEGORY_ITEMS[selected].2,
                180.48,
                735.48,
                57,
                Color::WHITE,
            );
            help.add_theme_font_override(
                "font",
                &godot::tools::load::<godot::classes::Font>(
                    "res://assets/ui/native/fonts/HIN_Text-1080.fnt",
                ),
            );
            help.set_size(Vector2::new(1566.72, 54.));
            help.set_horizontal_alignment(godot::global::HorizontalAlignment::CENTER);
            self.button(menu, "PRESETS", "avatar:page:preset", 130., 950., 280., 60.);
            if !self.avatar_editing {
                self.button(
                    menu,
                    "PREVIOUS",
                    "avatar:cursor:prev",
                    1320.,
                    690.,
                    215.,
                    55.,
                );
                self.button(menu, "NEXT", "avatar:cursor:next", 1550., 690., 215., 55.);
                let category = CATEGORY_ITEMS[selected].0;
                let action = if category == "done" {
                    "nav:main".into()
                } else {
                    format!("avatar:edit:{category}")
                };
                self.button(menu, "SELECT", &action, 1120., 990., 260., 60.);
                self.button(menu, "DONE", "nav:main", 1510., 990., 260., 60.);
                return;
            }
            self.button(
                menu,
                "PREVIOUS",
                "avatar:cursor:prev",
                1320.,
                690.,
                215.,
                55.,
            );
            self.button(menu, "NEXT", "avatar:cursor:next", 1550., 690., 215., 55.);
            {
                let category = match self.avatar_category.as_str() {
                    "clothes" => "top",
                    "facial" => "facialhair",
                    "brow" => "eyebrows",
                    other => other,
                };
                let choices: Vec<_> = data["components"]
                    .as_array()
                    .into_iter()
                    .flatten()
                    .filter(|c| {
                        c["category"].as_str() == Some(category)
                            && c["gender_tags"].as_array().is_some_and(|g| {
                                g.iter().any(|x| x.as_str() == Some(&snap.profile.gender))
                            })
                            && c["availability_status"]
                                .as_str()
                                .is_some_and(|s| s.starts_with("gender/subname"))
                    })
                    .collect();
                let pages = choices.len().div_ceil(7).max(1);
                self.avatar_cursor = self.avatar_cursor.min(pages - 1);
                for (row, component) in choices
                    .iter()
                    .skip(self.avatar_cursor * 7)
                    .take(7)
                    .enumerate()
                {
                    self.button(
                        menu,
                        &format!("STYLE {}", self.avatar_cursor * 7 + row + 1),
                        &format!(
                            "avatar:component:{}",
                            component["id"].as_str().unwrap_or("")
                        ),
                        1270.,
                        230. + row as f32 * 62.,
                        500.,
                        53.,
                    );
                }
                if self.avatar_category == "clothes" {
                    for (i, category) in ["top", "bottom", "hat"].iter().enumerate() {
                        self.button(
                            menu,
                            &category.to_uppercase(),
                            &format!("avatar:page:{category}"),
                            80.,
                            300. + i as f32 * 70.,
                            250.,
                            55.,
                        );
                    }
                }
            }
        }
        self.button(menu, "BACK", "avatar:back", 1050., 960., 260., 60.);
        self.button(menu, "DONE", "nav:main", 1510., 960., 260., 60.);
        Self::text(menu, &self.notice, 150., 1015., 23, Color::WHITE);
        // Precise native control layouts are reused; dynamic callbacks and menu travel
        // are host adapters. Component unlock/HSV execution is not inferred here.
    }
}

fn icon(parent: &mut Gd<godot::classes::Control>, hash: &str, position: Vector2, size: Vector2) {
    let Some(texture) = ResourceLoader::singleton()
        .load(&format!("res://assets/ui/native/ui_frontend/{hash}.png"))
        .and_then(|r| r.try_cast::<Texture2D>().ok())
    else {
        return;
    };
    let mut node = godot::classes::TextureRect::new_alloc();
    node.set_expand_mode(godot::classes::texture_rect::ExpandMode::IGNORE_SIZE);
    node.set_stretch_mode(godot::classes::texture_rect::StretchMode::KEEP_ASPECT_CENTERED);
    node.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
    node.set_texture(&texture);
    parent.add_child(&node);
    node.set_position(position);
    node.set_size(size);
}

fn control_position(action: &Value, profile: &PlayerProfile) -> f32 {
    let Some(channels) = action["morph_channels"][&profile.gender].as_array() else {
        return 0.;
    };
    for c in channels {
        let Some(level) = c["name"]
            .as_str()
            .and_then(|n| profile.native_attributes.get(n))
            .copied()
        else {
            continue;
        };
        let a = c["native_ramp_start"].as_f64().unwrap_or(0.) as f32;
        let b = c["native_ramp_finish"].as_f64().unwrap_or(0.) as f32;
        let start = c["control_start"].as_f64().unwrap_or(0.) as f32;
        let finish = c["control_finish"].as_f64().unwrap_or(1.) as f32;
        if b != a {
            let p = (level - a) / (b - a);
            if p >= start && p <= finish {
                return p;
            }
        }
    }
    0.
}

pub fn camera_pose(actor: &Gd<Node3D>, category: &str) -> Option<(Vector3, Vector3, f32, f32)> {
    // These are the category Main cameras, not unbound per-slider aliases.
    let name = match category {
        "categories" => "AvatarCamMenu",
        "face" => "AvatarCamFaceMain",
        "nose" => "AvatarCamNoseMain",
        "eyes" => "AvatarCamEyeMain",
        "mouth" | "lips" => "AvatarCamMouthMain",
        "head" => "AvatarCamShapeMain",
        "hair" => "AvatarCamHairMain",
        "skin" => "AvatarCamSkin",
        "brow" => "AvatarCamBrow",
        "hat" => "AvatarCamHatMain",
        "clothes" => "AvatarCamCLothMenu",
        "top" => "AvatarCamTopMenu",
        "bottom" => "AvatarCamBottomsMenu",
        // SelectDriver vs AvatarSelectDriver is not yet a proven alias.
        _ => return None,
    };
    let rows: Vec<Vec<Value>> = serde_json::from_str(include_str!("avatar-cameras.json")).ok()?;
    let begin = rows
        .iter()
        .position(|row| row[0].as_str() == Some("[Cam]") && row[1].as_str() == Some(name))?;
    let block: Vec<_> = rows
        .iter()
        .skip(begin + 1)
        .take_while(|row| row[0].as_str() != Some("[EndCam]"))
        .collect();
    let anchor_offset = |key: &str| -> Option<Vector3> {
        let row = block.iter().find(|r| r[0].as_str() == Some(key))?;
        let anchor = super::source_bone_anchor(&actor.clone().upcast(), row[3].as_str()?)?;
        Some(
            anchor
                + Vector3::new(
                    -(row[5].as_f64()? as f32),
                    row[6].as_f64()? as f32,
                    row[7].as_f64()? as f32,
                ),
        )
    };
    let fov = block.iter().find(|r| r[0].as_str() == Some("CamFOV"))?[2].as_f64()? as f32;
    let roll = -(block.iter().find(|r| r[0].as_str() == Some("CamRoll"))?[2].as_f64()? as f32);
    Some((
        anchor_offset("CamPosEnd")?,
        anchor_offset("TargetPosEnd")?,
        fov,
        roll,
    ))
}

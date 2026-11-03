//! Recovered static UI geometry for the cart and credits, not a native UI VM.
//! Transitions, gadget zoom and original GPU material equations remain untranslated.
use godot::classes::{Control, Font, FontFile, Label, Polygon2D, ResourceLoader, Texture2D};
use godot::prelude::*;
use serde_json::Value;
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq)]
enum Kind {
    Box,
    Text,
    Menu,
    Slider,
}
#[derive(Clone, Debug)]
pub struct Slot {
    kind: Kind,
    pub name: String,
    pub rect: [f32; 4],
    color: [f32; 4],
    vertices: Option<[[f32; 4]; 4]>,
    texture: Option<String>,
    uv: [f32; 4],
    pub font: String,
    align: String,
    shadow: bool,
    additive: bool,
    pub item_height: f32,
    pub item_spacing: f32,
    pub max_scale: f32,
    pub unselected_offset_y: f32,
}
pub struct NativeLayout {
    slots: Vec<Slot>,
}
pub struct RenderedLayout {
    pub texts: BTreeMap<String, Gd<Label>>,
}
impl NativeLayout {
    pub fn cart() -> Self {
        Self::parse(include_str!("layouts/cart.json")).expect("verified native cart rows")
    }
    pub fn credits() -> Self {
        Self::parse(include_str!("layouts/credits.json")).expect("verified native credit rows")
    }
    pub fn parse(json: &str) -> Result<Self, String> {
        let value: Value = serde_json::from_str(json).map_err(|e| e.to_string())?;
        let rows = value["fields"]
            .as_array()
            .ok_or("Missing native UI fields")?;
        let mut slots = vec![];
        let mut current: Option<Slot> = None;
        for row in rows {
            let op = row[0].as_str().unwrap_or("");
            if let Some(kind) = match op {
                "BeginBox" => Some(Kind::Box),
                "BeginText" => Some(Kind::Text),
                "BeginMenu" => Some(Kind::Menu),
                "BeginSlider" => Some(Kind::Slider),
                _ => None,
            } {
                if current.is_some() {
                    return Err("Nested source UI element".into());
                }
                let mut rect = [0.; 4];
                for (i, v) in rect.iter_mut().enumerate() {
                    *v = row[i + 2].as_f64().ok_or("Invalid native UI rect")? as f32;
                }
                current = Some(Slot {
                    kind,
                    name: row[1].as_str().ok_or("Missing native UI name")?.into(),
                    rect,
                    color: [1.; 4],
                    vertices: None,
                    texture: None,
                    uv: [0., 1., 0., 1.],
                    font: "HIN_Text".into(),
                    align: "Left".into(),
                    shadow: false,
                    additive: false,
                    item_height: 0.05,
                    item_spacing: 0.,
                    max_scale: 1.,
                    unselected_offset_y: 0.,
                });
                continue;
            }
            let Some(slot) = &mut current else { continue };
            match op {
                "Colour" if slot.kind == Kind::Box => slot.color = argb(row, 1),
                "VertexColour" => {
                    let index = match row[1].as_str() {
                        Some("TOPLEFT") => 0,
                        Some("TOPRIGHT") => 1,
                        Some("BOTRIGHT") => 2,
                        Some("BOTLEFT") => 3,
                        _ => return Err("Unknown source UI vertex".into()),
                    };
                    slot.vertices.get_or_insert([[1.; 4]; 4])[index] = argb(row, 2);
                }
                "Texture" => slot.texture = row[1].as_str().map(str::to_owned),
                "UVs" => {
                    for (i, v) in slot.uv.iter_mut().enumerate() {
                        *v = row[i + 1].as_f64().ok_or("Invalid native UV")? as f32;
                    }
                }
                "Font" => {
                    slot.font = row[1].as_str().ok_or("Missing source font")?.into();
                    slot.color = argb(row, 2);
                }
                "Align" => slot.align = row[1].as_str().unwrap_or("Left").into(),
                "Shadowed" => slot.shadow = true,
                "Additive" => slot.additive = true,
                "ItemHeight" => {
                    slot.item_height = row[1].as_f64().ok_or("Invalid source item height")? as f32
                }
                "ItemSpacing" => {
                    slot.item_spacing = row[1].as_f64().ok_or("Invalid source item spacing")? as f32
                }
                "MaxScale" => {
                    slot.max_scale = row[1].as_f64().ok_or("Invalid source menu scale")? as f32
                }
                "UnselectedOffsetY" => {
                    slot.unselected_offset_y =
                        row[1].as_f64().ok_or("Invalid source menu offset")? as f32
                }
                "EndBox" | "EndText" | "EndMenu" | "EndSlider" => {
                    slots.push(current.take().unwrap())
                }
                _ => {}
            }
        }
        if current.is_some() {
            return Err("Unclosed source UI element".into());
        }
        Ok(Self { slots })
    }
    pub fn slot(&self, name: &str) -> Option<&Slot> {
        self.slots.iter().find(|slot| slot.name == name)
    }
    pub fn render(
        &self,
        parent: &mut Gd<Control>,
        texts: &[(&str, String)],
    ) -> Result<RenderedLayout, String> {
        for slot in self.slots.iter().filter(|slot| slot.kind == Kind::Box) {
            slot.draw_box(parent)?;
        }
        let mut result = RenderedLayout {
            texts: BTreeMap::new(),
        };
        for (name, text) in texts {
            let slot = self
                .slot(name)
                .ok_or_else(|| format!("Missing native text slot {name}"))?;
            if slot.kind != Kind::Text {
                return Err(format!("Native slot {name} is not text"));
            }
            let mut clip = Control::new_alloc();
            let (position, size) = slot.pixels();
            clip.set_position(position);
            clip.set_size(size);
            clip.set_clip_contents(true);
            clip.set_meta("native_layout_slot", &slot.name.to_variant());
            clip.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
            parent.add_child(&clip);
            let mut label = Label::new_alloc();
            label.set_text(text);
            label.set_size(Vector2::new(size.x, 0.));
            label.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
            let (font, height) = slot.font_resource()?;
            label.add_theme_font_override("font", &font);
            label.add_theme_font_size_override("font_size", height);
            label.add_theme_color_override("font_color", color(slot.color));
            label.set_horizontal_alignment(match slot.align.as_str() {
                "Centre" => godot::global::HorizontalAlignment::CENTER,
                "Right" => godot::global::HorizontalAlignment::RIGHT,
                _ => godot::global::HorizontalAlignment::LEFT,
            });
            if slot.shadow {
                label.add_theme_color_override("font_shadow_color", Color::BLACK);
                label.add_theme_constant_override("shadow_offset_x", 2);
                label.add_theme_constant_override("shadow_offset_y", 2);
            }
            label.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
            clip.add_child(&label);
            result.texts.insert((*name).into(), label);
        }
        Ok(result)
    }
}
impl Slot {
    pub fn pixels(&self) -> (Vector2, Vector2) {
        (
            Vector2::new(self.rect[0] * 1920., self.rect[1] * 1080.),
            Vector2::new(self.rect[2] * 1920., self.rect[3] * 1080.),
        )
    }
    pub fn font_resource(&self) -> Result<(Gd<Font>, i32), String> {
        let path = format!("res://assets/ui/native/fonts/{}-1080.fnt", self.font);
        if !ResourceLoader::singleton().exists(&path) {
            return Err(format!("Missing native font {path}"));
        }
        let font = godot::tools::load::<FontFile>(&path);
        let height = font.get_fixed_size().max(1);
        Ok((font.upcast(), height))
    }
    fn draw_box(&self, parent: &mut Gd<Control>) -> Result<(), String> {
        let (position, size) = self.pixels();
        let mut polygon = Polygon2D::new_alloc();
        polygon.set_polygon(&PackedVector2Array::from(
            &[
                Vector2::ZERO,
                Vector2::new(size.x, 0.),
                size,
                Vector2::new(0., size.y),
            ][..],
        ));
        polygon.set_position(position);
        if let Some(vertices) = self.vertices {
            polygon.set_vertex_colors(&PackedColorArray::from(&vertices.map(color)[..]));
        } else {
            polygon.set_color(color(self.color));
        }
        if let Some(name) = &self.texture {
            let path = format!("res://assets/ui/native/named/{name}.png");
            if !ResourceLoader::singleton().exists(&path) {
                return Err(format!("Missing native texture {path}"));
            }
            let texture = godot::tools::load::<Texture2D>(&path);
            let w = texture.get_width() as f32;
            let h = texture.get_height() as f32;
            let [u0, u1, v0, v1] = self.uv;
            polygon.set_uv(&PackedVector2Array::from(
                &[
                    Vector2::new(u0 * w, v0 * h),
                    Vector2::new(u1 * w, v0 * h),
                    Vector2::new(u1 * w, v1 * h),
                    Vector2::new(u0 * w, v1 * h),
                ][..],
            ));
            polygon.set_texture(&texture);
            polygon.set_texture_repeat(godot::classes::canvas_item::TextureRepeat::ENABLED);
            polygon.set_meta("native_asset", &name.to_variant());
        }
        if self.additive {
            let mut shader = godot::classes::Shader::new_gd();
            shader.set_code("shader_type canvas_item;render_mode blend_add;void fragment(){COLOR*=texture(TEXTURE,UV);}");
            let mut material = godot::classes::ShaderMaterial::new_gd();
            material.set_shader(&shader);
            polygon.set_material(&material);
        }
        polygon.set_meta("native_layout_slot", &self.name.to_variant());
        parent.add_child(&polygon);
        Ok(())
    }
}
fn color(rgba: [f32; 4]) -> Color {
    Color::from_rgba(rgba[0], rgba[1], rgba[2], rgba[3])
}
fn argb(row: &Value, index: usize) -> [f32; 4] {
    let v = |i| row[i].as_f64().unwrap_or(255.) as f32 / 255.;
    [v(index + 1), v(index + 2), v(index + 3), v(index)]
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn native_argb_keeps_alpha_and_black_outline_channels_distinct() {
        assert_eq!(
            argb(&serde_json::json!(["FontOutline", 255, 0, 0, 0]), 1),
            [0., 0., 0., 1.]
        );
    }
    #[test]
    fn native_cart_columns_and_price_baseline_are_preserved() {
        let layout = NativeLayout::cart();
        assert_eq!(
            layout.slots.iter().filter(|s| s.kind == Kind::Box).count(),
            36
        );
        assert_eq!(
            layout.slot("BG_03").unwrap().color,
            [202. / 255., 198. / 255., 1., 100. / 255.]
        );
        let parts = layout.slot("MENU_PART").unwrap();
        let prices = layout.slot("MENU_PRICE").unwrap();
        assert!((parts.rect[0] - 0.11266).abs() < 0.00001);
        assert!((prices.rect[0] - 0.49827).abs() < 0.00001);
        assert!((parts.item_height - 0.05).abs() < 0.00001);
        assert!((parts.item_spacing - 0.016).abs() < 0.00001);
        assert!((layout.slot("TOTAL").unwrap().rect[1] - 0.81611).abs() < 0.00001);
    }
    #[test]
    fn native_credits_text_uses_original_font_and_clip_rectangle() {
        let layout = NativeLayout::credits();
        let text = layout.slot("TEXT").unwrap();
        assert_eq!(text.font, "HIN_Text");
        assert_eq!(text.align, "Centre");
        assert!((text.rect[0] - 0.15625).abs() < 0.00001);
        assert!((text.rect[3] - 0.68333).abs() < 0.00001);
    }
    #[test]
    fn native_goal_menu_retains_selected_scale_and_unselected_vertical_offset() {
        let layout = NativeLayout::parse(include_str!("layouts/goals.json")).unwrap();
        let menu = layout.slot("MENU").unwrap();
        assert!((menu.item_height * menu.max_scale - 0.195).abs() < 0.000001);
        assert!((menu.unselected_offset_y - 0.1).abs() < 0.000001);
        assert!((layout.slot("MENU_GOALTITLE").unwrap().rect[1] - 0.20615).abs() < 0.000001);
    }
}

//! Original 24×11 colour chart in Oversteer chrome, with precision editing.
//! Layout/ARGB cells: 82344C80/82345160 and ui-17099544's COLOUR gadget.

use godot::classes::{
    Button, ColorPicker, Control, FileAccess, IControl, InputEvent, Label, StyleBoxFlat,
};
use godot::prelude::*;

const COLUMNS: usize = 24;
const ROWS: usize = 11;
const DISPLAY_COLUMNS: usize = 6;
const CELL_HEIGHT: f32 = 44.;
const CHART_POSITION: Vector2 = Vector2::new(72., 352.);
const CHART_SIZE: Vector2 = Vector2::new(392., 176.);

#[derive(GodotClass)]
#[class(base=Control)]
pub struct NativePalette {
    color: Color,
    cells: Vec<Color>,
    selected: usize,
    title: String,
    price: u32,
    edit_alpha: bool,
    buttons: Vec<Gd<Button>>,
    swatches: Option<Gd<godot::classes::ScrollContainer>>,
    precision: Option<Gd<ColorPicker>>,
    precision_expanded: bool,
    price_label: Option<Gd<Label>>,
    base: Base<Control>,
}

#[godot_api]
impl IControl for NativePalette {
    fn init(base: Base<Control>) -> Self {
        Self {
            color: Color::WHITE,
            cells: vec![],
            selected: 0,
            title: String::new(),
            price: 0,
            edit_alpha: false,
            buttons: vec![],
            swatches: None,
            precision: None,
            precision_expanded: false,
            price_label: None,
            base,
        }
    }

    fn ready(&mut self) {
        self.base_mut().set_size(Vector2::new(1920., 1080.));
        self.base_mut().set_z_index(90);
        self.base_mut()
            .set_focus_mode(godot::classes::control::FocusMode::ALL);
        self.base_mut()
            .set_mouse_filter(godot::classes::control::MouseFilter::STOP);
        self.base_mut().set_theme(&super::menu_theme());
        let mut parent = self.base().clone();
        self.price_label = Some(super::OversteerApp::paint_stage_chrome(
            &mut parent,
            &self.title,
            self.price,
        ));
        if let Some(label) = &mut self.price_label {
            label.set_position(Vector2::new(72., 308.));
            label.add_theme_font_size_override("font_size", 18);
        }
        let mut scroll = godot::classes::ScrollContainer::new_alloc();
        scroll.set_position(CHART_POSITION);
        scroll.set_size(CHART_SIZE);
        scroll.set_horizontal_scroll_mode(godot::classes::scroll_container::ScrollMode::DISABLED);
        scroll.set_vertical_scroll_mode(godot::classes::scroll_container::ScrollMode::AUTO);
        scroll.set_mouse_filter(godot::classes::control::MouseFilter::PASS);
        let mut grid = Control::new_alloc();
        grid.set_custom_minimum_size(Vector2::new(
            CHART_SIZE.x - 16.,
            (COLUMNS * ROWS).div_ceil(DISPLAY_COLUMNS) as f32 * CELL_HEIGHT,
        ));
        scroll.add_child(&grid);
        self.base_mut().add_child(&scroll);
        self.swatches = Some(scroll);
        for index in 0..COLUMNS * ROWS {
            let mut button = Button::new_alloc();
            button.set_name(&format!("Colour_{}_{}", index / ROWS, index % ROWS));
            let width = (CHART_SIZE.x - 16.) / DISPLAY_COLUMNS as f32;
            button.set_position(Vector2::new(
                (index % DISPLAY_COLUMNS) as f32 * width,
                (index / DISPLAY_COLUMNS) as f32 * CELL_HEIGHT,
            ));
            button.set_size(Vector2::new(width - 4., CELL_HEIGHT - 4.));
            button.set_focus_mode(godot::classes::control::FocusMode::NONE);
            button.set_accessibility_name(&format!("Colour #{}", self.cells[index].to_html()));
            button.set_meta("ui_action", &format!("palette_cell:{index}").to_variant());
            button.connect(
                "pressed",
                &self
                    .base()
                    .callable("pick_cell")
                    .bind(&[(index as i64).to_variant()]),
            );
            grid.add_child(&button);
            self.buttons.push(button);
        }
        let mut value = super::OversteerApp::text(&mut parent, "", 72., 576., 18, Color::WHITE);
        value.set_name("ColourValue");
        let mut chip = godot::classes::ColorRect::new_alloc();
        chip.set_name("ColourChip");
        chip.set_position(Vector2::new(72., 540.));
        chip.set_size(Vector2::new(392., 24.));
        chip.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        self.base_mut().add_child(&chip);
        let mut intensity = super::OversteerApp::text(
            &mut parent,
            "I = intensity (HDR)",
            72.,
            946.,
            14,
            Color::WHITE,
        );
        intensity.set_name("IntensityHelp");
        intensity.set_visible(true);
        self.update_selection();
        let mut precision_heading = super::OversteerApp::text(
            &mut parent,
            "PRECISE COLOUR · RGB",
            72.,
            636.,
            16,
            super::ui_accent(),
        );
        precision_heading.set_name("PrecisionHeading");
        self.button(
            "Colour field…",
            Vector2::new(280., 942.),
            Vector2::new(184., 28.),
            "show_precision",
        );
        self.button(
            "SELECT",
            Vector2::new(272., 1000.),
            Vector2::new(200., 48.),
            "accept_color",
        );
        self.button(
            "BACK",
            Vector2::new(48., 1000.),
            Vector2::new(200., 48.),
            "cancel_color",
        );
        super::OversteerApp::chrome(
            &mut parent,
            Vector2::new(536., 992.),
            Vector2::new(1336., 68.),
        );
        super::OversteerApp::text(
            &mut parent,
            "Arrows: swatch · Enter: select · Esc: back",
            560.,
            1012.,
            20,
            Color::from_rgb(0.67, 0.74, 0.77),
        );

        let mut precision = ColorPicker::new_alloc();
        precision.set_theme(&super::menu_theme());
        precision.add_theme_constant_override("sv_height", 128);
        precision.set_position(Vector2::new(72., 668.));
        precision.set_size(Vector2::new(392., 260.));
        precision.set_picker_shape(godot::classes::color_picker::PickerShapeType::NONE);
        precision.add_theme_font_size_override("font_size", 18);
        precision.set_edit_alpha(self.edit_alpha);
        precision.set_pick_color(self.color);
        precision.set_presets_visible(false);
        precision.set_modes_visible(false);
        precision.set_sampler_visible(false);
        precision.set_visible(true);
        precision.set_meta("presentation", &"Precision color editing is a reconstruction adaptation; the default chart uses original cells.".to_variant());
        precision.connect("color_changed", &self.base().callable("preview_color"));
        self.base_mut().add_child(&precision);
        self.precision = Some(precision);
        self.base_mut().call_deferred("reveal_selection", &[]);
        self.base_mut().grab_focus();
    }

    fn gui_input(&mut self, event: Gd<InputEvent>) {
        let next = if event.is_action_pressed("ui_left") {
            Some(self.selected.saturating_sub(1))
        } else if event.is_action_pressed("ui_right") {
            Some((self.selected + 1).min(self.cells.len() - 1))
        } else if event.is_action_pressed("ui_up") {
            Some(self.selected.saturating_sub(DISPLAY_COLUMNS))
        } else if event.is_action_pressed("ui_down") {
            Some((self.selected + DISPLAY_COLUMNS).min(self.cells.len() - 1))
        } else {
            None
        };
        if let Some(index) = next {
            self.pick_cell(index as i64);
            self.base_mut().accept_event();
        } else if event.is_action_pressed("ui_accept") {
            self.accept_color();
            self.base_mut().accept_event();
        } else if event.is_action_pressed("ui_cancel") {
            self.cancel_color();
            self.base_mut().accept_event();
        }
    }
}

#[godot_api]
impl NativePalette {
    #[func]
    fn reveal_selection(&mut self) {
        if let Some(scroll) = &mut self.swatches {
            scroll.ensure_control_visible(&self.buttons[self.selected].clone().upcast::<Control>());
        }
    }

    #[func]
    pub fn set_price(&mut self, price: u32) {
        self.price = price;
        if let Some(label) = &mut self.price_label {
            label.set_text(&format!(
                "Selection total: {}",
                super::money(i64::from(price))
            ));
        }
    }

    #[signal]
    fn color_changed(color: Color);
    #[signal]
    fn accepted(color: Color);
    #[signal]
    fn cancelled();

    #[func]
    fn pick_cell(&mut self, index: i64) {
        let Some(color) = self.cells.get(index as usize).copied() else {
            return;
        };
        self.preview_color(color);
    }

    /// The precision ColorPicker and the grid both use this preview signal path.
    #[func]
    pub fn preview_color(&mut self, color: Color) {
        self.color = color;
        self.selected = nearest(&self.cells, color);
        if let Some(picker) = &mut self.precision
            && picker.get_pick_color() != color
        {
            picker.set_block_signals(true);
            picker.set_pick_color(color);
            picker.set_block_signals(false);
        }
        self.update_selection();
        if let Some(scroll) = &mut self.swatches {
            scroll.ensure_control_visible(&self.buttons[self.selected].clone().upcast::<Control>());
        }
        self.base_mut()
            .emit_signal("color_changed", &[color.to_variant()]);
    }

    #[func]
    fn show_precision(&mut self) {
        self.precision_expanded = !self.precision_expanded;
        let expanded = self.precision_expanded;
        if let Some(picker) = &mut self.precision {
            picker.set_pick_color(self.color);
            picker.set_picker_shape(if expanded {
                godot::classes::color_picker::PickerShapeType::HSV_RECTANGLE
            } else {
                godot::classes::color_picker::PickerShapeType::NONE
            });
            picker.set_position(Vector2::new(72., if expanded { 352. } else { 668. }));
            picker.set_size(Vector2::new(392., if expanded { 440. } else { 260. }));
        }
        if let Some(scroll) = &mut self.swatches {
            scroll.set_visible(!expanded);
        }
        for child in self.base().get_children().iter_shared() {
            if let Ok(mut button) = child.try_cast::<Button>()
                && button.has_meta("ui_action")
                && button.get_meta("ui_action").to::<String>() == "palette_precision"
            {
                button.set_text(if expanded {
                    "Back to swatches"
                } else {
                    "Colour field…"
                });
            }
        }
        self.update_selection();
    }

    #[func]
    pub fn accept_color(&mut self) {
        let color = self.color;
        self.base_mut().set_visible(false);
        self.base_mut()
            .emit_signal("accepted", &[color.to_variant()]);
    }

    #[func]
    pub fn cancel_color(&mut self) {
        self.base_mut().set_visible(false);
        self.base_mut().emit_signal("cancelled", &[]);
    }
}

impl NativePalette {
    /// Add the returned control to the UI after connecting its three signals.
    /// The host commits acceptance and handles stage Back or full cancellation.
    pub fn create(
        initial: Color,
        title: &str,
        price: u32,
        edit_alpha: bool,
    ) -> Result<Gd<Self>, String> {
        let json = FileAccess::get_file_as_string("res://assets/ui/native/colour-chart.json");
        let chart: serde_json::Value =
            serde_json::from_str(&json.to_string()).map_err(|error| error.to_string())?;
        let entries = chart["cells"]
            .as_array()
            .ok_or("Native colour chart is missing its cells")?;
        if chart["columns"] != COLUMNS || chart["rows"] != ROWS || entries.len() != COLUMNS * ROWS {
            return Err("Native colour chart must be the recovered 24×11 grid".into());
        }
        let mut cells = Vec::with_capacity(entries.len());
        for (index, entry) in entries.iter().enumerate() {
            if entry["column"] != index / ROWS || entry["row"] != index % ROWS {
                return Err("Native colour chart order differs from the source consumer".into());
            }
            let values = entry["rgba"]
                .as_array()
                .filter(|values| values.len() == 4)
                .ok_or("Invalid native chart RGBA")?;
            let mut rgba = [0.; 4];
            for (slot, value) in values.iter().enumerate() {
                rgba[slot] = value
                    .as_u64()
                    .filter(|value| *value <= 255)
                    .ok_or("Invalid native chart byte")? as f32
                    / 255.;
            }
            cells.push(Color::from_rgba(rgba[0], rgba[1], rgba[2], rgba[3]));
        }
        let mut node = Self::new_alloc();
        {
            let mut state = node.bind_mut();
            state.selected = nearest(&cells, initial);
            state.cells = cells;
            state.color = initial;
            state.title = title.into();
            state.price = price;
            state.edit_alpha = edit_alpha;
        }
        Ok(node)
    }

    pub fn picker(&self) -> Option<Gd<ColorPicker>> {
        self.precision.clone()
    }
    pub fn color(&self) -> Color {
        self.color
    }
    pub fn cell_button(&self, index: usize) -> Option<Gd<Button>> {
        self.buttons.get(index).cloned()
    }

    fn button(&mut self, text: &str, position: Vector2, size: Vector2, method: &str) -> Gd<Button> {
        let mut button = Button::new_alloc();
        button.set_text(text);
        button.set_position(position);
        button.set_size(size);
        button.add_theme_font_override("font", &super::native_font());
        button.add_theme_font_size_override("font_size", 23);
        let action = match method {
            "show_precision" => "palette_precision",
            "accept_color" => "palette_accept",
            "cancel_color" => "palette_cancel",
            _ => unreachable!("Palette button requires an explicit action"),
        };
        if method == "accept_color" {
            let mut style = StyleBoxFlat::new_gd();
            style.set_bg_color(super::ui_accent());
            style.set_content_margin_all(8.);
            button.add_theme_stylebox_override("normal", &style);
            button.add_theme_color_override("font_color", Color::from_rgb(0.043, 0.063, 0.078));
            button
                .add_theme_color_override("font_focus_color", Color::from_rgb(0.043, 0.063, 0.078));
        }
        if method == "show_precision" {
            button.add_theme_font_size_override("font_size", 14);
            for state in ["normal", "hover", "pressed"] {
                let mut style = StyleBoxFlat::new_gd();
                style.set_content_margin_all(3.);
                style.set_bg_color(Color::from_rgb(0.086, 0.110, 0.149));
                button.add_theme_stylebox_override(state, &style);
            }
        }
        button.set_meta("ui_action", &action.to_variant());
        button.connect("pressed", &self.base().callable(method));
        self.base_mut().add_child(&button);
        button
    }

    fn update_selection(&mut self) {
        for child in self.base().get_children().iter_shared() {
            let precision_visible = self.precision_expanded;
            if child.get_name() == "ColourChip" {
                let mut chip = child.clone().cast::<godot::classes::ColorRect>();
                chip.set_color(self.color);
                chip.set_visible(!precision_visible);
            }
            if child.get_name() == "IntensityHelp" {
                let mut help = child.clone().cast::<Control>();
                help.set_visible(true);
                help.set_position(Vector2::new(
                    72.,
                    if precision_visible { 824. } else { 946. },
                ));
            }
            if child.get_name() == "PrecisionHeading" {
                child
                    .clone()
                    .cast::<Control>()
                    .set_visible(!precision_visible);
            }
            if child.get_name() == "ColourValue"
                && let Ok(mut label) = child.try_cast::<Label>()
            {
                label.set_text(&format!(
                    "Selected #{}\nR {:.2}   G {:.2}   B {:.2}",
                    self.color.to_html(),
                    self.color.r,
                    self.color.g,
                    self.color.b
                ));
                label.set_visible(!self.precision_expanded);
            }
        }
        for (index, button) in self.buttons.iter_mut().enumerate() {
            let mut normal = StyleBoxFlat::new_gd();
            normal.set_bg_color(self.cells[index]);
            normal.set_border_width_all(if index == self.selected { 3 } else { 1 });
            normal.set_border_color(if index == self.selected {
                if self.cells[index].r + self.cells[index].g + self.cells[index].b > 1.5 {
                    Color::BLACK
                } else {
                    Color::WHITE
                }
            } else {
                Color::from_rgb(0.12, 0.12, 0.12)
            });
            button.add_theme_stylebox_override("normal", &normal);
            let mut hover = StyleBoxFlat::new_gd();
            hover.set_bg_color(self.cells[index]);
            hover.set_border_width_all(2);
            hover.set_border_color(Color::WHITE);
            button.add_theme_stylebox_override("hover", &hover);
            button.add_theme_stylebox_override("pressed", &hover);
        }
    }
}

fn nearest(cells: &[Color], color: Color) -> usize {
    cells
        .iter()
        .enumerate()
        .min_by(|(_, left), (_, right)| {
            let distance = |cell: &Color| {
                (cell.r - color.r).powi(2) + (cell.g - color.g).powi(2) + (cell.b - color.b).powi(2)
            };
            distance(left).total_cmp(&distance(right))
        })
        .map(|(index, _)| index)
        .unwrap_or(0)
}

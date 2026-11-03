//! Original 24×11 colour chart, with a separate precision-editing adaptation.
//! Layout/ARGB cells: 82344C80/82345160 and ui-17099544's COLOUR gadget.

use godot::classes::{
    Button, ColorPicker, Control, FileAccess, IControl, InputEvent, Label, StyleBoxFlat, Texture2D,
    TextureRect,
};
use godot::prelude::*;

const COLUMNS: usize = 24;
const ROWS: usize = 11;
const CHART_POSITION: Vector2 = Vector2::new(174.0096, 693.0036);
const CHART_SIZE: Vector2 = Vector2::new(630.0096, 236.25);

#[derive(GodotClass)]
#[class(base=Control)]
pub struct NativePalette {
    original: Color,
    color: Color,
    cells: Vec<Color>,
    selected: usize,
    title: String,
    price: u32,
    cash: i64,
    edit_alpha: bool,
    buttons: Vec<Gd<Button>>,
    precision: Option<Gd<ColorPicker>>,
    price_label: Option<Gd<Label>>,
    base: Base<Control>,
}

#[godot_api]
impl IControl for NativePalette {
    fn init(base: Base<Control>) -> Self {
        Self {
            original: Color::WHITE,
            color: Color::WHITE,
            cells: vec![],
            selected: 0,
            title: String::new(),
            price: 0,
            cash: 0,
            edit_alpha: false,
            buttons: vec![],
            precision: None,
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
        let layout =
            super::native_layout::NativeLayout::parse(include_str!("layouts/palette-chrome.json"))
                .expect("verified native colour-chart chrome");
        let title = self.title.clone();
        let price = format!("Price: ${}", self.price);
        let cash = format!("${}", self.cash);
        let mut parent = self.base().clone();
        match layout.render(
            &mut parent,
            &[
                ("MENUTITLE", "PAINT COLOR".into()),
                ("TITLE", title),
                ("PRICE", price),
                ("CASH", cash),
            ],
        ) {
            Ok(mut rendered) => self.price_label = rendered.texts.remove("PRICE"),
            Err(error) => {
                godot_error!("Native colour-chart chrome: {error}");
            }
        }
        for column in 0..COLUMNS {
            for row in 0..ROWS {
                let index = column * ROWS + row;
                let mut button = Button::new_alloc();
                button.set_name(&format!("Colour_{column}_{row}"));
                button.set_position(
                    CHART_POSITION
                        + Vector2::new(
                            column as f32 * CHART_SIZE.x / COLUMNS as f32,
                            row as f32 * CHART_SIZE.y / ROWS as f32,
                        ),
                );
                button.set_size(Vector2::new(
                    CHART_SIZE.x / COLUMNS as f32,
                    CHART_SIZE.y / ROWS as f32,
                ));
                button.set_focus_mode(godot::classes::control::FocusMode::NONE);
                button.set_meta("ui_action", &format!("palette_cell:{index}").to_variant());
                button.connect(
                    "pressed",
                    &self
                        .base()
                        .callable("pick_cell")
                        .bind(&[(index as i64).to_variant()]),
                );
                self.base_mut().add_child(&button);
                self.buttons.push(button);
            }
        }
        self.update_selection();
        let overlay =
            super::native_layout::NativeLayout::parse(include_str!("layouts/palette-overlay.json"))
                .expect("verified native colour-chart overlays");
        if let Err(error) = overlay.render(&mut self.base_mut().clone(), &[]) {
            godot_error!("Native colour-chart overlay: {error}");
        }
        let mut wheel = self.button(
            "",
            Vector2::new(857.5, 765.82),
            Vector2::new(205., 205.),
            "show_precision",
        );
        wheel.set_flat(true);
        let mut artwork = TextureRect::new_alloc();
        artwork.set_texture(&load::<Texture2D>("res://assets/ui/native/ui/ddc62781.png"));
        artwork.set_size(Vector2::new(205., 205.));
        artwork.set_expand_mode(godot::classes::texture_rect::ExpandMode::IGNORE_SIZE);
        artwork.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        wheel.add_child(&artwork);
        self.prompt(
            "SELECT",
            Vector2::new(1500., 950.),
            Vector2::new(155., 60.),
            "accept_color",
            "res://assets/ui/native/ui/2cb792e4.png",
        );
        self.prompt(
            "BACK",
            Vector2::new(1670., 950.),
            Vector2::new(180., 60.),
            "cancel_color",
            "res://assets/ui/native/ui/480cb5a0.png",
        );

        let mut precision = ColorPicker::new_alloc();
        precision.set_position(Vector2::new(1110., 650.));
        precision.set_size(Vector2::new(360., 280.));
        precision.set_edit_alpha(self.edit_alpha);
        precision.set_pick_color(self.color);
        precision.set_presets_visible(false);
        precision.set_modes_visible(false);
        precision.set_sampler_visible(false);
        precision.set_visible(false);
        precision.set_meta("presentation", &"Precision color editing is a reconstruction adaptation; the default chart uses original cells.".to_variant());
        precision.connect("color_changed", &self.base().callable("preview_color"));
        self.base_mut().add_child(&precision);
        self.precision = Some(precision);
        self.base_mut().grab_focus();
    }

    fn gui_input(&mut self, event: Gd<InputEvent>) {
        let column = self.selected / ROWS;
        let row = self.selected % ROWS;
        let next = if event.is_action_pressed("ui_left") {
            Some(column.saturating_sub(1) * ROWS + row)
        } else if event.is_action_pressed("ui_right") {
            Some((column + 1).min(COLUMNS - 1) * ROWS + row)
        } else if event.is_action_pressed("ui_up") {
            Some(column * ROWS + row.saturating_sub(1))
        } else if event.is_action_pressed("ui_down") {
            Some(column * ROWS + (row + 1).min(ROWS - 1))
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
    pub fn set_price(&mut self, price: u32) {
        self.price = price;
        if let Some(label) = &mut self.price_label {
            label.set_text(&format!("Price: ${price}"));
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
        self.update_selection();
        self.base_mut()
            .emit_signal("color_changed", &[color.to_variant()]);
    }

    #[func]
    fn show_precision(&mut self) {
        let color = self.color;
        if let Some(picker) = &mut self.precision {
            picker.set_pick_color(color);
            let visible = !picker.is_visible();
            picker.set_visible(visible);
        }
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
        self.preview_color(self.original);
        self.base_mut().set_visible(false);
        self.base_mut().emit_signal("cancelled", &[]);
    }
}

impl NativePalette {
    /// Add the returned control to the UI after connecting its three signals.
    /// Commit a customization only on `accepted`; cancellation restores preview.
    pub fn create(
        initial: Color,
        title: &str,
        price: u32,
        cash: i64,
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
            state.original = initial;
            state.color = initial;
            state.title = title.into();
            state.price = price;
            state.cash = cash;
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

    // Original A/B glyph art; footer hit rectangles remain an input adaptation
    // until their shared native prompt consumer's placement is recovered.
    fn prompt(&mut self, text: &str, position: Vector2, size: Vector2, method: &str, icon: &str) {
        let mut button = self.button("", position, size, method);
        button.set_flat(true);
        let mut artwork = TextureRect::new_alloc();
        artwork.set_texture(&load::<Texture2D>(icon));
        artwork.set_position(Vector2::new(0., 6.));
        artwork.set_size(Vector2::new(48., 48.));
        artwork.set_expand_mode(godot::classes::texture_rect::ExpandMode::IGNORE_SIZE);
        artwork.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        button.add_child(&artwork);
        let mut label = Label::new_alloc();
        label.set_text(text);
        label.set_position(Vector2::new(52., 8.));
        label.add_theme_font_override("font", &super::native_font());
        label.add_theme_font_size_override("font_size", 28);
        label.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        button.add_child(&label);
    }

    fn button(&mut self, text: &str, position: Vector2, size: Vector2, method: &str) -> Gd<Button> {
        let mut button = Button::new_alloc();
        button.set_text(text);
        button.set_position(position);
        button.set_size(size);
        button.add_theme_font_override("font", &super::native_font());
        button.add_theme_font_size_override("font_size", 30);
        let action = match method {
            "show_precision" => "palette_precision",
            "accept_color" => "palette_accept",
            "cancel_color" => "palette_cancel",
            _ => unreachable!("Palette button requires an explicit action"),
        };
        button.set_meta("ui_action", &action.to_variant());
        button.connect("pressed", &self.base().callable(method));
        self.base_mut().add_child(&button);
        button
    }

    fn update_selection(&mut self) {
        for (index, button) in self.buttons.iter_mut().enumerate() {
            let mut normal = StyleBoxFlat::new_gd();
            normal.set_bg_color(self.cells[index]);
            normal.set_border_width_all(if index == self.selected { 3 } else { 1 });
            normal.set_border_color(Color::from_rgb(0.12, 0.12, 0.12));
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

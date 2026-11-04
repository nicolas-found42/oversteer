mod audio;
mod effects;
mod loading;
mod native_layout;
mod native_palette;
mod paint;
mod persistence;
mod verification;
use godot::classes::{
    BoxMesh, Button, Camera3D, CanvasLayer, ColorRect, Control, DirectionalLight3D, Environment,
    FileAccess, INode3D, Input, InputEvent, InputEventKey, Label, MeshInstance3D, Node3D,
    PackedScene, ProjectSettings, RenderingServer, ResourceLoader, StandardMaterial3D,
    WorldEnvironment,
};
use godot::global::Key;
use godot::prelude::*;
use oversteer_core::*;
use std::cell::Cell;
use std::collections::BTreeMap;

struct OversteerExtension;
#[gdextension]
unsafe impl ExtensionLibrary for OversteerExtension {}

#[derive(GodotClass)]
#[class(base=Node3D)]
pub struct OversteerApp {
    base: Base<Node3D>,
    game: Option<Game>,
    content: GameContent,
    camera: Option<Gd<Camera3D>>,
    sun: Option<Gd<DirectionalLight3D>>,
    environment: Option<Gd<Environment>>,
    audio: Option<audio::RuntimeAudio>,
    scene: Option<Gd<Node3D>>,
    loading: Option<loading::SceneLoad>,
    loading_layer: Option<Gd<Control>>,
    loading_label: Option<Gd<Label>>,
    load_target: String,
    loaded_race: String,
    preload_resources: Vec<Gd<godot::classes::Resource>>,
    loading_reports: Vec<serde_json::Value>,
    title: bool,
    credits: bool,
    stage: Option<Gd<Node3D>>,
    main_stage: Option<Gd<Node3D>>,
    paint_stage: Option<Gd<Node3D>>,
    extras: bool,
    video_player: Option<Gd<godot::classes::VideoStreamPlayer>>,
    video_panel: Option<Gd<Control>>,
    video_queue: Vec<String>,
    video_active: bool,
    cars: Vec<Gd<Node3D>>,
    car_effects: Vec<effects::CarEffects>,
    last_input: PlayerInput,
    preview_angle: Option<f32>,
    all30_before: serde_json::Value,
    all30_probes: Vec<serde_json::Value>,
    sample_first: Option<serde_json::Value>,
    sample_last: Option<serde_json::Value>,
    preview: Option<Gd<Node3D>>,
    avatar: Option<Gd<Node3D>>,
    avatar_key: String,
    avatar_report: serde_json::Value,
    menu: Option<Gd<Control>>,
    hud: Option<Gd<Control>>,
    rpm_bar: Option<Gd<ColorRect>>,
    nitrous_bar: Option<Gd<ColorRect>>,
    speed_mph: bool,
    labels: BTreeMap<String, Gd<Label>>,
    previous_screen: String,
    previous_presentation: String,
    previous_car: String,
    selected_event: usize,
    selected_rival: usize,
    ui_steps: Vec<serde_json::Value>,
    ui_step: usize,
    ui_action_log: Vec<serde_json::Value>,
    ui_pending: bool,
    ui_palette_phase: u8,
    ui_capture_wait: Option<u64>,
    show_goals: bool,
    show_stats: bool,
    selected_dna: String,
    palette_target: String,
    palette_original: Option<Customization>,
    paint_session: Option<paint::Session>,
    paint_scalar_panel: Option<Gd<Control>>,
    palette_control: Option<Gd<native_palette::NativePalette>>,
    decal_catalog: serde_json::Value,
    decal_category: usize,
    goal_page: usize,
    selected_goal: String,
    event_override: String,
    car_override: String,
    save_override: String,
    settings_dir: String,
    input_event_path: String,
    input_events: Vec<serde_json::Value>,
    input_event_index: usize,
    input_frame: u64,
    input_samples: Vec<serde_json::Value>,
    command_history: std::collections::VecDeque<serde_json::Value>,
    input_nitrous_initial: Option<f32>,
    virtual_joy_replay: bool,
    settings_status: serde_json::Value,
    settings_blocked: bool,
    audio_options: serde_json::Value,
    render_quality: u8,
    save_blocked: bool,
    io_retry: String,
    load_status: serde_json::Value,
    save_status: serde_json::Value,
    wager: u32,
    pink_slip: bool,
    notice: String,
    clock: f64,
    replay: bool,
    replay_frames: Vec<RaceSnapshot>,
    replay_cursor: usize,
    wheel_audit: bool,
    scenario: String,
    capture_dir: String,
    screenshot_limit: u32,
    screenshots_generated: Cell<u32>,
    screenshot_budget_exhausted: Cell<bool>,
    frame_budget: Option<u64>,
    warmup_frames: u64,
    scenario_frame: u64,
    frame_times: Vec<f64>,
    engine_frame_times: Vec<f64>,
    last_frame: Option<std::time::Instant>,
    viewport_rid: Option<Rid>,
    gpu_times: Vec<f64>,
    cpu_times: Vec<f64>,
    physics_cpu_ms: f64,
    physics_advance_calls: u64,
    scene_sync_cpu_ms: f64,
    scene_sync_max_ms: f64,
    customization: Customization,
    options: bool,
    event_picker: bool,
    confirmation: Option<String>,
    error_dialog: Option<String>,
    custom_return: GameScreen,
    custom_page: String,
    cart_page: usize,
    cart_selected: String,
    vinyl_layer: usize,
    rebind: Option<String>,
    bindings: BTreeMap<String, Key>,
    joy_axes: BTreeMap<String, i32>,
    joy_buttons: BTreeMap<String, i32>,
    content_json: String,
}

#[godot_api]
impl INode3D for OversteerApp {
    fn init(base: Base<Node3D>) -> Self {
        Self {
            base,
            game: None,
            content: GameContent::default(),
            camera: None,
            sun: None,
            environment: None,
            audio: None,
            scene: None,
            loading: None,
            loading_layer: None,
            loading_label: None,
            load_target: String::new(),
            loaded_race: String::new(),
            preload_resources: vec![],
            loading_reports: vec![],
            title: false,
            credits: false,
            stage: None,
            main_stage: None,
            paint_stage: None,
            extras: false,
            video_player: None,
            video_panel: None,
            video_queue: vec![],
            video_active: false,
            cars: vec![],
            car_effects: vec![],
            last_input: PlayerInput::default(),
            preview_angle: None,
            all30_before: serde_json::Value::Null,
            all30_probes: vec![],
            sample_first: None,
            sample_last: None,
            preview: None,
            avatar: None,
            avatar_key: String::new(),
            avatar_report: serde_json::Value::Null,
            menu: None,
            hud: None,
            rpm_bar: None,
            nitrous_bar: None,
            speed_mph: true,
            labels: BTreeMap::new(),
            previous_screen: String::new(),
            previous_presentation: String::new(),
            previous_car: String::new(),
            selected_event: 0,
            selected_rival: 1,
            ui_steps: Vec::new(),
            ui_step: 0,
            ui_action_log: Vec::new(),
            ui_pending: false,
            ui_palette_phase: 0,
            ui_capture_wait: None,
            show_goals: false,
            show_stats: false,
            selected_dna: String::new(),
            palette_target: String::new(),
            palette_original: None,
            paint_session: None,
            paint_scalar_panel: None,
            palette_control: None,
            decal_catalog: serde_json::Value::Null,
            decal_category: 0,
            goal_page: 0,
            selected_goal: String::new(),
            event_override: String::new(),
            car_override: String::new(),
            save_override: String::new(),
            settings_dir: String::new(),
            input_event_path: String::new(),
            input_events: Vec::new(),
            input_event_index: 0,
            input_frame: 0,
            input_samples: Vec::new(),
            command_history: std::collections::VecDeque::new(),
            input_nitrous_initial: None,
            virtual_joy_replay: false,
            settings_status: serde_json::Value::Null,
            settings_blocked: false,
            audio_options: serde_json::Value::Null,
            render_quality: 1,
            save_blocked: false,
            io_retry: String::new(),
            load_status: serde_json::Value::Null,
            save_status: serde_json::Value::Null,
            wager: 0,
            pink_slip: false,
            notice: String::new(),
            clock: 0.,
            replay: false,
            replay_frames: vec![],
            replay_cursor: 0,
            wheel_audit: false,
            scenario: String::new(),
            capture_dir: String::new(),
            screenshot_limit: 50,
            screenshots_generated: Cell::new(0),
            screenshot_budget_exhausted: Cell::new(false),
            frame_budget: None,
            warmup_frames: 300,
            scenario_frame: 0,
            frame_times: vec![],
            engine_frame_times: vec![],
            last_frame: None,
            viewport_rid: None,
            gpu_times: vec![],
            cpu_times: vec![],
            physics_cpu_ms: 0.,
            physics_advance_calls: 0,
            scene_sync_cpu_ms: 0.,
            scene_sync_max_ms: 0.,
            customization: Customization::default(),
            options: false,
            event_picker: false,
            confirmation: None,
            error_dialog: None,
            custom_return: GameScreen::Garage,
            custom_page: "paint".into(),
            cart_page: 0,
            cart_selected: String::new(),
            vinyl_layer: 0,
            rebind: None,
            bindings: BTreeMap::from([
                ("throttle".into(), Key::W),
                ("brake".into(), Key::S),
                ("left".into(), Key::A),
                ("right".into(), Key::D),
                ("handbrake".into(), Key::SPACE),
                ("nitrous".into(), Key::SHIFT),
                ("reverse".into(), Key::Q),
            ]),
            joy_axes: BTreeMap::from([
                ("throttle".into(), 5),
                ("brake".into(), 4),
                ("steering".into(), 0),
            ]),
            joy_buttons: BTreeMap::from([
                ("nitrous".into(), 0),
                ("handbrake".into(), 2),
                ("reverse".into(), 3),
            ]),
            content_json: String::new(),
        }
    }
    fn ready(&mut self) {
        let args = godot::classes::Os::singleton().get_cmdline_user_args();
        let args: Vec<String> = args.as_slice().iter().map(|s| s.to_string()).collect();
        for (i, arg) in args.iter().enumerate() {
            if arg == "--scenario" {
                self.scenario = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--ui-actions" {
                let path = args.get(i + 1).cloned().unwrap_or_default();
                match std::fs::read_to_string(&path)
                    .ok()
                    .and_then(|text| serde_json::from_str::<Vec<serde_json::Value>>(&text).ok())
                {
                    Some(steps) => self.ui_steps = steps,
                    None => {
                        godot_error!("Cannot read UI action array: {}", path);
                        self.base().get_tree().quit_ex().exit_code(1).done();
                        return;
                    }
                }
            }
            if arg == "--input-events" {
                self.input_event_path = args.get(i + 1).cloned().unwrap_or_default();
                if !std::path::Path::new(&self.input_event_path).is_absolute() {
                    godot_error!("--input-events must be absolute");
                    self.base().get_tree().quit_ex().exit_code(1).done();
                    return;
                }
                match std::fs::read_to_string(&self.input_event_path)
                    .ok()
                    .and_then(|text| serde_json::from_str::<Vec<serde_json::Value>>(&text).ok())
                {
                    Some(mut events) => {
                        events.sort_by_key(|event| event["frame"].as_u64().unwrap_or(0));
                        self.virtual_joy_replay = events.iter().any(|event| {
                            !event["joy_axis"].is_null() || !event["joy_button"].is_null()
                        });
                        self.input_events = events;
                    }
                    None => {
                        godot_error!("Cannot read timed input event array");
                        self.base().get_tree().quit_ex().exit_code(1).done();
                        return;
                    }
                }
            }
            if arg == "--settings-dir" {
                self.settings_dir = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--save-file" {
                self.save_override = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--event" {
                self.event_override = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--car" {
                self.car_override = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--wager" {
                self.wager = args.get(i + 1).and_then(|s| s.parse().ok()).unwrap_or(0);
            }
            if arg == "--pink-slip" {
                self.pink_slip = true;
            }
            if arg == "--wheel-audit" {
                self.wheel_audit = true;
            }
            if arg == "--frames" {
                self.frame_budget = args.get(i + 1).and_then(|s| s.parse().ok());
            }
            if arg == "--warmup" {
                self.warmup_frames = args.get(i + 1).and_then(|s| s.parse().ok()).unwrap_or(300);
            }
            if arg == "--capture" {
                self.capture_dir = args.get(i + 1).cloned().unwrap_or_default();
            }
            if arg == "--screenshot-limit" {
                self.screenshot_limit = args
                    .get(i + 1)
                    .and_then(|s| s.parse::<u32>().ok())
                    .unwrap_or(50)
                    .min(50);
            }
        }
        self.content_json =
            FileAccess::get_file_as_string("res://assets/game-content.json").to_string();
        self.content = match serde_json::from_str(&self.content_json) {
            Ok(content) => content,
            Err(error) => {
                godot_error!("Invalid bundled game-content.json: {}", error);
                self.base().get_tree().quit_ex().exit_code(1).done();
                return;
            }
        };
        self.content.apply_oversteer_vehicle_corrections();
        if let Err(error) = self.content.apply_oversteer_career() {
            godot_error!("Invalid Oversteer career: {}", error);
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        if self.content.cars.len() != 30
            || self.content.tracks.len() != 2
            || self.content.events.len() != 18
            || self
                .content
                .events
                .iter()
                .any(|e| !self.content.tracks.iter().any(|t| t.id == e.track_id))
        {
            godot_error!(
                "Incomplete Oversteer content: expected 30 cars / 2 courses / 18 events with valid track references, got {}/{}/{}",
                self.content.cars.len(),
                self.content.tracks.len(),
                self.content.events.len()
            );
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        if !self.input_event_path.is_empty() && self.scenario.is_empty() {
            self.scenario = "manual-driving".into();
        }
        if !self.car_override.is_empty()
            && !self.content.cars.iter().any(|c| c.id == self.car_override)
        {
            godot_error!(
                "Requested car not present in production content: {}",
                self.car_override
            );
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        if !self.event_override.is_empty() {
            if let Some(index) = self
                .content
                .events
                .iter()
                .position(|e| e.id == self.event_override)
            {
                self.selected_event = index;
            } else {
                godot_error!(
                    "Requested event not present in production content: {}",
                    self.event_override
                );
                self.base().get_tree().quit_ex().exit_code(1).done();
                return;
            }
        }
        if !self.save_override.is_empty()
            && !std::path::Path::new(&self.save_override).is_absolute()
        {
            godot_error!("--save-file must be absolute");
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        if FileAccess::file_exists("res://assets/decals/catalog.json") {
            match serde_json::from_str(
                &FileAccess::get_file_as_string("res://assets/decals/catalog.json").to_string(),
            ) {
                Ok(catalog) => self.decal_catalog = catalog,
                Err(error) => {
                    godot_error!("Invalid native decal catalog: {}", error);
                    self.base().get_tree().quit_ex().exit_code(1).done();
                    return;
                }
            }
        }
        if !self.settings_dir.is_empty() && !std::path::Path::new(&self.settings_dir).is_absolute()
        {
            godot_error!("--settings-dir must be absolute");
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        self.title = self.scenario.is_empty() || self.scenario == "title";
        self.load_career();
        if self.save_blocked && !self.scenario.is_empty() {
            if !self.capture_dir.is_empty() {
                let _ = std::fs::create_dir_all(&self.capture_dir);
                let _ = std::fs::write(
                    format!("{}/load-error.json", self.capture_dir),
                    serde_json::to_string_pretty(&self.load_status).unwrap(),
                );
            }
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        self.load_settings();
        self.setup_world();
        self.setup_ui();
        self.setup_audio();
        self.apply_render_quality();
        // Direct driving automation never visits the showroom. Race loading
        // below requests the selected track and the actual participating cars.
        if self.scenario != "driving" {
            self.rebuild_menu();
            let mut initial = vec![
                "res://assets/worlds/paintbooth.glb".to_string(),
                "res://assets/worlds/tunnel_tunnel.glb".to_string(),
            ];
            if let Some(car) = self.content.cars.iter().find(|c| c.id == "GT4_HOND0030") {
                initial.push(car.model_path.clone());
            }
            let selected = self.game.as_ref().unwrap().frame_snapshot().selected_car;
            if let Some(car) = self.content.cars.iter().find(|c| c.id == selected) {
                initial.push(car.model_path.clone());
            }
            initial.push("res://assets/driver/streetwear.glb".into());
            self.begin_loading(initial, "showroom".into());
        }
        if !self.scenario.is_empty()
            && let Some(viewport) = self.base().get_viewport()
        {
            let rid = viewport.get_viewport_rid();
            RenderingServer::singleton().viewport_set_measure_render_time(rid, true);
            self.viewport_rid = Some(rid);
        }
        let server = RenderingServer::singleton();
        godot_print!(
            "OVERSTEER backend={} driver={} viewport=1920x1080",
            server.get_current_rendering_method(),
            server.get_current_rendering_driver_name()
        );
    }
    // Keep staged setup explicit so fixture overrides and input sampling order remain visible.
    #[allow(clippy::field_reassign_with_default)]
    fn process(&mut self, dt: f64) {
        if self.game.is_none() {
            return;
        }
        if self.video_active {
            if self.video_player.as_ref().is_some_and(|p| p.is_playing()) {
                return;
            }
            self.next_movie();
        }
        if !self.poll_loading() {
            self.last_frame = Some(std::time::Instant::now());
            return;
        }
        self.clock += dt;
        self.scenario_frame += 1;
        self.advance_ui_actions();
        self.replay_native_inputs();
        let now = std::time::Instant::now();
        let wall = self
            .last_frame
            .replace(now)
            .map(|last| now.duration_since(last).as_secs_f64())
            .unwrap_or(dt);
        let active_sample = self.scenario != "benchmark"
            || self
                .game
                .as_ref()
                .unwrap()
                .frame_snapshot()
                .race
                .as_ref()
                .is_some_and(|r| r.countdown <= 0.);
        if !self.scenario.is_empty() && active_sample {
            let phase = self.game.as_ref().unwrap().frame_snapshot();
            let phase = serde_json::json!({"frame":self.scenario_frame,"screen":phase.screen,"countdown":phase.race.as_ref().map(|r|r.countdown),"elapsed":phase.race.as_ref().map(|r|r.elapsed)});
            if self.sample_first.is_none() {
                self.sample_first = Some(phase.clone());
            }
            self.sample_last = Some(phase);
            self.frame_times.push(wall * 1000.);
            self.engine_frame_times.push(dt * 1000.);
            if let Some(rid) = self.viewport_rid {
                let server = RenderingServer::singleton();
                self.gpu_times
                    .push(server.viewport_get_measured_render_time_gpu(rid));
                self.cpu_times
                    .push(server.viewport_get_measured_render_time_cpu(rid));
            }
        }
        let input = Input::singleton();
        let pressed = |key| {
            if input.is_physical_key_pressed(key) {
                1.
            } else {
                0.
            }
        };
        let mut controls = PlayerInput::default();
        controls.reverse = pressed(self.bindings["reverse"]) > 0.;
        controls.throttle = pressed(self.bindings["throttle"]);
        controls.brake = pressed(self.bindings["brake"]);
        controls.steering = host_steering(
            pressed(self.bindings["left"]),
            pressed(self.bindings["right"]),
            0.,
        );
        controls.handbrake = pressed(self.bindings["handbrake"]);
        controls.nitrous = pressed(self.bindings["nitrous"]);
        let ids = input.get_connected_joypads();
        if !ids.is_empty() || self.virtual_joy_replay {
            use godot::global::JoyAxis;
            let id = if self.virtual_joy_replay {
                0
            } else {
                ids.get(0).unwrap_or(0) as i32
            };
            controls.throttle = controls.throttle.max(
                input
                    .get_joy_axis(id, JoyAxis::from_ord(self.joy_axes["throttle"]))
                    .max(0.),
            );
            controls.brake = controls.brake.max(
                input
                    .get_joy_axis(id, JoyAxis::from_ord(self.joy_axes["brake"]))
                    .max(0.),
            );
            controls.reverse |= input.is_joy_button_pressed(
                id,
                godot::global::JoyButton::from_ord(self.joy_buttons["reverse"]),
            );
            controls.nitrous = controls.nitrous.max(
                if input.is_joy_button_pressed(
                    id,
                    godot::global::JoyButton::from_ord(self.joy_buttons["nitrous"]),
                ) {
                    1.
                } else {
                    0.
                },
            );
            controls.handbrake = controls.handbrake.max(
                if input.is_joy_button_pressed(
                    id,
                    godot::global::JoyButton::from_ord(self.joy_buttons["handbrake"]),
                ) {
                    1.
                } else {
                    0.
                },
            );
            let steering = input.get_joy_axis(id, JoyAxis::from_ord(self.joy_axes["steering"]));
            if steering.abs() > 0.12 {
                controls.steering = host_steering(0., 0., steering);
            }
        }
        if !self.scenario.is_empty() {
            self.run_scenario(&mut controls);
        }
        self.last_input = controls;
        if self.input_event_path.is_empty()
            && matches!(
                self.scenario.as_str(),
                "career-race" | "results" | "podium" | "round-results"
            )
        {
            for _ in 0..5 {
                let input = self.game.as_ref().unwrap().scenario_player_ai_input();
                self.game.as_mut().unwrap().advance(dt as f32, input);
            }
        }
        let physics_start = std::time::Instant::now();
        self.game.as_mut().unwrap().advance(dt as f32, controls);
        self.physics_cpu_ms += physics_start.elapsed().as_secs_f64() * 1000.;
        self.physics_advance_calls += 1;
        let sync_start = std::time::Instant::now();
        if self.scenario != "driving" || self.scenario_frame >= 3 {
            self.refresh();
        }
        let sync_ms = sync_start.elapsed().as_secs_f64() * 1000.;
        self.scene_sync_cpu_ms += sync_ms;
        self.scene_sync_max_ms = self.scene_sync_max_ms.max(sync_ms);
        self.record_native_inputs(dt, controls);
        if self.loading.is_none() {
            let snapshot = self.game.as_ref().unwrap().frame_snapshot();
            if let Some(audio) = &mut self.audio {
                let nitrous = snapshot
                    .race
                    .as_ref()
                    .and_then(|race| race.racers.first())
                    .is_some_and(|racer| racer.nitrous_active);
                audio.update(&snapshot, controls.throttle, nitrous);
            }
        }
    }
    fn exit_tree(&mut self) {
        if self.scenario.is_empty() {
            self.send(GameCommand::Navigate {
                screen: GameScreen::MainMenu,
            });
        }
        if let Some(audio) = &mut self.audio {
            audio.shutdown();
        }
        if let Some(video) = &mut self.video_player {
            video.stop();
            video.set_stream(None::<&Gd<godot::classes::VideoStream>>);
        }
        self.persist();
    }
    fn input(&mut self, event: Gd<InputEvent>) {
        if self.video_active {
            let pressed = event
                .clone()
                .try_cast::<InputEventKey>()
                .is_ok_and(|key| key.is_pressed() && !key.is_echo())
                || event
                    .clone()
                    .try_cast::<godot::classes::InputEventJoypadButton>()
                    .is_ok_and(|button| button.is_pressed());
            if pressed {
                self.next_movie();
                if let Some(mut viewport) = self.base().get_viewport() {
                    viewport.set_input_as_handled();
                }
            }
            return;
        }
        if self.loading.is_some() {
            return;
        }
        if self.paint_scalar_panel.is_some() {
            let cancel = event
                .clone()
                .try_cast::<InputEventKey>()
                .is_ok_and(|key| key.is_pressed() && key.get_keycode() == Key::ESCAPE)
                || event
                    .clone()
                    .try_cast::<godot::classes::InputEventJoypadButton>()
                    .is_ok_and(|button| {
                        button.is_pressed()
                            && button.get_button_index() == godot::global::JoyButton::B
                    });
            let accept = event.clone().try_cast::<InputEventKey>().is_ok_and(|key| {
                key.is_pressed() && matches!(key.get_keycode(), Key::ENTER | Key::KP_ENTER)
            }) || event
                .clone()
                .try_cast::<godot::classes::InputEventJoypadButton>()
                .is_ok_and(|button| {
                    button.is_pressed() && button.get_button_index() == godot::global::JoyButton::A
                });
            if cancel {
                self.paint_stage_cancel();
            } else if accept {
                self.advance_paint_stage();
            }
            if (cancel || accept)
                && let Some(mut viewport) = self.base().get_viewport()
            {
                viewport.set_input_as_handled();
            }
            return;
        }
        // Palette owns GUI navigation/cancel while open; global Escape must not leave the screen.
        if self.palette_control.is_some() {
            return;
        }
        if let Ok(motion) = event
            .clone()
            .try_cast::<godot::classes::InputEventJoypadMotion>()
            && motion.get_axis_value().abs() > 0.6
            && let Some(action) = self
                .rebind
                .clone()
                .and_then(|s| s.strip_prefix("axis:").map(str::to_owned))
        {
            swap_binding(&mut self.joy_axes, action, motion.get_axis().ord());
            self.rebind = None;
            if let Some(mut viewport) = self.base().get_viewport() {
                viewport.set_input_as_handled();
            }
            self.save_settings();
            self.rebuild_menu();
            return;
        }
        if let Ok(button) = event
            .clone()
            .try_cast::<godot::classes::InputEventJoypadButton>()
            && button.is_pressed()
        {
            if self.title && button.get_button_index() == godot::global::JoyButton::START {
                self.action("title_start".into());
                return;
            }
            if button.get_button_index() == godot::global::JoyButton::START && self.rebind.is_none()
            {
                if let Some(game) = &mut self.game {
                    let paused = game.frame_snapshot().screen == GameScreen::Paused;
                    let _ = game.command(if paused {
                        GameCommand::Resume
                    } else {
                        GameCommand::Pause
                    });
                }
                return;
            }
            if let Some(action) = self
                .rebind
                .clone()
                .and_then(|s| s.strip_prefix("button:").map(str::to_owned))
            {
                swap_binding(
                    &mut self.joy_buttons,
                    action,
                    button.get_button_index().ord(),
                );
                self.rebind = None;
                if let Some(mut viewport) = self.base().get_viewport() {
                    viewport.set_input_as_handled();
                }
                self.save_settings();
                self.rebuild_menu();
                return;
            }
        }
        if let Ok(key) = event.try_cast::<InputEventKey>() {
            if !key.is_pressed() || key.is_echo() {
                return;
            }
            if self
                .rebind
                .as_ref()
                .is_some_and(|s| s.starts_with("axis:") || s.starts_with("button:"))
            {
                return;
            }
            if let Some(action) = self.rebind.take() {
                let new_key = key.get_physical_keycode();
                let old_key = self.bindings[&action];
                let conflict = self
                    .bindings
                    .iter()
                    .find(|(a, k)| **a != action && **k == new_key)
                    .map(|(a, _)| a.clone());
                if let Some(conflict) = conflict {
                    self.bindings.insert(conflict, old_key);
                }
                self.bindings.insert(action, new_key);
                self.save_settings();
                self.rebuild_menu();
                return;
            }
            if key.get_keycode() == Key::ESCAPE {
                if self.confirmation.take().is_some() {
                    self.rebuild_menu();
                    return;
                }
                if self.show_stats {
                    self.show_stats = false;
                    self.rebuild_menu();
                    return;
                }
                if self.show_goals {
                    self.show_goals = false;
                    self.rebuild_menu();
                    return;
                }
                if self.options {
                    self.options = false;
                    self.rebuild_menu();
                    return;
                }
                if let Some(game) = &mut self.game {
                    let paused = game.snapshot().screen == GameScreen::Paused;
                    let _ = game.command(if paused {
                        GameCommand::Resume
                    } else {
                        GameCommand::Pause
                    });
                }
            }
            if key.get_keycode() == Key::R {
                self.send(GameCommand::ResetCar);
            }
        }
    }
}

#[godot_api]
impl OversteerApp {
    /// Read-only tooling seam: callers can wait without serializing the full scene each frame.
    #[func]
    fn diagnostic_input_frame(&self) -> i64 {
        self.input_frame as i64
    }

    #[func]
    fn diagnostic_snapshot(&self) -> GString {
        let snapshot = self.game.as_ref().map(Game::frame_snapshot);
        let player = snapshot
            .as_ref()
            .and_then(|s| s.race.as_ref())
            .and_then(|r| r.racers.first());
        let catalog: serde_json::Value = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
        )
        .unwrap_or_default();
        let definition = player.and_then(|p| {
            catalog["cars"]
                .as_array()?
                .iter()
                .find(|c| c["code"].as_str() == Some(&p.car_id))
        });
        let materials = self
            .cars
            .first()
            .zip(definition)
            .map(|(car, definition)| verification::materials(car, definition));
        let wheels = self
            .cars
            .first()
            .zip(player)
            .map(|(car, player)| wheel_visual_samples(car, player));
        let hud: BTreeMap<_, _> = self
            .labels
            .iter()
            .map(|(name, label)| {
                let rect = label.get_global_rect();
                (
                    name,
                    serde_json::json!({"text":label.get_text().to_string(),
                "position":[rect.position.x,rect.position.y],"size":[rect.size.x,rect.size.y]}),
                )
            })
            .collect();
        GString::from(&serde_json::json!({"schema":1,"input_frame":self.input_frame,"process_frame":self.scenario_frame,
            "input_events_processed":self.input_event_index,"input_events_total":self.input_events.len(),
            "snapshot":snapshot,"rendered_wheels":wheels,"materials":materials,"hud":hud,
            "recent_commands":self.command_history,
            "recent_input_samples":&self.input_samples[self.input_samples.len().saturating_sub(120)..],
            "timing":{"physics_cpu_ms":self.physics_cpu_ms,"physics_advance_calls":self.physics_advance_calls,"scene_sync_cpu_ms":self.scene_sync_cpu_ms,"scene_sync_max_ms":self.scene_sync_max_ms},
            "loading":self.loading_reports,"save_status":self.save_status,"load_status":self.load_status
        }).to_string())
    }

    #[func]
    fn paint_scalar_changed(&mut self, value: f64, channel: i64) {
        if self.paint_session.as_ref().and_then(paint::Session::stage)
            != Some(paint::Stage::Scalar(channel as u32))
        {
            return;
        }
        let mut record = paint::donor_seed(&self.customization);
        match paint::scalar(&mut record, channel as u32, value as f32) {
            Ok(()) => {
                self.customization.native_paint = Some(record);
                // Local preview only. The final accepted stage submits one draft.
                if let Some(mut preview) = self.preview.take() {
                    let (uniform, value) = match channel {
                        2 => (
                            "paint_balance",
                            self.customization
                                .native_paint
                                .as_ref()
                                .unwrap()
                                .two_tone_exp,
                        ),
                        4 => (
                            "paint_flakie",
                            self.customization.native_paint.as_ref().unwrap().flakie,
                        ),
                        5 => (
                            "paint_focus",
                            self.customization
                                .native_paint
                                .as_ref()
                                .unwrap()
                                .fleck_power,
                        ),
                        _ => (
                            "paint_film",
                            self.customization
                                .native_paint
                                .as_ref()
                                .unwrap()
                                .film_thickness,
                        ),
                    };
                    preview_paint_scalar(&mut preview, uniform, value as f64);
                    self.preview = Some(preview);
                }
            }
            Err(error) => self.error_dialog = Some(error),
        }
    }
    fn reload_paint_preview(&mut self) {
        let selected = self.game.as_ref().unwrap().frame_snapshot().selected_car;
        let Some(path) = self
            .content
            .cars
            .iter()
            .find(|car| car.id == selected)
            .map(|car| car.model_path.clone())
        else {
            return;
        };
        let transform = self
            .preview
            .as_ref()
            .map(|preview| preview.get_transform())
            .unwrap_or(Transform3D::IDENTITY);
        if let Some(mut previous) = self.preview.take() {
            previous.queue_free();
        }
        let mut preview = Self::load_scene(&path);
        preview.set_transform(transform);
        self.base_mut().add_child(&preview);
        self.tint(&mut preview, &selected, &self.customization);
        self.swap_wheels(&mut preview, &selected, &self.customization);
        self.apply_kits(&mut preview, &selected, &self.customization);
        self.preview = Some(preview);
    }
    fn preview_quote_cost(&self, field: &str) -> u32 {
        let game = self.game.as_ref().unwrap();
        if field == "paint" && self.paint_session.is_some() {
            return game
                .quote_native_paint(&paint::donor_seed(&self.customization))
                .expect("paint session has a validated native family")
                .cost;
        }
        game.quote_customization(&self.customization)
            .iter()
            .filter(|item| item.field == field)
            .map(|item| item.cost)
            .sum()
    }
    fn advance_paint_stage(&mut self) {
        if let Some(mut panel) = self.paint_scalar_panel.take() {
            panel.set_visible(false);
            panel.queue_free();
        }
        let Some(session) = self.paint_session.as_mut() else {
            return;
        };
        session.cursor += 1;
        match session.stage() {
            Some(paint::Stage::Color(channel)) => {
                self.palette_opened(if channel == 1 { "secondary" } else { "fleck" }.into());
            }
            Some(paint::Stage::Scalar(channel)) => self.open_paint_scalar_stage(channel),
            None => {
                self.paint_session = None;
                if let Some(record) = self.customization.native_paint.clone() {
                    let car_id = self.game.as_ref().unwrap().frame_snapshot().selected_car;
                    self.send(GameCommand::AcceptNativePaint {
                        car_id,
                        paint: record,
                    });
                    self.previous_car.clear();
                    self.persist();
                    self.rebuild_menu();
                }
            }
        }
    }
    #[func]
    fn paint_stage_cancel(&mut self) {
        if let Some(mut palette) = self.palette_control.take() {
            palette.set_visible(false);
            palette.queue_free();
        }
        if let Some(mut panel) = self.paint_scalar_panel.take() {
            panel.set_visible(false);
            panel.queue_free();
        }
        self.palette_target.clear();
        self.palette_original = None;
        if let Some(session) = self.paint_session.as_mut()
            && session.back()
        {
            match session.stage() {
                Some(paint::Stage::Color(channel)) => self.palette_opened(
                    match channel {
                        0 => "body",
                        1 => "secondary",
                        _ => "fleck",
                    }
                    .into(),
                ),
                Some(paint::Stage::Scalar(channel)) => self.open_paint_scalar_stage(channel),
                None => unreachable!("verified paint stage order"),
            }
            return;
        }
        if let Some(session) = self.paint_session.take() {
            self.customization = session.original;
        }
        self.reload_paint_preview();
        self.rebuild_menu();
    }
    fn open_paint_scalar_stage(&mut self, channel: u32) {
        let record = paint::donor_seed(&self.customization);
        let (title, value) = match channel {
            2 => ("SELECT PEARLESCENT BALANCE", record.two_tone_exp),
            4 => ("SET FLAKE SIZE", (record.flakie - 0.3) / 0.7),
            5 => ("SET FLAKE FOCUS", (record.fleck_power - 100.) / 48.),
            _ => ("SET FILM DEPTH", (record.film_thickness - 0.0055) / 0.02),
        };
        let mut panel = Control::new_alloc();
        panel.set_size(Vector2::new(1920., 1080.));
        panel.set_z_index(90);
        panel.set_mouse_filter(godot::classes::control::MouseFilter::STOP);
        let price = self.preview_quote_cost("paint");
        let cash = self.game.as_ref().unwrap().frame_snapshot().career.cash;
        let layout =
            native_layout::NativeLayout::parse(include_str!("layouts/palette-chrome.json"))
                .expect("verified native paint chrome");
        if let Err(error) = layout.render(
            &mut panel,
            &[
                ("MENUTITLE", "PAINT COLOR".into()),
                ("TITLE", title.into()),
                ("PRICE", format!("Price: ${price}")),
                ("CASH", format!("${cash}")),
            ],
        ) {
            self.error_dialog = Some(error);
        }
        // Scalar widget coordinates are a presentation adapter; the channel,
        // order and conversion are retained from the original source consumer.
        let mut slider = godot::classes::HSlider::new_alloc();
        slider.set_min(0.);
        slider.set_max(1.);
        slider.set_step(0.001);
        slider.set_value(value.clamp(0., 1.) as f64);
        slider.set_position(Vector2::new(174., 760.));
        slider.set_size(Vector2::new(630., 54.));
        slider.set_meta("ui_action", &format!("paint:scalar:{channel}").to_variant());
        slider.connect(
            "value_changed",
            &self
                .base()
                .callable("paint_scalar_changed")
                .bind(&[(channel as i64).to_variant()]),
        );
        panel.add_child(&slider);
        self.button(
            &mut panel,
            "ACCEPT",
            "paint_stage_accept",
            1240.,
            954.,
            230.,
            60.,
        );
        self.button(
            &mut panel,
            "BACK",
            "paint_stage_cancel",
            1510.,
            954.,
            230.,
            60.,
        );
        if let Some(menu) = &mut self.menu {
            for child in menu.get_children().iter_shared() {
                if let Ok(mut control) = child.try_cast::<Control>() {
                    control.set_visible(false);
                }
            }
            menu.add_child(&panel);
        }
        slider.grab_focus();
        self.paint_scalar_panel = Some(panel);
    }
    #[func]
    fn palette_opened(&mut self, target: GString) {
        if self.palette_control.is_some() {
            return;
        }
        let target = target.to_string();
        let family = if self.customization.finish == "matte" {
            "matt"
        } else {
            self.customization.finish.as_str()
        };
        if target == "body" && self.paint_session.is_none() && !paint::stages(family).is_empty() {
            let original = self.customization.clone();
            let family = family.to_string();
            if self.customization.native_paint.is_none() {
                let mut record = paint::donor_seed(&self.customization);
                let rgb = self.customization.paint;
                paint::color(&mut record, &family, 0, [rgb[0], rgb[1], rgb[2]])
                    .expect("validated native paint family");
                self.customization.native_paint = Some(record);
            }
            self.paint_session = Some(paint::Session {
                original,
                family,
                cursor: 0,
            });
        }
        if target == "body" && self.paint_session.is_none() {
            self.error_dialog = Some("Choose a paint finish before editing its color.".into());
            self.rebuild_menu();
            return;
        }
        let color = match target.as_str() {
            "body" => self.customization.paint,
            "secondary" => {
                let rgb = paint::donor_seed(&self.customization).secondary_rgb;
                [rgb[0], rgb[1], rgb[2], 1.]
            }
            "fleck" => {
                let rgb = paint::donor_seed(&self.customization).fleck_rgb;
                [rgb[0], rgb[1], rgb[2], 1.]
            }
            "wheel" => self.customization.wheel_paint,
            "vinyl" => self
                .customization
                .vinyls
                .get(self.vinyl_layer)
                .map(|layer| layer.color)
                .unwrap_or([1.; 4]),
            _ => return,
        };
        let field = match target.as_str() {
            "body" | "secondary" | "fleck" => "paint",
            "wheel" => "wheel_paint",
            _ => "vinyls",
        };
        let price = self.preview_quote_cost(field);
        match native_palette::NativePalette::create(
            Color::from_rgba(color[0], color[1], color[2], color[3]),
            match target.as_str() {
                "body" => "SELECT BASE COLOUR",
                "secondary" => "SELECT PEARLESCENT COLOR",
                "fleck" => "SET FLAKE COLOR",
                "wheel" => "SELECT WHEEL COLOUR",
                _ => "SELECT VINYL COLOUR",
            },
            price,
            self.game.as_ref().unwrap().frame_snapshot().career.cash,
            matches!(target.as_str(), "wheel" | "vinyl"),
        ) {
            Ok(mut palette) => {
                palette.connect(
                    "color_changed",
                    &self
                        .base()
                        .callable("palette_changed")
                        .bind(&[target.to_variant()]),
                );
                palette.connect("accepted", &self.base().callable("palette_accepted"));
                palette.connect("cancelled", &self.base().callable("palette_cancelled"));
                if let Some(menu) = &mut self.menu {
                    for child in menu.get_children().iter_shared() {
                        if let Ok(mut control) = child.try_cast::<Control>() {
                            control.set_visible(false);
                        }
                    }
                    menu.add_child(&palette);
                }
                self.palette_original = Some(self.customization.clone());
                self.palette_target = target;
                self.palette_control = Some(palette);
            }
            Err(error) => {
                self.error_dialog = Some(error);
                self.rebuild_menu();
            }
        }
    }
    #[func]
    fn palette_accepted(&mut self, color: Color) {
        self.palette_changed(color, GString::from(self.palette_target.as_str()));
        if let Some(mut palette) = self.palette_control.take() {
            palette.queue_free();
        }
        self.palette_target.clear();
        self.palette_original = None;
        if self.paint_session.is_some() {
            self.advance_paint_stage();
        } else {
            self.apply_custom();
        }
    }
    #[func]
    fn palette_cancelled(&mut self) {
        if self.paint_session.is_some() {
            self.paint_stage_cancel();
            return;
        }
        if let Some(original) = self.palette_original.take() {
            self.customization = original;
        }
        self.previous_car.clear();
        if let Some(mut palette) = self.palette_control.take() {
            palette.queue_free();
        }
        self.palette_target.clear();
        self.rebuild_menu();
    }
    #[func]
    fn palette_changed(&mut self, color: Color, target: GString) {
        let rgba = [color.r, color.g, color.b, color.a];
        let field = match target.to_string().as_str() {
            "body" | "secondary" | "fleck" => {
                let channel = match target.to_string().as_str() {
                    "secondary" => 1,
                    "fleck" => 3,
                    _ => 0,
                };
                let mut record = paint::donor_seed(&self.customization);
                let family = self
                    .paint_session
                    .as_ref()
                    .map(|session| session.family.as_str())
                    .unwrap_or(self.customization.finish.as_str());
                if paint::stages(family).is_empty()
                    && channel == 0
                    && self.customization.native_paint.is_none()
                {
                    // Preserve legacy save finishes without inventing a native
                    // family mapping, particularly chrome versus thin film.
                    self.customization.paint = rgba;
                } else {
                    if let Err(error) =
                        paint::color(&mut record, family, channel, [color.r, color.g, color.b])
                    {
                        self.error_dialog = Some(error);
                        return;
                    }
                    self.customization.paint = [
                        record.base_rgb[0],
                        record.base_rgb[1],
                        record.base_rgb[2],
                        1.,
                    ];
                    self.customization.native_paint = Some(record);
                }
                "paint"
            }
            "wheel" => {
                self.customization.wheel_paint = rgba;
                "wheel_paint"
            }
            "vinyl" => {
                if let Some(layer) = self.customization.vinyls.get_mut(self.vinyl_layer) {
                    layer.color = rgba;
                }
                "vinyls"
            }
            _ => return,
        };
        if let Some(mut preview) = self.preview.take() {
            match field {
                "paint" => {
                    let target = target.to_string();
                    if target == "secondary" || target == "fleck" {
                        preview_paint_uniform(
                            &mut preview,
                            if target == "secondary" {
                                "paint_secondary"
                            } else {
                                "paint_fleck"
                            },
                            color,
                        );
                    } else {
                        preview_paint(&mut preview, color);
                    }
                }
                "wheel_paint" => {
                    if !preview_rim_tint(&mut preview, color) {
                        self.swap_wheels(
                            &mut preview,
                            &self.game.as_ref().unwrap().frame_snapshot().selected_car,
                            &self.customization,
                        );
                    }
                }
                _ => preview_vinyl_tint(&mut preview, self.vinyl_layer, color),
            }
            self.preview = Some(preview);
        }
        let price = self.preview_quote_cost(field);
        if let Some(palette) = &mut self.palette_control {
            palette.call_deferred("set_price", &[price.to_variant()]);
        }
    }
    #[func]
    fn decal_category_selected(&mut self, index: i64) {
        self.decal_category = index.max(0) as usize;
        self.rebuild_menu();
    }
    #[func]
    fn decal_design_selected(&mut self, index: i64) {
        let ids = &self.decal_catalog["categories"][self.decal_category]["design_ids"];
        if let Some(id) = ids[index.max(0) as usize].as_str()
            && let Some(layer) = self.customization.vinyls.get_mut(self.vinyl_layer)
        {
            layer.design_id = id.into();
            layer.color = [1.; 4];
            self.apply_custom();
        }
    }
    #[func]
    fn vinyl_selected(&mut self, index: i64) {
        self.vinyl_layer =
            (index.max(0) as usize).min(self.customization.vinyls.len().saturating_sub(1));
        self.rebuild_menu();
    }
    #[func]
    fn plate_name(&mut self, name: GString) {
        self.customization.plate_text = name.to_string();
        self.apply_custom();
    }
    #[func]
    fn driver_name(&mut self, name: GString) {
        let mut profile = self.game.as_ref().unwrap().frame_snapshot().profile;
        profile.name = name.to_string();
        self.send(GameCommand::CustomizeAvatar { profile });
        self.persist();
    }
    #[func]
    // Keep staged setup explicit so fixture overrides and input sampling order remain visible.
    #[allow(clippy::field_reassign_with_default)]
    fn action(&mut self, key: GString) {
        let key = key.to_string();
        self.notice.clear();
        if let Some(audio) = &mut self.audio {
            audio.effect("select");
        }
        if let Some(kind) = key.strip_prefix("audio:") {
            if let Some(audio) = &mut self.audio {
                audio.cycle_gain(kind);
            }
            self.save_settings();
            self.rebuild_menu();
            return;
        }

        if key == "podium" {
            self.send(GameCommand::ShowPodium);
            return;
        }
        if key == "career_events" {
            self.selected_goal.clear();
            self.event_picker = true;
            self.rebuild_menu();
            return;
        }
        if key == "replay" {
            self.replay = true;
            self.replay_cursor = 0;
            self.rebuild_menu();
            return;
        }
        if key == "replay_done" {
            self.replay = false;
            self.rebuild_menu();
            return;
        }
        if let Some(movie) = key.strip_prefix("movie:") {
            self.video_queue = vec![movie.into()];
            self.next_movie();
            return;
        }
        if key == "movie_skip" {
            self.next_movie();
            return;
        }
        if key == "extras" {
            self.extras = true;
            self.rebuild_menu();
            return;
        }
        if key == "extras_back" {
            self.extras = false;
            self.rebuild_menu();
            return;
        }
        if key == "title_start" {
            self.title = false;
            self.rebuild_menu();
            return;
        }
        if key == "credits" {
            self.credits = true;
            self.rebuild_menu();
            return;
        }
        if key == "credits_back" {
            self.credits = false;
            self.rebuild_menu();
            return;
        }
        if key == "retry_io" {
            self.error_dialog = None;
            if self.io_retry == "load" {
                self.load_career();
            } else if self.io_retry == "settings_load" {
                self.load_settings();
                self.apply_render_quality();
            } else if self.io_retry == "settings_save" {
                self.save_settings();
            } else {
                self.persist();
            }
            self.rebuild_menu();
            return;
        }
        if key == "new_career" {
            let path = self.save_path();
            match persistence::preserve(std::path::Path::new(&path)) {
                Ok(_) => {
                    let backup = format!("{path}.backup");
                    if let Err(error) = persistence::preserve(std::path::Path::new(&backup)) {
                        self.error_dialog = Some(error);
                        self.rebuild_menu();
                        return;
                    }
                    self.game = Some(Game::new(self.content.clone()));
                    self.load_settings();
                    self.save_blocked = false;
                    self.io_retry.clear();
                    self.error_dialog = None;
                    self.persist();
                    self.send(GameCommand::Navigate {
                        screen: GameScreen::Career,
                    });
                }
                Err(error) => self.error_dialog = Some(error),
            }
            self.rebuild_menu();
            return;
        }
        if key == "custom_done" {
            self.send(GameCommand::Navigate {
                screen: self.custom_return,
            });
            self.persist();
            return;
        }
        if key == "error_ok" {
            self.error_dialog = None;
            self.rebuild_menu();
            return;
        }
        if key == "confirm_no" {
            self.confirmation = None;
            self.rebuild_menu();
            return;
        }
        if key == "confirm_yes" {
            let action = self.confirmation.take().unwrap_or_default();
            let id = self.game.as_ref().unwrap().frame_snapshot().selected_car;
            match action.as_str() {
                "buy" => self.send(GameCommand::BuyCar { car_id: id }),
                "sell" => self.send(GameCommand::SellCar { car_id: id }),
                "checkout" => {
                    self.send(GameCommand::Checkout);
                    self.previous_car.clear();
                }
                "pink_offer" => self.send(GameCommand::OfferPinkSlip {
                    racer: self.selected_rival,
                }),
                "discard" => {
                    self.send(GameCommand::DiscardCart { car_id: None });
                    self.previous_car.clear();
                }
                _ => {}
            }
            self.persist();
            self.rebuild_menu();
            return;
        }
        if key == "checkout" {
            self.confirmation = Some("checkout".into());
            self.rebuild_menu();
            return;
        }
        if key == "discard_cart" {
            self.confirmation = Some("discard".into());
            self.rebuild_menu();
            return;
        }
        if let Some(item) = key.strip_prefix("cart_remove:") {
            self.send(GameCommand::RemoveCartItem {
                item_id: item.into(),
            });
            self.previous_car.clear();
            self.rebuild_menu();
            return;
        }
        if key == "wheel_color" {
            self.customization.wheel_paint = if self.customization.wheel_paint[0] > 0.6 {
                [0.08, 0.08, 0.09, 1.]
            } else {
                [0.85, 0.6, 0.18, 1.]
            };
            self.apply_custom();
            return;
        }
        if key == "plate_style" {
            self.customization.plate_style = if self.customization.plate_style == "stock" {
                "dark".into()
            } else {
                "stock".into()
            };
            self.apply_custom();
            return;
        }
        if key == "units" {
            self.speed_mph = !self.speed_mph;
            self.save_settings();
            self.rebuild_menu();
            return;
        }
        if key == "quality" {
            self.render_quality = (self.render_quality + 1) % 3;
            self.apply_render_quality();
            self.save_settings();
            self.rebuild_menu();
            return;
        }
        if key == "difficulty" {
            let level = (self.game.as_ref().unwrap().frame_snapshot().difficulty + 1) % 3;
            self.send(GameCommand::SetDifficulty { level });
            self.save_settings();
            self.persist();
            self.rebuild_menu();
            return;
        }
        if key == "options" {
            self.options = true;
            self.rebuild_menu();
            return;
        }
        if key == "back_options" {
            self.options = false;
            self.rebuild_menu();
            return;
        }
        if key.starts_with("axis:") || key.starts_with("button:") {
            self.rebind = Some(key);
            self.notice = "Move a controller axis or press its new button…".into();
            self.rebuild_menu();
            return;
        }
        if let Some(action) = key.strip_prefix("bind:") {
            self.rebind = Some(action.into());
            self.notice = "Press a key…".into();
            self.rebuild_menu();
            return;
        }
        if key == "quit" {
            self.send(GameCommand::Navigate {
                screen: GameScreen::MainMenu,
            });
            if self.persist() {
                self.base().get_tree().quit();
            }
            return;
        }
        if key == "save" {
            self.persist();
            self.notice = "Career saved".into();
            self.rebuild_menu();
            return;
        }
        if let Some(screen) = key.strip_prefix("nav:") {
            let screen = match screen {
                "career" => GameScreen::Career,
                "quick" => GameScreen::QuickRace,
                "garage" => GameScreen::Garage,
                "dealer" => GameScreen::Dealership,
                "custom" => GameScreen::Customization,
                "checkout" => GameScreen::Checkout,
                _ => GameScreen::MainMenu,
            };
            if screen == GameScreen::Customization {
                let current = self.game.as_ref().unwrap().frame_snapshot().screen;
                if current != GameScreen::Checkout && current != GameScreen::Customization {
                    self.custom_return = if current == GameScreen::QuickRace {
                        GameScreen::QuickRace
                    } else {
                        GameScreen::Garage
                    };
                }
            }
            self.options = false;
            self.event_picker = false;
            self.selected_goal.clear();
            let leaving_race = self.game.as_ref().unwrap().frame_snapshot().race.is_some();
            self.send(GameCommand::Navigate { screen });
            if leaving_race {
                self.persist();
            }
            self.previous_screen.clear();
            return;
        }
        if key == "car_next" || key == "car_prev" {
            let snap = self.game.as_ref().unwrap().frame_snapshot();
            let eligible: Vec<_> = self
                .content
                .cars
                .iter()
                .filter(|c| {
                    !matches!(snap.screen, GameScreen::Garage | GameScreen::Career)
                        || snap.career.garage.contains_key(&c.id)
                })
                .collect();
            if !eligible.is_empty() {
                let index = eligible
                    .iter()
                    .position(|c| c.id == snap.selected_car)
                    .unwrap_or(0);
                let next = if key == "car_next" {
                    (index + 1) % eligible.len()
                } else {
                    (index + eligible.len() - 1) % eligible.len()
                };
                self.send(GameCommand::SelectCar {
                    car_id: eligible[next].id.clone(),
                });
                self.previous_car.clear();
            }
            return;
        }
        if key == "event_next" || key == "event_prev" {
            let snap = self.game.as_ref().unwrap().frame_snapshot();
            let goal_events = self
                .game
                .as_ref()
                .unwrap()
                .events_for_goal(&self.selected_goal);
            let eligible: Vec<_> = self
                .content
                .events
                .iter()
                .enumerate()
                .filter(|(_, e)| {
                    snap.screen == GameScreen::QuickRace
                        || (e.league <= snap.career.league
                            && (self.selected_goal.is_empty() || goal_events.contains(&e.id)))
                })
                .map(|(i, _)| i)
                .collect();
            if !eligible.is_empty() {
                let index = eligible
                    .iter()
                    .position(|i| *i == self.selected_event)
                    .unwrap_or(0);
                self.selected_event = eligible[if key == "event_next" {
                    (index + 1) % eligible.len()
                } else {
                    (index + eligible.len() - 1) % eligible.len()
                }];
            }
            self.rebuild_menu();
            return;
        }
        if let Some(id) = key.strip_prefix("car:") {
            self.send(GameCommand::SelectCar { car_id: id.into() });
            self.previous_car.clear();
            return;
        }
        if let Some(index) = key.strip_prefix("event:") {
            self.selected_event = index.parse().unwrap_or(0);
            self.rebuild_menu();
            return;
        }
        if key == "wager" {
            if let Some(audio) = &mut self.audio {
                audio.say("bet");
            }
            self.wager = if self.wager >= 5000 {
                0
            } else {
                self.wager + 1000
            };
            self.rebuild_menu();
            return;
        }
        if key == "pink" {
            self.pink_slip = !self.pink_slip;
            self.rebuild_menu();
            return;
        }
        if let Some(item) = key.strip_prefix("cart_select:") {
            self.cart_selected = item.into();
            self.rebuild_menu();
            return;
        }
        if key == "cart_next" || key == "cart_prev" {
            self.cart_page = if key == "cart_next" {
                self.cart_page + 1
            } else {
                self.cart_page.saturating_sub(1)
            };
            self.rebuild_menu();
            return;
        }
        if let Some(page) = key.strip_prefix("custom_page:") {
            if ["paint", "wheels", "vinyl", "performance", "parts"].contains(&page) {
                self.custom_page = page.into();
                self.previous_car.clear();
                self.rebuild_menu();
            }
            return;
        }
        if let Some(tag) = key.strip_prefix("dna:") {
            self.selected_dna = tag.into();
            self.rebuild_menu();
            return;
        }
        if key == "vehicle_stats" || key == "stats_back" {
            self.show_stats = key == "vehicle_stats";
            self.rebuild_menu();
            return;
        }
        if key == "goals_select" {
            let game = self.game.as_ref().unwrap();
            let snap = game.snapshot();
            if let Some(status) = snap.league_progress.goals.get(self.goal_page) {
                let eligible = game.events_for_goal(&status.goal.id);
                if let Some(index) = self
                    .content
                    .events
                    .iter()
                    .position(|event| eligible.contains(&event.id))
                {
                    self.selected_goal = status.goal.id.clone();
                    self.selected_event = index;
                    self.show_goals = false;
                    self.event_picker = true;
                } else {
                    self.notice = if status.goal.qualifier && !snap.league_progress.promotion_open {
                        "Win this tier's circuit and drift events to open promotion".into()
                    } else {
                        "No matching events are available in this tier".into()
                    };
                }
            }
            self.rebuild_menu();
            return;
        }
        if let Some(index) = key.strip_prefix("goal_icon:") {
            self.goal_page = index.parse().unwrap_or(0);
            self.rebuild_menu();
            return;
        }
        if key == "career_goals"
            || key == "goals_back"
            || key == "goals_next"
            || key == "goals_prev"
        {
            if key == "career_goals" {
                self.show_goals = true;
                self.goal_page = self
                    .game
                    .as_ref()
                    .unwrap()
                    .snapshot()
                    .league_progress
                    .goals
                    .iter()
                    .position(|goal| !goal.goal.qualifier)
                    .unwrap_or(0);
            }
            if key == "goals_back" {
                self.show_goals = false;
            }
            if key == "goals_next" {
                let count = self
                    .game
                    .as_ref()
                    .unwrap()
                    .snapshot()
                    .league_progress
                    .goals
                    .len()
                    .max(1);
                self.goal_page = (self.goal_page + 1) % count;
            }
            if key == "goals_prev" {
                let count = self
                    .game
                    .as_ref()
                    .unwrap()
                    .snapshot()
                    .league_progress
                    .goals
                    .len()
                    .max(1);
                self.goal_page = (self.goal_page + count - 1) % count;
            }
            self.rebuild_menu();
            return;
        }
        if let Some(index) = key.strip_prefix("rival:") {
            self.selected_rival = index.parse().unwrap_or(1);
            self.rebuild_menu();
            return;
        }
        if key == "spectate" {
            if let Some(event) = self.content.events.get(self.selected_event) {
                self.send(GameCommand::StartSpectating {
                    event_id: event.id.clone(),
                });
            }
            return;
        }
        if key == "spectator_bet" {
            self.send(GameCommand::PlaceSpectatorBet {
                racer: self.selected_rival,
                amount: self.wager.max(1000),
            });
            self.persist();
            self.rebuild_menu();
            return;
        }
        if key == "cheer" || key == "boo" {
            self.send(GameCommand::SpectatorCheer {
                racer: self.selected_rival,
                positive: key == "cheer",
            });
            return;
        }
        if key == "grid_launch" {
            self.send(GameCommand::LaunchRace);
            return;
        }
        if key == "offer_cash" {
            self.send(GameCommand::OfferDriverBet {
                racer: self.selected_rival,
                amount: self.wager.max(1000),
            });
            self.rebuild_menu();
            return;
        }
        if key == "offer_pink" {
            self.confirmation = Some("pink_offer".into());
            self.rebuild_menu();
            return;
        }
        if key == "offer_accept" || key == "offer_decline" {
            self.send(if key == "offer_accept" {
                GameCommand::AcceptBetOffer
            } else {
                GameCommand::DeclineBetOffer
            });
            self.persist();
            self.rebuild_menu();
            return;
        }
        if key == "start" {
            if let Some(event) = self.content.events.get(self.selected_event) {
                let career =
                    self.game.as_ref().unwrap().frame_snapshot().screen == GameScreen::Career;
                self.send(GameCommand::StartRace {
                    event_id: event.id.clone(),
                    career,
                    wager: if career { 0 } else { self.wager },
                    pink_slip: !career && self.pink_slip,
                });
                if career && self.error_dialog.is_none() {
                    self.send(GameCommand::OpenGrid);
                }
            }
            return;
        }
        if key == "buy" || key == "sell" {
            self.confirmation = Some(key);
            self.rebuild_menu();
            return;
        }
        if key == "recruit" || key.starts_with("recruit:") {
            let snap = self.game.as_ref().unwrap().snapshot();
            let tag = key.strip_prefix("recruit:");
            if let Some(driver) = snap.drivers.iter().find(|d| {
                tag.map_or(!snap.career.crew.iter().any(|c| c.name == d.name), |tag| {
                    d.native_tag == tag
                })
            }) {
                self.send(GameCommand::Recruit {
                    driver: driver.clone(),
                });
            }
            self.rebuild_menu();
            return;
        }
        match key.as_str() {
            "resume" => self.send(GameCommand::Resume),
            "restart" => {
                self.send(GameCommand::Restart);
                self.persist();
            }
            "continue" => {
                self.send(GameCommand::Continue);
                self.persist();
            }
            _ => {}
        }
        if let Some(value) = key.strip_prefix("paint:") {
            self.customization.paint = match value {
                "blue" => [0.02, 0.22, 0.9, 1.],
                "green" => [0.1, 0.8, 0.18, 1.],
                "white" => [0.9, 0.9, 0.88, 1.],
                "black" => [0.02, 0.02, 0.025, 1.],
                "gold" => [0.95, 0.6, 0.03, 1.],
                _ => [0.8, 0.04, 0.025, 1.],
            };
            self.apply_custom();
        }
        if key == "paint_stage_accept" {
            self.advance_paint_stage();
            return;
        }
        if key == "paint_stage_cancel" {
            self.paint_stage_cancel();
            return;
        }
        if let Some(value) = key.strip_prefix("finish:") {
            let mut record = paint::donor_seed(&self.customization);
            let color = self.customization.paint;
            match paint::color(&mut record, value, 0, [color[0], color[1], color[2]]) {
                Ok(()) => {
                    self.paint_session = Some(paint::Session {
                        original: self.customization.clone(),
                        family: value.into(),
                        cursor: 0,
                    });
                    self.customization.finish = value.into();
                    self.customization.native_paint = Some(record);
                    self.reload_paint_preview();
                    self.palette_opened("body".into());
                }
                Err(error) => self.error_dialog = Some(error),
            }
        }
        if let Some(value) = key.strip_prefix("wheels:") {
            self.customization.wheels = value.into();
            self.apply_custom();
        }
        if let Some(value) = key.strip_prefix("part:") {
            if let Some((slot, id)) = value.split_once(':') {
                let selected = self.game.as_ref().unwrap().frame_snapshot().selected_car;
                if let Some(options) = self
                    .content
                    .cars
                    .iter()
                    .find(|car| car.id == selected)
                    .and_then(|car| car.parts.get(slot))
                {
                    if options.contains(&self.customization.body_kit) {
                        self.customization.body_kit = "stock".into();
                    }
                    if options.contains(&self.customization.interior_kit) {
                        self.customization.interior_kit = "stock".into();
                    }
                }
                self.customization.parts.insert(slot.into(), id.into());
                self.apply_custom();
            }
            return;
        }
        if let Some(value) = key.strip_prefix("kit:") {
            self.customization.body_kit = value.into();
            self.apply_custom();
        }
        if let Some(value) = key.strip_prefix("interior:") {
            self.customization.interior_kit = value.into();
            self.apply_custom();
        }
        if let Some(index) = key
            .strip_prefix("tune:")
            .and_then(|index| index.parse::<usize>().ok())
            .filter(|index| *index < 4)
        {
            self.customization.tuning[index] = if self.customization.tuning[index] >= 0.99 {
                -1.
            } else {
                (self.customization.tuning[index] + 0.2).min(1.)
            };
            self.apply_custom();
            return;
        }
        if let Some(value) = key.strip_prefix("upgrade:") {
            match value {
                "engine" => self.customization.engine = (self.customization.engine + 1) % 4,
                "transmission" => {
                    self.customization.transmission = (self.customization.transmission + 1) % 4
                }
                "suspension" => {
                    self.customization.suspension = (self.customization.suspension + 1) % 4
                }
                "tyres" => self.customization.tyres = (self.customization.tyres + 1) % 4,
                _ => return,
            };
            self.apply_custom();
        }
        if key == "vinyl:add" {
            if self.customization.vinyls.len() >= 16 {
                self.error_dialog = Some("Maximum 16 vinyl layers.".into());
                self.rebuild_menu();
                return;
            }
            let mut layer = Vinyl::default();
            layer.design_id = self.decal_catalog["categories"][self.decal_category]["design_ids"]
                [0]
            .as_str()
            .unwrap_or("")
            .into();
            self.customization.vinyls.push(layer);
            self.vinyl_layer = self.customization.vinyls.len() - 1;
            self.apply_custom();
        }
        if key == "vinyl:remove" {
            if !self.customization.vinyls.is_empty() {
                self.customization
                    .vinyls
                    .remove(self.vinyl_layer.min(self.customization.vinyls.len() - 1));
                self.vinyl_layer = self.vinyl_layer.saturating_sub(1);
            }
            self.apply_custom();
        }
        if key == "vinyl:next" && !self.customization.vinyls.is_empty() {
            self.vinyl_layer = (self.vinyl_layer + 1) % self.customization.vinyls.len();
            self.rebuild_menu();
            return;
        }
        if key == "vinyl:front" && self.vinyl_layer + 1 < self.customization.vinyls.len() {
            self.customization
                .vinyls
                .swap(self.vinyl_layer, self.vinyl_layer + 1);
            self.vinyl_layer += 1;
            self.apply_custom();
            return;
        }
        if key == "vinyl:back" && self.vinyl_layer > 0 {
            self.customization
                .vinyls
                .swap(self.vinyl_layer, self.vinyl_layer - 1);
            self.vinyl_layer -= 1;
            self.apply_custom();
            return;
        }
        if key.starts_with("vinyl:") && key != "vinyl:add" && key != "vinyl:remove" {
            if let Some(layer) = self.customization.vinyls.get_mut(self.vinyl_layer) {
                match key.as_str() {
                    "vinyl:color" => {
                        layer.color = if layer.color == [1., 1., 1., 1.] {
                            [1., 0.05, 0.02, 1.]
                        } else if layer.color[0] == 1. && layer.color[1] < 0.1 {
                            [0.02, 0.02, 0.02, 1.]
                        } else {
                            [1., 1., 1., 1.]
                        }
                    }
                    "vinyl:left" => layer.position[0] -= 0.1,
                    "vinyl:right" => layer.position[0] += 0.1,
                    "vinyl:up" => layer.position[1] -= 0.1,
                    "vinyl:down" => layer.position[1] += 0.1,
                    "vinyl:rotate" => layer.rotation += 0.25,
                    "vinyl:rotate_back" => layer.rotation -= 0.25,
                    "vinyl:scale_x_up" => layer.scale[0] += 0.1,
                    "vinyl:scale_x_down" => layer.scale[0] = (layer.scale[0] - 0.1).max(0.01),
                    "vinyl:scale_y_up" => layer.scale[1] += 0.1,
                    "vinyl:scale_y_down" => layer.scale[1] = (layer.scale[1] - 0.1).max(0.01),
                    "vinyl:scale" => {
                        layer.scale[0] += 0.1;
                        layer.scale[1] += 0.1;
                    }
                    "vinyl:shape" => {
                        layer.shape = if layer.shape == "stripe" {
                            "flame".into()
                        } else {
                            "stripe".into()
                        }
                    }
                    _ => {}
                }
            }
            self.apply_custom();
        }
    }
}

impl OversteerApp {
    fn next_movie(&mut self) {
        if let Some(player) = &mut self.video_player {
            player.stop();
        }
        if self.video_queue.is_empty() {
            self.video_active = false;
            if let Some(panel) = &mut self.video_panel {
                panel.set_visible(false);
            }
            if let Some(audio) = &mut self.audio {
                audio.set_cinematic(false);
            }
            return;
        }
        let id = self.video_queue.remove(0);
        let path = format!("res://assets/video/{id}.ogv");
        if let Some(stream) = ResourceLoader::singleton()
            .load(&path)
            .and_then(|r| r.try_cast::<godot::classes::VideoStream>().ok())
        {
            if let Some(player) = &mut self.video_player {
                player.set_stream(&stream);
                player.play();
            }
            if let Some(panel) = &mut self.video_panel {
                panel.set_visible(true);
            }
            self.video_active = true;
            if let Some(audio) = &mut self.audio {
                audio.set_cinematic(true);
            }
        } else {
            godot_error!("Original movie unavailable: {}", path);
            self.video_active = false;
        }
    }
    fn begin_loading(&mut self, paths: Vec<String>, target: String) {
        match loading::SceneLoad::new(paths) {
            Ok(job) => {
                self.loading = Some(job);
                self.load_target = target;
                if let Some(panel) = &mut self.loading_layer {
                    panel.set_visible(true);
                }
            }
            Err(error) => {
                godot_error!("{}", error);
                self.error_dialog = Some("Game data could not be loaded.".into());
                self.previous_screen.clear();
                if !self.scenario.is_empty() {
                    self.base().get_tree().quit_ex().exit_code(1).done();
                }
            }
        }
    }
    fn poll_loading(&mut self) -> bool {
        let Some(job) = &mut self.loading else {
            return true;
        };
        let status = job.poll();
        match status {
            Ok((progress, false)) => {
                if let Some(label) = &mut self.loading_label {
                    label.set_text(&format!("LOADING... {:.0}%", progress * 100.));
                }
                if self.scenario == "loading"
                    && progress > 0.2
                    && !self.capture_dir.is_empty()
                    && !std::path::Path::new(&format!("{}/loading.png", self.capture_dir)).exists()
                {
                    self.capture("loading");
                }
                false
            }
            Ok((_, true)) => {
                let (resources, report) = self.loading.take().unwrap().finish();
                self.preload_resources = resources;
                self.loading_reports.push(report);
                let target = std::mem::take(&mut self.load_target);
                if target == "showroom" {
                    let mut paint = Self::load_scene("res://assets/worlds/paintbooth.glb");
                    paint.set_position(Vector3::new(30., 1.640575715, -30.));
                    paint.set_visible(false);
                    self.base_mut().add_child(&paint);
                    self.paint_stage = Some(paint);
                    let mut tunnel = Self::load_scene("res://assets/worlds/tunnel_tunnel.glb");
                    tunnel.set_position(Vector3::new(-36.74981, -1.566545, -2.374297));
                    prepare_tunnel(&mut tunnel);
                    if let Some(main) = &mut self.main_stage {
                        main.add_child(&tunnel);
                    }
                } else if let Some(key) = target.strip_prefix("race:") {
                    self.loaded_race = key.to_owned();
                }
                if let Some(panel) = &mut self.loading_layer {
                    panel.set_visible(false);
                }
                self.previous_screen.clear();
                true
            }
            Err(error) => {
                godot_error!("{}", error);
                self.loading = None;
                if let Some(panel) = &mut self.loading_layer {
                    panel.set_visible(false);
                }
                self.error_dialog = Some("Game data could not be loaded.".into());
                self.previous_screen.clear();
                if !self.scenario.is_empty() {
                    self.base().get_tree().quit_ex().exit_code(1).done();
                }
                true
            }
        }
    }
    fn save_path(&self) -> String {
        if !self.save_override.is_empty() {
            return self.save_override.clone();
        }
        ProjectSettings::singleton()
            .globalize_path(if self.scenario.is_empty() {
                "user://career.json"
            } else {
                "user://scenario-career.json"
            })
            .to_string()
    }
    fn load_career(&mut self) {
        let path = self.save_path();
        match persistence::load(self.content.clone(), std::path::Path::new(&path)) {
            Ok(loaded) => {
                self.save_blocked = false;
                self.io_retry.clear();
                self.load_status = serde_json::json!({"ok":true,"source":loaded.source,"preserved":loaded.preserved.as_ref().map(|p|p.display().to_string()),"path":path,"recovered_race":loaded.game.recovered_race()});
                self.game = Some(loaded.game);
                if loaded.source == "backup" {
                    self.error_dialog = Some(
                        "A backup career was restored. The damaged save has been retained.".into(),
                    );
                    self.title = false;
                }
            }
            Err(error) => {
                godot_error!("Career load failed: {}", error);
                self.load_status = serde_json::json!({"ok":false,"error":error,"path":path});
                self.game = Some(Game::new(self.content.clone()));
                self.save_blocked = true;
                self.io_retry = "load".into();
                self.error_dialog=Some("Your career could not be loaded. The existing save has been retained. Retry loading or start a new career.".into());
                self.title = false;
            }
        }
    }
    fn persist(&mut self) -> bool {
        if self.save_blocked {
            self.save_status = serde_json::json!({"ok":false,"error":"Unrecovered career is protected","path":self.save_path()});
            return false;
        }
        let Some(game) = &self.game else { return false };
        let path = self.save_path();
        match persistence::save(game, std::path::Path::new(&path)) {
            Ok(()) => {
                self.save_status = serde_json::json!({"ok":true,"path":path});
                if self.io_retry == "save" {
                    self.error_dialog = None;
                    self.io_retry.clear();
                }
                true
            }
            Err(error) => {
                godot_error!("Career save failed: {}", error);
                self.save_status = serde_json::json!({"ok":false,"error":error,"path":path});
                self.io_retry = "save".into();
                self.error_dialog = Some(
                    "Your career could not be saved. Check the save location and retry.".into(),
                );
                self.previous_screen.clear();
                false
            }
        }
    }
    fn replay_native_inputs(&mut self) {
        if self.input_event_path.is_empty() {
            return;
        }
        let snap = self.game.as_ref().unwrap().frame_snapshot();
        if snap.screen != GameScreen::Race {
            return;
        }
        if snap.race.as_ref().is_some_and(|race| race.countdown <= 0.) {
            self.input_frame += 1;
        }
        // Only frame0 events are eligible during countdown; later events retain
        // their active-frame clock and are polled one frame after queueing.

        while let Some(event) = self
            .input_events
            .get(self.input_event_index)
            .filter(|event| event["frame"].as_u64().unwrap_or(0) <= self.input_frame)
        {
            if !self.queue_binding_input(event, event["pressed"].as_bool().unwrap_or(true)) {
                godot_error!("Invalid native input event{}", self.input_event_index);
                self.base().get_tree().quit_ex().exit_code(1).done();
                return;
            }
            self.input_event_index += 1;
        }
    }
    fn record_native_inputs(&mut self, dt: f64, controls: PlayerInput) {
        if self.input_event_path.is_empty() {
            return;
        }
        let snap = self.game.as_ref().unwrap().frame_snapshot();
        if let Some(player) = snap
            .race
            .as_ref()
            .and_then(|race| race.racers.iter().find(|racer| racer.is_player))
        {
            if self.input_frame == 0 {
                // Last pre-active post-tick state, used for the first observed
                // recharge delta; countdown controls still have no effect.
                self.input_nitrous_initial = Some(player.nitrous);
                return;
            }
            let right = self
                .camera
                .as_ref()
                .map(|camera| camera.get_global_transform().basis * Vector3::RIGHT)
                .unwrap_or(Vector3::ZERO);
            let input = Input::singleton();
            self.input_samples.push(serde_json::json!({"frame":self.input_frame,"process_frame":self.scenario_frame,"delta":dt,"position":player.position,"rotation":player.rotation,"speed_kph":player.speed_kph,"camera_right":[right.x,right.y,right.z],"nitrous":{"active":player.nitrous_active,"fraction":player.nitrous,"pressure_band":player.nitrous_pressure_band},"controls":controls,"physical_keys":{"throttle":input.is_physical_key_pressed(self.bindings["throttle"]),"left":input.is_physical_key_pressed(self.bindings["left"]),"right":input.is_physical_key_pressed(self.bindings["right"])},"raw_joy_steering":if self.virtual_joy_replay{Some(input.get_joy_axis(0,godot::global::JoyAxis::from_ord(self.joy_axes["steering"])))}else{None}}));
            if self.wheel_audit {
                let audit = serde_json::json!({
                    "angle_degrees": (self.input_frame.saturating_sub(1) / 30).min(11) * 30,
                    "wheel_angles": player.wheel_angles, "wheel_omega": player.wheel_omega,
                    "wheel_steer_angles": player.wheel_steer_angles,
                    "contacts": player.surface_contacts, "velocity": player.velocity,
                    "wheel_radius": self.content.cars.iter().find(|car| car.id == player.car_id).map(|car| car.handling.wheel_radius),
                    "rendered_wheels": if matches!(self.input_frame % 30, 15 | 16) {
                        self.cars.first().map(|car| wheel_visual_samples(car, player))
                    } else { None },
                });
                self.input_samples.last_mut().unwrap()["wheel_audit"] = audit;
            }
        }
    }
    fn league_label(&self, league: u8) -> String {
        self.content
            .leagues
            .iter()
            .find(|definition| definition.league == league)
            .map(|definition| definition.name.clone())
            .unwrap_or_else(|| "Career".into())
    }
    fn settings_path(&self, file: &str) -> std::path::PathBuf {
        if self.settings_dir.is_empty() {
            std::path::PathBuf::from(
                ProjectSettings::singleton()
                    .globalize_path(&format!("user://{file}"))
                    .to_string(),
            )
        } else {
            std::path::Path::new(&self.settings_dir).join(file)
        }
    }
    fn load_settings(&mut self) -> bool {
        let path = self.settings_path("options.json");
        let result = (|| -> Result<serde_json::Value, String> {
            if let Some(value) = persistence::load_preferences(&path)? {
                if value["schema"].as_u64() != Some(1) {
                    return Err("Unsupported options schema".into());
                }
                return Ok(value);
            }
            let read = |file: &str| -> Result<serde_json::Value, String> {
                Ok(persistence::load_preferences(&self.settings_path(file))?.unwrap_or_default())
            };
            Ok(
                serde_json::json!({"schema":1,"keyboard":read("settings.json")?,"controller":read("controller.json")?,"presentation":read("presentation.json")?,"audio":read("audio.json")?}),
            )
        })();
        match result {
            Ok(value) => {
                if let Ok(bindings) =
                    serde_json::from_value::<BTreeMap<String, i32>>(value["keyboard"].clone())
                {
                    for (action, ordinal) in bindings {
                        if self.bindings.contains_key(&action)
                            && let Some(key) = Key::try_from_ord(ordinal)
                        {
                            self.bindings.insert(action, key);
                        }
                    }
                }
                if let Ok(axes) = serde_json::from_value::<BTreeMap<String, i32>>(
                    value["controller"]["axes"].clone(),
                ) {
                    self.joy_axes.extend(axes);
                }
                if let Ok(buttons) = serde_json::from_value::<BTreeMap<String, i32>>(
                    value["controller"]["buttons"].clone(),
                ) {
                    self.joy_buttons.extend(buttons);
                }
                self.speed_mph = value["presentation"]["mph"].as_bool().unwrap_or(true);
                self.render_quality = value["presentation"]["quality"]
                    .as_u64()
                    .unwrap_or(1)
                    .min(2) as u8;
                if let Some(level) = value["presentation"]["difficulty"].as_u64() {
                    self.send(GameCommand::SetDifficulty {
                        level: level.min(2) as u8,
                    });
                }
                self.audio_options = value["audio"].clone();
                if let Some(audio) = &mut self.audio {
                    audio.apply_options(&self.audio_options);
                }
                self.settings_blocked = false;
                self.settings_status =
                    serde_json::json!({"ok":true,"operation":"load","path":path,"values":value});
                if self.io_retry.starts_with("settings_") {
                    self.io_retry.clear();
                    self.error_dialog = None;
                }
                true
            }
            Err(error) => {
                self.settings_blocked = true;
                self.settings_status =
                    serde_json::json!({"ok":false,"operation":"load","path":path,"error":error});
                self.io_retry = "settings_load".into();
                self.error_dialog=Some("Options could not be loaded. Existing files are retained. Retry loading options.".into());
                false
            }
        }
    }
    fn save_settings(&mut self) -> bool {
        if self.settings_blocked {
            self.io_retry = "settings_load".into();
            self.error_dialog =
                Some("Options must be recovered before changes can be saved.".into());
            return false;
        }
        let keyboard: BTreeMap<_, _> = self
            .bindings
            .iter()
            .map(|(action, key)| (action.clone(), key.ord()))
            .collect();
        let value = serde_json::json!({"schema":1,"keyboard":keyboard,"controller":{"axes":self.joy_axes,"buttons":self.joy_buttons},"presentation":{"mph":self.speed_mph,"quality":self.render_quality,"difficulty":self.game.as_ref().unwrap().frame_snapshot().difficulty},"audio":self.audio.as_ref().map(audio::RuntimeAudio::options).unwrap_or(self.audio_options.clone())});
        let path = self.settings_path("options.json");
        match persistence::save_preferences(&path, &value) {
            Ok(()) => {
                self.settings_status =
                    serde_json::json!({"ok":true,"operation":"save","path":path,"values":value});
                if self.io_retry == "settings_save" {
                    self.io_retry.clear();
                    self.error_dialog = None;
                }
                true
            }
            Err(error) => {
                godot_error!("Options save failed: {}", error);
                self.settings_status =
                    serde_json::json!({"ok":false,"operation":"save","path":path,"error":error});
                self.io_retry = "settings_save".into();
                self.error_dialog = Some(
                    "Options could not be saved. Check the options location and retry.".into(),
                );
                false
            }
        }
    }
    fn apply_render_quality(&mut self) {
        if let Some(mut viewport) = self.base().get_viewport() {
            viewport.set_msaa_3d(match self.render_quality {
                0 => godot::classes::viewport::Msaa::DISABLED,
                2 => godot::classes::viewport::Msaa::MSAA_4X,
                _ => godot::classes::viewport::Msaa::MSAA_2X,
            });
        }
        if let Some(sun) = &mut self.sun {
            sun.set_shadow(self.render_quality > 0);
        }
        if let Some(environment) = &mut self.environment {
            environment.set_ssao_enabled(self.render_quality == 2);
        }
    }
    fn ui_substate(&self) -> serde_json::Value {
        let snap = self.game.as_ref().unwrap().frame_snapshot();
        serde_json::json!({"title":self.title,"extras":self.extras,"avatar_profile":snap.profile,"avatar_components":self.avatar_report,"event_picker":self.event_picker,"goals":self.show_goals,"vehicle_stats":self.show_stats,"selected_dna":self.selected_dna,"customization_page":self.custom_page,"cart_page":self.cart_page,"cart_selected":self.cart_selected,"palette":self.palette_target,"paint_translation":paint::provenance(),"paint_draft":self.paint_session.as_ref().map(|_|self.customization.clone()),"paint_stage":self.paint_session.as_ref().map(|session|serde_json::json!({"family":session.family,"cursor":session.cursor,"stage":format!("{:?}",session.stage())})),"palette_preview":self.palette_control.as_ref().map(|palette|{let c=palette.bind().color();[c.r,c.g,c.b,c.a]}),"goal_page":self.goal_page,"selected_goal":self.selected_goal,"options":self.options,"confirmation":self.confirmation,"error":self.error_dialog,"selected_event":self.content.events.get(self.selected_event).map(|event|&event.id),"selected_car":snap.selected_car,"selected_rival":self.selected_rival,"cart":snap.cart,"customization":snap.selected_customization,"cash":snap.career.cash,"settings":self.settings_status,"render_quality":self.render_quality,"difficulty":snap.difficulty,"offer":snap.race.as_ref().and_then(|race|race.bet_offer.as_ref()),"spectating":snap.race.as_ref().is_some_and(|race|race.spectating)})
    }
    fn queue_binding_input(&self, step: &serde_json::Value, pressed: bool) -> bool {
        let mut input = Input::singleton();
        if let Some(code) = step["key_code"]
            .as_i64()
            .and_then(|code| Key::try_from_ord(code as i32))
        {
            let mut event = InputEventKey::new_gd();
            event.set_keycode(code);
            event.set_physical_keycode(code);
            event.set_pressed(pressed);
            input.call_deferred("parse_input_event", &[event.to_variant()]);
            return true;
        }
        if let Some(button) = step["joy_button"]
            .as_i64()
            .and_then(|code| godot::global::JoyButton::try_from_ord(code as i32))
        {
            let mut event = godot::classes::InputEventJoypadButton::new_gd();
            event.set_button_index(button);
            event.set_pressed(pressed);
            input.call_deferred("parse_input_event", &[event.to_variant()]);
            return true;
        }
        if let Some(axis) = step["joy_axis"]["axis"]
            .as_i64()
            .and_then(|code| godot::global::JoyAxis::try_from_ord(code as i32))
        {
            let mut event = godot::classes::InputEventJoypadMotion::new_gd();
            event.set_axis(axis);
            event.set_axis_value(if pressed {
                step["joy_axis"]["value"].as_f64().unwrap_or(0.8) as f32
            } else {
                0.
            });
            input.call_deferred("parse_input_event", &[event.to_variant()]);
            return true;
        }
        false
    }
    fn advance_ui_actions(&mut self) {
        if self.ui_pending {
            if self.ui_palette_phase < 2
                && self
                    .queue_binding_input(&self.ui_steps[self.ui_step], self.ui_palette_phase == 0)
            {
                self.ui_palette_phase += 1;
                return;
            }
            if let Some(values) = self.ui_steps[self.ui_step]["color"]
                .as_array()
                .filter(|values| values.len() == 4 && self.ui_palette_phase < 3)
                && let Some(palette) = &self.palette_control
            {
                if self.ui_palette_phase == 0 {
                    let picker = palette.bind().picker();
                    if let Some(mut picker) = picker {
                        if !picker.is_visible() {
                            for child in palette.get_children().iter_shared() {
                                if let Ok(mut button) = child.try_cast::<Button>()
                                    && button.has_meta("ui_action")
                                    && button.get_meta("ui_action").to::<String>()
                                        == "palette_precision"
                                {
                                    button.call_deferred("emit_signal", &["pressed".to_variant()]);
                                    return;
                                }
                            }
                        }
                        let color = Color::from_rgba(
                            values[0].as_f64().unwrap_or(1.) as f32,
                            values[1].as_f64().unwrap_or(1.) as f32,
                            values[2].as_f64().unwrap_or(1.) as f32,
                            values[3].as_f64().unwrap_or(1.) as f32,
                        );
                        picker.call_deferred("set_pick_color", &[color.to_variant()]);
                        picker.call_deferred(
                            "emit_signal",
                            &["color_changed".to_variant(), color.to_variant()],
                        );
                        self.ui_palette_phase = 1;
                        return;
                    }
                }
                if self.ui_palette_phase == 1
                    && self.ui_steps[self.ui_step]["close_palette"]
                        .as_bool()
                        .unwrap_or(true)
                {
                    for child in palette.get_children().iter_shared() {
                        if let Ok(mut button) = child.try_cast::<Button>()
                            && button.has_meta("ui_action")
                            && button.get_meta("ui_action").to::<String>() == "palette_accept"
                        {
                            button.call_deferred("emit_signal", &["pressed".to_variant()]);
                            self.ui_palette_phase = 2;
                            return;
                        }
                    }
                }
            }
            self.ui_palette_phase = 3;
            if self.ui_steps[self.ui_step]["capture"].is_string() {
                let delay = self.ui_steps[self.ui_step]["capture_after_frames"]
                    .as_u64()
                    .unwrap_or(3)
                    .max(3);
                let until = *self
                    .ui_capture_wait
                    .get_or_insert(self.scenario_frame + delay);
                if self.scenario_frame < until {
                    return;
                }
            }
            self.ui_capture_wait = None;
            self.ui_palette_phase = 0;
            self.ui_pending = false;
            let screen = format!("{:?}", self.game.as_ref().unwrap().frame_snapshot().screen);
            let substate = self.ui_substate();
            let bounds = self.menu.as_ref().map(control_bounds);
            if let Some(entry) = self.ui_action_log.last_mut() {
                entry["screen_after"] = screen.into();
                entry["substate_after"] = substate;
                entry["capture_frame"] = self.scenario_frame.into();
                entry["capture_substate"] = entry["substate_after"].clone();
                if !self.ui_steps[self.ui_step]["key_code"].is_null()
                    || !self.ui_steps[self.ui_step]["joy_button"].is_null()
                    || !self.ui_steps[self.ui_step]["joy_axis"].is_null()
                {
                    entry["input_control"] = serde_json::json!({"via":"Input.parse_input_event press/release","key_code":self.ui_steps[self.ui_step]["key_code"],"joy_button":self.ui_steps[self.ui_step]["joy_button"],"joy_axis":self.ui_steps[self.ui_step]["joy_axis"]});
                }
                entry["capture_native_ui_bounds"] = serde_json::json!(bounds);
                if self.ui_steps[self.ui_step]["color"].is_array() {
                    entry["color_control"] = serde_json::json!({"rgba":self.ui_steps[self.ui_step]["color"],"via":"palette_precision Button.pressed → ColorPicker.color_changed → NativePalette.color_changed","closed":self.ui_steps[self.ui_step]["close_palette"].as_bool().unwrap_or(true)});
                }
            }
            if let Some(name) = self.ui_steps[self.ui_step]["capture"].as_str() {
                self.capture(name);
            }
            self.ui_step += 1;
            if !self.capture_dir.is_empty() {
                let _ = std::fs::create_dir_all(&self.capture_dir);
                let _ = std::fs::write(
                    format!("{}/ui-actions.json", self.capture_dir),
                    serde_json::to_string_pretty(&self.ui_action_log).unwrap(),
                );
            }
        }
        let Some(step) = self.ui_steps.get(self.ui_step) else {
            return;
        };
        if self.scenario_frame < step["after_frame"].as_u64().unwrap_or(0) {
            return;
        }
        let Some(action) = step["action"].as_str() else {
            return;
        };
        let since = self
            .ui_action_log
            .last()
            .and_then(|v| v["frame"].as_u64())
            .unwrap_or(0)
            .max(step["after_frame"].as_u64().unwrap_or(0));
        if self.scenario_frame > since + step["timeout_frames"].as_u64().unwrap_or(600) {
            godot_error!("UI action unavailable: {} at step {}", action, self.ui_step);
            if !self.capture_dir.is_empty() {
                let _ = std::fs::create_dir_all(&self.capture_dir);
                let _ = std::fs::write(format!("{}/ui-action-error.json", self.capture_dir), serde_json::json!({"action":action,"step":self.ui_step,"screen":format!("{:?}",self.game.as_ref().unwrap().frame_snapshot().screen)}).to_string());
            }
            self.ui_steps.clear();
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        let Some(menu) = &self.menu else { return };
        let mut controls = menu.get_children().iter_shared().collect::<Vec<_>>();
        if let Some(panel) = &self.paint_scalar_panel {
            controls.extend(panel.get_children().iter_shared());
        }
        if let Some(palette) = &self.palette_control {
            if let Some(index) = action
                .strip_prefix("palette_cell:")
                .and_then(|index| index.parse().ok())
            {
                if let Some(button) = palette.bind().cell_button(index) {
                    controls.push(button.upcast());
                }
            } else {
                controls.extend(palette.get_children().iter_shared());
            }
        }
        for child in controls {
            if let Ok(mut edit) = child.clone().try_cast::<godot::classes::LineEdit>()
                && edit.is_visible_in_tree()
                && edit.has_meta("ui_action")
                && edit.get_meta("ui_action").to::<String>() == action
                && let Some(text) = step["text"].as_str()
            {
                self.ui_action_log.push(serde_json::json!({"action":action,"text":text,"frame":self.scenario_frame,"screen_before":format!("{:?}",self.game.as_ref().unwrap().frame_snapshot().screen),"via":"visible-LineEdit.text_changed","substate_before":self.ui_substate()}));
                edit.call_deferred("set_text", &[text.to_variant()]);
                edit.call_deferred(
                    "emit_signal",
                    &["text_changed".to_variant(), text.to_variant()],
                );
                self.ui_pending = true;
                return;
            }
            if let Ok(mut slider) = child.clone().try_cast::<godot::classes::HSlider>()
                && slider.is_visible_in_tree()
                && slider.has_meta("ui_action")
                && slider.get_meta("ui_action").to::<String>() == action
            {
                let Some(value) = step["value"].as_f64() else {
                    return;
                };
                self.ui_action_log.push(serde_json::json!({"action":action,"value":value,"frame":self.scenario_frame,"screen_before":format!("{:?}",self.game.as_ref().unwrap().frame_snapshot().screen),"via":"visible-HSlider.value_changed","substate_before":self.ui_substate()}));
                slider.call_deferred("set_value_no_signal", &[value.to_variant()]);
                slider.call_deferred(
                    "emit_signal",
                    &["value_changed".to_variant(), value.to_variant()],
                );
                self.ui_pending = true;
                return;
            }
            if let Ok(mut button) = child.try_cast::<Button>() {
                if !button.is_visible_in_tree()
                    || button.is_disabled()
                    || !button.has_meta("ui_action")
                {
                    continue;
                }
                if button.get_meta("ui_action").to::<String>() == action {
                    self.ui_action_log.push(serde_json::json!({"action":action,"frame":self.scenario_frame,"screen_before":format!("{:?}",self.game.as_ref().unwrap().frame_snapshot().screen),"via":"visible-enabled-Button.pressed","substate_before":self.ui_substate()}));
                    button.call_deferred("emit_signal", &["pressed".to_variant()]);
                    self.ui_pending = true;
                    return;
                }
            }
        }
    }
    fn send(&mut self, command: GameCommand) {
        if let Some(game) = &mut self.game {
            let before = game.frame_snapshot();
            let mut record = serde_json::json!({"frame":self.scenario_frame,"input_frame":self.input_frame,
                "command":command,"screen_before":before.screen,"cash_before":before.career.cash});
            let result = game.command(command);
            let after = game.frame_snapshot();
            record["screen_after"] = serde_json::json!(after.screen);
            record["cash_after"] = serde_json::json!(after.career.cash);
            record["error"] = serde_json::json!(result.as_ref().err());
            self.command_history.push_back(record);
            if self.command_history.len() > 128 {
                self.command_history.pop_front();
            }
            if let Err(error) = result {
                self.notice = error.clone();
                self.error_dialog = Some(error);
                self.previous_screen.clear();
            }
        }
    }
    fn apply_custom(&mut self) {
        let id = self.game.as_ref().unwrap().frame_snapshot().selected_car;
        self.send(GameCommand::Customize {
            car_id: id.clone(),
            customization: self.customization.clone(),
        });
        self.previous_car.clear();
        self.persist();
        self.rebuild_menu();
    }
    fn setup_world(&mut self) {
        let mut camera = Camera3D::new_alloc();
        camera.set_position(Vector3::new(9., 5., 10.));
        camera.set_fov(62.);
        camera.set_far(1800.);
        self.base_mut().add_child(&camera);
        camera.look_at(Vector3::new(0., 0.8, 0.));
        camera.make_current();
        self.camera = Some(camera);
        let mut sun = DirectionalLight3D::new_alloc();
        sun.set_rotation_degrees(Vector3::new(-27., -45., 0.));
        sun.set_color(Color::from_rgb(1., 0.9, 0.79));
        sun.set_param(godot::classes::light_3d::Param::ENERGY, 0.9);
        sun.set_shadow(true);
        self.base_mut().add_child(&sun);
        self.sun = Some(sun);
        let mut env = Environment::new_gd();
        // A coherent late-afternoon sky provides both background and specular radiance.
        let mut sky_material = godot::classes::ProceduralSkyMaterial::new_gd();
        sky_material.set_sky_top_color(Color::from_rgb(0.2, 0.31, 0.48));
        sky_material.set_sky_horizon_color(Color::from_rgb(0.65, 0.61, 0.56));
        sky_material.set_ground_bottom_color(Color::from_rgb(0.035, 0.04, 0.065));
        sky_material.set_ground_horizon_color(Color::from_rgb(0.24, 0.23, 0.28));
        sky_material.set_energy_multiplier(1.0);
        let mut sky = godot::classes::Sky::new_gd();
        sky.set_material(&sky_material);
        env.set_sky(&sky);
        env.set_reflection_source(godot::classes::environment::ReflectionSource::SKY);
        env.set_background(godot::classes::environment::BgMode::SKY);
        env.set_bg_color(Color::from_rgb(0.015, 0.018, 0.035));
        env.set_ambient_source(godot::classes::environment::AmbientSource::COLOR);
        env.set_ambient_light_color(Color::from_rgb(0.45, 0.53, 0.7));
        env.set_ambient_light_energy(0.8);
        env.set_tonemapper(godot::classes::environment::ToneMapper::FILMIC);
        let mut world = WorldEnvironment::new_alloc();
        world.set_environment(&env);
        self.environment = Some(env);
        self.base_mut().add_child(&world);
        let mut scene = Node3D::new_alloc();
        scene.set_name("RaceWorld");
        self.base_mut().add_child(&scene);
        self.scene = Some(scene);
        let mut stage = Node3D::new_alloc();
        stage.set_name("Showroom");
        self.base_mut().add_child(&stage);
        Self::box_mesh(
            &mut stage,
            "Concrete floor",
            Vector3::new(0., -0.1, 0.),
            Vector3::new(30., 0.2, 30.),
            Color::from_rgb(0.16, 0.18, 0.20),
        );
        for z in [-12., 12.] {
            Self::box_mesh(
                &mut stage,
                "Workshop wall",
                Vector3::new(0., 5., z),
                Vector3::new(40., 10., 0.2),
                Color::from_rgb(0.22, 0.25, 0.28),
            );
            for x in [-6., 0., 6.] {
                Self::box_mesh(
                    &mut stage,
                    "Door frame",
                    Vector3::new(x, 2., z - z.signum() * 0.16),
                    Vector3::new(4.9, 4.1, 0.12),
                    Color::from_rgb(0.06, 0.075, 0.09),
                );
                for row in 0..8 {
                    Self::box_mesh(
                        &mut stage,
                        "Roller door slat",
                        Vector3::new(x, 0.3 + row as f32 * 0.48, z - z.signum() * 0.24),
                        Vector3::new(4.6, 0.44, 0.08),
                        Color::from_rgb(0.19, 0.22, 0.24),
                    );
                }
            }
        }

        for (x, z, color) in [
            (-4., -3., Color::from_rgb(0.86, 0.93, 1.)),
            (4., 3., Color::from_rgb(1., 0.94, 0.86)),
        ] {
            let mut light = godot::classes::OmniLight3D::new_alloc();
            light.set_position(Vector3::new(x, 4.5, z));
            light.set_shadow(true);
            light.set_color(color);
            light.set_param(godot::classes::light_3d::Param::ENERGY, 5.);
            light.set_param(godot::classes::light_3d::Param::RANGE, 15.);
            stage.add_child(&light);
        }
        self.stage = Some(stage);
        let mut main = Node3D::new_alloc();
        main.set_name("OriginalMainMenuTunnel");
        self.base_mut().add_child(&main);
        for (x, z) in [(-4., 2.), (4., -2.)] {
            let mut light = godot::classes::OmniLight3D::new_alloc();
            light.set_position(Vector3::new(x, 2., z));
            light.set_color(Color::from_rgb(0.9, 0.05, 0.45));
            light.set_param(godot::classes::light_3d::Param::ENERGY, 5.);
            light.set_param(godot::classes::light_3d::Param::RANGE, 25.);
            main.add_child(&light);
        }
        self.main_stage = Some(main);
    }
    fn box_mesh(
        parent: &mut Gd<Node3D>,
        name: &str,
        pos: Vector3,
        size: Vector3,
        color: Color,
    ) -> Gd<MeshInstance3D> {
        let mut mesh = BoxMesh::new_gd();
        mesh.set_size(size);
        let mut mat = StandardMaterial3D::new_gd();
        mat.set_albedo(color);
        mat.set_roughness(0.8);
        let mut node = MeshInstance3D::new_alloc();
        node.set_name(name);
        node.set_mesh(&mesh);
        node.set_material_override(&mat);
        node.set_position(pos);
        parent.add_child(&node);
        node
    }
    fn build_track(&mut self, index: usize) {
        if let Some(scene) = &mut self.scene {
            for mut child in scene.get_children().iter_shared() {
                child.queue_free();
            }
        }
        let Some(track) = self.content.tracks.get(index).cloned() else {
            return;
        };
        let scene = self.scene.as_mut().unwrap();
        let route_path = format!("res://assets/worlds/{}.glb", track.id);
        let metadata: serde_json::Value = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/tracks.json").to_string(),
        )
        .unwrap_or_default();
        if let Some(entry) = metadata["tracks"]
            .as_array()
            .and_then(|tracks| tracks.iter().find(|t| t["id"].as_str() == Some(&track.id)))
        {
            let city = entry["city"]
                .as_str()
                .unwrap_or("")
                .to_lowercase()
                .replace(' ', "_");
            let path = if ResourceLoader::singleton().exists(&route_path) {
                route_path.clone()
            } else {
                format!("res://assets/worlds/{city}.glb")
            };
            if ResourceLoader::singleton().exists(&path) {
                let mut native = Self::load_scene(&path);
                prepare_layered_world(&mut native, &path);
                let origin = &entry["source"]["origin_source_units"];
                native.set_position(Vector3::new(
                    -origin[0].as_f64().unwrap_or(0.) as f32 * 0.01,
                    -origin[1].as_f64().unwrap_or(0.) as f32 * 0.01,
                    -origin[2].as_f64().unwrap_or(0.) as f32 * 0.01,
                ));
                native.set_name("NativeReferenceWorld");
                scene.add_child(&native);
                return;
            }
        }
        Self::box_mesh(
            scene,
            "Terrain",
            Vector3::new(100., -0.7, 100.),
            Vector3::new(6000., 1., 6000.),
            Color::from_rgb(0.10, 0.115, 0.11),
        );
        let mut surface = godot::classes::SurfaceTool::new_gd();
        surface.begin(godot::classes::mesh::PrimitiveType::TRIANGLES);
        for i in 0..track.points.len() {
            let a = v3(track.points[i]);
            let b = v3(track.points[(i + 1) % track.points.len()]);
            let delta = b - a;
            let side = Vector3::new(delta.z, 0., -delta.x).normalized();
            let color = Color::from_rgb(0.16, 0.165, 0.175);
            let corners = [
                a - side * track.road_width * 0.5,
                b - side * track.road_width * 0.5,
                b + side * track.road_width * 0.5,
                a + side * track.road_width * 0.5,
            ];
            for n in [0, 2, 1, 0, 3, 2] {
                surface.set_color(color);
                surface.add_vertex(corners[n]);
            }
            for sign in [-1., 1.] {
                let center = (a + b) * 0.5
                    + side * (track.road_width * 0.5 + 0.35) * sign
                    + Vector3::UP * 0.55;
                let basis = Basis::from_axis_angle(Vector3::UP, delta.x.atan2(delta.z));
                append_box(
                    &mut surface,
                    center,
                    Vector3::new(0.7, 1.1, delta.length() + 0.1),
                    basis,
                    if i % 3 == 0 {
                        Color::from_rgb(0.75, 0.07, 0.05)
                    } else {
                        Color::from_rgb(0.82, 0.80, 0.72)
                    },
                );
                if i % 5 == 0 {
                    let p = (a + b) * 0.5 + side * (track.road_width * 0.5 + 25.) * sign;
                    let h = 12. + ((i * 7) % 29) as f32;
                    append_box(
                        &mut surface,
                        p + Vector3::UP * h * 0.5,
                        Vector3::new(17., h, 20.),
                        basis,
                        Color::from_rgb(0.29, 0.285, 0.30),
                    );
                    for level in 0..(h / 3.) as usize {
                        append_box(
                            &mut surface,
                            p + Vector3::UP * (2. + level as f32 * 3.) - side * 9.0 * sign,
                            Vector3::new(0.07, 1.3, 15.),
                            basis,
                            Color::from_rgb(0.58, 0.56, 0.44),
                        );
                    }
                }
            }
            if i % 3 == 0 {
                append_box(
                    &mut surface,
                    (a + b) * 0.5 + Vector3::UP * 0.025,
                    Vector3::new(0.14, 0.015, 2.5),
                    Basis::from_axis_angle(Vector3::UP, delta.x.atan2(delta.z)),
                    Color::from_rgb(0.95, 0.83, 0.34),
                );
            }
        }
        surface.generate_normals();
        if let Some(mesh) = surface.commit() {
            let mut material = StandardMaterial3D::new_gd();
            material.set_flag(
                godot::classes::base_material_3d::Flags::ALBEDO_FROM_VERTEX_COLOR,
                true,
            );
            material.set_roughness(0.82);
            let mut node = MeshInstance3D::new_alloc();
            node.set_name("RecoveredRouteReconstructedScenery");
            node.set_mesh(&mesh);
            node.set_material_override(&material);
            scene.add_child(&node);
        }
        let path = format!("res://assets/tracks/{}.glb", track.id);
        if ResourceLoader::singleton().exists(&path) {
            let mut native = Self::load_scene(&path);
            scene.add_child(&native);
            native.set_name("RecoveredEnvironment");
        }
    }
    fn load_scene(path: &str) -> Gd<Node3D> {
        ResourceLoader::singleton()
            .load(path)
            .and_then(|r| r.try_cast::<PackedScene>().ok())
            .and_then(|r| r.instantiate())
            .and_then(|n| n.try_cast::<Node3D>().ok())
            .unwrap_or_else(Node3D::new_alloc)
    }
    fn setup_audio(&mut self) {
        let mut root = Node3D::new_alloc();
        root.set_name("NativeAudio");
        self.base_mut().add_child(&root);
        let mut audio = audio::RuntimeAudio::new(root);
        audio.apply_options(&self.audio_options);
        self.audio = Some(audio);
    }
    fn setup_ui(&mut self) {
        let mut canvas = CanvasLayer::new_alloc();
        self.base_mut().add_child(&canvas);
        let mut menu = Control::new_alloc();
        menu.set_name("Menus");
        menu.set_size(Vector2::new(1920., 1080.));
        canvas.add_child(&menu);
        self.menu = Some(menu);
        let mut hud = Control::new_alloc();
        hud.set_name("RaceHUD");
        hud.set_size(Vector2::new(1920., 1080.));
        canvas.add_child(&hud);
        self.hud = Some(hud);
        let mut loading = Control::new_alloc();
        loading.set_size(Vector2::new(1920., 1080.));
        canvas.add_child(&loading);
        Self::rect(
            &mut loading,
            Vector2::ZERO,
            Vector2::new(1920., 1080.),
            Color::from_rgb(0.01, 0.015, 0.025),
        );
        Self::chrome(
            &mut loading,
            Vector2::new(0., 430.),
            Vector2::new(1920., 160.),
        );
        let label = Self::text(&mut loading, "LOADING...", 720., 470., 56, Color::WHITE);
        let mut tip = Self::text(
            &mut loading,
            &native_loading_tip(),
            560.,
            850.,
            28,
            Color::WHITE,
        );
        tip.set_size(Vector2::new(1120., 180.));
        tip.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
        loading.set_visible(false);
        self.loading_layer = Some(loading);
        self.loading_label = Some(label);
        let mut panel = Control::new_alloc();
        panel.set_size(Vector2::new(1920., 1080.));
        canvas.add_child(&panel);
        Self::rect(
            &mut panel,
            Vector2::ZERO,
            Vector2::new(1920., 1080.),
            Color::BLACK,
        );
        let mut player = godot::classes::VideoStreamPlayer::new_alloc();
        player.set_size(Vector2::new(1920., 1080.));
        player.set_expand(true);
        player.set_volume_db(-6.);
        panel.add_child(&player);
        self.button(&mut panel, "SKIP", "movie_skip", 1580., 970., 260., 65.);
        panel.set_visible(false);
        self.video_panel = Some(panel);
        self.video_player = Some(player);
    }
    fn rect(parent: &mut Gd<Control>, pos: Vector2, size: Vector2, color: Color) {
        let mut rect = ColorRect::new_alloc();
        rect.set_position(pos);
        rect.set_size(size);
        rect.set_color(color);
        rect.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        parent.add_child(&rect);
    }
    fn text(
        parent: &mut Gd<Control>,
        value: &str,
        x: f32,
        y: f32,
        size: i32,
        color: Color,
    ) -> Gd<Label> {
        let mut label = Label::new_alloc();
        label.add_theme_font_override("font", &native_font());
        label.set_text(value);
        label.set_position(Vector2::new(x, y));
        label.add_theme_font_size_override("font_size", size);
        label.add_theme_color_override("font_color", color);
        parent.add_child(&label);
        label
    }
    // Keep the existing presentation helper interface during tooling-only adoption.
    #[allow(clippy::too_many_arguments)]
    fn palette(
        &self,
        parent: &mut Gd<Control>,
        label: &str,
        target: &str,
        _color: [f32; 4],
        x: f32,
        y: f32,
        width: f32,
    ) {
        let mut button = Button::new_alloc();
        button.set_text(label);
        button.set_position(Vector2::new(x, y));
        button.set_size(Vector2::new(width, 48.));
        button.add_theme_font_override("font", &native_font());
        button.add_theme_font_size_override("font_size", 22);
        button.set_meta("ui_action", &format!("palette:{target}").to_variant());
        button.connect(
            "pressed",
            &self
                .base()
                .callable("palette_opened")
                .bind(&[target.to_variant()]),
        );
        parent.add_child(&button);
    }
    // Keep the existing presentation helper interface during tooling-only adoption.
    #[allow(clippy::too_many_arguments)]
    fn button(
        &self,
        parent: &mut Gd<Control>,
        label: &str,
        key: &str,
        x: f32,
        y: f32,
        w: f32,
        h: f32,
    ) {
        let mut button = Button::new_alloc();
        button.add_theme_font_override("font", &native_font());
        button.set_text(label);
        button.set_meta("ui_action", &key.to_variant());
        if self.confirmation.is_some() && !key.starts_with("confirm_") {
            button.set_disabled(true);
        }
        button.set_position(Vector2::new(x, y));
        button.set_size(Vector2::new(w, h));
        button.add_theme_font_size_override("font_size", 23);
        button.set_flat(true);
        let callable = self.base().callable("action").bind(&[key.to_variant()]);
        button.connect("pressed", &callable);
        let first = parent
            .get_children()
            .iter_shared()
            .filter(|n| n.is_class("Button") && !n.is_queued_for_deletion())
            .count()
            == 0;
        parent.add_child(&button);
        if button.is_inside_tree()
            && (key == "confirm_no" || (first && self.confirmation.is_none()))
        {
            button.grab_focus();
        }
    }
    fn rebuild_menu(&mut self) {
        let Some(game) = &self.game else { return };
        let snap = game.snapshot();
        let screen = snap.screen;
        let mut menu = self.menu.take().unwrap();
        for mut child in menu.get_children().iter_shared() {
            child.queue_free();
        }
        if let Some(error) = &self.error_dialog {
            menu.set_visible(true);
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 1080.),
                Color::from_rgba(0., 0., 0., 0.75),
            );
            Self::chrome(
                &mut menu,
                Vector2::new(350., 300.),
                Vector2::new(1220., 100.),
            );
            Self::text(&mut menu, "NOTICE", 820., 320., 42, Color::WHITE);
            let mut label = Self::text(&mut menu, error, 430., 430., 30, Color::WHITE);
            label.set_size(Vector2::new(1060., 190.));
            label.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
            if !self.io_retry.is_empty() {
                self.button(&mut menu, "RETRY", "retry_io", 550., 680., 350., 65.);
            }
            if self.save_blocked {
                self.button(
                    &mut menu,
                    "START NEW CAREER",
                    "new_career",
                    1000.,
                    680.,
                    420.,
                    65.,
                );
            } else {
                self.button(&mut menu, "OK", "error_ok", 1000., 680., 350., 65.);
            }
            self.menu = Some(menu);
            return;
        }
        if self.title {
            menu.set_visible(true);
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(720., 1080.),
                Color::from_rgba(0.035, 0.045, 0.055, 0.94),
            );
            Self::text(&mut menu, "OVERSTEER", 80., 170., 72, Color::WHITE);
            Self::text(
                &mut menu,
                "Find your line.",
                85.,
                275.,
                28,
                Color::from_rgb(0.67, 0.74, 0.77),
            );
            self.button(
                &mut menu,
                "START DRIVING",
                "title_start",
                80.,
                680.,
                540.,
                76.,
            );
            Self::text(
                &mut menu,
                "CAREER  /  QUICK RACE",
                85.,
                790.,
                19,
                Color::from_rgb(0.52, 0.78, 0.76),
            );
            self.menu = Some(menu);
            return;
        }
        if self.credits {
            menu.set_visible(true);
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 1080.),
                Color::from_rgba(0.035, 0.045, 0.055, 0.97),
            );
            Self::text(&mut menu, "OVERSTEER", 100., 100., 56, Color::WHITE);
            Self::text(
                &mut menu,
                "An independent racing game",
                100.,
                185.,
                28,
                Color::from_rgb(0.67, 0.74, 0.77),
            );
            Self::text(
                &mut menu,
                "Built with Godot and Rust.\n\nCharacter, vehicle and environment assets retain their original provenance.\nSource collections and adaptations are documented with the project.",
                100.,
                350.,
                27,
                Color::WHITE,
            );
            self.button(&mut menu, "BACK", "credits_back", 100., 850., 420., 65.);
            self.menu = Some(menu);
            return;
        }
        if self.replay {
            Self::text(&mut menu, "REPLAY", 70., 55., 38, Color::WHITE);
            self.button(&mut menu, "CONTINUE", "replay_done", 1510., 950., 320., 65.);
            self.menu = Some(menu);
            return;
        }
        if !self.options && screen == GameScreen::MainMenu {
            menu.set_visible(true);
            self.reference_main(&mut menu);
            self.menu = Some(menu);
            return;
        }
        if self.show_stats {
            menu.set_visible(true);
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 1080.),
                Color::from_rgba(0.015, 0.025, 0.065, 0.94),
            );
            Self::chrome(&mut menu, Vector2::new(0., 90.), Vector2::new(1600., 95.));
            Self::text(&mut menu, "VEHICLE HISTORY", 120., 100., 44, Color::WHITE);
            if let Some(car) = snap.cars.iter().find(|car| car.id == snap.selected_car) {
                Self::text(&mut menu, &car.name, 120., 245., 40, Color::WHITE);
            }
            if let Some(history) = snap.career.vehicle_history.get(&snap.selected_car) {
                Self::text(
                    &mut menu,
                    &format!(
                        "DISTANCE {:.1} KM\nWINS {}    LOSSES {}\nPINK SLIP WINS {}    LOSSES {}\nPURCHASE PRICE ${}\nTOTAL SPENT ${}\nACQUIRED BY {}",
                        history.mileage_m / 1000.,
                        history.wins,
                        history.losses,
                        history.pink_slip_wins,
                        history.pink_slip_losses,
                        history.purchase_price,
                        history.total_spent,
                        history.acquired_by
                    ),
                    120.,
                    330.,
                    32,
                    Color::WHITE,
                );
            }
            Self::text(&mut menu, "YOUR GARAGE", 1090., 245., 36, Color::WHITE);
            Self::text(
                &mut menu,
                "Buy cars and fit upgrades with race earnings.\nCash bets and pink slips are optional.\nYour last owned car cannot be staked.",
                1090.,
                330.,
                25,
                Color::WHITE,
            );
            self.button(&mut menu, "BACK", "stats_back", 1430., 955., 300., 60.);
            self.menu = Some(menu);
            return;
        }
        if self.show_goals {
            menu.set_visible(true);
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 1080.),
                Color::from_rgb(0.035, 0.045, 0.055),
            );
            let progress = &snap.league_progress;
            self.goal_page = self.goal_page.min(progress.goals.len().saturating_sub(1));
            let white = Color::WHITE;
            let muted = Color::from_rgb(0.67, 0.74, 0.77);
            let accent = Color::from_rgb(0.52, 0.78, 0.76);
            Self::text(&mut menu, "CAREER PROGRESSION", 70., 65., 48, white);
            Self::text(
                &mut menu,
                "Win the circuit and drift events, then win promotion.",
                74.,
                140.,
                25,
                muted,
            );
            for (row, tier) in self.content.leagues.iter().enumerate() {
                let state = if tier.league < snap.career.league {
                    "COMPLETE"
                } else if tier.league == snap.career.league {
                    "CURRENT"
                } else {
                    "LOCKED"
                };
                Self::text(
                    &mut menu,
                    &tier.name,
                    74.,
                    235. + row as f32 * 102.,
                    30,
                    if tier.league == snap.career.league {
                        accent
                    } else {
                        white
                    },
                );
                Self::text(&mut menu, state, 76., 278. + row as f32 * 102., 18, muted);
            }
            Self::text(
                &mut menu,
                &self.league_label(snap.career.league),
                760.,
                235.,
                36,
                accent,
            );
            for (index, status) in progress.goals.iter().enumerate() {
                let state = if status.progress.complete {
                    "COMPLETE"
                } else if status.goal.qualifier && !progress.promotion_open {
                    "LOCKED"
                } else {
                    "OPEN"
                };
                self.button(
                    &mut menu,
                    &format!(
                        "{} {}  ·  {}",
                        if index == self.goal_page { "▶" } else { " " },
                        status.goal.description,
                        state
                    ),
                    &format!("goal_icon:{index}"),
                    760.,
                    320. + index as f32 * 100.,
                    1050.,
                    76.,
                );
            }
            Self::text(
                &mut menu,
                "Next tier: win this tier's promotion race.\nEvery event is free to enter. Bets are optional.\nEarlier events remain available for earnings.",
                770.,
                655.,
                25,
                muted,
            );
            Self::text(&mut menu, &self.notice, 770., 800., 23, white);
            self.button(
                &mut menu,
                "VIEW EVENT",
                "goals_select",
                760.,
                920.,
                680.,
                70.,
            );
            self.button(&mut menu, "BACK", "goals_back", 1500., 920., 310., 70.);
            self.menu = Some(menu);
            return;
        }
        if !self.options
            && (screen == GameScreen::MainMenu
                || (screen == GameScreen::Career && !self.event_picker))
        {
            self.reference_home(&mut menu, &snap);
            self.menu = Some(menu);
            return;
        }
        let race = screen == GameScreen::Race;
        let spectating = snap.race.as_ref().is_some_and(|r| r.spectating);
        menu.set_visible(!race || spectating);
        if race && spectating {
            if let Some(race) = &snap.race {
                Self::rect(
                    &mut menu,
                    Vector2::new(30., 180.),
                    Vector2::new(480., 720.),
                    Color::from_rgba(0., 0., 0., 0.65),
                );
                for (index, racer) in race.racers.iter().enumerate() {
                    self.button(
                        &mut menu,
                        &format!(
                            "{} {}",
                            if index == self.selected_rival {
                                ">"
                            } else {
                                " "
                            },
                            racer.name
                        ),
                        &format!("rival:{index}"),
                        45.,
                        200. + index as f32 * 58.,
                        440.,
                        52.,
                    );
                }
                self.button(
                    &mut menu,
                    &format!("STAKE ${}", self.wager.max(1000)),
                    "wager",
                    45.,
                    780.,
                    220.,
                    50.,
                );
                self.button(
                    &mut menu,
                    "PLACE BET",
                    "spectator_bet",
                    270.,
                    780.,
                    220.,
                    50.,
                );
                let odds = Self::text(&mut menu, "", 45., 920., 28, Color::WHITE);
                self.labels.insert("spectator_odds".into(), odds);
            }
            self.menu = Some(menu);
            return;
        }
        if race {
            self.menu = Some(menu);
            return;
        }
        let white = Color::from_rgb(0.96, 0.96, 0.93);
        let red = Color::from_rgb(0.52, 0.78, 0.76);
        let muted = Color::from_rgb(0.63, 0.67, 0.73);
        if !matches!(
            screen,
            GameScreen::Grid
                | GameScreen::Customization
                | GameScreen::Checkout
                | GameScreen::Avatar
        ) {
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 120.),
                Color::from_rgba(0.025, 0.025, 0.035, 0.96),
            );
            Self::text(&mut menu, "OVERSTEER", 60., 24., 46, white);
            Self::text(&mut menu, "BUILT TO DRIVE", 64., 78., 15, muted);
            Self::text(
                &mut menu,
                &format!(
                    "{}     ${}     {} WINS",
                    self.league_label(snap.career.league),
                    snap.career.cash,
                    snap.career.wins
                ),
                1260.,
                53.,
                22,
                white,
            );
            Self::rect(
                &mut menu,
                Vector2::new(0., 120.),
                Vector2::new(540., 890.),
                Color::from_rgba(0.025, 0.025, 0.045, 0.91),
            );
            Self::rect(
                &mut menu,
                Vector2::new(0., 1006.),
                Vector2::new(1920., 74.),
                Color::from_rgba(0.025, 0.025, 0.035, 0.94),
            );
            Self::text(
                &mut menu,
                if self.options {
                    "OPTIONS"
                } else {
                    match screen {
                        GameScreen::Career => "CAREER",
                        GameScreen::QuickRace => "QUICK RACE",
                        GameScreen::Garage => "GARAGE",
                        GameScreen::Dealership => "DEALERSHIP",
                        GameScreen::Customization => "CUSTOMIZE",
                        GameScreen::Crew => "CREW DNA",
                        GameScreen::Paused => "PAUSED",
                        GameScreen::Results => "RACE RESULTS",
                        GameScreen::Complete => "CAREER COMPLETE",
                        GameScreen::Checkout => "SHOPPING CART",
                        GameScreen::Avatar => "DRIVER PROFILE",
                        GameScreen::Podium => "PODIUM",
                        GameScreen::RoundResults => "ROUND RESULTS",
                        _ => "MAIN MENU",
                    }
                },
                58.,
                150.,
                38,
                white,
            );
            Self::rect(
                &mut menu,
                Vector2::new(60., 210.),
                Vector2::new(90., 5.),
                red,
            );
            Self::text(&mut menu, &self.notice, 580., 1025., 22, red);
            if screen != GameScreen::Avatar {
                Self::text(
                    &mut menu,
                    "W/S ACCELERATE / BRAKE    A/D STEER    SHIFT NITROUS    SPACE HANDBRAKE    ESC PAUSE",
                    60.,
                    1028.,
                    19,
                    muted,
                );
            }
        }
        if self.options {
            Self::rect(
                &mut menu,
                Vector2::new(540., 120.),
                Vector2::new(1380., 886.),
                Color::from_rgba(0.035, 0.045, 0.055, 0.96),
            );
            Self::text(&mut menu, "DRIVER NAME", 620., 580., 22, muted);
            let mut name = godot::classes::LineEdit::new_alloc();
            name.set_text(&snap.profile.name);
            name.set_position(Vector2::new(620., 630.));
            name.set_size(Vector2::new(400., 58.));
            name.set_max_length(24);
            name.set_meta("ui_action", &"driver_name".to_variant());
            name.add_theme_font_override("font", &native_font());
            name.add_theme_font_size_override("font_size", 24);
            name.connect("text_changed", &self.base().callable("driver_name"));
            menu.add_child(&name);
            for (i, (action, key)) in self.bindings.iter().enumerate() {
                self.button(
                    &mut menu,
                    &format!("{}   {:?}", action.to_uppercase(), key),
                    &format!("bind:{action}"),
                    60.,
                    250. + i as f32 * 65.,
                    420.,
                    54.,
                );
            }
            self.button(
                &mut menu,
                &format!(
                    "DIFFICULTY {}",
                    ["EASY", "NORMAL", "HARD"][snap.difficulty as usize]
                ),
                "difficulty",
                620.,
                280.,
                400.,
                58.,
            );
            self.button(
                &mut menu,
                &format!(
                    "QUALITY {}",
                    ["LOW", "BALANCED", "HIGH"][self.render_quality as usize]
                ),
                "quality",
                620.,
                365.,
                400.,
                58.,
            );
            if let Some(audio) = &self.audio {
                for (i, (kind, gain)) in [
                    ("music", audio.music_gain),
                    ("engine", audio.engine_gain),
                    ("speech", audio.speech_gain),
                    ("sfx", audio.sfx_gain),
                ]
                .iter()
                .enumerate()
                {
                    self.button(
                        &mut menu,
                        &format!("{} {:.0}%", kind.to_uppercase(), gain * 100.),
                        &format!("audio:{kind}"),
                        1050. + (i % 2) as f32 * 310.,
                        230. + (i / 2) as f32 * 65.,
                        300.,
                        58.,
                    );
                }
            }
            for (i, (action, axis)) in self.joy_axes.iter().enumerate() {
                self.button(
                    &mut menu,
                    &format!("{}   AXIS {}", action.to_uppercase(), axis),
                    &format!("axis:{action}"),
                    1090.,
                    400. + i as f32 * 65.,
                    600.,
                    55.,
                );
            }
            for (i, (action, button)) in self.joy_buttons.iter().enumerate() {
                self.button(
                    &mut menu,
                    &format!("{}   BUTTON {}", action.to_uppercase(), button),
                    &format!("button:{action}"),
                    1090.,
                    620. + i as f32 * 65.,
                    600.,
                    55.,
                );
            }
            self.button(
                &mut menu,
                if self.speed_mph {
                    "SPEED UNITS: MPH"
                } else {
                    "SPEED UNITS: KPH"
                },
                "units",
                620.,
                450.,
                400.,
                55.,
            );
            self.button(&mut menu, "BACK", "back_options", 60., 780., 420., 58.);
            Self::text(&mut menu, "DRIVING", 620., 220., 32, white);
            let mut help = Self::text(
                &mut menu,
                "Select a binding, then press its new key or controller input.\n\nGamepad: left stick and triggers.",
                620.,
                740.,
                22,
                muted,
            );
            help.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
            help.set_size(Vector2::new(400., 200.));
            self.menu = Some(menu);
            return;
        }
        match screen {
            GameScreen::MainMenu | GameScreen::Complete => {
                let actions = [
                    ("CAREER", "nav:career"),
                    ("QUICK RACE", "nav:quick"),
                    ("GARAGE", "nav:garage"),
                    ("DEALERSHIP", "nav:dealer"),
                    ("OPTIONS", "options"),
                    ("SAVE & QUIT", "quit"),
                ];
                for (i, (label, key)) in actions.iter().enumerate() {
                    self.button(&mut menu, label, key, 60., 250. + i as f32 * 84., 420., 68.);
                }
                Self::text(&mut menu, "", 1120., 780., 52, white);
                Self::text(
                    &mut menu,
                    "30 CARS   •   CIRCUIT   •   DRIFT   •   CAREER",
                    1125.,
                    845.,
                    21,
                    red,
                );
            }
            GameScreen::QuickRace | GameScreen::Career => {
                let goal_events = self
                    .game
                    .as_ref()
                    .unwrap()
                    .events_for_goal(&self.selected_goal);
                let events: Vec<_> = snap
                    .events
                    .iter()
                    .enumerate()
                    .filter(|(_, e)| {
                        screen == GameScreen::QuickRace
                            || (e.league <= snap.career.league
                                && (self.selected_goal.is_empty() || goal_events.contains(&e.id)))
                    })
                    .collect();
                for (row, (index, event)) in events
                    .iter()
                    .skip(
                        events
                            .iter()
                            .position(|(i, _)| *i == self.selected_event)
                            .unwrap_or(0)
                            / 8
                            * 8,
                    )
                    .take(8)
                    .enumerate()
                {
                    self.button(
                        &mut menu,
                        &format!(
                            "{} {}",
                            if *index == self.selected_event {
                                "▶"
                            } else {
                                " "
                            },
                            event.name
                        ),
                        &format!("event:{index}"),
                        50.,
                        240. + row as f32 * 65.,
                        450.,
                        56.,
                    );
                }
                Self::rect(
                    &mut menu,
                    Vector2::new(1420., 200.),
                    Vector2::new(460., 650.),
                    Color::from_rgba(0.035, 0.045, 0.055, 0.96),
                );
                if let Some(event) = snap.events.get(self.selected_event) {
                    let mut title = Self::text(&mut menu, "", 1445., 225., 28, white);
                    title.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
                    title.set_size(Vector2::new(410., 80.));
                    title.set_text(&event.name.to_uppercase());
                    let detail_text = format!(
                        "{}  ·  {} {}\nWIN ${}  ·  2ND ${}\n\n{}\n\n{}\n\n{}",
                        if event.mode.is_drift() {
                            format!("DRIFT / {:.0} MIN", event.time_limit / 60.)
                        } else {
                            "CIRCUIT".into()
                        },
                        event.laps,
                        if event.laps == 1 { "LAP" } else { "LAPS" },
                        event.reward,
                        event.prizes.get(1).copied().unwrap_or(0),
                        if event.mode.is_drift() {
                            format!(
                                "Win with the highest score, at least {:.0} points.",
                                event.target
                            )
                        } else {
                            "Finish first to win.".into()
                        },
                        if event.qualifier
                            && event.league == snap.career.league
                            && !snap.league_progress.promotion_open
                        {
                            "Locked: win this tier's circuit and drift events."
                        } else if screen == GameScreen::QuickRace {
                            "Free entry. All cars available."
                        } else {
                            "Free entry. Any owned car."
                        },
                        if event.qualifier {
                            if event.league == 5 {
                                "Win to complete the career."
                            } else {
                                "Win to unlock the next tier."
                            }
                        } else {
                            "A win counts toward tier promotion."
                        }
                    );
                    let mut detail = Self::text(&mut menu, "", 1445., 310., 22, white);
                    detail.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
                    detail.set_size(Vector2::new(410., 330.));
                    detail.set_text(&detail_text);
                }
                let mut bets = Self::text(&mut menu, "", 1445., 670., 20, muted);
                bets.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
                bets.set_size(Vector2::new(410., 70.));
                bets.set_text("Optional cash bets and pink slips are offered on the career grid.");
                self.button(&mut menu, "START RACE", "start", 1445., 760., 410., 65.);
                self.car_picker(&mut menu, &snap, 240., screen == GameScreen::Career);
                self.button(&mut menu, "◀ EVENT", "event_prev", 60., 770., 200., 50.);
                self.button(&mut menu, "EVENT ▶", "event_next", 280., 770., 200., 50.);
                self.button(
                    &mut menu,
                    "CUSTOMIZE CAR",
                    "nav:custom",
                    60.,
                    830.,
                    420.,
                    55.,
                );
                self.button(&mut menu, "BACK", "nav:main", 60., 900., 420., 60.);
            }
            GameScreen::Garage | GameScreen::Dealership => {
                self.car_picker(&mut menu, &snap, 240., screen == GameScreen::Garage);
                self.button(&mut menu, "CUSTOMIZE", "nav:custom", 1090., 850., 300., 65.);
                self.button(
                    &mut menu,
                    if screen == GameScreen::Garage {
                        "SELL CAR"
                    } else {
                        "BUY CAR"
                    },
                    if screen == GameScreen::Garage {
                        "sell"
                    } else {
                        "buy"
                    },
                    1410.,
                    850.,
                    300.,
                    65.,
                );
                if screen == GameScreen::Garage {
                    self.button(
                        &mut menu,
                        "VEHICLE HISTORY",
                        "vehicle_stats",
                        1090.,
                        925.,
                        620.,
                        55.,
                    );
                }
                self.button(&mut menu, "BACK", "nav:main", 60., 910., 420., 60.);
            }
            GameScreen::Customization => {
                self.custom_menu(&mut menu, &snap);
            }
            GameScreen::Crew => {
                for (i, driver) in snap.drivers.iter().enumerate() {
                    self.button(
                        &mut menu,
                        &driver.name,
                        &format!("dna:{}", driver.native_tag),
                        1300.,
                        230. + i as f32 * 37.,
                        460.,
                        36.,
                    );
                }
                if let Some(driver) = snap
                    .drivers
                    .iter()
                    .find(|driver| driver.native_tag == self.selected_dna)
                    .or_else(|| snap.drivers.first())
                {
                    Self::text(
                        &mut menu,
                        &driver.name.to_uppercase(),
                        610.,
                        240.,
                        38,
                        white,
                    );
                    for (row, (label, genes, experience)) in [
                        (
                            "CIRCUIT",
                            driver.circuit_genes.to_vec(),
                            driver.circuit_experience.to_vec(),
                        ),
                        (
                            "DRIFT",
                            driver.drift_genes.to_vec(),
                            driver.drift_experience.to_vec(),
                        ),
                        (
                            "GAMBLING",
                            driver.gambling_genes.to_vec(),
                            driver.gambling_experience.to_vec(),
                        ),
                    ]
                    .into_iter()
                    .enumerate()
                    {
                        Self::text(&mut menu, label, 610., 335. + row as f32 * 155., 30, white);
                        Self::text(
                            &mut menu,
                            &format!(
                                "GENES {}\nEXPERIENCE {}",
                                genes
                                    .iter()
                                    .map(|value| format!("{value:.2}"))
                                    .collect::<Vec<_>>()
                                    .join(" / "),
                                experience
                                    .iter()
                                    .map(|value| format!("{value:.2}"))
                                    .collect::<Vec<_>>()
                                    .join(" / ")
                            ),
                            610.,
                            380. + row as f32 * 155.,
                            23,
                            muted,
                        );
                    }
                    self.button(
                        &mut menu,
                        "RECRUIT DRIVER",
                        &format!("recruit:{}", driver.native_tag),
                        60.,
                        300.,
                        420.,
                        65.,
                    );
                }
                Self::text(&mut menu, "YOUR CREW", 65., 425., 30, white);
                for (i, driver) in snap.career.crew.iter().enumerate() {
                    Self::text(
                        &mut menu,
                        &driver.name,
                        65.,
                        480. + i as f32 * 50.,
                        26,
                        white,
                    );
                }
                self.button(&mut menu, "BACK", "nav:main", 60., 910., 420., 60.);
            }
            GameScreen::Paused => {
                Self::chrome(
                    &mut menu,
                    Vector2::new(580., 280.),
                    Vector2::new(1120., 160.),
                );
                let mut warning = Self::text(&mut menu, "", 610., 300., 28, white);
                warning.set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
                warning.set_size(Vector2::new(1060., 120.));
                warning.set_text("Restarting or leaving forfeits your accepted cash or vehicle stake.\nA restarted race begins without a new bet.");
                for (i, (label, key)) in [
                    ("RESUME", "resume"),
                    ("RESTART RACE", "restart"),
                    ("OPTIONS", "options"),
                    ("QUIT TO MENU", "nav:main"),
                ]
                .iter()
                .enumerate()
                {
                    self.button(&mut menu, label, key, 60., 270. + i as f32 * 85., 420., 65.);
                }
            }
            GameScreen::Checkout => {
                self.checkout_menu(&mut menu, &snap);
            }
            GameScreen::Avatar => {}
            GameScreen::Podium => {
                if let Some(result) = &snap.result {
                    Self::chrome(
                        &mut menu,
                        Vector2::new(400., 200.),
                        Vector2::new(1200., 100.),
                    );
                    Self::text(
                        &mut menu,
                        &format!(
                            "{}    POSITION {}",
                            snap.profile.name.to_uppercase(),
                            result.position
                        ),
                        620.,
                        220.,
                        48,
                        white,
                    );
                    Self::text(
                        &mut menu,
                        &format!("PRIZE ${}", result.reward),
                        800.,
                        795.,
                        38,
                        white,
                    );
                }
                self.button(&mut menu, "CONTINUE", "continue", 60., 900., 420., 65.);
            }
            GameScreen::Grid => {
                Self::rect(
                    &mut menu,
                    Vector2::ZERO,
                    Vector2::new(1920., 1080.),
                    Color::from_rgba(0., 0., 0., 0.12),
                );
                Self::rect(
                    &mut menu,
                    Vector2::new(40., 40.),
                    Vector2::new(1840., 130.),
                    Color::from_rgba(0.035, 0.045, 0.055, 0.95),
                );
                Self::text(&mut menu, "RACE NIGHT", 70., 65., 42, white);
                Self::text(
                    &mut menu,
                    "Choose a rival. Betting is optional.",
                    70.,
                    120.,
                    24,
                    white,
                );
                Self::chrome(&mut menu, Vector2::new(40., 205.), Vector2::new(500., 65.));
                Self::text(
                    &mut menu,
                    &format!("CASH  ${}", snap.career.cash),
                    70.,
                    212.,
                    31,
                    white,
                );
                Self::text(&mut menu, "SELECT RIVAL", 70., 285., 36, white);
                Self::rect(
                    &mut menu,
                    Vector2::new(1260., 205.),
                    Vector2::new(620., 700.),
                    Color::from_rgba(0., 0., 0., 0.67),
                );
                if let Some(race) = &snap.race {
                    for (index, racer) in
                        race.racers.iter().enumerate().filter(|(_, r)| !r.is_player)
                    {
                        self.button(
                            &mut menu,
                            &format!(
                                "{} {}",
                                if index == self.selected_rival {
                                    ">"
                                } else {
                                    " "
                                },
                                racer.name
                            ),
                            &format!("rival:{index}"),
                            65.,
                            330. + index as f32 * 62.,
                            460.,
                            55.,
                        );
                    }
                    Self::text(&mut menu, "DRIVER BET", 1300., 235., 38, white);
                    let accepted = race
                        .bet_offer
                        .as_ref()
                        .is_some_and(|offer| offer.status == BetOfferStatus::Accepted);
                    if !accepted {
                        self.button(
                            &mut menu,
                            &format!("OFFER ${}", self.wager.max(1000)),
                            "wager",
                            1300.,
                            310.,
                            330.,
                            60.,
                        );
                        self.button(
                            &mut menu,
                            "MAKE CASH OFFER",
                            "offer_cash",
                            1300.,
                            385.,
                            540.,
                            60.,
                        );
                        self.button(
                            &mut menu,
                            "PINK SLIP OFFER",
                            "offer_pink",
                            1300.,
                            460.,
                            540.,
                            60.,
                        );
                    }
                    if let Some(offer) = &race.bet_offer {
                        let text = if accepted {
                            let rival = &race.racers[offer.racer];
                            if offer.kind == BetKind::Cash {
                                format!(
                                    "CASH BET ACCEPTED\n${} against {}.\n\nBeat this rival to win the bet. Leaving or restarting forfeits the stake.",
                                    offer.counter_amount, rival.name
                                )
                            } else {
                                let name = |id: &str| {
                                    self.content
                                        .cars
                                        .iter()
                                        .find(|c| c.id == id)
                                        .map(|c| c.name.clone())
                                        .unwrap_or_else(|| id.into())
                                };
                                format!(
                                    "PINK SLIPS ACCEPTED\nYour {} against {}'s {}.\n\nLose to this rival, leave or restart and you forfeit your car.",
                                    name(&race.racers[0].car_id),
                                    rival.name,
                                    name(&rival.car_id)
                                )
                            }
                        } else {
                            format!("{:?} offer\n{}", offer.kind, offer.reason)
                        };
                        let mut offer_text = Self::text(
                            &mut menu,
                            "",
                            1300.,
                            if accepted { 330. } else { 545. },
                            25,
                            white,
                        );
                        offer_text.set_autowrap_mode(
                            godot::classes::text_server::AutowrapMode::WORD_SMART,
                        );
                        offer_text.set_size(Vector2::new(540., if accepted { 350. } else { 115. }));
                        offer_text.set_text(&text);
                        if matches!(
                            offer.status,
                            BetOfferStatus::Offered | BetOfferStatus::Countered
                        ) {
                            self.button(
                                &mut menu,
                                "ACCEPT",
                                "offer_accept",
                                1300.,
                                670.,
                                250.,
                                60.,
                            );
                            self.button(
                                &mut menu,
                                "DECLINE",
                                "offer_decline",
                                1590.,
                                670.,
                                250.,
                                60.,
                            );
                        }
                    }
                }
                self.button(
                    &mut menu,
                    "START RACE",
                    "grid_launch",
                    1300.,
                    790.,
                    540.,
                    75.,
                );
            }
            GameScreen::RoundResults => {
                Self::text(&mut menu, "ROUND COMPLETE", 850., 280., 58, white);
                if let Some(result) = &snap.result {
                    Self::text(
                        &mut menu,
                        &format!(
                            "ROUND {} / {}\nPOINTS {:?}\nPOSITION {}",
                            result.round,
                            result.total_rounds,
                            result.tournament_points,
                            result.position
                        ),
                        850.,
                        390.,
                        32,
                        white,
                    );
                }
                self.button(&mut menu, "NEXT ROUND", "continue", 60., 300., 420., 65.);
                self.button(&mut menu, "BACK TO MENU", "nav:main", 60., 400., 420., 65.);
            }
            GameScreen::Results => {
                if let Some(result) = snap.result {
                    Self::rect(
                        &mut menu,
                        Vector2::new(620., 210.),
                        Vector2::new(1180., 475.),
                        Color::from_rgba(0.025, 0.032, 0.04, 0.93),
                    );
                    Self::text(
                        &mut menu,
                        if result.won {
                            "YOU WIN"
                        } else {
                            "RACE COMPLETE"
                        },
                        660.,
                        240.,
                        50,
                        white,
                    );
                    let mut details = format!(
                        "POSITION {}    ·    TIME {:02}:{:05.2}\nRACE REWARD +${}",
                        result.position,
                        (result.time / 60.) as u32,
                        result.time % 60.,
                        result.reward
                    );
                    if let Some(race) = &snap.race {
                        if race.mode.is_drift() {
                            details.push_str(&format!("\nDRIFT SCORE {:.0}", result.score));
                        }
                        if let Some(rival) = race.racers.get(race.bet_racer) {
                            if let Some(car_id) = &result.pink_slip {
                                let name = self
                                    .content
                                    .cars
                                    .iter()
                                    .find(|c| &c.id == car_id)
                                    .map(|c| c.name.as_str())
                                    .unwrap_or(car_id);
                                if race.racers.first().is_some_and(|r| &r.car_id == car_id) {
                                    details.push_str(&format!(
                                        "\n\nPINK SLIP LOST\nYour {name} was transferred to {}.",
                                        rival.name
                                    ));
                                } else {
                                    details.push_str(&format!(
                                        "\n\nPINK SLIP WON\n{}'s {name} is now in your garage.",
                                        rival.name
                                    ));
                                }
                            } else if race.wager > 0 {
                                if result.wager > 0 {
                                    details.push_str(&format!(
                                        "\n\nBET WON · +${} NET\nYou beat {}. Your ${} stake was also returned.",
                                        result.wager, rival.name, race.wager
                                    ));
                                } else {
                                    details.push_str(&format!(
                                        "\n\nBET LOST · -${}\n{} finished ahead. Your stake was forfeited.",
                                        race.wager, rival.name
                                    ));
                                }
                            }
                        }
                    }
                    let mut detail_label = Self::text(&mut menu, "", 660., 335., 28, white);
                    detail_label
                        .set_autowrap_mode(godot::classes::text_server::AutowrapMode::WORD_SMART);
                    detail_label.set_size(Vector2::new(1100., 320.));
                    detail_label.set_text(&details);
                }
                self.button(&mut menu, "CONTINUE", "continue", 60., 300., 420., 65.);
                self.button(&mut menu, "PODIUM", "podium", 60., 570., 420., 65.);
                self.button(&mut menu, "WATCH REPLAY", "replay", 60., 390., 420., 65.);
                self.button(&mut menu, "RESTART RACE", "restart", 60., 480., 420., 65.);
            }
            _ => {}
        }
        if let Some(car) = snap
            .cars
            .iter()
            .find(|c| c.id == snap.selected_car)
            .filter(|_| {
                matches!(
                    screen,
                    GameScreen::Career
                        | GameScreen::QuickRace
                        | GameScreen::Garage
                        | GameScreen::Dealership
                )
            })
        {
            Self::text(&mut menu, &car.name.to_uppercase(), 620., 890., 36, white);
            Self::text(
                &mut menu,
                &format!("${}    {}", car.price, self.league_label(car.league)),
                625.,
                943.,
                22,
                muted,
            );
        }
        if self.confirmation.is_some() || self.error_dialog.is_some() {
            Self::rect(
                &mut menu,
                Vector2::ZERO,
                Vector2::new(1920., 1080.),
                Color::from_rgba(0., 0., 0., 0.7),
            );
            Self::native_texture(
                &mut menu,
                "MessageBoxFrame",
                Vector2::new(430., 300.),
                Vector2::new(1060., 450.),
                true,
            );
            if let Some(error) = &self.error_dialog {
                Self::text(&mut menu, "NOTICE", 650., 315., 40, white);
                Self::text(&mut menu, error, 500., 435., 29, white);
                self.button(&mut menu, "OK", "error_ok", 770., 630., 380., 65.);
            } else if let Some(action) = &self.confirmation {
                let title = match action.as_str() {
                    "buy" => "PURCHASE VEHICLE?",
                    "sell" => "SELL VEHICLE?",
                    "checkout" => "PURCHASE SELECTED MODIFICATIONS?",
                    "pink_offer" => "RISK YOUR VEHICLE IN A PINK SLIP BET?",
                    _ => "DISCARD ALL CHANGES?",
                };
                Self::text(&mut menu, title, 650., 315., 40, white);
                if let Some(car) = snap.cars.iter().find(|c| c.id == snap.selected_car) {
                    Self::text(&mut menu, &car.name, 530., 435., 34, white);
                    if action == "buy" {
                        Self::text(
                            &mut menu,
                            &format!("PRICE ${}   CASH ${}", car.price, snap.career.cash),
                            530.,
                            495.,
                            30,
                            white,
                        );
                    }
                }
                if action == "checkout" {
                    Self::text(
                        &mut menu,
                        &format!(
                            "{} ITEMS    TOTAL ${}    CASH ${}",
                            snap.cart.len(),
                            snap.cart.iter().map(|item| item.cost).sum::<u32>(),
                            snap.career.cash
                        ),
                        530.,
                        510.,
                        30,
                        white,
                    );
                }
                self.button(&mut menu, "YES", "confirm_yes", 810., 610., 300., 50.);
                self.button(&mut menu, "NO", "confirm_no", 810., 665., 300., 50.);
            }
        }
        self.menu = Some(menu);
    }
    fn native_texture(
        parent: &mut Gd<Control>,
        asset: &str,
        position: Vector2,
        size: Vector2,
        stretch: bool,
    ) -> bool {
        let named = format!("res://assets/ui/native/named/{asset}.png");
        let path = if ResourceLoader::singleton().exists(&named) {
            named
        } else {
            format!("res://assets/ui/native/aliases/{asset}.png")
        };
        let Some(texture) = ResourceLoader::singleton()
            .load(&path)
            .and_then(|r| r.try_cast::<godot::classes::Texture2D>().ok())
        else {
            return false;
        };
        let mut node = godot::classes::TextureRect::new_alloc();
        node.set_name(&format!("Native_{asset}"));
        node.set_meta("native_asset", &asset.to_variant());
        node.set_expand_mode(godot::classes::texture_rect::ExpandMode::IGNORE_SIZE);
        node.set_stretch_mode(if stretch {
            godot::classes::texture_rect::StretchMode::SCALE
        } else {
            godot::classes::texture_rect::StretchMode::KEEP_ASPECT_CENTERED
        });
        node.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
        node.set_texture(&texture);
        parent.add_child(&node);
        node.set_position(position);
        node.set_size(size);
        true
    }
    fn chrome(parent: &mut Gd<Control>, position: Vector2, size: Vector2) {
        Self::rect(
            parent,
            position,
            size,
            Color::from_rgba(0.06, 0.08, 0.10, 0.96),
        );
        Self::rect(
            parent,
            position,
            Vector2::new(3., size.y),
            Color::from_rgb(0.52, 0.78, 0.76),
        );
    }
    fn reference_main(&mut self, menu: &mut Gd<Control>) {
        Self::rect(
            menu,
            Vector2::ZERO,
            Vector2::new(720., 1080.),
            Color::from_rgba(0.035, 0.045, 0.055, 0.94),
        );
        Self::text(menu, "OVERSTEER", 80., 110., 64, Color::WHITE);
        Self::text(
            menu,
            "Find your line.",
            85.,
            205.,
            26,
            Color::from_rgb(0.67, 0.74, 0.77),
        );
        for (i, (label, key)) in [
            ("CAREER", "nav:career"),
            ("QUICK RACE", "nav:quick"),
            ("OPTIONS", "options"),
            ("CREDITS", "credits"),
            ("SAVE & QUIT", "quit"),
        ]
        .iter()
        .enumerate()
        {
            self.button(menu, label, key, 80., 380. + i as f32 * 96., 540., 72.);
        }
        Self::text(
            menu,
            "CIRCUIT  /  DRIFT  /  YOUR GARAGE",
            85.,
            975.,
            18,
            Color::from_rgb(0.52, 0.78, 0.76),
        );
    }
    fn reference_home(&self, menu: &mut Gd<Control>, snap: &GameSnapshot) {
        Self::rect(
            menu,
            Vector2::ZERO,
            Vector2::new(650., 1080.),
            Color::from_rgba(0.035, 0.045, 0.055, 0.94),
        );
        Self::text(menu, "CAREER", 70., 80., 54, Color::WHITE);
        Self::text(
            menu,
            &snap.profile.name,
            74.,
            160.,
            25,
            Color::from_rgb(0.67, 0.74, 0.77),
        );
        Self::text(
            menu,
            &format!(
                "{}   /   ${}",
                self.league_label(snap.career.league),
                snap.career.cash
            ),
            74.,
            220.,
            26,
            Color::from_rgb(0.52, 0.78, 0.76),
        );
        for (i, (label, key)) in [
            ("RACE EVENTS", "career_events"),
            ("PROGRESSION", "career_goals"),
            ("GARAGE", "nav:garage"),
            ("DEALERSHIP", "nav:dealer"),
            ("OPTIONS", "options"),
            ("MAIN MENU", "nav:main"),
        ]
        .iter()
        .enumerate()
        {
            self.button(menu, label, key, 70., 345. + i as f32 * 91., 510., 70.);
        }
    }
    fn car_picker(&self, menu: &mut Gd<Control>, snap: &GameSnapshot, y: f32, owned: bool) {
        let cars: Vec<_> = snap
            .cars
            .iter()
            .filter(|c| !owned || snap.career.garage.contains_key(&c.id))
            .collect();
        if matches!(snap.screen, GameScreen::QuickRace | GameScreen::Career) {
            self.button(menu, "◀ CAR", "car_prev", 1060., 865., 210., 55.);
            self.button(menu, "CAR ▶", "car_next", 1550., 865., 210., 55.);
            return;
        }
        let selected = cars
            .iter()
            .position(|c| c.id == snap.selected_car)
            .unwrap_or(0);
        let page = selected / 10;
        for (row, car) in cars.iter().skip(page * 10).take(10).enumerate() {
            self.button(
                menu,
                &format!(
                    "{} {}",
                    if car.id == snap.selected_car {
                        "▶"
                    } else {
                        " "
                    },
                    car.name
                ),
                &format!("car:{}", car.id),
                50.,
                y + row as f32 * 54.,
                450.,
                49.,
            );
        }
        self.button(menu, "◀ PREV", "car_prev", 60., 820., 200., 54.);
        self.button(menu, "NEXT ▶", "car_next", 280., 820., 200., 54.);
    }
    fn checkout_menu(&self, menu: &mut Gd<Control>, snap: &GameSnapshot) {
        let white = Color::WHITE;
        let muted = Color::from_rgb(0.67, 0.74, 0.77);
        let accent = Color::from_rgb(0.52, 0.78, 0.76);
        let total = snap.cart.iter().map(|item| item.cost).sum::<u32>();
        Self::rect(
            menu,
            Vector2::ZERO,
            Vector2::new(1920., 1080.),
            Color::from_rgba(0.035, 0.045, 0.055, 0.98),
        );
        Self::text(menu, "MODIFICATIONS", 80., 65., 48, white);
        Self::text(
            menu,
            "Review your parts before purchasing.",
            84.,
            135.,
            24,
            muted,
        );
        Self::text(menu, "ITEM", 90., 210., 20, muted);
        Self::text(menu, "PRICE", 1040., 210., 20, muted);
        let pages = snap.cart.len().div_ceil(8).max(1);
        let page = self.cart_page.min(pages - 1);
        let selected = snap
            .cart
            .iter()
            .find(|item| item.id == self.cart_selected)
            .or_else(|| snap.cart.get(page * 8));
        for (index, item) in snap.cart.iter().skip(page * 8).take(8).enumerate() {
            let y = 250. + index as f32 * 70.;
            if selected.is_some_and(|selected| selected.id == item.id) {
                Self::chrome(menu, Vector2::new(80., y), Vector2::new(1130., 64.));
            }
            let car = self
                .content
                .cars
                .iter()
                .find(|car| car.id == item.car_id)
                .map(|car| car.name.as_str())
                .unwrap_or(&item.car_id);
            self.button(
                menu,
                &format!("{} — {}", item.label, car),
                &format!("cart_select:{}", item.id),
                90.,
                y,
                900.,
                64.,
            );
            Self::text(menu, &format!("${}", item.cost), 1040., y + 17., 26, white);
        }
        if snap.cart.is_empty() {
            Self::text(menu, "No modifications selected.", 90., 280., 28, muted);
        }
        Self::chrome(menu, Vector2::new(1280., 210.), Vector2::new(560., 420.));
        Self::text(menu, "BALANCE", 1320., 245., 20, muted);
        Self::text(
            menu,
            &format!("${}", snap.career.cash),
            1320.,
            280.,
            34,
            white,
        );
        Self::text(menu, "TOTAL", 1320., 355., 20, muted);
        Self::text(menu, &format!("${total}"), 1320., 390., 40, accent);
        Self::text(menu, "AFTER PURCHASE", 1320., 475., 20, muted);
        Self::text(
            menu,
            &format!("${}", snap.career.cash - i64::from(total)),
            1320.,
            510.,
            34,
            white,
        );
        self.button(menu, "PURCHASE", "checkout", 80., 960., 400., 58.);
        if let Some(child) = menu.get_child(menu.get_child_count() - 1)
            && let Ok(mut button) = child.try_cast::<Button>()
        {
            button.set_disabled(snap.cart.is_empty() || i64::from(total) > snap.career.cash);
        }
        self.button(
            menu,
            "KEEP CUSTOMIZING",
            "nav:custom",
            510.,
            960.,
            440.,
            58.,
        );
        if let Some(item) = selected {
            self.button(
                menu,
                "REMOVE ITEM",
                &format!("cart_remove:{}", item.id),
                990.,
                960.,
                400.,
                58.,
            );
        }
        self.button(menu, "DISCARD ALL", "discard_cart", 1430., 960., 400., 58.);
        if pages > 1 {
            self.button(menu, "PREVIOUS", "cart_prev", 80., 850., 260., 50.);
            Self::text(
                menu,
                &format!("{} / {}", page + 1, pages),
                580.,
                860.,
                24,
                muted,
            );
            self.button(menu, "NEXT", "cart_next", 950., 850., 260., 50.);
        }
    }
    fn custom_menu(&self, menu: &mut Gd<Control>, snap: &GameSnapshot) {
        let white = Color::WHITE;
        let title = match self.custom_page.as_str() {
            "wheels" => "ALLOY WHEELS",
            "vinyl" => "VINYLS",
            "performance" => "TUNING PACK",
            "parts" => "MOD BODY PARTS",
            _ => "PAINT STYLE",
        };
        Self::chrome(menu, Vector2::new(0., 85.), Vector2::new(1000., 90.));
        Self::text(menu, title, 155., 95., 43, white);
        Self::chrome(menu, Vector2::new(120., 175.), Vector2::new(450., 55.));
        Self::text(
            menu,
            &format!("$ {}", snap.career.cash),
            180.,
            180.,
            29,
            white,
        );
        Self::chrome(menu, Vector2::new(1360., 85.), Vector2::new(560., 95.));
        Self::text(
            menu,
            &format!(
                "ITEMS: {}    ${}",
                snap.cart.len(),
                snap.cart.iter().map(|item| item.cost).sum::<u32>()
            ),
            1410.,
            110.,
            28,
            white,
        );
        Self::rect(
            menu,
            Vector2::new(0., 755.),
            Vector2::new(1920., 325.),
            Color::from_rgba(0.035, 0.045, 0.055, 0.96),
        );
        match self.custom_page.as_str() {
            "paint" => {
                self.palette(
                    menu,
                    "PAINT COLOR",
                    "body",
                    self.customization.paint,
                    70.,
                    815.,
                    300.,
                );
                for (index, finish) in ["gloss", "metallic", "matt", "pearl", "flake", "thinfilm"]
                    .iter()
                    .enumerate()
                {
                    self.button(
                        menu,
                        &finish.to_uppercase(),
                        &format!("finish:{finish}"),
                        400. + index as f32 * 230.,
                        815.,
                        220.,
                        62.,
                    );
                }
                Self::text(menu, "Choose paint color and finish", 80., 725., 27, white);
            }
            "wheels" => {
                for (index, style) in ["stock", "sport", "mesh", "deep-dish"].iter().enumerate() {
                    self.button(
                        menu,
                        &style.to_uppercase(),
                        &format!("wheels:{style}"),
                        400. + index as f32 * 340.,
                        815.,
                        320.,
                        62.,
                    );
                }
                self.palette(
                    menu,
                    "WHEEL COLOR",
                    "wheel",
                    self.customization.wheel_paint,
                    70.,
                    815.,
                    300.,
                );
                let metadata: serde_json::Value = serde_json::from_str(
                    &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                )
                .unwrap_or_default();
                if metadata["cars"].as_array().is_some_and(|cars| {
                    cars.iter().any(|car| {
                        car["code"].as_str() == Some(&snap.selected_car)
                            && car["plate_socket"].is_object()
                    })
                }) {
                    self.button(menu, "PLATE STYLE", "plate_style", 70., 655., 300., 50.);
                    let mut text = godot::classes::LineEdit::new_alloc();
                    text.set_text(&self.customization.plate_text);
                    text.set_position(Vector2::new(70., 715.));
                    text.set_size(Vector2::new(300., 45.));
                    text.connect("text_submitted", &self.base().callable("plate_name"));
                    menu.add_child(&text);
                }
            }
            "vinyl" => {
                Self::rect(
                    menu,
                    Vector2::new(45., 265.),
                    Vector2::new(440., 620.),
                    Color::from_rgba(0.015, 0.02, 0.04, 0.88),
                );
                let mut layers = godot::classes::OptionButton::new_alloc();
                for (index, layer) in self.customization.vinyls.iter().enumerate() {
                    layers.add_item(&format!(
                        "LAYER {}: {}",
                        index + 1,
                        if layer.design_id.is_empty() {
                            layer.shape.as_str()
                        } else {
                            layer.design_id.as_str()
                        }
                    ));
                }
                if !self.customization.vinyls.is_empty() {
                    layers.select(self.vinyl_layer as i32);
                }
                layers.set_position(Vector2::new(65., 280.));
                layers.set_size(Vector2::new(400., 44.));
                layers.connect("item_selected", &self.base().callable("vinyl_selected"));
                menu.add_child(&layers);
                if let Some(categories) = self.decal_catalog["categories"].as_array() {
                    let mut category = godot::classes::OptionButton::new_alloc();
                    for item in categories {
                        category.add_item(item["name"].as_str().unwrap_or("DECALS"));
                    }
                    if !categories.is_empty() {
                        category.select(self.decal_category.min(categories.len() - 1) as i32);
                    }
                    category.set_position(Vector2::new(65., 335.));
                    category.set_size(Vector2::new(400., 44.));
                    category.connect(
                        "item_selected",
                        &self.base().callable("decal_category_selected"),
                    );
                    menu.add_child(&category);
                    let mut design = godot::classes::OptionButton::new_alloc();
                    if let Some(ids) =
                        self.decal_catalog["categories"][self.decal_category]["design_ids"]
                            .as_array()
                    {
                        for id in ids {
                            let entry =
                                self.decal_catalog["designs"]
                                    .as_array()
                                    .and_then(|designs| {
                                        designs.iter().find(|design| design["id"] == *id)
                                    });
                            design.add_item(
                                entry
                                    .and_then(|design| design["native_label"].as_str())
                                    .unwrap_or("DECAL"),
                            );
                        }
                        if !ids.is_empty() {
                            let selected = self
                                .customization
                                .vinyls
                                .get(self.vinyl_layer)
                                .map(|layer| layer.design_id.as_str())
                                .unwrap_or("");
                            design.select(
                                ids.iter()
                                    .position(|id| id.as_str() == Some(selected))
                                    .unwrap_or(0) as i32,
                            );
                        }
                    }
                    design.set_position(Vector2::new(65., 390.));
                    design.set_size(Vector2::new(400., 44.));
                    design.connect(
                        "item_selected",
                        &self.base().callable("decal_design_selected"),
                    );
                    menu.add_child(&design);
                }
                if let Some(layer) = self.customization.vinyls.get(self.vinyl_layer) {
                    self.palette(menu, "VINYL COLOR", "vinyl", layer.color, 65., 445., 400.);
                }
                for (index, (label, key)) in [
                    ("+ LAYER", "add"),
                    ("DELETE", "remove"),
                    ("TO FRONT", "front"),
                    ("TO BACK", "back"),
                    ("X -", "left"),
                    ("X +", "right"),
                    ("Y -", "up"),
                    ("Y +", "down"),
                    ("ROTATE +", "rotate"),
                    ("ROTATE -", "rotate_back"),
                    ("WIDTH +", "scale_x_up"),
                    ("WIDTH -", "scale_x_down"),
                    ("HEIGHT +", "scale_y_up"),
                    ("HEIGHT -", "scale_y_down"),
                ]
                .iter()
                .enumerate()
                {
                    self.button(
                        menu,
                        label,
                        &format!("vinyl:{key}"),
                        65. + (index % 2) as f32 * 205.,
                        510. + (index / 2) as f32 * 50.,
                        195.,
                        44.,
                    );
                }
                if let Some(layer) = self.customization.vinyls.get(self.vinyl_layer) {
                    Self::text(
                        menu,
                        &format!(
                            "X {:.2}   Y {:.2}   ROT {:.1}deg\nWIDTH {:.2}   HEIGHT {:.2}",
                            layer.position[0],
                            layer.position[1],
                            layer.rotation.to_degrees(),
                            layer.scale[0],
                            layer.scale[1]
                        ),
                        600.,
                        810.,
                        28,
                        white,
                    );
                }
            }
            "performance" => {
                for (index, (name, stage)) in [
                    ("engine", self.customization.engine),
                    ("transmission", self.customization.transmission),
                    ("suspension", self.customization.suspension),
                    ("tyres", self.customization.tyres),
                ]
                .iter()
                .enumerate()
                {
                    self.button(
                        menu,
                        &format!("{}  STAGE {}", name.to_uppercase(), stage),
                        &format!("upgrade:{name}"),
                        65. + index as f32 * 370.,
                        810.,
                        350.,
                        60.,
                    );
                }
                for (index, name) in ["STEERING", "GEARING", "TYRE GRIP", "WEIGHT BALANCE"]
                    .iter()
                    .enumerate()
                {
                    self.button(
                        menu,
                        &format!("{} {:.0}%", name, self.customization.tuning[index] * 100.),
                        &format!("tune:{index}"),
                        65. + index as f32 * 450.,
                        725.,
                        430.,
                        50.,
                    );
                }
            }
            "parts" => {
                if let Some(car) = snap.cars.iter().find(|car| car.id == snap.selected_car) {
                    let mut row = 0;
                    for (slot, parts) in &car.parts {
                        for id in std::iter::once("stock").chain(parts.iter().map(String::as_str)) {
                            self.button(
                                menu,
                                &format!("{}: {}", slot.to_uppercase(), id),
                                &format!("part:{slot}:{id}"),
                                70. + (row % 4) as f32 * 450.,
                                775. + (row / 4) as f32 * 60.,
                                430.,
                                52.,
                            );
                            row += 1;
                        }
                    }
                    if row == 0 {
                        Self::text(
                            menu,
                            "No compatible body or interior parts available",
                            130.,
                            815.,
                            30,
                            white,
                        );
                    }
                }
            }
            _ => {}
        }
        for (index, (title, page)) in [
            ("PAINT", "paint"),
            ("WHEELS", "wheels"),
            ("VINYLS", "vinyl"),
            ("PERFORMANCE", "performance"),
            ("BODY PARTS", "parts"),
        ]
        .iter()
        .enumerate()
        {
            self.button(
                menu,
                title,
                &format!("custom_page:{page}"),
                370. + index as f32 * 300.,
                940.,
                285.,
                58.,
            );
        }
        self.button(
            menu,
            if self.custom_return == GameScreen::QuickRace {
                "DONE"
            } else {
                "SHOPPING CART"
            },
            if self.custom_return == GameScreen::QuickRace {
                "custom_done"
            } else {
                "nav:checkout"
            },
            65.,
            940.,
            280.,
            58.,
        );
    }
    fn build_hud(&mut self) {
        let mut hud = self.hud.take().unwrap();
        for mut child in hud.get_children().iter_shared() {
            child.queue_free();
        }
        self.labels.clear();
        self.rpm_bar = None;
        self.nitrous_bar = None;
        let white = Color::WHITE;
        Self::rect(
            &mut hud,
            Vector2::new(40., 40.),
            Vector2::new(350., 125.),
            Color::from_rgba(0.035, 0.045, 0.055, 0.85),
        );
        Self::text(&mut hud, "OVERSTEER", 65., 55., 27, white);
        for (id, x, y, size, color) in [
            ("lap", 120., 965., 25, white),
            ("position", 1540., 55., 30, white),
            ("time", 65., 105., 25, white),
            ("opponents", 1540., 115., 20, white),
            ("speed", 1525., 850., 68, white),
            ("gear", 1790., 873., 46, white),
            ("rpm", 1525., 945., 20, white),
            ("nitrous", 1570., 625., 22, Color::from_rgb(0.25, 0.65, 1.)),
            ("drift", 830., 260., 54, white),
            ("family", 650., 95., 27, white),
            ("message", 560., 440., 120, white),
            ("minimap", 107., 1004., 18, white),
        ] {
            let mut label = Self::text(&mut hud, "", x, y, size, color);
            if id == "message" {
                label.set_size(Vector2::new(800., 200.));
                label.set_horizontal_alignment(godot::global::HorizontalAlignment::CENTER);
                label.set_vertical_alignment(godot::global::VerticalAlignment::CENTER);
                label.add_theme_color_override("font_shadow_color", Color::BLACK);
                label.add_theme_constant_override("shadow_offset_x", 3);
                label.add_theme_constant_override("shadow_offset_y", 3);
            }
            if id == "position" || id == "opponents" {
                label.add_theme_color_override("font_shadow_color", Color::BLACK);
                label.add_theme_constant_override("shadow_offset_x", 2);
                label.add_theme_constant_override("shadow_offset_y", 2);
            }
            self.labels.insert(id.into(), label);
        }
        // Independent instruments keep the road visible and use no source UI art.
        let panel = Color::from_rgba(0.035, 0.045, 0.055, 0.85);
        Self::rect(
            &mut hud,
            Vector2::new(1500., 795.),
            Vector2::new(380., 245.),
            panel,
        );
        Self::rect(
            &mut hud,
            Vector2::new(90., 720.),
            Vector2::new(260., 295.),
            panel,
        );
        Self::rect(
            &mut hud,
            Vector2::new(1510., 40.),
            Vector2::new(370., 330.),
            panel,
        );
        Self::text(&mut hud, "GEAR", 1780., 844., 18, white);
        Self::text(&mut hud, "NITROUS", 1525., 995., 17, white);
        for (position, width, color, rpm) in [
            (
                Vector2::new(1525., 822.),
                330.,
                Color::from_rgb(0.55, 0.82, 0.8),
                true,
            ),
            (
                Vector2::new(1625., 1005.),
                230.,
                Color::from_rgb(0.55, 0.72, 0.9),
                false,
            ),
        ] {
            Self::rect(
                &mut hud,
                position,
                Vector2::new(width, 8.),
                Color::from_rgb(0.18, 0.22, 0.25),
            );
            let mut fill = ColorRect::new_alloc();
            fill.set_position(position);
            fill.set_size(Vector2::new(width, 8.));
            fill.set_color(color);
            fill.set_mouse_filter(godot::classes::control::MouseFilter::IGNORE);
            hud.add_child(&fill);
            if rpm {
                self.rpm_bar = Some(fill);
            } else {
                self.nitrous_bar = Some(fill);
            }
        }
        if let Some(race) = self.game.as_ref().unwrap().frame_snapshot().race
            && let Some(track) = self.content.tracks.iter().find(|t| t.id == race.track_id)
        {
            let (center, scale) = map_transform(&track.points);
            let mut line = godot::classes::Line2D::new_alloc();
            let mut points: Vec<Vector2> = track
                .points
                .iter()
                .map(|p| Vector2::new(219.5, 839.5) + (Vector2::new(p[0], p[2]) - center) * scale)
                .collect();
            if let Some(first) = points.first().copied() {
                points.push(first);
            }
            line.set_points(&PackedVector2Array::from(points));
            line.set_default_color(Color::from_rgb(0.5, 0.7, 1.));
            line.set_width(3.);
            hud.add_child(&line);
            let dot = Self::text(
                &mut hud,
                "●",
                170.,
                910.,
                18,
                Color::from_rgb(1., 0.2, 0.15),
            );
            self.labels.insert("map_player".into(), dot);
        }
        for label in self.labels.values_mut() {
            label.move_to_front();
        }
        self.hud = Some(hud);
    }
    // Keep staged setup explicit so fixture overrides and input sampling order remain visible.
    #[allow(clippy::field_reassign_with_default)]
    fn showdown_avatar(&mut self, _snap: &GameSnapshot, visible: bool) {
        if visible {
            self.show_driver("grid", Vector3::new(3.4, 0., -0.8));
        } else if self.avatar_key == "grid" {
            if let Some(mut actor) = self.avatar.take() {
                actor.queue_free();
            }
            self.avatar_key.clear();
        }
    }
    fn show_driver(&mut self, role: &str, position: Vector3) {
        if self.avatar_key == role {
            return;
        }
        if let Some(mut actor) = self.avatar.take() {
            actor.queue_free();
        }
        let mut actor = Self::load_scene("res://assets/driver/streetwear.glb");
        actor.set_position(position);
        self.base_mut().add_child(&actor);
        actor.set_rotation(Vector3::new(0., std::f32::consts::PI, 0.));
        play_source_animation(&mut actor.clone().upcast(), "CommonMale_CrewIdle01", true);
        self.avatar_report = serde_json::json!({"model":"fixed_streetwear_driver", "source":"driver/streetwear.glb", "customizable":false, "visual_acceptance":"pending"});
        self.avatar = Some(actor);
        self.avatar_key = role.into();
    }
    // Keep the existing explicit presentation branches during tooling-only adoption.
    #[allow(clippy::if_same_then_else)]
    fn refresh(&mut self) {
        let mut snap = self.game.as_ref().unwrap().frame_snapshot();
        if self.replay {
            if !self.replay_frames.is_empty() {
                snap.race = Some(
                    self.replay_frames[self.replay_cursor.min(self.replay_frames.len() - 1)]
                        .clone(),
                );
                if self.scenario_frame.is_multiple_of(3) {
                    self.replay_cursor = (self.replay_cursor + 1) % self.replay_frames.len();
                }
            }
        } else if snap.screen == GameScreen::Race
            && self.scenario_frame.is_multiple_of(3)
            && let Some(race) = &snap.race
        {
            if race.elapsed < 0.05 {
                self.replay_frames.clear();
            }
            if self.replay_frames.len() < 12000 {
                self.replay_frames.push(race.clone());
            }
        }
        let presentation_role = if snap.screen == GameScreen::Avatar {
            "CreateCharacter"
        } else if snap.screen != GameScreen::MainMenu {
            ""
        } else if self.credits {
            "ExtrasToCredits"
        } else if self.extras {
            "MainToExtras"
        } else if self.options {
            "MainToOptions"
        } else if self.title {
            "TunnelStart"
        } else {
            "StartToMain"
        };
        let presentation_changed = presentation_role != self.previous_presentation;
        self.previous_presentation = presentation_role.into();
        let screen = format!("{:?}", snap.screen);
        let screen_changed = screen != self.previous_screen;
        let car_changed = snap.selected_car != self.previous_car;
        if screen_changed || car_changed {
            self.customization = snap.selected_customization.clone();
            self.rebuild_menu();
            self.previous_screen = screen;
            self.previous_car = snap.selected_car.clone();
        }
        let racing = matches!(
            snap.screen,
            GameScreen::Race | GameScreen::Paused | GameScreen::Results | GameScreen::Grid
        );
        let showdown = snap.screen == GameScreen::Grid;
        self.showdown_avatar(&snap, showdown);
        let paint_presentation =
            snap.screen == GameScreen::Customization && self.custom_page == "paint";
        let main_presentation = snap.screen == GameScreen::MainMenu;
        let profile_presentation = snap.screen == GameScreen::Avatar;
        let tunnel_presentation = profile_presentation;
        let showroom = !racing || showdown;
        if let Some(sun) = &mut self.sun {
            sun.set_visible(!showroom && !tunnel_presentation);
        }
        if let Some(environment) = &mut self.environment {
            environment.set_background(if showroom {
                godot::classes::environment::BgMode::COLOR
            } else {
                godot::classes::environment::BgMode::SKY
            });
            if showroom {
                environment.set_bg_color(Color::from_rgb(0.025, 0.03, 0.04));
            }
            environment.set_ambient_light_color(if showroom {
                Color::from_rgb(0.68, 0.72, 0.78)
            } else {
                Color::from_rgb(0.45, 0.53, 0.7)
            });
            environment.set_ambient_light_energy(if showroom { 0.55 } else { 0.8 });
        }
        if let Some(main) = &mut self.main_stage {
            main.set_visible(tunnel_presentation);
            // Scene-relative source marker placement: Character_CreateAvatar is
            // [-55.76,-0.99,0.42], while the shared tunnel child is centered on MainTarget.
            for child in main.get_children().iter_shared() {
                if child.clone().try_cast::<godot::classes::Light3D>().is_ok() {
                    continue;
                }
                if let Ok(mut geometry) = child.try_cast::<Node3D>() {
                    geometry.set_position(if profile_presentation {
                        Vector3::new(55.76, 0.99, -0.42)
                    } else {
                        Vector3::new(-36.74981, -1.566545, -2.374297)
                    });
                }
            }
            if screen_changed || presentation_changed {
                set_tunnel_palette(
                    main,
                    presentation_style(presentation_role).0,
                    if profile_presentation { 3.0 } else { 0.15 },
                );
                set_creator_room_visibility(main, profile_presentation);
                set_creator_tunnel_culling(main, profile_presentation);
                for child in main.get_children().iter_shared() {
                    if let Ok(mut light) = child.try_cast::<godot::classes::OmniLight3D>() {
                        // Reference presentation-light adapter; original Spotlight behavior
                        // and native light-mode coefficients remain unported.
                        let x = light.get_position().x;
                        // Paired native diagnostics show that rear fill creates a
                        // harsh central diffuse terminator on the source actor.
                        // Symmetric front fill is a reference-lighting adapter.
                        light.set_position(Vector3::new(
                            x,
                            2.,
                            if profile_presentation || x < 0. {
                                2.
                            } else {
                                -2.
                            },
                        ));
                        light.set_color(if profile_presentation {
                            Color::from_rgb(1., 0.95, 0.9)
                        } else {
                            Color::from_rgb(0.9, 0.05, 0.45)
                        });
                    }
                }
            }
        }
        if let Some(scene) = &mut self.scene {
            scene.set_visible(racing && !showdown);
        }
        if let Some(stage) = &mut self.stage {
            stage.set_visible((!racing || showdown) && !tunnel_presentation && !paint_presentation);
        }
        if let Some(stage) = &mut self.paint_stage {
            stage.set_visible(paint_presentation);
        }
        if let Some(hud) = &mut self.hud {
            hud.set_visible(snap.screen == GameScreen::Race);
        }
        if racing {
            if let Some(mut preview) = self.preview.take() {
                preview.queue_free();
            }
            if let Some(race) = snap.race {
                let race_key = format!("{}:{}:{}", race.event_id, race.track_id, race.round);
                if self.loaded_race != race_key {
                    let mut paths = vec![format!("res://assets/worlds/{}.glb", race.track_id)];
                    for racer in &race.racers {
                        if let Some(car) = self.content.cars.iter().find(|c| c.id == racer.car_id) {
                            paths.push(car.model_path.clone());
                        }
                    }
                    self.begin_loading(paths, format!("race:{race_key}"));
                    return;
                }
                if self.cars.len() != race.racers.len() {
                    self.car_effects.clear();
                    for mut c in self.cars.drain(..) {
                        c.queue_free();
                    }
                    let index = self
                        .content
                        .tracks
                        .iter()
                        .position(|t| t.id == race.track_id)
                        .unwrap_or(0);
                    self.build_track(index);
                    for racer in &race.racers {
                        let path = self
                            .content
                            .cars
                            .iter()
                            .find(|c| c.id == racer.car_id)
                            .map(|c| c.model_path.as_str())
                            .unwrap_or("");
                        let mut car = Self::load_scene(path);
                        car.set_name(format!("RaceCar_{}", self.cars.len()).as_str());
                        self.base_mut().add_child(&car);
                        car.set_meta(
                            "oversteer_racer_index",
                            &(self.cars.len() as i64).to_variant(),
                        );
                        car.set_meta("oversteer_car_id", &racer.car_id.to_variant());
                        self.tint(&mut car, &racer.car_id, &racer.customization);
                        if self.cars.is_empty() {
                            self.swap_wheels(&mut car, &racer.car_id, &racer.customization);
                            self.apply_kits(&mut car, &racer.car_id, &racer.customization);
                        }
                        let metadata: serde_json::Value = serde_json::from_str(
                            &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                        )
                        .unwrap_or_default();
                        let definition = metadata["cars"].as_array().and_then(|cars| {
                            cars.iter()
                                .find(|c| c["code"].as_str() == Some(&racer.car_id))
                        });
                        let length = definition
                            .and_then(|c| c["length_m"].as_f64())
                            .unwrap_or(4.2) as f32;
                        let width = definition
                            .and_then(|c| c["width_m"].as_f64())
                            .unwrap_or(1.8) as f32;
                        self.car_effects
                            .push(effects::CarEffects::new(&mut car, length, width));
                        self.cars.push(car);
                    }
                    self.build_hud();
                    if race.spectating {
                        self.rebuild_menu();
                    }
                }
                for (i, racer) in race.racers.iter().enumerate() {
                    if let Some(effect) = self.car_effects.get_mut(i) {
                        effect.update(
                            racer,
                            if racer.is_player {
                                Some(self.last_input)
                            } else {
                                None
                            },
                            snap.screen != GameScreen::Race,
                        );
                    }
                    let car = &mut self.cars[i];
                    car.set_position(v3(racer.position));
                    car.set_quaternion(
                        Quaternion::new(
                            racer.rotation[0],
                            racer.rotation[1],
                            racer.rotation[2],
                            racer.rotation[3],
                        ) * Quaternion::from_axis_angle(Vector3::UP, std::f32::consts::PI),
                    );
                    car.set_visible(!showdown || i == self.selected_rival);
                    if showdown {
                        car.set_position(Vector3::new(1.7, 0., 0.));
                        car.set_rotation(Vector3::ZERO);
                    }
                    let handling = self
                        .content
                        .cars
                        .iter()
                        .find(|c| c.id == racer.car_id)
                        .map(|c| &c.handling);
                    animate_wheels(car, racer, if showdown { None } else { handling });
                }
                if let Some(label) = self.labels.get_mut("spectator_odds") {
                    let odds = race
                        .spectator_odds
                        .get(self.selected_rival)
                        .copied()
                        .unwrap_or(0.);
                    label.set_text(&format!("ODDS {:.2}:1    CASH ${}", odds, snap.career.cash));
                }
                if let Some(player) = race.racers.get(if race.spectating {
                    self.selected_rival.min(race.racers.len().saturating_sub(1))
                } else {
                    0
                }) {
                    let pos = v3(player.position);
                    let q = Quaternion::new(
                        player.rotation[0],
                        player.rotation[1],
                        player.rotation[2],
                        player.rotation[3],
                    );
                    let forward = q * Vector3::new(0., 0., 1.);
                    if let Some(cam) = &mut self.camera {
                        let orbit = self.wheel_audit && !showdown;
                        let angle = ((self.input_frame.saturating_sub(1) / 30).min(11) as f32
                            * 30.)
                            .to_radians();
                        let target = if orbit {
                            // Stay inside trackside fences. Orthographic inspection
                            // keeps the entire car readable from the close side views.
                            let radius = (1.2 / angle.sin().abs().max(0.01)).min(4.8);
                            cam.set_projection(
                                godot::classes::camera_3d::ProjectionType::ORTHOGONAL,
                            );
                            cam.set_size(3.6);
                            pos + q * Vector3::new(angle.sin() * radius, 1.8, -angle.cos() * radius)
                        } else if showdown {
                            Vector3::new(4.8, 2.1, -9.6)
                        } else if self.replay {
                            pos + Vector3::new(
                                (self.clock as f32 * 0.2).sin() * 11.,
                                4.,
                                (self.clock as f32 * 0.2).cos() * 11.,
                            )
                        } else {
                            pos - forward * 4.3 + Vector3::UP * 2.2
                        };
                        let camera_pos = if showdown || screen_changed || orbit {
                            target
                        } else {
                            cam.get_position().lerp(target, 0.12)
                        };
                        cam.set_position(camera_pos);
                        cam.look_at(if orbit {
                            pos + Vector3::UP * 0.75
                        } else if showdown {
                            Vector3::new(1.7, 0.9, 0.)
                        } else {
                            pos + forward * 5.5 + Vector3::UP * 0.85
                        });
                        cam.set_fov(if showdown || orbit {
                            48.
                        } else {
                            62. + (player.speed_kph / 250.).min(1.) * 9.
                        });
                    }
                    if let Some(track) = self.content.tracks.iter().find(|t| t.id == race.track_id)
                    {
                        let (center, scale) = map_transform(&track.points);
                        if let Some(dot) = self.labels.get_mut("map_player") {
                            dot.set_position(
                                Vector2::new(214.5, 828.5)
                                    + (Vector2::new(pos.x, pos.z) - center) * scale,
                            );
                        }
                    }
                    if let Some(bar) = &mut self.rpm_bar {
                        let redline = self
                            .content
                            .cars
                            .iter()
                            .find(|car| car.id == player.car_id)
                            .map_or(7000., |car| car.handling.redline);
                        let fraction = (player.rpm / redline).clamp(0., 1.);
                        bar.set_size(Vector2::new(330. * fraction, 8.));
                        bar.set_color(if fraction > 0.9 {
                            Color::from_rgb(1., 0.35, 0.25)
                        } else {
                            Color::from_rgb(0.55, 0.82, 0.8)
                        });
                    }
                    if let Some(bar) = &mut self.nitrous_bar {
                        bar.set_size(Vector2::new(230. * player.nitrous.clamp(0., 1.), 8.));
                    }
                    let values = [
                        (
                            "family",
                            format!(
                                "{}{}{}",
                                if race.total_rounds > 1 {
                                    format!("ROUND {} / {}   ", race.round, race.total_rounds)
                                } else {
                                    String::new()
                                },
                                if race.mode == RaceMode::DriftKing {
                                    format!(
                                        "TIME {:.1}   SCORE {:.0}",
                                        (race.target - race.elapsed).max(0.),
                                        player.drift_score
                                    )
                                } else if race.mode == RaceMode::DriftEndurance {
                                    format!(
                                        "CHAIN {:.0}   TARGET {:.0}",
                                        player.chain_score, race.target
                                    )
                                } else if race.mode == RaceMode::Drift {
                                    format!("SCORE {:.0} / {:.0}", player.drift_score, race.target)
                                } else if race.mode.is_drift() {
                                    format!(
                                        "SCORE {:.0} / {:.0}   ATTEMPTS {}",
                                        player.drift_score, race.target, race.lives
                                    )
                                } else if race.mode == RaceMode::SpeedChallenge {
                                    format!(
                                        "TARGET {:.0} {}",
                                        race.target
                                            * 3.6
                                            * if self.speed_mph { 0.621371 } else { 1. },
                                        if self.speed_mph { "MPH" } else { "KPH" }
                                    )
                                } else if race.mode == RaceMode::TeamRace {
                                    format!(
                                        "TEAM POINTS {}",
                                        race.team_scores
                                            .iter()
                                            .map(|s| format!("{:.0}", s))
                                            .collect::<Vec<_>>()
                                            .join(" : ")
                                    )
                                } else if matches!(
                                    race.mode,
                                    RaceMode::PerfectLap | RaceMode::LapTime | RaceMode::TimeAttack
                                ) {
                                    format!(
                                        "TARGET {:.2}s   {}",
                                        race.target,
                                        if player.clean_lap {
                                            "CLEAN LAP"
                                        } else {
                                            "INVALID LAP"
                                        }
                                    )
                                } else {
                                    String::new()
                                },
                                if player.eliminated {
                                    "  ELIMINATED"
                                } else {
                                    ""
                                }
                            ),
                        ),
                        ("lap", format!("LAP {} / {}", player.lap.max(1), race.laps)),
                        (
                            "position",
                            format!("POSITION  {} / {}", race.position, race.racers.len()),
                        ),
                        (
                            "time",
                            format!(
                                "TIME  {:02}:{:05.2}",
                                (race.elapsed / 60.) as u32,
                                race.elapsed % 60.
                            ),
                        ),
                        (
                            "speed",
                            format!(
                                "{:03}",
                                (player.speed_kph * if self.speed_mph { 0.621371 } else { 1. })
                                    as u32
                            ),
                        ),
                        (
                            "gear",
                            if player.gear < 0 {
                                "R".into()
                            } else if player.gear == 0 {
                                "N".into()
                            } else {
                                player.gear.to_string()
                            },
                        ),
                        (
                            "rpm",
                            if self.speed_mph {
                                "MPH".into()
                            } else {
                                "KPH".into()
                            },
                        ),
                        ("nitrous", String::new()),
                        (
                            "drift",
                            if race.drift_combo > 1. {
                                format!("{:.0}  x{:.1}", player.drift_score, race.drift_combo)
                            } else {
                                String::new()
                            },
                        ),
                        (
                            "message",
                            if race.countdown > 0. {
                                format!("{}", race.countdown.ceil() as u32)
                            } else if race.elapsed < 0.8 {
                                "GO".into()
                            } else {
                                race.message.clone()
                            },
                        ),
                        (
                            "opponents",
                            (if race.standings.is_empty() {
                                (0..race.racers.len()).collect::<Vec<_>>()
                            } else {
                                race.standings.clone()
                            })
                            .iter()
                            .filter_map(|index| race.racers.get(*index))
                            .enumerate()
                            .map(|(i, racer)| format!("{}  {}", i + 1, racer.name))
                            .collect::<Vec<_>>()
                            .join("\n"),
                        ),
                        ("minimap", String::new()),
                    ];
                    for (id, text) in values {
                        if let Some(label) = self.labels.get_mut(id) {
                            if id == "message" {
                                label.add_theme_font_size_override(
                                    "font_size",
                                    if race.countdown > 0. || race.elapsed < 0.8 {
                                        120
                                    } else {
                                        32
                                    },
                                );
                            }
                            label.set_text(&text);
                        }
                    }
                }
            }
        } else {
            self.car_effects.clear();
            for mut c in self.cars.drain(..) {
                c.queue_free();
            }
            if car_changed || screen_changed || presentation_changed || self.preview.is_none() {
                if let Some(mut p) = self.preview.take() {
                    p.queue_free();
                }
                if let Some(car) = self
                    .content
                    .cars
                    .iter()
                    .find(|c| {
                        c.id == if profile_presentation {
                            "GT4_MITS0001"
                        } else {
                            snap.selected_car.as_str()
                        }
                    })
                    .cloned()
                {
                    let mut instance = Self::load_scene(&car.model_path);
                    instance.set_position(Vector3::ZERO);
                    self.base_mut().add_child(&instance);
                    if profile_presentation {
                        // Native StartToMain's CarColour is byte RGB160/160/160.
                        let presentation = Customization {
                            paint: if profile_presentation {
                                [0.65, 0.65, 0.65, 1.]
                            } else {
                                presentation_style(presentation_role).1
                            },
                            ..Customization::default()
                        };
                        self.tint(&mut instance, &car.id, &presentation);
                    } else {
                        self.tint(&mut instance, &car.id, &self.customization);
                        self.swap_wheels(&mut instance, &car.id, &self.customization);
                        self.apply_kits(&mut instance, &snap.selected_car, &self.customization);
                    }
                    self.preview = Some(instance);
                }
            }
            if snap.screen == GameScreen::Podium {
                self.show_driver("podium", Vector3::new(2.3, 0., 0.));
            } else {
                if let Some(mut actor) = self.avatar.take() {
                    actor.queue_free();
                }
                self.avatar_key.clear();
            }
            if let Some(car) = &mut self.preview {
                if main_presentation {
                    car.set_position(Vector3::ZERO);
                    car.set_rotation(Vector3::new(0., std::f32::consts::PI - 0.35, 0.));
                } else if profile_presentation {
                    // Source CreateAvatar_Car minus Character_CreateAvatar. The donor
                    // Evo and its facing are a presentation proxy, not recovered Car1 identity.
                    car.set_position(Vector3::new(-1.34, 0.03, -1.11));
                    car.set_rotation(Vector3::new(0., std::f32::consts::PI, 0.));
                } else if paint_presentation {
                    car.set_position(Vector3::ZERO);
                    // Recovered native pose yaw, plus donor -Z to native +Z forward adapter.
                    car.set_rotation(Vector3::new(
                        0.,
                        1.570000052 + std::f32::consts::PI + self.preview_angle.unwrap_or(0.),
                        0.,
                    ));
                } else {
                    car.set_rotation(Vector3::new(
                        0.,
                        if snap.screen == GameScreen::Checkout {
                            -std::f32::consts::FRAC_PI_2
                        } else {
                            self.preview_angle.unwrap_or(self.clock as f32 * 0.10)
                        },
                        0.,
                    ));
                }
            }
            if let Some(cam) = &mut self.camera {
                if paint_presentation {
                    let chassis = self
                        .preview
                        .as_ref()
                        .and_then(world_mesh_bounds)
                        .map(|b| (b[0] + b[1]) * 0.5)
                        .unwrap_or(Vector3::new(0., 0.7, 0.));
                    // Exact Paintshop end offsets in the recovered pose's local basis;
                    // donor body center replaces unavailable DRIVER_CHASS. Component
                    // matrix conventions remain an explicit renderer adapter.
                    let offset = Basis::from_axis_angle(Vector3::UP, 1.570000052)
                        * Vector3::new(-3., 1., 0.);
                    if self.preview_angle.is_some() {
                        // Inspection rotates the donor inside the booth. Keep the eye
                        // inside too, then fit its actual bounds above the lower UI.
                        let booth_basis =
                            Basis::from_axis_angle(Vector3::UP, 1.570000052 + std::f32::consts::PI);
                        cam.set_position(chassis + booth_basis * Vector3::new(-2.8, 1.1, 2.8));
                        cam.look_at(chassis - Vector3::new(0., 0.2, 0.));
                        let fov = self
                            .preview
                            .as_ref()
                            .and_then(world_mesh_bounds)
                            .map(|bounds| {
                                inspection_camera_fov(
                                    bounds,
                                    cam.get_global_transform(),
                                    1920. / 1080.,
                                )
                            })
                            .unwrap_or(script_camera_fov(120.));
                        cam.set_fov(fov);
                    } else {
                        cam.set_position(chassis + offset);
                        cam.look_at(chassis);
                        cam.set_fov(script_camera_fov(120.));
                    }
                    return;
                }
                if main_presentation {
                    cam.set_position(Vector3::new(5.5, 2.4, 6.8));
                    cam.look_at(Vector3::new(-1.8, 0.7, 0.));
                    cam.set_fov(45.);
                    return;
                }
                cam.set_position(Vector3::new(4.4, 2.2, 5.6));
                cam.look_at(
                    if snap.screen == GameScreen::MainMenu
                        || (snap.screen == GameScreen::Career && !self.event_picker)
                    {
                        Vector3::new(0., 0.7, 0.)
                    } else {
                        Vector3::new(-1.3, 0.7, 0.)
                    },
                );
                cam.set_fov(45.);
            }
        }
    }
    fn apply_plate(&self, node: &mut Gd<Node3D>, car_id: &str, custom: &Customization) {
        let metadata: serde_json::Value = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
        )
        .unwrap_or_default();
        let Some(socket) = metadata["cars"]
            .as_array()
            .and_then(|cars| cars.iter().find(|c| c["code"].as_str() == Some(car_id)))
            .map(|car| &car["plate_socket"])
            .filter(|s| s.is_object())
        else {
            return;
        };
        let vector = |key: &str| -> Vector3 {
            let a = &socket[key];
            Vector3::new(
                a[0].as_f64().unwrap_or(0.) as f32,
                a[1].as_f64().unwrap_or(0.) as f32,
                a[2].as_f64().unwrap_or(0.) as f32,
            )
        };
        let center = vector("center");
        let normal = vector("normal");
        let basis = Basis::from_cols(vector("right"), vector("up"), normal);
        let width = socket["size"][0].as_f64().unwrap_or(0.32) as f32;
        let height = socket["size"][1].as_f64().unwrap_or(0.16) as f32;
        let mut mesh = godot::classes::QuadMesh::new_gd();
        mesh.set_size(Vector2::new(width, height));
        let mut material = StandardMaterial3D::new_gd();
        material.set_texture(
            godot::classes::base_material_3d::TextureParam::ALBEDO,
            &godot::tools::load::<godot::classes::Texture2D>(
                "res://assets/ui/native/named/LPlate_GB_01.png",
            ),
        );
        material.set_albedo(if custom.plate_style == "dark" {
            Color::from_rgb(0.12, 0.12, 0.14)
        } else {
            Color::WHITE
        });
        let mut surface = MeshInstance3D::new_alloc();
        surface.set_name("CustomLicensePlate");
        surface.set_mesh(&mesh);
        surface.set_material_override(&material);
        surface.set_transform(Transform3D::new(basis, center + normal * 0.001));
        node.add_child(&surface);
        let mut text = godot::classes::Label3D::new_alloc();
        text.set_name("LicensePlateText");
        text.set_text(&custom.plate_text);
        text.set_font(&godot::tools::load::<godot::classes::Font>(
            "res://assets/ui/native/fonts/lplate-1080.fnt",
        ));
        text.set_font_size(64);
        text.set_outline_size(0);
        text.set_modulate(if custom.plate_style == "dark" {
            Color::WHITE
        } else {
            Color::BLACK
        });
        text.set_pixel_size(width * 0.82 / (custom.plate_text.chars().count().max(1) as f32 * 38.));
        text.set_transform(Transform3D::new(basis, center + normal * 0.003));
        node.add_child(&text);
    }
    fn apply_kits(&self, node: &mut Gd<Node3D>, car_id: &str, custom: &Customization) {
        self.apply_plate(node, car_id, custom);
        let data: serde_json::Value = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/kits.json").to_string(),
        )
        .unwrap_or_default();
        let mut selected = custom
            .parts
            .values()
            .cloned()
            .collect::<std::collections::BTreeSet<_>>();
        selected.insert(custom.body_kit.clone());
        selected.insert(custom.interior_kit.clone());
        if let Some(kits) = data["kits"].as_array() {
            for kit in kits {
                if !selected.contains(kit["id"].as_str().unwrap_or(""))
                    || !kit["compatible_cars"]
                        .as_array()
                        .is_some_and(|cars| cars.iter().any(|c| c.as_str() == Some(car_id)))
                {
                    continue;
                }
                if let Some(path) = kit["model_path"].as_str() {
                    let mut part = Self::load_scene(path);
                    part.set_name(&format!(
                        "Installed_{}",
                        kit["id"].as_str().unwrap_or("part")
                    ));
                    node.add_child(&part);
                    let names = kit["paint_materials"]
                        .as_array()
                        .map(|items| {
                            items
                                .iter()
                                .filter_map(|i| i.as_str().map(str::to_owned))
                                .collect::<Vec<_>>()
                        })
                        .unwrap_or_default();
                    if !names.is_empty() {
                        let paint = custom
                            .part_paints
                            .get(kit["id"].as_str().unwrap_or(""))
                            .copied()
                            .unwrap_or(custom.paint);
                        let mut part_custom = custom.clone();
                        part_custom.paint = paint;
                        self.paint_nodes(&mut part, car_id, &part_custom, &names);
                    }
                }
            }
        }
    }
    fn tint(&self, node: &mut Gd<Node3D>, car_id: &str, custom: &Customization) {
        let metadata: serde_json::Value = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
        )
        .unwrap_or_default();
        let names: Vec<String> = metadata["cars"]
            .as_array()
            .and_then(|cars| cars.iter().find(|c| c["code"].as_str() == Some(car_id)))
            .and_then(|c| c["paint_materials"].as_array())
            .map(|m| {
                m.iter()
                    .filter_map(|m| m["name"].as_str().map(str::to_owned))
                    .filter(|n| !n.contains("wheel") && !n.contains("tire") && !n.contains("glass"))
                    .collect()
            })
            .unwrap_or_default();
        self.paint_nodes(node, car_id, custom, &names);
    }
    fn paint_nodes(
        &self,
        node: &mut Gd<Node3D>,
        car_id: &str,
        custom: &Customization,
        names: &[String],
    ) {
        let paint = custom.paint;
        let finish = custom.finish.as_str();
        for child in node.get_children().iter_shared() {
            if let Ok(mut mesh) = child.clone().try_cast::<MeshInstance3D>()
                && let Some(resource) = mesh.get_mesh()
            {
                for i in 0..resource.get_surface_count() {
                    if let Some(material) = mesh.get_active_material(i) {
                        let name = material.get_name().to_string();
                        if names.contains(&name)
                            || (names.is_empty()
                                && name.contains("paint")
                                && !name.contains("wheel")
                                && !name.contains("tire"))
                        {
                            let decal_paths = custom
                                .vinyls
                                .iter()
                                .take(16)
                                .map(|layer| {
                                    self.decal_catalog["designs"]
                                        .as_array()
                                        .and_then(|designs| {
                                            designs.iter().find(|design| {
                                                design["id"].as_str() == Some(&layer.design_id)
                                            })
                                        })
                                        .and_then(|design| design["texture_path"].as_str())
                                        .map(str::to_owned)
                                })
                                .collect::<Vec<_>>();
                            let source_material =
                                material.clone().try_cast::<StandardMaterial3D>().ok();
                            let mut shader = godot::classes::Shader::new_gd();
                            let mut code = String::from(
                                "shader_type spatial; uniform sampler2D base_texture:source_color; uniform bool has_texture=false; uniform bool decal_repeat_uv=false; uniform sampler2D paint_mask; uniform bool has_mask=false; uniform float factory_luma=0.5; uniform vec4 original_albedo:source_color=vec4(1.0); uniform float original_roughness=0.5; uniform float original_metallic=0.0; uniform vec4 paint:source_color=vec4(1.0);uniform vec4 paint_secondary:source_color=vec4(1.0);uniform vec4 paint_fleck:source_color=vec4(1.0);uniform float paint_balance=0.5;uniform float paint_flakie=0.52;uniform float paint_focus=100.0;uniform float paint_film=0.011; uniform vec3 uv1_scale=vec3(1.0);uniform vec3 uv1_offset=vec3(0.0);uniform bool use_vertex_color=false;uniform bool srgb_vertex_color=false;vec3 linear_vertex(vec3 c){return mix(c/12.92,pow((c+vec3(0.055))/1.055,vec3(2.4)),step(vec3(0.04045),c));} void fragment(){vec2 base_uv=UV*uv1_scale.xy+uv1_offset.xy;vec4 vertex_base=use_vertex_color?COLOR:vec4(1.0);if(srgb_vertex_color){vertex_base.rgb=linear_vertex(vertex_base.rgb);}vec4 base=has_texture?texture(base_texture,base_uv):vec4(1.0);vec3 original=base.rgb*original_albedo.rgb*vertex_base.rgb;float coverage=(has_mask?texture(paint_mask,base_uv).r:1.0)*paint.a;ALBEDO=mix(original,paint.rgb*dot(original,vec3(0.2126,0.7152,0.0722))/factory_luma,coverage);",
                            );
                            if let Some(source) = &source_material {
                                let repeat = if source.get_flag(
                                    godot::classes::base_material_3d::Flags::USE_TEXTURE_REPEAT,
                                ) {
                                    "repeat_enable"
                                } else {
                                    "repeat_disable"
                                };
                                let filter = match source.get_texture_filter().ord() {
                                    0 => "filter_nearest",
                                    1 => "filter_linear",
                                    2 => "filter_nearest_mipmap",
                                    4 => "filter_nearest_mipmap_anisotropic",
                                    5 => "filter_linear_mipmap_anisotropic",
                                    _ => "filter_linear_mipmap",
                                };
                                // Paint and its mask share the source atlas coordinates.
                                // Losing clamp-to-edge repeats body paint across glass/trim.
                                code = code.replacen(
                                    "base_texture:source_color;",
                                    &format!("base_texture:source_color,{filter},{repeat};"),
                                    1,
                                );
                                code = code.replacen(
                                    "paint_mask;",
                                    &format!("paint_mask:{filter},{repeat};"),
                                    1,
                                );
                                let cull = match source.get_cull_mode() {
                                    godot::classes::base_material_3d::CullMode::FRONT => {
                                        "render_mode cull_front;"
                                    }
                                    godot::classes::base_material_3d::CullMode::DISABLED => {
                                        "render_mode cull_disabled;"
                                    }
                                    _ => "",
                                };
                                code = code.replacen(
                                    "shader_type spatial;",
                                    &format!("shader_type spatial;{cull}"),
                                    1,
                                );
                            }
                            let uniforms = custom.vinyls.iter().take(16).enumerate().map(|(index,_)| {
                                    let texture = if decal_paths[index].is_some() {format!("uniform sampler2D decal_{index}:source_color;uniform bool decal_{index}_alpha_mask=false;")}else{String::new()};
                                    format!("{texture}uniform vec4 vinyl_tint_{index}:source_color=vec4(1.0);")
                                }).collect::<String>();
                            code = code.replacen(
                                "void fragment()",
                                &format!("{uniforms}void fragment()"),
                                1,
                            );
                            code.push_str(&format!(
                                    "ROUGHNESS=mix(original_roughness,{:.3},coverage);METALLIC=mix(original_metallic,{:.3},coverage);",
                                    if matches!(finish, "matt" | "matte") { 0.85 } else { 0.19 },
                                    if finish == "chrome" {
                                        1.0
                                    } else if matches!(finish, "metallic" | "flake") {
                                        0.8
                                    } else {
                                        0.3
                                    }
                                ));
                            if finish == "gloss" {
                                code.push_str("CLEARCOAT=0.7*coverage;CLEARCOAT_ROUGHNESS=0.1;");
                            }
                            code.push_str("vec2 decal_uv=decal_repeat_uv?fract(base_uv):base_uv;");
                            for (layer_index, layer) in custom.vinyls.iter().take(16).enumerate() {
                                if !layer.design_id.is_empty() && decal_paths[layer_index].is_none()
                                {
                                    godot_warn!("Native decal unavailable: {}", layer.design_id);
                                    continue;
                                }
                                let c = layer.rotation.cos();
                                let sn = layer.rotation.sin();
                                let sx = layer.scale[0].max(0.01);
                                let sy = layer.scale[1].max(0.01);
                                code.push_str(&format!("{{vec2 p=mat2(vec2({c:.4},{sn:.4}),vec2({neg:.4},{c:.4}))*(decal_uv-vec2({x:.4},{y:.4})-vec2(0.5));p/=vec2({sx:.4},{sy:.4});float mask=",neg=-sn,x=layer.position[0],y=layer.position[1]));
                                if decal_paths[layer_index].is_some() {
                                    code.push_str(&format!("step(abs(p.x),0.5)*step(abs(p.y),0.5);vec4 decal=texture(decal_{layer_index},p+vec2(0.5));mask*=decal.a;"));
                                } else {
                                    code.push_str(if layer.shape=="flame"{"step(abs(p.x+sin(p.y*28.0)*0.04),0.045)*(1.0-step(0.43,abs(p.y)));"}else{"(1.0-step(0.045,abs(p.x)))*(1.0-step(0.48,abs(p.y)));"});
                                }
                                let artwork = if decal_paths[layer_index].is_some() {
                                    format!("(decal_{layer_index}_alpha_mask?vec3(1.0):decal.rgb)*")
                                } else {
                                    String::new()
                                };
                                code.push_str(&format!("mask*=has_mask?texture(paint_mask,base_uv).r:1.0;ALBEDO=mix(ALBEDO,{artwork}vinyl_tint_{layer_index}.rgb,mask*vinyl_tint_{layer_index}.a);}}"));
                            }
                            // PBR translations distinguish the recovered families; the
                            // original uniform bindings are known, but its GPU BRDF is not.
                            if finish == "flake" {
                                code.push_str("float fleck=step(1.0-paint_flakie*0.03,fract(sin(dot(floor(base_uv*(1000.0+paint_focus*8.0)),vec2(12.9898,78.233)))*43758.5453));ROUGHNESS=mix(ROUGHNESS,0.07,fleck*coverage);ALBEDO=mix(ALBEDO,paint_fleck.rgb,fleck*coverage*0.55);");
                            }
                            if matches!(finish, "pearl" | "pearlescent") {
                                code.push_str("ALBEDO=mix(ALBEDO,paint_secondary.rgb,pow(1.0-abs(dot(NORMAL,VIEW)),0.5+paint_balance*5.0)*0.65*coverage);");
                            }
                            if finish == "thinfilm" {
                                code.push_str("float film_angle=1.0-abs(dot(normalize(NORMAL),normalize(VIEW)));vec3 film=0.5+0.5*cos(vec3(0.0,2.094395,4.18879)+film_angle*(paint_film*1142.3973));ALBEDO=mix(ALBEDO,ALBEDO*(0.35+film*1.3),coverage*0.75);CLEARCOAT=coverage;CLEARCOAT_ROUGHNESS=0.1;");
                            }
                            if let Some(source) = &source_material
                                && source.get_transparency()
                                    == godot::classes::base_material_3d::Transparency::ALPHA_SCISSOR
                            {
                                code.push_str(&format!("ALPHA=base.a*original_albedo.a*vertex_base.a;ALPHA_SCISSOR_THRESHOLD={:.7};", source.get_alpha_scissor_threshold()));
                            }
                            code.push('}');
                            shader.set_code(&code);
                            let mut mat = godot::classes::ShaderMaterial::new_gd();
                            mat.set_shader(&shader);
                            // These controls preserve the recovered material record;
                            // their mapping into Godot PBR remains an explicit adapter.
                            let mut record = paint::donor_seed(custom);
                            if custom.native_paint.is_none() && !paint::stages(finish).is_empty() {
                                // Legacy saves have no72-byte record. Translate the
                                // selected donor color through the same recovered writer.
                                let _ = paint::color(
                                    &mut record,
                                    finish,
                                    0,
                                    [paint[0], paint[1], paint[2]],
                                );
                            }
                            for (name, rgb) in [
                                ("paint_secondary", record.secondary_rgb),
                                ("paint_fleck", record.fleck_rgb),
                            ] {
                                mat.set_shader_parameter(
                                    name,
                                    &Color::from_rgba(rgb[0], rgb[1], rgb[2], 1.).to_variant(),
                                );
                            }
                            for (name, value) in [
                                ("paint_balance", record.two_tone_exp),
                                ("paint_flakie", record.flakie),
                                ("paint_focus", record.fleck_power),
                                ("paint_film", record.film_thickness),
                            ] {
                                mat.set_shader_parameter(name, &value.to_variant());
                            }
                            if let Some(source) = &source_material {
                                mat.set_shader_parameter(
                                    "uv1_scale",
                                    &source.get_uv1_scale().to_variant(),
                                );
                                mat.set_shader_parameter(
                                    "uv1_offset",
                                    &source.get_uv1_offset().to_variant(),
                                );
                                mat.set_shader_parameter("use_vertex_color", &source.get_flag(godot::classes::base_material_3d::Flags::ALBEDO_FROM_VERTEX_COLOR).to_variant());
                                mat.set_shader_parameter("srgb_vertex_color", &source.get_flag(godot::classes::base_material_3d::Flags::SRGB_VERTEX_COLOR).to_variant());
                            }
                            for (index, layer) in custom.vinyls.iter().take(16).enumerate() {
                                mat.set_shader_parameter(
                                    &format!("vinyl_tint_{index}"),
                                    &Color::from_rgba(
                                        layer.color[0],
                                        layer.color[1],
                                        layer.color[2],
                                        layer.color[3],
                                    )
                                    .to_variant(),
                                );
                            }
                            for (index, path) in decal_paths.iter().enumerate() {
                                if let Some(path) = path {
                                    let alpha_mask = self.decal_catalog["designs"]
                                        .as_array()
                                        .is_some_and(|designs| {
                                            designs.iter().any(|design| {
                                                design["id"].as_str()
                                                    == Some(&custom.vinyls[index].design_id)
                                                    && design["color_mode"].as_str()
                                                        == Some("alpha_mask")
                                            })
                                        });
                                    mat.set_shader_parameter(
                                        &format!("decal_{index}_alpha_mask"),
                                        &alpha_mask.to_variant(),
                                    );
                                    mat.set_shader_parameter(
                                        &format!("decal_{index}"),
                                        &godot::tools::load::<godot::classes::Texture2D>(path)
                                            .to_variant(),
                                    );
                                }
                            }
                            mat.set_shader_parameter(
                                "paint",
                                &Color::from_rgba(paint[0], paint[1], paint[2], paint[3])
                                    .to_variant(),
                            );
                            if let Ok(base) = material.try_cast::<StandardMaterial3D>() {
                                mat.set_shader_parameter(
                                    "original_albedo",
                                    &base.get_albedo().to_variant(),
                                );
                                mat.set_shader_parameter(
                                    "original_roughness",
                                    &base.get_roughness().to_variant(),
                                );
                                mat.set_shader_parameter(
                                    "original_metallic",
                                    &base.get_metallic().to_variant(),
                                );
                                let a = base.get_albedo().srgb_to_linear();
                                mat.set_shader_parameter(
                                    "factory_luma",
                                    &(a.r * 0.2126 + a.g * 0.7152 + a.b * 0.0722)
                                        .max(0.01)
                                        .to_variant(),
                                );
                                if let Some(texture) = base.get_texture(
                                    godot::classes::base_material_3d::TextureParam::ALBEDO,
                                ) {
                                    mat.set_shader_parameter("base_texture", &texture.to_variant());
                                    mat.set_shader_parameter("has_texture", &true.to_variant());
                                }
                            }
                            let metadata: serde_json::Value = serde_json::from_str(
                                &FileAccess::get_file_as_string("res://assets/cars.json")
                                    .to_string(),
                            )
                            .unwrap_or_default();
                            if let Some(entry) = metadata["cars"]
                                .as_array()
                                .and_then(|cars| {
                                    cars.iter().find(|c| c["code"].as_str() == Some(car_id))
                                })
                                .and_then(|c| c["paint_materials"].as_array())
                                .and_then(|materials| {
                                    materials.iter().find(|m| m["name"].as_str() == Some(&name))
                                })
                            {
                                mat.set_shader_parameter(
                                    "decal_repeat_uv",
                                    &entry["decal_repeat_uv"]
                                        .as_bool()
                                        .unwrap_or(false)
                                        .to_variant(),
                                );
                                if let Some(path) = entry["mask_path"].as_str()
                                    && let Some(texture) = ResourceLoader::singleton().load(path)
                                {
                                    mat.set_shader_parameter("paint_mask", &texture.to_variant());
                                    mat.set_shader_parameter("has_mask", &true.to_variant());
                                    let rgb = &entry["factory_rgb"];
                                    let values = [
                                        rgb[0].as_f64().unwrap_or(0.5),
                                        rgb[1].as_f64().unwrap_or(0.5),
                                        rgb[2].as_f64().unwrap_or(0.5),
                                    ];
                                    let denominator = if values.iter().any(|value| *value > 1.) {
                                        255.
                                    } else {
                                        1.
                                    };
                                    let reference = Color::from_rgb(
                                        (values[0] / denominator) as f32,
                                        (values[1] / denominator) as f32,
                                        (values[2] / denominator) as f32,
                                    )
                                    .srgb_to_linear();
                                    let luma = entry["factory_luma_linear"].as_f64().unwrap_or(
                                        (reference.r * 0.2126
                                            + reference.g * 0.7152
                                            + reference.b * 0.0722)
                                            as f64,
                                    );
                                    mat.set_shader_parameter(
                                        "factory_luma",
                                        &(luma.max(0.01) as f32).to_variant(),
                                    );
                                }
                            }
                            mesh.set_surface_override_material(i, &mat);
                        }
                    }
                }
            }
            if let Ok(mut spatial) = child.try_cast::<Node3D>() {
                self.paint_nodes(&mut spatial, car_id, custom, names);
            }
        }
    }
    fn run_scenario(&mut self, controls: &mut PlayerInput) {
        let frame = self.scenario_frame;
        if self.wheel_audit
            && let Some(sample) = self.input_samples.last()
        {
            let tick = sample["frame"].as_u64().unwrap_or(0);
            if tick <= 360 && matches!(tick % 60, 15 | 16) {
                let angle = sample["wheel_audit"]["angle_degrees"].as_u64().unwrap_or(0);
                let name = format!("wheel-angle-{angle:03}-tick-{tick:03}");
                // The viewport still contains this cached post-tick state.
                self.capture(&name);
                let _ = std::fs::write(
                    format!("{}/{name}.json", self.capture_dir),
                    serde_json::to_string_pretty(sample).unwrap(),
                );
            }
        }
        if frame == 3 {
            if self.scenario != "reload" {
                let level = self.game.as_ref().unwrap().frame_snapshot().difficulty;
                self.game = Some(Game::new(self.content.clone()));
                self.send(GameCommand::SetDifficulty { level });
            }
            if !self.car_override.is_empty() {
                self.send(GameCommand::SelectCar {
                    car_id: self.car_override.clone(),
                });
            }
            let screen = match self.scenario.as_str() {
                "menu" | "reload" | "title" | "credits" => Some(GameScreen::MainMenu),
                "career" | "event" | "bet" => Some(GameScreen::Career),
                "quick" | "all30" => Some(GameScreen::QuickRace),
                "garage" => Some(GameScreen::Garage),
                "dealer" => Some(GameScreen::Dealership),
                "crew" => Some(GameScreen::Crew),
                "avatar" => Some(GameScreen::MainMenu),
                "customization" | "vinyl" => Some(GameScreen::Customization),
                "options" => Some(GameScreen::MainMenu),
                _ => None,
            };
            if self.scenario == "event" || self.scenario == "bet" {
                self.event_picker = true;
            }
            if let Some(screen) = screen {
                self.send(GameCommand::Navigate { screen });
            } else {
                let event = if !self.event_override.is_empty() {
                    self.content.events[self.selected_event].id.clone()
                } else {
                    self.content
                        .events
                        .iter()
                        .find(|e| {
                            if self.scenario == "drift" {
                                e.mode == RaceMode::Drift
                            } else {
                                e.mode == RaceMode::Circuit
                            }
                        })
                        .unwrap_or(&self.content.events[0])
                        .id
                        .clone()
                };
                self.send(GameCommand::StartRace {
                    event_id: event,
                    career: self.scenario == "career-race",
                    wager: if self.scenario == "career-race" {
                        self.wager
                    } else {
                        0
                    },
                    pink_slip: self.scenario == "career-race" && self.pink_slip,
                });
            }
            if self.scenario == "credits" {
                self.credits = true;
                self.rebuild_menu();
            }
            if self.scenario == "options" {
                self.options = true;
                self.previous_screen.clear();
            }
            if self.scenario == "vinyl" {
                self.custom_page = "vinyl".into();
                self.customization.vinyls = vec![Vinyl::default()];
                self.apply_custom();
            }
        }
        if self.scenario == "pause" && frame == 120 {
            self.send(GameCommand::Pause);
        }
        if self.scenario == "crew" && frame == 8 {
            if let Some(driver) = self
                .game
                .as_ref()
                .unwrap()
                .snapshot()
                .drivers
                .first()
                .cloned()
            {
                self.send(GameCommand::Recruit { driver });
            }
            self.previous_screen.clear();
        }
        if self.scenario == "all30" && frame >= 10 {
            let index = ((frame - 10) / 80) as usize;
            let phase = (frame - 10) % 80;
            if index < self.content.cars.len() {
                let car = self.content.cars[index].clone();
                let id = car.id.clone();
                if phase == 0 {
                    self.custom_return = GameScreen::QuickRace;
                    self.preview_angle = Some(0.);
                    self.send(GameCommand::Navigate {
                        screen: GameScreen::QuickRace,
                    });
                    self.send(GameCommand::SelectCar { car_id: id.clone() });
                    self.customization = Customization::default();
                    self.send(GameCommand::Customize {
                        car_id: id.clone(),
                        customization: self.customization.clone(),
                    });
                    self.send(GameCommand::Navigate {
                        screen: GameScreen::Customization,
                    });
                    self.previous_car.clear();
                }
                if phase == 8 {
                    self.capture(&format!("car-{index:02}-{id}-before-rear"));
                    let data: serde_json::Value = serde_json::from_str(
                        &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                    )
                    .unwrap_or_default();
                    let definition = data["cars"]
                        .as_array()
                        .and_then(|c| c.iter().find(|c| c["code"].as_str() == Some(&id)))
                        .cloned()
                        .unwrap_or_default();
                    let materials = self
                        .preview
                        .as_ref()
                        .map(|node| verification::materials(node, &definition))
                        .unwrap_or_default();
                    self.all30_before = serde_json::json!({"customization":self.game.as_ref().unwrap().frame_snapshot().selected_customization,"materials":materials});
                }
                if phase == 16 {
                    self.preview_angle = Some(std::f32::consts::PI);
                }
                if phase == 24 {
                    self.capture(&format!("car-{index:02}-{id}-before-front"));
                }
                if phase == 28 {
                    self.preview_angle = Some(0.);
                    self.customization = Customization {
                        paint: [0.02 + (index % 3) as f32 * 0.25, 0.2, 0.85, 1.],
                        finish: ["gloss", "metallic", "matt", "pearl", "flake", "thinfilm"]
                            [index % 6]
                            .into(),
                        wheels: ["sport", "mesh", "deep-dish"][index % 3].into(),
                        wheel_paint: [0.85, 0.6, 0.18, 1.],
                        vinyls: vec![Vinyl::default()],
                        engine: 1,
                        transmission: 1,
                        suspension: 1,
                        tyres: 1,
                        ..Customization::default()
                    };
                    let mut record = paint::donor_seed(&self.customization);
                    let family = self.customization.finish.clone();
                    let rgb = self.customization.paint;
                    paint::color(&mut record, &family, 0, [rgb[0], rgb[1], rgb[2]])
                        .expect("native all30 base color");
                    match family.as_str() {
                        "pearl" => {
                            paint::color(&mut record, &family, 1, [0.9, 0.15, 0.25]).unwrap();
                            paint::scalar(&mut record, 2, 0.625).unwrap();
                        }
                        "flake" => {
                            paint::color(&mut record, &family, 3, [1., 0.85, 0.2]).unwrap();
                            paint::scalar(&mut record, 4, 0.25).unwrap();
                            paint::scalar(&mut record, 5, 0.75).unwrap();
                        }
                        "thinfilm" => paint::scalar(&mut record, 6, 0.875).unwrap(),
                        _ => {}
                    }
                    self.customization.native_paint = Some(record.clone());
                    let plate_metadata: serde_json::Value = serde_json::from_str(
                        &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                    )
                    .unwrap_or_default();
                    if plate_metadata["cars"].as_array().is_some_and(|cars| {
                        cars.iter().any(|c| {
                            c["code"].as_str() == Some(&id) && c["plate_socket"].is_object()
                        })
                    }) {
                        self.customization.plate_text = format!("OVR{index:03}");
                        self.customization.plate_style = "dark".into();
                    }
                    if let Some(layer) = self.customization.vinyls.first_mut() {
                        layer.design_id = self.decal_catalog["categories"][0]["design_ids"][0]
                            .as_str()
                            .unwrap_or("")
                            .into();
                    }
                    self.customization.body_kit =
                        car.body_kits.first().cloned().unwrap_or("stock".into());
                    self.customization.interior_kit =
                        car.interior_kits.first().cloned().unwrap_or("stock".into());
                    for (slot, options) in &car.parts {
                        if let Some(part) = options.first() {
                            self.customization.parts.insert(slot.clone(), part.clone());
                        }
                    }
                    self.send(GameCommand::Customize {
                        car_id: id.clone(),
                        customization: self.customization.clone(),
                    });
                    self.send(GameCommand::AcceptNativePaint {
                        car_id: id.clone(),
                        paint: record,
                    });
                    self.previous_car.clear();
                }
                if phase == 44 {
                    let name = format!("car-{index:02}-{id}-after-rear");
                    self.capture(&name);
                    let data: serde_json::Value = serde_json::from_str(
                        &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                    )
                    .unwrap_or_default();
                    let definition = data["cars"]
                        .as_array()
                        .and_then(|c| c.iter().find(|c| c["code"].as_str() == Some(&id)))
                        .cloned()
                        .unwrap_or_default();
                    let materials = self
                        .preview
                        .as_ref()
                        .map(|node| verification::materials(node, &definition))
                        .unwrap_or_default();
                    let actual = self
                        .game
                        .as_ref()
                        .unwrap()
                        .frame_snapshot()
                        .selected_customization;
                    self.all30_probes.push(serde_json::json!({"car_id":id,"stock":self.all30_before,"modified":{"customization":actual,"materials":materials},"state_matches_requested":actual==self.customization,"unpainted_factory_state_unchanged":verification::trim_unchanged(&self.all30_before["materials"],&materials),"paint_trim_override_isolation":materials["unexpected_unpainted_overrides"].as_u64()==Some(0),"compatible_body_kits":car.body_kits,"compatible_interior_kits":car.interior_kits,"performance_scope":"Existing adapted engine/transmission/suspension/tyre parameters; not original Power/Handling/Weight package parity. Legacy NOS tier is not edited."}));
                }
                if phase == 48 {
                    self.preview_angle = Some(std::f32::consts::PI);
                }
                if phase == 64 {
                    self.capture(&format!("car-{index:02}-{id}-after-front"));
                }
            }
        }
        if self.input_event_path.is_empty()
            && matches!(
                self.scenario.as_str(),
                "driving"
                    | "race"
                    | "drift"
                    | "career-race"
                    | "results"
                    | "podium"
                    | "round-results"
                    | "benchmark"
            )
        {
            *controls = self.game.as_ref().unwrap().scenario_player_ai_input();
            if self.scenario == "benchmark" {
                controls.nitrous = if frame % 600 < 180 { 1. } else { 0. };
            }
        }
        let long = matches!(
            self.scenario.as_str(),
            "career-race" | "results" | "podium" | "round-results"
        );
        let end = self
            .frame_budget
            .unwrap_or(if self.scenario == "benchmark" {
                2100
            } else if self.scenario == "all30" {
                self.content.cars.len() as u64 * 80 + 40
            } else if long {
                21600
            } else if matches!(self.scenario.as_str(), "driving" | "race" | "drift") {
                900
            } else {
                360
            });
        let current = self.game.as_ref().unwrap().frame_snapshot();
        let replay_terminal_success = !self.input_event_path.is_empty()
            && self.input_event_index == self.input_events.len()
            && matches!(current.screen, GameScreen::Results | GameScreen::Complete);
        let replay_ended_early = !self.input_event_path.is_empty()
            && (self.input_frame > 0 || self.input_event_index > 0)
            && self.input_event_index < self.input_events.len()
            && current.screen != GameScreen::Race;
        let replay_timed_out = !self.input_event_path.is_empty()
            && !replay_terminal_success
            && frame > end.saturating_mul(2) + 600
            && self.input_frame < end;
        if replay_timed_out {
            godot_error!("Native input replay did not reach its active-frame budget");
        }
        if long && current.screen == GameScreen::RoundResults && self.scenario != "round-results" {
            if let Some(result) = &current.result {
                self.capture(&format!("round-{}", result.round));
            }
            self.send(GameCommand::Continue);
            return;
        }
        if self.scenario == "podium" && current.screen == GameScreen::Results {
            self.send(GameCommand::ShowPodium);
            return;
        }
        let finished = long
            && if self.scenario == "podium" {
                current.screen == GameScreen::Podium
            } else if self.scenario == "round-results" {
                current.screen == GameScreen::RoundResults
            } else {
                current.screen == GameScreen::Results
            };
        if (if !self.input_event_path.is_empty() {
            self.input_frame >= end
        } else if self.scenario == "benchmark" {
            self.frame_times.len() as u64 >= end
        } else {
            frame == end
        }) || finished
            || replay_timed_out
            || replay_terminal_success
            || replay_ended_early
        {
            self.persist();
            let saved = self.game.as_ref().unwrap().save_json().unwrap();
            let loaded = Game::load_json(self.content.clone(), &saved);
            let disk_data = std::fs::read_to_string(self.save_path());
            let disk_reload_equal = disk_data
                .as_ref()
                .ok()
                .and_then(|s| Game::load_json(self.content.clone(), s).ok())
                .and_then(|g| g.save_json().ok())
                .is_some_and(|s| s == saved);
            let save_reload_equal = loaded
                .as_ref()
                .map(|g| g.save_json().unwrap() == saved)
                .unwrap_or(false);
            let reloaded_save = loaded
                .as_ref()
                .ok()
                .and_then(|game| game.save_json().ok())
                .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok());
            let mut times = self.frame_times.clone();
            times.sort_by(|a, b| a.total_cmp(b));
            let warmup = self.warmup_frames.min(self.frame_times.len() as u64) as usize;
            let measured = &self.frame_times[warmup..];
            let mut measured_sorted = measured.to_vec();
            measured_sorted.sort_by(f64::total_cmp);
            let mut families = BTreeMap::<String, usize>::new();
            for event in &self.content.events {
                *families.entry(format!("{:?}", event.mode)).or_default() += 1;
            }
            let server = RenderingServer::singleton();
            let viewport = self
                .base()
                .get_viewport()
                .map(|v| v.get_visible_rect().size)
                .unwrap_or(Vector2::ZERO);
            let mut report = serde_json::json!({"scenario":self.scenario,"native_ui_bounds":self.menu.as_ref().map(control_bounds),"presentation":{"menu_scene":"Independent workshop with neutral lighting and restrained Oversteer panels; material refinement remains in progress","bet_scene":"Fixed adult streetwear driver and selected rival car; stable camera and optional cash/pink-slip controls","profile_scene":"Character editor removed; driver-name entry retained in Options","avatar":self.avatar.as_ref().map(spatial_diagnostic),"paint_scene":"Original PaintBox subset/pose XZ/render-floor; donor ground-reference adaptation. Paintshop end FOV/offset values use donor body-center CHASS and source-pose-rotated component-offset adapter; original DLT lighting and camera parent basis remain unresolved. Explicit inspection rotation retains the source booth yaw for donor length alignment, with a corresponding inside-booth eye and donor-bounds-fitted FOV above lower UI; original interactive Paintshop end camera is retained.","paintbooth":self.paint_stage.as_ref().map(spatial_diagnostic),"avatar_anchor":self.avatar.as_ref().map(|avatar| { let v = avatar.get_global_position(); [v.x,v.y,v.z] }),"camera":self.camera.as_ref().map(|node|spatial_diagnostic(&node.clone().upcast::<Node3D>())),"preview":self.preview.as_ref().map(spatial_diagnostic)},"customization_catalog":{"native_decals":self.decal_catalog["designs"].as_array().map(Vec::len).unwrap_or(0),"native_categories":self.decal_catalog["categories"].as_array().map(Vec::len).unwrap_or(0),"alpha_mask_designs":self.decal_catalog["designs"].as_array().map(|designs|designs.iter().filter(|design|design["color_mode"].as_str()==Some("alpha_mask")).count()).unwrap_or(0),"colorization":"Exact constant black/white source artwork uses source alpha with chosen tint; varied RGB artwork retains source RGB multiplied by tint. Explicit renderer adaptation; native compositor unresolved.","layer_limit":16,"mapping":"Recovered source RGBA artwork on donor UV with isolated body paint masks; original decal projection consumer not recovered"},"ui_actions":self.ui_action_log,"ui_actions_complete":self.ui_step==self.ui_steps.len(),"simulation_speed":if long&&self.input_event_path.is_empty(){6}else{1},"frames":frame,"sampled_frames":self.frame_times.len(),"sample_first":self.sample_first,"sample_last":self.sample_last,"all30_probes":self.all30_probes,"load_status":self.load_status,"save_status":self.save_status,"content":{"cars":self.content.cars.len(),"tracks":self.content.tracks.len(),"events":self.content.events.len(),"event_families":families,"sha256":GString::from(self.content_json.as_str()).sha256_text().to_string()},"renderer":{"method":server.get_current_rendering_method().to_string(),"driver":server.get_current_rendering_driver_name().to_string(),"viewport":[viewport.x,viewport.y],"draw_calls":server.get_rendering_info(godot::classes::rendering_server::RenderingInfo::TOTAL_DRAW_CALLS_IN_FRAME),"primitives":server.get_rendering_info(godot::classes::rendering_server::RenderingInfo::TOTAL_PRIMITIVES_IN_FRAME),"video_memory_bytes":server.get_rendering_info(godot::classes::rendering_server::RenderingInfo::VIDEO_MEM_USED)},"frame_clock":"Rust monotonic Instant at process entry (includes render/vsync/host work between entries)","frame_times_ms":self.frame_times,"engine_delta_times_ms":self.engine_frame_times,"viewport_gpu_timing_available":self.gpu_times.iter().any(|v|*v>0.),"viewport_cpu_timing_available":self.cpu_times.iter().any(|v|*v>0.),"viewport_gpu_times_ms":self.gpu_times,"viewport_cpu_times_ms":self.cpu_times,"viewport_timing_note":"Godot measured viewport render times, read at following process entry","warmup_frames":warmup,"measured_frames":measured.len(),"measured_frame_ms_mean":if measured.is_empty(){0.}else{measured.iter().sum::<f64>()/measured.len() as f64},"measured_frame_ms_p95":if measured_sorted.is_empty(){0.}else{measured_sorted[(measured_sorted.len() as f32*0.95) as usize]},"measured_frame_ms_p99":if measured_sorted.is_empty(){0.}else{measured_sorted[(measured_sorted.len() as f32*0.99) as usize]},"measured_frame_ms_max":measured_sorted.last(),"measured_over_16_67_ms":measured.iter().filter(|t|**t>16.67).count(),"frame_ms_mean":times.iter().sum::<f64>()/times.len() as f64,"frame_ms_p95":times[(times.len() as f32*0.95) as usize],"save_reload_equal":save_reload_equal,"disk_reload_equal":disk_reload_equal,"audio":self.audio.as_ref().map(audio::RuntimeAudio::summary),"loading":self.loading_reports,"effects":self.car_effects.iter().map(effects::CarEffects::summary).collect::<Vec<_>>(),"saved_state":serde_json::from_str::<serde_json::Value>(&saved).unwrap(),"snapshot":self.game.as_ref().unwrap().frame_snapshot()});
            report["input_replay_timed_out"] = replay_timed_out.into();
            report["reloaded_state"] = serde_json::json!(reloaded_save);
            report["disk_save_matches_memory"] =
                disk_data.as_ref().is_ok_and(|text| text == &saved).into();
            report["input_replay_ended_early"] = replay_ended_early.into();
            report["input_replay_terminal_success"] = replay_terminal_success.into();
            report["native_input_replay"] = serde_json::json!({"path":self.input_event_path,"source":"Input.parse_input_event → is_physical_key_pressed/get_joy_axis; AI disabled","virtual_joy_device":self.virtual_joy_replay,"frames":self.input_frame,"event_clock":"Frame0 events preload during Race countdown. Active frame k events queue before poll k and are observed at sample k+1; input_frame counts active Race frames only","events":self.input_events,"events_processed":self.input_event_index,"events_complete":self.input_event_index==self.input_events.len(),"samples":self.input_samples,"nitrous_observations":verification::nitrous_observations(&self.input_samples,self.input_nitrous_initial)});
            report["preview_screen_bounds"] = serde_json::json!(
                self.camera
                    .as_ref()
                    .zip(self.preview.as_ref())
                    .and_then(|(camera, preview)| projected_bounds(camera, preview))
            );
            report["world_layers"] = serde_json::json!({"bindings":self.scene.as_ref().map(world_layer_states),"sampling":"Layered road materials retain the recovered UV translation; previously unbound paving variants use a two-metre world-XZ tile. Both are Oversteer PBR adaptations."});
            report["avatar_components"] = self.avatar_report.clone();
            report["content"]["runtime_sha256"] =
                GString::from(serde_json::to_string(&self.content).unwrap().as_str())
                    .sha256_text()
                    .to_string()
                    .into();
            report["content"]["vehicle_corrections"] = serde_json::json!({
                "GT4_MITS0001": {"mass_kg": 1410, "source": "Mitsubishi January 2003 Evolution VIII press kit, p.19, GSR"}
            });
            report["avatar_animations"] =
                serde_json::json!(self.avatar.as_ref().map(|avatar| animation_states(
                    &avatar.clone().upcast::<godot::classes::Node>()
                )));
            report["settings_status"] = self.settings_status.clone();
            report["settings_path"] = serde_json::json!(self.settings_path("options.json"));
            report["render_quality"] = self.render_quality.into();
            if let Some(audio) = &mut self.audio {
                audio.shutdown();
            }
            if !self.capture_dir.is_empty() {
                let _ = std::fs::create_dir_all(&self.capture_dir);
                self.capture("final");
                report["screenshots_generated"] = self.screenshots_generated.get().into();
                report["screenshot_limit"] = self.screenshot_limit.into();
                report["screenshot_budget_exhausted"] =
                    self.screenshot_budget_exhausted.get().into();
                let _ = std::fs::write(
                    format!("{}/scenario.json", self.capture_dir),
                    serde_json::to_string_pretty(&report).unwrap(),
                );
            }
            self.base()
                .get_tree()
                .quit_ex()
                .exit_code(
                    if self.save_status["ok"].as_bool() == Some(true)
                        && !self.screenshot_budget_exhausted.get()
                        && !replay_timed_out
                        && !replay_ended_early
                        && (self.input_event_path.is_empty()
                            || self.input_event_index == self.input_events.len())
                    {
                        0
                    } else {
                        1
                    },
                )
                .done();
        }
    }
    fn swap_wheels(&self, node: &mut Gd<Node3D>, car_id: &str, custom: &Customization) {
        let style = custom.wheels.as_str();
        if style == "stock" {
            if custom.wheel_paint != Customization::default().wheel_paint {
                let metadata: serde_json::Value = serde_json::from_str(
                    &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                )
                .unwrap_or_default();
                if let Some(car) = metadata["cars"]
                    .as_array()
                    .and_then(|cars| cars.iter().find(|car| car["code"].as_str() == Some(car_id)))
                    && let Some(sockets) = car["wheel_sockets"].as_array()
                {
                    let names = car["stock_rim_materials"]
                        .as_array()
                        .map(|names| {
                            names
                                .iter()
                                .filter_map(|name| name.as_str().map(str::to_owned))
                                .collect::<Vec<_>>()
                        })
                        .unwrap_or_default();
                    paint_stock_rims(node, sockets, &names, custom.wheel_paint);
                }
            }
            return;
        }
        for child in node.get_children().iter_shared() {
            if let Ok(mut spatial) = child.try_cast::<Node3D>() {
                let name = spatial.get_name().to_string().to_lowercase();
                if name.starts_with("wheel_") && !name.contains("tire") {
                    hide_geometry(&mut spatial);
                    let mut radius = 0.20;
                    let mut replacement_transform = None;
                    let scale = spatial.get_global_transform().basis.get_scale().abs();
                    let metadata: serde_json::Value = serde_json::from_str(
                        &FileAccess::get_file_as_string("res://assets/cars.json").to_string(),
                    )
                    .unwrap_or_default();
                    if let Some(socket) = metadata["cars"]
                        .as_array()
                        .and_then(|cars| cars.iter().find(|c| c["code"].as_str() == Some(car_id)))
                        .and_then(|c| c["wheel_sockets"].as_array())
                        .and_then(|sockets| {
                            sockets.iter().find(|s| s["node"].as_str() == Some(&name))
                        })
                    {
                        radius = socket["radius"].as_f64().unwrap_or(0.20) as f32;
                        replacement_transform =
                            matrix_transform(&socket["replacement_transforms"][style]);
                        if socket["tire_embedded"].as_bool() == Some(true) {
                            let mut tire = Self::load_scene(
                                socket["replacement_tire_path"]
                                    .as_str()
                                    .unwrap_or("res://assets/wheels/shared-tire.glb"),
                            );
                            let outer = socket["outer_radius"].as_f64().unwrap_or(0.30) as f32;
                            if let Some(transform) =
                                matrix_transform(&socket["replacement_tire_transform"])
                            {
                                tire.set_transform(transform);
                            } else {
                                tire.set_scale(Vector3::new(
                                    outer / scale.x,
                                    outer / scale.y,
                                    outer / scale.z,
                                ));
                            }
                            spatial.add_child(&tire);
                        }
                    }
                    let mut replacement =
                        Self::load_scene(&format!("res://assets/wheels/{style}.glb"));
                    color_meshes(&mut replacement, custom.wheel_paint);
                    if let Some(transform) = replacement_transform {
                        replacement.set_transform(transform);
                    } else {
                        replacement.set_scale(Vector3::new(
                            radius / scale.x,
                            radius / scale.y,
                            radius / scale.z,
                        ));
                    }
                    spatial.add_child(&replacement);
                } else {
                    self.swap_wheels(&mut spatial, car_id, custom);
                }
            }
        }
    }
    fn capture(&self, name: &str) {
        if self.capture_dir.is_empty() {
            return;
        }
        if self.screenshots_generated.get() >= self.screenshot_limit {
            self.screenshot_budget_exhausted.set(true);
            godot_error!("Screenshot budget exhausted; capture {} refused", name);
            self.base().get_tree().quit_ex().exit_code(1).done();
            return;
        }
        self.screenshots_generated
            .set(self.screenshots_generated.get() + 1);
        let _ = std::fs::create_dir_all(&self.capture_dir);
        // Covered macOS windows can retain an old viewport despite live physics.
        // Render the current scene without presentation before reading pixels.
        let capture_start = std::time::Instant::now();
        RenderingServer::singleton()
            .force_draw_ex()
            .swap_buffers(false)
            .frame_step(0.)
            .done();
        if let Some(viewport) = self.base().get_viewport()
            && let Some(texture) = viewport.get_texture()
            && let Some(image) = texture.get_image()
        {
            let _ = image.save_png(&format!("{}/{name}.png", self.capture_dir));
            godot_print!(
                "OVERSTEER capture={} input_frame={} process_frame={} capture_ms={:.2}",
                name,
                self.input_frame,
                self.scenario_frame,
                capture_start.elapsed().as_secs_f64() * 1000.
            );
        }
    }
}

fn preview_paint(node: &mut Gd<Node3D>, color: Color) {
    preview_paint_uniform(node, "paint", color);
}
fn preview_paint_uniform(node: &mut Gd<Node3D>, uniform: &str, color: Color) {
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(mut shader) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
                && !shader.get_shader_parameter("paint").is_nil()
            {
                shader.set_shader_parameter(uniform, &color.to_variant());
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            preview_paint_uniform(&mut child, uniform, color);
        }
    }
}

fn preview_paint_scalar(node: &mut Gd<Node3D>, uniform: &str, value: f64) {
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(mut shader) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
                && !shader.get_shader_parameter("paint").is_nil()
            {
                shader.set_shader_parameter(uniform, &value.to_variant());
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            preview_paint_scalar(&mut child, uniform, value);
        }
    }
}

fn play_source_animation(node: &mut Gd<godot::classes::Node>, clip: &str, looping: bool) {
    if clip.is_empty() {
        return;
    }
    if let Ok(mut player) = node.clone().try_cast::<godot::classes::AnimationPlayer>() {
        let names = player.get_animation_list();
        if let Some(name) = names.as_slice().iter().find(|name| {
            name.to_string() == clip || name.to_string().ends_with(&format!("/{clip}"))
        }) {
            let name = StringName::from(name);
            if let Some(mut animation) = player.get_animation(&name) {
                animation.set_loop_mode(if looping {
                    godot::classes::animation::LoopMode::LINEAR
                } else {
                    godot::classes::animation::LoopMode::NONE
                });
            }
            player.play_ex().name(&name).done();
        }
    }
    for mut child in node.get_children().iter_shared() {
        play_source_animation(&mut child, clip, looping);
    }
}
fn animation_states(node: &Gd<godot::classes::Node>) -> Vec<serde_json::Value> {
    let mut states = vec![];
    if let Ok(player) = node.clone().try_cast::<godot::classes::AnimationPlayer>() {
        states.push(serde_json::json!({"clip":player.get_current_animation().to_string(),"position":player.get_current_animation_position(),"playing":player.is_playing()}));
    }
    for child in node.get_children().iter_shared() {
        states.extend(animation_states(&child));
    }
    states
}

// Inspection framing is a donor/UI adapter, independent of original script FOVs.
fn inspection_camera_fov(bounds: [Vector3; 2], camera: Transform3D, aspect: f32) -> f32 {
    let inverse = camera.affine_inverse();
    let mut tangent = (60_f32.to_radians() * 0.5).tan();
    for corner in 0..8 {
        let point = inverse
            * (bounds[0]
                + (bounds[1] - bounds[0])
                    * Vector3::new(
                        (corner & 1) as f32,
                        ((corner >> 1) & 1) as f32,
                        ((corner >> 2) & 1) as f32,
                    ));
        if point.z >= -0.05 {
            continue;
        }
        tangent = tangent.max(point.x.abs() / -point.z / aspect / 0.85);
        tangent = tangent.max(point.y / -point.z / 0.6);
        tangent = tangent.max(-point.y / -point.z / 0.4);
    }
    (2. * tangent.atan()).to_degrees().min(169.)
}

fn world_mesh_bounds(node: &Gd<Node3D>) -> Option<[Vector3; 2]> {
    let mut bounds: Option<[Vector3; 2]> = None;
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && mesh.get_mesh().is_some()
    {
        let aabb = mesh.get_aabb();
        let transform = mesh.get_global_transform();
        for corner in 0..8 {
            let point = transform
                * (aabb.position
                    + aabb.size
                        * Vector3::new(
                            (corner & 1) as f32,
                            ((corner >> 1) & 1) as f32,
                            ((corner >> 2) & 1) as f32,
                        ));
            if let Some(pair) = &mut bounds {
                pair[0] = Vector3::new(
                    pair[0].x.min(point.x),
                    pair[0].y.min(point.y),
                    pair[0].z.min(point.z),
                );
                pair[1] = Vector3::new(
                    pair[1].x.max(point.x),
                    pair[1].y.max(point.y),
                    pair[1].z.max(point.z),
                );
            } else {
                bounds = Some([point, point]);
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(child) = child.try_cast::<Node3D>()
            && let Some(pair) = world_mesh_bounds(&child)
        {
            if let Some(current) = &mut bounds {
                current[0] = Vector3::new(
                    current[0].x.min(pair[0].x),
                    current[0].y.min(pair[0].y),
                    current[0].z.min(pair[0].z),
                );
                current[1] = Vector3::new(
                    current[1].x.max(pair[1].x),
                    current[1].y.max(pair[1].y),
                    current[1].z.max(pair[1].z),
                );
            } else {
                bounds = Some(pair);
            }
        }
    }
    bounds
}

fn world_layer_states(node: &Gd<Node3D>) -> Vec<serde_json::Value> {
    let mut states = vec![];
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(material) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
                .filter(|material| {
                    material.has_meta("native_tarmac_uv")
                        || material.has_meta("oversteer_paving_metres")
                })
            {
                if material.has_meta("oversteer_paving_metres") {
                    states.push(serde_json::json!({"node":mesh.get_name().to_string(),"surface":surface,"sampling":"world_xz_metres","tile_metres":2.0,"base_texture":material.get_shader_parameter("paving").try_to::<Gd<godot::classes::Texture2D>>().ok().map(|texture|texture.get_path().to_string())}));
                    continue;
                }
                states.push(serde_json::json!({"node":mesh.get_name().to_string(),"surface":surface,"base_uv_native":0,"markings_uv_native":2,"base_texture":material.get_shader_parameter("native_tarmac").try_to::<Gd<godot::classes::Texture2D>>().ok().map(|texture|texture.get_path().to_string()),"markings_texture":material.get_shader_parameter("native_markings").try_to::<Gd<godot::classes::Texture2D>>().ok().map(|texture|texture.get_path().to_string())}));
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(child) = child.try_cast::<Node3D>() {
            states.extend(world_layer_states(&child));
        }
    }
    states
}

fn projected_bounds(camera: &Gd<Camera3D>, node: &Gd<Node3D>) -> Option<[[f32; 2]; 2]> {
    let bounds = world_mesh_bounds(node)?;
    let mut min = Vector2::new(f32::MAX, f32::MAX);
    let mut max = Vector2::new(f32::MIN, f32::MIN);
    for corner in 0..8 {
        let point = Vector3::new(
            if corner & 1 == 0 {
                bounds[0].x
            } else {
                bounds[1].x
            },
            if corner & 2 == 0 {
                bounds[0].y
            } else {
                bounds[1].y
            },
            if corner & 4 == 0 {
                bounds[0].z
            } else {
                bounds[1].z
            },
        );
        let projected = camera.unproject_position(point);
        min = Vector2::new(min.x.min(projected.x), min.y.min(projected.y));
        max = Vector2::new(max.x.max(projected.x), max.y.max(projected.y));
    }
    Some([[min.x, min.y], [max.x, max.y]])
}

fn spatial_diagnostic(node: &Gd<Node3D>) -> serde_json::Value {
    let transform = node.get_global_transform();
    let p = transform.origin;
    let x = transform.basis * Vector3::RIGHT;
    let y = transform.basis * Vector3::UP;
    let z = transform.basis * Vector3::BACK;
    serde_json::json!({"name":node.get_name().to_string(),"position":[p.x,p.y,p.z],"basis":[[x.x,x.y,x.z],[y.x,y.y,y.z],[z.x,z.y,z.z]],"vertical_fov_degrees":node.clone().try_cast::<Camera3D>().ok().map(|camera|camera.get_fov()),"mesh_bounds":world_mesh_bounds(node).map(|pair|[[pair[0].x,pair[0].y,pair[0].z],[pair[1].x,pair[1].y,pair[1].z]])})
}

fn control_bounds(parent: &Gd<Control>) -> Vec<serde_json::Value> {
    fn visit(node: &Gd<godot::classes::Node>, rows: &mut Vec<serde_json::Value>) {
        if node.is_queued_for_deletion() {
            return;
        }
        if node.has_meta("native_asset") || node.has_meta("native_layout_slot") {
            let asset = node
                .has_meta("native_asset")
                .then(|| node.get_meta("native_asset").to::<String>());
            let slot = node
                .has_meta("native_layout_slot")
                .then(|| node.get_meta("native_layout_slot").to::<String>());
            if let Ok(control) = node.clone().try_cast::<Control>() {
                let rect = control.get_global_rect();
                let minimum = control.get_combined_minimum_size();
                rows.push(serde_json::json!({"name":control.get_name().to_string(),"asset":asset,"layout_slot":slot,"size":[rect.size.x,rect.size.y],"minimum":[minimum.x,minimum.y],"position":[rect.position.x,rect.position.y],"visible":control.is_visible_in_tree()}));
            } else if let Ok(polygon) = node.clone().try_cast::<godot::classes::Polygon2D>() {
                let points = polygon.get_polygon();
                if !points.is_empty() {
                    let mut min = Vector2::new(f32::INFINITY, f32::INFINITY);
                    let mut max = -min;
                    for point in points.as_slice() {
                        let point = polygon.get_global_transform() * *point;
                        min = Vector2::new(min.x.min(point.x), min.y.min(point.y));
                        max = Vector2::new(max.x.max(point.x), max.y.max(point.y));
                    }
                    rows.push(serde_json::json!({"name":polygon.get_name().to_string(),"asset":asset,"layout_slot":slot,"size":[max.x-min.x,max.y-min.y],"minimum":[0,0],"position":[min.x,min.y],"visible":polygon.is_visible_in_tree(),"vertex_rgba":polygon.get_vertex_colors().as_slice().iter().map(|color|[color.r,color.g,color.b,color.a]).collect::<Vec<_>>()}));
                }
            }
        }
        for child in node.get_children().iter_shared() {
            visit(&child, rows);
        }
    }
    let mut rows = vec![];
    visit(&parent.clone().upcast(), &mut rows);
    rows
}

fn matrix_transform(value: &serde_json::Value) -> Option<Transform3D> {
    let values = value.as_array()?;
    if values.len() != 16 {
        return None;
    }
    let mut m = [0.0; 16];
    for (out, value) in m.iter_mut().zip(values) {
        *out = value.as_f64()? as f32;
        if !out.is_finite() {
            return None;
        }
    }
    Some(Transform3D::new(
        Basis::from_cols(
            Vector3::new(m[0], m[1], m[2]),
            Vector3::new(m[4], m[5], m[6]),
            Vector3::new(m[8], m[9], m[10]),
        ),
        Vector3::new(m[12], m[13], m[14]),
    ))
}

fn script_camera_fov(value: f32) -> f32 {
    // 820869D8..DC uses this recovered multiplier before renderer mode 2
    // (vertical FOV). Keep its f32 rounding rather than approximating value / 2.
    (value * 0.008726389147341251_f32).to_degrees()
}

fn host_steering(left: f32, right: f32, axis: f32) -> f32 {
    // Explicit host adaptation: reflect stick sign and normalize its usable range after deadzone.
    if axis.abs() > 0.12 {
        -axis.signum() * (axis.abs() - 0.12) / 0.88
    } else {
        left - right
    }
}

fn swap_binding(bindings: &mut BTreeMap<String, i32>, action: String, value: i32) {
    if let Some(previous) = bindings.get(&action).copied()
        && let Some(conflict) = bindings
            .iter()
            .find(|(name, binding)| **name != action && **binding == value)
            .map(|(name, _)| name.clone())
    {
        bindings.insert(conflict, previous);
    }
    bindings.insert(action, value);
}

#[cfg(test)]
// Keep colocated regression tests beside the helpers they cover.
#[allow(clippy::items_after_test_module)]
mod binding_tests {
    #[test]
    fn wheel_travel_resolves_contact_along_the_suspension_axis() {
        use godot::prelude::Vector3;
        let travel = super::wheel_contact_travel(
            -0.02836,
            Vector3::UP,
            Vector3::new(0., 0.99347, 0.11409),
            0.1,
            true,
        );
        assert!((travel * 0.99347 - 0.02836).abs() < 0.000001);
        assert_eq!(
            super::wheel_contact_travel(-0.02, Vector3::UP, Vector3::UP, 0.1, false),
            0.
        );
        assert_eq!(
            super::wheel_contact_travel(-0.2, Vector3::UP, Vector3::UP, 0.1, true),
            0.1
        );
        assert_eq!(
            super::wheel_contact_travel(0.04, Vector3::UP, Vector3::UP, 0.1, true),
            -0.04
        );
    }
    #[test]
    fn donor_sockets_map_to_physics_sides_after_the_body_half_turn() {
        // Canonical donor front-left is (-X, -Z). The rendered body turns PI,
        // placing that socket at (+X, +Z): physics wheel 1, not wheel 0.
        assert_eq!(super::wheel_physics_index("tire_front_left"), Some(1));
        assert_eq!(super::wheel_physics_index("wheel_rear_right"), Some(2));
    }

    use super::swap_binding;
    use std::collections::BTreeMap;
    #[test]
    fn script_camera_units_match_native_vertical_projection() {
        let vertical = super::script_camera_fov(80.);
        assert!((vertical - 39.99882).abs() < 0.00001);
        // Native projection mode 2 keeps M11 and divides M00 by viewport aspect.
        let m11 = 1. / (vertical.to_radians() * 0.5).tan();
        let native_m11 = 1. / (80_f32 * 0.008726389147341251 * 0.5).tan();
        assert!((m11 - native_m11).abs() < 0.000001);
        assert!((m11 / (16. / 9.) - 1.54554).abs() < 0.0001);
    }
    #[test]
    fn stick_deadzone_is_continuous_and_legal_inputs_roundtrip() {
        let epsilon = 0.00001;
        assert_eq!(super::host_steering(1., 0., 0.12), 1.);
        assert!(super::host_steering(0., 0., 0.12 + epsilon).abs() < 0.0001);
        for steering in [-1_f32, -0.085, -0.001, 0.001, 0.085, 1.] {
            let raw = -steering.signum() * (0.12 + 0.88 * steering.abs());
            assert!((super::host_steering(0., 0., raw) - steering).abs() < 0.000001);
        }
    }
    #[test]
    fn right_keyboard_and_stick_turn_toward_rh_chase_camera_right() {
        use oversteer_core::{Handling, PhysicsGlobals, PlayerInput, VehicleState};
        for input in [
            super::host_steering(0., 1., 0.),
            super::host_steering(0., 0., 1.),
        ] {
            let handling = Handling::default();
            let globals = PhysicsGlobals::recovered_script_settings();
            let mut vehicle = VehicleState::default();
            vehicle.velocity = [0., 0., 15.];
            vehicle.wheel_omega = [15. / handling.wheel_radius; 4];
            for _ in 0..60 {
                vehicle.step(
                    &handling,
                    &globals,
                    PlayerInput {
                        throttle: 0.7,
                        steering: input,
                        ..Default::default()
                    },
                    1. / 60.,
                );
            }
            assert!(
                vehicle.position[0] < 0.,
                "RH screen-right from forward+Z is−X, got{:?}",
                vehicle.position
            );
        }
    }
    #[test]
    fn assigning_nitrous_to_reverse_button_swaps_previous_button() {
        let mut buttons = BTreeMap::from([
            ("nitrous".into(), 0),
            ("reverse".into(), 3),
            ("handbrake".into(), 1),
        ]);
        swap_binding(&mut buttons, "nitrous".into(), 3);
        assert_eq!(buttons["nitrous"], 3);
        assert_eq!(buttons["reverse"], 0);
        assert_eq!(buttons["handbrake"], 1);
    }
    #[test]
    fn assigning_steering_to_brake_axis_preserves_both_controls() {
        let mut axes = BTreeMap::from([
            ("steering".into(), 0),
            ("brake".into(), 4),
            ("throttle".into(), 5),
        ]);
        swap_binding(&mut axes, "steering".into(), 4);
        assert_eq!(axes["steering"], 4);
        assert_eq!(axes["brake"], 0);
        assert_eq!(axes["throttle"], 5);
    }
}

fn v3(p: [f32; 3]) -> Vector3 {
    Vector3::new(p[0], p[1], p[2])
}

fn append_box(
    surface: &mut Gd<godot::classes::SurfaceTool>,
    center: Vector3,
    size: Vector3,
    basis: Basis,
    color: Color,
) {
    let corners = [
        Vector3::new(-1., -1., -1.),
        Vector3::new(1., -1., -1.),
        Vector3::new(1., 1., -1.),
        Vector3::new(-1., 1., -1.),
        Vector3::new(-1., -1., 1.),
        Vector3::new(1., -1., 1.),
        Vector3::new(1., 1., 1.),
        Vector3::new(-1., 1., 1.),
    ];
    for i in [
        0, 1, 2, 0, 2, 3, 5, 4, 7, 5, 7, 6, 4, 0, 3, 4, 3, 7, 1, 5, 6, 1, 6, 2, 3, 2, 6, 3, 6, 7,
        4, 5, 1, 4, 1, 0,
    ] {
        surface.set_color(color);
        surface.add_vertex(center + basis * (corners[i] * size * 0.5));
    }
}

fn wheel_physics_index(name: &str) -> Option<usize> {
    if !name.starts_with("wheel_") && !name.starts_with("tire_") {
        return None;
    }
    ["front_left", "front_right", "rear_left", "rear_right"]
        .iter()
        .position(|suffix| name.contains(suffix))
        // Donor forward is -Z; the chassis half-turn also swaps its X sides.
        .map(|index| index ^ 1)
}

fn wheel_visual_samples(node: &Gd<Node3D>, racer: &RacerSnapshot) -> Vec<serde_json::Value> {
    let mut result = vec![];
    for child in node.get_children().iter_shared() {
        let Ok(spatial) = child.try_cast::<Node3D>() else {
            continue;
        };
        let name = spatial.get_name().to_string().to_lowercase();
        if let Some(index) = wheel_physics_index(&name) {
            let contact = &racer.surface_contacts[index];
            let point = Vector3::new(contact.anchor_xz[0], contact.height, contact.anchor_xz[1]);
            let normal = v3(contact.normal);
            let mut clearance = f32::INFINITY;
            wheel_ground_clearance(&spatial, point, normal, &mut clearance);
            let transform = spatial.get_global_transform();
            let center = transform.origin;
            let axes = [Vector3::RIGHT, Vector3::UP, Vector3::BACK].map(|axis| {
                let direction = transform.basis * axis;
                [direction.x, direction.y, direction.z]
            });
            result.push(serde_json::json!({"node":name,"wheel_index":index,
                "center":[center.x,center.y,center.z],"basis":axes,"determinant":transform.basis.determinant(),
                "contact_active":contact.active,
                "minimum_vertex_plane_clearance_m":if clearance.is_finite(){Some(clearance)}else{None}}));
        } else {
            result.extend(wheel_visual_samples(&spatial, racer));
        }
    }
    result
}

fn wheel_ground_clearance(node: &Gd<Node3D>, point: Vector3, normal: Vector3, minimum: &mut f32) {
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        let transform = mesh.get_global_transform();
        let key = "oversteer_wheel_vertices";
        let vertices = if mesh.has_meta(key) {
            mesh.get_meta(key).to::<PackedVector3Array>()
        } else {
            let mut vertices = PackedVector3Array::new();
            for surface in 0..resource.get_surface_count() {
                if let Some(surface_vertices) = resource
                    .surface_get_arrays(surface)
                    .get(0)
                    .and_then(|value| value.try_to::<PackedVector3Array>().ok())
                {
                    vertices.extend_array(&surface_vertices);
                }
            }
            // Reading an ArrayMesh's buffers can synchronize with the renderer.
            // Wheel geometry is static; suspension and spin only change transforms.
            mesh.set_meta(key, &vertices.to_variant());
            vertices
        };
        let local_normal = transform.basis.transposed() * normal;
        let origin_distance = (transform.origin - point).dot(normal);
        for vertex in vertices.as_slice() {
            *minimum = minimum.min(origin_distance + vertex.dot(local_normal));
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(child) = child.try_cast::<Node3D>() {
            wheel_ground_clearance(&child, point, normal, minimum);
        }
    }
}

fn wheel_contact_travel(
    clearance: f32,
    up: Vector3,
    normal: Vector3,
    limit: f32,
    active: bool,
) -> f32 {
    let alignment = up.dot(normal);
    if !active || !clearance.is_finite() || alignment <= 0.1 {
        return 0.;
    }
    (-clearance / alignment).clamp(-limit, limit)
}

fn animate_wheels(node: &mut Gd<Node3D>, racer: &RacerSnapshot, handling: Option<&Handling>) {
    let mut wheels = vec![];
    animate_wheel_rotations(node, racer, &mut wheels);
    let Some(handling) = handling else {
        return;
    };
    let up = (node.get_global_basis() * Vector3::UP).normalized();
    let mut clearances = [f32::INFINITY; 4];
    // Tires and rims share axle travel. Use their actual geometry so a tilted
    // contact plane cannot cut through the tire's shoulder; keep physics spin.
    for (wheel, i) in &wheels {
        let contact = racer.surface_contacts[*i];
        if contact.active {
            let point = Vector3::new(contact.anchor_xz[0], contact.height, contact.anchor_xz[1]);
            wheel_ground_clearance(wheel, point, v3(contact.normal), &mut clearances[*i]);
        }
    }
    for (mut wheel, i) in wheels {
        let contact = racer.surface_contacts[i];
        let limit = if i < 2 {
            handling.max_spring_compression
        } else {
            handling
                .rear_max_spring_compression
                .unwrap_or(handling.max_spring_compression)
        };
        let travel =
            wheel_contact_travel(clearances[i], up, v3(contact.normal), limit, contact.active);
        let position = wheel.get_global_position();
        wheel.set_global_position(position + up * travel);
    }
}

fn animate_wheel_rotations(
    node: &mut Gd<Node3D>,
    racer: &RacerSnapshot,
    wheels: &mut Vec<(Gd<Node3D>, usize)>,
) {
    for child in node.get_children().iter_shared() {
        if let Ok(mut spatial) = child.try_cast::<Node3D>() {
            let name = spatial.get_name().to_string().to_lowercase();
            let index = wheel_physics_index(&name);
            if let Some(i) = index {
                let key = "oversteer_wheel_rest";
                let rest = if spatial.has_meta(key) {
                    spatial.get_meta(key).to::<Transform3D>()
                } else {
                    let rest = spatial.get_transform();
                    spatial.set_meta(key, &rest.to_variant());
                    rest
                };
                let steer = Basis::from_axis_angle(Vector3::UP, racer.wheel_steer_angles[i]);
                let spin = Basis::from_axis_angle(Vector3::RIGHT, -racer.wheel_angles[i]);
                spatial.set_transform(Transform3D::new(steer * rest.basis * spin, rest.origin));
                wheels.push((spatial, i));
            } else {
                animate_wheel_rotations(&mut spatial, racer, wheels);
            }
        }
    }
}

fn map_transform(points: &[[f32; 3]]) -> (Vector2, f32) {
    let mut min = Vector2::new(f32::MAX, f32::MAX);
    let mut max = Vector2::new(f32::MIN, f32::MIN);
    for p in points {
        min = Vector2::new(min.x.min(p[0]), min.y.min(p[2]));
        max = Vector2::new(max.x.max(p[0]), max.y.max(p[2]));
    }
    (
        (min + max) * 0.5,
        165. / (max - min).x.max((max - min).y).max(1.),
    )
}

fn hide_geometry(node: &mut Gd<Node3D>) {
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>() {
        mesh.set_mesh(None::<&Gd<godot::classes::Mesh>>);
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            hide_geometry(&mut child);
        }
    }
}

fn native_font() -> Gd<godot::classes::Font> {
    godot::classes::ThemeDb::singleton()
        .get_fallback_font()
        .expect("Godot default font")
}

fn paint_stock_rims(
    node: &mut Gd<Node3D>,
    sockets: &[serde_json::Value],
    names: &[String],
    color: [f32; 4],
) {
    let name = node.get_name().to_string();
    if let Some(socket) = sockets
        .iter()
        .find(|socket| socket["node"].as_str() == Some(&name))
    {
        if socket["tire_embedded"].as_bool() != Some(true) {
            color_meshes(node, color);
        } else {
            color_named_meshes(node, names, color);
        }
        return;
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            paint_stock_rims(&mut child, sockets, names, color);
        }
    }
}

// Retain the current Godot Resource duplication semantics during tooling-only adoption.
#[allow(deprecated)]
fn color_named_meshes(node: &mut Gd<Node3D>, names: &[String], color: [f32; 4]) {
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(material) = mesh
                .get_active_material(surface)
                .filter(|material| names.contains(&material.get_name().to_string()))
                && let Some(mut copy) = material
                    .duplicate()
                    .and_then(|material| material.try_cast::<StandardMaterial3D>().ok())
            {
                copy.set_meta("wheel_tint", &true.to_variant());
                copy.set_albedo(Color::from_rgba(color[0], color[1], color[2], color[3]));
                mesh.set_surface_override_material(surface, &copy);
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            color_named_meshes(&mut child, names, color);
        }
    }
}

fn preview_vinyl_tint(node: &mut Gd<Node3D>, index: usize, color: Color) {
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(mut material) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
            {
                let parameter = format!("vinyl_tint_{index}");
                if material
                    .get_shader()
                    .is_some_and(|shader| shader.get_code().to_string().contains(&parameter))
                {
                    material.set_shader_parameter(&parameter, &color.to_variant());
                }
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            preview_vinyl_tint(&mut child, index, color);
        }
    }
}
fn preview_rim_tint(node: &mut Gd<Node3D>, color: Color) -> bool {
    let mut changed = false;
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(mut material) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<StandardMaterial3D>().ok())
                && material.has_meta("wheel_tint")
            {
                material.set_albedo(color);
                changed = true;
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            changed = preview_rim_tint(&mut child, color) || changed;
        }
    }
    changed
}
// Retain the current Godot Resource duplication semantics during tooling-only adoption.
#[allow(deprecated)]
fn color_meshes(node: &mut Gd<Node3D>, color: [f32; 4]) {
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for i in 0..resource.get_surface_count() {
            if let Some(material) = mesh.get_active_material(i)
                && let Some(mut copy) = material
                    .duplicate()
                    .and_then(|m| m.try_cast::<StandardMaterial3D>().ok())
            {
                copy.set_meta("wheel_tint", &true.to_variant());
                copy.set_albedo(Color::from_rgba(color[0], color[1], color[2], color[3]));
                mesh.set_surface_override_material(i, &copy);
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            color_meshes(&mut child, color);
        }
    }
}

fn native_loading_tip() -> String {
    let path = "res://assets/ui/native/loading-tips.json";
    if !FileAccess::file_exists(path) {
        return String::new();
    }
    let data: serde_json::Value =
        serde_json::from_str(&FileAccess::get_file_as_string(path).to_string()).unwrap_or_default();
    data["tips"]
        .as_array()
        .and_then(|tips| tips.first())
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_owned()
}

fn prepare_layered_world(node: &mut Gd<Node3D>, path: &str) {
    let contract_path = "res://assets/worlds/render-contract.json";
    if !FileAccess::file_exists(contract_path) {
        return;
    }
    let contract: serde_json::Value =
        serde_json::from_str(&FileAccess::get_file_as_string(contract_path).to_string())
            .unwrap_or_default();
    let filename = path.rsplit('/').next().unwrap_or("");
    let Some(catalog) = contract["worlds"][filename].as_str() else {
        return;
    };
    let Some(layers) = contract["catalogs"][catalog]["tarmac"].as_array() else {
        return;
    };
    let mut shader = godot::classes::Shader::new_gd();
    // Original UV attributes/art/parameters; layered PBR sampling is a documented translation.
    shader.set_code("shader_type spatial;render_mode cull_disabled;uniform sampler2D native_tarmac:source_color,filter_linear_mipmap_anisotropic,repeat_enable;uniform sampler2D native_markings:source_color,filter_linear_mipmap_anisotropic,repeat_enable;uniform float native_tarmac_scale=1.0;uniform float native_tarmac_brightness=1.0;void fragment(){vec3 road=texture(native_tarmac,UV*native_tarmac_scale).rgb*native_tarmac_brightness;vec4 markings=texture(native_markings,UV2);ALBEDO=mix(road,markings.rgb,markings.a);ROUGHNESS=mix(0.94,0.72,markings.a);METALLIC=0.0;}");
    let mut materials = BTreeMap::<String, Gd<godot::classes::ShaderMaterial>>::new();
    for layer in layers {
        let Some(name) = layer["name"].as_str() else {
            continue;
        };
        let Some(base) = layer["base_texture_path"].as_str() else {
            continue;
        };
        let Some(markings) = layer["markings_texture_path"].as_str() else {
            continue;
        };
        let mut material = godot::classes::ShaderMaterial::new_gd();
        material.set_shader(&shader);
        material.set_shader_parameter(
            "native_tarmac",
            &godot::tools::load::<godot::classes::Texture2D>(base).to_variant(),
        );
        material.set_shader_parameter(
            "native_markings",
            &godot::tools::load::<godot::classes::Texture2D>(markings).to_variant(),
        );
        material.set_shader_parameter(
            "native_tarmac_scale",
            &(layer["native_scalars"]["tarmacScale"]
                .as_f64()
                .unwrap_or(1.) as f32)
                .to_variant(),
        );
        material.set_shader_parameter(
            "native_tarmac_brightness",
            &(layer["native_scalars"]["tarmacBrightness"]
                .as_f64()
                .unwrap_or(1.) as f32)
                .to_variant(),
        );
        material.set_meta("native_tarmac_uv", &0i32.to_variant());
        material.set_meta("native_markings_uv", &2i32.to_variant());
        materials.insert(name.into(), material);
    }
    // Some road variants have a base texture instead of a tarmacTexture layer.
    // Their source UVs depend on the original shader and stretch under plain PBR.
    // Tile the retained paving in world metres for a stable independent finish.
    let catalog_path = contract["catalogs"][catalog]["materials_path"]
        .as_str()
        .unwrap_or("");
    let definitions: serde_json::Value =
        serde_json::from_str(&FileAccess::get_file_as_string(catalog_path).to_string())
            .unwrap_or_default();
    let mut paving_shader = godot::classes::Shader::new_gd();
    paving_shader.set_code("shader_type spatial;render_mode cull_disabled;uniform sampler2D paving:source_color,filter_linear_mipmap_anisotropic,repeat_enable;varying vec3 world_position;void vertex(){world_position=(MODEL_MATRIX*vec4(VERTEX,1.0)).xyz;}void fragment(){ALBEDO=texture(paving,world_position.xz/2.0).rgb;ROUGHNESS=0.94;METALLIC=0.0;}");
    for definition in definitions.as_array().into_iter().flatten() {
        let Some(name) = definition["name"].as_str() else {
            continue;
        };
        if definition["nativeShader"].as_str() != Some("tarmac") || materials.contains_key(name) {
            continue;
        }
        let Some(texture_id) = definition["nativeTextureBindings"]["baseTexture"].as_u64() else {
            continue;
        };
        let texture_path = format!("res://assets/worlds/textures/{catalog}/{texture_id}.png");
        if !ResourceLoader::singleton().exists(&texture_path) {
            continue;
        }
        let mut material = godot::classes::ShaderMaterial::new_gd();
        material.set_shader(&paving_shader);
        material.set_shader_parameter(
            "paving",
            &godot::tools::load::<godot::classes::Texture2D>(&texture_path).to_variant(),
        );
        material.set_meta("oversteer_paving_metres", &2f32.to_variant());
        materials.insert(name.into(), material);
    }
    apply_named_world_materials(node, &materials);
}
fn apply_named_world_materials(
    node: &mut Gd<Node3D>,
    materials: &BTreeMap<String, Gd<godot::classes::ShaderMaterial>>,
) {
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(material) = mesh
                .get_active_material(surface)
                .and_then(|material| materials.get(&material.get_name().to_string()))
            {
                mesh.set_surface_override_material(surface, material);
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            apply_named_world_materials(&mut child, materials);
        }
    }
}

fn presentation_style(role: &str) -> ([[u8; 3]; 3], [f32; 4]) {
    // Recovered record470 RGB bytes;822D4340 uploads raw/255 floats without sRGB transfer. These are distinct from gadget ARGB rows.
    let (palette, car) = match role {
        "TunnelStart" => ([[20, 0, 30], [34, 20, 60], [179, 135, 200]], [65, 0, 155]),
        "CreateCharacter" => ([[5, 0, 6], [4, 0, 2], [1, 0, 2]], [160, 160, 160]),
        "MainToOptions" => ([[2, 0, 5], [10, 0, 20], [25, 0, 55]], [10, 0, 70]),
        "MainToExtras" => ([[47, 19, 5], [210, 145, 65], [0, 0, 0]], [215, 20, 25]),
        "ExtrasToCredits" => ([[15, 20, 0], [0, 0, 0], [0, 0, 0]], [0, 120, 65]),
        _ => ([[36, 6, 29], [82, 22, 33], [0, 0, 0]], [160, 160, 160]),
    };
    (
        palette,
        [
            car[0] as f32 / 255.,
            car[1] as f32 / 255.,
            car[2] as f32 / 255.,
            1.,
        ],
    )
}
fn set_tunnel_palette(node: &mut Gd<Node3D>, palette: [[u8; 3]; 3], exposure: f32) {
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(mut material) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
            {
                let code = material
                    .get_shader()
                    .map(|shader| shader.get_code().to_string())
                    .unwrap_or_default();
                for (index, rgb) in palette.iter().enumerate() {
                    let name = format!("tunnel_col{}", index + 1);
                    if code.contains(&format!("uniform vec3 {name}")) {
                        let color = Color::from_rgb(
                            rgb[0] as f32 * f32::from_bits(0x3b808081),
                            rgb[1] as f32 * f32::from_bits(0x3b808081),
                            rgb[2] as f32 * f32::from_bits(0x3b808081),
                        );
                        material.set_shader_parameter(
                            &name,
                            &Vector3::new(color.r, color.g, color.b).to_variant(),
                        );
                    }
                }
                if code.contains("uniform float presentation_exposure") {
                    material.set_shader_parameter("presentation_exposure", &exposure.to_variant());
                }
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            set_tunnel_palette(&mut child, palette, exposure);
        }
    }
}
fn set_creator_room_visibility(node: &mut Gd<Node3D>, visible: bool) {
    let name = node.get_name().to_string().to_lowercase();
    if ["dj_profile", "floor_reflect", "glass_reflect"]
        .iter()
        .any(|part| name.contains(part))
    {
        node.set_visible(visible);
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            set_creator_room_visibility(&mut child, visible);
        }
    }
}
fn prepare_tunnel(node: &mut Gd<Node3D>) {
    let materials: serde_json::Value = serde_json::from_str(
        &FileAccess::get_file_as_string("res://assets/worlds/tunnel-materials.json").to_string(),
    )
    .unwrap_or_default();
    prepare_tunnel_nodes(node, &materials);
}
// Retain the current Godot Resource duplication semantics during tooling-only adoption.
#[allow(deprecated)]
fn prepare_tunnel_nodes(node: &mut Gd<Node3D>, materials: &serde_json::Value) {
    // Native palette upload is raw/255 linear and PS694 uses UV0 RGB weights.
    // Shared g_exp grading, sampler transfer and blend-variant selection remain
    // unbound; per-venue exposure is an explicit presentation adapter.
    let name = node.get_name().to_string().to_lowercase();
    if [
        "dj_photo",
        "dj_profile",
        "floor_reflect",
        "glass_reflect",
        "black_box",
    ]
    .iter()
    .any(|part| name.contains(part))
    {
        node.set_visible(false);
        // Visibility is chosen by presentation role later. Still translate child
        // luminous passes: leaving their imported MASK material discards low-alpha art.
    }
    if let Ok(mut mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for i in 0..resource.get_surface_count() {
            if let Some(material) = mesh.get_active_material(i) {
                let definition = materials.as_array().and_then(|materials| {
                    materials.iter().find(|definition| {
                        definition["name"].as_str() == Some(&material.get_name().to_string())
                    })
                });
                if let Some(definition) = definition.filter(|definition| {
                    definition["nativeShader"].as_str() == Some("simpleGradient")
                }) {
                    let mut shader = godot::classes::Shader::new_gd();
                    shader.set_code("shader_type spatial;render_mode unshaded,cull_disabled;uniform sampler2D gradient_weights:repeat_enable;uniform vec3 tunnel_col1=vec3(0.14117647,0.02352941,0.11372549);uniform vec3 tunnel_col2=vec3(0.32156863,0.08627451,0.12941176);uniform vec3 tunnel_col3=vec3(0.0);uniform float brightness=2.5;uniform float presentation_exposure=0.15;void fragment(){vec3 weights=texture(gradient_weights,UV).rgb;vec3 tint=tunnel_col1*weights.r+tunnel_col2*weights.g+tunnel_col3*weights.b;ALBEDO=tint*brightness*presentation_exposure;}");
                    let mut translated = godot::classes::ShaderMaterial::new_gd();
                    translated.set_shader(&shader);
                    translated.set_shader_parameter(
                        "gradient_weights",
                        &godot::tools::load::<godot::classes::Texture2D>(
                            "res://assets/worlds/textures/tunnel/12.png",
                        )
                        .to_variant(),
                    );
                    translated.set_shader_parameter(
                        "brightness",
                        &(definition["nativeScalars"]["brightness"]
                            .as_f64()
                            .unwrap_or(2.5) as f32)
                            .to_variant(),
                    );
                    mesh.set_surface_override_material(i, &translated);
                    continue;
                }
                if let Some(definition) = definition.filter(|definition| {
                    matches!(
                        definition["nativeShader"].as_str(),
                        Some("luminousScroll" | "backLightScroll")
                    )
                }) {
                    let mut shader = godot::classes::Shader::new_gd();
                    shader.set_code("shader_type spatial;render_mode unshaded,cull_disabled,blend_add,depth_draw_never;uniform sampler2D base_texture:source_color,repeat_enable;uniform sampler2D lum_texture:source_color,repeat_enable;uniform vec2 native_scroll=vec2(0.0);uniform float multiplier=1.0;uniform float lum_strength=1.0;uniform bool authored_color=false;void fragment(){vec2 uv=UV+TIME*native_scroll;vec4 base=texture(base_texture,uv);vec3 lum=texture(lum_texture,uv).rgb;ALBEDO=authored_color?lum*lum_strength*base.rgb:vec3(1.0);ALPHA=base.a*(authored_color?1.0:multiplier);}");
                    let mut translated = godot::classes::ShaderMaterial::new_gd();
                    translated.set_shader(&shader);
                    for (uniform, binding) in [
                        ("base_texture", "baseTexture"),
                        ("lum_texture", "lumTexture"),
                    ] {
                        if let Some(index) = definition["nativeTextureBindings"][binding].as_u64() {
                            translated.set_shader_parameter(
                                uniform,
                                &godot::tools::load::<godot::classes::Texture2D>(&format!(
                                    "res://assets/worlds/textures/tunnel/{index}.png"
                                ))
                                .to_variant(),
                            );
                        }
                    }
                    translated.set_shader_parameter(
                        "authored_color",
                        &(definition["nativeShader"].as_str() == Some("luminousScroll"))
                            .to_variant(),
                    );
                    let scalars = &definition["nativeScalars"];
                    translated.set_shader_parameter(
                        "native_scroll",
                        &Vector2::new(
                            scalars["uScroll"].as_f64().unwrap_or(0.) as f32,
                            scalars["vScroll"].as_f64().unwrap_or(0.) as f32,
                        )
                        .to_variant(),
                    );
                    translated.set_shader_parameter(
                        "multiplier",
                        &(scalars["multiplier"].as_f64().unwrap_or(1.) as f32).to_variant(),
                    );
                    translated.set_shader_parameter(
                        "lum_strength",
                        &(scalars["lumStrength"].as_f64().unwrap_or(1.) as f32).to_variant(),
                    );
                    mesh.set_surface_override_material(i, &translated);
                    continue;
                }
                if let Some(mut material) = material
                    .duplicate()
                    .and_then(|m| m.try_cast::<StandardMaterial3D>().ok())
                {
                    if definition.is_some_and(|definition| {
                        definition["nativeShader"].as_str() == Some("building_reflect")
                    }) {
                        // Keep original floor artwork until its reflection pass is ported.
                        continue;
                    }
                    material.set_albedo(Color::from_rgb(36. / 255., 6. / 255., 29. / 255.));
                    material.set_roughness(0.8);
                    material.set_metallic(0.);
                    material.set_feature(godot::classes::base_material_3d::Feature::EMISSION, true);
                    material.set_emission(Color::from_rgb(82. / 255., 22. / 255., 33. / 255.));
                    material.set_emission_energy_multiplier(0.25);
                    if let Some(texture) =
                        material.get_texture(godot::classes::base_material_3d::TextureParam::ALBEDO)
                    {
                        material.set_texture(
                            godot::classes::base_material_3d::TextureParam::EMISSION,
                            &texture,
                        );
                    }
                    mesh.set_surface_override_material(i, &material);
                }
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            prepare_tunnel_nodes(&mut child, materials);
        }
    }
}

fn set_creator_tunnel_culling(node: &mut Gd<Node3D>, creator: bool) {
    if let Ok(mesh) = node.clone().try_cast::<MeshInstance3D>()
        && let Some(resource) = mesh.get_mesh()
    {
        for surface in 0..resource.get_surface_count() {
            if let Some(material) = mesh
                .get_active_material(surface)
                .and_then(|material| material.try_cast::<godot::classes::ShaderMaterial>().ok())
                && let Some(mut shader) = material.get_shader()
            {
                let code = shader.get_code().to_string();
                if code.contains("gradient_weights") || code.contains("lum_strength") {
                    let revised = if creator {
                        code.replace("cull_disabled", "cull_back")
                    } else {
                        code.replace("cull_back", "cull_disabled")
                    };
                    if revised != code {
                        shader.set_code(&revised);
                    }
                }
            }
        }
    }
    for child in node.get_children().iter_shared() {
        if let Ok(mut child) = child.try_cast::<Node3D>() {
            set_creator_tunnel_culling(&mut child, creator);
        }
    }
}

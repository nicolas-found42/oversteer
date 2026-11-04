use crate::{substeps, Handling, PhysicsGlobals, PlayerInput, VehicleState};
use serde::{Deserialize, Serialize};
use std::collections::BTreeMap;
use std::sync::Arc;

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct CarDefinition {
    pub parts: BTreeMap<String, Vec<String>>,
    pub id: String,
    pub name: String,
    pub model_path: String,
    pub length_m: f32,
    pub width_m: f32,
    pub price: u32,
    pub league: u8,
    pub classes: Vec<String>,
    pub handling: Handling,
    pub native_performance: Option<crate::NativePerformanceDefinition>,
    pub body_kits: Vec<String>,
    pub interior_kits: Vec<String>,
}
impl CarDefinition {
    pub fn supports_class(&self, class: &str) -> bool {
        class.is_empty()
            || class.eq_ignore_ascii_case("Any")
            || self
                .classes
                .iter()
                .any(|own| own.eq_ignore_ascii_case(class))
    }
}
impl Default for CarDefinition {
    fn default() -> Self {
        Self {
            parts: BTreeMap::new(),
            id: String::new(),
            name: String::new(),
            model_path: String::new(),
            length_m: 0.,
            width_m: 0.,
            price: 15000,
            league: 0,
            classes: vec![],
            handling: Handling::default(),
            native_performance: None,
            body_kits: vec![],
            interior_kits: vec![],
        }
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub enum RaceMode {
    #[default]
    Circuit,
    Drift,
    Eliminator,
    TimeAttack,
    SpeedChallenge,
    TeamRace,
    CircuitTournament,
    DriftKing,
    #[serde(alias = "DriftRace")]
    DriftObliterator,
    #[serde(alias = "DriftEnduro")]
    DriftEndurance,
    #[serde(alias = "LapTimeChallenge")]
    LapTime,
    #[serde(alias = "PerfectLapChallenge")]
    PerfectLap,
    #[serde(alias = "CarBeaterChallenge")]
    BeatCar,
    #[serde(alias = "LMS")]
    LastManStanding,
    SoloDrift,
    TwinDrift,
}
impl RaceMode {
    pub fn ranks_by_score(self) -> bool {
        self.is_drift() && self != Self::DriftObliterator
    }
    pub fn is_drift(self) -> bool {
        matches!(
            self,
            Self::Drift
                | Self::DriftKing
                | Self::DriftObliterator
                | Self::DriftEndurance
                | Self::SoloDrift
                | Self::TwinDrift
        )
    }
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct EventContestant {
    pub tag: String,
    pub car_id: String,
    pub team: u8,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct EventStage {
    pub track_id: String,
    pub laps: u32,
    pub target: f32,
}
impl Default for EventStage {
    fn default() -> Self {
        Self {
            track_id: String::new(),
            laps: 1,
            target: 0.,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
#[repr(u8)]
pub enum NativeDiscipline {
    Circuit = 0,
    Drift = 1,
    TestDrive = 2,
    Solo = 3,
}
impl NativeDiscipline {
    pub fn source_index(self) -> u8 {
        self as u8
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct EventDefinition {
    pub native_discipline: Option<NativeDiscipline>,
    pub prototype: bool,
    pub extreme_nos: bool,
    pub car_class: String,
    pub id: String,
    pub name: String,
    pub track_id: String,
    pub mode: RaceMode,
    pub league: u8,
    pub laps: u32,
    pub reward: u32,
    pub prizes: Vec<u32>,
    pub target: f32,
    pub opponents: u8,
    pub stages: Vec<EventStage>,
    pub drivers_per_crew: u8,
    pub contest_type: String,
    pub challenge_data: f32,
    pub prize_type: String,
    pub endurance: u32,
    pub qualifier: bool,
    pub rounds: u32,
    pub lives: u32,
    pub time_limit: f32,
    pub entrance_fee: u32,
    pub native_subtype: String,
    pub target_car: Option<String>,
    pub contestants: Vec<EventContestant>,
    pub is_sponsor: bool,
    pub sponsor_type: String,
}
impl Default for EventDefinition {
    fn default() -> Self {
        Self {
            native_discipline: None,
            prototype: false,
            extreme_nos: false,
            car_class: String::new(),
            id: "harbor-circuit".into(),
            name: "Harbor Circuit".into(),
            track_id: "harbor".into(),
            mode: RaceMode::Circuit,
            league: 0,
            laps: 2,
            reward: 5000,
            prizes: vec![],
            target: 3000.,
            opponents: 5,
            stages: vec![],
            drivers_per_crew: 1,
            contest_type: "None".into(),
            challenge_data: 0.,
            prize_type: "Cash".into(),
            endurance: 0,
            qualifier: false,
            rounds: 1,
            lives: 3,
            time_limit: 0.,
            entrance_fee: 0,
            native_subtype: String::new(),
            target_car: None,
            contestants: vec![],
            is_sponsor: false,
            sponsor_type: String::new(),
        }
    }
}
impl EventDefinition {
    pub fn stage_mode(&self) -> RaceMode {
        if self.mode == RaceMode::CircuitTournament {
            match self.native_subtype.as_str() {
                "Eliminator" => RaceMode::Eliminator,
                "LMS" => RaceMode::LastManStanding,
                _ => RaceMode::Circuit,
            }
        } else {
            self.mode
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct TrackDefinition {
    pub native_route: String,
    pub start_grid: Vec<TrackStart>,
    pub collision: Option<crate::NativeCollisionDefinition>,
    pub surface_half_widths: Vec<[f32; 2]>,
    pub wall_half_widths: Vec<[Option<f32>; 2]>,
    pub location: String,
    pub surface_points: Vec<[f32; 3]>,
    pub id: String,
    pub name: String,
    pub points: Vec<[f32; 3]>,
    pub road_width: f32,
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct TrackStart {
    pub position: [f32; 3],
    pub native_yaw_radians: f32,
    pub source_record_index: u32,
}
impl Default for TrackDefinition {
    fn default() -> Self {
        Self {
            native_route: String::new(),
            start_grid: vec![],
            collision: None,
            surface_half_widths: vec![],
            wall_half_widths: vec![],
            location: String::new(),
            id: "harbor".into(),
            name: "Harbor".into(),
            points: vec![
                [0., 0., 0.],
                [0., 0., 250.],
                [120., 0., 350.],
                [300., 0., 300.],
                [350., 0., 100.],
                [200., 0., 0.],
            ],
            surface_points: vec![],
            road_width: 18.,
        }
    }
}
impl TrackDefinition {
    fn surface(&self) -> &[[f32; 3]] {
        if self.surface_points.len() == self.points.len() {
            &self.surface_points
        } else {
            &self.points
        }
    }
}
#[derive(Clone, Debug, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct GameContent {
    pub leagues: Vec<crate::LeagueDefinition>,
    pub drivers: Vec<DriverDna>,
    pub cars: Vec<CarDefinition>,
    pub tracks: Vec<TrackDefinition>,
    pub events: Vec<EventDefinition>,
}
impl GameContent {
    /// Independent-game corrections; recovered source catalogs remain unchanged.
    pub fn apply_oversteer_vehicle_corrections(&mut self) {
        if let Some(evo) = self.cars.iter_mut().find(|car| car.id == "GT4_MITS0001") {
            // Mitsubishi's January 2003 Evolution VIII press kit, p.19: GSR 1410 kg.
            // The secondary donor catalog incorrectly supplied 320 kg.
            // See docs/game/PIVOT_STATUS.md for the primary document and remaining audit.
            evo.handling.mass = 1410.;
        }
    }
}
#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, Serialize, Deserialize)]
pub enum GameScreen {
    Grid,
    #[default]
    MainMenu,
    QuickRace,
    Career,
    Garage,
    Dealership,
    Customization,
    Crew,
    Race,
    Paused,
    Results,
    Complete,
    Avatar,
    Podium,
    RoundResults,
    Checkout,
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(default)]
pub struct PlayerProfile {
    /// Native definition IDs and all56 raw levels; execution/ranges belong to source-backed renderer bindings.
    pub native_components: BTreeMap<String, String>,
    pub native_attributes: BTreeMap<String, f32>,
    pub name: String,
    pub gender: String,
    pub preset: String,
    pub skin_color: [f32; 4],
    pub hair: String,
    pub top: String,
    pub bottom: String,
    pub accessories: Vec<String>,
    pub hair_color: [f32; 4],
    pub top_color: [f32; 4],
    pub bottom_color: [f32; 4],
}
impl Default for PlayerProfile {
    fn default() -> Self {
        Self {
            native_components: BTreeMap::new(),
            native_attributes: BTreeMap::new(),
            name: "Driver".into(),
            gender: "M".into(),
            preset: "stock".into(),
            skin_color: [0.65, 0.45, 0.3, 1.],
            hair: "stock".into(),
            top: "stock".into(),
            bottom: "stock".into(),
            accessories: vec![],
            hair_color: [0.1, 0.07, 0.04, 1.],
            top_color: [0.15, 0.15, 0.2, 1.],
            bottom_color: [0.1, 0.1, 0.15, 1.],
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(default)]
pub struct Vinyl {
    pub design_id: String,
    pub shape: String,
    pub color: [f32; 4],
    pub position: [f32; 2],
    pub scale: [f32; 2],
    pub rotation: f32,
}
impl Default for Vinyl {
    fn default() -> Self {
        Self {
            design_id: String::new(),
            shape: "stripe".into(),
            color: [1., 1., 1., 1.],
            position: [0., 0.],
            scale: [1., 1.],
            rotation: 0.,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(default)]
pub struct Customization {
    pub native_performance_parts: Option<[u32; 3]>,
    pub parts: BTreeMap<String, String>,
    pub plate_text: String,
    pub plate_style: String,
    pub wheel_paint: [f32; 4],
    pub part_paints: BTreeMap<String, [f32; 4]>,
    pub paint: [f32; 4],
    pub finish: String,
    pub native_paint: Option<crate::NativePaintRecord>,
    pub wheels: String,
    pub body_kit: String,
    pub interior_kit: String,
    pub engine: u8,
    pub transmission: u8,
    pub suspension: u8,
    pub tyres: u8,
    pub nitrous: u8,
    pub nitrous_capacity_control: Option<f32>,
    pub tuning: [f32; 4],
    pub vinyls: Vec<Vinyl>,
}
impl Default for Customization {
    fn default() -> Self {
        Self {
            native_performance_parts: None,
            parts: BTreeMap::new(),
            plate_text: "OVERSTR".into(),
            plate_style: "stock".into(),
            wheel_paint: [0.7, 0.7, 0.72, 1.],
            part_paints: BTreeMap::new(),
            paint: [0.8, 0.08, 0.04, 1.],
            finish: "gloss".into(),
            native_paint: None,
            wheels: "stock".into(),
            body_kit: "stock".into(),
            interior_kit: "stock".into(),
            engine: 0,
            transmission: 0,
            suspension: 0,
            tyres: 0,
            nitrous: 0,
            nitrous_capacity_control: None,
            tuning: [0.; 4],
            vinyls: vec![],
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
#[serde(default)]
pub struct DriverDna {
    pub native_tag: String,
    pub spook_rate: f32,
    pub recklessness: f32,
    pub blocking: f32,
    pub race_throttle: f32,
    pub corner_throttle: f32,
    pub drift_throttle: f32,
    pub drift_corner_throttle: f32,
    pub circuit_genes: [u8; 5],
    pub circuit_experience: [u8; 5],
    pub drift_genes: [u8; 3],
    pub drift_experience: [u8; 3],
    pub gambling_genes: [u8; 3],
    pub gambling_experience: [u8; 3],
    pub provenance: String,
    pub name: String,
    pub aggression: f32,
    pub precision: f32,
    pub composure: f32,
    pub drift: f32,
    pub experience: f32,
}
impl Default for DriverDna {
    fn default() -> Self {
        Self {
            native_tag: String::new(),
            spook_rate: 1.,
            recklessness: 0.7,
            blocking: 0.7,
            race_throttle: 0.8,
            corner_throttle: 0.8,
            drift_throttle: 0.8,
            drift_corner_throttle: 0.8,
            circuit_genes: [4; 5],
            circuit_experience: [0; 5],
            drift_genes: [4; 3],
            drift_experience: [0; 3],
            gambling_genes: [4; 3],
            gambling_experience: [0; 3],
            provenance: "Adapted rookie profile".into(),
            name: "Rookie".into(),
            aggression: 0.5,
            precision: 0.7,
            composure: 0.5,
            drift: 0.5,
            experience: 0.,
        }
    }
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CareerState {
    #[serde(default)]
    pub native_performance: Option<crate::NativePerformanceCareer>,
    #[serde(default)]
    pub sponsor_packages: BTreeMap<String, Vec<u8>>,
    #[serde(default)]
    pub visual_unlocks: Vec<String>,
    #[serde(default)]
    pub prototype_unlocked: bool,
    #[serde(default)]
    pub goal_progress: BTreeMap<String, crate::GoalProgress>,
    #[serde(default)]
    pub vehicle_history: BTreeMap<String, crate::VehicleHistory>,
    #[serde(default)]
    pub transactions: Vec<crate::CareerTransaction>,
    #[serde(default)]
    pub parts_inventory: BTreeMap<String, Vec<String>>,
    pub cash: i64,
    pub league: u8,
    pub completed_events: Vec<String>,
    pub garage: BTreeMap<String, Customization>,
    pub crew: Vec<DriverDna>,
    pub wins: u32,
    pub losses: u32,
    pub reputation: u32,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RaceResult {
    pub round: u32,
    pub total_rounds: u32,
    pub tournament_points: Vec<u32>,
    pub is_final: bool,
    pub event_id: String,
    pub won: bool,
    pub position: u32,
    pub reward: i64,
    pub wager: i64,
    pub pink_slip: Option<String>,
    pub score: f32,
    pub time: f32,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum GameCommand {
    AcceptNativePaint {
        car_id: String,
        paint: crate::NativePaintRecord,
    },
    UnlockPrototype {
        league: u8,
        category: crate::PrototypeCategory,
    },
    SetDifficulty {
        level: u8,
    },
    OfferDriverBet {
        racer: usize,
        amount: u32,
    },
    OfferPinkSlip {
        racer: usize,
    },
    AcceptBetOffer,
    DeclineBetOffer,
    OpenGrid,
    LaunchRace,
    PlaceDriverBet {
        racer: usize,
        amount: u32,
    },
    StartSpectating {
        event_id: String,
    },
    PlaceSpectatorBet {
        racer: usize,
        amount: u32,
    },
    SpectatorCheer {
        racer: usize,
        positive: bool,
    },
    RemoveCartItem {
        item_id: String,
    },
    DiscardCart {
        car_id: Option<String>,
    },
    Checkout,
    CustomizeAvatar {
        profile: PlayerProfile,
    },
    ShowPodium,
    Navigate {
        screen: GameScreen,
    },
    SelectCar {
        car_id: String,
    },
    StartRace {
        event_id: String,
        career: bool,
        wager: u32,
        pink_slip: bool,
    },
    BuyCar {
        car_id: String,
    },
    SellCar {
        car_id: String,
    },
    Customize {
        car_id: String,
        customization: Customization,
    },
    Recruit {
        driver: DriverDna,
    },
    Pause,
    Resume,
    Restart,
    Continue,
    ResetCar,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RacerSnapshot {
    #[serde(default)]
    pub applied_input: PlayerInput,
    #[serde(default)]
    pub clutch_engaged: bool,
    pub wheel_omega: [f32; 4],
    pub wheel_angles: [f32; 4],
    pub wheel_steer_angles: [f32; 4],
    pub surface_contacts: [crate::SurfaceContact; 4],
    pub is_player: bool,
    pub team: u8,
    pub role: String,
    pub lives: u32,
    pub chain_score: f32,
    pub best_lap_time: f32,
    pub clean_lap: bool,
    pub car_id: String,
    pub name: String,
    #[serde(default)]
    pub native_tag: String,
    pub position: [f32; 3],
    pub rotation: [f32; 4],
    pub velocity: [f32; 3],
    pub speed_kph: f32,
    pub rpm: f32,
    pub gear: i32,
    pub steering: f32,
    pub nitrous: f32,
    pub nitrous_active: bool,
    pub nitrous_pressure_band: u8,
    pub lap: u32,
    pub checkpoint: usize,
    pub progress: f32,
    pub drift_score: f32,
    pub spook: f32,
    #[serde(default)]
    pub finish_time: Option<f32>,
    pub finished: bool,
    pub eliminated: bool,
    pub customization: Customization,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct RaceSnapshot {
    #[serde(default)]
    pub career: bool,
    pub native_discipline: Option<NativeDiscipline>,
    pub bet_offer: Option<crate::DriverBetOffer>,
    pub wager: u32,
    #[serde(default)]
    pub pink_slip: bool,
    pub bet_racer: usize,
    pub spectating: bool,
    pub spectator_bets: Vec<crate::SpectatorBet>,
    pub spectator_odds: Vec<f32>,
    pub speed_challenge: crate::SpeedChallengeState,
    pub round: u32,
    pub total_rounds: u32,
    pub lives: u32,
    pub target: f32,
    pub team_scores: Vec<f32>,
    pub tournament_points: Vec<u32>,
    pub event_id: String,
    pub track_id: String,
    pub mode: RaceMode,
    pub elapsed: f32,
    pub countdown: f32,
    pub position: u32,
    pub laps: u32,
    pub racers: Vec<RacerSnapshot>,
    /// Racer indices in live race order, using the same rules as settlement.
    #[serde(default)]
    pub standings: Vec<usize>,
    pub drift_combo: f32,
    pub message: String,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GameSnapshot {
    pub difficulty: u8,
    pub league_progress: crate::LeagueProgress,
    pub cart: Vec<crate::CartItem>,
    pub drivers: Vec<DriverDna>,
    pub profile: PlayerProfile,
    pub selected_customization: Customization,
    pub screen: GameScreen,
    pub selected_car: String,
    pub cars: Vec<CarDefinition>,
    pub tracks: Vec<TrackDefinition>,
    pub events: Vec<EventDefinition>,
    pub career: CareerState,
    pub race: Option<RaceSnapshot>,
    pub result: Option<RaceResult>,
}
fn normal_difficulty() -> u8 {
    1
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GameSave {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub interrupted_race: Option<InterruptedRace>,
    #[serde(default = "normal_difficulty")]
    pub difficulty: u8,
    #[serde(default)]
    pub profile: PlayerProfile,
    #[serde(default)]
    pub quick_customizations: BTreeMap<String, Customization>,
    pub schema_version: u32,
    pub selected_car: String,
    pub career: CareerState,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct InterruptedRace {
    pub event_id: String,
    pub car_id: String,
    pub wager: u32,
    pub entrance_fee: u32,
}
impl InterruptedRace {
    pub fn refund(&self) -> i64 {
        i64::from(self.wager) + i64::from(self.entrance_fee)
    }
}
impl Racer {
    fn apply_human_motion(
        &mut self,
        globals: &mut crate::HumanDriftGlobals,
        input: PlayerInput,
        h: f32,
        drift_mode: bool,
    ) {
        let [x, y, z, w] = self.state.orientation;
        let angle = if !(-2.0..=2.0).contains(&self.state.slip_angle) {
            0.
        } else {
            self.state
                .slip_angle
                .clamp(-std::f32::consts::FRAC_PI_2, std::f32::consts::FRAC_PI_2)
        };
        let motion = self.human_drift.advance(
            globals,
            input,
            h,
            drift_mode,
            crate::HumanDriftMotion {
                world_velocity: self.state.velocity,
                body_angular_velocity: [
                    self.state.pitch_rate,
                    self.state.yaw_rate,
                    self.state.roll_rate,
                ],
                forward_axis: [
                    2. * (x * z + w * y),
                    2. * (y * z - w * x),
                    1. - 2. * (x * x + y * y),
                ],
                right_axis: [
                    1. - 2. * (y * y + z * z),
                    2. * (x * y + w * z),
                    2. * (x * z - w * y),
                ],
                score_angle: angle,
                airborne_time: self.unsupported_time,
            },
        );
        // Native 8226B8C8/8226BA58 set world velocity/body angular velocity;
        // this reconstruction stores those channels directly, with no separate momentum cache.
        self.state.velocity = motion.world_velocity;
        [
            self.state.pitch_rate,
            self.state.yaw_rate,
            self.state.roll_rate,
        ] = motion.body_angular_velocity;
        let local = self.state.body_velocity();
        self.state.slip_angle = local[0].atan2(local[2]);
    }
}
#[derive(Clone, Debug)]
struct Racer {
    human_drift: crate::HumanDriftState,
    unsupported_time: f32,
    drive_layout: crate::DriveLayout,
    wheelbase: f32,
    max_steer: f32,
    drift_direction: f32,
    drift_kick_latched: bool,
    stuck_time: f32,
    reverse_recovery: f32,
    team: u8,
    lives: u32,
    chain_score: f32,
    input_clock: f32,
    lap_start: f32,
    best_lap_time: f32,
    clean_lap: bool,
    finish_time: Option<f32>,
    life_cooldown: f32,
    drift_state: crate::NativeDriftState,
    enduro_stopped: bool,
    car_id: String,
    name: String,
    state: VehicleState,
    applied_input: PlayerInput,
    customization: Customization,
    dna: DriverDna,
    lap: u32,
    checkpoint: usize,
    progress: f32,
    score: f32,
    spook: f32,
    finished: bool,
    eliminated: bool,
}
#[derive(Clone, Debug)]
struct Race {
    collision_world: Option<Arc<crate::NativeCollisionWorld>>,
    bet_offer: Option<crate::DriverBetOffer>,
    finish_observation_window: f32,
    bet_racer: usize,
    spectating: bool,
    spectator_bets: Vec<crate::SpectatorBet>,
    max_speed_kph: f32,
    air_time: f32,
    spooked_tags: Vec<String>,
    round: u32,
    total_rounds: u32,
    stage_indices: Vec<usize>,
    tournament_points: Vec<u32>,
    speed_challenge: crate::SpeedChallengeState,
    event: EventDefinition,
    track: TrackDefinition,
    racers: Vec<Racer>,
    elapsed: f32,
    countdown: f32,
    career: bool,
    wager: u32,
    pink_slip: bool,
    settled: bool,
    combo: f32,
}
pub struct Game {
    recovered_race: Option<InterruptedRace>,
    collision_worlds: BTreeMap<String, Arc<crate::NativeCollisionWorld>>,
    pub drift_assist_globals: crate::HumanDriftGlobals,
    difficulty: u8,
    tick_accumulator: f64,
    profile: PlayerProfile,
    pub content: GameContent,
    pub globals: PhysicsGlobals,
    screen: GameScreen,
    selected_car: String,
    career: CareerState,
    race: Option<Race>,
    result: Option<RaceResult>,
    quick_customizations: BTreeMap<String, Customization>,
    quick_mode: bool,
    pending_customizations: BTreeMap<String, Customization>,
    accepted_native_paint: std::collections::BTreeSet<String>,
}
impl Game {
    pub fn new(mut content: GameContent) -> Self {
        for car in &mut content.cars {
            if car.length_m > 0. {
                car.handling.body_length = car.length_m;
            }
            if car.width_m > 0. {
                car.handling.body_width = car.width_m;
            }
        }
        if content.drivers.is_empty() {
            content.drivers = serde_json::from_str(include_str!("../data/native-drivers.json"))
                .expect("validated native driver fixture");
        }
        if content.tracks.is_empty() {
            content.tracks.push(TrackDefinition::default());
        }
        if content.events.is_empty() {
            content.events.push(EventDefinition::default());
        }
        let selected = content
            .cars
            .first()
            .map(|c| c.id.clone())
            .unwrap_or_default();
        let mut garage = BTreeMap::new();
        if !selected.is_empty() {
            garage.insert(selected.clone(), Customization::default());
        }
        Self {
            recovered_race: None,
            drift_assist_globals: crate::HumanDriftGlobals::default(),
            collision_worlds: BTreeMap::new(),
            tick_accumulator: 0.,
            content,
            difficulty: 1,
            profile: PlayerProfile::default(),
            globals: PhysicsGlobals::recovered_script_settings(),
            screen: GameScreen::MainMenu,
            selected_car: selected.clone(),
            career: CareerState {
                native_performance: Some(crate::NativePerformanceCareer::default()),
                sponsor_packages: BTreeMap::new(),
                visual_unlocks: vec![],
                prototype_unlocked: false,
                goal_progress: BTreeMap::new(),
                vehicle_history: if selected.is_empty() {
                    BTreeMap::new()
                } else {
                    BTreeMap::from([(
                        selected.clone(),
                        crate::VehicleHistory {
                            acquired_by: "Starter".into(),
                            ..Default::default()
                        },
                    )])
                },
                transactions: vec![],
                parts_inventory: if selected.is_empty() {
                    BTreeMap::new()
                } else {
                    BTreeMap::from([(
                        selected.clone(),
                        crate::garage::owned_parts(&Customization::default()),
                    )])
                },
                cash: 25000,
                league: 0,
                completed_events: vec![],
                garage,
                crew: vec![],
                wins: 0,
                losses: 0,
                reputation: 0,
            },
            race: None,
            result: None,
            quick_customizations: BTreeMap::new(),
            quick_mode: false,
            pending_customizations: BTreeMap::new(),
            accepted_native_paint: Default::default(),
        }
    }
    pub fn save_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(&GameSave {
            interrupted_race: self
                .race
                .as_ref()
                .filter(|race| {
                    race.career
                        && !race.spectating
                        && !race.settled
                        && (race.wager > 0 || race.event.entrance_fee > 0 || race.pink_slip)
                })
                .map(|race| InterruptedRace {
                    event_id: race.event.id.clone(),
                    car_id: race.racers[0].car_id.clone(),
                    wager: race.wager,
                    entrance_fee: race.event.entrance_fee,
                }),
            difficulty: self.difficulty,
            profile: self.profile.clone(),
            quick_customizations: self.quick_customizations.clone(),
            schema_version: 1,
            selected_car: self.selected_car.clone(),
            career: self.career.clone(),
        })
    }
    pub fn load_json(content: GameContent, json: &str) -> Result<Self, String> {
        let save: GameSave = serde_json::from_str(json).map_err(|e| e.to_string())?;
        if save.schema_version != 1 {
            return Err("Unsupported save schema".into());
        }
        let mut game = Self::new(content);
        if !game.content.cars.iter().any(|c| c.id == save.selected_car) {
            return Err("Save contains unavailable selected vehicle".into());
        }
        if save
            .career
            .garage
            .keys()
            .any(|id| !game.content.cars.iter().any(|c| &c.id == id))
        {
            return Err("Save contains unavailable garage vehicle".into());
        }
        game.selected_car = save.selected_car;
        game.career = save.career;
        if game.career.native_performance.is_none() {
            // Earlier reconstruction saves could earn these rewards but could not
            // spend original choice currency. Restore earned choices, never parts.
            let mut tokens = u8::from(game.career.league >= 3);
            for goal in game.content.leagues.iter().flat_map(|league| &league.goals) {
                if goal.prot_unlock
                    && game
                        .career
                        .goal_progress
                        .get(&goal.id)
                        .map(|p| p.complete)
                        .unwrap_or(false)
                {
                    tokens = tokens.wrapping_add(1);
                }
            }
            game.career.native_performance = Some(crate::NativePerformanceCareer {
                prototype_tokens: tokens,
                ..Default::default()
            });
        }
        for (id, custom) in &game.career.garage {
            game.career
                .parts_inventory
                .entry(id.clone())
                .or_insert_with(|| crate::garage::owned_parts(custom));
        }
        game.difficulty = save.difficulty.min(2);
        game.profile = save.profile;
        game.quick_customizations = save.quick_customizations;
        if let Some(interrupted) = save.interrupted_race {
            game.career.cash = game
                .career
                .cash
                .checked_add(interrupted.refund())
                .ok_or("Interrupted race refund exceeds the cash limit")?;
            record_transaction(
                &mut game.career,
                crate::TransactionKind::RaceRefund,
                interrupted.refund(),
                Some(interrupted.car_id.clone()),
                Some(interrupted.event_id.clone()),
                "Interrupted race cancelled; unsettled cash returned and owned car retained",
            );
            game.recovered_race = Some(interrupted);
        }
        Ok(game)
    }
    pub fn recovered_race(&self) -> Option<&InterruptedRace> {
        self.recovered_race.as_ref()
    }
    pub fn command(&mut self, command: GameCommand) -> Result<(), String> {
        match command {
            GameCommand::AcceptNativePaint { car_id, paint } => {
                paint.price().ok_or("Unsupported native paint family")?;
                let prior = if self.quick_mode {
                    self.quick_customizations
                        .get(&car_id)
                        .or_else(|| self.career.garage.get(&car_id))
                } else {
                    self.pending_customizations
                        .get(&car_id)
                        .or_else(|| self.career.garage.get(&car_id))
                };
                let mut custom = prior.cloned().unwrap_or_default();
                custom.native_paint = Some(paint);
                crate::paint::sync_customization(&mut custom);
                self.command(GameCommand::Customize {
                    car_id: car_id.clone(),
                    customization: custom.clone(),
                })?;
                if self.quick_mode {
                    self.quick_customizations.insert(car_id, custom);
                } else {
                    self.accepted_native_paint.insert(car_id.clone());
                    self.pending_customizations.insert(car_id, custom);
                }
            }
            GameCommand::UnlockPrototype { league, category } => {
                if !(3..=9).contains(&league) || league > self.career.league {
                    return Err("Prototype choice is unavailable in this league".into());
                }
                let performance = self
                    .career
                    .native_performance
                    .get_or_insert_with(Default::default);
                if performance.prototype_unlocks.contains(&(league, category)) {
                    return Err("Prototype choice is already unlocked".into());
                }
                if performance.prototype_tokens == 0 {
                    return Err("No prototype choice available".into());
                }
                performance.prototype_unlocks.push((league, category));
                performance.prototype_tokens -= 1;
            }
            GameCommand::SetDifficulty { level } => {
                if level > 2 {
                    return Err("Difficulty must be 0 (Easy), 1 (Normal), or 2 (Hard)".into());
                }
                self.difficulty = level;
            }
            GameCommand::Checkout => self.checkout()?,
            GameCommand::DiscardCart { car_id } => {
                if let Some(id) = car_id {
                    self.pending_customizations.remove(&id);
                    self.accepted_native_paint.remove(&id);
                } else {
                    self.pending_customizations.clear();
                    self.accepted_native_paint.clear();
                }
            }
            GameCommand::RemoveCartItem { item_id } => {
                let item = self
                    .cart_items()
                    .into_iter()
                    .find(|item| item.id == item_id)
                    .ok_or("Unknown cart item")?;
                let old = self
                    .career
                    .garage
                    .get(&item.car_id)
                    .ok_or("Cart vehicle is no longer owned")?;
                let preview = self
                    .pending_customizations
                    .get_mut(&item.car_id)
                    .ok_or("No preview for cart item")?;
                crate::garage::revert_field(preview, old, &item.field);
                if item.field == "paint" {
                    self.accepted_native_paint.remove(&item.car_id);
                }
                if preview == old && !self.accepted_native_paint.contains(&item.car_id) {
                    self.pending_customizations.remove(&item.car_id);
                }
            }
            GameCommand::OfferDriverBet { racer, amount } => {
                let race = self.race.as_mut().ok_or("No race grid")?;
                if !race.career
                    || race.spectating
                    || race.countdown <= 0.
                    || race.settled
                    || race.wager > 0
                    || race.pink_slip
                {
                    return Err("Grid stake unavailable".into());
                }
                if racer == 0
                    || racer >= race.racers.len()
                    || amount == 0
                    || self.career.cash < i64::from(amount)
                {
                    return Err("Invalid rival or stake".into());
                }
                // Native class BetRanges recovered; conversion/preference is an explicit adaptation.
                let range = [5, 8, 15, 21, 36, 50, 75, 110, 160, 500]
                    [usize::from(race.event.league).min(9)]
                    * 1000u32;
                let gene = race.racers[racer].dna.gambling_genes[1].min(10) as f32;
                let preferred =
                    ((range as f32 * (0.4 + gene * 0.04) / 250.).ceil() as u32 * 250).min(range);
                let counter = amount.max(preferred).min(range);
                race.bet_offer = Some(crate::DriverBetOffer {
                    racer,
                    kind: crate::BetKind::Cash,
                    amount,
                    counter_amount: counter,
                    status: if counter == amount {
                        crate::BetOfferStatus::Offered
                    } else {
                        crate::BetOfferStatus::Countered
                    },
                    reason: if counter == amount {
                        "Rival accepts this stake".into()
                    } else {
                        format!("Rival counters with ${counter}")
                    },
                });
            }
            GameCommand::OfferPinkSlip { racer } => {
                let race = self.race.as_mut().ok_or("No race grid")?;
                if !race.career
                    || race.spectating
                    || race.countdown <= 0.
                    || race.settled
                    || race.wager > 0
                    || race.pink_slip
                {
                    return Err("Grid stake unavailable".into());
                }
                if racer == 0 || racer >= race.racers.len() || self.career.garage.len() < 2 {
                    return Err("Pink slips require a rival and a spare owned vehicle".into());
                }
                if self.career.garage.contains_key(&race.racers[racer].car_id) {
                    return Err("Choose a rival whose car is not already in your garage".into());
                }
                race.bet_offer = Some(crate::DriverBetOffer {
                    racer,
                    kind: crate::BetKind::PinkSlip,
                    amount: 0,
                    counter_amount: 0,
                    status: crate::BetOfferStatus::Offered,
                    reason: "Lose to this rival and forfeit your selected vehicle".into(),
                });
            }
            GameCommand::AcceptBetOffer => {
                let offer = self
                    .race
                    .as_ref()
                    .and_then(|r| r.bet_offer.clone())
                    .ok_or("No bet offer")?;
                if !matches!(
                    offer.status,
                    crate::BetOfferStatus::Offered | crate::BetOfferStatus::Countered
                ) {
                    return Err("Offer is already closed".into());
                }
                if offer.kind == crate::BetKind::Cash {
                    self.command(GameCommand::PlaceDriverBet {
                        racer: offer.racer,
                        amount: offer.counter_amount,
                    })?;
                } else {
                    let race = self.race.as_mut().unwrap();
                    if race.countdown <= 0. || race.settled || self.career.garage.len() < 2 {
                        return Err("Pink slip offer expired".into());
                    }
                    race.pink_slip = true;
                    race.bet_racer = offer.racer;
                }
                self.race
                    .as_mut()
                    .unwrap()
                    .bet_offer
                    .as_mut()
                    .unwrap()
                    .status = crate::BetOfferStatus::Accepted;
            }
            GameCommand::DeclineBetOffer => {
                let offer = self
                    .race
                    .as_mut()
                    .and_then(|r| r.bet_offer.as_mut())
                    .ok_or("No bet offer")?;
                if offer.status == crate::BetOfferStatus::Accepted {
                    return Err("An accepted stake cannot be withdrawn".into());
                }
                offer.status = crate::BetOfferStatus::Declined;
            }
            GameCommand::OpenGrid => {
                let race = self.race.as_ref().ok_or("No race grid")?;
                if race.elapsed > 0. || race.countdown <= 0. || race.spectating {
                    return Err("Race has already launched".into());
                }
                self.screen = GameScreen::Grid;
            }
            GameCommand::LaunchRace => {
                if self.screen != GameScreen::Grid {
                    return Err("No grid to launch".into());
                }
                self.screen = GameScreen::Race;
            }
            GameCommand::PlaceDriverBet { racer, amount } => {
                let race = self.race.as_mut().ok_or("No race grid")?;
                if !race.career || race.spectating || race.countdown <= 0. || race.settled {
                    return Err("Driver bets require the career grid before launch".into());
                }
                if racer == 0 || racer >= race.racers.len() {
                    return Err("Choose an opponent".into());
                }
                if race.wager > 0 {
                    return Err("Driver bet already escrowed".into());
                }
                if amount == 0 || self.career.cash < i64::from(amount) {
                    return Err("Insufficient driver stake".into());
                }
                self.career.cash -= i64::from(amount);
                race.wager = amount;
                race.bet_racer = racer;
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::WagerEscrow,
                    -i64::from(amount),
                    Some(race.racers[0].car_id.clone()),
                    Some(race.event.id.clone()),
                    "Selected driver wager escrow",
                );
            }
            GameCommand::StartSpectating { event_id } => {
                let event = self
                    .content
                    .events
                    .iter()
                    .find(|e| e.id == event_id)
                    .ok_or("Unknown event")?;
                if event.league > self.career.league {
                    return Err("Spectator league is locked".into());
                }
                if event.opponents == 0 || event.mode.is_drift() {
                    return Err("Choose a circuit race with multiple drivers".into());
                }
                self.start_race(&event_id, false, 0, false, true)?;
                let race = self.race.as_mut().unwrap();
                race.spectating = true;
                race.total_rounds = 1;
                race.event.contest_type = "Spectator".into();
                race.racers[0].dna = self.content.drivers[0].clone();
                race.racers[0].name = race.racers[0].dna.name.clone();
            }
            GameCommand::PlaceSpectatorBet { racer, amount } => {
                let race = self.race.as_mut().ok_or("No race")?;
                if !race.spectating || race.settled || self.screen != GameScreen::Race {
                    return Err("Spectator betting is unavailable".into());
                }
                if amount == 0 || self.career.cash < i64::from(amount) {
                    return Err("Insufficient spectator stake".into());
                }
                let entrant = race.racers.get(racer).ok_or("Unknown racer")?;
                if entrant.finished || entrant.eliminated {
                    return Err("Racer cannot receive new bets".into());
                }
                let odds = spectator_odds(race)[racer];
                race.spectator_bets.push(crate::SpectatorBet {
                    racer,
                    stake: amount,
                    odds,
                    payout: 0,
                });
                self.career.cash -= i64::from(amount);
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::SpectatorStake,
                    -i64::from(amount),
                    None,
                    Some(race.event.id.clone()),
                    "Spectator bet placed at displayed odds",
                );
            }
            GameCommand::SpectatorCheer { .. } => {
                return Err("Spooking is not part of Oversteer races".into());
            }
            GameCommand::CustomizeAvatar { profile } => self.profile = profile,
            GameCommand::ShowPodium => {
                if self.screen != GameScreen::Results {
                    return Err("Podium requires settled race".into());
                }
                self.screen = GameScreen::Podium;
            }
            GameCommand::Navigate { screen } => {
                if screen == GameScreen::Crew {
                    return Err("Crew management is deferred".into());
                }
                if matches!(
                    screen,
                    GameScreen::Race
                        | GameScreen::Results
                        | GameScreen::Complete
                        | GameScreen::Grid
                ) {
                    return Err("Screen requires a game transition".into());
                }
                if screen != GameScreen::Paused && self.race.is_some() {
                    self.abandon_race();
                }
                if screen == GameScreen::QuickRace {
                    self.quick_mode = true;
                } else if matches!(
                    screen,
                    GameScreen::Career | GameScreen::Garage | GameScreen::Dealership
                ) {
                    self.quick_mode = false;
                }
                self.screen = screen;
            }
            GameCommand::SelectCar { car_id } => {
                self.car(&car_id)?;
                self.selected_car = car_id;
            }
            GameCommand::StartRace {
                event_id,
                career,
                wager,
                pink_slip,
            } => {
                if self.race.as_ref().is_some_and(|race| !race.settled) {
                    return Err("Finish, restart or leave the current race first".into());
                }
                self.start_race(&event_id, career, wager, pink_slip, false)?;
            }
            GameCommand::BuyCar { car_id } => {
                let car = self.car(&car_id)?.clone();
                if self.career.garage.contains_key(&car_id) {
                    return Err("Vehicle already owned".into());
                }
                if car.league > self.career.league {
                    return Err("Vehicle league is locked".into());
                }
                if self.career.cash < i64::from(car.price) {
                    return Err("Insufficient cash".into());
                }
                self.career.cash -= i64::from(car.price);
                self.career
                    .garage
                    .insert(car_id.clone(), Customization::default());
                let history = self
                    .career
                    .vehicle_history
                    .entry(car_id.clone())
                    .or_default();
                history.purchase_price = car.price;
                history.total_spent += u64::from(car.price);
                history.acquired_by = "Purchased".into();
                self.career.parts_inventory.insert(
                    car_id.clone(),
                    crate::garage::owned_parts(&Customization::default()),
                );
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::BuyCar,
                    -i64::from(car.price),
                    Some(car_id.clone()),
                    None,
                    "Dealership purchase",
                );
                self.selected_car = car_id;
            }
            GameCommand::SellCar { car_id } => {
                let price = self.car(&car_id)?.price;
                if self.career.garage.len() <= 1 {
                    return Err("Keep one career vehicle".into());
                }
                if self.career.garage.remove(&car_id).is_none() {
                    return Err("Vehicle not owned".into());
                }
                self.career.cash += i64::from(price / 2);
                self.pending_customizations.remove(&car_id);
                self.accepted_native_paint.remove(&car_id);
                self.career
                    .vehicle_history
                    .entry(car_id.clone())
                    .or_default()
                    .sales += 1;
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::SellCar,
                    i64::from(price / 2),
                    Some(car_id.clone()),
                    None,
                    "Vehicle sale",
                );
                if self.selected_car == car_id {
                    self.selected_car = self.career.garage.keys().next().unwrap().clone();
                }
            }
            GameCommand::Customize {
                car_id,
                mut customization,
            } => {
                let prior = if self.quick_mode {
                    self.quick_customizations
                        .get(&car_id)
                        .or_else(|| self.career.garage.get(&car_id))
                } else {
                    self.pending_customizations
                        .get(&car_id)
                        .or_else(|| self.career.garage.get(&car_id))
                };
                if customization.native_paint.is_some()
                    || prior.and_then(|p| p.native_paint.as_ref()).is_some()
                {
                    let prior = prior.cloned().unwrap_or_default();
                    customization.native_paint = prior.native_paint;
                    customization.paint = prior.paint;
                    customization.finish = prior.finish;
                }
                crate::paint::sync_customization(&mut customization);
                // Retired tier survives old saves but cannot create a new fake upgrade.
                customization.nitrous = if self.quick_mode {
                    self.quick_customizations
                        .get(&car_id)
                        .or_else(|| self.career.garage.get(&car_id))
                } else {
                    self.career.garage.get(&car_id)
                }
                .map(|prior| prior.nitrous)
                .unwrap_or(0);
                let car = self.car(&car_id)?;
                for (slot, part) in &customization.parts {
                    if part != "stock"
                        && !car
                            .parts
                            .get(slot)
                            .map(|catalog| catalog.contains(part))
                            .unwrap_or(false)
                    {
                        return Err(format!(
                            "Part {part} is incompatible with {slot} on this vehicle"
                        ));
                    }
                }
                if customization.body_kit != "stock"
                    && !car.body_kits.contains(&customization.body_kit)
                {
                    return Err("Body kit incompatible with this vehicle".into());
                }
                if customization.interior_kit != "stock"
                    && !car.interior_kits.contains(&customization.interior_kit)
                {
                    return Err("Interior kit incompatible with this vehicle".into());
                }
                if [
                    customization.engine,
                    customization.transmission,
                    customization.suspension,
                    customization.tyres,
                ]
                .iter()
                .any(|v| *v > 3)
                {
                    return Err("Upgrade level must be zero through three".into());
                }
                if self.quick_mode {
                    self.quick_customizations.insert(car_id, customization);
                } else if self.career.garage.contains_key(&car_id) {
                    if self.career.garage[&car_id] == customization
                        && !self.accepted_native_paint.contains(&car_id)
                    {
                        self.pending_customizations.remove(&car_id);
                    } else {
                        self.pending_customizations.insert(car_id, customization);
                    }
                } else {
                    return Err("Purchase this vehicle to save career customization".into());
                }
            }
            GameCommand::Recruit { .. } => {
                return Err("Crew management is deferred".into());
            }
            GameCommand::Pause => {
                if self.screen == GameScreen::Race {
                    self.screen = GameScreen::Paused;
                }
            }
            GameCommand::Resume => {
                if self.screen == GameScreen::Paused {
                    self.screen = GameScreen::Race;
                }
            }
            GameCommand::Restart => {
                let race = self.race.as_ref().ok_or("No race to restart")?;
                if race.spectating {
                    return Err("Spectator stakes cannot be restarted".into());
                }
                let id = race.event.id.clone();
                let career = race.career;
                self.abandon_race();
                self.screen = if career {
                    GameScreen::Career
                } else {
                    GameScreen::QuickRace
                };
                self.start_race(&id, career, 0, false, false)?;
            }
            GameCommand::Continue => {
                if self.race.as_ref().is_some_and(|race| !race.settled)
                    && self.screen != GameScreen::RoundResults
                {
                    return Err("Finish or leave the current race before continuing".into());
                }
                if self.screen == GameScreen::RoundResults {
                    self.next_round()?;
                    return Ok(());
                }
                if self.screen == GameScreen::Podium {
                    self.screen = GameScreen::Results;
                    return Ok(());
                }
                self.race = None;
                let complete =
                    if let Some(last) = self.content.leagues.iter().max_by_key(|l| l.league) {
                        last.goals.iter().filter(|g| g.qualifier).any(|g| {
                            self.career
                                .goal_progress
                                .get(&g.id)
                                .map(|p| p.complete)
                                .unwrap_or(false)
                        })
                    } else {
                        self.content
                            .events
                            .iter()
                            .filter(|e| !e.is_sponsor)
                            .all(|e| self.career.completed_events.contains(&e.id))
                    };
                self.screen = if complete {
                    GameScreen::Complete
                } else {
                    GameScreen::Career
                };
            }
            GameCommand::ResetCar => {
                if let Some(race) = &mut self.race {
                    if race.spectating {
                        return Err("Spectators cannot reset drivers".into());
                    }
                    let p =
                        race.track.surface()[race.racers[0].checkpoint % race.track.points.len()];
                    race.racers[0].state.position = p;
                    race.racers[0].state.velocity = [0.; 3];
                    let next = race.track.points
                        [(race.racers[0].checkpoint + 1) % race.track.points.len()];
                    race.racers[0]
                        .state
                        .set_yaw((next[0] - p[0]).atan2(next[2] - p[2]));
                }
            }
        }
        Ok(())
    }
    fn car(&self, id: &str) -> Result<&CarDefinition, String> {
        self.content
            .cars
            .iter()
            .find(|c| c.id == id)
            .ok_or_else(|| format!("Unknown vehicle {id}"))
    }
    fn abandon_race(&mut self) {
        let Some(race) = self.race.take() else {
            return;
        };
        if race.settled || !race.career || race.spectating {
            return;
        }
        self.career.losses += 1;
        let car_id = &race.racers[0].car_id;
        self.career
            .vehicle_history
            .entry(car_id.clone())
            .or_default()
            .losses += 1;
        if race.wager > 0 {
            // The original stake was already deducted at acceptance/entry.
            record_transaction(
                &mut self.career,
                crate::TransactionKind::WagerSettlement,
                0,
                Some(car_id.clone()),
                Some(race.event.id.clone()),
                "Cash stake forfeited on voluntary restart or abandonment",
            );
        }
        if race.pink_slip && self.career.garage.len() > 1 {
            self.career.garage.remove(car_id);
            self.career
                .vehicle_history
                .entry(car_id.clone())
                .or_default()
                .pink_slip_losses += 1;
            self.pending_customizations.remove(car_id);
            self.accepted_native_paint.remove(car_id);
            record_transaction(
                &mut self.career,
                crate::TransactionKind::PinkSlipLoss,
                0,
                Some(car_id.clone()),
                Some(race.event.id.clone()),
                "Vehicle forfeited on voluntary restart or abandonment",
            );
            self.selected_car = self.career.garage.keys().next().unwrap().clone();
        }
    }
    fn start_race(
        &mut self,
        id: &str,
        career: bool,
        wager: u32,
        pink_slip: bool,
        spectating: bool,
    ) -> Result<(), String> {
        let mut event = self
            .content
            .events
            .iter()
            .find(|e| e.id == id)
            .ok_or("Unknown event")?
            .clone();
        let stage_indices = runtime_stage_indices(&event);
        if let Some(stage) = stage_indices.first().and_then(|i| event.stages.get(*i)) {
            event.track_id = stage.track_id.clone();
            event.laps = stage.laps;
            if stage.target > 0. {
                event.target = stage.target;
            }
        }
        if event.challenge_data > 0. && event.stages.is_empty() {
            event.target = event.challenge_data;
        }
        let total_rounds = if event.contest_type == "Tournament" {
            stage_indices.len() as u32
        } else {
            (event.stages.len() as u32).max(event.rounds).max(1)
        };
        let track = self
            .content
            .tracks
            .iter()
            .find(|t| t.id == event.track_id)
            .ok_or("Unknown event track")?
            .clone();
        if track.points.len() < 3 {
            return Err("Track needs at least three checkpoints".into());
        }
        let collision_world = cached_collision(&mut self.collision_worlds, &track)?;
        let eligible_cars: Vec<_> = self
            .content
            .cars
            .iter()
            .filter(|car| car.supports_class(&event.car_class))
            .collect();
        let car = if spectating {
            eligible_cars
                .first()
                .copied()
                .ok_or("No vehicle matches the event class")?
        } else {
            self.car(&self.selected_car)?
        };
        if !car.supports_class(&event.car_class) {
            return Err(format!("This event requires class {}", event.car_class));
        }
        if career && !self.pending_customizations.is_empty() {
            return Err("Checkout or discard pending garage changes before racing".into());
        }
        if career {
            if !self.career.garage.contains_key(&car.id) {
                return Err("Career requires an owned vehicle".into());
            }
            if event.qualifier
                && event.league == self.career.league
                && self
                    .content
                    .leagues
                    .iter()
                    .any(|l| l.league == event.league)
                && !self.league_progress().promotion_open
            {
                return Err("Win this tier's circuit and drift events to open promotion".into());
            }
            if event.league > self.career.league {
                return Err("Win the previous tier's promotion race to unlock this event".into());
            }
            if self.career.cash < i64::from(wager) + i64::from(event.entrance_fee) {
                return Err("Insufficient cash for wager".into());
            }
            if pink_slip && self.career.garage.len() < 2 {
                return Err("Pink slips require a spare vehicle".into());
            }
        }
        let selected = self.selected_car.clone();
        let mut racers = vec![];
        let player_entry = event
            .contestants
            .iter()
            .find(|c| c.tag.starts_with("Player"));
        let native_player_team = player_entry.map(|c| c.team).unwrap_or(0);
        let ordered: Vec<_> = if event.contest_type == "Tournament" {
            player_entry
                .into_iter()
                .chain(tournament_rival(&event, 1, &self.content.drivers))
                .collect()
        } else {
            player_entry
                .into_iter()
                .chain(
                    event
                        .contestants
                        .iter()
                        .filter(|c| !c.tag.starts_with("Player")),
                )
                .collect()
        };
        let effective_opponents = if event.contest_type == "Tournament" {
            1
        } else {
            event.opponents
        };
        for i in 0..=effective_opponents as usize {
            let entry = ordered.get(i).copied();
            let dna = if i == 0 {
                DriverDna::default()
            } else if entry
                .map(|c| c.tag.starts_with("Crewmate"))
                .unwrap_or(false)
            {
                self.career.crew.first().cloned().unwrap_or_else(|| {
                    self.content
                        .drivers
                        .iter()
                        .find(|d| d.native_tag == "Char09")
                        .cloned()
                        .unwrap_or_default()
                })
            } else {
                entry
                    .and_then(|c| self.content.drivers.iter().find(|d| d.native_tag == c.tag))
                    .cloned()
                    .unwrap_or_else(|| {
                        self.content
                            .drivers
                            .get((i + event.league as usize) % self.content.drivers.len())
                            .cloned()
                            .unwrap_or_default()
                    })
            };
            let definition = if i == 0 {
                car
            } else {
                entry
                    .and_then(|e| eligible_cars.iter().copied().find(|c| c.id == e.car_id))
                    .unwrap_or(eligible_cars[(i + event.league as usize) % eligible_cars.len()])
            };
            let custom = if i > 0 {
                Some(rival_customization(i))
            } else if career {
                self.career.garage.get(&definition.id).cloned()
            } else {
                self.quick_customizations
                    .get(&definition.id)
                    .or_else(|| self.career.garage.get(&definition.id))
                    .cloned()
            }
            .unwrap_or_default();
            let state = grid_state(i, &track, collision_world.as_deref());
            racers.push(Racer {
                human_drift: crate::HumanDriftState::default(),
                unsupported_time: 0.,
                drive_layout: definition.handling.layout,
                wheelbase: definition.handling.wheelbase,
                max_steer: definition.handling.max_steer,
                drift_direction: 1.,
                drift_kick_latched: false,
                stuck_time: 0.,
                reverse_recovery: 0.,
                team: if i == 0 {
                    0
                } else if matches!(event.mode, RaceMode::TeamRace | RaceMode::TwinDrift) {
                    if let Some(entry) = entry.filter(|entry| entry.team > 0) {
                        if entry.team == native_player_team {
                            0
                        } else if entry.team < native_player_team {
                            entry.team
                        } else {
                            entry.team - 1
                        }
                    } else {
                        (i % 2) as u8
                    }
                } else {
                    1
                },
                lives: event.lives.max(1),
                chain_score: 0.,
                input_clock: 0.,
                lap_start: 0.,
                best_lap_time: 0.,
                clean_lap: true,
                finish_time: None,
                life_cooldown: 0.,
                drift_state: crate::NativeDriftState::default(),
                enduro_stopped: false,
                car_id: definition.id.clone(),
                name: if i == 0 {
                    self.profile.name.clone()
                } else {
                    dna.name.clone()
                },
                state,
                applied_input: PlayerInput::default(),
                customization: custom,
                dna,
                lap: 0,
                checkpoint: 1,
                progress: 0.,
                score: 0.,
                spook: 0.,
                finished: false,
                eliminated: false,
            });
        }
        if career
            && pink_slip
            && racers
                .get(1)
                .is_none_or(|rival| self.career.garage.contains_key(&rival.car_id))
        {
            return Err("Pink slips require a rival car not already in your garage".into());
        }
        if career {
            self.career.cash -= i64::from(wager) + i64::from(event.entrance_fee);
            if wager > 0 {
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::WagerEscrow,
                    -i64::from(wager),
                    Some(selected.clone()),
                    Some(event.id.clone()),
                    "Race wager escrow",
                );
            }
            if event.entrance_fee > 0 {
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::EntranceFee,
                    -i64::from(event.entrance_fee),
                    Some(selected.clone()),
                    Some(event.id.clone()),
                    "Event entrance fee",
                );
            }
        }
        let racer_count = racers.len();
        if event.stage_mode() == RaceMode::Eliminator {
            event.laps = racer_count.saturating_sub(1) as u32;
        }
        if let Some(player) = racers.first_mut() {
            player.team = 0;
        }
        let finish_observation_window =
            if career && matches!(event.stage_mode(), RaceMode::Circuit | RaceMode::TeamRace) {
                self.content
                    .leagues
                    .iter()
                    .find(|l| l.league == self.career.league)
                    .into_iter()
                    .flat_map(|l| &l.goals)
                    .filter(|g| {
                        g.kind.eq_ignore_ascii_case("CloseFinish")
                            || g.kind.eq_ignore_ascii_case("VictoryMargin")
                    })
                    .filter_map(|g| g.args.first().and_then(|a| a.as_f64()))
                    .fold(0., f64::max) as f32
            } else {
                0.
            };
        self.race = Some(Race {
            collision_world,
            bet_offer: None,
            finish_observation_window,
            bet_racer: 1,
            spectating: false,
            spectator_bets: vec![],
            max_speed_kph: 0.,
            air_time: 0.,
            spooked_tags: vec![],
            round: 1,
            total_rounds,
            stage_indices,
            tournament_points: vec![0; racer_count],
            speed_challenge: crate::SpeedChallengeState::Pending,
            event,
            track,
            racers,
            elapsed: 0.,
            countdown: 3.,
            career,
            wager,
            pink_slip,
            settled: false,
            combo: 1.,
        });
        self.result = None;
        self.tick_accumulator = 0.;
        self.quick_mode = !career;
        self.selected_car = selected;
        self.screen = GameScreen::Race;
        Ok(())
    }
    pub fn advance(&mut self, delta_seconds: f32, input: PlayerInput) {
        if self.screen != GameScreen::Race || !delta_seconds.is_finite() || delta_seconds <= 0. {
            return;
        }
        // Explicit reconstruction timing policy, not a claim about the unrecovered native clock.
        // Render cadence never changes gameplay sampling or the native dt-squared score equation.
        const TICK: f64 = 1. / 60.;
        self.tick_accumulator += f64::from(delta_seconds.min(0.2));
        while self.tick_accumulator + 1e-9 >= TICK {
            self.tick_accumulator = (self.tick_accumulator - TICK).max(0.);
            let (n, h) = substeps(TICK as f32);
            for _ in 0..n {
                self.advance_step(h, input);
            }
            if self.screen != GameScreen::Race {
                self.tick_accumulator = 0.;
                break;
            }
        }
    }
    fn advance_step(&mut self, h: f32, input: PlayerInput) {
        let Some(race) = &mut self.race else { return };
        if race.countdown > 0. {
            race.countdown = (race.countdown - h).max(0.);
            return;
        }
        race.elapsed += h;
        // Native scheduler ordering: prepare all; then each object's contacts immediately before its update; finish all.
        let old_laps: Vec<_> = race.racers.iter().map(|r| r.lap).collect();
        let old_progress: Vec<_> = race.racers.iter().map(|r| r.progress).collect();
        let old_positions: Vec<_> = race.racers.iter().map(|r| r.state.position).collect();
        let mut drift_multipliers = Vec::new();
        if race.event.stage_mode() == RaceMode::DriftKing && !race.spectating {
            drift_multipliers.resize(race.racers.len(), 1.);
            // Sample scores/ranks before this tick: native rank-update scheduling remains unbound.
            let human_total = race.racers[0].drift_state.total();
            for (rank, index) in ranked_indices(race).into_iter().enumerate() {
                if index > 0 {
                    drift_multipliers[index] = crate::native_king_multiplier(
                        Some(human_total),
                        race.racers[index].drift_state.total(),
                        rank as i32 + 1,
                        u32::from(self.career.league),
                        false, // Native config36/gamestate context mapping remains unbound.
                    );
                }
            }
        }
        for i in 0..race.racers.len() {
            // Finish times classify racers, but their cars must keep driving so
            // they do not become immovable obstacles for the remaining field.
            if race.racers[i].eliminated {
                continue;
            }
            if i > 0
                && race.event.stage_mode() == RaceMode::BeatCar
                && race.elapsed <= race.event.target.max(0.)
            {
                continue;
            }
            race.racers[i].input_clock += h;
            if race.event.stage_mode().is_drift() {
                let r = &mut race.racers[i];
                let kick = drift_kick_requested(r);
                if kick && !r.drift_kick_latched {
                    if r.drift_state.phase != crate::DriftPhase::Idle {
                        r.drift_direction = -r.drift_direction;
                    } else {
                        let cp = r.checkpoint;
                        let points = &race.track.points;
                        let a = points[(cp + points.len() - 1) % points.len()];
                        let b = points[cp];
                        let c = points[(cp + 1) % points.len()];
                        let turn = wrap_angle(
                            (c[0] - b[0]).atan2(c[2] - b[2]) - (b[0] - a[0]).atan2(b[2] - a[2]),
                        );
                        if turn.abs() > 0.001 {
                            r.drift_direction = turn.signum();
                        }
                    }
                    r.drift_kick_latched = true;
                } else if !kick {
                    r.drift_kick_latched = false;
                }
            }
            let mut u = input;
            if i > 0 || race.spectating || race.racers[i].finished {
                u = avoid_eliminated_cars(
                    race,
                    i,
                    ai_input(&race.racers[i], &race.track, race.event.stage_mode(), false),
                );
                // Reconstruction option: Normal preserves the baseline; Easy slows AI pursuit.
                // Native difficulty scaling consumers have not been recovered.
                if self.difficulty == 0 {
                    u.throttle *= 0.75;
                }
                if self.difficulty == 2 {
                    u.throttle = (u.throttle * 1.15).min(1.);
                }
            }
            // Body SAT queries and ordered responses preserve explicit object/contact ordering.
            let car_i = self
                .content
                .cars
                .iter()
                .find(|c| c.id == race.racers[i].car_id);
            for j in 0..race.racers.len() {
                if i == j {
                    continue;
                }
                let car_j = self
                    .content
                    .cars
                    .iter()
                    .find(|c| c.id == race.racers[j].car_id);
                let half = |c: Option<&CarDefinition>| {
                    c.map(|c| {
                        [
                            if c.width_m > 0. {
                                c.width_m / 2.
                            } else {
                                (c.handling.track_width + 0.4) / 2.
                            },
                            if c.length_m > 0. {
                                c.length_m / 2.
                            } else {
                                (c.handling.wheelbase + 1.4) / 2.
                            },
                        ]
                    })
                    .unwrap_or([1., 2.2])
                };
                let state_i = &race.racers[i].state;
                let state_j = &race.racers[j].state;
                if let Some(push) = crate::chassis_overlap(
                    state_i.position,
                    state_i.yaw(),
                    half(car_i),
                    state_j.position,
                    state_j.yaw(),
                    half(car_j),
                ) {
                    let other_velocity = state_j.velocity;
                    let depth = (push[0] * push[0] + push[2] * push[2]).sqrt();
                    let normal = [push[0] / depth, 0., push[2] / depth];
                    let r = &mut race.racers[i];
                    r.state.position[0] += push[0];
                    r.state.position[2] += push[2];
                    let closing = (r.state.velocity[0] - other_velocity[0]) * normal[0]
                        + (r.state.velocity[2] - other_velocity[2]) * normal[2];
                    if closing < 0. {
                        r.state.velocity[0] -= normal[0] * closing * 0.8;
                        r.state.velocity[2] -= normal[2] * closing * 0.8;
                        r.state.yaw_rate *= 0.8;
                    }
                    if closing < -2. || depth > 0.2 {
                        register_collision(r, race.event.stage_mode());
                    }
                }
                if i > 0 {
                    let r = &race.racers[i];
                    let other = &race.racers[j];
                    let delta = [
                        other.state.position[0] - r.state.position[0],
                        other.state.position[2] - r.state.position[2],
                    ];
                    let yaw = r.state.yaw();
                    let ahead = delta[0] * yaw.sin() + delta[1] * yaw.cos();
                    let side = delta[0] * yaw.cos() - delta[1] * yaw.sin();
                    let lane_clearance = (car_i.map_or(1.8, |c| c.handling.body_width)
                        + car_j.map_or(1.8, |c| c.handling.body_width))
                        * 0.5
                        + 0.15;
                    if ahead > 0. && ahead < 16. && side.abs() < lane_clearance {
                        let closing = (r.state.velocity[0] - other.state.velocity[0]) * yaw.sin()
                            + (r.state.velocity[2] - other.state.velocity[2]) * yaw.cos();
                        let lengths = car_i.map_or(4.5, |c| c.handling.body_length)
                            + car_j.map_or(4.5, |c| c.handling.body_length);
                        let gap = ahead - lengths * 0.5;
                        // Grid rows travel together. Distance alone kept rear
                        // rivals braking against their throttle at engine idle.
                        if closing > 0.2 && gap < 1.5 + closing * 1.2 {
                            u.throttle = u.throttle.min(0.2);
                            if gap < 0.75 + closing * 0.5 {
                                u.brake = u.brake.max((closing * 0.15).min(0.8));
                            }
                        }
                        if closing > 0.2 {
                            let evade = if side >= 0. { -1. } else { 1. };
                            u.steering =
                                (u.steering + evade * 0.12 * (1. - ahead / 16.)).clamp(-1., 1.);
                        }
                    }
                }
            }
            let r = &mut race.racers[i];
            let Some(def) = self.content.cars.iter().find(|c| c.id == r.car_id) else {
                continue;
            };
            let handling = motion_handling(
                &def.handling,
                r,
                race.event.stage_mode(),
                i == 0 && !race.spectating,
            );

            r.state.nitrous_allowed = matches!(
                race.event.native_discipline,
                Some(
                    NativeDiscipline::Circuit
                        | NativeDiscipline::TestDrive
                        | NativeDiscipline::Solo
                )
            );
            r.state.extreme_nos = race.event.extreme_nos;
            r.state.nitrous_control_mode = if i == 0 && !race.spectating { 1 } else { 2 };
            r.life_cooldown = (r.life_cooldown - h).max(0.);
            update_surface_contacts(
                &mut r.state,
                &handling,
                &race.track,
                r.checkpoint,
                race.collision_world.as_deref(),
            );
            r.applied_input = u;
            r.state.step(&handling, &self.globals, u, h);
            if i == 0 && !race.spectating && !r.state.reversing {
                r.apply_human_motion(
                    &mut self.drift_assist_globals,
                    u,
                    h,
                    race.event.stage_mode().is_drift(),
                );
            }

            r.state.update_nitrous_gameplay(h);

            // 820F5480 follows the assistance call; the next tick consumes actor680.
            // SurfaceContact.active is the reconstruction's wheel-contact binding.
            if r.state
                .contacts
                .iter()
                .filter(|contact| contact.active)
                .count()
                < 2
            {
                r.unsupported_time += h;
            } else {
                r.unsupported_time = 0.;
            }
            r.reverse_recovery = (r.reverse_recovery - h).max(0.);
            if i == 0 {
                race.max_speed_kph = race.max_speed_kph.max(r.state.speed() * 3.6);
                if r.state
                    .contacts
                    .iter()
                    .all(|c| !c.active || r.state.position[1] - c.height > 0.85)
                {
                    race.air_time += h;
                }
            } else if r.spook >= 1. && !race.spooked_tags.contains(&r.dna.native_tag) {
                race.spooked_tags.push(r.dna.native_tag.clone());
            }
            let hit_wall = if let Some(world) = &race.collision_world {
                world.resolve_chassis(&mut r.state, &handling, old_positions[i])
            } else {
                road_contact(
                    &mut r.state,
                    &race.track,
                    h,
                    r.checkpoint,
                    handling.body_width * 0.5,
                )
            };
            if hit_wall {
                register_collision(r, race.event.stage_mode());
                if race.event.stage_mode() == RaceMode::LastManStanding {
                    r.eliminated = true;
                }
            }
            let target = race.track.points[r.checkpoint];
            let previous = race.track.points
                [(r.checkpoint + race.track.points.len() - 1) % race.track.points.len()];
            let segment = [target[0] - previous[0], target[2] - previous[2]];
            let length = (segment[0] * segment[0] + segment[1] * segment[1]).sqrt();
            let along = ((r.state.position[0] - previous[0]) * segment[0]
                + (r.state.position[2] - previous[2]) * segment[1])
                / length.max(0.01);
            r.progress = r.lap as f32 * race.track.points.len() as f32
                + (r.checkpoint + race.track.points.len() - 1) as f32
                    % race.track.points.len() as f32
                + (along / length.max(0.01)).clamp(0., 1.);
            // Recovery observes actual path progress after wall response: a wheel can
            // report speed while repeatedly pushing into the same barrier.
            // Valid stationary drift chains deliberately do not require route progress.
            let stalled = r.state.speed() < 1.
                || (!race.event.stage_mode().is_drift()
                    && hit_wall
                    && u.throttle > 0.1
                    && r.progress <= old_progress[i] + h * 0.05);
            if stalled && r.input_clock > 4. && r.reverse_recovery == 0. && r.unsupported_time == 0.
            {
                r.stuck_time += h;
                if r.stuck_time > 3. {
                    r.reverse_recovery = 4.;
                    r.stuck_time = 0.;
                }
            } else {
                r.stuck_time = 0.;
            }
            if distance_xz(r.state.position, target) < race.track.road_width.max(10.)
                || along > length
                    && distance_to_segment(r.state.position, previous, target).0
                        < race.track.road_width
            {
                if r.checkpoint == 0 {
                    r.lap += 1;
                    let lap_time = race.elapsed - r.lap_start;
                    if r.best_lap_time == 0. || lap_time < r.best_lap_time {
                        r.best_lap_time = lap_time;
                    }
                    r.lap_start = race.elapsed;
                    if race.event.stage_mode() == RaceMode::DriftObliterator {
                        let achieved = r.drift_state.total() as f32 >= race.event.target;
                        if !achieved {
                            r.lives = r.lives.saturating_sub(1);
                            if r.lives == 0 {
                                r.eliminated = true;
                            }
                        }
                        // Native82114840 clamps driftlap156 to the configured lap
                        // goal, so finishing the final lap does not reset its score.
                        if r.lap < race.event.laps {
                            r.drift_state.reset_lap();
                            r.score = 0.;
                            r.chain_score = 0.;
                        }
                    }
                }
                r.checkpoint = (r.checkpoint + 1) % race.track.points.len();
            }
            let mode = race.event.stage_mode();
            if r.finished {
                continue; // Preserve the classified score and finish time during rollout.
            }
            if mode.is_drift() {
                let banked = r.drift_state.advance(
                    r.state.speed(),
                    r.state.slip_angle,
                    h,
                    mode == RaceMode::DriftEndurance,
                    if mode == RaceMode::DriftObliterator && (i > 0 || race.spectating) {
                        10.
                    } else {
                        drift_multipliers.get(i).copied().unwrap_or(1.)
                    },
                    1.,
                );
                if mode == RaceMode::DriftEndurance && banked {
                    r.enduro_stopped = true;
                }
                r.score = r.drift_state.total() as f32;
                r.chain_score = r.drift_state.points as f32;
                if i == 0 {
                    race.combo = 1. + r.drift_state.chains as f32;
                }
            }
            if r.lap >= race.event.laps.max(1)
                && !matches!(mode, RaceMode::DriftKing | RaceMode::DriftEndurance)
            {
                r.finished = true;
                r.drift_state.bank();
                r.score = r.drift_state.total() as f32;
                r.chain_score = 0.;
                if r.finish_time.is_none() {
                    r.finish_time = Some(race.elapsed);
                }
            }
        }

        if race.event.stage_mode() == RaceMode::Eliminator {
            // 821370B8 evaluates the actor crossing its lap, rather than
            // removing the rear driver when the leader crosses.
            for (index, old_lap) in old_laps.iter().enumerate() {
                if race.racers[index].eliminated || race.racers[index].lap <= *old_lap {
                    continue;
                }
                let live: Vec<_> = ranked_indices(race)
                    .into_iter()
                    .filter(|i| !race.racers[*i].eliminated)
                    .collect();
                // Native actor380 is ONE-BASED (82139FF0/8213A5D8).
                // Rank liveCount−1 crosses, then vector[rank] selects the LAST other actor.
                if live.len() > 1 && live.get(live.len() - 2) == Some(&index) {
                    race.racers[*live.last().unwrap()].eliminated = true;
                }
            }
        }

        if race.event.stage_mode() == RaceMode::SpeedChallenge {
            race.speed_challenge = race.speed_challenge.update(
                race.racers[0].state.speed(),
                race.event.target,
                race.elapsed,
            );
        }
        let timeout = if race.event.time_limit > 0. {
            race.event.time_limit
        } else {
            match race.event.stage_mode() {
                RaceMode::Drift => race.event.target.max(60.).min(180.),
                RaceMode::TimeAttack => race.event.target.max(30.),
                RaceMode::SpeedChallenge => f32::INFINITY,
                RaceMode::TwinDrift => 180.,
                RaceMode::DriftKing => race.event.target.max(1.),
                _ => f32::INFINITY,
            }
        };
        let scores = team_scores(race);
        let target_achieved = match race.event.stage_mode() {
            RaceMode::SoloDrift => race.racers[0].drift_state.banked as f32 >= race.event.target,
            RaceMode::DriftEndurance => race.racers[0].enduro_stopped,
            RaceMode::TwinDrift => scores[0] >= race.event.target,
            RaceMode::DriftObliterator => false,
            RaceMode::SpeedChallenge => race.speed_challenge.failed(),
            RaceMode::Eliminator | RaceMode::LastManStanding => {
                race.racers.iter().filter(|r| !r.eliminated).count() == 1
            }
            _ => false,
        };
        let finished = (race.spectating && race.racers.iter().any(|r| r.finished))
            || race.racers[0].finished
            || race.racers[0].eliminated
            || race.elapsed >= timeout
            || target_achieved;
        let observing_finish = race.racers[0]
            .finish_time
            .map(|time| {
                race.finish_observation_window > 0.
                    && !race.racers[0].eliminated
                    && race.elapsed - time < race.finish_observation_window
                    && race.racers.iter().skip(1).all(|r| r.finish_time.is_none())
            })
            .unwrap_or(false);
        if finished && !observing_finish {
            self.settle();
        }
    }
    fn next_round(&mut self) -> Result<(), String> {
        let race = self.race.as_mut().ok_or("No contest in progress")?;
        if race.round >= race.total_rounds {
            return Err("Contest is complete".into());
        }
        race.round += 1;
        if let Some(stage) = race
            .stage_indices
            .get((race.round - 1) as usize)
            .and_then(|i| race.event.stages.get(*i))
        {
            race.track = self
                .content
                .tracks
                .iter()
                .find(|t| t.id == stage.track_id)
                .ok_or("Unknown stage track")?
                .clone();
            race.event.laps = stage.laps;
            if stage.target > 0. {
                race.event.target = stage.target;
            }
        }
        if race.event.contest_type == "Tournament" {
            if let Some(entry) = tournament_rival(&race.event, race.round, &self.content.drivers) {
                if let Some(rival) = race.racers.get_mut(1) {
                    if let Some(dna) = self
                        .content
                        .drivers
                        .iter()
                        .find(|d| d.native_tag == entry.tag)
                    {
                        rival.dna = dna.clone();
                        rival.name = dna.name.clone();
                    }
                    if let Some(car) = self.content.cars.iter().find(|c| c.id == entry.car_id) {
                        rival.car_id = car.id.clone();
                    }
                }
            }
        }
        if race.event.stage_mode() == RaceMode::Eliminator {
            race.event.laps = race.racers.len().saturating_sub(1) as u32;
        }
        race.collision_world = cached_collision(&mut self.collision_worlds, &race.track)?;
        race.elapsed = 0.;
        race.countdown = 3.;
        race.settled = false;
        race.combo = 1.;
        race.speed_challenge = crate::SpeedChallengeState::Pending;
        for (i, r) in race.racers.iter_mut().enumerate() {
            r.state = grid_state(i, &race.track, race.collision_world.as_deref());
            r.lap = 0;
            r.checkpoint = 1;
            r.progress = 0.;
            r.score = 0.;
            r.spook = 0.;
            r.finished = false;
            r.eliminated = false;
            r.finish_time = None;
            r.lives = race.event.lives.max(1);
            r.chain_score = 0.;
            r.input_clock = 0.;
            r.applied_input = PlayerInput::default();
            r.stuck_time = 0.;
            r.reverse_recovery = 0.;
            r.lap_start = 0.;
            r.best_lap_time = 0.;
            r.clean_lap = true;
            r.life_cooldown = 0.;
            r.drift_state = crate::NativeDriftState::default();
            r.human_drift = crate::HumanDriftState::default();
            r.unsupported_time = 0.;
            r.enduro_stopped = false;
        }
        self.result = None;
        self.screen = GameScreen::Race;
        Ok(())
    }
    fn settle(&mut self) {
        let Some(race) = &mut self.race else { return };
        if race.settled {
            return;
        }
        race.settled = true;
        // 820F82D0 stops gameplay NOS in the post-race states.
        for racer in &mut race.racers {
            racer.state.native_nitrous.request(false);
        }
        let ranking = ranked_indices(race);
        let mut position = ranking.iter().position(|i| *i == 0).unwrap_or(0) as u32 + 1;
        if race.spectating {
            let winner = ranking[0];
            let mut payout = 0;
            let mut profit = 0;
            for bet in &mut race.spectator_bets {
                if bet.racer == winner {
                    bet.payout = (f64::from(bet.stake) * f64::from(bet.odds)).floor() as i64;
                    payout += bet.payout;
                    profit += bet.payout - i64::from(bet.stake);
                }
            }
            self.career.cash += payout;
            if payout > 0 {
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::SpectatorPayout,
                    payout,
                    None,
                    Some(race.event.id.clone()),
                    "Spectator winnings",
                );
            }
            if let Some(league) = self
                .content
                .leagues
                .iter()
                .find(|l| l.league == self.career.league)
            {
                for goal in &league.goals {
                    if goal.kind.eq_ignore_ascii_case("WinSpectatorBet") {
                        let progress = self
                            .career
                            .goal_progress
                            .entry(goal.id.clone())
                            .or_default();
                        progress.value = progress.value.max(profit as f64);
                        progress.complete = progress.value
                            >= goal.args.first().and_then(|v| v.as_f64()).unwrap_or(1.);
                    }
                }
            }
            self.result = Some(RaceResult {
                event_id: race.event.id.clone(),
                won: payout > 0,
                position: 1,
                reward: payout,
                wager: profit,
                pink_slip: None,
                score: 0.,
                time: race.elapsed,
                round: 1,
                total_rounds: 1,
                tournament_points: vec![],
                is_final: true,
            });
            self.screen = GameScreen::Results;
            return;
        }
        let player = &race.racers[0];
        let team = team_scores(race);
        let mut won = match race.event.stage_mode() {
            RaceMode::Drift => player.score >= race.event.target && position == 1,
            RaceMode::SoloDrift | RaceMode::DriftEndurance => {
                player.score >= race.event.target && !player.eliminated
            }
            RaceMode::TwinDrift => team[0] >= race.event.target && team[0] >= team[1],
            RaceMode::DriftKing => position == 1 && !player.eliminated,
            RaceMode::DriftObliterator => player.finished && !player.eliminated && position == 1,
            RaceMode::TimeAttack => player.finished && race.elapsed <= race.event.target,
            RaceMode::LapTime => {
                player.best_lap_time > 0. && player.best_lap_time <= race.event.target
            }
            RaceMode::PerfectLap => {
                player.finished
                    && player.clean_lap
                    && (race.event.target <= 0. || player.best_lap_time <= race.event.target)
            }
            RaceMode::SpeedChallenge => {
                player.finished && race.speed_challenge == crate::SpeedChallengeState::Armed
            }
            RaceMode::TeamRace => team.iter().skip(1).all(|score| team[0] > *score),
            RaceMode::BeatCar => {
                let rival = race
                    .racers
                    .iter()
                    .skip(1)
                    .position(|r| {
                        race.event
                            .target_car
                            .as_ref()
                            .map(|id| id == &r.car_id)
                            .unwrap_or(true)
                    })
                    .map(|i| i + 1)
                    .or_else(|| (race.racers.len() > 1).then_some(1));
                rival
                    .map(|i| {
                        ranking.iter().position(|v| *v == 0) < ranking.iter().position(|v| *v == i)
                    })
                    .unwrap_or(false)
                    && player.finished
            }
            RaceMode::LastManStanding | RaceMode::Eliminator => {
                (race.racers.iter().filter(|r| !r.eliminated).count() == 1
                    || player.finished && position == 1)
                    && !player.eliminated
            }
            RaceMode::Circuit | RaceMode::CircuitTournament => {
                position == 1 && !player.eliminated && player.finished
            }
        };
        if race.event.stage_mode() == RaceMode::TeamRace {
            position = 1 + team
                .iter()
                .skip(1)
                .filter(|score| **score > team[0])
                .count() as u32;
        }
        for (place, index) in ranking.iter().enumerate() {
            race.tournament_points[*index] += round_points(place);
        }
        if race.career {
            self.career
                .vehicle_history
                .entry(player.car_id.clone())
                .or_default()
                .mileage_m += f64::from(player.state.distance);
        }
        if race.round < race.total_rounds && (race.event.contest_type != "Tournament" || won) {
            self.result = Some(RaceResult {
                round: race.round,
                total_rounds: race.total_rounds,
                tournament_points: race.tournament_points.clone(),
                is_final: false,
                event_id: race.event.id.clone(),
                won,
                position,
                reward: 0,
                wager: 0,
                pink_slip: None,
                score: player.score,
                time: race.elapsed,
            });
            self.screen = GameScreen::RoundResults;
            return;
        }
        if race.total_rounds > 1 && race.event.contest_type != "Tournament" {
            position = 1 + race
                .tournament_points
                .iter()
                .skip(1)
                .filter(|points| **points > race.tournament_points[0])
                .count() as u32;
            won = position == 1;
        }
        if race.career && race.event.league == self.career.league {
            if let Some(league) = self
                .content
                .leagues
                .iter()
                .find(|l| l.league == self.career.league)
            {
                update_goals(&mut self.career, league, race, won, position, &ranking);
            }
        }
        let reward = if race.event.prizes.is_empty() {
            if won {
                i64::from(race.event.reward)
            } else {
                0
            }
        } else if position == 1 && !won {
            // A failed score/time challenge has no winning entrant, even when
            // its lone player has ordinal position one.
            0
        } else {
            i64::from(
                race.event
                    .prizes
                    .get((position - 1) as usize)
                    .copied()
                    .unwrap_or(0),
            )
        };
        let bet_won = ranking.iter().position(|i| *i == 0)
            < ranking.iter().position(|i| *i == race.bet_racer);
        let wager = if bet_won {
            i64::from(race.wager) * 2
        } else {
            0
        };
        let mut pink = None;
        if race.career {
            self.career.cash += reward + wager;
            let history = self
                .career
                .vehicle_history
                .entry(player.car_id.clone())
                .or_default();
            if won {
                history.wins += 1;
            } else {
                history.losses += 1;
            }
            if reward > 0 {
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::RaceReward,
                    reward,
                    Some(player.car_id.clone()),
                    Some(race.event.id.clone()),
                    "Event reward",
                );
            }
            if wager > 0 {
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::WagerSettlement,
                    wager,
                    Some(player.car_id.clone()),
                    Some(race.event.id.clone()),
                    "Winning wager payout",
                );
            }
            if won {
                self.career.wins += 1;
                self.career.reputation += 100;
                if race.event.is_sponsor {
                    let packages = self
                        .career
                        .sponsor_packages
                        .entry(race.event.sponsor_type.clone())
                        .or_default();
                    if !packages.contains(&race.event.league) {
                        packages.push(race.event.league);
                        packages.sort_unstable();
                    }
                }
                if !self.career.completed_events.contains(&race.event.id) {
                    self.career.completed_events.push(race.event.id.clone());
                }

                let current_done = if let Some(league) = self
                    .content
                    .leagues
                    .iter()
                    .find(|l| l.league == self.career.league)
                {
                    race.event.qualifier
                        && race.event.league == self.career.league
                        && league.goals.iter().filter(|g| g.qualifier).all(|g| {
                            self.career
                                .goal_progress
                                .get(&g.id)
                                .map(|p| p.complete)
                                .unwrap_or(false)
                        })
                } else {
                    self.content
                        .events
                        .iter()
                        .filter(|e| e.league == self.career.league && !e.is_sponsor)
                        .all(|e| self.career.completed_events.contains(&e.id))
                };
                if current_done {
                    let max = self
                        .content
                        .events
                        .iter()
                        .map(|e| e.league)
                        .max()
                        .unwrap_or(0);
                    self.career.league = (self.career.league + 1).min(max);
                    if self.career.league == 3 {
                        let performance = self
                            .career
                            .native_performance
                            .get_or_insert_with(Default::default);
                        if performance.prototype_unlocks.len() < 40 {
                            performance.prototype_tokens = 1;
                        }
                    }
                }
            } else {
                self.career.losses += 1;
            }
            if race.pink_slip && bet_won {
                if let Some(opponent) = race.racers.get(race.bet_racer) {
                    let custom = self
                        .career
                        .garage
                        .entry(opponent.car_id.clone())
                        .or_default();
                    self.career
                        .parts_inventory
                        .entry(opponent.car_id.clone())
                        .or_insert_with(|| crate::garage::owned_parts(custom));
                    pink = Some(opponent.car_id.clone());
                    let history = self
                        .career
                        .vehicle_history
                        .entry(opponent.car_id.clone())
                        .or_default();
                    history.pink_slip_wins += 1;
                    if history.acquired_by.is_empty() {
                        history.acquired_by = "Pink slip".into();
                    }
                    record_transaction(
                        &mut self.career,
                        crate::TransactionKind::PinkSlipWin,
                        0,
                        Some(opponent.car_id.clone()),
                        Some(race.event.id.clone()),
                        "Pink slip vehicle won",
                    );
                }
            }
            if race.pink_slip && !bet_won && self.career.garage.len() > 1 {
                self.career.garage.remove(&player.car_id);
                pink = Some(player.car_id.clone());
                self.career
                    .vehicle_history
                    .entry(player.car_id.clone())
                    .or_default()
                    .pink_slip_losses += 1;
                self.pending_customizations.remove(&player.car_id);
                self.accepted_native_paint.remove(&player.car_id);
                record_transaction(
                    &mut self.career,
                    crate::TransactionKind::PinkSlipLoss,
                    0,
                    Some(player.car_id.clone()),
                    Some(race.event.id.clone()),
                    "Pink slip vehicle forfeited",
                );
                self.selected_car = self.career.garage.keys().next().unwrap().clone();
            }
            for dna in &mut self.career.crew {
                dna.experience += race.elapsed;
            }
        }
        self.result = Some(RaceResult {
            round: race.round,
            total_rounds: race.total_rounds,
            tournament_points: race.tournament_points.clone(),
            is_final: true,
            event_id: race.event.id.clone(),
            won,
            position,
            reward: if race.career { reward } else { 0 },
            wager: if race.career {
                wager - i64::from(race.wager)
            } else {
                0
            },
            pink_slip: pink,
            score: player.score,
            time: player.finish_time.unwrap_or(race.elapsed),
        });
        self.screen = GameScreen::Results;
    }
    /// Terminal821C5E20 purchase intent has a family price even when bytes match.
    pub fn quote_native_paint(
        &self,
        paint: &crate::NativePaintRecord,
    ) -> Result<crate::CartItem, String> {
        let price = paint.price().ok_or("Unsupported native paint family")?;
        Ok(crate::CartItem {
            id: format!("{}:paint", self.selected_car),
            car_id: self.selected_car.clone(),
            label: "Body paint".into(),
            cost: if self.quick_mode { 0 } else { price },
            field: "paint".into(),
        })
    }
    /// Quotes the selected vehicle against purchased state without changing its draft.
    pub fn quote_customization(&self, customization: &Customization) -> Vec<crate::CartItem> {
        if self.quick_mode {
            return vec![];
        }
        let mut normalized = customization.clone();
        crate::paint::sync_customization(&mut normalized);
        self.career
            .garage
            .get(&self.selected_car)
            .map(|old| {
                crate::garage::cart_changes(
                    &self.selected_car,
                    old,
                    &normalized,
                    self.career
                        .parts_inventory
                        .get(&self.selected_car)
                        .map(Vec::as_slice)
                        .unwrap_or(&[]),
                )
            })
            .unwrap_or_default()
    }
    fn cart_items(&self) -> Vec<crate::CartItem> {
        self.pending_customizations
            .iter()
            .flat_map(|(id, new)| {
                self.career
                    .garage
                    .get(id)
                    .map(|old| {
                        let mut items = crate::garage::cart_changes(
                            id,
                            old,
                            new,
                            self.career
                                .parts_inventory
                                .get(id)
                                .map(Vec::as_slice)
                                .unwrap_or(&[]),
                        );
                        if self.accepted_native_paint.contains(id) {
                            items.retain(|item| item.field != "paint");
                            if let Some(paint) = &new.native_paint {
                                items.push(crate::CartItem {
                                    id: format!("{id}:paint"),
                                    car_id: id.clone(),
                                    label: "Body paint".into(),
                                    cost: paint.price().expect("accepted native family"),
                                    field: "paint".into(),
                                });
                            }
                        }
                        items
                    })
                    .unwrap_or_default()
            })
            .collect()
    }
    fn checkout(&mut self) -> Result<(), String> {
        let items = self.cart_items();
        if items.is_empty() {
            return Err("Cart is empty".into());
        }
        if self
            .pending_customizations
            .keys()
            .any(|id| !self.career.garage.contains_key(id))
        {
            return Err("Cart contains a vehicle no longer owned".into());
        }
        let total: i64 = items.iter().map(|item| i64::from(item.cost)).sum();
        if self.career.cash < total {
            return Err("Insufficient cash for checkout".into());
        }
        self.career.cash -= total;
        for (id, custom) in std::mem::take(&mut self.pending_customizations) {
            let cost: u64 = items
                .iter()
                .filter(|item| item.car_id == id)
                .map(|item| u64::from(item.cost))
                .sum();
            self.career
                .vehicle_history
                .entry(id.clone())
                .or_default()
                .total_spent += cost;
            let owned = self.career.parts_inventory.entry(id.clone()).or_default();
            for part in crate::garage::owned_parts(&custom) {
                if !owned.contains(&part) {
                    owned.push(part);
                }
            }
            self.career.garage.insert(id.clone(), custom);
            record_transaction(
                &mut self.career,
                crate::TransactionKind::Customization,
                -(cost as i64),
                Some(id),
                None,
                "Garage checkout",
            );
        }
        self.accepted_native_paint.clear();
        self.screen = GameScreen::Garage;
        Ok(())
    }
    /// Current-league playable contests matching the same context used at settlement.
    pub fn events_for_goal(&self, goal_id: &str) -> Vec<String> {
        let Some(league) = self
            .content
            .leagues
            .iter()
            .find(|league| league.league == self.career.league)
        else {
            return vec![];
        };
        let Some(goal) = league.goals.iter().find(|goal| goal.id == goal_id) else {
            return vec![];
        };
        let qualifier_open = self.league_progress().promotion_open;
        self.content
            .events
            .iter()
            .filter(|event| {
                event.league == self.career.league && (!event.qualifier || qualifier_open)
            })
            .filter(|event| {
                self.content
                    .tracks
                    .iter()
                    .find(|track| track.id == event.track_id)
                    .map(|track| goal_matches_event(goal, event, track))
                    .unwrap_or(false)
            })
            .map(|event| event.id.clone())
            .collect()
    }

    pub fn league_progress(&self) -> crate::LeagueProgress {
        let Some(league) = self
            .content
            .leagues
            .iter()
            .find(|l| l.league == self.career.league)
        else {
            return Default::default();
        };
        let goals: Vec<_> = league
            .goals
            .iter()
            .map(|goal| crate::GoalStatus {
                goal: goal.clone(),
                progress: self
                    .career
                    .goal_progress
                    .get(&goal.id)
                    .cloned()
                    .unwrap_or_default(),
            })
            .collect();
        let completed = goals
            .iter()
            .filter(|g| !g.goal.qualifier && g.progress.complete)
            .count() as u32;
        crate::LeagueProgress {
            league: league.league,
            optional_completed: completed,
            optional_required: league.optional_goals_required,
            promotion_open: completed >= league.optional_goals_required,
            goals,
        }
    }
    pub fn snapshot(&self) -> GameSnapshot {
        self.snapshot_content(true)
    }
    /// Lightweight frame state; static content vectors are empty.
    pub fn frame_snapshot(&self) -> GameSnapshot {
        self.snapshot_content(false)
    }
    fn snapshot_content(&self, include_content: bool) -> GameSnapshot {
        let race = self.race.as_ref().map(|r| RaceSnapshot {
            career: r.career,
            native_discipline: r.event.native_discipline,
            bet_offer: r.bet_offer.clone(),
            wager: r.wager,
            pink_slip: r.pink_slip,
            bet_racer: r.bet_racer,
            spectating: r.spectating,
            spectator_bets: r.spectator_bets.clone(),
            spectator_odds: spectator_odds(r),
            speed_challenge: r.speed_challenge,
            round: r.round,
            total_rounds: r.total_rounds,
            lives: r.racers[0].lives,
            target: r.event.target,
            team_scores: team_scores(r),
            tournament_points: r.tournament_points.clone(),
            event_id: r.event.id.clone(),
            track_id: r.track.id.clone(),
            mode: r.event.mode,
            elapsed: r.elapsed,
            countdown: r.countdown,
            position: 1 + ranked_indices(r)
                .iter()
                .position(|index| *index == 0)
                .unwrap_or(0) as u32,
            standings: ranked_indices(r),
            laps: r.event.laps,
            racers: r
                .racers
                .iter()
                .enumerate()
                .map(|(i, v)| RacerSnapshot {
                    applied_input: v.applied_input,
                    clutch_engaged: v.state.clutch_engaged,
                    wheel_omega: v.state.wheel_omega,
                    wheel_angles: v.state.wheel_angles,
                    wheel_steer_angles: v.state.wheel_steer_angles,
                    surface_contacts: v.state.contacts,
                    is_player: i == 0 && !r.spectating,
                    team: v.team,
                    role: if v.team == 0 {
                        if v.name == "You" {
                            "Leader"
                        } else {
                            "Wingman"
                        }
                    } else {
                        "Rival"
                    }
                    .into(),
                    lives: v.lives,
                    chain_score: v.chain_score,
                    best_lap_time: v.best_lap_time,
                    clean_lap: v.clean_lap,
                    car_id: v.car_id.clone(),
                    name: v.name.clone(),
                    native_tag: v.dna.native_tag.clone(),
                    finish_time: v.finish_time,
                    position: v.state.position,
                    rotation: v.state.orientation,
                    velocity: v.state.velocity,
                    speed_kph: v.state.speed() * 3.6,
                    rpm: v.state.engine_omega * 9.54929638,
                    gear: if v.state.reversing {
                        -1
                    } else {
                        v.state.gear as i32
                    },
                    steering: v.state.steering,
                    nitrous: v.state.nitrous,
                    nitrous_active: v.state.native_nitrous.active
                        && v.state.native_nitrous.tank > 0.,
                    nitrous_pressure_band: v.state.native_nitrous.pressure_band,
                    lap: v.lap,
                    checkpoint: v.checkpoint,
                    progress: v.progress,
                    drift_score: v.score,
                    spook: v.spook,
                    finished: v.finished,
                    eliminated: v.eliminated,
                    customization: v.customization.clone(),
                })
                .collect(),
            drift_combo: r.combo,
            message: if r.countdown > 0. {
                format!("{}", r.countdown.ceil())
            } else {
                String::new()
            },
        });
        GameSnapshot {
            league_progress: self.league_progress(),
            cart: self.cart_items(),
            drivers: if include_content {
                self.content.drivers.clone()
            } else {
                vec![]
            },
            difficulty: self.difficulty,
            profile: self.profile.clone(),
            selected_customization: if self.quick_mode {
                self.quick_customizations
                    .get(&self.selected_car)
                    .or_else(|| self.career.garage.get(&self.selected_car))
            } else {
                self.pending_customizations
                    .get(&self.selected_car)
                    .or_else(|| self.career.garage.get(&self.selected_car))
            }
            .cloned()
            .unwrap_or_default(),
            screen: self.screen,
            selected_car: self.selected_car.clone(),
            cars: if include_content {
                self.content.cars.clone()
            } else {
                vec![]
            },
            tracks: if include_content {
                self.content
                    .tracks
                    .iter()
                    .map(|track| TrackDefinition {
                        native_route: track.native_route.clone(),
                        start_grid: track.start_grid.clone(),
                        collision: None,
                        surface_half_widths: track.surface_half_widths.clone(),
                        wall_half_widths: track.wall_half_widths.clone(),
                        location: track.location.clone(),
                        surface_points: track.surface_points.clone(),
                        id: track.id.clone(),
                        name: track.name.clone(),
                        points: track.points.clone(),
                        road_width: track.road_width,
                    })
                    .collect()
            } else {
                vec![]
            },
            events: if include_content {
                self.content.events.clone()
            } else {
                vec![]
            },
            career: self.career.clone(),
            race,
            result: self.result.clone(),
        }
    }
    /// Deterministic general driving inputs, shared with the reconstructed opponent controller.
    pub fn scenario_player_ai_input(&self) -> PlayerInput {
        self.race
            .as_ref()
            .map(|r| {
                avoid_eliminated_cars(
                    r,
                    0,
                    ai_input(&r.racers[0], &r.track, r.event.stage_mode(), true),
                )
            })
            .unwrap_or_default()
    }
    /// Input-only endurance experiment, validated for AWD on the native Rome arena.
    /// Other layouts remain experimental; no predicted state is committed.
    pub fn scenario_endurance_predictive_input(&self) -> PlayerInput {
        self.race
            .as_ref()
            .map(|r| {
                let input = ai_input(&r.racers[0], &r.track, r.event.stage_mode(), true);
                if r.event.stage_mode() == RaceMode::DriftEndurance {
                    self.predict_endurance_input(r, input)
                } else {
                    input
                }
            })
            .unwrap_or_default()
    }
    /// Experimental input-only drift policy for bounded career-driving probes.
    /// It does not modify the authoritative vehicle or scoring state.
    pub fn scenario_drift_predictive_input(&self) -> PlayerInput {
        self.race
            .as_ref()
            .map(|race| {
                let input = ai_input(&race.racers[0], &race.track, race.event.stage_mode(), true);
                if matches!(
                    race.event.stage_mode(),
                    RaceMode::Drift
                        | RaceMode::SoloDrift
                        | RaceMode::DriftEndurance
                        | RaceMode::DriftKing
                        | RaceMode::DriftObliterator
                ) {
                    self.predict_endurance_input(race, input)
                } else {
                    avoid_eliminated_cars(race, 0, input)
                }
            })
            .unwrap_or_default()
    }
    // Reconstruction policy: compare legal controls with the same motion/contact model.
    // Predicted states are discarded; only the chosen input reaches advance().
    fn predict_endurance_input(&self, race: &Race, baseline: PlayerInput) -> PlayerInput {
        let mut baseline = baseline;
        baseline.handbrake = if baseline.handbrake > 0. { 1. } else { 0. };
        let player = &race.racers[0];
        if race.event.stage_mode() == RaceMode::DriftObliterator
            && player.drift_state.banked as f32 >= race.event.target
        {
            return avoid_eliminated_cars(
                race,
                0,
                ai_input(player, &race.track, RaceMode::Circuit, true),
            );
        }
        let score_target = if race.event.stage_mode() == RaceMode::DriftKing {
            f32::INFINITY
        } else {
            race.event.target
        };
        if player.chain_score >= score_target && score_target > 0. {
            return PlayerInput {
                brake: 1.,
                ..Default::default()
            };
        }
        let launch_speed = if player.drive_layout == crate::DriveLayout::Rwd {
            11.
        } else {
            6.
        };
        if player.state.speed() < launch_speed || player.state.reversing {
            // At launch tiny lateral velocities make slip angle meaningless; a
            // binary handbrake would disengage the source clutch and prevent launch.
            baseline.handbrake = 0.;
            return baseline;
        }
        let Some(world) = race.collision_world.as_deref() else {
            return baseline;
        };
        let Some(car) = self.content.cars.iter().find(|car| car.id == player.car_id) else {
            return baseline;
        };
        let mut selected = baseline;
        let mut best = f32::NEG_INFINITY;
        let throttles: &[f32] = if player.drive_layout == crate::DriveLayout::Rwd {
            &[0., 1.]
        } else {
            &[1.]
        };
        let brakes: &[f32] = if player.drive_layout == crate::DriveLayout::Rwd {
            &[0., 0.4, 0.8]
        } else {
            &[0., 0.2, 0.4]
        };
        for steering in [-1., -0.65, -0.3, 0., 0.3, 0.65, 1.] {
            for handbrake in [0., 1.] {
                for &throttle in throttles {
                    for &brake in brakes {
                        let input = PlayerInput {
                            throttle,
                            brake,
                            steering,
                            handbrake,
                            ..Default::default()
                        };
                        let mut predicted = player.clone();
                        let mut globals = self.drift_assist_globals.clone();
                        let mut value = 0.;
                        for _ in 0..90 {
                            let h = 1. / 60.;
                            let handling = motion_handling(
                                &car.handling,
                                &predicted,
                                race.event.stage_mode(),
                                true,
                            );
                            update_surface_contacts(
                                &mut predicted.state,
                                &handling,
                                &race.track,
                                predicted.checkpoint,
                                Some(world),
                            );
                            let old = predicted.state.position;
                            predicted.state.step(&handling, &self.globals, input, h);
                            predicted.apply_human_motion(&mut globals, input, h, true);
                            let contacts = predicted
                                .state
                                .contacts
                                .iter()
                                .filter(|contact| contact.active)
                                .count();
                            predicted.unsupported_time = if contacts < 2 {
                                predicted.unsupported_time + h
                            } else {
                                0.
                            };
                            if world.resolve_chassis(&mut predicted.state, &handling, old)
                                || predicted.unsupported_time > 0.05
                            {
                                value -= 10000.;
                                break;
                            }
                            let angle = predicted.state.slip_angle.abs();
                            let speed = predicted.state.speed();
                            value += if speed > 10. && angle > 0.18 && angle < 1.6 {
                                6. + angle.min(0.9) * 2. - (speed - 14.).abs() * 0.3
                            } else {
                                -2.
                            };
                            if angle > 1.8 {
                                value -= 20.;
                            }
                            if player.drive_layout == crate::DriveLayout::Rwd {
                                // Break non-scoring candidate ties toward building speed;
                                // otherwise the first coasting candidate traps launch below10m/s.
                                value += speed * 0.02;
                            }
                        }
                        value -= (steering - baseline.steering).abs() * 0.5;
                        if value > best {
                            best = value;
                            selected = input;
                        }
                    }
                }
            }
        }
        selected
    }
    /// Deterministic scenario hook: regular simulation still performs scoring and settlement.
    pub fn scenario_place_player(
        &mut self,
        position: [f32; 3],
        velocity: [f32; 3],
        lap: u32,
        checkpoint: usize,
    ) -> Result<(), String> {
        self.scenario_place_racer(0, position, velocity, lap, checkpoint)
    }
    pub fn scenario_place_racer(
        &mut self,
        index: usize,
        position: [f32; 3],
        velocity: [f32; 3],
        lap: u32,
        checkpoint: usize,
    ) -> Result<(), String> {
        let race = self.race.as_mut().ok_or("No active race")?;
        if checkpoint >= race.track.points.len() {
            return Err("Checkpoint out of range".into());
        }
        let p = race
            .racers
            .get_mut(index)
            .ok_or("Racer index out of range")?;
        p.state.position = position;
        p.state.velocity = velocity;
        p.lap = lap;
        p.checkpoint = checkpoint;
        Ok(())
    }
}

fn cached_collision(
    cache: &mut BTreeMap<String, Arc<crate::NativeCollisionWorld>>,
    track: &TrackDefinition,
) -> Result<Option<Arc<crate::NativeCollisionWorld>>, String> {
    let Some(definition) = &track.collision else {
        return Ok(None);
    };
    if let Some(world) = cache.get(&track.id) {
        return Ok(Some(world.clone()));
    }
    let world = Arc::new(crate::NativeCollisionWorld::new(definition)?);
    cache.insert(track.id.clone(), world.clone());
    Ok(Some(world))
}

fn distance_xz(a: [f32; 3], b: [f32; 3]) -> f32 {
    ((a[0] - b[0]).powi(2) + (a[2] - b[2]).powi(2)).sqrt()
}
fn wrap_angle(mut a: f32) -> f32 {
    while a > std::f32::consts::PI {
        a -= std::f32::consts::TAU;
    }
    while a < -std::f32::consts::PI {
        a += std::f32::consts::TAU;
    }
    a
}
fn motion_handling(base: &Handling, r: &Racer, mode: RaceMode, human: bool) -> Handling {
    let mut handling = customized_handling(base, &r.customization);
    if mode.is_drift() {
        if human {
            handling.gears.truncate(4);
        }
        let mu = crate::native_drift_tyre_mu(
            [
                handling.tyre_mu,
                handling.rear_tyre_mu.unwrap_or(handling.tyre_mu),
            ],
            handling.layout,
            r.state.speed(),
            true,
            !r.state.reversing,
        );
        handling.tyre_mu = mu[0];
        handling.rear_tyre_mu = Some(mu[1]);
    }
    handling
}

fn customized_handling(base: &Handling, customization: &Customization) -> Handling {
    let mut handling = base.clone();
    handling.peak_torque *= 1. + customization.engine as f32 * 0.12;
    handling.peak_bhp *= 1. + customization.engine as f32 * 0.12;
    // Accepted-donor power tuning remains an adaptation until the native package catalog is bound.
    handling.nitrous_power_factor *= handling.peak_bhp / base.peak_bhp;
    if let Some(control) = customization.nitrous_capacity_control {
        handling.nitrous_capacity_control = control;
    }
    let tyre_scale = 1. + customization.tyres as f32 * 0.06;
    handling.tyre_mu *= tyre_scale;
    handling.rear_tyre_mu = handling.rear_tyre_mu.map(|mu| mu * tyre_scale);
    handling.max_steer *= 1. + customization.tuning[0] * 0.1;
    handling.shift_duration *= 1. - customization.transmission as f32 * 0.15;
    let spring_scale = 1. + customization.suspension as f32 * 0.12;
    handling.spring_rate *= spring_scale;
    handling.rear_spring_rate = handling.rear_spring_rate.map(|rate| rate * spring_scale);
    handling.damping_ratio *= 1. + customization.suspension as f32 * 0.05;
    handling.final_drive *= 1. + customization.tuning[1] * 0.15;
    let grip_scale = 1. + customization.tuning[2] * 0.05;
    handling.tyre_mu *= grip_scale;
    handling.rear_tyre_mu = handling.rear_tyre_mu.map(|mu| mu * grip_scale);
    handling.front_weight =
        (handling.front_weight + customization.tuning[3] * 0.03).clamp(0.3, 0.7);

    handling
}

/// Recovered 82133FE0: signed throttle/brake demand from local forward speed.
/// `reverse_state` is the caller's native actor+244 value, not a physics force flag.
pub fn native_ai_speed_demand(forward_speed: f32, target: f32, reverse_state: u32) -> f32 {
    let error = forward_speed - target;
    if error < -1. {
        if forward_speed < -1. && reverse_state == 0 {
            -1.
        } else {
            (error * -0.06666667014360428).clamp(0., 1.)
        }
    } else if error > 1. {
        -(error * 0.10000000149011612).clamp(0., 1.)
    } else {
        0.
    }
}

// Reconstructed input policy: eliminated contestants remain physical obstacles.
// Steer around their actual bodies instead of repeatedly pursuing through them.
fn avoid_eliminated_cars(race: &Race, index: usize, mut input: PlayerInput) -> PlayerInput {
    if race.event.stage_mode().is_drift() {
        return input;
    }
    let racer = &race.racers[index];
    if racer.state.reversing || racer.reverse_recovery > 0. {
        return input;
    }
    let yaw = racer.state.yaw();
    let forward = [yaw.sin(), yaw.cos()];
    let right = [yaw.cos(), -yaw.sin()];
    for (other_index, other) in race.racers.iter().enumerate() {
        if other_index == index || !other.eliminated {
            continue;
        }
        let dx = other.state.position[0] - racer.state.position[0];
        let dz = other.state.position[2] - racer.state.position[2];
        let ahead = dx * forward[0] + dz * forward[1];
        let side = dx * right[0] + dz * right[1];
        if ahead > 0. && ahead < (racer.state.speed() * 1.5).max(12.) && side.abs() < 3. {
            let direction = if side >= 0. { -1. } else { 1. };
            let angle = (direction * 5. - side).atan2(ahead.max(4.));
            input.steering = ((2. * racer.wheelbase * angle.sin() / ahead.max(4.)).atan()
                / racer.max_steer)
                .clamp(-1., 1.);
            if ahead < 10. && racer.state.speed() > 8. {
                input.throttle = 0.;
                input.brake = 0.4;
            }
            break;
        }
    }
    input
}

fn ai_input(
    r: &Racer,
    track: &TrackDefinition,
    mode: RaceMode,
    human_assisted: bool,
) -> PlayerInput {
    let max_steer = r.max_steer * (1. + r.customization.tuning[0] * 0.1);
    let checkpoint = track.points[r.checkpoint];
    let speed = r.state.speed();
    let previous = track.points[(r.checkpoint + track.points.len() - 1) % track.points.len()];
    let projection = distance_to_segment(r.state.position, previous, checkpoint).1;
    // A wide corner can pass a waypoint's plane without entering its gate.
    // Return to that real gate instead of perpetually pursuing later points.
    let missed_gate = distance_xz(projection, checkpoint) < 0.1
        && distance_xz(r.state.position, checkpoint) >= track.road_width.max(10.);
    let lookahead = if missed_gate {
        0.
    } else if mode.is_drift() {
        4. + speed * 0.35
    } else {
        // A long pursuit horizon otherwise lets wide cars remain at the road edge.
        // This is reconstructed input control, not a change to tire or collision forces.
        ((8. + speed * 0.8) / (1. + distance_xz(r.state.position, projection) * 0.5)).max(8.)
    };
    let remaining = distance_xz(projection, checkpoint);
    let mut target = checkpoint;
    let mut ahead = lookahead - remaining;
    if lookahead < remaining {
        let t = lookahead / remaining;
        for j in 0..3 {
            target[j] = projection[j] + (checkpoint[j] - projection[j]) * t;
        }
    }
    let mut index = r.checkpoint;
    while ahead > 0. {
        let next = track.points[(index + 1) % track.points.len()];
        let length = distance_xz(target, next);
        if ahead < length {
            let t = ahead / length;
            for j in 0..3 {
                target[j] += (next[j] - target[j]) * t;
            }
            break;
        }
        ahead -= length;
        target = next;
        index = (index + 1) % track.points.len();
        if index == r.checkpoint {
            break;
        }
    }
    let section = if lookahead < remaining {
        (r.checkpoint + track.points.len() - 1) % track.points.len()
    } else {
        index
    };
    let (widths, _, left) = cross_section(track, section, target);
    let mut offset = if widths[0] < 2. {
        widths[0] - 2.
    } else if widths[1] < 2. {
        2. - widths[1]
    } else {
        0.
    };
    if !mode.is_drift() && r.input_clock < 5. && widths[0] >= 2. && widths[1] >= 2. {
        // Keep each grid lane while launching, then blend onto the racing line.
        // Immediate pursuit of the same centerline point crowds adjacent rows.
        let lateral = (r.state.position[0] - projection[0]) * left[0]
            + (r.state.position[2] - projection[2]) * left[1];
        offset +=
            lateral.clamp(-(widths[1] - 2.), widths[0] - 2.) * (5. - r.input_clock).clamp(0., 1.);
    }
    target[0] += left[0] * offset;
    target[2] += left[1] * offset;
    let desired = (target[0] - r.state.position[0]).atan2(target[2] - r.state.position[2]);
    let error = wrap_angle(desired - r.state.yaw());
    if r.reverse_recovery > 0. {
        return PlayerInput {
            throttle: 0.7,
            steering: -error.clamp(-1., 1.),
            reverse: true,
            ..Default::default()
        };
    }
    if r.state.reversing && speed > 0.5 {
        return PlayerInput {
            brake: 1.,
            ..Default::default()
        };
    }
    let next = track.points[(r.checkpoint + 1) % track.points.len()];
    let previous = track.points[(r.checkpoint + track.points.len() - 1) % track.points.len()];
    let turn = wrap_angle(
        (next[0] - checkpoint[0]).atan2(next[2] - checkpoint[2])
            - (checkpoint[0] - previous[0]).atan2(checkpoint[2] - previous[2]),
    )
    .abs();
    let corner = turn > 0.3 && distance_xz(r.state.position, checkpoint) < speed * 3. + 15.;
    let desired_speed = if mode.is_drift() {
        drift_target_speed(r, track)
    } else if error.abs() > 1.2 {
        4.
    } else if corner {
        8.
    } else {
        22. + r.dna.aggression * 6.
    };
    let desired_speed = if mode.is_drift() || r.drive_layout != crate::DriveLayout::Rwd {
        desired_speed
    } else {
        // Reconstructed RWD input policy: brake before a curved route, not only
        // after the heading error is large. This does not alter vehicle forces.
        // Grid rows can be behind the first segment. Their longitudinal
        // distance to its endpoint is not a lateral departure from the road.
        let lateral_error = ((r.state.position[0] - projection[0]) * left[0]
            + (r.state.position[2] - projection[2]) * left[1])
            .abs();
        let mut limit = desired_speed / (1. + lateral_error * 0.15);
        let mut distance = distance_xz(r.state.position, checkpoint);
        for ahead in 0..12.min(track.points.len()) {
            let j = (r.checkpoint + ahead) % track.points.len();
            let a = track.points[(j + track.points.len() - 1) % track.points.len()];
            let b = track.points[j];
            let c = track.points[(j + 1) % track.points.len()];
            let angle =
                wrap_angle((c[0] - b[0]).atan2(c[2] - b[2]) - (b[0] - a[0]).atan2(b[2] - a[2]))
                    .abs();
            let curvature = angle / ((distance_xz(a, b) + distance_xz(b, c)) * 0.5).max(0.1);
            let corner = (6. / curvature.max(0.0001)).sqrt().max(5.);
            limit = limit.min((corner * corner + 8. * distance).sqrt());
            distance += distance_xz(b, c);
        }
        limit
    };
    let demand = native_ai_speed_demand(
        r.state.body_velocity()[2],
        desired_speed,
        u32::from(r.state.reversing),
    );
    if mode.is_drift() {
        let direction = r.drift_direction;
        let kick = drift_kick_requested(r);
        let drifting = kick || r.state.slip_angle.abs() > 0.12;
        let velocity_heading = r.state.velocity[0].atan2(r.state.velocity[2]);
        let course_error = wrap_angle(desired - velocity_heading);
        let predicted_slip = if r.drive_layout == crate::DriveLayout::Rwd {
            r.state.slip_angle
        } else {
            wrap_angle(r.state.slip_angle - r.state.yaw_rate * 0.3)
        };
        return PlayerInput {
            throttle: demand.max(0.),
            brake: (-demand).max(0.),
            steering: if human_assisted && r.human_drift.blend > 0.15 {
                let desired_yaw = (course_error * 2.
                    + (r.state.slip_angle + direction * 0.45) * 1.4)
                    .clamp(-1.2, 1.2);
                let feedback = if demand >= 0.99 {
                    r.human_drift.blend * r.state.slip_angle.signum() * 15.
                } else {
                    0.
                };
                (((desired_yaw / 0.02 - r.human_drift.yaw_control) * 4. + feedback)
                    / (170.
                        * if r.drive_layout == crate::DriveLayout::Rwd {
                            1.
                        } else {
                            1.8
                        }))
                .clamp(-1., 1.)
            } else if predicted_slip.abs() > 0.5 {
                predicted_slip.signum()
            } else if drifting {
                ((3.5 * course_error + 1.4 * (r.state.slip_angle + direction * 0.45)
                    - r.state.yaw_rate * 0.9)
                    / max_steer)
                    .clamp(-1., 1.)
            } else {
                (((2. * r.wheelbase) * error.sin() / distance_xz(r.state.position, target).max(4.))
                    .atan()
                    / max_steer)
                    .clamp(-1., 1.)
            },
            handbrake: if drifting && r.drive_layout != crate::DriveLayout::Rwd {
                0.8
            } else if kick && r.state.slip_angle.abs() < 0.25 {
                1.
            } else {
                0.
            },
            ..Default::default()
        };
    }
    PlayerInput {
        steering: if error.abs() > 1.2 {
            error.clamp(-1., 1.)
        } else {
            (((2. * r.wheelbase) * error.sin()
                / distance_xz(r.state.position, target).clamp(4., (8. + speed * 0.8).max(4.)))
            .atan()
                / max_steer)
                .clamp(-1., 1.)
        },
        throttle: demand.clamp(
            0.,
            if corner {
                r.dna.corner_throttle
            } else {
                r.dna.race_throttle
            }
            .clamp(0., 1.),
        ),
        brake: (-demand).max(0.),
        handbrake: if mode.is_drift() && speed > 12. && error.abs() > 0.07 {
            0.65
        } else {
            0.
        },
        ..Default::default()
    }
}
fn distance_to_segment(p: [f32; 3], a: [f32; 3], b: [f32; 3]) -> (f32, [f32; 3]) {
    let dx = b[0] - a[0];
    let dz = b[2] - a[2];
    let t = (((p[0] - a[0]) * dx + (p[2] - a[2]) * dz) / (dx * dx + dz * dz)).clamp(0., 1.);
    let q = [a[0] + t * dx, a[1] + t * (b[1] - a[1]), a[2] + t * dz];
    (distance_xz(p, q), q)
}
fn road_contact(
    state: &mut VehicleState,
    track: &TrackDefinition,
    h: f32,
    checkpoint: usize,
    clearance: f32,
) -> bool {
    let mut nearest = (f32::MAX, [0.; 3]);
    let mut segment = checkpoint;
    for i in contact_segments(track, checkpoint) {
        let q = distance_to_segment(
            state.position,
            track.surface()[i],
            track.surface()[(i + 1) % track.points.len()],
        );
        if q.0 < nearest.0 {
            nearest = q;
            segment = i;
        }
    }
    let (widths, walls, left) = cross_section(track, segment, state.position);
    let signed =
        (state.position[0] - nearest.1[0]) * left[0] + (state.position[2] - nearest.1[2]) * left[1];
    let side = if signed >= 0. { 0 } else { 1 };
    if signed.abs() > widths[side] {
        let drag = (1. - h * 1.5).max(0.);
        state.velocity[0] *= drag;
        state.velocity[2] *= drag;
    }
    // Measured wall candidates are distinct from floor coverage. Missing walls retain the documented safety ribbon.
    let mut limits = [
        walls[0].unwrap_or(widths[0] + 3.) - clearance,
        walls[1].unwrap_or(widths[1] + 3.) - clearance,
    ];
    if limits[0] + limits[1] < 0.5 {
        limits = [track.road_width * 0.5 + 3. - clearance; 2];
    }
    let corrected = signed.clamp(-limits[1], limits[0]);
    let collided = (corrected - signed).abs() > 0.001;
    if collided {
        state.position[0] += left[0] * (corrected - signed);
        state.position[2] += left[1] * (corrected - signed);
        let outward = if signed > corrected { 1. } else { -1. };
        let speed = (state.velocity[0] * left[0] + state.velocity[2] * left[1]) * outward;
        if speed > 0. {
            state.velocity[0] -= left[0] * outward * speed * 1.4;
            state.velocity[2] -= left[1] * outward * speed * 1.4;
        }
    }
    collided
}

fn cross_section(
    track: &TrackDefinition,
    index: usize,
    point: [f32; 3],
) -> ([f32; 2], [Option<f32>; 2], [f32; 2]) {
    let next = (index + 1) % track.points.len();
    let a = track.points[index];
    let b = track.points[next];
    let d = [b[0] - a[0], b[2] - a[2]];
    let len = (d[0] * d[0] + d[1] * d[1]).sqrt().max(0.001);
    let t = (((point[0] - a[0]) * d[0] + (point[2] - a[2]) * d[1]) / (len * len)).clamp(0., 1.);
    let left = [-d[1] / len, d[0] / len];
    let fallback = ([track.road_width * 0.5; 2], [None; 2], left);
    if track.surface_half_widths.len() != track.points.len() {
        return fallback;
    }
    let widths = std::array::from_fn(|i| {
        track.surface_half_widths[index][i] * (1. - t) + track.surface_half_widths[next][i] * t
    });
    // Tiny disconnected spans cannot describe a drivable car surface; retain explicit fallback for these candidates.
    if widths.iter().any(|w| !w.is_finite() || *w < 0.) || widths[0] + widths[1] < 2.5 {
        return fallback;
    }
    let walls = if track.wall_half_widths.len() == track.points.len() {
        std::array::from_fn(|i| {
            match (
                track.wall_half_widths[index][i],
                track.wall_half_widths[next][i],
            ) {
                (Some(a), Some(b)) => Some(a * (1. - t) + b * t),
                _ => None,
            }
        })
    } else {
        [None; 2]
    };
    (widths, walls, left)
}

fn update_surface_contacts(
    state: &mut VehicleState,
    handling: &Handling,
    track: &TrackDefinition,
    checkpoint: usize,
    collision: Option<&crate::NativeCollisionWorld>,
) {
    let [qx, qy, qz, qw] = state.orientation;
    for i in 0..4 {
        let z = if i < 2 {
            handling.wheelbase * (1. - handling.front_weight)
        } else {
            -handling.wheelbase * handling.front_weight
        };
        let x = if i % 2 == 0 {
            -handling.track_width / 2.
        } else {
            handling.track_width / 2.
        };
        let p = [
            state.position[0] + (1. - 2. * (qy * qy + qz * qz)) * x + 2. * (qx * qz + qw * qy) * z,
            state.position[1] + 2. * (qx * qy + qw * qz) * x + 2. * (qy * qz - qw * qx) * z,
            state.position[2] + 2. * (qx * qz - qw * qy) * x + (1. - 2. * (qx * qx + qy * qy)) * z,
        ];
        if let Some(world) = collision {
            state.contacts[i] = match world.ground(
                p,
                handling.body_height,
                if i < 2 {
                    handling.max_spring_compression
                } else {
                    handling
                        .rear_max_spring_compression
                        .unwrap_or(handling.max_spring_compression)
                },
            ) {
                Some(hit) => crate::SurfaceContact {
                    anchor_xz: [p[0], p[2]],
                    height: hit.height,
                    normal: hit.normal,
                    grip: 1.,
                    active: true,
                },
                None => crate::SurfaceContact {
                    anchor_xz: [p[0], p[2]],
                    height: p[1] - 1.,
                    normal: [0., 1., 0.],
                    grip: 1.,
                    active: false,
                },
            };
            continue;
        }
        let mut nearest = (f32::MAX, [0.; 3]);
        let mut normal = [0., 1., 0.];
        let mut segment = checkpoint;
        for j in contact_segments(track, checkpoint) {
            let a = track.surface()[j];
            let b = track.surface()[(j + 1) % track.points.len()];
            let q = distance_to_segment(p, a, b);
            if q.0 < nearest.0 {
                nearest = q;
                segment = j;
                let dx = b[0] - a[0];
                let dz = b[2] - a[2];
                let dy = b[1] - a[1];
                let length = (dx * dx + dz * dz).sqrt();
                let norm = (length * length + dy * dy).sqrt();
                normal = [
                    -dy * dx / length / norm,
                    length / norm,
                    -dy * dz / length / norm,
                ];
            }
        }
        let (widths, _, left) = cross_section(track, segment, p);
        let signed = (p[0] - nearest.1[0]) * left[0] + (p[2] - nearest.1[2]) * left[1];
        state.contacts[i] = crate::SurfaceContact {
            anchor_xz: [nearest.1[0], nearest.1[2]],
            height: nearest.1[1],
            normal,
            grip: if signed.abs() > widths[if signed >= 0. { 0 } else { 1 }] {
                0.65
            } else {
                1.
            },
            active: true,
        };
    }
}

/// Route-local broad phase keeps overlapping/stacked ribbon branches distinct.
fn contact_segments(track: &TrackDefinition, checkpoint: usize) -> impl Iterator<Item = usize> {
    let n = track.points.len();
    let count = if track.surface_half_widths.len() == n {
        n
    } else {
        n.min(12)
    };
    let start = if count == n {
        0
    } else {
        (checkpoint + n - count / 2) % n
    };
    (0..count).map(move |offset| (start + offset) % n)
}

fn rival_customization(index: usize) -> Customization {
    let colors = [
        [0.12, 0.22, 0.52, 1.],
        [0.72, 0.72, 0.68, 1.],
        [0.07, 0.09, 0.11, 1.],
        [0.73, 0.45, 0.08, 1.],
        [0.16, 0.38, 0.22, 1.],
        [0.46, 0.12, 0.09, 1.],
        [0.35, 0.22, 0.45, 1.],
        [0.1, 0.38, 0.4, 1.],
    ];
    Customization {
        paint: colors[(index - 1) % colors.len()],
        plate_text: format!("RIVAL{index:02}"),
        ..Default::default()
    }
}

fn grid_state(
    i: usize,
    track: &TrackDefinition,
    collision: Option<&crate::NativeCollisionWorld>,
) -> VehicleState {
    if !track.start_grid.is_empty() {
        // Native82141CD0 clamps slot to the final16-byte grid record.
        // 82082EC0's yaw is reflected with worldX; preserve genuine XYZ.
        let start = &track.start_grid[i.min(track.start_grid.len() - 1)];
        let mut state = VehicleState::default();
        state.position = start.position;
        state.set_yaw(-start.native_yaw_radians);
        if let Some(hit) = collision.and_then(|world| world.ground(start.position, 1., 1.)) {
            // 820F2D00: vertical native±100cm seed ray, exact hitpoint,
            // ground-normal up axis and rebuilt right/forward; no added offset.
            use parry3d::math::{Mat3, Rotation, Vector};
            let up = Vector::from_array(hit.normal);
            let yaw = -start.native_yaw_radians;
            let forward = Vector::new(yaw.sin(), 0., yaw.cos());
            let right = up.cross(forward).normalize();
            let forward = right.cross(up).normalize();
            state.position[1] = hit.height;
            state.orientation = Rotation::from_mat3(&Mat3::from_cols(right, up, forward))
                .normalize()
                .to_array();
        }
        return state;
    }
    let a = track.points[0];
    let b = track.points[1];
    let yaw = (b[0] - a[0]).atan2(b[2] - a[2]);
    let side = ((i % 2) as f32 - 0.5) * 4.;
    let behind = (i / 2) as f32 * 7.;
    let mut state = VehicleState::default();
    state.position = [
        a[0] + side * yaw.cos() - behind * yaw.sin(),
        track.surface()[0][1],
        a[2] - side * yaw.sin() - behind * yaw.cos(),
    ];
    state.set_yaw(yaw);
    if let Some(hit) = collision.and_then(|world| world.ground(state.position, 2., 4.)) {
        state.position[1] = hit.height;
    }
    state
}
fn round_points(place: usize) -> u32 {
    [10, 8, 6, 4, 2, 1].get(place).copied().unwrap_or(0)
}
fn ranked_indices(race: &Race) -> Vec<usize> {
    let mut indices: Vec<_> = (0..race.racers.len()).collect();
    indices.sort_by(|a, b| {
        let a = &race.racers[*a];
        let b = &race.racers[*b];
        if a.eliminated != b.eliminated {
            a.eliminated.cmp(&b.eliminated)
        } else if race.event.stage_mode().ranks_by_score() {
            b.score.total_cmp(&a.score)
        } else {
            match (a.finish_time, b.finish_time) {
                (Some(a), Some(b)) => a.total_cmp(&b),
                (Some(_), None) => std::cmp::Ordering::Less,
                (None, Some(_)) => std::cmp::Ordering::Greater,
                _ => b.progress.total_cmp(&a.progress),
            }
        }
    });
    indices
}
fn team_scores(race: &Race) -> Vec<f32> {
    let count = race
        .racers
        .iter()
        .map(|r| r.team as usize + 1)
        .max()
        .unwrap_or(2)
        .max(2);
    let mut scores = vec![0.; count];
    for (rank, index) in ranked_indices(race).iter().enumerate() {
        let r = &race.racers[*index];
        scores[r.team as usize] += if race.event.stage_mode().is_drift() {
            r.score
        } else {
            round_points(rank) as f32
        };
    }
    scores
}

fn register_collision(r: &mut Racer, mode: RaceMode) {
    r.clean_lap = false;
    if mode == RaceMode::PerfectLap {
        r.eliminated = true;
    }
    if mode.is_drift() && r.life_cooldown == 0. {
        let endurance = mode == RaceMode::DriftEndurance;
        r.drift_state.collide(0., endurance);
        r.score = r.drift_state.total() as f32;
        r.chain_score = r.drift_state.points as f32;
        r.life_cooldown = 1.;
        if endurance {
            r.enduro_stopped = true;
        }
    }
}

fn runtime_stage_indices(event: &EventDefinition) -> Vec<usize> {
    if event.contest_type != "Tournament" {
        return (0..event.stages.len().max(event.rounds as usize).max(1)).collect();
    }
    let count = event
        .contestants
        .len()
        .max(event.opponents as usize + 1)
        .max(2)
        .next_power_of_two();
    let seed = event
        .contestants
        .iter()
        .position(|c| c.tag.starts_with("Player"))
        .unwrap_or(0);
    let mut offset = 0;
    let mut plan = vec![];
    for round in 1..=count.trailing_zeros() {
        let index = offset + (seed >> round);
        plan.push(index.min(event.stages.len().saturating_sub(1)));
        offset += count >> round;
    }
    plan
}
fn tournament_rival<'a>(
    event: &'a EventDefinition,
    round: u32,
    drivers: &[DriverDna],
) -> Option<&'a EventContestant> {
    let seed = event
        .contestants
        .iter()
        .position(|c| c.tag.starts_with("Player"))
        .unwrap_or(0);
    let width = 1usize.checked_shl(round).unwrap_or(2);
    let start = seed / width * width;
    let half = width / 2;
    let opponent_start = if seed < start + half {
        start + half
    } else {
        start
    };
    event
        .contestants
        .iter()
        .skip(opponent_start)
        .take(half)
        .filter(|c| !c.tag.starts_with("Player"))
        .max_by(|a, b| {
            let value = |c: &EventContestant| {
                drivers
                    .iter()
                    .find(|d| d.native_tag == c.tag)
                    .map(|d| d.aggression + d.precision * 0.01)
                    .unwrap_or(0.)
            };
            value(a).total_cmp(&value(b))
        })
}

fn record_transaction(
    career: &mut CareerState,
    kind: crate::TransactionKind,
    amount: i64,
    car_id: Option<String>,
    event_id: Option<String>,
    description: &str,
) {
    career.transactions.push(crate::CareerTransaction {
        sequence: career.transactions.len() as u64 + 1,
        kind,
        amount,
        car_id,
        event_id,
        description: description.into(),
    });
}

fn goal_matches_event(
    goal: &crate::GoalDefinition,
    event: &EventDefinition,
    track: &TrackDefinition,
) -> bool {
    let route = if goal.route.is_empty() {
        goal.native_rows
            .iter()
            .find(|row| row.first().and_then(|v| v.as_str()) == Some("Route"))
            .and_then(|row| row.get(1))
            .and_then(|v| v.as_str())
            .unwrap_or("")
    } else {
        &goal.route
    };
    let drift = event.stage_mode().is_drift();
    let subtype = match event.stage_mode() {
        RaceMode::Eliminator => "Eliminator",
        RaceMode::LastManStanding => "LMS",
        RaceMode::DriftKing => "DriftKing",
        RaceMode::DriftObliterator => "DriftRace",
        RaceMode::DriftEndurance => "DriftEnduro",
        RaceMode::SoloDrift => "SoloDrift",
        RaceMode::TwinDrift => "TwinDrift",
        RaceMode::SpeedChallenge => "SpeedChallenge",
        RaceMode::LapTime => "LapTimeChallenge",
        RaceMode::PerfectLap => "PerfectLapChallenge",
        RaceMode::BeatCar => "BeatCarChallenge",
        _ => "None",
    };
    !(goal.qualifier != event.qualifier
        || (!goal.discipline.is_empty()
            && goal.discipline != "Any"
            && (goal.discipline == "Drift") != drift)
        || (!goal.subtype.is_empty() && goal.subtype != "Any" && goal.subtype != subtype)
        || (!goal.location.is_empty() && goal.location != "Any" && goal.location != track.location)
        || (!route.is_empty() && route != "Any" && route != track.native_route)
        || (!goal.contest_type.is_empty()
            && goal.contest_type != "Any"
            && goal.contest_type != event.contest_type)
        || (goal.team_race && event.mode != RaceMode::TeamRace)
        || (goal.endurance && event.endurance == 0)
        || (!goal.prize_type.is_empty()
            && goal.prize_type != "Any"
            && goal.prize_type != event.prize_type)
        || (goal.prototype && !event.prototype)
        || (goal.extreme_nos && !event.extreme_nos)
        || (!goal.car_class.is_empty()
            && goal.car_class != "Any"
            && !goal.car_class.eq_ignore_ascii_case(&event.car_class)))
}

fn update_goals(
    career: &mut CareerState,
    league: &crate::LeagueDefinition,
    race: &Race,
    won: bool,
    position: u32,
    ranking: &[usize],
) {
    let player = &race.racers[0];
    let beats = |tag: &str| {
        race.racers.iter().enumerate().skip(1).any(|(i, r)| {
            r.dna.native_tag == tag
                && ranking.iter().position(|v| *v == 0) < ranking.iter().position(|v| *v == i)
        })
    };
    for goal in &league.goals {
        if !goal_matches_event(goal, &race.event, &race.track) {
            continue;
        }
        let target = goal.args.first().and_then(|v| v.as_f64()).unwrap_or(1.);
        let tag = goal.args.first().and_then(|v| v.as_str()).unwrap_or("");
        let progress = career.goal_progress.entry(goal.id.clone()).or_default();
        if progress.complete {
            continue;
        }
        let (value, threshold, accumulate) = match goal.kind.to_ascii_lowercase().as_str() {
            "winrace" => (if won { 1. } else { 0. }, 1., false),
            "placeinrace" => (
                if f64::from(position) <= target {
                    1.
                } else {
                    0.
                },
                1.,
                false,
            ),
            "beatdriver" => (if beats(tag) { 1. } else { 0. }, 1., false),
            "windriverbet" => {
                let opponent = goal.args.get(1).and_then(|v| v.as_str()).unwrap_or("Any");
                (
                    if race
                        .racers
                        .get(race.bet_racer)
                        .map(|r| opponent == "Any" || r.dna.native_tag == opponent)
                        .unwrap_or(false)
                        && ranking.iter().position(|i| *i == 0)
                            < ranking.iter().position(|i| *i == race.bet_racer)
                    {
                        f64::from(race.wager)
                    } else {
                        0.
                    },
                    target,
                    false,
                )
            }
            "driftpoints" => (f64::from(player.score), target, true),
            "airtime" => (f64::from(race.air_time), target, true),
            "speedbarrier" => (f64::from(race.max_speed_kph), target, false),
            "trashcar" => (
                if race.spooked_tags.iter().any(|t| t == tag) {
                    1.
                } else {
                    0.
                },
                1.,
                false,
            ),
            "closefinish" | "victorymargin" => {
                let second = ranking
                    .iter()
                    .copied()
                    .find(|i| *i != 0)
                    .and_then(|i| race.racers[i].finish_time);
                let margin = player
                    .finish_time
                    .map(|time| f64::from(second.unwrap_or(race.elapsed) - time));
                let satisfied = won
                    && margin
                        .map(|m| {
                            if goal.kind.eq_ignore_ascii_case("CloseFinish") {
                                m <= target
                            } else {
                                m >= target
                            }
                        })
                        .unwrap_or(false);
                (if satisfied { 1. } else { 0. }, 1., false)
            }
            // Spectator betting has a separate settlement path, not a driver-race wager.
            _ => continue,
        };
        progress.value = if accumulate {
            progress.value + value
        } else {
            progress.value.max(value)
        };
        progress.complete = progress.value >= threshold;
        if progress.complete {
            if goal.prot_unlock {
                career.prototype_unlocked = true;
                let performance = career
                    .native_performance
                    .get_or_insert_with(Default::default);
                if performance.prototype_unlocks.len() < 40 {
                    performance.prototype_tokens = performance.prototype_tokens.wrapping_add(1);
                }
            }
            if goal.vis_unlock && !career.visual_unlocks.contains(&goal.id) {
                career.visual_unlocks.push(goal.id.clone());
            }
        }
    }
}

// Dynamic odds are a reconstruction policy; native probability/house-edge consumers are unrecovered.
fn spectator_odds(race: &Race) -> Vec<f32> {
    let leader = race.racers.iter().map(|r| r.progress).fold(0., f32::max);
    let weights: Vec<f32> = race
        .racers
        .iter()
        .map(|r| {
            if r.eliminated {
                0.
            } else {
                ((r.progress - leader) / race.track.points.len().max(1) as f32 * 4.).exp()
                    * (0.5 + r.dna.precision + r.dna.aggression * 0.2)
            }
        })
        .collect();
    let total: f32 = weights.iter().sum();
    weights
        .iter()
        .map(|w| (total / w.max(0.01) * 0.9).clamp(1.1, 20.))
        .collect()
}

fn drift_kick_requested(r: &Racer) -> bool {
    r.state.speed() > 12.
        && (r.input_clock % 6. < 0.5
            || (r.drift_state.phase == crate::DriftPhase::Coasting && r.drift_state.coast > 0.)
            || (r.drift_state.phase == crate::DriftPhase::Active
                && r.state.slip_angle.abs() < 0.35
                && r.state.slip_angle * r.state.yaw_rate > 0.1))
}

fn drift_target_speed(r: &Racer, track: &TrackDefinition) -> f32 {
    let mut allowed = 200. / 3.6f32;
    let mut distance = distance_xz(r.state.position, track.points[r.checkpoint]);
    for ahead in 0..20.min(track.points.len()) {
        let i = (r.checkpoint + ahead) % track.points.len();
        let a = track.points[(i + track.points.len() - 1) % track.points.len()];
        let b = track.points[i];
        let c = track.points[(i + 1) % track.points.len()];
        let turn =
            wrap_angle((c[0] - b[0]).atan2(c[2] - b[2]) - (b[0] - a[0]).atan2(b[2] - a[2])).abs();
        let curvature = turn / ((distance_xz(a, b) + distance_xz(b, c)) * 0.5).max(0.1);
        let corner_speed = (12. / curvature.max(0.0001)).sqrt().max(12.);
        allowed = allowed.min((corner_speed * corner_speed + 16. * distance).sqrt());
        distance += distance_xz(b, c);
    }
    allowed
}

#[cfg(test)]
mod standings_tests {
    use super::*;

    #[test]
    fn live_drift_position_uses_score_instead_of_track_distance() {
        let content = GameContent {
            cars: vec![CarDefinition::default()],
            tracks: vec![TrackDefinition::default()],
            events: vec![EventDefinition {
                mode: RaceMode::DriftKing,
                opponents: 1,
                ..Default::default()
            }],
            ..Default::default()
        };
        let mut game = Game::new(content);
        game.command(GameCommand::StartRace {
            event_id: "harbor-circuit".into(),
            career: false,
            wager: 0,
            pink_slip: false,
        })
        .unwrap();
        let race = game.race.as_mut().unwrap();
        race.racers[0].progress = 10.;
        race.racers[0].score = 100.;
        race.racers[1].progress = 5.;
        race.racers[1].score = 500.;
        let snapshot = game.frame_snapshot().race.unwrap();
        assert_eq!(snapshot.position, 2);
        assert_eq!(snapshot.standings, vec![1, 0]);
        // An eliminated high-scoring driver belongs below an active driver.
        game.race.as_mut().unwrap().racers[1].eliminated = true;
        let snapshot = game.frame_snapshot().race.unwrap();
        assert_eq!(snapshot.position, 1);
        assert_eq!(snapshot.standings, vec![0, 1]);
    }
}

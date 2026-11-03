//! Native source audio presentation. Family proxies are declared in audio/runtime.json.
use godot::classes::{
    AudioStream, AudioStreamMp3, AudioStreamPlayer, AudioStreamPlayer3D, FileAccess, Node3D,
    ResourceLoader,
};
use godot::prelude::*;
use oversteer_core::{GameScreen, GameSnapshot};
use serde_json::{Value, json};

struct Voice {
    player: Gd<AudioStreamPlayer3D>,
    path: String,
}
pub struct RuntimeAudio {
    root: Gd<Node3D>,
    data: Value,
    voices: Vec<Voice>,
    music: Gd<AudioStreamPlayer>,
    speech: Gd<AudioStreamPlayer>,
    sfx: Gd<AudioStreamPlayer>,
    pub music_gain: f32,
    pub engine_gain: f32,
    pub speech_gain: f32,
    pub sfx_gain: f32,
    previous_screen: GameScreen,
    previous_position: u32,
    previous_gear: i32,
    previous_nitrous: bool,
    previous_spook: bool,
    music_path: String,
}
impl RuntimeAudio {
    pub fn new(mut root: Gd<Node3D>) -> Self {
        let data = serde_json::from_str(
            &FileAccess::get_file_as_string("res://assets/audio/runtime.json").to_string(),
        )
        .unwrap_or(Value::Null);
        let mut music = AudioStreamPlayer::new_alloc();
        let speech = AudioStreamPlayer::new_alloc();
        let sfx = AudioStreamPlayer::new_alloc();
        root.add_child(&music);
        root.add_child(&speech);
        root.add_child(&sfx);
        music.set_volume_db(-20.);

        Self {
            root,
            data,
            voices: vec![],
            music,
            speech,
            sfx,
            music_gain: 0.5,
            engine_gain: 0.8,
            speech_gain: 0.8,
            sfx_gain: 0.65,
            previous_screen: GameScreen::MainMenu,
            previous_position: 1,
            previous_gear: 1,
            previous_nitrous: false,
            previous_spook: false,
            music_path: String::new(),
        }
    }
    pub fn shutdown(&mut self) {
        self.music.stop();
        self.music.set_stream(None::<&Gd<AudioStream>>);
        self.speech.stop();
        self.speech.set_stream(None::<&Gd<AudioStream>>);
        self.sfx.stop();
        self.sfx.set_stream(None::<&Gd<AudioStream>>);
        for voice in &mut self.voices {
            voice.player.stop();
            voice.player.set_stream(None::<&Gd<AudioStream>>);
        }
    }
    pub fn set_cinematic(&mut self, enabled: bool) {
        self.music.set_stream_paused(enabled);
        if enabled {
            self.speech.stop();
            self.sfx.stop();
            for voice in &mut self.voices {
                voice.player.set_stream_paused(true);
            }
        }
    }
    pub fn cycle_gain(&mut self, kind: &str) {
        let gain = match kind {
            "music" => &mut self.music_gain,
            "engine" => &mut self.engine_gain,
            "speech" => &mut self.speech_gain,
            _ => &mut self.sfx_gain,
        };
        *gain = if *gain >= 0.99 {
            0.
        } else {
            (*gain + 0.1).min(1.)
        };
    }
    pub fn options(&self) -> Value {
        json!({"music":self.music_gain,"engine":self.engine_gain,"speech":self.speech_gain,"sfx":self.sfx_gain})
    }
    pub fn apply_options(&mut self, value: &Value) {
        self.music_gain = value["music"].as_f64().unwrap_or(0.5) as f32;
        self.engine_gain = value["engine"].as_f64().unwrap_or(0.8) as f32;
        self.speech_gain = value["speech"].as_f64().unwrap_or(0.8) as f32;
        self.sfx_gain = value["sfx"].as_f64().unwrap_or(0.65) as f32;
    }
    pub fn effect(&mut self, key: &str) {
        let path = self.data["sfx"][key]
            .as_str()
            .or(match key {
                "nitrous" => Some("res://assets/audio/banks/53fab793/nos_ignite5.mp3"),
                "gear" => Some("res://assets/audio/banks/53fab793/gearv1_up.mp3"),
                _ => None,
            })
            .map(str::to_owned);
        if let Some(path) = path {
            play_2d(&mut self.sfx, &path, self.sfx_gain * 0.4, false);
        }
    }
    pub fn say(&mut self, key: &str) {
        if let Some(path) = self.data["speech"][key].as_str() {
            play_2d(&mut self.speech, path, self.speech_gain * 0.6, false);
        }
    }
    pub fn update(&mut self, snapshot: &GameSnapshot, throttle: f32, nitrous: bool) {
        let racing = snapshot.screen == GameScreen::Race;
        let prefix = snapshot
            .race
            .as_ref()
            .map(|r| {
                let id = &r.track_id;
                if id.starts_with("alps") {
                    "alp"
                } else if id.starts_with("tokyo") {
                    "jap"
                } else if id.starts_with("london") {
                    "lon"
                } else if id.starts_with("rome") {
                    "rom"
                } else if id.starts_with("sydney") {
                    "syd"
                } else {
                    "san"
                }
            })
            .unwrap_or("alp");
        let next = self.data["music"]
            .as_array()
            .and_then(|music| {
                music
                    .iter()
                    .filter_map(Value::as_str)
                    .find(|p| p.rsplit('/').next().is_some_and(|n| n.starts_with(prefix)))
            })
            .map(str::to_owned)
            .unwrap_or_default();
        if self.music_path != next && !next.is_empty() {
            self.music_path = next;
            play_2d(
                &mut self.music,
                &self.music_path,
                self.music_gain * 0.17,
                true,
            );
        }
        self.music.set_volume_db(db(self.music_gain * 0.17));
        if !self.music_path.is_empty() && !self.music.is_playing() {
            self.music.play();
        }
        if snapshot.screen != self.previous_screen {
            match snapshot.screen {
                GameScreen::Race => self.say("start"),
                GameScreen::Results => {
                    self.say(if snapshot.result.as_ref().is_some_and(|r| r.won) {
                        "race_win"
                    } else {
                        "finish"
                    })
                }
                _ => {}
            }
            self.previous_screen = snapshot.screen;
        }
        let Some(race) = &snapshot.race else {
            for mut voice in self.voices.drain(..) {
                voice.player.queue_free();
            }
            return;
        };
        let count = race
            .racers
            .iter()
            .map(|r| if r.is_player { 8 } else { 2 })
            .sum();
        while self.voices.len() < count {
            let mut player = AudioStreamPlayer3D::new_alloc();
            player.set_unit_size(8.);
            player.set_max_distance(100.);
            self.root.add_child(&player);
            self.voices.push(Voice {
                player,
                path: String::new(),
            });
        }
        if self.voices.len() > count {
            for mut voice in self.voices.drain(count..) {
                voice.player.queue_free();
            }
        }
        let mut slots = Vec::with_capacity(count);
        for car in &race.racers {
            let family = self.data["cars"][&car.car_id].as_str().unwrap_or("");
            let samples = self.data["families"][family]["samples"].as_array();
            let load = if car.is_player {
                throttle.clamp(0., 1.)
            } else {
                0.7
            };
            let roles = if car.is_player {
                vec![
                    ("engine", "off", (1. - load) * 0.65),
                    ("engine", "on", load * 0.65),
                    ("exhaust", "off", (1. - load) * 0.35),
                    ("exhaust", "on", load * 0.35),
                ]
            } else {
                vec![("engine", "on", 0.18)]
            };
            for (role, loading, weight) in roles {
                let mut choices: Vec<_> = samples
                    .map(|samples| {
                        samples
                            .iter()
                            .filter(|s| {
                                s["role"].as_str() == Some(role)
                                    && s["load"].as_str() == Some(loading)
                            })
                            .filter_map(|s| {
                                Some((
                                    s["reference_rpm"].as_f64()? as f32,
                                    s["path"].as_str()?.to_owned(),
                                ))
                            })
                            .collect()
                    })
                    .unwrap_or_default();
                choices.sort_by(|a, b| a.0.total_cmp(&b.0));
                choices.dedup_by(|a, b| a.0 == b.0);
                if choices.is_empty() {
                    slots.push((String::new(), 1., 0., car.position));
                    slots.push((String::new(), 1., 0., car.position));
                    continue;
                }
                let lower = choices.iter().rposition(|s| s.0 <= car.rpm).unwrap_or(0);
                let upper = (lower + 1).min(choices.len() - 1);
                let blend = if lower == upper {
                    0.
                } else {
                    ((car.rpm - choices[lower].0) / (choices[upper].0 - choices[lower].0).max(1.))
                        .clamp(0., 1.)
                };
                for (index, gain) in [(lower, 1. - blend), (upper, blend)] {
                    let sample = &choices[index];
                    slots.push((
                        sample.1.clone(),
                        (car.rpm / sample.0.max(600.)).clamp(0.45, 2.0),
                        gain * weight * self.engine_gain * 0.22,
                        car.position,
                    ));
                }
            }
        }
        for (voice, (path, pitch, gain, position)) in self.voices.iter_mut().zip(slots) {
            voice
                .player
                .set_position(Vector3::new(position[0], position[1] + 0.7, position[2]));
            voice.player.set_stream_paused(!racing);
            voice.player.set_pitch_scale(pitch);
            voice.player.set_volume_db(db(gain));
            if !path.is_empty() && voice.path != path {
                if let Some(stream) = stream(&path, true) {
                    voice.player.set_stream(&stream);
                    voice.path = path;
                    voice.player.play();
                }
            } else if racing && !voice.path.is_empty() && !voice.player.is_playing() {
                voice.player.play();
            }
        }
        if let Some(player) = race.racers.iter().find(|r| r.is_player) {
            if racing {
                if player.gear != self.previous_gear {
                    self.effect("gear");
                }
                if nitrous && !self.previous_nitrous {
                    self.effect("nitrous");
                }
                if player.spook > 0.6 && !self.previous_spook {
                    self.say("spook");
                }
                if race.position < self.previous_position {
                    self.say("overtake");
                }
            }
            self.previous_gear = player.gear;
            self.previous_nitrous = nitrous;
            self.previous_spook = player.spook > 0.6;
            self.previous_position = race.position;
        }
    }
    pub fn summary(&self) -> Value {
        json!({"source":"res://assets/audio/runtime.json","mixing_model":"neighboring native RPM/load loops with adapted linear crossfades and pitch","output_device":godot::classes::AudioServer::singleton().get_output_device().to_string(),"music_playing":self.music.is_playing(),"engine_voice_count":self.voices.len(),"active_engine_voices":self.voices.iter().filter(|v|v.player.is_playing()&&!v.player.get_stream_paused()&&v.player.get_volume_db()>-65.).count(),"speech_playing":self.speech.is_playing(),"music_path":self.music_path,"volumes":{"music":self.music_gain,"engine":self.engine_gain,"speech":self.speech_gain,"sfx":self.sfx_gain}})
    }
}
fn db(gain: f32) -> f32 {
    20. * gain.max(0.00001).log10()
}
fn stream(path: &str, looping: bool) -> Option<Gd<AudioStream>> {
    let stream = ResourceLoader::singleton()
        .load(path)?
        .try_cast::<AudioStream>()
        .ok()?;
    if let Ok(mut mp3) = stream.clone().try_cast::<AudioStreamMp3>() {
        mp3.set_loop(looping);
    }
    Some(stream)
}
fn play_2d(player: &mut Gd<AudioStreamPlayer>, path: &str, gain: f32, looping: bool) {
    if let Some(stream) = stream(path, looping) {
        player.set_stream(&stream);
        player.set_volume_db(db(gain));
        player.play();
    }
}

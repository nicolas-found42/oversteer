//! Checked atomic save I/O, preserving an invalid primary before backup recovery.
use crate::diagnostics;
use oversteer_core::{Game, GameContent};
use serde_json::json;
use std::{
    fs,
    io::Write,
    path::{Path, PathBuf},
};
pub struct Loaded {
    pub game: Game,
    pub source: &'static str,
    pub preserved: Option<PathBuf>,
}
fn side(path: &Path, suffix: &str) -> PathBuf {
    PathBuf::from(format!("{}{suffix}", path.display()))
}
fn io<T>(stage: &str, result: std::io::Result<T>) -> std::io::Result<T> {
    diagnostics::event(
        "storage.step",
        json!({"stage":stage,"outcome":if result.is_ok(){"ok"}else{"error"},"category":result.as_ref().err().map(|e|format!("{:?}", e.kind())).unwrap_or_else(||"none".into())}),
    );
    result
}
fn atomic(path: &Path, data: &str) -> Result<(), String> {
    diagnostics::event(
        "storage.write",
        json!({"target":if path.extension().is_some_and(|e| e == "backup"){"backup"}else{"primary"}}),
    );
    let parent = path.parent().ok_or("Save path has no parent")?;
    io("create_directory", fs::create_dir_all(parent))
        .map_err(|e| format!("Create save directory: {e}"))?;
    let temp = side(path, &format!(".tmp-{}", std::process::id()));
    let mut file = io("create_temporary", fs::File::create(&temp))
        .map_err(|e| format!("Create temporary save: {e}"))?;
    io("write", file.write_all(data.as_bytes())).map_err(|e| format!("Write save: {e}"))?;
    io("sync", file.sync_all()).map_err(|e| format!("Sync save: {e}"))?;
    io("replace", fs::rename(temp, path)).map_err(|e| format!("Replace save: {e}"))?;
    Ok(())
}
pub fn preserve(path: &Path) -> Result<Option<PathBuf>, String> {
    if !path.exists() {
        return Ok(None);
    }
    let stamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map_err(|e| e.to_string())?
        .as_nanos();
    let retained = side(path, &format!(".corrupt-{stamp}"));
    io("preserve", fs::copy(path, &retained)).map_err(|e| format!("Preserve damaged save: {e}"))?;
    Ok(Some(retained))
}
pub fn load(content: GameContent, path: &Path) -> Result<Loaded, String> {
    diagnostics::operation("career.load", |_| load_inner(content, path))
}
fn load_inner(content: GameContent, path: &Path) -> Result<Loaded, String> {
    let primary = io("read_primary", fs::read_to_string(path));
    let backup_path = side(path, ".backup");
    if matches!(&primary,Err(e)if e.kind()==std::io::ErrorKind::NotFound) && !backup_path.exists() {
        return Ok(Loaded {
            game: Game::new(content),
            source: "new",
            preserved: None,
        });
    }
    let problem = match primary {
        Ok(text) => match Game::load_json(content.clone(), &text) {
            Ok(game) => {
                return Ok(Loaded {
                    game,
                    source: "primary",
                    preserved: None,
                });
            }
            Err(e) => {
                diagnostics::event(
                    "storage.invalid",
                    json!({"target":"primary","category":"invalid_save"}),
                );
                e
            }
        },
        Err(e) => e.to_string(),
    };
    diagnostics::event("storage.fallback", json!({"target":"backup"}));
    let backup = io("read_backup", fs::read_to_string(&backup_path))
        .map_err(|e| format!("Career cannot be loaded ({problem}); backup unavailable: {e}"))?;
    let game = Game::load_json(content, &backup)
        .map_err(|e| format!("Career cannot be loaded ({problem}); backup invalid: {e}"))?;
    let preserved = preserve(path)?;
    atomic(path, &backup)?;
    Ok(Loaded {
        game,
        source: "backup",
        preserved,
    })
}
pub fn save(game: &Game, path: &Path) -> Result<(), String> {
    diagnostics::operation("career.save", |_| save_inner(game, path))
}
fn save_inner(game: &Game, path: &Path) -> Result<(), String> {
    let data = game
        .save_json()
        .map_err(|e| format!("Serialize career: {e}"))?;
    if path.exists() {
        let previous = io("read_previous", fs::read_to_string(path))
            .map_err(|e| format!("Read previous career: {e}"))?;
        if Game::load_json(game.content.clone(), &previous).is_ok() {
            atomic(&side(path, ".backup"), &previous)?;
        } else {
            preserve(path)?;
        }
    }
    atomic(path, &data)
}

pub fn load_preferences(path: &Path) -> Result<Option<serde_json::Value>, String> {
    diagnostics::operation("options.load", |_| load_preferences_inner(path))
}
fn load_preferences_inner(path: &Path) -> Result<Option<serde_json::Value>, String> {
    let primary = io("read_primary", fs::read_to_string(path));
    let backup_path = side(path, ".backup");
    if matches!(&primary,Err(error) if error.kind()==std::io::ErrorKind::NotFound)
        && !backup_path.exists()
    {
        return Ok(None);
    }
    let problem = match primary {
        Ok(text) => match serde_json::from_str::<serde_json::Value>(&text) {
            Ok(value) => return Ok(Some(value)),
            Err(error) => {
                diagnostics::event(
                    "storage.invalid",
                    json!({"target":"primary","category":"invalid_json"}),
                );
                error.to_string()
            }
        },
        Err(error) => error.to_string(),
    };
    diagnostics::event("storage.fallback", json!({"target":"backup"}));
    let backup = io("read_backup", fs::read_to_string(&backup_path))
        .map_err(|error| format!("Options unavailable ({problem}); backup: {error}"))?;
    let value = serde_json::from_str(&backup)
        .map_err(|error| format!("Options backup invalid: {error}"))?;
    preserve(path)?;
    atomic(path, &backup)?;
    Ok(Some(value))
}
pub fn save_preferences(path: &Path, value: &serde_json::Value) -> Result<(), String> {
    diagnostics::operation("options.save", |_| save_preferences_inner(path, value))
}
fn save_preferences_inner(path: &Path, value: &serde_json::Value) -> Result<(), String> {
    if path.exists() {
        let previous = io("read_previous", fs::read_to_string(path))
            .map_err(|error| format!("Read previous options: {error}"))?;
        if serde_json::from_str::<serde_json::Value>(&previous).is_ok() {
            atomic(&side(path, ".backup"), &previous)?;
        } else {
            preserve(path)?;
        }
    }
    atomic(
        path,
        &serde_json::to_string_pretty(value).map_err(|error| error.to_string())?,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use oversteer_core::{CarDefinition, GameCommand, PlayerProfile};
    fn fixture() -> GameContent {
        GameContent {
            cars: vec![CarDefinition {
                id: "test".into(),
                ..CarDefinition::default()
            }],
            ..GameContent::default()
        }
    }
    static NEXT: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    fn folder() -> PathBuf {
        let path = std::env::temp_dir().join(format!(
            "oversteer-save-{}-{}-{}",
            std::process::id(),
            NEXT.fetch_add(1, std::sync::atomic::Ordering::Relaxed),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ));
        fs::create_dir(&path).unwrap();
        path
    }
    #[test]
    fn damaged_primary_is_retained_before_backup_recovery() {
        let dir = folder();
        let path = dir.join("career.json");
        let text = Game::new(fixture()).save_json().unwrap();
        fs::write(&path, "damaged primary").unwrap();
        fs::write(side(&path, ".backup"), &text).unwrap();
        let loaded = load(fixture(), &path).unwrap();
        assert_eq!(loaded.source, "backup");
        assert_eq!(
            fs::read_to_string(loaded.preserved.unwrap()).unwrap(),
            "damaged primary"
        );
        assert_eq!(fs::read_to_string(&path).unwrap(), text);
        assert_eq!(fs::read_to_string(side(&path, ".backup")).unwrap(), text);
        fs::remove_dir_all(dir).unwrap();
    }
    #[test]
    fn two_damaged_copies_are_never_overwritten_by_load() {
        let dir = folder();
        let path = dir.join("career.json");
        fs::write(&path, "bad primary").unwrap();
        fs::write(side(&path, ".backup"), "bad backup").unwrap();
        assert!(load(fixture(), &path).is_err());
        assert_eq!(fs::read_to_string(&path).unwrap(), "bad primary");
        assert_eq!(
            fs::read_to_string(side(&path, ".backup")).unwrap(),
            "bad backup"
        );
        fs::remove_dir_all(dir).unwrap();
    }
    #[test]
    fn failed_backup_replace_prevents_primary_overwrite() {
        let dir = folder();
        let path = dir.join("career.json");
        let mut game = Game::new(fixture());
        save(&game, &path).unwrap();
        let before = fs::read_to_string(&path).unwrap();
        fs::create_dir(side(&path, ".backup")).unwrap();
        game.command(GameCommand::CustomizeAvatar {
            profile: PlayerProfile {
                name: "Changed".into(),
                ..PlayerProfile::default()
            },
        })
        .unwrap();
        assert!(save(&game, &path).is_err());
        assert_eq!(fs::read_to_string(&path).unwrap(), before);
        fs::remove_dir_all(dir).unwrap();
    }
    #[test]
    fn preferences_recover_backup_and_keep_damaged_bytes() {
        let dir = folder();
        let path = dir.join("options.json");
        let value = serde_json::json!({"schema":1,"presentation":{"mph":false,"quality":2}});
        let text = serde_json::to_string(&value).unwrap();
        fs::write(&path, "damaged preferences").unwrap();
        fs::write(side(&path, ".backup"), &text).unwrap();
        assert_eq!(load_preferences(&path).unwrap(), Some(value));
        assert_eq!(fs::read_to_string(&path).unwrap(), text);
        assert!(
            fs::read_dir(&dir)
                .unwrap()
                .filter_map(Result::ok)
                .any(
                    |entry| entry.file_name().to_string_lossy().contains(".corrupt-")
                        && fs::read_to_string(entry.path()).unwrap() == "damaged preferences"
                )
        );
        fs::remove_dir_all(dir).unwrap();
    }
    #[test]
    fn preferences_backup_failure_protects_existing_options() {
        let dir = folder();
        let path = dir.join("options.json");
        let old = serde_json::json!({"schema":1,"keyboard":{"throttle":87}});
        let text = serde_json::to_string(&old).unwrap();
        fs::write(&path, &text).unwrap();
        fs::create_dir(side(&path, ".backup")).unwrap();
        assert!(
            save_preferences(
                &path,
                &serde_json::json!({"schema":1,"keyboard":{"throttle":75}})
            )
            .is_err()
        );
        assert_eq!(fs::read_to_string(path).unwrap(), text);
        fs::remove_dir_all(dir).unwrap();
    }
}

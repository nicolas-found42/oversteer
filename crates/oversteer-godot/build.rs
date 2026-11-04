use std::{
    collections::hash_map::DefaultHasher,
    fs,
    hash::{Hash, Hasher},
    path::Path,
};

fn sources(path: &Path, hash: &mut DefaultHasher) {
    let mut entries: Vec<_> = fs::read_dir(path)
        .unwrap()
        .map(|e| e.unwrap().path())
        .collect();
    entries.sort();
    for entry in entries {
        if entry.is_dir() {
            sources(&entry, hash);
        } else {
            println!("cargo:rerun-if-changed={}", entry.display());
            entry.hash(hash);
            fs::read(entry).unwrap().hash(hash);
        }
    }
}
fn main() {
    let git = |args: &[&str]| {
        std::process::Command::new("git")
            .args(args)
            .output()
            .ok()
            .filter(|r| r.status.success())
            .and_then(|r| String::from_utf8(r.stdout).ok())
            .map(|s| s.trim().to_owned())
    };
    let commit = git(&["rev-parse", "HEAD"]).unwrap_or_else(|| "unknown".into());
    println!("cargo:rustc-env=OVERSTEER_COMMIT={commit}");
    for reference in [
        Some("HEAD".to_owned()),
        Some("packed-refs".to_owned()),
        git(&["symbolic-ref", "-q", "HEAD"]),
    ]
    .into_iter()
    .flatten()
    {
        if let Some(path) = git(&["rev-parse", "--git-path", &reference]) {
            println!("cargo:rerun-if-changed={path}");
        }
    }
    let mut hash = DefaultHasher::new();
    sources(Path::new("src"), &mut hash);
    sources(Path::new("../oversteer-core/src"), &mut hash);
    for path in [
        "build.rs",
        "Cargo.toml",
        "../oversteer-core/Cargo.toml",
        "../../Cargo.lock",
        "../../Cargo.toml",
        "../../rust-toolchain.toml",
    ] {
        println!("cargo:rerun-if-changed={path}");
        fs::read(path).unwrap().hash(&mut hash);
    }
    // Diagnostic source fingerprint, not a cryptographic integrity proof or binary hash.
    println!(
        "cargo:rustc-env=OVERSTEER_SOURCE_ID=source-{:016x}",
        hash.finish()
    );
}

#!/usr/bin/env python3
"""Build, import, run, and export the pinned native Godot/Rust game."""

import argparse
import json
import platform
import re
import shutil
import subprocess
from pathlib import Path

import background_window
import diagnostics
from bootstrap import prepare_template

ROOT = Path(__file__).resolve().parents[2]
GODOT = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"


def run(arguments):
    diagnostics.recorded_run([str(value) for value in arguments], cwd=ROOT, check=True)


def validate_imports():
    assets = ROOT / "godot/assets"
    invalid = [path for path in assets.rglob("*.import") if "valid=false" in path.read_text()]
    content = json.loads((assets / "game-content.json").read_text())
    scenes = [assets / "worlds" / f"{track['id']}.glb" for track in content["tracks"]]
    scenes.extend(
        ROOT / "godot" / car["model_path"].removeprefix("res://") for car in content["cars"]
    )
    missing = [path for path in scenes if not path.exists() or not Path(f"{path}.import").exists()]
    if invalid or missing:
        names = "\n".join(str(path.relative_to(ROOT)) for path in invalid + missing)
        raise RuntimeError(f"Runtime scenes have invalid or missing Godot imports:\n{names}")


def configure_road_mipmaps(root=ROOT):
    """Custom shader samplers are not covered by Godot's automatic 3D detection."""
    contract_path = root / "godot/assets/worlds/render-contract.json"
    if not contract_path.exists():
        return 0
    contract = json.loads(contract_path.read_text())
    paths = set()
    for catalog, definition in contract.get("catalogs", {}).items():
        for layer in definition.get("tarmac", []):
            paths.update(layer.get(key) for key in ("base_texture_path", "markings_texture_path"))
        materials_path = definition.get("materials_path", "")
        if materials_path:
            materials = root / "godot" / materials_path.removeprefix("res://")
            for material in json.loads(materials.read_text()):
                texture = material.get("nativeTextureBindings", {}).get("baseTexture")
                if material.get("nativeShader") == "tarmac" and texture is not None:
                    paths.add(f"res://assets/worlds/textures/{catalog}/{texture}.png")
    changed = 0
    for path in sorted(p for p in paths if p):
        imported = root / "godot" / (path.removeprefix("res://") + ".import")
        if not imported.exists():
            continue  # First import creates the settings; the post-import pass handles these.
        before = imported.read_text()
        after = before.replace("mipmaps/generate=false", "mipmaps/generate=true")
        if after != before:
            imported.write_text(after)
            changed += 1
    return changed


def import_assets(headless=False):
    configure_road_mipmaps()
    # Godot can retain a failed import even after its source has been repaired.
    # Remove only generated failure metadata so the editor retries that resource.
    for path in (ROOT / "godot/assets").rglob("*.import"):
        if "valid=false" in path.read_text():
            path.unlink()
    # The dummy renderer can report success while emitting texture initialization
    # errors for valid embedded GLB art. Import with the actual target renderer.
    arguments = [GODOT, "--path", ROOT / "godot", "--editor", "--import"]
    if headless:
        arguments.insert(1, "--headless")
    process = diagnostics.recorded_run(
        [str(value) for value in arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=None if headless else background_window.environment(GODOT),
    )
    print(process.stdout, end="", flush=True)
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, arguments)
    if re.search(r"^ERROR:|^SCRIPT ERROR:", process.stdout, re.M):
        raise RuntimeError("Godot asset import emitted errors despite a successful process exit")
    if "BACKGROUND FOCUS VIOLATION" in process.stdout:
        raise RuntimeError("Asset import activated its app; background focus verification failed")
    validate_imports()
    if configure_road_mipmaps():
        import_assets(headless=headless)


def require_runtime_inputs():
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeError("The native game requires Apple Silicon macOS")
    if not GODOT.is_file():
        raise RuntimeError("Pinned Godot missing; run python tools/game/bootstrap.py")
    if not (ROOT / "godot/assets/game-content.json").is_file():
        raise RuntimeError("Prepared runtime assets missing; see tools/game/assets/README.md")


def require_unloaded_library(target):
    if not target.exists():
        return
    process = subprocess.run(
        ["/usr/sbin/lsof", "-t", str(target)], capture_output=True, text=True, check=False
    )
    if process.returncode not in (0, 1):
        raise RuntimeError(f"Could not check loaded extension: {process.stderr.strip()}")
    if process.stdout.strip():
        raise RuntimeError(
            f"Close the Godot process before replacing {target} (PIDs {process.stdout.split()})"
        )


def build(headless=False, profile="release", skip_import=False):
    if not skip_import:
        require_runtime_inputs()
    configurations = ["debug"] if profile == "dev" else ["debug", "release"]
    targets = [ROOT / f"godot/bin/{name}/liboversteer_godot.dylib" for name in configurations]
    for target in targets:
        require_unloaded_library(target)
    arguments = ["cargo", "build", "--locked", "-p", "oversteer-godot"]
    if profile == "release":
        arguments.append("--release")
    arguments.extend(["--target", "aarch64-apple-darwin"])
    run(arguments)
    directory = "debug" if profile == "dev" else "release"
    source = ROOT / f"build/rust/aarch64-apple-darwin/{directory}/liboversteer_godot.dylib"
    for target in targets:
        # A process may have opened the extension while Cargo was compiling.
        require_unloaded_library(target)
    for target in targets:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    if not skip_import:
        import_assets(headless=headless)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "import", "run", "export", "test"])
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--profile", choices=["dev", "release"], default="release")
    parser.add_argument(
        "--skip-import", action="store_true", help="Build extension without importing assets"
    )
    parser.add_argument("--scenario")
    parser.add_argument("--ui-actions", type=Path)
    parser.add_argument("--input-events", type=Path)
    parser.add_argument("--settings-dir", type=Path)
    parser.add_argument("--capture", type=Path)
    parser.add_argument(
        "--save-file", type=Path, help="Explicit isolated save for native verification"
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--packaged", type=Path, help="Run this exported .app instead of the editor project"
    )
    parser.add_argument("--event")
    parser.add_argument("--car")
    parser.add_argument("--wager", type=int)
    parser.add_argument("--pink-slip", action="store_true")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--warmup", type=int)
    options = parser.parse_args()
    if options.skip_import and options.action != "build":
        parser.error("--skip-import is only valid for build")
    if options.action == "export" and options.profile != "release":
        parser.error("export requires --profile release")
    if options.action == "test":
        run(["cargo", "test", "--workspace", "--locked"])
        return
    if options.action == "import":
        require_runtime_inputs()
        import_assets(headless=options.headless)
        return
    if not options.skip_build and not options.packaged:
        build(headless=options.headless, profile=options.profile, skip_import=options.skip_import)
    elif options.action in {"run", "export"} and not options.packaged:
        require_runtime_inputs()
    if options.action == "run":
        arguments = (
            [options.packaged.resolve() / "Contents/MacOS/Oversteer"]
            if options.packaged
            else [GODOT, "--path", ROOT / "godot"]
        )
        if options.headless:
            arguments.append("--headless")
        arguments.append("--")
        if options.scenario:
            arguments.extend(["--scenario", options.scenario])
        if options.ui_actions:
            arguments.extend(["--ui-actions", options.ui_actions.resolve()])
        if options.input_events:
            arguments.extend(["--input-events", options.input_events.resolve()])
        if options.settings_dir:
            arguments.extend(["--settings-dir", options.settings_dir.resolve()])
        if options.capture:
            options.capture.mkdir(parents=True, exist_ok=True)
            arguments.extend(["--capture", options.capture.resolve()])
        if options.save_file:
            arguments.extend(["--save-file", options.save_file.resolve()])
        for name in ["event", "car", "wager", "frames", "warmup"]:
            value = getattr(options, name)
            if value is not None:
                arguments.extend([f"--{name}", value])
        if options.pink_slip:
            arguments.append("--pink-slip")
        run(arguments)
    elif options.action == "export":
        if options.skip_build:
            validate_imports()
        prepare_template()
        destination = ROOT / "build/packages/Oversteer.app"
        destination.parent.mkdir(parents=True, exist_ok=True)
        run([GODOT, "--headless", "--path", "godot", "--export-release", "macOS", destination])
        run(["codesign", "--force", "--deep", "--sign", "-", destination])


if __name__ == "__main__":
    main()

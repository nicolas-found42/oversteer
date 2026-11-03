#!/usr/bin/env python3
"""Build, import, run, and export the pinned native Godot/Rust game."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from bootstrap import prepare_template

ROOT = Path(__file__).resolve().parents[2]
GODOT = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"


def run(arguments):
    subprocess.run([str(value) for value in arguments], cwd=ROOT, check=True)


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


def import_assets(headless=False):
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
    process = subprocess.run(
        [str(value) for value in arguments],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(process.stdout, end="", flush=True)
    if process.returncode:
        raise subprocess.CalledProcessError(process.returncode, arguments)
    if re.search(r"^ERROR:|^SCRIPT ERROR:", process.stdout, re.M):
        raise RuntimeError("Godot asset import emitted errors despite a successful process exit")
    validate_imports()


def build(headless=False):
    run(
        ["cargo", "build", "-p", "oversteer-godot", "--release", "--target", "aarch64-apple-darwin"]
    )
    source = ROOT / "build/rust/aarch64-apple-darwin/release/liboversteer_godot.dylib"
    for configuration in ["debug", "release"]:
        target = ROOT / f"godot/bin/{configuration}"
        target.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target / source.name)
    import_assets(headless=headless)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["build", "import", "run", "export", "test"])
    parser.add_argument("--skip-build", action="store_true")
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
    if options.action == "test":
        run(["cargo", "test", "--workspace"])
        return
    if options.action == "import":
        import_assets(headless=options.headless)
        return
    if not options.skip_build and not options.packaged:
        build(headless=options.headless)
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

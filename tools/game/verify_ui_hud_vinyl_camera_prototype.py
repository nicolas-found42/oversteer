"""Throwaway V088 experiment: four native PNGs, workshop camera only."""

import argparse
import json
import subprocess
from pathlib import Path

import background_window

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    command = [
        str(godot),
        "--path",
        str(ROOT / "godot"),
        "--rendering-driver",
        "metal",
        "--script",
        str(Path(__file__).with_name("ui_hud_vinyl_camera_prototype.gd")),
        "--",
        str(output),
        "--save-file",
        str(output / "save.json"),
        "--settings-dir",
        str(output / "settings"),
    ]
    report = {"prototype": True, "png_budget": 4, "status": "running", "command": command}
    try:
        with (output / "runtime.log").open("w") as log:
            result = subprocess.run(
                command,
                env=background_window.environment(godot),
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=120,
            )
        runtime = (output / "runtime.log").read_text()
        if result.returncode or any(x in runtime for x in ["SCRIPT ERROR", "ERROR:", "panicked"]):
            raise RuntimeError("Prototype failed; inspect runtime.log")
        if background_window.MARKER not in runtime:
            raise RuntimeError("Missing background focus guard")
        captures = sorted(p.name for p in output.glob("*.png"))
        if captures != ["current.png", "high-oblique.png", "rear.png", "side.png"]:
            raise RuntimeError(f"Four-image budget/coverage mismatch: {captures}")
        evidence = json.loads((output / "vinyl-camera.json").read_text())
        if not all(item["passed"] for item in evidence["checks"]):
            raise RuntimeError("Prototype evidence assertion failed")
        report.update(status="passed", captures=captures, exit_code=result.returncode)
    except Exception as error:
        report.update(status="failed", error=str(error))
        raise
    finally:
        (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

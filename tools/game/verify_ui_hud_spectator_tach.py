"""Headless, silent spectator logic observations with actual Buttons and isolated state."""

import argparse
import json
import subprocess
from pathlib import Path

import background_window
from verify_ui_hud_window import ROOT


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    environment = background_window.environment(godot)
    environment.pop("OVERSTEER_BACKGROUND_VISIBLE", None)
    command = [
        str(godot),
        "--headless",
        "--audio-driver",
        "Dummy",
        "--path",
        str(ROOT / "godot"),
        "--script",
        str(Path(__file__).with_name("ui_hud_spectator_tach.gd")),
        "--",
        str(output),
        "--save-file",
        str(output / "save.json"),
        "--settings-dir",
        str(output / "settings"),
    ]
    with (output / "runtime.log").open("w") as log:
        result = subprocess.run(
            command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=120
        )
    runtime = (output / "runtime.log").read_text()
    if result.returncode or any(
        marker in runtime
        for marker in ("ERROR:", "SCRIPT ERROR", "panicked", "BACKGROUND FOCUS VIOLATION")
    ):
        raise RuntimeError("Spectator tach check failed; inspect runtime.log and observation JSON")
    report = json.loads((output / "spectator-tach.json").read_text())
    if report["status"] != "passed" or list(output.glob("*.png")):
        raise RuntimeError("Spectator logic failed or unexpectedly produced images")
    if not report.get("logic_only") or report.get("rendered"):
        raise RuntimeError("Headless result must not claim rendering verification")
    observations = report["observations"]
    if len(observations) != 2 or len({item["catalog_redline"] for item in observations}) != 2:
        raise RuntimeError("Two distinct real redlines were not observed")
    print(json.dumps({"status": "passed", "observations": observations}))


if __name__ == "__main__":
    main()

"""Exercise the existing navigation scenarios silently, without a display window."""

import argparse
import json
import subprocess
from pathlib import Path

import background_window

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    command = [
        str(godot),
        "--headless",
        "--audio-driver",
        "Dummy",
        "--path",
        str(ROOT / "godot"),
        "--script",
        str(Path(__file__).with_name("ui_hud_navigation_headless.gd")),
        "--",
        str(output),
        "--save-file",
        str(output / "save.json"),
        "--settings-dir",
        str(output / "settings"),
    ]
    with (output / "runtime.log").open("w") as log:
        result = subprocess.run(
            command,
            env=background_window.environment(godot),
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
    runtime = (output / "runtime.log").read_text()
    checks = json.loads((output / "navigation.json").read_text())
    observations = json.loads((output / "headless-observations.json").read_text())
    assert result.returncode == 0, "Headless navigation process failed"
    assert not any(
        marker in runtime for marker in ("ERROR:", "SCRIPT ERROR", "panicked", "FOCUS VIOLATION")
    ), "Inspect runtime.log"
    assert checks and all(item["passed"] for item in checks), "Navigation assertion failed"
    assert observations["drivers"] == {"display": "headless", "audio": "Dummy"}
    assert observations["logic_only"] and not observations["rendered"]
    assert not list(output.glob("*.png")), "Headless check must not produce image evidence"
    report = {
        "status": "passed",
        "command": command,
        "exit_code": result.returncode,
        "checks": len(checks),
        "observations": [item["name"] for item in observations["observations"]],
        "logic_only": True,
        "rendered": False,
        "png_count": 0,
    }
    (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()

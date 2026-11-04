"""Bounded silent headless actual-control finance and cart checks, no image claims."""

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
        str(Path(__file__).with_name("ui_hud_finance_headless.gd")),
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
        raise RuntimeError("Finance logic failed; inspect retained runtime.log and finance.json")
    report = json.loads((output / "finance.json").read_text())
    if (
        report["status"] != "passed"
        or not report["logic_only"]
        or report["rendered"]
        or list(output.glob("*.png"))
    ):
        raise RuntimeError("Invalid logic-only finance receipt")
    if not report["checks"] or not all(check["passed"] for check in report["checks"]):
        raise RuntimeError("Finance assertions failed")
    print(
        json.dumps(
            {
                "status": "passed",
                "checks": len(report["checks"]),
                "checkpoints": [item["label"] for item in report["checkpoints"]],
                "drivers": report["drivers"],
            }
        )
    )


if __name__ == "__main__":
    main()

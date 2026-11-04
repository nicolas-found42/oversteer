"""Bounded real-control wager/forfeit matrix; headless, muted, zero images."""

import argparse
import json
import subprocess
from pathlib import Path

import background_window

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    f"{stake}_{action}_{decision}"
    for stake in ("cash", "pink")
    for action in ("restart", "exit")
    for decision in ("cancel", "commit")
] + ["none_restart_commit", "none_exit_commit"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--case", choices=CASES)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    environment = background_window.environment(godot)
    reports = []
    for case in [args.case] if args.case else CASES:
        destination = output / case
        destination.mkdir()
        command = [
            str(godot),
            "--headless",
            "--audio-driver",
            "Dummy",
            "--path",
            str(ROOT / "godot"),
            "--script",
            str(Path(__file__).with_name("ui_hud_forfeit_headless.gd")),
            "--",
            str(destination),
            case,
            "--save-file",
            str(destination / "save.json"),
            "--settings-dir",
            str(destination / "settings"),
        ]
        with (destination / "runtime.log").open("w") as log:
            result = subprocess.run(
                command, env=environment, stdout=log, stderr=subprocess.STDOUT, timeout=90
            )
        runtime = (destination / "runtime.log").read_text()
        receipt = json.loads((destination / "forfeit.json").read_text())
        assert result.returncode == 0, f"{case}: inspect runtime.log and forfeit.json"
        assert not any(
            marker in runtime
            for marker in ("ERROR:", "SCRIPT ERROR", "panicked", "FOCUS VIOLATION")
        ), case
        assert receipt["drivers"] == {"display": "headless", "audio": "Dummy"}, case
        assert receipt["logic_only"] and not receipt["rendered"], case
        assert receipt["checks"] and all(item["passed"] for item in receipt["checks"]), case
        assert not list(destination.rglob("*.png")), "Headless logic check produced an image"
        reports.append(
            {
                "case": case,
                "checks": len(receipt["checks"]),
                "observations": len(receipt["observations"]),
                "exit": result.returncode,
            }
        )
        print(json.dumps(reports[-1]), flush=True)
    (output / "verification.json").write_text(
        json.dumps(
            {
                "status": "passed",
                "logic_only": True,
                "rendered": False,
                "png_count": 0,
                "cases": reports,
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()

"""UI/HUD brief scenarios using the existing native renderer and isolated saves."""

import argparse
import json
import subprocess
from pathlib import Path

import background_window
import verify

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "family",
        choices=[
            "editing",
            "finance",
            "navigation",
            "paint",
            "circuit-hud",
            "drift-hud",
            "pink-win",
            "pink-loss",
            "instruments",
        ],
    )
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.family in [
        "navigation",
        "circuit-hud",
        "drift-hud",
        "pink-win",
        "pink-loss",
        "instruments",
    ]:
        godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
        command = [
            str(godot),
            "--path",
            str(ROOT / "godot"),
            "--rendering-driver",
            "metal",
            "--script",
            str(
                Path(__file__).with_name(
                    "ui_hud_navigation.gd"
                    if args.family == "navigation"
                    else "ui_hud_wager_result.gd"
                    if args.family.startswith("pink-")
                    else "ui_hud_race.gd"
                )
            ),
            "--",
            str(output),
            "--save-file",
            str(output / "save.json"),
            "--settings-dir",
            str(output / "settings"),
        ]
        if args.family != "navigation":
            command += [
                "--scenario",
                "career-race" if args.family.startswith("pink-") else "driving",
                "--event",
                "oversteer-0-drift" if args.family == "drift-hud" else "oversteer-0-circuit",
                "--screenshot-limit",
                "10",
            ]
        if args.family.startswith("pink-"):
            command += ["--capture", str(output), "--wager", "100"]
        if args.family in ("circuit-hud", "drift-hud"):
            # Observe unaccelerated simulation and let the observer finish at Results.
            command += ["--frames", "15000"]
        if args.family == "instruments":
            settings = output / "settings"
            settings.mkdir()
            (settings / "options.json").write_text(
                json.dumps({"schema": 1, "presentation": {"mph": False}})
            )
            command += [
                "--input-events",
                str(ROOT / "data/oversteer/scenarios/ui-hud-instruments.json"),
                "--frames",
                "1440",
                "--car",
                "MCLA_VP_SLN_S7_06",
            ]
        environment = background_window.environment(godot)
        with (output / "runtime.log").open("w") as log:
            result = subprocess.run(
                command,
                env=environment,
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=300,
            )
        runtime = (output / "runtime.log").read_text()
        if (
            any(line.startswith(("ERROR:", "SCRIPT ERROR:")) for line in runtime.splitlines())
            or "panicked at" in runtime
        ):
            raise AssertionError("Runtime error: inspect runtime.log")
        if result.returncode == 0 and args.family in ("instruments", "circuit-hud", "drift-hud"):
            observations = json.loads((output / "hud-observations.json").read_text())
            if not observations:
                raise AssertionError("HUD observer produced no evidence")
        if result.returncode == 0 and args.family == "navigation":
            from PIL import Image

            # This isolated fixture retains its red Civic through the editor/credits route.
            # Inspect the car stage, excluding the orange menu chrome on the left.
            car_pixels = {}
            for name in ("title", "utility-focus"):
                with Image.open(output / f"{name}.png") as image:
                    stage = image.convert("RGB").crop((850, 350, 1800, 900))
                    count = sum(
                        r > 70 and r > 1.4 * g and r > 1.4 * b
                        for r, g, b in stage.get_flattened_data()
                    )
                car_pixels[name] = count
                if count < 5000:
                    raise AssertionError(f"Red fixture vehicle absent from {name}: {count} pixels")
            (output / "preview-pixels.json").write_text(json.dumps(car_pixels, indent=2))
        if result.returncode == 0 and args.family.startswith("pink-"):
            snapshot = json.loads((output / "scenario.json").read_text())["snapshot"]
            outcome = snapshot["result"]
            lost = outcome["pink_slip"] == "GT4_HOND0018"
            expected_loss = args.family == "pink-loss"
            if lost != expected_loss:
                raise AssertionError(f"Expected {args.family}, observed {outcome}")
            if lost and "GT4_HOND0018" in snapshot["career"]["garage"]:
                raise AssertionError("Lost vehicle remains owned")
        raise SystemExit(result.returncode)
    names = ["customization", "parts"] if args.family == "editing" else [args.family]
    cases = []
    for name in names:
        plan = ROOT / f"data/oversteer/scenarios/ui-hud-{name}.json"
        steps = json.loads(plan.read_text())
        cases.append(
            {
                "id": name,
                "scenario": "title",
                "frames": steps[-1]["after_frame"] + 40,
                "ui_actions": plan,
            }
        )
    budget = sum(
        1 + sum("capture" in step for step in json.loads(case["ui_actions"].read_text()))
        for case in cases
    )
    if budget > 50:
        raise ValueError(f"Capture budget exceeded: {budget}")
    results = [verify.run_case(case, output, None, screenshot_limit=budget) for case in cases]
    (output / "verification.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    if not all(all(result["checks"].values()) for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

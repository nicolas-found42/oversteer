#!/usr/bin/env python3
"""Capture close full-car views across three camera axes and explicit lighting."""

import argparse
import hashlib
import html
import json
import struct
import subprocess
import time
from pathlib import Path

import background_window
import metal_capture
from build import GODOT, ROOT

CARS = ["GT4_HOND0018", "GT4_MAZD0012", "GT4_MITS0001"]
MAX_SCREENSHOTS = 50
VIEWS_PER_CAR = 14


def screenshot_budget(cars, smoke=False):
    count = len(cars) * (6 if smoke else VIEWS_PER_CAR)
    if len(cars) != len(set(cars)):
        raise ValueError("Select each car only once per run")
    if count > MAX_SCREENSHOTS:
        raise ValueError(f"Run requires {count} screenshots; maximum is {MAX_SCREENSHOTS}")
    return count


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture_contract_checks(captures, events, smoke=False):
    begins = {e["details"]["index"]: e for e in events if e["event"] == "capture_begin"}
    ends = {e["details"]["id"]: e for e in events if e["event"] == "capture_complete"}
    timing_matches = bool(captures) and len(begins) == len(ends) == len(captures)
    for index, capture in enumerate(captures):
        begin, end = begins.get(index), ends.get(capture["id"])
        timing_matches = timing_matches and begin is not None and end is not None
        if begin is not None and end is not None:
            timing_matches = timing_matches and (
                capture["capture_ms"] > 0
                and capture["capture_started_wall_ms"] == begin["wall_ms"]
                and capture["capture_ms"] == end["wall_ms"] - begin["wall_ms"]
                and capture["capture_ms"] == end["details"]["capture_ms"]
            )
    checks = {"capture_timing_matches_event_log": timing_matches}
    if not smoke:
        shots = [c["shot"] for c in captures]
        isolated = [s for s in shots if s["isolated"]]
        checks["all_isolated_azimuths"] = {s["azimuth"] for s in isolated} == set(range(0, 360, 45))
        checks["course_quarter_views"] = {s["azimuth"] for s in shots if not s["isolated"]} == {
            45,
            135,
            225,
            315,
        }
        checks["top_underbody_and_roll"] = {s["roll"] for s in isolated} >= {-20, 20} and {
            s["elevation"] for s in isolated
        } >= {-25, 75}
        checks["multiple_lighting_conditions"] = {s["light"] for s in shots} >= {
            "race",
            "neutral",
            "grazing",
            "backlight",
        }
    return checks


def material_import_check(raw, surfaces, wheels=None, finish="gloss"):
    size = struct.unpack_from("<I", raw, 12)[0]
    source = json.loads(raw[20 : 20 + size])
    materials = {m["name"]: m for m in source.get("materials", []) if "name" in m}
    mismatches = []
    compared = 0
    for row in surfaces:
        material = materials.get(row["base_name"])
        factory = row.get("factory_state")
        if material is None or factory is None:
            continue
        compared += 1
        alpha = material.get("pbrMetallicRoughness", {}).get("baseColorFactor", [1, 1, 1, 1])[3]
        transparency = {"OPAQUE": 0, "MASK": 2, "BLEND": 4}[material.get("alphaMode", "OPAQUE")]
        if abs(factory["rgba"][3] - alpha) > 1e-5 or factory["transparency"] != transparency:
            mismatches.append(
                {
                    "material": row["base_name"],
                    "source_alpha": alpha,
                    "source_transparency": transparency,
                    "runtime": factory,
                }
            )
        standard = row.get("runtime_standard_state", {})
        shader = row.get("runtime_render_state", {})
        if row.get("wheel"):
            if standard.get("cull_mode") != 0:
                mismatches.append(
                    {"material": row["base_name"], "error": "Wheel must use back-face culling"}
                )
            if "tire" in row["base_name"] and transparency in (0, 2):
                if (
                    factory["rgba"][3] <= 0
                    or row.get("runtime_standard_rgba", [0, 0, 0, 0])[3] <= 0
                ):
                    mismatches.append(
                        {"material": row["base_name"], "error": "Opaque/masked tire has zero alpha"}
                    )
        roughness = standard.get("roughness", factory.get("roughness"))
        if roughness is not None and not 0 <= roughness <= 1:
            mismatches.append({"material": row["base_name"], "error": "Invalid roughness"})
        if row.get("paint_target") and finish == "gloss":
            if not 0.05 <= shader.get("paint_roughness", 1) <= 0.3 or not shader.get(
                "paint_clearcoat"
            ):
                mismatches.append(
                    {
                        "material": row["base_name"],
                        "error": "Gloss override missing low roughness/clearcoat",
                    }
                )
    if wheels is not None:
        if not wheels:
            mismatches.append({"error": "No rendered wheel observations"})
        for wheel in wheels:
            a, b, c = wheel["basis"]
            determinant = (
                a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])
            )
            orthonormal = all(
                abs(sum(x * y for x, y in zip(u, v)) - (1 if i == j else 0)) < 0.001
                for i, u in enumerate((a, b, c))
                for j, v in enumerate((a, b, c))
            )
            if determinant <= 0 or not orthonormal:
                mismatches.append(
                    {
                        "wheel": wheel["node"],
                        "error": "Wheel basis is not orthonormal and right-handed",
                        "determinant": determinant,
                    }
                )
    return {
        "passed": compared > 0 and not mismatches,
        "compared": compared,
        "mismatches": mismatches,
        "scope": "Factory alpha/transparency, wheel handedness/orthonormality/back-face culling, tire alpha, roughness and effective gloss shader finish",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--car", action="append", choices=CARS)
    parser.add_argument(
        "--smoke", action="store_true", help="Six views per car to verify the capture pipeline"
    )
    parser.add_argument(
        "--freeze-frame", type=int, help="Override the default final input event + 2 active ticks"
    )
    parser.add_argument(
        "--metal-capture",
        action="store_true",
        help="Capture one GPU frame per car using a separately signed diagnostic engine",
    )
    args = parser.parse_args()
    cars = args.car or CARS
    try:
        planned_screenshots = screenshot_budget(cars, args.smoke)
    except ValueError as error:
        parser.error(str(error))
    destination = args.output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    script = ROOT / "tools/game/inspection/vehicle.gd"
    library = ROOT / "godot/bin/debug/liboversteer_godot.dylib"
    executable = GODOT
    engine = {"source": str(GODOT), "source_sha256": digest(GODOT)}
    if args.metal_capture:
        executable, engine = metal_capture.diagnostic_engine(GODOT)
    identities = {
        str(p.relative_to(ROOT)): digest(p)
        for p in [
            script,
            library,
            Path(__file__).resolve(),
            Path(metal_capture.__file__),
            ROOT / "godot/assets/cars.json",
        ]
    }
    result = {
        "tool_and_binary_hashes": identities,
        "engine": engine,
        "planned_screenshots": planned_screenshots,
        "maximum_screenshots": MAX_SCREENSHOTS,
        "scope": "Actual race state, frozen after the input plan by default; 4 course-context and 10 isolated views per car. Motion/spin acceptance still uses wheel-audit.",
        "cars": [],
    }
    for car in cars:
        folder = destination / car
        folder.mkdir()
        input_source = (
            ROOT
            / "data/oversteer/scenarios"
            / ("wheel-audit-awd-input.json" if car == "GT4_MITS0001" else "wheel-audit-input.json")
        )
        input_plan = folder / "input-plan.json"
        input_plan.write_bytes(input_source.read_bytes())
        last_input_frame = max(event["frame"] for event in json.loads(input_plan.read_text()))
        freeze_frame = args.freeze_frame if args.freeze_frame is not None else last_input_frame + 2
        if freeze_frame < 1:
            parser.error("--freeze-frame must be positive")
        asset = ROOT / "godot/assets/cars" / f"{car}.glb"
        asset_hash = digest(asset)
        command = [
            str(executable),
            "--path",
            str(ROOT / "godot"),
            "--script",
            str(script),
            "--fixed-fps",
            "60",
            "--",
            "--scenario",
            "driving",
            "--inspection-output",
            str(folder),
            "--save-file",
            str(folder / "save.json"),
            "--settings-dir",
            str(folder / "settings"),
            "--event",
            "oversteer-0-circuit",
            "--car",
            car,
            "--input-events",
            str(input_plan),
            "--frames",
            str(freeze_frame + 60),
            "--freeze-frame",
            str(freeze_frame),
        ]
        if args.smoke:
            command.append("--inspection-smoke")
        if args.metal_capture:
            command.append("--inspection-metal-capture")
        env = background_window.environment(executable)
        if args.metal_capture:
            env["MTL_CAPTURE_ENABLED"] = "1"
        with (folder / "runtime.log").open("w") as log:
            process = subprocess.Popen(
                command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT
            )
            (folder / "process.json").write_text(
                json.dumps(
                    {"pid": process.pid, "command": command, "asset_sha256": asset_hash}, indent=2
                )
                + "\n"
            )
            print(json.dumps({"car": car, "pid": process.pid, "output": str(folder)}), flush=True)
            gpu = None
            deadline = time.monotonic() + 900
            try:
                while process.poll() is None:
                    if (
                        args.metal_capture
                        and gpu is None
                        and (folder / "metal-capture-ready.json").exists()
                    ):
                        gpu = metal_capture.capture_frame(process.pid, folder)
                    if time.monotonic() > deadline:
                        raise subprocess.TimeoutExpired(command, 900)
                    time.sleep(0.1)
                code = process.returncode
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                code = -1
        report_path = folder / "inspection.json"
        report = json.loads(report_path.read_text()) if report_path.exists() else {}
        state_path = folder / "race-state.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {}
        imports = material_import_check(
            asset.read_bytes(),
            state.get("materials", {}).get("surfaces", []),
            state.get("rendered_wheels", []),
            state.get("snapshot", {})
            .get("race", {})
            .get("racers", [{}])[0]
            .get("customization", {})
            .get("finish", "gloss"),
        )
        (folder / "material-import-check.json").write_text(json.dumps(imports, indent=2) + "\n")
        log = (folder / "runtime.log").read_text()
        event_path = folder / "events.jsonl"
        events = (
            [json.loads(line) for line in event_path.read_text().splitlines()]
            if event_path.exists()
            else []
        )
        checks = {
            "process_exit": code == 0,
            "inspection_passed": report.get("passed") is True,
            "focus_guard": "BACKGROUND FOCUS VIOLATION" not in log
            and "Oversteer background window guard installed" in log,
            "no_runtime_errors": not any(
                line.startswith(("ERROR:", "SCRIPT ERROR:")) for line in log.splitlines()
            ),
            "all_images": len(list(folder.glob("view-*.png")))
            == (6 if args.smoke else VIEWS_PER_CAR),
            "no_incidental_images": len(list(folder.rglob("*.png")))
            == (6 if args.smoke else VIEWS_PER_CAR),
            "viewport_1080p": bool(report.get("captures"))
            and all(c["image_size"] == [1920, 1080] for c in report["captures"]),
            "imported_materials_match_source": imports["passed"],
            "frozen_physics_unchanged": report.get("frozen_simulation_unchanged") is True,
            "projected_bounds_centered": bool(report.get("captures"))
            and all(c["camera"]["centered"] for c in report["captures"]),
            "course_views_clear_of_rivals": bool(report.get("captures"))
            and all(c["camera"].get("blocking_rivals") == [] for c in report["captures"]),
            "per_shot_capture_timing": bool(report.get("captures"))
            and all(c["capture_ms"] > 0 for c in report["captures"]),
            "asset_unchanged": digest(asset) == asset_hash,
            "road_mipmaps_and_anisotropy": bool(state.get("rendering", {}).get("road_sampling"))
            and all(
                row["mipmaps"] and row["anisotropic"] for row in state["rendering"]["road_sampling"]
            ),
            "sky_reflections": state.get("rendering", {}).get("sky_present") is True
            and state["rendering"].get("sky_reflections") is True,
            "only_race_assets_preloaded": bool(state.get("loading"))
            and sorted(path for batch in state["loading"] for path in batch["paths"])
            == sorted(
                {
                    f"res://assets/cars/{r['car_id']}.glb"
                    for r in state["snapshot"]["race"]["racers"]
                }
                | {f"res://assets/worlds/{state['snapshot']['race']['track_id']}.glb"}
            ),
            "loading_samples_deduplicated": bool(state.get("loading"))
            and all(
                batch["samples"]
                and all(
                    a["progress"] != b["progress"]
                    for a, b in zip(batch["samples"], batch["samples"][1:])
                )
                for batch in state["loading"]
            ),
        }
        checks.update(capture_contract_checks(report.get("captures", []), events, args.smoke))
        if args.metal_capture:
            checks["metal_capture_completed"] = gpu is not None and gpu["passed"]
        if args.freeze_frame is None:
            checks["full_input_plan_elapsed"] = state.get("input_frame", 0) > last_input_frame
            checks["all_input_events_processed"] = state.get("input_events_processed") == len(
                json.loads(input_plan.read_text())
            )
        result["cars"].append(
            {
                "car": car,
                "checks": checks,
                "asset_sha256": asset_hash,
                "requested_freeze_frame": freeze_frame,
                "last_input_frame": last_input_frame,
                "input_plan_scope": "full"
                if freeze_frame > last_input_frame
                else "explicit partial override",
            }
        )
        print(json.dumps({"car": car, "checks": checks}), flush=True)
        (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
        if not all(checks.values()):
            break
    result["identities_unchanged"] = (
        all(digest(ROOT / p) == value for p, value in identities.items())
        and digest(GODOT) == engine["source_sha256"]
    )
    result["actual_screenshots"] = len(list(destination.rglob("*.png")))
    result["screenshot_budget_passed"] = (
        result["actual_screenshots"] == planned_screenshots
        and result["actual_screenshots"] <= MAX_SCREENSHOTS
    )
    result["passed"] = (
        len(result["cars"]) == len(cars)
        and result["identities_unchanged"]
        and result["screenshot_budget_passed"]
        and all(all(c["checks"].values()) for c in result["cars"])
    )
    (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    cards = []
    for path in sorted(destination.glob("*/view-*.png")):
        source = html.escape(str(path.relative_to(destination)))
        cards.append(
            f'<article><a href="{source}"><img loading="lazy" src="{source}"></a><p>{html.escape(path.parent.name)} · {html.escape(path.stem)} · <a href="{source[:-4]}.json">diagnostics</a></p></article>'
        )
    (destination / "index.html").write_text(
        '<!doctype html><meta charset="utf-8"><title>Oversteer vehicle inspection</title><style>body{background:#111820;color:#eef;font:16px system-ui;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));gap:20px}img{width:100%}a{color:#9dd}article{border:1px solid #345;padding:12px}</style><h1>Oversteer vehicle inspection</h1><p>Three camera axes, multiple lighting conditions. Race views retain the course; isolated views expose occluded surfaces. Each image links to its camera/framing/light diagnostics. Per-car race-state.json contains materials, wheels, physics and recent command/input history. This static sweep does not test driving motion.</p><main>'
        + "".join(cards)
        + "</main>"
    )
    print(destination / "index.html", flush=True)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

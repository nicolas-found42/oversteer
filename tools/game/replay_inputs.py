#!/usr/bin/env python3
"""Translate recorded, host-reachable core controls into actual Godot input events."""

import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def f32(value):
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f32_equal(left, right):
    return struct.pack("<f", left) == struct.pack("<f", right)


def steering(raw):
    raw = f32(raw)
    if abs(raw) <= f32(0.12):
        return 0.0
    difference = f32(abs(raw) - f32(0.12))
    return f32(f32(-math.copysign(1, raw) * difference) / f32(0.88))


def convert(evidence_path, output):
    evidence = json.loads(evidence_path.read_text())
    content_sha256 = evidence.get("replay_content_sha256", evidence.get("content_sha256"))
    if not isinstance(content_sha256, str) or len(content_sha256) != 64:
        raise ValueError("Replay evidence must identify the actual content SHA256")
    nitrous_button = evidence.get("raw_nitrous_button")
    reverse_button = evidence.get("raw_reverse_button")
    if reverse_button is not None and (type(reverse_button) is not int or reverse_button != 3):
        raise ValueError("Recorded reverse button must use the supported default binding 3")
    if nitrous_button is not None and (type(nitrous_button) is not int or nitrous_button != 0):
        raise ValueError("Recorded nitrous button must use the supported default binding 0")
    for record in evidence["files"].values():
        path = ROOT / record["path"]
        if digest(path) != record["sha256"]:
            raise ValueError(f"Recorded evidence identity changed: {path}")
    lineage = list(evidence.get("preceding_playthrough", []))
    if "fresh_profile_initial_save" in evidence:
        lineage.append(evidence["fresh_profile_initial_save"])
    for record in lineage:
        if digest(ROOT / record["path"]) != record["sha256"]:
            raise ValueError(f"Recorded career lineage changed: {record['path']}")
    archive = evidence.get("source_archive")
    if archive:
        archive_root = ROOT / archive["path"]
        archive_manifest = archive_root / "manifest.json"
        if digest(archive_manifest) != archive["manifest_sha256"]:
            raise ValueError("Recorded source archive manifest changed")
        archived = json.loads(archive_manifest.read_text())["files"]
        for relative, expected in archived.items():
            if digest(archive_root / relative) != expected:
                raise ValueError(f"Recorded archived source changed: {relative}")
        if any(
            archived.get(path) != expected
            for path, expected in evidence.get("source_sha256", {}).items()
        ):
            raise ValueError("Recorded source identities disagree with the archive")
    control_path = ROOT / evidence["files"]["controls"]["path"]
    controls = json.loads(control_path.read_text())
    if len(controls) != evidence["tick_count"]:
        raise ValueError("Recorded tick count differs from evidence")
    first = evidence["first_active_tick"]
    active = controls[first:]
    if len(active) != evidence["active_ticks"]:
        raise ValueError("Recorded active tick count differs from evidence")
    events = []
    previous = {}
    for index, record in enumerate(controls):
        if record["tick"] != index:
            raise ValueError("Control ticks must be sequential")
        if index < first:
            if record["active_tick"] is not None or record["countdown_before"] <= 0:
                raise ValueError("Dropped ticks must belong to the actual countdown")
            continue
        frame = index - first
        if record["active_tick"] != frame or record["countdown_before"] != 0:
            raise ValueError("Active tick clock differs from the source record")
        desired = record["input"]
        raw = record["raw_axes"]
        actual = {
            "steering": steering(raw["steering_0"]),
            "throttle": max(0, f32(raw["throttle_5"])),
            "brake": max(0, f32(raw["brake_4"])),
        }
        if any(not f32_equal(actual[key], desired[key]) for key in actual):
            raise ValueError(f"Raw axes do not reproduce the recorded f32 controls at tick {index}")
        if not any(f32_equal(desired["handbrake"], value) for value in [0, 1]):
            raise ValueError("Recorded handbrake is not reachable through the digital binding")
        if not any(f32_equal(desired["nitrous"], value) for value in [0, 1]):
            raise ValueError("Recorded nitrous is not reachable through the digital binding")
        if desired["nitrous"] != 0 and nitrous_button is None:
            raise ValueError("Nitrous replay requires an explicit recorded raw_nitrous_button")
        if (desired["reverse"] and reverse_button is None) or desired["shift"] != 0:
            raise ValueError("This recorded replay requires an unsupported additional binding")
        for name, axis in [("steering_0", 0), ("throttle_5", 5), ("brake_4", 4)]:
            value = raw[name]
            if not math.isfinite(value) or not -1 <= value <= 1:
                raise ValueError("Recorded raw axis is outside the controller range")
            if name not in previous or not f32_equal(previous[name], value):
                events.append({"frame": frame, "joy_axis": {"axis": axis, "value": value}})
                previous[name] = value
        handbrake = bool(desired["handbrake"])
        if previous.get("handbrake") != handbrake:
            events.append(
                {
                    "frame": frame,
                    "joy_button": evidence["raw_handbrake_button"],
                    "pressed": handbrake,
                }
            )
            previous["handbrake"] = handbrake
        nitrous = bool(desired["nitrous"])
        if nitrous_button is not None and previous.get("nitrous") != nitrous:
            events.append(
                {
                    "frame": frame,
                    "joy_button": nitrous_button,
                    "pressed": nitrous,
                }
            )
            previous["nitrous"] = nitrous
        reverse = bool(desired["reverse"])
        if reverse_button is not None and previous.get("reverse") != reverse:
            events.append({"frame": frame, "joy_button": reverse_button, "pressed": reverse})
            previous["reverse"] = reverse
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    outputs = [output, output.with_suffix(".manifest.json")]
    if "grid_driver_bet" in evidence or "ui-plan" in evidence["files"]:
        outputs.append(output.with_suffix(".ui.json"))
    if any(path.exists() for path in outputs):
        raise FileExistsError("Replay output already exists; retain the earlier recording")
    output.write_text(json.dumps(events, indent=2) + "\n")
    manifest = {
        "source_evidence": str(evidence_path.resolve()),
        "source_evidence_sha256": digest(evidence_path),
        "source_controls": str(control_path),
        "source_controls_sha256": digest(control_path),
        "event_plan": str(output),
        "event_plan_sha256": digest(output),
        "event_count": len(events),
        "first_active_tick": first,
        "active_ticks": len(active),
        "event_id": evidence["event_id"],
        "car_id": evidence["car_id"],
        "content_sha256": content_sha256,
        "initial_save": str(ROOT / evidence["files"]["initial-save"]["path"]),
        "initial_save_sha256": evidence["files"]["initial-save"]["sha256"],
        "expected_result": evidence["result"],
        "clock": (
            "Godot --fixed-fps 60. Frame0 preloads controls in countdown; an event at frame k "
            "is polled on active frame k+1. Countdown inputs have no physical effect."
        ),
        "scope": "Input events only; no vehicle state, velocity or score is injected.",
    }
    if "save" in evidence["files"]:
        initial = json.loads(Path(manifest["initial_save"]).read_text())
        final = json.loads((ROOT / evidence["files"]["save"]["path"]).read_text())
        manifest["expected_final_cash"] = final["career"]["cash"]
        manifest["expected_new_transactions"] = final["career"]["transactions"][
            len(initial["career"]["transactions"]) :
        ]
        manifest["expected_final_save"] = evidence["files"]["save"]
    for field in [
        "preceding_playthrough",
        "fresh_profile_initial_save",
        "native_parity_limits",
        "nitrous_observations",
        "runtime_content_sha256",
    ]:
        if field in evidence:
            manifest[field] = evidence[field]
    if "ui-plan" in evidence["files"]:
        ui_plan = output.with_suffix(".ui.json")
        ui_plan.write_bytes((ROOT / evidence["files"]["ui-plan"]["path"]).read_bytes())
        manifest.update(ui_plan=str(ui_plan), ui_plan_sha256=digest(ui_plan))
        if "grid_driver_bet" in evidence:
            manifest["grid_driver_bet"] = evidence["grid_driver_bet"]
    elif "grid_driver_bet" in evidence:
        bet = evidence["grid_driver_bet"]
        steps = [
            ("nav:career", None),
            ("career_events", None),
            ("start", "grid"),
            (f"rival:{bet['racer']}", "rival"),
            ("offer_cash", "counteroffer"),
            ("offer_accept", "accepted"),
            ("grid_launch", "launched"),
        ]
        ui_plan = output.with_suffix(".ui.json")
        ui_plan.write_text(
            json.dumps(
                [
                    {
                        "action": action,
                        "after_frame": 30 + index * 40,
                        **({"capture": capture} if capture else {}),
                    }
                    for index, (action, capture) in enumerate(steps)
                ],
                indent=2,
            )
            + "\n"
        )
        manifest.update(grid_driver_bet=bet, ui_plan=str(ui_plan), ui_plan_sha256=digest(ui_plan))
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    result = convert(options.evidence.resolve(), options.output)
    print(json.dumps({key: result[key] for key in ["event_plan", "event_count", "active_ticks"]}))


if __name__ == "__main__":
    main()

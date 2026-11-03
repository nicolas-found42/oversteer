#!/usr/bin/env python3
"""Run native game scenarios and retain captures, timings and exact build identity."""

import argparse
import hashlib
import html
import json
import math
import platform
import re
import shutil
import struct
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GODOT = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
# Recovered purchase consumers 821C48C0/821C4F00; independent of runtime pricing code.
STARTER_CAR_ID = "GT4_MINI0001"
NATIVE_PAINT_PRICES = {
    "gloss": 3000,
    "metallic": 5000,
    "flake": 12000,
    "pearl": 12000,
    "matt": 7500,
    "thinfilm": 20000,
}


def digest(path):
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def car_capture_diversity_checks(folder, ids):
    """Reject stale/occluded roster captures; pixel differences alone prove no fidelity."""
    fingerprints = {}
    for index, car_id in enumerate(ids):
        for phase in ["before", "after"]:
            for view in ["front", "rear"]:
                path = folder / f"car-{index:02}-{car_id}-{phase}-{view}.png"
                if not path.exists():
                    return {
                        "car_capture_pixels_change_with_view_and_customization": False,
                        "stock_front_captures_distinguish_all_thirty_cars": False,
                    }
                fingerprints[car_id, phase, view] = digest(path)
    return {
        "car_capture_pixels_change_with_view_and_customization": len(ids) == 30
        and all(
            len(
                {
                    fingerprints[car_id, phase, view]
                    for phase in ["before", "after"]
                    for view in ["front", "rear"]
                }
            )
            == 4
            for car_id in ids
        ),
        "stock_front_captures_distinguish_all_thirty_cars": len(ids) == 30
        and len({fingerprints[car_id, "before", "front"] for car_id in ids}) == 30,
    }


def controller_event_values(events):
    # Godot's InputEventJoypadMotion stores float32. JSON report serialization
    # may change a float64 spelling by one ULP while retaining the exact axis.
    from replay_inputs import f32

    return [
        {**event, "joy_axis": {**event["joy_axis"], "value": f32(event["joy_axis"]["value"])}}
        if "joy_axis" in event
        else event
        for event in events
    ]


def input_control_differences(actual, wanted):
    return [
        field
        for field, value in wanted.items()
        if actual.get(field) is None
        or (
            actual[field] != value
            if isinstance(value, bool)
            else struct.pack("<f", actual[field]) != struct.pack("<f", value)
        )
    ]


def ui_control_actions_match(steps, actions):
    if [entry["action"] for entry in actions] != [step["action"] for step in steps]:
        return False
    for step, entry in zip(steps, actions):
        if step["action"].startswith(("avatar_control:", "paint:scalar:")) and "value" in step:
            if entry.get("via") != "visible-HSlider.value_changed":
                return False
            if entry.get("value") != step["value"]:
                return False
        elif entry.get("via") != "visible-enabled-Button.pressed":
            return False
    return True


def equal_f32_state(actual, expected):
    """Compare Rust profile values after Godot and serde's JSON number spellings."""
    if isinstance(expected, dict):
        return (
            isinstance(actual, dict)
            and actual.keys() == expected.keys()
            and all(equal_f32_state(actual[key], value) for key, value in expected.items())
        )
    if isinstance(expected, list):
        return (
            isinstance(actual, list)
            and len(actual) == len(expected)
            and all(equal_f32_state(value, wanted) for value, wanted in zip(actual, expected))
        )
    if isinstance(expected, (int, float)) and not isinstance(expected, bool):
        return (
            isinstance(actual, (int, float))
            and not isinstance(actual, bool)
            and (struct.pack("<f", actual) == struct.pack("<f", expected))
        )
    if isinstance(expected, bool):
        return actual is expected
    return actual == expected


def avatar_render_checks(profile, rendered, catalog):
    components = {item["id"]: item for item in catalog["components"]}
    skins = {item["id"]: item for item in catalog["skins"]}
    selected = [components[item] for item in profile["native_components"].values()]
    wanted = {}
    for component in selected:
        for skin_id in component["skin_ids"]:
            skin = skins[skin_id]
            if skin["gender_tag"] != profile["gender"]:
                continue
            enabled = any(
                skin_id in other["skin_ids"] and other["native_initial_mesh_enabled"]
                for other in selected
            )
            for chunk in skin["mesh_nodes"]:
                wanted[(skin_id, chunk["name"])] = (skin, enabled)
    meshes = rendered.get("meshes", [])
    observed = {(mesh["skin"], mesh["mesh"]): mesh for mesh in meshes}
    exact_chunks = (
        bool(wanted) and len(observed) == len(meshes) and observed.keys() == wanted.keys()
    )
    binds = exact_chunks and all(
        observed[key]["bind_count"] == skin["bone_count"]
        and observed[key]["skeleton_path"] == "../Skeleton3D"
        for key, (skin, _) in wanted.items()
    )
    visibility = exact_chunks and all(
        observed[key]["enabled"] is enabled for key, (_, enabled) in wanted.items()
    )
    morphs = exact_chunks
    morph_count = 0
    for key, (skin, _) in wanted.items():
        if key not in observed:
            continue
        expected = {}
        for attribute in skin["morph_attributes"]:
            name = attribute["name"]
            level = struct.unpack(
                "<f", struct.pack("<f", profile["native_attributes"].get(name, 0))
            )[0]
            scale = struct.unpack(
                "<f", struct.pack("<f", attribute["native_level_to_render_weight"])
            )[0]
            expected[(name, attribute["target_index"])] = level * scale
        actual = {
            (entry["name"], entry["target_index"]): entry["render_weight"]
            for entry in observed[key]["morphs"]
        }
        morph_count += len(expected)
        morphs = (
            morphs
            and len(actual) == len(observed[key]["morphs"])
            and (actual.keys() == expected.keys())
            and all(
                equal_f32_state(actual[attribute], value) for attribute, value in expected.items()
            )
        )
    return {
        "all_selected_source_mesh_chunks_attached": exact_chunks,
        "source_bind_counts_and_shared_skeleton_path": binds,
        "source_hidden_component_flags_applied": visibility,
        "actual_blend_weights_match_source_attributes": morphs and morph_count > 0,
    }


def avatar_ui_checks(report, actions, catalog, relaunch=False):
    presets = {item["id"]: item for item in catalog["native_presets"]["presets"]}
    captured = {
        entry["action"]: entry["capture_substate"]
        for entry in actions
        if "capture_substate" in entry
    }

    def matches_preset(profile, name):
        preset = presets[name]
        return (
            profile["gender"] == preset["gender"]
            and profile["preset"] == name
            and (
                profile["native_components"] == preset["native_components"]
                and equal_f32_state(profile["native_attributes"], preset["native_attributes"])
            )
        )

    profile = report["saved_state"]["profile"]
    checks = {"final_native_female_preset_saved": matches_preset(profile, "FMPreset1")}
    checks.update(avatar_render_checks(profile, report.get("avatar_components", {}), catalog))
    if relaunch:
        state = captured.get("nav:avatar", {})
        checks["reloaded_profile_rendered_on_avatar_screen"] = (
            equal_f32_state(state.get("avatar_profile"), profile)
            and state.get("avatar_category") == "gender"
        )
        checks["reloaded_capture_meshes_binds_visibility_and_morphs"] = all(
            avatar_render_checks(
                state.get("avatar_profile", profile), state.get("avatar_components", {}), catalog
            ).values()
        )
        return checks
    for action, name in [
        ("avatar:gender:M", "MPreset2"),
        ("avatar:native:MPreset1", "MPreset1"),
        ("avatar:gender:F", "FMPreset3"),
        ("avatar:native:FMPreset4", "FMPreset4"),
        ("avatar:native:FMPreset1", "FMPreset1"),
    ]:
        state = captured.get(action, {})
        checks[f"source_preset_{name}_selected"] = "avatar_profile" in state and matches_preset(
            state["avatar_profile"], name
        )
    checks["gender_and_preset_are_separate_phases"] = (
        captured.get("avatar:page:gender", {}).get("avatar_category") == "gender"
        and captured.get("avatar:gender:F", {}).get("avatar_category") == "preset"
    )
    before = captured.get("avatar:page:nose", {}).get("avatar_profile", {})
    after = captured.get("avatar_control:NOSEBIGSLIDER", {}).get("avatar_profile", {})
    expected = {
        **before,
        "native_attributes": {**before.get("native_attributes", {}), "NoseBig": 45.0},
    }
    checks["male_nose_slider_applies_source_0_to_60_ramp_only"] = equal_f32_state(after, expected)
    jeans = captured.get("avatar:component:componentdefs-81a9443b_13", {}).get("avatar_profile", {})
    expected = {
        **after,
        "native_components": {
            **after.get("native_components", {}),
            "bottom": "componentdefs-81a9443b_13",
        },
    }
    checks["jeans_replaces_only_source_bottom_component"] = equal_f32_state(jeans, expected)
    states = [
        state
        for state in captured.values()
        if state.get("avatar_profile", {}).get("native_components")
    ]
    checks["per_step_actual_render_diagnostics_present"] = bool(states) and all(
        "avatar_components" in state for state in states
    )
    checks["per_step_source_meshes_binds_visibility_and_morphs"] = bool(states) and all(
        all(
            avatar_render_checks(
                state["avatar_profile"], state.get("avatar_components", {}), catalog
            ).values()
        )
        for state in states
    )
    final = captured.get("avatar:native:FMPreset1", {}).get("avatar_profile")
    checks["rendered_final_profile_persisted"] = equal_f32_state(final, profile)
    return checks


def native_paint_record_checks(custom, family):
    record = custom.get("native_paint")
    checks = {
        "typed_native_paint_present": isinstance(record, dict),
        "native_paint_raw_bytes_match_typed_fields": False,
        "native_paint_family_matches": False,
        "native_paint_base_matches_visible_color": False,
    }
    if not isinstance(record, dict):
        return checks
    try:
        scalars = [
            record[name]
            for name in [
                "two_tone_exp",
                "min_reflect",
                "max_reflect",
                "flakie",
                "fleck_power",
                "fleck_locality",
                "try_thin_film",
                "film_thickness",
            ]
        ]
        vectors = [record[name] for name in ["base_rgb", "fleck_rgb", "secondary_rgb"]]
        if any(len(vector) != 3 for vector in vectors):
            return checks
        floats = [value for vector in vectors for value in vector] + scalars
        raw = record["raw_be_bytes"]
        checks["native_paint_raw_bytes_match_typed_fields"] = (
            len(raw) == 72
            and all(type(value) is int and 0 <= value <= 255 for value in raw)
            and all(math.isfinite(value) for value in floats)
            and bytes(raw) == struct.pack(">I17f", record["native_type"], *floats)
        )
        checks["native_paint_family_matches"] = (
            record["native_type"] == list(NATIVE_PAINT_PRICES).index(family)
            and custom["finish"] == family
        )
        checks["native_paint_base_matches_visible_color"] = equal_f32_state(
            record["base_rgb"], custom["paint"][:3]
        )
    except (KeyError, ValueError, TypeError, struct.error, OverflowError):
        pass
    return checks


def paint_family_ui_checks(report, steps, actions, family):
    captured = {
        step["capture"]: entry["capture_substate"]
        for step, entry in zip(steps, actions)
        if "capture" in step and "capture_substate" in entry
    }
    required = {"initial", "opened", "selected", "accepted", "cart", "confirmation"}
    checks = {"paint_family_checkpoints_present": required <= captured.keys()}
    if not checks["paint_family_checkpoints_present"]:
        return checks
    initial = captured["initial"]
    quoted = captured["cart"]["cart"]
    price = NATIVE_PAINT_PRICES[family]
    checks["source_family_has_one_exactly_priced_paint_item"] = (
        len(quoted) == 1 and quoted[0]["field"] == "paint" and quoted[0]["cost"] == price
    )
    checks["style_and_color_preview_do_not_charge"] = all(
        state["cash"] == initial["cash"] for name, state in captured.items() if name != "purchased"
    )
    active = [
        entry["substate_after"]
        for entry in actions
        if entry.get("substate_after", {}).get("paint_stage") is not None
    ]
    checks["intermediate_stages_preserve_core_cart_and_customization"] = bool(active) and all(
        state["cart"] == initial["cart"]
        and equal_f32_state(state["customization"], initial["customization"])
        for state in active
    )
    custom = report["saved_state"]["career"]["garage"][STARTER_CAR_ID]
    chart = json.loads((ROOT / "data/juiced2/native-colour-chart.json").read_text())
    expected = [channel / 255 for channel in chart["cells"][173]["rgba"]]
    checks["chosen_source_family_and_color_persisted"] = custom[
        "finish"
    ] == family and equal_f32_state(custom["paint"], expected)
    drafts = [
        state.get("paint_draft")
        for state in captured.values()
        if state.get("paint_stage") is not None
    ]
    checks["all_live_draft_material_records_are_consistent"] = bool(drafts) and all(
        isinstance(draft, dict) and all(native_paint_record_checks(draft, family).values())
        for draft in drafts
    )
    selected_draft = captured["selected"].get("paint_draft") or {}
    checks["source_base_color_previews_before_acceptance"] = equal_f32_state(
        selected_draft.get("paint"), expected
    )
    checks.update(native_paint_record_checks(custom, family))
    checks["accepted_draft_equals_purchased_record"] = equal_f32_state(
        captured["accepted"]["customization"], custom
    )
    stage_count = {"pearl": 3, "flake": 4, "thinfilm": 2}.get(family, 1)
    accepts = [
        entry["substate_after"].get("paint_stage")
        for entry in actions
        if entry["action"] in {"palette_accept", "paint_stage_accept"}
    ]
    checks["source_ordered_stage_accepts"] = len(accepts) == stage_count and all(
        state is None
        if index == stage_count - 1
        else isinstance(state, dict)
        and state.get("family") == family
        and state.get("cursor") == index + 1
        for index, state in enumerate(accepts)
    )
    record = custom.get("native_paint") or {}
    if family in {"pearl", "flake"}:
        field, cell = ("secondary_rgb", 219) if family == "pearl" else ("fleck_rgb", 77)
        color = [channel / 255 for channel in chart["cells"][cell]["rgba"][:3]]
        checks["source_secondary_or_fleck_color_persisted"] = equal_f32_state(
            record.get(field), color
        )
        draft = (
            captured.get("secondary_selected" if family == "pearl" else "fleck_selected", {}).get(
                "paint_draft"
            )
            or {}
        )
        draft_record = draft.get("native_paint") or {}
        checks["source_secondary_or_fleck_preview_preserves_base"] = equal_f32_state(
            draft_record.get(field), color
        ) and equal_f32_state(draft.get("paint"), expected)
    # Chosen binary-exact UI fractions keep the independent double calculation
    # exact until this single f32 rounding, matching the recovered fused setter.
    scalar_values = {
        "pearl": {"two_tone_exp": 0.625},
        "flake": {
            "flakie": 0.25 * 0.699999988079071 + 0.30000001192092896,
            "fleck_power": 0.75 * 48 + 100,
        },
        "thinfilm": {
            "film_thickness": 0.875 * 0.019999999552965164 + 0.005499999970197678,
        },
    }.get(family, {})
    if scalar_values:
        checks["source_fused_scalar_values_persisted"] = all(
            equal_f32_state(record.get(field), value) for field, value in scalar_values.items()
        )
        channels = {"two_tone_exp": 2, "flakie": 4, "fleck_power": 5, "film_thickness": 6}
        checks["source_fused_scalar_values_previewed"] = all(
            equal_f32_state(
                (
                    (captured.get(f"scalar{channels[field]}", {}).get("paint_draft") or {}).get(
                        "native_paint"
                    )
                    or {}
                ).get(field),
                value,
            )
            for field, value in scalar_values.items()
        )
    transactions = report["snapshot"]["career"]["transactions"]
    checks["one_checkout_charges_native_family_price"] = (
        len(transactions) == 1
        and transactions[0]["kind"] == "Customization"
        and transactions[0]["amount"] == -price
        and report["saved_state"]["career"]["cash"] == initial["cash"] - price
        and report["snapshot"]["cart"] == []
    )
    return checks


def paint_cancel_ui_checks(report, steps, actions, family):
    captured = {
        step["capture"]: entry["capture_substate"]
        for step, entry in zip(steps, actions)
        if "capture" in step and "capture_substate" in entry
    }
    required = {"prior", "cancelled", "cart", "purchased"}
    checks = {"paint_cancel_checkpoints_present": required <= captured.keys()}
    if not checks["paint_cancel_checkpoints_present"]:
        return checks
    prior, cancelled = captured["prior"], captured["cancelled"]
    backs = [
        entry["substate_after"]
        for entry in actions
        if entry["action"] in {"paint_stage_cancel", "palette_cancel"}
    ]
    cursors = [1, 0] if family == "pearl" else [2, 1, 0]
    checks["source_back_returns_one_stage_before_exiting_base"] = (
        len(backs) == len(cursors) + 1
        and all(
            isinstance(state.get("paint_stage"), dict)
            and state["paint_stage"].get("family") == family
            and state["paint_stage"].get("cursor") == cursor
            for state, cursor in zip(backs[:-1], cursors)
        )
        and backs[-1].get("paint_stage") is None
    )
    edited = captured.get("scalar2" if family == "pearl" else "scalar5", {})
    checks["source_intermediate_back_preserves_current_draft_and_prior_cart"] = (
        bool(edited.get("paint_draft"))
        and len(backs) == len(cursors) + 1
        and all(
            equal_f32_state(state.get("paint_draft"), edited["paint_draft"])
            and equal_f32_state(state["customization"], prior["customization"])
            and state["cart"] == prior["cart"]
            and state["cash"] == prior["cash"]
            for state in backs[:-1]
        )
    )
    draft = captured.get("selected", {}).get("paint_draft") or {}
    checks["paint_cancel_discards_a_changed_live_draft"] = bool(draft) and not equal_f32_state(
        draft, prior["customization"]
    )
    checks["paint_cancel_restores_entire_prior_proposal"] = (
        equal_f32_state(cancelled["customization"], prior["customization"])
        and cancelled.get("paint_stage") is None
        and cancelled.get("paint_draft") is None
    )
    checks["paint_cancel_preserves_entire_cart_and_cash"] = (
        cancelled["cart"] == prior["cart"]
        and cancelled["cash"] == prior["cash"]
        and captured["cart"]["cart"] == prior["cart"]
    )
    custom = report["saved_state"]["career"]["garage"][STARTER_CAR_ID]
    checks["paint_cancelled_draft_cannot_be_purchased"] = equal_f32_state(
        custom, prior["customization"]
    )
    checks.update(native_paint_record_checks(custom, "matt"))
    transactions = report["snapshot"]["career"]["transactions"]
    checks["paint_cancel_checkout_charges_only_prior_item"] = (
        len(transactions) == 1
        and transactions[0]["kind"] == "Customization"
        and transactions[0]["amount"] == -NATIVE_PAINT_PRICES["matt"]
        and report["saved_state"]["career"]["cash"] == prior["cash"] - NATIVE_PAINT_PRICES["matt"]
        and report["snapshot"]["cart"] == []
    )
    return checks


def paint_repeat_ui_checks(report, steps, actions):
    captured = {
        step["capture"]: entry["capture_substate"]
        for step, entry in zip(steps, actions)
        if "capture" in step and "capture_substate" in entry
    }
    required = {
        "initial",
        "purchased-first",
        "accepted-matt",
        "same-selected",
        "accepted-same",
        "accepted-again",
        "cart",
        "purchased-repeat",
    }
    checks = {"repeated_paint_checkpoints_present": required <= captured.keys()}
    if not checks["repeated_paint_checkpoints_present"]:
        return checks
    first = captured["purchased-first"]
    price = NATIVE_PAINT_PRICES["gloss"]
    checks["first_paint_purchase_charged_once"] = (
        first["cash"] == captured["initial"]["cash"] - price and first["cart"] == []
    )
    checks["identical_material_draft_preserves_prior_cart_until_accepted"] = (
        equal_f32_state(captured["same-selected"].get("paint_draft"), first["customization"])
        and captured["same-selected"]["cart"] == captured["accepted-matt"]["cart"]
        and len(captured["accepted-matt"]["cart"]) == 1
        and captured["accepted-matt"]["cart"][0]["cost"] == NATIVE_PAINT_PRICES["matt"]
    )
    for name in ["accepted-same", "accepted-again", "cart"]:
        state = captured[name]
        checks[f"{name}_keeps_identical_material_and_one_paid_paint"] = (
            equal_f32_state(state["customization"], first["customization"])
            and len(state["cart"]) == 1
            and state["cart"][0]["field"] == "paint"
            and state["cart"][0]["cost"] == price
            and state["cash"] == first["cash"]
        )
    custom = report["saved_state"]["career"]["garage"][STARTER_CAR_ID]
    checks.update(native_paint_record_checks(custom, "gloss"))
    checks["second_paid_acceptance_preserves_all_material_bytes"] = equal_f32_state(
        custom, first["customization"]
    )
    transactions = report["snapshot"]["career"]["transactions"]
    checks["two_checkouts_charge_same_material_twice_without_duplicate_lines"] = (
        len(transactions) == 2
        and all(
            item["kind"] == "Customization" and item["amount"] == -price for item in transactions
        )
        and report["saved_state"]["career"]["cash"] == captured["initial"]["cash"] - 2 * price
        and report["snapshot"]["cart"] == []
    )
    return checks


def runtime_identity(app):
    if app:
        pack = app / "Contents/Resources/Oversteer.pck"
        return {"kind": "exported-resource-pack", "path": str(pack), "sha256": digest(pack)}
    project = ROOT / "godot"
    files = []
    for folder in ["assets", "shaders", ".godot/imported"]:
        files.extend(path for path in (project / folder).rglob("*") if path.is_file())
    files.extend(path for path in project.iterdir() if path.is_file())
    inventory = []
    for path in sorted(set(files)):
        stat = path.stat()
        inventory.append([str(path.relative_to(project)), stat.st_size, stat.st_mtime_ns])
    return {
        "kind": "development-runtime-file-metadata",
        "file_count": len(inventory),
        "metadata_sha256": hashlib.sha256(json.dumps(inventory).encode()).hexdigest(),
        "scope": (
            "Project files, assets, shaders and imported resources; sizes and modification "
            "times, not file-content hashes. Exported PCK receives a content hash."
        ),
    }


def scenarios(suite, content):
    plan = []
    if suite in {"input", "all"}:
        plan.extend(
            {
                "id": f"input-{device}-{direction}",
                "scenario": "driving",
                "event": "native_28956449_001",
                "car": "FOCUS_SVT",
                "frames": 300,
                "input_events": ROOT / f"data/juiced2/scenarios/{device}-{direction}-input.json",
                "intent": direction,
                "device": device,
                "fixed_fps": 60,
            }
            for device in ["keyboard", "controller"]
            for direction in ["left", "right"]
        )
    if suite in {"ui", "all"}:
        plan.extend(
            {
                "id": f"ui-{name}",
                "scenario": "reload",
                "frames": 1200,
                "ui_actions": ROOT / f"data/juiced2/scenarios/{name}-ui.json",
                **(
                    {"event": "native_28956449_001"}
                    if name in {"career-wager", "pink-slip", "spectator"}
                    else {}
                ),
            }
            for name in [
                "career-wager",
                "dealer",
                "cart",
                "pink-slip",
                "spectator",
                "palettes-vinyl",
                "options",
                "body-palette",
                "wheel-palette",
                "vinyl-palette",
                "native-palette",
                "native-avatar",
            ]
        )
        plan.append({"id": "ui-options-relaunch", "scenario": "reload"})
        plan.append(
            {
                "id": "ui-native-avatar-relaunch",
                "scenario": "reload",
                "frames": 180,
                "ui_actions": ROOT / "data/juiced2/scenarios/native-avatar-relaunch-ui.json",
            }
        )
        plan.extend(
            {
                "id": f"ui-native-paint-{family}",
                "scenario": "reload",
                "frames": 900,
                "paint_family": family,
                "ui_actions": ROOT / f"data/juiced2/scenarios/native-paint-{family}-ui.json",
            }
            for family in NATIVE_PAINT_PRICES
        )
        plan.extend(
            {
                "id": f"ui-native-paint-{family}-relaunch",
                "scenario": "reload",
                "frames": 180,
                "paint_relaunch_family": family,
                "ui_actions": ROOT / "data/juiced2/scenarios/native-paint-relaunch-ui.json",
            }
            for family in NATIVE_PAINT_PRICES
        )
        plan.extend(
            {
                "id": f"ui-native-paint-{family}-cancel",
                "scenario": "reload",
                "frames": 900,
                "paint_cancel_family": family,
                "ui_actions": ROOT / f"data/juiced2/scenarios/native-paint-{family}-cancel-ui.json",
            }
            for family in ["pearl", "flake"]
        )
        plan.append(
            {
                "id": "ui-native-paint-repeat",
                "scenario": "reload",
                "frames": 1000,
                "ui_actions": ROOT / "data/juiced2/scenarios/native-paint-repeat-ui.json",
            }
        )
    if suite in {"screens", "all"}:
        plan.extend(
            {"id": name, "scenario": name}
            for name in [
                "title",
                "menu",
                "avatar",
                "career",
                "quick",
                "event",
                "bet",
                "garage",
                "dealer",
                "crew",
                "customization",
                "vinyl",
                "options",
                "credits",
                "pause",
            ]
        )
    if suite in {"driving", "all"}:
        # One normal race for each actual native mode, with its original content.
        modes = {}
        for event in content["events"]:
            modes.setdefault(event["mode"], event)
        plan.extend(
            {"id": f"mode-{mode}", "scenario": "results", "event": event["id"]}
            for mode, event in sorted(modes.items())
        )
        plan.append({"id": "career-race", "scenario": "career-race", "wager": 100})
    if suite in {"all30", "all"}:
        plan.extend(
            [{"id": "all30", "scenario": "all30"}, {"id": "all30-relaunch", "scenario": "reload"}]
        )
    if suite in {"performance", "all"}:
        # Different native environments exercise city, vegetation and bridge content.
        for track in [
            "alps_alps_masterworld1",
            "tokyo_circuit5",
            "downtown_sanfrancisco_masterworld_route1",
        ]:
            event = next(
                (e for e in content["events"] if e["track_id"] == track and e["mode"] == "Circuit"),
                None,
            )
            if event:
                plan.append(
                    {
                        "id": f"benchmark-{track}",
                        "scenario": "benchmark",
                        "event": event["id"],
                        "frames": 2100,
                        "warmup": 300,
                    }
                )
    if suite == "smoke":
        plan = [
            {"id": "menu", "scenario": "menu"},
            {"id": "driving", "scenario": "driving"},
            {"id": "relaunch", "scenario": "reload"},
        ]
    return plan


def isolation_profile(offline=False, independent=False):
    rules = ["(version 1)", "(allow default)"]
    if offline or independent:
        rules.append("(deny network*)")
    if independent:
        rules.append(f"(deny file-read* (subpath {json.dumps(str(ROOT))}))")
    return "".join(rules)


def native_command(app, offline=False, independent=False):
    command = [app / "Contents/MacOS/Oversteer"] if app else [GODOT, "--path", ROOT / "godot"]
    if offline or independent:
        command = [
            "/usr/bin/sandbox-exec",
            "-p",
            isolation_profile(offline, independent),
            *command,
        ]
    return command


def input_intent_checks(report, case):
    replay = report.get("native_input_replay", {})
    samples = {sample["frame"]: sample for sample in replay.get("samples", [])}
    checks = {
        "native_input_replay_completed": replay.get("events_complete") is True,
        "normal_speed_without_autopilot": report.get("simulation_speed") == 1,
        "physical_input_samples_retained": all(
            frame in samples for frame in [119, 125, 175, 179, 245]
        ),
        "correct_input_device": replay.get("virtual_joy_device")
        == (case["device"] == "controller"),
    }
    if not checks["physical_input_samples_retained"]:
        return checks, {}
    sign = 1 if case["intent"] == "right" else -1
    during = [sample for frame, sample in samples.items() if 125 <= frame <= 175]
    checks["requested_steering_polled"] = all(
        abs(sample["controls"]["steering"] + sign) < 1e-6 for sample in during
    )
    if case["device"] == "keyboard":
        checks["requested_physical_key_polled"] = all(
            sample["physical_keys"][case["intent"]] is True
            and sample["physical_keys"]["left" if case["intent"] == "right" else "right"] is False
            for sample in during
        )
    else:
        checks["requested_physical_axis_polled"] = all(
            abs(sample["raw_joy_steering"] - sign) < 1e-6 for sample in during
        )
    checks["steering_released"] = abs(samples[245]["controls"]["steering"]) < 1e-6
    checks["vehicle_moving_before_turn"] = samples[119]["speed_kph"] > 2
    right = samples[119]["camera_right"]
    horizontal_length = math.hypot(right[0], right[2])
    if horizontal_length < 0.1:
        checks["camera_right_measurable"] = False
        return checks, {}
    right = [right[0] / horizontal_length, 0, right[2] / horizontal_length]

    def forward(sample):
        x, y, z, w = sample["rotation"]
        return [2 * (x * z + w * y), 2 * (y * z - w * x), 1 - 2 * (x * x + y * y)]

    before, after = samples[119], samples[179]
    forward_before, forward_after = forward(before), forward(after)
    heading_toward_intent = sign * sum(
        (forward_after[axis] - forward_before[axis]) * right[axis] for axis in range(3)
    )
    displacement_toward_intent = sign * sum(
        (after["position"][axis] - before["position"][axis]) * right[axis] for axis in range(3)
    )
    checks["vehicle_heading_toward_requested_screen_side"] = heading_toward_intent > 0.02
    checks["vehicle_moves_toward_requested_screen_side"] = displacement_toward_intent > 0.05
    return checks, {
        "basis": "Camera right frozen before the turn, projected onto the horizontal plane",
        "before_frame": 119,
        "after_frame": 179,
        "heading_delta_toward_intent": heading_toward_intent,
        "displacement_metres_toward_intent": displacement_toward_intent,
        "camera_right": right,
    }


def run_case(case, destination, app, offline=False, independent=False):
    folder = destination / case["id"]
    folder.mkdir(parents=True, exist_ok=False)
    command = native_command(app, offline, independent)
    if "fixed_fps" in case:
        command.extend(["--fixed-fps", str(case["fixed_fps"])])
    save_file = folder / "save.json"
    if "seed_save" in case:
        shutil.copyfile(case["seed_save"], folder / "initial-save.json")
        shutil.copyfile(case["seed_save"], save_file)
    settings_dir = folder / "settings"
    previous_id = {
        "all30-relaunch": "all30",
        "relaunch": "driving",
        "ui-options-relaunch": "ui-options",
        "ui-native-avatar-relaunch": "ui-native-avatar",
    }.get(case["id"])
    if "paint_relaunch_family" in case:
        previous_id = f"ui-native-paint-{case['paint_relaunch_family']}"
    if previous_id:
        previous = destination / previous_id
        save_file = previous / "save.json"
        settings_dir = previous / "settings"
    command.extend(
        ["--", "--scenario", case["scenario"], "--capture", folder, "--save-file", save_file]
    )
    command.extend(["--settings-dir", settings_dir])
    ui_plan = None
    if "ui_actions" in case:
        ui_plan = folder / "ui-plan.json"
        ui_plan.write_bytes(case["ui_actions"].read_bytes())
        command.extend(["--ui-actions", ui_plan])
    input_plan = None
    replay_manifest = None
    if "input_events" in case:
        input_plan = folder / "input-plan.json"
        input_plan.write_bytes(case["input_events"].read_bytes())
        command.extend(["--input-events", input_plan])
    if "replay_manifest" in case:
        replay_manifest = json.loads(case["replay_manifest"].read_text())
        (folder / "replay-manifest.json").write_bytes(case["replay_manifest"].read_bytes())
        for seed in [folder / "initial-save.json", save_file]:
            if digest(seed) != replay_manifest["initial_save_sha256"]:
                raise ValueError("Source replay initial save changed")
        evidence_copy = folder / "replay-evidence.json"
        shutil.copyfile(Path(replay_manifest["source_evidence"]), evidence_copy)
        if digest(evidence_copy) != replay_manifest["source_evidence_sha256"]:
            raise ValueError("Source replay evidence changed")
        controls_source = Path(replay_manifest["source_controls"])
        controls_copy = folder / "replay-controls.json"
        shutil.copyfile(controls_source, controls_copy)
        if digest(controls_copy) != replay_manifest["source_controls_sha256"]:
            raise ValueError("Source replay controls changed")
        if digest(input_plan) != replay_manifest["event_plan_sha256"]:
            raise ValueError("Source replay events changed")
        if (
            "ui_plan_sha256" in replay_manifest
            and digest(ui_plan) != replay_manifest["ui_plan_sha256"]
        ):
            raise ValueError("Source replay UI plan changed")
    for name in ["event", "car", "wager", "frames", "warmup"]:
        if name in case:
            command.extend([f"--{name}", str(case[name])])
    started = time.monotonic()
    with (folder / "runtime.log").open("w") as log:
        process = subprocess.run(
            [str(x) for x in command],
            cwd=folder if app else ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=900,
        )
    text = (folder / "runtime.log").read_text(errors="replace")
    report_path = folder / "scenario.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else None
    errors = re.findall(r"^.*(?:ERROR:|SCRIPT ERROR:|Shader compilation failed).*$", text, re.M)
    checks = {
        "process_exited": process.returncode == 0,
        "scenario_report": report is not None,
        "no_runtime_errors": not errors,
        "final_capture": (folder / "final.png").exists(),
    }
    if replay_manifest:
        checks.update(recorded_initial_save_identity=True, recorded_evidence_identity=True)
    input_metrics = None
    if report:
        checks.update(
            {
                "thirty_cars": report["content"]["cars"] == 30,
                "thirty_three_routes": report["content"]["tracks"] == 33,
                "native_metal": report["renderer"]["driver"] == "metal",
                "viewport_1080p": report["renderer"]["viewport"] == [1920, 1080],
                "save_roundtrip": report["save_reload_equal"],
                "disk_reload": report["disk_reload_equal"],
                "save_written": report.get("save_status", {}).get("ok") is True,
                "isolated_save": report.get("save_status", {}).get("path") == str(save_file),
                "isolated_options": report.get("settings_path")
                == str(settings_dir / "options.json"),
                "settings_loaded": report.get("settings_status", {}).get("ok") is True,
            }
        )
        if input_plan:
            if "intent" in case:
                input_checks, input_metrics = input_intent_checks(report, case)
                checks.update(input_checks)
            replay = report.get("native_input_replay", {})
            expected_events = json.loads(input_plan.read_text())
            checks["exact_input_plan_executed"] = (
                replay.get("path") == str(input_plan)
                and controller_event_values(replay.get("events", []))
                == controller_event_values(expected_events)
                and replay.get("events_processed") == len(expected_events)
            )
            checks["deterministic_input_clock"] = all(
                abs(sample["delta"] - 1 / case["fixed_fps"]) < 1e-6
                for sample in replay.get("samples", [])
            )
        if replay_manifest:
            replay = report.get("native_input_replay", {})
            source = json.loads((folder / "replay-controls.json").read_text())
            expected = source[replay_manifest["first_active_tick"] :]
            samples = replay.get("samples", [])
            mismatches = []
            for index, sample in enumerate(samples):
                if index >= len(expected):
                    mismatches.append({"frame": sample["frame"], "reason": "extra sample"})
                    break
                wanted = expected[index]["input"]
                actual = sample["controls"]
                different = input_control_differences(actual, wanted)
                if sample["frame"] != index + 1 or different:
                    mismatches.append(
                        {
                            "frame": sample["frame"],
                            "fields": different,
                            "expected": wanted,
                            "actual": actual,
                        }
                    )
                    if len(mismatches) >= 10:
                        break
            (folder / "input-comparison.json").write_text(
                json.dumps(
                    {
                        "expected_active_ticks": len(expected),
                        "actual_samples": len(samples),
                        "first_mismatches": mismatches,
                        "scope": (
                            "Numeric controls compared as packed binary32, including signed zero; "
                            "no state injection"
                        ),
                    },
                    indent=2,
                )
                + "\n"
            )
            result = report["snapshot"].get("result") or {}
            target = replay_manifest["expected_result"]
            initial = json.loads((folder / "initial-save.json").read_text())
            checks.update(
                {
                    "recorded_content_identity": report["content"]["sha256"]
                    == replay_manifest["content_sha256"],
                    "recorded_car_selected": report["snapshot"]["selected_car"]
                    == replay_manifest["car_id"],
                    "recorded_initial_save_loaded": report.get("load_status", {}).get("source")
                    == "primary",
                    "recorded_controls_polled_exactly": len(samples) == len(expected)
                    and not mismatches,
                    "all_replay_events_processed": replay.get("events_complete") is True,
                    "natural_terminal_replay": report.get("input_replay_terminal_success") is True
                    and report["snapshot"]["screen"] in {"Results", "Complete"},
                    "native_event_won": result.get("event_id") == replay_manifest["event_id"]
                    and result.get("won") is True,
                    "recorded_score_reproduced": result.get("score") == target["score"],
                    "recorded_time_reproduced": abs(result.get("time", -1) - target["time"]) < 1e-4,
                    "native_reward_paid": result.get("reward") == target["reward"]
                    and report["saved_state"]["career"]["cash"]
                    == replay_manifest.get(
                        "expected_final_cash",
                        initial["career"]["cash"] + target["reward"] + target.get("wager", 0),
                    )
                    and replay_manifest["event_id"]
                    in report["saved_state"]["career"]["completed_events"],
                    "recorded_net_wager_reproduced": result.get("wager") == target.get("wager", 0),
                }
            )
            if "expected_new_transactions" in replay_manifest:
                checks["recorded_new_transactions_reproduced"] = (
                    report["saved_state"]["career"]["transactions"][
                        len(initial["career"]["transactions"]) :
                    ]
                    == replay_manifest["expected_new_transactions"]
                )
            if "grid_driver_bet" in replay_manifest:
                bet = replay_manifest["grid_driver_bet"]
                accepted = next(
                    (
                        entry
                        for entry in report.get("ui_actions", [])
                        if entry["action"] == "offer_accept"
                    ),
                    {},
                )
                offer = accepted.get("substate_after", {}).get("offer") or {}
                checks["recorded_driver_counteroffer_accepted"] = (
                    offer.get("racer") == bet["racer"]
                    and offer.get("status") == "Accepted"
                    and offer.get("counter_amount") == bet["accepted_counter"]
                )
            if "nitrous_observations" in replay_manifest:
                observed = report.get("native_input_replay", {}).get("nitrous_observations", {})
                expected = replay_manifest["nitrous_observations"]
                checks["every_active_tick_has_a_native_nitrous_observation"] = (
                    observed.get("sampled_ticks") == replay_manifest["active_ticks"]
                )
                checks["recorded_nitrous_request_activation_and_recharge_counts"] = all(
                    observed.get(field) == expected[field]
                    for field in ["requested_ticks", "active_ticks", "recharge_ticks"]
                )
                checks["recorded_minimum_nitrous_fraction_reproduced"] = equal_f32_state(
                    observed.get("minimum_fraction"), expected["minimum_fraction"]
                )
        if case["scenario"] == "benchmark":
            racers = report["snapshot"].get("race", {}).get("racers", [])
            audio = report.get("audio") or {}
            checks.update(
                {
                    "normal_simulation_speed": report["simulation_speed"] == 1,
                    "stable_sample_count": report["measured_frames"] >= 1800,
                    "mean_60fps": report["measured_frame_ms_mean"] <= 1000 / 60,
                    "p95_60fps": report["measured_frame_ms_p95"] <= 1000 / 60,
                    "active_race_at_end": report["snapshot"]["screen"] == "Race",
                    "active_race_sample_start": report.get("sample_first", {}).get("screen")
                    == "Race"
                    and report.get("sample_first", {}).get("countdown") == 0,
                    "active_race_sample_end": report.get("sample_last", {}).get("screen") == "Race"
                    and report.get("sample_last", {}).get("countdown") == 0,
                    "opponents_present": len(racers) >= 2
                    and any(not racer["is_player"] for racer in racers),
                    "engine_audio_playing": audio.get("active_engine_voices", 0) > 0,
                    "music_playing": audio.get("music_playing") is True,
                    "vehicle_effect_nodes_present": len(report.get("effects", [])) == len(racers),
                }
            )
        if case["scenario"] == "all30":
            probes = report.get("all30_probes", [])
            ids = [probe["car_id"] for probe in probes]
            checks["thirty_unique_car_probes"] = len(ids) == len(set(ids)) == 30
            checks.update(car_capture_diversity_checks(folder, ids))
            checks["stock_and_modified_front_rear_captures"] = len(ids) == 30 and all(
                (folder / f"car-{index:02}-{car_id}-{phase}-{view}.png").exists()
                for index, car_id in enumerate(ids)
                for phase in ["before", "after"]
                for view in ["front", "rear"]
            )
            checks["thirty_saved_customizations"] = (
                len(report["saved_state"]["quick_customizations"]) == 30
            )
            checks["requested_customizations_applied"] = len(probes) == 30 and all(
                probe["state_matches_requested"] for probe in probes
            )
            checks["all_thirty_use_consistent_typed_native_paint_records"] = len(
                probes
            ) == 30 and all(
                probe["modified"]["customization"]["finish"] in NATIVE_PAINT_PRICES
                and all(
                    native_paint_record_checks(
                        probe["modified"]["customization"],
                        probe["modified"]["customization"]["finish"],
                    ).values()
                )
                for probe in probes
            )
            checks["all_six_native_paint_families_represented"] = {
                probe["modified"]["customization"]["finish"] for probe in probes
            } == NATIVE_PAINT_PRICES.keys()
            checks["obsolete_nitrous_tier_not_used_as_upgrade_proof"] = len(probes) == 30 and all(
                probe["modified"]["customization"]["nitrous"] == 0 for probe in probes
            )
            checks["unpainted_materials_preserved"] = len(probes) == 30 and all(
                probe["unpainted_factory_state_unchanged"]
                and probe["paint_trim_override_isolation"]
                for probe in probes
            )
            checks["paint_has_actual_shader_instances"] = len(probes) == 30 and all(
                any(
                    surface.get("paint_target") and surface.get("runtime_paint", {}).get("rgba")
                    for surface in probe["modified"]["materials"]["surfaces"]
                )
                for probe in probes
            )
            # These are the existing donor upgrade adapters. Native package
            # installation/eligibility needs separate checks after its source port.
            checks["legacy_four_performance_fields_applied"] = len(probes) == 30 and all(
                probe["modified"]["customization"][part] == 1
                for probe in probes
                for part in ["engine", "transmission", "suspension", "tyres"]
            )
        if previous_id:
            checks["loaded_prior_process_save"] = (
                report.get("load_status", {}).get("source") == "primary"
            )
            previous_report = save_file.parent / "scenario.json"
            if previous_report.exists():
                before = json.loads(previous_report.read_text())
                checks["prior_state_equal"] = report["saved_state"] == before["saved_state"]
        if "ui_actions" in case:
            steps = json.loads(ui_plan.read_text())
            actions = report.get("ui_actions", [])
            checks["all_ui_actions_completed"] = report.get("ui_actions_complete") is True
            checks["actual_control_actions_match"] = ui_control_actions_match(steps, actions)
            checks["all_ui_captures_exist"] = all(
                (folder / f"{step['capture']}.png").exists() for step in steps if "capture" in step
            )
            checks["ui_captures_waited_for_rendered_frames"] = all(
                entry.get("capture_frame", -1) >= entry["frame"] + 3 and "capture_substate" in entry
                for step, entry in zip(steps, actions)
                if "capture" in step
            )
            checks["no_ui_action_errors"] = all(
                entry.get("substate_after", {}).get("error") is None for entry in actions
            )
            if case["id"] in {"ui-native-avatar", "ui-native-avatar-relaunch"}:
                catalog = json.loads((ROOT / "godot/assets/characters/components.json").read_text())
                checks.update(
                    avatar_ui_checks(
                        report, actions, catalog, relaunch=case["id"].endswith("-relaunch")
                    )
                )
            if "paint_family" in case:
                checks.update(paint_family_ui_checks(report, steps, actions, case["paint_family"]))
            if "paint_relaunch_family" in case:
                checks.update(
                    native_paint_record_checks(
                        report["saved_state"]["career"]["garage"][STARTER_CAR_ID],
                        case["paint_relaunch_family"],
                    )
                )
            if "paint_cancel_family" in case:
                checks.update(
                    paint_cancel_ui_checks(report, steps, actions, case["paint_cancel_family"])
                )
            if case["id"] == "ui-native-paint-repeat":
                checks.update(paint_repeat_ui_checks(report, steps, actions))
            if case["id"] in {"ui-body-palette", "ui-wheel-palette", "ui-vinyl-palette"}:
                target = case["id"].removeprefix("ui-").removesuffix("-palette")
                checks["palette_control_activated"] = (
                    bool(actions) and actions[-1]["action"] == f"palette:{target}"
                )
            if case["id"] == "ui-native-palette":
                captured = {
                    step["capture"]: entry["substate_after"]
                    for step, entry in zip(steps, actions)
                    if "capture" in step
                }
                required = {"opened", "preview", "cancelled", "selected", "accepted", "cart"}
                checks["native_palette_checkpoints_present"] = required <= captured.keys()
                if checks["native_palette_checkpoints_present"]:
                    chart = json.loads((ROOT / "data/juiced2/native-colour-chart.json").read_text())

                    def matches_cell(value, index):
                        expected = [channel / 255 for channel in chart["cells"][index]["rgba"]]
                        return (
                            isinstance(value, list)
                            and len(value) == 4
                            and all(
                                abs(actual - wanted) < 1e-6
                                for actual, wanted in zip(value, expected)
                            )
                        )

                    checks["original_chart_cells_previewed"] = matches_cell(
                        captured["preview"]["palette_preview"], 7
                    ) and matches_cell(captured["selected"]["palette_preview"], 173)
                    initial = captured["opened"]
                    cancelled = captured["cancelled"]
                    checks["palette_cancel_restores_without_cart_mutation"] = (
                        cancelled["customization"] == initial["customization"]
                        and cancelled["cart"] == initial["cart"]
                        and cancelled["cash"] == initial["cash"]
                    )
                    checks["preview_does_not_commit"] = (
                        captured["preview"]["cart"] == initial["cart"]
                        and captured["preview"]["cash"] == initial["cash"]
                    )
                    quoted = captured["cart"]["cart"]
                    checks["accepted_one_body_paint_item"] = (
                        len(quoted) == 1 and quoted[0]["field"] == "paint"
                    )
                    transactions = report["snapshot"]["career"]["transactions"]
                    checks["accepted_color_bought_once_at_quote"] = (
                        len(transactions) == 1
                        and transactions[0]["kind"] == "Customization"
                        and transactions[0]["amount"] == -sum(item["cost"] for item in quoted) < 0
                        and matches_cell(
                            report["saved_state"]["career"]["garage"][STARTER_CAR_ID]["paint"],
                            173,
                        )
                    )
            career = report["snapshot"]["career"]
            transactions = career["transactions"]
            if case["id"] == "ui-career-wager":
                race = report["snapshot"].get("race") or {}
                escrows = [t for t in transactions if t["kind"] == "WagerEscrow"]
                checks["accepted_wager_escrowed_once"] = (
                    len(escrows) == 1 and escrows[0]["amount"] == -race.get("wager", 0) < 0
                )
                checks["race_started_through_grid"] = report["snapshot"]["screen"] == "Race"
            elif case["id"] == "ui-dealer":
                checks["buy_and_sell_once"] = [t["kind"] for t in transactions] == [
                    "BuyCar",
                    "SellCar",
                ]
                checks["cancelled_actions_did_not_transact"] = len(transactions) == 2
                checks["only_starter_owned_after_sale"] = list(career["garage"]) == [STARTER_CAR_ID]
            elif case["id"] == "ui-cart":
                custom = career["garage"][STARTER_CAR_ID]
                checks["removed_wheels_stayed_stock"] = custom["wheels"] == "stock"
                checks["paint_and_finish_purchased"] = custom["finish"] == "matt"
                checks["checkout_applied_once"] = (
                    len(transactions) == 1
                    and transactions[0]["kind"] == "Customization"
                    and transactions[0]["amount"] == -NATIVE_PAINT_PRICES["matt"]
                )
            elif case["id"] == "ui-pink-slip":
                race = report["snapshot"].get("race") or {}
                offer = race.get("bet_offer") or {}
                checks["spare_car_purchased_once"] = [t["kind"] for t in transactions] == [
                    "BuyCar"
                ] and len(career["garage"]) == 2
                checks["pink_offer_accepted_for_selected_rival"] = (
                    offer.get("kind") == "PinkSlip"
                    and offer.get("status") == "Accepted"
                    and race.get("bet_racer") == offer.get("racer", 0) > 0
                )
                checks["pink_race_launched"] = report["snapshot"]["screen"] == "Race"
                checks["warning_cancel_and_offer_decline_observed"] = any(
                    entry["action"] == "confirm_no"
                    and entry["substate_before"]["confirmation"] == "pink_offer"
                    and entry["substate_after"]["confirmation"] is None
                    for entry in actions
                ) and any(
                    entry["action"] == "offer_decline"
                    and (entry["substate_after"].get("offer") or {}).get("status") == "Declined"
                    for entry in actions
                )
            elif case["id"] == "ui-spectator":
                race = report["snapshot"].get("race") or {}
                bets = race.get("spectator_bets", [])
                checks["spectator_race_active"] = (
                    race.get("spectating") is True and report["snapshot"]["screen"] == "Race"
                )
                checks["selected_driver_stake_recorded_once"] = (
                    len(bets) == 1
                    and bets[0]["racer"] == 2
                    and bets[0]["stake"] == 1000
                    and bets[0]["odds"] > 0
                    and [t["kind"] for t in transactions] == ["SpectatorStake"]
                    and transactions[0]["amount"] == -1000
                )
                checks["camera_target_changed_through_rival_button"] = (
                    bool(actions) and actions[-1]["substate_after"]["selected_rival"] == 3
                )
            elif case["id"] == "ui-palettes-vinyl":
                custom = career["garage"][STARTER_CAR_ID]
                checks["continuous_body_rgba_persisted"] = all(
                    abs(actual - expected) < 1e-6
                    for actual, expected in zip(custom["paint"], [0.13, 0.42, 0.77, 1], strict=True)
                )
                checks["continuous_wheel_rgba_persisted"] = all(
                    abs(actual - expected) < 1e-6
                    for actual, expected in zip(
                        custom["wheel_paint"], [0.24, 0.51, 0.19, 1], strict=True
                    )
                )
                layers = custom["vinyls"]
                catalog = report.get("customization_catalog", {})
                checks["original_catalog_loaded"] = (
                    catalog.get("native_decals") == 1089 and catalog.get("native_categories") == 84
                )
                checks["native_vinyl_survived_reorder_delete"] = (
                    len(layers) == 1 and layers[0].get("design_id") == "native_d3d1d2b8"
                )
                checks["vinyl_rgba_and_transform_persisted"] = len(layers) == 1 and all(
                    abs(actual - expected) < 1e-6
                    for actual, expected in zip(
                        [
                            *layers[0]["color"],
                            *layers[0]["position"],
                            *layers[0]["scale"],
                            layers[0]["rotation"],
                        ],
                        [0.81, 0.23, 0.54, 0.7, 0.1, 0, 1.1, 0.9, 0.25],
                        strict=True,
                    )
                )
                checkout = next((entry for entry in actions if entry["action"] == "checkout"), {})
                cart = checkout.get("substate_before", {}).get("cart", [])
                checks["palette_checkout_charged_once"] = (
                    bool(cart)
                    and len(transactions) == 1
                    and transactions[0]["kind"] == "Customization"
                    and transactions[0]["amount"] == -sum(item["cost"] for item in cart)
                )
            elif case["id"] == "ui-options":
                settings_path = settings_dir / "options.json"
                preferences = (
                    json.loads(settings_path.read_text()) if settings_path.exists() else {}
                )
                checks["keyboard_binding_saved"] = (
                    preferences.get("keyboard", {}).get("throttle") == 75
                )
                controller = preferences.get("controller", {})
                checks["gamepad_binding_saved"] = (
                    controller.get("buttons", {}).get("nitrous") == 3
                    and controller.get("axes", {}).get("steering") == 2
                )
                checks["conflicting_gamepad_binding_swapped"] = (
                    controller.get("buttons", {}).get("reverse") == 0
                )
                checks["actual_input_events_used_for_binding"] = all(
                    entry.get("input_control", {}).get("via")
                    == "Input.parse_input_event press/release"
                    for entry in actions
                    if entry["action"] in {"bind:throttle", "button:nitrous", "axis:steering"}
                )
                checks["difficulty_quality_units_saved"] = preferences.get("presentation") == {
                    "difficulty": 2,
                    "quality": 2,
                    "mph": False,
                }
                checks["difficulty_and_quality_applied"] = (
                    report["snapshot"].get("difficulty") == 2 and report.get("render_quality") == 2
                )
                checks["audio_gains_saved_and_applied"] = all(
                    abs(preferences.get("audio", {}).get(kind, -1) - value) < 1e-6
                    and abs(report.get("audio", {}).get("volumes", {}).get(kind, -1) - value) < 1e-6
                    for kind, value in [("music", 0.6), ("engine", 0.9)]
                )
        if case["id"] == "ui-options-relaunch":
            previous = json.loads((destination / "ui-options/scenario.json").read_text())
            checks["options_loaded_from_prior_process"] = report.get("settings_status", {}).get(
                "values"
            ) == previous.get("settings_status", {}).get("values")
            checks["difficulty_and_quality_restored"] = (
                report["snapshot"].get("difficulty") == 2 and report.get("render_quality") == 2
            )
            checks["audio_restored"] = report.get("audio", {}).get("volumes") == previous.get(
                "audio", {}
            ).get("volumes")
        if case["scenario"] in {"results", "career-race"}:
            checks["actual_race_finished"] = report["snapshot"]["screen"] in {"Results", "Complete"}
    result = {
        "case": {
            key: str(value) if isinstance(value, Path) else value for key, value in case.items()
        },
        "command": [str(x) for x in command],
        "working_directory": str(folder if app else ROOT),
        "duration_seconds": time.monotonic() - started,
        "exit_code": process.returncode,
        "checks": checks,
        "errors": errors,
        "scenario_json": str(report_path.relative_to(destination)),
        "capture": str((folder / "final.png").relative_to(destination)),
        "status": "passed" if all(checks.values()) else "failed",
        **(
            {"retained_ui_plan": ui_plan.name, "ui_plan_sha256": digest(ui_plan)} if ui_plan else {}
        ),
        **(
            {
                "retained_input_plan": input_plan.name,
                "input_plan_sha256": digest(input_plan),
                "input_intent_measurements": input_metrics,
                "input_clock_policy": (
                    "Godot --fixed-fps 60 supplies a deterministic delta for actual input replay. "
                    "Rendering still executes; this is not wall-clock performance evidence."
                ),
            }
            if input_plan
            else {}
        ),
    }
    print(
        json.dumps(
            {
                "case": case["id"],
                "status": result["status"],
                "failed": [key for key, passed in checks.items() if not passed],
            }
        ),
        flush=True,
    )
    return result


def write_gallery(destination, result):
    esc = html.escape
    body = [
        "<!doctype html><meta charset=utf-8><title>Oversteer native verification</title>",
        "<style>body{background:#10141c;color:#e9eef8;font:16px system-ui;margin:32px}"
        "article{margin:30px 0;padding:20px;background:#1b2432}img{max-width:100%;height:auto}"
        "a{color:#9dc9ff}code{overflow-wrap:anywhere}.failed{color:#ff9c9c}"
        ".roster-pair{display:grid;grid-template-columns:1fr 1fr;gap:12px}"
        "figure{margin:0}figcaption{margin:8px 0}</style>",
        "<h1>Native verification</h1>",
        "<p>Executed captures and measurements. A passing technical scenario alone "
        "does not establish visual parity.</p>",
        f"<p>Binary SHA256: <code>{esc(result['binary_sha256'])}</code></p>",
    ]
    for item in result["cases"]:
        body.append(f"<article><h2>{esc(item['case']['id'])}: {esc(item['status'])}</h2>")
        failures = [key for key, passed in item["checks"].items() if not passed]
        if failures:
            body.append(f"<p class=failed>{esc(', '.join(failures))}</p>")
        body.append(
            f"<a href='{esc(item['scenario_json'])}'>Scenario state and timings</a>"
            f"<p><img loading=lazy src='{esc(item['capture'])}'></p></article>"
        )
        if item["case"]["scenario"] == "all30":
            report = json.loads((destination / item["scenario_json"]).read_text())
            for index, probe in enumerate(report.get("all30_probes", [])):
                car_id = probe["car_id"]
                prefix = f"{item['case']['id']}/car-{index:02}-{car_id}"
                body.append(f"<article><h2>{esc(car_id)}</h2><div class=roster-pair>")
                for phase in ["before", "after"]:
                    for view in ["front", "rear"]:
                        file = f"{prefix}-{phase}-{view}.png"
                        body.append(
                            f"<figure><figcaption>{phase} · {view}</figcaption>"
                            f"<a href='{esc(file)}'><img loading=lazy src='{esc(file)}'>"
                            "</a></figure>"
                        )
                body.append("</div></article>")
    (destination / "index.html").write_text("\n".join(body))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--suite",
        choices=[
            "smoke",
            "screens",
            "driving",
            "performance",
            "all30",
            "ui",
            "input",
            "replay",
            "all",
        ],
        default="smoke",
    )
    parser.add_argument("--app", type=Path)
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Deny network access to each game process using macOS sandbox-exec",
    )
    parser.add_argument(
        "--independent",
        action="store_true",
        help="Deny network and checkout reads; requires an app and output outside the checkout",
    )
    parser.add_argument("--output", type=Path)
    parser.add_argument("--replay-manifest", type=Path)
    parser.add_argument("--case", action="append", help="Run only this named case from the suite")
    options = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = (options.output or ROOT / f"build/verification/{stamp}-{options.suite}").resolve()
    app = options.app.resolve() if options.app else None
    if options.independent and (
        not app or app.is_relative_to(ROOT) or destination.is_relative_to(ROOT)
    ):
        parser.error("--independent requires --app and --output outside the checkout")
    destination.mkdir(parents=True, exist_ok=False)
    library = (
        app / "Contents/Frameworks/liboversteer_godot.dylib"
        if app
        else ROOT / "godot/bin/debug/liboversteer_godot.dylib"
    )
    if app and not library.exists():
        matches = list(app.rglob("liboversteer_godot.dylib"))
        if len(matches) != 1:
            raise RuntimeError(f"Expected exactly one packaged extension; found {matches}")
        library = matches[0]
    content_path = ROOT / "godot/assets/game-content.json"
    content = json.loads(content_path.read_text())
    result = {
        "started_utc": stamp,
        "verification_tools_sha256": {
            str(path.relative_to(ROOT)): digest(path)
            for path in [Path(__file__).resolve(), ROOT / "tools/game/replay_inputs.py"]
        },
        "suite": options.suite,
        "app": str(app) if app else None,
        "network_denied_by_os": options.offline or options.independent,
        "checkout_reads_denied_by_os": options.independent,
        "binary": str(library),
        "binary_sha256": digest(library),
        "content_sha256": digest(content_path),
        "runtime_resources": runtime_identity(app),
        "host": {
            "architecture": platform.machine(),
            "macos": platform.mac_ver()[0],
            "processor": subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True
            ).strip(),
            "memory_bytes": int(
                subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip()
            ),
        },
        "cases": [],
    }
    if options.independent:
        probe = subprocess.run(
            [
                "/usr/bin/sandbox-exec",
                "-p",
                isolation_profile(independent=True),
                "/bin/cat",
                str(ROOT / "README.md"),
            ],
            cwd=destination,
            capture_output=True,
            text=True,
            timeout=10,
        )
        result["checkout_denial_probe"] = {
            "command": ["/bin/cat", str(ROOT / "README.md")],
            "returncode": probe.returncode,
            "stderr": probe.stderr,
            "stdout_empty": not probe.stdout,
        }
        if probe.returncode == 0 or probe.stdout:
            raise RuntimeError("OS isolation did not deny the checkout read probe")
    plan = scenarios(options.suite, content)
    if options.suite == "replay":
        if not options.replay_manifest:
            parser.error("--suite replay requires --replay-manifest")
        manifest = json.loads(options.replay_manifest.read_text())
        plan = [
            {
                "id": "native-career-replay",
                "scenario": "reload",
                "event": manifest["event_id"],
                "car": manifest["car_id"],
                "fixed_fps": 60,
                "frames": manifest["active_ticks"] + 10,
                "seed_save": Path(manifest["initial_save"]),
                "ui_actions": Path(manifest["ui_plan"])
                if "ui_plan" in manifest
                else ROOT / "data/juiced2/scenarios/career-replay-ui.json",
                "input_events": Path(manifest["event_plan"]),
                "replay_manifest": options.replay_manifest.resolve(),
            }
        ]
        if "ui_plan" in manifest and digest(plan[0]["ui_actions"]) != manifest["ui_plan_sha256"]:
            raise ValueError("Recorded replay UI plan changed")
        if "grid_driver_bet" in manifest:
            plan[0]["wager"] = manifest["grid_driver_bet"]["offer_amount"]
    if options.case:
        unknown = set(options.case) - {case["id"] for case in plan}
        if unknown:
            parser.error(f"Unknown cases in {options.suite}: {sorted(unknown)}")
        plan = [case for case in plan if case["id"] in options.case]
    for case in plan:
        result["cases"].append(
            run_case(case, destination, app, options.offline, options.independent)
        )
        (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
        write_gallery(destination, result)
    result["inputs_unchanged"] = (
        digest(library) == result["binary_sha256"]
        and digest(content_path) == result["content_sha256"]
        and runtime_identity(app) == result["runtime_resources"]
    )
    result["verification_tools_unchanged"] = all(
        digest(ROOT / path) == expected
        for path, expected in result["verification_tools_sha256"].items()
    )
    result["passed"] = (
        result["inputs_unchanged"]
        and result["verification_tools_unchanged"]
        and all(x["status"] == "passed" for x in result["cases"])
    )
    (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(destination / "index.html", flush=True)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

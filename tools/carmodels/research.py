"""Turn evidence/proxy records into auditable complete simulation profiles.

Every writable registry key gets a value AND an evidence status. A secondary
compilation, a donor trim, a mesh measurement and a model prior are distinct.
Nothing here upgrades an estimate to a measured vehicle fact.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess

import numpy as np

from tools.carmodels.assets import COMMIT, ROOT, WORK
from tools.carmodels.policy import import_policy
from tools.carmodels.scope import is_included


def registry(path):
    result = {}
    for line in path.read_text().splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        name = cells[0].strip("`")
        low, high = cells[3].split(" .. ")
        result[name] = {
            "default": float(cells[1]),
            "unit": cells[2],
            "min": float(low),
            "max": float(high),
            "derived": cells[6] == "yes",
            "meaning": cells[8],
        }
    if len(result) < 100:
        raise ValueError("incomplete registry export")
    return result


def tyre_sizes(text):
    return [
        (float(a), float(b), float(c))
        for a, b, c in re.findall(
            r"(\d{3})\s*/\s*(\d{2})\s*[A-Z ]*R\s*(\d{2}(?:\.\d+)?)(?![\d.])", text.upper()
        )
    ]


def check_source(source):
    """Reject inconsistent reported fields; retain their original values as evidence."""
    source = {
        **source,
        "values": dict(source["values"]),
        "derived": dict(source.get("derived", {})),
        "rejected_values": [],
    }
    values, derived = source["values"], source["derived"]
    for alias, canonical in [("curbMassKg", "curbWeightKg"), ("driveLayout", "drivetrain")]:
        if values.get(canonical) is None and values.get(alias) is not None:
            values[canonical] = values[alias]
    for key in ["powerKw", "powerRpm", "torqueRpm"]:
        if derived.get(key) is None and values.get(key) is not None:
            derived[key] = values[key]
    if not values.get("drivetrain") and values.get("driveType"):
        values["drivetrain"] = values["driveType"]
    for key in ["cylinders", "torqueNm"]:
        if values.get(key) is None and derived.get(key) is not None:
            values[key] = derived[key]
    hardware = dict(source.get("hardware", {}))
    for key, target in [
        ("gearRatios", "gear_ratios"),
        ("finalDriveRatio", "final_drive"),
        ("finalDrive", "final_drive"),
    ]:
        if key in derived and target not in hardware:
            hardware[target] = derived[key]
    source["hardware"] = hardware
    limits = {
        "lengthMm": (1500, 15000),
        "widthMm": (500, 3500),
        "heightMm": (400, 4500),
        "wheelbaseMm": (500, 10000),
        "curbWeightKg": (100, 30000),
    }
    for key, (low, high) in limits.items():
        value = source["values"].get(key)
        if value is not None and not low <= value <= high:
            source["rejected_values"].append(
                {"key": key, "value": value, "reason": "implausible stated metric magnitude"}
            )
            source["values"][key] = None
    length, wheelbase = (source["values"].get(k) for k in ["lengthMm", "wheelbaseMm"])
    if length and wheelbase and wheelbase >= length:
        source["rejected_values"].append(
            {
                "key": "wheelbaseMm",
                "value": wheelbase,
                "reason": "wheelbase not shorter than overall length",
            }
        )
        source["values"]["wheelbaseMm"] = None
    width = source["values"].get("widthMm") or 1800
    for key in ["frontTrackMm", "rearTrackMm", "groundClearanceMm"]:
        value = source["derived"].get(key)
        low, high = (0, 800) if key == "groundClearanceMm" else (width * 0.5, width * 1.1)
        if value is not None and not low < value < high:
            source["rejected_values"].append(
                {"key": key, "value": value, "reason": "inconsistent clearance/track units"}
            )
            source["derived"][key] = None
    return source


def benchmark_sources(path):
    result = []
    for record in json.loads(path.read_text())["records"]:
        v = record["values"]
        values = {}
        aliases = {
            "lengthMm": ["length_mm"],
            "widthMm": ["width_mm"],
            "heightMm": ["height_mm", "height_softtop_mm"],
            "wheelbaseMm": ["wheelbase_mm"],
            "curbWeightKg": ["kerb_kg", "curb_kg", "curb_estimated_kg", "unladen_kg"],
            "displacementCc": ["engine_cc"],
            "torqueNm": ["torque_Nm", "engine_torque_Nm"],
            "zeroToHundredKmhS": ["zero_100kmh_s", "zero_62mph_s"],
        }
        for name, candidates in aliases.items():
            values[name] = next((v[k] for k in candidates if k in v), None)
        if values["torqueNm"] is None and "torque_lbft" in v:
            values["torqueNm"] = v["torque_lbft"] * 1.3558179483314
        if "top_mph" in v:
            values["topSpeedKmh"] = v["top_mph"] * 1.609344
        power = v.get("power_kW")
        if power is None:
            for name, multiplier in [
                ("power_PS", 0.73549875),
                ("power_bhp", 0.745699872),
                ("engine_bhp", 0.745699872),
                ("power_hp", 0.745699872),
            ]:
                if name in v:
                    power = v[name] * multiplier
                    break
        gears = v.get("gear_ratios")
        if gears:
            values["transmission"] = str(len(gears)) + "-speed"
        elif "gears" in v:
            values["transmission"] = str(v["gears"]) + "-speed"
        derived = {
            "powerKw": power,
            "powerRpm": v.get("power_rpm"),
            "torqueRpm": v.get("torque_rpm"),
            "dragCoefficient": v.get("cd"),
            "frontTrackMm": v.get("track_front_mm"),
            "rearTrackMm": v.get("track_rear_mm"),
        }
        # Preserve conflicting manufacturer values; do not quietly choose one.
        if record["id"] == "r34_2000":
            values["widthMm"] = None
        result.append(
            {
                "id": "benchmark:" + record["id"],
                "sourceUrl": record["source_url"],
                "sourceClass": record.get("evidence_class", "manufacturer"),
                "values": values,
                "derived": derived,
                "rawSpecs": v,
                "hardware": v,
                "notes": record.get("limits", []),
                "qualityFlags": [],
                "vehicle": record["vehicle"],
                "match": record.get("match"),
            }
        )
    return result


def enforce_curve_minimums(rpm, curve, constraints):
    """A complete curve is estimated; reported one-sided limits must still hold."""
    samples = np.linspace(rpm[0], rpm[-1], 1001)
    peak_kw = float(np.max(np.interp(samples, rpm, curve) * samples * 2 * math.pi / 60 / 1000))
    scale = max(
        1.0,
        constraints.get("powerKw", {}).get("lower", 0) * 1.02 / max(peak_kw, 1e-9),
        constraints.get("torqueNm", {}).get("lower", 0) * 1.02 / max(float(max(curve)), 1e-9),
    )
    return curve * scale


def build_profile(identity, match, source, reference, parameters, policy=None, body_feature=None):
    if not is_included(identity):
        raise ValueError("Excluded source cannot generate a profile: " + identity["code"])
    fields = {}
    source_ref = {
        "url": source["sourceUrl"],
        "record": source["id"],
        "pointer": source.get("jsonPointer"),
        "match_kind": match["match_kind"],
    }
    for name, item in parameters.items():
        if item["derived"]:
            continue
        fields[name] = {
            "value": item["default"],
            "unit": item["unit"],
            "status": "model_prior",
            "evidence": "src/dev/dev_params.c; " + item["meaning"],
            "reason": "No vehicle-specific value in selected evidence; retain validated solver/"
            "hardware prior, not a manufacturer measurement.",
            "uncertainty": "unquantified; requires vehicle-specific measurement/calibration",
        }

    def put(key, value, status="estimated", reason="", evidence=None):
        if key not in fields or value is None:
            return
        if not math.isfinite(float(value)):
            raise ValueError("non-finite evidence: " + key)
        fields[key] = {
            "value": float(value),
            "unit": parameters[key]["unit"],
            "status": status,
            "evidence": evidence if evidence is not None else source_ref,
            "reason": reason,
            "uncertainty": "not supplied by source"
            if status in {"reported", "proxy_reported"}
            else "model assumption; not measured",
        }

    status = "reported" if match["match_kind"] == "exact" else "proxy_reported"
    values, derived = source["values"], source.get("derived", {})
    hardware = source.get("hardware", {})
    constraints = source.get("constraints", {})
    length = (
        float(values.get("lengthMm") or (5200 if identity["vehicle_type"] == "truck" else 4300))
        / 1000
    )
    width = float(values.get("widthMm") or 1800) / 1000
    height = (
        float(values["heightMm"]) / 1000
        if values.get("heightMm")
        else (reference["source_bounds"][1][1] - reference["source_bounds"][0][1])
        / reference["width"]
        * width
    )
    wheelbase = float(values["wheelbaseMm"]) / 1000 if values.get("wheelbaseMm") else length * 0.61
    for key, value, raw_key in [
        ("body.wheelbase", wheelbase, "wheelbaseMm"),
        ("body.width_overall", width, "widthMm"),
        ("body.height_overall", height, "heightMm"),
    ]:
        put(
            key,
            value,
            status if values.get(raw_key) else "estimated",
            "Selected source dimensions; proxy identity is explicit. Width measurement convention "
            "and manufacturer rounding may differ from the recovered mesh.",
        )
    if source["id"] == "benchmark:r34_2000" and policy:
        interval = policy["r34_width_interval_mm"]
        if interval:
            width = sum(interval) / 2000
            put(
                "body.width_overall",
                width,
                "estimated",
                "Midpoint of conflicting Nissan English/Japanese manufacturer statements.",
            )
            fields["body.width_overall"]["uncertainty"] = {
                "interval_m": [v / 1000 for v in interval],
                "kind": "source disagreement",
            }
    overhang = max(length - wheelbase, 0.05)
    put(
        "body.front_overhang",
        overhang * 0.48,
        "estimated",
        "Length minus wheelbase split 48:52; no sourced axle-overhang measurement.",
    )
    put(
        "body.rear_overhang",
        overhang * 0.52,
        "estimated",
        "Length minus wheelbase split 48:52; preserves sourced total length.",
    )
    for axle in ["front", "rear"]:
        track = derived.get(axle + "TrackMm")
        put(
            "body.track_" + axle,
            track / 1000 if track else width * 0.87,
            status if track else "estimated",
            "Sourced track or 87% body-width prior.",
        )
        clearance = derived.get("groundClearanceMm")
        put(
            "body.ride_height_" + axle,
            clearance / 1000 if clearance else 0.14,
            status if clearance else "estimated",
            "Ground clearance is a provisional ride-height "
            "proxy; suspension travel is independently unknown.",
        )

    raw = source.get("rawSpecs", {})
    tyres = tyre_sizes(
        " ".join(
            str(v)
            for k, v in {**derived, **raw}.items()
            if "tire" in k.lower() or "tyre" in k.lower()
        )
    )
    for n, axle in enumerate(["front", "rear"]):
        if tyres:
            section, aspect, rim = tyres[min(n, len(tyres) - 1)]
            put("tire.section_width_" + axle, section, status, "Verbatim tire designation, mm.")
            put("tire.aspect_" + axle, aspect, status, "Verbatim tire aspect percentage.")
            put("tire.rim_diameter_" + axle, rim, status, "Verbatim rim diameter in inches.")
            put(
                "tire.rim_width_" + axle,
                section / 25.4 * 0.8,
                "estimated",
                "Rim width prior 80% of section width; not inferred as a measured designation.",
            )
    if source["id"] == "additional:benz1886":
        put("wheel.front_count", 1, "reported", "One centered steered front wheel.")
        put("body.track_front", 0, "derived_from_evidence", "Single front wheel has no separation.")
        put("engine.cylinders", 1, "reported", "Source describes one cylinder.")
        put("drive.reverse", 0, "reported", "Source explicitly reports no reverse gear.")
        for axle in ["front", "rear"]:
            diameter = derived[axle + "WheelDiameterMm"] / 1000
            put("tire.section_width_" + axle, 50, "estimated", "Solid rubber width unknown.")
            put("tire.aspect_" + axle, 50, "estimated", "Equivalent solid-wheel geometry.")
            put("tire.rim_width_" + axle, 1.5, "estimated", "Solid-wheel width prior.")
            put(
                "tire.rim_diameter_" + axle,
                (diameter / 0.97 - 0.05) / 0.0254,
                "estimated",
                "Equivalent designation reproduces reported diameter after solver's 0.97 "
                "loaded-radius factor; not a real pneumatic tire size.",
            )
    drive = str(values.get("drivetrain", ""))
    layout = (
        1
        if drive.startswith("Front") or drive.upper() == "FWD"
        else 2
        if ("All" in drive or "4x4" in drive or drive.upper() in {"AWD", "4WD"})
        else 0
    )
    if source["id"] == "benchmark:prius2004":
        layout = 1
    put(
        "drive.layout",
        layout,
        status if drive else "estimated",
        "Source drive-axle designation; Prius FWD from Toyota technical specification.",
    )
    mass = float(
        values.get("curbWeightKg")
        or derived.get("chassisMassKg")
        or derived.get("sourceMassKg")
        or constraints.get("massKg", {}).get("lower", 0) * 1.05
        or 1200
    )
    if "includes_driver" in " ".join(source.get("qualityFlags", [])):
        mass -= 75
    # Curb evidence excludes the added simulation driver. Fractions are an explicit prior.
    engine_mass, gearbox_mass, fuel_mass = mass * 0.15, max(20, mass * 0.05), max(20, mass * 0.03)
    particle_masses = {
        "engine": engine_mass,
        "gearbox": gearbox_mass,
        "fuel": fuel_mass,
        "chassis": mass - engine_mass - gearbox_mass - fuel_mass,
    }
    for part, x in [
        ("engine", wheelbase * 0.30),
        ("gearbox", wheelbase * 0.12),
        ("fuel", -wheelbase * 0.30),
        ("chassis", -wheelbase * 0.035),
    ]:
        put(
            "mass." + part,
            particle_masses[part],
            "estimated",
            "Particle decomposition prior; four particles sum to the selected aggregate mass "
            "reference (basis retained in source quality flags) or 1200kg fallback. Separate "
            "driver added; an aggregate measurement does not identify individual particles.",
        )
        if "massKg" in constraints:
            fields["mass." + part]["uncertainty"] = {
                "aggregate_mass_constraint": constraints["massKg"],
                "estimate_rule": "Curb reference 5% above reported lower bound; particle "
                "fractions are estimates. No finite upper bound asserted.",
            }
        put("mass." + part + "_x", x, "estimated", "Layout-frame mass-position prior.")
        put("mass." + part + "_z", height * 0.34, "estimated", "CG-height prior 34% of height.")
    put("mass.driver", 75, "estimated", "75 kg test driver added to sourced curb mass.")
    put("mass.driver_x", 0, "estimated", "Driver at axle-midpoint layout origin.")
    put("mass.driver_z", height * 0.40, "estimated", "Driver CG-height prior.")
    if hardware.get("front_mass_fraction"):
        # Constrain the aggregate CG, while keeping individual particle locations estimates.
        target_x = (hardware["front_mass_fraction"] - 0.5) * wheelbase
        other_moment = sum(
            fields["mass." + p]["value"] * fields["mass." + p + "_x"]["value"]
            for p in ["engine", "gearbox", "fuel"]
        )
        chassis_x = (target_x * mass - other_moment) / particle_masses["chassis"]
        put(
            "mass.chassis_x",
            chassis_x,
            "derived_from_evidence",
            "Fit aggregate curb-mass CG to published front mass fraction. Particle "
            "decomposition remains an estimate; added driver changes loaded distribution.",
        )

    torque = values.get("torqueNm")
    power_kw = derived.get("powerKw")
    if power_kw is None and derived.get("powerBhp"):
        power_kw = derived["powerBhp"] * 0.745699872
    if power_kw is None and derived.get("powerPs"):
        power_kw = derived["powerPs"] * 0.73549875
    if power_kw is None and derived.get("powerHp"):
        power_kw = derived["powerHp"] * 0.745699872
    if power_kw is None and "powerKw" in constraints:
        power_kw = constraints["powerKw"]["lower"] * 1.05
    if torque is None and "torqueNm" in constraints:
        torque = constraints["torqueNm"]["lower"] * 1.05
    power_rpm = float(derived.get("powerRpm") or 5500)
    torque_rpm = float(derived.get("torqueRpm") or power_rpm * 0.65)
    if torque is None and power_kw:
        torque = power_kw * 1000 / (2 * math.pi * power_rpm / 60) * 1.15
    torque = float(torque or 220)
    redline = float(
        hardware.get("redline_rpm")
        or hardware.get("max_rpm")
        or max(power_rpm * 1.10, torque_rpm * 1.15, 200)
    )
    idle = min(900.0, redline * 0.2)
    put("engine.idle_rpm", idle, "estimated", "Idle RPM prior; no measured idle supplied.")
    put(
        "engine.redline_rpm",
        redline,
        status if hardware.get("redline_rpm") or hardware.get("max_rpm") else "estimated",
        "Published limit or explicit peak-RPM prior.",
    )
    power_torque = power_kw * 1000 / (2 * math.pi * power_rpm / 60) if power_kw else torque * 0.85
    rpm = np.linspace(idle, redline, 7)
    anchors_x = [idle, max(torque_rpm, idle + 1), max(power_rpm, torque_rpm + 2), redline]
    anchors_y = [torque * 0.50, torque, power_torque, power_torque * 0.72]
    curve = np.interp(rpm, anchors_x, anchors_y)
    if source["id"] == "benchmark:prius2004":
        # 110 bhp is combined system output, NOT 76 bhp ICE + motor peak.
        power_kw = 110 * 0.745699872
        curve = np.minimum(np.full(7, 180.0), power_kw * 1000 / (2 * math.pi * rpm / 60))
    if source["id"] == "benchmark:viper2005" and policy:
        torque = policy["viper_torque_nm"]
        power_kw = policy["viper_power_kw"]
        curve = np.interp(
            rpm,
            anchors_x,
            [
                torque * 0.50,
                torque,
                power_kw * 1000 / (2 * math.pi * power_rpm / 60),
                power_torque * 0.72,
            ],
        )
    # Linear torque interpolation has an interior quadratic power maximum. Bound it,
    # rather than merely capping the seven endpoints and exceeding reported peak power.
    if power_kw:
        samples = np.linspace(idle, redline, 1001)
        peak = float(np.max(np.interp(samples, rpm, curve) * samples * 2 * math.pi / 60 / 1000))
        curve *= min(1, power_kw / peak)
    curve = enforce_curve_minimums(rpm, curve, constraints)
    for n, value in enumerate(curve):
        put(
            "engine.torque_p" + str(n),
            value,
            "estimated",
            "Piecewise-linear seven-point curve constrained by reported peak torque/power RPM; "
            "the full torque curve was not measured.",
        )
        if constraints:
            fields["engine.torque_p" + str(n)]["uncertainty"] = {
                "known_constraints": constraints,
                "estimate_rule": "Start 5% above reported minimum; ensure at least 2% margin "
                "after seven-point curve interpolation. No finite upper bound asserted.",
            }
    put("engine.cylinders", values.get("cylinders"), status, "Reported cylinder count.")
    if str(values.get("fuelType", "")).lower() == "electric":
        put(
            "engine.cylinders",
            0,
            "derived_from_evidence",
            "Battery-electric vehicle has no cylinders.",
        )
        put(
            "engine.displacement",
            0,
            "derived_from_evidence",
            "Battery-electric vehicle has no engine displacement.",
        )
    put(
        "engine.braking_torque",
        min(200, torque * 0.12),
        "estimated",
        "Closed-throttle braking prior 12% of estimated peak torque, not a measured coastdown.",
    )
    cc = values.get("displacementCc")
    put("engine.displacement", cc / 1000 if cc else None, status, "cm³ divided by 1000.")
    gear_match = re.search(r"(\d+)[- ]speed", str(values.get("transmission", "")))
    transmission = str(values.get("transmission", "")).lower()
    continuous = "cvt" in transmission or source["id"] == "benchmark:prius2004"
    gears = 1 if continuous else int(gear_match[1]) if gear_match else 5
    put(
        "drive.gear_count",
        gears,
        status if gear_match else "estimated",
        "Reported gear count. CVT/hybrid/electric behavior requires a separate capability check.",
    )
    for n in range(int(parameters["drive.gear_count"]["max"])):
        ratio = 3.55 * (0.78 / 3.55) ** (n / max(gears - 1, 1)) if n < gears else 0
        put(
            "drive.gear" + str(n + 1),
            ratio,
            "estimated",
            "Geometrically spaced ratio prior; count is sourced separately, ratios are not.",
        )
    if continuous:
        put(
            "drive.continuous",
            1,
            "derived_from_evidence",
            "Equivalent CVT solver; not a planetary hybrid or battery state model.",
        )
        put("drive.gear_count", 1, "estimated", "One forward selector; no physical stepped gears.")
        put("drive.cvt_target_rpm", power_rpm, "estimated", "Peak-power target at full throttle.")
        put("drive.cvt_min_ratio", 0.5, "estimated", "Unknown CVT lower ratio bound.")
        put("drive.cvt_max_ratio", 4.0, "estimated", "Unknown CVT upper ratio bound.")
        if source["id"] == "benchmark:prius2004":
            put(
                "drive.max_wheel_rpm",
                6000 / 4.113,
                "derived_from_evidence",
                "Toyota P112 motor maximum 6000rpm divided by motor-to-axle reduction4.113; "
                "equivalent output limit, never a fixed ICE ratio.",
                {
                    "url": "https://global.toyota/pages/global_toyota/mobility/technology/"
                    "toyota-technical-review/TTR_Vol54-1_E.pdf",
                    "table": "P112",
                },
            )
    for name, key in [
        ("redline_rpm", "engine.redline_rpm"),
        ("max_rpm", "engine.redline_rpm"),
        ("final_drive", "drive.final"),
        ("reverse_ratio", "drive.reverse"),
    ]:
        put(key, hardware.get(name), status, "Published hardware specification.")
    if source["id"] == "additional:benz1886":
        # A single-speed equivalent can use the published speed/RPM constraint.
        # This is explicitly target-informed, not a held-out top-speed prediction.
        wheel_radius = derived["rearWheelDiameterMm"] / 2000
        total_ratio = power_rpm * 2 * math.pi / 60 * wheel_radius / (values["topSpeedKmh"] / 3.6)
        put("drive.gear1", 1, "estimated", "Single-speed equivalent ratio convention.")
        put(
            "drive.final",
            total_ratio,
            "calibrated_estimate",
            "Equivalent total reduction from published engine power RPM, rear wheel diameter "
            "and top speed. Target-informed constraint, not a measured belt ratio or an "
            "independent performance prediction.",
        )
    if hardware.get("gear_ratios"):
        ratios = hardware["gear_ratios"]
        put("drive.gear_count", len(ratios), status, "Count of published forward gear ratios.")
        finals = hardware.get("final_drive_by_gear")
        if finals:
            final = finals[0]
            put(
                "drive.final",
                final,
                "derived_from_evidence",
                "Reference final drive; each published gear's effective ratio is preserved.",
            )
            ratios = [r * f / final for r, f in zip(ratios, finals)]
        for n, ratio in enumerate(ratios):
            put(
                "drive.gear" + str(n + 1),
                ratio,
                "derived_from_evidence" if finals else status,
                "Published gear ratio"
                + (" times its own final/reference final." if finals else "."),
                source.get("hardwareSource", source_ref),
            )
    for axle in ["front", "rear"]:
        spring = hardware.get("spring_" + axle + "_lbin")
        if spring:
            put(
                "susp.wheel_rate_" + axle,
                spring * 175.126835 * 0.75**2,
                "estimated",
                "Published spring rate lb/in converted to N/m times assumed 0.75 motion-ratio "
                "squared; actual motion ratio unknown. Not a handling calibration input.",
            )
        brake = hardware.get("brake_" + axle + "_mm") or hardware.get("brake_rotor_diameter_mm")
        put(
            "brake.disc_radius_" + axle,
            brake / 2000 if brake else None,
            status,
            "Published rotor diameter mm converted to radius m.",
        )
    if derived.get("dragCoefficient"):
        put("body.drag_coefficient", derived["dragCoefficient"], status, "Reported Cd.")

    # Geometry observations are normalized source-shape measurements, scaled to real dimensions.
    profile = reference["profile"]
    mesh_evidence = {
        "commit": COMMIT,
        "code": identity["code"],
        "sha256": reference["sha256"],
        "view": "orthographic top-down",
    }
    put(
        "body.tail_width",
        max(profile[1], 0.02) * width,
        "mesh_scaled",
        "Normalized source silhouette at 1/64 length, scaled to reported width.",
        mesh_evidence,
    )
    put(
        "body.nose_width",
        max(profile[-2], 0.02) * width,
        "mesh_scaled",
        "Normalized source silhouette at 63/64 length, scaled to reported width.",
        mesh_evidence,
    )
    shoulder = int(np.argmax(profile)) / 64
    tail_x = -wheelbase / 2 - overhang * 0.52
    put(
        "body.shoulder_x",
        tail_x + shoulder * length,
        "mesh_scaled",
        "First maximum-width station of source silhouette, mapped to axle-midpoint frame.",
        mesh_evidence,
    )
    put("body.cowl_x", length * 0.12, "estimated", "Cabin package prior, pending measured glass.")
    put("body.backlight_x", -length * 0.18, "estimated", "Cabin package prior.")
    put("body.roof_start_x", length * 0.08, "estimated", "Roof package prior.")
    put("body.roof_end_x", -length * 0.15, "estimated", "Roof package prior.")
    put("body.roof_width", width * 0.60, "estimated", "Roof width prior.")
    if identity["vehicle_type"] == "truck":
        put(
            "body.bed_length",
            0,
            "estimated",
            "Cargo-body type is not established by truck "
            "classification; do not turn enclosed commercial trucks into pickups.",
        )
    if identity["code"] == "F350" and policy and policy["f350_bed"] == "present":
        put(
            "body.bed_length",
            length * 0.38,
            "estimated",
            "Jev bed hypothesis corroborated by "
            "the recovered orthographic cargo tub. Bed length is an estimated fraction.",
        )
    if body_feature and body_feature["open_bed_observed"]:
        bed_length = length * 0.38
        bed_end = tail_x + bed_length
        feature_evidence = {
            **mesh_evidence,
            "inspection": body_feature["inspection"],
            "jev_probability": body_feature["hypothesis_probability"],
            "disagreement": body_feature["disagreement"],
            "resolution": body_feature["resolution"],
        }
        put(
            "body.bed_length",
            bed_length,
            "estimated",
            "Open tub visually corroborated; "
            "length is a 38% body-length prior, not a measured bed dimension.",
            feature_evidence,
        )
        put(
            "body.backlight_x",
            min(length * 0.12 - 0.30, bed_end + 0.10),
            "estimated",
            "Cab ends ahead of estimated pickup bed; glass boundary was not measured.",
            feature_evidence,
        )
        put(
            "body.roof_end_x",
            min(length * 0.08 - 0.20, bed_end + 0.25),
            "estimated",
            "Pickup cab roof package ahead of bed; not a measured roof station.",
            feature_evidence,
        )
    return fields


def load_sources():
    sources = {}
    for path in sorted((WORK / "sources").glob("*specs.jsonl")):
        if path.exists():
            for line in path.read_text().splitlines():
                record = json.loads(line)
                sources[record["id"]] = record
    for record in benchmark_sources(WORK / "benchmarks/summary.json"):
        sources[record["id"]] = record
    if "corrected:ford-focus-svt-2002" in sources:
        sources["corrected:ford-focus-svt-2002"]["hardware"] = sources["benchmark:focus2003"][
            "hardware"
        ]
        sources["corrected:ford-focus-svt-2002"]["hardwareSource"] = sources["benchmark:focus2003"][
            "sourceUrl"
        ]
    constraints_path = WORK / "adopted-constraints.json"
    if constraints_path.exists():
        for source_id, item in json.loads(constraints_path.read_text()).items():
            if source_id not in sources:
                continue
            source = sources[source_id]
            source["constraints"] = item["constraints"]
            source["constraint_judgments"] = item["judgment_hashes"]
            source["rejected_constraint_fields"] = item["rejected_fields"]
            for field, key in [("power_rpm", "powerRpm"), ("torque_rpm", "torqueRpm")]:
                if field in item["rpm"]:
                    existing = source.setdefault("derived", {}).get(key)
                    if existing is not None and existing != item["rpm"][field]:
                        raise ValueError("Conflicting RPM anchors: " + source_id)
                    source["derived"][key] = item["rpm"][field]
    return sources


def apply_calibration(fields, calibration):
    if calibration["held_out_loss"] >= calibration["baseline_loss"]:
        raise ValueError("refuse unsuccessful physics calibration")
    for key, coefficient in zip(calibration["coefficient_keys"], calibration["coefficients"]):
        field = fields[key]
        if field["status"] != "model_prior":
            continue
        base = field["value"]
        field.update(
            value=coefficient if key == "drive.efficiency" else base * coefficient,
            uncalibrated_value=base,
            status="calibrated_prior",
            evidence="data/carmodels/physics-fit.json; production solver experiments",
            reason="Shared prior fitted to published performance targets; no "
            "vehicle-specific hardware measurement is asserted.",
            uncertainty={
                "family_loss_improvement_95ci": calibration["family_improvement_bootstrap_95ci"],
                "vehicle_specific_uncertainty": "unquantified",
            },
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measure", action="store_true")
    args = parser.parse_args()
    policy = import_policy(WORK / "jev-workflow/results.json")
    (WORK / "import-policy.json").write_text(json.dumps(policy, indent=2))
    parameters = registry(WORK / "params.txt")
    identities = json.loads((WORK / "identities.json").read_text())["identities"]
    matches = {
        x["code"]: x for x in json.loads((WORK / "matching/matches.json").read_text())["matches"]
    }
    sources = load_sources()
    feature_path = WORK / "body-features/inspection.json"
    body_features = {r["code"]: r for r in json.loads(feature_path.read_text())}
    calibration_path = ROOT / "data/carmodels/physics-fit.json"
    calibration = json.loads(calibration_path.read_text()) if calibration_path.exists() else None
    references = {
        x["code"]: x for x in json.loads((WORK / "references/measurements.json").read_text())
    }
    profiles = WORK / "profiles"
    profiles.mkdir(exist_ok=True)
    (WORK / "cards").mkdir(exist_ok=True)
    bounds, unresolved, records = [], [], []
    for identity in identities:
        if not is_included(identity):
            continue
        code = identity["code"]
        match = matches[code]
        if match["review_status"] == "needs_review":
            unresolved.append(code)
            continue
        source = check_source(sources[match["sourceId"]])
        fields = build_profile(
            identity, match, source, references[code], parameters, policy, body_features.get(code)
        )
        if calibration:
            apply_calibration(fields, calibration)
        for key, field in fields.items():
            if not parameters[key]["min"] <= field["value"] <= parameters[key]["max"]:
                bounds.append(
                    {
                        "code": code,
                        "key": key,
                        "value": field["value"],
                        "range": [parameters[key]["min"], parameters[key]["max"]],
                    }
                )
        path = profiles / (code + ".txt")
        path.write_text(
            "# oversteer tuning profile v1\n"
            + "\n".join(
                key + " = " + format(field["value"], ".9g") for key, field in fields.items()
            )
            + "\n# carmodels.model = "
            + code
            + "\n"
        )
        records.append(
            {
                "code": code,
                "identity": identity,
                "match": match,
                "source": {
                    k: source.get(k)
                    for k in [
                        "id",
                        "sourceUrl",
                        "sourceClass",
                        "qualityFlags",
                        "rawSpecs",
                        "rejected_values",
                        "constraints",
                        "constraint_judgments",
                        "rejected_constraint_fields",
                    ]
                },
                "fields": fields,
            }
        )
        if args.measure and not any(b["code"] == code for b in bounds):
            subprocess.run(
                [
                    str(ROOT / "build/tests/oversteer_tests"),
                    "--vehicle-card",
                    str(path),
                    str(WORK / "cards" / code),
                ],
                check=True,
            )
            card = json.loads((WORK / "cards" / (code + ".json")).read_text())
            for key, field in fields.items():
                actual = card["parameters"][key]
                if not math.isclose(actual, field["value"], rel_tol=2e-5, abs_tol=2e-5):
                    raise ValueError(
                        f"profile silently changed {code} {key}: {field['value']} -> {actual}"
                    )
    (WORK / "field-research.jsonl").write_text("\n".join(json.dumps(r) for r in records) + "\n")
    (WORK / "coverage.json").write_text(
        json.dumps(
            {
                "source_commit": COMMIT,
                "catalog_entries": len(identities),
                "profiles": len(records),
                "excluded": sum(not is_included(i) for i in identities),
                "unresolved_matches": unresolved,
                "bounds_violations": bounds,
                "writable_keys": sum(not p["derived"] for p in parameters.values()),
                "field_statuses": {
                    status: sum(
                        f["status"] == status for r in records for f in r["fields"].values()
                    )
                    for status in {f["status"] for r in records for f in r["fields"].values()}
                },
            },
            indent=2,
        )
    )
    print(
        json.dumps(
            {
                "profiles": len(records),
                "unresolved": len(unresolved),
                "bounds_violations": len(bounds),
            }
        )
    )
    if bounds or unresolved:
        raise SystemExit("Incomplete or out-of-range research profiles; inspect coverage.json")


if __name__ == "__main__":
    main()

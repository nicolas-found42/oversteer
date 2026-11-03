"""Calibrate shared unknown solver parameters against published performance figures.

Each candidate runs the production solver. Manufacturer-family folds and equal
family weights prevent duplicate cross-game models dominating the assessment.
Reported hardware, geometry, Cd and engine anchors are never overwritten.
"""

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import math
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.research import check_source, load_sources
from tools.carmodels.scope import is_included
from tools.carmodels.validation import family_fold, validation_group

BASELINE = (0.9, 1.0, 1.0)
KEYS = ("drive.efficiency", "tire.long.mu_scale", "body.drag_coefficient")


def profile_text(fields, coefficients=None):
    values = {key: item["value"] for key, item in fields.items()}
    if coefficients:
        for key, coefficient in zip(KEYS, coefficients):
            if fields[key]["status"] not in {"model_prior", "calibrated_prior"}:
                continue
            base = fields[key].get("uncalibrated_value", values[key])
            values[key] = coefficient if key == "drive.efficiency" else base * coefficient
    return "\n".join(f"{key} = {value:.9g}" for key, value in values.items()) + "\n"


def measure(text, binary_hash):
    cache = WORK / "physics/cache"
    cache.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256((binary_hash + text).encode()).hexdigest()
    path = cache / (digest + ".json")
    if path.exists():
        return json.loads(path.read_text())
    with tempfile.TemporaryDirectory(dir=cache) as temporary:
        temporary = Path(temporary)
        profile = temporary / "profile.txt"
        prefix = temporary / "run"
        profile.write_text(text)
        result = subprocess.run(
            [
                str(ROOT / "build/tests/oversteer_tests"),
                "--measure-physics",
                str(profile),
                str(prefix),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            raise ValueError("production physics benchmark failed: " + result.stderr)
        answer = json.loads((temporary / "run_physics.json").read_text())
        completed = temporary / "complete.json"
        completed.write_text(json.dumps(answer))
        completed.replace(path)
    return answer


def target_for(source):
    v = source["values"]
    return {"acceleration_s": v.get("zeroToHundredKmhS"), "top_kmh": v.get("topSpeedKmh")}


def losses(measured, targets):
    result = []
    for actual, target in zip(measured, targets):
        dimensions = []
        if target["acceleration_s"]:
            prediction = actual["zero_to_100_s"] or 120.0
            dimensions.append(math.log(prediction / target["acceleration_s"]) ** 2)
        if target["top_kmh"]:
            dimensions.append(math.log(max(actual["max_120s_kmh"], 1) / target["top_kmh"]) ** 2)
        result.append(sum(dimensions) / len(dimensions))
    return np.array(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fit", action="store_true")
    args = parser.parse_args()
    sources = load_sources()
    rows = [
        row
        for line in (WORK / "field-research.jsonl").read_text().splitlines()
        if is_included((row := json.loads(line))["identity"])
    ]
    binary_hash = hashlib.sha256((ROOT / "build/tests/oversteer_tests").read_bytes()).hexdigest()
    (WORK / "physics").mkdir(exist_ok=True)
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=8)

    def run(records, coefficients):
        return list(
            pool.map(
                lambda row: measure(profile_text(row["fields"], coefficients), binary_hash), records
            )
        )

    try:
        baseline = run(rows, BASELINE)
        (WORK / "physics/baseline.json").write_text(
            json.dumps(
                [{"code": r["code"], **actual} for r, actual in zip(rows, baseline)], indent=2
            )
        )
        eligible, targets, baseline_filtered = [], [], []
        for row, actual in zip(rows, baseline):
            source = check_source(sources[row["source"]["id"]])
            target = target_for(source)
            if not source["values"].get("curbWeightKg"):
                continue
            if target["acceleration_s"] and not 2 <= target["acceleration_s"] <= 60:
                target["acceleration_s"] = None
            if target["top_kmh"] and not 40 <= target["top_kmh"] <= 450:
                target["top_kmh"] = None
            if not any(target.values()):
                continue
            eligible.append(row)
            targets.append(target)
            baseline_filtered.append(actual)
        print(
            json.dumps({"simulated": len(rows), "with_published_targets": len(eligible)}),
            flush=True,
        )
        if not args.fit:
            return
        candidates = list(itertools.product([0.7, 0.8, 0.9], [0.75, 1.0, 1.25], [1.0, 1.15]))
        predictions, candidate_losses = [], []
        for candidate in candidates:
            measured = baseline_filtered if candidate == BASELINE else run(eligible, candidate)
            predictions.append(measured)
            candidate_losses.append(losses(measured, targets))
            print(
                json.dumps(
                    {
                        "candidate": candidate,
                        "mean_log_squared_error": float(np.mean(candidate_losses[-1])),
                    }
                ),
                flush=True,
            )
        errors = np.array(candidate_losses)
        groups = np.array([validation_group(r["identity"]) for r in eligible])
        folds = np.array([family_fold(g) for g in groups])
        weights = np.array([1 / np.sum(groups == g) for g in groups])
        baseline_errors = losses(baseline_filtered, targets)
        held_out = np.empty(len(eligible))
        reports = []
        for fold in range(5):
            train, test = folds != fold, folds == fold
            choice = int(np.argmin(np.average(errors[:, train], axis=1, weights=weights[train])))
            held_out[test] = errors[choice, test]
            reports.append(
                {
                    "fold": fold,
                    "train": int(train.sum()),
                    "test": int(test.sum()),
                    "coefficients": candidates[choice],
                }
            )
        choice = int(np.argmin(np.average(errors, axis=1, weights=weights)))
        improvement = np.array(
            [
                np.mean(baseline_errors[groups == g] - held_out[groups == g])
                for g in sorted(set(groups))
            ]
        )
        rng = np.random.default_rng(20261102)
        bootstrap = rng.choice(improvement, (2000, len(improvement))).mean(axis=1)
        report = {
            "profiles_simulated": len(rows),
            "calibration_entries": len(eligible),
            "training_inputs_sha256": hashlib.sha256(
                "".join(r["code"] + profile_text(r["fields"], BASELINE) for r in rows).encode()
            ).hexdigest(),
            "groups": len(set(groups)),
            "candidate_count": len(candidates),
            "coefficient_keys": KEYS,
            "baseline_coefficients": BASELINE,
            "coefficients": candidates[choice],
            "baseline_loss": float(np.average(baseline_errors, weights=weights)),
            "held_out_loss": float(np.average(held_out, weights=weights)),
            "final_train_loss": float(np.average(errors[choice], weights=weights)),
            "family_improvement_bootstrap_95ci": np.quantile(bootstrap, [0.025, 0.975]).tolist(),
            "folds": reports,
            "binary_sha256": binary_hash,
            "metric": "Mean squared log error of available 0-100s and 120s top-speed "
            "figures, equal weight per manufacturer family.",
            "limitations": [
                "Published figures include secondary compilations and proxies, "
                "not uniform independently measured tests.",
                "120s terminal speed is a bounded protocol, not exact v-max.",
                "Handling hardware remains explicitly unmeasured where absent.",
            ],
        }
        (WORK / "physics/fit.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report, indent=2), flush=True)
        if report["held_out_loss"] >= report["baseline_loss"]:
            raise ValueError("Shared calibration did not improve held-out loss; do not adopt")
    finally:
        pool.shutdown()


if __name__ == "__main__":
    main()

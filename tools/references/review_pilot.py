"""Build a frozen, blind human audit from cached Juiced 2 classifications. No API calls."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import random
import shutil
from pathlib import Path

from jev_catalog_v2 import SCREEN_STATES

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VAULT = ROOT / "artifacts/juiced2-vault"
DEFAULT_OUTPUT = DEFAULT_VAULT / "review-pilot"
OUTCOMES = {"label", "category", "unreadable", "insufficient_context", "not_in_catalog"}
MIN_PRECISION = 0.95
CONFIDENCE = 0.95


def identity(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    encoded = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    with path.open("x") as stream:
        stream.write(encoded)


def seal(pilot):
    pilot["pilot_id"] = identity({k: v for k, v in pilot.items() if k != "pilot_id"})
    return pilot


def make_pilot(assets, predictions, size=200, seed="juiced2-human-pilot-1"):
    lookup = {x["id"]: x for x in predictions}
    if len(lookup) != len(predictions) or len({x["id"] for x in assets}) != len(assets):
        raise ValueError("Duplicate asset or prediction identifier")
    rows = []
    for asset in sorted(assets, key=lambda x: x["id"]):
        prediction = lookup.get(asset["id"], {})
        if prediction.get("status") != "complete":
            raise ValueError("Pilot population requires complete cached predictions")
        if prediction.get("image_sha256") != asset["sha256"]:
            raise ValueError("Prediction image hash mismatch: " + asset["id"])
        if prediction["screen_state"] not in SCREEN_STATES:
            raise ValueError("Prediction is outside the frozen catalog")
        source = asset["source_page"] if asset["kind"] == "press-screenshot" else asset["source_id"]
        rows.append({**asset, "source_key": source, "prediction": prediction})

    # A press gallery is one source. Exact duplicate images also join source groups,
    # preventing a re-used image from leaking across the tuning/heldout boundary.
    parents = {x["source_key"]: x["source_key"] for x in rows}

    def group(key):
        while parents[key] != key:
            parents[key] = parents[parents[key]]
            key = parents[key]
        return key

    hashes = {}
    for row in rows:
        source = row["source_key"]
        if row["sha256"] in hashes:
            left, right = sorted((group(source), group(hashes[row["sha256"]])))
            parents[right] = left
        hashes[row["sha256"]] = source
    unique = {}
    for row in rows:
        unique.setdefault(row["sha256"], row)
    rows = list(unique.values())
    if size < 1 or size > len(rows):
        raise ValueError("Sample size must fit the unique-image population")
    state_counts = collections.Counter(x["prediction"]["screen_state"] for x in rows)
    strata = collections.defaultdict(list)
    for row in rows:
        row["source_group"] = group(row["source_key"])
        row["split"] = (
            "heldout" if int(identity([seed, row["source_group"]])[:8], 16) % 2 else "tuning"
        )
        prediction = row["prediction"]
        stratum = json.dumps(
            [
                row["split"],
                bool(prediction["screen_review"]),
                "rare" if state_counts[prediction["screen_state"]] < 50 else "common",
                row["platform_declared"],
            ],
            separators=(",", ":"),
        )
        strata[stratum].append(row)
    if size < len(strata):
        raise ValueError(f"Need at least {len(strata)} items to cover every sampling stratum")
    keys = sorted(strata)
    quotas = dict.fromkeys(keys, 0)
    # Balanced allocation across split/review/frequency/platform cells. Within a cell,
    # simple random sampling without replacement gives known inclusion probabilities.
    for index in range(size):
        available = [key for key in keys if quotas[key] < len(strata[key])]
        key = min(available, key=lambda k: (quotas[k], identity([seed, index, k])))
        quotas[key] += 1
    chosen, populations = [], []
    for key in keys:
        candidates = strata[key]
        selected = random.Random(identity([seed, key])).sample(candidates, quotas[key])
        populations.append(
            {
                "stratum": key,
                "split": candidates[0]["split"],
                "screen_review": bool(candidates[0]["prediction"]["screen_review"]),
                "size": len(candidates),
                "sample_size": len(selected),
                "states": dict(
                    sorted(
                        collections.Counter(
                            x["prediction"]["screen_state"] for x in candidates
                        ).items()
                    )
                ),
            }
        )
        for row in selected:
            chosen.append(
                {
                    "asset_id": row["id"],
                    "source_group": row["source_group"],
                    "split": row["split"],
                    "stratum": key,
                    "weight": len(candidates) / len(selected),
                    "source_sha256": row["sha256"],
                    "source_path": row["path"],
                    "platform_declared": row["platform_declared"],
                    "screen_state": row["prediction"]["screen_state"],
                    "screen_review": bool(row["prediction"]["screen_review"]),
                    "prediction": row["prediction"],
                }
            )
    chosen.sort(key=lambda x: identity([seed, "display", x["asset_id"]]))
    for index, row in enumerate(chosen, 1):
        row["review_id"] = f"{index:04d}"
        row["image"] = f"images/{index:04d}{Path(row['source_path']).suffix.lower()}"
    return seal(
        {
            "schema_version": 1,
            "seed": seed,
            "population": "unique image hashes; one deterministic representative per hash",
            "population_size": len(rows),
            "rare_definition": "predicted state has fewer than 50 unique images",
            "catalog": dict(sorted(SCREEN_STATES.items())),
            "sources": [
                {"source_key": source, "group": group(source)} for source in sorted(parents)
            ],
            "populations": populations,
            "items": chosen,
        }
    )


def public_data(pilot):
    return {
        "pilot_id": pilot["pilot_id"],
        "items": [{"id": x["review_id"], "image": x["image"]} for x in pilot["items"]],
        "catalog": pilot["catalog"],
    }


def success_lower_count(population, sample, successes, alpha):
    """Exact one-sided hypergeometric lower bound for a fixed finite population."""
    if not successes:
        return 0
    denominator = math.comb(population, sample)

    def tail(total_successes):
        return (
            sum(
                math.comb(total_successes, x) * math.comb(population - total_successes, sample - x)
                for x in range(
                    max(successes, sample - (population - total_successes)),
                    min(sample, total_successes) + 1,
                )
            )
            / denominator
        )

    low, high = successes, population - sample + successes
    while low < high:
        middle = (low + high) // 2
        if tail(middle) >= alpha:
            high = middle
        else:
            low = middle + 1
    return low


def evaluate(pilot, annotations):
    expected = identity({k: v for k, v in pilot.items() if k != "pilot_id"})
    if pilot["pilot_id"] != expected:
        raise ValueError("Manifest identity changed")
    if annotations.get("pilot_id") != pilot["pilot_id"]:
        raise ValueError("Annotations belong to another pilot")
    answers = annotations.get("answers", {})
    by_id = {x["review_id"]: x for x in pilot["items"]}
    if not isinstance(answers, dict) or set(answers) - set(by_id):
        raise ValueError("Unknown review identifier")
    category_paths = {
        "/".join(parts[:level])
        for label in pilot["catalog"]
        for parts in [label.split("/")]
        for level in range(1, len(parts))
    }
    for answer in answers.values():
        if answer.get("outcome") not in OUTCOMES:
            raise ValueError("Unknown annotation outcome")
        if answer["outcome"] == "label" and answer.get("label") not in pilot["catalog"]:
            raise ValueError("Unknown gold label")
        if answer["outcome"] == "category" and answer.get("label") not in category_paths:
            raise ValueError("Unknown broad category")
        if answer["outcome"] not in {"label", "category"} and answer.get("label"):
            raise ValueError("Unresolved answers cannot carry a gold label")
    complete = len(answers) == len(by_id)
    categories = {}
    for state in pilot["catalog"]:
        cells = [
            cell
            for cell in pilot["populations"]
            if cell["split"] == "heldout" and not cell["screen_review"] and state in cell["states"]
        ]
        lower = 0
        auto_n = auto_correct = auto_unresolved = 0
        weighted_auto = weighted_correct = 0
        for cell in cells:
            items = [
                x
                for x in pilot["items"]
                if x["stratum"] == cell["stratum"] and x["screen_state"] == state
            ]
            successes = 0
            for item in items:
                answer = answers.get(item["review_id"])
                auto_n += 1
                correct = bool(answer and answer["outcome"] == "label" and answer["label"] == state)
                successes += correct
                auto_correct += correct
                auto_unresolved += bool(answer and answer["outcome"] != "label")
                weighted_auto += item["weight"]
                weighted_correct += item["weight"] * correct
            # Conditional on the number of this predicted category sampled in a cell,
            # those examples remain a uniform sample without replacement. Bonferroni
            # covers all cells for this category. No iid-frame assumption is required.
            lower += success_lower_count(
                cell["states"][state], len(items), successes, (1 - CONFIDENCE) / len(cells)
            )
        total = sum(cell["states"][state] for cell in cells)
        bound = lower / total if total else None
        metrics = {}
        for split in ("tuning", "heldout"):
            predicted = gold = true_positive = unresolved = 0
            sample_predicted = sample_gold = sample_correct = sample_unresolved = 0
            for item in pilot["items"]:
                if item["split"] != split:
                    continue
                answer = answers.get(item["review_id"])
                is_prediction = item["screen_state"] == state
                is_gold = bool(answer and answer["outcome"] == "label" and answer["label"] == state)
                is_unresolved = bool(is_prediction and answer and answer["outcome"] != "label")
                sample_predicted += is_prediction
                sample_gold += is_gold
                sample_correct += is_prediction and is_gold
                sample_unresolved += is_unresolved
                predicted += item["weight"] * is_prediction
                gold += item["weight"] * is_gold
                true_positive += item["weight"] * (is_prediction and is_gold)
                unresolved += item["weight"] * is_unresolved
            metrics[split] = {
                "sample_predicted": sample_predicted,
                "sample_gold": sample_gold,
                "sample_correct": sample_correct,
                "sample_unresolved": sample_unresolved,
                "precision_estimate": true_positive / predicted if complete and predicted else None,
                "recall_estimate_among_resolved": true_positive / gold
                if complete and gold
                else None,
                "unresolved_predicted_weight": unresolved,
                "unresolved_rate": unresolved / predicted if complete and predicted else None,
            }
        tuning_present = any(
            c["split"] == "tuning" and state in c["states"] for c in pilot["populations"]
        )
        categories[state] = {
            **metrics,
            "heldout_auto_population": total,
            "heldout_auto_sample": auto_n,
            "heldout_auto_sample_correct": auto_correct,
            "heldout_auto_sample_unresolved": auto_unresolved,
            "heldout_auto_precision_estimate": (
                weighted_correct / weighted_auto if complete and weighted_auto else None
            ),
            "heldout_auto_precision_lower_95": bound,
            "eligible": bool(
                complete and tuning_present and bound is not None and bound >= MIN_PRECISION
            ),
        }
    return {
        "schema_version": 1,
        "pilot_id": pilot["pilot_id"],
        "annotation_sha256": identity(annotations),
        "reviewer": annotations.get("reviewer", ""),
        "answered": len(answers),
        "missing_annotations": len(by_id) - len(answers),
        "unresolved_annotations": sum(x["outcome"] != "label" for x in answers.values()),
        "broad_category_annotations": sum(x["outcome"] == "category" for x in answers.values()),
        "automatic_acceptance_enabled": False,
        "scope": "Frozen unique-image corpus; eligibility is diagnostic, no production flags change.",
        "interval_method": "Exact finite-population hypergeometric; one-sided 95%; Bonferroni across category cells.",
        "limits": [
            "Not an accuracy guarantee for future sources or gameplay mechanics.",
            "Source-disjoint splits prevent tuning/heldout leakage, not all semantic similarity.",
            "Sampling without replacement handles dependence within this fixed corpus by design.",
            "Precision includes unresolved and missing answers as non-successes; incomplete pilots cannot qualify.",
            "Recall is a weighted estimate among resolved gold labels, not full-corpus recall.",
            "Broad category answers retain the chosen path but are not exact-label successes.",
            "Declared platform metadata is not independent platform verification.",
            "The 200-example pilot may leave every category ineligible.",
        ],
        "categories": categories,
    }


def build(vault, output, size, seed):
    if output.exists():
        raise ValueError("Output already exists; use a new path to preserve frozen reviews")
    assets_path = vault / "assets.json"
    predictions_path = vault / "judgments/classifications.json"
    pilot = make_pilot(
        json.loads(assets_path.read_text()), json.loads(predictions_path.read_text()), size, seed
    )
    pilot["inputs"] = {
        "assets_sha256": file_hash(assets_path),
        "classifications_sha256": file_hash(predictions_path),
    }
    coverage_path = ROOT / "data/juiced2/reference-coverage.json"
    coverage = json.loads(coverage_path.read_text())
    pilot["inputs"]["coverage_sha256"] = file_hash(coverage_path)
    seal(pilot)
    # Verify all selected bytes before creating any output.
    for item in pilot["items"]:
        if file_hash(vault / item["source_path"]) != item["source_sha256"]:
            raise ValueError("Selected image hash mismatch: " + item["asset_id"])
    output.mkdir(parents=True)
    (output / "images").mkdir()
    for item in pilot["items"]:
        shutil.copyfile(vault / item["source_path"], output / item["image"])
    verify_images(pilot, output)
    write_json(output / "audit-manifest.json", pilot)
    data = json.dumps(public_data(pilot), ensure_ascii=False).replace("<", "\\u003c")
    template = Path(__file__).with_name("review_pilot.html").read_text()
    (output / "index.html").write_text(template.replace("__PILOT_DATA__", data))
    write_json(output / "claim-evidence.json", evidence_ledger(coverage, pilot["pilot_id"]))
    return {
        "pilot_id": pilot["pilot_id"],
        "examples": len(pilot["items"]),
        "review_page": str(output / "index.html"),
    }


def verify_images(pilot, directory):
    for item in pilot["items"]:
        if file_hash(directory / item["image"]) != item["source_sha256"]:
            raise ValueError("Review image hash changed: " + item["review_id"])


def evidence_ledger(coverage, pilot_id):
    return {
        "schema_version": 1,
        "pilot_id": pilot_id,
        "benchmark_status": "awaiting independent human adjudication",
        "inventory_complete": False,
        "temporal_rules_verified_by_this_pilot": False,
        "authorization": {
            "current_record": "docs/design/JUICED2_REBUILD_INTERVIEW.md#current-execution-authorization",
            "historical_pending_records": "artifacts/juiced2-vault/judgments/interview-round-0*.json",
            "policy": "Historical records remain intact; later authorization does not establish fidelity.",
        },
        "release_checks": [
            {"claim": claim, "status": "unverified-in-this-audit", "evidence": []}
            for claim in [
                "Source-linked single-player screen and state coverage",
                "Matched original and reconstruction scene captures",
                "Repeatable driving, race, and complete career scenarios",
                "Customization checks for every vehicle in the initial roster",
                "Progress and customization survive save and relaunch",
                "1080p at 60 FPS on the agreed M5 Pro target",
            ]
        ],
        "state_candidates": [
            {
                "state": row["state"],
                "status": "classifier-lead-only",
                "leads": row["reference_leads"],
                "verified_evidence": [],
                "transition_inventory_status": "not-audited",
                "transitions": [],
            }
            for row in coverage["states"]
            if row["scope"] == "single-player-review-candidate"
        ],
        "requirements": [
            "Verify declared PS3/Xbox 360 provenance before using an acceptance reference.",
            "PC is supplemental; PS2/PSP cannot supply acceptance references.",
            "A temporal claim needs preconditions, visible inputs/actions, timestamped transitions and outcomes.",
            "Hidden rules require traced native logic or controlled original-game experiments.",
            "Record applicable failure, cancellation, retry, loss and save/reload transitions; do not assume them.",
            "Distinguish observed, statically recovered, estimated, contradicted and unresolved claims.",
            "Add matched implementation checks before marking a fidelity claim verified.",
            "Candidates and empty lists never establish exhaustive coverage or absence of a feature.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    create.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    create.add_argument("--size", type=int, default=200)
    create.add_argument("--seed", default="juiced2-human-pilot-1")
    score = commands.add_parser("score")
    score.add_argument("annotations", type=Path)
    score.add_argument("--manifest", type=Path, default=DEFAULT_OUTPUT / "audit-manifest.json")
    score.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "build":
        result = build(args.vault, args.output, args.size, args.seed)
    else:
        pilot = json.loads(args.manifest.read_text())
        verify_images(pilot, args.manifest.parent)
        report = evaluate(pilot, json.loads(args.annotations.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_json(args.output, report)
        result = {
            "report": str(args.output),
            "answered": report["answered"],
            "missing": report["missing_annotations"],
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

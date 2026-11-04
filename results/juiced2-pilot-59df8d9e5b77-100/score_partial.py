"""Validate and describe the saved subset without changing the frozen acceptance gate."""

import collections
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/references"))
import review_pilot  # noqa: E402

SOURCE = ROOT / "results/juiced2-annotations-59df8d9e5b77.json"
MANIFEST = ROOT / "artifacts/juiced2-vault/review-pilot/audit-manifest.json"
OUTPUT = Path(__file__).parent


def load_unique(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(), object_pairs_hook=pairs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def describe(rows):
    exact = [x for x in rows if x["human_outcome"] == "label"]
    broad = [x for x in rows if x["human_outcome"] == "category"]
    correct = sum(x["comparison"] == "exact_match" for x in exact)
    compatible = sum(x["comparison"] == "broad_compatible" for x in broad)
    return {
        "saved_answers": len(rows),
        "outcomes": dict(sorted(collections.Counter(x["human_outcome"] for x in rows).items())),
        "exact_label_comparisons": len(exact),
        "exact_label_matches": correct,
        "exact_label_disagreements": len(exact) - correct,
        "exact_label_agreement": correct / len(exact) if exact else None,
        "broad_category_comparisons": len(broad),
        "broad_category_compatible": compatible,
        "broad_category_disagreements": len(broad) - compatible,
        "broad_category_compatibility": compatible / len(broad) if broad else None,
        "uncertainty_or_no_label": len(rows) - len(exact) - len(broad),
    }


def main():
    original_digest = digest(SOURCE)
    answers = load_unique(SOURCE)
    pilot = load_unique(MANIFEST)
    assert answers["schema_version"] == pilot["schema_version"] == 1
    assert isinstance(answers.get("reviewer", ""), str)
    assert type(answers["position"]) is int and 0 <= answers["position"] < len(pilot["items"])
    review_pilot.verify_images(pilot, MANIFEST.parent)
    official = review_pilot.evaluate(pilot, answers)
    saved_official = load_unique(OUTPUT / "official-evaluation.json")
    assert official == saved_official, "Official CLI output does not match the supplied inputs"
    items = {x["review_id"]: x for x in pilot["items"]}
    assert len(items) == len(pilot["items"]) == 200
    assert len({x["source_sha256"] for x in items.values()}) == 200
    groups = collections.defaultdict(set)
    for item in items.values():
        groups[item["source_group"]].add(item["split"])
    assert all(len(splits) == 1 for splits in groups.values())
    rows = []
    for key, answer in sorted(answers["answers"].items()):
        assert isinstance(answer["notes"], str)
        timestamp = datetime.datetime.fromisoformat(answer["updated_at"].replace("Z", "+00:00"))
        assert timestamp.utcoffset() is not None
        item = items[key]
        predicted, label, outcome = item["screen_state"], answer["label"], answer["outcome"]
        if outcome == "label":
            comparison = "exact_match" if label == predicted else "exact_disagreement"
        elif outcome == "category":
            comparison = (
                "broad_compatible" if predicted.startswith(label + "/") else "broad_disagreement"
            )
        else:
            comparison = "unresolved"
        rows.append(
            {
                "review_id": key,
                "asset_id": item["asset_id"],
                "image": str(MANIFEST.parent / item["image"]),
                "image_sha256": item["source_sha256"],
                "split": item["split"],
                "platform_declared": item["platform_declared"],
                "classifier_review_flag": item["screen_review"],
                "classifier_prediction": predicted,
                "human_outcome": outcome,
                "human_label_or_category": label,
                "human_notes": answer["notes"],
                "updated_at": answer["updated_at"],
                "comparison": comparison,
            }
        )
    summary = describe(rows)
    missing = sorted(set(items) - set(answers["answers"]))
    # Independent reconciliation against the existing evaluator's leaf confusion counts.
    assert summary["exact_label_matches"] == sum(
        x[s]["sample_correct"]
        for x in official["categories"].values()
        for s in ("tuning", "heldout")
    )
    assert summary["exact_label_comparisons"] == sum(
        x[s]["sample_gold"] for x in official["categories"].values() for s in ("tuning", "heldout")
    )
    assert len(rows) == official["answered"]
    assert len(missing) == official["missing_annotations"]
    assert summary["broad_category_comparisons"] == official["broad_category_annotations"]
    assert (
        summary["uncertainty_or_no_label"] + summary["broad_category_comparisons"]
        == official["unresolved_annotations"]
    )
    assert not any(x["eligible"] for x in official["categories"].values())
    assert official["automatic_acceptance_enabled"] is False
    provenance = {
        "annotations": str(SOURCE),
        "annotations_file_sha256": original_digest,
        "annotations_content_sha256": official["annotation_sha256"],
        "manifest": str(MANIFEST),
        "manifest_file_sha256": digest(MANIFEST),
        "pilot_id": pilot["pilot_id"],
        "scorer_sha256": digest(Path(review_pilot.__file__)),
    }
    validation = {
        "status": "valid_partial_export",
        "checks_passed": [
            "JSON parses without duplicate keys",
            "schema and position valid",
            "frozen manifest and pilot identities match",
            "all 200 image hashes verified",
            "all saved review IDs and exact/parent labels valid",
            "notes and timezone-aware timestamps valid",
            "no duplicate selected image hashes",
            "source groups do not cross tuning/heldout splits",
            "official scorer output independently reconciled against saved answer counts",
        ],
        "saved_answers": len(rows),
        "pilot_examples": len(items),
        "missing_annotations": len(missing),
        "missing_review_ids": missing,
        "qualifications": [
            "The export saves examples 0002 through 0100; example 0001 is not saved.",
            "Human annotations are the reference for agreement; their pixel-level truth "
            "was not independently re-adjudicated.",
        ],
        "provenance": provenance,
    }
    report = {
        "status": "descriptive_partial_pilot_scores",
        "scope": "Unweighted comparisons within the 99 saved answers only, "
        "not corpus accuracy or full-pilot precision/recall estimates.",
        "summary": summary,
        "by_split": {
            split: describe([x for x in rows if x["split"] == split])
            for split in ("tuning", "heldout")
        },
        "by_classifier_review_flag": {
            name: describe([x for x in rows if x["classifier_review_flag"] == flag])
            for name, flag in [("flagged", True), ("automatically_accepted", False)]
        },
        "by_predicted_label": {
            label: describe([x for x in rows if x["classifier_prediction"] == label])
            for label in sorted({x["classifier_prediction"] for x in rows})
        },
        "gate": {
            "eligible_categories": 0,
            "automatic_acceptance_enabled": False,
            "reason": "The original 200-example pilot is incomplete; "
            "missing answers are not imputed.",
            "minimum_precision": review_pilot.MIN_PRECISION,
            "confidence": review_pilot.CONFIDENCE,
        },
        "limits": [
            "Exact-label agreement uses only the 23 examples given a leaf label; "
            "specificity was selected by the reviewer.",
            "Broad compatibility checks path ancestry only "
            "and does not establish the predicted leaf label.",
            "The first example was skipped and only the first 100 displayed examples were visited; "
            "stopping may affect representativeness.",
            "Stratification oversamples some groups. "
            "These unweighted descriptive rates are not weighted corpus estimates.",
            "The scorer's full-pilot point estimates remain null; "
            "original thresholds and completion gate are unchanged.",
            "Scores do not establish temporal gameplay rules, "
            "platform equivalence, or reconstruction fidelity.",
        ],
        "disagreement_review_ids": [
            x["review_id"] for x in rows if x["comparison"].endswith("disagreement")
        ],
        "provenance": provenance,
    }
    assert digest(SOURCE) == original_digest
    for name, value in [
        ("validation.json", validation),
        ("subset-scores.json", report),
        ("item-comparisons.json", rows),
    ]:
        review_pilot.write_json(OUTPUT / name, value)
    print(
        json.dumps(
            {
                "validation": validation["status"],
                "summary": summary,
                "heldout": report["by_split"]["heldout"],
                "gate": report["gate"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()

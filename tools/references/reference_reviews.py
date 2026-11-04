"""Resolve hash-bound human screen reviews without changing machine judgments."""

from collections import Counter, defaultdict

from jev_catalog_v2 import SCREEN_STATES

PARENTS = {
    "/".join(parts[:level])
    for state in SCREEN_STATES
    for parts in [state.split("/")]
    for level in range(1, len(parts))
}
UNCERTAIN = {"unreadable", "insufficient_context", "not_in_catalog"}


def import_annotations(pilot, annotations, document, provenance):
    """Import a validated pilot export once, retaining earlier manual decisions."""
    imports = document.get("pilot_imports", [])
    for previous in imports:
        if previous["pilot_id"] == pilot["pilot_id"]:
            if previous["annotations_content_sha256"] != provenance["annotations_content_sha256"]:
                raise ValueError("This pilot already has a different imported annotation set")
            return document
    items = {x["review_id"]: x for x in pilot["items"]}
    reviews = list(document["reviews"])
    for key, answer in sorted(annotations["answers"].items()):
        item = items[key]
        reviews.append(
            {
                "action": "annotate-screen",
                "asset_id": item["asset_id"],
                "source_sha256": item["source_sha256"],
                "pilot_id": pilot["pilot_id"],
                "review_id": key,
                "outcome": answer["outcome"],
                "label": answer["label"],
                "notes": answer["notes"],
                "updated_at": answer["updated_at"],
                "original_machine_state": item["screen_state"],
            }
        )
    return {
        **document,
        "schema_version": 2,
        "scope": "Human screen reviews overlay original classifier records; parent labels never verify descendants.",
        "reviews": reviews,
        "pilot_imports": [
            *imports,
            {
                "pilot_id": pilot["pilot_id"],
                **provenance,
                "saved_answers": len(annotations["answers"]),
                "missing_answers": len(items) - len(annotations["answers"]),
            },
        ],
    }


def apply_reviews(assets, classifications, document):
    annotations, rejected = {}, {}
    for review in document["reviews"]:
        asset_id = review["asset_id"]
        if asset_id not in assets or assets[asset_id]["sha256"] != review["source_sha256"]:
            raise ValueError("Reviewed reference image identity changed: " + asset_id)
        if review["action"] == "exclude-from-state-leads":
            rejected[(review["state"], asset_id)] = review
        elif review["action"] == "annotate-screen":
            if asset_id in annotations:
                raise ValueError("Duplicate screen annotation: " + asset_id)
            outcome, label = review["outcome"], review["label"]
            if outcome == "label":
                if label not in SCREEN_STATES:
                    raise ValueError("Unknown reviewed screen label")
            elif outcome == "category":
                if label not in PARENTS:
                    raise ValueError("Unknown reviewed parent category")
            elif outcome not in UNCERTAIN or label:
                raise ValueError("Unknown or inconsistent review outcome")
            annotations[asset_id] = review
        else:
            raise ValueError("Unknown reference review action")
    effective, parents = [], defaultdict(list)
    corrected = incompatible = uncertain = 0
    seen = set()
    for row in classifications:
        if row.get("status") != "complete":
            continue
        asset_id, state = row["id"], row["screen_state"]
        review = annotations.get(asset_id)
        resolved = row
        if review:
            seen.add(asset_id)
            outcome, label = review["outcome"], review["label"]
            resolved = {
                **row,
                "machine_screen_state": state,
                "machine_screen_review": row.get("screen_review", True),
                "machine_probability": row.get("screen_distribution", {}).get(state),
                "human_review": {
                    key: review[key]
                    for key in ("pilot_id", "review_id", "outcome", "label", "notes", "updated_at")
                },
            }
            reason = None
            if outcome == "label":
                resolved["screen_state"] = label
                resolved["screen_review"] = False
                if label != state:
                    corrected += 1
                    reason = "Human exact label replaces the machine screen assignment"
            elif outcome == "category":
                parents[label].append(asset_id)
                if state.startswith(label + "/"):
                    # The human confirmed only the parent, not this proposed child.
                    resolved["screen_review"] = True
                else:
                    incompatible += 1
                    reason = "Machine screen is outside the human-reviewed parent category"
            else:
                uncertain += 1
                reason = "Human could not establish a precise catalog screen from this frame"
            if reason:
                rejected[(state, asset_id)] = {
                    **review,
                    "state": state,
                    "review_action": review["action"],
                    "action": "exclude-from-state-leads",
                    "reason": reason,
                }
                if outcome != "label":
                    continue
        if (resolved["screen_state"], asset_id) not in rejected:
            effective.append(resolved)
    if seen != set(annotations):
        raise ValueError("Reviewed asset is missing a complete machine record")
    outcomes = Counter(x["outcome"] for x in annotations.values())
    return {
        "rows": effective,
        "rejected": rejected,
        "parent_categories": [
            {
                "category": label,
                "asset_ids": sorted(ids),
                "sample_count": len(ids),
                "exact_label_evidence": False,
            }
            for label, ids in sorted(parents.items())
        ],
        "summary": {
            "human_screen_reviews": len(annotations),
            "outcomes": dict(sorted(outcomes.items())),
            "corrected_exact_labels": corrected,
            "incompatible_parent_labels": incompatible,
            "uncertain_screen_assignments_withheld": uncertain,
            "rejected_machine_state_pairs": len(rejected),
        },
    }


def review_fields(row):
    return {
        key: row[key]
        for key in (
            "human_review",
            "machine_screen_state",
            "machine_screen_review",
            "machine_probability",
        )
        if key in row
    }


def lead_order(platform_priority, lead):
    exact = lead.get("human_review", {}).get("outcome") == "label"
    probability = lead["probability"]
    return (
        platform_priority,
        not exact,
        lead["requires_review"],
        -(probability if probability is not None else 0),
    )

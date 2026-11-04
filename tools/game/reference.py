#!/usr/bin/env python3
"""Build a provenance-preserving, edition-aware reference coverage registry."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "artifacts/juiced2-vault"
sys.path.insert(0, str(ROOT / "tools/references"))
from jev_catalog_v2 import SCREEN_STATES  # noqa: E402
from reference_reviews import apply_reviews, lead_order, review_fields  # noqa: E402


def platform_rank(platform):
    value = platform.lower().replace(" ", "")
    if value in {"ps3", "xbox360"}:
        return 0
    if value == "pc":
        return 1
    if "ps2" in value or "psp" in value:
        return 3
    return 2


def build():
    assets = {item["id"]: item for item in json.loads((VAULT / "assets.json").read_text())}
    reviews = json.loads((ROOT / "data/juiced2/reference-reviews.json").read_text())
    classifications = json.loads((VAULT / "judgments/classifications.json").read_text())
    resolved = apply_reviews(assets, classifications, reviews)
    groups = defaultdict(list)
    for judgment in resolved["rows"]:
        state = judgment["screen_state"]
        asset = assets[judgment["id"]]
        groups[state].append(
            {
                "asset_id": asset["id"],
                "path": str(VAULT / asset["path"]),
                "source_url": asset["source_url"],
                "timestamp_seconds": asset.get("timestamp_seconds"),
                "platform": asset["platform_declared"],
                "edition_rank": platform_rank(asset["platform_declared"]),
                "probability": judgment.get("screen_distribution", {}).get(state),
                "requires_review": judgment.get("screen_review", True),
                **review_fields(judgment),
            }
        )
    states = {row["screen_state"] for row in classifications if row.get("status") == "complete"}
    rows = []
    for state in sorted(states | set(groups)):
        candidates = sorted(groups[state], key=lambda lead: lead_order(lead["edition_rank"], lead))
        eligible = [lead for lead in candidates if lead["edition_rank"] != 3]
        rejected_leads = [
            review for (label, _), review in resolved["rejected"].items() if label == state
        ]
        excluded = (
            state.startswith(("multiplayer/", "reference/"))
            or state == "career/dna-opponents/download"
        )
        rank = candidates[0]["edition_rank"] if candidates else None
        scope = (
            "deferred-or-not-gameplay"
            if excluded
            else "reference-gap"
            if rank is None
            else "console-reference"
            if rank == 0
            else "pc-supplement"
            if rank == 1
            else "platform-unconfirmed"
            if rank == 2
            else "other-edition-only"
        )
        rows.append(
            {
                "state": state,
                "description": SCREEN_STATES.get(state, ""),
                "reference_scope": scope,
                "candidate_count": len(candidates),
                "eligible_reference_count": len(eligible),
                "reviewed_rejections": rejected_leads,
                "reference_leads": eligible[:4],
                "reference_validation": (
                    "human screen reviews and machine leads are distinct; no temporal behavior or fidelity pass"
                ),
                "implementation_validation": "pending executed scenario and visual comparison",
            }
        )
    result = {
        "schema_version": 1,
        "states": rows,
        "human_review_summary": resolved["summary"],
        "reviewed_parent_categories": resolved["parent_categories"],
        "scope_counts": dict(Counter(row["reference_scope"] for row in rows)),
        "rules": [
            "Prefer PS3/Xbox360 over PC, unknown platforms, PS2 and PSP.",
            "Multiplayer, online downloads and creator/emulator overlays are outside "
            "the accepted offline scope.",
            "A parent-screen screenshot does not by itself prove every granular child interaction.",
            "PS2/PSP cannot supply reference leads; empty reviewed states remain explicit gaps.",
            "No implementation or visual comparison is marked passed "
            "by this reference-index builder.",
        ],
    }
    destination = ROOT / "data/juiced2/runtime-reference.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"states": len(rows), "scopes": result["scope_counts"]}))


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()

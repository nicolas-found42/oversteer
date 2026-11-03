#!/usr/bin/env python3
"""Build a provenance-preserving, edition-aware reference coverage registry."""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "artifacts/juiced2-vault"


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
    reviews = json.loads((ROOT / "data/juiced2/reference-reviews.json").read_text())["reviews"]
    rejected = {}
    for review in reviews:
        if assets[review["asset_id"]]["sha256"] != review["source_sha256"]:
            raise ValueError("Reviewed reference image identity changed")
        if review["action"] != "exclude-from-state-leads":
            raise ValueError("Unknown reference review action")
        rejected[(review["state"], review["asset_id"])] = review
    rows = []
    for path in sorted((VAULT / "categories").rglob("index.md")):
        lines = path.read_text().splitlines()
        state = path.parent.relative_to(VAULT / "categories").as_posix()
        if state == ".":
            continue
        candidates = []
        rejected_leads = []
        for line in lines:
            match = re.search(r"p=([0-9.]+).*?\[([^\]]+)\]\(([^)]+)\)", line)
            if not match or match.group(2) not in assets:
                continue
            asset = assets[match.group(2)]
            if review := rejected.get((state, asset["id"])):
                rejected_leads.append(review)
                continue
            rank = platform_rank(asset.get("platform_declared", ""))
            candidates.append(
                {
                    "asset_id": asset["id"],
                    "path": str(VAULT / asset["path"]),
                    "source_url": asset["source_url"],
                    "timestamp_seconds": asset.get("timestamp_seconds"),
                    "platform": asset.get("platform_declared"),
                    "edition_rank": rank,
                    "probability": float(match.group(1)),
                    "requires_review": "PROPOSED" in line,
                }
            )
        if not candidates:
            continue
        candidates.sort(
            key=lambda item: (item["edition_rank"], item["requires_review"], -item["probability"])
        )
        excluded = (
            state.startswith(("multiplayer/", "reference/"))
            or state == "career/dna-opponents/download"
        )
        rank = candidates[0]["edition_rank"]
        scope = (
            "deferred-or-not-gameplay"
            if excluded
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
                "description": lines[2] if len(lines) > 2 else "",
                "reference_scope": scope,
                "candidate_count": len(candidates),
                "reviewed_rejections": rejected_leads,
                "reference_leads": candidates[:4],
                "reference_validation": (
                    "model label is a lead, not independently verified behavior"
                ),
                "implementation_validation": "pending executed scenario and visual comparison",
            }
        )
    result = {
        "schema_version": 1,
        "states": rows,
        "scope_counts": dict(Counter(row["reference_scope"] for row in rows)),
        "rules": [
            "Prefer PS3/Xbox360 over PC, unknown platforms, PS2 and PSP.",
            "Multiplayer, online downloads and creator/emulator overlays are outside "
            "the accepted offline scope.",
            "A parent-screen screenshot does not by itself prove every granular child interaction.",
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

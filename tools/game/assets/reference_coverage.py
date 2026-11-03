"""Index existing visual judgments as review leads, not assertions of parity."""

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VAULT = ROOT / "artifacts/juiced2-vault"
CANONICAL_PLATFORMS = {"PS3", "Xbox 360"}
PRESS_PLATFORMS = {"Xbox 360 / PS3 press batch", "Xbox 360 press batch"}
EXCLUDED_PLATFORMS = {"PS2", "PSP", "PS2 press batch"}


def source_role(platform):
    if platform in CANONICAL_PLATFORMS:
        return "canonical-platform-lead", 0
    if platform in PRESS_PLATFORMS:
        return "console-press-visual-lead", 1
    if platform == "PC":
        return "supplemental-pc-lead", 2
    if platform == "Unspecified by title":
        return "unverified-platform-lead", 3
    if platform == "Xbox 360 / PS3 press batch (prerelease)":
        return "prerelease-visual-lead", 4
    if platform in EXCLUDED_PLATFORMS:
        return "excluded-platform", 5
    raise ValueError(f"Unrecognized declared platform: {platform!r}")


def main():
    assets = {asset["id"]: asset for asset in json.loads((VAULT / "assets.json").read_text())}
    reviews = json.loads((ROOT / "data/juiced2/reference-reviews.json").read_text())["reviews"]
    rejected = {}
    for review in reviews:
        if assets[review["asset_id"]]["sha256"] != review["source_sha256"]:
            raise ValueError("Reviewed reference image identity changed")
        if review["action"] != "exclude-from-state-leads":
            raise ValueError("Unknown reference review action")
        rejected[(review["state"], review["asset_id"])] = review
    rows = json.loads((VAULT / "judgments/classifications.json").read_text())
    groups = collections.defaultdict(list)
    for row in rows:
        if row.get("status") != "complete" or row["id"] not in assets:
            continue
        state = row.get("screen_state", "unresolved")
        asset = assets[row["id"]]
        role, priority = source_role(asset.get("platform_declared"))
        groups[state].append(
            {
                "asset_id": asset["id"],
                "frame_path": str(VAULT / asset["path"]),
                "source_url": asset.get("source_url"),
                "timestamp_seconds": asset.get("timestamp_seconds"),
                "platform": asset.get("platform_declared"),
                "probability": row.get("screen_distribution", {}).get(state, 0),
                "requires_review": row.get("screen_review", True),
                "tags": row.get("tags", []),
                "source_role": role,
                "source_priority": priority,
            }
        )
    coverage = []
    for state, leads in sorted(groups.items()):
        leads.sort(
            key=lambda lead: (
                lead["source_priority"], lead["requires_review"], -lead["probability"]
            )
        )
        canonical_count = sum(lead["platform"] in CANONICAL_PLATFORMS for lead in leads)
        eligible = [lead for lead in leads if (state, lead["asset_id"]) not in rejected]
        eligible_canonical_count = sum(
            lead["platform"] in CANONICAL_PLATFORMS for lead in eligible
        )
        excluded_count = sum(lead["platform"] in EXCLUDED_PLATFORMS for lead in leads)
        in_scope = not (
            state.startswith(("multiplayer/", "reference/"))
            or state == "career/dna-opponents/download"
        )
        coverage.append(
            {
                "state": state,
                "classifier_sample_count": len(leads),
                "platform_counts": dict(collections.Counter(lead["platform"] for lead in leads)),
                "canonical_platform_sample_count": canonical_count,
                "eligible_canonical_platform_sample_count": eligible_canonical_count,
                "reviewed_rejections": [
                    rejected[(state, lead["asset_id"])]
                    for lead in leads if (state, lead["asset_id"]) in rejected
                ],
                "excluded_platform_sample_count": excluded_count,
                "scope": (
                    "single-player-review-candidate" if in_scope else "outside-accepted-game-scope"
                ),
                "canonical_reference_gap": in_scope and eligible_canonical_count == 0,
                "reference_leads": [
                    {key: value for key, value in lead.items() if key != "source_priority"}
                    for lead in eligible if lead["platform"] not in EXCLUDED_PLATFORMS
                ][:4],
                "implementation_status": "not independently compared",
                "claim": (
                    "classification lead; observed behavior and full state coverage "
                    "require visual review"
                ),
            }
        )
    result = {
        "schema_version": 2,
        "source": "existing vault classifications, not newly observed guarantees",
        "states": coverage,
        "limits": [
            "State taxonomy candidates are not guaranteed observed states.",
            "Declared platforms are retained source metadata, not new platform verification.",
            "PS3/Xbox 360 retail leads precede press, PC, unverified and prerelease leads.",
            "PS2/PSP samples remain counted but cannot supply acceptance reference leads.",
            "Highest-scoring exemplars may still need review; probabilities are retained.",
            "No matched application capture or fidelity pass is claimed.",
        ],
    }
    (ROOT / "data/juiced2/reference-coverage.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "classified_state_groups": len(coverage),
        "reference_samples": sum(len(group) for group in groups.values()),
        "single_player_candidates": sum(
            row["scope"] == "single-player-review-candidate" for row in coverage
        ),
        "canonical_reference_gaps": [
            row["state"] for row in coverage if row["canonical_reference_gap"]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()

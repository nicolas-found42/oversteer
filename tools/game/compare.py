#!/usr/bin/env python3
"""Create explicitly reviewable source/current screenshot pairs from native runs."""

import argparse
import hashlib
import html
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
# Only these named observations are paired. Child interactions need their own evidence.
PAIRS = [
    ("boot/title", "title"),
    ("menu/main", "menu"),
    ("career/hub", "career"),
    ("career/event-details/track", "event"),
    ("betting/cash-wager/offer", "bet"),
    ("garage/owned-cars/list", "garage"),
    ("dealership/car-list/model", "dealer"),
    ("crew/selection/roster", "crew"),
    ("customization/category", "customization"),
    ("customization/vinyl/placement/panel", "vinyl"),
    ("character/identity/unspecified", "avatar"),
    ("options/audio/volumes", "options"),
    ("presentation/credits", "credits"),
    ("race/pause/menu", "pause"),
    ("race/driving/circuit/lap-race", "driving"),
    ("results/standings/circuit", "mode-Circuit"),
    ("results/standings/drift", "mode-SoloDrift"),
]
UI_PAIRS = [
    ("career/goals/checklist", "ui-career-wager", "goals.png"),
    ("betting/opponent-list/driver", "ui-career-wager", "grid.png"),
    ("betting/cash-wager/counteroffer", "ui-career-wager", "counteroffer.png"),
    ("betting/cash-wager/accepted", "ui-career-wager", "accepted.png"),
    ("dealership/purchase-confirm/dialog", "ui-dealer", "purchase-confirm.png"),
    ("garage/sell-confirm/offer", "ui-dealer", "sale-confirm.png"),
    ("customization/checkout/items", "ui-cart", "cart.png"),
    ("customization/checkout/confirm", "ui-cart", "checkout-confirm.png"),
    ("customization/paint/body/palette", "ui-body-palette", "palette-open.png"),
    ("customization/wheels/color/palette", "ui-wheel-palette", "palette-open.png"),
    ("customization/vinyl/color/palette", "ui-vinyl-palette", "palette-open.png"),
    ("customization/vinyl/layers/list", "ui-palettes-vinyl", "two-layers.png"),
    ("customization/vinyl/placement/transform", "ui-palettes-vinyl", "transformed.png"),
    ("customization/vinyl/catalog/design", "ui-palettes-vinyl", "native-design.png"),
    ("customization/wheels/rims/design", "ui-cart", "wheels.png"),
    ("betting/pink-slip/warning", "ui-pink-slip", "pink-warning.png"),
    ("betting/pink-slip/opponent", "ui-pink-slip", "pink-offer.png"),
    ("betting/spectator/selection", "ui-spectator", "spectator-selection.png"),
    ("race/driving/spectator/competitor", "ui-spectator", "camera-target.png"),
    ("character/identity/unspecified", "ui-native-avatar", "gender.png"),
    ("character/preset", "ui-native-avatar", "male-preset.png"),
    ("character/face/nose", "ui-native-avatar", "nose.png"),
    ("character/clothing/bottom", "ui-native-avatar", "bottoms.png"),
    ("customization/paint/body/palette", "ui-native-palette", "opened.png"),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", nargs="+", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = (options.output or ROOT / f"build/verification/{stamp}-comparisons").resolve()
    destination.mkdir(parents=True, exist_ok=False)
    references = json.loads((ROOT / "data/juiced2/runtime-reference.json").read_text())
    assets = {
        a["id"]: a for a in json.loads((ROOT / "artifacts/juiced2-vault/assets.json").read_text())
    }
    states = {item["state"]: item for item in references["states"]}
    cases = {}
    for folder in options.runs:
        record = json.loads((folder / "verification.json").read_text())
        for case in record["cases"]:
            cases[case["case"]["id"]] = (folder.resolve(), record, case)
    pairs = []
    unpaired = []
    for state, case_id, capture in [(s, c, None) for s, c in PAIRS] + UI_PAIRS:
        if state not in states or case_id not in cases:
            continue
        if not states[state]["reference_leads"] or states[state]["reference_scope"] in {
            "deferred-or-not-gameplay",
            "other-edition-only",
        }:
            unpaired.append(
                {
                    "state": state,
                    "case": case_id,
                    "reason": states[state]["reference_scope"],
                }
            )
            continue
        folder, run, case = cases[case_id]
        current = folder / case_id / capture if capture else folder / case["capture"]
        if not current.exists():
            continue
        reference = states[state]["reference_leads"][0]
        source = ROOT / "artifacts/juiced2-vault" / assets[reference["asset_id"]]["path"]
        with Image.open(source) as original, Image.open(current) as implementation:
            canvas = Image.new("RGB", (2560, 780), "#141a24")
            draw = ImageDraw.Draw(canvas)
            draw.text((20, 14), f"REFERENCE: {reference['asset_id']}", fill="white")
            draw.text((1300, 14), f"CURRENT: {case_id}", fill="white")
            canvas.paste(ImageOps.contain(original.convert("RGB"), (1280, 720)), (0, 60))
            canvas.paste(ImageOps.contain(implementation.convert("RGB"), (1280, 720)), (1280, 60))
            name = state.replace("/", "--") + f"--{case_id}.jpg"
            canvas.save(destination / name, quality=94)
        pairs.append(
            {
                "state": state,
                "case": case_id,
                "image": name,
                "source_asset": reference["asset_id"],
                "source_url": reference["source_url"],
                "source_time_seconds": reference["timestamp_seconds"],
                "source_sha256": assets[reference["asset_id"]]["sha256"],
                "source_platform": reference["platform"],
                "source_reference_scope": states[state]["reference_scope"],
                "source_label_requires_review": reference["requires_review"],
                "current_capture": str(current),
                "current_sha256": hashlib.sha256(current.read_bytes()).hexdigest(),
                "binary_sha256": run["binary_sha256"],
                "content_sha256": run["content_sha256"],
                "scenario_status": case["status"],
                "visual_review": "pending explicit comparison; pairing is not acceptance",
            }
        )
    (destination / "comparisons.json").write_text(
        json.dumps({"pairs": pairs, "unpaired": unpaired}, indent=2) + "\n"
    )
    esc = html.escape
    page = [
        "<!doctype html><meta charset=utf-8><title>Reference comparisons</title>",
        "<style>body{font:16px system-ui;background:#10141c;color:#eef;margin:24px}"
        "img{width:100%;height:auto}article{margin:40px 0}a{color:#abd2ff}</style>",
        "<h1>Reference comparisons</h1>",
        "<p>Pairs await visual review. A reference label or passing scenario "
        "does not establish parity.</p>",
    ]
    for pair in pairs:
        url = pair["source_url"] + f"&t={int(pair['source_time_seconds'] or 0)}s"
        page.append(
            f"<article><h2>{esc(pair['state'])}</h2>"
            f"<p><a href='{esc(url)}'>Original source at this timestamp</a> · "
            f"{esc(str(pair['source_platform']))} · Visual review pending</p>"
            f"<img loading=lazy src='{esc(pair['image'])}'></article>"
        )
    (destination / "index.html").write_text("\n".join(page))
    print(json.dumps({"pairs": len(pairs), "gallery": str(destination / "index.html")}))


if __name__ == "__main__":
    main()

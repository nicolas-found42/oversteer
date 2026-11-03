"""Classify public reference images with pinned Jev through OpenRouter Decisions.

Usage: python3 tools/references/classify_vault.py [--limit N] [--workers N]
Requires OPENROUTER_API_KEY. It is never written to the evidence log.
Images go to the configured provider; private game source is not sent.
"""

from __future__ import annotations

import argparse
import base64
import concurrent.futures
import gzip
import hashlib
import io
import json
import os
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

from jev_catalog import (
    CHOICE_ACCEPT,
    CHOICE_MARGIN,
    FACETS,
    SCREEN_STATES,
    TAG_NO,
    TAG_YES,
    TAGS,
    questions,
)

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "artifacts/juiced2-vault"
MODEL = "typesafe/jev-1.14"
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
CATALOG = questions()
CATALOG_HASH = hashlib.sha256(json.dumps(CATALOG, sort_keys=True).encode()).hexdigest()
LOCK = threading.Lock()
COST = 0.0


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def distribution(answer, criteria):
    values = answer.get("probabilities", {})
    if set(values) != set(criteria):
        raise ValueError("Response probability catalog mismatch")
    if any(not isinstance(p, (int, float)) or not 0 <= p <= 1 for p in values.values()):
        raise ValueError("Invalid probability")
    if abs(sum(values.values()) - 1) > 0.03:
        raise ValueError("Probability distribution does not sum to one")
    if answer.get("choice") not in values:
        raise ValueError("Choice absent from probability distribution")
    ranked = sorted(values.values(), reverse=True)
    top = max(values, key=values.get)
    if top != answer["choice"] and values[top] != values[answer["choice"]]:
        raise ValueError("Choice contradicts highest probability")
    review = ranked[0] < CHOICE_ACCEPT or ranked[0] - ranked[1] < CHOICE_MARGIN
    return answer["choice"], review


def noul(answer):
    value = answer.get("noul")
    if answer.get("type") != "noul" or not isinstance(value, (int, float)):
        raise ValueError("Missing Noul response")
    if not 0 <= value <= 1:
        raise ValueError("Invalid Noul probability")
    return value


def classify(asset, key, cost_cap):
    global COST
    asset_id = asset["id"]
    output = VAULT / "judgments/raw" / (asset_id + ".response.json")
    request_path = output.with_name(asset_id + ".request.json.gz")
    image = (VAULT / asset["path"]).read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != asset["sha256"]:
        raise ValueError("Image hash changed: " + asset_id)
    if output.exists():
        saved = json.loads(output.read_text())
        if saved.get("catalog_sha256") != CATALOG_HASH or saved.get("image_sha256") != digest:
            raise ValueError("Cached judgment input mismatch: " + asset_id)
        response = saved["response"]
    else:
        with LOCK:
            if COST >= cost_cap:
                raise RuntimeError("Local spending cap reached; remaining assets unresolved")
        reference = "7a81fe2d-vault-image"
        # Preserve the original evidence; prepare only the submitted copy to fit
        # TypeSafe's documented maximum image dimensions.
        with Image.open(io.BytesIO(image)) as original:
            prepared = ImageOps.exif_transpose(original)
            submitted_dimensions = prepared.size
            if max(prepared.size) > 1568 or original.getexif().get(274, 1) != 1:
                prepared.thumbnail((1568, 1568))
                buffer = io.BytesIO()
                prepared.convert("RGB").save(buffer, "JPEG", quality=90)
                image = buffer.getvalue()
                submitted_dimensions = prepared.size
        body = {
            "model": MODEL,
            "state": {
                "screenshot": reference,
                "scope": (
                    "One recorded game image; no hidden rules or temporal behavior established."
                ),
            },
            "assets": {
                reference: {
                    "type": "image",
                    "format": "jpg",
                    "data_base64": base64.b64encode(image).decode(),
                }
            },
            "questions": CATALOG,
        }
        payload = json.dumps(body).encode()
        request_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(request_path, "wb") as stream:
            stream.write(payload)
        request = urllib.request.Request(
            ENDPOINT,
            data=payload,
            headers={
                "Authorization": "Bearer " + key,
                "Content-Type": "application/json",
                "TypeSafe-Danger-Zone-Images": "true",
            },
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(request, timeout=90) as stream:
                    response = json.load(stream)
                break
            except urllib.error.HTTPError as error:
                if error.code not in (429, 502, 503, 504) or attempt == 2:
                    raise RuntimeError(f"Jev HTTP {error.code}") from error
                time.sleep(2 ** (attempt + 1))
        write_json(
            output,
            {
                "image_sha256": digest,
                "submitted_image_sha256": hashlib.sha256(image).hexdigest(),
                "submitted_dimensions": submitted_dimensions,
                "catalog_sha256": CATALOG_HASH,
                "response": response,
            },
        )
        with LOCK:
            COST += response.get("usage", {}).get("cost", 0)
    answers = response.get("answers", {})
    if set(answers) != set(CATALOG):
        raise ValueError("Missing or additional answers")
    screen, review = distribution(answers["screen"], SCREEN_STATES)
    visible = noul(answers["game_visible"])
    facets = {}
    facet_review = []
    for name, criteria in FACETS.items():
        facets[name], needs_review = distribution(answers[name], criteria)
        if needs_review:
            facet_review.append(name)
    probabilities = {name: noul(answers[name]) for name in TAGS}
    return {
        "id": asset_id,
        "screen_state": screen,
        "screen_review": review or visible < TAG_YES,
        "game_visible_probability": visible,
        "facets": facets,
        "facet_review": facet_review,
        "tags": [name for name, p in probabilities.items() if p >= TAG_YES],
        "uncertain_tags": [name for name, p in probabilities.items() if TAG_NO < p < TAG_YES],
        "tag_probabilities": probabilities,
        "screen_distribution": answers["screen"]["probabilities"],
        "model": response["model"],
        "usage": response.get("usage", {}),
        "raw_response": str(output.relative_to(VAULT)),
        "request": str(request_path.relative_to(VAULT)),
        "catalog_sha256": CATALOG_HASH,
        "image_sha256": digest,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--cost-cap", type=float, default=3.0)
    parser.add_argument("--assets", type=Path, default=VAULT / "assets.json")
    args = parser.parse_args()
    key = os.environ["OPENROUTER_API_KEY"]
    assets = json.loads(args.assets.read_text())
    if args.limit:
        assets = assets[: args.limit]
    write_json(
        VAULT / "judgments/catalog.json",
        {
            "model": MODEL,
            "endpoint": ENDPOINT,
            "catalog_sha256": CATALOG_HASH,
            "questions": CATALOG,
            "thresholds": {
                "choice_accept": CHOICE_ACCEPT,
                "choice_margin": CHOICE_MARGIN,
                "tag_yes": TAG_YES,
                "tag_no": TAG_NO,
            },
            "limitations": [
                "Image support is experimental according to TypeSafe's live documentation.",
                "A label is a probabilistic visual judgment, not a verified game rule.",
                "A single frame cannot establish timing, controls, causality, or physics.",
                "Absent labels mean not visibly detected, not absent from the game.",
            ],
        },
    )
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending = {pool.submit(classify, a, key, args.cost_cap): a for a in assets}
        for index, future in enumerate(concurrent.futures.as_completed(pending), 1):
            asset = pending[future]
            try:
                results.append(future.result())
            except Exception as error:
                results.append({"id": asset["id"], "error": str(error)})
                print(asset["id"], "ERROR", str(error), flush=True)
            if index % 25 == 0 or index == len(assets):
                write_json(VAULT / "judgments/classifications.json", results)
                print(f"{index}/{len(assets)} classified; new call cost ${COST:.4f}", flush=True)
    results.sort(key=lambda item: item["id"])
    write_json(VAULT / "judgments/classifications.json", results)
    errors = sum("error" in item for item in results)
    usage = {
        "assets": len(results),
        "errors": errors,
        "screen_review": sum(item.get("screen_review", False) for item in results),
        "input_tokens": sum(item.get("usage", {}).get("input_tokens", 0) for item in results),
        "output_tokens": sum(item.get("usage", {}).get("output_tokens", 0) for item in results),
        "reported_cost_usd": sum(item.get("usage", {}).get("cost", 0) for item in results),
        "new_call_cost_usd": COST,
    }
    write_json(VAULT / "judgments/usage.json", usage)
    print(json.dumps(usage), flush=True)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()

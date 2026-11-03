"""Hierarchical Jev image judgments, spatial regions and adjacent-frame comparisons.

All images remain in the vault. Each source frame is judged individually; exact
request/response evidence is retained. Classification suggestions never establish
hidden gameplay rules. OPENROUTER_API_KEY is read only from the environment.
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

import jev_catalog_v2 as catalog
from classify_vault import distribution, noul, write_json
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[2]
VAULT = ROOT / "artifacts/juiced2-vault"
WORK = VAULT / "judgments/v2"
MODEL = "typesafe/jev-1.14"
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
LOCK = threading.Lock()
SPENT = 0.0
STOP = threading.Event()
OFFLINE = False
READABILITY_METADATA = WORK.parent / "taxonomy-v2/text-dependent-tags.json"
TEXT_DEPENDENT_TAGS = (
    set(json.loads(READABILITY_METADATA.read_text())["tag_ids"])
    if READABILITY_METADATA.exists()
    else set()
)
TRANSITIONS = {
    "transition/screen-changed": (
        "Did the kind of game screen change between previous and screenshot?"
    ),
    "transition/selection-changed": (
        "Did the visibly highlighted menu selection change between previous and screenshot?"
    ),
    "transition/car-appearance-changed": (
        "Did visible car paint or fitted body parts change between previous and screenshot?"
    ),
    "transition/score-changed": (
        "Did a visibly displayed drift score change between previous and screenshot?"
    ),
    "transition/notification-appeared": (
        "Did a new game notification appear in screenshot that was absent in previous?"
    ),
}


def signature(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def prepared_asset(asset):
    path = VAULT / asset["path"]
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != asset["sha256"]:
        raise ValueError("Source image hash mismatch: " + asset["id"])
    with Image.open(io.BytesIO(data)) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        original_size = image.size
        # Jev rejects either side below 280 or above 1568. Upscaling only makes
        # the transport valid; it does not recover missing source information.
        scale = min(1.0, 1568 / max(image.size))
        if min(image.size) * scale < 280:
            scale = 280 / min(image.size)
        size = tuple(round(side * scale) for side in image.size)
        if max(size) > 1568:
            image.thumbnail((1568, 1568))
            canvas = Image.new("RGB", (max(280, image.width), max(280, image.height)))
            canvas.paste(image, ((canvas.width - image.width) // 2, 0))
            image = canvas
        elif size != image.size:
            image = image.resize(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, "JPEG", quality=90)
        submitted = buffer.getvalue()
        preparation = {
            "source_sha256": asset["sha256"],
            "submitted_sha256": hashlib.sha256(submitted).hexdigest(),
            "source_dimensions": list(original_size),
            "submitted_dimensions": list(image.size),
            "upscaled": min(original_size) < 280,
            "coordinate_space": "normalized submitted-image coordinates",
        }
    return {
        "type": "image",
        "format": "jpg",
        "data_base64": base64.b64encode(submitted).decode(),
    }, preparation


def ask(asset, stage, questions, key, cap, previous=None):
    global SPENT
    dependencies = {
        "image": asset["sha256"],
        "previous": previous["sha256"] if previous else None,
        "questions": signature(questions),
        "model": MODEL,
        "preparation_version": 1,
    }
    stamp = signature(dependencies)[:16]
    name = f"{asset['id']}.{stage}.{stamp}"
    response_path = WORK / "raw" / (name + ".response.json")
    request_path = WORK / "raw" / (name + ".request.json.gz")
    if response_path.exists():
        saved = json.loads(response_path.read_text())
        if saved["dependencies"] != dependencies:
            raise ValueError("Cached dependency mismatch")
    else:
        if OFFLINE:
            raise RuntimeError("pending_cache: Jev judgment not yet cached")
        if STOP.is_set():
            raise RuntimeError("pending_credit: provider credits exhausted")
        with LOCK:
            if SPENT >= cap:
                raise RuntimeError("Spending cap reached; remaining judgments unresolved")
        image, preparation = prepared_asset(asset)
        current_reference = "983fc1e6-current-image"
        state = {
            "screenshot": current_reference,
            "scope": "Judge only visible evidence. Hidden mechanics remain unknown.",
        }
        assets = {current_reference: image}
        preparations = {"screenshot": preparation}
        if previous:
            old_image, old_preparation = prepared_asset(previous)
            old_reference = "7246acb9-previous-image"
            state["previous"] = old_reference
            state["time_between_seconds"] = (
                asset["timestamp_seconds"] - previous["timestamp_seconds"]
            )
            assets[old_reference] = old_image
            preparations["previous"] = old_preparation
        body = {"model": MODEL, "state": state, "assets": assets, "questions": questions}
        payload = json.dumps(body).encode()
        request_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(request_path, "wb", compresslevel=3) as stream:
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
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=120) as stream:
                    response = json.load(stream)
                break
            except urllib.error.HTTPError as error:
                detail = error.read().decode(errors="replace")[:1200]
                if error.code == 402:
                    STOP.set()
                if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    write_json(
                        WORK / "errors" / (name + ".json"),
                        {"status": error.code, "detail": detail, "dependencies": dependencies},
                    )
                    raise RuntimeError(f"Jev HTTP {error.code}: {detail[:200]}") from error
                delay = error.headers.get("Retry-After", "")
                time.sleep(min(30, float(delay) if delay.isdigit() else 2 ** (attempt + 1)))
        if set(response.get("answers", {})) != set(questions):
            raise ValueError("Jev omitted or added answers")
        saved = {
            "dependencies": dependencies,
            "request_sha256": hashlib.sha256(payload).hexdigest(),
            "preparations": preparations,
            "response": response,
        }
        write_json(response_path, saved)
        with LOCK:
            SPENT += response.get("usage", {}).get("cost", 0)
    return {
        "answers": saved["response"]["answers"],
        "model": saved["response"]["model"],
        "usage": saved["response"].get("usage", {}),
        "preparations": saved["preparations"],
        "raw_response": str(response_path.relative_to(VAULT)),
        "request": str(request_path.relative_to(VAULT)),
    }


def valid_box(answer):
    box = answer.get("box", {})
    if set(box) != {"top", "bottom", "left", "right"}:
        return False
    if any(not isinstance(p, (int, float)) or not 0 <= p <= 1 for p in box.values()):
        return False
    return box["top"] < box["bottom"] and box["left"] < box["right"]


def parse_answers(answers, questions):
    choices, tags, scores, regions, unresolved = {}, {}, {}, {}, []
    for name, question in questions.items():
        answer = answers[name]
        if answer.get("type") != question["type"]:
            raise ValueError("Answer type mismatch: " + name)
        if question["type"] == "choice":
            value, review = distribution(answer, question["criteria"])
            choices[name] = {"value": value, "review": review, "answer": answer}
        elif question["type"] == "noul":
            tags[name] = noul(answer)
        elif question["type"] == "score":
            levels = question["criteria"]
            values = answer.get("probabilities", {})
            if set(values) != {str(i) for i in range(len(levels))}:
                raise ValueError("Score level mismatch: " + name)
            if any(not isinstance(p, (int, float)) or not 0 <= p <= 1 for p in values.values()):
                raise ValueError("Invalid score distribution")
            if abs(sum(values.values()) - 1) > 0.03:
                raise ValueError("Score distribution sum mismatch")
            position = answer.get("score")
            if not isinstance(position, (int, float)) or not 0 <= position <= len(levels) - 1:
                raise ValueError("Invalid score position")
            scores[name] = answer
        elif question["type"] == "box":
            presence_key = name.replace("box/", "box_present/", 1)
            presence = tags.get(presence_key)
            if presence is None:
                raise ValueError("Box missing companion presence Noul: " + name)
            if presence <= 0.2:
                continue
            if valid_box(answer):
                regions[name] = answer
            else:
                unresolved.append(name)
    return choices, tags, scores, regions, unresolved


def classify(asset, previous, key, cap):
    broad_questions = catalog.broad_questions()
    if previous:
        broad_questions.update(
            {name: {"type": "noul", "instructions": text} for name, text in TRANSITIONS.items()}
        )
    broad = ask(asset, "broad", broad_questions, key, cap, previous)
    broad_choices, probabilities, scores, _, unresolved = parse_answers(
        broad["answers"], broad_questions
    )
    domain = broad_choices["domain"]
    ranking = sorted(domain["answer"]["probabilities"].items(), key=lambda x: -x[1])
    groups = [domain["value"]]
    if domain["review"] and len(ranking) > 1 and ranking[1][1] >= 0.15:
        groups.append(ranking[1][0])
    detail_questions = {}
    leaf_keys = {}
    for group in groups:
        for name, question in catalog.detail_questions(group, include_boxes=True).items():
            if name == "screen":
                name = "screen__" + group
                leaf_keys[group] = name
            elif name == "domain_matches":
                name = "domain_matches__" + group
            detail_questions[name] = question
    detail = ask(asset, "detail", detail_questions, key, cap)
    choices, tag_values, detail_scores, boxes, box_errors = parse_answers(
        detail["answers"], detail_questions
    )
    probabilities.update(tag_values)
    scores.update(detail_scores)
    unresolved.extend(box_errors)
    screen = choices[leaf_keys[domain["value"]]]
    facets = {}
    facet_review = []
    for name, value in {**broad_choices, **choices}.items():
        if name != "domain" and not name.startswith("screen__"):
            name = name.removeprefix("facet/")
            facets[name] = value["value"]
            if value["review"]:
                facet_review.append(name)
    regions = {}
    for name, answer in boxes.items():
        presence_key = name.replace("box/", "box_present/", 1)
        presence = probabilities.get(presence_key)
        if presence is None:
            raise ValueError("Box missing companion presence Noul: " + name)
        if presence > 0.2:
            regions[name.removeprefix("box/")] = {
                "box": answer["box"],
                "presence_probability": presence,
                "confidence": answer.get("confidence"),
                "review": presence < 0.8
                or answer.get("confidence") is None
                or answer["confidence"] < 0.8,
                "coordinate_space": "normalized submitted-image coordinates",
            }
    transitions = {name: p for name, p in probabilities.items() if name.startswith("transition/")}
    visible_tags = {name: p for name, p in probabilities.items() if name in catalog.TAGS}
    readability = scores["score/readability"]["probabilities"]
    low_readability = readability["0"] + readability["1"] >= 0.7
    tag_reviews = {
        name: "Text-dependent category remains proposed because interface text is not readable."
        for name, p in visible_tags.items()
        if low_readability and p >= 0.8 and name in TEXT_DEPENDENT_TAGS
    }
    usage = {
        name: sum(stage["usage"].get(name, 0) for stage in [broad, detail])
        for name in ["input_tokens", "output_tokens", "cost"]
    }
    return {
        "id": asset["id"],
        "status": "complete",
        "domain": domain["value"],
        "domain_review": domain["review"],
        "domain_distribution": domain["answer"]["probabilities"],
        "screen_state": screen["value"],
        "screen_review": domain["review"]
        or screen["review"]
        or probabilities.get("game_visible", 0) < 0.8
        or probabilities.get("domain_matches__" + domain["value"], 0) < 0.8,
        "screen_distribution": screen["answer"]["probabilities"],
        "alternative_categories": {
            group: choices[leaf_keys[group]] for group in groups if group != domain["value"]
        },
        "game_visible_probability": probabilities.get("game_visible"),
        "facets": facets,
        "facet_review": facet_review,
        "tags": [name for name, p in visible_tags.items() if p >= 0.8 and name not in tag_reviews],
        "uncertain_tags": [
            name for name, p in visible_tags.items() if 0.2 < p < 0.8 or name in tag_reviews
        ],
        "tag_probabilities": visible_tags,
        "tag_review_reasons": tag_reviews,
        "evaluated_tag_count": len(visible_tags),
        "scores": scores,
        "regions": regions,
        "unresolved_regions": unresolved,
        "transitions": transitions,
        "previous_asset_id": previous["id"] if previous else None,
        "model": broad["model"],
        "usage": usage,
        "image_sha256": asset["sha256"],
        "image_preparation": broad["preparations"]["screenshot"],
        "raw_response": detail["raw_response"],
        "request": detail["request"],
        "stage_evidence": [
            {k: stage[k] for k in ["raw_response", "request", "model", "usage"]}
            for stage in [broad, detail]
        ],
        "catalog_version": 2,
    }


def previous_frames(assets):
    previous = {}
    sources = {}
    for asset in assets:
        if asset["kind"] == "frame":
            sources.setdefault(asset["source_id"], []).append(asset)
    for rows in sources.values():
        rows.sort(key=lambda x: x["timestamp_seconds"])
        for before, current in zip(rows, rows[1:]):
            gap = current["timestamp_seconds"] - before["timestamp_seconds"]
            if 0 < gap <= 6:
                previous[current["id"]] = before
    return previous


def main():
    global OFFLINE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, default=VAULT / "assets.json")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--cost-cap", type=float, default=15)
    parser.add_argument("--offline", action="store_true", help="Reuse caches without API calls")
    args = parser.parse_args()
    OFFLINE = args.offline
    assets = json.loads(args.assets.read_text())
    previous = previous_frames(assets)
    if args.limit:
        assets = assets[: args.limit]
    # Preserve the earlier production pass and its unresolved failures.
    old = VAULT / "judgments/classifications.json"
    archive = WORK / "previous-pass.json"
    if old.exists() and not archive.exists():
        write_json(archive, json.loads(old.read_text()))
    write_json(
        VAULT / "judgments/catalog.json",
        {
            "version": 2,
            "model": MODEL,
            "groups": catalog.GROUPS,
            "screen_groups": catalog.SCREEN_GROUPS,
            "questions": {
                "screen": {"type": "choice", "criteria": catalog.SCREEN_STATES},
                **{
                    name: {"type": "noul", "instructions": text}
                    for name, text in catalog.TAGS.items()
                },
            },
            "broad_questions": catalog.broad_questions(),
            "detail_questions": {
                group: catalog.detail_questions(group) for group in catalog.GROUPS
            },
            "thresholds": {"choice": 0.85, "margin": 0.5, "yes": 0.8, "no": 0.2},
            "limitations": [
                "Probabilistic image judgments; experimental image and Box support.",
                "Low resolution inputs are upscaled for transport only; no detail is recovered.",
                "Region coordinates refer to the submitted image; review flags are retained.",
                "Temporal comparisons observe recorded images, not inputs or hidden game rules.",
            ],
        },
    )
    results = []
    WORK.mkdir(parents=True, exist_ok=True)
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not OFFLINE and not key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")
    with (WORK / "progress.jsonl").open("w") as journal:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(classify, a, previous.get(a["id"]), key, args.cost_cap): a
                for a in assets
            }
            for count, future in enumerate(concurrent.futures.as_completed(futures), 1):
                asset = futures[future]
                try:
                    result = future.result()
                except Exception as error:
                    message = str(error)
                    pending = message.startswith("pending_") or "Jev HTTP 402" in message
                    result = {
                        "id": asset["id"],
                        "status": "pending_credit" if pending else "error",
                        "error": message,
                    }
                    if not pending or "Jev HTTP 402" in message:
                        print(asset["id"], "ERROR", message[:250], flush=True)
                results.append(result)
                journal.write(json.dumps(result) + "\n")
                journal.flush()
                if count % 100 == 0 or count == len(assets):
                    print(f"{count}/{len(assets)}; new request cost ${SPENT:.4f}", flush=True)
    results.sort(key=lambda item: item["id"])
    write_json(VAULT / "judgments/classifications.json", results)
    errors = sum(item.get("status") == "error" for item in results)
    pending = sum(item.get("status") == "pending_credit" for item in results)
    stats = {
        "assets": len(results),
        "errors": errors,
        "pending": pending,
        "complete": len(results) - errors - pending,
        "screen_review": sum(item.get("screen_review", False) for item in results),
        "input_tokens": sum(item.get("usage", {}).get("input_tokens", 0) for item in results),
        "output_tokens": sum(item.get("usage", {}).get("output_tokens", 0) for item in results),
        "reported_cost_usd": sum(item.get("usage", {}).get("cost", 0) for item in results),
        "new_call_cost_usd": SPENT,
        "temporal_pairs": sum(item.get("previous_asset_id") is not None for item in results),
        "regions": sum(len(item.get("regions", {})) for item in results),
    }
    write_json(VAULT / "judgments/usage.json", stats)
    write_json(
        WORK / "resume-queue.json",
        {
            "pending_asset_ids": [row["id"] for row in results if row.get("status") != "complete"],
            "reason": (
                "Provider work remains pending; inspect classification records for errors."
                if errors or pending
                else None
            ),
            "command": "python3 tools/references/classify_vault_v2.py --workers 16 --cost-cap 20",
            "cache_policy": (
                "Matching completed stages are reused without another provider request."
            ),
        },
    )
    print(json.dumps(stats), flush=True)
    raise SystemExit(1 if errors else 2 if pending else 0)


if __name__ == "__main__":
    main()

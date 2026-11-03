#!/usr/bin/env python3
"""Retain typed Jev pixel judgments for explicit source/current scene pairs."""

import argparse
import base64
import gzip
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps
from verify import ROOT, digest

MODEL = "typesafe/jev-1.14"
ENDPOINT = "https://openrouter.ai/api/alpha/decisions"
QUESTIONS = {
    "reference_readable": {
        "type": "noul",
        "instructions": "Is the UI text in reference readable enough to identify its game screen?",
    },
    "current_readable": {
        "type": "noul",
        "instructions": "Is the UI text in current readable enough to identify its game screen?",
    },
    "same_phase": {
        "type": "noul",
        "instructions": (
            "Do reference and current show the same game screen or phase? A main menu, "
            "a garage, a pre-race bet, active driving and race results are different phases. "
            "Different vehicle models are allowed."
        ),
    },
    "same_panel_placement": {
        "type": "noul",
        "instructions": (
            "Are the main menu lists, information panels or driving HUD elements in current "
            "arranged in the same screen regions as reference? Judge their visible positions, "
            "not their wording or vehicle identity."
        ),
    },
    "same_background_composition": {
        "type": "noul",
        "instructions": (
            "Does current use the same kind of visible background and camera composition "
            "as reference? A tunnel and a garage are different backgrounds. "
            "Different vehicle models are allowed."
        ),
    },
    "same_letter_style": {
        "type": "noul",
        "instructions": (
            "Does current use the same visible main UI lettering style as reference? "
            "Compare letter shapes and weight, not the words or vehicle identity."
        ),
    },
}


def image_asset(path):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((1568, 1568))
        if min(image.size) < 280:
            raise ValueError(f"Image is too small for a trustworthy comparison: {path}")
        output = io.BytesIO()
        image.save(output, "JPEG", quality=94)
        payload = output.getvalue()
    return (
        {"type": "image", "format": "jpg", "data_base64": base64.b64encode(payload).decode()},
        {
            "source_sha256": digest(path),
            "submitted_sha256": hashlib.sha256(payload).hexdigest(),
            "dimensions": list(image.size),
        },
    )


def judge(pair, reference, current, destination, key):
    assets = {}
    preparations = {}
    for role, path in [("reference", reference), ("current", current)]:
        assets[f"scene-{role}"], preparations[role] = image_asset(path)
    body = {
        "model": MODEL,
        "state": {
            "reference": "scene-reference",
            "current": "scene-current",
            "scope": (
                "Compare only visible screen composition. Screenshots cannot establish "
                "hidden gameplay rules or full implementation correctness."
            ),
        },
        "assets": assets,
        "questions": QUESTIONS,
    }
    payload = json.dumps(body).encode()
    request_sha = hashlib.sha256(payload).hexdigest()
    stem = pair["state"].replace("/", "--")
    if "case" in pair:
        stem += "--" + pair["case"]
    response_file = destination / f"{stem}.response.json"
    with gzip.open(destination / f"{stem}.request.json.gz", "wb") as stream:
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
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        failure = {
            "http_status": error.code,
            "message": error.read().decode(errors="replace")[:1200],
        }
        response_file.write_text(
            json.dumps({"error": failure, "request_sha256": request_sha}, indent=2) + "\n"
        )
        raise RuntimeError(f"Jev HTTP {error.code}; pair remains unresolved") from error
    response_file.write_text(
        json.dumps(
            {"request_sha256": request_sha, "preparations": preparations, "response": result},
            indent=2,
        )
        + "\n"
    )
    if set(result.get("answers", {})) != set(QUESTIONS):
        raise ValueError("Jev did not return the exact requested question set")
    probabilities = {}
    for name, answer in result["answers"].items():
        if answer.get("type") != "noul":
            raise ValueError(f"Invalid Jev answer type for {name}")
        value = answer.get("noul")
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"Invalid Jev probability for {name}")
        probabilities[name] = value
    # A mismatch directs repair. Every other result still needs explicit pixel review.
    mismatches = [
        name
        for name in [
            "same_phase",
            "same_panel_placement",
            "same_background_composition",
            "same_letter_style",
        ]
        if probabilities[name] <= 0.2
    ]
    return {
        "state": pair["state"],
        "case": pair.get("case"),
        "source_sha256": digest(reference),
        "current_sha256": digest(current),
        "binary_sha256": pair.get("binary_sha256"),
        "content_sha256": pair.get("content_sha256"),
        "probabilities": probabilities,
        "mismatches": mismatches,
        "status": "repair-required" if mismatches else "explicit-review-required",
        "response_file": response_file.name,
        "usage": result.get("usage", {}),
        "reference_source_label_requires_review": pair.get("source_label_requires_review"),
        "warning": "A model judgment is not visual acceptance or evidence of gameplay behavior.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--comparisons", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--state", action="append")
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Check identical-image and unrelated-scene probes before judging the pairs",
    )
    options = parser.parse_args()
    destination = options.output.resolve()
    destination.mkdir(parents=True, exist_ok=False)
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OpenRouter credential is unavailable; no judgment was made")
    assets = {
        asset["id"]: asset
        for asset in json.loads((ROOT / "artifacts/juiced2-vault/assets.json").read_text())
    }
    pairs = json.loads(options.comparisons.read_text())["pairs"]
    if options.state:
        pairs = [pair for pair in pairs if pair["state"] in options.state]
    records = []
    for index, pair in enumerate(pairs):
        reference = ROOT / "artifacts/juiced2-vault" / assets[pair["source_asset"]]["path"]
        current = Path(pair["current_capture"])
        if digest(reference) != pair["source_sha256"] or digest(current) != pair["current_sha256"]:
            raise ValueError("Comparison image identity changed")
        if options.probe and index == 0:
            positive = judge({"state": "probe-identical"}, reference, reference, destination, key)
            negative_path = ROOT / "build/verification/checkpoint-smoke/driving/final.png"
            if not negative_path.exists():
                raise ValueError("The retained driving negative probe is unavailable")
            negative = judge(
                {"state": "probe-menu-vs-driving"}, reference, negative_path, destination, key
            )
            probes = {"positive": positive, "negative": negative}
            (destination / "probes.json").write_text(json.dumps(probes, indent=2) + "\n")
            if (
                positive["probabilities"]["same_phase"] < 0.8
                or positive["probabilities"]["same_panel_placement"] < 0.8
                or negative["probabilities"]["same_phase"] > 0.2
            ):
                raise RuntimeError(
                    "Live image judgment probes failed; pair judgments remain unresolved"
                )
        record = judge(pair, reference, current, destination, key)
        records.append(record)
        (destination / "judgments.json").write_text(
            json.dumps({"judgments": records}, indent=2) + "\n"
        )
        print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()

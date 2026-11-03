#!/usr/bin/env python3
"""Check actual roster captures for visible, unobstructed cars with typed Jev questions."""

import argparse
import gzip
import hashlib
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from judge_comparisons import ENDPOINT, MODEL, image_asset
from verify import digest


def judge_capture(path, destination, key):
    asset, preparation = image_asset(path)
    body = {
        "model": MODEL,
        "state": {"screenshot": "car-capture"},
        "assets": {"car-capture": asset},
        "questions": {
            "visible_car": {
                "type": "noul",
                "instructions": "Is a rendered car body clearly visible in screenshot?",
            },
            "unobstructed_car": {
                "type": "noul",
                "instructions": (
                    "Is most of the rendered car body unobstructed by foreground scene "
                    "geometry in screenshot? A wall covering the vehicle is an obstruction."
                ),
            },
        },
    }
    payload = json.dumps(body).encode()
    stem = preparation["source_sha256"]
    with gzip.open(destination / f"{stem}.request.json.gz", "wb") as stream:
        stream.write(payload)
    request = urllib.request.Request(ENDPOINT, data=payload, headers={
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json", "TypeSafe-Danger-Zone-Images": "true",
    })
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        (destination / f"{stem}.error.json").write_text(json.dumps({
            "http_status": error.code,
            "message": error.read().decode(errors="replace")[:1200],
        }, indent=2) + "\n")
        raise RuntimeError(f"Jev HTTP {error.code}; visibility remains unresolved") from error
    (destination / f"{stem}.response.json").write_text(json.dumps({
        "request_sha256": hashlib.sha256(payload).hexdigest(),
        "preparation": preparation, "response": result,
    }, indent=2) + "\n")
    if set(result.get("answers", {})) != set(body["questions"]):
        raise ValueError("Jev did not return the exact visibility question set")
    probabilities = {}
    for name, answer in result["answers"].items():
        probability = answer.get("noul")
        if answer.get("type") != "noul" or type(probability) not in (int, float) or not 0 <= probability <= 1:
            raise ValueError(f"Invalid visibility answer for {name}")
        probabilities[name] = probability
    status = ("repair-required" if min(probabilities.values()) <= 0.2 else
              "visible-car-evidence" if min(probabilities.values()) >= 0.8 else
              "explicit-review-required")
    return {"source_sha256": stem, "probabilities": probabilities, "status": status,
            "usage": result.get("usage", {})}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    options = parser.parse_args()
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OpenRouter credential unavailable; no judgment made")
    options.output.mkdir(parents=True, exist_ok=False)
    distinct = {}
    for path in options.captures:
        distinct.setdefault(digest(path), []).append(path)
    records = []
    for paths in distinct.values():
        record = judge_capture(paths[0], options.output, key)
        if any(digest(path) != record["source_sha256"] for path in paths):
            raise ValueError("Capture identity changed during judgment")
        record["captures"] = [str(path.resolve()) for path in paths]
        records.append(record)
        (options.output / "judgments.json").write_text(json.dumps({
            "judgments": records,
            "scope": "Visible car evidence only; no material, identity, customization or reference parity acceptance.",
        }, indent=2) + "\n")
        print(json.dumps({**record, "captures": len(paths)}), flush=True)


if __name__ == "__main__":
    main()

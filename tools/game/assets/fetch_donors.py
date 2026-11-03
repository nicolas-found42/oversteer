#!/usr/bin/env python3
"""Fetch only the thirty accepted donor GLBs at their pinned commit and hashes."""

import hashlib
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
DESTINATION = ROOT / "artifacts/carmodels-research/models"


def fetch(car, commit):
    destination = DESTINATION / f"{car['code']}.glb"
    expected = car["source_sha256"]
    if destination.exists():
        with destination.open("rb") as source:
            if hashlib.file_digest(source, "sha256").hexdigest() == expected:
                return car["code"]
    url = car["source_url"]
    parsed = urlparse(url)
    prefix = f"/nicolas-found42/carmodels/{commit}/"
    if (
        parsed.scheme != "https"
        or parsed.netloc != "raw.githubusercontent.com"
        or not parsed.path.startswith(prefix)
    ):
        raise ValueError(f"Unpinned donor URL: {car['code']}")
    temporary = destination.with_suffix(".glb.partial")
    digest = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as response, temporary.open("wb") as output:
        while block := response.read(1024 * 1024):
            output.write(block)
            digest.update(block)
    if digest.hexdigest() != expected:
        temporary.unlink()
        raise ValueError(f"Pinned donor SHA256 mismatch: {car['code']}")
    temporary.replace(destination)
    return car["code"]


def main():
    roster = json.loads((ROOT / "data/juiced2/accepted-roster.json").read_text())
    if len(roster["cars"]) != 30:
        raise ValueError("The accepted initial roster must contain exactly thirty vehicles")
    DESTINATION.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=4) as executor:
        verified = list(
            executor.map(lambda car: fetch(car, roster["source_commit"]), roster["cars"])
        )
    print(json.dumps({"verified_donors": len(verified), "source_commit": roster["source_commit"]}))


if __name__ == "__main__":
    main()

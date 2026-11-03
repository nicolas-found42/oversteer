"""Checksum-verified source-sprite assets, research facts and offline Jev decisions."""

import argparse
import hashlib
import json
import shutil

from tools.carmodels.assets import COMMIT, ROOT, WORK
from tools.carmodels.scope import included_identities

DATA = ROOT / "data/carmodels"


def bundle():
    from tools.carmodels.judgments import prepare_jobs
    from tools.carmodels.research import load_sources

    DATA.mkdir(exist_ok=True)
    sources = load_sources()
    identities = json.loads((WORK / "identities.json").read_text())
    matches = json.loads((WORK / "matching/matches.json").read_text())
    included = {i["code"] for i in included_identities(identities["identities"])}
    keep_match = {
        "code",
        "sourceId",
        "sourceLabel",
        "match_kind",
        "review_status",
        "rationale",
        "source_url",
        "source_limits",
        "source_notes",
        "adjudication",
        "source_confidence",
        "qualityFlags",
        "selection_exists_verdict",
        "selection_probability",
        "selection_review_resolution",
        "previous_match_correction",
        "family_review",
        "family_search_evidence",
        "trim_search_evidence",
    }
    matches = {
        "matches": [
            {k: v for k, v in m.items() if k in keep_match}
            for m in matches["matches"]
            if m["code"] in included
        ]
    }
    selected = {m["sourceId"] for m in matches["matches"]}
    # Original prose remains in ignored research snapshots. Publish numerical facts,
    # original fact-table strings, source URLs, qualifiers and dataset attribution.
    records = [
        {k: v for k, v in sources[key].items() if k not in {"evidence", "sourceText"}}
        for key in sorted(selected)
    ]
    for record in records:
        if "catalogCodes" in record:
            record["catalogCodes"] = [code for code in record["catalogCodes"] if code in included]
    (DATA / "sources.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    )
    models = json.loads((WORK / "models.json").read_text())
    measurements = json.loads((WORK / "references/measurements.json").read_text())
    for label, codes in [
        ("matches", [m["code"] for m in matches["matches"]]),
        ("models", [m["code"] for m in models["cars"] if m["code"] in included]),
        ("measurements", [m["code"] for m in measurements if m["code"] in included]),
    ]:
        if len(codes) != len(included) or set(codes) != included:
            raise ValueError("Incomplete or duplicate included " + label)
    models = {
        "source_commit": COMMIT,
        "cars": [
            {k: r[k] for k in ["code", "sha256", "bytes"]}
            for r in models["cars"]
            if r["code"] in included
        ],
    }
    files = {
        "identities.json": identities,
        "matches.json": matches,
        "models.json": models,
        "measurements.json": [r for r in measurements if r["code"] in included],
        "benchmarks.json": json.loads((WORK / "benchmarks/summary.json").read_text()),
        "judgments.json": {
            "jobs": prepare_jobs(),
            "results": [
                r
                for r in json.loads((WORK / "jev-workflow/results.json").read_text())
                if r["tool"] not in {"jev_review", "jev_gate"}
            ],
        },
        "body-features.json": [
            r
            for r in json.loads((WORK / "body-features/inspection.json").read_text())
            if r["code"] in included
        ],
    }
    for name, value in files.items():
        (DATA / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    manifest = {
        "source_commit": COMMIT,
        "catalog_entries": len(identities["identities"]),
        "included": len(included),
        "excluded": len(identities["identities"]) - len(included),
        "source_records": len(records),
        "files": {},
    }
    for path in sorted(DATA.rglob("*")):
        if (
            not path.is_file()
            or path.suffix not in {".json", ".jsonl", ".txt"}
            or path.name == "manifest.json"
        ):
            continue
        manifest["files"][path.relative_to(DATA).as_posix()] = hashlib.sha256(
            path.read_bytes()
        ).hexdigest()
    sprites = json.loads((DATA / "sprites.json").read_text())
    manifest["sprite_assets"] = {r["code"] + ".png": r["atlas_sha256"] for r in sprites}
    for name, digest in manifest["sprite_assets"].items():
        if hashlib.sha256((ROOT / "resources/vehicles" / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Sprite checksum mismatch: " + name)
    (DATA / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "files"}))


def restore():
    manifest = json.loads((DATA / "manifest.json").read_text())
    if manifest["source_commit"] != COMMIT:
        raise ValueError("training source revision mismatch")
    for name, digest in manifest["files"].items():
        if hashlib.sha256((DATA / name).read_bytes()).hexdigest() != digest:
            raise ValueError("training input checksum mismatch: " + name)
    for name, digest in manifest["sprite_assets"].items():
        if hashlib.sha256((ROOT / "resources/vehicles" / name).read_bytes()).hexdigest() != digest:
            raise ValueError("Sprite checksum mismatch: " + name)
    mapping = {
        "identities.json": "identities.json",
        "models.json": "models.json",
        "matches.json": "matching/matches.json",
        "sources.jsonl": "sources/selected-specs.jsonl",
        "measurements.json": "references/measurements.json",
        "benchmarks.json": "benchmarks/summary.json",
        "body-features.json": "body-features/inspection.json",
    }
    for source, destination in mapping.items():
        path = WORK / destination
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DATA / source, path)
    profiles = WORK / "profiles"
    profiles.mkdir(exist_ok=True)
    for path in (DATA / "profiles").glob("*.txt"):
        shutil.copyfile(path, profiles / path.name)
    snapshot = json.loads((DATA / "sprite-judgments.json").read_text())
    notes = WORK / "sprites/source-notes"
    notes.mkdir(parents=True, exist_ok=True)
    for name, text in snapshot.get("source_notes", {}).items():
        (notes / name).write_text(text)
    judgments = json.loads((DATA / "judgments.json").read_text())
    output = WORK / "jev-workflow"
    output.mkdir(exist_ok=True)
    (output / "results.json").write_text(json.dumps(judgments["results"], indent=2))
    for row in judgments["results"]:
        prefix = row["id"] + "-" + row["request_hash"]
        (output / (prefix + ".response.json")).write_text(json.dumps(row["result"], indent=2))
    print("Restored checksum-verified training inputs to " + str(WORK))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["bundle", "restore"])
    args = parser.parse_args()
    bundle() if args.action == "bundle" else restore()

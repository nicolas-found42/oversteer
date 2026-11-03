"""Check all documented same-make families, avoiding a lexical shortlist that can omit SC430→SC."""

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

from tools.carmodels.assets import WORK
from tools.carmodels.research import load_sources
from tools.carmodels.scope import is_included
from tools.carmodels.trim_selection import RELEASE_YEAR


def token(label):
    ascii_label = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_label.lower()).strip("_")


def prepare():
    sources = load_sources()
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    matches = json.loads((WORK / "matching/matches.json").read_text())["matches"]
    families = {}
    for source in sources.values():
        if source["id"].startswith("gor3a:"):
            families.setdefault(source["make"], {}).setdefault(source["model"], []).append(
                source["id"]
            )
    jobs, context = [], {}
    for match in matches:
        identity = identities[match["code"]]
        if not is_included(identity) or not match["sourceId"].startswith("gor3a:"):
            continue
        source = sources[match["sourceId"]]
        make = identity.get("make") if identity.get("make") in families else source["make"]
        candidates = families[make]
        if len(candidates) > 250:
            raise ValueError("Full family set exceeds provider limit: " + make)
        key = "family_" + hashlib.sha256(identity["code"].encode()).hexdigest()[:12]
        ids = {
            token(make + " " + model) + "_" + hashlib.sha256(model.encode()).hexdigest()[:6]: model
            for model in candidates
        }
        if len(ids) != len(candidates):
            raise ValueError("Family ID collision")
        jobs.append(
            {
                "id": key,
                "tool": "jev_find",
                "arguments": {
                    "query": "Find the documented production model family named by this catalog "
                    "vehicle, allowing year/grade differences: "
                    + identity["source_name"]
                    + " ("
                    + str(identity.get("make"))
                    + "). A different model from the same "
                    "make is not a same-family match.",
                    "candidates": [
                        {"id": candidate, "text": make + " " + model}
                        for candidate, model in ids.items()
                    ],
                    "top_k": 3,
                },
            }
        )
        context[key] = {
            "code": identity["code"],
            "make": make,
            "model_ids": ids,
            "current_source": match["sourceId"],
            "current_family": source["model"],
        }
    (WORK / "family-selection-context.json").write_text(json.dumps(context, indent=2))
    return jobs


def prepare_trims():
    sources = load_sources()
    context = json.loads((WORK / "family-selection-context.json").read_text())
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    jobs, changes, unresolved = [], {}, []
    for row in json.loads((WORK / "family-selection/results.json").read_text()):
        item, result = context[row["id"]], row["result"]
        top = result["top"]
        margin = top[0]["probability"] - (top[1]["probability"] if len(top) > 1 else 0)
        if result["exists_verdict"] != "answered" or top[0]["probability"] < 0.85 or margin < 0.5:
            unresolved.append({"code": item["code"], "result": result})
            continue
        model = item["model_ids"][top[0]["id"]]
        if model == item["current_family"]:
            continue
        identity = identities[item["code"]]
        year = identity.get("year") or RELEASE_YEAR[identity["game"]]
        candidates = [
            s
            for s in sources.values()
            if s.get("make") == item["make"]
            and s.get("model") == model
            and s["id"].startswith("gor3a:")
        ]

        def distance(s, reference_year=year):
            return max(
                s["yearStart"] - reference_year,
                reference_year - (s.get("yearEnd") or s["yearStart"]),
                0,
            )

        best = min(map(distance, candidates))
        candidates = [s for s in candidates if distance(s) == best]
        key = row["id"] + "-trim"
        jobs.append(
            {
                "id": key,
                "tool": "jev_find",
                "arguments": {
                    "query": "Select the closest listed production trim for "
                    + identity["source_name"]
                    + ". The same model family is independently established; the nearest date "
                    "ranges were selected in code. Any year/grade substitution stays labeled.",
                    "candidates": [
                        {
                            "id": s["id"].replace(":", "_"),
                            "text": s["generation"] + " | " + s["engineLabel"],
                        }
                        for s in candidates
                    ],
                    "top_k": 3,
                },
            }
        )
        changes[key] = {
            **item,
            "selected_family": model,
            "family_probability": top[0]["probability"],
            "family_request_hash": row["request_hash"],
            "candidate_ids": {s["id"].replace(":", "_"): s["id"] for s in candidates},
        }
    (WORK / "family-trim-context.json").write_text(json.dumps(changes, indent=2))
    (WORK / "family-selection/unresolved.json").write_text(json.dumps(unresolved, indent=2))
    print(
        f"Confident family corrections: {len(changes)}; "
        f"uncertain family judgments: {len(unresolved)}"
    )
    return jobs


def adopt(review_path):
    """Family names overlap (GT-R/Skyline, AMG/CLS); require recorded agent review."""
    context = json.loads((WORK / "family-trim-context.json").read_text())
    reviews = json.loads(review_path.read_text())
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    sources = load_sources()
    path = WORK / "matching/matches.json"
    document = json.loads(path.read_text())
    matches = {m["code"]: m for m in document["matches"]}
    count = 0
    for row in json.loads((WORK / "family-trims/results.json").read_text()):
        item, result = context[row["id"]], row["result"]
        review = reviews[row["id"]]
        if not review.get("reason") or not is_included(identities[item["code"]]):
            raise ValueError("Missing review reason or excluded identity: " + item["code"])
        if review["action"] == "retain":
            continue
        if review["action"] != "replace" or review["sourceId"] not in sources:
            raise ValueError("Invalid family review: " + row["id"])
        match = matches[item["code"]]
        if match["sourceId"] == review["sourceId"]:
            continue
        if match["sourceId"] != item["current_source"]:
            raise ValueError("Source changed since family review: " + item["code"])
        source = sources[review["sourceId"]]
        match["previous_match_correction"] = {
            "sourceId": match["sourceId"],
            "sourceLabel": match["sourceLabel"],
        }
        match.update(
            sourceId=source["id"],
            sourceLabel=item["make"] + " | " + source["generation"] + " | " + source["engineLabel"],
            match_kind="nearest_trim",
            review_status="accepted_agent_reviewed_family_search",
            rationale=review["reason"],
            family_review={"review": review, "prediction": result},
            family_search_evidence=item["family_request_hash"],
            trim_search_evidence=row["request_hash"],
        )
        count += 1
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False))
    print(f"Adopted {count} model-family corrections")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "trims", "adopt"])
    parser.add_argument("--review-file", type=Path)
    args = parser.parse_args()
    if args.action == "adopt":
        if not args.review_file:
            parser.error("adopt requires --review-file with per-proposal agent dispositions")
        adopt(args.review_file)
    else:
        jobs = prepare() if args.action == "prepare" else prepare_trims()
        path = WORK / "family-selection-jobs.json"
        path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))
        print(path)

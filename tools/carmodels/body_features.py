"""Typed body-feature hypotheses; only visually corroborated positives affect profiles."""

import json

from tools.carmodels.assets import WORK
from tools.carmodels.research import load_sources
from tools.carmodels.scope import is_included


def reference_label(source):
    return source.get("vehicle") or " ".join(
        str(source.get(key) or "") for key in ["make", "model", "generation"]
    )


def prepare():
    sources = load_sources()
    matches = {
        m["code"]: m for m in json.loads((WORK / "matching/matches.json").read_text())["matches"]
    }
    identities = [
        i
        for i in json.loads((WORK / "identities.json").read_text())["identities"]
        if is_included(i) and i["vehicle_type"] == "truck"
    ]
    jobs, index = [], {}
    for n in range(0, len(identities), 64):
        chunk = identities[n : n + 64]
        job_id = f"pickup-bed-{n // 64}"
        jobs.append(
            {
                "id": job_id,
                "tool": "jev_noul",
                "arguments": {
                    "context": "Catalog labels describe recovered game objects. This is a semantic "
                    "body-type hypothesis, not a pixel observation or a physical dimension. "
                    "Opaque/modified vehicles may be unresolved. A later independent render "
                    "inspection must corroborate any adopted cargo-bed feature.",
                    "propositions": [
                        f"The game vehicle {i['source_name']}, whose labeled body reference is "
                        f"{reference_label(sources[matches[i['code']]['sourceId']])}, "
                        "has an open pickup cargo bed behind the cabin."
                        for i in chunk
                    ],
                },
            }
        )
        index[job_id] = [i["code"] for i in chunk]
    (WORK / "body-feature-index.json").write_text(json.dumps(index, indent=2))
    return jobs


if __name__ == "__main__":
    path = WORK / "body-feature-jobs.json"
    path.write_text(json.dumps(prepare(), ensure_ascii=False, indent=2))
    print(path)

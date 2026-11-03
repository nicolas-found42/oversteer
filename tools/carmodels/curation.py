"""Apply independently researched catalog-code corrections, keeping prior mappings."""

import json

from tools.carmodels.assets import WORK
from tools.carmodels.scope import is_included


def apply_corrections():
    path = WORK / "matching/matches.json"
    document = json.loads(path.read_text())
    matches = {m["code"]: m for m in document["matches"]}
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    history_path = WORK / "identity-audit/corrections.json"
    changes = json.loads(history_path.read_text()) if history_path.exists() else []
    count = 0
    for source_path in sorted((WORK / "sources").glob("corrected-*-specs.jsonl")):
        for line in source_path.read_text().splitlines():
            source = json.loads(line)
            for code in source.get("catalogCodes", []):
                if not is_included(identities[code]):
                    continue
                match = matches[code]
                if match["sourceId"] == source["id"]:
                    continue
                changes.append(
                    {
                        "code": code,
                        "previous_source": match["sourceId"],
                        "source": source["id"],
                        "audit": source.get("auditStatus"),
                    }
                )
                count += 1
                match["previous_match_correction"] = {
                    "sourceId": match["sourceId"],
                    "sourceLabel": match["sourceLabel"],
                }
                match.update(
                    sourceId=source["id"],
                    sourceLabel=" | ".join(
                        str(source.get(k) or "") for k in ["make", "generation", "engineLabel"]
                    ),
                    match_kind="nearest_trim",
                    review_status="accepted_documented_partial_reference",
                    rationale="Catalog-code mapping to the independently researched actual "
                    "family or explicitly labeled nearby grade/year. Only retained "
                    "facts are adopted; missing/disputed values remain estimates.",
                    source_url=source["sourceUrl"],
                    source_notes=source.get("notes", []),
                )
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    history_path.write_text(json.dumps(changes, indent=2) + "\n")
    print(f"Applied {count} new source corrections")


if __name__ == "__main__":
    apply_corrections()

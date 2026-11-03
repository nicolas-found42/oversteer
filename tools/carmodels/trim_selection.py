"""Prepare bounded Jev source selections for independently identified family corrections."""

import json

from tools.carmodels.assets import WORK
from tools.carmodels.research import load_sources
from tools.carmodels.scope import is_included

RELEASE_YEAR = {
    "gran-turismo": 1997,
    "gran-turismo-4": 2004,
    "midnight-club-3-remix": 2006,
    "midnight-club-los-angeles": 2009,
    "ford-racing-2": 2003,
    "redline": 2007,
}
FAMILIES = {
    "GT4_MINE0002": ("Mitsubishi", "Lancer Evolution", 1999),
    "GT4_OPRA0001": ("Honda", "S2000", 2004),
    "GT4_REAM0001": ("Mazda", "RX-7", 2002),
    "GT4_SPON0001": ("Honda", "Jazz / Fit", 2003),
    "MCLA_VP_NSN_GTR_08": ("Nissan", "GT-R", 2008),
    "GT4_ORG_0001": (None, None, None),
}


def prepare():
    sources = load_sources()
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    matches = json.loads((WORK / "matching/matches.json").read_text())["matches"]
    jobs, context = [], {}
    for match in matches:
        code = match["code"]
        identity = identities[code]
        if not is_included(identity):
            continue
        source = sources[match["sourceId"]]
        if not source["id"].startswith("gor3a:"):
            continue
        year = identity.get("year") or RELEASE_YEAR[identity["game"]]
        make, model = source.get("make"), source.get("model")
        correction = code in FAMILIES and FAMILIES[code][0] is not None
        if correction:
            make, model, year = FAMILIES[code]
        elif not source.get("yearStart") or source["yearStart"] <= year:
            continue
        candidates = [
            s
            for s in sources.values()
            if s.get("make") == make
            and s.get("model") == model
            and s["id"].startswith("gor3a:")
            and not s.get("qualityFlags")
        ]
        if not candidates:
            raise ValueError("No researched family candidates for " + code)

        def distance(s, reference_year=year):
            start, end = s["yearStart"], s.get("yearEnd") or s["yearStart"]
            return max(start - reference_year, reference_year - end, 0)

        best = min(map(distance, candidates))
        candidates = [s for s in candidates if distance(s) == best]
        if len(candidates) > 250:
            raise ValueError("Candidate family needs narrower body/generation: " + code)
        jobs.append(
            {
                "id": "trim-" + code.lower().replace("_", "-"),
                "tool": "jev_find",
                "arguments": {
                    "query": "Choose the closest listed real production trim "
                    "for this catalog identity. Year ranges have already been narrowed "
                    "by exact chronology in code. All numbers will describe the explicitly "
                    "labeled substitute, never an undocumented game tune. Catalog: "
                    + identity["source_name"],
                    "candidates": [
                        {
                            "id": s["id"].replace(":", "_"),
                            "text": f"{s['make']} {s['model']} | {s['generation']} | "
                            f"{s['engineLabel']}",
                        }
                        for s in candidates
                    ],
                    "top_k": 3,
                },
            }
        )
        context[jobs[-1]["id"]] = {
            "code": code,
            "candidate_ids": {s["id"].replace(":", "_"): s["id"] for s in candidates},
            "reason": "Independently identified family correction"
            if correction
            else "No post-catalog/post-game generation when a period reference exists",
            "reference_year": year,
        }
    (WORK / "trim-selection-context.json").write_text(json.dumps(context, indent=2))
    return jobs


if __name__ == "__main__":
    path = WORK / "trim-selection-jobs.json"
    path.write_text(json.dumps(prepare(), ensure_ascii=False, indent=2))
    print(path)

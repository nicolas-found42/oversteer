"""Batch semantic identity checks; uncertain mappings require a recorded adjudication."""

import json

from tools.carmodels.assets import WORK
from tools.carmodels.research import benchmark_sources
from tools.carmodels.scope import is_included


def prepare():
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    sources = {}
    for path in (WORK / "sources").glob("*specs.jsonl"):
        for line in path.read_text().splitlines():
            source = json.loads(line)
            sources[source["id"]] = source
    for source in benchmark_sources(WORK / "benchmarks/summary.json"):
        sources[source["id"]] = source
    items = []
    for match in json.loads((WORK / "matching/matches.json").read_text())["matches"]:
        identity = identities[match["code"]]
        if not is_included(identity):
            continue
        source = sources[match["sourceId"]]
        items.append(
            {
                "id": identity["code"],
                "text": json.dumps(
                    {
                        "catalog": {
                            k: identity.get(k)
                            for k in ["source_name", "make", "model", "year", "vehicle_type"]
                        },
                        "reference": {
                            k: source.get(k)
                            for k in [
                                "make",
                                "model",
                                "generation",
                                "yearStart",
                                "yearEnd",
                                "engineLabel",
                                "vehicle",
                            ]
                        },
                        "mapping_kind": match["match_kind"],
                    },
                    ensure_ascii=False,
                ),
            }
        )
    classes = [
        {
            "id": "same_family",
            "description": "Same actual vehicle family with a plausible "
            "nearby generation/grade or explicitly labeled race derivative/market substitution. "
            "Trim mismatch alone belongs here.",
        },
        {
            "id": "incompatible_reference",
            "description": "Different vehicle identity, "
            "architecture or historical era makes the reference unsuitable even as the closest "
            "physical production substitute: e.g. a 1930s streamliner mapped to a modern minivan. "
            "A clear mismatch takes precedence.",
        },
        {
            "id": "manual_review",
            "description": "Names and supplied context do not settle "
            "whether the reference is a physically reasonable closest model. Never infer missing "
            "facts from short opaque codes.",
        },
    ]
    return [
        {
            "id": f"identity-audit-{n // 64:02d}",
            "tool": "jev_classify",
            "arguments": {
                "purpose": "Audit catalog identity to selected real-spec mapping before training. "
                "The user permits labeled closest real production trims; unrelated eras or chassis "
                "are not useful nearest trims. Source correctness is checked separately.",
                "classes": classes,
                "items": items[n : n + 64],
            },
        }
        for n in range(0, len(items), 64)
    ]


if __name__ == "__main__":
    path = WORK / "identity-audit-jobs.json"
    path.write_text(json.dumps(prepare(), ensure_ascii=False, indent=2))
    print(path)

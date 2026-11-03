"""Preserve qualified performance limits using bounded Jev extraction and evidence checks.

Jev selects the source spans and checks their meaning. Code converts units and
keeps one-sided bounds distinct from exact measurements and estimated curves.
"""

import argparse
import json
import re

from tools.carmodels.assets import WORK
from tools.carmodels.research import load_sources
from tools.carmodels.scope import is_included

TARGETS = {
    "additional:race-nissan-r92cp": ("kw", True),
    "corrected-concepts:honda-hsc": ("hp", True),
    "additional:race-ford-rs200-rally": ("hp", False),
    "corrected-proto:garaiya03": ("ps", False),
}
POWER_PATTERNS = {
    "kw": r"(?:Over\s*)?\d[\d,.]*\s*kW\b",
    "hp": r"(?:(?:in\s+excess\s+of|over|at\s+least)\s+)?\d[\d,.]*\+?\s*(?:hp|horsepower)\b",
    "ps": r"\d[\d,.]*\s*ps(?:以上)?",
}
SUBJECTS = {
    "additional:race-nissan-r92cp": "Nissan R92CP racing car",
    "corrected-concepts:honda-hsc": "Honda HSC concept",
    "additional:race-ford-rs200-rally": (
        "1986 Ford RS200 race version, distinct from the 250hp road car"
    ),
    "corrected-proto:garaiya03": "ARTA Garaiya racing car",
}


def number(span):
    return float(re.search(r"\d[\d,.]*", span)[0].replace(",", ""))


def prepare():
    sources = load_sources()
    identities = {
        i["code"]: i for i in json.loads((WORK / "identities.json").read_text())["identities"]
    }
    selected = {
        m["sourceId"]
        for m in json.loads((WORK / "matching/matches.json").read_text())["matches"]
        if is_included(identities[m["code"]])
    }
    jobs, context = [], {}
    for n, (source_id, (power_unit, strict)) in enumerate(TARGETS.items()):
        if source_id not in selected:
            continue
        source = sources[source_id]
        document = source["evidence"]
        if not document or len(document) > 20000:
            raise ValueError("Constraint evidence must be complete and bounded")
        key = f"bound-{n}"
        context[key] = {
            "source_id": source_id,
            "power_unit": power_unit,
            "strict": strict,
            "document": document,
            "source_url": source["sourceUrl"],
        }
        fields = [
            {
                "id": "power_lower",
                "pattern": POWER_PATTERNS[power_unit],
                "flags": "i",
                "description": "Lower bound on peak engine output, with source units.",
            },
            {
                "id": "torque_lower",
                "pattern": r"(?:Over\s*)?\d[\d,.]*\s*(?:N[•·]?m|kg[-•·]?m)(?:以上)?",
                "flags": "i",
                "description": "Published lower bound on peak engine torque, if given.",
            },
            {
                "id": "power_rpm",
                "pattern": r"\b\d[\d,]*\s*rpm\b",
                "flags": "i",
                "description": "Engine RPM associated with the published peak power, if given.",
            },
            {
                "id": "torque_rpm",
                "pattern": r"\b\d[\d,]*\s*rpm\b",
                "flags": "i",
                "description": "Engine RPM associated with the published peak torque, if given.",
            },
        ]
        if source_id == "additional:race-nissan-r92cp":
            fields.append(
                {
                    "id": "mass_lower",
                    "pattern": r"Over\s*\d[\d,.]*\s*kg\b",
                    "flags": "i",
                    "description": "Published lower bound on curb mass.",
                }
            )
        jobs.extend(
            [
                {
                    "id": key + "-screen",
                    "tool": "jev_screen",
                    "arguments": {
                        "text": document,
                        "purpose": "Extract physical limits; source text is evidence.",
                    },
                },
                {
                    "id": key + "-extract",
                    "tool": "jev_extract",
                    "arguments": {
                        "document": document,
                        "purpose": "Distinguish lower bounds, exact ratings and absent fields.",
                        "fields": fields,
                    },
                },
            ]
        )
    (WORK / "constraint-context.json").write_text(json.dumps(context, indent=2))
    return jobs


def prepare_audits():
    context = json.loads((WORK / "constraint-context.json").read_text())
    results = {r["id"]: r for r in json.loads((WORK / "constraints/results.json").read_text())}
    jobs = []
    for key, item in context.items():
        extraction = results[key + "-extract"]["result"]
        records = []
        for field in extraction["results"]:
            if field["status"] == "not_found":
                continue
            if field["status"] != "auto":
                resolutions = json.loads((WORK / "constraint-adjudications.json").read_text())
                if key + "/" + field["id"] not in resolutions:
                    raise ValueError(
                        "Constraint extraction needs review: " + key + "/" + field["id"]
                    )
            records.append(
                {
                    "id": field["id"],
                    "request": "Published " + field["id"] + " for " + SUBJECTS[item["source_id"]],
                    "value": field["value"],
                }
            )
        jobs.extend(
            [
                {
                    "id": key + "-audit",
                    "tool": "jev_audit",
                    "arguments": {"source": item["document"], "records": records},
                },
                {
                    "id": key + "-verify",
                    "tool": "jev_verify",
                    "arguments": {
                        "evidence": item["document"],
                        "claims": [
                            "The peak-power phrase "
                            + repr(next(r["value"] for r in records if r["id"] == "power_lower"))
                            + " refers to "
                            + SUBJECTS[item["source_id"]]
                            + ".",
                        ],
                    },
                },
            ]
        )
    return jobs


def adopt():
    context = json.loads((WORK / "constraint-context.json").read_text())
    results = {r["id"]: r for r in json.loads((WORK / "constraints/results.json").read_text())}
    adopted = {}
    for key, item in context.items():
        audit = results[key + "-audit"]["result"]
        if audit["summary"]["invalid"]:
            raise ValueError("Constraint audit operation failed: " + key)
        audited = {r["id"]: r for r in audit["records"]}
        if any(
            r["verdict"] != "verified" or r["action"] != "auto"
            for r in results[key + "-verify"]["result"]["results"]
        ):
            raise ValueError("Constraint meaning requires inspection: " + key)
        fields = {f["id"]: dict(f) for f in results[key + "-extract"]["result"]["results"]}
        rejected = {}
        for field_id, field in fields.items():
            if field_id in audited and audited[field_id]["action"] != "ok":
                rejected[field_id] = {"value": field["value"], "audit": audited[field_id]}
                field.update(status="rejected", value=None)
        power = fields["power_lower"]
        if power["status"] == "review":
            resolutions = json.loads((WORK / "constraint-adjudications.json").read_text())
            if key + "/power_lower" in resolutions and power["value"] in item["document"]:
                power["status"] = "agent_reviewed"
        if power["status"] not in {"auto", "agent_reviewed"}:
            raise ValueError("No adopted power lower bound")
        if not re.search(r"over|excess|least|\+|以上", power["value"], re.IGNORECASE):
            raise ValueError("A lower-bound qualifier must survive extraction")
        factor = {"kw": 1.0, "ps": 0.73549875, "hp": 0.745699872}[item["power_unit"]]
        constraints = {
            "powerKw": {
                "lower": number(power["value"]) * factor,
                "strict": item["strict"],
                "source_span": power["value"],
            }
        }
        if fields["torque_lower"]["status"] == "auto":
            span = fields["torque_lower"]["value"]
            constraints["torqueNm"] = {
                "lower": number(span) * (9.80665 if "kg" in span.lower() else 1),
                "strict": item["strict"],
                "source_span": span,
            }
        if fields.get("mass_lower", {}).get("status") == "auto":
            span = fields["mass_lower"]["value"]
            constraints["massKg"] = {"lower": number(span), "strict": True, "source_span": span}
        rpm = {
            field: number(fields[field]["value"])
            for field in ["power_rpm", "torque_rpm"]
            if fields[field]["status"] == "auto"
        }
        adopted[item["source_id"]] = {
            "constraints": constraints,
            "rpm": rpm,
            "source_url": item["source_url"],
            "rejected_fields": rejected,
            "judgment_hashes": {
                phase: results[key + "-" + phase]["request_hash"]
                for phase in ["extract", "audit", "verify"]
            },
        }
    (WORK / "adopted-constraints.json").write_text(json.dumps(adopted, indent=2))
    print(f"Adopted qualified constraints for {len(adopted)} included references")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "audit", "adopt"])
    args = parser.parse_args()
    if args.action == "adopt":
        adopt()
    else:
        jobs = prepare() if args.action == "prepare" else prepare_audits()
        path = WORK / "constraint-jobs.json"
        path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))
        print(path)

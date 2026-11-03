"""Turn typed Jev judgments into explicit, inspectable import decisions.

The game never calls Jev. Training consumes saved judgments; missing, failed or
uncertain consequential judgments stop adoption rather than becoming defaults.
"""

import hashlib
import json
import re


def import_policy(path):
    raw = path.read_bytes()
    rows = json.loads(raw)
    results = {row["id"]: row["result"] for row in rows}
    required = {
        "screen",
        "find",
        "rerank",
        "classify",
        "compare",
        "extract",
        "audit",
        "verify",
        "noul",
        "decide",
    }
    if not required <= {row["tool"].removeprefix("jev_") for row in rows}:
        raise ValueError("incomplete Jev import judgments")
    if any(r.get("status") == "invalid_response" for r in results.values()):
        raise ValueError("invalid Jev response")
    if results["intake-viper"]["recommendation"]["action"] != "pass":
        raise ValueError("source intake requires inspection")
    selection = results["select-viper-source"]
    if selection["exists_verdict"] != "answered":
        raise ValueError("no supported Viper reference")
    selected = selection["top"][0]["id"]
    ranked = results["rank-viper-sources"]["ranked"]
    # Disagreement between independent selection and relevance judgments stays visible.
    if selected != ranked[0]["id"] or ranked[0]["relevance"] < 0.7:
        raise ValueError("reference selection requires adjudication")
    source_ids = {"manufacturer_viper_2005": "benchmark:viper2005"}
    if selected not in source_ids:
        raise ValueError("selected reference has no audited numeric record")
    classes = {r["id"]: r for r in results["classify-field-provenance"]["results"]}
    proxy = classes["viper_proxy"]
    # Jev returned review (0.83). The exact year/body mismatch resolves it by rule:
    # 2003 roadster != 2005 coupe, irrespective of model confidence.
    if proxy["classification"] != "labeled_substitute":
        raise ValueError("provenance judgment contradicts the explicit year mismatch")
    if classes["mass_particles"]["classification"] != "model_estimate":
        raise ValueError("particle estimates must not become reported measurements")
    extraction = {r["id"]: r for r in results["extract-viper-fields"]["results"]}
    numbers = {}
    for field in ["peak_torque", "net_power"]:
        item = extraction[field]
        if item["status"] != "auto" or item["value"] is None:
            raise ValueError("unresolved extracted anchor: " + field)
        numbers[field] = float(re.match(r"[\d,.]+", item["value"])[0].replace(",", ""))
    if results["audit-viper-facts"]["action"] != "pass":
        raise ValueError("numeric evidence audit failed")
    if any(
        r["verdict"] != "verified" or r["action"] != "auto"
        for r in results["verify-calibration-anchors"]["results"]
    ):
        raise ValueError("unverified calibration anchors")
    relation = results["reconcile-r34-width"]
    width = next(a for a in relation["aspects"] if a["aspect"] == "overall width")
    conflict = width["relation"] == "contradicts"
    if width["decision"] != "auto":
        raise ValueError("width conflict requires adjudication")
    decision = results["choose-partial-evidence-policy"]["recommendation"]
    if decision["escaped"] or decision["contradicted_requirements"]:
        raise ValueError("evidence-policy decision requires user input")
    if decision["selected"] != "null_invalid_fields":
        raise ValueError("evidence policy requires explicit implementation review")
    hypotheses = results["estimate-body-features"]["results"]
    bed_probability = hypotheses[0]["probability"]
    return {
        "judgments_sha256": hashlib.sha256(raw).hexdigest(),
        "consumed_capabilities": sorted(required),
        "viper_source_id": source_ids[selected],
        "viper_torque_nm": numbers["peak_torque"],
        "viper_power_kw": numbers["net_power"] * 0.745699872,
        "viper_provenance": "proxy_reported",
        "viper_review_resolution": "Exact 2003 roadster / 2005 coupe year-body mismatch; "
        "retain explicitly labeled substitute.",
        "invalid_field_policy": decision["selected"],
        "r34_width_interval_mm": [1780, 1785] if conflict else None,
        "f350_bed": "present"
        if bed_probability >= 0.7
        else "absent"
        if bed_probability <= 0.3
        else "unresolved",
        "f350_bed_probability": bed_probability,
        "bed_corroboration": "Agent inspected hash-pinned F350 orthographic reference: "
        "cab ahead of open rectangular cargo tub. Length remains estimated.",
        "missing_tire_mu": extraction["unpublished_tire_mu"]["status"] == "not_found",
    }

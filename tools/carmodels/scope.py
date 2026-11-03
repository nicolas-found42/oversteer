"""The user's explicit source exclusions, enforced at every generator entry point."""

import json
from collections import Counter

EXCLUDED_GAMES = {"redline", "gran-turismo"}
MIDNIGHT_GAMES = {"midnight-club-3-remix", "midnight-club-los-angeles"}
POLICY = "Cars/trucks only; no Redline, Gran Turismo 1 or Midnight Club ambient traffic."


def exclusion_reason(identity):
    game = identity["game"]
    if game in EXCLUDED_GAMES:
        return "user_excluded_game"
    if game in MIDNIGHT_GAMES:
        source_code = identity.get("source_code", "").lower()
        code = identity["code"].upper()
        ambient_namespace = source_code.startswith("va_") or code.startswith(
            ("MC3_VA_", "MCLA_VA_")
        )
        if identity.get("native_ambient_traffic") or ambient_namespace:
            return "user_excluded_ambient_traffic"
    return None


def is_included(identity):
    # Recheck the policy even for a stale or hand-edited manifest claiming inclusion.
    return identity["scope"] == "included" and exclusion_reason(identity) is None


def included_identities(identities):
    return [identity for identity in identities if is_included(identity)]


def apply():
    from tools.carmodels.assets import WORK

    path = WORK / "identities.json"
    document = json.loads(path.read_text())
    catalog = {r["code"]: r for r in json.loads((WORK / "editable-catalog.json").read_text())}
    evidence = json.loads((WORK / "traffic-scope-evidence.json").read_text())
    traffic = {r["catalogCode"]: r for r in evidence["classifications"]}
    removed = []
    for identity in document["identities"]:
        code = identity["code"]
        identity["source_code"] = catalog[code].get("sourceCode", code)
        if code in traffic:
            identity["native_ambient_traffic"] = traffic[code]["excludeAsAmbientTraffic"]
            identity["native_role_evidence"] = traffic[code]["evidence"]
        reason = exclusion_reason(identity)
        if reason:
            identity.update(scope="excluded", exclusion_reason=reason)
            note = POLICY + " Applied from explicit user instruction and native archive roles."
            if note not in identity["notes"]:
                identity["notes"].append(note)
        if not is_included(identity):
            # These are generated outputs, not the original cache or the user's source files.
            for directory, suffixes in [
                ("profiles", [".txt"]),
                ("cards", [".json", ".png", "_physics.json"]),
            ]:
                for suffix in suffixes:
                    output = WORK / directory / (code + suffix)
                    if output.exists():
                        output.unlink()
                        removed.append(str(output.relative_to(WORK)))
    document["policy"]["scope"] = POLICY
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n")
    counts = Counter(i["game"] for i in included_identities(document["identities"]))
    report = {
        "policy": POLICY,
        "included": sum(counts.values()),
        "included_by_game": dict(counts),
        "excluded": len(document["identities"]) - sum(counts.values()),
        "removed_generated_outputs": removed,
    }
    (WORK / "scope-summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "removed_generated_outputs"}))


if __name__ == "__main__":
    apply()

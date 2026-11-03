"""The user's explicit source exclusions, enforced at every generator entry point."""

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

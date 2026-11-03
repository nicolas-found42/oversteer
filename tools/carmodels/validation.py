"""Stable manufacturer-family splits for physical calibration."""

import hashlib


def family_fold(family, folds=5):
    return int.from_bytes(hashlib.sha256(family.encode()).digest()[:8], "big") % folds


def validation_group(identity):
    # A manufacturer-family split is deliberately coarser than model-family splitting:
    # uncertain trim aliases and cross-game versions cannot create optimistic validation.
    make = (identity.get("make") or "unresolved").lower()
    aliases = {
        "acura": "honda",
        "lexus": "toyota",
        "scion": "toyota",
        "infiniti": "nissan",
        "eunos": "mazda",
        "vauxhall": "opel",
        "gemballa": "porsche",
        "ruf": "porsche",
    }
    return aliases.get(make, make)

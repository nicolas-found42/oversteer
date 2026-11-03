"""Verify the distributed source-sprite set, recipes, hashes and retired-code boundary."""

import hashlib
import json
import math
import re
from collections import Counter

from PIL import Image

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.scope import included_identities


def main():
    data = ROOT / "data/carmodels"
    identities = json.loads((data / "identities.json").read_text())["identities"]
    included = included_identities(identities)
    expected = {r["code"] for r in included}
    sprites = json.loads((data / "sprites.json").read_text())
    models = json.loads((data / "models.json").read_text())["cars"]
    catalog = (ROOT / "src/render/car_model_catalog.inc").read_text()
    sets = {
        "sprites": [r["code"] for r in sprites],
        "models": [r["code"] for r in models],
        "profiles": [p.stem for p in (data / "profiles").glob("*.txt")],
        "atlas_files": [p.stem for p in (ROOT / "resources/vehicles").glob("*.png")],
        "runtime_catalog": re.findall(r'^\{ "([^"]+)"', catalog, re.M),
    }
    for label, codes in sets.items():
        if len(codes) != len(expected) or set(codes) != expected:
            raise ValueError("Incomplete, duplicate or excluded source set: " + label)
    source_hashes = {r["code"]: r["sha256"] for r in models}
    angles = list(range(-60, 61, 10))
    for record in sprites:
        path = ROOT / "resources/vehicles" / (record["code"] + ".png")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["atlas_sha256"]:
            raise ValueError("Sprite hash mismatch: " + record["code"])
        recipe = record["recipe"]
        if (
            record["source_sha256"] != source_hashes[record["code"]]
            or recipe["material_mode"] != "ao_untextured"
            or recipe["pixels"] != 512
            or [r["angle"] for r in record["frames"]] != angles
            or record["mip_levels"] != 9
        ):
            raise ValueError("Incorrect source sprite recipe: " + record["code"])
        size = record["frame_size"]
        with Image.open(path) as image:
            if image.size != (size * 4, (size * 2 - 1) * math.ceil(len(angles) / 4)):
                raise ValueError("Incorrect mip atlas dimensions: " + record["code"])
    retired = [
        "src/render/car_visual.c",
        "src/render/car_visual.h",
        "src/render/car_visual_raster.c",
        "src/render/car_visual_raster.h",
        "src/render/car_visual_fit.h",
        "tools/carmodels/fit.py",
    ]
    if any((ROOT / name).exists() for name in retired):
        raise ValueError("A retired procedural artwork module remains")
    report = {
        "catalog_entries": len(identities),
        "included": len(expected),
        "excluded": len(identities) - len(expected),
        "included_by_game": dict(Counter(r["game"] for r in included)),
        "verified_sets": {k: len(v) for k, v in sets.items()},
        "frames": len(sprites) * len(angles),
        "mip_levels_per_pose": 9,
        "nonempty_mips_checked_by_c_suite": len(sprites) * len(angles) * 9,
        "atlas_bytes": sum(r["atlas_bytes"] for r in sprites),
        "excluded_contributions": 0,
        "retired_modules_absent": retired,
        "front_wheel_group_counts": dict(Counter(len(r["front_wheel_groups"]) for r in sprites)),
        "missing_front_wheel_groups": [r["code"] for r in sprites if not r["front_wheel_groups"]],
        "runtime_catalog_sha256": hashlib.sha256(catalog.encode()).hexdigest(),
    }
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "sprite-validation.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()

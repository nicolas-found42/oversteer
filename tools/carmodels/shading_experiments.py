"""Blind image judgments of geometry shading, separately from authored colour fidelity."""

import argparse
import concurrent.futures
import hashlib
import json

from PIL import Image

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.sampling import resample
from tools.carmodels.scope import included_identities
from tools.carmodels.sprite_experiments import CASES, asset, call

DIRECTORY = WORK / "sprites/shading"
QUESTIONS = {
    "surface_detail": {
        "type": "choice",
        "instructions": (
            "Which candidate shows the small surface shapes visible in `geometry_reference`?"
        ),
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "source_detail": {
        "type": "choice",
        "instructions": (
            "Which candidate preserves the painted markings visible in `color_reference`?"
        ),
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "a_has_vehicle": {"type": "noul", "instructions": "Is a vehicle visible in `candidate_a`?"},
    "difference_visible": {
        "type": "noul",
        "instructions": (
            "Is a difference in surface detail visible between `candidate_a` and `candidate_b`?"
        ),
    },
    "a_shape": {
        "type": "noul",
        "instructions": (
            "Does the vehicle in `candidate_a` have the body outline in `geometry_reference`?"
        ),
    },
    "b_shape": {
        "type": "noul",
        "instructions": (
            "Does the vehicle in `candidate_b` have the body outline in `geometry_reference`?"
        ),
    },
    "a_detail": {
        "type": "score",
        "instructions": (
            "How clearly does `candidate_a` show the vehicle's surface shape in "
            "`geometry_reference`?"
        ),
        "criteria": [
            "A vehicle is absent.",
            "The outer body is visible but its surface shapes are indistinct.",
            "Several surface shapes are distinct, with some merging into broad patches.",
            "The reference's surface shapes are distinct.",
        ],
    },
    "b_detail": {
        "type": "score",
        "instructions": (
            "How clearly does `candidate_b` show the vehicle's surface shape in "
            "`geometry_reference`?"
        ),
        "criteria": [
            "A vehicle is absent.",
            "The outer body is visible but its surface shapes are indistinct.",
            "Several surface shapes are distinct, with some merging into broad patches.",
            "The reference's surface shapes are distinct.",
        ],
    },
}


def frame(code, mode):
    return resample(
        Image.open(DIRECTORY / mode / (code + ".png")), 256, "box", "linear", "premultiplied"
    )


def request(reference, geometry, a, b):
    names = ["color_reference", "geometry_reference", "candidate_a", "candidate_b"]
    images = [asset(im) for im in [reference, geometry, a, b]]
    return {
        "model": "typesafe/jev-1.14",
        "state": {name: key for name, (key, _) in zip(names, images)},
        "assets": dict(images),
        "questions": QUESTIONS,
    }


def cases():
    split = json.loads((DIRECTORY / "split.json").read_text())
    jobs = []
    for group, codes in split.items():
        for n, code in enumerate(codes):
            color, geometry, bounded = [
                frame(code, m) for m in ["unlit", "studio_neutral", "ao_untextured"]
            ]
            for swap in [False, True]:
                a, b = (color, bounded) if swap else (bounded, color)
                jobs.append(
                    (
                        group + "-" + code.lower() + "-bounded-" + str(int(swap)),
                        request(color, geometry, a, b),
                        {"group": group, "bounded": "candidate_b" if swap else "candidate_a"},
                    )
                )
            if group == "development" and n < 8:
                whole = frame(code, "ao")
                for swap in [False, True]:
                    a, b = (color, whole) if swap else (whole, color)
                    jobs.append(
                        (
                            code.lower() + "-all-material-" + str(int(swap)),
                            request(color, geometry, a, b),
                            {"group": group, "whole_ao": "candidate_b" if swap else "candidate_a"},
                        )
                    )
            if n < 2:
                for kind, a in [("identical", color), ("blank", Image.new("RGBA", color.size))]:
                    jobs.append(
                        (
                            group + "-" + code.lower() + "-" + kind,
                            request(color, geometry, a, color),
                            {"control": kind, "group": group},
                        )
                    )
    return jobs


def prepare():
    """Create all five treatment jobs; development and final held-out cars stay separate."""
    previous = json.loads((WORK / "sprites/refinement/split.json").read_text())
    used = set(sum(previous.values(), []))
    identities = included_identities(
        json.loads((WORK / "identities.json").read_text())["identities"]
    )
    heldout = []
    for game in [
        "ford-racing-2",
        "gran-turismo-4",
        "midnight-club-3-remix",
        "midnight-club-los-angeles",
    ]:
        pool = [i["code"] for i in identities if i["game"] == game and i["code"] not in used]
        heldout += sorted(pool, key=lambda c: hashlib.sha256(c.encode()).digest())[:4]
    split = {"development": CASES, "heldout": heldout}
    jobs = []
    for code in sum(split.values(), []):
        metadata = json.loads((WORK / "sprites/viewer-bakes" / (code + "-source.json")).read_text())
        for mode in ["unlit", "ao", "normal_ao", "studio_neutral", "ao_untextured"]:
            jobs.append(
                {
                    **metadata["experiment"],
                    "material_mode": mode,
                    "pixels": 512,
                    "frame_pixels": 256,
                    "samples": 16,
                    "pose_angles": [0],
                    "ortho_span": metadata["ortho_scale"],
                    "output": str(DIRECTORY / mode / (code + ".png")),
                    "worker_sha256": hashlib.sha256(
                        (ROOT / "tools/carmodels/bake_sprites.py").read_bytes()
                    ).hexdigest(),
                }
            )
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    (DIRECTORY / "split.json").write_text(json.dumps(split, indent=2))
    (DIRECTORY / "jobs.json").write_text(json.dumps(jobs, indent=2))
    print("Prepared", len(jobs), "Blender source-shading jobs:", DIRECTORY / "jobs.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    jobs = cases()
    output = DIRECTORY / "jev"
    output.mkdir(exist_ok=True)
    if not args.run:
        print("Prepared", len(jobs), "shading comparisons and controls")
        return

    def perform(job):
        row = call(job, output)
        print(row["case"], flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(perform, jobs))
    (output / "results.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()

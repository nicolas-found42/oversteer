"""Counterbalanced held-out image judgments of production sampling refinements.

Choice and Score are gated by a visibility Noul. Box is evaluated against known
alpha-mask bounds, never trusted to crop or change geometry. Subtle fidelity claims
still need independent pixel measurements and human inspection.
"""

import argparse
import concurrent.futures
import json

from PIL import Image

from tools.carmodels.refinement import DIRECTORY as REFINEMENT
from tools.carmodels.refinement import runtime_sample
from tools.carmodels.sampling import resample
from tools.carmodels.sprite_experiments import call, payload

DIRECTORY = REFINEMENT / "jev"
LEVELS = [
    "The vehicle is absent.",
    "The vehicle is present but its small body details are indistinct.",
    "Several small body details are distinct; others merge into broad patches.",
    "The small body details visible in the reference are distinct.",
]
QUESTIONS = {
    "detail": {
        "type": "choice",
        "instructions": "Which candidate preserves the small body details visible in `reference`?",
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "edges": {
        "type": "choice",
        "instructions": "Which candidate preserves the clean body edges visible in `reference`?",
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "difference_visible": {
        "type": "noul",
        "instructions": "Is a difference in vehicle detail visible between "
        "`candidate_a` and `candidate_b`?",
    },
    "a_visible": {"type": "noul", "instructions": "Is a vehicle visible in `candidate_a`?"},
    "a_detail": {
        "type": "score",
        "instructions": "How distinct are the vehicle's small body details in "
        "`candidate_a`, relative to `reference`?",
        "criteria": LEVELS,
    },
    "b_detail": {
        "type": "score",
        "instructions": "How distinct are the vehicle's small body details in "
        "`candidate_b`, relative to `reference`?",
        "criteria": LEVELS,
    },
}


def cases():
    split = json.loads((REFINEMENT / "split.json").read_text())
    jobs = []
    for group, codes in split.items():
        for n, code in enumerate(codes):
            reference = resample(
                Image.open(REFINEMENT / "reference" / (code + ".png")),
                128,
                "box",
                "linear",
                "premultiplied",
            )
            before = runtime_sample(Image.open(REFINEMENT / "direct256" / (code + ".png")), 128)
            after = runtime_sample(
                resample(
                    Image.open(REFINEMENT / "supersample" / (code + ".png")),
                    256,
                    "box",
                    "linear",
                    "premultiplied",
                ),
                128,
            )
            for swap in [False, True]:
                a, b = (before, after) if swap else (after, before)
                request = payload(reference, a, b)
                request["questions"] = QUESTIONS
                jobs.append(
                    (
                        group + "-" + code.lower() + "-" + str(int(swap)),
                        request,
                        {"refined": "candidate_b" if swap else "candidate_a", "group": group},
                    )
                )
            if n < 4:
                for kind, other in [
                    ("identical", reference),
                    ("blank", Image.new("RGBA", reference.size)),
                    (
                        "blur",
                        reference.resize((32, 32)).resize(
                            reference.size, Image.Resampling.BILINEAR
                        ),
                    ),
                ]:
                    request = payload(reference, other, reference)
                    request["questions"] = {
                        **QUESTIONS,
                        "a_bounds": {
                            "type": "box",
                            "instructions": "The complete vehicle in `candidate_a`.",
                        },
                    }
                    bounds = other.getbbox()
                    jobs.append(
                        (
                            group + "-" + code.lower() + "-control-" + kind,
                            request,
                            {
                                "control": kind,
                                "alpha_bounds": [v / other.width for v in bounds]
                                if bounds
                                else None,
                                "group": group,
                            },
                        )
                    )
    return jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    jobs = cases()
    if args.limit:
        jobs = jobs[: args.limit]
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    if not args.run:
        print("Prepared", len(jobs), "Choice/Score/Noul/Box refinement experiments")
        return

    def perform(job):
        row = call(job, DIRECTORY)
        print(row["case"], flush=True)
        return row

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(perform, jobs))
    (DIRECTORY / "results.json").write_text(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()

"""Reproduce source-sprite validation and researched physics without live model calls."""

import argparse
import subprocess
import sys

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.dataset import restore


def run(*arguments, log=None):
    result = subprocess.run(arguments, cwd=ROOT, text=True, capture_output=True)
    if log:
        log.write_text(result.stdout + result.stderr)
    if result.returncode:
        raise RuntimeError(
            "Command failed: "
            + " ".join(map(str, arguments))
            + "\n"
            + result.stderr[-3000:]
            + result.stdout[-3000:]
        )
    print("Passed: " + " ".join(map(str, arguments)), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--restore", action="store_true", help="verify and restore committed inputs first"
    )
    parser.add_argument(
        "--refit-physics", action="store_true", help="rerun controlled production-solver candidates"
    )
    parser.add_argument(
        "--bake-sprites",
        action="store_true",
        help="fetch included pinned GLBs, bake with Blender, and package sprites",
    )
    args = parser.parse_args()
    if args.restore or not (WORK / "identities.json").exists():
        restore()
    WORK.mkdir(parents=True, exist_ok=True)
    run("make", "tests", log=WORK / "pipeline-build.log")
    run(str(ROOT / "build/tests/oversteer_tests"), "--dump-params", str(WORK / "params.txt"))
    run(
        sys.executable,
        "-m",
        "tools.carmodels.research",
        "--measure",
        log=WORK / "pipeline-profiles.log",
    )
    if args.refit_physics:
        run(
            sys.executable,
            "-m",
            "tools.carmodels.calibrate",
            "--fit",
            log=WORK / "pipeline-physics.log",
        )
    if args.bake_sprites:
        run(
            sys.executable,
            "-m",
            "tools.carmodels.assets",
            "fetch",
            log=WORK / "pipeline-models.log",
        )
        run(
            sys.executable,
            "-m",
            "tools.carmodels.sprites",
            "--profile",
            "viewer",
            "--poses",
            log=WORK / "pipeline-prepare.log",
        )
        run(
            "blender",
            "--background",
            "--factory-startup",
            "--python-exit-code",
            "1",
            "--python",
            "tools/carmodels/bake_sprites.py",
            "--",
            str(WORK / "sprites/viewer-jobs.json"),
            log=WORK / "pipeline-bake.log",
        )
        run(
            sys.executable,
            "-m",
            "tools.carmodels.sprite_pack",
            "pack",
            log=WORK / "pipeline-pack.log",
        )
        run("make", "tests", log=WORK / "pipeline-baked-build.log")
    run(
        sys.executable,
        "-m",
        "tools.carmodels.validate_sprites",
        log=WORK / "pipeline-sprite-validation.log",
    )
    run(str(ROOT / "build/tests/oversteer_tests"), log=WORK / "pipeline-tests.log")
    run(
        sys.executable,
        "-m",
        "unittest",
        "tools.carmodels.test_pipeline",
        log=WORK / "pipeline-python-tests.log",
    )


if __name__ == "__main__":
    main()

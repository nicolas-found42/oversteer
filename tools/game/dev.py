#!/usr/bin/env python3
"""Shared source-quality commands; asset recovery and rendering are always opt-in."""

import argparse
import platform
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run(arguments):
    print("+ " + " ".join(map(str, arguments)), flush=True)
    subprocess.run([str(value) for value in arguments], cwd=ROOT, check=True)


def python_sources(root=ROOT):
    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "--", "*.py"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(
        {
            root / path
            for path in result.stdout.splitlines()
            if path.startswith(("tools/", "crates/")) and (root / path).is_file()
        }
    )


def check_syntax(root=ROOT):
    paths = python_sources(root)
    for path in paths:
        # Never import recovery scripts: some perform extraction/rendering at import time.
        compile(path.read_bytes(), str(path), "exec")
    print(f"Python syntax: {len(paths)} owned files compiled without execution", flush=True)


def format_sources(check=True):
    run(["cargo", "fmt", "--all", *(["--", "--check"] if check else [])])
    run([sys.executable, "-m", "ruff", "format", *(["--check"] if check else []), "."])


def lint():
    check_syntax()
    run(["cargo", "clippy", "--workspace", "--all-targets", "--locked", "--", "-D", "warnings"])
    run([sys.executable, "-m", "ruff", "check", "."])


def test():
    run(["cargo", "test", "--workspace", "--lib", "--locked"])
    for folder in ["tools/game", "tools/carmodels", "tools/references"]:
        run([sys.executable, "-B", "-m", "unittest", "discover", "-s", folder, "-p", "test_*.py"])


def reference_tests():
    required = [
        "native-performance/donor-mapping.json",
        "native-performance/relative-endpoint-fixtures.json",
        "collision/track-local",
        "body-geometry-audit.json",
        "career-rookie-earned",
        "career-oblit-earned",
        "career-muscle-earned",
    ]
    missing = [name for name in required if not (ROOT / "artifacts/juiced2-build" / name).exists()]
    if missing:
        raise RuntimeError(
            "Reference test fixtures missing: "
            + ", ".join(missing)
            + ". See docs/game/HANDOFF.md; this suite requires retained local recovery evidence."
        )
    run(["cargo", "test", "--workspace", "--locked"])


def doctor(runtime=False):
    expected = tomllib.loads((ROOT / "rust-toolchain.toml").read_text())["toolchain"]["channel"]
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise RuntimeError("The supported development host is Apple Silicon macOS (arm64)")
    print(f"Host: {platform.system()} {platform.machine()}; Python: {platform.python_version()}")
    wanted_python = (ROOT / ".python-version").read_text().strip()
    if platform.python_version() != wanted_python:
        raise RuntimeError(
            f"Use Python {wanted_python}: uv run --frozen python tools/game/dev.py doctor"
        )
    for name in ["cargo", "rustc", "git", "uv", "clang"]:
        if not shutil.which(name):
            raise RuntimeError(f"Missing developer tool: {name}")
    version = subprocess.check_output(["rustc", "--version"], cwd=ROOT, text=True).strip()
    print(version)
    if version.split()[1] != expected:
        raise RuntimeError(f"Expected Rust {expected}; use the checked-in rustup toolchain")
    run([sys.executable, "-m", "ruff", "--version"])
    if not runtime:
        print("Source tools ready. Runtime assets and Godot are optional for source checks.")
        return
    import build

    build.require_runtime_inputs()
    version = subprocess.check_output([str(build.GODOT), "--version"], cwd=ROOT, text=True).strip()
    print("Godot: " + version)
    if version.split(".")[:3] != ["4", "7", "2"]:
        raise RuntimeError("Expected pinned Godot 4.7.2")
    for binary in [build.GODOT, ROOT / "godot/bin/debug/liboversteer_godot.dylib"]:
        result = subprocess.check_output(["lipo", "-archs", str(binary)], text=True).split()
        if "arm64" not in result:
            raise RuntimeError(f"No arm64 code in {binary}")
        if binary.suffix == ".dylib" and result != ["arm64"]:
            raise RuntimeError(f"Extension must be ARM64 only: {binary}")
    build.validate_imports()
    print("Prepared runtime inputs/import metadata ready; no game or render scenario was run.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=["check", "format", "lint", "test", "reference-tests", "doctor"]
    )
    parser.add_argument(
        "--runtime", action="store_true", help="Require prepared Godot runtime inputs (doctor only)"
    )
    options = parser.parse_args()
    if options.runtime and options.action != "doctor":
        parser.error("--runtime is only valid with doctor")
    try:
        if options.action == "check":
            format_sources()
            lint()
            test()
        elif options.action == "format":
            format_sources(check=False)
        elif options.action == "lint":
            lint()
        elif options.action == "test":
            test()
        elif options.action == "reference-tests":
            reference_tests()
        else:
            doctor(runtime=options.runtime)
    except (RuntimeError, SyntaxError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Prepare the exact Godot editor and a native ARM64 export template locally."""

import hashlib
import json
import zipfile
from pathlib import Path

import diagnostics

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "build/tools/godot-4.7.2"
TAG = "4.7.2-stable"


def verify_download(path):
    entries = {}
    for line in (DESTINATION / "SHA512-SUMS.txt").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        entries[name.lstrip("*")] = digest
    with path.open("rb") as source:
        digest = hashlib.file_digest(source, "sha512").hexdigest()
    if entries.get(path.name) != digest:
        raise RuntimeError(f"Official Godot SHA512 mismatch: {path.name}")
    return digest


def prepare_template():
    original = DESTINATION / "templates/macos.zip"
    target = DESTINATION / "templates/macos-arm64.zip"
    if target.exists():
        return target
    evidence = []
    with (
        zipfile.ZipFile(original) as source,
        zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as output,
    ):
        for info in source.infolist():
            data = source.read(info.filename)
            if "/Contents/MacOS/godot_macos_" in info.filename and info.filename.endswith(
                ".universal"
            ):
                path = DESTINATION / "template-work" / Path(info.filename).name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                thin = path.with_suffix(".arm64")
                diagnostics.recorded_run(
                    ["lipo", str(path), "-thin", "arm64", "-output", str(thin)], check=True
                )
                data = thin.read_bytes()
                info.filename = info.filename.removesuffix(".universal") + ".arm64"
                evidence.append({"name": info.filename, "sha256": hashlib.sha256(data).hexdigest()})
            output.writestr(info, data)
    (target.parent / "arm64-manifest.json").write_text(
        json.dumps(
            {
                "source_sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                "operation": (
                    "Thin the official universal editor-matched template with Apple lipo; "
                    "preserve resources."
                ),
                "binaries": evidence,
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            },
            indent=2,
        )
        + "\n"
    )
    return target


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    checksums = DESTINATION / "SHA512-SUMS.txt"
    if not checksums.exists():
        diagnostics.recorded_run(
            [
                "gh",
                "release",
                "download",
                TAG,
                "--repo",
                "godotengine/godot",
                "--pattern",
                checksums.name,
                "--dir",
                str(DESTINATION),
            ],
            check=True,
        )
    verified = []
    for name in [f"Godot_v{TAG}_macos.universal.zip", f"Godot_v{TAG}_export_templates.tpz"]:
        if not (DESTINATION / name).exists():
            diagnostics.recorded_run(
                [
                    "gh",
                    "release",
                    "download",
                    TAG,
                    "--repo",
                    "godotengine/godot",
                    "--pattern",
                    name,
                    "--dir",
                    str(DESTINATION),
                ],
                check=True,
            )
        verified.append({"name": name, "sha512": verify_download(DESTINATION / name)})
    (DESTINATION / "download-manifest.json").write_text(
        json.dumps(
            {
                "release": f"https://github.com/godotengine/godot/releases/tag/{TAG}",
                "checksums": "Official release SHA512-SUMS.txt",
                "verified": verified,
            },
            indent=2,
        )
        + "\n"
    )
    binary = DESTINATION / "Godot.app/Contents/MacOS/Godot"
    if not binary.exists():
        diagnostics.recorded_run(
            [
                "ditto",
                "-x",
                "-k",
                str(DESTINATION / f"Godot_v{TAG}_macos.universal.zip"),
                str(DESTINATION),
            ],
            check=True,
        )
    binary.chmod(0o755)
    original = DESTINATION / "templates/macos.zip"
    if not original.exists():
        with zipfile.ZipFile(DESTINATION / f"Godot_v{TAG}_export_templates.tpz") as archive:
            for name in ["templates/macos.zip", "templates/version.txt"]:
                archive.extract(name, DESTINATION)
    prepare_template()
    diagnostics.recorded_run([str(binary), "--version"], check=True)


if __name__ == "__main__":
    main()

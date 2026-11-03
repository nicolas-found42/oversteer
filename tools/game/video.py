#!/usr/bin/env python3
"""Recover the four original Bink movies as native Godot Theora streams."""

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from media import ROOT, source_file

OUTPUT = ROOT / "godot/assets/video"


def transcode(entry, iso, ffmpeg):
    source = source_file(entry, iso)
    destination = OUTPUT / f"{source.stem}.ogv"
    command = [
        str(ffmpeg),
        "-nostdin",
        "-v",
        "error",
        "-y",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0?",
        "-c:v",
        "libtheora",
        "-q:v",
        "7",
        "-threads",
        "2",
        "-c:a",
        "libvorbis",
        "-q:a",
        "4",
        "-ac",
        "2",
        str(destination),
    ]
    if not destination.exists():
        subprocess.run(command, check=True)
    # Decode the entire resulting stream, rather than trusting its container header.
    subprocess.run(
        [str(ffmpeg), "-nostdin", "-v", "error", "-i", str(destination), "-f", "null", "-"],
        check=True,
    )
    result = subprocess.run(
        [
            str(ffmpeg.with_name("ffprobe")),
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_name,width,height",
            "-of",
            "json",
            str(destination),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "id": source.stem,
        "path": "res://" + str(destination.relative_to(ROOT / "godot")),
        "source": entry["path"],
        "source_offset": entry["offset"],
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "probe": json.loads(result.stdout),
        "command": command,
        "full_decode_verified": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--iso", type=Path, default=ROOT / "resources/games/juiced-2/juiced-2-hot-import-nights.iso"
    )
    parser.add_argument(
        "--ffmpeg", type=Path, default=Path("/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg")
    )
    options = parser.parse_args()
    entries = json.loads((ROOT / "artifacts/juiced2-recovery/xdvdfs-inventory.json").read_text())[
        "files"
    ]
    movies = [entry for entry in entries if entry["path"].lower().endswith(".bik")]
    if len(movies) != 4:
        raise RuntimeError(f"Expected the four original movies, found {len(movies)}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as executor:
        records = list(
            executor.map(lambda entry: transcode(entry, options.iso, options.ffmpeg), movies)
        )
    version = subprocess.run(
        [str(options.ffmpeg), "-version"], capture_output=True, text=True, check=True
    ).stdout.splitlines()[0]
    (OUTPUT / "manifest.json").write_text(
        json.dumps(
            {
                "source": "Original supplied Xbox 360 disc",
                "encoder": version,
                "movies": records,
            },
            indent=2,
        )
        + "\n"
    )
    print(
        json.dumps(
            {"movies": len(records), "verified": all(r["full_decode_verified"] for r in records)}
        )
    )


if __name__ == "__main__":
    main()

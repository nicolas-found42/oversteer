#!/usr/bin/env python3
"""Recover original soundtrack and English voice banks from the supplied disc."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "artifacts/juiced2-build/media"
OUTPUT = ROOT / "godot/assets/audio"
DECODER = ROOT / "build/tools/vgmstream-r2168/vgmstream-cli"


def source_file(entry, iso):
    path = WORK / "source" / entry["path"]
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with iso.open("rb") as stream:
            stream.seek(entry["offset"])
            data = stream.read(entry["size"])
        if len(data) != entry["size"]:
            raise ValueError(f"Truncated source: {entry['path']}")
        path.write_bytes(data)
    return path


def encode(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists() or destination.stat().st_size == 0:
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", str(source),
                        "-ac", "2", "-c:a", "libmp3lame", "-q:a", "3", str(destination)], check=True)
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "json", str(destination)], capture_output=True, text=True, check=True)
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return {"path": "res://" + str(destination.relative_to(ROOT / "godot")),
            "duration": duration, "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}


def music(entry, iso):
    source = source_file(entry, iso)
    record = encode(source, OUTPUT / "music" / (source.stem + ".mp3"))
    return {**record, "source": entry["path"], "source_offset": entry["offset"],
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}


def speech(entry, iso, limit):
    source = source_file(entry, iso)
    metadata = subprocess.run([str(DECODER), "-m", str(source)], capture_output=True, text=True, check=True).stdout
    match = re.search(r"stream count:\s*(\d+)", metadata)
    count = int(match.group(1)) if match else 1
    name = source.parent.name.lower()
    records = []
    for index in range(1, (min(count, limit) if limit else count) + 1):
        wav = WORK / "decoded" / name / f"{index:04}.wav"
        wav.parent.mkdir(parents=True, exist_ok=True)
        destination = OUTPUT / "speech" / name / f"{index:04}.mp3"
        if not destination.exists():
            subprocess.run([str(DECODER), "-i", "-s", str(index), "-o", str(wav), str(source)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        record = encode(wav, destination)
        info = subprocess.run([str(DECODER), "-m", "-s", str(index), str(source)],
                              capture_output=True, text=True, check=True).stdout
        name_match = re.search(r"stream name:\s*(.+)", info)
        records.append({**record, "source": entry["path"], "subsong": index,
                        "name": name_match.group(1).strip() if name_match else ""})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iso", type=Path, default=ROOT / "resources/games/juiced-2/juiced-2-hot-import-nights.iso")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--speech-limit", type=int, default=0, help="0 decodes every English subsong")
    options = parser.parse_args()
    entries = json.loads((ROOT / "artifacts/juiced2-recovery/xdvdfs-inventory.json").read_text())["files"]
    songs = [entry for entry in entries if entry["path"].lower().endswith(".wma")]
    banks = [entry for entry in entries if entry["path"].startswith("audio/english/") and entry["path"].endswith(".xwb")]
    with ThreadPoolExecutor(max_workers=options.workers) as executor:
        soundtrack = list(executor.map(lambda entry: music(entry, options.iso), songs))
        voices = list(executor.map(lambda entry: speech(entry, options.iso, options.speech_limit), banks))
    manifest = {"music": soundtrack, "speech": [voice for bank in voices for voice in bank],
                "source": "Original supplied Xbox 360 disc; decoded with ffmpeg and vgmstream r2168.",
                "speech_scope": (f"First {options.speech_limit} subsongs per English bank" if options.speech_limit
                                 else "All English wave-bank subsongs") + "; trigger mapping is separate."}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"music": len(soundtrack), "speech": len(manifest["speech"])}))


if __name__ == "__main__":
    main()

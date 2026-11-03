#!/usr/bin/env python3
"""Decode the original inline sound banks, preserving their names and controls."""

import hashlib
import json
import re
import struct
import subprocess
import zlib
from concurrent.futures import ThreadPoolExecutor

from media import DECODER, OUTPUT, ROOT, WORK, encode, source_file


def main():
    inventory = json.loads((ROOT / "artifacts/juiced2-recovery/xdvdfs-inventory.json").read_text())[
        "files"
    ]
    iso = ROOT / "resources/games/juiced-2/juiced-2-hot-import-nights.iso"
    archive = source_file(next(e for e in inventory if e["path"] == "audio.jfs"), iso).read_bytes()
    header = source_file(
        next(e for e in inventory if e["path"] == "audio.jfshdr"), iso
    ).read_bytes()
    configurations, jobs, banks = [], [], []
    for index in range(struct.unpack_from(">I", header)[0]):
        key, offset, compressed_size, size, _, _ = struct.unpack_from(">6I", header, 4 + index * 24)
        raw = archive[offset : offset + compressed_size]
        try:
            data = zlib.decompress(raw)
        except zlib.error:
            data = raw
        if len(data) != size:
            raise ValueError(f"Size mismatch {key:08x}")
        if data.startswith(b"[BeginBank]"):
            text = data.decode("utf8", errors="replace")
            match = re.search(r"bank_name\s+(\S+)", text)
            names = re.findall(r"declare_sample\s+(\S+)", text)
            configurations.append(
                {
                    "key": f"{key:08x}",
                    "name": match.group(1) if match else f"{key:08x}",
                    "samples": names,
                    "definition": text,
                }
            )
            continue
        if len(data) < 184:
            continue
        count = struct.unpack_from(">I", data)[0]
        if not 0 < count < 4096 or 4 + count * 180 > len(data):
            continue
        sounds = []
        for sound in range(count):
            position = 4 + sound * 180
            encoded_size, format_size = struct.unpack_from(">II", data, position)
            payload_offset = struct.unpack_from(">I", data, position + 136)[0]
            name = (
                data[position + 148 : position + 180]
                .split(b"\0")[0]
                .decode("ascii", errors="replace")
            )
            if format_size not in (18, 32) or payload_offset + encoded_size > len(data):
                continue  # External English wave banks are decoded separately.
            fmt = data[position + 8 : position + 8 + format_size]
            tag = struct.unpack_from(">H", fmt)[0]
            if tag == 0x165 and format_size == 32:
                fmt = struct.pack("<5H2B4I2BH", *struct.unpack(">5H2B4I2BH", fmt))
            elif tag == 1 and format_size == 18:
                fmt = struct.pack("<HHIIHHH", *struct.unpack(">HHIIHHH", fmt))
            else:
                continue
            payload = data[payload_offset : payload_offset + encoded_size]
            chunks = (
                b"fmt "
                + struct.pack("<I", len(fmt))
                + fmt
                + b"data"
                + struct.pack("<I", len(payload))
                + payload
            )
            destination = WORK / "banks" / f"{key:08x}" / f"{name}.xma"
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks)
            target = OUTPUT / "banks" / f"{key:08x}" / f"{name}.mp3"
            record = {
                "name": name,
                "path": "res://" + str(target.relative_to(ROOT / "godot")),
                "encoded_size": encoded_size,
                "payload_offset": payload_offset,
            }
            sounds.append(record)
            jobs.append((destination, target, record))
        if sounds:
            banks.append(
                {
                    "key": f"{key:08x}",
                    "source_archive_offset": offset,
                    "source_sha256": hashlib.sha256(data).hexdigest(),
                    "samples": sounds,
                }
            )

    def convert(job):
        source, target, record = job
        wav = source.with_suffix(".wav")
        if not target.exists():
            subprocess.run(
                [str(DECODER), "-i", "-o", str(wav), str(source)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        record.update(encode(wav, target))

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(convert, jobs))
    for bank in banks:
        names = {sample["name"] for sample in bank["samples"]}
        bank["configuration_candidates"] = [
            config["name"] for config in configurations if set(config["samples"]) == names
        ]
    output = {
        "source": "Original audio.jfs inline banks; endian-converted original XMA/PCM format and payload.",
        "banks": banks,
        "configurations": configurations,
        "identity_limit": "Matching sample-name sets are candidates, not proof of a unique car identity.",
    }
    (OUTPUT / "banks.json").write_text(json.dumps(output, indent=2) + "\n")
    write_runtime(output)
    print(
        json.dumps(
            {
                "inline_banks": len(banks),
                "decoded_samples": len(jobs),
                "configurations": len(configurations),
            }
        )
    )


def write_runtime(data):
    bindings = json.loads((ROOT / "data/juiced2/audio-bindings.json").read_text())
    media = json.loads((OUTPUT / "manifest.json").read_text())
    configurations = {item["name"]: item for item in data["configurations"]}
    families = {}
    for family, name in bindings["families"].items():
        configuration = configurations[name]
        matches = [bank for bank in data["banks"] if name in bank["configuration_candidates"]]
        ordered = [
            bank
            for bank in matches
            if [sample["name"] for sample in bank["samples"]] == configuration["samples"]
        ]
        bank = (ordered or matches)[0]
        samples = []
        for sample in bank["samples"]:
            token = sample["name"].lower()
            rpm_match = re.search(r"(\d)k", token)
            samples.append(
                {
                    **sample,
                    "reference_rpm": int(rpm_match.group(1)) * 1000 if rpm_match else 1000,
                    "load": "on" if "_on_" in token else "off",
                    "role": "exhaust" if "_ex_" in token or "_x_" in token else "engine",
                }
            )
        families[family] = {
            "source_config": name,
            "source_bank": bank["key"],
            "identity_candidates": bank["configuration_candidates"],
            "samples": samples,
            "native_definition": configuration["definition"],
        }
    effects = {}
    for bank in data["banks"]:
        for sample in bank["samples"]:
            if sample["name"].lower() in [
                "select",
                "click",
                "warning",
                "skid",
                "crash",
                "nitrous",
                "gear",
                "confirm",
                "cancel",
            ]:
                effects.setdefault(sample["name"].lower(), sample["path"])
    voices = {}
    for voice in media["speech"]:
        for trigger, needle in [
            ("airtime", "AirTime"),
            ("race_win", "WonEvent"),
            ("overtake", "Overtake"),
            ("start", "Start"),
            ("finish", "Finish"),
            ("spook", "Spook"),
            ("bet", "Bet"),
        ]:
            if needle.lower() in voice.get("name", "").lower():
                voices.setdefault(trigger, voice["path"])
    runtime = {
        "music": [song["path"] for song in media["music"]],
        "speech": voices,
        "sfx": effects,
        "cars": bindings["cars"],
        "families": families,
        "provenance": bindings["provenance"],
    }
    (OUTPUT / "runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")


if __name__ == "__main__":
    main()

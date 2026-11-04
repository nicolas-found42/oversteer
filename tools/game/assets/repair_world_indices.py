"""Repair prepared world topology without rebuilding materials, UVs or instances."""

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from world_indices import triangles

ROOT = Path(__file__).resolve().parents[3]


def repair(path, geometry):
    raw = path.read_bytes()
    size = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + size])
    binary = bytearray(raw[28 + size :])
    sections = struct.unpack_from(">4I", geometry)
    changes = []
    for mesh in doc["meshes"]:
        match = re.fullmatch(r"native_(\d+)_(\d+)", mesh["name"])
        if not match:
            continue
        model, group = map(int, match.groups())
        header = 20 + model * 60
        index_offset, _, _, descriptor_offset = struct.unpack_from(">4I", geometry, header)
        descriptor = sections[0] + descriptor_offset + group * 92
        _, first, count, topology = struct.unpack_from(">4I", geometry, descriptor)
        source = struct.unpack_from(
            f">{count}H", geometry, sum(sections[:2]) + index_offset + first * 2
        )
        indices = triangles(source, topology)
        if doc["extras"].get("coordinate_system") == "godot-rh-reflect-x":
            for i in range(0, len(indices), 3):
                indices[i + 1], indices[i + 2] = indices[i + 2], indices[i + 1]
        for primitive in mesh["primitives"]:
            accessor = doc["accessors"][primitive["indices"]]
            view = doc["bufferViews"][accessor["bufferView"]]
            kind = {5125: "I", 5123: "H"}[accessor["componentType"]]
            prior = struct.unpack_from(
                f"<{accessor['count']}{kind}", binary,
                view.get("byteOffset", 0) + accessor.get("byteOffset", 0),
            )
            if list(prior) == indices:
                continue
            changes.append({"mesh": mesh["name"], "topology": topology,
                            "before_triangles": len(prior) // 3,
                            "after_triangles": len(indices) // 3})
            binary.extend(b"\0" * (-len(binary) % 4))
            encoded = struct.pack(f"<{len(indices)}I", *indices)
            primitive["indices"] = len(doc["accessors"])
            doc["accessors"].append({"bufferView": len(doc["bufferViews"]),
                                     "componentType": 5125, "count": len(indices),
                                     "type": "SCALAR"})
            doc["bufferViews"].append({"buffer": 0, "byteOffset": len(binary),
                                      "byteLength": len(encoded), "target": 34963})
            binary.extend(encoded)
    if not changes:
        return {"world": path.name, "changed_draws": 0}
    evidence = ROOT / "artifacts/oversteer-pivot/world-topology"
    evidence.mkdir(parents=True, exist_ok=True)
    backup = evidence / (path.name + ".before")
    if not backup.exists():
        backup.write_bytes(raw)
    doc["extras"]["drawTopology"] = "BDL descriptor+12: 0 strip with restart, 1 triangle list"
    doc["buffers"][0]["byteLength"] = len(binary)
    encoded = json.dumps(doc, separators=(",", ":"), allow_nan=False).encode()
    encoded += b" " * (-len(encoded) % 4)
    result = (struct.pack("<4sII", b"glTF", 2, 28 + len(encoded) + len(binary))
              + struct.pack("<II", len(encoded), 0x4E4F534A) + encoded
              + struct.pack("<II", len(binary), 0x004E4942) + binary)
    path.write_bytes(result)
    report = {"world": path.name, "before_sha256": hashlib.sha256(raw).hexdigest(),
              "after_sha256": hashlib.sha256(result).hexdigest(),
              "source_sha256": hashlib.sha256(geometry).hexdigest(),
              "changed_draws": len(changes), "draws": changes}
    (evidence / (path.stem + ".json")).write_text(json.dumps(report, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", action="append", required=True, help="Prepared GLB stem")
    args = parser.parse_args()
    inventory = json.loads((ROOT / "artifacts/juiced2-recovery/xdvdfs-inventory.json").read_text())
    with open(inventory["iso"], "rb") as stream:
        for world in args.world:
            path = ROOT / "godot/assets/worlds" / (world + ".glb")
            raw = path.read_bytes()
            size = struct.unpack_from("<I", raw, 12)[0]
            doc = json.loads(raw[20 : 20 + size])
            entry = next(row for row in inventory["files"] if row["path"] == doc["extras"]["source"])
            stream.seek(entry["offset"])
            report = repair(path, stream.read(entry["size"]))
            print(world, "corrected draws:", report["changed_draws"], flush=True)


if __name__ == "__main__":
    main()

"""Prepare the fixed streetwear driver, preserving the assembled rig and motions.

The previous preview painted both shirt draw groups blue, including bare arms.
Bind the source skin/shoe/denim images to their corresponding draw groups; this
is a fixed PBR outfit, with no character-editor or original shader dependency.
"""

import hashlib
import json
import shutil
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "godot/assets/characters/native_male_baggy_t.glb"
OUTPUT = ROOT / "godot/assets/driver"
ART = ROOT / "artifacts/juiced2-build/characters/avatar-textures"


def prepare():
    raw = SOURCE.read_bytes()
    length = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20 : 20 + length])
    binary_chunk = raw[20 + length :]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    textures = OUTPUT / "textures"
    textures.mkdir(exist_ok=True)
    provenance = []
    for entry in doc["images"]:
        source = SOURCE.parent / entry["uri"]
        shutil.copyfile(source, OUTPUT / entry["uri"])

    def bind(material, filename, color):
        source = ART / filename
        shutil.copyfile(source, textures / filename)
        index = len(doc["textures"])
        doc["textures"].append({"source": len(doc["images"])})
        doc["images"].append({"uri": "textures/" + filename})
        pbr = material["pbrMetallicRoughness"]
        pbr["baseColorTexture"] = {"index": index}
        pbr["baseColorFactor"] = color
        provenance.append(
            {
                "material": material["name"],
                "source": str(source.relative_to(ROOT)),
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            }
        )

    materials = {item["name"]: item for item in doc["materials"]}
    bind(materials["top_top_1"], "7b0e90c1.png", [1, 1, 1, 1])
    bind(materials["bottom_bottom_0"], "8bfdc629.png", [0.65, 0.7, 0.75, 1])
    bind(materials["shoes_shoes_0"], "aef8861a.png", [1, 1, 1, 1])
    # A restrained charcoal tee; separate exposed skin retains its own albedo.
    materials["top_top_0"]["pbrMetallicRoughness"]["baseColorFactor"] = [0.06, 0.065, 0.07, 1]
    for material in doc["materials"]:
        material["pbrMetallicRoughness"]["roughnessFactor"] = (
            0.3 if material["name"].startswith("eyes_") else 0.85
        )
    doc["extras"]["oversteer_fixed_driver"] = {
        "customizable": False,
        "materials": "Fixed charcoal tee, exposed arms, denim and trainers",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "texture_bindings": provenance,
        "limits": "Adapted common adult assembly; not an exact original character preset.",
    }
    encoded = json.dumps(doc, separators=(",", ":"), allow_nan=False).encode()
    encoded += b" " * (-len(encoded) % 4)
    result = (
        struct.pack("<4sII", b"glTF", 2, 20 + len(encoded) + len(binary_chunk))
        + struct.pack("<II", len(encoded), 0x4E4F534A)
        + encoded
        + binary_chunk
    )
    (OUTPUT / "streetwear.glb").write_bytes(result)
    (OUTPUT / "provenance.json").write_text(
        json.dumps(doc["extras"]["oversteer_fixed_driver"], indent=2) + "\n"
    )
    print(f"Prepared fixed driver: {OUTPUT / 'streetwear.glb'}")


if __name__ == "__main__":
    prepare()

"""Give London atlas banners readable back faces without mirroring their front UVs."""

import copy
import json
import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
# Actual London lettering atlas islands, including their authored sampling inset.
REGIONS = [(0.2091064453125, 0.4130859375, 0.6279296875, 0.8720703125),
           (0.50146484375, 0.99658203125, 0.572265625, 0.876953125)]


def repair(raw):
    size = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + size])
    binary = bytearray(raw[28 + size:])
    if doc.get("extras", {}).get("oversteerReadableBannerBacks"):
        return raw, []
    materials = {}
    for index, material in enumerate(doc["materials"]):
        texture = material.get("pbrMetallicRoughness", {}).get("baseColorTexture", {}).get("index")
        if texture is not None:
            image = doc["images"][doc["textures"][texture]["source"]]
            if image.get("uri") == "textures/london/266.png":
                materials[index] = len(doc["materials"]) + len(materials)
    for index in materials:
        material = copy.deepcopy(doc["materials"][index])
        material["name"] += "_readable_banner"
        material["doubleSided"] = False
        doc["materials"].append(material)

    def read(index):
        a = doc["accessors"][index]
        v = doc["bufferViews"][a["bufferView"]]
        dtype = np.dtype({5123: "<u2", 5125: "<u4", 5126: "<f4"}[a["componentType"]])
        width = {"SCALAR": 1, "VEC2": 2}[a["type"]]
        return np.ndarray((a["count"], width), dtype=dtype, buffer=binary,
                          offset=v.get("byteOffset", 0) + a.get("byteOffset", 0),
                          strides=(v.get("byteStride", dtype.itemsize * width), dtype.itemsize)).copy()

    def append(source, values):
        a = copy.deepcopy(doc["accessors"][source])
        values = values.astype(read(source).dtype)
        binary.extend(b"\0" * (-len(binary) % 4))
        a.update(bufferView=len(doc["bufferViews"]), count=len(values))
        for key in ["byteOffset", "min", "max"]:
            a.pop(key, None)
        doc["bufferViews"].append({"buffer": 0, "byteOffset": len(binary), "byteLength": values.nbytes})
        binary.extend(values.tobytes())
        doc["accessors"].append(a)
        return len(doc["accessors"]) - 1

    report = []
    for mesh in doc["meshes"]:
        primitives = []
        for primitive in mesh["primitives"]:
            if primitive.get("material") not in materials:
                primitives.append(primitive)
                continue
            uv_index = primitive["attributes"]["TEXCOORD_0"]
            uv = read(uv_index)
            triangles = read(primitive["indices"]).reshape(-1, 3)
            selected = np.zeros(len(triangles), dtype=bool)
            for lo, hi, top, bottom in REGIONS:
                inside = (uv[:, 0] >= lo-0.004) & (uv[:, 0] <= hi+0.004) & (uv[:, 1] >= top-0.001) & (uv[:, 1] <= bottom+0.001)
                faces = inside[triangles].all(axis=1)
                if not faces.any():
                    continue
                selected |= faces
                front = copy.deepcopy(primitive)
                front["material"] = materials[primitive["material"]]
                front["indices"] = append(primitive["indices"], triangles[faces].reshape(-1, 1))
                back = copy.deepcopy(front)
                back_uv = uv.copy()
                vertices = np.unique(triangles[faces])
                back_uv[vertices, 0] = lo + hi - back_uv[vertices, 0]
                back["attributes"]["TEXCOORD_0"] = append(uv_index, back_uv)
                back["indices"] = append(primitive["indices"], triangles[faces][:, [0, 2, 1]].reshape(-1, 1))
                # These recovered world draws have no authored normals; Godot
                # derives opposite normals from the explicit front/back winding.
                assert "NORMAL" not in back["attributes"]
                primitives.extend([front, back])
                report.append({"mesh": mesh["name"], "triangles_per_side": int(faces.sum()), "u_mirror_sum": lo+hi})
            if (~selected).any():
                primitive["indices"] = append(primitive["indices"], triangles[~selected].reshape(-1, 1))
                primitives.append(primitive)
        mesh["primitives"] = primitives
    if not report:
        raise ValueError("No London banner faces found")
    doc.setdefault("extras", {})["oversteerReadableBannerBacks"] = report
    doc["buffers"][0]["byteLength"] = len(binary)
    header = json.dumps(doc, separators=(",", ":")).encode()
    header += b" " * (-len(header) % 4)
    return (struct.pack("<4sII", b"glTF", 2, 28+len(header)+len(binary))
            + struct.pack("<II", len(header), 0x4E4F534A) + header
            + struct.pack("<II", len(binary), 0x004E4942) + binary), report


if __name__ == "__main__":
    path = ROOT / "godot/assets/worlds/london_circuit1.glb"
    result, report = repair(path.read_bytes())
    path.write_bytes(result)
    print(json.dumps(report, indent=2))

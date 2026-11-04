"""Bake GT4 wheel transforms, retaining world-space geometry and texture UVs."""

import argparse
import copy
import hashlib
import json
import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.carmodels.assets import node_matrix


def bake(raw):
    size = struct.unpack_from("<I", raw, 12)[0]
    doc = json.loads(raw[20:20 + size])
    binary = bytearray(raw[28 + size:])
    if doc.get("extras", {}).get("oversteerWheelBakeVersion") == 2:
        return raw, []
    roots = doc["scenes"][doc.get("scene", 0)]["nodes"]
    world, parents = {}, {}

    def visit(index, matrix, parent=None):
        world[index] = matrix @ node_matrix(doc["nodes"][index])
        parents[index] = parent
        for child in doc["nodes"][index].get("children", []):
            visit(child, world[index], index)

    for index in roots:
        visit(index, np.eye(4))

    def read(index):
        accessor = doc["accessors"][index]
        view = doc["bufferViews"][accessor["bufferView"]]
        dtype = np.dtype({5123: "<u2", 5125: "<u4", 5126: "<f4"}[accessor["componentType"]])
        width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[accessor["type"]]
        return np.ndarray((accessor["count"], width), dtype=dtype, buffer=binary,
                          offset=view.get("byteOffset", 0) + accessor.get("byteOffset", 0),
                          strides=(view.get("byteStride", dtype.itemsize * width), dtype.itemsize)).copy()

    def append(index, values):
        accessor = copy.deepcopy(doc["accessors"][index])
        values = values.astype(read(index).dtype)
        binary.extend(b"\0" * (-len(binary) % 4))
        accessor["bufferView"] = len(doc["bufferViews"])
        accessor.pop("byteOffset", None)
        doc["bufferViews"].append({"buffer": 0, "byteOffset": len(binary), "byteLength": values.nbytes})
        binary.extend(values.tobytes())
        if "min" in accessor:
            accessor["min"] = values.min(axis=0).tolist()
            accessor["max"] = values.max(axis=0).tolist()
        doc["accessors"].append(accessor)
        return len(doc["accessors"]) - 1

    report = []
    for index, transform in world.items():
        node = doc["nodes"][index]
        if not node.get("name", "").startswith(("wheel_", "tire_")):
            continue
        if "mesh" not in node or node.get("children"):
            raise ValueError("Expected a direct GT4 wheel mesh: " + node["name"])
        basis = transform[:3, :3]
        determinant = float(np.linalg.det(basis))
        mesh = copy.deepcopy(doc["meshes"][node["mesh"]])
        for primitive in mesh["primitives"]:
            attributes = primitive["attributes"]
            for semantic in ["POSITION", "NORMAL", "TANGENT"]:
                if semantic not in attributes:
                    continue
                source = attributes[semantic]
                values = read(source)
                if semantic == "POSITION":
                    values = values @ basis.T
                else:
                    values[:, :3] = values[:, :3] @ (np.linalg.inv(basis) if semantic == "NORMAL" else basis.T)
                    values[:, :3] /= np.maximum(np.linalg.norm(values[:, :3], axis=1, keepdims=True), 1e-12)
                    if semantic == "TANGENT" and determinant < 0:
                        values[:, 3] *= -1
                attributes[semantic] = append(source, values)
            # GT4's exported outer rim faces and tire tread wind inward.
            # Correct that once, together with any baked reflection.
            source = primitive["indices"]
            indices = read(source).reshape(-1, 3)
            if determinant > 0:
                indices = indices[:, [0, 2, 1]]
            primitive["indices"] = append(source, indices.reshape(-1, 1))
            if "NORMAL" in attributes:
                positions = read(attributes["POSITION"])
                faces = np.cross(positions[indices[:, 1]] - positions[indices[:, 0]],
                                 positions[indices[:, 2]] - positions[indices[:, 0]])
                normals = np.zeros_like(positions)
                for corner in range(3):
                    np.add.at(normals, indices[:, corner], faces)
                normals /= np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)
                attributes["NORMAL"] = append(attributes["NORMAL"], normals)
            material_ids = {primitive["material"]}
            for mapping in primitive.get("extensions", {}).get("KHR_materials_variants", {}).get("mappings", []):
                material_ids.add(mapping["material"])
            for material_id in material_ids:
                material = doc["materials"][material_id]
                material["doubleSided"] = False
                if node["name"].startswith("tire_") and material.get("alphaMode", "OPAQUE") in ("OPAQUE", "MASK"):
                    material["pbrMetallicRoughness"]["baseColorFactor"][3] = 1.0
        node["mesh"] = len(doc["meshes"])
        doc["meshes"].append(mesh)
        if parents[index] is not None:
            doc["nodes"][parents[index]]["children"].remove(index)
            roots.append(index)
        for field in ["matrix", "scale", "rotation"]:
            node.pop(field, None)
        node["translation"] = transform[:3, 3].tolist()
        report.append({"node": node["name"], "source_determinant": determinant, "baked_determinant": 1.0})
    if not report:
        raise ValueError("No wheel meshes found")
    doc.setdefault("extras", {})["oversteerBakedWheels"] = report
    doc["extras"]["oversteerWheelBakeVersion"] = 2
    doc["buffers"][0]["byteLength"] = len(binary)
    header = json.dumps(doc, separators=(",", ":")).encode()
    header += b" " * (-len(header) % 4)
    return (struct.pack("<4sII", b"glTF", 2, 28 + len(header) + len(binary))
            + struct.pack("<II", len(header), 0x4E4F534A) + header
            + struct.pack("<II", len(binary), 0x004E4942) + binary), report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--car", action="append", required=True)
    args = parser.parse_args()
    hashes = {}
    for car in args.car:
        path = ROOT / "godot/assets/cars" / f"{car}.glb"
        raw, report = bake(path.read_bytes())
        path.write_bytes(raw)
        hashes[car] = hashlib.sha256(raw).hexdigest()
        print(car, json.dumps(report))
    for path in [ROOT / "data/juiced2/cars.json", ROOT / "godot/assets/cars.json"]:
        catalog = json.loads(path.read_text())
        for car in catalog["cars"]:
            if car["code"] in hashes:
                car["prepared_sha256"] = hashes[car["code"]]
        path.write_text(json.dumps(catalog, indent=2) + "\n")

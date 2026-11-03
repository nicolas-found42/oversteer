"""GLB integrity checks and selected-scene decoding for native donor preparation."""

from __future__ import annotations

import hashlib
import io
import json
import re
import struct
from pathlib import Path

import numpy as np
from PIL import Image


def verify_asset(path, record):
    data = Path(path).read_bytes()
    if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("asset checksum/size mismatch: " + str(path))
    return data


def node_matrix(node):
    if "matrix" in node:
        return np.array(node["matrix"], dtype=float).reshape(4, 4).T
    x, y, z, w = node.get("rotation", [0, 0, 0, 1])
    rotation = np.array(
        [
            [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
        ]
    )
    matrix = np.eye(4)
    matrix[:3, :3] = rotation @ np.diag(node.get("scale", [1, 1, 1]))
    matrix[:3, 3] = node.get("translation", [0, 0, 0])
    return matrix


def decode_scene(data, game=None):
    magic, version, size = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or size != len(data):
        raise ValueError("invalid GLB header")
    chunks = {}
    offset = 12
    while offset < len(data):
        length, kind = struct.unpack_from("<I4s", data, offset)
        offset += 8
        chunks[kind] = data[offset : offset + length]
        offset += length
    document = json.loads(chunks[b"JSON"])
    binary = chunks.get(b"BIN\x00", b"")
    types = {5120: "i1", 5121: "u1", 5122: "<i2", 5123: "<u2", 5125: "<u4", 5126: "<f4"}
    sizes = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}

    def accessor(index):
        item = document["accessors"][index]
        if "sparse" in item:
            raise ValueError("sparse accessor requires explicit support")
        view = document["bufferViews"][item["bufferView"]]
        if view.get("buffer", 0) != 0:
            raise ValueError("external GLB buffer")
        dtype = np.dtype(types[item["componentType"]])
        count = sizes[item["type"]]
        result = np.ndarray(
            (item["count"], count),
            dtype=dtype,
            buffer=binary,
            offset=view.get("byteOffset", 0) + item.get("byteOffset", 0),
            strides=(view.get("byteStride", dtype.itemsize * count), dtype.itemsize),
        ).copy()
        if item.get("normalized") and dtype.kind in "iu":
            result = result.astype(float) / np.iinfo(dtype).max
            if dtype.kind == "i":
                result = np.maximum(result, -1)
        return result

    images = {}

    def material(index):
        item = document.get("materials", [{}])[index] if index is not None else {}
        pbr = item.get("pbrMetallicRoughness", {})
        texture = None
        if "baseColorTexture" in pbr:
            source = document["textures"][pbr["baseColorTexture"]["index"]]["source"]
            if source not in images:
                image = document["images"][source]
                view = document["bufferViews"][image["bufferView"]]
                start = view.get("byteOffset", 0)
                image_data = binary[start : start + view["byteLength"]]
                images[source] = np.array(Image.open(io.BytesIO(image_data)).convert("RGBA"))
            texture = images[source]
        return {
            "factor": np.array(pbr.get("baseColorFactor", [1, 1, 1, 1])),
            "texture": texture,
            "name": item.get("name", ""),
            "alpha_mode": item.get("alphaMode", "OPAQUE"),
            "alpha_cutoff": item.get("alphaCutoff", 0.5),
        }

    parts = []

    def visit(index, parent, ancestors):
        if index in ancestors:
            raise ValueError("cyclic GLB scene")
        node = document["nodes"][index]
        if game == "ford-racing-2" and "HELMET" in node.get("extras", {}).get("sourceNames", []):
            return
        transform = parent @ node_matrix(node)
        if "mesh" in node:
            mesh = document["meshes"][node["mesh"]]
            for primitive in mesh["primitives"]:
                material_index = primitive.get("material")
                material_name = (
                    document["materials"][material_index].get("name", "")
                    if material_index is not None
                    else ""
                )
                if game == "ford-racing-2" and material_name == "UNDER_SHADOW":
                    continue
                if game == "gran-turismo-4" and re.search(r"/mat-1(?:\+vc)?/BLEND/", material_name):
                    continue
                if primitive.get("mode", 4) != 4:
                    raise ValueError("non-triangle primitive")
                positions = accessor(primitive["attributes"]["POSITION"])
                positions = positions @ transform[:3, :3].T + transform[:3, 3]
                indices = (
                    accessor(primitive["indices"]).ravel()
                    if "indices" in primitive
                    else np.arange(len(positions))
                )
                uv_index = primitive["attributes"].get("TEXCOORD_0")
                parts.append(
                    {
                        "positions": positions,
                        "indices": indices.reshape(-1, 3),
                        "uv": accessor(uv_index) if uv_index is not None else None,
                        "material": material(primitive.get("material")),
                        "name": node.get("name", mesh.get("name", "")),
                    }
                )
        for child in node.get("children", []):
            visit(child, transform, ancestors | {index})

    scene = document["scenes"][document.get("scene", 0)]
    for node in scene.get("nodes", []):
        visit(node, np.eye(4), set())
    if not parts:
        raise ValueError("selected GLB scene contains no triangles")
    return parts

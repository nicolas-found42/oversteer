"""Hash-pinned source assets and an orthographic CPU reference renderer.

Only the GLB's selected scene is drawn. Alternative LOD/state scenes are not piled
on top of one another. No source scripts, external buffers or shaders are executed.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import io
import json
import os
import re
import struct
import urllib.request
from pathlib import Path

import numpy as np
from PIL import Image

from tools.carmodels.scope import included_identities

COMMIT = "ce047799fc550cdf92e4f7b62d97ef5c603e53ad"
REPOSITORY = "https://raw.githubusercontent.com/nicolas-found42/carmodels/" + COMMIT
ROOT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get("OVERSTEER_CARMODELS_WORK", ROOT / "artifacts/carmodels-research"))


def verify_asset(path, record):
    data = Path(path).read_bytes()
    if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("asset checksum/size mismatch: " + str(path))
    return data


def fetch_asset(record, directory):
    code = record["code"]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", code):
        raise ValueError("unsafe source code: " + code)
    path = directory / (code + ".glb")
    if not path.exists():
        url = REPOSITORY + "/dealership/dealership/models/" + code + ".glb"
        with urllib.request.urlopen(url, timeout=90) as response:
            data = response.read()
        if len(data) != record["bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError("download checksum/size mismatch: " + code)
        path.write_bytes(data)
    verify_asset(path, record)
    return code


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


def render(parts, pixels=160, forward_axis=2, forward_sign=1):
    """Nearest-sampled orthographic render, Y-up, transparent background.

    Normalized source-space references measure shape, never assert physical metres.
    The caller separately scales against sourced real dimensions.
    """
    all_positions = np.concatenate([p["positions"] for p in parts])
    low, high = all_positions.min(axis=0), all_positions.max(axis=0)
    lateral_axis = 0 if forward_axis == 2 else 2
    length = high[forward_axis] - low[forward_axis]
    width = high[lateral_axis] - low[lateral_axis]
    if min(length, width) <= 0:
        raise ValueError("degenerate projected source geometry")
    scale = (pixels - 4) / max(length, width)
    centre = (low + high) / 2
    rgba = np.zeros((pixels, pixels, 4), dtype=np.uint8)
    depth = np.full((pixels, pixels), -np.inf)
    for part in parts:
        points = part["positions"]
        screen = np.column_stack(
            [
                (points[:, lateral_axis] - centre[lateral_axis]) * scale + pixels / 2,
                -(points[:, forward_axis] - centre[forward_axis]) * forward_sign * scale
                + pixels / 2,
            ]
        )
        material = part["material"]
        for triangle in part["indices"]:
            a, b, c = screen[triangle]
            minimum = np.maximum(np.floor(np.minimum(np.minimum(a, b), c)).astype(int), 0)
            maximum = np.minimum(np.ceil(np.maximum(np.maximum(a, b), c)).astype(int), pixels - 1)
            if np.any(minimum > maximum):
                continue
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-9:
                continue
            xx, yy = np.meshgrid(
                np.arange(minimum[0], maximum[0] + 1) + 0.5,
                np.arange(minimum[1], maximum[1] + 1) + 0.5,
            )
            u = ((b[1] - c[1]) * (xx - c[0]) + (c[0] - b[0]) * (yy - c[1])) / den
            v = ((c[1] - a[1]) * (xx - c[0]) + (a[0] - c[0]) * (yy - c[1])) / den
            w = 1 - u - v
            z = u * points[triangle[0], 1] + v * points[triangle[1], 1] + w * points[triangle[2], 1]
            area = np.s_[minimum[1] : maximum[1] + 1, minimum[0] : maximum[0] + 1]
            visible = (u >= -1e-6) & (v >= -1e-6) & (w >= -1e-6) & (z > depth[area])
            if not visible.any():
                continue
            texture = material["texture"]
            if texture is not None and part["uv"] is not None:
                uv = part["uv"][triangle]
                uv = u[..., None] * uv[0] + v[..., None] * uv[1] + w[..., None] * uv[2]
                tx = np.minimum(
                    (np.mod(uv[..., 0], 1) * texture.shape[1]).astype(int), texture.shape[1] - 1
                )
                ty = np.minimum(
                    (np.mod(uv[..., 1], 1) * texture.shape[0]).astype(int), texture.shape[0] - 1
                )
                color = texture[ty, tx].astype(float) * material["factor"]
            else:
                color = np.broadcast_to(material["factor"] * 255, (*z.shape, 4)).copy()
            if material["alpha_mode"] != "OPAQUE":
                visible &= color[..., 3] >= 255 * material["alpha_cutoff"]
            color[..., 3] = 255
            rgba[area][visible] = np.clip(color[visible], 0, 255).astype(np.uint8)
            depth[area][visible] = z[visible]
    return rgba, {
        "source_bounds": [low.tolist(), high.tolist()],
        "length": float(length),
        "width": float(width),
        "scale_px_source_unit": float(scale),
    }


def render_record(identity, record):
    code = identity["code"]
    output = WORK / "references"
    path = output / (code + ".json")
    if path.exists():
        cached = json.loads(path.read_text())
        if cached.get("render_version") == 3 and cached.get("sha256") == record["sha256"]:
            return cached
    parts = decode_scene(verify_asset(WORK / "models" / (code + ".glb"), record), identity["game"])
    axis = 0 if identity["game"] == "gran-turismo" else 2
    sign = (
        -1
        if identity["game"]
        in {"gran-turismo-4", "midnight-club-3-remix", "midnight-club-los-angeles"}
        else 1
    )
    rgba, info = render(parts, forward_axis=axis, forward_sign=sign)
    Image.fromarray(rgba).save(output / (code + ".png"))
    rows = []
    for row in rgba[..., 3] > 0:
        indices = np.flatnonzero(row)
        rows.append(float(indices[-1] - indices[0] + 1) if len(indices) else 0)
    nonempty = np.flatnonzero(np.array(rows) > 0)
    if not len(nonempty):
        raise ValueError("empty projected source: " + code)
    profile = np.interp(np.linspace(nonempty[-1], nonempty[0], 65), np.arange(len(rows)), rows)
    profile /= max(profile)
    result = {
        "code": code,
        "family": identity["family_key"],
        "game": identity["game"],
        "forward_axis": axis,
        "forward_sign": sign,
        "profile": profile.tolist(),
        "orientation_status": "pinned_viewer_front_camera",
        "render_version": 3,
        "sha256": record["sha256"],
        **info,
    }
    path.write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["fetch", "render"])
    parser.add_argument("--identities", type=Path, default=WORK / "identities.json")
    parser.add_argument("--manifest", type=Path, default=WORK / "models.json")
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    identities = json.loads(args.identities.read_text())["identities"]
    records = {r["code"]: r for r in json.loads(args.manifest.read_text())["cars"]}
    included = included_identities(identities)[: args.limit]
    directory = WORK / "models"
    directory.mkdir(parents=True, exist_ok=True)
    if args.command == "fetch":
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(fetch_asset, records[i["code"]], directory) for i in included]
            for n, future in enumerate(concurrent.futures.as_completed(futures), 1):
                future.result()
                if n % 100 == 0 or n == len(included):
                    print("verified assets", n, "/", len(included), flush=True)
    else:
        output = WORK / "references"
        output.mkdir(parents=True, exist_ok=True)
        measurements = []
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures = [pool.submit(render_record, i, records[i["code"]]) for i in included]
            for n, future in enumerate(concurrent.futures.as_completed(futures), 1):
                measurements.append(future.result())
                if n % 50 == 0 or n == len(included):
                    print("rendered references", n, "/", len(included), flush=True)
        measurements.sort(key=lambda m: m["code"])
        (output / "measurements.json").write_text(json.dumps(measurements))


if __name__ == "__main__":
    main()

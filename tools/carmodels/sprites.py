"""Prepare faithful 2D sprite bakes from the retained carmodels GLBs."""

import argparse
import hashlib
import json
import struct
import subprocess

from tools.carmodels.assets import ROOT, WORK, verify_asset
from tools.carmodels.scope import included_identities

SPRITES = WORK / "sprites"


def selected_scene(data, game):
    """Keep the source viewer's selected scene and explicit loader exclusions.

    Blender imports glTF scenes as collections. Removing alternate scenes prevents
    alternate LODs/poses from being rendered together. Original node transforms and
    material/texture bytes are retained.
    """
    length = struct.unpack_from("<I", data, 12)[0]
    document = json.loads(data[20 : 20 + length])
    document["scenes"] = [document["scenes"][document.get("scene", 0)]]
    document["scene"] = 0
    for node in document["nodes"]:
        if game == "ford-racing-2" and "HELMET" in node.get("extras", {}).get("sourceNames", []):
            node.pop("children", None)
            node.pop("mesh", None)
    for mesh in document["meshes"]:
        mesh["primitives"] = [
            primitive
            for primitive in mesh["primitives"]
            if not excluded_material(
                document.get("materials", [{}])[primitive.get("material", 0)].get("name", ""),
                game,
            )
        ]
    if document.get("skins") or document.get("animations"):
        raise ValueError("Static sprite bake requires an explicit posed skin/animation input")
    reachable = set()

    def visit(index):
        if index in reachable:
            return
        reachable.add(index)
        for child in document["nodes"][index].get("children", []):
            visit(child)

    for index in document["scenes"][0]["nodes"]:
        visit(index)
    mapping = {index: new for new, index in enumerate(sorted(reachable))}
    nodes = [document["nodes"][index] for index in sorted(reachable)]
    for node in nodes:
        if "children" in node:
            node["children"] = [mapping[c] for c in node["children"]]
        if "mesh" in node and not document["meshes"][node["mesh"]]["primitives"]:
            node.pop("mesh")
    document["nodes"] = nodes
    document["scenes"][0]["nodes"] = [mapping[i] for i in document["scenes"][0]["nodes"]]
    encoded = json.dumps(document, separators=(",", ":")).encode()
    encoded += b" " * (-len(encoded) % 4)
    trailing = data[20 + length :]
    return (
        struct.pack("<4sII", b"glTF", 2, 20 + len(encoded) + len(trailing))
        + struct.pack("<I4s", len(encoded), b"JSON")
        + encoded
        + trailing
    )


def excluded_material(name, game):
    import re

    return (game == "ford-racing-2" and bool(re.search(r"(^|_)UNDER_SHADOW", name, re.I))) or (
        game == "gran-turismo-4" and bool(re.search(r"/mat-1(?:\+vc)?/BLEND/", name))
    )


def prepare(codes, profile="authored", poses=False):
    from tools.carmodels.sprite_judgments import import_sprite_policy

    policy = import_sprite_policy() if profile == "viewer" else None
    identities = included_identities(
        json.loads((WORK / "identities.json").read_text())["identities"]
    )
    models = {r["code"]: r for r in json.loads((WORK / "models.json").read_text())["cars"]}
    if codes and set(codes) - {i["code"] for i in identities}:
        raise ValueError("Unknown or excluded model code")
    selected = [i for i in identities if not codes or i["code"] in codes]
    output = SPRITES / ("viewer-scenes" if profile == "viewer" else "selected-scenes")
    output.mkdir(parents=True, exist_ok=True)
    if profile == "viewer":
        corrected = SPRITES / "viewer-materials"
        corrected.mkdir(exist_ok=True)
        corrections = [
            {
                "code": i["code"],
                "source": str(WORK / "models" / (i["code"] + ".glb")),
                "output": str(corrected / (i["code"] + ".glb")),
                "sha256": models[i["code"]]["sha256"],
            }
            for i in selected
            if i["game"] == "gran-turismo-4"
        ]
        correction_jobs = SPRITES / "preview-material-jobs.json"
        correction_jobs.write_text(json.dumps(corrections, indent=2))
        subprocess.run(
            [
                "node",
                str(ROOT / "tools/carmodels/preview_materials.mjs"),
                str(correction_jobs),
                str(SPRITES / "preview-material-reports.json"),
            ],
            check=True,
        )
    jobs = []
    for identity in selected:
        code = identity["code"]
        model = output / (code + ".glb")
        source = verify_asset(WORK / "models" / (code + ".glb"), models[code])
        if profile == "viewer" and identity["game"] == "gran-turismo-4":
            source = (SPRITES / "viewer-materials" / (code + ".glb")).read_bytes()
        model.write_bytes(selected_scene(source, identity["game"]))
        for mode in [policy["material_mode"]] if profile == "viewer" else ["studio", "unlit"]:
            jobs.append(
                {
                    "code": code,
                    "model": str(model),
                    "output": str(
                        SPRITES
                        / ("viewer-bakes" if profile == "viewer" else "pilot")
                        / (code + ("-source" if profile == "viewer" else "-" + mode) + ".png")
                    ),
                    "forward_axis": 2,
                    "forward_sign": 1 if identity["game"] == "ford-racing-2" else -1,
                    "pixels": policy["render_pixels"] if profile == "viewer" else 256,
                    "frame_pixels": 256,
                    "samples": 16,
                    "material_mode": mode,
                    "source_profile": profile,
                    "refinement_sha256": policy["refinement_sha256"] if policy else None,
                    "exclude_steering_control": bool(policy and policy["exclude_steering_control"]),
                    "pose_angles": list(range(-60, 61, 10)) if poses else [0],
                    "source_sha256": models[code]["sha256"],
                    "filtered_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
                    "worker_sha256": hashlib.sha256(
                        (ROOT / "tools/carmodels/bake_sprites.py").read_bytes()
                    ).hexdigest(),
                }
            )
    path = SPRITES / ("viewer-jobs.json" if profile == "viewer" else "pilot-jobs.json")
    path.write_text(json.dumps(jobs, indent=2))
    print(
        "blender --background --factory-startup --python-exit-code 1 --python "
        + str(ROOT / "tools/carmodels/bake_sprites.py")
        + " -- "
        + str(path)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("codes", nargs="*")
    parser.add_argument("--profile", choices=["authored", "viewer"], default="authored")
    parser.add_argument("--poses", action="store_true", help="render the bounded steering grid")
    args = parser.parse_args()
    prepare(args.codes, args.profile, args.poses)

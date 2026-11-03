"""Package mesh-baked steering frames and generate the runtime's explicit catalog."""

import argparse
import hashlib
import json
import math
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.sampling import mip_chain
from tools.carmodels.scope import included_identities

DIRECTORY = WORK / "sprites"
RESOURCE = ROOT / "resources/vehicles"
ANGLES = list(range(-60, 61, 10))
COLUMNS = 4
MIP_LEVELS = 9


def records():
    identities = included_identities(
        json.loads((WORK / "identities.json").read_text())["identities"]
    )
    included = {i["code"] for i in identities}
    fields = {
        r["code"]: r
        for line in (WORK / "field-research.jsonl").read_text().splitlines()
        if (r := json.loads(line))["code"] in included
    }
    result = []
    for identity in sorted(identities, key=lambda i: i["code"]):
        code = identity["code"]
        # Body bounds are unchanged by the viewer's material correction. This permits
        # catalog generation while the explicit pose-grid render is still in progress.
        metadata = json.loads((DIRECTORY / "viewer-bakes" / (code + "-source.json")).read_text())
        f = fields[code]["fields"]
        length = sum(
            f[k]["value"] for k in ["body.wheelbase", "body.front_overhang", "body.rear_overhang"]
        )
        low, high = metadata["bounds"]
        name = identity["source_name"]
        if name.lower().startswith(("vp_", "vpd_")):
            name = " ".join(str(identity.get(k) or "") for k in ["make", "model"]).strip()
        result.append(
            {
                "code": code,
                "name": name,
                "source_length": high[1] - low[1],
                "ortho_span": metadata["ortho_scale"],
                "physical_length_m": length,
                "frame_size": metadata["experiment"].get(
                    "frame_pixels", metadata["experiment"]["pixels"]
                ),
            }
        )
    return result


def catalog(rows):
    lines = ["/* Generated from the included-only carmodels sprite catalog. */\n"]
    for r in rows:
        code = r["code"]
        strings = [code, r["name"], "resources/vehicles/" + code + ".png"]
        lines.append(
            "{ "
            + ", ".join(json.dumps(s, ensure_ascii=True) for s in strings)
            + f", {r['source_length']:.9f}f, {r['ortho_span']:.9f}f, "
            + f"{r['physical_length_m']:.9f}f, {r['frame_size']}, {COLUMNS}, "
            + f"{len(ANGLES)}, {ANGLES[0]}, {ANGLES[1] - ANGLES[0]}, {MIP_LEVELS} }},\n"
        )
    (ROOT / "src/render/car_model_catalog.inc").write_text("".join(lines))


def premultiply(image):
    rgba = np.array(image.convert("RGBA"), dtype=np.uint16)
    rgba[..., :3] = (rgba[..., :3] * rgba[..., 3:4] + 127) // 255
    return Image.fromarray(rgba.astype(np.uint8))


def pack(rows):
    decision = json.loads((ROOT / "data/carmodels/sprite-mip-decision.json").read_text())[0]
    answer = decision["result"]["recommendation"]
    if (
        answer["escaped"]
        or answer["selected"] != "baked_linear"
        or answer["contradicted_requirements"]
        or not 0.7 <= answer["probabilities"]["baked_linear"] <= 1
    ):
        raise ValueError("Unresolved source-sprite mip policy")
    RESOURCE.mkdir(parents=True, exist_ok=True)
    profiles = ROOT / "data/carmodels/profiles"
    profiles.mkdir(exist_ok=True)
    report = []
    for r in rows:
        code, size = r["code"], r["frame_size"]
        metadata = json.loads((DIRECTORY / "viewer-bakes" / (code + "-source.json")).read_text())
        if [f["angle_degrees"] for f in metadata["frames"]] != ANGLES:
            raise ValueError("Incomplete source-mesh steering grid: " + code)
        atlas = Image.new(
            "RGBA", (size * COLUMNS, (size * 2 - 1) * math.ceil(len(ANGLES) / COLUMNS))
        )
        frames = []
        for n, frame in enumerate(metadata["frames"]):
            path = Path(frame["path"])
            image = Image.open(path).convert("RGBA")
            if image.size != (metadata["experiment"]["pixels"],) * 2 or not image.getbbox():
                raise ValueError("Empty or mismatched source render: " + str(path))
            top = 0
            for level, mip in enumerate(mip_chain(image)):
                mip_size = size >> level
                atlas.paste(
                    premultiply(mip), (n % COLUMNS * mip_size, top + n // COLUMNS * mip_size)
                )
                top += mip_size * math.ceil(len(ANGLES) / COLUMNS)
            frames.append(
                {
                    "angle": frame["angle_degrees"],
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        output = RESOURCE / (code + ".png")
        atlas.save(output, format="PNG", compress_level=9)
        # The authored display colors are independent of these simulation values.
        profile = profiles / (code + ".txt")
        shutil.copyfile(WORK / "profiles" / (code + ".txt"), profile)
        text = profile.read_text()
        tag = "# carmodels.model = " + code
        if tag not in text.splitlines():
            with profile.open("a") as file:
                file.write(tag + "\n")
        report.append(
            {
                **r,
                "frames": frames,
                "source_sha256": metadata["experiment"]["source_sha256"],
                "recipe": {
                    **metadata["experiment"],
                    "downsample": "box, linear light, premultiplied alpha",
                },
                "front_wheel_groups": metadata["front_wheel_groups"],
                "atlas_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
                "atlas_bytes": output.stat().st_size,
                "mip_levels": MIP_LEVELS,
                "mip_recipe": "linear-light premultiplied averaging from the 512px source; "
                "no intermediate quantization",
                "mip_decision_request_hash": decision["request_hash"],
                "alpha": "premultiplied sRGB RGBA; use premultiplied alpha blending",
            }
        )
    catalog(rows)
    (ROOT / "data/carmodels/sprites.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "models": len(report),
                "frames": len(report) * len(ANGLES),
                "bytes": sum(r["atlas_bytes"] for r in report),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["catalog", "pack"])
    args = parser.parse_args()
    rows = records()
    catalog(rows) if args.action == "catalog" else pack(rows)

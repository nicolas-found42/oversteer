"""Exhaustive sampling/alpha experiment grid against high-resolution 3D projections."""

import argparse
import hashlib
import json

import numpy as np
from PIL import Image

from tools.carmodels.assets import ROOT, WORK
from tools.carmodels.sampling import FILTERS, resample, to_linear
from tools.carmodels.scope import included_identities
from tools.carmodels.sprite_experiments import CASES

DIRECTORY = WORK / "sprites/refinement"
RESOLUTIONS = [128, 192, 256, 384]


def references():
    identities = included_identities(
        json.loads((WORK / "identities.json").read_text())["identities"]
    )
    heldout = []
    for game, count in [
        ("ford-racing-2", 4),
        ("gran-turismo-4", 6),
        ("midnight-club-3-remix", 3),
        ("midnight-club-los-angeles", 3),
    ]:
        pool = [i["code"] for i in identities if i["game"] == game and i["code"] not in CASES]
        heldout += sorted(pool, key=lambda code: hashlib.sha256(code.encode()).digest())[:count]
    codes = CASES + heldout
    jobs = []
    for code in codes:
        metadata = json.loads((WORK / "sprites/viewer-bakes" / (code + "-source.json")).read_text())
        job = dict(metadata["experiment"])
        job["material_mode"] = "unlit"
        job.update(
            output=str(DIRECTORY / "reference" / (code + ".png")),
            pixels=1024,
            samples=64,
            ortho_span=metadata["ortho_scale"],
            pose_angles=[0],
            worker_sha256=hashlib.sha256(
                (ROOT / "tools/carmodels/bake_sprites.py").read_bytes()
            ).hexdigest(),
        )
        jobs.append(job)
        for directory, pixels in [("direct256", 256), ("supersample", 512)]:
            jobs.append(
                {
                    **job,
                    "pixels": pixels,
                    "samples": 16,
                    "output": str(DIRECTORY / directory / (code + ".png")),
                }
            )
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    (DIRECTORY / "split.json").write_text(
        json.dumps({"development": CASES, "heldout": heldout}, indent=2)
    )
    (DIRECTORY / "reference-jobs.json").write_text(json.dumps(jobs, indent=2))
    print(
        "Prepared", len(jobs), "fixed-framing source jobs: 1024px references and 256/512px controls"
    )


def loss(candidate, reference):
    a, b = [np.asarray(im, dtype=np.float32) / 255 for im in [candidate, reference]]
    union = (a[..., 3] > 0.01) | (b[..., 3] > 0.01)
    if not union.any():
        raise ValueError("Empty fidelity comparison")
    ac, bc = to_linear(a[..., :3]), to_linear(b[..., :3])
    aa, ba = a[..., 3:4], b[..., 3:4]
    errors = []
    for background in [0.03, 0.3, 0.9]:
        ca, cb = ac * aa + background * (1 - aa), bc * ba + background * (1 - ba)
        errors.append(float(np.mean((ca[union] - cb[union]) ** 2)))
    alpha_error = float(np.mean((aa[..., 0][union] - ba[..., 0][union]) ** 2))
    return {"color_mse": sum(errors) / len(errors), "alpha_mse": alpha_error}


def compare():
    split = json.loads((DIRECTORY / "split.json").read_text())
    results = []
    for group, codes in split.items():
        for code in codes:
            reference = Image.open(DIRECTORY / "reference" / (code + ".png")).convert("RGBA")
            targets = {
                p: resample(reference, p, "box", "linear", "premultiplied") for p in [128, 256, 512]
            }
            for pixels in RESOLUTIONS:
                for method in FILTERS:
                    for space in ["srgb", "linear"]:
                        for alpha in ["straight", "premultiplied"]:
                            image = resample(reference, pixels, method, space, alpha)
                            values = {
                                str(p): loss(
                                    resample(image, p, "bilinear", "linear", "premultiplied"),
                                    target,
                                )
                                for p, target in targets.items()
                            }
                            results.append(
                                {
                                    "code": code,
                                    "group": group,
                                    "pixels": pixels,
                                    "filter": method,
                                    "space": space,
                                    "alpha": alpha,
                                    "display_metrics": values,
                                }
                            )
            print(code, "80 sampling/alpha variants measured", flush=True)
    (DIRECTORY / "results.json").write_text(json.dumps(results, indent=2))


def runtime_sample(image, pixels):
    """Approximate axis-aligned GPU minification of premultiplied sRGB8 textures.

    Integral mip levels average 2x2 texels. Bilinear/trilinear fractional levels and
    transformed sampling still require native capture inspection.
    """
    values = np.asarray(image.convert("RGBA"), dtype=np.float32) / 255
    values[..., :3] *= values[..., 3:4]
    while values.shape[0] >= pixels * 2:
        size = values.shape[0] // 2
        values = values.reshape(size, 2, size, 2, 4).mean(axis=(1, 3))
        values = np.round(values * 255) / 255
    result = np.stack(
        [
            np.asarray(
                Image.fromarray(values[..., c]).resize((pixels, pixels), Image.Resampling.BILINEAR)
            )
            for c in range(4)
        ],
        axis=2,
    )
    a = result[..., 3:4]
    result[..., :3] = np.divide(result[..., :3], a, out=np.zeros_like(result[..., :3]), where=a > 0)
    return Image.fromarray(np.round(np.clip(result, 0, 1) * 255).astype(np.uint8))


def production_comparison():
    split = json.loads((DIRECTORY / "split.json").read_text())
    rows = []
    for group, codes in split.items():
        for code in codes:
            reference = Image.open(DIRECTORY / "reference" / (code + ".png")).convert("RGBA")
            baseline = Image.open(DIRECTORY / "direct256" / (code + ".png")).convert("RGBA")
            supersample = Image.open(DIRECTORY / "supersample" / (code + ".png")).convert("RGBA")
            candidates = {
                "direct_256": baseline,
                "supersample_512_box_linear_premultiplied": resample(
                    supersample, 256, "box", "linear", "premultiplied"
                ),
                "reference_1024_box_linear_premultiplied": resample(
                    reference, 256, "box", "linear", "premultiplied"
                ),
            }
            for name, image in candidates.items():
                values = {}
                for p in [128, 256, 512]:
                    target = resample(reference, p, "box", "linear", "premultiplied")
                    values[str(p)] = loss(runtime_sample(image, p), target)
                rows.append(
                    {"group": group, "code": code, "candidate": name, "display_metrics": values}
                )
    summary = {}
    for group in split:
        summary[group] = {}
        for name in candidates:
            group_rows = [r for r in rows if r["group"] == group and r["candidate"] == name]
            summary[group][name] = {
                str(p): float(
                    np.mean(
                        [
                            r["display_metrics"][str(p)]["color_mse"]
                            + r["display_metrics"][str(p)]["alpha_mse"]
                            for r in group_rows
                        ]
                    )
                )
                for p in [128, 256, 512]
            }
    (DIRECTORY / "production-comparison.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, indent=2)
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["references", "compare", "production"])
    args = parser.parse_args()
    {"references": references, "compare": compare, "production": production_comparison}[
        args.stage
    ]()

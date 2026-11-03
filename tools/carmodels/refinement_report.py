"""Summarize actual sprite experiments and prepare bounded Jev adoption judgments."""

import hashlib
import json
from collections import Counter

import numpy as np
from PIL import Image

from tools.carmodels.assets import WORK

DIRECTORY = WORK / "sprites"
TRANSCRIPT = (
    "Visual inspection of shading/bounded-comparison.png, three columns: unlit, "
    "ao_untextured, studio_neutral. The Focus SVT is blue with white headlights and "
    "black window regions in both unlit and ao_untextured. The Ford GT has a red body, "
    "white racing stripes, round white number markings, and a visible rear engine "
    "panel in both unlit and ao_untextured. In the earlier shading/comparison.png, "
    "all-material AO darkens those headlight and engine details. The SC430 has a white "
    "body and exposed engine area in both unlit and ao_untextured; the latter shows "
    "darker narrow recesses near its window edges. The MCLA GT-R is a nearly flat "
    "white silhouette in unlit, with a few dark slits; ao_untextured makes its hood "
    "creases, vents, bumper outlines and roof boundary visible. The MCLA Camaro is "
    "also nearly flat white in unlit; ao_untextured reveals hood, roof and bumper "
    "contours. Window regions on those MCLA cars remain pale; missing native glass "
    "colour has not been recovered. All three columns have matching outer shapes. "
    "The neutral studio column has softer shading and visible render noise. This "
    "is an agent's image transcript, not an independent verification of the pixels."
)


def image_summary(rows, selected_key, questions):
    summary = {}
    for group in ["development", "heldout"]:
        group_rows = [
            r for r in rows if r["expected"].get("group") == group and selected_key in r["expected"]
        ]
        summary[group] = {"comparisons": len(group_rows)}
        for q in questions:
            summary[group][q] = dict(
                Counter(
                    "refined"
                    if r["answers"][q]["choice"] == r["expected"][selected_key]
                    else "baseline"
                    for r in group_rows
                )
            )
        summary[group]["difference_visibility"] = dict(
            Counter(
                "yes"
                if r["answers"]["difference_visible"]["noul"] >= 0.7
                else "no"
                if r["answers"]["difference_visible"]["noul"] <= 0.3
                else "uncertain"
                for r in group_rows
            )
        )
    return summary


def main():
    sampling = json.loads((DIRECTORY / "refinement/production-comparison.json").read_text())
    improvements = {}
    rows = sampling["rows"]
    for group in ["development", "heldout"]:
        codes = sorted({r["code"] for r in rows if r["group"] == group})
        lookup = {(r["code"], r["candidate"]): r for r in rows if r["group"] == group}
        improvements[group] = {}
        for pixels in [128, 256, 512]:
            p = str(pixels)

            def values(candidate, lookup=lookup, p=p, codes=codes):
                return np.array(
                    [sum(lookup[c, candidate]["display_metrics"][p].values()) for c in codes]
                )

            before, after = values("direct_256"), values("supersample_512_box_linear_premultiplied")
            rng = np.random.default_rng(20261102)
            draws = rng.integers(0, len(codes), (10000, len(codes)))
            bootstrap = 1 - np.mean(after[draws], axis=1) / np.mean(before[draws], axis=1)
            improvements[group][p] = {
                "relative_reduction": float(1 - after.mean() / before.mean()),
                "bootstrap_95_interval": np.quantile(bootstrap, [0.025, 0.975]).tolist(),
                "cars_improved": int(sum(after < before)),
                "cars": len(codes),
            }
    sampling_images = json.loads((DIRECTORY / "refinement/jev/results.json").read_text())
    shading_images = json.loads((DIRECTORY / "shading/jev/results.json").read_text())
    split = json.loads((DIRECTORY / "shading/split.json").read_text())
    silhouettes = []
    for group, codes in split.items():
        for code in codes:
            before, after = [
                np.array(Image.open(DIRECTORY / "shading" / mode / (code + ".png")))
                for mode in ["unlit", "ao_untextured"]
            ]
            a, b = before[..., 3] > 127, after[..., 3] > 127
            silhouettes.append(
                {
                    "code": code,
                    "group": group,
                    "mask_iou": float(np.count_nonzero(a & b) / np.count_nonzero(a | b)),
                    "alpha_identical": bool(np.array_equal(before[..., 3], after[..., 3])),
                }
            )
    controls = []
    for stage, records in [("sampling", sampling_images), ("shading", shading_images)]:
        for r in records:
            kind = r["expected"].get("control")
            if not kind:
                continue
            a = r["answers"]
            controls.append(
                {
                    "stage": stage,
                    "case": r["case"],
                    "kind": kind,
                    "difference_probability": a["difference_visible"]["noul"],
                    "presence_probability": a[
                        "a_visible" if stage == "sampling" else "a_has_vehicle"
                    ]["noul"],
                }
            )
    report = {
        "sampling_grid_comparisons": len(
            json.loads((DIRECTORY / "refinement/results.json").read_text())
        ),
        "sampling": {
            "metric": (
                "mean linear RGB composite MSE across three backgrounds plus alpha coverage MSE"
            ),
            "gpu_model_limit": (
                "axis-aligned integral sRGB8 premultiplied mip approximation; "
                "transformed/trilinear sampling requires native captures"
            ),
            "summary": sampling["summary"],
            "improvements": improvements,
            "image_judgments": image_summary(sampling_images, "refined", ["detail", "edges"]),
        },
        "shading": {
            "rendered_candidates": sum(
                len(list((DIRECTORY / "shading" / mode).glob("*.json")))
                for mode in ["unlit", "ao", "normal_ao", "studio_neutral", "ao_untextured"]
            ),
            "image_judgments": image_summary(
                shading_images, "bounded", ["surface_detail", "source_detail"]
            ),
            "silhouettes": silhouettes,
            "transcript": TRANSCRIPT,
            "limit": (
                "Occlusion is geometry-derived preview shading, not recovered native game "
                "lighting. Neutral reconstructed materials remain neutral. The full PBR "
                "reference is a controlled Blender presentation, not an authentic native game"
                " capture."
            ),
        },
        "live_image_calls": len(sampling_images) + len(shading_images),
        "controls": controls,
        "raw_results_sha256": {
            str(path.relative_to(WORK)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in [
                DIRECTORY / "refinement/results.json",
                DIRECTORY / "refinement/jev/results.json",
                DIRECTORY / "shading/jev/results.json",
            ]
        },
        "limits": (
            "AB choices can be arbitrary on visually identical inputs. No universal "
            "perceptual win is claimed. Score distributions and Noul uncertainty are "
            "retained. Box estimates never crop sprites; exact geometry and alpha bounds "
            "remain authoritative."
        ),
    }
    (DIRECTORY / "refinement-report.json").write_text(json.dumps(report, indent=2))
    evidence = json.dumps({k: report[k] for k in ["sampling", "shading", "limits"]})
    # Bound semantic evidence; numeric per-car receipts remain separately inspectable.
    decision_evidence = json.dumps(
        {
            "sampling": report["sampling"],
            "shading_judgments": report["shading"]["image_judgments"],
            "transcript": TRANSCRIPT,
            "implementation": (
                "The bounded AO candidate multiplies only unlinked source Base Color "
                "materials by geometry-derived ambient occlusion. Linked texture and "
                "vertex-color inputs remain their original emission inputs. Alpha and "
                "geometry are unchanged. Whole-material AO also darkens baked texture detail;"
                " it was rejected. Neutral studio lighting shifts source paint brightness."
            ),
            "limits": report["limits"],
        }
    )
    jobs = [
        {
            "id": "sprite-refinement-transcript-screen",
            "tool": "jev_screen",
            "arguments": {
                "text": TRANSCRIPT,
                "purpose": (
                    "Use image observations as evidence when selecting a source-sprite "
                    "material policy."
                ),
            },
        },
        {
            "id": "sprite-refinement-transcript-audit",
            "tool": "jev_audit",
            "arguments": {
                "source": TRANSCRIPT,
                "records": [
                    {
                        "id": "texture_details",
                        "request": (
                            "What happens to the Ford GT's authored stripes and engine detail"
                            " under bounded AO?"
                        ),
                        "value": "The white stripes and visible engine panel remain present.",
                    },
                    {
                        "id": "white_geometry",
                        "request": "What does bounded AO reveal on the pale MCLA models?",
                        "value": (
                            "Hood, roof and bumper contours become visible; window regions "
                            "remain pale."
                        ),
                    },
                    {
                        "id": "limitation",
                        "request": "Has original native MCLA glass colour been recovered?",
                        "value": "No; missing native glass colour has not been recovered.",
                    },
                ],
            },
        },
        {
            "id": "sprite-refinement-sampling-selection",
            "tool": "jev_decide",
            "arguments": {
                "decision": "Select the measured sampling recipe for 256px source-sprite frames.",
                "evidence": decision_evidence,
                "priorities": (
                    "Keep the existing 256px runtime frame footprint and physical screen "
                    "scale; maximize fidelity to source-mesh projections. Prefer "
                    "independently measured reductions to uncertain aesthetic votes. Offline "
                    "bake time may increase."
                ),
                "candidates": [
                    {
                        "id": "direct_256",
                        "description": (
                            "Render directly at 256px, 16 samples. Existing runtime frame size."
                        ),
                    },
                    {
                        "id": "supersample_512",
                        "description": (
                            "Render 512px, 16 samples at identical framing, then box-average "
                            "in linear light with premultiplied alpha to 256px. Lower "
                            "measured error on development and held-out cars."
                        ),
                    },
                ],
                "requirements": [
                    "Final frames remain 256 by 256 pixels.",
                    "Mean held-out sampling error decreases relative to direct 256px rendering.",
                ],
            },
        },
        {
            "id": "sprite-refinement-shading-selection",
            "tool": "jev_decide",
            "arguments": {
                "decision": (
                    "Select source-sprite shading that preserves texture detail and reveals "
                    "otherwise flat untextured mesh surfaces."
                ),
                "evidence": decision_evidence,
                "priorities": (
                    "The user wants fine detail faithful to the 3D models in top-down 2D. "
                    "Preserve source paint and livery texture inputs. Use source geometry for"
                    " shading, without inventing missing glass colours. Uncertain AB votes "
                    "are advisory; compare actual source inputs and observed defects."
                ),
                "candidates": [
                    {
                        "id": "unlit",
                        "description": (
                            "Emit source base colour everywhere; preserves textures but "
                            "leaves pale untextured surfaces flat."
                        ),
                    },
                    {
                        "id": "ao_untextured",
                        "description": (
                            "Preserve linked textures/vertex colours as emission. Apply "
                            "ambient occlusion only to unlinked flat material colours, "
                            "revealing geometry on neutral source surfaces. Source alpha and "
                            "geometry remain unchanged."
                        ),
                    },
                    {
                        "id": "ao_everywhere",
                        "description": (
                            "Apply ambient occlusion to every source material, including "
                            "baked textured paint; observed darkened headlights and engine "
                            "details."
                        ),
                    },
                ],
                "requirements": [
                    "Linked source texture and vertex-colour inputs remain unmodified.",
                    "Untextured surface shape contributes visible shading.",
                ],
            },
        },
        {
            "id": "sprite-refinement-claims",
            "tool": "jev_verify",
            "arguments": {
                "evidence": evidence,
                "claims": [
                    (
                        "The sampling refinement reduces mean held-out color-and-coverage "
                        "error under the reported approximate mipmap protocol."
                    ),
                    "The new shading has not recovered authentic native glass colours or lighting.",
                    (
                        "Jev's held-out image comparisons establish a universal clear "
                        "perceptual improvement for every car."
                    ),
                ],
            },
        },
    ]
    (DIRECTORY / "refinement-judgment-jobs.json").write_text(json.dumps(jobs, indent=2))
    print("Wrote experiment report and five bounded evidence judgments")


if __name__ == "__main__":
    main()

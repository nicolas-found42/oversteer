"""Reproducible visual Jev experiments with counterbalanced negative controls.

The experimental image API supplies advisory judgments. Every exact image-bearing
request/response is retained, and reported cost is reconciled with the shared $5 cap.
Numerical geometry/coverage tests remain independent of these probabilities.
"""

import argparse
import base64
import concurrent.futures
import hashlib
import io
import json
import os
import threading
import urllib.request
import uuid

from PIL import Image

from tools.carmodels.assets import ROOT, WORK

DIRECTORY = WORK / "sprites/experiments"
BUDGET = ROOT / "artifacts/carmodels-research/jev-budget.json"
LOCK = threading.Lock()
CASES = [
    "F350",
    "FOCUS_SVT",
    "FORD_GT",
    "EXPLORER",
    "GT4_BENZ0001",
    "GT4_DAIH0006",
    "GT4_DODG0005",
    "GT4_LNCA0003",
    "GT4_SUBR0019",
    "GT4_MINI0001",
    "GT4_TOYT0008",
    "GT4_FORD0007",
    "MC3_VP_SC430_04",
    "MC3_VP_D_H3T_05",
    "MCLA_VP_NSN_GTR_08",
    "GT4_PEUG0001",
]
QUESTIONS = {
    "paint": {
        "type": "choice",
        "instructions": "Which candidate preserves the original paint and livery colors "
        "in `reference`?",
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "shape": {
        "type": "choice",
        "instructions": "Which candidate preserves the vehicle's body outline and "
        "proportions in `reference`?",
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "front": {
        "type": "choice",
        "instructions": "Which candidate preserves the front-to-rear orientation in `reference`?",
        "criteria": {
            "candidate_a": "The image in `candidate_a`.",
            "candidate_b": "The image in `candidate_b`.",
        },
    },
    "a_has_vehicle": {"type": "noul", "instructions": "Is a vehicle visible in `candidate_a`?"},
    "b_has_vehicle": {"type": "noul", "instructions": "Is a vehicle visible in `candidate_b`?"},
}


def asset(image):
    background = Image.new("RGBA", image.size, "#8d939b")
    background.alpha_composite(image.convert("RGBA"))
    background = background.convert("RGB").resize((480, 480), Image.Resampling.NEAREST)
    stream = io.BytesIO()
    background.save(stream, format="PNG")
    data = stream.getvalue()
    key = str(uuid.uuid5(uuid.NAMESPACE_URL, hashlib.sha256(data).hexdigest()))
    return key, {"type": "image", "format": "png", "data_base64": base64.b64encode(data).decode()}


def payload(reference, a, b):
    images = [asset(im) for im in [reference, a, b]]
    return {
        "model": "typesafe/jev-1.14",
        "state": {
            name: key for name, (key, _) in zip(["reference", "candidate_a", "candidate_b"], images)
        },
        "assets": dict(images),
        "questions": QUESTIONS,
    }


def squeezed(image):
    narrow = image.resize((round(image.width * 0.625), image.height))
    frame = Image.new("RGBA", image.size)
    frame.paste(narrow, ((image.width - narrow.width) // 2, 0))
    return frame


def call(case, directory=DIRECTORY):
    label, request, expected = case
    digest = hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest()[:16]
    prefix = directory / (label + "-" + digest)
    response_path = prefix.with_suffix(".response.json")
    if response_path.exists():
        response = json.loads(response_path.read_text())
    else:
        prefix.with_suffix(".request.json").write_text(json.dumps(request))
        with LOCK:
            budget = json.loads(BUDGET.read_text())
            reserve = budget["per_call_reserve_usd"]
            if budget["reserved_usd"] + reserve > budget["cap_usd"]:
                raise RuntimeError("Jev experiment budget exhausted")
            accounting = {
                "id": label,
                "tool": "sprite_image_experiment",
                "request_hash": digest,
                "reserve_usd": reserve,
                "status": "started",
            }
            budget["reserved_usd"] += reserve
            budget["calls"].append(accounting)
            BUDGET.write_text(json.dumps(budget, indent=2))
        http = urllib.request.Request(
            "https://openrouter.ai/api/alpha/decisions",
            data=json.dumps(request).encode(),
            headers={
                "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"],
                "Content-Type": "application/json",
                "TypeSafe-Danger-Zone-Images": "true",
            },
        )
        with urllib.request.urlopen(http, timeout=60) as result:
            response = json.load(result)
        response_path.write_text(json.dumps(response, indent=2))
        with LOCK:
            budget = json.loads(BUDGET.read_text())
            accounting = next(
                r for r in budget["calls"] if r.get("request_hash") == digest and r["id"] == label
            )
            accounting.update(status="returned", usage=response.get("usage"))
            cost = response.get("usage", {}).get("cost")
            if cost is not None:
                accounting["accounted_usd"] = cost
                budget["reserved_usd"] += cost - accounting["reserve_usd"]
            BUDGET.write_text(json.dumps(budget, indent=2))
    answers = response.get("answers", {})
    questions = request["questions"]
    if set(answers) != set(questions):
        raise ValueError("Missing typed image judgments: " + str(response_path))
    for name, question in questions.items():
        answer = answers[name]
        if answer["type"] != question["type"]:
            raise ValueError("Wrong answer type: " + name)
        if question["type"] == "choice":
            if set(answer["probabilities"]) != set(question["criteria"]):
                raise ValueError("Invalid candidate distribution")
            if abs(sum(answer["probabilities"].values()) - 1) > 0.02:
                raise ValueError("Invalid probability total")
            if answer["choice"] not in question["criteria"] or any(
                not 0 <= p <= 1 for p in answer["probabilities"].values()
            ):
                raise ValueError("Invalid typed candidate answer")
        elif question["type"] == "score":
            probabilities = answer["probabilities"]
            values = (
                list(probabilities.values()) if isinstance(probabilities, dict) else probabilities
            )
            if (
                len(values) != len(question["criteria"])
                or any(not 0 <= p <= 1 for p in values)
                or abs(sum(values) - 1) > 0.02
            ):
                raise ValueError("Invalid score distribution")
            if not 0 <= answer["score"] <= len(question["criteria"]) - 1:
                raise ValueError("Invalid score position")
        elif question["type"] == "box":
            box = answer["box"]
            if not (0 <= box["left"] < box["right"] <= 1 and 0 <= box["top"] < box["bottom"] <= 1):
                raise ValueError("Invalid bounding box")
        elif not 0 <= answer["noul"] <= 1:
            raise ValueError("Invalid typed probability")
    return {
        "case": label,
        "request_hash": digest,
        "expected": expected,
        "answers": answers,
        "usage": response.get("usage"),
    }


def cases():
    result = []
    for code in CASES:
        reference = Image.open(WORK / "references" / (code + ".png")).convert("RGBA")
        unlit = Image.open(WORK / "sprites/pilot" / (code + "-unlit.png")).convert("RGBA")
        studio = Image.open(WORK / "sprites/pilot" / (code + "-studio.png")).convert("RGBA")
        for swap in [False, True]:
            a, b = (studio, unlit) if swap else (unlit, studio)
            result.append(
                (code.lower() + "-material-" + str(int(swap)), payload(reference, a, b), {})
            )
        if code not in CASES[:8]:
            continue
        for name, wrong, dimension in [
            ("flip", reference.transpose(Image.Transpose.FLIP_TOP_BOTTOM), "front"),
            ("squeeze", squeezed(reference), "shape"),
            ("blank", Image.new("RGBA", reference.size), "presence"),
            ("desaturate", reference.convert("L").convert("RGBA"), "paint"),
        ]:
            if name == "desaturate":
                wrong.putalpha(reference.getchannel("A"))
            for swap in [False, True]:
                a, b = (wrong, reference) if swap else (reference, wrong)
                expected = {dimension: "candidate_b" if swap else "candidate_a"}
                result.append(
                    (
                        code.lower() + "-" + name + "-" + str(int(swap)),
                        payload(reference, a, b),
                        expected,
                    )
                )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    args = parser.parse_args()
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    jobs = cases()
    if args.run:
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for row in pool.map(call, jobs):
                results.append(row)
                print(row["case"], flush=True)
        (DIRECTORY / "results.json").write_text(json.dumps(results, indent=2))
    else:
        print("Prepared", len(jobs), "counterbalanced live image experiments")

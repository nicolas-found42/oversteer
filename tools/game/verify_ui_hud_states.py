"""Render canonical saved-state variations through normal menu controls.

Progress/wealth fixtures are presentation fixtures, not earned-driving evidence.
"""

import argparse
import copy
import json
from pathlib import Path

import verify

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--base-save", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    base = json.loads(args.base_save.read_text())
    cases = []
    for state, goals in [("partial", ["circuit"]), ("promotion-ready", ["circuit", "drift"])]:
        save = copy.deepcopy(base)
        for goal in goals:
            save["career"]["goal_progress"][f"oversteer-0-{goal}-win"] = {
                "complete": True,
                "value": 1.0,
            }
        path = output / f"{state}-save.json"
        path.write_text(json.dumps(save))
        actions = [
            ("nav:career", state),
            ("career_events", state + "-events"),
            ("event:2", state + "-promotion"),
        ]
        cases.append(make_case(output, state, actions, path))
    poor = copy.deepcopy(base)
    poor["career"]["cash"] = 0
    path = output / "poor-save.json"
    path.write_text(json.dumps(poor))
    cases.append(
        make_case(
            output,
            "poor-cart",
            [
                ("nav:career", None),
                ("nav:garage", None),
                ("nav:custom", None),
                ("custom_page:performance", None),
                ("upgrade:engine", None),
                ("nav:checkout", "insufficient-cart"),
            ],
            path,
        )
    )
    cases.append(
        make_case(
            output,
            "fresh-events",
            [
                ("nav:career", "fresh"),
                ("career_events", "circuit"),
                ("event:1", "drift"),
                ("event:2", "locked"),
                ("event:0", None),
                ("start", "no-wager-unavailable-pink"),
                ("offer_cash", "cash-offered"),
                ("offer_decline", "cash-declined"),
            ],
            args.base_save,
        )
    )
    cases.append(
        make_case(
            output,
            "quick-courses",
            [
                ("nav:quick", "quick-circuit"),
                ("event:1", "quick-drift"),
                ("car_next", None),
                ("car_next", None),
                ("car_next", None),
                ("car_next", "long-car-name"),
            ],
            args.base_save,
        )
    )
    budget = sum(
        1 + sum("capture" in x for x in json.loads(c["ui_actions"].read_text())) for c in cases
    )
    assert budget <= 40
    results = [verify.run_case(c, output, None, screenshot_limit=budget) for c in cases]
    (output / "verification.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
    assert all(result["status"] == "passed" for result in results)


def make_case(output, name, actions, seed):
    plan = [
        {"after_frame": 20 + i * 28, "action": action, **({"capture": capture} if capture else {})}
        for i, (action, capture) in enumerate(actions)
    ]
    path = output / f"{name}-plan.json"
    path.write_text(json.dumps(plan, indent=2) + "\n")
    return {
        "id": name,
        "scenario": "reload",
        "seed_save": seed,
        "ui_actions": path,
        "frames": plan[-1]["after_frame"] + 40,
    }


if __name__ == "__main__":
    main()

"""Bounded rear-quarter observation and same-bitmap research-only chevron comparison."""

import argparse
import hashlib
import html
import json
import subprocess
from pathlib import Path

import background_window
from verify_ui_hud_window import ROOT


def comparison(output, evidence):
    capture = evidence["captures"].get("rear-quarter")
    if not capture:
        return
    filename = capture["file"]
    side = capture["qualifying"][0]["side"]
    digest = hashlib.sha256((output / filename).read_bytes()).hexdigest()
    # The identical original bitmap is displayed twice; SVG is a separate prototype layer.
    page = f"""<!doctype html><meta charset="utf-8"><title>Blind-spot hypothesis</title>
<style>body{{background:#161616;color:#f6ebce;font:16px sans-serif;margin:24px}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}.frame{{position:relative}}img{{width:100%;display:block}}svg{{position:absolute;width:1.46%;height:1.48%;bottom:12%;{side}:2%;overflow:visible}}h2{{font-size:18px}}</style>
<h1>Research only: same captured race frame</h1><p>No game indicator was installed. Compare whether the amber mark helps identify an actually obscured rear-quarter rival. Geometry is a trigger candidate, not proof of a blind spot.</p>
<div class="pair"><section><h2>Current HUD</h2><div class="frame"><img src="{html.escape(filename)}"></div></section><section><h2>Optional amber cue ({side})</h2><div class="frame"><img src="{html.escape(filename)}"><svg viewBox="0 0 28 16" aria-label="research chevron"><path d="M3 3 L14 12 L25 3" fill="none" stroke="#ffb347" stroke-width="3" opacity=".8"/></svg></div></section></div><p>Shared bitmap SHA-256: {digest}. No temporal A/B claim. Inspect the rival and HUD coverage in the observation JSON before deciding keep/omit.</p>"""
    (output / "comparison.html").write_text(page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--input-events",
        type=Path,
        default=ROOT / "data/oversteer/scenarios/ui-hud-instruments.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    plan = output / "input-events.json"
    plan.write_bytes(args.input_events.read_bytes())
    command = [
        str(godot),
        "--path",
        str(ROOT / "godot"),
        "--rendering-driver",
        "metal",
        "--script",
        str(Path(__file__).with_name("ui_hud_blindspot.gd")),
        "--",
        str(output),
        "--scenario",
        "driving",
        "--event",
        "oversteer-0-circuit",
        "--input-events",
        str(plan),
        "--frames",
        "20000",
        "--save-file",
        str(output / "save.json"),
        "--settings-dir",
        str(output / "settings"),
    ]
    environment = background_window.environment(godot)
    with (output / "runtime.log").open("w") as log:
        result = subprocess.run(
            command,
            env=environment,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=100,
        )
    runtime = (output / "runtime.log").read_text()
    if result.returncode or any(
        marker in runtime for marker in ("ERROR:", "SCRIPT ERROR", "panicked")
    ):
        raise RuntimeError("Blind-spot observation failed; inspect runtime.log")
    evidence = json.loads((output / "blindspot.json").read_text())
    if len(list(output.glob("*.png"))) > 2 or not evidence["samples"]:
        raise RuntimeError("Capture budget exceeded or no real race samples")
    comparison(output, evidence)
    print(
        json.dumps(
            {
                "status": evidence["status"],
                "captures": list(evidence["captures"]),
                "samples": len(evidence["samples"]),
                "shipped_indicator": False,
            }
        )
    )


if __name__ == "__main__":
    main()

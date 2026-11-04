"""Capture minimum-size native windows, preserving focus and viewport rendering."""

import argparse
import json
import subprocess
import time
from pathlib import Path

import background_window

ROOT = Path(__file__).resolve().parents[2]
WINDOW_ID = """import CoreGraphics
import Foundation
let pid = Int(CommandLine.arguments[1])!
let list = CGWindowListCopyWindowInfo(.optionAll, kCGNullWindowID) as? [[String:Any]] ?? []
for window in list where (window[kCGWindowOwnerPID as String] as? Int) == pid && (window[kCGWindowLayer as String] as? Int) == 0 {
 print(window[kCGWindowNumber as String]!)
}
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    seen = []
    with (output / "runtime.log").open("w") as log:
        process = subprocess.Popen(
            [
                str(godot),
                "--path",
                str(ROOT / "godot"),
                "--rendering-driver",
                "metal",
                "--script",
                str(Path(__file__).with_name("ui_hud_window.gd")),
                "--",
                str(output),
                "--save-file",
                str(output / "save.json"),
                "--settings-dir",
                str(output / "settings"),
            ],
            env=background_window.environment(godot),
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 150
            while process.poll() is None and time.monotonic() < deadline:
                request = output / "window-request.json"
                if request.exists():
                    state = json.loads(request.read_text())
                    label = state["label"]
                    if label not in [item["label"] for item in seen]:
                        if len(seen) >= 5:
                            raise RuntimeError("Five-image window budget exceeded")
                        ids = subprocess.check_output(
                            ["swift", "-e", WINDOW_ID, str(process.pid)], text=True
                        ).splitlines()
                        if len(ids) != 1:
                            raise RuntimeError(f"Expected exactly one game window: {ids}")
                        subprocess.run(
                            [
                                "screencapture",
                                "-x",
                                "-o",
                                "-l",
                                ids[0],
                                str(output / f"{label}.png"),
                            ],
                            check=True,
                        )
                        seen.append({**state, "window_id": ids[0]})
                        (output / "window-evidence.json").write_text(
                            json.dumps(seen, indent=2) + "\n"
                        )
                        (output / f"{label}.done").touch()
                time.sleep(0.1)
            if process.poll() is None:
                raise RuntimeError("Window verification timeout")
            if process.returncode or len(seen) != 5:
                raise RuntimeError(
                    f"Window check failed: exit={process.returncode}, captures={len(seen)}"
                )
        finally:
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    main()

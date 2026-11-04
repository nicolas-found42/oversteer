"""Record one finite real-window menu movie without changing render cadence/focus."""

import argparse
import json
import subprocess
import time
from pathlib import Path

import background_window
from verify_ui_hud_window import ROOT, WINDOW_ID


def validate_motion(evidence):
    settled = []
    actions = evidence["actions"]
    for index, action in enumerate(actions):
        next_time = actions[index + 1]["seconds"] if index + 1 < len(actions) else float("inf")
        sample = next(
            (
                sample
                for sample in evidence["samples"]
                if action["seconds"] + 0.2 <= sample["seconds"] < next_time
            ),
            None,
        )
        if sample is None:  # Intentionally interrupted before its 200 ms reveal ends.
            continue
        if not (
            sample["visible"]
            and sample["alpha"] >= 0.99
            and max(abs(value) for value in sample["position"]) < 0.5
            and not sample["destination_visible"]
            and sample["focus"] != "none"
        ):
            raise RuntimeError(f"Unsettled menu after {action['action']}: {sample}")
        settled.append({"action": action["action"], "seconds": sample["since_action"]})
    if len(settled) < 7:
        raise RuntimeError("Missing seven uninterrupted reveal checkpoints")
    return settled


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    godot = ROOT / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    report = {"movie_seconds": 12, "movie_budget": 1, "still_budget": 4, "status": "running"}
    recorder = None
    with (
        (output / "runtime.log").open("w") as log,
        (output / "recording.log").open("w") as recording_log,
    ):
        process = subprocess.Popen(
            [
                str(godot),
                "--path",
                str(ROOT / "godot"),
                "--rendering-driver",
                "metal",
                "--script",
                str(Path(__file__).with_name("ui_hud_motion.gd")),
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
            deadline = time.monotonic() + 90
            while not (output / "motion-ready").exists():
                if process.poll() is not None or time.monotonic() > deadline:
                    raise RuntimeError("Game did not reach motion-ready title")
                time.sleep(0.05)
            ids = subprocess.check_output(
                ["swift", "-e", WINDOW_ID, str(process.pid)], text=True
            ).splitlines()
            if len(ids) != 1:
                raise RuntimeError(f"Expected one game window: {ids}")
            report["window_id"] = ids[0]
            report["recording_started_monotonic"] = time.monotonic()
            recorder = subprocess.Popen(
                [
                    "screencapture",
                    "-x",
                    "-v",
                    "-V12",
                    "-l" + ids[0],
                    str(output / "menu-motion.mov"),
                ],
                stdout=recording_log,
                stderr=subprocess.STDOUT,
            )
            # This waits only in the observer; the game continues its normal render loop.
            time.sleep(0.4)
            if recorder.poll() is not None:
                raise RuntimeError(
                    "OS window recording exited before the handshake; inspect recording.log"
                )
            (output / "recording-started").touch()
            recorder.wait(timeout=20)
            (output / "recording-done").touch()
            process.wait(timeout=15)
            movie = output / "menu-motion.mov"
            runtime = (output / "runtime.log").read_text()
            if recorder.returncode or not movie.exists() or movie.stat().st_size == 0:
                raise RuntimeError("OS window video unavailable; renderer was not changed")
            if process.returncode or any(
                marker in runtime for marker in ("SCRIPT ERROR", "ERROR:", "panicked")
            ):
                raise RuntimeError("Motion script failed; inspect runtime.log")
            evidence = json.loads((output / "motion.json").read_text())
            if not evidence["checks"] or not all(item["passed"] for item in evidence["checks"]):
                raise RuntimeError("Motion observations failed")
            settled = validate_motion(evidence)
            report.update(
                status="passed",
                samples=len(evidence["samples"]),
                actions=len(evidence["actions"]),
                movie_bytes=movie.stat().st_size,
                first_samples_after_200ms=settled,
            )
        except Exception as error:
            report.update(status="failed", error=str(error))
            raise
        finally:
            if recorder is not None and recorder.poll() is None:
                recorder.terminate()
                recorder.wait(timeout=5)
            if process.poll() is None:
                process.terminate()
                process.wait(timeout=10)
            (output / "verification.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()

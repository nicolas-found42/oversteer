#!/usr/bin/env python3
"""Four isolated headless processes: failed save, recovery, crash, telemetry failure.

Requires prepared runtime inputs and the current dev extension. Copies the seed;
never changes the supplied save. No windows, captures, network or asset publication.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import diagnostics
from build import GODOT, ROOT, require_runtime_inputs


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def retrieve(folder, since):
    command = [
        sys.executable,
        str(ROOT / "tools/game/diagnostics.py"),
        "query",
        "--directory",
        str(folder / "diagnostics"),
        "--since",
        since,
        "--until",
        datetime.now(timezone.utc).isoformat(),
        "--limit",
        "500",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def verify(seed, output):
    require_runtime_inputs()
    output.mkdir(parents=True, exist_ok=False)
    seed_bytes = seed.read_bytes()
    json.loads(seed_bytes)
    started = datetime.now(timezone.utc).isoformat()
    save = output / "career.json"
    backup = output / "career.json.backup"
    save.write_bytes(seed_bytes)
    backup.mkdir()
    truth = {
        "injection": "directory at backup destination",
        "primary_before_sha256": hashlib.sha256(seed_bytes).hexdigest(),
    }
    write(output / "ground-truth.json", truth)
    command = [
        str(GODOT),
        "--headless",
        "--path",
        str(ROOT / "godot"),
        "--quit-after",
        "120",
        "--",
        "--save-file",
        str(save),
        "--settings-dir",
        str(output / "settings"),
    ]

    def run(label):
        with (output / f"{label}-runtime.log").open("w") as log:
            return diagnostics.recorded_run(
                command, stdout=log, stderr=subprocess.STDOUT, timeout=90
            ).returncode

    first_exit = run("failure")
    first = retrieve(output, started)
    write(output / "retrieved-failure.json", first)
    # Reconstruction deliberately consumes only returned evidence, not the seed/injection.
    failures = [
        r
        for r in first["records"]
        if r["event"] == "operation.end"
        and r.get("stage") == "career.save"
        and r.get("outcome") == "error"
    ]
    failed = failures[-1]
    related = [
        r
        for r in first["records"]
        if r["session"] == failed["session"] and r.get("parent") == failed["operation"]
    ]
    reconstruction = {
        "session": failed["session"],
        "operation": failed["operation"],
        "backup_selected": any(r.get("target") == "backup" for r in related),
        "replacement_type_conflict": any(
            r.get("stage") == "replace" and r.get("category") == "IsADirectory" for r in related
        ),
        "write_and_sync_succeeded": all(
            any(r.get("stage") == stage and r.get("outcome") == "ok" for r in related)
            for stage in ["write", "sync"]
        ),
        "limits": "Does not establish who created the directory. No match cannot prove absence. This is a storage failure reconstruction, not a fix to application save semantics.",
    }
    write(output / "reconstruction.json", reconstruction)
    # Compare with injection only after writing reconstruction.
    ground_truth = json.loads((output / "ground-truth.json").read_text())
    primary_unchanged = (
        hashlib.sha256(save.read_bytes()).hexdigest() == ground_truth["primary_before_sha256"]
    )
    backup.rmdir()
    backup.write_bytes(seed_bytes)
    save.write_text("deliberately invalid local fixture")
    recovery_exit = run("recovery")
    recovered = retrieve(output, started)
    write(output / "retrieved-recovery.json", recovered)
    # Abrupt termination: the trigger is separate ground truth, never a claimed cause in logs.
    crash_command = command.copy()
    del crash_command[crash_command.index("--quit-after") : crash_command.index("--quit-after") + 2]
    before = {r["session"] for r in recovered["records"]}
    with (output / "crash-runtime.log").open("w") as log:
        with subprocess.Popen(crash_command, stdout=log, stderr=subprocess.STDOUT) as process:
            deadline = time.monotonic() + 30
            while process.poll() is None and time.monotonic() < deadline:
                rows = retrieve(output, started)["records"]
                if any(r["session"] not in before and r["event"] == "career.loaded" for r in rows):
                    break
                time.sleep(0.1)
            process.kill()
            process.wait(timeout=10)
    crashed = retrieve(output, started)
    write(output / "retrieved-crash.json", crashed)
    crash_sessions = {r["session"] for r in crashed["records"]} - before
    # Make telemetry unavailable while preserving valid application storage.
    (output / "diagnostics").rename(output / "retained-diagnostics")
    (output / "diagnostics").write_text("unavailable fixture")
    unavailable_exit = run("unavailable")
    unavailable_query = diagnostics.query(output / "diagnostics", 0, 9999999999999)
    write(output / "retrieved-unavailable.json", unavailable_query)
    checks = {
        "native_normal_exit_on_handled_failure": first_exit == 0,
        "reconstructed_backup_type_conflict": reconstruction["backup_selected"]
        and reconstruction["replacement_type_conflict"]
        and reconstruction["write_and_sync_succeeded"],
        "primary_unchanged_after_failed_backup": primary_unchanged,
        "new_process_recovered_backup": recovery_exit == 0
        and any(
            r["event"] == "career.loaded" and r.get("source") == "backup"
            for r in recovered["records"]
        ),
        "corrupt_bytes_preserved": any(
            p.read_text() == "deliberately invalid local fixture"
            for p in output.glob("career.json.corrupt-*")
        ),
        "crash_prefix_survives_without_invented_terminal": len(crash_sessions) == 1
        and not any(
            r["session"] in crash_sessions and r["event"] == "session.end"
            for r in crashed["records"]
        ),
        "telemetry_failure_preserves_game_save": unavailable_exit == 0
        and isinstance(json.loads(save.read_text()), dict),
        "query_failure_explicit": not unavailable_query["query_complete"],
        "queries_complete_within_retained_files": all(
            q["query_complete"] for q in [first, recovered, crashed]
        ),
    }
    result = {
        "checks": checks,
        "passed": all(checks.values()),
        "native_launches": 4,
        "screenshots": 0,
        "scope": "headless storage/lifecycle, not rendering/audio/performance acceptance",
        "library_sha256": hashlib.sha256(
            (ROOT / "godot/bin/debug/liboversteer_godot.dylib").read_bytes()
        ).hexdigest(),
    }
    write(output / "verification.json", result)
    print(json.dumps(result, indent=2))
    return result["passed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-save", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    return 0 if verify(args.seed_save.resolve(), args.output.resolve()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

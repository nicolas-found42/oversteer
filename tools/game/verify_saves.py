#!/usr/bin/env python3
"""Check real-process save recovery using a save produced by a native scenario."""

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from verify import ROOT, digest, native_command, runtime_identity


def run_case(name, destination, seed, app, offline=False):
    folder = destination / name
    folder.mkdir()
    save = folder / "save.json"
    backup = folder / "save.json.backup"
    damaged_primary = b"invalid primary retained by native verification\n"
    damaged_backup = b"invalid backup retained by native verification\n"
    if name == "primary":
        save.write_bytes(seed)
    elif name == "backup-recovery":
        save.write_bytes(damaged_primary)
        backup.write_bytes(seed)
    elif name == "missing-primary":
        backup.write_bytes(seed)
    elif name == "both-corrupt":
        save.write_bytes(damaged_primary)
        backup.write_bytes(damaged_backup)
    elif name == "backup-write-failure":
        save.write_bytes(seed)
        backup.mkdir()
    command = native_command(app, offline)
    command.extend(
        ["--", "--scenario", "reload", "--frames", "120", "--capture", folder, "--save-file", save]
    )
    command.extend(["--settings-dir", folder / "settings"])
    with (folder / "runtime.log").open("w") as log:
        process = subprocess.run(
            [str(value) for value in command],
            cwd=folder if app else ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
            timeout=300,
        )
    if name == "both-corrupt":
        error = folder / "load-error.json"
        checks = {
            "failure_exit": process.returncode == 1,
            "load_error_reported": error.exists()
            and json.loads(error.read_text()).get("ok") is False,
            "primary_untouched": save.read_bytes() == damaged_primary,
            "backup_untouched": backup.read_bytes() == damaged_backup,
            "no_success_report": not (folder / "scenario.json").exists(),
        }
    else:
        report_file = folder / "scenario.json"
        report = json.loads(report_file.read_text()) if report_file.exists() else {}
        expected_source = "backup" if name in {"backup-recovery", "missing-primary"} else "primary"
        checks = {
            "report_exists": bool(report),
            "loaded_expected_source": report.get("load_status", {}).get("source")
            == expected_source,
            "loaded_exact_seed_state": report.get("saved_state") == json.loads(seed),
            "capture_exists": (folder / "final.png").exists(),
        }
        if name == "backup-write-failure":
            checks.update(
                failure_exit=process.returncode == 1,
                save_error_reported=report.get("save_status", {}).get("ok") is False,
                primary_untouched=save.read_bytes() == seed,
                backup_directory_untouched=backup.is_dir(),
            )
        else:
            checks.update(
                normal_exit=process.returncode == 0,
                save_written=report.get("save_status", {}).get("ok") is True,
                exact_disk_state=json.loads(save.read_text()) == json.loads(seed),
            )
        if name == "backup-recovery":
            retained = report.get("load_status", {}).get("preserved")
            checks["damaged_primary_retained"] = (
                bool(retained) and Path(retained).read_bytes() == damaged_primary
            )
        if name == "missing-primary":
            checks["no_invented_damaged_primary"] = (
                report.get("load_status", {}).get("preserved") is None
            )
    result = {
        "case": name,
        "command": [str(value) for value in command],
        "working_directory": str(folder if app else ROOT),
        "exit_code": process.returncode,
        "checks": checks,
        "passed": all(checks.values()),
    }
    (folder / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {
                "case": name,
                "passed": result["passed"],
                "failed": [key for key, value in checks.items() if not value],
            }
        ),
        flush=True,
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-save", type=Path, required=True)
    parser.add_argument("--app", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    source = options.seed_save.resolve()
    seed = source.read_bytes()
    json.loads(seed)
    # Keep the scenario's seed and provenance together, including a source hash.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = (options.output or ROOT / f"build/verification/{stamp}-saves").resolve()
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(source, destination / "seed-save.json")
    app = options.app.resolve() if options.app else None
    library = (
        app / "Contents/Frameworks/liboversteer_godot.dylib"
        if app
        else ROOT / "godot/bin/debug/liboversteer_godot.dylib"
    )
    result = {
        "seed_source": str(source),
        "seed_sha256": digest(source),
        "binary_sha256": digest(library),
        "runtime_resources": runtime_identity(app),
        "app": str(app) if app else None,
        "network_denied_by_os": options.offline,
        "cases": [],
    }
    for name in [
        "primary",
        "backup-recovery",
        "missing-primary",
        "both-corrupt",
        "backup-write-failure",
    ]:
        result["cases"].append(run_case(name, destination, seed, app, options.offline))
        (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    result["inputs_unchanged"] = (
        digest(source) == result["seed_sha256"]
        and digest(library) == result["binary_sha256"]
        and runtime_identity(app) == result["runtime_resources"]
    )
    result["passed"] = result["inputs_unchanged"] and all(
        case["passed"] for case in result["cases"]
    )
    (destination / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()

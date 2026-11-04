#!/usr/bin/env python3
"""Bounded local event journal, incident queries, and an opt-in legacy command wrapper."""

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FILE_BYTES = 4 * 1024 * 1024
EVENT_BYTES = 2048
TOKEN = re.compile(r"[A-Za-z0-9_.:-]{1,96}\Z")
TEXT_FIELDS = {
    "operation",
    "parent_operation",
    "outcome",
    "category",
    "stage",
    "label",
    "source_id",
    "asset_id",
    "dependency_id",
    "command",
    "component",
}
NUMBER_FIELDS = {"attempt", "duration_ms", "exit_code", "http_status", "argument_count"}


class Journal:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.source_id = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.session = uuid.uuid4().hex
        self.sequence = 0
        self.dropped = 0
        self.warned = False
        self.started = time.monotonic()
        self.window = self.started
        self.count = 0
        self.lock = threading.Lock()

    def emit(self, event, **fields):
        with self.lock:
            self.sequence += 1
            now = time.monotonic()
            if now - self.window >= 1:
                self.window, self.count = now, 0
            self.count += 1
            row = {
                "schema": 1,
                "timestamp_ms": int(time.time() * 1000),
                "elapsed_ms": int((now - self.started) * 1000),
                "component": "tools",
                "session": self.session,
                "sequence": self.sequence,
                "event": event,
                "dropped_before": self.dropped,
                "collector_id": self.source_id,
            }
            for key, value in fields.items():
                if key in TEXT_FIELDS and isinstance(value, str) and TOKEN.fullmatch(value):
                    row[key] = value
                elif key in NUMBER_FIELDS and isinstance(value, int):
                    row[key] = value
            try:
                payload = (json.dumps(row, separators=(",", ":")) + "\n").encode()
                if not TOKEN.fullmatch(event) or len(payload) > EVENT_BYTES or self.count > 64:
                    raise OSError("event bound")
                self.directory.mkdir(parents=True, exist_ok=True, mode=0o700)
                with os.fdopen(
                    os.open(self.directory / "journal.lock", os.O_CREAT | os.O_WRONLY, 0o600), "wb"
                ) as lock:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    path = self.directory / "journal.jsonl"
                    if path.exists() and path.stat().st_size + len(payload) > FILE_BYTES:
                        path.replace(self.directory / "journal.previous.jsonl")
                    with os.fdopen(
                        os.open(path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600),
                        "wb",
                        buffering=0,
                    ) as output:
                        if output.write(payload) != len(payload):
                            raise OSError("short journal write")
                self.dropped = 0
            except (OSError, ValueError):
                self.dropped += 1
                if not self.warned:
                    try:
                        print(
                            "Oversteer diagnostics incomplete: write, contention, size or rate limit",
                            file=sys.stderr,
                        )
                    except (OSError, ValueError):
                        pass  # A closed stderr must not make telemetry fatal either.
                    self.warned = True


JOURNAL = Journal(os.environ.get("OVERSTEER_DIAGNOSTICS_DIR", ROOT / "build/diagnostics"))


def emit(event, **fields):
    JOURNAL.emit(event, **fields)


@contextmanager
def attempt(operation, number, stage, dependency_id, source_id=None):
    fields = {
        "operation": operation,
        "attempt": number,
        "stage": stage,
        "dependency_id": dependency_id,
        "component": "provider",
        "source_id": source_id,
    }
    started = time.monotonic()
    emit("provider.start", **fields)
    try:
        yield
    except BaseException as error:
        emit(
            "provider.end",
            **fields,
            outcome="error",
            category=type(error).__name__,
            http_status=getattr(error, "code", None),
            duration_ms=int((time.monotonic() - started) * 1000),
        )
        raise
    else:
        emit(
            "provider.end",
            **fields,
            outcome="ok",
            duration_ms=int((time.monotonic() - started) * 1000),
        )


def recorded_run(arguments, **kwargs):
    """Preserve subprocess.run behavior; record safe metadata, never argv/output/env."""
    operation = uuid.uuid4().hex
    started = time.monotonic()
    fields = {
        "operation": operation,
        "command": Path(str(arguments[0])).name,
        "argument_count": len(arguments),
        "parent_operation": os.environ.get("OVERSTEER_PARENT_OPERATION", ""),
    }
    # Hash only a bounded repository Python entry point, never an arbitrary argument/file.
    if len(arguments) > 1:
        candidate = Path(str(arguments[1]))
        try:
            candidate = (Path(kwargs.get("cwd", Path.cwd())) / candidate).resolve()
            if (
                candidate.is_relative_to(ROOT)
                and candidate.suffix == ".py"
                and candidate.stat().st_size <= 1024 * 1024
            ):
                fields["source_id"] = hashlib.sha256(candidate.read_bytes()).hexdigest()
                fields["label"] = candidate.name
        except OSError:
            pass  # Missing script remains the child's failure to report.
    emit("process.start", **fields)
    kwargs["env"] = {
        **(kwargs.get("env") if kwargs.get("env") is not None else os.environ),
        "OVERSTEER_PARENT_OPERATION": operation,
    }
    try:
        result = subprocess.run(arguments, **kwargs)
    except BaseException as error:
        emit(
            "process.end",
            **fields,
            outcome="error",
            category=type(error).__name__,
            duration_ms=int((time.monotonic() - started) * 1000),
            exit_code=getattr(error, "returncode", None),
        )
        raise
    emit(
        "process.end",
        **fields,
        outcome="ok" if result.returncode == 0 else "error",
        exit_code=result.returncode,
        duration_ms=int((time.monotonic() - started) * 1000),
    )
    return result


def instant(text):
    value = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if value.tzinfo is None:
        raise ValueError("Time requires an explicit timezone (Z or +/-HH:MM)")
    return int(value.timestamp() * 1000)


def query(
    directory,
    start,
    end,
    *,
    session=None,
    operation=None,
    event=None,
    source_id=None,
    component=None,
    limit=500,
    max_bytes=8 * 1024 * 1024,
):
    if start > end or not 1 <= limit <= 10000 or not 1 <= max_bytes <= 8 * 1024 * 1024:
        raise ValueError("Invalid time range or query bounds")
    if operation is not None and operation.isdigit() and session is None:
        raise ValueError("Numeric operation IDs require --session")
    rows, problems, scanned, files = [], [], 0, []
    # Read under the same nonblocking lock as writers. Contention is an explicit gap.
    try:
        with (Path(directory) / "journal.lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
            for name in ["journal.previous.jsonl", "journal.jsonl"]:
                path = Path(directory) / name
                try:
                    source = path.open("rb")
                except FileNotFoundError:
                    if name == "journal.jsonl":
                        problems.append({"file": name, "error": "missing_current"})
                    continue
                with source:
                    files.append(name)
                    line = 0
                    while scanned < max_bytes:
                        raw = source.readline(min(EVENT_BYTES + 1, max_bytes - scanned))
                        if not raw:
                            break
                        scanned += len(raw)
                        line += 1
                        if len(raw) > EVENT_BYTES or not raw.endswith(b"\n"):
                            problems.append(
                                {"file": name, "line": line, "error": "oversized_or_partial_record"}
                            )
                            break
                        try:
                            row = json.loads(raw)
                            valid = (
                                isinstance(row, dict)
                                and type(row.get("schema")) is int
                                and row["schema"] == 1
                                and type(row.get("timestamp_ms")) is int
                                and isinstance(row.get("session"), str)
                                and TOKEN.fullmatch(row["session"])
                                and isinstance(row.get("event"), str)
                                and TOKEN.fullmatch(row["event"])
                                and type(row.get("sequence")) is int
                                and row["sequence"] > 0
                            )
                            if not valid:
                                raise ValueError("schema")
                        except (ValueError, UnicodeError):
                            problems.append({"file": name, "line": line, "error": "invalid_record"})
                            continue
                        if not start <= row["timestamp_ms"] <= end:
                            continue
                        filters = [
                            ("session", session),
                            ("event", event),
                            ("source_id", source_id),
                            ("component", component),
                        ]
                        if any(
                            wanted is not None and row.get(key) != wanted for key, wanted in filters
                        ):
                            continue
                        if (
                            operation is not None
                            and str(row.get("operation", row["sequence"])) != operation
                            and str(row.get("parent")) != operation
                            and row.get("parent_operation") != operation
                        ):
                            continue
                        if len(rows) == limit:
                            problems.append({"error": "result_limit", "limit": limit})
                            break
                        rows.append(row)
                    if scanned >= max_bytes:
                        problems.append({"error": "byte_limit", "limit": max_bytes})
                        break
    except OSError as error:
        problems.append({"error": type(error).__name__, "errno": error.errno})
    rows.sort(key=lambda row: (row["timestamp_ms"], row["session"], row["sequence"]))
    return {
        "records": rows,
        "problems": problems,
        "files": files,
        "bytes_scanned": scanned,
        "matched": len(rows),
        "query_complete": not problems,
        "history_complete": False,
        "limits": "Two rotating files; no minimum time retention. Drops, crashes before write, power loss, earlier rotation, other directories/builds and uninstrumented paths may omit evidence. No match does not prove no event. Sequence orders one session; timestamps do not establish causality.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    read = commands.add_parser("query")
    read.add_argument("--directory", required=True, type=Path)
    read.add_argument("--since", required=True, type=instant)
    read.add_argument("--until", required=True, type=instant)
    for name in ["session", "operation", "event", "source-id", "component"]:
        read.add_argument("--" + name)
    read.add_argument("--limit", type=int, default=500)
    read.add_argument("--max-bytes", type=int, default=8 * 1024 * 1024)
    run = commands.add_parser("run")
    run.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    try:
        if args.action == "query":
            result = query(
                args.directory,
                args.since,
                args.until,
                session=args.session,
                operation=args.operation,
                event=args.event,
                source_id=args.source_id,
                component=args.component,
                limit=args.limit,
                max_bytes=args.max_bytes,
            )
            print(json.dumps(result, indent=2))
            return 0 if result["query_complete"] else 2
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            parser.error("run requires a command after --")
        return recorded_run(command).returncode
    except (OSError, ValueError) as error:
        parser.exit(2, f"Investigation failed: {type(error).__name__}: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())

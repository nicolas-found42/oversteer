import concurrent.futures
import fcntl
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import diagnostics
import verify


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "evidence"
        self.journal = diagnostics.Journal(self.directory)

    def query(self, **kwargs):
        return diagnostics.query(self.directory, 0, 9999999999999, **kwargs)

    def test_redaction_rotation_rate_and_restart(self):
        with patch.object(diagnostics, "FILE_BYTES", 1000):
            for _ in range(10):
                self.journal.emit("sample", password="SECRET", label="path/private", attempt=1)
        rows = self.query()
        self.assertTrue(rows["query_complete"])
        self.assertEqual(len(rows["files"]), 2)
        self.assertNotIn("SECRET", json.dumps(rows))
        self.assertNotIn("path/private", json.dumps(rows))
        self.assertLessEqual(sum(p.stat().st_size for p in self.directory.glob("*.jsonl")), 2000)
        for _ in range(80):
            self.journal.emit("burst")
        dropped = self.journal.dropped
        self.assertGreater(dropped, 0)
        self.journal.window -= 2
        self.journal.emit("resumed")
        self.assertEqual(self.query(event="resumed")["records"][0]["dropped_before"], dropped)
        restarted = diagnostics.Journal(self.directory)
        restarted.emit("restart")
        self.assertNotEqual(restarted.session, self.journal.session)
        self.assertEqual(self.query(session=restarted.session)["matched"], 1)

    def test_corrupt_missing_oversized_and_query_bounds_are_explicit(self):
        self.assertFalse(self.query()["query_complete"])
        self.journal.emit("sample")
        self.assertEqual(self.query(event="absent")["matched"], 0)
        self.assertFalse(self.query()["history_complete"])
        with (self.directory / "journal.jsonl").open("ab") as output:
            output.write(b"{bad}\n" + b"x" * 3000 + b"\n")
        problems = self.query()["problems"]
        self.assertEqual(
            [p["error"] for p in problems], ["invalid_record", "oversized_or_partial_record"]
        )
        self.assertFalse(self.query(max_bytes=16)["query_complete"])
        with self.assertRaises(ValueError):
            diagnostics.instant("2026-11-04T12:00:00")
        self.assertEqual(
            diagnostics.instant("2026-11-04T07:00:00-05:00"),
            diagnostics.instant("2026-11-04T12:00:00Z"),
        )

    def test_json_with_invalid_event_envelope_is_not_successful_evidence(self):
        self.journal.emit("valid")
        path = self.directory / "journal.jsonl"
        row = json.loads(path.read_text())
        for change in [{"schema": True}, {"event": None}, {"sequence": -1}]:
            path.write_text(json.dumps({**row, **change}) + "\n")
            result = self.query()
            self.assertFalse(result["query_complete"])
            self.assertEqual(result["problems"][0]["error"], "invalid_record")

    def test_contention_and_io_failure_do_not_change_application_result(self):
        self.journal.emit("first")
        with (self.directory / "journal.lock").open("rb") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.journal.emit("dropped")
            self.assertEqual(self.journal.dropped, 1)
            self.assertFalse(self.query()["query_complete"])
        self.journal.directory = self.directory / "journal.jsonl"
        with patch.object(diagnostics, "JOURNAL", self.journal):
            result = diagnostics.recorded_run([sys.executable, "-c", "pass"], check=True)
        self.assertEqual(result.returncode, 0)

    def test_broken_warning_sink_does_not_escape_telemetry(self):
        self.directory.write_text("not a directory")
        with patch.object(sys.stderr, "write", side_effect=OSError("closed pipe")):
            self.journal.emit("unavailable")
        self.assertEqual(self.journal.dropped, 1)

    def test_parallel_operations_have_unique_links_and_retained_failures(self):
        with patch.object(diagnostics, "JOURNAL", self.journal):
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                results = list(
                    executor.map(
                        lambda _: diagnostics.recorded_run(
                            [sys.executable, "-c", "raise SystemExit(7)"], check=False
                        ),
                        range(4),
                    )
                )
        self.assertEqual([r.returncode for r in results], [7] * 4)
        rows = self.query()["records"]
        operations = {r["operation"] for r in rows}
        self.assertEqual(len(operations), 4)
        for operation in operations:
            records = self.query(operation=operation)["records"]
            self.assertEqual([r["event"] for r in records], ["process.start", "process.end"])
            self.assertEqual(records[-1]["exit_code"], 7)
        self.assertFalse(self.query(limit=1)["query_complete"])

    def test_actual_child_exit_and_timeout_can_be_queried_from_new_process(self):
        with patch.object(diagnostics, "JOURNAL", self.journal):
            with self.assertRaises(subprocess.TimeoutExpired):
                diagnostics.recorded_run(
                    [sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.05
                )
        output = subprocess.check_output(
            [
                sys.executable,
                str(Path(diagnostics.__file__)),
                "query",
                "--directory",
                str(self.directory),
                "--since",
                "2020-01-01T00:00:00Z",
                "--until",
                "2100-01-01T00:00:00Z",
            ],
            text=True,
        )
        records = json.loads(output)["records"]
        self.assertEqual(records[-1]["category"], "TimeoutExpired")
        self.assertLess(records[-1]["duration_ms"], 5000)

    def test_child_parent_operation_is_propagated_without_secret_capture(self):
        with patch.object(diagnostics, "JOURNAL", self.journal):
            result = diagnostics.recorded_run(
                [
                    sys.executable,
                    "-c",
                    "import os; print(os.environ['OVERSTEER_PARENT_OPERATION'])",
                ],
                capture_output=True,
                text=True,
                env={**os.environ, "PRIVATE_TOKEN": "SECRET"},
            )
        rows = self.query()["records"]
        self.assertEqual(result.stdout.strip(), rows[0]["operation"])
        self.assertNotIn("SECRET", json.dumps(rows))


class VerificationTimeoutTests(unittest.TestCase):
    def test_timeout_retains_case_failure_and_actual_image_count(self):
        with tempfile.TemporaryDirectory() as temp:
            with (
                patch.object(verify, "native_command", return_value=["fixture"]),
                patch.object(verify.subprocess, "Popen") as launch,
            ):
                process = launch.return_value.__enter__.return_value
                process.wait.side_effect = [subprocess.TimeoutExpired("fixture", 900), None]
                process.returncode = -9
                result = verify.run_case(
                    {"id": "timeout", "scenario": "reload", "frames": 1},
                    Path(temp),
                    None,
                    background=False,
                )
            retained = json.loads((Path(temp) / "timeout/timeout.json").read_text())
            self.assertEqual(result, retained)
            self.assertEqual(result["category"], "timeout")
            self.assertEqual(result["screenshots_generated"], 0)
            self.assertEqual(result["status"], "failed")
            process.kill.assert_called_once()
            verify.write_gallery(
                Path(temp), {"cases": [result], "suite": "fixture", "binary_sha256": "fixture"}
            )
            gallery = (Path(temp) / "index.html").read_text()
            self.assertIn("timeout/timeout.json", gallery)
            self.assertIn("timeout/runtime.log", gallery)
            self.assertNotIn("final.png", gallery)


if __name__ == "__main__":
    unittest.main()

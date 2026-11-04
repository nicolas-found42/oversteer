"""Focus protection must fail before launching a rendered game if unavailable."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import background_window


class BackgroundWindowTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        self.source = root / "guard.m"
        self.library = root / "guard.dylib"
        self.source.write_text("test source")
        self.library.write_bytes(b"test library")
        os.utime(self.source, (1, 1))
        os.utime(self.library, (2, 2))
        self.addCleanup(patch.stopall)
        patch.object(background_window, "SOURCE", self.source).start()
        patch.object(background_window, "LIBRARY", self.library).start()

    def test_ignored_guard_cancels_launch_even_when_engine_exits_successfully(self):
        probe = subprocess.CompletedProcess([], 0, stdout="4.7.2", stderr="")
        with patch.object(background_window.subprocess, "run", return_value=probe) as run:
            with self.assertRaisesRegex(RuntimeError, "launch cancelled"):
                background_window.environment(Path("/test/Godot"))
        self.assertEqual(run.call_args.args[0], ["/test/Godot", "--headless", "--version"])

    def test_failed_guard_never_falls_back_to_an_unguarded_run(self):
        probe = subprocess.CompletedProcess([], 78, stderr="unsupported application")
        with patch.object(background_window.subprocess, "run", return_value=probe) as run:
            with self.assertRaisesRegex(RuntimeError, "launch cancelled"):
                background_window.environment(Path("/test/Godot"))
        self.assertEqual(run.call_count, 1)

    def test_verified_guard_is_scoped_to_the_child_environment(self):
        before = dict(os.environ)
        probe = subprocess.CompletedProcess([], 0, stderr=background_window.MARKER)
        with patch.object(background_window.subprocess, "run", return_value=probe):
            environment = background_window.environment(Path("/test/Godot"))
        self.assertEqual(environment["DYLD_INSERT_LIBRARIES"], str(self.library))
        self.assertEqual(dict(os.environ), before)


if __name__ == "__main__":
    unittest.main()

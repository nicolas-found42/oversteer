"""Tooling boundaries: source checks must not execute recovery or replace live libraries."""

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build
import dev


class DeveloperToolsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="oversteer tools ")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_syntax_validation_does_not_execute_recovery_script(self):
        source = self.root / "worker.py"
        sentinel = self.root / "published.txt"
        source.write_text(
            f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('unsafe')\n"
        )
        with patch.object(dev, "python_sources", return_value=[source]):
            dev.check_syntax(self.root)
        self.assertFalse(sentinel.exists())

    def test_syntax_validation_rejects_invalid_code(self):
        source = self.root / "broken.py"
        source.write_text("def invalid(:\n")
        with patch.object(dev, "python_sources", return_value=[source]):
            with self.assertRaises(SyntaxError):
                dev.check_syntax(self.root)

    def test_reference_suite_missing_inputs_fails_before_cargo(self):
        with patch.object(dev, "ROOT", self.root), patch.object(dev, "run") as launch:
            with self.assertRaisesRegex(RuntimeError, "Reference test fixtures missing"):
                dev.reference_tests()
        launch.assert_not_called()

    def library(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def test_dev_build_keeps_release_library_and_skips_import(self):
        self.library("build/rust/aarch64-apple-darwin/debug/liboversteer_godot.dylib", b"dev")
        release = self.library("godot/bin/release/liboversteer_godot.dylib", b"release")
        with (
            patch.object(build, "ROOT", self.root),
            patch.object(build, "require_unloaded_library"),
            patch.object(build, "run") as cargo,
            patch.object(build, "import_assets") as imports,
        ):
            build.build(profile="dev", skip_import=True)
        self.assertEqual(
            (self.root / "godot/bin/debug/liboversteer_godot.dylib").read_bytes(), b"dev"
        )
        self.assertEqual(release.read_bytes(), b"release")
        self.assertIn("--locked", cargo.call_args.args[0])
        self.assertNotIn("--release", cargo.call_args.args[0])
        imports.assert_not_called()

    def test_loaded_extension_is_rejected_before_compilation(self):
        target = self.library("godot/bin/debug/liboversteer_godot.dylib", b"loaded")
        busy = subprocess.CompletedProcess([], 0, stdout="42\n", stderr="")
        with (
            patch.object(build, "ROOT", self.root),
            patch.object(build.subprocess, "run", return_value=busy),
            patch.object(build, "run") as cargo,
        ):
            with self.assertRaisesRegex(RuntimeError, "Close the Godot process"):
                build.build(profile="dev", skip_import=True)
        cargo.assert_not_called()
        self.assertEqual(target.read_bytes(), b"loaded")

    def test_extension_opened_during_compilation_is_not_overwritten(self):
        target = self.library("godot/bin/debug/liboversteer_godot.dylib", b"loaded")
        with (
            patch.object(build, "ROOT", self.root),
            patch.object(build, "run"),
            patch.object(
                build, "require_unloaded_library", side_effect=[None, RuntimeError("busy")]
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "busy"):
                build.build(profile="dev", skip_import=True)
        self.assertEqual(target.read_bytes(), b"loaded")

    def test_missing_runtime_inputs_have_actionable_error(self):
        with (
            patch.object(build.platform, "system", return_value="Darwin"),
            patch.object(build.platform, "machine", return_value="arm64"),
            patch.object(build, "GODOT", self.root / "missing-godot"),
        ):
            with self.assertRaisesRegex(RuntimeError, "bootstrap.py"):
                build.require_runtime_inputs()


if __name__ == "__main__":
    unittest.main()

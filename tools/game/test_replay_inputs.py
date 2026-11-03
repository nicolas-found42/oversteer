"""Replay lineage and host input guards, without launching the renderer."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import replay_inputs
import verify


class ReplayIdentityTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.seed = self.root / "seed.json"
        self.seed.write_text('{"career":{"cash":25000}}\n')
        self.controls = self.root / "controls.json"
        self.controls.write_text(json.dumps([{
            "tick": 0, "active_tick": 0, "countdown_before": 0,
            "input": {
                "steering": 0, "throttle": 0.5, "brake": 0,
                "handbrake": 0, "nitrous": 0, "reverse": False, "shift": 0,
            },
            "raw_axes": {"steering_0": 0, "throttle_5": 0.5, "brake_4": 0},
        }]))
        self.evidence = self.root / "evidence.json"
        self.write_evidence()
        self.output = self.root / "events.json"
        self.root_patch = patch.object(replay_inputs, "ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)

    def write_evidence(self):
        self.evidence.write_text(json.dumps({
            "content_sha256": "a" * 64,
            "files": {
                key: {"path": str(path), "sha256": replay_inputs.digest(path)}
                for key, path in [("initial-save", self.seed), ("controls", self.controls)]
            },
            "tick_count": 1, "first_active_tick": 0, "active_ticks": 1,
            "raw_handbrake_button": 2, "event_id": "event", "car_id": "car",
            "result": {},
        }))

    def case(self):
        return {
            "id": "identity", "scenario": "reload", "seed_save": self.seed,
            "input_events": self.output,
            "replay_manifest": self.output.with_suffix(".manifest.json"),
        }

    def run_to_launch(self):
        with patch.object(verify, "native_command", return_value=["unused"]), patch.object(
            verify.subprocess, "run", side_effect=RuntimeError("native-launch-boundary")
        ) as launch:
            try:
                verify.run_case(self.case(), self.root / "verification", None)
            except ValueError:
                launch.assert_not_called()
                raise

    def test_unchanged_record_reaches_launch_boundary(self):
        manifest = replay_inputs.convert(self.evidence, self.output)
        self.assertEqual(manifest["initial_save_sha256"], replay_inputs.digest(self.seed))
        with self.assertRaisesRegex(RuntimeError, "native-launch-boundary"):
            self.run_to_launch()

    def test_seed_changed_after_conversion_is_rejected_before_launch(self):
        replay_inputs.convert(self.evidence, self.output)
        self.seed.write_text('{"career":{"cash":1}}\n')
        with self.assertRaisesRegex(ValueError, "initial save changed"):
            self.run_to_launch()

    def test_evidence_changed_after_conversion_is_rejected_before_launch(self):
        replay_inputs.convert(self.evidence, self.output)
        self.evidence.write_text(self.evidence.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            self.run_to_launch()

    def test_wrong_signed_zero_control_is_rejected_by_converter(self):
        controls = json.loads(self.controls.read_text())
        controls[0]["input"]["steering"] = -0.0
        self.controls.write_text(json.dumps(controls))
        self.write_evidence()
        with self.assertRaisesRegex(ValueError, "f32 controls at tick 0"):
            replay_inputs.convert(self.evidence, self.output)
        self.assertFalse(self.output.exists())

    def test_recorded_nitrous_press_and_release_use_actual_default_button(self):
        controls = json.loads(self.controls.read_text())
        controls[0]["input"]["nitrous"] = 1
        second = json.loads(json.dumps(controls[0]))
        second.update(tick=1, active_tick=1)
        second["input"]["nitrous"] = 0
        self.controls.write_text(json.dumps(controls + [second]))
        self.write_evidence()
        evidence = json.loads(self.evidence.read_text())
        evidence.update(raw_nitrous_button=0, tick_count=2, active_ticks=2)
        self.evidence.write_text(json.dumps(evidence))
        replay_inputs.convert(self.evidence, self.output)
        events = json.loads(self.output.read_text())
        self.assertEqual([event for event in events if event.get("joy_button") == 0], [
            {"frame": 0, "joy_button": 0, "pressed": True},
            {"frame": 1, "joy_button": 0, "pressed": False},
        ])

    def test_nitrous_requires_explicit_recorded_binding(self):
        controls = json.loads(self.controls.read_text())
        controls[0]["input"]["nitrous"] = 1
        self.controls.write_text(json.dumps(controls))
        self.write_evidence()
        with self.assertRaisesRegex(ValueError, "explicit recorded raw_nitrous_button"):
            replay_inputs.convert(self.evidence, self.output)
        self.assertFalse(self.output.exists())

    def test_wrong_nitrous_button_is_rejected(self):
        evidence = json.loads(self.evidence.read_text())
        evidence["raw_nitrous_button"] = 3
        self.evidence.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, "supported default binding 0"):
            replay_inputs.convert(self.evidence, self.output)
        self.assertFalse(self.output.exists())

    def test_negative_zero_digital_controls_are_not_reachable(self):
        for field in ["handbrake", "nitrous"]:
            with self.subTest(field=field):
                controls = json.loads(self.controls.read_text())
                controls[0]["input"]["handbrake"] = 0
                controls[0]["input"]["nitrous"] = 0
                controls[0]["input"][field] = -0.0
                self.controls.write_text(json.dumps(controls))
                self.write_evidence()
                with self.assertRaisesRegex(ValueError, f"{field} is not reachable"):
                    replay_inputs.convert(self.evidence, self.output)
                self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()

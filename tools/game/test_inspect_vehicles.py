import json
import struct
import unittest

from inspect_vehicles import CARS, capture_contract_checks, material_import_check, screenshot_budget
from metal_capture import capture_boundary, presented_layer


class CaptureBudgetTests(unittest.TestCase):
    def test_standard_and_smoke_fit_whole_run_ceiling(self):
        self.assertEqual(screenshot_budget(CARS), 42)
        self.assertEqual(screenshot_budget(CARS, smoke=True), 18)

    def test_rejects_more_than_fifty_before_launch(self):
        with self.assertRaisesRegex(ValueError, "maximum is 50"):
            screenshot_budget([f"car-{i}" for i in range(5)])

    def test_rejects_repeated_car_output(self):
        with self.assertRaisesRegex(ValueError, "only once"):
            screenshot_budget([CARS[0], CARS[0]])

    def test_gpu_capture_requires_one_presented_godot_layer(self):
        listing = (
            "  1 Device Apple M5 Pro 1.5 1500\n  2 Layer CAMetalLayer: GodotContentView 8.3 632\n"
        )
        self.assertEqual(presented_layer(listing), "2")
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            presented_layer(" 1 Device Apple M5 Pro 1.5 1500\n")
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            presented_layer(listing + " 3 Layer CAMetalLayer: GodotContentView 8.3 10\n")

    def test_covered_window_queue_capture_is_not_claimed_as_presented_frame(self):
        listing = (
            " 6 Queue Godot Main Command Queue 1.7 1331\n 7 Queue Copy Command Queue 0.02 169\n"
        )
        boundary, scope = capture_boundary(listing, False)
        self.assertEqual(boundary, "6")
        self.assertIn("not a presented frame", scope)
        with self.assertRaisesRegex(RuntimeError, "exactly one"):
            capture_boundary(" 7 Queue Copy Command Queue 0.02 169\n", False)


class CaptureContractTests(unittest.TestCase):
    def test_capture_duration_must_match_both_journal_boundaries(self):
        captures = [{"id": "view-0", "capture_ms": 20, "capture_started_wall_ms": 100}]
        events = [
            {"event": "capture_begin", "wall_ms": 100, "details": {"index": 0}},
            {
                "event": "capture_complete",
                "wall_ms": 120,
                "details": {"id": "view-0", "capture_ms": 20},
            },
        ]
        self.assertTrue(all(capture_contract_checks(captures, events, smoke=True).values()))
        captures[0]["capture_ms"] = 19
        self.assertFalse(all(capture_contract_checks(captures, events, smoke=True).values()))
        self.assertFalse(all(capture_contract_checks(captures, events[:1], smoke=True).values()))

    def test_repeated_rear_views_cannot_claim_full_axis_coverage(self):
        shots = [
            {"azimuth": az, "elevation": 5, "roll": 0, "light": "neutral", "isolated": True}
            for az in range(0, 360, 45)
        ]
        shots.extend(
            {"azimuth": az, "elevation": 10, "roll": 0, "light": "race", "isolated": False}
            for az in (45, 135, 225, 315)
        )
        shots.extend(
            [
                {"azimuth": 45, "elevation": 75, "roll": -20, "light": "grazing", "isolated": True},
                {
                    "azimuth": 225,
                    "elevation": -25,
                    "roll": 20,
                    "light": "backlight",
                    "isolated": True,
                },
            ]
        )
        captures = [{"id": str(i), "shot": shot} for i, shot in enumerate(shots)]
        checks = capture_contract_checks(captures, [])
        self.assertTrue(
            all(value for key, value in checks.items() if key != "capture_timing_matches_event_log")
        )
        shots[4]["azimuth"] = 0
        self.assertFalse(capture_contract_checks(captures, [])["all_isolated_azimuths"])


class ImportedMaterialTests(unittest.TestCase):
    def source(self):
        document = json.dumps(
            {
                "materials": [
                    {
                        "name": "window",
                        "alphaMode": "BLEND",
                        "pbrMetallicRoughness": {"baseColorFactor": [0.012, 0.018, 0.025, 0.98]},
                    }
                ]
            }
        ).encode()
        document += b" " * (-len(document) % 4)
        return (
            struct.pack("<4sIIII", b"glTF", 2, 20 + len(document), len(document), 0x4E4F534A)
            + document
        )

    def runtime(self, alpha, mode):
        return [
            {
                "base_name": "window",
                "factory_state": {"rgba": [0.112, 0.143, 0.171, alpha], "transparency": mode},
            }
        ]

    def test_rejects_stale_import_even_when_source_asset_is_restored(self):
        result = material_import_check(self.source(), self.runtime(0.3, 4))
        self.assertFalse(result["passed"])
        self.assertEqual(result["mismatches"][0]["source_alpha"], 0.98)

    def test_accepts_godot_depth_prepass_translation_and_float_rounding(self):
        self.assertTrue(
            material_import_check(self.source(), self.runtime(0.980000019, 4))["passed"]
        )
        self.assertFalse(material_import_check(self.source(), self.runtime(0.98, 0))["passed"])

    def test_missing_runtime_observations_cannot_pass(self):
        self.assertFalse(material_import_check(self.source(), [])["passed"])

    def test_rejects_reflected_wheel_and_disabled_culling(self):
        rows = self.runtime(0.98, 4)
        rows[0].update(wheel=True, runtime_standard_state={"cull_mode": 0})
        wheels = [{"node": "wheel_front_left", "basis": [[-1, 0, 0], [0, 1, 0], [0, 0, 1]]}]
        self.assertFalse(material_import_check(self.source(), rows, wheels)["passed"])
        wheels[0]["basis"][0][0] = 1
        self.assertTrue(material_import_check(self.source(), rows, wheels)["passed"])
        rows[0]["runtime_standard_state"]["cull_mode"] = 2
        self.assertFalse(material_import_check(self.source(), rows, wheels)["passed"])

    def test_gloss_checks_the_effective_shader_finish(self):
        rows = self.runtime(0.98, 4)
        rows[0].update(
            paint_target=True,
            runtime_render_state={"paint_roughness": 0.7, "paint_clearcoat": True},
        )
        self.assertFalse(material_import_check(self.source(), rows)["passed"])
        rows[0]["runtime_render_state"]["paint_roughness"] = 0.19
        self.assertTrue(material_import_check(self.source(), rows)["passed"])

    def test_zero_alpha_tire_fails_even_when_it_matches_the_source(self):
        raw = self.source()
        size = struct.unpack_from("<I", raw, 12)[0]
        doc = json.loads(raw[20 : 20 + size])
        doc["materials"][0].update(name="tire_front", alphaMode="OPAQUE")
        doc["materials"][0]["pbrMetallicRoughness"]["baseColorFactor"][3] = 0
        data = json.dumps(doc).encode()
        data += b" " * (-len(data) % 4)
        raw = struct.pack("<4sIIII", b"glTF", 2, 20 + len(data), len(data), 0x4E4F534A) + data
        rows = self.runtime(0, 0)
        rows[0].update(
            base_name="tire_front",
            wheel=True,
            runtime_standard_state={"cull_mode": 0},
            runtime_standard_rgba=[1, 1, 1, 0],
        )
        result = material_import_check(raw, rows)
        self.assertEqual(
            result["mismatches"],
            [{"material": "tire_front", "error": "Opaque/masked tire has zero alpha"}],
        )

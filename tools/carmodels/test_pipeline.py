"""Small fixtures for source integrity, scene transforms and family isolation."""

import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from PIL import Image

from tools.carmodels import sprite_judgments
from tools.carmodels.assets import decode_scene, verify_asset
from tools.carmodels.policy import import_policy
from tools.carmodels.research import build_profile, check_source, enforce_curve_minimums, tyre_sizes
from tools.carmodels.sampling import mip_chain, resample
from tools.carmodels.scope import included_identities, is_included
from tools.carmodels.sprite_experiments import squeezed
from tools.carmodels.sprites import excluded_material, selected_scene
from tools.carmodels.validation import family_fold


class SourceTests(unittest.TestCase):
    def test_production_mips_keep_coverage_without_transparent_color_fringes(self):
        image = Image.new("RGBA", (512, 512), (0, 0, 255, 0))
        image.paste((255, 0, 0, 255), (0, 0, 256, 512))
        levels = list(mip_chain(image))
        self.assertEqual([im.width for im in levels], [256, 128, 64, 32, 16, 8, 4, 2, 1])
        self.assertEqual(levels[-1].getpixel((0, 0)), (255, 0, 0, 128))
        image.paste((0, 0, 0, 255), (256, 0, 512, 512))
        image.paste((255, 255, 255, 255), (0, 0, 256, 512))
        self.assertEqual(list(mip_chain(image))[-1].getpixel((0, 0)), (188, 188, 188, 255))

    def test_sprite_policy_requires_intake_resolution_and_complete_refinement(self):
        data = sprite_judgments.ROOT / "data/carmodels"
        source = json.loads((data / "sprite-judgments.json").read_text())
        refinement = json.loads((data / "sprite-refinement.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "data/carmodels"
            target.mkdir(parents=True)
            (target / "sprite-judgments.json").write_text(json.dumps(source))
            (target / "sprite-refinement.json").write_text(json.dumps(refinement))
            with (
                patch.object(sprite_judgments, "ROOT", root),
                patch.object(sprite_judgments, "DIRECTORY", root / "sprites"),
            ):
                policy = sprite_judgments.import_sprite_policy()
                self.assertEqual(policy["material_mode"], "ao_untextured")
                self.assertEqual(policy["render_pixels"], 512)
                source["intake"]["sprite-source-model-load-mjs"].pop("request_hash")
                (target / "sprite-judgments.json").write_text(json.dumps(source))
                with self.assertRaisesRegex(ValueError, "Unresolved sprite source intake"):
                    sprite_judgments.import_sprite_policy()
                source = json.loads((data / "sprite-judgments.json").read_text())
                (target / "sprite-judgments.json").write_text(json.dumps(source))
                for row in refinement["results"]:
                    if row["id"] == "sprite-refinement-claims":
                        row["result"]["results"] = []
                (target / "sprite-refinement.json").write_text(json.dumps(refinement))
                with self.assertRaisesRegex(ValueError, "Unsupported refinement result"):
                    sprite_judgments.import_sprite_policy()

    def test_premultiplied_sampling_rejects_hidden_transparent_color(self):
        image = Image.fromarray(
            np.array(
                [[[255, 0, 0, 255], [0, 0, 255, 0]], [[255, 0, 0, 255], [0, 0, 255, 0]]],
                dtype=np.uint8,
            )
        )
        correct = resample(image, 1, "box", "linear", "premultiplied")
        wrong = resample(image, 1, "box", "linear", "straight")
        self.assertEqual(correct.getpixel((0, 0)), (255, 0, 0, 128))
        self.assertGreater(wrong.getpixel((0, 0))[2], 100)

    def test_linear_sampling_preserves_average_light(self):
        image = Image.fromarray(
            np.array(
                [[[255, 255, 255, 255], [0, 0, 0, 255]], [[255, 255, 255, 255], [0, 0, 0, 255]]],
                dtype=np.uint8,
            )
        )
        linear = resample(image, 1, "box", "linear", "premultiplied")
        srgb = resample(image, 1, "box", "srgb", "premultiplied")
        self.assertEqual(linear.getpixel((0, 0)), (188, 188, 188, 255))
        self.assertEqual(srgb.getpixel((0, 0)), (128, 128, 128, 255))

    def test_proportion_negative_control_changes_geometry_not_only_sampling(self):
        image = Image.new("RGBA", (160, 160))
        image.paste((255, 0, 0, 255), (30, 10, 130, 150))
        result = squeezed(image)
        self.assertEqual(result.size, image.size)
        before, after = image.getbbox(), result.getbbox()
        self.assertLess(after[2] - after[0], (before[2] - before[0]) * 0.7)
        self.assertEqual(after[3] - after[1], before[3] - before[1])

    def test_ford_ground_shadow_namespace_is_not_bodywork(self):
        for name in ["UNDER_SHADOW", "EX_UNDER_SHADOW2", "GT90_UNDER_SHADOW"]:
            self.assertTrue(excluded_material(name, "ford-racing-2"))
        self.assertFalse(excluded_material("EX_UNDER_SHADOW2", "gran-turismo-4"))

    def test_blender_input_removes_orphans_and_remaps_the_selected_scene(self):
        document = {
            "scene": 1,
            "scenes": [{"nodes": [0]}, {"nodes": [2]}],
            "nodes": [{"name": "other_lod"}, {"name": "wheel"}, {"children": [1]}],
            "meshes": [],
        }
        encoded = json.dumps(document).encode()
        encoded += b" " * (-len(encoded) % 4)
        data = (
            struct.pack("<4sIIII", b"glTF", 2, 20 + len(encoded), len(encoded), 0x4E4F534A)
            + encoded
        )
        result = selected_scene(data, "ford-racing-2")
        size = struct.unpack_from("<I", result, 12)[0]
        actual = json.loads(result[20 : 20 + size])
        self.assertEqual(len(actual["nodes"]), 2)
        self.assertEqual(actual["scenes"], [{"nodes": [1]}])
        self.assertEqual(actual["nodes"][1]["children"], [0])

    def test_profile_entry_point_rejects_excluded_sources(self):
        with self.assertRaisesRegex(ValueError, "Excluded source"):
            build_profile(
                {"code": "REDLINE_TEST", "game": "redline", "scope": "included"}, {}, {}, {}, {}
            )

    def test_estimated_curve_respects_reported_minimum_power_and_torque(self):
        rpm = np.linspace(900, 8400, 7)
        initial = np.full(7, 220.0)
        fitted = enforce_curve_minimums(
            rpm, initial, {"powerKw": {"lower": 588}, "torqueNm": {"lower": 784}}
        )
        samples = np.linspace(rpm[0], rpm[-1], 1001)
        power = np.max(np.interp(samples, rpm, fitted) * samples * 2 * np.pi / 60 / 1000)
        self.assertGreater(power, 588)
        self.assertGreater(max(fitted), 784)
        np.testing.assert_array_equal(initial, np.full(7, 220.0))

    def test_excluded_games_cannot_reenter_through_a_stale_included_flag(self):
        for game in ["redline", "gran-turismo"]:
            identity = {"code": "car", "game": game, "scope": "included"}
            self.assertFalse(is_included(identity))

    def test_ambient_versions_are_excluded_while_player_versions_remain(self):
        ambient = {
            "code": "MCLA_VA_350Z_04",
            "game": "midnight-club-los-angeles",
            "scope": "included",
            "source_code": "va_350z_04",
        }
        player = {**ambient, "code": "MCLA_VP_NSN_350Z_06", "source_code": "vp_nsn_350z_06"}
        dlc = {**ambient, "code": "MCLA_VPD_AM_DB9_08", "source_code": "vpd_am_db9_08"}
        self.assertEqual(included_identities([ambient, player, dlc]), [player, dlc])

    def test_native_traffic_role_overrides_a_player_like_filename(self):
        identity = {
            "code": "MC3_VP_TEST",
            "game": "midnight-club-3-remix",
            "source_code": "vp_test",
            "scope": "included",
            "native_ambient_traffic": True,
        }
        self.assertFalse(is_included(identity))

    def test_police_name_is_not_a_traffic_role(self):
        identity = {
            "code": "MCLA_VP_CHV_POLICE_96",
            "game": "midnight-club-los-angeles",
            "source_code": "vp_chv_police_96",
            "scope": "included",
        }
        self.assertTrue(is_included(identity))

    def test_content_hash_is_required_even_when_size_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "car.glb"
            path.write_bytes(b"bad")
            with self.assertRaises(ValueError):
                verify_asset(path, {"bytes": 3, "sha256": hashlib.sha256(b"car").hexdigest()})

    def test_only_default_scene_is_used_and_parent_transforms_compose(self):
        vertices = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 0, 1)
        document = {
            "asset": {"version": "2.0"},
            "scene": 1,
            "scenes": [{"nodes": [0]}, {"nodes": [1]}],
            "nodes": [
                {"mesh": 0, "translation": [100, 0, 0]},
                {"translation": [2, 0, 0], "children": [2]},
                {"mesh": 0, "translation": [0, 3, 0]},
            ],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
            "buffers": [{"byteLength": len(vertices)}],
            "bufferViews": [{"buffer": 0, "byteLength": len(vertices)}],
            "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3"}],
        }
        header = json.dumps(document).encode()
        header += b" " * (-len(header) % 4)
        data = (
            struct.pack("<4sII", b"glTF", 2, 28 + len(header) + len(vertices))
            + struct.pack("<I4s", len(header), b"JSON")
            + header
            + struct.pack("<I4s", len(vertices), b"BIN\x00")
            + vertices
        )
        parts = decode_scene(data)
        self.assertEqual(len(parts), 1)
        np.testing.assert_allclose(parts[0]["positions"], [[2, 3, 0], [3, 3, 0], [2, 3, 1]])

    def test_cross_game_family_cannot_leak_between_folds(self):
        self.assertEqual(family_fold("ford/mustang-1999"), family_fold("ford/mustang-1999"))
        folds = {family_fold("family-" + str(i)) for i in range(100)}
        self.assertEqual(folds, {0, 1, 2, 3, 4})

    def test_impossible_units_are_rejected_without_guessing_a_conversion(self):
        source = {
            "values": {"lengthMm": 4300, "widthMm": 1800, "wheelbaseMm": 62000},
            "derived": {"frontTrackMm": 61},
        }
        result = check_source(source)
        self.assertIsNone(result["values"]["wheelbaseMm"])
        self.assertIsNone(result["derived"]["frontTrackMm"])
        self.assertEqual(source["values"]["wheelbaseMm"], 62000)
        self.assertEqual(len(result["rejected_values"]), 2)

    def test_axle_track_cannot_be_copied_from_an_inches_value(self):
        source = {"values": {"widthMm": 1780}, "derived": {"rearTrackMm": 58.7}}
        self.assertIsNone(check_source(source)["derived"]["rearTrackMm"])

    def test_documented_source_schema_aliases_reach_physics_anchors(self):
        source = {
            "values": {"curbMassKg": 1742, "powerKw": 223, "driveLayout": "RWD"},
            "derived": {},
        }
        normalized = check_source(source)
        self.assertEqual(normalized["values"]["curbWeightKg"], 1742)
        self.assertEqual(normalized["values"]["drivetrain"], "RWD")
        self.assertEqual(normalized["derived"]["powerKw"], 223)
        self.assertEqual(source["derived"], {})

    def test_staggered_tire_units_preserve_axle_order(self):
        self.assertEqual(
            tyre_sizes("P275/35 ZR18 front; P345/30 ZR19 rear"), [(275, 35, 18), (345, 30, 19)]
        )

    def test_missing_or_invalid_judgments_cannot_become_training_permission(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "judgments.json"
            path.write_text("[]")
            with self.assertRaisesRegex(ValueError, "incomplete"):
                import_policy(path)


if __name__ == "__main__":
    unittest.main()

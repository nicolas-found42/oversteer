"""Fixtures for native donor integrity, scene transforms, and source scope."""

import hashlib
import json
import struct
import tempfile
import unittest
from pathlib import Path

import numpy as np

from tools.carmodels.assets import decode_scene, verify_asset
from tools.carmodels.scope import included_identities, is_included


class SourceTests(unittest.TestCase):
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

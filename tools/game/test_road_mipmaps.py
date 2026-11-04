import json
import tempfile
import unittest
from pathlib import Path

from build import configure_road_mipmaps


class RoadMipmapTests(unittest.TestCase):
    def test_shader_bound_markings_and_paving_get_mips_without_touching_other_art(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            world = root / "godot/assets/worlds"
            world.mkdir(parents=True)
            (world / "render-contract.json").write_text(
                json.dumps(
                    {
                        "catalogs": {
                            "london": {
                                "tarmac": [
                                    {
                                        "base_texture_path": "res://assets/worlds/base.png",
                                        "markings_texture_path": "res://assets/worlds/marks.png",
                                    }
                                ]
                            }
                        }
                    }
                )
            )
            for name in ["base", "marks", "other"]:
                (world / f"{name}.png.import").write_text("[params]\nmipmaps/generate=false\n")
            self.assertEqual(configure_road_mipmaps(root), 2)
            self.assertIn("mipmaps/generate=true", (world / "marks.png.import").read_text())
            self.assertIn("mipmaps/generate=false", (world / "other.png.import").read_text())
            self.assertEqual(configure_road_mipmaps(root), 0)

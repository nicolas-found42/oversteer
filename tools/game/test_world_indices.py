import unittest

from assets.world_indices import triangles


class WorldIndicesTests(unittest.TestCase):
    def test_disconnected_list_faces_do_not_gain_bridge_triangles(self):
        # London native_283_0, descriptor topology 1: two separate curb faces.
        source = [4, 5, 6, 7, 8, 9]
        self.assertEqual(triangles(source, 1), source)

    def test_strip_winding_and_restart_are_preserved(self):
        self.assertEqual(triangles([0, 1, 2, 3, 65535, 4, 5, 6], 0), [0, 1, 2, 2, 1, 3, 4, 5, 6])

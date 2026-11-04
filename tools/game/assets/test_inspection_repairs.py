import json
import struct
import unittest

import numpy as np

from bake_inspection_wheels import bake
from repair_london_sign_faces import repair
from tools.carmodels.assets import decode_scene, node_matrix


def fixture(texture=False):
    binary = bytearray()
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [{"scale": [2, 2, 2], "children": [1]},
                     {"name": "tire_front_left", "translation": [-1, 0.5, 0], "scale": [-1, 1, 1], "mesh": 0}],
           "meshes": [], "materials": [{"name": "tire", "doubleSided": True, "alphaMode": "OPAQUE",
                       "pbrMetallicRoughness": {"baseColorFactor": [0.2, 0.2, 0.2, 0]}}],
           "accessors": [], "bufferViews": []}

    def add(values, kind, component):
        values = np.array(values, dtype="<f4" if component == 5126 else "<u2")
        binary.extend(b"\0" * (-len(binary) % 4))
        doc["bufferViews"].append({"buffer": 0, "byteOffset": len(binary), "byteLength": values.nbytes})
        binary.extend(values.tobytes())
        doc["accessors"].append({"bufferView": len(doc["bufferViews"])-1, "count": len(values), "type": kind, "componentType": component})
        return len(doc["accessors"])-1

    attributes = {"POSITION": add([[0.1, -0.1, -0.1], [0.1, 0.1, -0.1], [0.1, 0, 0.1]], "VEC3", 5126),
                  "TEXCOORD_0": add([[0.50146484375, 0.572265625], [0.99658203125, 0.572265625], [0.50146484375, 0.876953125]], "VEC2", 5126)}
    if not texture:
        attributes["NORMAL"] = add([[-1, 0, 0]]*3, "VEC3", 5126)
    doc["meshes"] = [{"name": "wheel", "primitives": [{"attributes": attributes, "indices": add([0, 2, 1], "SCALAR", 5123), "material": 0}]}]
    if texture:
        doc["images"] = [{"uri": "textures/london/266.png"}]
        doc["textures"] = [{"source": 0}]
        doc["materials"][0]["pbrMetallicRoughness"]["baseColorTexture"] = {"index": 0}
    binary.extend(b"\0" * (-len(binary) % 4))
    doc["buffers"] = [{"byteLength": len(binary)}]
    header = json.dumps(doc).encode()
    header += b" " * (-len(header) % 4)
    return struct.pack("<4sII", b"glTF", 2, 28+len(header)+len(binary))+struct.pack("<II", len(header), 0x4E4F534A)+header+struct.pack("<II", len(binary), 0x004E4942)+binary


def document(raw):
    return json.loads(raw[20:20+struct.unpack_from("<I", raw, 12)[0]])


class InspectionRepairTests(unittest.TestCase):
    def test_mirrored_tire_keeps_geometry_with_orthonormal_socket_and_outward_faces(self):
        source = fixture()
        fixed, report = bake(source)
        before, after = decode_scene(source)[0], decode_scene(fixed)[0]
        np.testing.assert_allclose(before["positions"], after["positions"], atol=1e-6)
        np.testing.assert_array_equal(before["uv"], after["uv"])
        doc = document(fixed)
        np.testing.assert_array_equal(node_matrix(doc["nodes"][1])[:3, :3], np.eye(3))
        self.assertIn(1, doc["scenes"][0]["nodes"])
        self.assertFalse(doc["materials"][0]["doubleSided"])
        self.assertEqual(after["material"]["factor"][3], 1)
        tri = after["positions"][after["indices"][0]]
        self.assertLess(np.cross(tri[1]-tri[0], tri[2]-tri[0])[0], 0)
        self.assertLess(report[0]["source_determinant"], 0)
        self.assertEqual(bake(fixed)[0], fixed)

    def test_banner_adds_readable_back_without_changing_front_or_scene(self):
        source = fixture(texture=True)
        fixed, report = repair(source)
        a, b = document(source), document(fixed)
        self.assertEqual(a["nodes"], b["nodes"])
        front, back = b["meshes"][0]["primitives"]
        self.assertEqual(front["attributes"], a["meshes"][0]["primitives"][0]["attributes"])
        self.assertNotEqual(front["attributes"]["TEXCOORD_0"], back["attributes"]["TEXCOORD_0"])
        self.assertEqual(front["attributes"]["POSITION"], back["attributes"]["POSITION"])
        self.assertFalse(b["materials"][front["material"]]["doubleSided"])
        self.assertEqual(report[0]["triangles_per_side"], 1)
        self.assertEqual(repair(fixed)[0], fixed)

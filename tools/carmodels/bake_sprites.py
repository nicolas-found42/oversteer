"""Blender worker: orthographic sprites from selected, hash-verified GLB scenes.

Run with Blender, not the project's Python environment. The orchestrator supplies
the filtered source scene and a finite experiment list; no model service is called.
"""

import json
import math
import re
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def bounds(objects):
    corners = [obj.matrix_world @ Vector(v) for obj in objects for v in obj.bound_box]
    return Vector(tuple(min(v[i] for v in corners) for i in range(3))), Vector(
        tuple(max(v[i] for v in corners) for i in range(3))
    )


def front_wheels(scene, body_low, body_high, exclude_steering_control):
    """Use named source wheel assemblies, never draw replacement wheel shapes."""
    candidates = []
    centre_y = (body_low.y + body_high.y) / 2
    for obj in scene.objects:
        if exclude_steering_control and re.search(
            r"steer(?:ing)?[_ .-]*(?:whl|wheel)", obj.name, re.I
        ):
            continue
        if not re.search(r"wheel|tire|tyre|whl", obj.name, re.I):
            continue
        meshes = [x for x in [obj, *obj.children_recursive] if x.type == "MESH"]
        if not meshes:
            continue
        low, high = bounds(meshes)
        if (low.y + high.y) / 2 <= centre_y:
            continue
        if high.y - low.y > (body_high.y - body_low.y) * 0.3:
            continue  # A whole-body mesh is not a wheel carrier.
        candidates.append(obj)
    roots = []
    for obj in candidates:
        parent = obj.parent
        while parent is not None and parent not in candidates:
            parent = parent.parent
        if parent is None:
            roots.append(obj)
    groups = {}
    for obj in roots:
        meshes = [x for x in [obj, *obj.children_recursive] if x.type == "MESH"]
        low, high = bounds(meshes)
        origin = obj.matrix_world.translation.copy()
        # Some exports bake world positions into vertices instead of node translations.
        if not low.y - 0.02 <= origin.y <= high.y + 0.02:
            origin = (low + high) / 2
        side = (
            "centre"
            if abs(origin.x) < (body_high.x - body_low.x) * 0.1
            else ("left" if origin.x < 0 else "right")
        )
        groups.setdefault(side, []).append((obj, origin, obj.matrix_world.copy()))
    result = []
    for side, members in sorted(groups.items()):
        pivot = Vector(
            tuple(sorted(m[1][axis] for m in members)[len(members) // 2] for axis in range(3))
        )
        result.append((side, pivot, [(m[0], m[2]) for m in members]))
    return result


def steer_wheels(groups, degrees):
    angle = math.radians(degrees)
    for _, pivot, members in groups:
        transform = (
            Matrix.Translation(pivot) @ Matrix.Rotation(angle, 4, "Z") @ Matrix.Translation(-pivot)
        )
        for obj, original in members:
            obj.matrix_world = transform @ original
    bpy.context.view_layer.update()


def render_job(job):
    output = Path(job["output"])
    if output.exists() and output.with_suffix(".json").exists():
        saved = json.loads(output.with_suffix(".json").read_text())
        if saved["experiment"] == job and all(
            Path(p["path"]).exists() for p in saved.get("frames", [])
        ):
            print("CACHED", job["code"], job["material_mode"], flush=True)
            return
    started = time.perf_counter()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=job["model"], import_pack_images=True)
    scene = bpy.context.scene
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    if not meshes:
        raise ValueError("No selected-scene meshes: " + job["code"])
    # glTF +Y up maps to Blender +Z up; glTF +Z maps to Blender -Y.
    rotation = math.pi if job["forward_sign"] == 1 else 0
    if job["forward_axis"] == 0:
        rotation = math.pi / 2
    root = bpy.data.objects.new("sprite_orientation", None)
    scene.collection.objects.link(root)
    for obj in list(scene.objects):
        if obj != root and obj.parent is None:
            obj.parent = root
    root.rotation_euler.z = rotation
    bpy.context.view_layer.update()
    low, high = bounds(meshes)
    wheel_groups = front_wheels(scene, low, high, job.get("exclude_steering_control", False))
    centre = (low + high) / 2
    span = max(high.x - low.x, high.y - low.y)
    if span <= 0:
        raise ValueError("Degenerate source geometry")
    bpy.ops.object.camera_add(location=(centre.x, centre.y, high.z + span * 2))
    camera = bpy.context.object
    camera.name = "sprite_camera"
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = job.get(
        "ortho_span",
        span
        * (
            job.get("frame_pixels", job.get("pixels", 256))
            / (job.get("frame_pixels", job.get("pixels", 256)) - 8)
        ),
    )
    scene.camera = camera
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = job.get("samples", 16)
    scene.cycles.use_denoising = False
    scene.cycles.seed = 20261102
    scene.render.resolution_x = job.get("pixels", 256)
    scene.render.resolution_y = job.get("pixels", 256)
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.world = bpy.data.worlds.new("neutral_studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.8, 0.8, 0.8, 1)
    scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.8
    for name, position, power, size in [
        ("key", (-1, -1, 2), 500, 3),
        ("fill", (1, 1, 1.5), 250, 4),
    ]:
        bpy.ops.object.light_add(type="AREA", location=centre + Vector(position) * span)
        light = bpy.context.object
        light.name = name
        light.data.energy = power * span**2
        light.data.shape = "DISK"
        light.data.size = size * span
        light.rotation_euler = (centre - light.location).to_track_quat("-Z", "Y").to_euler()
    if job.get("material_mode") == "studio_neutral":
        scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
        for light in [obj for obj in scene.objects if obj.type == "LIGHT"]:
            light.data.energy *= 0.1
    if job.get("material_mode") in {"unlit", "ao", "normal_ao", "ao_untextured"}:
        for material in bpy.data.materials:
            if not material.use_nodes:
                continue
            tree = material.node_tree
            shader = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            material_output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None)
            if shader is None or material_output is None:
                continue
            emission = tree.nodes.new("ShaderNodeEmission")
            base = shader.inputs["Base Color"]
            if base.is_linked:
                tree.links.new(base.links[0].from_socket, emission.inputs["Color"])
            else:
                emission.inputs["Color"].default_value = base.default_value
            if job["material_mode"] in {"ao", "normal_ao"} or (
                job["material_mode"] == "ao_untextured" and not base.is_linked
            ):
                ao = tree.nodes.new("ShaderNodeAmbientOcclusion")
                ao.samples = 4
                ao.inputs["Distance"].default_value = span * 0.08
                if base.is_linked:
                    tree.links.new(base.links[0].from_socket, ao.inputs["Color"])
                else:
                    ao.inputs["Color"].default_value = base.default_value
                tree.links.new(ao.outputs["Color"], emission.inputs["Color"])
                if job["material_mode"] == "normal_ao":
                    geometry = tree.nodes.new("ShaderNodeNewGeometry")
                    dot = tree.nodes.new("ShaderNodeVectorMath")
                    dot.operation = "DOT_PRODUCT"
                    dot.inputs[1].default_value = (-0.35, -0.45, 0.82)
                    tree.links.new(geometry.outputs["Normal"], dot.inputs[0])
                    light = tree.nodes.new("ShaderNodeMapRange")
                    light.clamp = True
                    light.inputs["From Min"].default_value = 0
                    light.inputs["From Max"].default_value = 1
                    light.inputs["To Min"].default_value = 0.65
                    light.inputs["To Max"].default_value = 1
                    tree.links.new(dot.outputs["Value"], light.inputs["Value"])
                    multiply = tree.nodes.new("ShaderNodeMixRGB")
                    multiply.blend_type = "MULTIPLY"
                    multiply.inputs[0].default_value = 1
                    tree.links.new(ao.outputs["Color"], multiply.inputs[1])
                    tree.links.new(light.outputs["Result"], multiply.inputs[2])
                    tree.links.new(multiply.outputs["Color"], emission.inputs["Color"])
            # Preserve authored coverage; transparent decals must not become rectangles.
            transparent = tree.nodes.new("ShaderNodeBsdfTransparent")
            mix = tree.nodes.new("ShaderNodeMixShader")
            alpha = shader.inputs["Alpha"]
            if alpha.is_linked:
                tree.links.new(alpha.links[0].from_socket, mix.inputs[0])
            else:
                mix.inputs[0].default_value = alpha.default_value
            tree.links.new(transparent.outputs[0], mix.inputs[1])
            tree.links.new(emission.outputs[0], mix.inputs[2])
            tree.links.new(mix.outputs[0], material_output.inputs["Surface"])
    output.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    for angle in job.get("pose_angles", [0]):
        steer_wheels(wheel_groups, angle)
        frame_path = output if angle == 0 else output.with_stem(output.stem + f"-steer{angle:+04d}")
        scene.render.filepath = str(frame_path)
        bpy.ops.render.render(write_still=True)
        frames.append({"angle_degrees": angle, "path": str(frame_path)})
    output.with_suffix(".json").write_text(
        json.dumps(
            {
                "code": job["code"],
                "blender_version": bpy.app.version_string,
                "bounds": [list(low), list(high)],
                "ortho_scale": camera.data.ortho_scale,
                "mesh_count": len(meshes),
                "elapsed_seconds": time.perf_counter() - started,
                "objects": [obj.name for obj in meshes],
                "front_wheel_groups": [
                    {
                        "side": side,
                        "pivot": list(pivot),
                        "objects": [obj.name for obj, _ in members],
                    }
                    for side, pivot, members in wheel_groups
                ],
                "frames": frames,
                "experiment": job,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    jobs = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text())
    for job in jobs:
        render_job(job)

# Throwaway V088 observer: four existing-geometry views, no production changes.
extends "ui_hud_navigation.gd"

var preview: Node3D
var camera: Camera3D
var view_index := 0
var views: Array = []
var baseline: Dictionary
const STAGE = Rect2(536, 224, 1336, 752)
const LABELS = ["current", "side", "rear", "high-oblique"]

func mesh_points(node: Node3D) -> Array[Vector3]:
    var points: Array[Vector3] = []
    for mesh in node.find_children("*", "MeshInstance3D", true, false):
        if not mesh.is_visible_in_tree():
            continue
        var box: AABB = mesh.get_aabb()
        for i in range(8):
            points.append(mesh.global_transform * box.get_endpoint(i))
    return points

func pose_for_draw():
    # Runs after ordinary app processing; never changes the model or gameplay.
    if view_index == 0 or not is_instance_valid(preview):
        return
    var points = mesh_points(preview)
    if points.is_empty():
        return
    var bounds = AABB(points[0], Vector3.ZERO)
    for point in points:
        bounds = bounds.expand(point)
    var center = bounds.get_center()
    var local_direction = [Vector3.ZERO, Vector3(1, 0.22, 0), Vector3(0, 0.25, 1), Vector3(1, 2, 1)][view_index]
    var direction = (preview.global_basis.orthonormalized() * local_direction).normalized()
    var distance = Vector3(5, 1.1, 2.2).length()
    camera.global_position = center + direction * distance
    camera.h_offset = 0
    camera.v_offset = 0
    camera.look_at(center)
    for step in range(60):
        camera.fov = 16 + step * 2
        var height = 2 * distance * tan(deg_to_rad(camera.fov) * 0.5)
        camera.h_offset = (960 - STAGE.get_center().x) / 1080 * height
        camera.v_offset = (STAGE.get_center().y - 540) / 1080 * height
        var fits = true
        for point in points:
            if not STAGE.grow(-48).has_point(camera.unproject_position(point)):
                fits = false
                break
        if fits:
            break

func run():
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await visual_ready()
    for action in ["title_start", "nav:career", "nav:garage", "nav:custom", "custom_page:vinyl", "vinyl:add", "nav:checkout", "checkout", "confirm_yes"]:
        await press(action)
    await press("nav:custom")
    await press("custom_page:vinyl")
    await visual_ready()
    await create_timer(0.5).timeout
    baseline = JSON.parse_string(app.diagnostic_snapshot()).snapshot
    check(baseline.screen == "Customization", "workshop only")
    check(not baseline.career.garage[baseline.selected_car].vinyls.is_empty(), "actual installed vinyl")
    camera = root.get_camera_3d()
    preview = app.get_node_or_null("Showroom model — static wheels")
    check(preview != null and camera != null, "exact observed preview and viewport camera")
    if preview == null or camera == null:
        return
    RenderingServer.frame_pre_draw.connect(pose_for_draw)
    for index in range(4):
        view_index = index
        await create_timer(0.35).timeout
        await RenderingServer.frame_post_draw
        var points = mesh_points(preview)
        var pixels: Array = []
        for point in points:
            var pixel = camera.unproject_position(point)
            pixels.append([pixel.x, pixel.y])
        root.get_texture().get_image().save_png(output + "/" + LABELS[index] + ".png")
        views.append({"label": LABELS[index], "camera_node": str(camera.get_path()), "preview_node": str(preview.get_path()), "camera_position": str(camera.global_position), "camera_rotation": str(camera.global_rotation), "preview_transform": str(preview.global_transform), "fov": camera.fov, "offset": [camera.h_offset, camera.v_offset], "projected_mesh_corners": pixels})
        check(JSON.parse_string(app.diagnostic_snapshot()).snapshot == baseline, "snapshot unchanged for " + LABELS[index])
    RenderingServer.frame_pre_draw.disconnect(pose_for_draw)
    var file = FileAccess.open(output + "/vinyl-camera.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"prototype": true, "question": "Do existing camera views improve actual installed decal inspection?", "installed_customization": baseline.career.garage[baseline.selected_car], "views": views, "checks": evidence}, "  "))
    finish(0)

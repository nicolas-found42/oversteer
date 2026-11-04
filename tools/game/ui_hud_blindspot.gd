# Observe actual normal-cadence race geometry; never place racers or alter the camera.
extends SceneTree
var output: String
var app: Node
var catalog := {}
var samples: Array = []
var captures := {}
var started := 0
var last_sample := -1.0
var rendered_serial := 0
var consumed_serial := 0
var rendered_canvas := {}
var last_render_msec := 0

func visible_canvas() -> Dictionary:
    var labels := {}
    for node in root.find_children("*", "Label", true, false):
        if node.is_visible_in_tree():
            labels[str(node.get_path())] = node.text
    return labels

func rendered_frame():
    rendered_serial += 1
    rendered_canvas = visible_canvas()
    last_render_msec = Time.get_ticks_msec()

func _initialize():
    output = OS.get_cmdline_user_args()[0]
    run.call_deferred()

func vector(values) -> Vector3:
    return Vector3(values[0], values[1], values[2])

func orientation(racer) -> Basis:
    var q = racer.rotation
    return Basis(Quaternion(q[0], q[1], q[2], q[3]))

func dimensions(racer) -> Vector2:
    var definition = catalog.get(racer.car_id, {})
    return Vector2(float(definition.get("width_m", 0)), float(definition.get("length_m", 0)))

func run():
    for car in JSON.parse_string(FileAccess.get_file_as_string("res://assets/cars.json")).cars:
        catalog[car.code] = car
    RenderingServer.frame_post_draw.connect(rendered_frame)
    last_render_msec = Time.get_ticks_msec()
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    var launch_deadline = Time.get_ticks_msec() + 60000
    while started == 0 or Time.get_ticks_msec() - started < 20000:
        await process_frame
        if rendered_serial == consumed_serial:
            if Time.get_ticks_msec() - last_render_msec > 5000:
                finish("failed", "No fresh render for five seconds; geometry is not screenshot evidence")
                return
            continue
        consumed_serial = rendered_serial
        if visible_canvas() != rendered_canvas:
            continue
        if started == 0 and Time.get_ticks_msec() > launch_deadline:
            finish("failed", "No active race within 60 seconds")
            return
        var now = Time.get_ticks_msec() / 1000.0
        if now - last_sample < 0.1:
            continue
        last_sample = now
        var state = JSON.parse_string(app.diagnostic_snapshot())
        var snap = state.get("snapshot", {})
        var race = snap.get("race")
        if snap.get("screen") != "Race" or race == null or race.countdown > 0:
            continue
        if started == 0:
            started = Time.get_ticks_msec()
        var player = race.racers[0]
        var basis = orientation(player)
        var size = dimensions(player)
        if size.x <= 0 or size.y <= 0:
            finish("failed", "Actual player dimensions unavailable")
            return
        var camera = root.get_camera_3d()
        var rivals: Array = []
        var qualifying: Array = []
        for rival in race.racers.slice(1):
            var rival_size = dimensions(rival)
            if rival_size.x <= 0 or rival_size.y <= 0:
                continue
            var delta = vector(rival.position) - vector(player.position)
            var lateral = delta.dot(basis.x)
            var along = delta.dot(basis.z)
            var rival_basis = orientation(rival)
            var half_along = abs(rival_basis.x.dot(basis.z)) * rival_size.x / 2 + abs(rival_basis.z.dot(basis.z)) * rival_size.y / 2
            var half_side = abs(rival_basis.x.dot(basis.x)) * rival_size.x / 2 + abs(rival_basis.z.dot(basis.x)) * rival_size.y / 2
            var side_gap = abs(lateral) - size.x / 2 - half_side
            var overlaps_rear = along < 0 and along + half_along >= -size.y / 2 and along - half_along <= 0
            var projected: Array = []
            var behind = 0
            var on_screen = false
            # Body footprint corners at two heights; height is a stated observation approximation.
            for x in [-1.0, 1.0]:
                for z in [-1.0, 1.0]:
                    for height in [0.2, 1.4]:
                        var point = vector(rival.position) + rival_basis * Vector3(x * rival_size.x / 2, height, z * rival_size.y / 2)
                        var pixel = camera.unproject_position(point)
                        projected.append([pixel.x, pixel.y])
                        if camera.is_position_behind(point):
                            behind += 1
                        elif Rect2(Vector2.ZERO, Vector2(root.size)).has_point(pixel):
                            on_screen = true
            # Adjacent grid lanes are several metres apart. Observe their actual
            # projection instead of equating a contact-distance gap with visibility.
            var candidate = overlaps_rear and abs(lateral) >= size.x / 2 and side_gap >= -0.25 and abs(delta.y) < 1.5 and on_screen
            var observation = {"car_id": rival.car_id, "lateral_m": lateral, "longitudinal_m": along, "side_gap_m": side_gap, "rear_quarter_overlap": overlaps_rear, "qualifies_geometry": candidate, "side": "right" if lateral > 0 else "left", "projected_body_corners": projected, "corners_behind_camera": behind}
            rivals.append(observation)
            if candidate:
                qualifying.append(observation)
        var sample = {"ticks_usec": Time.get_ticks_usec(), "rendered_serial": rendered_serial, "rendered_msec": last_render_msec, "race_elapsed": race.elapsed, "input_frame": app.diagnostic_input_frame(), "player": player, "rivals": rivals, "camera_position": [camera.global_position.x, camera.global_position.y, camera.global_position.z], "camera_transform": str(camera.global_transform), "camera_fov": camera.fov, "viewport_size": [root.size.x, root.size.y]}
        samples.append(sample)
        var label = "rear-quarter" if not qualifying.is_empty() else "negative"
        if not captures.has(label) and (label == "rear-quarter" or race.elapsed >= 2):
            var file = label + ".png"
            var error = root.get_texture().get_image().save_png(output + "/" + file)
            if error != OK:
                finish("failed", "Capture failed")
                return
            captures[label] = {"file": file, "sample": sample, "qualifying": qualifying, "hud": state.get("hud", {})}
    finish("observed" if captures.has("rear-quarter") else "inconclusive", "No shipped indicator; geometry alone does not prove visual occlusion")

func finish(status: String, reason: String):
    var file = FileAccess.open(output + "/blindspot.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": status, "reason": reason, "duration_seconds": 20, "thresholds": {"side_gap_min_m": -0.25, "vertical_center_difference_max_m": 1.5, "rear_quarter": "rival center behind; oriented footprint intersects player rear half; body corner projects inside viewport", "projected_height_approximation_m": [0.2, 1.4]}, "captures": captures, "samples": samples}, "  "))
    file.close()
    quit(1 if status == "failed" else 0)

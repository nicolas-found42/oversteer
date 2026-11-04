extends SceneTree
## Diagnostic-only sweep of a frozen, normally simulated race state.
var app: Node
var vehicle: Node3D
var camera: Camera3D
var sun: DirectionalLight3D
var environment: Environment
var output := ""
var journal: FileAccess
var corners: Array[Vector3] = []
var captures: Array = []
var failures: Array = []
var started := Time.get_ticks_msec()
var rendered_frames := 0
var warmup_draws: Array = []
var rival_bounds: Array = []
var vehicle_local_bounds := AABB()

func pipeline_counts() -> Dictionary:
    return {"canvas":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_PIPELINE_COMPILATIONS_CANVAS),
        "mesh":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_PIPELINE_COMPILATIONS_MESH),
        "surface":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_PIPELINE_COMPILATIONS_SURFACE),
        "draw":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_PIPELINE_COMPILATIONS_DRAW),
        "specialization":RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_PIPELINE_COMPILATIONS_SPECIALIZATION)}

func _initialize():
    RenderingServer.frame_post_draw.connect(func(): rendered_frames += 1)
    call_deferred("run")

func settle_rendered_frames(count: int) -> bool:
    for frame in count:
        await process_frame
        var before := rendered_frames
        # A covered macOS window can skip automatic draws. Render the real
        # viewport without requesting presentation or changing desktop focus.
        RenderingServer.force_draw(false, 1.0/60.0)
        if rendered_frames <= before:
            fail("Explicit inspection draw did not emit frame_post_draw")
            return false
    return true

func write_json(path: String, value) -> bool:
    var file := FileAccess.open(output.path_join(path), FileAccess.WRITE)
    if file == null:
        push_error("Cannot write inspection JSON: " + path)
        return false
    file.store_string(JSON.stringify(value, "  "))
    return true

func log_event(kind: String, details: Dictionary, wall_ms: int = -1):
    journal.store_line(JSON.stringify({"event":kind,"wall_ms":Time.get_ticks_msec()-started if wall_ms < 0 else wall_ms,"details":details}))
    journal.flush()

func fail(message: String):
    push_error(message)
    failures.append(message)
    if journal != null:
        log_event("failure", {"message":message})
    write_json("inspection.json", {"passed":false,"failures":failures,"captures":captures})
    quit(1)

func nodes(node: Node) -> Array[Node]:
    var result: Array[Node] = [node]
    for child in node.get_children():
        result.append_array(nodes(child))
    return result

func vector(v: Vector3) -> Array:
    return [v.x,v.y,v.z]

func color(c: Color) -> Array:
    return [c.r,c.g,c.b,c.a]

func transform(t: Transform3D) -> Dictionary:
    return {"origin":vector(t.origin),"basis":[vector(t.basis.x),vector(t.basis.y),vector(t.basis.z)]}

func collect_bounds():
    for node in nodes(vehicle):
        if node is MeshInstance3D and node.is_visible_in_tree() and node.mesh != null:
            for surface in node.mesh.get_surface_count():
                var vertices: PackedVector3Array = node.mesh.surface_get_arrays(surface)[Mesh.ARRAY_VERTEX]
                for point in vertices:
                    corners.append(node.global_transform * point)
    var lo := Vector3(INF,INF,INF)
    var hi := Vector3(-INF,-INF,-INF)
    var inverse := vehicle.global_transform.affine_inverse()
    for point in corners:
        var local := inverse*point
        lo = lo.min(local)
        hi = hi.max(local)
    vehicle_local_bounds = AABB(lo,hi-lo)

func collect_rival_bounds():
    for racer in nodes(app):
        if racer == vehicle or not racer.has_meta("oversteer_racer_index"):
            continue
        var lo := Vector3(INF,INF,INF)
        var hi := Vector3(-INF,-INF,-INF)
        var inverse: Transform3D = racer.global_transform.affine_inverse()
        for mesh in nodes(racer):
            if mesh is MeshInstance3D and mesh.mesh != null:
                for endpoint in 8:
                    var point: Vector3 = inverse*mesh.global_transform*mesh.get_aabb().get_endpoint(endpoint)
                    lo = lo.min(point)
                    hi = hi.max(point)
        if lo.is_finite():
            rival_bounds.append({"racer":str(racer.name),"bounds":AABB(lo,hi-lo),"world_to_local":inverse})

func blocking_rivals() -> Array:
    var blocked: Array = []
    for rival in rival_bounds:
        for endpoint in 9:
            var target := vehicle_local_bounds.get_center() if endpoint==8 else vehicle_local_bounds.get_endpoint(endpoint)
            target = rival.world_to_local*vehicle.global_transform*target
            if rival.bounds.intersects_segment(rival.world_to_local*camera.global_position,target) != null:
                blocked.append(rival.racer)
                break
    return blocked

func road_sampling() -> Array:
    var observations: Array = []
    var seen := {}
    for node in nodes(app):
        if not node is MeshInstance3D or node.mesh == null:
            continue
        for surface in node.mesh.get_surface_count():
            var material = node.get_active_material(surface)
            if not material is ShaderMaterial or material.shader == null or seen.has(material.get_instance_id()):
                continue
            seen[material.get_instance_id()] = true
            var code: String = material.shader.code
            for sampler in ["native_tarmac", "native_markings", "paving"]:
                if not ("uniform sampler2D " + sampler + ":") in code:
                    continue
                var texture = material.get_shader_parameter(sampler)
                var declaration: String = code.split("uniform sampler2D " + sampler + ":")[1].split(";")[0]
                observations.append({"sampler":sampler,"texture":texture.resource_path,
                    "mipmaps":texture.get_image().has_mipmaps(),"anisotropic":"filter_linear_mipmap_anisotropic" in declaration})
    return observations

func centered_offset(points: PackedVector3Array, distance: float) -> Vector2:
    var offset := Vector2.ZERO
    for iteration in 8:
        var lo := Vector2(INF, INF)
        var hi := Vector2(-INF, -INF)
        var ends: Array[Vector3] = [Vector3.ZERO,Vector3.ZERO,Vector3.ZERO,Vector3.ZERO]
        for point in points:
            var projected := (Vector2(point.x,point.y)-offset)/(distance-point.z)
            if projected.x < lo.x:
                lo.x = projected.x
                ends[0] = point
            if projected.x > hi.x:
                hi.x = projected.x
                ends[1] = point
            if projected.y < lo.y:
                lo.y = projected.y
                ends[2] = point
            if projected.y > hi.y:
                hi.y = projected.y
                ends[3] = point
        var next := Vector2(
            (ends[0].x*(distance-ends[1].z)+ends[1].x*(distance-ends[0].z))/(2*distance-ends[0].z-ends[1].z),
            (ends[2].y*(distance-ends[3].z)+ends[3].y*(distance-ends[2].z))/(2*distance-ends[2].z-ends[3].z))
        if next.distance_to(offset) < 0.000001:
            return next
        offset = next
    return offset

func fit_camera(azimuth: float, elevation: float, roll: float) -> Dictionary:
    var minimum := corners[0]
    var maximum := corners[0]
    for point in corners:
        minimum = minimum.min(point)
        maximum = maximum.max(point)
    var center := (minimum + maximum) * 0.5
    var a := deg_to_rad(azimuth)
    var e := deg_to_rad(elevation)
    var direction := vehicle.global_basis.orthonormalized() * Vector3(sin(a)*cos(e),sin(e),cos(a)*cos(e))
    camera.projection = Camera3D.PROJECTION_PERSPECTIVE
    camera.keep_aspect = Camera3D.KEEP_HEIGHT
    camera.fov = 42.0
    camera.near = 0.04
    camera.far = 1800.0
    camera.global_position = center + direction * 10.0
    camera.look_at(center, Vector3.UP)
    camera.rotate_object_local(Vector3.BACK, deg_to_rad(roll))
    var size := root.get_visible_rect().size
    var aspect := size.x/size.y
    var tangent := tan(deg_to_rad(camera.fov)*0.5)
    var distance := 0.1
    var basis := camera.global_basis
    var local_points := PackedVector3Array()
    for point in corners:
        var relative := point-center
        var z := relative.dot(basis.z)
        var local := Vector3(relative.dot(basis.x),relative.dot(basis.y),z)
        local_points.append(local)
        distance = max(distance, z + max(camera.near,abs(local.y)/(tangent*0.92)))
        distance = max(distance, z + abs(local.x)/(tangent*aspect*0.92))
    var offset := Vector2.ZERO
    for iteration in 8:
        offset = centered_offset(local_points, distance)
        var fitted := 0.1
        for point in local_points:
            fitted = max(fitted,point.z+max(camera.near,abs(point.y-offset.y)/(tangent*0.92)))
            fitted = max(fitted,point.z+abs(point.x-offset.x)/(tangent*aspect*0.92))
        if abs(fitted-distance) < 0.00001:
            break
        distance = fitted
    offset = centered_offset(local_points, distance)
    var target := center+basis.x*offset.x+basis.y*offset.y
    camera.global_position = target+basis.z*distance
    var lo := Vector2(INF,INF)
    var hi := Vector2(-INF,-INF)
    var behind := false
    for point in corners:
        var p := camera.unproject_position(point)
        lo = lo.min(p)
        hi = hi.max(p)
        behind = behind or camera.is_position_behind(point)
    return {"azimuth":azimuth,"elevation":elevation,"roll":roll,"transform":transform(camera.global_transform),
        "target":vector(target),"fov":camera.fov,"near":camera.near,"far":camera.far,
        "viewport":[size.x,size.y],"projected_bounds":[[lo.x,lo.y],[hi.x,hi.y]],
        "center_error_pixels":vector(Vector3((lo.x+hi.x-size.x)*0.5,(lo.y+hi.y-size.y)*0.5,0)),
        "centered":((lo+hi)*0.5-size*0.5).length() <= 1.0,
        "whole_car_in_frame":not behind and lo.x>=0 and lo.y>=0 and hi.x<=size.x and hi.y<=size.y,
        "mesh_bounds_min":vector(minimum),"mesh_bounds_max":vector(maximum),"bounds_points":corners.size()}

func run():
    var args := OS.get_cmdline_user_args()
    var freeze_frame := 332
    for i in args.size():
        if args[i] == "--inspection-output" and i+1 < args.size():
            output = args[i+1]
        if args[i] == "--freeze-frame" and i+1 < args.size():
            freeze_frame = int(args[i+1])
    if output.is_empty():
        push_error("Inspection requires --inspection-output absolute-directory")
        quit(1)
        return
    DirAccess.make_dir_recursive_absolute(output)
    journal = FileAccess.open(output.path_join("events.jsonl"), FileAccess.WRITE)
    if journal == null:
        fail("Cannot create inspection journal")
        return
    log_event("startup", {"engine":Engine.get_version_info(),"renderer":RenderingServer.get_current_rendering_method(),"driver":RenderingServer.get_current_rendering_driver_name()})
    var initialization_start := Time.get_ticks_msec()
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    var initialization_ms := Time.get_ticks_msec()-initialization_start
    var simulation_start := Time.get_ticks_msec()
    var waited := 0
    var previous_pipelines := pipeline_counts()
    while app.diagnostic_input_frame() < freeze_frame:
        var tick_start := Time.get_ticks_msec()
        await process_frame
        waited += 1
        var pipelines := pipeline_counts()
        if pipelines != previous_pipelines:
            warmup_draws.append({"process_frame":waited,"frame_wall_ms":Time.get_ticks_msec()-tick_start,"before":previous_pipelines,"after":pipelines})
            previous_pipelines = pipelines
        if waited > 18000:
            fail("Race did not reach requested inspection tick %d" % freeze_frame)
            return
    app.process_mode = Node.PROCESS_MODE_DISABLED
    var draw_start := Time.get_ticks_msec()
    if not await settle_rendered_frames(1):
        return
    var explicit_draw_ms := Time.get_ticks_msec()-draw_start
    var initial: Dictionary = JSON.parse_string(app.diagnostic_snapshot())
    for node in nodes(app):
        if node is Camera3D and node.current:
            camera = node
        if node is DirectionalLight3D:
            sun = node
        if node is WorldEnvironment:
            environment = node.environment
        if node.has_meta("oversteer_racer_index") and node.get_meta("oversteer_racer_index") == 0:
            vehicle = node
        if node is CanvasLayer:
            node.visible = false
    if vehicle == null or camera == null or sun == null or environment == null:
        fail("Inspection scene is missing car/camera/sun/environment")
        return
    initial["rendering"] = {"road_sampling":road_sampling(),"anisotropic_filtering_level":ProjectSettings.get_setting("rendering/textures/default_filters/anisotropic_filtering_level"),
        "sky_present":environment.sky != null,"reflection_source":environment.reflected_light_source,
        "sky_reflections":environment.reflected_light_source == Environment.REFLECTION_SOURCE_SKY,"sun_energy":sun.light_energy}
    if not write_json("race-state.json", initial):
        fail("Cannot persist frozen race state")
        return
    var bounds_start := Time.get_ticks_msec()
    collect_bounds()
    collect_rival_bounds()
    var bounds_ms := Time.get_ticks_msec()-bounds_start
    if corners.is_empty():
        fail("No visible vehicle geometry bounds")
        return
    log_event("race_frozen", {"input_frame":initial.input_frame,"requested_freeze_frame":freeze_frame,"car":vehicle.get_meta("oversteer_car_id"),"mesh_bounds_points":corners.size(),
        "initialization_ms":initialization_ms,"simulation_and_loading_ms":bounds_start-simulation_start,"mesh_bounds_ms":bounds_ms,"loading":initial.loading,
        "runtime_cpu":initial.timing,"explicit_draw_ms":explicit_draw_ms,"shader_pipeline_frames":warmup_draws,"pipeline_counts":pipeline_counts(),
        "shader_timing_scope":"Frames with pipeline compilation are timed wall-clock; asynchronous compile CPU time is not separately exposed by Godot."})
    var natural := {"rotation":sun.rotation_degrees,"color":sun.light_color,"energy":sun.light_energy,"ambient":environment.ambient_light_color,"ambient_energy":environment.ambient_light_energy,"background":environment.background_mode}
    var race_world: Node3D = app.get_node("RaceWorld")
    var presets := [
        {"name":"neutral","rotation":Vector3(-50,-35,0),"color":Color(1,0.98,0.95),"energy":1.0,"ambient":Color(0.65,0.68,0.72),"ambient_energy":0.7},
        {"name":"grazing","rotation":Vector3(-12,65,0),"color":Color(1,0.82,0.65),"energy":2.0,"ambient":Color(0.3,0.35,0.45),"ambient_energy":0.4},
        {"name":"backlight","rotation":Vector3(-25,145,0),"color":Color(0.7,0.82,1),"energy":2.2,"ambient":Color(0.28,0.32,0.4),"ambient_energy":0.28}
    ]
    var shots: Array = []
    # Every isolated azimuth plus course quarters/top/underside: 14 per car, 42 total.
    for view in [[45,10],[225,10],[135,35],[315,35]]:
        shots.append({"azimuth":view[0],"elevation":view[1],"roll":0,"light":"race","isolated":false})
    for azimuth in range(0,360,45):
        shots.append({"azimuth":azimuth,"elevation":35 if azimuth%90 else 5,
            "roll":-20 if azimuth==135 else (20 if azimuth==315 else 0),
            "light":"grazing" if azimuth==135 else ("backlight" if azimuth==315 else "neutral"),"isolated":true})
    shots.append({"azimuth":45,"elevation":75,"roll":0,"light":"neutral","isolated":true})
    shots.append({"azimuth":225,"elevation":-25,"roll":0,"light":"neutral","isolated":true})
    if "--inspection-smoke" in args:
        shots = [shots[8],shots[6],shots[7],shots[11],shots[12],shots[13]]
    for i in shots.size():
        var shot: Dictionary = shots[i]
        var capture_start := Time.get_ticks_msec()
        log_event("capture_begin", {"index":i,"shot":shot}, capture_start-started)
        race_world.visible = not shot.isolated
        for node in nodes(app):
            if node.has_meta("oversteer_racer_index") and node != vehicle:
                node.visible = not shot.isolated
            if node is Light3D and node != sun:
                node.visible = not shot.isolated
            if node is GPUParticles3D:
                node.visible = not shot.isolated
        var lighting: Dictionary = natural if not shot.isolated else presets.filter(func(p):return p.name==shot.light)[0]
        sun.rotation_degrees = lighting.rotation
        sun.light_color = lighting.color
        sun.light_energy = lighting.energy
        sun.visible = true
        environment.ambient_light_color = lighting.ambient
        environment.ambient_light_energy = lighting.ambient_energy
        environment.background_mode = natural.background if not shot.isolated else Environment.BG_COLOR
        environment.background_color = Color(0.045,0.055,0.07)
        var camera_state := fit_camera(shot.azimuth,shot.elevation,shot.roll)
        var requested_elevation: float = shot.elevation
        var blockers: Array = [] if shot.isolated else blocking_rivals()
        var initial_blockers := blockers.duplicate()
        while not blockers.is_empty() and shot.elevation < 80:
            shot.elevation = min(80,shot.elevation+15)
            camera_state = fit_camera(shot.azimuth,shot.elevation,shot.roll)
            blockers = blocking_rivals()
        camera_state["requested_elevation"] = requested_elevation
        camera_state["initial_blocking_rivals"] = initial_blockers
        camera_state["blocking_rivals"] = blockers
        if not blockers.is_empty():
            failures.append("Course view obstructed by rivals: " + str(blockers))
        var id := "view-%03d-%s-az%03d-el%+03d-roll%+03d" % [i,shot.light,shot.azimuth,shot.elevation,shot.roll]
        # Allow scene changes to render; never grab the preceding camera's image.
        if not await settle_rendered_frames(3):
            return
        if i == 0 and "--inspection-metal-capture" in args:
            write_json("metal-capture-ready.json", {"id":id,"shot":shot,"camera":camera_state,
                "window_can_draw":DisplayServer.window_can_draw(),"render_loop_enabled":RenderingServer.is_render_loop_enabled()})
            var deadline := Time.get_ticks_msec() + 120000
            while not FileAccess.file_exists(output.path_join("metal-capture-done")):
                await process_frame
                RenderingServer.force_draw(DisplayServer.window_can_draw(), 1.0/60.0)
                if Time.get_ticks_msec() > deadline:
                    fail("Timed out waiting for bounded Metal capture")
                    return
            if not await settle_rendered_frames(1):
                return
        var image := root.get_texture().get_image()
        var error := image.save_png(output.path_join(id+".png"))
        var completed_wall_ms := Time.get_ticks_msec()-started
        var capture_ms := completed_wall_ms-(capture_start-started)
        var record := {"id":id,"shot":shot,"camera":camera_state,"image_size":[image.get_width(),image.get_height()],
            "capture_ms":capture_ms,"capture_started_wall_ms":capture_start-started,
            "light":{"rotation_degrees":vector(sun.rotation_degrees),"color":color(sun.light_color),"energy":sun.light_energy,"shadow":sun.shadow_enabled,
            "ambient_color":color(environment.ambient_light_color),"ambient_energy":environment.ambient_light_energy,"tonemapper":environment.tonemap_mode},
            "simulation":"frozen at race-state.json; no physics advanced during sweep","input_frame":initial.input_frame,
            "rendered_frames":rendered_frames,"window_can_draw":DisplayServer.window_can_draw(),
            "materials_and_physics":"race-state.json","process_time_monitor":Performance.get_monitor(Performance.TIME_PROCESS),
            "draw_calls_monitor":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
            "primitives_monitor":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
            "monitor_scope":"Godot cached contextual monitors; not a performance benchmark"}
        if error != OK or not write_json(id+".json", record):
            fail("Failed to save capture " + id)
            return
        captures.append(record)
        if not camera_state.whole_car_in_frame:
            failures.append("Framing: " + id)
        if not camera_state.centered:
            failures.append("Off-center: " + id)
        log_event("capture_complete", {"id":id,"index":i,"capture_ms":capture_ms,"png_bytes":FileAccess.get_file_as_bytes(output.path_join(id+".png")).size(),"framed":camera_state.whole_car_in_frame}, completed_wall_ms)
    var final_state: Dictionary = JSON.parse_string(app.diagnostic_snapshot())
    var unchanged: bool = initial.snapshot == final_state.snapshot and initial.input_frame == final_state.input_frame
    write_json("inspection.json", {"passed":failures.is_empty() and unchanged,"failures":failures,"captures":captures,
        "frozen_simulation_unchanged":unchanged,"expected_captures":shots.size(),"car":vehicle.get_meta("oversteer_car_id"),
        "renderer":RenderingServer.get_current_rendering_method(),"driver":RenderingServer.get_current_rendering_driver_name()})
    log_event("finished", {"captures":captures.size(),"physics_unchanged":unchanged,"failures":failures})
    quit(0 if failures.is_empty() and unchanged else 1)

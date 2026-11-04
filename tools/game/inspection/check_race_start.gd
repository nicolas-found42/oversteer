extends SceneTree
## Two synchronized rendered checkpoints; no periodic or incidental images.
var output := ""

func _initialize():
    call_deferred("run")

func run():
    var args := OS.get_cmdline_user_args()
    for i in args.size()-1:
        if args[i] == "--inspection-output":
            output = args[i+1]
    if output.is_empty():
        quit(1)
        return
    DirAccess.make_dir_recursive_absolute(output)
    var app = load("res://main.tscn").instantiate()
    root.add_child(app)
    var reports: Array = []
    var failures: Array = []
    var previous_grid: Array = []
    for phase in ["countdown", "go", "launch"]:
        var state: Dictionary
        var reached := false
        for tick in 18000:
            await process_frame
            # Read the expensive geometry/material snapshot only at these checkpoints.
            var input_frame: int = app.diagnostic_input_frame()
            if (phase == "countdown" and tick >= 120 and app.find_child("RaceHUD",true,false).get_child_count() > 0) or (phase == "go" and input_frame >= 15) or (phase == "launch" and input_frame >= 166):
                state = JSON.parse_string(app.diagnostic_snapshot())
                if state.snapshot.race == null or not state.hud.has("message"):
                    continue
                reached = true
                break
        if not reached:
            failures.append("Checkpoint never reached: " + phase)
            break
        app.process_mode = Node.PROCESS_MODE_DISABLED
        var camera := root.get_camera_3d()
        var t := camera.global_transform
        state["camera"] = {"position":[t.origin.x,t.origin.y,t.origin.z],"basis":[[t.basis.x.x,t.basis.x.y,t.basis.x.z],[t.basis.y.x,t.basis.y.y,t.basis.y.z],[t.basis.z.x,t.basis.z.y,t.basis.z.z]],"fov":camera.fov}
        var race: Dictionary = state.snapshot.race
        var label: Dictionary = state.hud.message
        var center := Vector2(label.position[0],label.position[1])+Vector2(label.size[0],label.size[1])*0.5
        if center.distance_to(Vector2(960,540)) > 1:
            failures.append("Countdown/GO label not centered")
        if phase == "countdown":
            if race.countdown <= 0 or race.elapsed != 0 or state.hud.speed.text != "000":
                failures.append("Countdown HUD/clock mismatch")
            for racer in race.racers:
                previous_grid.append(racer.position)
                if racer.speed_kph != 0:
                    failures.append("Vehicle moved before GO")
        elif phase == "go":
            if label.text != "GO" or race.elapsed <= 0:
                failures.append("GO HUD/clock mismatch")
            if race.racers[0].position == previous_grid[0]:
                failures.append("Player did not leave the grid after GO")
        else:
            for racer in race.racers.slice(1):
                if racer.speed_kph < 10 or racer.rpm <= 1000:
                    failures.append("Rival launch stalled: " + racer.name)
        if phase != "launch":
            await process_frame
            RenderingServer.force_draw(false,1.0/60.0)
            var error := root.get_texture().get_image().save_png(output.path_join(phase+".png"))
            if error != OK:
                failures.append("Screenshot failed: " + phase)
        reports.append({"phase":phase,"state":state})
        app.process_mode = Node.PROCESS_MODE_INHERIT
    var file := FileAccess.open(output.path_join("race-start-check.json"),FileAccess.WRITE)
    file.store_string(JSON.stringify({"passed":failures.is_empty() and reports.size()==3,"failures":failures,"checkpoints":reports},"  "))
    quit(0 if failures.is_empty() and reports.size()==3 else 1)

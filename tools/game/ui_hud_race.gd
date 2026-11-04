# Observe the normal scenario simulation; never write race or scoring state.
extends SceneTree
var output: String
var seen := {}
var samples: Array = []
var app: Node
var rendered_serial := 0
var consumed_serial := 0
var rendered_canvas := {}
var last_render_msec := 0
var observation_render := {}

# This signal can be emitted synchronously inside a borrowed Rust method.
# Read native Label state only; never call app.diagnostic_snapshot() here.
func rendered_frame():
    rendered_serial += 1
    rendered_canvas = visible_canvas()
    last_render_msec = Time.get_ticks_msec()

func visible_canvas() -> Dictionary:
    var labels := {}
    for node in root.find_children("*", "Label", true, false):
        if node.is_visible_in_tree():
            labels[str(node.get_path())] = node.text
    return labels

func fail_evidence(reason: String):
    var file = FileAccess.open(output + "/capture-failure.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "failed", "reason": reason,
        "rendered_serial": rendered_serial, "consumed_serial": consumed_serial,
        "window_can_draw": DisplayServer.window_can_draw(),
        "render_loop_enabled": RenderingServer.is_render_loop_enabled()}, "  "))
    push_error(reason)
    quit(1)
func _initialize():
    output = OS.get_cmdline_user_args()[0]
    run.call_deferred()
func capture(label: String, state: Dictionary):
    var selected = OS.get_environment("OVERSTEER_CAPTURE_LABELS")
    if not selected.is_empty() and not label in selected.split(","):
        return
    if seen.has(label) or seen.size() >= 30:
        return
    seen[label] = true
    var error = root.get_texture().get_image().save_png(output + "/hud-" + label + ".png")
    if error != OK:
        fail_evidence("Viewport image could not be saved")
        return
    samples.append({"label": label, "state": state, "render": observation_render.duplicate()})
    var file = FileAccess.open(output + "/hud-observations.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(samples, "  "))
func run():
    RenderingServer.frame_post_draw.connect(rendered_frame)
    last_render_msec = Time.get_ticks_msec()
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    while true:
        # SceneTree emits this before the Rust app's next _process callback.
        # Consume a completed normal draw here, outside any Rust borrow.
        await process_frame
        if rendered_serial == consumed_serial:
            if Time.get_ticks_msec() - last_render_msec > 5000:
                fail_evidence("No completed render for five seconds; simulation state is not screenshot evidence")
                return
            continue
        consumed_serial = rendered_serial
        if visible_canvas() != rendered_canvas:
            # A native forced capture may have drawn partway through a callback;
            # discard it if the scene's labels changed after that draw.
            continue
        observation_render = {"serial": rendered_serial,
            "completed_msec": last_render_msec,
            "sampled_msec": Time.get_ticks_msec(),
            "window_can_draw": DisplayServer.window_can_draw()}
        observe()
func observe():
    var state = JSON.parse_string(app.diagnostic_snapshot())
    var snap = state.get("snapshot", {})
    if snap.get("screen") == "Results":
        capture("results", state)
        var result_file = FileAccess.open(output + "/race-result.json", FileAccess.WRITE)
        result_file.store_string(JSON.stringify(state, "  "))
        quit(0)
        return
    var loading = root.find_child("Destination", true, false)
    if loading and loading is CanvasItem and loading.is_visible_in_tree():
        capture("loading-garage" if loading.text == "Preparing your garage" else "loading-event", state)
    if snap.get("screen") != "Race" or not snap.get("race"):
        return
    var race = snap.race
    var player = race.racers[0]
    var speed_label = root.find_child("Hud_speed", true, false)
    var speed = speed_label.text if speed_label else ""
    if speed.is_empty():
        return
    var labels = []
    for row in range(4):
        var split = root.find_child("Hud_split_" + str(row), true, false)
        if split and split.text.begins_with("~"):
            labels.append("measured-split")
            break
    labels.append("speed-" + str(speed.length()) + "-digits")
    labels.append("gear-" + str(player.gear))
    labels.append("position-" + str(race.position))
    if race.elapsed > 10 and race.elapsed < 12:
        labels.append("background-early")
    if race.elapsed > 40 and race.elapsed < 42:
        labels.append("background-later")
    if player.nitrous >= .99:
        labels.append("nitrous-full")
    if player.nitrous <= .01:
        labels.append("nitrous-empty")
    if race.mode == "Drift":
        if player.drift_score == 0:
            labels.append("drift-zero")
        if player.drift_score >= race.target * .85 and player.drift_score < race.target:
            labels.append("drift-near-target")
        if player.drift_score >= race.target:
            labels.append("drift-target-reached")
        if player.drift_score >= race.target * 10:
            labels.append("drift-above-target")
        if race.elapsed >= 170:
            labels.append("drift-late-score")
        if player.chain_score > 0:
            labels.append("drift-active-chain")
        if player.drift_score > 0 and player.chain_score == 0:
            labels.append("drift-banked")
    for label in labels:
        if not seen.has(label):
            capture(label, state)

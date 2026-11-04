# Actual menu/control behavior only. No screenshots or rendered-quality claims.
extends "ui_hud_navigation.gd"
var observations: Array = []
var finishing := false

func finish(code: int):
    if finishing:
        return
    finishing = true
    var file = FileAccess.open(output + "/navigation.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(evidence, "  "))
    file.close()
    # Let the actual scene release its music playback before the Dummy audio
    # driver shuts down; an immediate SceneTree.quit leaves the stream queued.
    app.queue_free()
    await process_frame
    await create_timer(0.1).timeout
    quit(code)

func run():
    check(DisplayServer.get_name() == "headless", "headless display required")
    check(AudioServer.get_driver_name() == "Dummy", "silent Dummy audio required")
    await super.run()

func capture(name: String):
    await visual_ready()
    await create_timer(0.5).timeout
    var controls: Array = []
    for node in root.find_children("*", "Control", true, false):
        if node.is_queued_for_deletion() or not node.is_visible_in_tree():
            continue
        if not (node is Label or node is Button):
            continue
        var bounds = node.get_global_rect()
        controls.append({"name": str(node.name), "text": node.text,
            "action": node.get_meta("ui_action", ""),
            "rect": [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y]})
    var state = JSON.parse_string(app.diagnostic_snapshot()).snapshot
    observations.append({"name": name, "screen": state.screen,
        "focus": focus_action(), "controls": controls})
    var file = FileAccess.open(output + "/headless-observations.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"logic_only": true, "rendered": false,
        "drivers": {"display": DisplayServer.get_name(), "audio": AudioServer.get_driver_name()},
        "observations": observations}, "  "))

# Capture the real minimum configured window through macOS without taking focus.
extends "ui_hud_navigation.gd"
func run():
    root.size = Vector2i(1440, 810)
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await settle()
    await window_capture("title")
    await press("title_start")
    await press("options")
    await window_capture("settings")
    await press("back_options")
    await press("nav:career")
    await press("nav:garage")
    await press("nav:custom")
    await window_capture("paint")
    await press("custom_page:performance")
    await window_capture("tuning")
    await press("custom_page:vinyl")
    await press("vinyl:add")
    await window_capture("vinyl")
    finish(0)
func window_capture(label: String):
    await visual_ready()
    await create_timer(0.25).timeout
    await settle(12)
    var request = FileAccess.open(output + "/window-request.json", FileAccess.WRITE)
    request.store_string(JSON.stringify({"label": label, "window_size": [root.size.x, root.size.y], "viewport_size": [root.get_visible_rect().size.x, root.get_visible_rect().size.y]}))
    request.close()
    for i in range(1200):
        await process_frame
        if FileAccess.file_exists(output + "/" + label + ".done"):
            return
    check(false, "window capture timeout")

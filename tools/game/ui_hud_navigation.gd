# Exercise real controls and input dispatch without activating the desktop window.
extends SceneTree
var output: String
var evidence: Array = []
var app: Node
func _initialize():
    output = OS.get_cmdline_user_args()[0]
    run.call_deferred()
func settle(count: int = 8):
    for i in range(count):
        await process_frame
func button(action: String):
    var menu = root.find_child("Menus", true, false)
    for child in menu.get_children():
        if child is Button and not child.is_queued_for_deletion() and child.get_meta("ui_action", "") == action:
            return child
    return null
func check(condition: bool, label: String):
    evidence.append({"check": label, "passed": condition})
    print(label, "=", condition)
    if not condition:
        finish(1)
func finish(code: int):
    var file = FileAccess.open(output + "/navigation.json", FileAccess.WRITE)
    file.store_string(JSON.stringify(evidence, "  "))
    quit(code)
func press(action: String):
    var control = button(action)
    check(control != null, "control " + action)
    if control == null:
        return
    control.grab_focus()
    control.pressed.emit()
    await settle()
func focus_action():
    var owner = root.gui_get_focus_owner()
    return owner.get_meta("ui_action", "") if owner else "none"
func key(code: Key):
    var event = InputEventKey.new()
    event.keycode = code
    event.physical_keycode = code
    event.pressed = true
    root.push_input(event)
    await settle(2)
    event.pressed = false
    root.push_input(event)
    await settle()
func joy(code: JoyButton):
    var event = InputEventJoypadButton.new()
    event.button_index = code
    event.pressed = true
    root.push_input(event)
    await settle(2)
    event.pressed = false
    root.push_input(event)
    await settle()
func visual_ready():
    for i in range(600):
        var destination = root.find_child("Destination", true, false)
        if not destination or not destination.is_visible_in_tree():
            break
        await process_frame
    await settle(2)
func capture(name: String):
    await visual_ready()
    # Let the 200 ms menu reveal and asynchronous material pipelines settle.
    # This waits in the normal render loop; it does not force a frame or change simulation speed.
    await create_timer(0.5).timeout
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png(output + "/" + name + ".png")
    if name == "utility-focus":
        var camera = root.get_camera_3d()
        var report = {"camera_position": str(camera.global_position), "camera_rotation": str(camera.global_rotation), "fov": camera.fov, "offset": [camera.h_offset, camera.v_offset], "children": []}
        for child in app.get_children():
            if child is Node3D:
                report.children.append({"name": str(child.name), "position": str(child.global_position), "visible": child.is_visible_in_tree(), "meshes": child.find_children("*", "MeshInstance3D", true, false).size(), "screen": str(camera.unproject_position(child.global_position))})
        var file = FileAccess.open(output + "/main-preview.json", FileAccess.WRITE)
        file.store_string(JSON.stringify(report, "  "))
func run():
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await settle()
    await capture("title")
    await press("title_quick")
    check(JSON.parse_string(app.diagnostic_snapshot()).snapshot.screen == "QuickRace", "title Quick Race enters setup")
    var reachable := {}
    for page in range(3):
        var menu = root.find_child("Menus", true, false)
        for child in menu.get_children():
            if child is Button and not child.is_queued_for_deletion():
                var action = child.get_meta("ui_action", "")
                if action.begins_with("event:"):
                    reachable[action] = true
        if page == 0:
            await capture("quick-dossier")
        await press("event_page_next")
    check(reachable.size() == 18, "all 18 Quick Race events reachable")
    check(button("event:0") != null, "event pages wrap to first event")
    await press("event_page_prev")
    await capture("quick-last-page")
    await press("nav:custom")
    for i in range(6):
        await press("custom_page:wheels")
        var wheels = app.find_children("*", "SubViewport", true, false).size()
        check(wheels == 4, "four actual rim previews " + str(i))
        await press("custom_page:paint")
        check(app.find_children("*", "SubViewport", true, false).is_empty(), "rim viewports released " + str(i))
    await press("custom_done")
    await press("nav:main")
    await press("credits")
    await capture("credits")
    await key(KEY_ESCAPE)
    check(button("options") != null, "Escape returns Credits to Main Menu")
    button("options").grab_focus()
    await settle()
    await capture("utility-focus")
    await press("nav:career")
    await press("nav:dealer")
    await press("car:GT4_MINI0001")
    await press("buy")
    check(focus_action() == "confirm_no", "purchase Cancel initial focus")
    var before = JSON.parse_string(app.diagnostic_snapshot())["snapshot"]
    for i in range(6):
        await key(KEY_TAB)
        check(focus_action() in ["confirm_no", "confirm_yes"], "modal Tab contained " + str(i) + " (" + focus_action() + ")")
    await joy(JOY_BUTTON_START)
    await key(KEY_R)
    var after = JSON.parse_string(app.diagnostic_snapshot())["snapshot"]
    check(before == after, "Start and restart cannot leak through purchase modal")
    check(button("confirm_no") != null, "modal remains open after unrelated shortcuts")
    await key(KEY_ESCAPE)
    check(button("confirm_no") == null, "Escape cancels purchase")
    check(focus_action() == "buy", "Escape restores purchase focus")
    await press("buy")
    await joy(JOY_BUTTON_B)
    check(button("confirm_no") == null, "gamepad B cancels purchase")
    check(focus_action() == "buy", "gamepad cancellation restores focus")
    await press("buy")
    await joy(JOY_BUTTON_DPAD_RIGHT)
    check(focus_action() == "confirm_yes", "gamepad direction traverses dialog")
    await joy(JOY_BUTTON_DPAD_LEFT)
    check(focus_action() == "confirm_no", "gamepad direction returns to Cancel")
    await joy(JOY_BUTTON_A)
    check(button("confirm_no") == null, "gamepad A activates Cancel")
    await press("buy")
    await press("confirm_yes")
    var purchased = JSON.parse_string(app.diagnostic_snapshot())["snapshot"]
    check(purchased["career"]["cash"] == 5500, "25000 minus 19500 leaves 5500")
    check(purchased["career"]["garage"].has("GT4_MINI0001"), "purchase transfers ownership")
    await press("nav:main")
    await press("options")
    for action in ["units", "units", "quality", "quality", "difficulty", "difficulty"]:
        await press(action)
        check(focus_action() == action, "redraw preserves " + action + " focus")
    for action in ["bind:throttle", "button:nitrous", "axis:steering"]:
        var prior = button(action).text
        await press(action)
        await key(KEY_ESCAPE)
        check(button(action).text == prior, "Escape cancels " + action + " without changing assignment")
    await press("bind:throttle")
    await capture("rebind-keyboard")
    await key(KEY_W)
    check(button("bind:throttle").text == "W", "keyboard binding accepts W")
    await press("button:nitrous")
    await capture("rebind-gamepad")
    await joy(JOY_BUTTON_A)
    check(button("button:nitrous").text == "Button 0", "gamepad binding accepts A")
    await press("bind:throttle")
    await key(KEY_E)
    check(button("bind:throttle").text == "E", "non-default binding set before reset")
    var quality = button("quality").text
    await press("reset_bindings")
    check(button("bind:throttle").text == "W", "reset restores keyboard defaults")
    check(button("button:nitrous").text == "Button 0", "reset restores button defaults")
    check(button("axis:steering").text == "Axis 0", "reset restores axis defaults")
    check(button("quality").text == quality, "reset preserves unrelated display settings")
    var saved = JSON.parse_string(FileAccess.get_file_as_string(output + "/settings/options.json"))
    check(saved.controller.axes.steering == 0 and saved.keyboard.throttle == KEY_W, "reset defaults persisted")
    await capture("settings-rebound")
    finish(0)

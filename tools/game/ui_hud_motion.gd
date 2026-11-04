# Observe normal render-loop menu transitions without activating the desktop window.
extends "ui_hud_navigation.gd"

func run():
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await visual_ready()
    await create_timer(0.4).timeout
    var ready = FileAccess.open(output + "/motion-ready", FileAccess.WRITE)
    ready.store_string(str(Time.get_ticks_usec()))
    ready.close()
    var deadline = Time.get_ticks_msec() + 30000
    while not FileAccess.file_exists(output + "/recording-started"):
        if Time.get_ticks_msec() > deadline:
            check(false, "recording start timeout")
            return
        await process_frame
    var started = Time.get_ticks_usec()
    var sequence = [
        [0.40, "title_start"], [0.48, "options"], [0.56, "back_options"],
        [1.20, "nav:quick"], [1.28, "event:1"], [1.36, "event:0"],
        [2.00, "nav:main"], [2.08, "options"], [2.16, "back_options"],
        [2.80, "nav:quick"], [2.88, "event:1"], [2.96, "event:0"],
        [3.60, "nav:main"], [3.68, "options"], [3.76, "back_options"],
        [4.40, "nav:quick"], [4.48, "event:1"], [4.56, "event:0"],
        [5.20, "nav:main"]
    ]
    var cursor = 0
    var last_action = -1.0
    var last_sample = -1.0
    var samples: Array = []
    var actions: Array = []
    while not FileAccess.file_exists(output + "/recording-done"):
        await process_frame
        var elapsed = (Time.get_ticks_usec() - started) / 1000000.0
        if elapsed > 25.0:
            check(false, "recording completion timeout")
            return
        if cursor < sequence.size() and elapsed >= sequence[cursor][0]:
            var action = sequence[cursor][1]
            var control = button(action)
            check(control != null, "motion control " + action)
            if control == null:
                return
            control.grab_focus()
            control.pressed.emit()
            last_action = elapsed
            actions.append({"seconds": elapsed, "ticks_usec": Time.get_ticks_usec(), "action": action})
            cursor += 1
        if elapsed - last_sample >= 0.05 and samples.size() < 400:
            var menu = root.find_child("Menus", true, false)
            var destination = root.find_child("Destination", true, false)
            var sample = {"seconds": elapsed, "ticks_usec": Time.get_ticks_usec(), "since_action": elapsed - last_action, "focus": focus_action(), "visible": menu.is_visible_in_tree(), "alpha": menu.modulate.a, "position": [menu.position.x, menu.position.y], "destination_visible": destination != null and destination.is_visible_in_tree()}
            samples.append(sample)
            last_sample = elapsed
    check(cursor == sequence.size(), "all rapid transitions dispatched")
    var settled = 0
    for sample in samples:
        if sample.seconds > 0.8 and sample.since_action >= 0.30:
            settled += 1
            check(sample.visible and sample.alpha >= 0.99 and abs(sample.position[0]) < 0.5 and abs(sample.position[1]) < 0.5 and not sample.destination_visible, "settled menu at %.3f" % sample.seconds)
    check(settled >= 20, "bounded settled samples available")
    var file = FileAccess.open(output + "/motion.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"actions": actions, "samples": samples, "checks": evidence}, "  "))
    file.close()
    finish(0)

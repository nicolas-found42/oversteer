# Native regression: repeat settings changes without losing keyboard focus.
extends SceneTree
func _initialize():
    run.call_deferred()
func settle():
    for i in range(8):
        await process_frame
func button(action):
    var menu = root.find_child("Menus", true, false)
    for child in menu.get_children():
        if child is Button and not child.is_queued_for_deletion() and child.get_meta("ui_action", "") == action:
            return child
    return null
func run():
    root.add_child(load("res://main.tscn").instantiate())
    await settle()
    button("title_start").pressed.emit()
    await settle()
    button("options").pressed.emit()
    await settle()
    for action in ["units", "units", "units", "quality", "quality", "difficulty", "difficulty"]:
        button(action).grab_focus()
        button(action).pressed.emit()
        await settle()
        var focus = root.gui_get_focus_owner()
        var actual = focus.get_meta("ui_action", "") if focus else "none"
        print("FOCUS_AFTER_", action.to_upper(), "=", actual)
        if actual != action:
            quit(1)
            return
    quit(0)

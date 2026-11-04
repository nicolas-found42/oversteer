# Actual control/settlement checks only. No renderer, screenshots or race overrides.
extends "ui_hud_navigation.gd"
var case_name: String
var observations: Array = []
var baseline := {}

func snapshot() -> Dictionary:
    return JSON.parse_string(app.diagnostic_snapshot()).snapshot

func visible_controls() -> Array:
    var controls: Array = []
    for node in root.find_children("*", "Control", true, false):
        if node.is_queued_for_deletion() or not node.is_visible_in_tree():
            continue
        if node is Label or node is Button:
            var rect = node.get_global_rect()
            controls.append({"text": node.text, "action": node.get_meta("ui_action", ""),
                "rect": [rect.position.x, rect.position.y, rect.size.x, rect.size.y]})
    return controls

func receipt(label: String):
    observations.append({"label": label, "snapshot": snapshot(),
        "focus": focus_action(), "controls": visible_controls()})

func has_text(part: String) -> bool:
    for control in visible_controls():
        if part in control.text:
            return true
    return false

func finish(code: int):
    var file = FileAccess.open(output + "/forfeit.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"case": case_name, "exit_code": code,
        "logic_only": true, "rendered": false,
        "drivers": {"display": DisplayServer.get_name(), "audio": AudioServer.get_driver_name()},
        "checks": evidence, "observations": observations}, "  "))
    file.close()
    quit(code)

func press(action: String):
    var deadline = Time.get_ticks_msec() + 20000
    var control = button(action)
    while Time.get_ticks_msec() < deadline:
        var loading = root.find_child("Destination", true, false)
        control = button(action)
        if control and control.is_visible_in_tree() and (not loading or not loading.is_visible_in_tree()):
            break
        await process_frame
    check(control != null, "actual control exists: " + action)
    if control == null:
        return
    check(not control.disabled, "actual control enabled: " + action)
    if control.disabled:
        return
    control.grab_focus()
    control.pressed.emit()
    await settle()

func wait_live_race():
    var deadline = Time.get_ticks_msec() + 15000
    while Time.get_ticks_msec() < deadline:
        var state = snapshot()
        if state.screen == "Race" and state.race and state.race.elapsed > 0.05:
            return
        await process_frame
    check(false, "normal simulation reaches a live unfinished race")

func pause_race():
    await wait_live_race()
    await key(KEY_ESCAPE)
    check(snapshot().screen == "Paused", "Escape pauses the actual race")

func purchase_spare():
    await press("nav:career")
    await press("nav:dealer")
    await press("car:GT4_MINI0001")
    var before = snapshot()
    await press("buy")
    receipt("legitimate-second-car-purchase-confirmation")
    await press("confirm_yes")
    var bought = snapshot()
    check(bought.career.garage.size() == before.career.garage.size() + 1, "actual purchase adds one owned car")
    check(bought.career.garage.has("GT4_MINI0001"), "purchased MINI ownership exists")
    check(bought.career.cash == before.career.cash - 19500, "actual purchase pays catalog price")
    await press("nav:main")
    await press("nav:career")
    await press("nav:garage")
    await press("car:GT4_HOND0018")
    await press("nav:main")

func run():
    case_name = OS.get_cmdline_user_args()[1]
    check(DisplayServer.get_name() == "headless", "headless display required")
    check(AudioServer.get_driver_name() == "Dummy", "Dummy audio required")
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await press("title_start")
    var parts = case_name.split("_")
    var stake = parts[0]
    var action = parts[1]
    var commit = parts[2] == "commit"
    if stake == "pink":
        await purchase_spare()
    await press("nav:career")
    await press("career_events")
    await press("event:0")
    await press("start")
    check(snapshot().screen == "Grid", "career event reaches actual pre-race grid")
    var grid_before = snapshot()
    if stake != "none":
        # Rival 2's car is not either legitimately owned vehicle in this fixture.
        await press("rival:2")
        if stake == "pink":
            await press("offer_pink")
            check(focus_action() == "confirm_no", "pink offer initially focuses Cancel")
            receipt("pink-offer-consequence")
            await press("confirm_yes")
        else:
            await press("offer_cash")
        receipt("unaccepted-offer")
        check(snapshot().career == grid_before.career, "an unaccepted offer changes no career state")
        await press("offer_accept")
        var accepted = snapshot()
        check(accepted.race.bet_offer.status == "Accepted", "actual rival offer accepted")
        if stake == "cash":
            check(accepted.race.wager > 0, "accepted cash stake is nonzero")
            check(accepted.career.cash == grid_before.career.cash - accepted.race.wager, "accepted actual counter-stake deducted exactly once")
            check(not accepted.race.pink_slip, "cash acceptance does not stake a vehicle")
        else:
            check(accepted.race.pink_slip, "pink stake active")
            check(accepted.career.cash == grid_before.career.cash, "pink acceptance has no cash charge")
            check(accepted.career.garage == grid_before.career.garage, "pink acceptance retains ownership until settlement")
        receipt("accepted-stake")
    await press("grid_launch")
    await pause_race()
    baseline = snapshot()
    receipt("paused-before-action")
    await press("restart" if action == "restart" else "nav:main")
    if stake == "none":
        check(button("confirm_yes") == null, "no-wager action has no destructive confirmation")
        check(not has_text("FORFEIT STAKE"), "no-wager action has no stake-forfeit warning")
        receipt("no-wager-action-completed")
        var state = snapshot()
        check(state.career.cash == baseline.career.cash, "no-wager action preserves cash")
        check(state.career.garage == baseline.career.garage, "no-wager action preserves ownership")
        if action == "restart":
            check(state.race != null and state.race.wager == 0 and not state.race.pink_slip, "no-wager restart has no new stake")
        else:
            check(state.screen == "MainMenu" and state.race == null, "no-wager exit ends race")
        finish(0)
        return
    check(focus_action() == "confirm_no", "forfeit confirmation defaults to Cancel")
    check(has_text("You will forfeit"), "actual visible confirmation states forfeiture")
    check(has_text("without a new wager") if action == "restart" else has_text("This race ends when you leave"), "actual consequence text matches action")
    receipt("forfeit-confirmation")
    if not commit:
        await press("confirm_no")
        var cancelled = snapshot()
        check(cancelled.screen == "Paused", "cancel stays paused")
        check(cancelled.career == baseline.career, "cancel preserves all career state")
        check(cancelled.race == baseline.race, "cancel preserves race and active stake")
        receipt("cancelled-forfeit")
        finish(0)
        return
    var staked_car = baseline.race.racers[0].car_id
    await press("confirm_yes")
    var settled = snapshot()
    receipt("committed-forfeit")
    check(settled.career.cash == baseline.career.cash, "forfeit never deducts an accepted stake twice")
    check(settled.career.losses == baseline.career.losses + 1, "forfeit records exactly one career loss")
    if stake == "pink":
        check(not settled.career.garage.has(staked_car), "pink forfeit removes the exact raced vehicle")
        check(settled.career.garage.size() == baseline.career.garage.size() - 1, "pink forfeit removes exactly one vehicle")
        for car in baseline.career.garage:
            if car != staked_car:
                check(settled.career.garage.has(car), "pink forfeit retains spare vehicle: " + car)
        check(settled.career.vehicle_history[staked_car].pink_slip_losses == baseline.career.vehicle_history[staked_car].pink_slip_losses + 1, "exact vehicle records one pink-slip loss")
    else:
        check(settled.career.garage == baseline.career.garage, "cash forfeit preserves every owned vehicle")
    if action == "restart":
        check(settled.screen == "Race", "confirmed restart launches replacement race")
        check(settled.race.wager == 0 and not settled.race.pink_slip, "replacement race places no new bet")
        check(settled.race.bet_offer == null, "replacement race inherits no accepted offer")
        check(settled.race.racers[0].car_id == settled.selected_car, "replacement race uses still-owned selected car")
        check(settled.career.garage.has(settled.race.racers[0].car_id), "replacement driver owns its vehicle")
        await pause_race()
        await press("nav:main")
        check(button("confirm_yes") == null, "replacement race exits without a second stake warning")
    else:
        check(settled.screen == "MainMenu" and settled.race == null, "confirmed exit discards finished race context")
    await press("nav:career")
    await press("nav:main")
    var revisited = snapshot()
    check(revisited.career.cash == settled.career.cash, "later navigation adds no stake deduction")
    check(revisited.career.garage == settled.career.garage, "later navigation causes no second vehicle loss")
    receipt("post-settlement-navigation")
    finish(0)

# Headless logic only: existing spectate entry and actual rival controls, no image claims.
extends "ui_hud_navigation.gd"
var observations: Array = []

func dial_at(position: Vector2):
    var hud = root.find_child("RaceHUD", true, false)
    for child in hud.get_children():
        if child is ColorRect and not child.is_queued_for_deletion() and child.position.distance_to(position) < 0.1 and child.material is ShaderMaterial:
            return child.material
    return null

func run():
    var drivers = {"display": DisplayServer.get_name(), "audio": AudioServer.get_driver_name()}
    check(drivers.display == "headless" and drivers.audio == "Dummy", "headless display and Dummy audio required")
    var catalog := {}
    for car in JSON.parse_string(FileAccess.get_file_as_string("res://assets/game-content.json")).cars:
        catalog[car.id] = car.handling.redline
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await visual_ready()
    await create_timer(0.4).timeout
    await press("title_start")
    await press("nav:career")
    await press("career_events")
    # This existing handler has no current entry Button. Do not claim UI reachability.
    app.action("spectate")
    for i in range(1200):
        await process_frame
        var state = JSON.parse_string(app.diagnostic_snapshot())
        if state.snapshot.screen == "Race" and state.snapshot.race != null and state.snapshot.race.spectating:
            break
    await visual_ready()
    var before = JSON.parse_string(app.diagnostic_snapshot()).snapshot
    check(before.screen == "Race" and before.race.spectating, "existing spectate action entered spectator race")
    for i in range(1200):
        if before.race.countdown <= 0:
            break
        await process_frame
        before = JSON.parse_string(app.diagnostic_snapshot()).snapshot
    check(before.race.countdown <= 0, "canonical spectator observations after countdown")
    var selected: Array = []
    var redlines: Array = []
    for index in range(before.race.racers.size()):
        var car_id = before.race.racers[index].car_id
        if catalog.has(car_id) and not redlines.has(catalog[car_id]):
            selected.append(index)
            redlines.append(catalog[car_id])
        if selected.size() == 2:
            break
    if selected.size() < 2:
        var failure = FileAccess.open(output + "/spectator-tach.json", FileAccess.WRITE)
        failure.store_string(JSON.stringify({"status": "inconclusive", "reason": "Actual spectator grid has fewer than two distinct catalog redlines", "racers": before.race.racers, "catalog_redlines": redlines}, "  "))
        failure.close()
        finish(1)
        return
    for index in selected:
        await press("rival:" + str(index))
        await create_timer(0.3).timeout
        await process_frame
        # Before the next native process callback; no renderer or screenshot dependency.
        var state = JSON.parse_string(app.diagnostic_snapshot())
        var racer = state.snapshot.race.racers[index]
        var control = button("rival:" + str(index))
        check(control != null and control.text.begins_with(">"), "actual selected rival marker " + str(index))
        var tach = dial_at(Vector2(1386, 581))
        var speed = dial_at(Vector2(1494, 662))
        check(tach != null and speed != null, "actual tach and speed materials " + str(index))
        var expected = float(catalog[racer.car_id]) / 1000.0
        check(abs(float(tach.get_shader_parameter("steps")) - expected) < 0.001, "tach steps match selected rival " + str(index))
        check(abs(float(speed.get_shader_parameter("steps")) - 12.0) < 0.001, "speed scale remains twelve intervals")
        var expected_value = clamp(float(racer.rpm) / float(catalog[racer.car_id]), 0.0, 1.0)
        check(abs(float(tach.get_shader_parameter("value")) - expected_value) < 0.002, "tach needle matches actual selected rival snapshot")
        # JSON numbers are floats; Array.find uses strict Variant types.
        var order = state.snapshot.race.standings.map(func(value): return int(value))
        var node_diagnostics: Array = []
        for node in root.find_child("RaceHUD", true, false).get_children():
            if node is Label:
                node_diagnostics.append({"path": str(node.get_path()), "name": str(node.name), "text": node.text, "visible": node.visible, "queued": node.is_queued_for_deletion(), "position": [node.position.x, node.position.y]})
        var diagnostics = FileAccess.open(output + "/logic-checkpoint.json", FileAccess.WRITE)
        diagnostics.store_string(JSON.stringify({"selected": index, "standings": order, "race_countdown": state.snapshot.race.countdown, "race_elapsed": state.snapshot.race.elapsed, "position_label": state.hud.position, "hud_labels": node_diagnostics}, "  "))
        diagnostics.close()
        check(state.hud.position.text == str(order.find(index) + 1), "position follows selected rival canonical standing")
        for rival_index in range(state.snapshot.race.racers.size()):
            var dot = root.find_child("Hud_map_rival_" + str(rival_index), true, false)
            check(dot != null and dot.visible == (rival_index != index), "one map marker per rival " + str(rival_index))
        var map_area = Rect2(60, 660, 364, 364)
        var standings_area = Rect2(64, 171, 360, 149)
        for action in ["rival:0", "rival:1", "rival:2", "rival:3", "wager", "spectator_bet"]:
            var bounds = button(action).get_global_rect()
            check(not bounds.intersects(map_area) and not bounds.intersects(standings_area), "spectator control clear of map and standings " + action)
        var geometry = {"start_angle": tach.get_shader_parameter("start_angle"), "sweep_angle": tach.get_shader_parameter("sweep_angle"), "cover_center": tach.get_shader_parameter("cover_center"), "cover_radius": tach.get_shader_parameter("cover_radius")}
        for progress in [0.85, 0.9, 0.95, 1.0]:
            for radius in [0.96, 0.985]:
                var angle = float(geometry.start_angle) + float(geometry.sweep_angle) * progress
                var point = Vector2(cos(angle), sin(angle)) * radius
                check(point.distance_to(geometry.cover_center) > float(geometry.cover_radius) + 0.01, "tach redline geometry clear of front gauge")
        geometry.cover_center = [geometry.cover_center.x, geometry.cover_center.y]
        observations.append({"tach_geometry": geometry, "rival_index": index, "car_id": racer.car_id, "catalog_redline": catalog[racer.car_id], "tach_steps": tach.get_shader_parameter("steps"), "tach_value": tach.get_shader_parameter("value"), "rpm": racer.rpm, "position": state.hud.position.text, "standings": order, "selected_button": control.text, "race_elapsed": state.snapshot.race.elapsed, "ticks_usec": Time.get_ticks_usec()})
    var after = JSON.parse_string(app.diagnostic_snapshot()).snapshot
    check(before.career.cash == after.career.cash and before.career.garage == after.career.garage, "spectator selection preserves wallet and garage")
    var report = FileAccess.open(output + "/spectator-tach.json", FileAccess.WRITE)
    report.store_string(JSON.stringify({"status": "passed", "logic_only": true, "rendered": false, "drivers": drivers, "entry": "existing app.action(spectate), not a current entry Button", "observations": observations, "checks": evidence}, "  "))
    report.close()
    finish(0)

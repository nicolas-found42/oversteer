# Actual-control finance verification only; no render, texture reads or image output.
extends "ui_hud_navigation.gd"
var checkpoints: Array = []
var failed := false
var drivers := {}

func snapshot():
    return JSON.parse_string(app.diagnostic_snapshot()).snapshot

func check(condition: bool, label: String):
    evidence.append({"check": label, "passed": condition})
    print(label, "=", condition)
    if not condition:
        failed = true
        finish(1)

func finish(code: int):
    var file = FileAccess.open(output + "/finance.json", FileAccess.WRITE)
    file.store_string(JSON.stringify({"status": "passed" if code == 0 else "failed", "logic_only": true, "rendered": false, "drivers": drivers, "checks": evidence, "checkpoints": checkpoints}, "  "))
    file.close()
    quit(code)

func press(action: String):
    if failed:
        return
    var control = button(action)
    check(control != null and not control.disabled, "enabled actual control " + action)
    if control == null or control.disabled:
        return
    control.grab_focus()
    control.pressed.emit()
    await settle()

func note(label: String):
    checkpoints.append({"label": label, "snapshot": snapshot()})

func label_at(x: float, y: float):
    var menu = root.find_child("Menus", true, false)
    for child in menu.get_children():
        if child is Label and not child.is_queued_for_deletion() and child.position.distance_to(Vector2(x, y)) < 0.1:
            return child
    return null

func money(value: int) -> String:
    var digits = str(abs(value))
    var grouped = ""
    for i in range(digits.length()):
        if i > 0 and (digits.length() - i) % 3 == 0:
            grouped += ","
        grouped += digits[i]
    return ("-" if value < 0 else "") + "$" + grouped

func verify_cart():
    var state = snapshot()
    var total = 0
    for item in state.cart:
        total += int(item.cost)
    for row in range(3):
        var expected = [int(state.career.cash), total, int(state.career.cash) - total][row]
        var label = label_at(1436, 272 + row * 128)
        check(label != null and label.text == money(expected), "actual cart arithmetic row " + str(row))
    check(button("checkout").disabled == (state.cart.is_empty() or total > state.career.cash), "checkout availability matches actual cart and cash")
    for item in state.cart:
        var remove = button("cart_remove:" + item.id)
        if remove != null:
            var select = button("cart_select:" + item.id)
            var subtitle = label_at(80, select.position.y + 29)
            var name = label_at(80, select.position.y + 5)
            var price = label_at(280, select.position.y + 49)
            check(remove.position.y == select.position.y + 48 and select.size.y == 76, "Remove occupies lower line of 76px row")
            check(subtitle != null and name != null and price != null, "cart row labels exist")
            check(not remove.get_global_rect().intersects(subtitle.get_global_rect()) and not remove.get_global_rect().intersects(name.get_global_rect()) and not remove.get_global_rect().intersects(price.get_global_rect()), "Remove geometry disjoint from name subtitle and price")
    return total

func run():
    drivers = {"display": DisplayServer.get_name(), "audio": AudioServer.get_driver_name()}
    check(drivers.display == "headless" and drivers.audio == "Dummy", "headless and Dummy required")
    app = load("res://main.tscn").instantiate()
    root.add_child(app)
    await settle(12)
    await press("title_start")
    await press("nav:career")
    await press("nav:dealer")
    await press("car:GT4_MINI0001")
    var before_buy = snapshot()
    var catalog = JSON.parse_string(FileAccess.get_file_as_string("res://assets/game-content.json"))
    var mini_price = 0
    for car in catalog.cars:
        if car.id == "GT4_MINI0001":
            mini_price = int(car.price)
    check(mini_price > 0 and before_buy.career.cash >= mini_price, "actual Mini price affordable")
    await press("buy")
    check(focus_action() == "confirm_no", "purchase defaults to Cancel")
    await press("confirm_no")
    check(snapshot().career == before_buy.career, "purchase cancel preserves complete career")
    await press("buy")
    await press("confirm_yes")
    var purchased = snapshot()
    check(purchased.career.cash == before_buy.career.cash - mini_price and purchased.career.garage.has("GT4_MINI0001"), "purchase exact debit and ownership")
    check(purchased.career.vehicle_history.GT4_MINI0001.purchase_price == mini_price and purchased.career.vehicle_history.GT4_MINI0001.acquired_by == "Purchased", "purchase history reflects actual vehicle and cost")
    check(purchased.career.transactions[-1].kind == "BuyCar" and purchased.career.transactions[-1].amount == -mini_price, "purchase ledger records exact debit")
    note("purchased")
    await press("car:GT4_HOND0030")
    check(button("buy").disabled, "unaffordable vehicle purchase disabled")
    check(snapshot().career == purchased.career, "unaffordable preview preserves career")
    await press("nav:main")
    await press("nav:career")
    await press("nav:garage")
    await press("car:GT4_MINI0001")
    await press("vehicle_stats")
    var history_text = label_at(120, 330)
    check(history_text != null and history_text.text.contains("PURCHASE PRICE " + money(mini_price)) and history_text.text.contains("ACQUIRED BY Purchased"), "history control shows purchased vehicle facts")
    await press("stats_back")
    var before_sale = snapshot()
    await press("sell")
    check(focus_action() == "confirm_no", "sale defaults to Cancel")
    await press("confirm_no")
    check(snapshot().career == before_sale.career, "sale cancel preserves career and ownership")
    await press("car:GT4_HOND0018")
    await press("nav:custom")
    await press("custom_page:performance")
    for field in ["engine", "transmission", "suspension", "tyres"]:
        for stage in range(3):
            await press("upgrade:" + field)
    await press("nav:checkout")
    var unaffordable = snapshot()
    check(verify_cart() > unaffordable.career.cash and button("checkout").disabled, "actual staged cart is unaffordable")
    note("unaffordable-cart")
    await press("discard_cart")
    await press("confirm_yes")
    check(snapshot().cart.is_empty(), "discard empties cart without purchase")
    check(verify_cart() == 0 and button("checkout").disabled, "empty cart purchase disabled")
    await press("nav:custom")
    await press("custom_page:performance")
    await press("upgrade:engine")
    await press("upgrade:transmission")
    await press("nav:checkout")
    check(verify_cart() == 2000 and snapshot().cart.size() == 2, "two actual Stage1 upgrades total2000")
    var item = snapshot().cart[0]
    await press("cart_select:" + item.id)
    verify_cart()
    var remove_cost = int(item.cost)
    await press("cart_remove:" + item.id)
    check(verify_cart() == 2000 - remove_cost and snapshot().cart.size() == 1, "Remove subtracts exactly selected item")
    var checkout_before = snapshot()
    var total = verify_cart()
    await press("checkout")
    await press("confirm_no")
    check(snapshot().career == checkout_before.career and snapshot().cart == checkout_before.cart, "checkout cancel preserves installed state wallet and draft")
    await press("checkout")
    await press("confirm_yes")
    var checked_out = snapshot()
    check(checked_out.cart.is_empty() and checked_out.career.cash == checkout_before.career.cash - total, "checkout commits exact quoted debit and clears cart")
    var committed_item = checkout_before.cart[0]
    check(checked_out.career.garage[committed_item.car_id][committed_item.field] == checkout_before.selected_customization[committed_item.field], "checkout installs actual remaining selected upgrade")
    check(checked_out.career.vehicle_history.GT4_HOND0018.total_spent == checkout_before.career.vehicle_history.GT4_HOND0018.total_spent + total, "checkout history includes actual cost")
    check(checked_out.career.transactions[-1].kind == "Customization" and checked_out.career.transactions[-1].amount == -total, "checkout ledger records actual quoted debit")
    note("checkout-committed")
    await press("car:GT4_MINI0001")
    var sale_before = snapshot()
    await press("sell")
    await press("confirm_yes")
    var sold = snapshot()
    check(not sold.career.garage.has("GT4_MINI0001") and sold.career.cash == sale_before.career.cash + mini_price / 2, "actual sale removes ownership and credits half base price")
    check(sold.career.vehicle_history.GT4_MINI0001.sales == 1, "sale retained in vehicle history")
    check(sold.career.transactions[-1].kind == "SellCar" and sold.career.transactions[-1].amount == mini_price / 2, "sale ledger records actual proceeds")
    check(button("sell").disabled, "last career vehicle cannot be sold")
    note("sale-committed")
    check(not failed, "all bounded finance logic checks passed")
    finish(1 if failed else 0)

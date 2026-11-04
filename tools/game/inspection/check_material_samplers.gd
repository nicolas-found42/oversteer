extends SceneTree
## Exercise actual in-race paint overrides without generating screenshots.

func _initialize():
    call_deferred("run")

func nodes(node: Node) -> Array[Node]:
    var result: Array[Node] = [node]
    for child in node.get_children():
        result.append_array(nodes(child))
    return result

func run():
    var app = load("res://main.tscn").instantiate()
    root.add_child(app)
    var waited := 0
    while app.diagnostic_input_frame() < 165:
        await process_frame
        waited += 1
        if waited > 18000:
            push_error("Sampler check did not reach active race")
            quit(1)
            return
    var filters := ["filter_nearest", "filter_linear", "filter_nearest_mipmap",
        "filter_linear_mipmap", "filter_nearest_mipmap_anisotropic", "filter_linear_mipmap_anisotropic"]
    var failures: Array = []
    var observations: Array = []
    for node in nodes(app):
        if not node is MeshInstance3D or node.mesh == null:
            continue
        for surface in node.mesh.get_surface_count():
            var source = node.mesh.surface_get_material(surface)
            var active = node.get_active_material(surface)
            if not source is StandardMaterial3D or not active is ShaderMaterial:
                continue
            var code: String = active.shader.code
            if not "uniform sampler2D paint_mask" in code:
                continue
            var repeat_hint := "repeat_enable" if source.get_flag(BaseMaterial3D.FLAG_USE_TEXTURE_REPEAT) else "repeat_disable"
            var filter_hint: String = filters[source.texture_filter]
            var row := {"node":str(node.get_path()),"material":source.resource_name,
                "repeat":repeat_hint,"filter":filter_hint,"passed":true}
            for sampler in ["base_texture", "paint_mask"]:
                var declaration: String = code.split("uniform sampler2D " + sampler)[1].split(";")[0]
                if not repeat_hint in declaration or not filter_hint in declaration:
                    failures.append({"material":source.resource_name,"sampler":sampler,
                        "declaration":declaration,"expected_repeat":repeat_hint,"expected_filter":filter_hint})
                    row.passed = false
            observations.append(row)
    var report := {"passed":not observations.is_empty() and failures.is_empty(),
        "compared":observations.size(),"failures":failures,"observations":observations}
    var args := OS.get_cmdline_user_args()
    for i in args.size()-1:
        if args[i] == "--sampler-report":
            var file := FileAccess.open(args[i+1], FileAccess.WRITE)
            file.store_string(JSON.stringify(report, "  "))
    print("SAMPLER_CHECK compared=%d failures=%d" % [observations.size(), failures.size()])
    quit(0 if report.passed else 1)

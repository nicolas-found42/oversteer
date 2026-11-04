# Vehicle inspection tools

Research date: 2026-11-03 (America/New_York). Scope: native Godot vehicle inspection on Apple Silicon, with reproducible images and diagnostics. Recommendations below are engineering judgment; linked API behavior comes from primary sources. No runtime, application preferences, or dependencies were changed during this research.

## Platform and version evidence

Read-only local checks found macOS 27.0.1 (26A434), arm64; `/usr/bin/gpucapture`; Blender 5.2.2 LTS at `/opt/homebrew/bin/blender`; and `xcode-select -p` pointing to `/Library/Developer/CommandLineTools`. This does not establish that a full Xcode installation is present. The repository pins `godot = "=0.5.5"` with `api-4-7` in `crates/oversteer-godot/Cargo.toml`; its existing integration note pins Godot 4.7.2. Preserve those pins. godot-rust distinguishes compile-time API version from runtime version and requires runtime >= API version. [Compatibility policy](https://godot-rust.github.io/book/toolchain/compatibility.html), [Godot 4.7.2 release](https://github.com/godotengine/godot/releases/tag/4.7.2-stable), [gdext 0.5.5 release](https://github.com/godot-rust/gdext/releases/tag/v0.5.5).

## Use the runtime as the visual authority

Keep final inspection captures in the actual Godot renderer and presentation path. Blender is useful for independent geometry/material diagnosis, but a Blender render cannot establish Godot transparency, import, lighting, or shader correctness.

Recommended bounded matrix: eight azimuths at 45-degree intervals, at a low side elevation and an elevated three-quarter elevation; add a near-top view and an underside view when geometry permits. For each, capture three explicit lighting presets: neutral soft illumination, strong directional grazing light, and low-key/backlight. The latter two reveal normal discontinuities, glass sorting and silhouette holes. Include straight front, rear and both side views. Keep the whole vehicle in frame with a small border, then add detail images for glass, wheels and suspect panels. These view counts and light presets are recommendations, not Godot requirements.

Frame the transformed mesh bounds, not a fixed guessed distance. Test all eight world AABB corners against camera projection and viewport bounds, reject points behind the camera, and record the resulting pixel margins. Store the camera transform, projection, FOV/orthographic size, near/far planes, viewport dimensions and vehicle bounds beside every image. Camera3D provides the projection, transform, frustum and projection helpers. [Camera3D API](https://docs.godotengine.org/en/stable/classes/class_camera3d.html).

Do not read pixels immediately after changing a camera or light. Godot documents waiting for `RenderingServer.frame_post_draw` before `Viewport.get_texture().get_image().save_png(...)`. Use a short warmup for temporal effects and shader compilation, then associate diagnostics with the same capture identifier. A rendered viewport is required; a headless import/logic smoke test alone is not a visual validation. [Viewport capture example](https://docs.godotengine.org/en/stable/classes/class_viewport.html#class-viewport-method-get-texture), [frame_post_draw](https://docs.godotengine.org/en/stable/classes/class_renderingserver.html#class-renderingserver-signal-frame-post-draw).

## Per-capture diagnostic contract

Recommended JSON companion fields:

- Identity: vehicle model, asset path/hash, build/commit, Godot version, rendering method and driver, capture ID, elapsed frame and physics tick.
- Camera: transform and target, projection parameters, viewport size, bounds and projected corner coordinates; distinguish framing failure from missing mesh.
- Lighting: active environment, background, ambient/reflected light sources, tone mapping/exposure, sun direction, energy and shadow flags. Fixed exposure makes lighting comparisons easier to interpret.
- Geometry/materials: mesh path and transform, AABB, surface count, effective material class/path, material override precedence, shader identity and parameters; texture path/dimensions, transparency, albedo alpha, culling, metallic, roughness and normal settings. Record unresolved materials explicitly rather than treating their absence as opaque.
- Physics: vehicle transform, linear/angular velocity, wheel transforms, contact flags/positions/normals, suspension travel, steering and inputs from the actual simulation. Freeze or deterministically settle physics for static comparisons; record whether the capture is static or moving.
- Performance: process and physics time, draw calls, rendered primitives, objects, texture/buffer/video memory where available; include validity/build-mode qualifiers.

Godot's Performance monitors can lag by up to one second, and some return zero in release builds; they are contextual samples, not exact GPU timings for a particular PNG. Rendered primitive counts include additional passes. [Performance API](https://docs.godotengine.org/en/stable/classes/class_performance.html). RenderingServer also exposes viewport render information and rendering-device/backend queries; prefer its viewport-specific figures when comparing a dedicated inspection viewport. [RenderingServer API](https://docs.godotengine.org/en/stable/classes/class_renderingserver.html).

## Transparency and texture traps

Godot **4.7.2's tagged importer maps glTF `alphaMode: BLEND` to `TRANSPARENCY_ALPHA_DEPTH_PRE_PASS`**, and `MASK` to `TRANSPARENCY_ALPHA_SCISSOR`; `doubleSided` disables culling. Count depth-prepass material mode when reporting transparent materials. A report checking only straight alpha blend will miss imported glass. [Exact importer source, lines 3014–3031](https://github.com/godotengine/godot/blob/4.7.2-stable/modules/gltf/gltf_document.cpp#L3014).

The glTF alpha mode determines whether texture alpha participates: OPAQUE ignores it, MASK thresholds it, BLEND composites it. Base-color alpha combines texture and factor. Metallic/roughness textures use G for roughness and B for metallic; normal and occlusion textures carry data rather than display color. Audit channels and color handling before changing lighting. Shared material resources and global overrides can make a change affect multiple surfaces or vehicles; log the effective material on each surface. The spec also requires a renderer to handle double-sided normals appropriately. [glTF material specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#materials).

Do not globally convert every depth-prepass material to opaque. Confirm the intended material role using source alpha mode, alpha distribution and actual images. Compare opposing side views and backlight images for transparent ordering; separate cutouts from glass. Geometry normals, flipped winding, duplicate coincident shells and unintended transparent body materials can produce superficially similar defects.

For effective-material diagnostics, use `MeshInstance3D.get_active_material(surface)` rather than only `mesh.surface_get_material(surface)`: it accounts for instance and surface overrides. After a BaseMaterial3D downcast, read `get_transparency()`, `get_cull_mode()`, `get_depth_draw_mode()`, `get_albedo()`, `get_texture(TEXTURE_ALBEDO)`, normal enable/scale, metallic/roughness values and texture channels. Record texture resource paths and sizes. Treat ShaderMaterial separately: record its shader and parameter values, since BaseMaterial3D accessors do not describe it. [Effective material API](https://docs.godotengine.org/en/stable/classes/class_meshinstance3d.html#class-meshinstance3d-method-get-active-material), [BaseMaterial3D API](https://docs.godotengine.org/en/stable/classes/class_basematerial3d.html), [ShaderMaterial API](https://docs.godotengine.org/en/stable/classes/class_shadermaterial.html).

## Validate GLB before diagnosing renderer bugs

First useful addition: the official **`gltf-validator` npm package**, preferably in a dedicated tools directory or existing tool package with a lockfile. Its JS distribution avoids selecting a native executable architecture. `validateBytes(new Uint8Array(asset), options)` returns a report; persist the report and fail on `report.issues.numErrors > 0`, not merely a rejected promise. Supply `externalResourceFunction` for external buffers/images. Native CLI is another option: it recursively accepts directories, writes JSON reports and returns nonzero on validation errors. [Validator repository and CLI](https://github.com/KhronosGroup/glTF-Validator), [official Node API and examples](https://github.com/KhronosGroup/glTF-Validator/blob/main/node/README.md).

Validation detects schema/buffer/accessor/image problems and reports statistics; it does not certify attractive lighting, correct vehicle identity, intended transparency or Godot-specific results. Preserve warnings for review instead of hiding them automatically.

Read-only npm registry inspection on the research date returned `latest: 2.0.0-dev.3.10`. This is the official published latest tag but has a prerelease version name; do not describe it as a stable-semver release. A concrete isolated installation is `npm install --prefix build/tools --save-exact gltf-validator@2.0.0-dev.3.10`; preserve its lockfile and record the resolved version in reports. The official Node README documents npm installation. [npm package](https://www.npmjs.com/package/gltf-validator), [official installation instructions](https://github.com/KhronosGroup/glTF-Validator/blob/main/node/README.md#installation).

Second useful addition: **`@gltf-transform/cli`** for read-only `gltf-transform inspect vehicle.glb`, which exposes scene/mesh/material/texture statistics. Use its transformation commands only on copies after establishing a defect; optimization changes are outside an inspection pass. Check the package's current Node engine requirement before installation and pin the resolved version. [CLI documentation](https://gltf-transform.dev/cli), [actual repository](https://github.com/donmccurdy/glTF-Transform).

Khronos's Sample Viewer provides a separate PBR rendering comparison to distinguish malformed assets from Godot behavior. Its agreement is supporting evidence, not a replacement for the runtime captures. [Sample Viewer](https://github.com/KhronosGroup/glTF-Sample-Viewer). Khronos's own tools index and Awesome Godot were used for discovery; compatibility claims should always be checked in the individual project. [Khronos tools index](https://github.com/KhronosGroup/glTF), [Awesome Godot](https://github.com/Calinou/awesome-godot).

## Blender without stealing focus

Blender is already installed; no additional installation is needed for background audits. Use `blender --background --factory-startup --python-exit-code 1 --python audit.py -- ...`. The script can import the GLB and dump mesh bounds, polygon/material assignments, UV layers, image metadata and node values. Store derived files outside source assets. For a prepared scene, set output and renderer options before the render trigger: `blender --background inspection.blend --render-output /tmp/inspection_ --render-format PNG --render-frame 1`. [Blender 5.2 CLI arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html).

Cycles accepts `--cycles-device METAL` after the `--` separator; `--cycles-print-stats` adds render memory/time statistics. `--profile-gpu` emits Trace Event Format data. Background mode avoids opening a window. Argument order matters because loading a blend file can replace prior scene settings. These diagnostics describe Blender's renderer, not Godot performance. [Blender CLI render/device options](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html#cycles-render-options).

## Metal capture and macOS profiling

**November 4 follow-up:** the signature limitation described below was fixed
with a separate diagnostic engine copy, and both capture and static CLI trace
inspection succeeded. Full Xcode is optional: this host also has `gpudebug`.
See [the source-backed remedy and executed evidence](METAL_CAPTURE_LIMITATION.md).
The current screenshot standard is 36 per run with an absolute maximum of 50;
the earlier exploratory matrix recommendations are superseded by
[the inspection guide](../../tools/game/inspection/README.md).

**Use installed `gpucapture` first for a bounded Metal workload capture.** Apple's repository says it ships with macOS 27+. Local `man gpucapture` confirms the installed syntax uses plural `boundaries`. Launch the target with `MTL_CAPTURE_ENABLED=1`; it cannot be enabled retroactively on a process launched without it. [Apple tool guidance](https://github.com/apple/game-porting-toolkit/blob/main/game-porting-skills/skills/using-gpucapture/SKILL.md).

```sh
# Launch target with MTL_CAPTURE_ENABLED=1 using its existing non-focusing launcher.
gpucapture list
gpucapture boundaries --pid PID
gpucapture start --pid PID --boundary BOUNDARY_ID --count 1 --output /absolute/path/inspection.gputrace
```

Select the actual PID and listed layer boundary for a full presented-frame capture. Device boundaries represent command-buffer work, which need not equal an entire frame. Verify the trace exists and record its size. Local man page is authoritative for the installed version. Capture instrumentation affects timings, so benchmark ordinary runs separately.

Local follow-up: launching the pinned Godot with `MTL_CAPTURE_ENABLED=1` made it
appear in `gpucapture list`, but the tool marked it **non-debuggable** and refused
boundary capture. The installed tool requires the `com.apple.security.get-task-allow`
entitlement on macOS. No GPU trace was captured. If a GPU trace is needed, prepare
and identify a separately signed diagnostic engine copy; do not silently replace
the pinned engine or claim the resulting trace belongs to the shipping signature.
This limitation does not prevent native Metal screenshots or scene diagnostics.

For deeper inspection, Apple's Metal debugger supports GPU trace analysis and Xcode frame capture. Full Xcode is the useful optional installation if unavailable; the selected Command Line Tools path alone cannot establish Metal debugger availability. GUI launch/analysis should wait until focus changes are acceptable. Programmatic `MTLCaptureManager` is a fallback when CLI capture is unavailable; it requires application integration and should not be introduced merely to collect routine PNGs. [Xcode capture](https://developer.apple.com/documentation/xcode/capturing-a-metal-workload-in-xcode), [programmatic capture](https://developer.apple.com/documentation/xcode/capturing-a-metal-workload-programmatically), [Metal debugger](https://developer.apple.com/documentation/xcode/metal-debugger).

Do not install RenderDoc for this native macOS Metal path: its official support matrix lists Windows/Linux/Android and graphics APIs including Vulkan/OpenGL/D3D, without macOS/Metal. Use it only for a separate supported-platform reproduction. [RenderDoc support matrix](https://github.com/baldurk/renderdoc#api-support).

## Recommended order

1. Extend the existing runtime capture path with the bounded camera/light matrix and paired JSON; verify full-car projected bounds and actual PNGs.
2. Install/use official glTF Validator and retain reports for the inspected roster. Add glTF Transform inspection only when detailed asset statistics help.
3. Use installed Blender background mode for asset-level ambiguities; compare with Khronos Sample Viewer if import/render differences remain.
4. Capture one representative bad frame with installed gpucapture after relaunching with capture enabled. Install full Xcode only when GPU trace analysis is needed.

Research limits: no tool installation, GPU capture, screenshot run or full-roster validation was performed by this research agent. This note verifies documentation and local availability, not successful operation of a new capture pipeline.

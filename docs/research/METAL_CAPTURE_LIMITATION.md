# Metal capture: Godot signing limitation and diagnostic alternatives

Research date: 2026-11-03. Scope: Apple Silicon macOS, pinned Godot 4.7.2, native Metal renderer. This research changed only this note; it did not re-sign or launch an engine. See [vehicle inspection context](VEHICLE_INSPECTION_TOOLS.md).

## Finding and recommended fix

The reported `gpucapture list` result (Godot visible but non-debuggable) is consistent with the official editor's distribution signature. `MTL_CAPTURE_ENABLED=1` loads capture instrumentation, but does not grant an external debugger access. Godot explicitly documents that signed official editors lack `com.apple.security.get-task-allow` because that entitlement prevents notarization; its documented remedy is local re-signing. Apple separately explains that even a debugger with its own debugger entitlement cannot obtain task ports for protected targets missing get-task-allow. [Godot macOS debugging](https://docs.godotengine.org/en/stable/engine_details/development/debugging/macos_debug.html), [Apple debugger entitlement](https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.security.cs.debugger).

**Smallest proposed remedy:** create an explicitly named diagnostic copy of the pinned Godot bundle, preserve its original entitlements, add get-task-allow, and ad-hoc sign that copy. Keep the original path, bytes and signature intact. This follows Godot's supported debugging workflow with a narrower entitlement change than copying every permission in its example. It is a proposal, not a successful local capture result.

Example preparation commands (replace the source path with the verified pinned bundle; the destination must not already exist):

```sh
SOURCE_GODOT_APP='/absolute/path/to/pinned/Godot.app'
DIAGNOSTIC_ROOT="$(mktemp -d /tmp/oversteer-metal-diagnostic.XXXXXX)"
DIAGNOSTIC_GODOT_APP="$DIAGNOSTIC_ROOT/Godot-diagnostic.app"
/usr/bin/shasum -a 256 "$SOURCE_GODOT_APP/Contents/MacOS/Godot"
/usr/bin/codesign --display --entitlements - --xml "$SOURCE_GODOT_APP" > "$DIAGNOSTIC_ROOT/entitlements.plist"
# Stop and inspect if extraction fails or the plist is empty/invalid.
/usr/bin/plutil -lint "$DIAGNOSTIC_ROOT/entitlements.plist"
/usr/bin/ditto "$SOURCE_GODOT_APP" "$DIAGNOSTIC_GODOT_APP"
/usr/bin/plutil -replace com.apple.security.get-task-allow -bool YES "$DIAGNOSTIC_ROOT/entitlements.plist"
/usr/bin/codesign -s - --deep --force --options=runtime --entitlements "$DIAGNOSTIC_ROOT/entitlements.plist" "$DIAGNOSTIC_GODOT_APP"
/usr/bin/codesign --verify --deep --strict --verbose=2 "$DIAGNOSTIC_GODOT_APP"
/usr/bin/codesign --display --entitlements - --xml "$DIAGNOSTIC_GODOT_APP"
/usr/bin/shasum -a 256 "$SOURCE_GODOT_APP/Contents/MacOS/Godot"
```

Godot documents that exact `codesign` signing mode. Entitlement extraction is documented by Apple; the preservation/addition recipe is an engineering adaptation. If the original has no entitlements, explicitly create an XML plist containing the one required key rather than silently treating extraction errors as success. `--deep` follows Godot's editor-specific example; do not generalize it to arbitrary distribution signing. Preserve original signing/runtime evidence and report the diagnostic engine path/version/hash with the trace. [Godot recipe](https://docs.godotengine.org/en/stable/engine_details/development/debugging/macos_debug.html), [Apple entitlement inspection](https://help.apple.com/xcode/mac/current/en.lproj/dev298d7b2cb.html).

Then relaunch **the copy** through the established non-focusing project launcher with `MTL_CAPTURE_ENABLED=1` and the same project/scene/renderer arguments. Do not use `open` or switch applications merely to collect the trace. Select the actual PID and boundary returned by the installed CLI:

```sh
/usr/bin/gpucapture list
/usr/bin/gpucapture boundaries --pid ACTUAL_PID
/usr/bin/gpucapture start --pid ACTUAL_PID --boundary ACTUAL_BOUNDARY_ID --count 1 --output /absolute/output/inspection.gputrace
```

Acceptance checks: the copy is listed as debuggable; the intended presented-frame layer (or explicitly selected Godot scope) appears; capture exits successfully; the trace bundle exists and contains data; the pinned source hash remains unchanged. A device boundary captures command-buffer work and need not represent an entire frame. The local `man gpucapture` uses **`boundaries`**, despite a singular spelling in Apple's repository overview. It defines layer boundaries as successive drawable presentations, and scope boundaries as beginScope/endScope. [Apple capture guidance](https://github.com/apple/game-porting-toolkit/blob/main/game-porting-skills/skills/using-gpucapture/SKILL.md), local `man gpucapture` read during this research.

### Risks and boundaries

The diagnostic copy loses the original Developer ID signature/notarization identity and deliberately allows debugger access. Keep it local and disposable; never ship it or describe its signature as production-equivalent. Apple states get-task-allow can permit runtime code injection and rejects it during notarization. Do not disable SIP, alter system policies, add broad permissions, or re-sign the pinned original to work around this. Existing dynamic extension loading still needs verification under the preserved runtime entitlements. Gatekeeper approval is not established by successful `codesign --verify`. [Apple notarization and get-task-allow](https://developer.apple.com/documentation/security/resolving-common-notarization-issues).

## Programmatic capture alternative

Apple documents in-process `MTLCaptureManager` capture: enable `MetalCaptureEnabled` in Info.plist or (macOS 14+) `MTL_CAPTURE_ENABLED=1`; check `supportsDestination(.gpuTraceDocument)`; create a descriptor with the renderer's actual device/queue/scope, `.gpuTraceDocument` destination and an absolute `.gputrace` file URL; start capture before creating command buffers and stop after committing the intended work. Handle the returned error. This saves a file without requiring an Xcode GUI attachment. [Apple programmatic capture](https://developer.apple.com/documentation/xcode/capturing-a-metal-workload-programmatically), [MTLCaptureManager API](https://developer.apple.com/documentation/metal/mtlcapturemanager).

This must execute **inside the Godot child process using its real Metal device**, through carefully integrated native extension/engine code. A separate Swift/Objective-C helper creating its own Metal device does not capture another process's Godot commands. The in-process route is a plausible alternative to external attachment, but this research has not proven it works with this signed Godot binary or this gdext version; do not claim it bypasses every signing/instrumentation constraint. Avoid a new renderer or source rebuild until the diagnostic-copy route is tested.

Godot 4.7.2 already enables a capture-availability flag from the capture environment variables and creates a Metal capture scope labelled `Godot Frame`; that is not a documented GDScript API for saving a trace. [Tagged Metal context source](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/metal/rendering_context_driver_metal.cpp#L60-L65), [tagged device/scope source](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/metal/rendering_device_driver_metal.cpp#L2775-L2782).

## Awesome-list and linked-repository search

The requested GitHub discovery path was followed, then claims were checked against their owners:

- [Awesome Metal](https://github.com/adamnemecek/awesome-metal) links [iTerm2](https://github.com/gnachman/iTerm2) and [Satin](https://github.com/Hi-Rez/Satin). iTerm2 has a concrete in-process implementation: `triggerProgrammaticCapture:` sets `MTLCaptureDestinationGPUTraceDocument`, output URL and the actual frame device, checks `startCaptureWithDescriptor:error:`, then stops capture when its frame completes. This corroborates the programmatic pattern; it does not provide a Godot attachment bypass. [iTerm2 implementation](https://github.com/gnachman/iTerm2/blob/master/sources/MetalRenderer/iTermMetalDriver.m#L490-L507), [frame completion](https://github.com/gnachman/iTerm2/blob/master/sources/MetalRenderer/iTermMetalDriver.m#L2612-L2619).
- Satin's similarly named screen capture example uses **ScreenCaptureKit**, which records screen images rather than Metal API/resource traces. Installing it does not resolve missing get-task-allow. [Satin example](https://github.com/Hi-Rez/Satin/blob/main/Example/Example/Renderers/PostProcessing/ScreenCaptureRenderer.swift).
- [Awesome Godot](https://github.com/Calinou/awesome-godot) was searched for capture/debugging tools, and its linked official engine was inspected at the pinned tag. No direct Godot Metal entitlement workaround was established from its add-on listings. The official Godot debugging recipe above is the applicable primary source.

This was a targeted search of the lists and the relevant linked projects, not an exhaustive audit of every repository they list.

## Full Xcode is optional on this host

**Capture does not require installing full Xcode here:** Apple's gpucapture guidance says the CLI ships with macOS 27+, and `/usr/bin/gpucapture` plus its man page were read locally. **CLI analysis also has an installed path:** read-only discovery found `/usr/bin/gpudebug`, and its local man page describes trace browsing, pipeline/resources, texture/buffer extraction and replay. Apple's companion guidance says gpudebug also ships with macOS 27+. This corrects the older inspection note's implication that analysis requires full Xcode. [Apple gpucapture guidance](https://github.com/apple/game-porting-toolkit/blob/main/game-porting-skills/skills/using-gpucapture/SKILL.md), [Apple gpudebug guidance](https://github.com/apple/game-porting-toolkit/blob/main/game-porting-skills/skills/using-gpudebug/SKILL.md).

After a trace exists, use a bounded noninteractive command such as:

```sh
/usr/bin/gpudebug --oneshot -t /absolute/output/inspection.gputrace -q -c 'list' -c 'status'
```

Local man documentation says browsing is available while replay initializes; resource `fetch` requires a ready replayer. Do not call a trace readable until this succeeds. Full Xcode remains useful for the graphical Metal Debugger and Xcode-driven frame capture, not a prerequisite established by the installed CLI workflow. `xcode-select -p` selecting Command Line Tools does not prove whether Xcode.app is installed. [Apple Metal debugger](https://developer.apple.com/documentation/xcode/metal-debugger).

## Verification status

Verified by source/documentation and read-only local inspection: signing explanation, Godot-supported re-signing recipe, pinned engine capture setup, installed capture/debug CLI syntax, awesome-list links and iTerm2 implementation. Not verified here: re-signing, launching the diagnostic copy, successful external capture, programmatic capture in Godot, or replaying a produced trace. Native Godot PNG capture and per-scene diagnostics remain available independently of this GPU trace limitation.

### Implementation follow-up, November 4

The parent implementation subsequently verified the copy-only signing remedy.
`tools/game/metal_capture.py` preserves the source app/entitlements, adds
get-task-allow to a separate diagnostic copy, verifies its signature and records
both executable hashes. The pinned source hash remains
`c7cccbf8fb143e34e02fd6521e09be2c2b974f0d5db080b19071c9c570718ccf`.

`build/verification/pivot-metal-essential-smoke/` completed with six 1080p PNGs,
unchanged frozen game state, no focus-guard violation and a 501,873,964-byte
presented-frame trace. Its `metal-capture.json` records PID, exact layer-boundary
command, view/camera and scope. `gpudebug --oneshot` opened the trace and listed
2 command buffers, 17 encoders and 936 draw calls. This is actual capture/static
inspection evidence; successful resource replay or profiling is not claimed.

The inspection script now explicitly draws each settled viewport frame without
presentation and checks the post-draw signal before PNG capture. A prior probe
stalled while awaiting automatic draws and was terminated; it is not a passed
inspection run. The completed static standard produced exactly 36 PNGs across
three cars. Current captures reported drawable windows, so deliberately covered
window rendering/capture still requires a dedicated runtime check.

For GPU tracing when `window_can_draw` is false, the runner chooses the Godot
main queue and explicitly records that the result is one command buffer, not a
presented frame. Boundary selection is unit-tested; that covered-window fallback
has not yet been exercised on this host. It does not claim that queue capture is
equivalent to a full-frame layer capture. No new Xcode installation, system
security setting change or engine-source patch was needed.

## Follow-up: stalled screenshot waits after a successful trace

2026-11-04: the implementing agent reports that a separately signed copy now produces a readable trace (>471 MB), but the subsequent PNG sweep sometimes waits indefinitely for `frame_post_draw`. The successful trace is implementation evidence supplied by that agent, not a capture executed during this research.

The pinned Godot source does **not** establish an intentional render-loop shutdown when external capture stops. Its Metal submission path ends and immediately begins the `Godot Frame` capture scope when presenting; there is no capture-completion render-disable branch in that inspected path. Apple's `stopCapture` contract stops recording, with no promise that it changes Godot's loop. [Pinned Metal frame boundary](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/metal/rendering_device_driver_metal3.cpp#L337-L343), [Apple stopCapture](https://developer.apple.com/documentation/metal/mtlcapturemanager/stopcapture()). This rules out that explanation only in the inspected engine path; it does not exclude an instrumentation or driver fault.

There is a source-backed alternative explanation that should be checked before treating this as a capture fault: macOS occlusion. The pinned window delegate derives visibility from `NSWindowOcclusionStateVisible`; `can_any_window_draw()` uses that visibility; `Main::iteration` skips ordinary rendering when no window can draw (unless other resource-processing conditions apply). A process can therefore keep processing at high CPU while an await of a rendering-only signal never resumes. [Occlusion handler](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/macos/godot_window_delegate.mm#L387-L393), [draw eligibility](https://github.com/godotengine/godot/blob/4.7.2-stable/platform/macos/display_server_macos.mm#L2709-L2723), [main draw gate](https://github.com/godotengine/godot/blob/4.7.2-stable/main/main.cpp#L5077-L5103).

Narrow proposed workaround: for **each** screenshot warmup/render frame when `DisplayServer.window_can_draw()` is false, manually render with `RenderingServer.force_draw(false, frame_step)` on the main thread, with the existing intended frame step. `false` suppresses buffer presentation; the pinned viewport implementation still renders viewports but skips the screen blit. Do not call the default `force_draw()` (which presents), and do not assume one forced draw restarts future automatic drawing while the window stays occluded. Preserve the existing count of warmup frames and scene updates; a zero frame step is suitable only if that matches the intended static inspection policy. [Pinned viewport drawing](https://github.com/godotengine/godot/blob/4.7.2-stable/servers/rendering/renderer_viewport.cpp#L782), [presentation guard](https://github.com/godotengine/godot/blob/4.7.2-stable/servers/rendering/renderer_viewport.cpp#L980-L986), [main-thread requirement](https://github.com/godotengine/godot/blob/4.7.2-stable/servers/rendering/rendering_server_default.cpp#L443-L454).

Connect any one-shot completion observer **before** forcing the draw: single-threaded rendering executes `_draw` synchronously, and the post-draw signal can already have fired when `force_draw` returns. Do not issue `force_draw` and then blindly await the next post-draw signal. An exact linked-project precedent is godot-mcp-runtime PR #25, which implemented this occlusion branch with a completion flag in an Array (GDScript closures capture scalar locals by value). Its author explicitly marked on-Mac verification pending at publication; source analysis supports the approach, but it is not proof for this project's run. [Rendering implementation and signal](https://github.com/godotengine/godot/blob/4.7.2-stable/servers/rendering/rendering_server_default.cpp#L210-L230), [linked-project fix and verification limits](https://github.com/Erodenn/godot-mcp-runtime/pull/25).

Before adopting the workaround, log `DisplayServer.window_can_draw()`, `RenderingServer.is_render_loop_enabled()` and the current screenshot/warmup index immediately before the wait. If drawable eligibility is true and the loop is enabled, this occlusion explanation is unconfirmed; inspect a bounded process sample for a GPU fence/nextDrawable stall rather than altering scene behavior. Keep capture and screenshots in separate child runs as an available isolation strategy, using the same scene parameters, if only capture-instrumented processes stall. The existing 36 essential screenshots and hard 50-per-run budget need no expansion to investigate this.

### Capture boundary consequence of nonpresenting draws

`force_draw(false, ...)` is a screenshot workaround, not a guarantee of bounded **full-frame** external GPU capture. In the pinned Metal driver, the Godot capture scope's end/begin pair runs only when the submitted swapchain list is nonempty. Consequently both a Layer boundary and the existing `Godot Frame` scope may stop advancing during nonpresenting occluded rendering. A listed scope with count zero is insufficient evidence that it can bound a frame; choose an observed advancing Layer while drawable eligibility is true, with a bounded timeout and explicit unavailable result otherwise. Do not silently substitute a Device boundary and call it a complete frame. [Pinned scope gating](https://github.com/godotengine/godot/blob/4.7.2-stable/drivers/metal/rendering_device_driver_metal3.cpp#L330-L343), local `man gpucapture` boundary definitions.

The pinned CLI parser/help exposes `--gpu-profile` for task timing summaries and `--gpu-validation` for validation; these do not start/stop a `.gputrace` capture. No Metal trace start/stop switch was found in the inspected pinned parser. [Pinned help](https://github.com/godotengine/godot/blob/4.7.2-stable/main/main.cpp#L650-L661), [profile parser](https://github.com/godotengine/godot/blob/4.7.2-stable/main/main.cpp#L1982-L1984). An in-process capture descriptor could delimit nonpresenting work, but requires the integration described above and is outside the narrow CLI/signature remedy.

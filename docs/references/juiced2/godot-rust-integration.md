# Godot and Rust integration for the proposed reconstruction

Checked November 3, 2026. This refines the selected Godot direction for the final
implementation plan. It does not approve implementation. No engine installation,
compilation, native launch, asset import, benchmark, or game test was performed.
The earlier [comparison](rust-stack-research.md) recommended Bevy; that historical
recommendation must not override the user's subsequent Godot selection.

## Verified engine boundary

Use **Godot 4.7.2 stable + godot-rust/gdext 0.5.5**, pinned rather than floating.
GitHub's release records report August 18 and August 9, 2026 respectively. The
0.5.5 tagged manifest exposes `api-4-7`. Proposed dependency:
`godot = { version = "=0.5.5", features = ["api-4-7"] }`; the adapter builds as a
`cdylib` for `aarch64-apple-darwin`. This is a documented pairing to prove locally,
not an observed successful build. The compiled API and runtime version are
separate; do not accidentally compile against an older default API.
[Godot release](https://github.com/godotengine/godot/releases/tag/4.7.2-stable),
[gdext release](https://github.com/godot-rust/gdext/releases/tag/v0.5.5),
[tagged features](https://github.com/godot-rust/gdext/blob/v0.5.5/godot/Cargo.toml),
[compatibility policy](https://godot-rust.github.io/book/toolchain/compatibility.html).

Keep Rust outside the Godot resource tree; copy the built extension into the
project for import/export. A proposed `.gdextension` contract is:

```ini
[configuration]
entry_symbol = "gdext_rust_init"
compatibility_minimum = "4.7"

[libraries]
macos.debug.arm64 = "res://bin/debug/liboversteer_godot.dylib"
macos.release.arm64 = "res://bin/release/liboversteer_godot.dylib"
```

Names are proposed, not existing files. The book documents the `arm64` tags,
`cdylib`, and entry symbol. With Cargo's explicit target, the build output is
`target/aarch64-apple-darwin/{debug,release}/liboversteer_godot.dylib` before the
copy. Export cannot use `res://../rust/target/...`; its library must be inside
`res://`. Set extension minimum to the chosen API, rather than copying the
book's older 4.1 example. Editor hot reload is optional, not an acceptance need.
[gdext setup and export paths](https://godot-rust.github.io/book/intro/hello-world.html).

Proposed `project.godot` rendering settings are:

```ini
[rendering]
renderer/rendering_method="forward_plus"
rendering_device/driver.macos="metal"
```

Forward+ and Mobile both support Metal. Forward+ is the initial visual proof
choice; Mobile is a later measured option if the budget requires it. The macOS
Metal driver is native on Apple Silicon, whereas Vulkan uses MoltenVK. Record
`RenderingServer.get_current_rendering_method()` and
`get_current_rendering_driver_name()` at startup: settings alone do not establish
the active backend because fallback and CLI overrides exist.
[renderer comparison](https://docs.godotengine.org/en/stable/tutorials/rendering/renderers.html),
[settings and runtime checks](https://docs.godotengine.org/en/stable/classes/class_projectsettings.html).

## Proposed minimal module contracts

These are design choices, not claims that Godot supplies recovered game rules.
Start with one ordinary Rust game-core library and one GDExtension adapter; keep
logical modules inside the core rather than creating a crate per feature.

| Owner | Input → output and boundary |
| --- | --- |
| Rust simulation core | Recovered vehicle parameters, input, explicit original interval and ordered contact data → next authoritative state and telemetry. Own numerical types and every recovered stage side effect. No Godot object, scene, timer or automatic solver dependency. |
| Rust rules modules | Race samples/events and explicit game state → scoring, AI/DNA/spooking, career/wager/unlock transitions and presentation events. Recover native rules where possible; label adaptations and unresolved branches. |
| Rust Godot adapter | Read device events, dispatch core commands, execute one explicit simulation schedule, and publish snapshots to nodes/UI/audio. Translate coordinates/units once. Presentation interpolation must not feed interpolated state back into simulation. |
| Godot resources | Declarative scenes, mesh/material/texture/audio/font resources, UI layout, animation and shader assets. Rust owns game behavior and signal callbacks. No GDScript gameplay layer is required. Shader code is rendering glue, not a second rules implementation. |
| Offline preparation | Recovered non-car content and permitted donor cars → normalized GLBs, textures, collision data and provenance/variant sidecars. No game-image extraction or source catalog dependency in the exported app. |
| Rust persistence | Versioned serializable game/settings structures → JSON under a resolved writable user directory. Persist stable IDs and values, never engine objects. |

The core must preserve recovered PPC float semantics where established, derivative
ordering, contact ordering, stage commits and local interval subdivision. Do not
replace the reference clock with a nominal Godot physics tick or collapse the
stateful RK4 into a textbook integrator. Godot schedules the adapter; the recovered
model determines numerical stepping. Full original update cadence and contact
response remain recovery gates, not choices to hide in engine defaults.
[handling decision](../../adr/0002-recover-reference-handling-before-adaptation.md),
[static recovery findings](../../../artifacts/juiced2-recovery/recompiled-handling/FINDINGS.md).

## Collision seam

**Propose Parry query-only geometry inside Rust** because the same contacts can
then be exercised by ordinary headless core tests without a Godot process. Use
one normalized collision representation with stable object/triangle identities;
retain original surface attributes and reference ordering. The exact dependency
version must be locked and compiled in the first proof; 0.31.1 was the candidate
in the previous report, not a demonstrated compatible dependency set.
[Parry's stated geometric-query scope](https://www.parry.rs/).

Godot `PhysicsDirectSpaceState3D` is a viable alternative: it exposes ray, shape,
closest-point and contact-related queries. It avoids maintaining a separate query
world, but ties those tests to an engine physics space and requires Godot-side
shape/transform synchronization. Neither backend establishes original road
sampling or wall/car response. Query results must be transformed and ordered by
recovered semantics, not accepted in incidental backend order. Do not integrate
the same car again with `VehicleBody3D`, `RigidBody3D`, or a stock vehicle solver.
[Godot query API](https://docs.godotengine.org/en/stable/classes/class_physicsdirectspacestate3d.html).

## Assets, customization, UI, input and audio

Use Godot's imported scenes/resources for prepared GLBs. The tagged
`GLTFDocument` supports named material extensions and extension registration;
its built-in supported-extension list does **not establish**
`KHR_materials_variants` preservation. Other extension classes can add support,
so absence from this one list is not proof that every importer path rejects it.
Conservatively normalize donor variants offline into explicit materials plus a
primitive/material selection sidecar. Verify actual colors/textures/alpha,
wheel pivots, axes, units, LODs and kit sockets for all 30 cars. GLB import is not
customization compatibility.
[tagged GLTFDocument](https://github.com/godotengine/godot/blob/4.7.2-stable/modules/gltf/gltf_document.cpp#L6967).

Use `ShaderMaterial` with a spatial PBR shader for paint/finish, paint-only mask
and composed vinyl texture, preserving separate glass/trim materials. Rust owns
vinyl layer descriptions, edits, transforms, ordering and persistence. Composite
on changes, then upload a texture; start without a live compositor framework.
This is a proposed technique requiring seam/mirrored-UV/transparent-glass proof,
not a supplied Godot vinyl editor. Duplicate mutable per-car material resources
so modifying one car cannot recolor every instance.
[ShaderMaterial sharing and parameters](https://docs.godotengine.org/en/stable/classes/class_shadermaterial.html),
[spatial shader outputs](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/spatial_shader.html).

Use Godot Control scene layouts for menus/HUD and Rust handlers for every
transition. `InputMap` supports runtime action-event replacement and deadzones;
Rust implements remapping capture, conflict policy, saved bindings, UI focus and
reconnect behavior. Use built-in audio buses and players first: positional
players expose pitch, volume and playback, sufficient building blocks for
family-shared RPM/load loops and Rust-controlled crossfades; tuning and recovered
speech/music remain content work. No extra runtime UI, input or audio framework
is justified before a measured shortfall.
[Control UI](https://docs.godotengine.org/en/stable/classes/class_control.html),
[InputMap](https://docs.godotengine.org/en/stable/classes/class_inputmap.html),
[AudioStreamPlayer3D](https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer3d.html).

Resolve `user://` through Godot to a filesystem path for Rust save I/O; it is
writable in exports, unlike project resources. Use serde/serde_json, explicit
schema version, temporary-write/replace and a recovery copy, then verify actual
interruption behavior. A separate directories crate is unnecessary if Godot
already supplies the destination.
[data paths](https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html).

## Build, proof and delivery gates after approval

The editor binary inside `Godot.app/Contents/MacOS/Godot` supports command-line
import/export. Proposed commands use a future project path, not an existing one:

```sh
cargo test -p oversteer-core
cargo build -p oversteer-godot --target aarch64-apple-darwin --release
"$GODOT_BIN" --headless --path godot --import
"$GODOT_BIN" --headless --path godot --export-release "macOS" dist/Oversteer.app
```

The export preset and destination directory must exist, matching export templates
must be installed, and release dylib must already be copied into `res://bin`.
Headless import/export does not prove Metal rendering, sound or device behavior.
The headless engine runs adapter checks separately from ordinary Rust tests.
[CLI requirements](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html).

Required proofs are: load the pinned ARM64 extension in editor and export; log
native Metal in a windowed release; inspect representative cars from each donor
then all 30; demonstrate independent per-car paint/vinyl/wheel/compatible-kit
changes and reload; verify ordered RK4/contact fixtures against address-bound
recovery evidence; exercise circuit/drift, AI, wager settlement and saved progress;
remap/reconnect keyboard/gamepad; verify positional audio and engine-loop changes.
No whole-vehicle golden trajectory is currently established merely by static
recovery, so report numerical coverage precisely.

Export an ARM64 macOS preset with all prepared resources and extension included.
Godot's macOS export documents architecture selection, `.app` packaging and
signing/notarization options; an engine export alone does not prove a movable,
self-contained app. Inspect Mach-O slices and linked dylibs, move the app away
from the checkout, launch from Finder offline without tools/source cache, and
verify saves stay outside the bundle. Measure actual 1920×1080 rendering at
60 fps (16.67 ms budget) on the agreed M5 Pro with representative AI/effects/audio;
this remains a target, not a measured result.
[macOS export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html).

Before bulk content work, unresolved gates are the local pinned-engine/extension
pair, real donor material/variant handling, original time/contact semantics,
recoverability and coverage of non-car assets/rules, and native performance.
These are proof tasks under the selected engine, not a request to approve an
engine choice again. The final plan still requires explicit implementation approval.

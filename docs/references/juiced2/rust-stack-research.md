# Rust stack research for the Juiced 2 reconstruction

**Current decision:** the user explicitly selected **Godot 4.7.2 + gdext 0.5.5**
after this comparison. [ADR-0005](../../adr/0005-use-godot-and-rust.md) supersedes
the Bevy recommendation below. The comparison is retained as research history;
use the [Godot integration note](godot-rust-integration.md) for the current plan.

Research date: November 3, 2026. Recommendation for planning; implementation and
final plan approval remain pending. No engine was installed, built, benchmarked,
or tested against these GLBs during this investigation.

## Recommendation

Choose **Bevy 0.20.1, using its conventional raster PBR renderer over wgpu/Metal,
with the recovered handling in an independent Rust library**. Add Parry for
geometric collision queries, not replacement vehicle dynamics. Keep runtime UI,
input and initial audio inside Bevy; use Blender and an offline asset conversion
step for content. This is the best overall fit for the stated Rust reconstruction,
not a claim that Bevy has the most complete editor or will automatically reproduce
the reference game.

The deciding tradeoff is ownership of the recovered numerical simulation and
custom car materials inside one Rust application, while retaining ready-made 3D,
asset, UI, input and audio infrastructure. Bevy's tagged renderer explicitly uses
wgpu 30 with Metal enabled. Its material extension example modifies the existing
PBR shader rather than requiring a new renderer. These are documented integration
points; their suitability for this project's actual assets remains an inference
until the proof below. [Renderer manifest](https://github.com/bevyengine/bevy/blob/v0.20.1/crates/bevy_render/Cargo.toml),
[extended material example](https://bevy.org/examples/shaders/extended-material/).

**Godot 4 + Rust is the strongest alternative.** Its integrated scene/UI editor and
export tooling are a real advantage for this content-heavy game. It is eligible:
Rust gameplay through GDExtension satisfies “implement the game in Rust”; the
accepted constraints do not require an engine itself written entirely in Rust.
I still prefer Bevy because a Rust numerical port, data pipeline and headless
verification are central here, and Bevy avoids a second object/FFI boundary for
the game layer. That is an engineering judgment, not a measured performance
penalty against Godot. If editor-led visual authoring becomes the dominant
workflow, Godot would be the reason to reopen this recommendation.
[Godot features](https://docs.godotengine.org/en/stable/about/list_of_features.html),
[godot-rust](https://godot-rust.github.io/).

## Scope and evidence boundary

The target is a native Apple Silicon, offline, self-contained macOS app: full 3D
tracks/cars, the accepted 30 vehicles, complete agreed single-player career and
quick race, garage/dealer, paint/vinyl/wheels/compatible kits, AI, wagers/pink
slips, drift and other evidenced events, English UI/speech and remappable keyboard
and conventional gamepad. The initial performance checkpoint is 1920×1080 at
60 fps on the user's M5 Pro, 48 GB, 20 GPU cores. This is a target, not a result.
See the [interview](../../design/JUICED2_REBUILD_INTERVIEW.md),
[glossary](../../../GLOSSARY.md) and
[platform decision](../../adr/0001-target-apple-silicon-only.md).

The current sprite pipeline does not establish a usable real-time 3D material or
customization pipeline. It retains provenance and corrective rules worth reusing,
but its emission/AO bake is a presentation choice. Some donor materials are
incomplete, wheels are not universally separable, and customization geometry is
not established. [Existing model pipeline](../../../tools/carmodels/README.md).

Handling recovery is concrete but incomplete: the latest findings establish a
dedicated vehicle RK4 with stateful stage commits, capped local interval
subdivision, tyre-response initialization and several force/drivetrain equations.
Upstream clock units/cadence, complete contact-blending state, traction-control
consumption and math-helper identification remain open. Do not replace these with Bevy timing defaults,
Rapier's vehicle controller, Godot VehicleBody3D, or invented arcade dynamics.
Collision queries alone cannot recover collision response. [Recovery findings](../../../artifacts/juiced2-recovery/recompiled-handling/FINDINGS.md),
[handling decision](../../adr/0002-recover-reference-handling-before-adaptation.md).

## Current versions actually checked

These are source/release observations on the research date, not a tested lockfile.
GitHub release metadata was fetched directly, avoiding stale search snippets.

| Component | Verified version/status | Primary record |
| --- | --- | --- |
| Bevy | 0.20.1, released October 28, 2026 | [Release](https://github.com/bevyengine/bevy/releases/tag/v0.20.1) |
| Fyrox | 1.0.0, released March 29, 2026 | [Release](https://github.com/FyroxEngine/Fyrox/releases/tag/v1.0.0) |
| Godot | 4.7.2 stable, August 18, 2026 | [Release](https://github.com/godotengine/godot/releases/tag/4.7.2-stable) |
| godot-rust/gdext | 0.5.5, August 9, 2026; tagged crate exposes `api-4-7` | [Release](https://github.com/godot-rust/gdext/releases/tag/v0.5.5), [features](https://github.com/godot-rust/gdext/blob/v0.5.5/godot/Cargo.toml) |
| Macroquad / miniquad | 0.4.16 / 0.4.11, crates.io stable metadata | [Macroquad](https://crates.io/api/v1/crates/macroquad), [miniquad](https://crates.io/api/v1/crates/miniquad) |
| wgpu / winit | 30.0.1 / 0.30.13 | [wgpu release](https://github.com/gfx-rs/wgpu/releases/tag/v30.0.1), [winit release](https://github.com/rust-windowing/winit/releases/tag/v0.30.13) |
| rend3 | Latest GitHub release 0.3.0 (2022); repository archived June 7, 2025 | [Release](https://github.com/BVE-Reborn/rend3/releases/tag/v0.3.0), [repository archive banner](https://github.com/BVE-Reborn/rend3) |
| Candidate support crates | parry3d 0.31.1; gltf 1.4.1; serde 1.0.229; serde_json 1.0.154; directories 6.0.0 | [Parry metadata](https://crates.io/api/v1/crates/parry3d), [gltf](https://crates.io/api/v1/crates/gltf), [serde](https://crates.io/api/v1/crates/serde), [JSON](https://crates.io/api/v1/crates/serde_json), [directories](https://crates.io/api/v1/crates/directories) |

Use Bevy's resolved wgpu/winit versions rather than independently forcing the
latest ecosystem versions. The Bevy 0.20.1 renderer specifies wgpu major 30;
this does not establish every combination in this table as compatible.
[Tagged manifest](https://github.com/bevyengine/bevy/blob/v0.20.1/crates/bevy_render/Cargo.toml).

## Bevy and five meaningful alternatives

The alternatives intentionally span complete engines and lower-level libraries.
They are not equivalent products; the missing assembly work is part of the
choice. Ordering below reflects fit for this project, not generic engine quality.

| Stack | What it supplies / why seriously consider it | Main project cost and disposition |
| --- | --- | --- |
| **Bevy baseline — recommended** | Rust ECS application, raster PBR, glTF scene loading, custom PBR extensions, UI, gamepad/window/input and audio under one application. Native Metal through wgpu. | Less integrated visual content authoring than Godot/Fyrox; bespoke reference UI, asset normalization and vinyl editor still needed. Rapid engine evolution requires version pinning. |
| **1. Godot 4.7.2 + gdext 0.5.5** | Full scene/UI/animation editor, native macOS ARM and Metal rendering, importer and macOS export. Rust classes can drive gameplay and independent simulation. | Strong runner-up; bridge engine objects/resources to Rust, package a matching ARM64 extension and manage two release surfaces. It does not eliminate donor-material repairs or handling recovery. |
| **2. Fyrox 1.0.0** | Rust engine with integrated scene editor, native UI/audio/animation and glTF PBR loading; 1.0 has automated project export. A credible choice when a Rust editor matters. | Tagged 1.0 engine uses OpenGL `GlGraphicsServer`; a `fyrox-graphics-wgpu` directory visible on current master must not be credited to this stable tag. Native Metal in the selected stable configuration is unestablished, making it less attractive for this Apple-only target. |
| **3. Macroquad 0.4.16 + miniquad 0.4.11** | Small Rust game library, simple 3D meshes/cameras, immediate UI, audio; miniquad documents macOS Metal. Useful for direct, compact rendering and simple authoring requirements. | Build/assemble PBR, lighting/shadows, GLB scene/material adaptation, richer UI navigation and gamepad integration. This full 3D content scope loses its small-library advantage. |
| **4. Custom wgpu 30.0.1 + winit 0.30.13** | Modern Rust GPU API with native Metal plus window/events; maximum control over renderer and data ownership. Legitimate when a distinctive renderer is the product requirement. | Neither is a game engine: assemble scene/resource system, PBR/shadows/post effects, glTF, animation, UI, audio and gamepads. Unnecessary engine construction for a behavior/content reconstruction. |
| **5. rend3-based Rust PBR stack** | Existing renderer/render graph plus PBR, shadows, tone mapping, glTF/framework and egui integrations reduce custom-wgpu work. It was a genuine middle ground. | Archived upstream; choosing it creates renderer maintenance and dependency-upgrade ownership now. Reject as a new foundation. Retained in comparison rather than silently substituting another candidate. |

Primary evidence for the table:

- **Bevy:** default 3D/UI/audio/platform feature collections and their constituents
  are explicit in the [0.20.1 manifest](https://github.com/bevyengine/bevy/blob/v0.20.1/Cargo.toml).
  Its [0.20 release](https://bevy.org/news/bevy-0-20/) documents ongoing scene/UI
  evolution and the shader-language transition to WESL. Feathers is presented as
  editor-oriented; do not mistake it for finished Juiced 2 menu art. Conventional
  raster PBR is the proposed starting point; Solari's new macOS support is not a
  reason to introduce path tracing into this checkpoint.
- **Godot:** [features](https://docs.godotengine.org/en/stable/about/list_of_features.html)
  document ARM macOS, editor, UI and Metal-capable Forward+/Mobile renderers.
  [GLB import](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_3d_scenes/available_formats.html),
  [custom spatial shaders](https://docs.godotengine.org/en/stable/tutorials/shaders/shader_reference/spatial_shader.html),
  [mutable InputMap](https://docs.godotengine.org/en/stable/classes/class_inputmap.html),
  [positional audio/pitch](https://docs.godotengine.org/en/stable/classes/class_audiostreamplayer3d.html)
  and [macOS export](https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html)
  cover the main services. [gdext compatibility policy](https://godot-rust.github.io/book/toolchain/compatibility.html)
  distinguishes compiled API from runtime versions and warns about occasional
  Rust API changes; tagged `api-4-7` availability is stronger evidence than merely
  assuming newer Godot compatibility. [ARM64 extension paths](https://godot-rust.github.io/book/intro/hello-world)
  are documented. No local pair compatibility test was run.
- **Fyrox:** the [1.0 announcement](https://fyrox.rs/blog/post/fyrox-game-engine-1-0-0/)
  documents scene/UI loading, editor improvements and export CLI, while candidly
  describing its small development team. The tagged
  [engine source](https://github.com/FyroxEngine/Fyrox/blob/v1.0.0/fyrox-impl/src/engine/mod.rs)
  imports the GL backend. Tagged [GLB loader](https://github.com/FyroxEngine/Fyrox/blob/v1.0.0/fyrox-impl/src/resource/gltf/mod.rs)
  and [material conversion](https://github.com/FyroxEngine/Fyrox/blob/v1.0.0/fyrox-impl/src/resource/gltf/material.rs)
  establish actual PBR channels. This is not an abandoned-engine dismissal or a
  claim that OpenGL cannot run natively on ARM; it is a stable-renderer tradeoff.
- **Macroquad:** [project](https://github.com/not-fl3/macroquad),
  [3D API](https://docs.rs/macroquad/0.4.16/macroquad/models/index.html) and
  [miniquad backends](https://github.com/not-fl3/miniquad#supported-platforms)
  establish the lightweight scope and Metal option. No full automotive PBR/glTF
  pipeline or remapping system was established from those APIs; completing one
  is project work, not a claim of technical impossibility.
- **Custom stack:** [wgpu's platform table](https://github.com/gfx-rs/wgpu/tree/v30.0.1)
  establishes native Metal; [winit](https://github.com/rust-windowing/winit/tree/v0.30.13)
  supplies windows/events rather than rendering/game systems. The integration
  list is an engineering estimate of work required by our scope.
- **rend3:** the [repository](https://github.com/BVE-Reborn/rend3) lists its renderer,
  PBR, glTF and egui companion crates. Its archive banner overrides the stale
  README sentence claiming active development. Metal via its historical wgpu
  foundation is not proof of compatibility with current wgpu or the M5 Pro.

None supplies reference career/economy/DNA/spooking/wager rules, AI driving logic,
automotive customization semantics or authenticated handling. These remain game
systems in every candidate. Choosing the most configurable renderer would not
remove that workload.

## Minimal coherent implementation stack

All choices below are recommendations to validate after plan approval.

| Responsibility | Proposed owner | Boundary and reason |
| --- | --- | --- |
| Application, renderer, camera, UI, animation, assets | Bevy 0.20.1; conventional PBR + custom material extension | Use built-in services first. Make the reference menu/HUD with Bevy UI; Blender authors tracks/props. Avoid introducing a separate runtime UI toolkit or third-party editor in the first proof. |
| Recovered numerical handling | Independent project Rust library | Parameters, ordered derivatives, RK4 commits, adaptive stepping and mutable scalars follow recovered evidence. Plain Rust inputs/state/output; presentation consumes snapshots. No ECS or renderer dependency inside the equations. |
| Collision geometry and queries | parry3d candidate 0.31.1 | Ray/contact/shape queries against authored collision meshes feed recovered force/contact logic. Parry supplies geometry queries, not car dynamics or response equivalence. Do not add Rapier/Avian unless a concrete nonvehicle dynamics requirement later justifies it. [Parry capabilities](https://www.parry.rs/), [query API](https://docs.rs/parry3d/latest/parry3d/query/index.html). |
| Assets | Existing pinned-source Python/Blender workflow, producing normalized GLBs + versioned JSON sidecars | Retain source hashes/scene selection and deliberate correction rules; author pivots, paint masks, collision meshes, kits, track geometry and LODs. Runtime only needs prepared offline assets. `gltf` 1.4.1 is a candidate only if a Rust offline parser is needed; do not add another runtime loader by default. |
| Controls | Bevy keyboard/gamepad APIs; small game action map in project code | Store action bindings, analog deadzones and sensitivity; support rebinding, UI focus and reconnect. Built-in platform features include `bevy_gilrs`; no separate input framework is needed before an actual gap. [Features](https://github.com/bevyengine/bevy/blob/v0.20.1/Cargo.toml). |
| Audio | Bevy audio initially | Family-shared RPM/load loops with per-car pitch/gain/crossfades, shifts, tyres, impacts, speech/music. Built-in settings expose looping, volume and speed; source audio and tuning remain content work. Do not add Kira/FMOD merely for possible future use. [Audio settings](https://github.com/bevyengine/bevy/blob/v0.20.1/crates/bevy_audio/src/audio.rs). |
| Career state, saves, settings | Project Rust structs + serde/serde_json; directories for user path | Explicit schema version, stable model/upgrade identifiers, write temporary file then replace, retained recovery copy. JSON avoids serializing engine entities as a save format. No database/server. [serde_json](https://docs.rs/serde_json/latest/serde_json/), [macOS user data path](https://docs.rs/directories/6.0.0/directories/struct.ProjectDirs.html). |
| Native offline delivery | `aarch64-apple-darwin` release executable + standard macOS bundle layout | Package selected assets in `Contents/Resources`, executable in `Contents/MacOS`, Info.plist and icon; resolve assets relative to executable/bundle, saves outside it. Inspect linked libraries, sign the actual bundle, and verify launch from Finder after moving it. No launcher or network dependency. [Apple bundle layout](https://developer.apple.com/documentation/bundleresources/placing-content-in-a-bundle). |
| Verification | Rust tests for numerical/career logic; scripted native scenarios and captures | Deterministic input/interval fixtures where warranted, asset validation and round-trip saves; Metal capture/profiling on the actual Mac. No extra test framework needed initially. |

Collision response remains a consequential unresolved seam: Parry can find
contacts, but wheel/road sampling, contact ordering, wall/car impulses and
friction scaling must match recovered evidence or be explicitly identified as
adaptations. A stock collision solver must not silently overwrite or double
integrate the recovered vehicle state. Godot could also use query-only physics
through [PhysicsDirectSpaceState3D](https://docs.godotengine.org/en/stable/classes/class_physicsdirectspacestate3d.html),
so independent handling is possible there too.

## Material and content pipeline gaps

Bevy 0.20.1 explicitly marks **`KHR_materials_variants` unsupported**; GLB support
alone is insufficient. It also documents feature gates for clearcoat/specular/
transmission textures and a limited `KHR_texture_transform` implementation.
Build an offline primitive-to-material variant table, preserve all required
textures/materials and select them deliberately at runtime. Alternatively emit
normalized variants as explicit assets. Test this on actual roster files before
committing to the representation. [Tagged glTF support table](https://github.com/bevyengine/bevy/blob/v0.20.1/crates/bevy_gltf/src/lib.rs).

Do not presume the five alternatives preserve every donor extension either.
Godot provides [GLTFDocument extension hooks](https://docs.godotengine.org/en/stable/classes/class_gltfdocument.html),
but this investigation did not establish native variants parity for its stock
importer. Fyrox's tagged gltf dependency enables only a limited named extension
set, not a demonstrated variants workflow. [Fyrox manifest](https://github.com/FyroxEngine/Fyrox/blob/v1.0.0/fyrox-impl/Cargo.toml).

For every accepted car, audit scene/LOD selection, units, handedness, forward
axis, textures, alpha/culling, vertex colours, normal/tangent space, paintable
surfaces, wheel nodes/pivots and compatible part sockets. Restore GT4 paint
coverage deliberately. Neutral glass remains a labeled fallback until better
native material evidence exists. Do not carry the sprite pipeline's unlit bake
into real-time PBR without a separate visual decision.
[Local source/material limits](../../../tools/carmodels/README.md).

Universal vinyl editing requires an authored paint mask and usable UV or
projection mapping for all 30 cars, plus layer composition/order, transforms,
mirroring and persistence. Recommend saving a compact layer description and
compositing a paint texture when edits change, sampled by the PBR material;
prove seams, mirrored UVs, paint-only masking and transparent glass first. This
is a proposed technique, not a ready-made Bevy feature or a settled reference
layer limit. Material variants change materials; they do not create body-kit
geometry. [KHR_materials_variants specification](https://github.com/KhronosGroup/glTF/tree/main/extensions/2.0/Khronos/KHR_materials_variants).

Tracks, lighting, collision meshes, AI racing lines, reference camera, traffic
where evidenced, compatible body/interior kits, replacement wheels and sound
sets are separate production work. No renderer converts the donor catalog into
these assets. Thirty structurally valid GLBs do not prove visual customization
or physics correctness.

## Proofs required after approval

1. **Native rendering and asset proof:** compile pinned release configuration for
   ARM64; log actual Metal adapter/backend. Render representative GT4, MC3, MCLA
   and FR2 cars and then load all 30. Compare material/variant/alpha/scale/pivot
   captures to source expectations. Prove one paint finish, vinyl edit/reload,
   wheel swap and compatible kit without shared-material contamination.
2. **Handling and collision proof:** port verified equations with address-bound
   fixtures and explicit unknowns. Exercise recovered adaptive intervals and
   RK4 commit behavior; prove road contacts, slope, kerb, wall and car contact
   ordering. Match available recovered intermediate values before claiming
   numerical equivalence. No original runtime trace currently establishes a
   whole-vehicle golden trajectory; resolve that limitation explicitly.
3. **Controls/audio proof:** remap keyboard and a connected conventional gamepad,
   persist bindings, reconnect and navigate menus; check analog range/deadzones.
   Demonstrate family-shared engine loops through idle/load/shifts, crossfades,
   AI positional audio and simultaneous speech/music. Add a specialist audio
   library only if the measured built-in result exposes a concrete shortfall.
4. **End-to-end proof:** the separately approved checkpoint should exercise car
   selection, one reconstructed course, circuit/drift, AI/HUD, cash wager,
   garage changes and persisted progression. Test settlement/relaunch and save
   interruption; do not invent still-unrecovered forfeiture/bankruptcy rules.
5. **Performance/delivery proof:** measure release build at actual 1920×1080
   rendering resolution (separate from Retina logical size), with representative
   AI, lighting, shadows, effects and audio. Record CPU/GPU frame times, frame
   distribution, loading and memory on the specified M5 Pro. Sixty fps means a
   16.67 ms frame budget, not an existing result. Launch the moved `.app` from
   Finder offline, without development checkout, source GLBs cache or toolchain;
   inspect ARM64 slices, asset completeness and external dylib paths.

Failure of the material/Metal or integration proof is a reason to reassess the
stack before bulk content work. Bevy is the planning recommendation now; none
of these unrun proofs is represented as passed, and this report does not itself
authorize implementation.

The primary agent selected this recommendation for the proposed plan under the
user's delegated research decision. See the
[stack decision](../../adr/0004-select-bevy-and-independent-handling.md). Native
compatibility and performance remain subject to the explicit proofs above.

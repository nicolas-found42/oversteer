# Vehicle inspection

Run from the repository root with prepared assets and the current development
extension. Uses real Godot/Metal rendering and the same focus guard as `verify.py`.

```sh
uv run --frozen python tools/game/build.py build --profile dev
uv run --frozen python tools/game/inspect_vehicles.py --output build/verification/vehicle-inspection
```

Use a new output directory for each run. `--car GT4_MITS0001` limits the run to
one representative car; `--smoke` takes six images to validate the pipeline.
The default is Civic EK (FWD), MX-5 NA (RWD) and Evo VIII (AWD).

The standard run produces **42 PNGs: 14 per car**, at 1920×1080. The absolute
ceiling is **50 screenshots for an entire run**, not per car or subprocess.
Smoke mode produces six per car (18 total). Do not split an exhaustive matrix
into repeated runs to evade the ceiling; select views that answer the defect.

| Situation per car | Views | Purpose |
| --- | ---: | --- |
| Four course-context quarters (45°/225° at 10° elevation; 135°/315° at 35°) | 4 | Road contact, stance, lighting and track occlusion |
| Front/rear/left/right, 5° elevation, neutral light | 4 | Silhouette, wheel alignment, panels and lamps |
| Four isolated quarters at 35°; two neutral, one grazing/−20° roll, one backlit/+20° roll | 4 | All eight isolated azimuths, normals, reflections and tilted framing |
| Near-top (75°) and underside (−25°), neutral light | 2 | Roof, cabin, floor and hidden geometry |

The external script uses its own `--inspection-output` argument so the game's
scenario capture path cannot add incidental PNGs. Both the planned count and
actual recursive PNG count are checked. General verification also has a shared
50-image budget across cases; periodic captures have been removed. Wheel-motion
verification uses six azimuths with adjacent-tick pairs (12 images per car), plus
one final checkpoint per car: **39 images** for its three-car suite. Telemetry
continues at every existing sample without additional screenshots.

The car reaches the final input-plan event plus two active ticks (currently 332).
`--freeze-frame N` allows an explicitly recorded partial override; the frame budget
is derived from that value. Brake/reverse and nitrous events are no longer skipped.
The diagnostic script then freezes scene processing, including physics, without
changing the saved car or source assets. It fits the actual transformed mesh
vertices in a 42° perspective camera with an 8% framing allowance. Perspective
bounds are centered after applying roll, with a one-pixel acceptance tolerance.
Course views test sightlines against oriented rival bounds and raise elevation,
up to 80°, when a rival blocks the car. Requested and actual elevations and the
blocking-rival lists are recorded; this adjustment creates no extra screenshots. The course,
opponents, particles and vehicle effect lights are hidden only for isolated
views so they cannot obstruct undersides or contaminate the controlled light.
HUD is hidden throughout the sweep. Three explicit nonpresenting render steps,
each checked for `frame_post_draw`, precede each PNG. This also avoids waiting
forever when macOS covers the window and suppresses automatic drawing. This is
a static material/geometry inspection, not a driving-motion or FPS
benchmark; keep the existing `verify.py --suite wheel-audit` motion pairs.

## Diagnostic output

- `index.html`: all images and companion JSON links.
- Per-car `race-state.json`: actual game snapshot, wheel geometry/contact
  measurements, effective material state, last 120 input samples and bounded
  history of the last 128 commands (before/after screen, cash and error).
- Per-image JSON: camera transform/FOV/clipping planes, projected vertex bounds,
  framing result, light/ambient settings, image size and contextual performance
  monitors, plus `capture_ms` equal to the capture-begin/complete JSONL timestamps.
  Cached Godot monitors are contextual only. Startup logs separate load wall time,
  scene-sync/physics CPU time, mesh extraction and frames with pipeline compilation.
  Godot does not expose isolated asynchronous shader-compiler CPU time.
- `events.jsonl`: flushed startup/freeze/capture-begin/capture-complete/failure
  records. An interrupted run leaves the last attempted capture identifiable.
  The runner cross-checks each duration and start timestamp against these records,
  asserts all required standard view angles/lights, rejects repeated loading
  progress rows, and checks every input-plan event was processed before freezing.
- `material-import-check.json`: source/factory alpha and transparency, positive
  orthonormal wheel bases, back-face culling, nonzero opaque/masked tire alpha,
  roughness ranges and the effective gloss shader finish.
- Race-state rendering diagnostics validate actual texture mip chains, anisotropic
  sampler hints, sky reflections and loading only the participating race assets.
- `process.json`, `runtime.log`, `inspection.json`, `verification.json`: exact
  launch, PID, engine output, capture results and asset/tool/binary identity.

A green technical result does not certify attractive materials, correct normals,
absence of all track occlusion, or overall vehicle quality. Inspect images.
Do not change capture scripts or assets while a batch is running.

## Additional tools and docs

The [primary-source research note](../../../docs/research/VEHICLE_INSPECTION_TOOLS.md)
covers Godot/godot-rust, Blender, Khronos tooling, awesome-list discovery and
Apple GPU diagnostics. Blender is already available for background geometry
inspection. Install the exact Khronos validator locally:

```sh
npm install --prefix build/tools/gltf-validator --save-exact gltf-validator@2.0.0-dev.3.10
node tools/game/inspection/validate_glb.cjs build/verification/glb-validation godot/assets/cars/GT4_MITS0001.glb
```

The validator preserves its version, source SHA-256 and full report. Validation
fails on nonzero `issues.numErrors`; warnings remain in the report. It is a file
validity check, not visual acceptance. The installed package's prerelease name
is its official published version; do not describe it as stable semver.

`--metal-capture` prepares a separately identified, locally signed diagnostic
Godot copy with `get-task-allow`, preserving the original entitlements and pinned
engine. At the first settled inspection view it captures one presented frame if
the window can draw. A covered window instead captures one Godot main-queue
command buffer, explicitly identified as **not a presented frame** in the report.
It retains the command, scope, boundary listing, view identity and trace size.
Capture failures fail verification. It does not add PNGs to the view budget.
The regular command continues to use the original engine. See the
[solution and primary-source research](../../../docs/research/METAL_CAPTURE_LIMITATION.md).

```sh
uv run --frozen python tools/game/inspect_vehicles.py --metal-capture --smoke --car GT4_MITS0001 --output build/verification/metal-smoke
gpudebug --oneshot -t build/verification/metal-smoke/GT4_MITS0001/frame.gputrace -c 'list' -c 'status'
```

Apple's installed `gpucapture` and `gpudebug` support CLI capture and inspection
without installing full Xcode. GPU-instrumented runs are not FPS benchmarks.
Never export or distribute the diagnostic engine copy.

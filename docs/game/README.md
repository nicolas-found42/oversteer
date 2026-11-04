# Native Rust game

Current product scope is the [accepted independent-game pivot](../design/OVERSTEER_PIVOT_INTERVIEW.md).
Use [PIVOT_STATUS.md](PIVOT_STATUS.md) for current implementation evidence and
remaining work. Historical reconstruction checks below describe the retained
foundation, not a requirement to match Juiced 2.

`tools/game/verify.py --suite pivot-ui` exercises
the new onboarding, driver-name persistence and fixed-driver betting screen.
Visual scenarios retain selected action checkpoints, with no periodic captures.
Every whole run is capped at 50 PNGs, including incidental images. Galleries
include every retained PNG for manual inspection.

The current runtime selects six Oversteer tiers and 18 circuit/drift/promotion
events on London Circuit and London Drift. The 30-car foundation remains; the
other 31 recovered courses and all 463 source contests are deferred/replaced,
as listed in [the content inventory](../../data/oversteer/content-selection.json).
Recovered catalogs remain unchanged. Tier names, prices and rewards are current
development tuning, not final economy acceptance.

`uv run --frozen python tools/game/verify.py --suite pivot-career` checks the
career/progression/event screens, separate-process save reload and the second
course, using eight screenshots. `cargo test -p oversteer-core --test pivot_career`
includes an actual-input first-tier playthrough on Easy with earned circuit,
drift and promotion wins and save/reload between races. This does not substitute
for rendered full-career, wager or human handling acceptance.

`uv run --frozen python tools/game/verify.py --suite pivot-wagers --output build/verification/wagers`
checks purchase/upgrade, cash and pink-slip restart/menu forfeiture, forced-crash
recovery and repeated relaunch in 16 cases with 33 screenshots. It terminates only
its own verification processes after the recorded crash checkpoints. Use a new
output directory. Race-finish wager outcomes are a separate acceptance check.

`uv run --frozen python tools/game/verify.py --suite wheel-audit` captures the
Civic (FWD), MX-5 (RWD) and Evo (AWD) during controller-driven racing, at six
60-degree camera intervals with two adjacent ticks per angle (36 angle PNGs plus
three final checkpoints: 39 total). Each
image has a JSON sidecar with actual spin, steering and contact telemetry, plus
rendered wheel vertices’ minimum clearance from their contact plane. The camera
is inspection-only; the normal simulation and input path remain active. These
short runs cover launch, steering, coasting, braking and handbrake, not all tracks
or airborne/body-collision acceptance. The faster Evo uses gentler steering to
keep roadside barriers out of the inspection camera's orbit. The reviewed
three-car gallery is `build/verification/pivot-wheel-review/index.html`, with
adjacent-tick toggles and links to each image's telemetry.

Automated verification and asset imports protect desktop focus by default while
retaining the actual Metal renderer. A development-only AppKit guard is
preflighted headlessly; an unavailable guard cancels the launch. Use
`verify.py --foreground` only for intentionally interactive testing. The guard
does not ship in the game. Background automated input is not a substitute for
the final keyboard/controller and foreground performance checks.

The cartoon Kenney driver was rejected by the user. Character acceptance now
requires realistic adult proportions and streetwear/racing-game presentation.
The fixed existing streetwear asset is being evaluated without reintroducing
character customization; the rejected candidate and its tooling are retained
only under `artifacts/oversteer-pivot/driver/rejected-kenney/`.

The current target is Apple Silicon macOS, using Godot **4.7.2** and the Rust
`godot` crate **0.5.5** (`api-4-7`). The workspace pins Rust **1.99.0**;
gdext itself declares a lower minimum, which is not this project's tested toolchain.
The authoritative simulation and career rules live in `crates/oversteer-core`;
Godot presentation, input, audio and native UI integration live in
`crates/oversteer-godot`. Gameplay does not use a Godot vehicle controller.

The accepted scope and six release evidence requirements are tracked in
[issue 1](https://github.com/nicolas-found42/oversteer/issues/1). Recovery,
implementation and validation are still in progress. Generated assets,
verification captures and packages are local build outputs.

For the exact paused source/runtime boundary and pending work, read
[the implementation handoff](HANDOFF.md) before resuming.

## Check sources in a fresh clone

Install rustup, uv, and Apple command-line developer tools on Apple Silicon.
Repository pins select Rust 1.99.0 with rustfmt/Clippy and Python 3.13.16.
No Godot or original game assets are needed for the source gate:

```sh
uv run --frozen python tools/game/dev.py doctor
uv run --frozen python tools/game/dev.py check
```

`tools/game/dev.py` is the authoritative developer command entry point. Use
`format` for explicit formatting edits, `lint` for source diagnostics, `test`
for existing Rust/Python tests, and `reference-tests` for the source reference
checks. `test` runs 27 Rust library tests and the Python game-tool, carmodel and
reference-review unit suites; the 89
core integration cases remain in `reference-tests` and require local recovery
evidence. Missing reference fixtures fail explicitly. A successful source gate
does not establish rendered or release behavior.
The native CI job runs this same gate on an ARM64 Mac; it does not prepare assets
or measure GPU performance.

## Prepare and run

The runtime tier requires the accepted local inputs described below. After
preparing them, `uv run --frozen python tools/game/dev.py doctor --runtime`
checks the prepared workspace. A fresh clone alone cannot reproduce it.

From the repository root:

```sh
uv run --frozen python tools/game/bootstrap.py
uv run --frozen python tools/game/build.py run
```

Bootstrap downloads the exact official editor and export templates, verifies
them against the release's SHA512 checksums, and prepares an ARM64 template by
thinning the official universal binaries with Apple's `lipo`. It writes its
manifest in `build/tools/godot-4.7.2/`. For Rust debugging without importing assets, use
`uv run --frozen python tools/game/build.py build --profile dev --skip-import`.
This compiles/copies the dev extension only; it does not prepare a runnable game.
The VS Code native LLDB profile launches the pinned Godot executable with this
extension and already imported assets. Breakpoints have not been verified; local
macOS debugger permissions/signing may need setup.

Close Godot before rebuilding: the build command refuses to replace an open
extension. Dev builds update only the debug-path library; the release-path
library remains unchanged. Export requires the release profile.

The default release build compiles the ARM64 Rust extension,
copies it into the project and imports its assets.
Asset import uses the native renderer and rejects logged import errors even
when Godot exits successfully. A dummy-renderer import previously produced
texture errors for valid kit art; the same asset imported cleanly with Metal.

Asset preparation is documented in [the pipeline](../../tools/game/assets/README.md).
It requires the accepted local carmodel sources and supplied game image.
Source provenance, adaptations and original rule recovery are retained in
`data/juiced2/`, [the reference docs](../references/juiced2/README.md), and
`artifacts/juiced2-recovery/`. A prepared exported app includes its runtime
assets and does not require those source inputs.

The default driving controls are W/S for throttle/brake, A/D for steering,
Space for handbrake, Shift for nitrous and Q for reverse. Keyboard and controller
bindings can be changed in Options. Escape pauses a race.

## Verify

```sh
python3 tools/game/build.py test
python3 tools/game/verify.py --suite screens
python3 tools/game/verify.py --suite driving
python3 tools/game/verify.py --suite input
python3 tools/game/verify.py --suite ui
python3 tools/game/verify.py --suite all30
python3 tools/game/verify.py --suite performance
python3 tools/game/verify_saves.py --seed-save /absolute/native-run/all30/save.json
```

Native suites open the actual Metal-rendered game. Reports retain the exact
extension and content hashes, process logs, screenshots, serialized game state,
save round trips and individual checks. Long race scenarios advance normal
simulation faster for repeatable completion; formal performance scenarios use
normal simulation speed, 300 warmup frames and at least 1,800 measured frames.
Their timings come from a monotonic host clock, with separate viewport render
measurements. Source-linked visual comparisons require explicit review;
successful technical checks do not by themselves establish visual parity.
The input suite injects real Godot keyboard and controller events, records the
polled controls and car poses, and checks left/right movement against the chase
camera. It disables scenario autopilot and retains each exact event file and
its hash. Godot's `--fixed-fps 60` supplies a deterministic simulation delta for
these rendered input scenarios. Their elapsed game time is independent of host
frame time; they are not performance benchmarks. UI scenarios activate real
controls and retain their action plans, settled-frame captures and transaction
results.

Recorded host-reachable controls can be translated into actual controller events
and replayed through career navigation:

```sh
python3 tools/game/replay_inputs.py --evidence /absolute/recording-evidence.json \
  --output /absolute/new-input-events.json
python3 tools/game/verify.py --suite replay \
  --replay-manifest /absolute/new-input-events.manifest.json
```

The converter checks input-file and recorded career-lineage hashes, archived source
identities when supplied, and every raw-axis-to-control conversion as packed binary32.
The native launch checks the exact initial save, retained recording evidence,
controls, input plan and any recording-specific UI plan against the manifest hashes.
The native verifier compares every active polled control and the natural race
result with the recording. It injects input events only. A replay that starts
from a prepared league save proves that event and its settlement, not complete
career progression.
The save-specific suite uses a save from an actual native scenario and starts
separate processes for primary/backup recovery and failure protection. It keeps
the seed unchanged and retains all damaged copies used by the checks.

A particular scenario can be run independently:

```sh
python3 tools/game/build.py run --skip-build --scenario benchmark \
  --event EVENT_ID --frames 2100 --warmup 300 --capture /absolute/output/path
```

## Package

```sh
python3 tools/game/build.py export
python3 tools/game/verify.py --app build/packages/Oversteer.app --suite smoke
python3 tools/game/verify.py --app /absolute/moved/Oversteer.app --suite smoke --offline
python3 tools/game/verify.py --app /absolute/moved/Oversteer.app --suite smoke \
  --independent --output /absolute/output/outside-the-checkout
```

The export is `build/packages/Oversteer.app`, an ARM64 bundle with local ad-hoc
signing. Release validation also requires copying it outside the checkout and
checking launch, saved progress and rendering from that independent location.
Packaged scenarios use an independent working directory. The `--offline` flag
uses macOS `sandbox-exec` to deny networking to the game process while leaving
the rest of the computer's network connection unchanged.
The stronger `--independent` check also denies checkout file reads at the OS
level, probes that denial, and requires the app and output outside the checkout.
The harness copies scenario/input files into the external output directory
before launching the isolated game. Export signing can change the extension's
complete-file hash; retain the packaged hash separately from its development
input and compare their Mach-O sections when verifying provenance.
No older Apple Silicon performance or minimum-macOS support is claimed before
testing it. The agreed initial performance target is actual 1920×1080 rendering
at 60 FPS on the current M5 Pro.

## Formatting and lint adoption

Rust uses the pinned rustfmt and strict Clippy on all workspace targets, including
examples. Documented allowances preserve recovered numeric literals, max/min NaN
behavior, and deliberate source-indexed equations. No automatic math rewrite is
part of the gate. Python uses the pinned Ruff: normal host tools enforce style
and correctness, while all recovery workers enforce fatal correctness rules and
syntax without a bulk formatting migration. To inspect remaining worker style debt:

```sh
uv run --frozen ruff check tools/game/assets --select E,F,W,I,B --ignore B905 --statistics
```

This advisory command currently fails on known style debt; it is separate from
the passing source gate. No import-all check, paid Jev request, asset publication,
Blender render or native launch occurs during source validation.

The three primary-source research reports and implementation decisions are linked
in [the developer-tooling audit](../references/juiced2/devtools-implementation.md).

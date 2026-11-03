# Native Rust game

The current target is Apple Silicon macOS, using Godot **4.7.2** and the Rust
`godot` crate **0.5.5** (`api-4-7`). Rust 1.94 or later is required by gdext.
The authoritative simulation and career rules live in `crates/oversteer-core`;
Godot presentation, input, audio and native UI integration live in
`crates/oversteer-godot`. Gameplay does not use a Godot vehicle controller.

The accepted scope and six release evidence requirements are tracked in
[issue 1](https://github.com/nicolas-found42/oversteer/issues/1). Recovery,
implementation and validation are still in progress. Generated assets,
verification captures and packages are local build outputs.

For the exact paused source/runtime boundary and pending work, read
[the implementation handoff](HANDOFF.md) before resuming.

## Prepare and run

From the repository root:

```sh
python3 tools/game/bootstrap.py
python3 tools/game/build.py run
```

Bootstrap downloads the exact official editor and export templates, verifies
them against the release's SHA512 checksums, and prepares an ARM64 template by
thinning the official universal binaries with Apple's `lipo`. It writes its
manifest in `build/tools/godot-4.7.2/`. Building compiles the ARM64 Rust extension,
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

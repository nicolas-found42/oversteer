# Independent Oversteer implementation

The user authorized the entire [pivot plan](../design/OVERSTEER_PIVOT_INTERVIEW.md).
The goal remains active until the retained game's implementation and verification
meet that plan; the first three-car/two-track slice is an intermediate milestone.

## Recalibration against the accepted plan

The implementation is between steps 2 and 3, not at release acceptance. The
wheel review completed a targeted defect pass; it did not complete handling or
the career slice. The preceding turn made concrete progress through fixes and
rendered evidence. The following gaps remain part of the active objective.

| Plan requirement | Current evidence | Work needed for acceptance |
| --- | --- | --- |
| Independent identity and restrained interface | Startup/menu/HUD changes and retained native captures | Review every retained screen, transition and track for remaining identity-bearing art and layout defects |
| Remove character customization; fixed realistic adult driver and name | Compiled editor removed; name save/relaunch passed; fixed model animates | Accept the driver's face/materials and all character appearances; current low-detail head is not final |
| Three representative cars and two tracks | Civic/MX-5/Evo wheel captures on London | Finish car materials, select/review the second course, and validate circuit and drift |
| Believable arcade handling and stable race behavior | Evo mass and wheel mapping/contact fixes; focused tests and input runs | Cornering, drifting, full-lock/airborne clipping, collision recovery, AI and chase-camera playtests on both courses |
| Clear tiered career; defer crew/DNA/spooking/sponsors | Six independent tiers, 18 events, quiet progression UI; crew/spooking disabled and sponsor contests removed from runtime | Validate all tiers and balance; complete rendered career/wager/persistence loop |
| Buy/customize/race/reward/unlock/save/resume | Rendered purchase, engine upgrade and relaunch pass; input-only first-tier core playthrough passes | Complete the rendered earned-reward/unlock loop with keyboard/controller |
| Cash bets, pink slips and no-stake earnings | Nine focused wager tests; rendered cash/pink race-finish wins/losses, restart, menu exit, forced crash and fresh-process reloads pass | Rendered last-car protection and no-stake earning paths |
| Thirty-car foundation | Asset inventory only; three cars partly reviewed | Validate each retained car's visuals, driving and customization; explicitly inventory deferred courses/events |
| Apple Silicon offline build, remapping, 1080p/60 | Development Metal runs capture at 1080p; protected input runs pass | Final keyboard/controller/remapping checks, uncontaminated timing and independent packaged offline export |
| No known visible defects on accepted paths | Captures still show glass, lamp, shadow and lighting defects | Repair and recapture; technical verification passes cannot substitute for visual acceptance |

Execution order remains: finish the representative cars' visible material faults;
implement and exercise the tiered career slice and wagers; complete both-course
handling/AI/camera checks; then extend across the retained roster and validate the
final package. Capture and inspect throughout, without desktop focus activation.

## Independent career foundation — 2026-11-04

### Race finishes, chosen-rival settlement and reload — verified continuation

The [finish summary](../../artifacts/oversteer-pivot/wagers/finish-summary.json)
records **eight passing native cases**: cash and pink-slip wins/losses, each
followed by a fresh-process reload. The cases branch from the previously earned
purchase/upgrade save, use Normal difficulty and ordinary controller events,
and compare every polled control, finish time, result, transaction and final save.
No pose, score, ownership or progression is injected. Accepted cases use **16
screenshots**; retained failed attempts bring this continuation to **22**.

| Outcome against Bobby Sawyer | Overall finish | Final cash | Garage after reload |
| --- | --- | --- | --- |
| Cash win, $2,250 stake | Second, 116.99 seconds | $8,250 | Civic and Mini |
| Cash loss, $2,250 stake | Fourth, 177.33 seconds | $2,750 | Civic and Mini |
| Pink-slip win | Second, 116.99 seconds | $6,000 | Civic, Mini and awarded MX-5 |
| Pink-slip loss | Fourth, 177.33 seconds | $5,000 | Mini only |

Each result records one overall race loss because none wins the event; beating
the chosen rival still wins the stake. Result panels now distinguish race reward,
net bet profit, returned cash stake and the named car transferred in pink slips.
The four final result screens were visually reviewed. Cash evidence is in
[`pivot-wager-finishes`](../../build/verification/pivot-wager-finishes/index.html);
the final pink-slip evidence is in
[`pivot-pink-finishes-accepted`](../../build/verification/pivot-pink-finishes-accepted/index.html).
Cash cases precede the isolated pink-slip inventory fix; each report retains its
own binary/tool identity. The earlier mixed batch remains failed for its omitted
pink-slip confirmation; it is not relabeled as an entirely passing run.

The delayed start reproduced a real finish-line blockage: finished rivals stopped
receiving physics updates while remaining collidable with stale velocity. A
focused regression measured zero movement in a second. Finished cars now keep
driving with AI controls, with recorded finish times exposed in snapshots. The
original ordinary-input London reproduction now finishes in 177 seconds instead
of remaining blocked after ten minutes. The regression also checks retained
finish time and score.

Native pink-slip reload exposed a second defect: awarded cars lacked their stock
parts inventory until loading repaired it. Settlement now initializes that
inventory immediately. A focused save/reload regression failed before the fix;
the native win and fresh reload now preserve the exact state. The loss retains
only the spare Mini, with no repeated car removal or payout on reload.

Verifier fixes distinguish raw catalog and selected runtime content hashes,
support the actual reverse binding and explicit pink-slip confirmation plan,
and compare the full recorded final save. Failed processes now report the actual
PNG count instead of their remaining image allowance; a regression reproduced
the previous incorrect `42` count for an aborted run that generated zero PNGs.
All failed reproductions are retained. The accepted runs report no runtime errors
or focus violations. Final checks pass **113 core tests**, **28 Rust library
tests**, **66 Python tests**, strict Clippy, Ruff and formatting. Logs and input
recordings are in `artifacts/oversteer-pivot/wagers/`.

Next: demonstrate last-car protection and a no-stake earning race through the
native UI, then complete the rendered promotion/unlock/relaunch loop. Both-course
handling, remaining art, later-tier balance, full-roster review and the offline
package remain open. This continuation is progress, not completion of the pivot.

### Purchases, wager abandonment and crash recovery — verified continuation

The [native wager gallery](../../build/verification/pivot-wagers-accepted/index.html)
passes **16 cases with 33 screenshots**, including actual UI purchase, upgrade,
stake acceptance, keyboard-event pause, restart/menu exit, forced process
termination and fresh-process relaunch. Binary/content/tool identities stay fixed;
there are no runtime errors or focus violations. This is persistence and UI
evidence, not a claim that the earned race-finish wager loop is complete.

The setup buys the Mini for $19,500 as a spare and installs the starter Civic's
$1,000 engine upgrade, leaving $4,500. Each wager branch copies that independently
earned save. Cash is staked against Bobby Sawyer at the accepted $2,250 counter.
Restart and menu exit leave $2,250 and one loss, with both cars retained and only
one escrow/settlement pair. Pink slips stake the Civic against Bobby's unowned
MX-5; voluntary abandonment removes the Civic once, leaves the Mini and $4,500,
and records one loss. Restart begins without another stake.

An unsettled career race is recorded in the save with its escrow, entry fee and
staked-car identity. Loading cancels that unfinished race, refunds its unsettled
cash and preserves ownership/losses. Successful or voluntarily abandoned races
omit the recovery record. The tests kill only the launched verification process
with SIGKILL after a rendered active-race checkpoint and a persisted stake. Fresh
loads restore $4,500, zero losses and both cars. A second process reload verifies
that neither cash nor the recovery transaction is duplicated. Eight focused core
wager tests pass, including settled-reward reload and rejecting pink-slip rivals
whose vehicle is already owned (the garage currently has one entry per model).

The full purchase path exposed **88 null-material renderer errors**. A minimized
performance-page entry reproduced 44 errors; ordinary car/menu transitions did
not. Removing the performance wireframe override made the same reproduction pass.
The player now sees the normally shaded car in the workshop; the unused wireframe
path was removed. The original purchase/upgrade path subsequently passes without
errors. Rejected and minimized reproductions remain in `build/verification/`
under `pivot-wager-purchase-path` and `pivot-material-*`.

Checkout now uses restrained typography, item/car names, prices, total and the
remaining balance instead of the recovered purple cart layout. Accepted bets
show the actual rival, stake and forfeiture terms and no longer offer replacement
stakes. Pause warnings have a readable panel; irrelevant dealership metadata was
removed from paused races. Garage/dealer actions sit below the car. These screens
were visually reviewed in the final captures. Driver/car/workshop art remains
unfinished as listed in the overall acceptance table.

The first complete wager run retained three failed assertions because its checker
still named the old Mini starter. Saved state showed the correct Civic upgrade
and Civic forfeiture. The checker now uses the independent Civic starter, and the
fresh final run passes all cases; the original failures were not overwritten.
The source gate passes strict Clippy, formatting, Ruff, 28 Rust library tests and
62 Python tests. Focused core wager tests pass 8/8. Logs are retained under
`artifacts/oversteer-pivot/wagers/`.

The race-finish wager checks are completed in the continuation above. Next:
verify the last-car/no-stake earning path through the UI, and connect rendered
race rewards to promotion/unlock/relaunch. Later-tier balancing, both-course
handling, final art, full-roster review and the offline package remain open.

The runtime now selects six tiers (Local, Club, Street, Regional, Pro, Masters),
each with a circuit race, drift event and promotion/final race. Win both regular
events to open promotion; win promotion to advance. Events are free to enter,
earlier tiers remain replayable, finishing positions pay cash, and no wager is
required for progression. The last tier's final completes the career. Full
six-tier driving/balance acceptance remains pending.

`crates/oversteer-core/src/career.rs` owns this selection. It retains all 30 cars,
selects London Circuit and London Drift, and replaces the recovered contest/goal
catalog at runtime without rewriting the source data. The explicit
[inventory](../../data/oversteer/content-selection.json) lists all retained cars,
31 deferred courses and 463 replaced source events. The starter Civic is stable
regardless of catalog order. The MX-5 is available immediately for $18,000; the
Evo unlocks in tier two at $32,000. Other car unlocks fit the six-tier structure.
Prices, three-car rival fields and later-tier difficulty still need broader tuning.

Crew recruitment/navigation and spectator spooking commands are rejected without
changing a career. AI no longer receives proximity/collision spooking steering
noise. The active events contain no crew, DNA or sponsor objectives. Recovered
driver data still supplies ordinary rival driving personalities. The progression
screen uses plain tier/requirement rows; event details explain rewards, eligibility,
drift target/time limit and promotion effects. Career car cycling now uses owned
cars, and cash/pink-slip stakes remain on the grid.

Six focused career tests pass, including a first-tier playthrough using ordinary
driving inputs on the actual selected tracks, on Easy. It buys the MX-5, wins
circuit/drift/promotion, saves and reloads between races, ends with three earned
completions, $17,000 and tier two unlocked. No pose, score or progression injection
is used in that playthrough. Separate small state-boundary tests use explicit
fixtures and are not presented as driving evidence. The full core suite passes
**108 tests**. The two retired Eliminator/Obliterator career-win replays were
replaced by the independent playthrough; retained physics/scoring source tests
remain active. No failing test was silently treated as a pass.

The first native `pivot-career-foundation` run passed its technical checks with
eight PNGs, but visual review found event text over the car. `pivot-career-layout`
separated the panel and exposed a label-minimum-size/wrapping issue. The focused
`pivot-career-wrap` recapture verifies the corrected panel with six PNGs. Earlier
captures are retained as rejected layout evidence. The separate-process reload
and London Drift rendering checks passed; these short rendered checks do not
establish a full rendered career playthrough. Source checks passed (strict
Clippy, formatting/Ruff, 28 Rust library and 58 Python tests).

The final [native acceptance gallery](../../build/verification/pivot-career-accepted/index.html)
passes all three cases with **eight screenshots**, no incidental captures or focus
violations. It confirms wrapped event-panel text, the explicit three-minute drift
limit, removal of the unrelated drift attempts counter, tier requirements and
new-career reload. The runtime report contains exactly 30 cars, two courses,
12 circuit/promotion races and six drift events. Final focused career tests and
the source gate pass. Logs and the input-only driving probes are retained under
`artifacts/oversteer-pivot/career/`.

Next acceptance work: render the earned career and race-finish wager rewards
through unlocks and relaunch; validate
later-tier balance; refine the second course's road materials/remaining branding
and the driver/car defects. The broader pivot is still active and incomplete.

## Capture standard and GPU diagnostics — 2026-11-04

### Current-build revalidation of the five inspection/race defects

The [fresh static gallery](../../build/verification/pivot-pipeline-revalidated/index.html)
passes all checks for Civic, MX-5 and Evo with **42 captures**. The runner now
independently checks complete isolated azimuth/course-quarter/top/underside/roll
coverage, lighting presets, capture durations against both JSONL boundaries,
deduplicated loading samples and processed input-event counts. Two focused
regressions reject mismatched capture timestamps and repeated rear views.

Startup-to-freeze is **9.394 / 8.192 / 8.050 seconds** respectively. GLB loading
took **3.668 / 2.610 / 2.452 seconds** and bounds extraction **36 / 45 / 39 ms**.
All ten input events were processed before freezing at frame 332. The largest
projected-center error across the run was **0.00256 pixels**. Current career
selection uses three rivals, so these timings are not an identical-field
performance comparison with the original six-rival report. Shader-compilation
frame wall times remain explicitly contextual, not isolated compiler CPU timings.

The [fresh race-start report](../../build/verification/pivot-race-start-revalidated/race-start-check.json)
passes countdown lock, centered countdown/GO, clock/HUD state and launch checks,
with two captures. The current three-rival field reaches **29.4–46.0 kph** and
**4000–5823 RPM** at input frame 166. The separate six-rival core regression and
the earlier six-rival native evidence remain passing. Rival paint/plates are
distinct. London lettering, road sampling, sky reflections, gloss paint and
wheel materials were reviewed in the fresh images. Both rendered processes use
the focus guard and report no runtime errors or focus violations.

This validation produced **44 native screenshots plus three review contact
sheets (47 image files total)**, below the 50-image ceiling. All 42 static views
were reviewed in contact sheets, with full-resolution checks of the Evo rear,
rolled glass reflection, countdown and GO images. Remaining coarse lamp textures,
faceted body highlights, cabin detail and unrelated track branding are not
claimed fixed by this inspection task.

The current core suite passes **111 tests**; the source gate passes formatting,
strict Clippy, Ruff, **28 Rust library tests and 62 Python tests**. The two asset
repair regressions pass separately. All three car GLBs pass Khronos validation
without errors or warnings. Logs are retained in
`artifacts/oversteer-pivot/pipeline-revalidation/`. The pre-existing London UV
validation errors and broader pivot acceptance work listed below remain open.

The latest user instruction supersedes the exhaustive matrix: **50 screenshots
maximum for a whole run, including incidental images**. The standard static
vehicle run is 42 (14 each for Civic/MX-5/Evo): four track quarters, all eight
isolated azimuths (including two rolled grazing/backlight views), top and underside. Targeted
smokes use six per car. Do not split an exhaustive matrix into runs to evade the
ceiling. See [the capture contract](../../tools/game/inspection/README.md).

## Vehicle inspection and race-start repair — accepted checks, 2026-11-04

This section supersedes the older capture counts and unresolved sampler/launch
findings below. The broader pivot remains incomplete.

- **Camera and timing:** the 14-view matrix covers all eight isolated azimuths,
  four course quarters, top and underside, with ±20° rolled lighting views.
  Projected mesh bounds are centered after roll within one pixel. Course camera
  elevations adapt to oriented rival bounds when needed; requested/actual angles
  are recorded without extra images. `capture_ms` matches capture-begin/complete
  JSONL timestamps. The default freeze is exactly input frame 332, after the final
  frame-330 input event; an explicit CLI override is identified as partial.
- **Startup:** inspection driving loads only participating cars and the course.
  Duplicate loading progress polls update counts/stall duration instead of adding
  rows. The final Civic/MX-5/Evo startup-to-freeze times are **10.838 / 10.444 /
  10.411 seconds**, compared with the reported 44.4-second baseline. GLB loading
  took 3.704 / 3.205 / 3.197 seconds; mesh extraction took 35 / 46 / 38 ms;
  cumulative physics CPU took 17.1 / 18.9 / 16.7 ms across 515 advance calls.
  Scene-sync CPU and frames with shader-pipeline compilation are logged separately.
  These are diagnostic runs, not FPS benchmarks. Godot does not expose isolated
  asynchronous shader-compiler CPU duration; compilation-bearing frame wall time
  includes other work and must not be presented as that duration.
- **Track and lighting:** ray/UV inspection traced mirrored lettering to the back
  of double-sided London signs. The repair adds outward back faces with corrected
  atlas UVs, preserving front lettering and other artwork. Road texture imports
  now generate mip chains and use anisotropic samplers; runtime checks inspect the
  actual textures. A coherent dusk sky, explicit sky reflections and sun energy
  0.9 replace the mismatched dark sky/2.5-energy sun.
- **Vehicle materials:** the three representative assets have baked, right-handed
  wheel transforms, outward wheel/tire winding and normals, back-face culling and
  opaque tire alpha. Paint overrides retain source texture sampler/repeat settings,
  fixing the MX-5 windshield stripes, and use gloss roughness/metallic/clearcoat.
  Race roots are named `RaceCar_N`. Material checks now cover basis determinants,
  orthonormality, culling, tire alpha and effective gloss roughness. Godot cull mode
  2 means **disabled**, not front-face culling; mode 0 is back-face culling.
- **Countdown and rivals:** core grid lock was already present and now has a
  full-control regression. Stale covered-window captures caused the apparent
  HUD/simulation disagreement; capture now forces a current nonpresenting draw.
  The centered countdown/GO label uses large typography. AI launch fixes correct
  behind-grid lateral-distance measurement, segment selection, initial lane
  retention and traffic braking. All six rivals now launch at 33–55 kph and above
  idle RPM at input frame 166 in the native probe. Each has its own paint and plate;
  player upgrades/customization are no longer copied to rivals.

Acceptance evidence:

- [Final static gallery](../../build/verification/pivot-pipeline-accepted/index.html):
  **42 PNGs**, all three cars pass every technical check, no incidental captures
  or focus violations. All course views were visually reviewed after the camera
  clearance fix; the prior 42-image iteration supplied the full material review.
- [Native countdown/GO/launch report](../../build/verification/pivot-sign-fixed/race-start-check.json):
  passes with **2 PNGs**, zero countdown movement, synchronized time/speed and all
  six rivals launching. The countdown screenshot confirms readable London signs.
- [Wheel motion suite](../../build/verification/pivot-wheel-motion-final/):
  **39 PNGs**, three cases pass. All 288 rendered-wheel basis observations match
  expected steering/spin transforms within 2.91e-7; active tire/contact-plane
  penetration is below 0.0001 mm (floating-point noise). Adjacent frames show
  current HUD time and wheel rotation, rather than cached viewport images.
- `cargo test -p oversteer-core --locked`: **104 passed**. Source gate: **28 Rust
  library tests**, **58 Python tests**, strict Clippy, formatting and Ruff pass.
  Two additional asset geometry/UV/idempotence tests pass with the assets group.
  All three repaired car GLBs pass Khronos validation with zero errors/warnings.

Remaining limits: London has **130 pre-existing UV semantic validation errors**
both before and after the sign repair (127 continuity, 3 missing texcoord errors).
The repair does not claim to fix those. Wheel asset repair is accepted for these
three cars, not the full roster. Civic window trim, coarse lamp textures, faceted
bodywork, cabin detail and remaining track branding still need visual refinement.
Full-lock/airborne/collision handling, second-course coverage, career and packaged
release acceptance remain open in the plan above.

Primary API references: [Godot culling/material properties](https://docs.godotengine.org/en/4.6/classes/class_basematerial3d.html)
and [sky/reflection environment](https://docs.godotengine.org/en/4.6/classes/class_environment.html).
Runtime acceptance uses the pinned 4.7.2 engine.

### Previously Visible

The wheel audit provided motion-paired images and contact telemetry. The first
exhaustive static run completed 912 planned views but also generated 312 incidental
images, **1,224 total**, through the older periodic scenario capture path. That
method is retired. Existing evidence is retained, not treated as visual acceptance.

### Blind Spots Identified

- Restoring a source GLB with its old timestamp left an experimentally changed
  import cached. Source hashes alone did not establish actual runtime materials.
- The pinned Godot signature prevented external Metal capture. Capture support
  requires a separately signed diagnostic copy; the shipping/pinned engine stays
  intact.
- A wait for automatic `frame_post_draw` can stall when macOS stops drawing a
  covered window. A capture probe stalled; it was stopped and remains failed.
- The original screenshot budget refusal was logged but overwritten by the final
  successful exit. A zero-budget reproducer exposed this; the exit now remains 1.

### What Changed

- Runtime snapshots now include bounded command/input history, wheel/contact
  measurements and effective material properties. Each inspection PNG has camera,
  framing, lighting and render-frame diagnostics; JSONL records interrupted work.
- Source GLB alpha/transparency is compared with the actual imported factory
  material. The stale import was reproduced, then corrected by protected reimport.
  A glass refinement experiment was visually rejected and restored; no accepted
  glass fix is claimed. All three representative GLBs passed Khronos validation
  with zero errors/warnings.
- Removed periodic/duplicate scenario captures. Runtime capture calls have a hard
  limit of 50, with the verification runner passing the remaining run budget to
  each case. Oversized suites are rejected before launch. Wheel-motion coverage
  is now six azimuths with adjacent-tick pairs, plus final checkpoints (39 planned
  images across three cars); that reduced motion suite has not yet been rerun.
- `pivot-essential-standard` passed with exactly **36 PNGs**, no incidental PNGs,
  1080p framing, unchanged frozen simulation/assets and focus protection. Sampled
  images still show black glass, MX-5 windshield striping, faceted highlights and
  weak interior detail; these remain defects, not capture failures.
- The opt-in diagnostic engine preserves entitlements and adds `get-task-allow`.
  `pivot-metal-essential-smoke` passed with six PNGs and a **501,873,964-byte**
  presented-frame trace. `gpudebug` opened its 2 command buffers, 17 encoders and
  936 draw calls. This verifies capture and static trace inspection; GPU replay,
  texture extraction and performance profiling have not been claimed as tested.
- Inspection explicitly renders settled viewport frames without presenting them
  or activating a window. GPU tracing selects a presented layer when drawable;
  its covered-window fallback is explicitly a main-queue command buffer, not a
  full presented frame. That fallback selection has unit coverage; actual
  covered-window GPU capture remains unverified.
- Source gate passed: 27 Rust library tests, 54 Python tests, formatting, Ruff and
  strict Clippy. The native zero-budget check produced no PNGs and failed as
  intended; the old 122-image roster plan was rejected before launch.

### Next Iteration Targets

Use the smaller standard to diagnose the visible material defects. Continue the
career, driver, second-course, physics and packaging work in the matrix above.
Diagnostics do not change the incomplete state of that broader plan. Research
and evidence sources: [tools](../research/VEHICLE_INSPECTION_TOOLS.md),
[Metal capture solution](../research/METAL_CAPTURE_LIMITATION.md).

## Baseline

- `tools/game/dev.py doctor --runtime` passed on the current workspace.
- `tools/game/dev.py check` passed: formatting, strict Clippy, Ruff, 29 Rust
  library tests and 41 Python tests. This does not establish runtime quality.
- Native title, menu, career and quick-race baseline scenarios passed their
  existing technical checks in `build/verification/pivot-baseline-screens/`.
  Manual inspection of the menu confirmed the Juiced logo, vivid tunnel,
  source typography and tilted camera still defined the presentation.
- Pre-pivot uncommitted changes and runtime DLL/content identities were retained
  in `artifacts/oversteer-pivot/baseline/`. Debug and release DLLs differed;
  baseline rendered evidence belongs to the debug identity in that manifest.

## Implemented and checked so far

- Removed branded startup videos and source-logo main menu. Main/title/career
  navigation now uses restrained typography and panels, with a level camera and
  neutral showroom lights. The Options overlap observed in the first captures
  was repaired; final layout inspection remains part of the next native run.
- Removed the character-editor module from the frontend build and its navigation,
  input handlers and original actor rendering. The pre-existing `avatar.rs` and
  NPC-profile work remain on disk as uncompiled historical work; they are not
  the replacement driver implementation. Driver name is editable in Options.
- The user rejected the cartoon Kenney candidate. Its sources, preparation
  worker and generated assets have been moved out of playable content to
  `artifacts/oversteer-pivot/driver/rejected-kenney/`. A fixed adult streetwear
  model now uses the existing character geometry and CrewIdle animation without
  restoring customization. In-game proportions and moving poses were inspected
  in `pivot-streetwear-grid-pass2`; materials/facial finish remain unaccepted.
- New native onboarding verification failed on the preceding binary's missing
  name-control behavior, then passed on `f33d90df873e5c0af908b94ccd473dbf08a5229f6560bc704fe9afafc799372e`:
  23 onboarding checks and 16 separate-process relaunch checks passed, with
  14 screenshots retained in `build/verification/pivot-onboarding-pass1/`.
  This proves the exercised navigation/name persistence, not career completion.
- The source gate passed after the editor removal: 24 remaining Rust library
  tests and 41 Python tests, plus formatting, strict Clippy and Ruff. Five
  original character-editor tests no longer belong to the compiled frontend.
- At the user's request, visual scenarios now retain a screenshot every 60
  frames, action plans capture every transition, and galleries expose all PNGs.
  Performance scenarios omit periodic screenshots to preserve timing validity.

## Verification evidence

The earlier `build/verification/pivot-ui-pass2/` exercised menu angle/paint,
Options wrapping, name save/relaunch and the replacement driver's betting-screen
appearance. All three cases passed their technical checks (23/16/22 checks),
retaining 24 PNGs. Visual review found a T-pose despite the Idle player running,
remaining HIN branding and unstable/clipped betting-screen framing. Those
captures were rejected; subsequent fixes and remaining limits are listed below.

The user permits windows but requires that automated runs never steal desktop
focus. Verification now installs a development-only AppKit focus guard into the
unchanged pinned Godot process, with a headless preflight that fails closed if
it cannot load. It suppresses application/window activation, leaving real Metal
rendering and game code intact. Asset imports use the same protection. The first
`pivot-background-probe` onboarding run passed, retained 1080p Metal screenshots
and reported no activation violation. Interactive desktop focus/input and final
foreground performance are separate acceptance checks; this guard is not part
of the shipped game.

The initial guard later caught one real activation in
`pivot-background-refinement/pivot-onboarding`; that batch is not a focus pass.
That revision forced macOS accessory-app startup and suppressed the newer
cooperative activation entry point. `pivot-background-accessory-probe` then
passed onboarding. `pivot-background-input` passed both keyboard-right and
controller-right scenarios (27 checks each), including actual input polling,
vehicle heading/displacement and no activation violation. Its content, binary
and verification-tool identity gates passed. Three focused Python tests check
that an unavailable/ignored guard cancels before any rendered launch.

A later, longer asset import exposed another activation under accessory policy.
The current guard forces `NSApplicationActivationPolicyProhibited`, while still
allowing Metal viewport rendering and injected game input. Imports now fail
when the guard reports a violation. Both three-car wheel batches
(`pivot-wheel-audit-three-layouts` and `pivot-wheel-audit-corrected`) passed the
focus guard; the earlier long import is not a focus pass.

## Latest implementation work

- Replaced the source speedometer/minimap artwork with quiet instrument panels,
  a redline-aware rev bar and a nitrous bar. `pivot-independent-hud` passed the
  rendered keyboard-steering case and focus guard; the 1080p capture was visually
  inspected. The opponent list now follows the same ranking as live position and
  result settlement; a drift-score regression failed before the fix and passes
  afterward.
- Reproduced a world geometry decoder defect: BDL descriptor +12 distinguishes
  strips (0) from triangle lists (1), but recovery treated both as strips. London
  has 241 list draws, all with index counts divisible by three. The disconnected
  face regression failed before the fix; strip restart/winding still passes.
  `repair_world_indices.py` preserves prepared transforms, UVs, materials and
  vertex buffers while correcting indices. The first London circuit repair
  changes those draws from 153,504 to 57,974 triangles; a second pass makes no
  changes. Before-assets and source-hashed reports are retained in
  `artifacts/oversteer-pivot/world-topology`. All 33 runtime tracks were repaired
  (6,233 draws; 3,881,768 spurious triangles removed). London rendered checks
  passed in `pivot-world-topology`; the stray faces are gone. Remaining tarmac
  variants using `baseTexture` now use world-space paving coordinates;
  `pivot-road-material` passed and was visually inspected. The other 32 tracks
  have not all received visual acceptance.
- The fixed adult driver now uses a charcoal tee, skin on the exposed arms,
  textured denim and trainers. The old preview mistakenly assigned shirt blue
  to the bare-arm draw group. `prepare_fixed_driver.py` produces a separate
  runtime asset with texture provenance; the source assembly, geometry, rig and
  animation data are unchanged. `pivot-driver-materials` passed its betting UI
  checks and focus guard; multiple animated captures were inspected. The face
  remains a low-detail common head, not a newly authored realistic character.
- `pivot-evo-mass-driving` passed the actual input/heading checks and focus guard.
  The runtime motion path takes the corrected base mass; no native performance
  definition overrides it for this car. The short driving capture is not full
  handling acceptance. Inspection exposed stretched road materials, remaining
  branded speedometer art and an overly close collision camera; these remain
  visual acceptance failures until repaired and recaptured.
- Removed HIN branding from the betting screen and race HUD. Betting controls
  have separate side panels. Grid entry now snaps to a stable camera instead of
  interpolating through the car from the previous menu. Three successive
  `pivot-streetwear-grid-pass2` captures confirm stable framing and animation.
- Replaced the broken imported showroom backdrop with a small independent
  workshop scene. First captures exposed overly warm outdoor lighting. Neutral
  indoor lighting and contact shadows were inspected in the later refinement
  captures. Surface detail and materials still need work; this is not final
  environment acceptance.
- Added five focused wager tests. The initial four reproduced three failures:
  restart placed an additional bet, pink slips were not forfeited immediately,
  and navigation did not settle abandonment. Restart now forfeits once and
  restarts without a new bet; leaving clears the race and forfeits accepted
  stakes, with last-car protection. Pause/resume preserves the stake. Direct
  StartRace/Continue cannot silently discard an unfinished race. The 89 existing
  core integration tests passed after updating the old restart expectation.
- Frontend restart/navigation now persist forfeitures; intentional quit settles
  abandonment, while scenario completion does not create a synthetic penalty.
  Pause text explains the consequences. End-to-end wager/persistence captures,
  crash recovery and other entry paths still require validation.
- `pivot-workshop-pass1` passed all three case-level checks, but its overall
  identity gate failed because the verification script changed during the run.
  Retain its screenshots as diagnostic evidence; do not call it a clean run.
- The latest source gate passed with 27 Rust library tests and 46 Python tests,
  formatting, Ruff and strict Clippy. Five pivot wager tests and the focused Evo
  mass regression also pass. The 89-test core integration suite and focused wager/handling tests passed
  after the vehicle correction and live-standings change.

## Next concrete work

- The user requested twelve in-race camera angles, with explicit attention to
  wheel spin, traction, road contact and clipping. The new `wheel-audit` suite
  captures paired adjacent-tick images at 30-degree intervals for the Civic,
  MX-5 and Evo, using real controller input through the normal simulation.
  Image-side JSON records wheel angular speeds/angles, steering, contacts and
  measured rendered-vertex clearance from each contact plane. The corrected
  mapping batch retained 72 angle PNGs, and all 36 main views were inspected.
  It exposed swapped donor/physics sides: the chassis half-turn reverses X.
  Animation and measurements now use the correct physics wheel index, with a
  red/green regression. Launch/coasting/handbrake telemetry and adjacent images
  confirm driven-wheel slip, rolling and rear-wheel lock.
- The same captures exposed fixed wheel rest positions during body suspension
  motion (worst tire/contact-plane penetration: Evo 28.36 mm, Civic 4.73 mm,
  MX-5 1.85 mm). Rendering now moves each rim/tire pair along the chassis
  suspension axis to its sampled contact plane, bounded by that axle’s travel.
  Airborne wheels retain rest placement; simulated angles/steering are unchanged.
  A focused contact-travel regression failed before implementation and passes.
  `pivot-wheel-contact` was stopped after discovering that repeated mesh-buffer
  reads stalled rendering. Static wheel vertices are now cached on their mesh;
  transforms and contact clearance are still evaluated every frame.
  `pivot-wheel-contact-cached` passed all three cases, identity gates and the
  focus guard, retaining 72 angle PNGs. All 36 primary views were inspected.
  All 288 active-tire measurements are within 0.0003 mm of their contact plane.
  Every recorded physics position, rotation, control, contact, wheel angle and
  angular speed matches the preceding mapping-only batch exactly: the visual
  suspension correction did not change the simulation.
- `pivot-wheel-evo-clear` adds 24 Evo images using gentler steering to keep
  barriers out of all twelve views. It passed the same runtime/identity/focus
  checks, and all twelve primary views were inspected. The original harder-turn
  run remains as evidence. The curated gallery is
  `build/verification/pivot-wheel-review/index.html`: 72 selected PNGs with
  adjacent-tick toggles, telemetry links and per-wheel measurements. Comparing
  rendered basis changes against contact-normal cross travel-velocity confirms
  correct rolling direction on all four wheels of each car during coasting.
  Rear-wheel angle changes stop under the handbrake while fronts continue.
  These captures do not establish airborne, curb, maximum-steering body
  clearance or full-roster acceptance. Glass, headlight materials, jagged shadows
  and harsh illumination remain visibly unfinished. The captured DLL is
  `844307338a45b2d9a43d24416eaf2215dde1ea51ac9ca909da8b277ebc9e4c64`;
  the release/export build has not yet been updated with these changes.
- Finish wager entry/quit/crash persistence verification, including other entry
  commands that might replace an unfinished race. Add rendered pause/restart
  evidence; the current five focused tests cover core state, not every UI path.
- Replace the 403+ inherited contests and ten source leagues with the accepted
  independent tiers and explicitly curated courses/events. A bounded `jg`
  discovery of `tools/game/assets` was incomplete; direct reads identified
  `build_content.py`, `bind_profiles.py`, `build_native_career.py` and
  `bind_native_leagues.py` as generation seams. Preserve raw recovery evidence.
- Correct the Evo's 320 kg runtime mass. `bind_profiles.py` takes this from a
  secondary catalog's `curbWeightKg`, overriding its already implausible donor
  profile. Mitsubishi's January 2003 press kit, Principal Specifications p.19,
  lists the Japan GSR at 1410 kg and a six-speed gearbox. The existing runtime
  has five generic ratios. Source: [original manufacturer press kit, mirrored PDF](https://manuals.plus/m/fdc11d3e0b0e28c4f27fc136e20427efdfd3df9e720ba5ec4dd21c17e0d6299b.pdf).
  The independent runtime now corrects mass to 1410 kg without rewriting the
  recovered catalog. Its focused regression failed at 320 kg before the fix,
  then passed. The five generic gears remain an audit item. Capture/test the
  revised motion before accepting the car's handling.
- Scenario presentation metadata now describes the actual workshop/fixed-driver
  paths. Reports retain the raw catalog hash and separately record the refined
  runtime-content hash and applied mass correction.

## PR #2 pink-slip restart review fix — 2026-11-04

- Acceptance: after forfeiting a pink-slip stake through Restart, rendered race
  car identities must match the replacement race's car identities; cash restarts
  must still render the retained car. Preserve settlement and save behavior.
- Verification budget: 20 native screenshots total (8 before, 12 after), including
  purchase setup and final captures. Use the background focus guard.
- Reproduced with `verify.py --suite pivot-wagers --case wager-purchase --case
  wager-pink-restart --output build/verification/pr2-restart-before`: only the new
  `rendered_cars_match_restarted_race` assertion failed. Physics used the Mini;
  the rendered node and inspected final capture still showed the Civic.
- Clear the loaded race key, car effects and rendered cars when the selected car
  changes during a race. The existing loader then preloads and rebuilds the cars.
- The same cases plus `--case wager-cash-restart` passed in
  `build/verification/pr2-restart-after`. Inspected final captures show the Mini
  after pink-slip forfeiture and the Civic after cash forfeiture. All rendered
  car identities match the race snapshots. Settlement, save and focus checks pass.
- Used exactly 20 screenshots (8 before, 12 after). `dev.py check` passed formatting,
  strict Clippy, 28 Rust library tests and 66 Python tests; the focused
  `pivot_wagers` and `pivot_race_start` suites passed all 13 tests.

## Remaining acceptance work

- Finish restrained presentation across every retained menu, HUD and transition;
  remove remaining Juiced identity-bearing content from playable paths.
- Import and validate one premade neutral driver; remove character customization
  and replace remaining original character appearances.
- Select and validate the representative FWD/RWD/AWD cars and two tracks, then
  extend visual/driving/customization checks across the retained 30-car roster.
- Reproduce and fix driving, collision, AI, camera, material and track defects.
- Implement clear career tiers; defer crew/DNA/spooking/sponsor progression.
- Validate cash/pink-slip outcomes, voluntary forfeiture, crash recovery,
  last-car protection and no-stake earning without progression dead ends.
- Verify new career saving and relaunch; no legacy player-save migration needed.
- Measure 1080p/60 FPS on the current final build and validate the independent
  offline macOS export, with packaged assets and retained evidence.
- Explicitly inventory retained/deferred content and review all retained paths;
  source checks or the first polished slice alone cannot close the goal.

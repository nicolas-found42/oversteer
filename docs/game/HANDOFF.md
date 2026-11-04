# Paused implementation handoff

Updated 2026-11-03 through pushed source/tooling baseline
`ada2864be4a2225a580ead13ae081c970f88d74f` on `main`. Gameplay implementation is
PAUSED at the user's request, not complete. Resume implementation only when the
user requests it; do not restart the interview. Subsequent cleanup, tooling,
reference-review UI and documentation work do not resume gameplay.

The implementation agents were interrupted at the original pause; no Cargo/game
scenario process was then running. Current source checks and hosted CI passed,
but no new native gameplay or release qualification was performed.

## Read first

1. Root `AGENTS.md`, `docs/agents/domain.md`, `GLOSSARY.md`, and `docs/adr/`.
2. Canonical specification: https://github.com/nicolas-found42/oversteer/issues/1.
   Tracked matching body: `docs/game/SPEC.md`. The ignored
   `artifacts/juiced2-build/spec-issue.md` is the historical pause snapshot;
   use the GitHub issue and tracked specification for current instructions.
3. `docs/design/JUICED2_REBUILD_INTERVIEW.md`, `docs/game/README.md`,
   `docs/references/juiced2/README.md`, and `tools/game/assets/README.md`.
4. This handoff and the exact checkpoint manifests below. The specification gives
   scope; these manifests establish what ran and which source/data bytes it used.

The user approved implementation without further consultation. Do not restart the
interview. Exact stack is Godot4.7.2 + gdext0.5.5/api-4-7, Apple Silicon only.
Rust core owns simulation/game state; Godot Metal4/Forward+ owns presentation.
Full singleplayer, 30 accepted donors, 33 courses, 403 career +60 sponsor contests,
10 leagues/261 goals. Multiplayer and wheel force feedback are deferred. The six
release evidence groups in issue1 remain open; technical passes are not completion.

## Resume order after the user requests gameplay work

1. Read the specification and this handoff, inspect `git status`, and run source
   preflight. Inventory the local inputs below before attempting runtime work.
2. Preserve the deployed `16a65` DLL/content identities. Diagnose the inspection
   camera and avatar fixes with the bounded all30/avatar suites below; review
   distinct visible-car captures, save/relaunch and the original comparison frames.
3. Before building current sources, archive their exact Cargo/Rust/embedded-data
   inputs into a new compile boundary. Keep the earlier deployments/checkpoints
   available and qualify only the new DLL/content pair actually executed.
4. Complete the source-backed performance/license/prototype/league-selection
   rules and primary donor stock audit together. Validate all 30 ranges and all 463
   event reachability before publishing corrected content; choose the eligible
   starter from those results and update verifier expectations consistently.
5. Run a fresh legal full career, complete outstanding reference/material/NPC/UI
   repairs and human evidence review, then repeat all30 customization/persistence,
   independent exported-app recovery and 1080p60 release evidence.

The detailed failure evidence and unfinished rule bindings later in this document
are part of that plan. Green source CI does not close any release evidence group.

## Workspace and portability

Workspace: `/Users/nicolas/Documents/github/oversteer`.
The implementation pause originally left HEAD at `8dd1fdf` with untracked source.
The user subsequently requested committing and pushing all current work. Source,
configuration, reviewed metadata, specification and this handoff are now versioned
in a retrospective Conventional Commit series. Exact retained source snapshots
were staged in their original checkpoint order without changing live source bytes.
See `COMMIT_HISTORY.md` for the recorded sequence and its limits.
Do not discard the ignored local asset/evidence directories.

A fresh agent IN THIS WORKSPACE can continue after reading these records and
checking the code. A fresh clone now contains the implementation source, but cannot
reproduce the complete runnable state from Git alone.
Preserve or transfer the ignored local vault, original-image/recompiled-source
intake, converted assets, staged corrections and checkpoints. Public tool and
dependency caches can be rebuilt from pins; they do not replace unique local evidence.
Lightweight checkpoint manifests, source-authored contracts and donor-stock audit
summaries are versioned under `docs/game/evidence/`; their referenced raw files
remain local. They do not make all original recovery inputs available in a clone.
The `origin` remote is `https://github.com/nicolas-found42/oversteer.git`. Use explicit
`--repo nicolas-found42/oversteer` for the agreed issue tracker.
Never expose configured API credentials.

| Local path | Required for |
| --- | --- |
| `resources/games/juiced-2/juiced-2-hot-import-nights.iso` | Original non-car recovery; user-supplied, absent from a clone. |
| `artifacts/carmodels-research/models/` | Accepted pinned donor GLBs; source IDs/hashes are tracked in `data/juiced2/accepted-roster.json`. |
| `artifacts/juiced2-recovery/` | Original-code/artifact intake and recovery evidence. |
| `artifacts/juiced2-build/` | Reference-test fixtures, compile/runtime checkpoints and staged donor corrections. |
| `artifacts/juiced2-vault/` | Original videos/images, classifications and retained human-review pilot. |
| `godot/assets/`, `godot/bin/`, `godot/.godot/` | Prepared runtime resources, deployed extensions and import cache. |
| `build/tools/`, `build/verification/`, `build/packages/` | Pinned applications, historical captures/comparisons and older exported apps. |

Use `tools/game/assets/README.md` for recovery prerequisites and production steps.
Its commands can write runtime assets and tracked content; source validation does
not run them. Preserve the current staged stock corrections and known-failure
captures before rebuilding. A fresh clone can check sources immediately after
installing source tools, but cannot reproduce the retained runnable/evidence state alone.

## Developer tooling update after the pause

The Rust/Godot workspace is the maintained game path. Cleanup removed the
superseded application's sources/tests, build wrappers, vendor headers, scenario
baselines, appearance inspector and 2D sprite generation/atlases, plus their
workflows and documentation. Root onboarding, VS Code tasks/debugger settings,
hooks and CI now describe the native project. Required shared donor inputs remain:

- `tools/carmodels/assets.py`: hash checks, selected-scene GLB decoding and node transforms.
- `tools/carmodels/preview_materials.mjs` and `tools/carmodels/source_viewer/gt4-materials.mjs`: pinned material translation.
- `data/carmodels/profiles/` and source metadata: donor input provenance; numeric estimates and known defects still require review.
- `tools/visual/package*.json`: Playwright dependency for reference-review browser tests.

Published maintenance changes through `ada2864` are:

| Commit | Result |
| --- | --- |
| `36b9ab4` | Repository cleanup and Python source inventory that excludes deleted files. |
| `1ab4f1a` | Final newlines in `crates/oversteer-core/data/native-drivers.json` and `data/juiced2/wheels.json`; JSON values unchanged. |
| `48e6440` | Reviewer-name entry removed from the reference review page; backup schema remains compatible. |
| `ada2864` | Hierarchical reference labels and broad-category answers, with scoring, browser tests and documentation. |

These follow the developer-tooling adoption recorded in
`docs/references/juiced2/devtools-implementation.md`. `COMMIT_HISTORY.md` records
the earlier retrospective implementation series, not these later maintenance commits.

### Start with source checks

Run from the repository root on Apple Silicon, after installing rustup, uv and
Apple command-line developer tools:

```sh
git status --short
uv run --frozen python tools/game/dev.py doctor
uv run --frozen python tools/game/dev.py check
uv run --frozen pre-commit run --all-files
```

`rust-toolchain.toml` pins Rust 1.99.0, rustfmt/Clippy and the ARM64 target;
`.python-version` pins Python 3.13.16. `pyproject.toml`/`uv.lock` own dependencies:
Ruff 0.15.20, pre-commit 4.7.0, NumPy 2.5.4 and Pillow 13.0.0. CI pins uv 0.13.6.
Compatibility requirements exports are not a second dependency authority.

`dev.py check` checks formatting, compiles Python in memory without importing
recovery workers, runs strict all-target Clippy and root Ruff, then Rust library
and Python unit suites. `format` explicitly rewrites supported formatting;
`lint` and `test` are narrower commands. Recovery workers retain a documented
advisory style audit; the mandatory correctness/syntax gate covers them.
Hooks may rewrite Python/whitespace, while the Rust hook checks only. Hook
installation is explicit per clone: `uv run --frozen pre-commit install`.
Retained checkpoint evidence is excluded from whitespace rewriting.

No original media, prepared assets or Godot install is required for the source
gate. An optional Python browser regression skips when its local corpus or
Playwright inputs are absent; it is not evidence of a fresh clone's browser coverage.

For this prepared workspace, the additional checks are:

```sh
uv run --frozen python tools/game/dev.py reference-tests
uv run --frozen python tools/game/dev.py doctor --runtime
npm test --prefix tools/visual
```

`reference-tests` requires retained local recovery fixtures and fails explicitly
when they are missing. It runs all workspace Rust tests; `build.py test` also runs
the full workspace suite and is not the source-only default. Runtime doctor queries
the pinned Godot version, checks ARM64 binaries and import metadata without rendering.
Browser setup, when needed, is `npm ci --prefix tools/visual` followed by
`npm exec --prefix tools/visual -- playwright install chromium`; the local vault
is also required. The browser harness builds the current template in a temporary
pilot and uses synthetic answers without changing the human pilot.

At `ada2864`, validation passed 27 Rust library tests and 36 Python tests
(16 game-tool, 6 donor-helper, 14 reference-review), plus the prepared 116-test Rust
suite (the same 27 library tests +89 core integration tests), all hooks,
lock/configuration checks, browser verification and runtime preflight.
[Hosted ARM64 source CI passed that exact revision](https://github.com/nicolas-found42/oversteer/actions/runs/41736476548).
That job runs the same source gate on `macos-26`; it does not prepare original
assets, run native scenarios or qualify M5 Pro rendering/performance.

### Builds and editor behavior

`uv run --frozen python tools/game/build.py build --profile dev --skip-import`
builds/copies only the debug-path extension without preparing/importing assets.
It replaces the historical debug deployment, so archive its identity first when
preserving a diagnosis target. Normal `build` defaults to release, updates both
debug/release deployment paths and performs a native-renderer import; export
requires release. Close Godot before rebuilding: loaded-library guards run before
and after compilation. Imports reject logged errors even after a successful exit.

VS Code defaults to native check/dev-build tasks, rust-analyzer, CodeLLDB and Ruff.
The LLDB profile launches the pinned Godot host with the dev extension and requires
prepared assets; actual breakpoint behavior remains unverified. No debugger
entitlements or host signing were changed. See `docs/game/README.md` for commands.

### Reference review status

The blind 200-example pilot hides model predictions, confidence and split
assignments. The UI supports category buttons, breadcrumbs, search, exact labels,
broader categories and explicit uncertainty, with browser persistence and backup
import/export. Broad categories retain their chosen path but count as unresolved
for exact-label precision. Scoring reports eligibility and never changes
automatic-acceptance flags. No synthetic test answers are human gold judgments.

`artifacts/juiced2-vault/review-pilot/` is the retained local pilot. Its generated
page need not match the latest tracked template. Build a separate pilot with
`uv run --frozen python tools/references/review_pilot.py build --output /absolute/new-pilot-directory`;
the output must not exist. Preserve existing reviews and exported answers. When
scoring a separately built pilot, pass its `--manifest` explicitly and choose a
new report filename. See `docs/references/juiced2/README.md` for the sampling and
scoring contract. Human adjudication and release screen/state acceptance remain open.

The DLL `16a65` and runtime hashes below are still historical deployments. Tooling,
style and newline-only embedded-JSON changes are later source inputs, not a newly
qualified runtime. Archive a new exact compile boundary before new gameplay evidence.

## Historical compiled source/runtime boundary

Current debug AND release DLL:
`16a65c105ffbff23ded469d7f53dce7c0c8a5df2b8b5077c496ce880a6c175cf`.
Runtime game-content SHA256:
`d5f6fabc4a921551f3b583e0229f1bbe7fee2bae2f2196b2671d353920d65ebe`.
Avatar components SHA256:
`b7486defc8365b7926216d222a14c8765cfa5863762daaba8ba7ee273a951502`.

Before-compiler source snapshot:
`artifacts/juiced2-build/checkpoints/precompile-20261103T214358Z/`.
Its exact70 inputs, archived copies AND live source rehashed unchanged at pause.
Input manifest: `compile-inputs-before.json`, SHA256
`7243dc20330dc9d9745d754ed0048fcb528d22c87e02f1a53e3de5fd4383d892`.
`compile-result.json` records the result and identities; this directory does not
use the `manifest.json` filename of the earlier runtime checkpoints.
Compile result:94 core/22 frontend checks passed; release compilation exit0.
This narrow build adds creator gender/preset phase layout corrections and the
paint-booth inspection camera fix, plus pure performance helpers. It DOES NOT
include numeric entry/package integration, a MINI starter or new stock data.
**No native GPU/scenario run of this DLL has been performed yet.**

Current content still starts with the historical Civic and contains the known
Evo320kg input defect. Do not treat that as corrected or final legal career data.
Do not publish partial stock corrections while a native suite is running.

## Established evidence and failures

- `artifacts/juiced2-build/checkpoints/168892b6/manifest.json`: prior DLL168892b6,
  exact69 precompile files,93 core/22 frontend checks,22 native cases and538
  retained file hashes; includes a full copy of D5 game-content.
- Those native cases:19 UI cases (six paint families, full72-byte records/scalars,
  source stage Back/cancel, identical-material paid acceptance, avatar/relaunch),
  all30 technical-state +relaunch, and observed stock NOS replay.
- Critical visual rejection: ALL150 all30 PNGs were the SAME exterior booth wall.
  Material/state checks passed but cars were invisible. Independent review and
  failed new diversity guards are retained in
  `artifacts/juiced2-build/checkpoints/168892b6-visual-review/`.
  Do not cite these as visible customization proof.
- Cause: `preview_angle=Some` skipped the inside PaintBox camera and selected a
  generic camera outside the booth. Controlled unchanged168892 diagnostic, camera
  override ONLY, shows a whole Civic and distinct stock/modified front/rear views:
  `artifacts/juiced2-build/paint-camera-occlusion/causal-result.json` +`fixed/`.
  This is ONE donor diagnostic, not a compiled full-roster pass.
- NOS actual replay:21,371 controls /41,383 real Godot events, natural Rookie
  circuit win,3478 requests/561 active ticks/85 recharge ticks/minfraction0;
  all38 guards passed. Historical Civic entry precedes numeric eligibility repair.
- `checkpoints/9535d0b0/manifest.json`:24 native cases passed, including earned
  Mustang1M and four-lap Obliterator replays and three formal performance cases.
  Mustang1,006,984 points/80.56939697s/4834 controls. Obliterator22,180 final-lap
  points/378.3517456s/22704 controls/8500 accepted wager. Save+reload pass.
  Earlier4bd save failure is retained: precise f64 mileage parsing fixed with
  serde_json float_roundtrip and verified by these later actual native runs.
- 9535 real-time1920x1080 benchmarks:300 warmup+1800 measured frames each.
  P95 Alps8.573ms/Tokyo9.398ms/SF8.558ms; max13.021ms,zero>16.67ms.
  GPU queries unavailable; worst-case active effects not established. These are
  NOT measurements of16a65 or a final exported app.
- Latest eight paired source/current scenes:
  `build/verification/checkpoint-9535-comparisons/` and
  `checkpoint-9535-comparison-judgments/`:6 repair-required/2 review-required.
  No visual acceptance. Actor/car framing, floor reflections, venue/light/text
  differences remain. Creator shell culling is an explicitly documented adapter.
- Older moved/signed d8 export passed OS network/checkout denial, prepared replays,
  all30/relaunch and performance. It predates current sources. Final independent
  ARM64 app export/save interruption/recovery/performance must be repeated.

## Immediate verification after an explicit resume

The deployed16a65 DLL remains available for diagnosis. Current source now has
tooling/style changes; record a new exact compile boundary before producing
evidence for a new runtime. To exercise the retained16a65 deployment first:

```sh
uv run --frozen python tools/game/verify.py --suite all30 \
  --output build/verification/resume-16a65-all30
uv run --frozen python tools/game/verify.py --suite ui \
  --case ui-native-avatar --case ui-native-avatar-relaunch \
  --output build/verification/resume-16a65-avatar
```

Choose unused output paths; preserve all previous evidence. Confirm the deployed
hashes still match this handoff before using the16a65 examples. Source tests and
runtime doctor are safe preflight; running these rendered suites requires the
explicit gameplay resume. The current parser uses `--case` with `action="append"`; both avatar cases run
in suite order and the relaunch case shares the first process's saved profile.

Review the resulting120 distinct stock/modified front/rear views manually.
30 additional PNGs intentionally alias modified-rear captures. New deterministic
capture-diversity guards in `verify.py` reject identical inspection/roster frames.
`judge_vehicle_captures.py` provides two typed image judgments with retained
requests/responses/hashes; current-wall .50/.48 was unresolved and independently
rejected, historical visible-car probe .99/.88. These judgments do not replace
manual review or establish material/reference parity.

Avatar plan is now22 visible actions: source gender/preset separation requires
return-to-gender at750, female default3 at790, adjacent preset4 at830, preset1 at870.
Per-preset/mesh/bind/morph/save guards now includeF4. Historical20-action plans are
retained in fixture history and executed checkpoint copies.

IMPORTANT: career paint/cart/dealer verifier expectations and cart action IDs
were PREPARED for `GT4_MINI0001` starter ahead of the future numeric-gated build.
Current16a65 still starts Civic. Therefore do NOT run the entire UI suite and
misdiagnose these anticipated starter mismatches as a runtime regression.
Old fixtures are under `data/juiced2/scenarios/fixture-history/`.
After the real starter change, dealer/pink `car_next` selects the Focus from MINI.
Eight replay identity/input converter tests passed at pause. Keep verifier files
unchanged during suite execution; recent runs bind tool hashes before execution.

## Pending original performance/career work

`crates/oversteer-core/src/performance.rs` has source packed decoding, factor,
price/state and donor-relative endpoint helpers. Runtime data/hook/challenge UI
integration remains unfinished. Four old engine/transmission/suspension/tyre
fields are donor adapters, NOT original Power/Handling/Weight packages.

Source rules already established in `artifacts/juiced2-build/native-performance/`:
-3 ordinary categories,4 prototype choices including EXTREME NITRO.
-State2 starts a license challenge, not a cash purchase. Original defaults own
 30 item0 licenses; items1/2 require original reward handling.
-Prototype unlock tokens/choices differ from installed parts. No token=freepart.
-Extreme Nitro selected league at car9644 is separate from float capacity9640;
 entry checks selected league against actual event league. Do not invent capacity.
-Human C558 uses RAW tuned power/mass as endpoint interpolation input. NOS force
 uses original PowerFactor, not resulting BHP ratio or WeightFactor.

ADR0007: corrected donor STOCK power/mass/drivetrain remain donor-specific.
Preserve original counterpart max P/W ceiling while adapting minimum mass by its
source mass-reduction ratio. Rejected percentage-HP-gain policy stranded muscle
progression. Raw counterpart ninefields remain provenance, not exact donor tunes.
No new runtime dataset has been published. First eligible accepted-roster starter
was MINI under current qualified inputs; recheck after primary corrections.

Reachability v2/v3 reports5 WorldClass prototype8 events blocked at PROFILE8.
Do not solve by silently remapping R34 to R33: v4 shows all463 eventually eligible
at PROFILE9 via Handling prototype9 +Power8/Weight8, with unchanged R34 mapping.
This assumes licenses/tokens/cash and is NOT a legal playthrough. Optional-goal
promotion/backtracking still needs complete source/UI verification.

New source lead from core agent: selected profile field0 and highest-unlocked
field4 appear distinct. Goal completion82221018 passes field0 into822192F0,
which indexes completion bits class*45+goal. Prototype guard8220EED0 uses field4.
Actual selection writer/UI proof still pending. Current core has one career.league
and only updates current-league goals; older-goal completion may need this axis.
Do not claim this lead is a finished port.

Root had just begun ordinary license result review (NOT completed):
`license-writer-leads-v1/820D8F00.cpp` and`820D9970.cpp` contain bit writers.
Exact helper821DD510 definition is in generated/default/juiced2_recomp.6.cpp:11877;
callers of820D9970 inrecomp.25.cpp:3002,820D8F00 inrecomp.46.cpp:3122.
Full result predicates/mode bindings remain open; no universal win-only mapping
or sponsor ordering has been accepted.

## Staged stock corrections and presentation work

Asset agent staged `artifacts/juiced2-build/donor-stock-audit/`:
`stock-corrections-v1.json`, `content-evo-mass-corrected-STAGED.json`,
`stock-identity-audit-v1.json`, original brochure/source bytes.
Mitsubishi-authored original EvoVIII brochure gives GSR1410kg (1430sunroof),
RS variants1320/1350. Existing320kg is invalid. These corrections are STAGED ONLY.
All30 inventory exposes nearest/proxy inputs; none are universally certified.
Primary identity-specific power/mass/drivetrain pass remains pending (especially
CivicEK vsEP3, R8V8 vsV10, S15 vsS14, SVTLightning, GNX). Other tune fields can
remain explicit adapters; do not call them verified original donor specifications.

Avatar original111 GLBs/100 head morphs and exact source case-folded texture/name
contracts are recovered. All19 NPC appearances have original56-attribute/component
contracts; runtime still uses generic rival preset proxies. TextureCombine
HSV/Alpha/MattAlpha integration remains unfinished. Do not substitute guessed
NPC identities, or interpret native missing accessory as a fabricated replacement.

Root recovered/independently fixture-checked car_nodamage PS619 two-tone/reflection
kernels in `native-paint-shaders/` and reference docs. Live pearl shader still uses
an approximate exponent. Active original full-car shader variant, complete BRDF,
color transfer, flake/thinfilm remain unbound. Frontend intended a later bounded
shader/material batch with native captures; it is NOT in16a65.

## Remaining full-release work

After visibility/avatar checkpoint, coordinate corrected stock dataset + original
3-package/license/prototype/numeric eligibility port, run a fresh LEGAL full career,
then complete remaining source screen/material/NPC/presentation repairs. Vault
contains16,439 classified records/205 groups, with36 singleplayer canonical lead
gaps. Category labels are review leads, never proof of complete screen behavior.
Repeat current all30 visual/state/save checks and final exported-app independence,
interruption/recovery and1080p60 performance after the final implementation.
Preserve failed evidence. Do not complete the active goal until all six agreed
release evidence groups and full scope are actually satisfied.

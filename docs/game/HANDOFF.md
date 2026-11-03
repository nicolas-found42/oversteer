# Paused implementation handoff

Recorded 2026-11-03 after the user explicitly paused work. The goal is PAUSED,
not complete. Resume implementation only when the user requests it. The three
implementation agents were interrupted; no Cargo/game scenario process was found
running at the pause check. The previously started compilation had already ended.

## Read first

1. Root `AGENTS.md`, `docs/agents/domain.md`, `GLOSSARY.md`, and `docs/adr/`.
2. Canonical specification: https://github.com/nicolas-found42/oversteer/issues/1.
   Versioned matching body: `docs/game/SPEC.md`. The original local mirror remains
   `artifacts/juiced2-build/spec-issue.md` (verified at pause).
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
The ignored local vault, original-image/recompiled-source intake, converted assets,
checkpoints and tooling caches must also remain available or be transferred.
Lightweight checkpoint manifests, source-authored contracts and donor-stock audit
summaries are versioned under `docs/game/evidence/`; their referenced raw files
remain local. They do not make all original recovery inputs available in a clone.
The `origin` remote is `https://github.com/nicolas-found42/oversteer.git`;
`upstream` is the legacy `nickth3man/drift-c` repository. Use explicit
`--repo nicolas-found42/oversteer` for the agreed issue tracker.
Never expose configured API credentials.

## Developer tooling update after the pause

Source-only developer tooling and configuration were updated after this gameplay
checkpoint: a pinned Rust/Python source gate, ARM64 CI, editor tasks, and a dev
extension build option. This does not resume gameplay implementation or validate
the runtime. The DLL `16a65` and its historical results below remain the recorded
checkpoint; current tooling/source changes are not a new compiled/rendered
checkpoint. No native scenario was run as part of the tooling update. Use
`uv run --frozen python tools/game/dev.py check` for source checks; retain the
explicit resume and native evidence requirements below.

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
Manifest SHA256: `7243dc20330dc9d9745d754ed0048fcb528d22c87e02f1a53e3de5fd4383d892`.
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
python3 tools/game/verify.py --suite all30 --output build/verification/checkpoint-16a65-all30
python3 tools/game/verify.py --suite ui --case ui-native-avatar --case ui-native-avatar-relaunch --output build/verification/checkpoint-16a65-avatar
```

The current parser uses `--case` with `action="append"`; both avatar cases run
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

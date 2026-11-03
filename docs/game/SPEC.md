# Godot/Rust Juiced 2 reconstruction

Implementation is authorized by the user's active goal: build the entire agreed game without further consultation. This is the living specification, not a claim of completed game or native parity.

## Current implementation evidence (work in progress)

- Exact Godot **4.7.2** / gdext **0.5.5** ARM64 extension runs in an actual Metal 4 / Forward+ window. Latest executed DLL SHA256: `168892b6a6ae843b9b98af47940290a34b17c2b01c7c202440977a0a6f62145f`; runtime content `d5f6fabc4a921551f3b583e0229f1bbe7fee2bae2f2196b2671d353920d65ebe`. Immutable `artifacts/juiced2-build/checkpoints/168892b6/` retains the exact **69 source/Cargo/embedded-data inputs copied before compilation**, build/test logs, the DLL, game-content file, all four native runs and **538 file hashes**. Its compiled source checkpoint passed **93 core / 22 frontend checks**. Later staged sources are separate from this executed build.
- This build passed **22 actual native cases**: **19 UI cases**, all-30 customization plus a separate-process reload, and a recorded stock-car NOS race. Paint cases cover all six separately priced native families, complete typed **72-byte records**, pearl/flake/thin-film scalar editing, source stage-by-stage Back behavior, cancellation, checkout and separate-process persistence. Reaccepting an identical paint record now creates one paid paint item and charges each checkout; the preceding build's red regression and this build's green run are both preserved. UI technical passes do not establish visual parity.
- The NOS race matched all **21,371 active control samples**, **41,383 actual Godot input events**, natural result and saved progress. Per-tick observation also matched **3,478 requests**, **561 active boost ticks**, **85 recharge ticks** and minimum tank fraction **zero**. The source-derived force, pressure, activation, drain and regeneration logic is now in this DLL. This recording uses the historical Civic starter before corrected numeric entry eligibility; it is not final legal career evidence.
- The previous immutable `9535d0b0/` checkpoint retains **24 passing native cases**. Earned Mustang London: **1,006,984 points / 80.56939697 seconds**, all **4,834** active controls. Earned four-lap Obliterator: **22,180 final-lap points / 378.3517456 seconds**, all **22,704** active controls, source-negotiated **8,500** wager and exact transactions. Both now pass actual save roundtrip and disk reload. The earlier `4bd8a7b/` Obliterator failure is retained: its exact f64 mileage parser discrepancy was reproduced and fixed with accurate JSON float parsing; the successful rerun verifies that fix.
- Formal **real-time 1920×1080** Metal performance passed on `9535d0b0`, with 300 warmup and 1,800 measured frames per case: Alps P95 **8.573 ms**, Tokyo **9.398 ms**, San Francisco **8.558 ms**. Largest measured frame **13.021 ms**; zero frames over **16.67 ms**. Actual AI, native course support and playing engine/music audio are recorded. GPU queries are unavailable and worst-case active effects remain unestablished. These results do not qualify the newer DLL or final exported app.
- All **30** pinned donor cars and **33** original courses are imported. Native CLD geometry includes bicubic roads and source-proven ruled spline walls, with curvature-bounded adaptive queries and 340 recovered starting transforms. Query triangles approximate continuous native surfaces; donor chassis proxies remain adaptations. The 30-car current run retains **150 captures**, typed paint/state/material-isolation checks and saved/reloaded changes. Its four legacy tuning fields are explicitly adapter coverage, not proof of the original three performance-package categories. Manual review rejected all **150 current captures**: they are byte-identical views of an occluding paint-booth wall, so these cannot establish visible customization. New capture-diversity guards reproduce the failure; the camera-path correction and complete roster rerun are pending. The technical-state checkpoint and separate visual rejection are both preserved. Older reviewed captures retain known interior/headlamp, plate and material differences.
- Native filenames bind **403 career + 60 offline sponsor contests**, ten leagues and 261 goals. A historical legal-input progression reached League 1, including lap quotas, endurance distances, team/multi-round events and wagers. Newly recovered source numeric package/class/entry, ordinary license-challenge and prototype/extreme-nitro rules are still being integrated; the historical progression does not establish a complete career under those later recovered rules. ADR-0007 preserves corrected donor stock inputs and original counterpart performance ceilings. An inherited **320 kg Evo** profile is being corrected against primary specifications. All-30 range and all-463 event reachability audits must finish before publishing that dataset. New eligible starter selection and full career replay remain required.
- Original supporting media includes 45 songs, 94 inline banks / 2,080 samples, 2,792 English clips, four movies, named UI art/fonts, 2,003 strings, loading tips and credits. Modular avatar intake includes **111** original-normal rigged exports, **100** head targets, 45 geometric attributes, ten original presets/all 56 levels and menu ramps. Actual imported mesh/bind/visibility/morph data is checked per interaction and after relaunch. Source material operations and all 19 individual NPC appearances have contracts; complete runtime integration remains open.
- Eight original/current comparisons for `9535d0b0` remain **six repair-required, two explicit-review-required**. Current creator-only shell culling addresses a confirmed foreground occlusion, but actor/car framing, floor reflections, lighting, venue, lettering and layout still need repair. Source gender/preset phase separation is staged after the latest DLL. Native paint shader instruction kernels have independently checked equations; this is bounded recovery, not full material parity.
- Older re-signed/moved draft exports remain separate evidence. One independently exported app passed strict signature verification, network/checkout denial, all-30/relaunch, menu/profile/settings, prepared career replays and three performance cases. It does not include current source changes. Final export, interruption/recovery and release performance checks are still required. No injected vehicle pose, velocity or score is used as driving evidence.
- The vault retains **16,439** classified records in **205** groups. Direct sequence review rejected an incorrectly classified transitional preset frame; **36** single-player groups still lack an eligible canonical-platform lead. Classification is not screen/state acceptance. The six completion groups below remain open, and **the game is not complete**.

## Accepted scope

- Godot **4.7.2** + **gdext 0.5.5**, Rust gameplay and independent recovered numerical core. Native Apple Silicon macOS only, Metal rendering, self-contained offline `.app`.
- PS3/Xbox 360 Juiced 2 shared behavioral reference. Original observable presentation, menus, race flow, career and customization are the target. Vault sequences and original artifacts take priority over probabilistic category labels.
- Complete single-player career and quick race: circuit/drift/challenge families, opponents, crew/DNA/spooking, wagers/pink slips, dealership, garage, tuning, unlocks and persistence. Multiplayer and steering-wheel force feedback are deferred.
- Exactly 30 accepted base vehicle identities from GT4, MC3 Remix, MCLA player/DLC, and Ford Racing 2 in carmodels commit `ce047799fc550cdf92e4f7b62d97ef5c603e53ad`. All 30 immediately available in quick race; earned/purchased in career. Preserve league/event structure while documenting smaller-roster eligibility/economy adaptations.
- All 30: paint/finishes, vinyl editing, wheel swaps and performance upgrades. Body/interior kits are vehicle-specific. Original supporting geometry may be authored. Correct known inherited profile errors; do not blindly reuse estimates as native tune data.
- Recover original non-car assets and scoring/AI/career/wager/unlock rules where possible; reconstruct missing assets and explicitly record remaining adaptations.
- Remappable keyboard/gamepad, English UI/speech, family-shared engine audio responding to per-car RPM/load/shifts.
- Performance target: actual 1920×1080 rendering at 60 FPS on the specified M5 Pro (48 GB, 20 GPU cores). No final release benchmark has passed yet.

## Architecture

`oversteer-core`: authoritative Rust state, recovered vehicle/contact/integration semantics, race/scoring/AI/career/economy/customization/save schema. No Godot object dependency. Preserve stateful RK4 commits, ordered contacts, mutable coefficients and native helper interval arithmetic; document the reconstruction clock policy separately; do not substitute a stock vehicle controller.

`oversteer-godot`: Rust GDExtension adapter, inputs/commands into the core and snapshots/events to Godot nodes, Control UI, audio and resources. Godot scenes/resources/shaders supply presentation. Query-only geometry must not double-integrate car state.

Offline tools convert permitted donor GLBs and original non-car assets into packaged resources with source IDs/hashes, material variants, wheel pivots, collision/route data and compatible part metadata. Raw ISO, extraction tools and research caches are not runtime dependencies.

## Accepted roster

```
GT4_HOND0018  GT4_MINI0001  FOCUS_SVT  MCLA_VP_VW_GOLF_83  GT4_RE__0001
GT4_HOND0019  GT4_MAZD0012  GT4_NISS0056  GT4_HOND0030  GT4_MAZD0007
GT4_TOYT0006  GT4_NISS0004  GT4_SUBR0017  GT4_MITS0001  GT4_NISS0021
GT4_LNCA0005  GT4_BMW_0010  MC3_VP_ELISE_04  MCLA_VP_AUD_R8_08
MCLA_VP_LAM_GALLARDO_06  MUSTANG_68  MCLA_VP_CHV_CAMAROSS_69
MCLA_VP_BUK_GRANDNATIONAL_87  MCLA_VP_CHV_CORVETTEZ06_07  GT4_DODG0005
GT4_ASMT0005  MCLA_VP_SLN_S7_06  LIGHTNING_SVT  F100_1956  MC3_VP_ESCALADE_03
```

## Execution and verification

- [ ] Native engine/extension: pin versions/API, build ARM64, verify actual Metal, import representative donor assets and package the extension inside project resources.
- [ ] Source/content intake: stable source registry; recover original course geometry/routes, non-car presentation/audio and native rules. Explicitly separate observed, recovered, adapted and unresolved evidence.
- [ ] Handling: port and independently check recovered equations, stage side effects, contact/clock semantics and donor configurations. No silent invented replacements for missing original handling.
- [ ] First complete loop: all-30 selection, one original course with circuit/drift, AI/HUD, wager/results settlement, garage changes and progress surviving relaunch.
- [ ] Full scope: all supported reference screens/transitions, course/event families, progression through completion, dealership/garage, crew/DNA/spooking, stakes, customization, settings and presentation.
- [ ] Delivery: export/move/launch the offline app from Finder, independent of checkout, toolchain and source cache; saves/settings outside the bundle.

## Required completion evidence

- [ ] **Reference-linked screen/state coverage:** each implemented state/transition has a reference anchor and an executed native scenario/capture. Candidate categories or proposed labels alone are not completion evidence.
- [ ] **Side-by-side scene captures:** original frame/timestamp alongside actual native output, with remaining visual differences identified and fixed where required by scope.
- [ ] **Repeatable driving and career scenarios:** real driving/racing, scoring, AI, wager settlement, purchases/unlocks and career completion; no teleport/test-only success path offered as gameplay proof.
- [ ] **All 30 cars' customization checks:** actual rendered paint/finish/vinyl/wheel/compatible-kit changes, material isolation and saved/reloaded state.
- [ ] **Save/relaunch checks:** real exported-app persistence, settings and transactions, including interruption handling and documented source stakes semantics.
- [ ] **1080p/60 FPS:** release Metal build, actual render dimensions, representative AI/effects/audio, recorded frame-time distribution and captures on the agreed Mac.

## Starting evidence and unresolved boundaries

The local vault contains 36 videos, 76 press screenshots and 16,363 timestamped frame records. Classification completion does not establish every label's truth. The matching Xbox 360 XEX is `ae20f2467cc0535872b18517941ac4434f60408cb6d07bf47da799ce1564e574`; source recipe is [Juiced2-Recompiled at cd5cb875](https://github.com/anishchandra24/Juiced2-Recompiled/tree/cd5cb875673fa13b0654bed26869341ae30aab19). Static recovery now covers the core vehicle/contact/assist and several race-rule paths; the original upstream clock, some caller/context bindings and incomplete branches remain open. No whole-original-game runtime trace establishes complete parity.

No milestone, screenshot count, or green unit-test suite alone completes this specification. The six evidence groups above and the agreed full single-player scope determine completion.

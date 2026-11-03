# Juiced 2 Rust reconstruction interview

Started November 3, 2026. The interview decisions are accepted. The user's
subsequent active goal explicitly authorizes building the entire game without
further consultation. Implementation is active under
[the specification](https://github.com/nicolas-found42/oversteer/issues/1).
Earlier approval-pending statements below describe historical interview rounds.

## Current execution authorization

The user instructed: “yes to all, build game in its entirety without consulting
me.” Completion requires reference-linked screen/state coverage, side-by-side
scene captures, repeatable driving and career scenarios, all 30 cars'
customization checks, save/relaunch checks, and the agreed 1080p/60 FPS target.
Do not ask for implementation approval again; continue autonomously and mark
completion only when this scope and evidence are achieved.

## Settled constraints

- Implement the game in Rust.
- Target native Apple Silicon macOS only. Windows compatibility is outside scope.
- Use full 3D cars and tracks with a third-person chase camera.
- Closely reproduce observable presentation and behavior; document estimates for
  hidden rules the evidence cannot establish.
- Deliver the agreed complete single-player experience first. Split-screen and
  online multiplayer are deferred.
- Use the [Juiced 2 vault](../references/juiced2/README.md) as the main visual reference.
- Use vehicle models only from GT4, MC3, MCLA, and Ford Racing 2 in
  [nicolas-found42/carmodels](https://github.com/nicolas-found42/carmodels).
- Start with 30 diverse vehicle models. The earlier proposal to expose all 904
  models in quick race was not accepted; expansion beyond 30 is uncommitted.
- The proposed 30-model list was accepted in round 3. All 30 are available in
  quick race immediately and earned/purchased through career. Adapt vehicle
  eligibility and economy to the smaller roster while preserving the reference
  league/event structure.
- Every initial vehicle supports paint/finishes, vinyl editing, wheel swaps, and
  performance upgrades; body/interior kits are specific to compatible vehicles.
- Deliver a self-contained native macOS `.app` with selected assets packaged for
  offline single-player play.
- For selected vehicles absent from the original parameter roster, adapt
  car-specific mass, drivetrain, gearing, and engine data inside the recovered
  model using documented specifications and labeled substitutes.
- First verify the agreed end-to-end checkpoint: 30-car selection, one course
  supporting circuit/drift events, AI/HUD, wager/results settlement, garage
  changes, and career progress surviving relaunch; then expand to the full scope.
- Initial language is English UI and speech. Similar engine families may share
  sound sets with per-car RPM, load, and gear-change response.
- The user explicitly selected Godot 4.7.2 + gdext 0.5.5 after the stack comparison.
  Use Godot's native Metal rendering, scenes/UI/input/audio with Rust gameplay,
  independent recovered Rust handling, Parry geometric queries where needed,
  offline Blender/Python asset preparation, and versioned JSON saves. Native
  build and release evidence is tracked separately. The earlier Bevy selection
  is superseded.
- Reuse recoverable original non-car assets from the supplied game image,
  reconstructing gaps; the four-collection base-vehicle restriction remains.
- Extend native recovery to drift scoring, AI/DNA/spooking, career, wagers and
  unlock rules where recoverable, checking behavior against vault sequences.
- Release acceptance includes source-linked screen/state coverage, matched scene
  captures, repeatable driving/race/career scenarios, all-30-car customization,
  save/relaunch checks, and the agreed performance target.
- Recover the handling model using the user-selected
  [Juiced2-Recompiled project](https://github.com/anishchandra24/Juiced2-Recompiled),
  the matching local disc image, and the vault recordings/photos, following REA's
  distinction between source, artifact, and runtime evidence.
  Recovery and implementation are authorized by the active goal. Do not
  silently substitute invented handling.
- Record resolved domain language in root `GLOSSARY.md`. Record consequential
  architectural trade-offs in `docs/adr/` when those choices are made.
- The explicit active goal grants implementation approval for the settled scope
  and acceptance criteria.

## Evidence boundary

The [donor metadata](../../data/carmodels/README.md) records 904
vehicles from the requested collections. The native game prepares 3D donor GLBs
for the accepted 30-car roster.

The vault mixes PC, PS3, Xbox 360, PS2, PSP, and unconfirmed captures. Its completed
classifications do not establish exhaustive game-state coverage: 13,997 screen
labels still require review. Exact physics, scoring, AI, timing, and some failure
outcomes remain unknown. Inspect original sequences before specifying transitions.

Existing REA evidence
`ev_0ede2a00180a8c274f6fe1f65faa2813478f819e7d4852d2a8da8f47279c1481`
records metadata acquisition, not Juiced 2 execution. Its retained summary was
reused for this interview. The user subsequently supplied
`resources/games/juiced-2/juiced-2-hot-import-nights.iso` for handling recovery.
The bounded disc pass recovered 94 parameter records. The pinned recompiled-project
tree excludes generated game functions;
its supported XEX identity matches the local extracted image. Static generation
with the pinned SDK subsequently succeeded, producing 147 files under
`artifacts/juiced2-recovery/recompiled-handling/generated/default/`. Parameter
consumer tracing subsequently recovered 22 concrete equations/branches covering
steering, suspension, tyre slip/combined forces, torque, gearing, ABS, and
integration. Remaining gaps include upstream clock/cadence/units, complete contact
blend state and override ordering, traction-control/input-assist consumption,
math-helper identity, coupled drivetrain semantics, and incomplete branches.
This is partial static evidence, not a verified complete handling model. No
original game execution was observed. The independent cross-check and reconciled
map are recorded in the recovery findings.

## Round 1: answered

The user answered this round on November 3, 2026. These are product decisions;
implementation remains subject to approval of the completed plan.

| Decision | Accepted answer |
| --- | --- |
| Canonical reference | The user treats PS3 and Xbox 360 behavior as equivalent; use their shared behavior as the reference. PC was not selected as authoritative. Record and resolve any concrete conflict if encountered. |
| Presentation | Full 3D cars and tracks with a third-person chase camera. |
| Supported systems | Apple Silicon only. Do not plan Windows compatibility. |
| First release multiplayer boundary | Complete agreed single-player game first; local and online multiplayer follow separately. |
| Fidelity and unknown rules | Closely reproduce observable behavior and presentation; document estimates for rules footage cannot establish. |

## Round 2: answered, with two caveats

The user accepted Q6–Q12, replacing the handling and roster recommendations as
recorded below. The performance checkpoint is a target, not a measured result.

| Question | Decision | Accepted answer |
| --- | --- | --- |
| Q6 | Meaning of complete single-player | Career through final completion, quick race, evidenced circuit/drift/challenge families, crew/DNA/spooking, wagers/pink slips, garage/dealership/customization, and persistent progress. Verify the complete inventory before promising parity. |
| Q7 | Track reconstruction | Recreate reference layouts, elevations, and recognizable settings; label uncertain geometry. |
| Q8 | Handling | Extract handling from Juiced2-Recompiled and the vault, using the matching local disc for artifact recovery. This replaces the proposal to author handling mainly from footage and playtesting. |
| Q9 | Source-model restriction | Restrict base vehicle identities to the four donor collections; allow original supporting assets, including body kits, wheels, vinyls, environments, and characters. |
| Q10 | First performance checkpoint | Measure 1080p at 60 fps on the current M5 Pro; establish older Apple Silicon support only through testing. |
| Q11 | Roster and progression | Choose 30 diverse eligible vehicle models to start. Do not include all 904 in the initial scope. |
| Q12 | Inputs | Remappable keyboard and conventional gamepad; steering wheels and force feedback deferred. |

The GLBs do not establish universal customization compatibility. Inspected MC3
and MCLA claim limits explicitly describe static stock assemblies and omit runtime
customization/shaders; MCLA also omits deforming convertible tops. Compatible
alternate kits and universal vinyl support must be authored or verified.

Jev judged these seven questions independently answerable in that round. Engine
selection, the first playable scenario, the per-car customization matrix, and
detailed career-loss/recovery rules remain downstream. Evidence and advisory judgments:
`artifacts/juiced2-vault/judgments/interview-round-02.json`.

## Round 3: answered

The user accepted Q13–Q16 without caveats. The selected roster and its identity checks are in
`artifacts/juiced2-recovery/diverse-30-proposal.md` and the adjacent JSON. The
proposal includes two pickups and an SUV, and its inherited vehicle profiles
contain known drivetrain errors and estimated specifications. Those must be
corrected before use; structural GLB checks do not validate physics.

| Question | Decision | Accepted answer |
| --- | --- | --- |
| Q13 | Exact initial roster | Use the proposed diverse 30, including its wagon, two pickups, and SUV. |
| Q14 | Smaller-roster progression | Make the 30 available in quick race immediately and earned through career; preserve reference league/event structure while adapting vehicle eligibility and economy where the smaller roster requires it. |
| Q15 | Per-car customization coverage | Paint/finishes, vinyl editing, wheel swaps, and performance upgrades for all 30; body/interior kits vary by compatible vehicle. |
| Q16 | Delivery | Self-contained native Apple Silicon macOS app, packaged with its selected assets and playable offline. |

Jev's engine-readiness judgment was uncertain (0.49), so a firm engine choice
remains deferred while handling integration and a native rendering/asset proof
are unresolved. Bevy remains a researched candidate, not an accepted decision.
This round settles the scope prerequisites for an end-to-end first milestone;
detailed customization limits remain open. Exact career failure/save transitions
need further evidence.
Advisory judgments and primary review for that round are retained in
`artifacts/juiced2-vault/judgments/interview-round-03.json`.

## Round 4: answered, with engine research delegated

The user accepted Q17 and Q19–Q21. Q18's Bevy proposal was not accepted; the user
requested research into five alternatives and delegated selection of the best
overall Rust stack. Full implementation approval remains pending.

| Question | Decision | Accepted answer or remaining work |
| --- | --- | --- |
| Q17 | Vehicles absent from original parameter roster | Author donor-specific mass, drivetrain, gearing, and engine configurations inside the recovered model using documented specifications and labeled native-class proxies. Preserve recovered global algorithms and distinguish adapted data from native data. |
| Q18 | Rust stack | Research five alternatives against the Bevy baseline using primary sources, then select the best overall stack. The earlier Bevy proposal is not an accepted technology decision. |
| Q19 | First end-to-end checkpoint | Native app with 30-vehicle selection, one reconstructed course supporting circuit/drift events, AI/HUD, one cash-wager settlement, core garage changes, and progress surviving relaunch; expand afterward through all agreed release content. |
| Q20 | Language | English UI and speech for the initial release. Additional language packs are outside initial scope. |
| Q21 | Donor engine audio | Share appropriate sound sets across acoustically similar engines, with per-car RPM/load/shift response. |

The delegated research is complete: [comparison](../references/juiced2/rust-stack-research.md)
and historical [selection](../adr/0004-select-bevy-and-independent-handling.md).
The user subsequently selected Godot 4.7.2 + gdext 0.5.5;
[ADR-0005](../adr/0005-use-godot-and-rust.md) is current. The native integration proof has not been run or
claimed. Earlier Jev readiness judgments concern whether a question could be
asked, not engine compatibility. There is no new request for engine approval;
the user's overall implementation approval is still required.

Further direct reference review confirms a pink-slip forfeiture warning
(`SSCgI4rqzlw`, 636s), a restart/bet-loss warning (`xiaQpIdUPnk`, 3120s), and a
save overlay after customization (`-GCF8J-tVyQ`, 651s). Actual last-car defeat,
bankruptcy, reload rollback, and complete save/profile rules remain unknown.
Those are research questions, not questions asking the user to recall the game.

Detailed kit/layer/slot limits require reference and per-car asset mapping.
Numerical equivalence criteria depend on remaining handling recovery. Full plan
approval is still pending. Current judgments and evidence leads are retained in
`artifacts/juiced2-vault/judgments/interview-round-04.json`.

## Round 5: answered; Godot selected

The user accepted Q22–Q24 and explicitly selected Godot 4.7.2 + gdext 0.5.5.
All product decisions asked so far are settled. No further preference question is
needed to replace the engine choice or ask the user for source facts.

| Question | Decision | Accepted answer |
| --- | --- | --- |
| Q22 | Original non-car assets | Reuse recoverable tracks, environments, UI/fonts, audio, and characters from the supplied game image; reconstruct gaps. All base vehicle models still come only from the accepted four collections. |
| Q23 | Native rules beyond handling | Recover drift scoring, AI/DNA/spooking, career/wager/unlock rules where possible; validate observable behavior against vault sequences and document unrecovered parts. |
| Q24 | Release acceptance | Require a source-linked screen/state checklist, matched scene captures, repeatable driving/race/career scenarios, all-30-car/customization checks, save/relaunch checks, and the agreed performance target. |

This round settles recovery scope and acceptance policy. Its judgments and the
historical stack-selection review are retained in the local vault. The subsequent
active goal grants full implementation authorization; the specification is
tracked in issue #1. Surface unresolved evidence gaps and continue the authorized
work rather than silently inventing native behavior or asking for approval again.

## Decisions unlocked by these answers

- Reference and fidelity → mode/content inventory, tracks, career progression,
  wagers, pink slips, crew/DNA, scoring, failure and recovery behavior.
- Presentation and fidelity → handling model, camera behavior, customization,
  incomplete donor materials, and additional geometry policy.
- Systems, presentation, multiplayer, and fidelity → Rust engine and physics
  technology, supported inputs, performance target, and migration boundary.
- Scope and presentation → final roster, unlock distribution, and first playable
  acceptance scenario.
- All settled branches → concrete implementation spec in the repository's GitHub
  issue tracker, validation plan, then explicit user approval.

The question ordering and factual verification are retained in the local vault at
`judgments/interview-round-01.json`. Jev's relevance scores are advisory. Dependency
checks keep handling and engine choices out of this first round even when they
rank highly.

## Evidence audit follow-up: accepted November 3, 2026

The user accepted both initial evidence-policy questions, both benchmark questions,
and the final shared-understanding check. These decisions extend evidence validation;
they do not reopen the existing implementation authorization.

- Audit evidence supporting the agreed rebuild acceptance claims. Clearing every
  corpus review flag is not a completion requirement.
- Establish semantic accuracy against an independently human-adjudicated benchmark.
  Agreement between models remains corroboration, not independent ground truth.
- Prepare an initial 200-example blind pilot for the user to adjudicate. Include
  flagged and accepted predictions, common and rare states, and varied sources.
  Hide proposed answers until review; allow unreadable and insufficient-context
  judgments without forcing a label.
- Freeze source-recording-disjoint tuning/test assignments. Keep press galleries
  and exact duplicate images together. Preserve hashes, predictions and sampling
  probabilities in a separate audit manifest.
- A category can qualify only when its held-out precision has a one-sided 95%
  lower confidence bound of at least 95%. Report recall separately. Insufficient
  evidence leaves a category ineligible; the pilot does not guarantee category
  coverage or eligibility.
- Prepare and score the pilot from cached inputs without new classification calls.
  Any later experiments or additional human-review batches must be scoped from
  its results. Preserve existing raw judgments and review flags.
- Temporal rules still require appropriate sequences/native evidence. A visible
  transition alone does not establish causation or hidden timing/scoring rules.
- Track required release checks and candidate state/transition evidence, retaining
  explicit estimates, contradictions, and unresolved gaps. Empty candidate lists
  do not establish absence or exhaustive coverage.

The implementation and local review workflow are documented in the
[vault reference guide](../references/juiced2/README.md#blind-human-review-pilot).

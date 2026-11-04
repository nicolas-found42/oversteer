# Observability audit and investigation runbook

Status: local improvements implemented; verification and review records below. Whole-system retrospective coverage remains partial where explicitly deferred. No claim that new instrumentation recovers old incidents.
Review ledger: `/Users/nicolas/.codex/reviews/oversteer-observability-20261104/review.json`.
Selected persona: Restart investigator; seed `697aefb7e467d85a10ca5f1e46669701`.

## Scope and coverage

Tracked inventory: 1,383 files at intake, grouped below. Binary/generated local trees
(`build`, `artifacts`, `resources`, imported `godot/assets`, caches, dependencies)
are inspected through producers, consumers and existing manifests, not individually
reverse engineered. User edits to AGENTS.md and docs/references/racing-ui are preserved.
The machine-readable [path inventory](observability-inventory.json) retains group membership. Component inspection is separate from cross-component workflow inspection. Inspected
means source/evidence inspection for observability, not exhaustive behavioral acceptance.

| Component | Disposition / source evidence | Existing evidence and limits |
| --- | --- | --- |
| Core simulation, physics, collision, AI, drift, goals, nitrous, assists, paint, performance (48 files including examples/tests) | Inspected: crates/oversteer-core/src/lib.rs module inventory; game.rs command/advance/save/load; tests/core.rs and pivot_*; PROVENANCE.md | Snapshots, deterministic example recordings, save transactions; no automatic disk telemetry in engine-independent library. Frame/input histories require explicit recording. |
| Godot host/UI/input/scene (lib.rs) | Inspected: ready/process/input/send/refresh/exit_tree, diagnostic_snapshot, run_scenario | 128 in-memory commands, scenario samples/reports and optional captures; ordinary restart discards memory. Commands may contain driver names in existing explicit diagnostic captures. |
| Persistence/preferences | Inspected: persistence.rs load/save/atomic/preserve; lib.rs load_career/persist/load_settings/save_settings | Primary, backup and corrupt copies retain state, not operation attempts; no rotation for corrupt copies. Atomic rename+file fsync, no directory fsync. |
| Loading/resources | Inspected: loading.rs new/poll/finish and lib.rs begin_loading/poll_loading | Progress samples retained in memory; failure discards job; no runtime timeout. |
| Audio/video/effects/paint/palette/layout | Inspected: audio.rs stream/update/summary; effects.rs and paint/native_palette/native_layout; lib.rs movies/rendering | Optional scenario audio/effect/material snapshots, Godot errors; no audio hardware or visual root-cause history during ordinary play. |
| Legacy avatar source | Inspected: avatar.rs not declared by lib.rs; fixed driver now constructed by host/assets | Not applicable to active character editor: removed by ADR-0008; retained source/history is not runtime instrumentation. |
| Build/bootstrap/import/export/source gate (game tools) | Inspected: build.py, bootstrap.py, dev.py, .cargo/config.toml, Godot configs, .github/workflows | Terminal output; pinned tools and download/template hashes; CI logs external. No server deployment, database, broker or remote runtime service exists. |
| Verification/input replay/background focus/native inspection | Inspected: verify.py run_case/main, verify_saves.py, replay_inputs.py, inspect_vehicles.py, background_window.py/.m, metal_capture.py, inspection/*.gd | Explicit per-case runtime.log, scenario.json, verification.json, controls, binary/content/tool hashes, optional images; timeout currently skips case summary. |
| Asset preparation/recovery/publication (155 files) | Inspected at boundary inventory level: assets/README.md production sequence; fetch_donors.py, extract_source_archives.py, prepare_cars.py, stage/bind/publish families and tests | Pinned inputs, stage contracts, hashes and JSON audits; individual scripts often overwrite output. Blender/decoder subprocesses and parallel workers have heterogeneous error handling. Deeper stage coverage tracked below. |
| Donor helpers/viewer (8 files) | Inspected: carmodels/assets.py verify_asset/decode_scene, scope.py, preview_materials.mjs and source_viewer | Hash checks, source material translation, helper tests; viewer is preparation tool, not game runtime. |
| Media/audio/video preparation | Inspected: media.py source_file/encode/speech, audio_banks.py, video.py | Manifests/hashes survive success; interrupted conversion attempts mostly terminal-only. |
| Reference collection/classification/review (12 files) | Inspected: vault_media.py, classify_vault*.py ask/classify/main, reference_reviews.py, review_pilot.py and catalog/test consumers | Cached request/response dependencies and usage, errors, progress JSONL, annotation hashes; transient retries not retained, progress overwritten on rerun. Live provider not exercised; HTTP outcomes tested locally. |
| Browser test harness (3 files) | Inspected: tools/visual/README.md/package.json, references/test_review_pilot.cjs | Local reference corpus + Playwright; source gate does not run browser suite. No UI change proposed. |
| Static content/scenarios/profiles (985 files), results (7) | Inspected via inventory, accepted-roster/content-selection/scenario schemas and producer/consumer paths | Tracked provenance survives git history; generated content may differ, manifests identify selected runtime. These are evidence/data, not independently executing services. |
| Docs/config/CI/editor (106 files) | Inspected entry docs, ADRs, glossary, CI, pins, export/GDExtension and task/debug configurations | Source changes reproducible by git; LLDB profile explicitly unverified. CI retention/access not specified in repository. |

## Cross-component workflows

| Workflow | Inspection / scenario | Evidence gap |
| --- | --- | --- |
| Launch → content → preferences/career → UI | Inspected ready/load methods; malformed input and backup recovery | G1 startup/build and recovery sequence |
| User/input → command → wager/ownership → save → restart | Inspected send, direct Pause/Resume callers, game load refund and persistence; known incidents in PIVOT_STATUS.md | G1 command and save correlation; raw existing snapshots can contain names |
| Simulation → finish/settlement → scene/UI/audio → save | Inspected process/refresh + game settlement; known finish blockage and pink-slip inventory incidents | G1 transition summary; exact per-frame causes remain dependent on explicit input recording |
| Resource request → worker polls → main-thread scene handoff | Inspected SceneLoad and callers; hypothetical failed/stalled/cancelled load | G2 finite history and durable terminal outcomes |
| CLI → compiler/importer/Godot/export | Inspected build/dev/bootstrap, background guard; hypothetical child failure/termination | G3 process outcomes/build context |
| ISO/donor network → decode/Blender → staged content → publication → runtime | Inspected stage contracts, pinned fetch and production sequence; hypothetical partial conversion/hash mismatch | G3 optional wrapper for legacy jobs; stage-specific semantics require original manifests |
| Vault → parallel provider attempts/cache → classification → human review → coverage | Inspected ask and cache keys, error/review contracts; hypothetical 429→success / timeout | G4 attempt retention and bounded safe metadata |
| Scenario → forced kill/timeout → evidence → fresh process replay | Inspected verify/replay/save verifier; historical wager kill evidence exists | G5 timeout summary; G6 bounded retrieval |

## Historical evidence actually retrieved at intake

- `build/verification/pivot-wheel-contact-cached/verification.json`: 10,214 bytes,
  `started_utc=20261104T041548Z`, `passed=true`, binary/content/tool identities present.
- `artifacts/oversteer-pivot/wagers/finish-summary.json`: 10,156 bytes, `passed=true`,
  accepted and failed attempts listed. This is an earlier test report, not production incidence frequency.
- `build/tools/godot-4.7.2/download-manifest.json`: 588 bytes, release/checksum records.
- `~/Library/Application Support/Godot/app_userdata/Oversteer/logs`: five files,
  235–282 bytes at inspection. Presence verified; no ordinary gameplay sequence established.
- Ignored local artifacts have no repository-managed TTL or backup guarantee; deletion,
  overwrites, checkout removal and machine loss can remove them. Access requires this
  local filesystem; other agents/machines cannot assume these ignored files exist.
- Godot log retention/default rotation is unverified (not configured explicitly here).
  GitHub CI retention/export delay is unknown. Authenticated `gh run list` and
  `gh run view 41800152450 --repo nicolas-found42/oversteer --log` succeeded: 81,651
  bytes retrieved for commit `3b5b64ea3df2afbea8c3410a39174233b2ceaa77`, including
  6/22 Rust library tests and 41/6/19 Python tests. This earlier CI run does not
  test this working-tree patch. CI access requires repository Actions read access.

## Gap register and acceptance plan

| ID | Priority / evidence | Proposed acceptance | Disposition |
| --- | --- | --- | --- |
| G1 | High: ordinary restart destroys commands/save outcomes; high impact on career, frequency unknown | Bounded safe journal, source/content identity, session/sequence/operation links; reconstruct save failure/recovery after process exit | Implemented and locally verified; see checks below |
| G2 | Medium: failed load drops all samples; changing progress can grow history | Persist request/outcome and bounded progress; distinguish start without terminal from observed failure | Implemented; bounds and successful native emission verified. Failed/cancelled loader integration remains unverified: branches inspected, no native resource-loader fault injection. |
| G3 | Medium: build/media/asset subprocess failures terminal-only | Shared safe command recording and documented wrapper; failing child retains exit/error without argv/secrets | Implemented and locally verified; see checks below |
| G4 | Medium: provider attempts before eventual success disappear | Retain logical operation and attempt, HTTP/transport category, duration without request bodies/keys | Implemented and locally verified; see checks below |
| G5 | Medium: verify.py timeout raises before returning case report | Actual timeout leaves machine-readable case outcome alongside runtime.log | Implemented and locally verified; see checks below |
| G6 | High: no bounded ordinary incident query path | UTC/offset time window, identifiers/source filter, explicit read/parse/truncation errors and completeness limits | Implemented and locally verified; see checks below |
| G7 | Medium: a failed warning sink could raise during telemetry failure | Broken stderr plus failed journal must preserve caller behavior | Implemented and verified: failing test then passing fix |
| G8 | Medium: audio JSON parse silently returned null (`audio.rs::new`) | Retain invalid-json category while preserving fallback and excluding input | Implemented; local parser regression and native valid-config path verified |
| G9 | Medium, hypothetical physics/render/audio incident: ordinary transition records omit full tick inputs, GPU work and device output | Select an incident-triggered bounded trace and measure gameplay overhead before enabling ordinary capture | Deferred: current explicit replay/inspection tools retain rich evidence; continuous collection would change storage/performance/privacy policy. Ordinary journal cannot distinguish all physical/rendering causes. |
| G10 | Medium, hypothetical interrupted multi-file asset publication: legacy stages overwrite outputs | Transactional per-stage manifests with before/after identities and partial-publication recovery | Deferred: legacy production sequence spans 155 scripts and retained reference inputs; a generic wrapper now preserves invocation/exit, but does not establish which writes completed. Requires stage-specific acceptance against original inputs; no asset publication was performed. |
| G11 | Release/provider integration evidence | Repeat on exported release and live provider failures under authorized run budget | Unverified: only dev/headless runtime and local HTTP fixtures exercised. No remote API requests, release export or deployment performed. |

## Verification budget and next action

Source checks: baseline then final, rerun only for fixes. Runtime: at most six isolated
process launches and four screenshots initially; expand only on a specific failure.
No asset publication, network purchases, credentials changes or external deployment.
Jev review budget: up to 16 bounded checkpoint calls initially; no live classification
requests. jg discovery reached its 16-request cap: incomplete search, compensated by
explicit file/module inventories and focused source reads.

Next: complete the current snapshot checks, record semantic findings/completion receipts, close the repair pass, and begin a separate unchanged review pass. The external ledger is authoritative after this documentation snapshot.



The table's first eight gaps are the implemented local slice. G9–G11 remain visible;
a clean local code review must not be described as complete historical forensic coverage.
No known incident frequency is inferred from test-case counts.

## Evidence sources and collection contract

| Source | Captures / retrieval | Retention, access and loss | Identity / observed status |
| --- | --- | --- | --- |
| New game journal | Session start/end, raw content digest, command kind and controlled rejection category, before/after screen/cash, transaction count, storage stages/fallback, loading start/progress/end, audio JSON status; `diagnostics.py query` | Next to the selected save in `diagnostics/`. Default macOS user path below. Same local account; created directories 0700 and files 0600 (existing modes unchanged). Two 4 MiB files; no guaranteed number of days. 2 KiB/event; 64 attempted events/second/session. No exporter, queue or retry; writes go directly to OS, no fsync. | Session + sequence; operation number is a start sequence **within that session**; storage steps use parent. `parent_operation` links launcher→game. Source fingerprint, git commit and debug/release profile; startup content SHA256, renderer mode, applied quality/difficulty. Post-exit/recovery/kill tested. Power loss, slow disks and release packaging unverified. |
| New tool journal | Process start/end, executable basename, bounded repository Python script label/SHA256, argument count, exit/exception category/duration; provider start/end, stable operation UUID, retry attempt, HTTP category/status, dependency hash | Default `build/diagnostics`; Python-only override `OVERSTEER_DIAGNOSTICS_DIR`. Same 8 MiB/2 KiB/64-per-second limits. Per-process thread lock, nonblocking cross-process file lock. No stdout/stderr/argv/env/body capture. Same privacy permissions and fsync limitation. | UUID operation and optional parent. `collector_id` is diagnostics.py SHA256, **not the executed program**. `source_id` is present only for an identified repository Python entry point or classifier source. Tests cover concurrent operations and child env propagation. Cache hits make no HTTP attempt, so emit no provider attempt. |
| Existing saves/preferences | Primary, backup, preserved `.corrupt-*`; inspect a copy with bounded JSON tools | No automatic expiry; corrupt copies are unbounded legacy evidence. Same local account. Latest state plus prior backup, not a command history; manual deletion/overwrite/machine loss apply. File fsync+rename is not a power-loss guarantee without directory sync. | Schema, selected car, career transactions and interrupted-race escrow; no wall-time or build identity. New journal supplies nearby operation context; cross-session causal joins require a known save path and state comparison, never timestamps alone. |
| Existing scenarios/inspection/replay | Per-case `runtime.log`, `scenario.json`, `ui-actions.json`, controls/input plans, `verification.json`, render/material snapshots; see game and inspection README | Opt-in, local output directories; no TTL or size cap on old artifacts. Images limited by existing harness. Partial runs can lack final output; verifier now writes `timeout.json` on timeout. Captures may contain profile names; keep local and redact before sharing. | Explicit binary/content/tool hashes and deterministic input plans; existing historical reports queried. New headless verification does not establish visual/audio quality or 60 FPS. |
| Existing asset/media manifests | `artifacts/juiced2-build`, source contracts, staged/published hashes; bootstrap download/template manifests | Local original disc/donor files required for many reproductions. Output may be overwritten; no central attempt retention before this patch. Added common process records; legacy stages require wrapper. | Source/member/content hashes and source commits; successful manifests do not prove no failed earlier attempt. `asset-verification.json` (5,301 bytes) and UI layout manifest (99,058 bytes) present and parsed. |
| Existing reference caches/reviews | `artifacts/juiced2-vault/judgments/v2`, raw request/response dependencies, review hashes; progress and classifications | No TTL; potentially large. Observed progress file 180,340,940 bytes, classifications 229,304,168 bytes. A bounded ~1 MiB prefix yielded 101 complete rows; remainder was **not scanned**. Progress is overwritten on rerun. Raw requests contain public images, raw error artifacts may contain provider response text; new journal excludes both. | Image/question/model/preparation dependency hashes, request hashes, usage, human review provenance. New retry log links attempts; HTTP/JSON success is not proof that downstream answer validation passed. Provider console/history access and retention remain unknown. |
| GitHub Actions | `gh run list`, `gh run view RUN_ID --log` | Authenticated repository read access verified for one historical run. Retention/deletion/export delay unknown; no settings changed. | Run ID, commit, job and UTC timestamps; historical source gate evidence only. |

`dropped_before` reports rate, size, contention or I/O losses when a later write succeeds.
One best-effort stderr warning is emitted per writer on loss. If the final write fails
and the process dies, the journal cannot report that drop. Sequence gaps and missing
session starts/ends are reasons to qualify completeness; an unmatched start does not
prove a crash. Rotation can remove the start of an operation. Query reports
`history_complete=false` even when all surviving files were read successfully.

No environment variables, access tokens, player names, paths, full commands, profiles,
provider bodies or arbitrary exception messages are added to the journal. Only explicit
numeric/boolean fields and restricted tokens are accepted. There is no sampling below
the rate cap; loading progress is emitted at most once/second, and in-memory loading
history is capped at 128 progress changes/job and 32 completed reports, with loss counts.
Disk cost is at most 8 MiB plus a lock file per directory, excluding existing captures,
saves, input recordings and provider caches. Creating many isolated directories is still
operator-controlled storage. A 50-event local Python probe measured median 51.375 µs,
maximum 890.875 µs, total 4.161 ms, 13,781 bytes, no drops. These are observations, not
real-time guarantees or gameplay performance acceptance. Journal writes are synchronous;
slow filesystem I/O can delay callers even though lock contention does not block.

## Investigation runbook

Prerequisites: repository checkout, Python 3.13 via `uv run --frozen`, local read access
to the affected evidence directory; runtime reproducers also need prepared assets and
the pinned Godot/dev extension. Replace uppercase placeholders below; keep timestamps
explicitly UTC (`Z`) or offset-qualified. These commands do not send records externally.

1. Start from the symptom and an approximate window. Ordinary game evidence defaults to:

   ```sh
   uv run --frozen python tools/game/diagnostics.py query \
     --directory "$HOME/Library/Application Support/Godot/app_userdata/Oversteer/diagnostics" \
     --since '2026-11-04T08:00:00Z' --until '2026-11-04T10:00:00Z' --limit 500
   ```

   With `--save-file`, use its parent directory's `diagnostics/`. For build/media/reference
   jobs use `--directory build/diagnostics`. An isolated test is a separate environment;
   do not search a scenario directory and conclude ordinary play produced no records.
   Exit 2 means a read/lock/parse/bounds failure. `query_complete=true, matched=0` means
   no matching retained records, never that the event did not happen. Narrow windows or
   filters after `result_limit`; `--max-bytes` is capped at 8 MiB and result limit at 10,000.

2. Find `session`, relevant `operation.start`/`command.start`, and terminal outcomes.
   Follow numeric game operations with **both** identifiers:

   ```sh
   uv run --frozen python tools/game/diagnostics.py query \
     --directory /ABSOLUTE/EVIDENCE/diagnostics \
     --since '2026-11-04T08:00:00Z' --until '2026-11-04T10:00:00Z' \
     --session SESSION_ID --operation OPERATION_NUMBER
   ```

   Use UUID operation alone for Python process/provider jobs. Follow the game's
   `parent_operation` in the **tool** journal for launcher outcome. Use `--component game`,
   `--event operation.end` or `--source-id SOURCE_ID` to narrow, then remove filters to
   inspect related records. Ordering is session sequence; cross-process ordering requires
   explicit parent links. Retries have one UUID plus attempt numbers. Separate manual
   invocations have separate IDs; no invented causal link is assigned between them.

3. Inspect current state without dumping names or entire payloads. Copy the save first;
   `jq` is an optional prerequisite for this example:

   ```sh
   jq '{schema_version,selected_car,interrupted_race,
        cash:.career.cash,owned_cars:(.career.garage|keys),
        transaction_count:(.career.transactions|length)}' /COPY/OF/career.json
   ```

   Preserve primary, backup and `.corrupt-*` files before experiments. A `NotFound` storage
   step followed by successful new/default load is expected; inspect the operation outcome.
   For backup write failure, follow `storage.write.target`, then ordered storage steps.
   `replace/IsADirectory` supports a destination type conflict; it does not identify its creator.
   Missing scene terminal events cannot distinguish hung loader, process termination or lost
   telemetry without runtime logs/process evidence. `audio.config/error/invalid_json` distinguishes
   parse failure; syntactically valid config and device/mixer failures require existing audio snapshots.

4. Test competing explanations against retained evidence. Compare source/commit/content
   identities before combining runs. The Rust `source-*` fingerprint is diagnostic, not a
   cryptographic binary identity; local uncommitted changes require retaining their diff.
   Compare published/staged hashes for content mismatches, terminal outcomes for transport
   versus downstream validation, and cash/transaction deltas for duplicated settlement.
   If inputs/frames were never recorded, record that physics/render explanations remain
   hypothetical. Use the existing `replay_inputs.py` → `verify.py --suite replay` path only
   with a real retained replay manifest, and keep visual/timing checks separate.

5. Verify a fix using the original observable failure and current build. Run source checks,
   the failure regression, then the same isolated native investigation and retrieve its evidence:

   ```sh
   uv run --frozen python tools/game/dev.py check
   uv run --frozen python tools/game/build.py build --profile dev --skip-import
   uv run --frozen python tools/game/verify_diagnostics.py \
     --seed-save /ABSOLUTE/VALID/COPY.json --output /ABSOLUTE/NEW/OUTPUT
   ```

   The last command launches four headless processes and takes zero screenshots. It writes
   injection ground truth separately, reconstructs from queried records after process exit,
   compares afterward, then verifies backup recovery, forced termination and unavailable
   telemetry. It never changes the supplied seed. A test injection is not a production root cause.

For a legacy asset command without native journal adoption, record its safe invocation:

```sh
uv run --frozen python tools/game/diagnostics.py run -- \
  uv run --frozen python tools/game/assets/STAGE_SCRIPT.py
```

Prefer wrapping the Python interpreter directly so its repository script identity is visible:

```sh
uv run --frozen python tools/game/diagnostics.py run -- \
  .venv/bin/python tools/game/assets/STAGE_SCRIPT.py
```

Subcommands still carry their normal side effects; the wrapper grants no publication permission.
It records process outcome, not arbitrary stdout or which stage writes completed. Inspect the
original stage manifest and normal error output. Do not add secrets to labels or journal fields.

## Verification and review record

- Before edits: source gate passed. The old verifier timeout path was executed from `git show HEAD`
  against the new timeout test: it raised `TimeoutExpired` before creating the case result.
- Timeout results were also passed through the normal gallery consumer: the first test failed with `KeyError: scenario_json`; the fix now renders links to timeout details and runtime logs without a nonexistent final image. A headless Chromium render was inspected (one report screenshot, no native captures).
- A malformed-envelope probe also failed before repair: boolean schema/missing event/negative sequence incorrectly counted as valid evidence. The query now rejects these explicitly.
- New deterministic checks cover query timezone/bounds/no-match distinction, corrupt/partial
  records, rate/size/rotation, blocked stores/locks, closed stderr, child timeout, parallel operation
  isolation, subprocess parent propagation, and provider 429→success plus transport timeout.
- Native checks: all nine assertions passed, four real headless processes per verification run.
  [Verification](evidence/observability/verification.json),
  [retrieved incident excerpt](evidence/observability/incident-query.json),
  [reconstruction](evidence/observability/reconstruction.json), and separate
  [ground truth](evidence/observability/ground-truth.json) are retained here. Full local logs,
  queries and snapshots are outside the source tree in the ledger directory.
- Initial six-launch budget was expanded to fourteen when warning-failure, audio fallback,
  loading-history bounds and build-identity repairs required final integration repeats. Actual
  count: thirteen native headless launches (one exploratory + three four-process runs), zero native screenshots and one browser report screenshot.
  Headless mode opened no windows and made no focus changes; it does not verify rendering or gameplay timing. Simulation-clock and input logic were not altered.
- Fresh review challenged clock rollback and missing current journals: a separate-process query
  recovered records without an operation ID; session sequence retained ordering despite reversed
  timestamps; surviving previous records remained accessible with explicit `missing_current` and
  exit 2. A wrapper probe confirmed caller timeout/check/environment behavior and one child call.
  Five assertions passed; exact probe and logs are retained with the review ledger. The pass also
  corrected G2 above to distinguish tested loading bounds/success from unverified failure/cancellation.
- Local median journal overhead is recorded in [overhead.json](evidence/observability/overhead.json).
  Rotation/restart/process exit were tested; power loss, days-long retention, release packaging,
  real provider failure, audio hardware and 60 FPS impact were not tested.
- Concurrent user work changed the host's menu presentation and added `menu_focus.gd` and `verify_menu_focus.py` during
  this audit. Those changes are preserved and are not observability fixes. Full gate runs that
  saw target mutation remain failed/stale in the external ledger even when their suites passed.
- The concurrent menu-focus helper was inspected at its launch boundary: a 60-second native
  subprocess uses an isolated temporary save directory that is deleted afterward. It is an
  explicit interactive acceptance helper, not retained incident evidence; its rendering acceptance
  belongs to the concurrent UI work. Its path is included in the coverage inventory.
- Jev intake preserved constraints (audit pass; highest wrong probability 0.36). Planning routed
  uncertain loading/provider/timeout hypotheses to concrete tests. Coherent repair reviews had
  low-confidence test/blast-radius judgments (safe-to-apply 0.45–0.72), so no model approval was
  treated as proof; source inspection, failure tests, native reconstruction and the fresh-pass
  checks provide the evidence. CI log screening requested manual review; selected lines contain
  only job names, timestamps and test counts, with no directives. Exact receipts are in the ledger
  directory. Optional live-provider experiments and visual judgments were not applicable to
  unchanged presentation code in this patch.

Review continuation: use `review.py --state /Users/nicolas/.codex/reviews/oversteer-observability-20261104/review.json status`.
The ledger records current checks, findings, semantic checkpoints, clean-pass state and the exact
next command. Any subsequent source edit invalidates its completion evidence. G9–G11 remain
explicit limits/deferred work even if the local review gate is clean.

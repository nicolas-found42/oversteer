# UI/HUD and observability checkpoint — unfinished

Recorded 2026-11-04. This packages the current work after the implementation goal was paused and cleared. It does **not** complete the UI/HUD brief. The subsequent instruction to “commit everything” includes the pre-existing observability changes, research images/PDF and unfinished verification tools. Ignored build products, credentials, prepared game assets and original disc media remain local.

## Scope and chronology

The branch starts at `origin/main` (`3b5b64e`), whose tree matches the earlier `e657d2f` starting point. The initial dirty patch is retained locally at `build/verification/ui-hud/pre-existing.patch`; it included both UI foundations and observability work. Commits organize the resulting work by responsibility, rather than fabricating historical intermediate milestones or backdating changes:

1. `7ada6d6` — brief, visual direction, research/reference pack and existing agent guidance. Reference captures are research, not shipped game art. Source attribution and limitations remain in the individual research notes; the separate 7,000-frame local library is not included.
2. `cbf22aa` — menu/customization presentation and code-drawn racing instruments, measured checkpoint splits, licensed fonts and CC0 studio lighting. The supplied generated HUD PNG is reference only; no generated HUD asset is shipped. Career/Quick Race ornament numbers are removed.
3. `b6e4a71` — existing bounded diagnostics, storage/loading/command events, subprocess/provider-attempt evidence, timeout reporting, tests and runbook.
4. `c987b6c` — UI scenarios and observers, including explicitly unfinished finance/forfeit/vinyl probes. Formatting of the forfeit Python wrapper was corrected during packaging.
5. This handoff, the requirement checklist and selected verification receipts.

The final source tree preserves the existing implementation. Intermediate commits were not independently run through the full suite. The only simulation-core addition is the defaulted `RaceSnapshot.career` presentation field; physics, AI and settlement rules are not edited. Diagnostics touch persistence observation, not its save format. UI changes still affect input/focus, preview lifecycles and transaction presentation and need runtime regression coverage.

## Verification ledger

| Check / receipt | Observed result and limits |
| --- | --- |
| `uv run --frozen python tools/game/dev.py check` at `c987b6c` | Passed: format, Clippy, Ruff, Python syntax, 37 Rust library tests and 76 Python tests. [Actual output](evidence/ui-hud/source-check.log). Later handoff changes are documentation only. |
| Initial packaging source check | Failed Ruff formatting for `verify_ui_hud_forfeit_headless.py`; corrected, then rerun successfully. [Original failure](evidence/ui-hud/source-check-initial-failure.log). |
| `git diff --check` | Source changes pass. Two original OFL license lines retain upstream trailing whitespace. The PDF was initially interpreted as text; binary attributes now preserve it without whitespace interpretation. No license or PDF bytes were rewritten to hide these results. |
| `verify_ui_hud_navigation_headless.py --output build/verification/ui-hud/headless-navigation-teardown` | Historical pass: 97 assertions, eight state observations, actual headless/Dummy drivers, zero PNGs. [Receipt](evidence/ui-hud/headless-navigation.json). Covers all 18 Quick Race entries, purchase cancel/commit, modal input containment, focus return and binding reset/persistence. |
| Earlier `headless-navigation` and `headless-navigation-diagnostic` | Failed at teardown despite passing navigation assertions: leaked MP3 playback/stream resource. Observer teardown now frees the app before quit; the later run above passes. Production audio code was not changed for this repair. Logs remain under the named local run directories. |
| `verify_ui_hud_spectator_tach.py --output build/verification/ui-hud/code-hud-spectator-headless-fixed` | Historical pass: 57 checks, two engine scales, selected positions, map visibility/names, control geometry and unchanged wallet/garage. [Receipt](evidence/ui-hud/headless-spectator.json). Logic/geometry only, not rendered acceptance. |
| Earlier `code-hud-spectator-headless` | Failed observer number-type lookup and real map-node name collision during queued deletion. Both repaired; children now detach before queueing deletion. |
| `code-hud-instruments-refined` / `code-hud-drift-target` | Historical Metal captures: 17 instrument states and four drift-target states, inspected at capture time. Predate final tach/spectator corrections. Static frames do not establish drift animation/banking cadence. |
| `reference-ticket-navigation`, `reference-finance`, `reference-ticket-editors`, `reference-seat-preview` | Historical rendered menu/editor/finance evidence. Finance has purchase commit and sale confirmation, **not sale commit**. Cart row correction occurred after its last rendered capture. |
| `reference-circuit` | Rejected timing/results evidence: stale/identical background pixels and a purported results image showing the race. Exit zero is not visual proof. The observer now requires a fresh completed-render serial and matching labels. |
| Initial `code-hud-instruments` / `code-hud-drift` | Failed fresh-render observation; not counted as passed captures. |
| Blind-spot experiment | First 20-second run: 177 samples and one negative frame, inconclusive. Projected follow-up exited without its receipt. No proximity cue shipped. |
| Observability storage/lifecycle checks | Recorded four headless launches, nine checks passed; [original receipt](evidence/observability/verification.json) names its library SHA. Historical, not a fresh final-revision performance/audio/rendering claim. |
| Finance and forfeit headless harnesses | Authored but **never executed in the game**. Python syntax/format checks are not GDScript parse or behavior verification. |
| Vinyl-camera prototype | Plan and harness prepared; **not executed**. No new surface-camera behavior shipped. |
| `uv run --frozen python tools/game/dev.py reference-tests` | Not rerun during packaging; local-fixture integration acceptance remains unverified here. |
| Final rendered matrix, release/performance and final adversarial gate | Not completed. The implementation goal was stopped; remaining findings are not waived by these commits. |

Historical runs used isolated saves/settings and local prepared assets. Their full logs, content identities and extension identities remain in the named `build/verification/ui-hud/` directories. The checked-in [provenance record](evidence/ui-hud/provenance.json) identifies the source check and selected images. Missing exact capture identities must not be inferred from the final commit.

Jev's packaging review did not grant whole-change acceptance (`escalate`, safe-to-apply 0.11); its unfinished-work disclosure check passed. It also questioned the test-total claim with low confidence. Direct log parsing confirms Rust suites 6+31 and Python suites 50+6+20; the logged aborted-case JSON and diagnostic-drop warnings come from passing negative tests. [Review disposition](evidence/ui-hud/packaging-review.json). The broad patch and missing rendered coverage remain review concerns; this is a draft checkpoint, not an accepted completion gate.

## Known unfinished requirements and blockers

- **V095: Results omit career promotion credit/status/new tier.** This is confirmed missing implementation, not merely missing screenshots. Drift finishing rank is in the table but not the requested hero placement. See the [read-only audit](../references/racing-ui/headless-continuation-audit.md). Work stopped before either repair.
- **Final visual acceptance remains open:** corrected spectator composition, tach redline sweep, cart row, paint/materials, career-state variants, wager/forfeit outcomes, results/podium, small-window layouts and drift cadence need current rendered evidence. User requires debug runs to remain headless, muted and non-focus-stealing; the pinned headless renderer cannot establish Metal pixels. Existing screenshots cannot certify the final revision.
- **Blind-spot cue and vinyl-camera direction remain hypotheses.** The former experiment is inconclusive/failed; the latter unexecuted. Do not represent either as a delivered feature or silently remove the assessment requirement.
- **Boost active/empty states cannot be exercised in the current native-discipline-less events.** HUD says BOOST UNAVAILABLE. Changing event rules solely to manufacture evidence is outside this UI work.
- **Full requirement reconciliation remains unfinished.** [UI_HUD_CHECKLIST.md](UI_HUD_CHECKLIST.md) preserves every requirement and the dated evidence trail. Older “pending” labels describe their recorded stage; newer bounded receipts supersede only the specific checks they cover. They do not establish whole-goal acceptance.

## PR screenshots and recovery

The historical title pair uses the red Civic at 1920×1080: `before-screens/title/final.png` and `reference-ticket-navigation/title.png`. Both were captured from `e657d2f` plus uncommitted work at their respective stages; neither is a clean baseline/final-commit capture. The pair shows the observed typography, action hierarchy and showroom change, and is labeled historical in the PR. Original pixels were reopened before attachment. Exact final-revision before/after evidence remains a PR completion blocker under the headless constraint.

Rollback is a code revert of the UI and/or diagnostics commits, followed by rebuilding the extension. No save migration is introduced. Reverting does not undo purchases, sales or wagers already committed through the UI; back up test saves before further transaction checks. Diagnostics are bounded best-effort local journals, with explicit retention/drop limits; reverting does not erase existing logs.

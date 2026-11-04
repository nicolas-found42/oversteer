# Code HUD instruments visual acceptance review

Reviewed 2026-11-04, read-only. All 17 supplied PNGs were opened at original 1920×1080 detail. No game launch, new capture, production edit, or runtime bitmap asset was involved. Evidence: [capture directory](../../../build/verification/ui-hud/code-hud-instruments-refined/) and [observation receipts](../../../build/verification/ui-hud/code-hud-instruments-refined/hud-observations.json). These relative evidence links resolve from the repository root by their written paths; exact filenames are below.

## Findings

- Visible speed 0, 10, 11, 26, 58, 94, 100, 47 and 12 KPH; gears 1–5 and R; positions 1–4 match the corresponding observation HUD text. Three digits fit the speed plate with KPH separate. Gear pulse growth remains inside its small circular instrument. Position pulses remain separated from POSITION and /4.
- Timer, lap, standings, LAST SPLIT heading, numeric approximate splits and dash states remain readable without new text clipping or text-to-text collision. The known tachometer 6 touching the big speed bezel is historical evidence already identified by root; root reports a subsequent source fix. This set cannot verify that later fix and it is not reported as a new duplicate.
- The right instrument cluster does cover substantial nearby rival bodywork in `hud-gear-3.0.png`, `hud-position-3.0.png`, and `hud-position-4.0.png`. This is a concrete peripheral visibility tradeoff, not proof of collision/AI failure. The central forward road remains clear. A blindspot receipt would be needed to assess whether the separate warning compensates.
- `hud-nitrous-full.png` actually shows **BOOST UNAVAILABLE**. Its filename is not evidence of installed, charged, or active boost. All race images show this unavailable state.
- Measured approximate splits are now rendered, superseding the earlier audit's blanket missing-split claim. `hud-measured-split.png` shows Leon ~+0.2s and dash states for unmatched/own rows; later captures cover positive, negative and ~+0.0s values. This visual review does not establish the timing algorithm's accuracy.

## Exact coverage and fresh render receipt

All receipts report `window_can_draw: true`; sampled time is 1–3 ms after completed render. Serial 22 legitimately supplies four labels from the same countdown frame; those are not four independent runtime states. Other serials progress to 1232.

| Exact filename | Serial | Completed / sampled ms | Speed | Gear | Position |
|---|---:|---:|---:|---|---:|
| hud-loading-event.png | 3 | 1329 / 1330 | — | — | — |
| hud-speed-1-digits.png | 22 | 2544 / 2547 | 0 | 1 | 1 |
| hud-gear-1.0.png | 22 | 2544 / 2547 | 0 | 1 | 1 |
| hud-position-1.0.png | 22 | 2544 / 2547 | 0 | 1 | 1 |
| hud-nitrous-full.png | 22 | 2544 / 2547 | 0 | 1 | 1 |
| hud-speed-2-digits.png | 162 | 7358 / 7361 | 10 | 1 | 1 |
| hud-gear-2.0.png | 164 | 7723 / 7726 | 11 | 2 | 1 |
| hud-measured-split.png | 171 | 8228 / 8231 | 11 | 2 | 1 |
| hud-position-2.0.png | 217 | 9763 / 9766 | 26 | 2 | 2 |
| hud-gear-3.0.png | 258 | 11182 / 11184 | 58 | 3 | 2 |
| hud-position-3.0.png | 259 | 11529 / 11532 | 58 | 3 | 3 |
| hud-gear-4.0.png | 297 | 12849 / 12852 | 94 | 4 | 1 |
| hud-speed-3-digits.png | 316 | 13681 / 13684 | 100 | 4 | 1 |
| hud-gear-5.0.png | 349 | 14845 / 14847 | 47 | 5 | 1 |
| hud-background-early.png | 478 | 18439 / 18441 | 12 | 2 | 3 |
| hud-position-4.0.png | 616 | 22218 / 22220 | 0 | 1 | 4 |
| hud-gear--1.0.png | 1232 | 37655 / 37658 | 0 | R | 4 |

## Limits and judgment trace

Missing from this particular evidence set: post-fix tach layout, active/installed boost if supported by the game, drift/objective score, results, active blindspot warnings, other tracks, and small-window HUD behavior. These are coverage gaps, not claims that production features are missing. No fictional NOS-active requirement is introduced. The parent supplied run exit 0 and log name `check-d9d5a655167d4cd4867254ec04bac3d9.log`; that exact log was not present under this checkout's `build` or repository file inventory during this audit, so exit status is parent-reported rather than independently read here.

Jev/TypeSafe: host visual transcript screened (review, injection .36 due to transcript's meta wording; host review found no external instruction to follow). Jev verified all four bounded claims: values match transcript (confidence .74, review), split/unavailable-boost limitation (.88), peripheral rival occlusion (1.0), post-run fix unverified (1.0). Host manually cross-checked the values against the original pixels and compact JSON table after the review flag. Jev evaluates the textual transcript and claims, not the original pixels; host visual inspection remains the evidence source.

# Reference pack review: tuning, settings and editor selection

Reviewed 2026-11-04 against `output/pdf/Racing_Game_HUD_UI_Reference_Pack.pdf`, using the actual rendered pages under `build/verification/ui-hud/reference-pack-reread/`. Scope: all **12 assigned pages, 19–24, 31–35 and 37**, plus five existing implementation screenshots. No code edits or new native captures. References inform original composition; they are not artwork to copy.

## Page coverage

| PDF page | Actual visual inspection | Concrete lesson and boundary |
| --- | --- | --- |
| 19 / R17 | FH5 intake grid, installed text badge separate from magenta focus, car right, specification table and performance graph below | Distinguish installed from focused; keep car visible. A graph is not required unless Oversteer has meaningful data to explain. |
| 20 / R18 | FH5 differential tabs; performance column left; FRONT/REAR/CENTER slider groups middle; values/end labels; description right | One selected row carries a strong accent and its explanation has a stable place. Do not import differential simulation or this screen's complexity. |
| 21 / R19 | GT7 wide tier tabs, four-column illustrated part/price cards, right car/specification panel | Consistent image/name/price positions make parts scannable. Original simple part icons could help; no external branded parts or new catalog scope. |
| 22 / R20 | GT7 setup: track/difficulty/reward/start summary left; two-column outlined options right; disabled items muted | Separate consequences/start action from editable values. This is a race-setup comparison, not a reason to add unsupported settings. |
| 23 / R21 | F1 tyre screen: tabs, four aligned rows of names/arrows/sliders/value/range; selected white row; diagram/explanation right | Row alignment and current-value/range hierarchy can improve setup controls. The source's tyre-pressure simulation is not an Oversteer requirement. |
| 24 / R22 | F1 formation-lap overlay: bottom comparison of one-stop/two-stop stint bars and labeled pit windows; separate top state strip | Good compact comparison vocabulary; pit strategy is outside current scope. Do not add pit mechanics. |
| 31 / R29 | FH5 accessibility: selected magenta row, description column, subtitle preview; several enlarged labels visibly clipped; subtitle and lower prompts overlap | Preview is useful, but this image is also a layout failure example. Never reproduce fixed-width clipping or prompt/preview collisions. |
| 32 / R30 | Forza Motorsport accessibility: subtitle/narrator section dividers; aligned values/sliders; selected dark/yellow row; description right | Stable value column and section rhythm reduce visual scanning. Screen narration is a separate feature, not implied by this presentation task. |
| 33 / R31 | Forza Motorsport video: selected graphics mode, two dark comparison previews, bright logo brightness sample, explanatory column | A truthful preview can explain a visual setting. Do not add fake previews, new HDR settings or rendering options merely to fill space. |
| 34 / R32 | ACC assists: short aligned option/value/arrow list, preset strip, bright help panel right | Small option sets can be compact and orderly. A huge white help panel would compete with Oversteer's identity and is unnecessary. |
| 35 / R33 | DiRT preferences: dense left list with named bilateral slider endpoints, full white selected row, separate description, Apply below | The selected setting should be unmistakable without recoloring every option. Oversteer autosaves; do not add Apply solely to imitate the reference. |
| 37 | Six enlarged component crops: focus versus installed, selected slider, F1 aligned range row, car carousel, pictured part selector, priced tier cards | Compare state distinction and hierarchy only: crops are independently scaled, so apparent text/control sizes are not physical-size measurements. |

Every listed page was opened as a rendered image, not inferred from PDF text. Original sources and capture classifications remain those linked in the supplied PDF; this review does not independently reauthenticate every source image.

## Implementation comparison and actionable findings

Evidence viewed:

- `build/verification/ui-hud/settled-navigation/settings-rebound.png` — settled orange/cream settings layout, keyboard/gamepad columns, audio bars and reset control.
- Historical `build/verification/ui-hud/refined-editors/customization/performance-default.png` and `tuning-positive.png` — upgrades/stage pips plus handling setup, endpoints and percentages, unobscured car.
- Historical `build/verification/ui-hud/refined-editors/customization/wheels-mesh.png` — wheel icons, Stock Installed/Mesh In cart, clear side-profile car.
- Historical `build/verification/ui-hud/refined-editors/customization/cart-multiple.png` — item list left, car center, cash/total/remaining right, purchase/keep/discard separated.

**1. Selected adjustment hierarchy is the strongest bounded opportunity.** Pages 20, 23 and 35 assign one entire row a clear active state. Historical tuning spreads attention among separate plus/minus buttons, percentage, rail and small endpoint labels. Consider a restrained cream or orange row-edge/background treatment tied to existing focused adjustment, keeping values and rails aligned. Do not turn every setting into an equally strong plate. Verification should cover keyboard/controller plus/minus movement and longest explanatory text, without changing adjustment values, simulation or transaction commands.

**2. Make the state vocabulary explicit.** Page 19 and page 37 show focus and installed as distinct signals. Historical wheel evidence has a cyan focus treatment on Paint while Wheels is the current underlined tab, with named Installed/In cart text in the part list. This is not proof of broken navigation; focus and current page are different states. Keep the distinction legible through a consistent current-tab indicator, bounded focus treatment and text badges. Preserve the installed-stage count versus pending-stage pips already present; color alone must not imply ownership or payment.

**3. Settings already has useful structure; refine its controls rather than adding a new menu system.** The settled capture groups driving/display/profile, keyboard, gamepad and audio and has readable row alignment. The controller bindings retain blue-gray rounded fields while other actions use angled orange/cream plates. A coherent keycap treatment and unmistakable focused row are a smaller presentation improvement than building new category tabs. Reset bindings must remain distinguishable from ordinary adjustment and back. Do not add new accessibility/rendering systems from pages 31–34.

**4. Contextual help exists in current source; the historical stills cannot establish it is absent.** Focused reads of `crates/oversteer-godot/src/lib.rs` found `setting_context` around line 1572, `tuning_context` around line 1603, and deferred `focus_entered` connections around lines 3920/3940. They update named `SettingHelp`/`TuningHelp` labels. Tuning copy already describes steering ±10%, gearing ±15%, grip ±5% and front-weight ±0.03. Generic helper text is also used to initialize those labels around lines 4695 and 7296. Therefore the useful remaining question is visibility, wrapping and placement of **existing** focus help, not whether to implement it. Current interactive operation is unverified by this review. Preserve the source's actual ranges; the displayed setup percentage is a normalized adjustment, not a physical percent for every parameter.

**5. Retain the editor/car and transaction strengths.** Historical wheel preview exposes the full side profile and both wheels, matching the car-first benefit of page 19. The cart shows `$25,000`, `$5,500`, `$19,500` and separated destructive action. These are strong visible structures to carry into the orange/cream presentation. A card grid or permanent explanation panel must not reclaim the protected vehicle stage or hide cart consequences.

## Judgment checks and limits

Repository discovery began with `jg` on the explicit narrowed root `/Users/nicolas/Documents/github/oversteer/crates/oversteer-godot`, using `--max-requests 8000 --concurrency 20`. Its complete process was awaited; byte-limited output omitted most source, so focused `rg`/reads established the exact help handlers and signal connections. The parent supplied PDF text had already passed screening; this review used trusted local rendered pages and screened its own visual transcript before judgments.

Jev audited four motif records against that host-produced transcript. Selection, settings and preservation records passed with P(wrong) 0.25, 0.31 and 0.26. The compact tuning record was flagged at **0.70** (incompleteness; hallucination 0.66): it compressed page 20's named endpoints and page 23's numeric ranges into one statement. The page-by-page table above keeps those observations separate; this flag was not retried away. Jev sees text, not pixels; host visual inspection remains the evidence.

A separate six-item Jev classification assigned two presentation candidates (state distinction and row hierarchy, top probability 0.97 each), one item needing runtime evidence (help behavior, 0.87), one preserve item (car/cart, 1.00), and two defer-scope items (pit/accessibility functionality and unnecessary category-tab rewrite, 1.00 each). All classification margins met defaults. These judgments advise; they do not authorize changing gameplay or invent test results.

No claim is made that historical cyan editor screenshots depict the latest build. No new gameplay test, input check, frame-time measurement, screenshot or animation inspection was run. Any implementation should use the existing verification budget to inspect current focused states, help wrapping, cart state differences and car visibility. Stills do not prove persistence, focus correctness, purchases or animation quality.

## Current editor capture inspection: all 25 images

Follow-up: opened **every PNG** in `build/verification/ui-hud/reference-editors/customization/` (21) and `parts/` (4) at original detail. These are current orange/cream editor captures, unlike the historical cyan evidence above. No new captures were taken. Paths in this table are relative to `build/verification/ui-hud/reference-editors/`.

| Exact file | Inspection result |
| --- | --- |
| `customization/performance-default.png` | Clear full car, legible upgrades and zero setup; known weight-balance endpoint/help overlap at bottom. Root already changed row spacing; this image predates its recapture. |
| `customization/performance-upgraded.png` | Stage 1/3 orange pips remain separate from Installed 0; prices readable; same known bottom overlap, no new vehicle occlusion. |
| `customization/tuning-positive.png` | Steering +100%, other displayed setup +20%, positive rails visible; same known overlap. These are displayed normalized controls, not inferred physical percentages. |
| `customization/tuning-negative.png` | Steering −100% rail goes left; remaining displayed +20%; same known overlap. |
| `customization/finish-installed.png` | Installed finish label legible; full car and wheels remain clear in paint booth. No additional clipping found. |
| `customization/wheels-stock.png` | Stock Installed text, all four pictured rows readable; both wheels and entire side-profile vehicle clear. |
| `customization/wheels-sport.png` | Sport In cart text and changed rendered wheel visible; car clear. Stock/Sport row thumbnails appear visually identical (minor unresolved concern below). |
| `customization/wheels-mesh.png` | Mesh In cart; mesh wheel geometry plainly visible and unobstructed. |
| `customization/wheels-deep-dish.png` | Deep Dish In cart; rendered wheel differs; side profile clear. |
| `customization/parts-empty.png` | Stock body only, readable wrapped explanation naming the Civic and three alternate customization actions. No panel covers car. |
| `customization/vinyl-empty.png` | Empty layer selector; Add/Back/Forward and category/design controls fit; empty-state explanation readable. No transform controls shown for no layer. |
| `customization/vinyl-single.png` | One layer named; graphic thumbnail beside editor; color, X/Y/Angle/Width/Height and separated Delete fit. Car fully clear. |
| `customization/vinyl-multiple.png` | 2/2 layer selector, overlapping graphics visible on car; controls fit. |
| `customization/layer-order.png` | 2/2 selector and layered car graphics readable; no UI overlap. A still cannot prove the layer-order command's effect. |
| `customization/layer-deleted.png` | 1/1 selector and single-layer car presentation; layout intact. A still cannot prove deletion/persistence. |
| `customization/transforms.png` | All numeric transform fields readable, no clipping. They show 0.00/0.00/0.0°/1.00×/1.00× in this frame; no claim of transform-action failure can be made from it. |
| `customization/cart-empty.png` | Empty copy, $25,000 cash, $0 total, $25,000 after; car clear; purchase/keep/discard separated. Purchase $0 has orange focus outline and muted text (behavior unverified). |
| `customization/cart-multiple.png` | Seven rows fit; cash $25,000, total $5,500, after $19,500 legible; car completely between columns. |
| `customization/cart-confirmation.png` | Intentional modal covers car. Count 7, total $5,500, after $19,500 and Cancel/Purchase action labels fit; no text clipping. Modal car coverage is not an editor-stage defect. |
| `customization/cart-cancelled.png` | Same seven-item ledger/amounts legible. UI slightly shifted/faded compared with settled cart frame: possible transition-frame evidence, not proof of a steady-state layout defect. |
| `customization/final.png` | Empty cart and unchanged $25,000 totals legible; header sits closer to top edge than cart-empty frame, consistent with a transient capture; no text is cut. |
| `parts/parts-populated.png` | Nissan Seats/Spoiler options fit with Preview state labels, full vehicle clear. No installed/payment state inferred from Preview. |
| `parts/parts-wing.png` | Selected Varis Wing has Preview label and actual visible wing; vehicle and wing unobstructed by UI. |
| `parts/parts-seats.png` | Native Seats has Preview label, but rear exterior camera and dark opaque windows prevent visually judging the interior-seat change. This is the concrete additional preview limitation. |
| `parts/final.png` | Same seat-preview limitation as parts-seats; short list and exterior car remain clear. |

### Findings to carry forward

**Additional concrete limitation:** `parts/parts-seats.png` and `parts/final.png` do not let the player inspect the selected seats. A preview label is not a visual preview of the interior. The exterior wing comparison works. A seat-focused view would need to expose the actual interior; do not infer missing seat geometry or change part availability from these stills.

**No additional hard text clipping found** beyond the root's already reported performance help overlap. All 24 nonmodal frames preserve UI-free car bodies and wheels; the confirmation is intentionally modal. Cart typography remains readable even though large summary numbers now use the condensed display face. Several left controls slightly overhang the angled background's right edge, but do not obscure the vehicle or cut text; this is a lower-priority alignment polish issue.

**Unresolved minor observations, not promoted to bug fixes:** Stock/Sport wheel thumbnails appear identical although actual wheel previews differ; an exact asset comparison would be needed. Empty-cart Purchase $0 visually retains a focus outline despite muted text; a still does not show whether it is disabled or what selecting it does. The transform and layer-order stills cannot establish whether commands were exercised successfully. Preserve transaction/input semantics until behavioral evidence establishes an issue.

The current-capture transcript passed Jev screening (injection 0.03). Audit passed the seat and nonmodal-visibility records, P(wrong) 0.13 and 0.45. It flagged compressed minor-concern and vinyl records for incompleteness at 0.74 and 0.80 (hallucination 0.68/0.67); these remain qualified observations rather than automatic fixes, and were not retried. Jev verification against the detailed transcript supported the three bounded claims—cart amounts, seat-view limitation, and no additional hard clipping found—at 0.98/0.99/0.99. These judgments compare text; they do not independently inspect pixels. The full original-detail host inspection is the visual evidence.

# Remaining UI/HUD acceptance audit

Read-only audit, 2026-11-04. Scope: all **136 numbered + 117 V rows** in `docs/game/UI_HUD_CHECKLIST.md`, their current receipts and existing rendered evidence. This records missing requirements and evidence, not a new stylistic wish list. No code, checklist edits or native captures. Working-tree changes may supersede the source observations after this audit.

## Follow-up correction: reference-ticket captures

Current follow-up inspected original-detail `reference-ticket-editors/customization/vinyl-single.png`, `vinyl-multiple.png`, `cart-empty.png`, `cart-multiple.png`, `cart-confirmation.png`, plus `reference-ticket-navigation/quick-dossier.png`. Cart prices are now right-aligned; the vinyl launcher has an actual RGBA chip; V067 arrows already flank the vehicle card. **The earlier V067 missing-feature claim was stale and incorrect**: it repeated the old checklist note instead of checking current source. Source places arrows x548/1320 around the card636..1296, confirmed by current pixels. No checklist edit was made.

One regression remains: moved-left Remove overlaps the selected cart row car subtitle in `cart-multiple.png`. The subtitle spans y+29..47; Remove begins at y+40, a seven-pixel intersection, visibly cutting the lower subtitle. Prices, totals, modal copy and car visibility are otherwise clear. Root was notified and has changed row height to76 and Remove to y+48/h28; a fresh capture remains necessary before resolving the regression. The vinyl single/multiple chips are white in these frames; source uses actual RGBA over checker backing, but a colored/transparent chip was not captured in this25-image family. No separate color PNG exists here, so nonwhite/alpha visual acceptance remains unverified.

Jev verification against the screened inspection transcript supported the V067 correction0.91, cart regression1.00 and RGBA-source/white-only evidence limit0.99. These are text-evidence judgments, not independent pixel inspection.

## Current finance follow-up: all 13 images

`reference-finance/verification.json` now records finance passed, exit0,13 images, all checks true and errors empty. Every `reference-finance/finance/*.png` was opened at original detail:

| Exact filename | Observed result |
| --- | --- |
| `dealer-owned.png` | Civic OWNED, buy action muted, clear model and specs. |
| `dealer-affordable.png` | Mini $19,500 with wallet $25,000; available, primary Buy; full vehicle clear. |
| `buy-confirmation.png` | Mini identified, price $19,500, balance $25,000, after $5,500; Cancel and explicit Buy fit. |
| `buy-cancelled.png` | Back to dealer with $25,000 and Mini still available. |
| `buy-complete.png` | Mini OWNED and wallet $5,500; buy action muted. |
| `dealer-unaffordable.png` | S2000 $51,000, wallet $5,500; explicit Insufficient Funds and red price/muted Buy. |
| `garage-multiple.png` | Mini2of2, base value $19,500, sale proceeds $9,750, separated Customise/History/Sell; clear car. Installed-upgrade summary near y958 crosses a bright floor stripe, reducing contrast but remaining readable. |
| `history.png` | Purchase price and total spent $19,500, acquired by Purchased; clear history values and Back. |
| `sell-confirmation.png` | Exact Mini identity and Cancel/destructive Sell fit. Modal does not repeat sale proceeds (shown on underlying garage); no extra sale-modal detail requirement inferred. |
| `settings.png` | Normal/Balanced/default audio percentages, categories, keycaps and specific Difficulty help fit. |
| `long-name.png` | Alexandra Montgomery-Kim fits fully in driver-name field. |
| `settings-changed.png` | Hard/Low, audio60/90/90/75 and long name fit. Difficulty focus is visible but helper is generic; possible transient/deferred-focus state, not a proved persistent bug. |
| `final.png` | Main menu with purchased Mini fully visible and text clear. |

No hard text clipping, incorrect displayed purchase arithmetic or nonmodal panel/car overlap was found. This current finance family supersedes the initial audit's finance-pixel gap for these states, **not** the separate wager/pause/results outcome matrix. One/multiple garage variants and full state coverage still require exact matching evidence; this review does not turn one receipt into blanket acceptance. No game launch or new capture was performed by the reviewer. Jev verified these three bounded finance/visibility/settings claims at0.99/0.99/1.00; two transcript audit records passed with P(wrong)0.27/0.44.

## Initial implementation-gap findings, with current disposition

| Requirement | Evidence | Required next result |
| --- | --- | --- |
| **V048: opponent relative split times** | Checklist explicitly says NOT implemented. Current `reference-instruments/hud-observations.json` standings contain rank/name, without relative seconds. | A truthful read-only timing design plus native evidence. Progress distance divided by speed must not be labeled a measured time gap. If authoritative comparison history is unavailable, document the precise limitation and decision; do not silently mark this firm subrequirement complete. |
| **083: right-aligned cart item prices — implemented; regression open** | New `checkout_menu` uses x280/width136/RIGHT; `reference-ticket-editors/customization/cart-multiple.png` confirms aligned amounts. Moved-left Remove clips selected car subtitle. | Repair subtitle/Remove overlap, preserving the right-aligned amounts and authoritative totals. Earlier left-alignment evidence is historical. |
| **V084: Vinyl Color swatch preview — implemented** | New `palette()` uses actual RGBA over checker backing; ticket single/multiple frames show a white tint chip clear of label. | Nonwhite and alpha appearance remain visually unverified; do not claim those states from white-only captures. Earlier missing-chip evidence is historical. |
| **V067: car arrows flank active card — already implemented** | Current source x548/1320 arrows and `reference-ticket-navigation/quick-dossier.png` confirm literal flanking. | Earlier omission claim withdrawn; old checklist wording is stale. |
| **071/V087: selected interior part can be inspected — visually addressed** | Original ticket `parts-seats.png` and `parts/final.png` now show a separate Part Preview card with two clear seat models above the fully visible car. Historical exterior-only screenshots no longer represent this state. | The selected seats can be inspected without hiding the car. No missing-geometry claim. |

The known tuning endpoint/help overlap is **not a new open duplicate**: the root repaired row spacing and the checklist cites `reference-window/tuning.png` as inspected. Older `reference-editors` performance PNGs still exhibit it and must remain explicitly pre-fix evidence.

## Hypotheses requiring decisions, not automatic feature growth

**V052 blind-spot proximity:** the later visual direction requests a bounded in-engine chevron/arc experiment, while the original brief says not to add radar/mirrors/opponent arrows merely because a reference contains them. A nearby-rivals comparison on both sides, plus an explicit keep/omit decision, resolves the hypothesis. No inspected current receipt demonstrates that experiment; absence of a shipped indicator alone is not a failed mandatory feature.

**V088 / brief vinyl-camera hypothesis:** current source/captures establish a bounds-fitted exterior preview and donor-UV decals, not a Side/Top/Hood/Rear toggle system. Check feasible existing preview viewpoints and record the result. Do not build a new projection editor or imply recovered target-surface metadata. Current car visibility is good, but hypothesis closure needs an evidence-backed camera decision.

**V053 drift cadence:** current `reference-briefings/drift` observes zero only. Existing historical near-target/target-reaching evidence does not verify the latest score/banked/active typography and temporal distinction. Inspect existing authoritative chain/banked states in a current bounded live/motion run, without changing scoring.

## Complete numbered-row reconciliation by family

“Current partial” means the receipt establishes some named behaviors/layouts, not whole-family acceptance. “Historical” does not mean broken; it means current changed presentation remains unverified.

| Rows | Latest relevant evidence and remaining work |
| --- | --- |
| 001–005 | `reference-stage-navigation` plus `reference-window/title.png` give current title/main/focus routes. Number001's old single-action wording is superseded by the explicit subordinate Quick Race requirement V103. Stage navigation JSON has95 checks, all `passed:true`; no whole-goal inference. |
| 006–010 | Current navigation reaches career, but fresh/partial/promotion-ready canonical career-state pixels remain historical/unrefreshed. Need exact current state fixtures, not a redesigned map. |
| 011–024 | `reference-stage-navigation/quick-dossier.png` and `quick-last-page.png` refresh Quick Race setup. Current career locked/ineligible/completed/promotion states and setup/results agreement remain partial. V067 is implemented and visually confirmed in the ticket follow-up. |
| 025–030 | Current stage navigation is not a full wager suite. Accepted/declined/unavailable cash/pink paths, owned-rival disablement and truthful offered-versus-active copy need current evidence. A run named refined-pink-loss previously won; it cannot establish loss. |
| 031–038 | Dealer purchase/cancel behavior appears in stage navigation, including transfer of ownership and return focus. The new finance follow-up above refreshes multiple-car, affordable/unaffordable, sale confirmation/history, names/spec-bar pixels; one-car-specific state is not inferred from those images. |
| 039–045 | Current25 editor captures provide shell, category strip, preview visibility and cart/header evidence. Focus versus current page is visible as separate signals; no broken-input claim follows from stills. |
| 046–050 | Current installed finish and small-window paint screen inspected. These do not refresh every finish preview, light/dark color, precision or scalar-state branch. |
| 051–057 | Current vinyl empty/single/multiple/order/delete/transform frames + editor action receipt. Color chip is implemented in the ticket follow-up; nonwhite/alpha, long graphic names and camera hypothesis remain; do not infer command failure from unchanged transform values in one still. |
| 058–062 | All four available wheel styles have current unobstructed side-profile frames and actual rim options. Stale 'latest camera pending' text can be replaced with exact frame references after owner reconciliation; no invented fifth design. |
| 063–067 | Current stage/default/positive/negative frame/action coverage; source already contains focus help. Root's compact spacing fix has small-window evidence. Need current focused-help wrapping and installed versus pending semantic review; not a new help feature. |
| 068–071 | Current empty Civic and populated350Z list/wing evidence exists. Ticket follow-up now shows two clear seat models in a Part Preview card, leaving the car clear. |
| 072–081 | Only paint overview has current reference-window evidence. Full palette/precision/alpha/light-dark/material min-middle-max/cost/accept-cancel matrix still relies on older compact-paint receipts. |
| 082–087 | Current empty/multiple/cancelled/confirmation cart frames show correct displayed $25,000/$5,500/$19,500 arithmetic and separated actions. Row083 price alignment is implemented; selected Remove/subtitle overlap is a new ticket-follow-up regression. Current insufficient-funds, long description and actual committing checkout need exact receipts; stills alone are insufficient. |
| 088–099 | Stage navigation purchase modal focus/escape/B/ownership transfer refreshed. Current finance follow-up refreshes purchase breakdown and selected sale/history states; current pink-slip two-way risk modal, last-car/unavailable cases, accepted/cancel/commit/outcome branches remain partial/historical. |
| 100–104 | No current `reference-*` cash/pink pause-forfeit confirmation/commit suite found. Preserve actual rules; test no-stake vs cash vs vehicle warnings and restart/exit confirmation semantics. |
| 105–110 | Stage navigation's reset/rebind checks include keyboard/button/axis defaults, unrelated setting preservation and persistence; settings images exist in reference-stage-navigation and reference-window. Checklist 'reset persistence pending' is stale. Long driver name now inspected in current finance; changed-settings generic-help observation remains bounded above. |
| 111–114 | `reference-briefings/circuit` and `/drift` provide two current loading destinations and outline composition; latest references supersede 'latest loading pending'. Verify each event/car/stake fact from its actual state; no artificial loading delay. |
| 115–123 | `reference-instruments`16 observations cover1/2/3 digit speeds, gears1–5/R and positions1–4. Need measured bright/dark readability, nearby rivals both sides, actual available gear/unit states and honest nitrous limitation. V048 relative timing remains missing. |
| 124–129 | Current briefing drift run shows zero objective only. Latest near/reached/above/large/banked/active state and live readability remain open, not covered by circuit instruments. |
| 130–136 | No current reference-results/wager outcome family was present in the audited inventory. Historical Quick Race $0, paid career, drift and pink win are not a current full result/promotion/podium/loss sweep. |

## V-row overlay reconciliation

| V rows | Status / precise dependency |
| --- | --- |
| V001–V002 | Ongoing verification contract: current family receipts exist; not all matrix states or final independent review complete. |
| V003–V013 | Current shared-shell/editor/window evidence partially supersedes generic pending wording. Preserve safe margins and protected car stage; full palette/status-header verification remains; V067 exact layout is already confirmed. |
| V014–V029 | Cyan/exact typography prescriptions are superseded where the user explicitly rejected them. Functional contrast, state semantics and formatted money/time remain required; do not revert orange identity to satisfy stale token text. |
| V030–V034 | Current actions/category layouts exist; current keyboard/controller evidence exists. Timed transition interruption and full destructive-state distinction need actual evidence. |
| V035–V036 | Current full paint/palette/material matrix missing; older compact-paint evidence retained, alpha unresolved. |
| V037 | Current four wheel images supersede camera-pending wording, subject to owner pixel acceptance. |
| V038–V047 | Current reference instrument observation/run exists; stale normal-speed-pending wording should point to it. Nitrous-active and all-background acceptance not established by these labels. |
| V048 | Relative split time firm subrequirement missing. |
| V049–V053 | Latest drift target/cadence matrix and blind-spot hypothesis open. |
| V054–V058 | Purchase-modal behavior partially current; pink risk/forfeit/outcomes need current suite. Loading V057 refreshed by two briefing destinations. |
| V059–V066 | Current Quick Race dossier/routes/pages refreshed; locked/promoted career variants remain. |
| V067 | Already implemented and visually confirmed; initial audit claim corrected. |
| V068–V074 | Current13-image finance sweep now inspected; see exact filenames above. This does not prove wager/results or every ownership variant. |
| V075–V078 | Current editing proves stage annotations; corrected compact tuning needs focused-help current evidence. |
| V079–V082 | Current cart/header frames supersede recapture-pending wording; committing checkout/insufficient funds still partial. |
| V083–V084 | Current vinyl cards and actual RGBA tint chip exist; nonwhite/alpha visual states remain unverified. |
| V085–V087 | Current empty/populated/wing refreshed; seat preview visually addressed by the ticket follow-up. |
| V088 | Camera hypothesis needs recorded feasibility decision. |
| V089–V092 | Full current rival/stakes state suite remains missing. |
| V093–V096 | Current outcome/podium/results matrix remains missing. |
| V097–V098 | Current main navigation refreshed; career progression-state variants remain. |
| V099–V102 | Current reset/rebinding/persistence receipt refreshes stale pending rows; long-name/focus-help wrapping acceptance still precise follow-up. |
| V103–V104 | Current title/credits references refresh recapture-pending wording. |
| V105–V117 | Aggregates cannot be marked complete from partial families: depend respectively on car/paint matrix, actions, finance, stakes, career, events, finance specs, tuning, loading, results, circuit HUD, drift HUD, settings/money. |

## Small-window title and paint inspection

Opened `reference-window/title.png` and `paint.png` at original detail. `window-evidence.json` records1440×810 OS client and1920×1080 design viewport, so these are scaled native-window observations, not newly rendered1920px images. Both show complete text and actions; the car silhouette and wheels are clear of panels. No clipping defect was reproduced. Title's orange kicker plate reaches the left boundary while its text is inset; this is not missing text. Paint overview contains every listed finish and readable price plus Back/Review. These two images do not prove palette/modal/scalar states or all viewport sizes.

## Receipt cautions and judgment limits

`reference-editors/verification.json` records customization passed/exit0/21images and parts passed/exit0/4images, with all listed checks true. `reference-stage-navigation/navigation.json` contains95 passed check records. These raw counts are not a claim of253 requirements passing. The current split/standings source discovery began with required `jg` settings on the explicit Godot subtree, awaited completion, and used focused reads after output truncation.

All16 `reference-instruments` observations and the two briefing observation sets have `native_discipline:null`; their `nitrous-full` labels show **NITROUS · UNAVAILABLE IN THIS EVENT**. They cannot be presented as boost-active/extremes coverage. The current drift briefing observations show zero; filename 'drift' alone is not target-completion evidence. Do not alter game rules to force otherwise unavailable nitrous states.

Jev verification supported the price/chip omission at0.99 and no clipping in the two inspected window frames at1.00. It gave review-level support for the combined split/hypothesis claim (0.66) and nitrous-evidence caution (0.84). A composite receipt-count/acceptance claim was unsupported with low same-subject0.37; it is not used as completion evidence. This note therefore states exact raw receipt fields and preserves open acceptance decisions. No judgments were retried to erase uncertainty. Jev checks text evidence; actual host image inspection remains necessary.

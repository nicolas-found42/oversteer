# Oversteer UI/HUD Improvement Brief

Goal: Implement a coherent, polished UI/HUD pass for Oversteer that improves clarity, consistency, hierarchy, and presentation while retaining its quiet urban tuner identity, car focus, and existing gameplay. Complete the implementation, run the game, review actual rendered screenshots, and iterate until the observable acceptance criteria below are met.

## 1. Working contract and evidence boundaries

Inspect the repository before changing code. Read and follow the root `AGENTS.md` and any applicable nested instructions. Identify the existing UI scenes/components, themes, preview cameras, input navigation, state bindings, transaction logic, and screenshot/build tooling. Preserve unrelated working-tree changes.

This specification is based on the reviewed `oversteer-ui-hud-benchmark.pdf`, including Oversteer captures **OS-01–OS-26** and seven reference games. The relevant observations are described below; you do not need the PDF to implement them. Treat these captures as evidence of one build. If the current repository already resolves an issue, retain the improvement and verify it.

Maintain these distinctions:

- **Visible observation:** Something directly present in a screenshot, such as an obscured wheel, an unlabeled value, or equally emphasized actions.
- **Design requirement:** A deliberate presentation decision to implement.
- **Hypothesis to validate:** Something requiring repository inspection or runtime evidence before deciding how to change it.

Screenshots do not establish animation quality, input latency, focus traversal, live scoring cadence, loading speed, or whether transaction handlers behave correctly. Test those behaviors where relevant; do not describe them as proven defects.

Respect the benchmark’s match limitations:

- **Same task** means comparable player intent, not identical cars, cameras, progression, control schemes, or rules.
- **Partial matches** support only the portion of the task shown. Free starter-car selection does not establish purchase behavior; a customization tutorial does not establish live editing behavior.
- **Analogues** support structural principles only. All ownership-risk confirmation references are analogues. Burnout’s face-off award does not demonstrate risking an owned car.
- ProStreet provides the direct drift-scoring comparison. Other action-feedback screenshots do not establish equivalent drift mechanics.
- The material-adjustment references are principally tuning/geometry analogues, with a partial paint-shop tutorial; they cannot establish Oversteer’s material units or behavior.
- Recording overlays, filmed-display artifacts, compression, pillarboxing, edition differences, and camera differences are not interface defects.

Preserve physics, AI, race rules, scoring, payouts, progression, vehicle ownership, save compatibility, tuning effects, and optional wagering. Preserve the underlying meaning of previewing, selecting, adding to cart, purchasing, and canceling. Expose existing state more clearly. Keep structural changes limited to what these UI improvements require.

## 2. Visual direction and reference principles

Build around **a composed London tuner workshop**: charcoal surfaces, off-white typography, restrained teal accents, precise numeric information, and existing cars and environments presented deliberately.

Retain the existing wordmark, “Find your line.” identity, garage/paint-booth settings, readable speed display, and generally clear central driving view. Use “Find your line.” consistently where a tagline is appropriate; avoid competing taglines across screens.

Borrow these principles rather than another game’s branding, graphics, or complete layout:

| Reference | Principle to apply | Evidence and limitation |
| --- | --- | --- |
| **Forza Motorsport 4** | Deliberate car composition, clear vehicle information, and itemized outcomes. | Recurring title `fm4-title`, owned-car selection `fm4-0037`, and results `fm4-0056` are same-task examples. |
| **Midnight Club: Los Angeles** | Compact task controls positioned around a useful car preview; contextual pause presentation. | Paint `mcla-0001`, wheels `mcla-0008`, and pause `mcla-0043` support these principles. Its Complete Edition title is only a partial comparison. |
| **Gran Turismo 5** | Structured event facts, organized inventory information, and explicit settings categories. | Event entry `gt5-0020`, garage `gt5-0026`, and settings `gt5-0074` are same-task examples. Its inventory density is unnecessary for Oversteer’s scale. |
| **Midnight Club 3: DUB Edition** | A clear relationship between the car, its price/specifications, and the current task. | Dealer `mc3-0000` is a same-task example with qualified original-edition confidence. Tutorial customization frames support presentation principles only. |
| **Need for Speed: ProStreet** | Selected-category context, understandable tuning controls, and a distinct hierarchy for drift objectives. | Main menu `prostreet-0007`, tuning `prostreet-0047`, and drift `prostreet-0089` support these principles; their mechanics remain their own. |
| **Burnout 3: Takedown** | Strong outcome emphasis and an obvious next action. | Results `burnout3-0007` is a same-task example. Its other modes and reward structures do not justify adding mechanics. |
| **Driver: San Francisco** | A dominant selected menu item and recognizable setting values. | Main menu `driver-0001` and settings `driver-0029` are same-task examples. Its challenge rewards are partial result comparisons. |

### Shared UI/HUD rules

Establish reusable theme values and component treatments before applying the screen changes. The following numbers are **proposed targets at 1920×1080**, not measurements taken from the references. Adapt through the repository’s existing scaling/layout system and verify smaller supported viewports.

1. **Spacing and alignment**
   - Use an 8 px spacing basis, normally selecting from 8, 16, 24, 32, and 48 px.
   - Use approximately 48 px outer safe margins, 24 px panel padding, and consistent 16–24 px gaps between related controls.
   - Align related labels, values, panel edges, and action rows. Use left-aligned names/descriptions and right-aligned monetary amounts.
   - Reduce oversized empty panels. Preserve useful negative space around the car.

2. **Typography**
   - Use one readable, locally available sans-serif family with a small, consistent weight hierarchy.
   - Start around 40–48 px for screen titles, 28–32 px for section headings, 20–24 px for controls/body text, and 18–20 px for secondary labels.
   - Keep speed approximately 64–80 px and major drift/result values approximately 44–56 px, adjusting after rendered review.
   - Use tabular numerals for speed, time, scores, prices, and counters. Reserve stable numeric widths so changing digits do not move neighboring information.
   - Use sentence case for explanations. Reserve uppercase for short headings and labels. Do not solve long names by shrinking them below readable size.

3. **Color and surfaces**
   - Use a compact palette near background `#0B1014`, surface `#141C22`, primary text `#F3F5F4`, secondary text `#AAB8C0`, and accent `#81CBC4`.
   - Use restrained amber for warnings and muted red for destructive consequences, always paired with wording or a symbol.
   - Use opaque surfaces where reading is the task and translucent, tightly fitted backing where the driving scene matters.
   - Check text against its actual rendered background, including bright scenery. Do not assume transparency preserves contrast.

4. **Selection, focus, and actions**
   - Give the primary committing action a distinct filled treatment.
   - Give persistent category/option selection a restrained fill, underline, or side marker.
   - Give keyboard/controller focus a separate, clearly visible outline. Focus, installed state, preview state, and primary-action importance must not all look identical.
   - Use explicit “Installed,” “Preview,” or “In cart” labels only when those states exist in the underlying model.
   - Keep destructive actions secondary and spatially separated from routine actions.
   - Disabled controls must retain a readable label and explain the reason where relevant.

5. **Navigation**
   - Preserve all existing destinations and supported input methods.
   - Use a consistent Back location and an accurate input-hint footer. Group event controls with events, car controls with cars, and editing controls with their values.
   - Keep one dominant committing action per task.
   - Validate navigation order, focus restoration, and modal containment in the running game. These are implementation checks, not screenshot-proven failures.
   - Do not add extra navigation steps merely to resemble a reference game.

6. **Money, names, and terminology**
   - Format currency consistently, for example `$25,000`. Preserve the existing currency and economy.
   - Distinguish purchase price, base value, sale proceeds, wager amount, reward, and wallet balance.
   - Normalize vehicle-name presentation without changing identifiers or save data.
   - Use one spelling convention for interface labels. Use **Colour**, **Tyres**, and **Customise** consistently in player-facing copy while preserving technical identifiers.
   - Replace raw asset identifiers with readable display names where reliable catalogue information exists.

7. **Vehicle presentation**
   - Calculate the usable preview rectangle after allocating controls, then frame the car inside that rectangle.
   - Keep the complete vehicle visible for general selection and finish comparison. Keep the edited component unobstructed for close inspection.
   - Use stable, comparable framing when switching cosmetic options.
   - Limit camera adjustments to menu/customization previews. Preserve the gameplay camera.

8. **Shared components**
   - Reuse a small set of headers, list rows, labeled-value rows, option selectors, action buttons, confirmation dialogs, status labels, and HUD groups.
   - Use task-specific compositions within that system. A settings page, purchase dialog, and race HUD should share visual rules without becoming identical layouts.

## 3. Priorities

Use these priorities throughout:

- **P1:** Clarify potentially costly decisions, conflicting mode information, or obscured task-critical content.
- **P2:** Improve common-task readability, information grouping, and navigation hierarchy.
- **P3:** Refine composition and identity where the existing presentation already works.

The five main outcomes, in order, are:

1. Accurate money, ownership-risk, and mode-specific consequences.
2. Unobstructed customization previews and understandable editing controls.
3. Clear race/drift objectives and instrument meanings.
4. Consistent event, vehicle, and navigation context.
5. Composed entry, utility, loading, and results presentation.

Implement the shared foundation first, then resolve the affected screens in that priority order.

## 4. Required screen and state improvements

### Entry and main navigation — OS-01, OS-02 — P2/P3

**Visible:** The title screen already has a readable wordmark, tagline, one Start Driving action, and a car preview. The car is surrounded by substantial empty garage space. The main menu has **five** visible actions—Career, Quick Race, Options, Credits, and Save & Quit—with very similar treatment. A teal focus border already exists.

**Implement:**

- Retain the single-action title screen. Compose the title, tagline, and Start Driving action as one intentional group.
- Reframe the car to occupy roughly two thirds of its available preview width while keeping the complete silhouette visible.
- Keep the short vertical main menu. Group Career and Quick Race as the main activities; separate Options/Credits and Save & Quit through spacing and quieter treatment.
- Strengthen the focused row without making inactive choices difficult to read.
- Show one concise contextual sentence for the focused activity using existing game facts.

**Why:** A more deliberate first impression and clearer activity hierarchy without expanding the navigation system. Treat title composition as P3; the current wordmark is not demonstrably illegible.

### Career overview — OS-03 — P2

**Visible:** Tier and cash appear above six similarly treated routes. Progress is behind a Progression button. The car sits against the sidebar edge while substantial space remains elsewhere.

**Implement:**

- Show a compact summary of current tier, balance, current car, and actual progress toward the next promotion.
- Make Race Events the clear route forward.
- Preserve Progression, Garage, Dealership, Options, and Main Menu.
- Frame the vehicle within the unobstructed content region.
- Derive progression wording from canonical data. If there is no defined next event, show actual requirements and available-event access.

**Why:** The hub should communicate current situation and next available action. A new geographic career map or recommendation system is outside this task.

### Quick Race setup — OS-04 — P1 for context, P2 for layout

**Visible:** The screen combines an event list, central car, a large prose panel, and distributed event/car navigation controls. It shows career cash/wins, prize amounts, and “A win counts toward tier promotion.” Course identity is not visible in the summary.

**Hypothesis to validate:** The benchmark identifies the captured results run as non-career, but the setup displays career reward/progression copy. Inspect Quick Race’s actual reward, persistence, car-availability, and progression rules before changing that copy.

**Implement:**

- Keep setup on one screen.
- Give event and vehicle selection clearly labeled regions; place each selector’s controls beside it.
- Structure the event summary as course, mode, laps or actual drift objective, and applicable conditions.
- Reuse an existing route outline or course thumbnail to identify the selected course.
- Make Start Race the sole dominant committing action.
- Display reward/progression information appropriate to the actual mode. If Quick Race does not pay or advance career, state that plainly.
- Make setup and results describe the same rules. Correct presentation without changing payouts or progression.

**Why:** The player should understand exactly what they are entering and what the outcome affects.

### Career event selection — OS-05 — P2

**Visible:** Three available events appear in the list. The details mix mode, laps, prizes, objective, eligibility, promotion, and wagering explanation as similarly weighted sentences separated by large gaps.

**Implement:**

- Retain the useful event-list/car/details relationship.
- Replace the prose wall with ordered sections: event name; course/mode; laps/objective; eligibility; rewards; promotion effect.
- Add a compact course outline or existing thumbnail.
- Align reward amounts and use concise labels.
- Keep the selected car’s identity and eligibility visible near Start Race.
- Show completed, locked, or ineligible states only where they exist, with truthful reasons.
- Retain accurate optional-wager information without making it compete with the event objective.

**Why:** Structured facts support comparison and reduce the need to reread the entire panel.

### Rival selection and pre-race stakes — OS-06 — P1

**Visible:** The screen already says betting is optional. Rival names appear on the left, a rival/car preview in the center, and cash/pink-slip/start actions on the right. “OFFER $1000” resembles another action. The selected rival’s car model and current wager status are not visible.

**Implement:**

- Keep the rival/car preview central and add the selected rival’s actual name and vehicle identity.
- Organize the wager panel around current wager status, a labeled amount control, cash offer, separated pink-slip offer, and Start Race.
- Make the no-wager route explicit, for example “Start race — no wager” when that is the actual state.
- Render offered, accepted, declined, or active status only when supported by the real state machine.
- Name the exact cash amount or vehicle involved once a stake exists.
- Do not imply that an offer is accepted or a stake is committed before the underlying logic says so.

**Why:** Optional wagering should be understandable without accidentally making a risky action appear to be the required next step.

### Owned garage and dealership — OS-07, OS-08 — P2

**Visible:** Both screens show a car name, an unlabeled monetary amount, and tier with substantial unused preview space. Garage gives Customise and Sell Car similar emphasis. Dealership gives Customise and Buy Car similar emphasis. Some names are inconsistently assembled; one reads “Honda HONDA S2000 ’03.”

**Implement:**

- Share a selected-car presentation: readable manufacturer/model, tier/class, ownership/current-car status where applicable, and a small set of meaningful existing specifications.
- Label each monetary amount according to its actual meaning.
- Left-align list entries. Handle long names with sensible wrapping or truncation while retaining the complete selected name in the detail area.
- Fix duplicated manufacturer wording in presentation logic.
- Improve preview framing without changing vehicle assets.
- In Garage, emphasize Customise, retain Vehicle History, and separate Sell Car as secondary.
- Communicate inventory position, including “1 of 1” where applicable, and accurately represent unavailable navigation.
- In Dealership, place actual purchase price, wallet balance, and affordability together. Use an explicit purchase action such as “Buy vehicle — $15,000.”

**Hypotheses to validate:** Determine which specifications are canonical and what dealership Customise actually does. Do not invent performance ratings, estimated top speeds, or a new customization transaction flow.

**Why:** Vehicle choice needs trustworthy identity, comparison facts, and financial context.

### Shared customization shell — OS-09, OS-10, OS-14–OS-16, OS-18, OS-19 — P1/P2

**Visible:** Large title/cash/cart banners and deep lower control bands consume substantial space. Paint views show a large car with lower bodywork hidden; wheel and other editing views show a smaller car whose relevant components still intersect the lower panel.

**Implement:**

- Use one compact header for task title, selected vehicle, cash, and cart count/total.
- Use one clearly marked category strip.
- Place task controls in a consistent side inspector beside a reserved vehicle stage, replacing the overlapping lower slabs.
- Start around an 80–96 px header and a 360–440 px inspector at 1080p; adjust after rendering to protect both legibility and preview space.
- Keep a predictable Back route and access to modification review.
- Separate category selection, focus, installed option, and preview/cart state.
- Keep the entire relevant car surface visible while adjusting it.

**Why:** The vehicle is the evidence used to judge a cosmetic choice. Controls must not cover that evidence.

### Paint finish — OS-09 — P2

**Visible:** Colour, six finishes, and global customization categories form two rows of similarly treated buttons. Help text sits over the car. The frame does not independently identify the installed or previewed finish.

**Implement:**

- Separate **Colour** from **Finish** within the inspector.
- Present the existing finishes as a concise option group with readable names and truthful installed/preview state.
- Place help text within the inspector.
- Keep cash and cart summary visible without large banners.
- Preserve all existing finish choices and their costs.

**Why:** Changing an appearance option should look distinct from navigating to another customization category.

### Vinyl editing — OS-10 — P2

**Visible:** Many equal-looking buttons fill the left inspector. A raw name such as `LOGO_3_3` is exposed. Transform values are detached from their controls. Decrease/increase order changes between position and rotation/size controls.

**Implement:**

- Group controls into **Layer**, **Graphic**, and **Transform**.
- Make the active layer and order clear; preserve add, delete, move-forward, and move-back operations.
- Use readable catalogue-derived names and existing thumbnails where available.
- Give every transform the same row structure: label, decrease, current value/unit, increase.
- Keep rotation in degrees and retain the actual position/scale units.
- Separate Delete from routine adjustments.
- Enlarge and frame the preview so the edited surface remains visible.

**Hypothesis to validate:** A surface-specific camera may help placement. Use existing projection information and preview controls if available; do not create a new projection/editor system.

**Why:** Controls and results should be easy to associate, and opposite adjustments should occupy predictable positions.

### Wheel customization — OS-14 — P2

**Visible:** Stock, Sport, Mesh, and Deep-Dish are text options. The near wheel is partly hidden by the lower band, and the view is too distant for useful shape comparison.

**Implement:**

- Use a stable side or three-quarter preview with at least one complete near wheel clearly visible.
- Present actual wheel designs with name, actual price, and installed/preview state.
- Use existing thumbnails or lightweight renders of the real wheel assets where feasible.
- Keep wheel colour separate from wheel design.
- Maintain comparable camera framing across choices.

**Why:** Wheel selection is a visual comparison task; the relevant object must be visible at a useful scale.

### Performance upgrades and tuning — OS-15 — P2, with mandatory semantic validation

**Visible:** Steering, Gearing, Tyre Grip, and Weight Balance show `0%`, alongside stage-zero upgrade buttons. The captured screen does not explain those values, their endpoints, costs, or tradeoffs.

**Implement:**

- Separate **Upgrades** from **Tuning adjustments** within the screen.
- Show installed stage, selected option, actual cost, and applicable state for upgrades.
- For tuning, show the current value, meaningful endpoints/range, and one concise explanation of the actual effect.
- Show numerical before/after differences only when backed by existing game data.
- Use aligned value rows and consistent adjustment controls.

**Hypothesis to validate:** `0%` may mean a neutral offset. If so, label it as default or an offset rather than implying zero tyre grip. Verify semantics before changing text or units; preserve bounds and simulation effects.

**Why:** Players need to understand what a purchase or adjustment changes. Invented performance graphs and a new tuning model are outside scope.

### Body-parts empty and populated states — OS-16 — P2

**Visible:** The captured car shows “No compatible body or interior parts available” in a large mostly empty area. Only an empty state is evidenced.

**Implement:**

- Use the heading **Body parts** and name the selected car in the empty-state message.
- Provide a clear route to another existing customization category or car selection.
- Explain unsupported, locked, or unavailable status only if the catalogue distinguishes them.
- If compatible vehicles already exist, apply the shared selector treatment to their populated state: actual part, price, installed/preview state, and unobstructed preview.

**Why:** An empty state should explain the current situation and the available next action. Do not create parts or unlock systems to populate this screen.

### Paint colour selection — OS-18 — P2

**Visible:** A wide lower panel covers much of the car. It combines a large swatch grid with small, visually different RGB/hex controls, tiny steppers, an unexplained `I` field, and a Precise Color button while precision controls are visible.

**Implement:**

- Move colour selection into the shared inspector.
- Make swatches the primary selection view and place precision controls in a clearly labeled section.
- Use the shared typography, field styling, spacing, and focus treatment throughout.
- Ensure the selected swatch remains identifiable on both very light and very dark colours; include a separate colour chip/value.
- Retain valid ranges and existing colour-space semantics.
- Keep cost and explicit selection/back actions close to the controls.

**Hypotheses to validate:** Determine what `I` represents and whether selection previews, stages, or commits a change. Label the actual meaning and preserve the existing transaction behavior.

**Why:** Precise adjustment should remain readable while the bodywork stays visible.

### Paint material adjustment — OS-19 — P2

**Visible:** A mostly empty, very large panel contains Pearlescent Balance, a slider, price, and Accept/Back. It hides the lower car and lacks a displayed value or meaningful endpoints.

**Implement:**

- Use a compact material-control section with label, current value, validated endpoints, and a short effect description.
- Keep painted surfaces visible under consistent preview lighting.
- Preserve the underlying value, range, and accept/cancel semantics.
- Determine whether the displayed price belongs to the overall paint choice or a separate charge, then label it accurately.

**Why:** The interface should explain the adjustment and leave room to assess it. The reference analogues do not establish units or physical behavior.

### Modification review/cart — OS-17 — P1/P2

**Visible:** The existing **Balance / Total / After purchase** summary works well. The item description is generic—such as “Wheel swap”—and Purchase, Keep Customising, Remove Item, and Discard All have similar emphasis.

**Implement:**

- Preserve the financial summary and authoritative calculations.
- Left-align item descriptions, right-align prices, and name the exact selected option where data permits.
- Use an explicit primary action such as “Purchase — $1,000.”
- Keep Keep Customising secondary, associate Remove with the selected item, and separate Discard All.
- Show truthful empty-cart and insufficient-funds states.
- Prioritize transaction clarity over adding a larger vehicle preview.

**Why:** The player should know exactly what is being bought and what remains afterward. Reference purchase/save dialogs are partial comparisons, not justification to replace the useful cart structure.

### Vehicle purchase confirmation — OS-20 — P1

**Visible:** The modal names the vehicle and shows price and current cash, but not remaining cash. Confirm is generic. Cancel is visibly focused in the capture, which does not prove initial-focus behavior.

**Implement:**

- Use a compact shared confirmation dialog with vehicle identity, price, current balance, and remaining balance.
- For the supplied example, `$25,000 − $19,500` must display `$5,500`.
- Use “Buy vehicle — $19,500” or an equivalent action-specific label.
- Put Cancel and the committing action in consistent positions.
- Verify safe initial focus on Cancel, modal focus containment, and return focus in live use. Do not reset focus on every redraw.
- Preserve affordability checks and purchase semantics.

**Why:** Concrete wording and remaining balance make the consequence reviewable before commitment.

### Pink-slip confirmation — OS-21 — P1

**Visible:** The dialog asks whether to risk the vehicle and names it, but uses generic Confirm/Cancel labels without plainly describing the loss consequence.

**Implement:**

- Use a concise heading such as **Risk your car?**
- Prominently name the actual wagered vehicle.
- State the actual consequence. If confirmed by code: “If you lose this race, you lose [vehicle] from your garage.”
- Use an explicit action such as “Confirm pink-slip wager,” with restrained warning styling and safely focused Cancel.
- Include actual opponent/stake context where available.
- Preserve the optional no-wager path.

**Why:** Ownership consequences deserve explicit language. Do not invent claims about permanence, recovery, or commitment timing, and do not introduce a new betting or hold-to-confirm system.

### Pause — OS-13 — P1/P2

**Visible:** Resume, Restart Race, Options, and Quit to Menu accompany an oversized warning about forfeiting accepted stakes and restarting without a new bet. The screenshot does not establish whether a wager is active.

**Implement:**

- Keep Resume primary and the paused scene visible.
- Group Resume/Options and separate Restart/Quit.
- Replace the oversized generic warning with a compact consequence card tied to the actual active stake.
- Name the amount or vehicle when applicable; do not imply a wager loss in a no-wager race.
- Preserve actual restart/forfeit rules and existing confirmation flows.

**Why:** The player should understand the consequence relevant to the current race, with returning to play remaining the clearest action.

### Settings — OS-11 — P2

**Visible:** Keyboard bindings occupy one column; Driving contains difficulty, quality, speed units, and a detached driver-name field; audio values and gamepad bindings occupy another area. Different control types look like similar buttons.

**Implement:**

- Organize existing settings into Driving, Controls, Audio, Display, and Profile categories with one coherent content panel.
- Place Difficulty and Speed Units under Driving, Quality under Display, and Driver Name under Profile.
- Separate Keyboard and Gamepad binding groups.
- Align action labels with distinct key/button/axis values. Group driving controls logically.
- Present audio as consistent labeled rows with percentages and a modest fill indicator, preserving current value handlers.
- Put contextual help beside the relevant group.

**Hypotheses to validate:** Inspect listening/rebinding states, device prompts, and navigation behavior. Style existing states clearly; do not assume the screenshot proves remapping failures.

**Why:** Category and control-type clarity reduce visual searching without adding settings.

### Credits — OS-12 — P3

**Visible:** The page is already calm and readable, with provenance text and a clear Back action.

**Implement:** Retain that treatment, add a modest Credits/About heading, use deliberate section spacing and comfortable line lengths, and preserve all existing attribution. Include only repository-authored factual content.

**Why:** This screen needs consistency and reading rhythm, not a new presentation concept.

### Loading — OS-22 — P2

**Visible:** A mostly black screen displays “Loading… 83%” and a Speed Challenge tip without identifying the destination.

**Implement:**

- Show the actual queued event, course, and mode/objective.
- Use a compact progress presentation tied to the real loading signal.
- Reuse existing course imagery/outline if available.
- Separate tips from destination information.

**Hypothesis to validate:** The Speed Challenge tip may not fit the queued event or existing modes. Check before replacing it. Do not infer stalled loading from the captured percentage, fabricate progress, or delay loading to display the design.

**Why:** Transitions should maintain context about where the player is going.

### Circuit HUD and nearby opponents — OS-23, OS-24 — P2

**Visible:** The four-corner layout already leaves the central road clear, and speed is already the largest instrument. Time/lap occupy the upper left; position and four names occupy the upper right; a square map sits lower left; speed, gear, an unlabeled teal meter, and nitrous sit lower right. In the nearby-opponent capture, part of a rival car falls beneath the map backing.

**Implement:**

- Preserve the corner anchors and central driving view.
- Tighten panel backing around content using consistent padding and margins.
- Keep speed dominant. Show ordinary values such as `16 MPH` without unnecessary leading zeroes, while retaining stable numeric width.
- Keep gear and units immediately legible but subordinate.
- Trace the unlabeled meter’s data source. Label it RPM only if that is what it represents; distinguish it clearly from nitrous.
- Emphasize current position over field size and make lap progress more distinct from its label.
- Keep the four-person standings compact and mark the player’s row with text plus restrained emphasis.
- Fit the route to the map area and remove surplus opaque backing. Preserve readable route and position information.
- Use heading/start-finish markers only if supported by existing data.

**Hypothesis to validate:** A tighter map footprint may improve peripheral opponent visibility. Compare actual nearby-car scenes before and after without changing the driving camera. Do not add proximity radar, mirrors, or opponent arrows merely because a reference contains them.

**Why:** Improve instrument meaning and peripheral visibility while retaining the existing useful glance pattern.

### Drift HUD — OS-25 — P1/P2

**Visible:** Drift adds a standalone “SCORE 898 / 1000” line while the usual position/standings retain prominence. Only score and target are established by the capture.

**Implement:**

- Give score and target a compact, aligned objective group near the upper center.
- Make the score primary and target secondary; a restrained progress track may represent the existing ratio.
- Use the same typography, backing, and spacing system as the rest of the HUD.
- Preserve map and instrument anchors across modes.
- Determine whether position and lap affect drift outcomes. Retain them appropriately, with score carrying the mode’s primary hierarchy.
- Show “Target reached” only from authoritative state and without implying the event has ended if it has not.

**Hypothesis to validate:** Active drift, chains, multipliers, pending points, or invalidation cues may exist in code, but the screenshot does not prove them. Display such states only if already implemented; do not add scoring mechanics.

**Why:** The mode’s actual objective must be more prominent than inherited circuit information.

### Results — OS-26 — P2

**Visible:** A large panel says Race Complete, Position 2, time, and `Race Reward +$0`, with substantial unused space. Continue, Watch Replay, Restart Race, and Podium have similar treatment. This capture is non-career; zero payout alone is not a defect.

**Implement:**

- Lead with the actual outcome, such as **2nd / 4**, with final time secondary. Use the correct score/target outcome for drift.
- Identify event, course, and mode.
- Show actual reward components and wager outcomes where available.
- Explain non-career payout context instead of leaving an unexplained `+$0`.
- Distinguish earned reward from resulting wallet balance.
- Make Continue primary, Replay/Podium secondary, and Restart clearly separate.
- Size the panel to its content.

**Why:** The screen should explain what happened, what changed, and the next action. Do not invent XP, records, multipliers, or statistics.

## 5. Visual verification and acceptance criteria

Capture the existing implementation before editing, then comparable rendered states after each major screen family changes. Use actual game output, not standalone mockups. Use isolated test saves and the repository’s existing capture facilities.

Capture at **1920×1080** and the smallest supported desktop viewport. Check additional aspect ratios only where the repository supports them. Keep event, car, save state, and camera comparable; document intentional preview-camera changes.

Cover every affected screen above, including these representative variations:

| Area | Representative states |
| --- | --- |
| Entry/navigation/career | Title; focus on main and utility actions; fresh career; partial progress; promotion-ready or completed state if supported. |
| Event setup | Career and Quick Race; circuit and drift; each existing course; long names; existing locked/ineligible conditions. |
| Garage/dealer | One and multiple owned cars; long names; affordable/unaffordable purchase; selection changes; existing sale and history routes. |
| Wagers/pause | No wager; accepted cash stake; vehicle stake; supported declined/unavailable state; confirmation and cancellation; paused consequence display. |
| Customization | Installed and previewed finish; each existing wheel style from comparable framing; unobstructed edited surfaces. |
| Vinyls | Empty, single, and multiple layers where supported; long graphic name; each transform; layer order and deletion. |
| Tuning/body parts | Default and upgraded stages; adjustment endpoints; existing unavailable states; body-parts empty state and populated state if one exists. |
| Paint | Light/dark selected swatches; precision controls; material minimum/middle/maximum; truthful prices. |
| Transactions | Empty, single-item, and multi-item cart; insufficient funds; long descriptions; purchase/cancel; remaining-balance calculations. |
| Circuit HUD | Bright and dark existing scene backgrounds; one-, two-, and three-digit speeds; available gears; nitrous extremes; each position; nearby rivals on both sides. |
| Drift HUD | Zero, near-target, target-reached, and above-target score; largest supported values; existing scoring substates only. |
| Results | Win and non-winning finish; non-career zero payout; paid career result; existing cash/vehicle wager outcomes; drift result. |
| Utilities | Each settings category; long driver name; supported rebinding states; credits; at least two loading destinations. |

The work passes when:

- Relevant car surfaces, wheels, and selected parts are not hidden behind editing controls.
- Text does not clip, collide, or become illegible at supported sizes.
- Focus, selection, installed/preview state, primary actions, and destructive actions are distinguishable.
- Each control is visually associated with the value or object it changes.
- Money and consequence copy match authoritative state. Purchase/cart arithmetic is correct.
- Quick Race setup and results agree about payout and progression.
- Race HUD values remain readable against tested backgrounds without covering the central road.
- Compacting the minimap reduces surplus backing without reducing route readability.
- Drift score/target have a clear hierarchy and do not imply nonexistent mechanics.
- Numeric changes do not shift adjacent labels or controls.
- All existing destinations remain reachable; modal cancellation and return focus work; no action leaks through an open modal.
- Gameplay, scoring, progression, purchases, ownership, and save behavior remain unchanged apart from the intended presentation improvements.

## 6. Implementation and iteration requirements

Implement the improvements rather than stopping at an audit or plan.

Work in coherent screen families using the shared theme/components. After each major pass, run the actual game, inspect screenshots at native size, and correct remaining problems in spacing, hierarchy, alignment, preview framing, wrapping, and contrast. A successful build alone is not visual verification.

Run the repository’s required checks and focused behavior checks for touched state bindings, settings, purchases, wagers, and navigation. Broaden testing only to resolve a concrete regression risk or satisfy repository requirements.

For each hypothesis, record what repository or runtime evidence established and which presentation decision followed. If a proposed detail lacks authoritative data, omit that detail and document the limitation rather than fabricating it. Continue with the supported improvements.

Finish with a concise report containing implemented screen changes, representative before/after screenshot locations, verification performed, resolved hypotheses, and any precise remaining blockers. Do not claim visual completion for screens that were not rendered and reviewed.

Goal: Elevate Oversteer’s UI and HUD to the readability, visual hierarchy, contextual clarity, and polish of mature racing benchmarks while preserving its quiet London urban tuner identity, restrained palette, car-centric presentation, and all existing gameplay mechanics.

---

## 1. Agent Workflow, Guardrails & Execution Contract

1. **Inspect Repository & Follow `AGENTS.md**`:

- Before writing code, read `AGENTS.md` and inspect the Godot scene tree, UI theme resources, control scripts, HUD overlays, camera controllers, and Rust/GDScript data bindings. Follow all build, linting, formatting, and screenshot-capture workflows defined in `AGENTS.md`.

1. **Preserve Gameplay & State Behavior**:

- Do not alter vehicle physics, AI behavior, career progression math, economy values, upgrade simulation parameters, or optional cash/pink-slip wagering rules.

- Keep existing user flows short and predictable. Do not add new game modes, fake features (such as a Dealership "Test Drive" button), or decorative tilted/3D-skewed menus that violate Oversteer’s grounded aesthetic.

1. **Respect Static-Evidence Boundaries (Firm Decisions vs. Hypotheses)**:

- The specifications below come from a static `1920x1080` visual benchmark against seven reference games (_Midnight Club: Los Angeles_ [MCLA], _Forza Motorsport 4_ [FM4], _Gran Turismo 5_ [GT5], _Midnight Club 3: DUB Edition_ [MC3], _Need for Speed: ProStreet_ [ProStreet], _Burnout 3: Takedown_ [Burnout 3], and _Driver: San Francisco_ [Driver: SF]).

- Implement **Firm Decisions** directly. Treat items marked **Hypothesis to Validate** as in-engine experiments because static screenshots cannot prove animation cadence, input feel, focus traversal, or live scoring dynamics.

1. **Render, Capture & Iterate**:

- After implementing changes, run the build and capture native `1920x1080` screenshots across the representative states listed in Section 4.

- Visually inspect every rendered screenshot for text clipping, label overlap, car occlusion, low-contrast HUD elements over bright/dark road surfaces, and focus ambiguity. Iterate on layout, margins, and camera framing until every acceptance criterion passes.

---

## 2. Cohesive Visual Direction & Shared UI/HUD Rules

### Aesthetic Direction: "Precision Urban Workshop & Telemetry"

Oversteer’s identity is a quiet, nocturnal London tuner workshop paired with crisp motorsport instrumentation. Instead of rendering every screen as a stack of identical dark-gray rectangular buttons and opaque black boxes, the UI must separate **navigation chrome**, **contextual data cards**, **primary commitments**, and **unobstructed 3D vehicle inspection**.

### Shared Layout & Spatial Grid (`1920x1080` Base Canvas)

- **Outer Safe Margin**: `48px` horizontal, `36px` vertical on all front-end screens; `32px` on Race/Drift HUDs.
- **Persistent Top Status Bar (`56px` height)**:
- Left: Screen/Context Title (e.g., `CAREER`, `GARAGE`, `DEALERSHIP`, `PAINT STYLE`) with a subtle muted breadcrumb or mode subtitle (`OVERSTEER // LONDON`).

- Right: Structured player status pills showing **Career Tier** (`TIER 1 · LOCAL`), **Wins** (`0 WINS`), **Cash Balance** (`$25,000` formatted with thousands separators), and, when inside Customization, **Cart Summary** (`CART: 1 ITEM · $250`).

- **Left Navigation / Control Column (`360px–420px` width)**:
- Houses primary vertical selection lists, category controls, or tuning sliders on the left side of the screen (`x: 48px` to `448px`), leaving the right two-thirds of the viewport open.

- **Strict Unobstructed Vehicle Inspection Zone (`x: 480px` to `1380px`, `y: 96px` to `920px`)**:
- Across Garage, Dealership, and all Customization screens (`S07`–`S10`, `S14`–`S19`), UI panels must **never** overlap the lower body or wheels of the 3D vehicle preview.

- Keep bottom category bars (`PAINT`, `WHEELS`, `VINYLS`, `PERFORMANCE`, `BODY PARTS`, `SHOPPING CART`, `SAVE & EXIT`) consolidated into a single compact bottom rail (`height <= 64px`) or top tab bar, and adjust the 3D camera target upward/leftward as needed so the entire car sits cleanly in open space.

- **Right Context / Dossier Column (`400px–460px` width, `x: 1412px` to `1872px`)**:
- Used on Event Selection, Quick Race, Rival Stakes, Garage, and Dealership screens for structured specification cards, track outlines, and the primary commit action.

### Shared Color & Surface Tokens

- **Canvas & Panel Surfaces**:
- **Primary Panel Surface**: Deep slate-charcoal `rgba(14, 18, 24, 0.88)` with a `1px` subtle border `rgba(255, 255, 255, 0.10)` (replaces flat, heavy opaque boxes).

- **Elevated / Card Surface**: `rgba(22, 28, 38, 0.94)` with a `2px` left or top structural accent rule.

- **HUD Backplate**: Frameless or soft horizontal gradient `rgba(10, 13, 18, 0.65)` fading to transparent, relying on crisp text shadows/outlines rather than thick dark rectangles.

- **Semantic Accent Palette**:
- **Primary Focus / Active Selection Accent**: High-visibility tuner amber/gold `#F5A623` or crisp ice-cyan `#38BDF8` (pick one primary accent and apply it consistently across all focused rows, active tabs, and primary CTA buttons; currently focused items only show a faint `1px` light border that barely stands out from unselected rows).

- **Positive / Cash / Eligible / Ahead**: Emerald `#34D399`.

- **Warning / Wager Stake / Near Redline**: Amber `#FBBF24`.

- **Destructive / Pink-Slip Risk / Deficit / Ineligible**: Crimson `#F87171`.

- **Typography & Numeric Hierarchy**:
- **Hero Display / HUD Speed & Position Numerals**: Bold condensed or geometric sans-serif with `tabular-nums` (`48px–64px`, weight `700–800`).

- **Screen Titles**: `28px–32px` uppercase, weight `700`, letter-spacing `0.06em`.

- **Section Headers / Card Titles**: `18px–20px` uppercase, weight `600`, letter-spacing `0.05em`.

- **Body / Row Labels**: `15px–16px` medium (`#F1F5F9` active, `#94A3B8` unselected).

- **Metadata / Micro-Labels**: `12px–13px` uppercase (`#64748B`), always paired with larger high-contrast values so labels never compete with data.

- **Currency & Time Formatting**: Format all currency with thousands separators (`$25,000` instead of `$25000`, `$1,000` instead of `$1000`) and all lap/race times with tabular numerals (`01:58.31`).

### Shared Component & Navigation Rules

1. **Three-Tier Action Button Hierarchy**:

- **Primary Commit Action** (`START DRIVING`, `START RACE`, `BUY CAR`, `PURCHASE`, `CONTINUE`, `RESUME`): High-contrast filled accent background, bold dark text, prominent height (`48px–52px`), visually isolated at the bottom of the active task panel.

- **Secondary Navigation / Utility Action** (`QUICK RACE`, `OPTIONS`, `KEEP CUSTOMIZING`, `WATCH REPLAY`): Dark surface fill with a `1px` border, transforming on focus/hover with a `4px` left accent bar and brighter surface fill.

- **Destructive / Forfeit Action** (`SELL CAR`, `DELETE`, `REMOVE ITEM`, `DISCARD ALL`, `RESTART RACE` / `QUIT TO MENU` when a stake is active, `STAKE MY CAR`): Muted crimson border/text at rest; crimson fill on focus/hover; visually separated by at least `16px` from safe primary actions.

1. **Consistent Footer Input Prompts**:

- Replace tiny, low-contrast footer text (`ENTER/SPACE: SELECT | ESC: BACK` or `ARROWS/TAB: NAVIGATE`) with clean keycap/button badges (`[ENTER] Select`, `[ESC] Back`, `[Q/E] Switch Car`) at `13px–14px` in `#94A3B8`.

---

## 3. Prioritized Improvements by Screen & State (`S01`–`S26`)

### Priority 1 (P1): Critical Occlusion, Costly Error Risk & In-Race Readability

#### 1. Paint, Material & Wheel Customization Viewport Occlusion (`S09`, `S14`, `S18`, `S19`)

- **Current Visible Problem**:
- In **Customization Hub / Paint Finish (`S09`)**, two full-width horizontal button bars across the lower third of the screen (`PAINT COLOR`, `GLOSS`, `METALLIC`, `MATT`, `PEARL`, `FLAKE`, `THINFILM` above `SHOPPING CART`, `PAINT`, `WHEELS`, `VINYLS`, `PERFORMANCE`, `BODY PARTS`, `SAVE & EXIT`) overlap and hide the lower body and wheels of the car.

- In **Paint Color Selection (`S18`)**, a massive opaque dark panel (`SELECT BASE COLOUR`) covers the bottom 45% of the screen—hiding the lower half of the car while combining a coarse swatch grid, `$1000` price tag, `USE CURRENT AS BASE`, and unlabeled `PRECISE COLOR` sliders.

- In **Paint Material Adjustment (`S19`)**, a similarly huge opaque panel covers the lower 40% of the car just to display a single unlabeled `SELECT PEARLESCENT BALANCE` slider (`$1200`) and `ACCEPT` / `BACK` buttons.

- In **Wheel Customization (`S14`)**, wheel choices (`WHEEL COLOR`, `STOCK`, `SPORT`, `MESH`, `DEEP-DISH`, `RACING`) are text-only buttons overlapping the bottom of a distant rear-three-quarter car view where the rims are foreshortened and in shadow.

- **Reference Principles & Match Limitations**:
- _MCLA_ (`SAME TASK` in `S09`, `S14`, `S18`; `ANALOGUE` numeric control in `S19`), _FM4_ (`SAME TASK` in `S09`, `S18`; `PARTIAL` in `S14`; `ANALOGUE` in `S19`), _ProStreet_ (`SAME TASK` in `S09`, `S18`; `PARTIAL` in `S14`; `ANALOGUE` in `S19`), and _GT5_ (`SAME TASK` in `S14`; `PARTIAL` in `S09`, `S18`) keep 100% of the vehicle body unobstructed during cosmetic editing by docking sub-controls in a compact corner/left panel or shallow bottom ribbon, and _MCLA_ + _GT5_ pair wheel selection with a close side-profile camera and visual rim thumbnails.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Relocate Sub-Controls to the Left Panel**: Move finish selection (`GLOSS`, `METALLIC`, `MATT`, `PEARL`, `FLAKE`, `THINFILM`), the `S18` Color Picker, the `S19` Pearlescent Balance slider, and the `S14` Wheel Selector out of the bottom-center viewport and into the left control column (`width: 380px`). Keep global category tabs in a single compact `56px` bottom rail.

- **Separate Coarse Swatches from Fine Color Tuning (`S18`)**: Split `SELECT BASE COLOUR` into a clean 6-column swatch grid at the top of the left panel and a clearly labeled `PRECISE COLOR` section below with explicit `HUE`, `SAT`, and `VAL` (or `R`, `G`, `B`) labels and numeric readouts (`0–360°` / `0–100%`) plus a live color preview chip and item cost (`$1,000`).

- **Compact Material Slider with Endpoints (`S19`)**: Replace the giant `SELECT PEARLESCENT BALANCE` box with a compact left-panel card displaying the current base/pearl color chips, a horizontal slider with named endpoints (`BASE TINT 0%` ◄───► `FULL PEARL 100%`), a live numeric percentage readout, the `$1,200` price, and `ACCEPT` / `BACK` actions.

- **Wheel-Focused Camera & Visual Rim Previews (`S14`)**: When entering `WHEELS`, transition or snap the workshop camera to a side-profile framing focused on the front/rear wheel arch (framing the car in the right two-thirds of the viewport), and add a 2D spoke-pattern icon/thumbnail and price (`$0 Stock` / `$1,000`) to each wheel option row (`STOCK`, `SPORT`, `MESH`, `DEEP-DISH`, `RACING`).

- **Why It Helps**: Players can inspect paint reflections, color shifts, and rim designs across the entire car body without UI panels blocking the exact part they are paying to modify.

#### 2. Race HUD & Drift HUD Hierarchy, Contrast & Mode Specificity (`S23`, `S24`, `S25`)

- **Current Visible Problem**:
- In **Race HUD / Open Road (`S23`)** and **Nearby Opponents (`S24`)**, four heavy dark rectangular boxes occupy all four corners (`LAP 1/1` + `TIME` + full 4-driver standings top-left; `POSITION 1/4` top-right; dim grey-on-black course minimap bottom-left; `016 MPH` + Gear `1` + RPM/Nitrous bars bottom-right). Every box has the same visual weight. The minimap route is low-contrast grey on black, and in `S24` an overtaking rival (`045-2`) enters the bottom-left chase-camera blind spot directly underneath the bulky minimap box.

- In **Drift / Live Scoring HUD (`S25`)**, Oversteer keeps the entire Circuit HUD—including `POSITION 1/4` in the top-right and the 4-driver race standings in the top-left—and simply appends a small `SCORE 898 / 1000` box below the top-left standings.

- **Reference Principles & Match Limitations**:
- _FM4_, _MCLA_, _MC3_, and _ProStreet_ (`SAME TASK` chase-cam HUDs in `S23`; _MCLA_, _FM4_, _MC3_ `SAME TASK` in `S24`) use frameless or lightweight telemetry clusters with strong typographic scale contrast (large numerals for Speed, Gear, and Position; small labels) and high-contrast route lines on the minimap.

- In `S25`, _ProStreet_ (`prostreet-0089`, `SAME TASK`) and _Burnout 3_ (`burnout3-0035`, `PARTIAL`) replace irrelevant circuit position panels with a dedicated, prominent live drift score and target progress bar.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Remove Heavy Opaque Boxes (`S23`, `S24`, `S25`)**: Replace the four solid dark rectangles with frameless typographic clusters backed by subtle directional gradients (`rgba(10, 13, 18, 0.55)`) and `2px` dark text drop-shadows/outlines so telemetry stays crisp against both bright sky/concrete and dark shadows while opening peripheral road visibility.

- **Primary Instrument Cluster (Bottom-Right)**:
- Render Speed in `60px` bold tabular numerals (`16` or `016` with leading zeroes muted in `rgba(255,255,255,0.22)`) and a small `MPH` / `KM/H` unit label.

- Place Gear (`1`–`6`, `R`, `N`) inside a high-contrast badge (`36px` bold) immediately beside Speed.

- Above Speed/Gear, render a crisp horizontal or arc RPM bar with a crimson redline zone (`85%–100%`) and a distinct cyan/amber `NITROUS` bar below.

- **High-Contrast Minimap (Bottom-Left)**:
- Reduce the opaque box footprint and render the course ribbon with a bright light-slate/white fill (`#E2E8F0`) and dark `2px` outer stroke so corners are immediately readable at a glance.

- Render the player as a high-contrast accent chevron and opponents as distinct bordered dots.

- **Race Progress & Compact Standings (`S23`, `S24`)**:
- **Top-Right**: Display `POS` (`1/4` with `1` at `48px` bold and `/4` at `24px` muted) alongside `LAP` (`1/1`).

- **Top-Left**: Display `TIME 00:17.92` (`24px` tabular monospace) above a compact, frameless standings list where the player’s active row is highlighted with an accent bar and opponents show relative split times (`+1.2s`) in `14px` text.

- **Dedicated Drift Mode HUD (`S25`)**:
- When the active event mode is `DRIFT`, hide `POSITION 1/4` and the multi-car circuit standings list (if solo/score-targeted) or demote opponent scores to a compact secondary list.

- Place a prominent **Drift Score & Target Header** at top-center or top-right displaying **Current Score** (`898` in `48px` bold numerals), **Target Score** (`/ 1,000`), a horizontal **Target Progress Bar** (`89.8%` filled, turning emerald upon reaching `1,000`), and live maneuver/angle score feedback.

- **Hypotheses to Validate**:
- _Hypothesis 1 (Blind-Spot Proximity Indicator in `S24`)_: Test adding a subtle amber chevron/arc near the lower-left/right screen edge when a rival car overlaps the rear quarter blind spot in chase camera, ensuring it does not clutter normal driving.

- _Hypothesis 2 (Live Drift Score Pop/Cadence in `S25`)_: Static frames cannot test score tick cadence or combo timeout readability; verify in live play that active drift points vs. banked total score are clearly distinguished.

- **Why It Helps**: Drivers can read speed, gear, upcoming corners, and mode-specific objectives (circuit position vs. drift score) in a single glance without heavy boxes blocking nearby traffic.

#### 3. High-Stakes Confirmation, Pause Forfeit & Loading Accuracy (`S13`, `S20`, `S21`, `S22`)

- **Current Visible Problem**:
- **Confirm Ownership Risk (`S21`)**: Risking permanent loss of an owned car (`RISK YOUR VEHICLE IN A PINK SLIP BET? / Honda CIVIC TYPE R (EK)`) uses a plain modal with generic `CONFIRM` / `CANCEL` buttons and never explicitly states that losing the race permanently forfeits the car or what car will be won.

- **Confirm Vehicle Purchase (`S20`)**: Shows `PURCHASE VEHICLE? / Mini COOPER-S / PRICE $14500 · CASH $25000` with generic `CONFIRM` / `CANCEL` buttons, omitting the resulting cash balance after purchase.

- **Pause / Interruption (`S13`)**: Shows 4 equal-weight buttons (`RESUME`, `RESTART RACE`, `OPTIONS`, `QUIT TO MENU`) beside a large static warning box (`Restarting or leaving forfeits your accepted cash or vehicle stake. A restarted race begins without a new bet.`), while the bottom-right race HUD (`000 MPH`) bleeds through unhidden.

- **Loading / Transition (`S22`)**: Shows `LOADING... 83%` on a pitch-black screen with a tip for **"Speed Challenge"** (`Achieve the target speed as fast as possible and then complete the lap without dropping below the target speed`)—a game mode that does not exist in Oversteer’s circuit/drift scope—and gives zero information about the upcoming track, mode, or rival.

- **Reference Principles & Match Limitations**:
- _MCLA_ (`SAME TASK` in `S13`; `PARTIAL` in `S20`; `ANALOGUE` in `S21`) uses a self-contained pause card and hides underlying HUD noise.

- _MC3_ (`mc3-0028`, `ANALOGUE` delete-save warning in `S21`; `mc3-0013`, `SAME TASK` in `S22`) and _FM4_ (`fm4-0034`, `ANALOGUE` in `S21`; `fm4-0080`, `SAME TASK` in `S22`) state irreversible loss consequences explicitly in confirmation prompts and use loading screens to brief the player on track location, layout, and event parameters.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Ownership Risk Modal (`S21`)**: Keep `CANCEL` as the default focused button. Add a crimson/amber hazard header (`HIGH-STAKES WAGER // PINK SLIP`), state the exact two-way outcome (`IF YOU WIN: Claim rival's [Rival Car Name]` / `IF YOU LOSE: Permanently forfeit your Honda Civic Type R (EK)`), and replace `CONFIRM` with explicit destructive-styled copy: `STAKE MY CAR`.

- **Vehicle Purchase Modal (`S20`)**: Keep `CANCEL` focused by default. Show a 3-row financial breakdown matching the Modification Cart (`Current Cash: $25,000`, `Vehicle Price: -$14,500`, `Remaining Cash: $10,500`) and change `CONFIRM` to `BUY FOR $14,500`.

- **Pause Screen (`S13`)**: Hide the underlying race HUD when paused. Style `RESUME` as the dominant primary action; visually separate destructive exit actions (`RESTART RACE`, `QUIT TO MENU`) with a divider. Make the stake warning contextual: if no bet is active, hide the forfeit warning or show `No active wager at risk`; if a cash or pink-slip bet is active, display an amber/crimson banner stating the exact stake (`ACTIVE STAKE AT RISK: $1,000` or `PINK SLIP: Honda Civic Type R (EK)`).

- **Event Briefing Loading Screen (`S22`)**: Replace the black screen and invalid "Speed Challenge" tip with an **Event Briefing Card** showing: Course Name, 2D Track Outline, Event Mode (`CIRCUIT` / `DRIFT`), Lap Count or Target Score, Selected Car, Active Wager (if any), the loading percentage bar, and gameplay tips strictly curated from Oversteer’s actual mechanics (circuit racing lines, drift scoring, tuning trade-offs, and career wagers).

- **Hypothesis to Validate**:
- _Pause Destructive Confirmation (`S13`)_: Inspect the pause code to verify whether clicking `RESTART RACE` or `QUIT TO MENU` during an active wager immediately forfeits the stake or prompts a confirmation; if it forfeits immediately, add a confirmation step when a cash/pink-slip wager is active.

- **Why It Helps**: Prevents accidental loss of cash or pink-slip vehicles, eliminates out-of-scope placeholder loading text, and prepares the driver for the exact course and rules ahead.

---

### Priority 2 (P2): Task Context, Comparison Hierarchy & Navigation Clarity

#### 4. Quick Race Setup & Career Event Selection (`S04`, `S05`)

- **Current Visible Problem**:
- **Quick Race (`S04`)** and **Career Event Selection (`S05`)** share a nearly identical layout where the right-hand event card (`LOCAL CIRCUIT`) displays small paragraphs of prose (`CIRCUIT · 1 LAP / WIN $2500 · 2ND $1500 / Finish first to win. / Free entry... / A win counts toward tier promotion. / Optional cash bets and pink slips are offered on the career grid.`).

- In Quick Race (`S04`), displaying `WIN $2500`, career promotion text, and career grid wager notes is misleading because non-career quick races actually award `+$0` (as seen in `S26`).

- Neither screen shows a 2D course map/outline, event list rows lack inline mode/completion badges, and redundant `< EVENT` / `EVENT >` buttons sit directly below the clickable vertical event list.

- **Reference Principles & Match Limitations**:
- _ProStreet_ (`prostreet-0023`, `SAME TASK` in `S04`, `S05`), _GT5_ (`gt5-0020`, `SAME TASK` in `S05`; `gt5-0106`, `PARTIAL` in `S04`), _FM4_ (`fm4-0078`, `SAME TASK` in `S05`), and _Burnout 3_ (`burnout3-0015`, `SAME TASK` in `S05`) pair event selection with a 2D circuit outline, structured key-value facts (Course, Laps, Eligibility, Reward), and inline status/mode badges on event rows.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Structured Event Dossier Card (Right Column)**:
- Top header: Event Title (`LOCAL CIRCUIT`) + colored Mode Pill (`CIRCUIT` / `DRIFT` / `PROMOTION`).

- Center visual: 2D vector outline of the selected London course.

- Structured key-value grid: `COURSE`, `MODE`, `TARGET` (`1 Lap` or `1,000 Pts`), `ELIGIBILITY` (`Tier 1 · Local` or `All Cars`), and `REWARD`.

- Mode-accurate Reward & Stakes copy: In **Career (`S05`)**, show `1ST: $2,500 · 2ND: $1,500`, promotion status, and `Optional Cash / Pink-Slip Wagers on Next Screen`. In **Quick Race (`S04`)**, show `PRACTICE / EXHIBITION ($0 Payout · No Career Stakes)`.

- Bottom primary button: Full-width accent `START RACE` (or `CONTINUE TO GRID` in Career).

- **Inline Badges & Streamlined Controls (Left & Bottom)**:
- Add a compact Mode tag (`CIR` / `DRF` / `PRM`) and completion/lock indicator directly inside each left-column event row, and remove the redundant `< EVENT` / `EVENT >` button row beneath the list.

- Consolidate the bottom car selector bar so `< CAR` and `CAR >` flank the active vehicle card (`HONDA CIVIC TYPE R (EK) · Tier 1 Local`) alongside a secondary `CUSTOMIZE CAR` button.

- **Why It Helps**: Players can scan track shape, mode, rules, and true payout in under two seconds without reading paragraphs of prose or confusing Quick Race with Career progression.

#### 5. Garage Owned Vehicle Selection & Dealership Vehicle Shopping (`S07`, `S08`)

- **Current Visible Problem**:
- Neither **Garage (`S07`)** nor **Dealership (`S08`)** shows any vehicle performance specifications—only a small floating bottom card reading `HONDA CIVIC TYPE R (EK) / $12000 Tier 1 - Local`.

- In **Dealership (`S08`)**, the left list of 10 cars shows only vehicle names with no prices, tiers, or ownership badges, forcing the player to click each car individually to check its cost. Furthermore, `CUSTOMIZE` and `BUY CAR` sit side by side with identical visual weight.

- In **Garage (`S07`)**, `CUSTOMIZE`, `SELL CAR`, and `VEHICLE HISTORY` share equal button weight, placing destructive `SELL CAR` right beside `CUSTOMIZE`.

- **Reference Principles & Match Limitations**:
- _FM4_ (`fm4-0037`, `SAME TASK` in `S07`), _ProStreet_ (`prostreet-0004` in `S07`, `prostreet-0054` in `S08`, both `SAME TASK`), _MC3_ (`mc3-0000`, `SAME TASK` in `S08`), _GT5_ (`gt5-0026` in `S07`, `gt5-0097` in `S08`, both `SAME TASK`), and _Driver: SF_ (`driver-0048`, `SAME TASK` in `S08`) pair the 3D car preview with a consistent set of 3–4 comparative performance bars/specs and prominent price/balance hierarchy. (_Note_: Do not copy _GT5_’s multi-dropdown filter density designed for hundreds of cars; Oversteer has 30 cars).

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Vehicle Specification & Comparison Card**: Add a right-hand (or consolidated bottom-right) Vehicle Spec Card in both `S07` and `S08` displaying:
- Manufacturer & Model Name, **Tier Badge** (`Tier 1 · Local`), and **Price / Value** (`$12,000`).

- 3–4 normalized stat bars derived from the car’s actual physics/tuning data in the repository (e.g., **Top Speed / Power**, **Acceleration / Gearing**, **Grip / Tire**, **Handling / Balance**) plus any installed upgrade stage summary in Garage.

- **Scannable Dealership List Rows (`S08`)**: Display the car’s **Tier tag** and **Price** (`$12,000`) right-aligned on every row in the Dealership list (or an `OWNED` badge if already in the garage, and muted red price text if price exceeds the player’s `$25,000` cash).

- **Action Hierarchy (`S07`, `S08`)**:
- In **Dealership (`S08`)**, make `BUY CAR ($12,000)` the dominant primary accent button; relabel or demote `CUSTOMIZE` to a secondary action (or clarify if it previews paint/parts).

- In **Garage (`S07`)**, make `CUSTOMIZE` (and `SELECT CAR` if applicable) primary/secondary, and style `SELL CAR` as a separated destructive action.

- **Why It Helps**: Players can meaningfully compare cars before buying or upgrading and immediately see which Dealership vehicles fit their budget and tier.

#### 6. Performance Upgrades & Tuning (`S15`) and Modification Cart Review (`S17`)

- **Current Visible Problem**:
- In **Performance Upgrades / Tuning (`S15`)**, the left panel (`TUNING PACK`) stacks 4 percentage steppers (`STEERING 0%`, `GEARING 0%`, `TYRE GRIP 0%`, `WEIGHT BALANCE 0%`) directly above 4 stage buttons (`ENGINE STAGE 0`, `TRANSMISSION STAGE 0`, `SUSPENSION STAGE 0`, `TYRES STAGE 0`) with no visual separation, no endpoint labels explaining what `-` vs `+` percentages do, no stage progress indicators (`0/3`), and no visible prices or trade-off descriptions.

- In **Review Modification Purchase (`S17`)**, the financial summary (`CURRENT CASH $25000`, `CART TOTAL $1000`, `CASH AFTER PURCHASE $24000`) is admirably clear, but the screen switches to an opaque dark view that completely hides the 3D car preview, and stacks 4 full-width buttons (`PURCHASE`, `KEEP CUSTOMIZING`, `REMOVE ITEM`, `DISCARD ALL`) with equal weight.

- **Reference Principles & Match Limitations**:
- In `S15`, _ProStreet_ (`prostreet-0047`, `SAME TASK`) labels slider endpoints (`SOFT` ◄─► `STIFF`), _FM4_ (`fm4-0014`, `SAME TASK`) shows a concise handling trade-off explanation for the focused parameter, and _MCLA_ / _Driver: SF_ (`mcla-0003`, `driver-0052`, `SAME TASK`) clearly indicate upgrade levels and prices.

- In `S17`, _MCLA_ (`mcla-0027`, `PARTIAL`) and _GT5_ (`gt5-0100`, `PARTIAL`) preserve visual context of the car/part while confirming the purchase.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Split Hardware Upgrades from Setup Tuning (`S15`)**:
- **Section A — Stage Upgrades**: Render `ENGINE`, `TRANSMISSION`, `SUSPENSION`, and `TYRES` rows with visual stage pips (e.g., `STAGE 0 [□][□][□]`), the next stage’s price, and a concise benefit summary.

- **Section B — Handling & Setup Tuning**: Render `STEERING`, `GEARING`, `TYRE GRIP`, and `WEIGHT BALANCE` with bilateral center-zero slider bars and explicit endpoint labels matching the underlying simulation math (e.g., `SLOW/STABLE ◄── 0% ──► QUICK/SHARP` for Steering; `ACCEL ◄── 0% ──► TOP SPEED` for Gearing; `DRIFT/LOOSE ◄── 0% ──► GRIP/PLANTED` for Tyre Grip; `REAR ◄── 0% ──► FRONT` for Weight Balance).

- Include a 2-line **Tuning Effect Footer** inside the panel explaining the handling trade-off of the currently focused row (do not invent fake telemetry graphs unless backed by real simulation data).

- **Preserve Car Preview & Button Hierarchy in Cart Review (`S17`)**:
- Render the `MODIFICATIONS` cart review over the live 3D workshop view of the modified car (docked on the left/right or as a framed modal that leaves the car visible).

- Keep the 3-box financial summary (`CURRENT CASH`, `CART TOTAL`, `CASH AFTER PURCHASE`).

- Put `REMOVE ITEM` inline on the selected cart item row, style `PURCHASE ($1,000)` as the primary accent button, `KEEP CUSTOMIZING` as secondary, and `DISCARD ALL` as a compact destructive action.

- **Why It Helps**: Eliminates guesswork when adjusting percentages or buying stages, and lets players verify their visual/performance build on the car while reviewing the bill.

#### 7. Vinyl Editing (`S10`) and Body Part Selection Empty State (`S16`)

- **Current Visible Problem**:
- In **Vinyl Editing (`S10`)**, layer selection (`LAYER stripe`), graphic cycling (`LOGO < >`), `VINYL COLOR`, layer ordering (`+ LAYER`, `DELETE`, `TO FRONT`, `TO BACK`), 8 transform buttons (`ROTATE -/+`, `WIDTH -/+`, `HEIGHT -/+`), and raw debug-style readout strings (`X 0.00 Y 0.00 ROT 0.0deg / WIDTH 1.00 HEIGHT 1.00`) are crammed into one narrow column while the car sits in a distant rear-3/4 view.

- In **Body Part Selection (`S16`)**, the starter Honda Civic EK shows a bare floating line `No compatible body or interior parts available` while the bottom category bars overlap the car.

- **Reference Principles & Match Limitations**:
- _ProStreet_ (`prostreet-0001`, `SAME TASK` in `S10`; `prostreet-0032`, `SAME TASK` in `S16`), _FM4_ (`fm4-0033`, `SAME TASK` in `S10`), and _MCLA_ (`mcla-0004`, `SAME TASK` in `S16`) separate layer stack management from decal transformation and frame the target body surface clearly.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Structured Vinyl Editor Panel (`S10`)**:
- Group the left panel into three distinct sub-cards: (1) **Layer Stack** (`Layer 1: stripe` with `+ Add`, `Delete` destructive, and `Front`/`Back` z-order buttons), (2) **Graphic & Color** (`Logo` selector + `Vinyl Color` swatch preview), and (3) **Transform Controls** (2-column stepper grid where values like `Pos X: 0.00`, `Pos Y: 0.00`, `Rot: 0.0°`, `Width: 1.00`, `Height: 1.00` are integrated directly between `-` and `+` buttons instead of printed as raw text at the bottom).

- **Informative Body Parts Empty State & Populated Selector (`S16`)**:
- When a car has no compatible body/interior parts, render a clean left-panel empty-state card explaining: `Stock Body Only — No aftermarket body or interior kits are available for the Honda Civic Type R (EK)` with quick-jump buttons to available visual categories (`PAINT`, `WHEELS`, `VINYLS`).

- Ensure that for cars among the 30-car roster that _do_ have compatible body parts, the selector uses the unobstructed left-panel list with part names, prices, and camera framing on the modified body zone.

- **Hypothesis to Validate**:
- _Vinyl Camera Framing (`S10`)_: Check whether the camera can automatically frame or toggle between target surfaces (Side / Top / Hood / Rear) when editing vinyls so the decal is large on screen.

- **Why It Helps**: Turns a cluttered, debug-like vinyl column into an organized creative tool and makes empty body-kit states feel intentional rather than broken.

#### 8. Rival / Pre-Race Stakes (`S06`) and Post-Race Results (`S26`)

- **Current Visible Problem**:
- In **Rival / Pre-Race Stakes (`S06`)**, the left rival list (`Leon Tyrrell`, `Bobby Sawyer`, `Keiko Miyama`) shows only names with no car model or performance context, and the right `DRIVER BET` panel presents `OFFER $1000`, `MAKE CASH OFFER`, and `PINK SLIP OFFER` above `START RACE` without clearly indicating the default no-bet state or the rival’s car at stake.

- In **Results / Reward (`S26`)**, the outcome (`RACE COMPLETE / POSITION 2 · TIME 01:58.31 / RACE REWARD +$0`) has flat typography, omits the 4-car finishing standings/times, gives no reason why the payout is `+$0` (non-career Quick Race), gives all 4 buttons (`CONTINUE`, `WATCH REPLAY`, `RESTART RACE`, `MAIN MENU`) identical weight, and suffers from **overlapping driver name labels** at the bottom of the 3D podium (`1. Keiko Miyama`, `2. Player`, `3. Bobby Sawyer` collide visually).

- **Reference Principles & Match Limitations**:
- In `S06`, _ProStreet_ (`prostreet-0053`, `ANALOGUE`) pairs each entrant with their vehicle and spec, and _Burnout 3_ (`burnout3-0018`, `PARTIAL`) makes car-reward stakes unmistakable.

- In `S26`, _FM4_ (`fm4-0056`, `SAME TASK`), _MC3_ (`mc3-0005`, `SAME TASK`), _ProStreet_ (`prostreet-0015`, `SAME TASK`), and _Burnout 3_ (`burnout3-0007`, `SAME TASK`) combine a hero placement readout (`1st` / `2nd`) with an itemized reward breakdown and a full entrant classification table.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Rival Dossier & Explicit Wager State (`S06`)**:
- Display each rival’s **Vehicle Model** beneath or beside their name in the `SELECT RIVAL` list and on a badge near the 3D rival preview.

- In the `DRIVER BET` card, display a prominent status line: `CURRENT WAGER: NONE ($0 — Optional)` when no bet is placed, or `ACTIVE WAGER: $1,000 CASH` / `PINK SLIP` when selected.

- Style `START RACE (NO BET)` (or `START RACE WITH BET` once an offer is accepted) as the unmistakable primary accent button at the bottom of the right panel.

- **Post-Race Results Hierarchy & Podium Label Fix (`S26`)**:
- **Fix Podium Label Overlap**: Remove the colliding floating 3D podium foot-labels or anchor them cleanly into non-overlapping horizontal columns (`min-gap: 24px`) above/below each podium step.

- **Hero Outcome & Classification Card**: Display finishing placement in hero typography (`2ND PLACE` or `1ST PLACE — VICTORY`), followed by a 4-row **Race Standings Table** (`Pos`, `Driver`, `Car`, `Time / Score`) and an **Itemized Reward Breakdown** (showing Base Purse, Wager Winnings/Losses, Career Promotion credit, or `Quick Race Exhibition — $0 Payout` when in Quick Race).

- **Action Hierarchy**: Make `CONTINUE` the primary accent button, `RESTART RACE` and `WATCH REPLAY` secondary buttons, and `MAIN MENU` a separated tertiary button.

- **Why It Helps**: Gives players informed context before risking money/cars against a rival, fixes visual text collisions on the podium, and makes post-race outcomes and payouts immediately understandable.

#### 9. Main Navigation (`S02`), Career Overview (`S03`), and Settings (`S11`)

- **Current Visible Problem**:
- **Main Navigation (`S02`)** and **Career Overview (`S03`)** render 5–6 equal-weight rectangular buttons (`CAREER`, `QUICK RACE`, `OPTIONS`, `CREDITS`, `SAVE & QUIT` in `S02`; `RACE EVENTS`, `PROGRESSION`, `GARAGE`, `DEALERSHIP`, `OPTIONS`, `MAIN MENU` in `S03`) with only a faint outline on the focused item and zero contextual summary. In `S03`, progression and next-event context are hidden one screen deeper.

- **Settings (`S11`)** dumps keyboard binds (left column), difficulty, audio volumes, graphics quality, speed units, and controller axes (middle column), and controller buttons + `Reset Binds` (right column, where controls clip/crowd at the bottom right) onto a single dense page of identical flat buttons.

- **Reference Principles & Match Limitations**:
- In `S02` and `S03`, _Driver: SF_ (`driver-0001`, `SAME TASK` in `S02`), _Burnout 3_ (`burnout3-0001` in `S02`, `burnout3-0022` in `S03`, `SAME TASK`), _ProStreet_ (`prostreet-0007` in `S02`, `prostreet-0021` in `S03`, `SAME TASK`), and _FM4_ (`fm4-0036` in `S02`, `fm4-0063` in `S03`, `SAME TASK`) use high-contrast active focus states, contextual descriptions for the highlighted mode, and visible career progress summaries.

- In `S11`, _Driver: SF_ (`driver-0029`, `SAME TASK`), _Burnout 3_ (`burnout3-0006`, `SAME TASK`), _GT5_ (`gt5-0074`, `SAME TASK`), and _FM4_ (`fm4-0054`, `PARTIAL`) group settings by task, render audio levels as visual bars, and provide an explanation for the focused option.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Main Navigation (`S02`)**: Apply high-contrast active styling (accent left bar + brighter surface + slight indent) to the focused button, separate primary play modes (`CAREER`, `QUICK RACE`) from system actions (`OPTIONS`, `CREDITS`, `SAVE & QUIT`) with a `16px` gap/divider, and display a 1–2 line contextual description below or beside the menu for the currently focused item.

- **Career Overview (`S03`)**: Add a **Career Status & Next Event Summary Card** (showing Current Tier `Tier 1 · Local`, Wins toward promotion, Active Garage Car `Honda Civic Type R (EK)`, and Next Available Event) so players see their career state immediately without clicking `PROGRESSION` first. Separate core career hubs (`RACE EVENTS`, `GARAGE`, `DEALERSHIP`, `PROGRESSION`) from utility routes (`OPTIONS`, `MAIN MENU`). _(Note: Do not build a geographic city map for Oversteer’s two-course scope)_.

- **Categorized Settings with Distinct Control Widgets (`S11`)**:
- Group `OPTIONS` into 4 clean tabs or clearly framed sections: **Driving & Gameplay** (`Difficulty`, `Speed Units`, `Graphics Quality`), **Audio** (`Music`, `Speech`, `Engine`, `SFX`), **Keyboard Binds**, and **Controller & Axes** (`Steering/Throttle/Brake Axes`, `Deadzone`, `Controller Buttons`, `Reset Defaults`), fixing all bottom-right clipping.

- Render percentage settings (`Music 50%`, `Deadzone 15%`) with visual horizontal fill bars, enum settings (`Difficulty: Normal`, `Quality: Balanced`, `Units: MPH`) with `< Value >` segmented indicators, and key/button bindings with distinct `[KEY]` pill badges.

- Add a persistent bottom description bar explaining the currently focused setting.

- **Why It Helps**: Stops every menu from looking like the same flat button list, surfaces career goals at a glance, and makes settings effortless to scan and adjust.

---

### Priority 3 (P3): Composition, Identity & Long-Form Polish

#### 10. First Impression / Title Screen (`S01`) and Credits (`S12`)

- **Current Visible Problem**:
- **First Impression / Start (`S01`)**: Uses a small `OVERSTEER / Find your line.` header and two stacked buttons (`START DRIVING`, `QUICK RACE`) on the left while the car sits small and distant in a largely empty gray workshop—looking almost identical to the Main Menu (`S02`) rather than a deliberate title screen.

- **Credits / Long-Form Information (`S12`)**: Uses a calm, legible left-aligned text block with a `BACK` button (which works well), but lacks typographic section headings to separate project identity, engine credits, and asset provenance.

- **Reference Principles & Match Limitations**:
- In `S01`, _FM4_ (`fm4-title`, `SAME TASK`), _MC3_ (`mc3-title`, `SAME TASK`), _ProStreet_ (`prostreet-0006`, `SAME TASK`), and _Burnout 3_ (`burnout3-0023`, `SAME TASK`) establish strong title scale, dramatic hero car framing, and a single dominant entry action.

- In `S12`, _Driver: SF_ (`driver-0044`, `SAME TASK`) uses clear role/category headings to structure attribution.

- **Desired Appearance & Behavior (Firm Decisions)**:
- **Hero Title Composition (`S01`)**: Scale up the `OVERSTEER` wordmark (`48px–56px` bold tracked uppercase) and tagline (`Find your line.`), bring the 3D workshop camera closer to the hero car with a stronger low-angle three-quarter composition, and make `START DRIVING` the dominant primary accent CTA (with `QUICK RACE` clearly subordinate below it).

- **Structured Credits Typography (`S12`)**: Preserve the calm left-aligned layout and clear `BACK` route, adding uppercase accent subheaders (`PROJECT`, `ENGINE & ARCHITECTURE`, `ASSET PROVENANCE & DOCUMENTATION`) and comfortable paragraph spacing (`16px–24px`).

- **Why It Helps**: Gives Oversteer a memorable, car-forward first impression and clean typographic rhythm on long-form text.

---

## 4. Observable Acceptance Criteria & Representative Verification States

After implementing the improvements above, launch the compiled game, capture native `1920x1080` screenshots across the representative states below, and verify that **every check passes** before concluding the task:

1. **Zero Vehicle Occlusion in Customization (`S09`, `S10`, `S14`, `S15`, `S16`, `S17`, `S18`, `S19`)**:

- In every customization state—especially **Paint Finish (`S09`)**, **Wheel Customization (`S14`)**, **Paint Color Picker (`S18`)**, **Paint Material / Pearlescent Slider (`S19`)**, and **Modification Cart Review (`S17`)**—the 3D vehicle body and wheels are 100% unobstructed by UI panels, and `S14` uses a side-profile wheel-focused camera with visual rim icons.

1. **Clear Action & Consequence Hierarchy (`S01`–`S08`, `S13`, `S17`, `S20`, `S21`, `S26`)**:

- Every screen has **one** unmistakable primary action button styled with the primary accent fill (`START DRIVING`, `START RACE`, `BUY CAR`, `PURCHASE`, `RESUME`, `CONTINUE`), while destructive actions (`SELL CAR`, `DELETE`, `DISCARD ALL`, `STAKE MY CAR`, and `RESTART`/`QUIT` with an active wager) are visually separated and styled with warning/destructive tokens.

- **Confirm Vehicle Purchase (`S20`)** displays `Current Cash`, `Vehicle Price`, and `Remaining Cash` with action-specific button copy.

- **Confirm Ownership Risk (`S21`)** explicitly states that losing the race permanently forfeits the named vehicle and names the rival car to be won.

1. **Structured Specs, Track Previews & Mode-Accurate Copy (`S03`–`S08`, `S15`, `S22`, `S26`)**:

- **Career Overview (`S03`)** shows a visible career progress and next-event summary card.

- **Quick Race (`S04`)** and **Career Event Selection (`S05`)** display a 2D course outline, structured key-value event specs, inline list badges, and mode-accurate payout copy (Quick Race no longer claims career payouts or pink-slip grid bets).

- **Garage (`S07`)** and **Dealership (`S08`)** display comparative vehicle performance bars, and Dealership list rows show inline prices and tiers.

- **Performance Tuning (`S15`)** separates Stage Upgrades (with stage pips and prices) from Setup Tuning sliders (with explicit bilateral endpoint labels and a trade-off description).

- **Loading (`S22`)** displays the upcoming event briefing card and removes the out-of-scope "Speed Challenge" tip.

- **Results (`S26`)** fixes the overlapping podium driver labels, shows a 4-driver standings table, and explains `+$0` payouts in Quick Race.

1. **High-Contrast, Mode-Aware Race & Drift HUD (`S23`, `S24`, `S25`)**:

- **Open Road (`S23`)** and **Nearby Opponents (`S24`)** replace the four heavy dark boxes with lightweight telemetry clusters, dominant Speed/Gear/Position numerals, a high-contrast minimap route line, and unobstructed lower-left peripheral visibility.

- **Drift HUD (`S25`)** prioritizes Live Drift Score, Target Score (`898 / 1,000`), and a target progress bar instead of circuit race position.

1. **No Layout Overflow or Text Clipping (`S11`, `S26`, All States)**:

- **Settings (`S11`)** is cleanly grouped by category with visual volume bars and keycap badges, with zero bottom-right clipping. All currency values across the game use consistent formatting (`$25,000`).

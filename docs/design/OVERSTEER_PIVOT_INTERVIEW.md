# Oversteer independent-game pivot interview

Started November 3, 2026. This interview supersedes the reconstruction direction
where it conflicts with [ADR-0008](../adr/0008-develop-oversteer-as-an-independent-game.md).
The user confirmed the consolidated scope and explicitly authorized implementing
this entire plan. The interview is complete; implementation and verification
are active. No further implementation approval is required.

## Requested outcome

Refine the existing game into an independent racing game with a finished look
and feel across menus, cars, tracks, career progression and driving physics.
Remove Juiced 2 branding. Keep its screenshots and resources as examples of a
mature racing game rather than specifications to copy. Fix visual glitches,
physics problems and other bugs against Oversteer's own quality criteria.

## Round 1: answered

| Decision | Accepted answer |
| --- | --- |
| Asset reuse | Retain usable existing imported assets for this refinement milestone. Replace Juiced-branded presentation and identity-bearing content; preserve development provenance. This is not a commitment to replace every source-derived environment or sound. |
| Scope and sequencing | First polish an end-to-end career slice: start, buy/customize a car, race, receive rewards, unlock another event, save and resume. Validate representative cars and tracks, then extend that quality standard across retained content. Content that cannot meet the standard may be deferred; all 463 existing contests are not automatically required. |
| Handling | Accessible arcade driving with believable weight, predictable grip, controllable drifting, distinct cars, understandable mistakes and sensible collision recovery. Change or replace recovered equations where playtesting demonstrates poor behavior. |
| Presentation | Retain the urban tuner-racing atmosphere, with restrained menus, readable typography, coherent lighting and strong car presentation. The user finds Juiced's menus and presentation too loud; visual resemblance is not the target. |
| Career | Simplify around racing, earning, improving or buying cars, and unlocking tougher competition. Remove inherited mechanics that obstruct this loop, except that betting and pink slips must remain. |
| Characters | Remove character customization. The user finds the current player models creepy and the feature too complicated. Find a basic premade character model to use; more characters can be added later. This does not remove car customization. |

## Round 2: answered

The user accepted Q6–Q10 and clarified that there are no existing player saves:
the game is still in development.

| Decision | Accepted answer |
| --- | --- |
| First polished milestone | Three existing cars representing FWD, RWD and AWD; two existing tracks; circuit and drift events; betting, pink slips, garage upgrades and saved progression. Finish all screens and transitions on this path before extending the standard across retained content. This is a milestone, not a permanent three-car/two-track limit. |
| Wager consequences | Cash bets remain against a chosen rival. Losses are permanent; protect the last owned car and provide a way to earn money without staking anything. Show stakes before entry. Voluntary abandonment or restart forfeits the stake; application crashes must not create an additional penalty. |
| Career structure | Clear tiers with visible unlock requirements. Defer crew management, DNA/spooking and separate sponsor progression. Ordinary opponent AI remains. Events explain eligibility, rewards and progression effects. |
| Character presence | One fixed neutral premade driver model, a driver-name field, and car-focused menus. Remove the editor and mandatory character-creation onboarding. Use the driver where a person is needed, without elaborate character showcases or facial animation. |
| Saves | Start the redesigned career cleanly. There are no existing player saves to migrate; do not add a legacy-save migration workstream. Saving and resuming newly created careers remain required. |

## Consolidated scope

Keep the existing Rust/Godot foundation, native Apple Silicon target, offline
single-player delivery, chase-camera driving, keyboard/controller support and
the established 1920×1080 at 60 FPS target on the current M5 Pro. The pivot
changes product identity and acceptance, not the engine or platform.

Use Oversteer branding and a restrained urban tuner presentation. Existing
reference screenshots support judgments about finish, readability and coherence;
matching their composition, typography, lighting or rules is not a requirement.
Preserve asset provenance and historical recovery evidence in development docs.

Build the accepted career slice, including betting and pink slips, before
extending the quality standard across retained cars, courses and events. Car
customization remains; character customization does not. Retain the accepted
30-car roster as the wider foundation, without treating all imported courses
or historical contests as mandatory release content.

The exact representative cars, tracks and premade character are implementation
selections to validate against the accepted direction. Numeric handling,
economy and AI tuning should follow current-game measurement and playtesting;
they are not requirements to reproduce Juiced.

## Implementation and verification sequence

During implementation the user explicitly requested substantially more
screenshots so the agent remains aware of what is on screen. Capture and inspect
settled frames after UI actions, multiple vehicle angles and driving sequences
covering acceleration, corners, drifting, contact and recovery. Retain failed
captures as well as passing ones. Regular visual-scenario captures must not
contaminate timed performance measurements.

**November 4 clarification:** the user rejected exhaustive screenshot volume.
The absolute ceiling is **50 screenshots per entire run**, including incidental
captures. Use essential situations and angles: the standard static inspection is
14 views per representative car (42 total), covering four track quarters, all
eight isolated azimuths, top/underside and tilted grazing/backlit views. Keep physics/event logging
without multiplying PNGs. Do not divide an exhaustive matrix into repeated runs
to circumvent this ceiling. The detailed current standard is in
[the inspection guide](../../tools/game/inspection/README.md).

The user subsequently reported disruptive game-window launches. Automated runs
must not steal desktop focus. The latest clarification permits visible windows
provided they leave the active app alone and retain screenshots. Preserve real
rendering, simulation and exercised input behavior; dummy-renderer headless runs
do not establish visual quality.

The user rejected the cartoon Kenney character during implementation. The fixed
driver must have realistic adult proportions and a look comparable to stock
Juiced 2 characters or similar racing games. This changes the character art
selection, not the decision to remove customization or the independent identity.

1. Establish the current runnable baseline and align active requirements with
   this scope. Record representative menus, races, physics failures and career
   transitions; distinguish reproducible defects from fidelity-only differences.
   Preserve unrelated work in progress.
2. Remove Juiced branding and character customization, introduce the fixed driver
   and refine the interface. Inspect native screens and input navigation for
   clipped text, occluded cars, broken materials, unreadable HUD and missing
   assets. Verify the new-career flow bypasses character creation.
3. Refine driving and race behavior across FWD, RWD and AWD cars on both selected
   tracks. Reproduce bugs before fixing them, add focused regression coverage
   where appropriate, and validate steering, braking, drifting, collisions,
   recovery and opponent behavior in the rendered game.
4. Finish the tiered career slice and wagers. Verify earning/spending,
   eligibility, unlocks, cash and pink-slip wins/losses, last-car protection,
   voluntary forfeiture, crash recovery and the no-stake earnings path.
   Save, quit and relaunch to verify newly earned progress.
5. Review the complete slice and measure the existing 1080p/60 FPS target on
   the current build. Require no known unresolved player-visible defects on
   the exercised paths; retain captures, test results and any remaining limits.
   Automated checks alone do not establish visual quality or driving feel.
6. Extend the standard across retained content, validating each addition.
   Explicitly report deferred content and unresolved defects; completing the
   first slice does not finish the entire refinement effort.

## Interview status

Both decision rounds and the consolidated scope are accepted. The user explicitly
instructed: "yes, implement the entire plan" in this document. Track actual
implementation and verification in the [implementation log](../game/PIVOT_STATUS.md);
acceptance of the plan is not evidence of completion.

## Evidence boundary

Repository discovery found a documented 30-car, 33-course foundation with 403
career and 60 sponsor contests. These inventory counts do not establish current
playability or quality. Existing visual and career checks remain incomplete;
reference-fidelity failures must be distinguished from player-visible defects
under the new direction. No new runtime validation has been performed during
this interview.

Focused source inspection found that pink-slip offers, acceptance and race entry
require at least two owned cars; settlement also protects the last car. Cash
bets are against a selected rival, with the stake escrowed before the race and
settled independently of overall race victory. These are current behaviors,
not new product decisions.

The character editor is a separate new-career flow, but player profiles also
supply driver names and characters appear on podiums. Removing the editor need
not remove names or all character appearances. Existing persistence code has
schema-1 validation, some targeted migration and backup recovery. The user
confirmed there are no player saves needing compatibility with the redesigned
career; retained test fixtures are development evidence, not a migration need.

## Premade character candidates

Creator-page research found these candidates; none has been imported or
visually accepted in Oversteer:

- [BELAZ race driver](https://sketchfab.com/3d-models/race-driver-e4e97df9865d466c8359fbb23e757308):
  free downloadable FBX, approximately 18,000 triangles, tagged as rigged,
  CC BY 4.0 with attribution required. Animation clips and appearance remain
  unverified. A focused candidate for the basic driver role.
- [Quaternius Ultimate Animated Character Pack](https://quaternius.com/packs/ultimatedanimatedcharacter.html):
  52 animated characters, FBX/OBJ/Blend, free under CC0. A fallback for selecting
  one fixed clothed character; specific model, animation and visual fit need
  inspection.
- [Kenney Animated Characters 3](https://kenney-assets.itch.io/animated-characters-3):
  rigged humans with idle, running and jump pose, free/name-your-price under
  CC0. File formats and Godot import suitability remain unverified.

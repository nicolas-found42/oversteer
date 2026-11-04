# Burnout 3: Takedown and Need for Speed: ProStreet UI evidence

Research captured 2026-11-04. **Coverage remains incomplete. This is a page-indexed evidence library, not an exhaustive retail UI inventory.** Each accepted entry below was extracted at source resolution and its pixels inspected individually. Repeated cars, colors, and selection highlights are not counted as new pages. Tutorial/award/HUD states are retained as separate reference categories, so frame counts must not be described as menu counts.

## Provenance and method

Primary evidence is recorded game output, not the uploader’s description of it. Search results and contact sheets only located candidate timestamps. Curated PNGs are separate from `sample-*` JPEGs and `*-sheet.jpg` discovery artifacts. Each JSON manifest records exact source timestamp, URL, local path, dimensions and SHA-256 hash. PNG extraction uses ffmpeg seek without scaling. These are source-video pixels, not native console framebuffer dumps.

Burnout evidence is the **PS2 retail UI**, including an explicitly named PCSX2 capture. PS2 memory-card wording and PlayStation button prompts independently identify the interface. No Xbox recompilation, development menu, prototype or beta-menu material was accepted. The video [Main Menu Video](https://www.youtube.com/watch?v=P9-JK4FAbB0) is the moving background alone and was excluded as menu evidence.

ProStreet evidence distinguishes **Windows/PC** keyboard prompts from **Xbox 360** controller prompts; neither proves PS2/Wii parity. English PC customization footage visibly uses enormous cash balances: it is useful for stock-looking page layouts, but authenticity of save state, game patch and modifications is **medium confidence**, not certified unmodified retail. The Italian tuning tutorial supplies a separately labeled PC localization. No Pepega, Extra Options or Remastered-mod source was accepted.

## Transcript-led inspection

The [GameRiot Xbox 360 walkthrough](https://www.youtube.com/watch?v=CVYeg1Fu3UA) includes English automatic captions retained as `videos/CVYeg1Fu3UA.en.vtt`. Caption clues around 02:18 discuss extended career/race-day events; 08:18–09:00 discuss race-day progression; 10:43 mentions repairs. Frames were inspected around the actual transition/onboarding sequence instead of treating those words as proof of a visible menu. This yielded the Battle Machine welcome dialog (10:00), challenge explanations (10:30 and 11:00), and race-day menu (11:30). The repair mention is **not** evidence of a captured repair dialog; the captured repair page is a PC loading tip at 05:30 in a different source.

## Accepted frame index

### Burnout 3: Takedown

33 inspected accepted frames; includes help/award/HUD states. [Machine-readable manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/manifest.json).

| Page/state | Source timestamp | Platform/edition | Local full-resolution frame |
|---|---|---|---|
| driver-save-dialog | [02:10.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=130s) | retail UI, platform PS2 | [driver-save-dialog.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/driver-save-dialog.png) |
| main-menu | [02:30.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=150s) | retail UI, platform PS2 | [main-menu.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/main-menu.png) |
| car-select | [03:10.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=190s) | retail UI, platform PS2 | [car-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/car-select.png) |
| race-training | [03:50.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=230s) | retail UI, platform PS2 | [race-training.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/race-training.png) |
| loading-tip | [05:50.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=350s) | retail UI, platform PS2 | [loading-tip.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/loading-tip.png) |
| race-hud | [06:10.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=370s) | retail UI, platform PS2 | [race-hud.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/race-hud.png) |
| audio-settings | [06:30.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=390s) | retail UI, platform PS2 | [audio-settings.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/audio-settings.png) |
| race-results | [12:15.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=735s) | retail UI, platform PS2 | [race-results.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/race-results.png) |
| burnout-points | [12:45.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=765s) | retail UI, platform PS2 | [burnout-points.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/burnout-points.png) |
| signature-takedowns | [13:15.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=795s) | retail UI, platform PS2 | [signature-takedowns.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/signature-takedowns.png) |
| crash-junction-select | [13:45.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=825s) | retail UI, platform PS2 | [crash-junction-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/crash-junction-select.png) |
| crash-training | [14:15.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=855s) | retail UI, platform PS2 | [crash-training.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/crash-training.png) |
| crash-results | [19:15.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=1155s) | retail UI, platform PS2 | [crash-results.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/crash-results.png) |
| award-unlock | [25:45.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=1545s) | retail UI, platform PS2 | [award-unlock.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/award-unlock.png) |
| world-location-select | [07:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=420s) | retail UI, platform PS2 | [world-location-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/world-location-select.png) |
| world-event-select | [14:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=840s) | retail UI, platform PS2 | [world-event-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/world-event-select.png) |
| takedown-achieved | [20:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=1200s) | retail UI, platform PS2 | [takedown-achieved.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/takedown-achieved.png) |
| new-special-event | [25:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=1500s) | retail UI, platform PS2 | [new-special-event.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/new-special-event.png) |
| face-off-introduction | [28:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=1680s) | retail UI, platform PS2 | [face-off-result.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/face-off-result.png) |
| autosave-success | [35:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=2100s) | retail UI, platform PS2 | [autosave-success.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/autosave-success.png) |
| series-unlocked | [55:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=3300s) | retail UI, platform PS2 | [series-unlocked.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/series-unlocked.png) |
| takedown-breakdown | [56:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=3360s) | retail UI, platform PS2 | [takedown-breakdown.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/takedown-breakdown.png) |
| world-region-select | [57:00.0](https://www.youtube.com/watch?v=mtovt4l8-hk&t=3420s) | retail UI, platform PS2 | [world-region-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/world-region-select.png) |
| press-start | [01:58.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=118s) | retail PS2 UI | [press-start.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/press-start.png) |
| profile-required | [02:02.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=122s) | retail PS2 UI | [profile-required.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/profile-required.png) |
| profile-name-keyboard | [02:04.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=124s) | retail PS2 UI | [profile-name-keyboard.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/profile-name-keyboard.png) |
| save-profile-confirm | [02:06.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=126s) | retail PS2 UI | [save-profile-confirm.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/save-profile-confirm.png) |
| profile-slot | [02:08.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=128s) | retail PS2 UI | [profile-slot.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/profile-slot.png) |
| profile-save-success | [02:20.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=140s) | retail PS2 UI | [profile-save-success.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/profile-save-success.png) |
| single-event-mode | [02:34.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=154s) | retail PS2 UI | [single-event-mode.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/single-event-mode.png) |
| race-options | [02:40.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=160s) | retail PS2 UI | [race-options.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/race-options.png) |
| crash-score-complete | [19:42.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=1182s) | retail PS2 UI | [crash-score-complete.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/crash-score-complete.png) |
| road-rage-options | [19:48.0](https://www.youtube.com/watch?v=_r5r0nE1sA4&t=1188s) | retail PS2 UI | [road-rage-options.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/road-rage-options.png) |

Sources:

- [Burnout 3 : Takedown -- Gameplay (PS2)](https://www.youtube.com/watch?v=_r5r0nE1sA4)
- [Burnout 3: Takedown (PCSX2) Gameplay 100% Walkthrough Part 1](https://www.youtube.com/watch?v=mtovt4l8-hk)

### Need for Speed: ProStreet

58 inspected accepted frames; includes help/award/HUD states. [Machine-readable manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/manifest.json).

| Page/state | Source timestamp | Platform/edition | Local full-resolution frame |
|---|---|---|---|
| career | [00:07.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=7.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [career.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/career.png) |
| layer-menu | [00:52.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=52.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [layer-menu.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/layer-menu.png) |
| transform-decal | [01:07.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=67.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [transform-decal.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/transform-decal.png) |
| customization | [01:22.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=82.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [customization.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/customization.png) |
| garage-blueprint | [02:07.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=127.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [garage-blueprint.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/garage-blueprint.png) |
| wind-tunnel | [03:52.5](https://www.youtube.com/watch?v=jGpXtsxdogE&t=232.5s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [wind-tunnel.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/wind-tunnel.png) |
| title-screen | [01:30.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=90s) | retail Xbox 360 UI | [title-screen.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/title-screen.png) |
| main-menu | [02:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=120s) | retail Xbox 360 UI | [main-menu.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/main-menu.png) |
| controller-loading | [06:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=360s) | retail Xbox 360 UI | [controller-loading.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/controller-loading.png) |
| challenge-welcome-dialog | [10:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=600s) | retail Xbox 360 UI | [challenge-welcome-dialog.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/challenge-welcome-dialog.png) |
| challenge-overview | [10:30.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=630s) | retail Xbox 360 UI | [challenge-overview.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/challenge-overview.png) |
| race-to-dominate | [11:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=660s) | retail Xbox 360 UI | [race-to-dominate.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/race-to-dominate.png) |
| race-day-menu | [11:30.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=690s) | retail Xbox 360 UI | [race-day-menu.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/race-day-menu.png) |
| grip-overview | [12:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=720s) | retail Xbox 360 UI | [grip-overview.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/grip-overview.png) |
| damage-help | [12:33.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=753s) | retail Xbox 360 UI | [damage-help.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/damage-help.png) |
| race-results | [19:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1140s) | retail Xbox 360 UI | [race-results.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/race-results.png) |
| drag-overview | [19:33.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1173s) | retail Xbox 360 UI | [drag-overview.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-overview.png) |
| drag-staging | [20:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1200s) | retail Xbox 360 UI | [drag-staging.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-staging.png) |
| drag-shifting | [20:20.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1220s) | retail Xbox 360 UI | [drag-shifting.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-shifting.png) |
| drag-results | [23:30.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1410s) | retail Xbox 360 UI | [drag-results.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-results.png) |
| reward-car-select | [24:00.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1440s) | retail Xbox 360 UI | [reward-car-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/reward-car-select.png) |
| career-map | [24:30.0](https://www.youtube.com/watch?v=CVYeg1Fu3UA&t=1470s) | retail Xbox 360 UI | [career-map.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/career-map.png) |
| repair-loading-tip | [05:30.0](https://www.youtube.com/watch?v=3di51RWowF8&t=330s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [repair-loading-tip.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/repair-loading-tip.png) |
| race-event-select | [11:00.0](https://www.youtube.com/watch?v=3di51RWowF8&t=660s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [race-event-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/race-event-select.png) |
| grip-driving-aids | [12:00.0](https://www.youtube.com/watch?v=3di51RWowF8&t=720s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [grip-driving-aids.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/grip-driving-aids.png) |
| grip-heads-up-tip | [12:30.0](https://www.youtube.com/watch?v=3di51RWowF8&t=750s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [grip-heads-up-tip.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/grip-heads-up-tip.png) |
| target-time | [15:30.0](https://www.youtube.com/watch?v=3di51RWowF8&t=930s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [target-time.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/target-time.png) |
| drag-staging-hud | [20:30.0](https://www.youtube.com/watch?v=3di51RWowF8&t=1230s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [drag-staging-hud.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-staging-hud.png) |
| drag-round-results | [21:00.0](https://www.youtube.com/watch?v=3di51RWowF8&t=1260s) | retail PC UI; garage source has modified save/cash, UI authenticity medium | [drag-round-results.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/drag-round-results.png) |
| tires-shop | [00:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=30s) | retail PC UI; English | [tires-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/tires-shop.png) |
| autosculpt-front-wheels | [00:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=45s) | retail PC UI; English | [autosculpt-front-wheels.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-front-wheels.png) |
| autosculpt-rear-wheels | [01:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=90s) | retail PC UI; English | [autosculpt-rear-wheels.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-rear-wheels.png) |
| body-kit-shop | [01:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=105s) | retail PC UI; English | [body-kit-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/body-kit-shop.png) |
| autosculpt-front-bumper | [02:00.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=120s) | retail PC UI; English | [autosculpt-front-bumper.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-front-bumper.png) |
| autosculpt-skirt | [02:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=135s) | retail PC UI; English | [autosculpt-skirt.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-skirt.png) |
| hood-shop | [02:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=150s) | retail PC UI; English | [hood-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/hood-shop.png) |
| autosculpt-hood | [02:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=165s) | retail PC UI; English | [autosculpt-hood.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-hood.png) |
| spoiler-shop | [03:00.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=180s) | retail PC UI; English | [spoiler-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/spoiler-shop.png) |
| autosculpt-spoiler | [03:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=195s) | retail PC UI; English | [autosculpt-spoiler.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-spoiler.png) |
| autosculpt-roof-scoop | [03:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=225s) | retail PC UI; English | [autosculpt-roof-scoop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/autosculpt-roof-scoop.png) |
| roll-cage-shop | [04:00.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=240s) | retail PC UI; English | [roll-cage-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/roll-cage-shop.png) |
| racing-seats-shop | [04:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=255s) | retail PC UI; English | [racing-seats-shop.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/racing-seats-shop.png) |
| wheel-paint | [04:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=270s) | retail PC UI; English | [wheel-paint.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/wheel-paint.png) |
| window-tint | [04:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=285s) | retail PC UI; English | [window-tint.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/window-tint.png) |
| body-paint | [05:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=315s) | retail PC UI; English | [body-paint.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/body-paint.png) |
| vinyl-category | [05:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=330s) | retail PC UI; English | [vinyl-category.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/vinyl-category.png) |
| vinyl-select | [05:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=345s) | retail PC UI; English | [vinyl-select.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/vinyl-select.png) |
| tune-suspension | [06:00.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=360s) | retail PC UI; English | [tune-suspension.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/tune-suspension.png) |
| tune-engine | [06:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=375s) | retail PC UI; English | [tune-engine.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/tune-engine.png) |
| tune-drivetrain | [06:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=390s) | retail PC UI; English | [tune-drivetrain.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/tune-drivetrain.png) |
| tune-brakes | [06:45.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=405s) | retail PC UI; English | [tune-brakes.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/tune-brakes.png) |
| dyno-specifications | [07:00.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=420s) | retail PC UI; English | [dyno-specifications.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/dyno-specifications.png) |
| update-blueprint-dialog | [08:15.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=495s) | retail PC UI; English | [update-blueprint-dialog.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/update-blueprint-dialog.png) |
| race-matchup | [08:30.0](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=510s) | retail PC UI; English | [race-matchup.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/race-matchup.png) |
| car-lot | [01:30.0](https://www.youtube.com/watch?v=tPwZswGZ7_0&t=90s) | retail PC UI; Italian localization | [car-lot.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/car-lot.png) |
| engine-upgrade | [03:15.0](https://www.youtube.com/watch?v=tPwZswGZ7_0&t=195s) | retail PC UI; Italian localization | [engine-upgrade.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/engine-upgrade.png) |
| forced-induction-upgrade | [03:30.0](https://www.youtube.com/watch?v=tPwZswGZ7_0&t=210s) | retail PC UI; Italian localization | [forced-induction-upgrade.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/forced-induction-upgrade.png) |
| brakes-upgrade | [03:45.0](https://www.youtube.com/watch?v=tPwZswGZ7_0&t=225s) | retail PC UI; Italian localization | [brakes-upgrade.png](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/brakes-upgrade.png) |

Sources:

- [NFSPS: My Garage](https://www.youtube.com/watch?v=jGpXtsxdogE)
- [Need for Speed Prostreet Gameplay Walkthrough Part 1 - GOING LEGIT](https://www.youtube.com/watch?v=CVYeg1Fu3UA)
- [Need for Speed: ProStreet (PC) | Walkthrough Part #1 - The Introduction [HD 60FPS]](https://www.youtube.com/watch?v=3di51RWowF8)
- [Mitsubishi Lancer Evo IX Grip - Customization & Race - NFS ProStreet](https://www.youtube.com/watch?v=0n-0RQOu-EQ)
- [NFS ProStreet: Tuning For Beginners](https://www.youtube.com/watch?v=tPwZswGZ7_0)

## Coverage inventory and known missing pages

This checklist combines visible parent-menu entries with the publisher’s [Burnout 3 Xbox manual](https://oldgamesdownload.com/manual/burnout-3-takedown-xbox-manual-english/) as a structural lead. The manual establishes that Driver Details contains progress/records/rewards/profile/settings/training/extras; its Xbox-specific online flow is not proof of PS2 page appearance. Missing pages below are explicit acquisition work, not inferred screenshots.

| Branch | Captured | Still missing/unverified |
|---|---|---|
| Burnout startup/profile | Press Start; profile-required choice; keyboard; save choice; slot choice; saving/success | Existing-profile load, overwrite/delete, missing/full memory-card and failure dialogs |
| Burnout World Tour | Region, location, event, car select; results; point/takedown breakdowns; award overlays | Detailed event description variants, championship standings/continuation, failure and retry dialogs |
| Burnout Single Event | Mode selection, race options, road-rage options, car select, crash junction choice, crash results | Time Attack options; full named junction selector; pause root; restart/quit confirmation; multiplayer setup |
| Burnout Driver Details | Profile creation; in-race audio sliders | Driver Details root; Progress; Rewards garage/photo album/trophies/signature lists; Records track browser; Profile management; Settings root/gameplay/video/controller/EA Trax; Training selection; Extras selection |
| Burnout online/multiplayer | None | Lobby select, server/game lobby, create/join, player profile, friends, invitation/error dialogs, local Race/Road Rage/Team Crush/Double Impact/Party Crash setup and results |
| ProStreet startup/career | Title; main menu; Career Cars branch; career map; reward car selector | Alias creation/load/save, career overview, personal records, marker management, code entry; map leaderboard; new-career/quit confirmation |
| ProStreet Race Day | Race-day root and event selector; matchup; results; drag rounds and scoring | Progress/standings, car assignment per mode, repair menu/dialogs, leave/exit/save dialogs, pause root and confirmations |
| ProStreet garage/customization | Garage blueprints; customization root; layer/transform; part shops; Autosculpt pages; paint/tint; vinyl; four tuning tabs; wind tunnel; dyno specifications; blueprint overwrite dialog | Garage action menu, change-mode, sell/create blueprint and confirmations; full Custom Upgrade category tree, quick-upgrade purchase page; rear bumper/exhaust/wheel shop; decal category/color/transform variants; scroll extents of tuning suspension/engine/drivetrain; actual dyno graph |
| ProStreet options/network | Main menu entries visible | Options root and every gameplay/audio/video/controller page; race-day creation/customization; Share, leaderboards, online/session dialogs |
| ProStreet later race modes | Grip/time attack/drag intro/UI | Drift, speed challenge and wheelie competition tutorials/HUD/results, king/super-promotion/race-day win/dominate pages, failure/totaled/disqualification dialogs |
| Platform variants | Burnout PS2; ProStreet PC and Xbox360 | Burnout original Xbox comparison; ProStreet PS3 and separate PS2/Wii interface inventory |

## Visual observations grounded in these frames

- Burnout places mode and step headings across the top of a single rounded trapezoid-like panel, uses a restrained blue grid, reserves yellow/orange for scores/awards, and gives every page a stable footer of labeled controller actions. World Tour moves from globe to regional map to local event map; each level changes information density while preserving the control vocabulary. See the captured [region](https://www.youtube.com/watch?v=mtovt4l8-hk&t=3420s), [location](https://www.youtube.com/watch?v=mtovt4l8-hk&t=420s), and [event](https://www.youtube.com/watch?v=mtovt4l8-hk&t=840s) pages.
- ProStreet uses the same black header, pale gray rows, fluorescent yellow selection and rectangular footer controls across car browsing, shops, tuning and confirmation dialogs. Car preview remains prominent while the left/top panel changes task. The [tuning](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=360s) page exposes category tabs, named sliders, explicit endpoints and a details action; the [blueprint confirmation](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=495s) dims context and uses a compact centered choice.

## Acquisition gaps and rejected evidence

Raw searches are retained in each game directory (`search*.jsonl`). Burnout exact Driver Details/options searches were heavily contaminated by beta/development and 2026 recompilation uploads; those were rejected. ProStreet options searches primarily returned Extra Options and mod-remaster videos; those were rejected. Generic full walkthroughs emphasize racing and do not prove coverage of settings or rare dialogs. Additional targeted footage or direct retail-game capture is required before claiming every page.

Rejected/duplicate candidates remain explicitly marked in manifests: ProStreet quick-upgrade is another selection on the customization root; dyno-chart-entry is not a dyno graph; incomplete Burnout crash score animation is superseded by crash-score-complete. A larger frame count is not a substitute for closing the inventory above.

## Expanded screenshot library — 1,000 per game

The later target is **1,000 useful screenshots per game**, including changing gameplay HUD, score/award overlays, garage states and transitions, rather than 1,000 distinct pages. The original page manifests above remain unchanged. The expanded libraries include those original useful captures and add source-resolution JPEGs:

- [Burnout 3 expanded manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/burnout3/expanded-manifest.json)
- [ProStreet expanded manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/prostreet/expanded-manifest.json)

Each normalized record contains `game`, `page`, `category`, `path`, `timestamp_seconds`, `source_url`, `source_title`, `edition`, `verification`, and `sha256`. Categories describe the selected source sequence; a sequence can include pause, result or loading transitions. They are not a frame-by-frame semantic annotation. `timestamp_seconds` is the exact ffmpeg seek target, within one source frame of the decoded image; source links point to that time. Bulk JPGs are not resized.

Burnout uses three recordings of the PS2 interface. ProStreet uses six recordings covering English PC, Xbox 360, an Italian PC tuning tutorial and a clean-looking English PC drift-king run. Source title/platform and visible controls establish the interface, but third-party uploads do not prove an untouched executable. Modified save/cash balances are explicitly flagged. The ultrawide speed-king source was downloaded for inspection and excluded from the accepted library because its interface aspect modification conflicts with using stock UI evidence.

QA distinguishes individually inspected original PNG pages from bulk captures. Bulk selection used previously pixel-inspected UI/HUD time ranges, global 128-bit difference-hash filtering (distance ≤6 rejected), blank filtering, nine representative 40-frame contact sheets per game, plus a Tesseract flagging pass over every initial 1,000-frame set. All 117 initial low-text flags were manually checked; five new refill flags were also checked, including full-resolution inspection. Cinematic-only views, blank/empty transitions and non-game color bars found in QA were excluded and replaced. This is **sampled visual QA with automated flagging**, not a claim that every bulk frame was individually inspected at full resolution. Low text was only a review flag: valid HUD frames were retained after inspection.

The original missing-menu inventory remains valid. Reaching 1,000 attributed screenshots does not establish exhaustive coverage of settings, network flows or rare dialogs.

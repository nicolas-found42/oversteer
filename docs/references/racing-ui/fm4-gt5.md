# Forza Motorsport 4 and Gran Turismo 5 UI evidence

Research date: 2026-11-04. This is an evidence inventory, not an exhaustive claim. Distinct page templates, dialogs, and materially different HUD states are captured; individual car choices, highlighted icons, camera rotations, and repeated race tracks are not separate menu pages. All media stays outside the repository.

## Method and confidence

Used original game recordings, timestamped automatic commentary transcripts where supplied by YouTube, and pixel inspection of contact sheets at the selected timestamps. Frames are extracted at the downloaded source resolution (not upscaled). A video title alone is insufficient: menu branding and content were checked. Exact game patch, region, capture hardware, and retail edition generally remain unknown. FM4 means the 2011 Xbox 360 Motorsport game, never Horizon or the 2023 reboot; GT5 means the PS3 full game, never Prologue.

Periodic sample folders are discovery aids, not curated evidence. Only manifest-listed PNG files are curated. Source recordings are primary observations of the software; spoken claims are only navigation leads. Automatic captions can be wrong.

## Official corroboration

- [Microsoft FM4 official manual](https://download.microsoft.com/download/F/9/9/F99AB8F0-5191-4EDD-B312-7A9B9E4784FA/Forza4_MNL_EN-US.pdf) documents the in-game Marketplace, Message Center, Autovista, Car Clubs, and Install Disc 2 flow. The manual was downloaded and text-extracted locally; it is not a complete illustrated page census.
- [GT5 official update 1.05](https://www.gran-turismo.com/us/news/02_0005516.html) establishes that Seasonal Events and Online Dealership were added after launch, so these cannot be inferred from launch-only tours. It also names Race Display and Personal BGM options.
- [GT5 official update 1.06](https://us.gran-turismo.com/us/news/02_0005552.html) is a version corroboration lead for the captured 1.06 overview; the detailed page fetch timed out, so the footage is the visual evidence.

## Design observations grounded in pixels

- FM4 uses a compact left navigation rail, a dominant car scene, a thumbnail ribbon for car choices, red focus lines, narrow uppercase headings, and persistent bottom controller prompts. Tuning uses aligned slider rows with contextual prose on the right; results separate credits from XP. See the corresponding page rows below.
- GT5 has several distinct visual systems: the asymmetric GT Life tile dashboard, silver Arcade selectors, the illustrated Tuning Shop, bright white/orange GT Auto, dark Options dialogs, and the blue online/remote-race surfaces. Treating GT5 as one generic menu would erase these distinctions. See the corresponding page rows below.

## Forza Motorsport 4 (2011 Xbox 360)

84 curated frame records. Manifest: [fm4/manifest.json](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/manifest.json). Every row links both source time and retained pixels; hashes, dimensions, source title, uploader/date and edition confidence are in the manifest.

| Page / state | Source time | Captured frame |
|---|---|---|
| startup-loading | [0:15](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=15s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00015-startup-loading.png) |
| welcome-help | [1:40](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=100s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00100-welcome-help.png) |
| how-to-play-controller | [1:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00115-how-to-play-controller.png) |
| tutorial-accelerate-overlay | [2:17](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=137s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00137-tutorial-accelerate-overlay.png) |
| tutorial-change-view-overlay | [2:27](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=147s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00147-tutorial-change-view-overlay.png) |
| finish-position | [4:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=285s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00285-finish-position.png) |
| import-profile-dialog | [5:15](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=315s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00315-import-profile-dialog.png) |
| profile-imported-dialog | [5:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=335s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00335-profile-imported-dialog.png) |
| first-car-select | [5:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=355s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00355-first-car-select.png) |
| car-color-select | [6:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=395s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00395-car-color-select.png) |
| message-center-welcome-dialog | [6:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=415s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00415-message-center-welcome-dialog.png) |
| message-center-inbox | [7:15](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=435s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00435-message-center-inbox.png) |
| play-career-hub | [7:25](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=445s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00445-play-career-hub.png) |
| quick-upgrade-help-dialog | [7:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=455s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00455-quick-upgrade-help-dialog.png) |
| quick-upgrade-class | [7:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=465s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00465-quick-upgrade-class.png) |
| tune-tires | [7:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=475s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00475-tune-tires.png) |
| tune-alignment | [8:05](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=485s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00485-tune-alignment.png) |
| tune-anti-roll-bars | [8:15](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=495s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00495-tune-anti-roll-bars.png) |
| tune-damping | [8:25](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=505s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00505-tune-damping.png) |
| tune-differential | [8:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=515s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00515-tune-differential.png) |
| tune-gearing | [8:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=525s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00525-tune-gearing.png) |
| upgrade-hub | [9:05](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=545s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00545-upgrade-hub.png) |
| showroom-search-results | [9:15](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=555s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00555-showroom-search-results.png) |
| car-details-context-menu | [9:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=575s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00575-car-details-context-menu.png) |
| storefront-search-result-expanded | [9:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=585s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00585-storefront-search-result-expanded.png) |
| tuning-file-options-dialog | [10:05](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=605s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00605-tuning-file-options-dialog.png) |
| paint-hub | [10:25](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=625s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00625-paint-hub.png) |
| paint-part-select | [10:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=635s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00635-paint-part-select.png) |
| paint-palette | [10:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=655s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00655-paint-palette.png) |
| paint-not-supported-dialog | [11:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=715s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00715-paint-not-supported-dialog.png) |
| no-saves-dialog | [13:05](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=785s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00785-no-saves-dialog.png) |
| choose-vinyl-group | [13:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=825s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00825-choose-vinyl-group.png) |
| locked-vinyl-dialog | [14:05](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=845s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00845-locked-vinyl-dialog.png) |
| design-tips-dialog | [14:25](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=865s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00865-design-tips-dialog.png) |
| create-layer-menu | [14:35](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=875s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00875-create-layer-menu.png) |
| save-changes-dialog | [14:45](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=885s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00885-save-changes-dialog.png) |
| my-profile-overview | [14:55](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=895s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/aHc6YIxHY8I-00895-my-profile-overview.png) |
| main-menu | [0:05](https://www.youtube.com/watch?v=upSr1pKvIKk&t=5s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00005-main-menu.png) |
| my-cars | [0:25](https://www.youtube.com/watch?v=upSr1pKvIKk&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00025-my-cars.png) |
| cars-hub | [1:15](https://www.youtube.com/watch?v=upSr1pKvIKk&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00075-cars-hub.png) |
| community-features | [1:25](https://www.youtube.com/watch?v=upSr1pKvIKk&t=85s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00085-community-features.png) |
| club-garage | [1:45](https://www.youtube.com/watch?v=upSr1pKvIKk&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00105-club-garage.png) |
| replay-controls | [7:25](https://www.youtube.com/watch?v=upSr1pKvIKk&t=445s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00445-replay-controls.png) |
| my-storefront-grid | [9:35](https://www.youtube.com/watch?v=upSr1pKvIKk&t=575s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00575-my-storefront-grid.png) |
| vinyl-group-details | [9:45](https://www.youtube.com/watch?v=upSr1pKvIKk&t=585s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00585-vinyl-group-details.png) |
| storefront-hub | [9:55](https://www.youtube.com/watch?v=upSr1pKvIKk&t=595s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00595-storefront-hub.png) |
| autovista-car-select | [10:05](https://www.youtube.com/watch?v=upSr1pKvIKk&t=605s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00605-autovista-car-select.png) |
| autovista-interior | [11:15](https://www.youtube.com/watch?v=upSr1pKvIKk&t=675s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00675-autovista-interior.png) |
| autovista-challenge-dialog | [11:25](https://www.youtube.com/watch?v=upSr1pKvIKk&t=685s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00685-autovista-challenge-dialog.png) |
| autovista-hotspot-overlay | [11:55](https://www.youtube.com/watch?v=upSr1pKvIKk&t=715s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00715-autovista-hotspot-overlay.png) |
| autovista-engine-performance | [12:45](https://www.youtube.com/watch?v=upSr1pKvIKk&t=765s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00765-autovista-engine-performance.png) |
| free-play-menu | [14:05](https://www.youtube.com/watch?v=upSr1pKvIKk&t=845s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00845-free-play-menu.png) |
| marketplace-hub | [14:15](https://www.youtube.com/watch?v=upSr1pKvIKk&t=855s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00855-marketplace-hub.png) |
| buy-car-tokens-dialog | [14:25](https://www.youtube.com/watch?v=upSr1pKvIKk&t=865s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/upSr1pKvIKk-00865-buy-car-tokens-dialog.png) |
| challenge-event-help-dialog | [0:25](https://www.youtube.com/watch?v=Gfcpak-301Y&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00025-challenge-event-help-dialog.png) |
| assists-and-difficulty | [0:55](https://www.youtube.com/watch?v=Gfcpak-301Y&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00055-assists-and-difficulty.png) |
| cockpit-race-hud | [1:55](https://www.youtube.com/watch?v=Gfcpak-301Y&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00115-cockpit-race-hud.png) |
| post-race-credit-breakdown | [5:15](https://www.youtube.com/watch?v=Gfcpak-301Y&t=315s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00315-post-race-credit-breakdown.png) |
| post-race-xp-breakdown | [5:25](https://www.youtube.com/watch?v=Gfcpak-301Y&t=325s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00325-post-race-xp-breakdown.png) |
| pre-race-menu | [5:35](https://www.youtube.com/watch?v=Gfcpak-301Y&t=335s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00335-pre-race-menu.png) |
| affinity-reward | [9:35](https://www.youtube.com/watch?v=Gfcpak-301Y&t=575s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00575-affinity-reward.png) |
| choose-reward-car | [9:45](https://www.youtube.com/watch?v=Gfcpak-301Y&t=585s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00585-choose-reward-car.png) |
| select-car-confirm-dialog | [10:15](https://www.youtube.com/watch?v=Gfcpak-301Y&t=615s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00615-select-car-confirm-dialog.png) |
| world-tour-division-complete | [10:25](https://www.youtube.com/watch?v=Gfcpak-301Y&t=625s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00625-world-tour-division-complete.png) |
| world-tour-map | [10:45](https://www.youtube.com/watch?v=Gfcpak-301Y&t=645s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/Gfcpak-301Y-00645-world-tour-map.png) |
| world-tour-event-select | [1:35](https://www.youtube.com/watch?v=JvLQQOHkoWc&t=95s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/JvLQQOHkoWc-00095-world-tour-event-select.png) |
| storefront-turn10-picks | [0:25](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00025-storefront-turn10-picks.png) |
| design-details-seller-menu | [0:35](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=35s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00035-design-details-seller-menu.png) |
| my-storefront-designs | [2:55](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=175s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00175-my-storefront-designs.png) |
| my-storefront-photos | [3:35](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=215s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00215-my-storefront-photos.png) |
| auction-details | [3:55](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=235s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00235-auction-details.png) |
| my-auctions-list | [4:35](https://www.youtube.com/watch?v=vBhTUO2tgqo&t=275s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/vBhTUO2tgqo-00275-my-auctions-list.png) |
| autovista-halo-interior-gauges | [0:25](https://www.youtube.com/watch?v=FX4pRYgOpYk&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/FX4pRYgOpYk-00025-autovista-halo-interior-gauges.png) |
| autovista-digital-gauges | [0:55](https://www.youtube.com/watch?v=FX4pRYgOpYk&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/FX4pRYgOpYk-00055-autovista-digital-gauges.png) |
| telemetry-overlay | [3:05](https://www.youtube.com/watch?v=VKHTTSv12XI&t=185s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/VKHTTSv12XI-00185-telemetry-overlay.png) |
| replay-theater-library | [0:05](https://www.youtube.com/watch?v=jBxfH1m1L38&t=5s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00005-replay-theater-library.png) |
| my-profile-media-hub | [0:45](https://www.youtube.com/watch?v=jBxfH1m1L38&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00045-my-profile-media-hub.png) |
| my-stats-general | [0:55](https://www.youtube.com/watch?v=jBxfH1m1L38&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00055-my-stats-general.png) |
| event-list-grid-porsche-dlc | [1:05](https://www.youtube.com/watch?v=jBxfH1m1L38&t=65s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00065-event-list-grid-porsche-dlc.png) |
| event-list-grid-event-details | [1:15](https://www.youtube.com/watch?v=jBxfH1m1L38&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00075-event-list-grid-event-details.png) |
| event-showcase-loading-card | [1:45](https://www.youtube.com/watch?v=jBxfH1m1L38&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00105-event-showcase-loading-card.png) |
| track-location-loading-card | [1:55](https://www.youtube.com/watch?v=jBxfH1m1L38&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00115-track-location-loading-card.png) |
| assists-event-rules | [2:15](https://www.youtube.com/watch?v=jBxfH1m1L38&t=135s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/jBxfH1m1L38-00135-assists-event-rules.png) |
| post-race-menu | [2:55](https://www.youtube.com/watch?v=h5PlRVkgniI&t=175s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/h5PlRVkgniI-00175-post-race-menu.png) |

### Known missing page inventory

- Full system Options subtree (HUD, audio, controller remapping/deadzones, video, Kinect/head tracking)
- Upgrade Shop category/item/purchase pages; tuning springs/aero/brakes and tuning-save/name dialogs
- Event championship standings/results beyond captured Event List grid/detail
- Quick Race and split-screen track/car/race setup
- Rivals event/leaderboard and rival details
- Public/private multiplayer lobby, create-game and advanced race-rule screens
- Auction search/create/bid/buy/claim flows beyond My Auctions/detail
- Club management/member/invite pages beyond club garage
- Photo mode controls/settings/save, replay save/upload and media galleries
- Marketplace pack/content detail/purchase, Install Disc 2 dialogs
- Paint layer-transform/editor tools, text/font and vinyl-shape subpages beyond create-layer chooser
- Benchmark/test-drive pages and race pause/restart/quit/rewind flows

## Gran Turismo 5 (PS3 full game)

112 curated frame records. Manifest: [gt5/manifest.json](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/manifest.json). Every row links both source time and retained pixels; hashes, dimensions, source title, uploader/date and edition confidence are in the manifest.

| Page / state | Source time | Captured frame |
|---|---|---|
| main-menu | [0:07](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=7s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00007-main-menu.png) |
| gt-life-home | [0:22](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=22s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00022-gt-life-home.png) |
| psn-sign-in-dialog | [1:16](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=76s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00076-psn-sign-in-dialog.png) |
| arcade-mode-single-race | [1:28](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=88s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00088-arcade-mode-single-race.png) |
| arcade-mode-2p | [1:32](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=92s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00092-arcade-mode-2p.png) |
| arcade-mode-time-trial | [1:37](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=97s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00097-arcade-mode-time-trial.png) |
| course-maker-location-select | [2:02](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=122s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00122-course-maker-location-select.png) |
| gran-turismo-tv | [2:42](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=162s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00162-gran-turismo-tv.png) |
| manual-index | [3:07](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=187s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00187-manual-index.png) |
| options-general | [3:29](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=209s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00209-options-general.png) |
| options-hardware | [3:32](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=212s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00212-options-hardware.png) |
| options-steering-controllers | [3:36](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=216s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00216-options-steering-controllers.png) |
| options-others | [3:43](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=223s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00223-options-others.png) |
| saving-data-warning-dialog | [3:59](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=239s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/JyP_HfW9cVs-00239-saving-data-warning-dialog.png) |
| first-run-setup-notice | [2:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=160s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00160-first-run-setup-notice.png) |
| gift-outfit-notice | [3:10](https://www.youtube.com/watch?v=3J4qpSENwzE&t=190s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00190-gift-outfit-notice.png) |
| patch-update-gift-notice | [3:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=220s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00220-patch-update-gift-notice.png) |
| race-loading-screen | [5:10](https://www.youtube.com/watch?v=3J4qpSENwzE&t=310s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00310-race-loading-screen.png) |
| chase-race-hud | [6:10](https://www.youtube.com/watch?v=3J4qpSENwzE&t=370s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00370-chase-race-hud.png) |
| bumper-race-hud | [6:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=400s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00400-bumper-race-hud.png) |
| experience-earned-dialog | [8:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=520s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00520-experience-earned-dialog.png) |
| race-entry-screen | [13:10](https://www.youtube.com/watch?v=3J4qpSENwzE&t=790s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-00790-race-entry-screen.png) |
| level-up-reward-dialog | [17:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=1060s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-01060-level-up-reward-dialog.png) |
| redeem-ticket-confirm-dialog | [18:40](https://www.youtube.com/watch?v=3J4qpSENwzE&t=1120s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-01120-redeem-ticket-confirm-dialog.png) |
| gift-car-use-dialog | [19:10](https://www.youtube.com/watch?v=3J4qpSENwzE&t=1150s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/3J4qpSENwzE-01150-gift-car-use-dialog.png) |
| news-list | [0:15](https://www.youtube.com/watch?v=dUh4i_1NG00&t=15s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00015-news-list.png) |
| news-article | [0:25](https://www.youtube.com/watch?v=dUh4i_1NG00&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00025-news-article.png) |
| garage-filter-list | [0:35](https://www.youtube.com/watch?v=dUh4i_1NG00&t=35s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00035-garage-filter-list.png) |
| upload-progress-dialog | [0:45](https://www.youtube.com/watch?v=dUh4i_1NG00&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00045-upload-progress-dialog.png) |
| profile-overview | [1:05](https://www.youtube.com/watch?v=dUh4i_1NG00&t=65s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00065-profile-overview.png) |
| friend-profile-overview | [1:15](https://www.youtube.com/watch?v=dUh4i_1NG00&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00075-friend-profile-overview.png) |
| shared-car-detail-borrow | [1:25](https://www.youtube.com/watch?v=dUh4i_1NG00&t=85s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00085-shared-car-detail-borrow.png) |
| updating-car-data-dialog | [1:45](https://www.youtube.com/watch?v=dUh4i_1NG00&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00105-updating-car-data-dialog.png) |
| garage-shared-car-tag | [2:05](https://www.youtube.com/watch?v=dUh4i_1NG00&t=125s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00125-garage-shared-car-tag.png) |
| tuning-sheet-tyres | [2:35](https://www.youtube.com/watch?v=dUh4i_1NG00&t=155s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00155-tuning-sheet-tyres.png) |
| tuning-power-limiter-dialog | [2:45](https://www.youtube.com/watch?v=dUh4i_1NG00&t=165s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00165-tuning-power-limiter-dialog.png) |
| tuning-body-chassis | [2:55](https://www.youtube.com/watch?v=dUh4i_1NG00&t=175s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00175-tuning-body-chassis.png) |
| tuning-ballast-dialog | [3:05](https://www.youtube.com/watch?v=dUh4i_1NG00&t=185s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00185-tuning-ballast-dialog.png) |
| tuning-gear-ratios-dialog | [3:15](https://www.youtube.com/watch?v=dUh4i_1NG00&t=195s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00195-tuning-gear-ratios-dialog.png) |
| tuning-transmission | [3:25](https://www.youtube.com/watch?v=dUh4i_1NG00&t=205s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00205-tuning-transmission.png) |
| garage-online-favourites-filter | [3:35](https://www.youtube.com/watch?v=dUh4i_1NG00&t=215s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00215-garage-online-favourites-filter.png) |
| community-friends-list | [3:55](https://www.youtube.com/watch?v=dUh4i_1NG00&t=235s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00235-community-friends-list.png) |
| driver-online-status-confirm-dialog | [4:05](https://www.youtube.com/watch?v=dUh4i_1NG00&t=245s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00245-driver-online-status-confirm-dialog.png) |
| remote-race-event-select | [4:35](https://www.youtube.com/watch?v=dUh4i_1NG00&t=275s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00275-remote-race-event-select.png) |
| remote-race-entry-list | [4:45](https://www.youtube.com/watch?v=dUh4i_1NG00&t=285s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00285-remote-race-entry-list.png) |
| remote-race-friend-driver-select | [4:55](https://www.youtube.com/watch?v=dUh4i_1NG00&t=295s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00295-remote-race-friend-driver-select.png) |
| remote-race-ready | [5:15](https://www.youtube.com/watch?v=dUh4i_1NG00&t=315s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00315-remote-race-ready.png) |
| b-spec-remote-race-hud | [5:35](https://www.youtube.com/watch?v=dUh4i_1NG00&t=335s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00335-b-spec-remote-race-hud.png) |
| server-standby-mode-dialog | [5:55](https://www.youtube.com/watch?v=dUh4i_1NG00&t=355s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00355-server-standby-mode-dialog.png) |
| my-drivers-grid | [6:05](https://www.youtube.com/watch?v=dUh4i_1NG00&t=365s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00365-my-drivers-grid.png) |
| driver-rewards-dialog | [6:15](https://www.youtube.com/watch?v=dUh4i_1NG00&t=375s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/dUh4i_1NG00-00375-driver-rewards-dialog.png) |
| tuning-shop-body-chassis | [0:35](https://www.youtube.com/watch?v=_rWBgLhaNT4&t=35s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/_rWBgLhaNT4-00035-tuning-shop-body-chassis.png) |
| tuning-shop-engine | [0:45](https://www.youtube.com/watch?v=_rWBgLhaNT4&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/_rWBgLhaNT4-00045-tuning-shop-engine.png) |
| tuning-shop-intake | [0:55](https://www.youtube.com/watch?v=_rWBgLhaNT4&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/_rWBgLhaNT4-00055-tuning-shop-intake.png) |
| tuning-shop-part-detail-dialog | [1:15](https://www.youtube.com/watch?v=_rWBgLhaNT4&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/_rWBgLhaNT4-00075-tuning-shop-part-detail-dialog.png) |
| tuning-shop-category-index | [1:35](https://www.youtube.com/watch?v=_rWBgLhaNT4&t=95s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/_rWBgLhaNT4-00095-tuning-shop-category-index.png) |
| gt-auto-hub | [0:15](https://www.youtube.com/watch?v=uYqMriyec1Y&t=15s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00015-gt-auto-hub.png) |
| gt-auto-aero-parts | [0:25](https://www.youtube.com/watch?v=uYqMriyec1Y&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00025-gt-auto-aero-parts.png) |
| gt-auto-wheel-selector | [0:55](https://www.youtube.com/watch?v=uYqMriyec1Y&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00055-gt-auto-wheel-selector.png) |
| gt-auto-paint-wheels | [1:15](https://www.youtube.com/watch?v=uYqMriyec1Y&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00075-gt-auto-paint-wheels.png) |
| gt-auto-paint-body | [1:45](https://www.youtube.com/watch?v=uYqMriyec1Y&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00105-gt-auto-paint-body.png) |
| paint-item-inventory-filter | [1:55](https://www.youtube.com/watch?v=uYqMriyec1Y&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00115-paint-item-inventory-filter.png) |
| gt-auto-oil-change-service | [2:35](https://www.youtube.com/watch?v=uYqMriyec1Y&t=155s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00155-gt-auto-oil-change-service.png) |
| gt-auto-car-wash-confirm | [3:05](https://www.youtube.com/watch?v=uYqMriyec1Y&t=185s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00185-gt-auto-car-wash-confirm.png) |
| gt-auto-car-wash-animation | [3:15](https://www.youtube.com/watch?v=uYqMriyec1Y&t=195s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/uYqMriyec1Y-00195-gt-auto-car-wash-animation.png) |
| controller-button-assignment-dialog | [0:25](https://www.youtube.com/watch?v=s1j-c2hf0dY&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/s1j-c2hf0dY-00025-controller-button-assignment-dialog.png) |
| controller-assignment-dropdown | [0:45](https://www.youtube.com/watch?v=s1j-c2hf0dY&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/s1j-c2hf0dY-00045-controller-assignment-dropdown.png) |
| in-race-ra-tcs-overlay | [2:15](https://www.youtube.com/watch?v=s1j-c2hf0dY&t=135s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/s1j-c2hf0dY-00135-in-race-ra-tcs-overlay.png) |
| in-race-ra-abs-overlay | [2:25](https://www.youtube.com/watch?v=s1j-c2hf0dY&t=145s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/s1j-c2hf0dY-00145-in-race-ra-abs-overlay.png) |
| options-arcade-laps-dialog | [0:15](https://www.youtube.com/watch?v=v28kRHDFqtY&t=15s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/v28kRHDFqtY-00015-options-arcade-laps-dialog.png) |
| options-demo-dialog | [0:25](https://www.youtube.com/watch?v=v28kRHDFqtY&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/v28kRHDFqtY-00025-options-demo-dialog.png) |
| options-audio-dialog | [1:05](https://www.youtube.com/watch?v=v28kRHDFqtY&t=65s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/v28kRHDFqtY-00065-options-audio-dialog.png) |
| options-communication-wait-dialog | [1:45](https://www.youtube.com/watch?v=v28kRHDFqtY&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/v28kRHDFqtY-00105-options-communication-wait-dialog.png) |
| manual-article | [0:25](https://www.youtube.com/watch?v=rziPD1-TdbY&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00025-manual-article.png) |
| options-race-display-dialog | [1:35](https://www.youtube.com/watch?v=rziPD1-TdbY&t=95s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00095-options-race-display-dialog.png) |
| options-audio-volume-dialog | [1:55](https://www.youtube.com/watch?v=rziPD1-TdbY&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00115-options-audio-volume-dialog.png) |
| options-user-music-picker | [2:05](https://www.youtube.com/watch?v=rziPD1-TdbY&t=125s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00125-options-user-music-picker.png) |
| options-audio-dynamic-range-dialog | [2:15](https://www.youtube.com/watch?v=rziPD1-TdbY&t=135s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00135-options-audio-dynamic-range-dialog.png) |
| options-display-dialog | [2:25](https://www.youtube.com/watch?v=rziPD1-TdbY&t=145s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00145-options-display-dialog.png) |
| options-playstation-eye-dialog | [2:35](https://www.youtube.com/watch?v=rziPD1-TdbY&t=155s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00155-options-playstation-eye-dialog.png) |
| options-steering-settings-dialog | [2:45](https://www.youtube.com/watch?v=rziPD1-TdbY&t=165s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00165-options-steering-settings-dialog.png) |
| options-network-dialog | [3:35](https://www.youtube.com/watch?v=rziPD1-TdbY&t=215s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00215-options-network-dialog.png) |
| options-utilities-dialog | [3:45](https://www.youtube.com/watch?v=rziPD1-TdbY&t=225s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/rziPD1-TdbY-00225-options-utilities-dialog.png) |
| community-message-board | [0:25](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00025-community-message-board.png) |
| joining-lounge-progress-dialog | [0:35](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=35s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00035-joining-lounge-progress-dialog.png) |
| lounge-member-list-dialog | [0:55](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00055-lounge-member-list-dialog.png) |
| online-lounge | [1:25](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=85s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00085-online-lounge.png) |
| online-spectator-hud | [1:55](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=115s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00115-online-spectator-hud.png) |
| online-live-timing | [2:15](https://www.youtube.com/watch?v=2TKVXLkDwM0&t=135s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/2TKVXLkDwM0-00135-online-live-timing.png) |
| photo-travel-location-select | [0:25](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00025-photo-travel-location-select.png) |
| photo-travel-camera-location-map | [1:15](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=75s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00075-photo-travel-camera-location-map.png) |
| photo-travel-walk-mode | [1:45](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=105s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00105-photo-travel-walk-mode.png) |
| photo-mode-camera | [2:45](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=165s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00165-photo-mode-camera.png) |
| photo-mode-camera-settings | [3:05](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=185s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00185-photo-mode-camera-settings.png) |
| photo-travel-exit-confirm-dialog | [3:55](https://www.youtube.com/watch?v=6vBMbsdZ7mQ&t=235s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/6vBMbsdZ7mQ-00235-photo-travel-exit-confirm-dialog.png) |
| arcade-track-select | [0:25](https://www.youtube.com/watch?v=WX31g_xCeDI&t=25s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/WX31g_xCeDI-00025-arcade-track-select.png) |
| arcade-car-select-favourites | [0:35](https://www.youtube.com/watch?v=WX31g_xCeDI&t=35s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/WX31g_xCeDI-00035-arcade-car-select-favourites.png) |
| arcade-car-select-stock | [0:45](https://www.youtube.com/watch?v=WX31g_xCeDI&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/WX31g_xCeDI-00045-arcade-car-select-stock.png) |
| dealership-model-carousel | [0:18](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=18s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00018-dealership-model-carousel.png) |
| dealership-paint-select | [0:28](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=28s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00028-dealership-paint-select.png) |
| new-car-delivery | [0:45](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=45s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00045-new-car-delivery.png) |
| gt-auto-aero-kit-selector | [1:35](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=95s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00095-gt-auto-aero-kit-selector.png) |
| tuning-shop-purchase-dialog | [3:45](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=225s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00225-tuning-shop-purchase-dialog.png) |
| tuning-shop-purchase-complete-dialog | [3:55](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=235s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00235-tuning-shop-purchase-complete-dialog.png) |
| tuning-shop-exhaust | [4:55](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=295s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00295-tuning-shop-exhaust.png) |
| tuning-shop-turbo | [5:25](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=325s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00325-tuning-shop-turbo.png) |
| tuning-shop-drivetrain-part | [5:45](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=345s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00345-tuning-shop-drivetrain-part.png) |
| tuning-shop-drivetrain | [5:55](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=355s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00355-tuning-shop-drivetrain.png) |
| practice-track-select | [6:45](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=405s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00405-practice-track-select.png) |
| practice-pre-race-menu | [7:25](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=445s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00445-practice-pre-race-menu.png) |
| cockpit-race-hud | [9:05](https://www.youtube.com/watch?v=Jmhh88KzvZU&t=545s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/Jmhh88KzvZU-00545-cockpit-race-hud.png) |
| dealership-manufacturer-grid | [0:55](https://www.youtube.com/watch?v=nvb5NuGiRv8&t=55s) | [PNG](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/nvb5NuGiRv8-00055-dealership-manufacturer-grid.png) |

### Known missing page inventory

- A-Spec/B-Spec event category grids, event details/regulations/championship standings
- License class/test selection and special-event selection/help/results
- Used-car list and online dealership (manufacturer grid and new-car pages captured)
- Seasonal Event and Open Lobby browse/create/race-rule screens
- B-Spec command/pit strategy screens beyond remote-race spectator HUD
- Full tuning suspension/LSD/brake sheets and all shop categories (suspension/tyres/transmission item lists)
- Course Maker editor sections/settings/test-drive/save (only location selector captured)
- Museum, music library, replay/photo albums, community mail/gifts/log/profile editor, car delivery inventory
- Helmet/suit/outfit item screens, paint-item detail and paint confirmation
- Photo save/export and full camera setting variants
- Pause/quick options/restart/quit/pit-service dialogs
- Racing-modification/engine rebuild/chassis restore purchase dialogs
- 3D/units/vibration/control-wheel-specific options and every scrolling subpage
- Gran Turismo TV program detail/download/cart pages

## Search audit and rejected evidence

Multiple targeted YouTube search passes are retained under the external references root (`*search.jsonl`). Queries covered original-title menu tours, commentary, options, tuning, GT Auto, career, auction house, online lobby, HUD, and virtual tours. Search results were noisy with Horizon/GT7/Prologue; these were excluded. The FM4 Multiplayer Hopper Compilation (`KISRzPXbbeY`) is replay footage rather than lobby UI and contributes no curated menu frames. The first GT5 Menu Tour has loading transitions and highlighted tiles; transition frames were replaced at exact timestamps and tile highlights were not counted as new subpages.

Commentary transcript navigation evidence: FM4 community tour `upSr1pKvIKk` mentions clubs at 84.80s, storefront around 577.84–599.12s, Autovista challenges around 607.68–695.28s, and Marketplace at 847.84s; visual inspection confirms those page families. GT5 patch overview `dUh4i_1NG00` mentions new tuning at 164.56s, online garage at 216.48s and remote play at 236.08s; inspected pixels show the corresponding tuning and remote-race pages. Timestamped transcript text and raw json3 subtitles are retained beside source videos or in the FM4 references folder. Several short dedicated virtual tours had no supplied English automatic subtitles; they were inspected directly.

The known-missing lists describe concrete unsatisfied coverage, including branches visible in captured menus. The library should not be described as every page in either game.

## Expanded screenshot library — completed

The expanded target is **1,000 useful screenshots per game**, including distinct menus, changed states, and varied in-race HUD situations; it is **not** a claim of 1,000 different menu pages. Original curated manifests remain intact. Expanded manifests are normalized JSON arrays and are the authoritative 1,000-item selections; cached candidate images outside those arrays are not accepted evidence.

All bulk static-menu, result-dialog, paint-car rotation, Autovista rotation, and photo-walk ranges were removed from the final extraction inputs to avoid counting an unchanged selection/text with a moving background. Newly discovered menus are single frames at inspected exact timestamps. Bulk additions come from approved HUD sequences with different traffic, position, timing, gear, cornering, camera and track contexts. Some race intervals include meaningful finish/result transitions with UI.

- **FM4: 1,000 accepted screenshots**, {'Curated page or state': 83, 'Race HUD': 916, 'Distinct menu state': 1}. [Expanded manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/expanded-manifest.json); [QA record](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/expanded-qa.json); [full-size contact sheets](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/fm4/expanded-contact-sheets).
- **GT5: 1,000 accepted screenshots**, {'Curated page or state': 110, 'Race HUD': 881, 'Distinct menu state': 9}. [Expanded manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/expanded-manifest.json); [QA record](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/expanded-qa.json); [full-size contact sheets](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/gt5/expanded-contact-sheets).

All 2,000 accepted paths exist, every image SHA256 was recomputed successfully, all required fields are present, and each game has 1,000 distinct SHA256 values. Perceptual filtering is stronger than exact-byte deduplication but does not prove semantic uniqueness; changing camera/HUD/traffic contexts remain deliberately represented. Original curated seeds were preserved without retrospective perceptual pruning. Blank or cinematic-only candidates found during review were excluded; FM4 title-only startup, extra tutorial driving without useful HUD and a finish cinematic were omitted from the expanded library; GT5 car-delivery cinematic and bare race-loading title were omitted.

QA scope: all final 40-frame contact sheets were inspected at thumbnail scale for UI/HUD presence and scene variation. The earlier named-page selection and discovery sheets were inspected at larger sizes, and specific questionable frames were opened at source resolution. This does **not** mean every expanded frame's small text was individually read at full resolution. Source timestamps are actual FFmpeg PTS plus range seek origin, not a guessed frame-number cadence. New bulk assets are JPGs at downloaded source resolution; retained curated seed assets remain PNGs.

New diversity includes FM4 Chevrolet Spark cockpit/chase races and an extended Event List completion session with Peugeot/Acura/Audi LMP races at Silverstone, Indianapolis, Sebring, Road America and Motegi; GT5 adds day/night Sunday Cup, FF, World Compact championship and Japanese Classics footage including London, Madrid, Cape Ring, Fuji, Suzuka and Clubman Stage Route 5. These are direct game recordings; the manifests explicitly avoid claiming the recording was necessarily made on original console hardware. The one original FM4 Gamescom presentation seed remains explicitly marked prerelease filmed-monitor evidence and the UI-artist reel remains marked portfolio/in-world gauges.

Expanded singleton menus close some initial gaps: GT5 A-Spec category/event details, Special Events cards, units options, Used Car Dealer, championship points and eligible-car dialog; FM4 retail World Tour event selection. The initial missing-branch lists above describe the first named-page pass; these listed additions supersede those particular missing items, while unrepresented branches remain unresolved.

Reproduction inputs: `fm4-ranges.json` and `gt5-ranges.json` in the external references root; final exclusions `fm4-qa-exclude.json` and `gt5-qa-exclude.json`; shared `expand_frames.py` extraction helper. Broader abandoned range candidates are kept separately as `*-all-range-candidates.json`, never counted as accepted coverage.

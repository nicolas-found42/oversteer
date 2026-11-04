# Driver: San Francisco UI reference evidence

Research date: 2026-11-04. Scope is the PC/PS3/Xbox 360 game, not the separate Wii game. This inventory is **not exhaustive**. A page is counted only when its UI is visible in the recording; narration is a search aid, not visual proof.

The local [browsable library](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/index.html) links full-resolution extracted frames to exact source timestamps. The [Driver manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/driver/manifest.json) preserves individual labels, provenance, edition uncertainty, and hashes.

## Primary visual evidence

The [579-second menu tour](https://www.youtube.com/watch?v=tGX6S8PPk1g) shows Xbox 360 prompts and an Xbox Live notification. Exact retail patch is unestablished. Captured branches:

- Story and main menu, 00:05–00:15.
- Online lobby, playlists, privacy, tutorials, profile icons, profile, upgrades and statistics, 00:25–02:05.
- Split-screen controller requirement, duration, competitive and cooperative modes, level selection, 02:25–03:15.
- Challenge cards and categories, 03:35–04:05; film-director recording selector, 04:15.
- Historical Uplay actions, reward details and rewards, 04:35–05:15. These are historical service UI captures, not a claim of current service availability.
- Driving and Shift controller presets, 05:44–06:00; options, volume, spoken language, subtitle language and social options, 06:08–06:32.
- Extras, Uplay passport notice, exclusive-content confirmation, 06:40–06:50.
- Manual index and Game Modes article pages, 06:56–07:00.
- General, stunt, record and multiplayer statistics, achievements and credits, 07:25–09:35.

The [ColourShed review's gameplay segment](https://www.youtube.com/watch?v=oOhT6MnbcIA&t=970s) shows mission launch, city Shift map, completion overlays, garage vehicles, locked garage upgrades, and driving HUD. The transcript's “upgrade” mention at 995.5 seconds led to the garage vehicle and upgrade frames at 995 and 997 seconds. This is evidence from the displayed game pixels; the reviewer's opinions are not adopted as facts. Exact hardware/patch is unknown.

Two short filmed-screen purchase recordings add [upgrade categories, purchase confirmation, and owned state](https://www.youtube.com/watch?v=zmzD5Hhd8I8), plus [locked upgrades and token finder](https://www.youtube.com/watch?v=pHWjJ1d9MSM). Their camera exposure makes them weaker typography references than the direct menu tour.

The [Fan Service guide](https://www.youtube.com/watch?v=ejSftCsXJys) adds the garage challenge checklist HUD and reward result, with Dutch text and Xbox prompts. The [garage montage](https://www.youtube.com/watch?v=meGn5pyLaIM) and [garage-themed trailer](https://www.youtube.com/watch?v=i8awz8BCnxg) were inspected but rejected as menu evidence: “garage” in a title does not mean a garage interface appears.

## Coverage still missing

The expanded collection now contains **1,000 accepted screenshots** in the [expanded manifest](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/driver/expanded-manifest.json). It preserves the 59 named references above and adds campaign and historical online HUD sequences. The [full playthrough](https://www.youtube.com/watch?v=BIBnZ45jsf4) supplies chase, cockpit, Shift, pursuit, objective, damage, ability and completion states. The [online Takedown recording](https://www.youtube.com/watch?v=Le2pZsqfFbM) supplies multiplayer standings, target roles, round transitions and results. PC capture is inferred from a Steam notification in the campaign; exact patch and the online recording's hardware remain unestablished.

Every accepted frame was inspected in contact sheets for visible UI and scene variation, including all replacement frames after 67 cinematic-only or redundant candidates were removed. Perceptual filtering also rejects nearly identical pixels. All 1,000 files have distinct verified SHA-256 hashes. This is not a claim that every frame received individual full-resolution typography inspection or that these are 1,000 distinct interface designs. The [QA record](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/driver/expanded-qa.json) records the manifest fingerprint and breakdown. Bulk repeated menu-tour backgrounds were excluded; named pages remain individually accessible in the gallery.

Despite the expanded count, these branches remain unverified:

- In-game pause page and its nested branches.
- Film-director editing timeline and camera/editor submenus; only recording selection is captured.
- Online vehicle selection, leaderboard details, race matchmaking/setup outcomes, and all mode-specific lobby variants.
- Manual articles beyond Game Modes, including story mode, controls, Shift/abilities, HUDs, garages and challenges.
- System storage selection and account/system overlays.
- Complete garage vehicle filters, purchase/insufficient-funds/cancel outcomes, and all upgrade category states.
- Every challenge/result variant and every localization/platform/update variant.

The two commentary transcripts were fetched and retained locally. One long playthrough's automatic captions mainly transcribe in-game dialogue; no menu-keyword lead emerged. The menu tour has no available captions. Mod-menu results were excluded from retail-UI evidence.

## Opinionated design analysis

The menu tour's repeated title rail, highlighted row, preview area and contextual explanation make the hierarchy legible across very different tasks. Driver uses yellow for solo and blue for online branches while keeping the same interaction language. That consistency is worth borrowing as a principle. The steep tilt, narrow lettering and moving backgrounds are less suitable for Oversteer's quiet tuner identity; copying those shapes would also sacrifice our own identity. [Visual basis: lobby](https://www.youtube.com/watch?v=tGX6S8PPk1g&t=25s), [split screen](https://www.youtube.com/watch?v=tGX6S8PPk1g&t=165s), [options](https://www.youtube.com/watch?v=tGX6S8PPk1g&t=368s).

Oversteer should give every action an obvious state, reserve a stable place for the page title and help, and keep confirmations inside the same visual system. The road must remain the dominant racing surface; status should be grouped at the edges with speed and objective readable at a glance. These are design judgments inferred from the inspected frames, not claims that Driver implements every interaction perfectly. [Visual basis: confirmation](https://www.youtube.com/watch?v=tGX6S8PPk1g&t=410s), [HUD](https://www.youtube.com/watch?v=oOhT6MnbcIA&t=1009s).

# Racing UI research library

The user requested references from seven games, then explicitly clarified the expanded target as **1,000 useful screenshots per game, including menu states, transitions and in-race HUDs**. This is a screenshot target, not a claim that each game has 1,000 unique menu pages.

[Open the local gallery](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/index.html). It contains **7,000 screenshots: 1,000 per game**, with game and capture-type filters, text search, pagination, source-resolution images, and timestamped source links. Media and raw source recordings are outside the repository; these notes retain the research and provenance.

All selected files and their hashes are validated in the [machine-readable validation report](/Users/nicolas/Documents/github/oversteer-ui-review-20261104/references/validation.json). Each game has 1,000 distinct file hashes. Visual QA examined all selected contact-sheet frames for MCLA, MC3, FM4, GT5 and Driver; Burnout 3 and ProStreet used reviewed ranges, representative sheets and inspection of machine-flagged candidates. The individual notes state the limits. Distinct hashes do not imply distinct menu designs or eliminate every semantically similar HUD frame.

| Games | Research and remaining page gaps |
|---|---|
| Midnight Club: Los Angeles; Midnight Club 3: DUB Edition | [Midnight Club inventory](midnight-club.md) |
| Forza Motorsport 4; Gran Turismo 5 | [Forza and GT inventory](fm4-gt5.md) |
| Burnout 3: Takedown; Need for Speed: ProStreet | [Burnout and ProStreet inventory](burnout-prostreet.md) |
| Driver: San Francisco | [Driver inventory](driver-san-francisco.md) |

## Evidence standards

Source recordings are direct visual observations of the games. Titles, automatic captions and chapter timestamps help locate candidate UI; they do not prove what appears on screen. Downloaded frames retain source resolution, which can be lower than the native game resolution. No upscaling is presented as recovered detail.

Each game's original `manifest.json` retains individually named pages/states. Its `expanded-manifest.json` adds time-indexed sequence frames. The combined `library.json` stores paths, game, page/state labels, exact extraction times or stated seek tolerance, source URLs, verification granularity, edition confidence and SHA-256 hashes. Duplicate filtering removes nearly identical pixel layouts but cannot decide whether a frame is a useful menu/HUD reference; visual contact-sheet QA provides that additional check. Contact-sheet inspection is not described as individual full-resolution inspection.

Confirmed Remix footage, prerelease demonstrations, modified interfaces, platform variants and historical online services are kept distinct. A source title alone cannot establish original MC3 rather than Remix, or retail Forza rather than a demo. Missing menu branches remain listed even after the numeric target is met.

## Direction for Oversteer

The current baseline's biggest problem is weak hierarchy: actions look like loose labels, controls change appearance across screens, and panels occupy space without making the next decision clearer. The reference games suggest specific improvements rather than a borrowed skin:

- **FM4:** keep the car prominent; use a stable navigation column, aligned tuning rows, and persistent action hints. [Tuning evidence](https://www.youtube.com/watch?v=aHc6YIxHY8I&t=475s).
- **GT5:** make each destination understandable through its task and content. Its multiple visual systems are a warning against treating “GT5 style” as one template. Preserve Oversteer's own consistent controls across destinations. [GT Life evidence](https://www.youtube.com/watch?v=JyP_HfW9cVs&t=22s).
- **Midnight Club:** make customization a visible relationship between a chosen part and the car preview. Keep category, current selection and purchase consequences close together. [MCLA customization evidence](https://www.youtube.com/watch?v=Iox-lbwsErU&t=45s), [MC3 purchase flow](https://www.youtube.com/watch?v=F2NtN_tYJHo&t=255s).
- **ProStreet:** repeat selection, category and confirmation rules across shops and tuning. Use restrained structure to carry dense information. [Tuning](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=360s), [confirmation](https://www.youtube.com/watch?v=0n-0RQOu-EQ&t=495s).
- **Burnout 3:** give each navigation step a clear heading and preserve the controller vocabulary as information density changes. [World Tour event selection](https://www.youtube.com/watch?v=mtovt4l8-hk&t=840s).
- **Driver:** keep the page title, selected row, preview and explanation in predictable places. Group racing information at the edges so the road remains dominant. [Options](https://www.youtube.com/watch?v=tGX6S8PPk1g&t=368s), [racing HUD](https://www.youtube.com/watch?v=oOhT6MnbcIA&t=1009s).

These are design judgments from the inspected evidence. Oversteer should retain its own charcoal, off-white and restrained teal identity, with clear focus/hover/disabled states, stable keyboard focus, bounded dialogs, separated car/action regions and compact racing instruments. Copying distinctive logos, menu geometry or ornamental assets is not required to obtain those strengths.

"""Granular visual reference taxonomy: observations, not claims about hidden game rules.

Routing is hierarchical. Broad domain first, then only that domain's leaf choices.
Use independent Nouls for overlapping details. Read each fallback as unresolved,
not as evidence that a game mechanic exists. Definitions requiring readable labels
must not be inferred from the uploader title or the platform filename.
"""

GROUPS = {
    "session": "Startup, profiles, top-level navigation, and saving; excludes driver appearance "
    "editing.",
    "character": "Driver name, avatar preset, face, hair, and clothing editing.",
    "career": "Leagues, goals, event selection, promotion, rewards, and player DNA.",
    "crew": "Selecting, hiring, inspecting DNA, or assigning crew members.",
    "garage": "Owned-car selection, sale, specifications, showroom view, or pink-slip ownership "
    "records.",
    "dealership": "Browsing or buying a car; excludes owned-car selection and modification "
    "checkout.",
    "body": "Visual car parts, interior, wheels, license plate, modification category navigation, "
    "and checkout.",
    "paint_vinyl": "Body or part paint, paint finish, vinyl designs, placement, layers, and color.",
    "performance": "Upgrade packs, component systems, tuning controls, and performance-unlock "
    "challenges.",
    "wagering": "Cash, pink-slip, or spectator bets and pre-race rival inspection; not ownership "
    "history.",
    "race": "Loading, pre-race introduction, countdown, active driving, pause, and finish overlay.",
    "results": "Post-event standings, challenge outcomes, payouts, car transfers, or podium.",
    "replay": "Explicit race replay playback or replay camera controls.",
    "options": "Input bindings, audio, display, difficulty, assists, language, or settings menus.",
    "multiplayer": "Online session interface, multiplayer roster, connection, or split-screen "
    "gameplay.",
    "presentation": "Non-actionable game cinematics, hosts, driver introductions, or credits.",
    "reference": "Uploader/editor/emulator overlay dominates, or image is too obscured to "
    "identify gameplay.",
}

SCREEN_GROUPS = {
    "session": {
        "boot/title": "Title logo or press-start screen before the main menu.",
        "boot/legal": "Publisher, developer, legal, or startup logo splash.",
        "menu/main": "Top-level menu choosing career, race, options, or other major modes.",
        "boot/controller-prompt": "Startup prompt requesting a controller, storage "
        "device, or sign-in before the main menu.",
        "menu/profile/create": "Creating or naming a save profile; distinguish from "
        "editing the in-game driver avatar.",
        "menu/profile/select": "Selecting an existing save profile or save slot.",
        "menu/profile/save": "Explicit saving, save success, or save overwrite interface.",
        "menu/profile/delete": "Explicit deletion or overwrite confirmation for a saved profile.",
        "menu/mode/quick-race": "Choosing quick race, arcade race, or free race outside career.",
        "menu/mode/celebrity": "Selecting an explicitly named celebrity race or celebrity "
        "challenge mode.",
        "menu/transition/animation": "Game menu animation between selections with no "
        "readable active choice.",
        "menu/profile/unspecified": "Profile or save-slot selection, creation, loading, "
        "or save confirmation. Use only when its more "
        "specific visible subtype cannot be read.",
        "menu/mode/unspecified": "Race-mode selection outside a career event list. Use "
        "only when its more specific visible subtype cannot be "
        "read.",
        "menu/transition/unspecified": "An animated game menu background or icon "
        "transition with no readable active menu yet. Use "
        "only when its more specific visible subtype "
        "cannot be read.",
    },
    "character": {
        "character/preset": "Choosing a driver avatar or character preset.",
        "character/face/head-shape": "Editing overall head or face shape; readable "
        "selected field identifies that region.",
        "character/face/eyes-brows": "Editing eye or eyebrow shape, position, width, or "
        "depth; selected field must be readable.",
        "character/face/nose": "Editing the nose; selected nose field must be readable.",
        "character/face/mouth-jaw": "Editing mouth, lips, jaw, or chin; selected field "
        "must be readable.",
        "character/face/skin": "Selecting skin tone or complexion; do not infer this "
        "from the avatar's appearance alone.",
        "character/face/hair": "Selecting hair style or hair color; an actionable hair "
        "choice must be visible.",
        "character/face/facial-hair": "Selecting facial-hair style or color; an "
        "actionable choice must be visible.",
        "character/clothing/headwear": "Selecting a hat, cap, or other headwear; "
        "actionable choice must be visible.",
        "character/clothing/top": "Selecting a shirt, jacket, or upper-body garment; "
        "actionable choice must be visible.",
        "character/clothing/bottom": "Selecting trousers, skirt, or lower-body "
        "clothing; actionable choice must be visible.",
        "character/clothing/shoes": "Selecting shoes or footwear; actionable choice "
        "must be visible.",
        "character/clothing/color": "Choosing the color of the selected garment rather "
        "than its design.",
        "character/identity/name": "On-screen entry or editing of the player's driver name.",
        "character/face/unspecified": "Editing face, head, skin, hair, or facial "
        "features. Use only when its more specific "
        "visible subtype cannot be read.",
        "character/clothing/unspecified": "Editing driver clothing, accessories, or "
        "outfit colors. Use only when its more "
        "specific visible subtype cannot be read.",
        "character/identity/unspecified": "Entering or confirming driver name, gender, "
        "or identity. Use only when its more specific "
        "visible subtype cannot be read.",
    },
    "career": {
        "career/hub": "Career overview with navigation to garage, leagues, or other career areas.",
        "career/dna-challenges": "Driver DNA discipline list such as circuit, overtake, "
        "nitrous, spooking, or betting.",
        "career/leagues/select": "Selecting an available league or tier in the league ladder.",
        "career/leagues/locked": "Inspecting an explicitly locked league with its unmet "
        "requirements visible.",
        "career/goals/checklist": "A league-goal list with checked and unchecked "
        "completion indicators.",
        "career/goals/detail": "One selected career goal's detailed condition or description.",
        "career/event-list/circuit": "An event-selection screen explicitly showing a "
        "circuit race or circuit category.",
        "career/event-list/drift": "An event-selection screen explicitly showing a drift "
        "event or drift category.",
        "career/event-list/tournament": "Selecting an explicitly labeled championship or "
        "multi-round tournament.",
        "career/event-details/requirements": "A selected event's eligibility, required car "
        "class, or entry requirement is the active "
        "information.",
        "career/event-details/track": "A selected event's course layout, venue, route "
        "length, or laps are the active information.",
        "career/event-details/rewards": "A selected event's entry fee or prize information "
        "is the active information.",
        "career/promotion/announcement": "Explicit promotion or newly reached league announcement.",
        "career/reward/visual-unlock": "Explicit visual-modification or decal unlock award.",
        "career/reward/prototype-unlock": "Explicit prototype or performance-unlock award.",
        "career/dna-profile/helix": "Driver DNA displayed as a helix with named driving "
        "disciplines; no opponent-selection list active.",
        "career/dna-profile/statistics": "Driver DNA shown as numerical statistics, bars, "
        "or a profile summary rather than a helix.",
        "career/dna-opponents/download": "Explicit selection or download of another driver's DNA.",
        "career/dna-opponents/challenge": "Selecting an explicitly labeled DNA challenge "
        "against another driver.",
        "career/leagues/unspecified": "League ladder or selection showing progression "
        "tiers. Use only when its more specific visible "
        "subtype cannot be read.",
        "career/goals/unspecified": "League goals, achievements, or promotion requirements "
        "list. Use only when its more specific visible subtype "
        "cannot be read.",
        "career/event-list/unspecified": "Choosing an event from a career event list or "
        "map. Use only when its more specific visible "
        "subtype cannot be read.",
        "career/event-details/unspecified": "Selected event rules, entry requirements, "
        "prize, or track preview. Use only when its "
        "more specific visible subtype cannot be read.",
        "career/promotion/unspecified": "League promotion, newly unlocked league, or "
        "career milestone announcement. Use only when its "
        "more specific visible subtype cannot be read.",
        "career/reward/unspecified": "Reward, unlock, achievement, or bonus announcement "
        "outside results tables. Use only when its more "
        "specific visible subtype cannot be read.",
        "career/dna-profile/unspecified": "Driver DNA profile or driving-style statistics "
        "overview. Use only when its more specific "
        "visible subtype cannot be read.",
        "career/dna-opponents/unspecified": "DNA opponent selection, download, or "
        "challenge list. Use only when its more "
        "specific visible subtype cannot be read.",
    },
    "crew": {
        "crew/selection/roster": "Choosing from a list of potential or current crew members.",
        "crew/selection/hire": "A selected crew member with an explicit Hire action or fee.",
        "crew/selection/dna": "A selected crew member's DNA profile or driving-style display.",
        "crew/management/lineup": "Assigning or replacing crew members in the active racing "
        "lineup.",
        "crew/management/race-role": "Explicitly assigning a crew member's race role or "
        "instruction.",
        "crew/selection/unspecified": "Selecting, recruiting, or inspecting a crew member. "
        "Use only when its more specific visible subtype "
        "cannot be read.",
        "crew/management/unspecified": "Crew management or teammate instructions menu. Use "
        "only when its more specific visible subtype cannot "
        "be read.",
    },
    "garage": {
        "garage/car-showcase": "Car displayed on a showroom turntable without an active "
        "editing or shopping interface.",
        "garage/overview/modification-navigation": "Owned-car garage menu with visual or "
        "performance modification category "
        "navigation.",
        "garage/owned-cars/list": "Choosing among owned cars, with no car-purchase price "
        "as the main action.",
        "garage/owned-cars/details": "Inspecting specifications or eligibility for a car "
        "already owned.",
        "garage/pink-slip-record/history": "Pink-slip document where ownership or "
        "transaction history is the prominent "
        "information.",
        "garage/pink-slip-record/statistics": "Pink-slip document where race count, wins, "
        "winnings, or spent amounts are prominent.",
        "garage/sell-confirm/offer": "Selected owned car with its sale value and explicit "
        "sell action.",
        "garage/sell-confirm/dialog": "An explicit yes/no confirmation to sell the owned car.",
        "garage/overview/unspecified": "Garage car overview with navigation among "
        "modification functions. Use only when its more "
        "specific visible subtype cannot be read.",
        "garage/owned-cars/unspecified": "Choosing among cars already owned, without a "
        "purchase transaction. Use only when its more "
        "specific visible subtype cannot be read.",
        "garage/pink-slip-record/unspecified": "Pink-slip ownership document with owner, "
        "value, races, or history; not placing a "
        "wager. Use only when its more specific "
        "visible subtype cannot be read.",
        "garage/sell-confirm/unspecified": "Confirming sale of an owned car or displaying "
        "its sale value. Use only when its more "
        "specific visible subtype cannot be read.",
    },
    "dealership": {
        "dealership/car-list/manufacturer": "Choosing a manufacturer or make before "
        "selecting a car model.",
        "dealership/car-list/model": "Browsing purchasable car models within a "
        "manufacturer or eligible league.",
        "dealership/car-details/specifications": "Purchase-focused car preview with "
        "technical specifications or class "
        "eligibility.",
        "dealership/car-details/color": "Selecting a car's purchase color within the dealership.",
        "dealership/purchase-confirm/dialog": "Explicit yes/no confirmation to buy a "
        "car for a shown price.",
        "dealership/purchase-confirm/insufficient-funds": "Explicitly denied car "
        "purchase because the player "
        "lacks enough funds.",
        "dealership/car-list/unspecified": "Browsing cars for purchase or choosing a "
        "starter car. Use only when its more "
        "specific visible subtype cannot be read.",
        "dealership/car-details/unspecified": "Purchase-focused car specifications, "
        "price, or color preview. Use only when "
        "its more specific visible subtype "
        "cannot be read.",
        "dealership/purchase-confirm/unspecified": "Confirming a car purchase or "
        "insufficient-funds transaction "
        "dialog. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
    },
    "body": {
        "customization/category": "Modification category menu without one specific editable "
        "part active.",
        "customization/body/front-bumper": "Selecting or previewing a front bumper.",
        "customization/body/rear-bumper": "Selecting or previewing a rear bumper.",
        "customization/body/side-skirts": "Selecting or previewing side skirts.",
        "customization/body/hood": "Selecting or previewing a hood or bonnet.",
        "customization/body/spoiler": "Selecting or previewing a rear wing or spoiler.",
        "customization/body/mirrors": "Selecting or previewing exterior mirrors.",
        "customization/body/lights": "Selecting or previewing headlights or taillights.",
        "customization/body/roof": "Selecting or previewing a roof modification.",
        "customization/checkout/items": "Itemized pending modifications with total and "
        "purchase, continue, or remove controls.",
        "customization/checkout/confirm": "Explicit confirmation to purchase the pending "
        "modification cart.",
        "customization/checkout/insufficient-funds": "Explicitly denied modification "
        "purchase due to insufficient cash.",
        "customization/interior/seats": "Selecting or previewing seat replacements as an "
        "editable modification.",
        "customization/interior/steering-wheel": "Selecting or previewing a steering-wheel "
        "replacement.",
        "customization/body/headlights": "Selecting or previewing front lights; distinguish "
        "from rear lights by label or view.",
        "customization/body/taillights": "Selecting or previewing rear lights; distinguish "
        "from front lights by label or view.",
        "customization/body/body-kit/wide": "An explicitly labeled wide-body-kit selector or "
        "preview.",
        "customization/body/body-kit/standard": "A body-kit selector not explicitly marked "
        "wide-body.",
        "customization/body/exhaust/tip": "Selecting an exhaust-tip visual design; not "
        "performance exhaust upgrades.",
        "customization/wheels/rims/design": "Selecting a rim design from alternative wheel "
        "thumbnails or names.",
        "customization/wheels/rims/brand": "Selecting a wheel manufacturer or brand as an "
        "explicit category.",
        "customization/wheels/size/diameter": "An explicit wheel-diameter or rim-size "
        "control is selected.",
        "customization/wheels/color/palette": "Wheel paint selected with color swatches or "
        "color picker visible.",
        "customization/plate/text": "Entering or changing the characters on a license plate.",
        "customization/plate/style": "Choosing the visual style, background, or shape of a "
        "license plate.",
        "customization/checkout/unspecified": "Shopping cart itemizing pending modifications "
        "with total and purchase or remove controls. "
        "Use only when its more specific visible "
        "subtype cannot be read.",
        "customization/interior/unspecified": "Selecting or previewing seats, steering "
        "wheel, or other interior modifications. Use "
        "only when its more specific visible subtype "
        "cannot be read.",
        "customization/body/body-kit/unspecified": "Selecting or previewing a complete body "
        "kit. Use only when its more specific "
        "visible subtype cannot be read.",
        "customization/body/exhaust/unspecified": "Selecting or previewing an exhaust tip. "
        "Use only when its more specific visible "
        "subtype cannot be read.",
        "customization/wheels/rims/unspecified": "Selecting a wheel or rim design. Use only "
        "when its more specific visible subtype "
        "cannot be read.",
        "customization/wheels/size/unspecified": "Editing wheel diameter, tire dimensions, "
        "or wheel geometry. Use only when its more "
        "specific visible subtype cannot be read.",
        "customization/wheels/color/unspecified": "Editing rim or wheel paint color. Use "
        "only when its more specific visible "
        "subtype cannot be read.",
        "customization/plate/unspecified": "Editing the license plate or plate text. Use "
        "only when its more specific visible subtype "
        "cannot be read.",
    },
    "paint_vinyl": {
        "customization/paint/body/palette": "Main body-color swatches or color picker "
        "active; not paint finish selection.",
        "customization/paint/finish/type": "Choosing paint finish or material type "
        "such as visibly labeled gloss, metallic, "
        "or pearl.",
        "customization/paint/part/palette": "An individual body panel's paint color "
        "is explicitly selected.",
        "customization/vinyl/catalog/category": "Choosing a vinyl or decal category "
        "before an individual design.",
        "customization/vinyl/catalog/design": "Selecting an individual decal or vinyl "
        "graphic design.",
        "customization/vinyl/placement/panel": "Choosing the target body panel or "
        "surface for a vinyl.",
        "customization/vinyl/placement/transform": "Active move, rotate, scale, or "
        "placement controls for one vinyl.",
        "customization/vinyl/layers/list": "A decal-layer list or layer index is "
        "active, including an Add Decal entry.",
        "customization/vinyl/layers/options": "Explicit options for a selected layer "
        "such as delete, copy, or order.",
        "customization/vinyl/color/palette": "Color swatches or color picker active "
        "while a vinyl is being edited.",
        "customization/paint/body/unspecified": "Editing the main body paint color or "
        "paint finish. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
        "customization/paint/finish/unspecified": "Choosing a paint type or finish "
        "rather than editing its color. Use "
        "only when its more specific "
        "visible subtype cannot be read.",
        "customization/paint/part/unspecified": "Editing paint on a specific body "
        "component rather than the whole "
        "body. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
        "customization/vinyl/catalog/unspecified": "Browsing vinyl or decal designs "
        "and categories. Use only when its "
        "more specific visible subtype "
        "cannot be read.",
        "customization/vinyl/placement/unspecified": "Moving, rotating, scaling, or "
        "positioning a vinyl on a car. "
        "Use only when its more specific "
        "visible subtype cannot be read.",
        "customization/vinyl/layers/unspecified": "Choosing, ordering, copying, or "
        "removing vinyl layers. Use only "
        "when its more specific visible "
        "subtype cannot be read.",
        "customization/vinyl/color/unspecified": "Editing the color of a vinyl or "
        "decal. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
    },
    "performance": {
        "performance/category/tuning-pack-matrix": "League-by-upgrade matrix for "
        "power, handling, weight, or "
        "nitrous packs.",
        "performance/category/component": "Choosing an individual performance system "
        "or component on a wireframe car.",
        "performance/upgrade/power-pack": "A power upgrade package, tier, or level is "
        "explicitly selected.",
        "performance/upgrade/handling-pack": "A handling upgrade package, tier, or "
        "level is explicitly selected.",
        "performance/upgrade/weight-pack": "A weight-reduction package, tier, or "
        "level is explicitly selected.",
        "performance/upgrade/nitrous-pack": "A nitrous upgrade package, tier, or "
        "level is explicitly selected.",
        "performance/upgrade/component-brand": "Selecting a performance component "
        "brand or named alternative.",
        "performance/upgrade/purchase-confirm": "Explicit confirmation to buy a "
        "performance upgrade or pack.",
        "performance/tuning/weight": "An adjustable weight-reduction or vehicle-mass "
        "control is visible and active.",
        "performance/tuning/power": "An explicit adjustable engine-power or "
        "power-output control is active.",
        "performance/tuning/handling": "An explicit adjustable handling setup control is active.",
        "performance/unlock-challenge/locked-pack": "Locked tuning-pack cell with a "
        "requirement or challenge action "
        "visible.",
        "performance/unlock-challenge/event-details": "Track, target, and challenge "
        "details required to unlock a "
        "selected upgrade.",
        "performance/category/unspecified": "Choosing a performance-upgrade system or "
        "component category. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
        "performance/upgrade/unspecified": "Comparing or purchasing a specific "
        "performance upgrade. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
        "performance/tuning/unspecified": "Adjustable performance tuning sliders or "
        "numerical setup values. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
        "performance/unlock-challenge/unspecified": "Locked upgrade requirement or "
        "challenge event to unlock a "
        "part. Use only when its more "
        "specific visible subtype cannot "
        "be read.",
    },
    "wagering": {
        "betting/opponent-list/driver": "Selecting or inspecting another driver before "
        "initiating a bet.",
        "betting/cash-wager/offer": "Selecting a money offer amount before the opponent "
        "accepts or rejects.",
        "betting/cash-wager/counteroffer": "An explicitly labeled counteroffer or "
        "revised negotiated wager.",
        "betting/cash-wager/accepted": "Explicit bet acceptance or wager agreement confirmation.",
        "betting/cash-wager/rejected": "Explicit refusal, rejection, or canceled cash wager.",
        "betting/pink-slip/warning": "Warning that losing the pink-slip race forfeits "
        "the player's car, with a confirmation choice.",
        "betting/pink-slip/opponent": "Selecting a pink-slip rival or viewing the "
        "rival's wagered car.",
        "betting/spectator/selection": "Selecting a competitor or money amount for a "
        "spectator bet.",
        "betting/opponent-list/unspecified": "Pre-race opponent roster where bets or "
        "challenges can be initiated. Use only when "
        "its more specific visible subtype cannot "
        "be read.",
        "betting/cash-wager/unspecified": "Negotiating, accepting, or adjusting a money "
        "wager. Use only when its more specific "
        "visible subtype cannot be read.",
        "betting/pink-slip/unspecified": "A car-ownership wager explicitly labeled pink "
        "slip or equivalent. Use only when its more "
        "specific visible subtype cannot be read.",
        "betting/spectator/unspecified": "Placing or viewing a bet while spectating "
        "other drivers. Use only when its more specific "
        "visible subtype cannot be read.",
    },
    "race": {
        "race/intro/venue": "Pre-race establishing shot of a venue or track.",
        "race/intro/grid": "Pre-race staged cars, drivers, grid, or starting lineup.",
        "race/intro/cinematic": "An in-game aerial or trackside camera transition before "
        "driving, with no actionable UI.",
        "race/driving/other": "Active player driving whose event subtype cannot be "
        "determined visually.",
        "race/loading/explicit": "An explicit loading label or progress indicator, rather "
        "than an unlabelled transition.",
        "race/intro/venue-name": "Venue name or event title over a pre-race establishing shot.",
        "race/intro/driver-lineup": "Pre-race lineup of drivers and their cars, before "
        "driving controls are active.",
        "race/intro/grid-cars": "Cars staged on the starting grid before the countdown.",
        "race/countdown/number": "A numerical pre-start countdown over the staged cars.",
        "race/countdown/go": "GO or equivalent race-start notification over driving.",
        "race/driving/circuit/lap-race": "Active non-drift race with lap and position HUD; "
        "no more specific mode visibly established.",
        "race/driving/drift/points": "An explicitly labeled drift-points event or drift HUD "
        "with target and accumulated score.",
        "race/driving/drift/chain": "An explicitly labeled chain-drift event or current "
        "CHAIN DRIFT feedback.",
        "race/driving/drift/endurance": "An explicitly labeled drift-endurance event, not "
        "inferred from a long timer.",
        "race/driving/drift/king": "An explicitly labeled Drift King event or mode.",
        "race/driving/time-attack/target": "Active single-target-time challenge with visible "
        "target and elapsed time.",
        "race/driving/elimination/warning": "Active race displaying an explicit elimination "
        "or knockout warning/countdown.",
        "race/driving/spectator/competitor": "Spectator race view with explicit viewing or "
        "betting indicators.",
        "race/pause/menu": "Paused driving with resume, restart, quit, or options menu visible.",
        "race/pause/restart-confirm": "Explicit confirmation to restart the current race.",
        "race/pause/quit-confirm": "Explicit confirmation to abandon or quit the current event.",
        "race/pause/controller-disconnected": "Explicit controller reconnect/disconnected "
        "prompt interrupts the race.",
        "race/finish-overlay/victory": "Explicit victory, winner, or first-place "
        "announcement over the race.",
        "race/finish-overlay/defeat": "Explicit defeat, loss, or failed event announcement "
        "over the race.",
        "race/finish-overlay/disqualified": "Explicit disqualification or race invalidation "
        "announcement.",
        "race/loading/unspecified": "Loading screen or explicit loading indicator between "
        "game states. Use only when its more specific visible "
        "subtype cannot be read.",
        "race/countdown/unspecified": "Starting countdown or GO prompt over the staged race. "
        "Use only when its more specific visible subtype "
        "cannot be read.",
        "race/driving/circuit/unspecified": "Active race driving with laps or position, "
        "without a primary drift score. Use only when "
        "its more specific visible subtype cannot be "
        "read.",
        "race/driving/drift/unspecified": "Active driving with a drift score, drift chain, "
        "or drift event HUD. Use only when its more "
        "specific visible subtype cannot be read.",
        "race/driving/time-attack/unspecified": "Active driving with an explicitly visible "
        "time-attack goal or timer mode. Use only "
        "when its more specific visible subtype "
        "cannot be read.",
        "race/driving/elimination/unspecified": "Active driving with an explicitly visible "
        "elimination mechanic. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
        "race/driving/spectator/unspecified": "Watching another driver's ongoing race with "
        "spectator controls or labeling. Use only when "
        "its more specific visible subtype cannot be "
        "read.",
        "race/pause/unspecified": "Paused race menu over a race or track background. Use "
        "only when its more specific visible subtype cannot be "
        "read.",
        "race/finish-overlay/unspecified": "Finish, win, lose, disqualification, or "
        "race-over announcement over driving. Use only "
        "when its more specific visible subtype cannot be "
        "read.",
    },
    "results": {
        "results/standings/circuit": "Finishing order with driver positions and race times.",
        "results/standings/drift": "Finishing order with driver drift scores.",
        "results/standings/tournament": "Tournament or championship cumulative points or "
        "round standings.",
        "results/challenge/time": "Challenge results compare a target time with achieved time.",
        "results/challenge/score": "Challenge results compare a target score with "
        "achieved score or points wasted.",
        "results/challenge/unlock": "Challenge result explicitly announces that a tuning "
        "pack or other item was unlocked.",
        "results/payout/race-prize": "Post-event prize or race winnings breakdown without "
        "a specific wager transfer as the main focus.",
        "results/payout/cash-bet": "Explicit post-race cash-wager settlement.",
        "results/payout/pink-slip-won": "Explicit acquisition or ownership transfer of a "
        "car won in a pink-slip race.",
        "results/payout/pink-slip-lost": "Explicit loss or transfer away of a car "
        "following a pink-slip defeat.",
        "results/podium/celebration": "Post-race drivers celebrating on a numbered podium.",
        "results/standings/unspecified": "Post-event finishing order, times, scores, or "
        "position table. Use only when its more specific "
        "visible subtype cannot be read.",
        "results/challenge/unspecified": "Challenge result comparing target and achieved "
        "score or time, including package unlock. Use "
        "only when its more specific visible subtype "
        "cannot be read.",
        "results/payout/unspecified": "Post-event prize, winnings, wager settlement, or "
        "money summary. Use only when its more specific "
        "visible subtype cannot be read.",
        "results/podium/unspecified": "Post-race podium or driver/car celebration scene. "
        "Use only when its more specific visible subtype "
        "cannot be read.",
    },
    "replay": {
        "replay/playback/controls": "Replay view with visible continue, next-car, restart, "
        "or playback controls.",
        "replay/playback/camera": "Replay or replay-camera view with an explicit replay "
        "label but controls hidden.",
        "replay/playback/unspecified": "Race replay camera view with replay labeling or "
        "playback controls. Use only when its more specific "
        "visible subtype cannot be read.",
    },
    "options": {
        "options/controls/bindings": "List of assignable keyboard or gamepad action bindings.",
        "options/controls/transmission": "An explicit manual/automatic transmission "
        "setting is selected.",
        "options/controls/device": "Choosing controller, keyboard, or another input device.",
        "options/audio/volumes": "Music, effects, speech, or other audio volume controls.",
        "options/audio/music": "Selecting music tracks, playlists, or soundtrack playback options.",
        "options/video/display": "Resolution, fullscreen, aspect ratio, or display settings.",
        "options/video/quality": "Graphics-quality or rendering feature controls.",
        "options/gameplay/difficulty": "An explicit difficulty or AI challenge setting is "
        "selected.",
        "options/gameplay/assists": "Driving assists or driving-aid toggles are shown.",
        "options/other/language": "Explicit interface language or localization selection.",
        "options/controls/unspecified": "Control mapping, controller, steering, or input "
        "settings. Use only when its more specific "
        "visible subtype cannot be read.",
        "options/audio/unspecified": "Music, effects, speech, or audio volume settings. "
        "Use only when its more specific visible subtype "
        "cannot be read.",
        "options/video/unspecified": "Display resolution, graphics quality, or rendering "
        "settings. Use only when its more specific visible "
        "subtype cannot be read.",
        "options/gameplay/unspecified": "Difficulty, driving aids, transmission, or "
        "gameplay settings. Use only when its more "
        "specific visible subtype cannot be read.",
        "options/other/unspecified": "Options menu whose settings subtype is not "
        "readable. Use only when its more specific visible "
        "subtype cannot be read.",
    },
    "multiplayer": {
        "multiplayer/lobby/browser": "Browse available online races, servers, or sessions.",
        "multiplayer/lobby/player-list": "Multiplayer room roster or ready-up screen.",
        "multiplayer/lobby/create": "Creating a multiplayer event and choosing its settings.",
        "multiplayer/lobby/connection": "Explicit network connection, sign-in, or "
        "disconnect status.",
        "multiplayer/split-screen/driving": "Simultaneous local-player driving viewports.",
        "multiplayer/lobby/unspecified": "Online or local multiplayer lobby, session "
        "list, or player roster. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
        "multiplayer/split-screen/unspecified": "Two or more simultaneous player "
        "viewports. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
    },
    "presentation": {
        "presentation/credits": "Game credits or staff roll.",
        "presentation/cutscene/host": "In-game race host or presenter is the central "
        "focus without an actionable menu.",
        "presentation/cutscene/driver": "In-game driver introduction or avatar "
        "animation without an actionable menu.",
        "presentation/cutscene/car": "Cinematic car showcase without actionable "
        "modification or shopping controls.",
        "presentation/cutscene/unspecified": "Story, host, nightclub, or promotional "
        "cinematic without an actionable menu. "
        "Use only when its more specific "
        "visible subtype cannot be read.",
    },
    "reference": {
        "reference/creator-overlay/title-card": "Uploader title card or edited "
        "explanatory graphic dominates the "
        "image.",
        "reference/creator-overlay/emulator-controls": "Emulator touch controls overlay "
        "an otherwise visible game "
        "scene.",
        "reference/creator-overlay/webcam": "Webcam or streamer camera obscures a "
        "substantial part of the game scene.",
        "reference/unreadable/black": "All or nearly all the image is black with no "
        "readable game state.",
        "reference/unreadable/transition": "Blurred, overexposed, or partial scene "
        "transition prevents identifying the current "
        "state.",
        "reference/creator-overlay/unspecified": "Uploader title card, webcam, video "
        "editor, or non-game presentation "
        "dominates. Use only when its more "
        "specific visible subtype cannot be "
        "read.",
        "reference/unreadable/unspecified": "Black, obstructed, blurred, transitional, "
        "or unidentifiable image. Use only when its "
        "more specific visible subtype cannot be "
        "read.",
    },
}

SCREEN_STATES = {
    "boot/title": "Title logo or press-start screen before the main menu.",
    "boot/legal": "Publisher, developer, legal, or startup logo splash.",
    "menu/main": "Top-level menu choosing career, race, options, or other major modes.",
    "character/preset": "Choosing a driver avatar or character preset.",
    "career/hub": "Career overview with navigation to garage, leagues, or other career areas.",
    "garage/car-showcase": "Car displayed on a showroom turntable without an active editing or "
    "shopping interface.",
    "career/dna-challenges": "Driver DNA discipline list such as circuit, overtake, nitrous, "
    "spooking, or betting.",
    "customization/category": "Modification category menu without one specific editable part "
    "active.",
    "customization/body/front-bumper": "Selecting or previewing a front bumper.",
    "customization/body/rear-bumper": "Selecting or previewing a rear bumper.",
    "customization/body/side-skirts": "Selecting or previewing side skirts.",
    "customization/body/hood": "Selecting or previewing a hood or bonnet.",
    "customization/body/spoiler": "Selecting or previewing a rear wing or spoiler.",
    "customization/body/mirrors": "Selecting or previewing exterior mirrors.",
    "customization/body/lights": "Selecting or previewing headlights or taillights.",
    "customization/body/roof": "Selecting or previewing a roof modification.",
    "race/intro/venue": "Pre-race establishing shot of a venue or track.",
    "race/intro/grid": "Pre-race staged cars, drivers, grid, or starting lineup.",
    "race/intro/cinematic": "An in-game aerial or trackside camera transition before driving, "
    "with no actionable UI.",
    "race/driving/other": "Active player driving whose event subtype cannot be determined "
    "visually.",
    "presentation/credits": "Game credits or staff roll.",
    "boot/controller-prompt": "Startup prompt requesting a controller, storage device, or sign-in "
    "before the main menu.",
    "menu/profile/create": "Creating or naming a save profile; distinguish from editing the "
    "in-game driver avatar.",
    "menu/profile/select": "Selecting an existing save profile or save slot.",
    "menu/profile/save": "Explicit saving, save success, or save overwrite interface.",
    "menu/profile/delete": "Explicit deletion or overwrite confirmation for a saved profile.",
    "menu/mode/quick-race": "Choosing quick race, arcade race, or free race outside career.",
    "menu/mode/celebrity": "Selecting an explicitly named celebrity race or celebrity challenge "
    "mode.",
    "menu/transition/animation": "Game menu animation between selections with no readable active "
    "choice.",
    "character/face/head-shape": "Editing overall head or face shape; readable selected field "
    "identifies that region.",
    "character/face/eyes-brows": "Editing eye or eyebrow shape, position, width, or depth; "
    "selected field must be readable.",
    "character/face/nose": "Editing the nose; selected nose field must be readable.",
    "character/face/mouth-jaw": "Editing mouth, lips, jaw, or chin; selected field must be "
    "readable.",
    "character/face/skin": "Selecting skin tone or complexion; do not infer this from the "
    "avatar's appearance alone.",
    "character/face/hair": "Selecting hair style or hair color; an actionable hair choice must be "
    "visible.",
    "character/face/facial-hair": "Selecting facial-hair style or color; an actionable choice "
    "must be visible.",
    "character/clothing/headwear": "Selecting a hat, cap, or other headwear; actionable choice "
    "must be visible.",
    "character/clothing/top": "Selecting a shirt, jacket, or upper-body garment; actionable "
    "choice must be visible.",
    "character/clothing/bottom": "Selecting trousers, skirt, or lower-body clothing; actionable "
    "choice must be visible.",
    "character/clothing/shoes": "Selecting shoes or footwear; actionable choice must be visible.",
    "character/clothing/color": "Choosing the color of the selected garment rather than its "
    "design.",
    "character/identity/name": "On-screen entry or editing of the player's driver name.",
    "career/leagues/select": "Selecting an available league or tier in the league ladder.",
    "career/leagues/locked": "Inspecting an explicitly locked league with its unmet requirements "
    "visible.",
    "career/goals/checklist": "A league-goal list with checked and unchecked completion "
    "indicators.",
    "career/goals/detail": "One selected career goal's detailed condition or description.",
    "career/event-list/circuit": "An event-selection screen explicitly showing a circuit race or "
    "circuit category.",
    "career/event-list/drift": "An event-selection screen explicitly showing a drift event or "
    "drift category.",
    "career/event-list/tournament": "Selecting an explicitly labeled championship or multi-round "
    "tournament.",
    "career/event-details/requirements": "A selected event's eligibility, required car class, or "
    "entry requirement is the active information.",
    "career/event-details/track": "A selected event's course layout, venue, route length, or laps "
    "are the active information.",
    "career/event-details/rewards": "A selected event's entry fee or prize information is the "
    "active information.",
    "career/promotion/announcement": "Explicit promotion or newly reached league announcement.",
    "career/reward/visual-unlock": "Explicit visual-modification or decal unlock award.",
    "career/reward/prototype-unlock": "Explicit prototype or performance-unlock award.",
    "career/dna-profile/helix": "Driver DNA displayed as a helix with named driving disciplines; "
    "no opponent-selection list active.",
    "career/dna-profile/statistics": "Driver DNA shown as numerical statistics, bars, or a "
    "profile summary rather than a helix.",
    "career/dna-opponents/download": "Explicit selection or download of another driver's DNA.",
    "career/dna-opponents/challenge": "Selecting an explicitly labeled DNA challenge against "
    "another driver.",
    "crew/selection/roster": "Choosing from a list of potential or current crew members.",
    "crew/selection/hire": "A selected crew member with an explicit Hire action or fee.",
    "crew/selection/dna": "A selected crew member's DNA profile or driving-style display.",
    "crew/management/lineup": "Assigning or replacing crew members in the active racing lineup.",
    "crew/management/race-role": "Explicitly assigning a crew member's race role or instruction.",
    "garage/overview/modification-navigation": "Owned-car garage menu with visual or performance "
    "modification category navigation.",
    "garage/owned-cars/list": "Choosing among owned cars, with no car-purchase price as the main "
    "action.",
    "garage/owned-cars/details": "Inspecting specifications or eligibility for a car already "
    "owned.",
    "garage/pink-slip-record/history": "Pink-slip document where ownership or transaction history "
    "is the prominent information.",
    "garage/pink-slip-record/statistics": "Pink-slip document where race count, wins, winnings, "
    "or spent amounts are prominent.",
    "garage/sell-confirm/offer": "Selected owned car with its sale value and explicit sell action.",
    "garage/sell-confirm/dialog": "An explicit yes/no confirmation to sell the owned car.",
    "dealership/car-list/manufacturer": "Choosing a manufacturer or make before selecting a car "
    "model.",
    "dealership/car-list/model": "Browsing purchasable car models within a manufacturer or "
    "eligible league.",
    "dealership/car-details/specifications": "Purchase-focused car preview with technical "
    "specifications or class eligibility.",
    "dealership/car-details/color": "Selecting a car's purchase color within the dealership.",
    "dealership/purchase-confirm/dialog": "Explicit yes/no confirmation to buy a car for a shown "
    "price.",
    "dealership/purchase-confirm/insufficient-funds": "Explicitly denied car purchase because the "
    "player lacks enough funds.",
    "customization/checkout/items": "Itemized pending modifications with total and purchase, "
    "continue, or remove controls.",
    "customization/checkout/confirm": "Explicit confirmation to purchase the pending modification "
    "cart.",
    "customization/checkout/insufficient-funds": "Explicitly denied modification purchase due to "
    "insufficient cash.",
    "customization/interior/seats": "Selecting or previewing seat replacements as an editable "
    "modification.",
    "customization/interior/steering-wheel": "Selecting or previewing a steering-wheel "
    "replacement.",
    "customization/body/headlights": "Selecting or previewing front lights; distinguish from rear "
    "lights by label or view.",
    "customization/body/taillights": "Selecting or previewing rear lights; distinguish from front "
    "lights by label or view.",
    "customization/body/body-kit/wide": "An explicitly labeled wide-body-kit selector or preview.",
    "customization/body/body-kit/standard": "A body-kit selector not explicitly marked wide-body.",
    "customization/body/exhaust/tip": "Selecting an exhaust-tip visual design; not performance "
    "exhaust upgrades.",
    "customization/wheels/rims/design": "Selecting a rim design from alternative wheel thumbnails "
    "or names.",
    "customization/wheels/rims/brand": "Selecting a wheel manufacturer or brand as an explicit "
    "category.",
    "customization/wheels/size/diameter": "An explicit wheel-diameter or rim-size control is "
    "selected.",
    "customization/wheels/color/palette": "Wheel paint selected with color swatches or color "
    "picker visible.",
    "customization/paint/body/palette": "Main body-color swatches or color picker active; not "
    "paint finish selection.",
    "customization/paint/finish/type": "Choosing paint finish or material type such as visibly "
    "labeled gloss, metallic, or pearl.",
    "customization/paint/part/palette": "An individual body panel's paint color is explicitly "
    "selected.",
    "customization/vinyl/catalog/category": "Choosing a vinyl or decal category before an "
    "individual design.",
    "customization/vinyl/catalog/design": "Selecting an individual decal or vinyl graphic design.",
    "customization/vinyl/placement/panel": "Choosing the target body panel or surface for a vinyl.",
    "customization/vinyl/placement/transform": "Active move, rotate, scale, or placement controls "
    "for one vinyl.",
    "customization/vinyl/layers/list": "A decal-layer list or layer index is active, including an "
    "Add Decal entry.",
    "customization/vinyl/layers/options": "Explicit options for a selected layer such as delete, "
    "copy, or order.",
    "customization/vinyl/color/palette": "Color swatches or color picker active while a vinyl is "
    "being edited.",
    "customization/plate/text": "Entering or changing the characters on a license plate.",
    "customization/plate/style": "Choosing the visual style, background, or shape of a license "
    "plate.",
    "performance/category/tuning-pack-matrix": "League-by-upgrade matrix for power, handling, "
    "weight, or nitrous packs.",
    "performance/category/component": "Choosing an individual performance system or component on "
    "a wireframe car.",
    "performance/upgrade/power-pack": "A power upgrade package, tier, or level is explicitly "
    "selected.",
    "performance/upgrade/handling-pack": "A handling upgrade package, tier, or level is "
    "explicitly selected.",
    "performance/upgrade/weight-pack": "A weight-reduction package, tier, or level is explicitly "
    "selected.",
    "performance/upgrade/nitrous-pack": "A nitrous upgrade package, tier, or level is explicitly "
    "selected.",
    "performance/upgrade/component-brand": "Selecting a performance component brand or named "
    "alternative.",
    "performance/upgrade/purchase-confirm": "Explicit confirmation to buy a performance upgrade "
    "or pack.",
    "performance/tuning/weight": "An adjustable weight-reduction or vehicle-mass control is "
    "visible and active.",
    "performance/tuning/power": "An explicit adjustable engine-power or power-output control is "
    "active.",
    "performance/tuning/handling": "An explicit adjustable handling setup control is active.",
    "performance/unlock-challenge/locked-pack": "Locked tuning-pack cell with a requirement or "
    "challenge action visible.",
    "performance/unlock-challenge/event-details": "Track, target, and challenge details required "
    "to unlock a selected upgrade.",
    "betting/opponent-list/driver": "Selecting or inspecting another driver before initiating a "
    "bet.",
    "betting/cash-wager/offer": "Selecting a money offer amount before the opponent accepts or "
    "rejects.",
    "betting/cash-wager/counteroffer": "An explicitly labeled counteroffer or revised negotiated "
    "wager.",
    "betting/cash-wager/accepted": "Explicit bet acceptance or wager agreement confirmation.",
    "betting/cash-wager/rejected": "Explicit refusal, rejection, or canceled cash wager.",
    "betting/pink-slip/warning": "Warning that losing the pink-slip race forfeits the player's "
    "car, with a confirmation choice.",
    "betting/pink-slip/opponent": "Selecting a pink-slip rival or viewing the rival's wagered car.",
    "betting/spectator/selection": "Selecting a competitor or money amount for a spectator bet.",
    "race/loading/explicit": "An explicit loading label or progress indicator, rather than an "
    "unlabelled transition.",
    "race/intro/venue-name": "Venue name or event title over a pre-race establishing shot.",
    "race/intro/driver-lineup": "Pre-race lineup of drivers and their cars, before driving "
    "controls are active.",
    "race/intro/grid-cars": "Cars staged on the starting grid before the countdown.",
    "race/countdown/number": "A numerical pre-start countdown over the staged cars.",
    "race/countdown/go": "GO or equivalent race-start notification over driving.",
    "race/driving/circuit/lap-race": "Active non-drift race with lap and position HUD; no more "
    "specific mode visibly established.",
    "race/driving/drift/points": "An explicitly labeled drift-points event or drift HUD with "
    "target and accumulated score.",
    "race/driving/drift/chain": "An explicitly labeled chain-drift event or current CHAIN DRIFT "
    "feedback.",
    "race/driving/drift/endurance": "An explicitly labeled drift-endurance event, not inferred "
    "from a long timer.",
    "race/driving/drift/king": "An explicitly labeled Drift King event or mode.",
    "race/driving/time-attack/target": "Active single-target-time challenge with visible target "
    "and elapsed time.",
    "race/driving/elimination/warning": "Active race displaying an explicit elimination or "
    "knockout warning/countdown.",
    "race/driving/spectator/competitor": "Spectator race view with explicit viewing or betting "
    "indicators.",
    "race/pause/menu": "Paused driving with resume, restart, quit, or options menu visible.",
    "race/pause/restart-confirm": "Explicit confirmation to restart the current race.",
    "race/pause/quit-confirm": "Explicit confirmation to abandon or quit the current event.",
    "race/pause/controller-disconnected": "Explicit controller reconnect/disconnected prompt "
    "interrupts the race.",
    "race/finish-overlay/victory": "Explicit victory, winner, or first-place announcement over "
    "the race.",
    "race/finish-overlay/defeat": "Explicit defeat, loss, or failed event announcement over the "
    "race.",
    "race/finish-overlay/disqualified": "Explicit disqualification or race invalidation "
    "announcement.",
    "results/standings/circuit": "Finishing order with driver positions and race times.",
    "results/standings/drift": "Finishing order with driver drift scores.",
    "results/standings/tournament": "Tournament or championship cumulative points or round "
    "standings.",
    "results/challenge/time": "Challenge results compare a target time with achieved time.",
    "results/challenge/score": "Challenge results compare a target score with achieved score or "
    "points wasted.",
    "results/challenge/unlock": "Challenge result explicitly announces that a tuning pack or "
    "other item was unlocked.",
    "results/payout/race-prize": "Post-event prize or race winnings breakdown without a specific "
    "wager transfer as the main focus.",
    "results/payout/cash-bet": "Explicit post-race cash-wager settlement.",
    "results/payout/pink-slip-won": "Explicit acquisition or ownership transfer of a car won in a "
    "pink-slip race.",
    "results/payout/pink-slip-lost": "Explicit loss or transfer away of a car following a "
    "pink-slip defeat.",
    "results/podium/celebration": "Post-race drivers celebrating on a numbered podium.",
    "replay/playback/controls": "Replay view with visible continue, next-car, restart, or "
    "playback controls.",
    "replay/playback/camera": "Replay or replay-camera view with an explicit replay label but "
    "controls hidden.",
    "options/controls/bindings": "List of assignable keyboard or gamepad action bindings.",
    "options/controls/transmission": "An explicit manual/automatic transmission setting is "
    "selected.",
    "options/controls/device": "Choosing controller, keyboard, or another input device.",
    "options/audio/volumes": "Music, effects, speech, or other audio volume controls.",
    "options/audio/music": "Selecting music tracks, playlists, or soundtrack playback options.",
    "options/video/display": "Resolution, fullscreen, aspect ratio, or display settings.",
    "options/video/quality": "Graphics-quality or rendering feature controls.",
    "options/gameplay/difficulty": "An explicit difficulty or AI challenge setting is selected.",
    "options/gameplay/assists": "Driving assists or driving-aid toggles are shown.",
    "options/other/language": "Explicit interface language or localization selection.",
    "multiplayer/lobby/browser": "Browse available online races, servers, or sessions.",
    "multiplayer/lobby/player-list": "Multiplayer room roster or ready-up screen.",
    "multiplayer/lobby/create": "Creating a multiplayer event and choosing its settings.",
    "multiplayer/lobby/connection": "Explicit network connection, sign-in, or disconnect status.",
    "multiplayer/split-screen/driving": "Simultaneous local-player driving viewports.",
    "presentation/cutscene/host": "In-game race host or presenter is the central focus without an "
    "actionable menu.",
    "presentation/cutscene/driver": "In-game driver introduction or avatar animation without an "
    "actionable menu.",
    "presentation/cutscene/car": "Cinematic car showcase without actionable modification or "
    "shopping controls.",
    "reference/creator-overlay/title-card": "Uploader title card or edited explanatory graphic "
    "dominates the image.",
    "reference/creator-overlay/emulator-controls": "Emulator touch controls overlay an otherwise "
    "visible game scene.",
    "reference/creator-overlay/webcam": "Webcam or streamer camera obscures a substantial part of "
    "the game scene.",
    "reference/unreadable/black": "All or nearly all the image is black with no readable game "
    "state.",
    "reference/unreadable/transition": "Blurred, overexposed, or partial scene transition "
    "prevents identifying the current state.",
    "menu/profile/unspecified": "Profile or save-slot selection, creation, loading, or save "
    "confirmation. Use only when its more specific visible subtype "
    "cannot be read.",
    "menu/mode/unspecified": "Race-mode selection outside a career event list. Use only when its "
    "more specific visible subtype cannot be read.",
    "character/face/unspecified": "Editing face, head, skin, hair, or facial features. Use only "
    "when its more specific visible subtype cannot be read.",
    "character/clothing/unspecified": "Editing driver clothing, accessories, or outfit colors. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "character/identity/unspecified": "Entering or confirming driver name, gender, or identity. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "career/leagues/unspecified": "League ladder or selection showing progression tiers. Use only "
    "when its more specific visible subtype cannot be read.",
    "career/goals/unspecified": "League goals, achievements, or promotion requirements list. Use "
    "only when its more specific visible subtype cannot be read.",
    "career/event-list/unspecified": "Choosing an event from a career event list or map. Use only "
    "when its more specific visible subtype cannot be read.",
    "career/event-details/unspecified": "Selected event rules, entry requirements, prize, or "
    "track preview. Use only when its more specific visible "
    "subtype cannot be read.",
    "career/promotion/unspecified": "League promotion, newly unlocked league, or career milestone "
    "announcement. Use only when its more specific visible "
    "subtype cannot be read.",
    "career/reward/unspecified": "Reward, unlock, achievement, or bonus announcement outside "
    "results tables. Use only when its more specific visible subtype "
    "cannot be read.",
    "career/dna-profile/unspecified": "Driver DNA profile or driving-style statistics overview. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "career/dna-opponents/unspecified": "DNA opponent selection, download, or challenge list. Use "
    "only when its more specific visible subtype cannot be "
    "read.",
    "crew/selection/unspecified": "Selecting, recruiting, or inspecting a crew member. Use only "
    "when its more specific visible subtype cannot be read.",
    "crew/management/unspecified": "Crew management or teammate instructions menu. Use only when "
    "its more specific visible subtype cannot be read.",
    "garage/overview/unspecified": "Garage car overview with navigation among modification "
    "functions. Use only when its more specific visible subtype "
    "cannot be read.",
    "garage/owned-cars/unspecified": "Choosing among cars already owned, without a purchase "
    "transaction. Use only when its more specific visible "
    "subtype cannot be read.",
    "garage/pink-slip-record/unspecified": "Pink-slip ownership document with owner, value, "
    "races, or history; not placing a wager. Use only when "
    "its more specific visible subtype cannot be read.",
    "dealership/car-list/unspecified": "Browsing cars for purchase or choosing a starter car. Use "
    "only when its more specific visible subtype cannot be "
    "read.",
    "dealership/car-details/unspecified": "Purchase-focused car specifications, price, or color "
    "preview. Use only when its more specific visible "
    "subtype cannot be read.",
    "dealership/purchase-confirm/unspecified": "Confirming a car purchase or insufficient-funds "
    "transaction dialog. Use only when its more "
    "specific visible subtype cannot be read.",
    "garage/sell-confirm/unspecified": "Confirming sale of an owned car or displaying its sale "
    "value. Use only when its more specific visible subtype "
    "cannot be read.",
    "customization/checkout/unspecified": "Shopping cart itemizing pending modifications with "
    "total and purchase or remove controls. Use only when "
    "its more specific visible subtype cannot be read.",
    "customization/interior/unspecified": "Selecting or previewing seats, steering wheel, or "
    "other interior modifications. Use only when its more "
    "specific visible subtype cannot be read.",
    "customization/body/body-kit/unspecified": "Selecting or previewing a complete body kit. Use "
    "only when its more specific visible subtype "
    "cannot be read.",
    "customization/body/exhaust/unspecified": "Selecting or previewing an exhaust tip. Use only "
    "when its more specific visible subtype cannot be "
    "read.",
    "customization/wheels/rims/unspecified": "Selecting a wheel or rim design. Use only when its "
    "more specific visible subtype cannot be read.",
    "customization/wheels/size/unspecified": "Editing wheel diameter, tire dimensions, or wheel "
    "geometry. Use only when its more specific visible "
    "subtype cannot be read.",
    "customization/wheels/color/unspecified": "Editing rim or wheel paint color. Use only when "
    "its more specific visible subtype cannot be read.",
    "customization/paint/body/unspecified": "Editing the main body paint color or paint finish. "
    "Use only when its more specific visible subtype "
    "cannot be read.",
    "customization/paint/finish/unspecified": "Choosing a paint type or finish rather than "
    "editing its color. Use only when its more specific "
    "visible subtype cannot be read.",
    "customization/paint/part/unspecified": "Editing paint on a specific body component rather "
    "than the whole body. Use only when its more specific "
    "visible subtype cannot be read.",
    "customization/vinyl/catalog/unspecified": "Browsing vinyl or decal designs and categories. "
    "Use only when its more specific visible subtype "
    "cannot be read.",
    "customization/vinyl/placement/unspecified": "Moving, rotating, scaling, or positioning a "
    "vinyl on a car. Use only when its more specific "
    "visible subtype cannot be read.",
    "customization/vinyl/layers/unspecified": "Choosing, ordering, copying, or removing vinyl "
    "layers. Use only when its more specific visible "
    "subtype cannot be read.",
    "customization/vinyl/color/unspecified": "Editing the color of a vinyl or decal. Use only "
    "when its more specific visible subtype cannot be "
    "read.",
    "customization/plate/unspecified": "Editing the license plate or plate text. Use only when "
    "its more specific visible subtype cannot be read.",
    "performance/category/unspecified": "Choosing a performance-upgrade system or component "
    "category. Use only when its more specific visible "
    "subtype cannot be read.",
    "performance/upgrade/unspecified": "Comparing or purchasing a specific performance upgrade. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "performance/tuning/unspecified": "Adjustable performance tuning sliders or numerical setup "
    "values. Use only when its more specific visible subtype "
    "cannot be read.",
    "performance/unlock-challenge/unspecified": "Locked upgrade requirement or challenge event to "
    "unlock a part. Use only when its more specific "
    "visible subtype cannot be read.",
    "betting/opponent-list/unspecified": "Pre-race opponent roster where bets or challenges can "
    "be initiated. Use only when its more specific visible "
    "subtype cannot be read.",
    "betting/cash-wager/unspecified": "Negotiating, accepting, or adjusting a money wager. Use "
    "only when its more specific visible subtype cannot be "
    "read.",
    "betting/pink-slip/unspecified": "A car-ownership wager explicitly labeled pink slip or "
    "equivalent. Use only when its more specific visible subtype "
    "cannot be read.",
    "betting/spectator/unspecified": "Placing or viewing a bet while spectating other drivers. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "race/loading/unspecified": "Loading screen or explicit loading indicator between game "
    "states. Use only when its more specific visible subtype cannot "
    "be read.",
    "race/countdown/unspecified": "Starting countdown or GO prompt over the staged race. Use only "
    "when its more specific visible subtype cannot be read.",
    "race/driving/circuit/unspecified": "Active race driving with laps or position, without a "
    "primary drift score. Use only when its more specific "
    "visible subtype cannot be read.",
    "race/driving/drift/unspecified": "Active driving with a drift score, drift chain, or drift "
    "event HUD. Use only when its more specific visible subtype "
    "cannot be read.",
    "race/driving/time-attack/unspecified": "Active driving with an explicitly visible "
    "time-attack goal or timer mode. Use only when its "
    "more specific visible subtype cannot be read.",
    "race/driving/elimination/unspecified": "Active driving with an explicitly visible "
    "elimination mechanic. Use only when its more "
    "specific visible subtype cannot be read.",
    "race/driving/spectator/unspecified": "Watching another driver's ongoing race with spectator "
    "controls or labeling. Use only when its more specific "
    "visible subtype cannot be read.",
    "race/pause/unspecified": "Paused race menu over a race or track background. Use only when "
    "its more specific visible subtype cannot be read.",
    "race/finish-overlay/unspecified": "Finish, win, lose, disqualification, or race-over "
    "announcement over driving. Use only when its more "
    "specific visible subtype cannot be read.",
    "results/standings/unspecified": "Post-event finishing order, times, scores, or position "
    "table. Use only when its more specific visible subtype "
    "cannot be read.",
    "results/challenge/unspecified": "Challenge result comparing target and achieved score or "
    "time, including package unlock. Use only when its more "
    "specific visible subtype cannot be read.",
    "results/payout/unspecified": "Post-event prize, winnings, wager settlement, or money "
    "summary. Use only when its more specific visible subtype "
    "cannot be read.",
    "results/podium/unspecified": "Post-race podium or driver/car celebration scene. Use only "
    "when its more specific visible subtype cannot be read.",
    "replay/playback/unspecified": "Race replay camera view with replay labeling or playback "
    "controls. Use only when its more specific visible subtype "
    "cannot be read.",
    "options/controls/unspecified": "Control mapping, controller, steering, or input settings. "
    "Use only when its more specific visible subtype cannot be "
    "read.",
    "options/audio/unspecified": "Music, effects, speech, or audio volume settings. Use only when "
    "its more specific visible subtype cannot be read.",
    "options/video/unspecified": "Display resolution, graphics quality, or rendering settings. "
    "Use only when its more specific visible subtype cannot be read.",
    "options/gameplay/unspecified": "Difficulty, driving aids, transmission, or gameplay "
    "settings. Use only when its more specific visible subtype "
    "cannot be read.",
    "options/other/unspecified": "Options menu whose settings subtype is not readable. Use only "
    "when its more specific visible subtype cannot be read.",
    "multiplayer/lobby/unspecified": "Online or local multiplayer lobby, session list, or player "
    "roster. Use only when its more specific visible subtype "
    "cannot be read.",
    "multiplayer/split-screen/unspecified": "Two or more simultaneous player viewports. Use only "
    "when its more specific visible subtype cannot be "
    "read.",
    "presentation/cutscene/unspecified": "Story, host, nightclub, or promotional cinematic "
    "without an actionable menu. Use only when its more "
    "specific visible subtype cannot be read.",
    "reference/creator-overlay/unspecified": "Uploader title card, webcam, video editor, or "
    "non-game presentation dominates. Use only when its "
    "more specific visible subtype cannot be read.",
    "reference/unreadable/unspecified": "Black, obstructed, blurred, transitional, or "
    "unidentifiable image. Use only when its more specific "
    "visible subtype cannot be read.",
    "menu/transition/unspecified": "An animated game menu background or icon transition with no "
    "readable active menu yet. Use only when its more specific "
    "visible subtype cannot be read.",
}

COMMON_TAGS = {
    "menu/selected-row": "Is a highlighted selected menu row or tile visible?",
    "menu/locked-item": "Is an explicitly locked item or padlock visible?",
    "menu/confirm-dialog": "Is a confirmation dialog with accept or cancel choices visible?",
    "menu/price": "Is a price for a car, part, or modification visible?",
    "menu/modification-cart": "Is an itemized cart of pending car modifications visible?",
    "menu/cart-total": "Is the total price of pending car modifications visible?",
    "menu/cash-balance": "Is the player's available cash balance visible?",
    "menu/performance-bars": "Are vehicle performance comparison bars visible?",
    "menu/car-specifications": "Are numerical vehicle specifications visible?",
    "menu/car-class": "Is an explicit car class or league eligibility label visible?",
    "menu/car-name": "Is the car's make or model name displayed in the interface?",
    "menu/part-thumbnails": "Are selectable car-part thumbnails visible?",
    "menu/color-swatches": "Are selectable color swatches visible?",
    "menu/color-sliders": "Are color adjustment sliders or a color picker visible?",
    "menu/tuning-slider": "Is an adjustable performance tuning slider visible?",
    "menu/before-after-stats": "Are old and new performance values visibly compared?",
    "menu/upgrade-tier": "Are performance upgrade tiers or stages visible?",
    "menu/unlock-requirement": "Is text stating a requirement to unlock a car or part visible?",
    "presentation/host": "Is a human race host or presenter a prominent part of the screen?",
    "presentation/avatar": "Is a customizable driver avatar prominently displayed?",
    "presentation/replay-controls": "Are replay playback controls visible?",
    "reference/uploader-overlay": "Is an uploader watermark, webcam, subtitle, or external "
    "overlay visible?",
    "reference/letterbox": "Are substantial black bars around the game image visible?",
    "reference/low-readability": "Is game interface text too small or blurred to read reliably?",
    "menu/left-right-carousel": "Are left/right arrows for cycling selectable items visible?",
    "menu/category-icons": "Is a row or ring of selectable category icons visible?",
    "menu/item-index": "Is an item count or current-index/total-items display visible?",
    "menu/tabs": "Are selectable menu tabs visible?",
    "menu/scrollbar": "Is a scrollbar or scroll-position indicator visible?",
    "menu/yes-no": "Are explicit Yes and No choices visible?",
    "menu/purchase-prompt": "Is a buy or purchase action prompt visible?",
    "menu/back-prompt": "Is an explicit back or cancel prompt visible?",
    "menu/inspect-prompt": "Is an inspect-car or view-car prompt visible?",
    "menu/controller-glyphs": "Are gamepad button glyphs visible in action prompts?",
    "menu/keyboard-glyphs": "Are keyboard key names or keyboard glyphs visible in action prompts?",
    "menu/timer-bar": "Is a time-limit bar visible in a menu or betting interface?",
    "menu/inset-preview": "Is a small secondary car preview inset visible?",
    "menu/wireframe-car": "Is the car displayed as a transparent wireframe in a performance "
    "interface?",
    "menu/numeric-slider": "Is an adjustable slider with numerical endpoint values visible?",
    "menu/slider-selected": "Is a particular slider highlighted as the active control?",
    "menu/radio-toggle": "Are visible on/off, yes/no, or mutually exclusive setting toggles "
    "present?",
    "menu/save-prompt": "Is an explicit save or apply-settings prompt visible?",
    "menu/cart-item-count": "Is the count of pending modification-cart items visible?",
    "menu/cart-delete-item": "Is an explicit remove or delete cart item action visible?",
    "menu/cart-continue": "Is an explicit continue-modifying action visible beside cart checkout?",
    "menu/currency-change": "Is a money gain or loss explicitly shown with a sign or transaction "
    "line?",
    "menu/insufficient-funds": "Is an explicit insufficient-money or cannot-afford message "
    "visible?",
    "menu/ownership-document": "Is a pink-slip ownership document visible?",
    "menu/owner-count": "Is a number-of-owners field visible on an ownership document?",
    "menu/vehicle-history": "Is a vehicle history or transaction-history field visible?",
    "menu/registered-date": "Is a vehicle registration-date field visible?",
    "menu/vehicle-sale": "Is an explicit sell-car action or sale-price offer visible?",
    "menu/manufacturer-logo": "Is a car-manufacturer logo visible in a car-selection interface?",
    "menu/drivetrain": "Is a drivetrain label such as FWD, RWD, or AWD visible?",
    "menu/performance-range": "Is an explicit performance-range bar with minimum and maximum "
    "visible?",
    "menu/stock-league": "Is a stock-league eligibility value explicitly visible?",
    "menu/max-league": "Is a maximum-league eligibility value explicitly visible?",
    "reference/emulator-buttons": "Are emulator touch-button outlines overlaid on the game image?",
    "reference/controller-disconnect": "Is a controller-disconnected or reconnect prompt visible?",
    "reference/subtitles-overlay": "Are uploader-added subtitles or commentary captions visible?",
    "reference/black-frame": "Is the image entirely or almost entirely black?",
    "reference/blurred-ui": "Is the interface blurred enough that labels cannot be read reliably?",
}

TAG_GROUPS = {
    "session": {},
    "character": {},
    "career": {
        "economy/wager-amount": "Is a wager amount visible?",
        "economy/wager-accept-reject": "Are options to accept or reject a bet visible?",
        "economy/pink-slip-explicit": "Is an explicit pink-slip or car-ownership wager "
        "label visible?",
        "economy/event-entry-fee": "Is an event entry fee explicitly displayed?",
        "economy/event-prize": "Is an event prize amount explicitly displayed?",
        "economy/payout-breakdown": "Is a breakdown of post-event money gains or losses visible?",
        "career/league-number": "Is an explicit league number or league name visible?",
        "career/goal-checklist": "Is a list of career goals with completion status visible?",
        "career/promotion-requirement": "Is an explicit requirement for league promotion visible?",
        "career/driver-dna": "Is a Driver DNA graph, profile, or labeled statistic visible?",
        "career/crew-member": "Is a crew member selection or crew profile visible?",
        "career/new-unlock": "Is an explicit newly unlocked item announcement visible?",
        "economy/offer-list": "Is a list of alternative wager amounts visible?",
        "economy/offer-selected": "Is one wager amount visibly highlighted?",
        "economy/counteroffer": "Is an explicit counteroffer or revised-wager notification "
        "visible?",
        "economy/bet-accepted": "Is explicit wager acceptance or agreement visible?",
        "economy/bet-rejected": "Is explicit wager rejection or refusal visible?",
        "economy/car-loss-warning": "Is an explicit warning that losing the race loses the "
        "car visible?",
        "economy/won-car": "Is an explicit newly won or acquired car notification visible?",
        "economy/lost-car": "Is an explicit lost or forfeited car notification visible?",
        "career/completed-goal": "Is a completed goal marked with a checkmark or completion icon?",
        "career/incomplete-goal": "Is an incomplete goal visibly marked as not completed?",
        "career/promotion-announcement": "Is an explicit promotion announcement visible?",
        "career/dna-helix": "Is DNA displayed as a helix graphic with driving disciplines?",
        "career/dna-driving-axis": "Are named driving disciplines or tendencies beside a "
        "DNA graph visible?",
        "career/dna-gambling-axis": "Are named gambling disciplines beside a DNA graph visible?",
    },
    "crew": {
        "career/league-number": "Is an explicit league number or league name visible?",
        "career/goal-checklist": "Is a list of career goals with completion status visible?",
        "career/promotion-requirement": "Is an explicit requirement for league promotion visible?",
        "career/driver-dna": "Is a Driver DNA graph, profile, or labeled statistic visible?",
        "career/crew-member": "Is a crew member selection or crew profile visible?",
        "career/new-unlock": "Is an explicit newly unlocked item announcement visible?",
        "career/completed-goal": "Is a completed goal marked with a checkmark or completion icon?",
        "career/incomplete-goal": "Is an incomplete goal visibly marked as not completed?",
        "career/promotion-announcement": "Is an explicit promotion announcement visible?",
        "career/dna-helix": "Is DNA displayed as a helix graphic with driving disciplines?",
        "career/dna-driving-axis": "Are named driving disciplines or tendencies beside a DNA "
        "graph visible?",
        "career/dna-gambling-axis": "Are named gambling disciplines beside a DNA graph visible?",
        "crew/hire-action": "Is an explicit Hire action for a crew member visible?",
        "crew/member-name": "Is a crew member name displayed in the crew-selection interface?",
        "crew/member-fee": "Is a fee or price to hire a crew member explicitly visible?",
        "crew/member-dna": "Is a crew member's DNA or driving-style profile visible?",
        "crew/lineup-slots": "Are multiple crew-member slots visible in a management interface?",
    },
    "garage": {
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to its "
        "course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, such "
        "as labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back "
        "driving camera?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the car's "
        "sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted "
        "beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
    },
    "dealership": {
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to "
        "its course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, "
        "such as labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back "
        "driving camera?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the "
        "car's sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted "
        "beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
    },
    "body": {
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to its "
        "course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, such as "
        "labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back "
        "driving camera?",
        "body/front-bumper-preview": "Is the customization preview focused on a front bumper?",
        "body/rear-bumper-preview": "Is the customization preview focused on a rear bumper?",
        "body/wheel-preview": "Is the customization preview focused on a wheel?",
        "body/spoiler-preview": "Is the customization preview focused on a rear wing?",
        "body/roof-preview": "Is the customization preview focused on the car roof?",
        "interior/seat-preview": "Is a seat or seat modification prominently previewed?",
        "interior/steering-wheel-preview": "Is a steering wheel modification prominently "
        "previewed?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the car's "
        "sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted "
        "beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
        "body/body-kit-thumbnails": "Are alternative body-kit thumbnails or silhouettes visible?",
        "body/headlight-preview": "Is the active modification preview focused on headlights?",
        "body/taillight-preview": "Is the active modification preview focused on taillights?",
        "body/hood-preview": "Is the active modification preview focused on the hood or bonnet?",
        "body/skirt-preview": "Is the active modification preview focused on side skirts?",
        "body/mirror-preview": "Is the active modification preview focused on exterior mirrors?",
        "body/exhaust-preview": "Is the active modification preview focused on an exhaust tip?",
        "body/wheel-size": "Is an explicit rim diameter or wheel-size value visible?",
        "body/wheel-brand": "Is a selectable wheel-brand name or logo visible?",
    },
    "paint_vinyl": {
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to "
        "its course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, "
        "such as labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing "
        "look-back driving camera?",
        "vinyl/transform-controls": "Are move, scale, or rotate controls for a vinyl visible?",
        "vinyl/layer-list": "Is a list of vinyl layers visible?",
        "vinyl/mirroring": "Is an explicit vinyl mirror or symmetry control visible?",
        "vinyl/opacity": "Is an explicit vinyl opacity or transparency control visible?",
        "vinyl/body-panel-choice": "Is a selectable body panel for placing vinyls visible?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the "
        "car's sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly "
        "emitted beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
        "paint/finish-name": "Is a paint finish or material-type name visible?",
        "paint/palette-grid": "Is a rectangular grid of paint-color swatches visible?",
        "paint/color-wheel": "Is a circular hue or color wheel visible?",
        "paint/body-panel-selected": "Is a specific body panel explicitly selected for painting?",
        "vinyl/add-decal": "Is an Add Decal or equivalent add-layer action visible?",
        "vinyl/layer-index": "Is a current decal-layer number or layer count visible?",
        "vinyl/delete-layer": "Is an explicit delete-decal or delete-layer action visible?",
        "vinyl/copy-layer": "Is an explicit copy or duplicate layer action visible?",
        "vinyl/reorder-layer": "Is an explicit move-layer-up/down or layer-order control visible?",
        "vinyl/rotate-control": "Is an explicit rotate-vinyl control visible?",
        "vinyl/scale-control": "Is an explicit scale or resize-vinyl control visible?",
        "vinyl/move-control": "Is an explicit move or position-vinyl control visible?",
        "vinyl/design-thumbnails": "Are individual decal or vinyl design thumbnails visible?",
        "vinyl/category-label": "Is a vinyl design category name visible?",
    },
    "performance": {
        "performance/pack-matrix": "Is a grid combining league rows and upgrade-pack "
        "columns visible?",
        "performance/power-pack": "Is a power package or power upgrade tier explicitly visible?",
        "performance/handling-pack": "Is a handling package or handling upgrade tier "
        "explicitly visible?",
        "performance/weight-pack": "Is a weight package or weight-reduction tier "
        "explicitly visible?",
        "performance/nitrous-pack": "Is a nitrous package or extreme-nitro tier "
        "explicitly visible?",
        "performance/take-challenge": "Is an explicit Take Challenge action visible "
        "for a locked upgrade?",
        "performance/weight-slider": "Is a vehicle mass or weight-reduction slider "
        "explicitly visible?",
        "performance/power-slider": "Is an adjustable engine-power value explicitly visible?",
        "performance/component-brand": "Is a selectable performance-component brand visible?",
    },
    "wagering": {
        "economy/wager-amount": "Is a wager amount visible?",
        "economy/wager-accept-reject": "Are options to accept or reject a bet visible?",
        "economy/pink-slip-explicit": "Is an explicit pink-slip or car-ownership wager "
        "label visible?",
        "economy/event-entry-fee": "Is an event entry fee explicitly displayed?",
        "economy/event-prize": "Is an event prize amount explicitly displayed?",
        "economy/payout-breakdown": "Is a breakdown of post-event money gains or losses visible?",
        "economy/offer-list": "Is a list of alternative wager amounts visible?",
        "economy/offer-selected": "Is one wager amount visibly highlighted?",
        "economy/counteroffer": "Is an explicit counteroffer or revised-wager "
        "notification visible?",
        "economy/bet-accepted": "Is explicit wager acceptance or agreement visible?",
        "economy/bet-rejected": "Is explicit wager rejection or refusal visible?",
        "economy/car-loss-warning": "Is an explicit warning that losing the race loses "
        "the car visible?",
        "economy/won-car": "Is an explicit newly won or acquired car notification visible?",
        "economy/lost-car": "Is an explicit lost or forfeited car notification visible?",
    },
    "race": {
        "hud/speed": "Is a numerical speed readout visible?",
        "hud/gear": "Is a current gear indicator visible?",
        "hud/tachometer": "Is an RPM gauge or tachometer visible?",
        "hud/minimap": "Is a small map of the race route visible?",
        "hud/position": "Is the player's race position visible?",
        "hud/lap-counter": "Is a current-lap or total-laps counter visible?",
        "hud/race-time": "Is elapsed race time visible?",
        "hud/lap-time": "Is a lap-time or best-lap-time field visible?",
        "hud/countdown-timer": "Is a decreasing event time limit visible?",
        "hud/opponent-name": "Is an opponent's name displayed near their car or in the race HUD?",
        "hud/spook-meter": "Is a fear or spook meter displayed for an opponent?",
        "hud/nitrous-meter": "Is a nitrous supply gauge visible?",
        "hud/wrong-way": "Is an explicit wrong-way warning visible?",
        "hud/checkpoint": "Is an explicit checkpoint notification visible?",
        "hud/goal-popup": "Is a goal or achievement progress notification visible during racing?",
        "hud/input-prompt": "Are keyboard or gamepad button prompts visible?",
        "drift/current-score": "Is a score for the current drift visible?",
        "drift/total-score": "Is an accumulated drift-event score visible?",
        "drift/multiplier": "Is a drift score multiplier visible?",
        "drift/chain": "Is an explicit drift chain or combo indicator visible?",
        "drift/target-score": "Is a drift-event target score visible?",
        "drift/angle-indicator": "Is an explicit drift-angle gauge visible?",
        "drift/banked-score": "Is an explicit newly banked or completed drift score "
        "notification visible?",
        "drift/failure": "Is an explicit failed, broken, or lost drift notification visible?",
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to its "
        "course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, such as "
        "labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back "
        "driving camera?",
        "race/multiple-opponents": "Are at least two opponent cars visible?",
        "race/start-grid": "Are multiple cars arranged on a starting grid?",
        "race/countdown": "Is a pre-race countdown number or GO text visible?",
        "race/finish-banner": "Is a finish, victory, defeat, or race-over announcement visible?",
        "race/spectator-crowd": "Are spectators visible along the course?",
        "race/barriers": "Are solid barriers lining the racing course visible?",
        "race/direction-arrows": "Are trackside direction arrows or chevrons visible?",
        "race/trackside-sponsor": "Are sponsor signs or branded trackside banners visible?",
        "race/road-reflection": "Are visible reflections on the road surface present?",
        "race/motion-blur": "Is motion blur visibly streaking the environment?",
        "race/elimination-warning": "Is a last-place elimination or knockout warning visible?",
        "hud/speed-unit-kph": "Is the visible speed unit explicitly kph or km/h?",
        "hud/speed-unit-mph": "Is the visible speed unit explicitly mph?",
        "hud/tachometer-redline": "Is a differently colored redline zone visible on the "
        "tachometer?",
        "hud/nitrous-segments": "Is nitrous supply represented by visible segments or bars?",
        "hud/minimap-player": "Is a player-location marker visible on the minimap?",
        "hud/minimap-opponents": "Are multiple competitor markers visible on the minimap?",
        "hud/minimap-heading": "Is an arrow or heading indicator visible on the minimap?",
        "hud/position-denominator": "Does the position display visibly include the total "
        "number of competitors?",
        "hud/target-time": "Is a target completion time explicitly displayed?",
        "hud/target-score": "Is a target event score explicitly displayed?",
        "hud/best-time": "Is a field explicitly labeled best time visible?",
        "hud/split-time": "Is an explicit split-time notification visible?",
        "hud/time-delta": "Is a positive or negative time difference visible?",
        "hud/final-lap": "Is an explicit final-lap notification visible?",
        "hud/spooked-notification": "Is the word SPOOKED or equivalent opponent-fear outcome "
        "notification visible?",
        "hud/driving-discipline": "Is an explicit driving-style feedback label such as "
        "Powerslide or Nitrous visible?",
        "hud/crew-command": "Is a crew command or teammate instruction prompt visible during "
        "driving?",
        "hud/crew-indicator": "Is an explicit teammate or crew indicator visible in the "
        "driving HUD?",
        "hud/player-name": "Is the player's driver name explicitly displayed?",
        "hud/damage-gauge": "Is an explicit vehicle damage gauge or damage percentage visible?",
        "drift/chain-text": "Is the phrase CHAIN DRIFT or an explicit drift-chain "
        "notification visible?",
        "drift/points-wasted": "Is a field explicitly labeled points wasted or equivalent visible?",
        "drift/score-increment": "Is a separate score increment displayed near the drifting car?",
        "drift/score-bank-feedback": "Is there explicit feedback that a drift score was "
        "banked or secured?",
        "drift/endurance-label": "Is the event explicitly labeled drift endurance?",
        "drift/king-label": "Is the event explicitly labeled Drift King?",
        "drift/points-label": "Is an event or discipline explicitly labeled drift points?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the car's "
        "sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted "
        "beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
        "race/start-lights": "Are race-start signal lights visible?",
        "race/finish-line": "Is a marked start or finish line visible on the road?",
        "race/lap-marker": "Is an overhead lap or finish gantry visible?",
        "race/apex-curb": "Are striped racing curbs visible beside the road?",
        "race/street-lighting": "Are artificial street lights visibly illuminating the course?",
        "race/tunnel": "Is a tunnel or covered roadway visible?",
        "race/track-fence": "Is a fence separating the track from spectators or scenery visible?",
        "race/rain-visible": "Are actual falling rain streaks or droplets visible?",
        "race/wet-road": "Does the road visibly appear wet, rather than only glossy?",
        "race/near-opponent": "Is an opponent car directly ahead within approximately one "
        "car length?",
        "race/side-by-side": "Are two cars visibly running side by side?",
        "race/blue-arrow": "Are blue route arrows or chevrons visible?",
        "race/yellow-arrow": "Are yellow route arrows or chevrons visible?",
        "race/red-arrow": "Are red route arrows or chevrons visible?",
        "race/host-on-grid": "Is a human host or flag starter standing near the pre-race cars?",
        "race/track-name": "Is a named track or venue displayed in the interface?",
    },
    "results": {
        "hud/speed": "Is a numerical speed readout visible?",
        "hud/gear": "Is a current gear indicator visible?",
        "hud/tachometer": "Is an RPM gauge or tachometer visible?",
        "hud/minimap": "Is a small map of the race route visible?",
        "hud/position": "Is the player's race position visible?",
        "hud/lap-counter": "Is a current-lap or total-laps counter visible?",
        "hud/race-time": "Is elapsed race time visible?",
        "hud/lap-time": "Is a lap-time or best-lap-time field visible?",
        "hud/countdown-timer": "Is a decreasing event time limit visible?",
        "hud/opponent-name": "Is an opponent's name displayed near their car or in the race HUD?",
        "hud/spook-meter": "Is a fear or spook meter displayed for an opponent?",
        "hud/nitrous-meter": "Is a nitrous supply gauge visible?",
        "hud/wrong-way": "Is an explicit wrong-way warning visible?",
        "hud/checkpoint": "Is an explicit checkpoint notification visible?",
        "hud/goal-popup": "Is a goal or achievement progress notification visible during racing?",
        "hud/input-prompt": "Are keyboard or gamepad button prompts visible?",
        "drift/current-score": "Is a score for the current drift visible?",
        "drift/total-score": "Is an accumulated drift-event score visible?",
        "drift/multiplier": "Is a drift score multiplier visible?",
        "drift/chain": "Is an explicit drift chain or combo indicator visible?",
        "drift/target-score": "Is a drift-event target score visible?",
        "drift/angle-indicator": "Is an explicit drift-angle gauge visible?",
        "drift/banked-score": "Is an explicit newly banked or completed drift score "
        "notification visible?",
        "drift/failure": "Is an explicit failed, broken, or lost drift notification visible?",
        "economy/wager-amount": "Is a wager amount visible?",
        "economy/wager-accept-reject": "Are options to accept or reject a bet visible?",
        "economy/pink-slip-explicit": "Is an explicit pink-slip or car-ownership wager "
        "label visible?",
        "economy/event-entry-fee": "Is an event entry fee explicitly displayed?",
        "economy/event-prize": "Is an event prize amount explicitly displayed?",
        "economy/payout-breakdown": "Is a breakdown of post-event money gains or losses visible?",
        "results/position-table": "Is a finishing order table visible?",
        "results/driver-times": "Are per-driver race times visible?",
        "results/driver-scores": "Are per-driver drift scores visible?",
        "results/podium": "Is a podium or winners' celebration visible?",
        "hud/speed-unit-kph": "Is the visible speed unit explicitly kph or km/h?",
        "hud/speed-unit-mph": "Is the visible speed unit explicitly mph?",
        "hud/tachometer-redline": "Is a differently colored redline zone visible on the "
        "tachometer?",
        "hud/nitrous-segments": "Is nitrous supply represented by visible segments or bars?",
        "hud/minimap-player": "Is a player-location marker visible on the minimap?",
        "hud/minimap-opponents": "Are multiple competitor markers visible on the minimap?",
        "hud/minimap-heading": "Is an arrow or heading indicator visible on the minimap?",
        "hud/position-denominator": "Does the position display visibly include the total "
        "number of competitors?",
        "hud/target-time": "Is a target completion time explicitly displayed?",
        "hud/target-score": "Is a target event score explicitly displayed?",
        "hud/best-time": "Is a field explicitly labeled best time visible?",
        "hud/split-time": "Is an explicit split-time notification visible?",
        "hud/time-delta": "Is a positive or negative time difference visible?",
        "hud/final-lap": "Is an explicit final-lap notification visible?",
        "hud/spooked-notification": "Is the word SPOOKED or equivalent opponent-fear "
        "outcome notification visible?",
        "hud/driving-discipline": "Is an explicit driving-style feedback label such as "
        "Powerslide or Nitrous visible?",
        "hud/crew-command": "Is a crew command or teammate instruction prompt visible "
        "during driving?",
        "hud/crew-indicator": "Is an explicit teammate or crew indicator visible in the "
        "driving HUD?",
        "hud/player-name": "Is the player's driver name explicitly displayed?",
        "hud/damage-gauge": "Is an explicit vehicle damage gauge or damage percentage visible?",
        "drift/chain-text": "Is the phrase CHAIN DRIFT or an explicit drift-chain "
        "notification visible?",
        "drift/points-wasted": "Is a field explicitly labeled points wasted or equivalent visible?",
        "drift/score-increment": "Is a separate score increment displayed near the drifting car?",
        "drift/score-bank-feedback": "Is there explicit feedback that a drift score was "
        "banked or secured?",
        "drift/endurance-label": "Is the event explicitly labeled drift endurance?",
        "drift/king-label": "Is the event explicitly labeled Drift King?",
        "drift/points-label": "Is an event or discipline explicitly labeled drift points?",
        "economy/offer-list": "Is a list of alternative wager amounts visible?",
        "economy/offer-selected": "Is one wager amount visibly highlighted?",
        "economy/counteroffer": "Is an explicit counteroffer or revised-wager "
        "notification visible?",
        "economy/bet-accepted": "Is explicit wager acceptance or agreement visible?",
        "economy/bet-rejected": "Is explicit wager rejection or refusal visible?",
        "economy/car-loss-warning": "Is an explicit warning that losing the race loses "
        "the car visible?",
        "economy/won-car": "Is an explicit newly won or acquired car notification visible?",
        "economy/lost-car": "Is an explicit lost or forfeited car notification visible?",
        "results/target-vs-achieved": "Are target and achieved values displayed together "
        "in challenge results?",
        "results/tournament-points": "Are cumulative tournament or championship points visible?",
        "results/round-number": "Is a tournament round number explicitly displayed?",
        "results/retry-action": "Is a retry or restart action visible on the results screen?",
        "results/replay-action": "Is a replay action visible on the results screen?",
        "results/continue-action": "Is a continue or next-event action visible on the "
        "results screen?",
    },
    "replay": {
        "hud/speed": "Is a numerical speed readout visible?",
        "hud/gear": "Is a current gear indicator visible?",
        "hud/tachometer": "Is an RPM gauge or tachometer visible?",
        "hud/minimap": "Is a small map of the race route visible?",
        "hud/position": "Is the player's race position visible?",
        "hud/lap-counter": "Is a current-lap or total-laps counter visible?",
        "hud/race-time": "Is elapsed race time visible?",
        "hud/lap-time": "Is a lap-time or best-lap-time field visible?",
        "hud/countdown-timer": "Is a decreasing event time limit visible?",
        "hud/opponent-name": "Is an opponent's name displayed near their car or in the race HUD?",
        "hud/spook-meter": "Is a fear or spook meter displayed for an opponent?",
        "hud/nitrous-meter": "Is a nitrous supply gauge visible?",
        "hud/wrong-way": "Is an explicit wrong-way warning visible?",
        "hud/checkpoint": "Is an explicit checkpoint notification visible?",
        "hud/goal-popup": "Is a goal or achievement progress notification visible during racing?",
        "hud/input-prompt": "Are keyboard or gamepad button prompts visible?",
        "drift/current-score": "Is a score for the current drift visible?",
        "drift/total-score": "Is an accumulated drift-event score visible?",
        "drift/multiplier": "Is a drift score multiplier visible?",
        "drift/chain": "Is an explicit drift chain or combo indicator visible?",
        "drift/target-score": "Is a drift-event target score visible?",
        "drift/angle-indicator": "Is an explicit drift-angle gauge visible?",
        "drift/banked-score": "Is an explicit newly banked or completed drift score "
        "notification visible?",
        "drift/failure": "Is an explicit failed, broken, or lost drift notification visible?",
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to its "
        "course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, such "
        "as labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back "
        "driving camera?",
        "race/multiple-opponents": "Are at least two opponent cars visible?",
        "race/start-grid": "Are multiple cars arranged on a starting grid?",
        "race/countdown": "Is a pre-race countdown number or GO text visible?",
        "race/finish-banner": "Is a finish, victory, defeat, or race-over announcement visible?",
        "race/spectator-crowd": "Are spectators visible along the course?",
        "race/barriers": "Are solid barriers lining the racing course visible?",
        "race/direction-arrows": "Are trackside direction arrows or chevrons visible?",
        "race/trackside-sponsor": "Are sponsor signs or branded trackside banners visible?",
        "race/road-reflection": "Are visible reflections on the road surface present?",
        "race/motion-blur": "Is motion blur visibly streaking the environment?",
        "race/elimination-warning": "Is a last-place elimination or knockout warning visible?",
        "hud/speed-unit-kph": "Is the visible speed unit explicitly kph or km/h?",
        "hud/speed-unit-mph": "Is the visible speed unit explicitly mph?",
        "hud/tachometer-redline": "Is a differently colored redline zone visible on the "
        "tachometer?",
        "hud/nitrous-segments": "Is nitrous supply represented by visible segments or bars?",
        "hud/minimap-player": "Is a player-location marker visible on the minimap?",
        "hud/minimap-opponents": "Are multiple competitor markers visible on the minimap?",
        "hud/minimap-heading": "Is an arrow or heading indicator visible on the minimap?",
        "hud/position-denominator": "Does the position display visibly include the total "
        "number of competitors?",
        "hud/target-time": "Is a target completion time explicitly displayed?",
        "hud/target-score": "Is a target event score explicitly displayed?",
        "hud/best-time": "Is a field explicitly labeled best time visible?",
        "hud/split-time": "Is an explicit split-time notification visible?",
        "hud/time-delta": "Is a positive or negative time difference visible?",
        "hud/final-lap": "Is an explicit final-lap notification visible?",
        "hud/spooked-notification": "Is the word SPOOKED or equivalent opponent-fear "
        "outcome notification visible?",
        "hud/driving-discipline": "Is an explicit driving-style feedback label such as "
        "Powerslide or Nitrous visible?",
        "hud/crew-command": "Is a crew command or teammate instruction prompt visible "
        "during driving?",
        "hud/crew-indicator": "Is an explicit teammate or crew indicator visible in the "
        "driving HUD?",
        "hud/player-name": "Is the player's driver name explicitly displayed?",
        "hud/damage-gauge": "Is an explicit vehicle damage gauge or damage percentage visible?",
        "drift/chain-text": "Is the phrase CHAIN DRIFT or an explicit drift-chain "
        "notification visible?",
        "drift/points-wasted": "Is a field explicitly labeled points wasted or equivalent visible?",
        "drift/score-increment": "Is a separate score increment displayed near the drifting car?",
        "drift/score-bank-feedback": "Is there explicit feedback that a drift score was "
        "banked or secured?",
        "drift/endurance-label": "Is the event explicitly labeled drift endurance?",
        "drift/king-label": "Is the event explicitly labeled Drift King?",
        "drift/points-label": "Is an event or discipline explicitly labeled drift points?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the car's "
        "sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted "
        "beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
        "race/start-lights": "Are race-start signal lights visible?",
        "race/finish-line": "Is a marked start or finish line visible on the road?",
        "race/lap-marker": "Is an overhead lap or finish gantry visible?",
        "race/apex-curb": "Are striped racing curbs visible beside the road?",
        "race/street-lighting": "Are artificial street lights visibly illuminating the course?",
        "race/tunnel": "Is a tunnel or covered roadway visible?",
        "race/track-fence": "Is a fence separating the track from spectators or scenery visible?",
        "race/rain-visible": "Are actual falling rain streaks or droplets visible?",
        "race/wet-road": "Does the road visibly appear wet, rather than only glossy?",
        "race/near-opponent": "Is an opponent car directly ahead within approximately one "
        "car length?",
        "race/side-by-side": "Are two cars visibly running side by side?",
        "race/blue-arrow": "Are blue route arrows or chevrons visible?",
        "race/yellow-arrow": "Are yellow route arrows or chevrons visible?",
        "race/red-arrow": "Are red route arrows or chevrons visible?",
        "race/host-on-grid": "Is a human host or flag starter standing near the pre-race cars?",
        "race/track-name": "Is a named track or venue displayed in the interface?",
    },
    "options": {},
    "multiplayer": {},
    "presentation": {
        "vehicle/sliding": "Is the player's car visibly angled sideways relative to "
        "its course of travel?",
        "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
        "vehicle/skid-marks": "Are tire skid marks visible on the road?",
        "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
        "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, "
        "such as labeled boost or boost flames?",
        "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
        "vehicle/sparks": "Are collision sparks visible?",
        "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
        "vehicle/airborne": "Are all visible wheels of a car off the road?",
        "vehicle/reverse-view": "Does the view explicitly show a rear-facing "
        "look-back driving camera?",
        "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
        "vehicle/headlights": "Are a car's headlights visibly illuminated?",
        "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the "
        "car's sideways yaw?",
        "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
        "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
        "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
        "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
        "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
        "vehicle/driver-model": "Is a driver model visible inside a car?",
        "vehicle/underglow": "Is artificial colored underbody lighting visibly "
        "emitted beneath a car?",
        "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
        "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
        "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
        "vehicle/license-text": "Are distinct license-plate characters visible?",
    },
    "reference": {},
}

TAGS = {
    "hud/speed": "Is a numerical speed readout visible?",
    "hud/gear": "Is a current gear indicator visible?",
    "hud/tachometer": "Is an RPM gauge or tachometer visible?",
    "hud/minimap": "Is a small map of the race route visible?",
    "hud/position": "Is the player's race position visible?",
    "hud/lap-counter": "Is a current-lap or total-laps counter visible?",
    "hud/race-time": "Is elapsed race time visible?",
    "hud/lap-time": "Is a lap-time or best-lap-time field visible?",
    "hud/countdown-timer": "Is a decreasing event time limit visible?",
    "hud/opponent-name": "Is an opponent's name displayed near their car or in the race HUD?",
    "hud/spook-meter": "Is a fear or spook meter displayed for an opponent?",
    "hud/nitrous-meter": "Is a nitrous supply gauge visible?",
    "hud/wrong-way": "Is an explicit wrong-way warning visible?",
    "hud/checkpoint": "Is an explicit checkpoint notification visible?",
    "hud/goal-popup": "Is a goal or achievement progress notification visible during racing?",
    "hud/input-prompt": "Are keyboard or gamepad button prompts visible?",
    "drift/current-score": "Is a score for the current drift visible?",
    "drift/total-score": "Is an accumulated drift-event score visible?",
    "drift/multiplier": "Is a drift score multiplier visible?",
    "drift/chain": "Is an explicit drift chain or combo indicator visible?",
    "drift/target-score": "Is a drift-event target score visible?",
    "drift/angle-indicator": "Is an explicit drift-angle gauge visible?",
    "drift/banked-score": "Is an explicit newly banked or completed drift score notification "
    "visible?",
    "drift/failure": "Is an explicit failed, broken, or lost drift notification visible?",
    "vehicle/sliding": "Is the player's car visibly angled sideways relative to its course of "
    "travel?",
    "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
    "vehicle/skid-marks": "Are tire skid marks visible on the road?",
    "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
    "vehicle/nitrous-feedback": "Is visible nitrous activation feedback present, such as labeled "
    "boost or boost flames?",
    "vehicle/body-damage": "Is visible deformation or missing bodywork present on a car?",
    "vehicle/sparks": "Are collision sparks visible?",
    "vehicle/collision-contact": "Is a car visibly touching another car or a barrier?",
    "vehicle/airborne": "Are all visible wheels of a car off the road?",
    "vehicle/reverse-view": "Does the view explicitly show a rear-facing look-back driving camera?",
    "race/multiple-opponents": "Are at least two opponent cars visible?",
    "race/start-grid": "Are multiple cars arranged on a starting grid?",
    "race/countdown": "Is a pre-race countdown number or GO text visible?",
    "race/finish-banner": "Is a finish, victory, defeat, or race-over announcement visible?",
    "race/spectator-crowd": "Are spectators visible along the course?",
    "race/barriers": "Are solid barriers lining the racing course visible?",
    "race/direction-arrows": "Are trackside direction arrows or chevrons visible?",
    "race/trackside-sponsor": "Are sponsor signs or branded trackside banners visible?",
    "race/road-reflection": "Are visible reflections on the road surface present?",
    "race/motion-blur": "Is motion blur visibly streaking the environment?",
    "race/elimination-warning": "Is a last-place elimination or knockout warning visible?",
    "menu/selected-row": "Is a highlighted selected menu row or tile visible?",
    "menu/locked-item": "Is an explicitly locked item or padlock visible?",
    "menu/confirm-dialog": "Is a confirmation dialog with accept or cancel choices visible?",
    "menu/price": "Is a price for a car, part, or modification visible?",
    "menu/modification-cart": "Is an itemized cart of pending car modifications visible?",
    "menu/cart-total": "Is the total price of pending car modifications visible?",
    "menu/cash-balance": "Is the player's available cash balance visible?",
    "menu/performance-bars": "Are vehicle performance comparison bars visible?",
    "menu/car-specifications": "Are numerical vehicle specifications visible?",
    "menu/car-class": "Is an explicit car class or league eligibility label visible?",
    "menu/car-name": "Is the car's make or model name displayed in the interface?",
    "menu/part-thumbnails": "Are selectable car-part thumbnails visible?",
    "menu/color-swatches": "Are selectable color swatches visible?",
    "menu/color-sliders": "Are color adjustment sliders or a color picker visible?",
    "menu/tuning-slider": "Is an adjustable performance tuning slider visible?",
    "menu/before-after-stats": "Are old and new performance values visibly compared?",
    "menu/upgrade-tier": "Are performance upgrade tiers or stages visible?",
    "menu/unlock-requirement": "Is text stating a requirement to unlock a car or part visible?",
    "vinyl/transform-controls": "Are move, scale, or rotate controls for a vinyl visible?",
    "vinyl/layer-list": "Is a list of vinyl layers visible?",
    "vinyl/mirroring": "Is an explicit vinyl mirror or symmetry control visible?",
    "vinyl/opacity": "Is an explicit vinyl opacity or transparency control visible?",
    "vinyl/body-panel-choice": "Is a selectable body panel for placing vinyls visible?",
    "body/front-bumper-preview": "Is the customization preview focused on a front bumper?",
    "body/rear-bumper-preview": "Is the customization preview focused on a rear bumper?",
    "body/wheel-preview": "Is the customization preview focused on a wheel?",
    "body/spoiler-preview": "Is the customization preview focused on a rear wing?",
    "body/roof-preview": "Is the customization preview focused on the car roof?",
    "interior/seat-preview": "Is a seat or seat modification prominently previewed?",
    "interior/steering-wheel-preview": "Is a steering wheel modification prominently previewed?",
    "economy/wager-amount": "Is a wager amount visible?",
    "economy/wager-accept-reject": "Are options to accept or reject a bet visible?",
    "economy/pink-slip-explicit": "Is an explicit pink-slip or car-ownership wager label visible?",
    "economy/event-entry-fee": "Is an event entry fee explicitly displayed?",
    "economy/event-prize": "Is an event prize amount explicitly displayed?",
    "economy/payout-breakdown": "Is a breakdown of post-event money gains or losses visible?",
    "career/league-number": "Is an explicit league number or league name visible?",
    "career/goal-checklist": "Is a list of career goals with completion status visible?",
    "career/promotion-requirement": "Is an explicit requirement for league promotion visible?",
    "career/driver-dna": "Is a Driver DNA graph, profile, or labeled statistic visible?",
    "career/crew-member": "Is a crew member selection or crew profile visible?",
    "career/new-unlock": "Is an explicit newly unlocked item announcement visible?",
    "results/position-table": "Is a finishing order table visible?",
    "results/driver-times": "Are per-driver race times visible?",
    "results/driver-scores": "Are per-driver drift scores visible?",
    "results/podium": "Is a podium or winners' celebration visible?",
    "presentation/host": "Is a human race host or presenter a prominent part of the screen?",
    "presentation/avatar": "Is a customizable driver avatar prominently displayed?",
    "presentation/replay-controls": "Are replay playback controls visible?",
    "reference/uploader-overlay": "Is an uploader watermark, webcam, subtitle, or external "
    "overlay visible?",
    "reference/letterbox": "Are substantial black bars around the game image visible?",
    "reference/low-readability": "Is game interface text too small or blurred to read reliably?",
    "hud/speed-unit-kph": "Is the visible speed unit explicitly kph or km/h?",
    "hud/speed-unit-mph": "Is the visible speed unit explicitly mph?",
    "hud/tachometer-redline": "Is a differently colored redline zone visible on the tachometer?",
    "hud/nitrous-segments": "Is nitrous supply represented by visible segments or bars?",
    "hud/minimap-player": "Is a player-location marker visible on the minimap?",
    "hud/minimap-opponents": "Are multiple competitor markers visible on the minimap?",
    "hud/minimap-heading": "Is an arrow or heading indicator visible on the minimap?",
    "hud/position-denominator": "Does the position display visibly include the total number of "
    "competitors?",
    "hud/target-time": "Is a target completion time explicitly displayed?",
    "hud/target-score": "Is a target event score explicitly displayed?",
    "hud/best-time": "Is a field explicitly labeled best time visible?",
    "hud/split-time": "Is an explicit split-time notification visible?",
    "hud/time-delta": "Is a positive or negative time difference visible?",
    "hud/final-lap": "Is an explicit final-lap notification visible?",
    "hud/spooked-notification": "Is the word SPOOKED or equivalent opponent-fear outcome "
    "notification visible?",
    "hud/driving-discipline": "Is an explicit driving-style feedback label such as Powerslide or "
    "Nitrous visible?",
    "hud/crew-command": "Is a crew command or teammate instruction prompt visible during driving?",
    "hud/crew-indicator": "Is an explicit teammate or crew indicator visible in the driving HUD?",
    "hud/player-name": "Is the player's driver name explicitly displayed?",
    "hud/damage-gauge": "Is an explicit vehicle damage gauge or damage percentage visible?",
    "drift/chain-text": "Is the phrase CHAIN DRIFT or an explicit drift-chain notification "
    "visible?",
    "drift/points-wasted": "Is a field explicitly labeled points wasted or equivalent visible?",
    "drift/score-increment": "Is a separate score increment displayed near the drifting car?",
    "drift/score-bank-feedback": "Is there explicit feedback that a drift score was banked or "
    "secured?",
    "drift/endurance-label": "Is the event explicitly labeled drift endurance?",
    "drift/king-label": "Is the event explicitly labeled Drift King?",
    "drift/points-label": "Is an event or discipline explicitly labeled drift points?",
    "vehicle/brake-lights": "Are the player's brake lights visibly illuminated?",
    "vehicle/headlights": "Are a car's headlights visibly illuminated?",
    "vehicle/wheel-countersteer": "Are visible front wheels steered opposite the car's sideways "
    "yaw?",
    "vehicle/body-roll": "Is visible car-body lean relative to the wheels apparent?",
    "vehicle/detached-part": "Is detached car bodywork visibly separate from a vehicle?",
    "vehicle/dented-panel": "Is a visibly dented or crumpled body panel present?",
    "vehicle/paint-scrape": "Are visible scrape marks or paint damage present on a car?",
    "vehicle/transparent-window": "Is the cabin visible through transparent car windows?",
    "vehicle/driver-model": "Is a driver model visible inside a car?",
    "vehicle/underglow": "Is artificial colored underbody lighting visibly emitted beneath a car?",
    "vehicle/convertible": "Is an open-top or visibly roofless car shown?",
    "vehicle/wide-body": "Are visibly extended wheel arches or a wide body kit present?",
    "vehicle/car-livery": "Is a non-solid-color decal or graphic livery visible on a car?",
    "vehicle/license-text": "Are distinct license-plate characters visible?",
    "race/start-lights": "Are race-start signal lights visible?",
    "race/finish-line": "Is a marked start or finish line visible on the road?",
    "race/lap-marker": "Is an overhead lap or finish gantry visible?",
    "race/apex-curb": "Are striped racing curbs visible beside the road?",
    "race/street-lighting": "Are artificial street lights visibly illuminating the course?",
    "race/tunnel": "Is a tunnel or covered roadway visible?",
    "race/track-fence": "Is a fence separating the track from spectators or scenery visible?",
    "race/rain-visible": "Are actual falling rain streaks or droplets visible?",
    "race/wet-road": "Does the road visibly appear wet, rather than only glossy?",
    "race/near-opponent": "Is an opponent car directly ahead within approximately one car length?",
    "race/side-by-side": "Are two cars visibly running side by side?",
    "race/blue-arrow": "Are blue route arrows or chevrons visible?",
    "race/yellow-arrow": "Are yellow route arrows or chevrons visible?",
    "race/red-arrow": "Are red route arrows or chevrons visible?",
    "race/host-on-grid": "Is a human host or flag starter standing near the pre-race cars?",
    "race/track-name": "Is a named track or venue displayed in the interface?",
    "menu/left-right-carousel": "Are left/right arrows for cycling selectable items visible?",
    "menu/category-icons": "Is a row or ring of selectable category icons visible?",
    "menu/item-index": "Is an item count or current-index/total-items display visible?",
    "menu/tabs": "Are selectable menu tabs visible?",
    "menu/scrollbar": "Is a scrollbar or scroll-position indicator visible?",
    "menu/yes-no": "Are explicit Yes and No choices visible?",
    "menu/purchase-prompt": "Is a buy or purchase action prompt visible?",
    "menu/back-prompt": "Is an explicit back or cancel prompt visible?",
    "menu/inspect-prompt": "Is an inspect-car or view-car prompt visible?",
    "menu/controller-glyphs": "Are gamepad button glyphs visible in action prompts?",
    "menu/keyboard-glyphs": "Are keyboard key names or keyboard glyphs visible in action prompts?",
    "menu/timer-bar": "Is a time-limit bar visible in a menu or betting interface?",
    "menu/inset-preview": "Is a small secondary car preview inset visible?",
    "menu/wireframe-car": "Is the car displayed as a transparent wireframe in a performance "
    "interface?",
    "menu/numeric-slider": "Is an adjustable slider with numerical endpoint values visible?",
    "menu/slider-selected": "Is a particular slider highlighted as the active control?",
    "menu/radio-toggle": "Are visible on/off, yes/no, or mutually exclusive setting toggles "
    "present?",
    "menu/save-prompt": "Is an explicit save or apply-settings prompt visible?",
    "menu/cart-item-count": "Is the count of pending modification-cart items visible?",
    "menu/cart-delete-item": "Is an explicit remove or delete cart item action visible?",
    "menu/cart-continue": "Is an explicit continue-modifying action visible beside cart checkout?",
    "menu/currency-change": "Is a money gain or loss explicitly shown with a sign or transaction "
    "line?",
    "menu/insufficient-funds": "Is an explicit insufficient-money or cannot-afford message "
    "visible?",
    "menu/ownership-document": "Is a pink-slip ownership document visible?",
    "menu/owner-count": "Is a number-of-owners field visible on an ownership document?",
    "menu/vehicle-history": "Is a vehicle history or transaction-history field visible?",
    "menu/registered-date": "Is a vehicle registration-date field visible?",
    "menu/vehicle-sale": "Is an explicit sell-car action or sale-price offer visible?",
    "menu/manufacturer-logo": "Is a car-manufacturer logo visible in a car-selection interface?",
    "menu/drivetrain": "Is a drivetrain label such as FWD, RWD, or AWD visible?",
    "menu/performance-range": "Is an explicit performance-range bar with minimum and maximum "
    "visible?",
    "menu/stock-league": "Is a stock-league eligibility value explicitly visible?",
    "menu/max-league": "Is a maximum-league eligibility value explicitly visible?",
    "body/body-kit-thumbnails": "Are alternative body-kit thumbnails or silhouettes visible?",
    "body/headlight-preview": "Is the active modification preview focused on headlights?",
    "body/taillight-preview": "Is the active modification preview focused on taillights?",
    "body/hood-preview": "Is the active modification preview focused on the hood or bonnet?",
    "body/skirt-preview": "Is the active modification preview focused on side skirts?",
    "body/mirror-preview": "Is the active modification preview focused on exterior mirrors?",
    "body/exhaust-preview": "Is the active modification preview focused on an exhaust tip?",
    "body/wheel-size": "Is an explicit rim diameter or wheel-size value visible?",
    "body/wheel-brand": "Is a selectable wheel-brand name or logo visible?",
    "paint/finish-name": "Is a paint finish or material-type name visible?",
    "paint/palette-grid": "Is a rectangular grid of paint-color swatches visible?",
    "paint/color-wheel": "Is a circular hue or color wheel visible?",
    "paint/body-panel-selected": "Is a specific body panel explicitly selected for painting?",
    "vinyl/add-decal": "Is an Add Decal or equivalent add-layer action visible?",
    "vinyl/layer-index": "Is a current decal-layer number or layer count visible?",
    "vinyl/delete-layer": "Is an explicit delete-decal or delete-layer action visible?",
    "vinyl/copy-layer": "Is an explicit copy or duplicate layer action visible?",
    "vinyl/reorder-layer": "Is an explicit move-layer-up/down or layer-order control visible?",
    "vinyl/rotate-control": "Is an explicit rotate-vinyl control visible?",
    "vinyl/scale-control": "Is an explicit scale or resize-vinyl control visible?",
    "vinyl/move-control": "Is an explicit move or position-vinyl control visible?",
    "vinyl/design-thumbnails": "Are individual decal or vinyl design thumbnails visible?",
    "vinyl/category-label": "Is a vinyl design category name visible?",
    "performance/pack-matrix": "Is a grid combining league rows and upgrade-pack columns visible?",
    "performance/power-pack": "Is a power package or power upgrade tier explicitly visible?",
    "performance/handling-pack": "Is a handling package or handling upgrade tier explicitly "
    "visible?",
    "performance/weight-pack": "Is a weight package or weight-reduction tier explicitly visible?",
    "performance/nitrous-pack": "Is a nitrous package or extreme-nitro tier explicitly visible?",
    "performance/take-challenge": "Is an explicit Take Challenge action visible for a locked "
    "upgrade?",
    "performance/weight-slider": "Is a vehicle mass or weight-reduction slider explicitly visible?",
    "performance/power-slider": "Is an adjustable engine-power value explicitly visible?",
    "performance/component-brand": "Is a selectable performance-component brand visible?",
    "economy/offer-list": "Is a list of alternative wager amounts visible?",
    "economy/offer-selected": "Is one wager amount visibly highlighted?",
    "economy/counteroffer": "Is an explicit counteroffer or revised-wager notification visible?",
    "economy/bet-accepted": "Is explicit wager acceptance or agreement visible?",
    "economy/bet-rejected": "Is explicit wager rejection or refusal visible?",
    "economy/car-loss-warning": "Is an explicit warning that losing the race loses the car "
    "visible?",
    "economy/won-car": "Is an explicit newly won or acquired car notification visible?",
    "economy/lost-car": "Is an explicit lost or forfeited car notification visible?",
    "career/completed-goal": "Is a completed goal marked with a checkmark or completion icon?",
    "career/incomplete-goal": "Is an incomplete goal visibly marked as not completed?",
    "career/promotion-announcement": "Is an explicit promotion announcement visible?",
    "career/dna-helix": "Is DNA displayed as a helix graphic with driving disciplines?",
    "career/dna-driving-axis": "Are named driving disciplines or tendencies beside a DNA graph "
    "visible?",
    "career/dna-gambling-axis": "Are named gambling disciplines beside a DNA graph visible?",
    "crew/hire-action": "Is an explicit Hire action for a crew member visible?",
    "crew/member-name": "Is a crew member name displayed in the crew-selection interface?",
    "crew/member-fee": "Is a fee or price to hire a crew member explicitly visible?",
    "crew/member-dna": "Is a crew member's DNA or driving-style profile visible?",
    "crew/lineup-slots": "Are multiple crew-member slots visible in a management interface?",
    "results/target-vs-achieved": "Are target and achieved values displayed together in challenge "
    "results?",
    "results/tournament-points": "Are cumulative tournament or championship points visible?",
    "results/round-number": "Is a tournament round number explicitly displayed?",
    "results/retry-action": "Is a retry or restart action visible on the results screen?",
    "results/replay-action": "Is a replay action visible on the results screen?",
    "results/continue-action": "Is a continue or next-event action visible on the results screen?",
    "reference/emulator-buttons": "Are emulator touch-button outlines overlaid on the game image?",
    "reference/controller-disconnect": "Is a controller-disconnected or reconnect prompt visible?",
    "reference/subtitles-overlay": "Are uploader-added subtitles or commentary captions visible?",
    "reference/black-frame": "Is the image entirely or almost entirely black?",
    "reference/blurred-ui": "Is the interface blurred enough that labels cannot be read reliably?",
}

FACETS = {
    "camera": {
        "chase": "Third-person camera behind the player's car during driving.",
        "bumper_hood": "Forward driving view from bumper or hood; no full player car visible.",
        "cockpit": "Interior driving view with dashboard or cockpit visible.",
        "cinematic": "Trackside, aerial, orbiting, grid, or replay presentation camera.",
        "car_preview": "A stationary car preview within garage, shop, or customization UI.",
        "interface": "Menu or text interface without a meaningful car-camera view.",
        "unclear": "Camera position cannot be resolved from this image.",
    },
    "lighting": {
        "day": "Scene visibly lit by daylight.",
        "night": "Dark nighttime scene with artificial lighting.",
        "dusk": "Visible twilight, sunset, or sunrise lighting.",
        "indoor": "Garage, showroom, nightclub, or other interior lighting.",
        "unresolved": "Time of day is indeterminate or no world scene is visible.",
    },
    "venue": {
        "city_street": "Built urban street with buildings close to the course.",
        "closed_circuit": "Purpose-built racing circuit with track infrastructure.",
        "industrial": "Docks, warehouses, airfield, factories, or industrial course.",
        "mountain": "Hillside, mountain road, or rural course.",
        "interior": "Garage, dealership, nightclub, or other indoor environment.",
        "unresolved": "Venue cannot be identified visually.",
    },
    "interface_control": {
        "list": "A vertical list or table is the main actionable control.",
        "carousel": "A horizontal icon or thumbnail carousel is the main actionable control.",
        "slider": "One or more adjustable sliders are the main actionable controls.",
        "palette": "A color grid, wheel, or palette is the main actionable control.",
        "text_entry": "A character-entry field or on-screen keyboard is the main control.",
        "dialog": "A modal yes/no or confirmation dialog is the main control.",
        "driving": "Driving HUD, without an actionable menu.",
        "cinematic": "Non-actionable cinematic or showroom view.",
        "unresolved": "The main actionable control cannot be identified.",
    },
    "race_feedback": {
        "none_visible": "No explicit transient race feedback is visible.",
        "countdown": "A race-start countdown or GO message is visible.",
        "drift": "A drift score, chain, or drift outcome notification is visible.",
        "spook": "An explicit spook or spooked notification is visible.",
        "split": "A split time or time delta notification is visible.",
        "goal": "A goal progress or achievement notification is visible.",
        "finish": "A win, loss, finish, or disqualification message is visible.",
        "other": "A different explicit race feedback notification is visible.",
    },
    "car_preview_view": {
        "front": "The front of the preview car dominates.",
        "rear": "The rear of the preview car dominates.",
        "side": "A side profile of the preview car dominates.",
        "three_quarter": "A three-quarter view of the preview car dominates.",
        "interior": "The cabin interior or interior part dominates.",
        "wireframe": "A transparent wireframe of the car dominates.",
        "not_preview": "There is no stationary editable car preview.",
        "unresolved": "Preview viewpoint cannot be identified.",
    },
    "visible_language": {
        "english": "The readable interface labels are mainly English.",
        "french": "The readable interface labels are mainly French.",
        "german": "The readable interface labels are mainly German.",
        "other": "Readable labels are mainly a different language.",
        "unreadable": "There are no reliably readable language cues.",
    },
}

SCORES = {
    "readability": {
        "instructions": "How readable is the game interface text in `screenshot`?",
        "criteria": [
            "No meaningful game text can be read.",
            "Only large headings or a few large numbers can be read.",
            "Most main labels can be read, but small detail is unclear.",
            "Small interface labels and numerical fields are clear.",
        ],
    },
    "action_detail": {
        "instructions": "How much directly visible interaction detail is in `screenshot`?",
        "criteria": [
            "No actionable controls or explicit gameplay feedback are visible.",
            "Broad game state is visible, but little specific interaction detail.",
            "Several controls or gameplay-feedback fields are identifiable.",
            "Selected controls, choices, and feedback give precise interaction detail.",
        ],
    },
    "visual_obstruction": {
        "instructions": "How much of the meaningful game image is obscured in `screenshot`?",
        "criteria": [
            "The game image is clear with little or no obstruction.",
            "Small overlays cover a minor area without hiding the main interface.",
            "Overlays or cropping hide some important game information.",
            "Most meaningful game information is obscured, black, or missing.",
        ],
    },
}

BOXES = {
    "player_car": {
        "instructions": "Locate the player-controlled car in `screenshot`.",
        "presence": "Is the player-controlled car visible in `screenshot`?",
    },
    "primary_menu": {
        "instructions": "Locate the main actionable menu or control panel in `screenshot`.",
        "presence": "Is an actionable menu or control panel visible in `screenshot`?",
    },
    "selected_control": {
        "instructions": "Locate the currently highlighted menu row, slider, or "
        "selected control in `screenshot`.",
        "presence": "Is a visibly highlighted selected menu control present in `screenshot`?",
    },
    "speed_cluster": {
        "instructions": "Locate the speed, gear, and tachometer cluster in `screenshot`.",
        "presence": "Is a speed, gear, or tachometer cluster visible in `screenshot`?",
    },
    "minimap": {
        "instructions": "Locate the race minimap in `screenshot`.",
        "presence": "Is a race minimap visible in `screenshot`?",
    },
    "event_score_time": {
        "instructions": "Locate the main event target, score, or time panel in `screenshot`.",
        "presence": "Is an event target, score, or time panel visible in `screenshot`?",
    },
    "race_feedback": {
        "instructions": "Locate the transient race feedback notification in `screenshot`.",
        "presence": "Is a transient race feedback notification visible in `screenshot`?",
    },
    "cash_price": {
        "instructions": "Locate the cash balance, price, or transaction total in `screenshot`.",
        "presence": "Is a cash balance, price, or transaction total visible in `screenshot`?",
    },
    "part_preview": {
        "instructions": "Locate the car part or graphic being edited in `screenshot`.",
        "presence": "Is a clearly selected editable car part or graphic preview "
        "visible in `screenshot`?",
    },
    "avatar": {
        "instructions": "Locate the driver avatar or crew member in `screenshot`.",
        "presence": "Is a prominent driver avatar or crew member visible in `screenshot`?",
    },
}

# Pixel-localization candidates are always paired with a presence Noul. A Box
# alone always returns a position, including when the requested object is absent.
for _definition in BOXES.values():
    _definition["presence_question"] = _definition["presence"]
BOXES.update(
    {
        "dialog": {
            "instructions": "Locate the active modal dialog in `screenshot`.",
            "presence": "Is an active modal dialog visible in `screenshot`?",
            "presence_question": "Is an active modal dialog visible in `screenshot`?",
        },
        "speed_readout": {
            "instructions": "Locate the numerical current-speed readout in `screenshot`.",
            "presence": "Is a numerical current-speed readout visible in `screenshot`?",
            "presence_question": "Is a numerical current-speed readout visible in `screenshot`?",
        },
    }
)

# Jev's candidate judgments prefer these as overlapping attributes, rather than
# primary states. Their existing presence tags remain in the independent catalog.
for _state in (
    "race/loading/explicit",
    "results/challenge/unlock",
    "reference/creator-overlay/webcam",
    "reference/unreadable/transition",
):
    SCREEN_STATES.pop(_state, None)
    for _catalog in SCREEN_GROUPS.values():
        _catalog.pop(_state, None)

CHOICE_ACCEPT = 0.85
CHOICE_MARGIN = 0.5
TAG_YES = 0.8
TAG_NO = 0.2


def noul_question(instructions):
    return {
        "type": "noul",
        "instructions": instructions + " Judge only the pixels in `screenshot`.",
        "criteria": {
            "true": "The specified feature is visibly present.",
            "false": "The image shows other content, or the specified feature is not visible.",
        },
    }


def broad_questions():
    result = {
        "game_visible": noul_question("Does `screenshot` contain a game scene or game interface?"),
        "domain": {
            "type": "choice",
            "instructions": "Which active screen domain best describes `screenshot`?",
            "criteria": GROUPS,
        },
    }
    for name, definition in SCORES.items():
        result["score/" + name] = {"type": "score", **definition}
    for name in ["camera", "lighting", "venue", "visible_language"]:
        result["facet/" + name] = {
            "type": "choice",
            "instructions": f"Which {name} is visibly present in `screenshot`?",
            "criteria": FACETS[name],
        }
    result.update({name: noul_question(text) for name, text in COMMON_TAGS.items()})
    return result


def detail_questions(group, include_boxes=False):
    if group not in SCREEN_GROUPS:
        raise ValueError("Unknown visual domain: " + group)
    result = {
        "screen": {
            "type": "choice",
            "instructions": (
                "Which active screen state best describes `screenshot`? Prefer a specific state "
                "only when its distinguishing selected control or readable label is visible."
            ),
            "criteria": SCREEN_GROUPS[group],
        },
        "domain_matches": noul_question(
            "Does the visible active interface belong to this domain: " + GROUPS[group] + "?"
        ),
    }
    result.update({name: noul_question(text) for name, text in TAG_GROUPS[group].items()})
    for name in ["interface_control", "race_feedback", "car_preview_view"]:
        result["facet/" + name] = {
            "type": "choice",
            "instructions": f"Which {name} is visibly present in `screenshot`?",
            "criteria": FACETS[name],
        }
    if include_boxes:
        for name, definition in BOXES.items():
            result["box_present/" + name] = noul_question(definition["presence"])
            result["box/" + name] = {"type": "box", "instructions": definition["instructions"]}
    return result


def questions():
    """Compatibility flat catalog; normal classification should use the two stages."""
    result = broad_questions()
    result["screen"] = {
        "type": "choice",
        "instructions": "Which active screen state best describes `screenshot`?",
        "criteria": SCREEN_STATES,
    }
    result.update({name: noul_question(text) for name, text in TAGS.items()})
    return result

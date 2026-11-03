"""Observable Juiced 2 screen states and independent visual questions.

These are reference-search categories, not assertions about the game's rules.
Keep question wording and thresholds here so the vault's judgments are auditable.
"""

SCREEN_STATES = {
    "boot/title": "Title logo or press-start screen before the main menu.",
    "boot/legal": "Publisher, developer, legal, or startup logo splash.",
    "menu/main": "Top-level menu choosing career, race, options, or other major modes.",
    "menu/profile": "Profile or save-slot selection, creation, loading, or save confirmation.",
    "menu/mode": "Race-mode selection outside a career event list.",
    "character/preset": "Choosing a driver avatar or character preset.",
    "character/face": "Editing face, head, skin, hair, or facial features.",
    "character/clothing": "Editing driver clothing, accessories, or outfit colors.",
    "character/identity": "Entering or confirming driver name, gender, or identity.",
    "career/hub": "Career overview with navigation to garage, leagues, or other career areas.",
    "career/leagues": "League ladder or selection showing progression tiers.",
    "career/goals": "League goals, achievements, or promotion requirements list.",
    "career/event-list": "Choosing an event from a career event list or map.",
    "career/event-details": "Selected event rules, entry requirements, prize, or track preview.",
    "career/promotion": (
        "League promotion, newly unlocked league, or career milestone announcement."
    ),
    "career/reward": "Reward, unlock, achievement, or bonus announcement outside results tables.",
    "career/dna-profile": "Driver DNA profile or driving-style statistics overview.",
    "career/dna-opponents": "DNA opponent selection, download, or challenge list.",
    "crew/selection": "Selecting, recruiting, or inspecting a crew member.",
    "crew/management": "Crew management or teammate instructions menu.",
    "garage/overview": "Garage car overview with navigation among modification functions.",
    "garage/owned-cars": "Choosing among cars already owned, without a purchase transaction.",
    "garage/car-showcase": (
        "Car displayed on a showroom turntable without an active editing or shopping interface."
    ),
    "garage/pink-slip-record": (
        "Pink-slip ownership document with owner, value, races, or history; not placing a wager."
    ),
    "career/dna-challenges": (
        "Driver DNA discipline list such as circuit, overtake, nitrous, spooking, or betting."
    ),
    "dealership/car-list": "Browsing cars for purchase or choosing a starter car.",
    "dealership/car-details": "Purchase-focused car specifications, price, or color preview.",
    "dealership/purchase-confirm": (
        "Confirming a car purchase or insufficient-funds transaction dialog."
    ),
    "garage/sell-confirm": "Confirming sale of an owned car or displaying its sale value.",
    "customization/category": (
        "Modification category menu without one specific editable part active."
    ),
    "customization/checkout": (
        "Shopping cart itemizing pending modifications with total and purchase or remove controls."
    ),
    "customization/interior": (
        "Selecting or previewing seats, steering wheel, or other interior modifications."
    ),
    "customization/body/body-kit": "Selecting or previewing a complete body kit.",
    "customization/body/front-bumper": "Selecting or previewing a front bumper.",
    "customization/body/rear-bumper": "Selecting or previewing a rear bumper.",
    "customization/body/side-skirts": "Selecting or previewing side skirts.",
    "customization/body/hood": "Selecting or previewing a hood or bonnet.",
    "customization/body/spoiler": "Selecting or previewing a rear wing or spoiler.",
    "customization/body/mirrors": "Selecting or previewing exterior mirrors.",
    "customization/body/lights": "Selecting or previewing headlights or taillights.",
    "customization/body/exhaust": "Selecting or previewing an exhaust tip.",
    "customization/body/roof": "Selecting or previewing a roof modification.",
    "customization/wheels/rims": "Selecting a wheel or rim design.",
    "customization/wheels/size": "Editing wheel diameter, tire dimensions, or wheel geometry.",
    "customization/wheels/color": "Editing rim or wheel paint color.",
    "customization/paint/body": "Editing the main body paint color or paint finish.",
    "customization/paint/finish": (
        "Choosing a paint type or finish rather than editing its color."
    ),
    "customization/paint/part": (
        "Editing paint on a specific body component rather than the whole body."
    ),
    "customization/vinyl/catalog": "Browsing vinyl or decal designs and categories.",
    "customization/vinyl/placement": "Moving, rotating, scaling, or positioning a vinyl on a car.",
    "customization/vinyl/layers": "Choosing, ordering, copying, or removing vinyl layers.",
    "customization/vinyl/color": "Editing the color of a vinyl or decal.",
    "customization/plate": "Editing the license plate or plate text.",
    "performance/category": "Choosing a performance-upgrade system or component category.",
    "performance/upgrade": "Comparing or purchasing a specific performance upgrade.",
    "performance/tuning": "Adjustable performance tuning sliders or numerical setup values.",
    "performance/unlock-challenge": (
        "Locked upgrade requirement or challenge event to unlock a part."
    ),
    "betting/opponent-list": "Pre-race opponent roster where bets or challenges can be initiated.",
    "betting/cash-wager": "Negotiating, accepting, or adjusting a money wager.",
    "betting/pink-slip": "A car-ownership wager explicitly labeled pink slip or equivalent.",
    "betting/spectator": "Placing or viewing a bet while spectating other drivers.",
    "race/loading": "Loading screen or explicit loading indicator between game states.",
    "race/intro/venue": "Pre-race establishing shot of a venue or track.",
    "race/intro/grid": "Pre-race staged cars, drivers, grid, or starting lineup.",
    "race/intro/cinematic": (
        "An in-game aerial or trackside camera transition before driving, with no actionable UI."
    ),
    "race/countdown": "Starting countdown or GO prompt over the staged race.",
    "race/driving/circuit": (
        "Active race driving with laps or position, without a primary drift score."
    ),
    "race/driving/drift": "Active driving with a drift score, drift chain, or drift event HUD.",
    "race/driving/time-attack": (
        "Active driving with an explicitly visible time-attack goal or timer mode."
    ),
    "race/driving/elimination": "Active driving with an explicitly visible elimination mechanic.",
    "race/driving/other": (
        "Active player driving whose event subtype cannot be determined visually."
    ),
    "race/driving/spectator": (
        "Watching another driver's ongoing race with spectator controls or labeling."
    ),
    "race/pause": "Paused race menu over a race or track background.",
    "race/finish-overlay": (
        "Finish, win, lose, disqualification, or race-over announcement over driving."
    ),
    "results/standings": "Post-event finishing order, times, scores, or position table.",
    "results/challenge": (
        "Challenge result comparing target and achieved score or time, including package unlock."
    ),
    "results/payout": "Post-event prize, winnings, wager settlement, or money summary.",
    "results/podium": "Post-race podium or driver/car celebration scene.",
    "replay/playback": "Race replay camera view with replay labeling or playback controls.",
    "options/controls": "Control mapping, controller, steering, or input settings.",
    "options/audio": "Music, effects, speech, or audio volume settings.",
    "options/video": "Display resolution, graphics quality, or rendering settings.",
    "options/gameplay": "Difficulty, driving aids, transmission, or gameplay settings.",
    "options/other": "Options menu whose settings subtype is not readable.",
    "multiplayer/lobby": "Online or local multiplayer lobby, session list, or player roster.",
    "multiplayer/split-screen": "Two or more simultaneous player viewports.",
    "presentation/cutscene": (
        "Story, host, nightclub, or promotional cinematic without an actionable menu."
    ),
    "presentation/credits": "Game credits or staff roll.",
    "reference/creator-overlay": (
        "Uploader title card, webcam, video editor, or non-game presentation dominates."
    ),
    "reference/unreadable": "Black, obstructed, blurred, transitional, or unidentifiable image.",
    "menu/transition": (
        "An animated game menu background or icon transition with no readable active menu yet."
    ),
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
    "drift/banked-score": (
        "Is an explicit newly banked or completed drift score notification visible?"
    ),
    "drift/failure": "Is an explicit failed, broken, or lost drift notification visible?",
    "vehicle/sliding": (
        "Is the player's car visibly angled sideways relative to its course of travel?"
    ),
    "vehicle/tire-smoke": "Is tire smoke visibly emitted near a car's tires?",
    "vehicle/skid-marks": "Are tire skid marks visible on the road?",
    "vehicle/exhaust-flame": "Is a visible flame emitted from an exhaust?",
    "vehicle/nitrous-feedback": (
        "Is visible nitrous activation feedback present, such as labeled boost or boost flames?"
    ),
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
    "reference/uploader-overlay": (
        "Is an uploader watermark, webcam, subtitle, or external overlay visible?"
    ),
    "reference/letterbox": "Are substantial black bars around the game image visible?",
    "reference/low-readability": "Is game interface text too small or blurred to read reliably?",
}

CHOICE_ACCEPT = 0.85
CHOICE_MARGIN = 0.5
TAG_YES = 0.8
TAG_NO = 0.2


def questions():
    result = {
        "game_visible": {
            "type": "noul",
            "instructions": "Does `screenshot` visibly contain a game scene or game interface?",
        },
        "screen": {
            "type": "choice",
            "instructions": (
                "Which screen state best describes the active interface in `screenshot`?"
            ),
            "criteria": SCREEN_STATES,
        },
    }
    for name, criteria in FACETS.items():
        result[name] = {
            "type": "choice",
            "instructions": f"Which {name} is visible in `screenshot`?",
            "criteria": criteria,
        }
    for name, question in TAGS.items():
        result[name] = {
            "type": "noul",
            "instructions": question + " Judge only the pixels in `screenshot`.",
            "criteria": {
                "true": "The specified feature is visibly present in the image.",
                "false": "The image shows other content, or the specified feature is not visible.",
            },
        }
    return result

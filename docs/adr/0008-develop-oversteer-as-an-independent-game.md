# Develop Oversteer as an independent racing game

The user redirected Oversteer from reconstructing Juiced 2 to refining the
current game into an independent racing game. Remove Juiced 2 branding and use
the existing screenshots and reference resources as examples of a mature racing
game, rather than specifications to copy. Prioritize finishing the current
menus, cars, tracks, career progression and driving physics, including visual
glitches and other bugs.

This supersedes reference fidelity as the product acceptance requirement,
including the recovery-before-adaptation mandate in ADR-0002 and the obligations
in ADR-0003, ADR-0005 and ADR-0007 to preserve original event structure, handling
and performance ceilings solely for fidelity. It does not itself select new
physics, progression rules, technology or a different roster. Existing recovery
work remains historical evidence; matching it is no longer the reason to keep
a behavior that undermines Oversteer's quality.

The user accepted retaining usable imported assets for the refinement milestone,
replacing Juiced-branded presentation and identity-bearing content, and preserving
provenance. Establish a polished end-to-end career slice before expanding that
quality standard across retained content; content that cannot meet it may be
deferred. Target accessible arcade handling with believable weight, predictable
grip and controllable drifting, with freedom to change recovered equations.

Keep an urban tuner-racing atmosphere with a quieter presentation than Juiced's
loud menus. Career progression may be simplified, but betting and pink slips
must remain. Remove character customization and replace the current player
models with a basic premade character; additional characters are deferred.

The accepted first milestone uses three cars covering FWD, RWD and AWD, two
tracks, circuit and drift events, garage upgrades, betting, pink slips and
persistent tiered progression. Defer crew management, DNA/spooking and separate
sponsor progression. Preserve meaningful wager losses, last-car protection and
a no-stake earnings path. Use one fixed premade driver and retain the driver
name field. There are no existing player saves to migrate.

The [pivot interview](../design/OVERSTEER_PIVOT_INTERVIEW.md) records the accepted
decisions and the consolidated implementation and verification sequence.
Earlier reconstruction specifications and interview records describe the
previous direction wherever they conflict with this decision.

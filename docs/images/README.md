# README screenshots

Real, unretouched 1920×1080 captures of the Oversteer development build on Apple
Silicon with Godot 4.7.2 / Metal. These are game screenshots, not concept art.
Original runtime assets remain outside version control.

| Image | Scenario | Retained local source |
| --- | --- | --- |
| `london-race.png` | Active career race at input frame 960 (16 seconds), third place at 46 mph; normal chase camera and HUD, no camera/lighting/pose changes | `build/verification/readme-rivals/race-0960.png` |
| `pink-slip-stake.png` | Accepted Civic-versus-MX-5 bet through the career UI | `build/verification/readme-gameplay/accepted-stake.png` |
| `london-evo.png` | Evo on London Circuit, frozen race with inspection camera; not the gameplay chase camera | `build/verification/pivot-pipeline-revalidated/GT4_MITS0001/view-000-race-az045-el+10-roll+00.png` |
| `garage-menu.png` | Main menu, isolated fresh save, revision `9235d31` | `build/verification/pivot-pr-after/menu/final.png` |
| `pink-slip-win.png` | Career result: second overall, beat chosen rival Bobby Sawyer, awarded MX-5 | `build/verification/pivot-pink-finishes-accepted/pink-finish-win/final.png` |

The README now leads with gameplay, followed by the accepted stake and a completed
wager result. The inspection image and menu remain available as supplementary
images; they are no longer the README's lead demonstration.

The new race/stake images were captured at revision `9235d31` with the prepared
local runtime assets. Capture scripts, controller/UI plans, state snapshots and
SHA-256 identities are retained under `build/verification/readme-gameplay/` and
`build/verification/readme-rivals/`. The second run delays the recorded throttle
input by 90 ticks so rivals remain ahead; it does not inject poses or change the
camera, lighting, HUD or AI. Both processes used the background focus guard.
There were **18 new PNGs total** (8 in the first run, 10 in the second), including
incidental UI captures; only two were selected for the README. No images were
retouched or generated. These stills do not demonstrate driving feel or motion.
The result screenshot comes from the earlier completed race, not the delayed-start
capture run; no continuous sequence or new race-finish verification is implied.

The inspection and wager-result captures predate the menu capture. Their scenario
reports retain their own binary/content identities; they are not all asserted
to use the same build. See [implementation evidence](../game/PIVOT_STATUS.md)
for remaining visual and gameplay acceptance. Replacements should be real
captures with accurate captions, descriptive alt text and matching provenance.

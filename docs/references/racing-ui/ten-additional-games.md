# Ten additional racing-game UI references

Collected and visually inspected on 2026-11-04 in response to the request for ten more games. These are ten distinct titles, beyond the earlier DiRT Rally 2.0, SuperTuxKart and HexGL research. The images remain research evidence; none is shipped as Oversteer artwork.

| Game | Evidence | Applicable lesson |
| --- | --- | --- |
| Need for Speed ProStreet | HUD and event menu; secondary WSGF captures | Condensed telemetry and an event composition with a strong identity. |
| Midnight Club: Los Angeles | Pause and performance shop; primary designer portfolio | Panels composed around the car; clear upgrade stages and checkout state. |
| Burnout Paradise | Driving HUD; secondary WSGF capture | A distinctive boost-meter silhouette with an open central road. |
| WipEout Omega Collection | Driving HUD; secondary encyclopedia image | Consistent angular instrument shapes; image is too small for typography measurements. |
| Need for Speed Heat | Driving HUD; secondary WSGF capture | An open tachometer rather than a boxed numeric dashboard. |
| Need for Speed Unbound | HUD and boost animation; primary UI artist portfolio | Adjacent resource information and animation tied to an actual boost state. |
| Forza Horizon 5 | Driving HUD; secondary accessibility review | Strong digital hierarchy and route contrast; this capture uses the reviewer's personal HUD setup. |
| Forza Motorsport (2023) | Car selection and career menus; primary designer portfolio | Authored event posters, distinct from merely recolouring identical cards. |
| Gran Turismo 7 | Annotated race screen; official manual | Stable, separated groups of position, timing and vehicle telemetry. |
| Driveclub | Standard driving HUD; secondary GTPlanet capture | Low visual mass lets the car and road provide the spectacle. This is not the VR HUD. |

Exact source URLs, dimensions, provenance, inspection limitations and Jev judgments are recorded in [four-more-games-visual-evidence.md](four-more-games-visual-evidence.md), [hud-creative-research.md](hud-creative-research.md), and [menu-art-research.md](menu-art-research.md). The four images originally collected in `/tmp/oversteer-menu-reference` are also preserved in `visual-evidence/` as `gt7-hud.png`, `forza2023-cars.jpg`, `forza2023-career.jpg`, and `driveclub-hud.jpg`.

Two comparison sheets are in `output/reference-racing-ui/ten-games-1.jpg` and `ten-games-2.jpg`. Use the original images to inspect small text; the sheets are overview aids.

## Applied direction and verification boundary

The current implementation introduces original orange/cream/soot graphics, bundled OFL Barlow Condensed display typography, angled menu plates, a segmented RPM dial, event hero typography, car-adjacent selection controls, and short presentation transitions. A CC0 studio panorama supplies menu reflections. Their implementation sources and licenses are separate from proprietary game references.

The current title and Quick Race screenshots in `build/verification/ui-hud/researched-navigation/` show the new font, palette, event composition and car controls in the actual native renderer. Navigation assertions passed, including all 18 events, modal containment, binding cancellation and persisted binding reset. This establishes those specific observations, not completion of the full visual brief. Motion, remaining screen families, HUD extremes and a fresh adversarial review still require current-build evidence.

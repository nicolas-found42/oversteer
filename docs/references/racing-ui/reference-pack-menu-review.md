# Reference pack menu review

Scope: visually inspect PDF pages 13-18 and 25-30, then compare the existing settled native menu captures. Research/review only: no code edits, no native execution, no new captures.

Source PDF: `output/pdf/Racing_Game_HUD_UI_Reference_Pack.pdf`. Reviewed rendered pages in `build/verification/ui-hud/reference-pack-reread/`. The parent screened extracted page text with Jev; I inspected every assigned page image directly. This review does not certify the other 29 PDF pages.

## Complete assigned page coverage

| Page | Actual visible reference | Observation relevant to Oversteer |
| --- | --- | --- |
| 13 | Gran Turismo 7 garage | Car dominates a soft dark showroom; narrow specifications sit left, large labeled action icons below. Floor lighting gives the car a grounded pedestal without a large rectangular preview frame. |
| 14 | Assetto Corsa Competizione track selection | A real circuit photo dominates the selected track; map and historical copy support it. The bottom thumbnail rail is subordinate to the selected destination. |
| 15 | DiRT Rally 2.0 team offers | Horizontal car/driver image strip, condensed specifications below, diffuse colorful backdrop. Selected image edge is brighter than neighbors. |
| 16 | Need for Speed Unbound garage | Car and character inhabit a complete lit garage; only three low navigation labels compete with the scene. The environment carries much of the personality. |
| 17 | Mario Kart 8 Deluxe character selection | Dense portrait grid balances a large right-side kart preview; patterned background makes even empty space feel authored. Bright highlight and footer communicate selection. |
| 18 | Mario Kart 8 Deluxe parts | Bright selected slot, performance bars and preview coexist. Decorative blue pattern provides continuity without replacing useful information. |
| 25 | Assetto Corsa Competizione multiplayer | Three content columns mix actual race/car images and a red unavailable state. Real imagery is more distinctive than the column containers. |
| 26 | F1 24 play menu | Mode icon cards sit over a large purple map. Useful one-selection border/underline, but the repeated icon cards alone would not solve Oversteer's requested aesthetic. |
| 27 | DiRT Rally 2.0 freeplay | Asymmetric, differently sized photographic mode tiles; custom tile taller than neighbors. Color, depth and imagery carry the racing identity. |
| 28 | Need for Speed Unbound pause | Sparse left actions over a large car; oversized 4 DAYS typographic anchor on the right. Action hierarchy and progression hierarchy are visually distinct. |
| 29 | Need for Speed Unbound calendar | Huge TUESDAY lettering sits behind a car; lower grid and marked current day remain legible. Type/car overlap turns the upper half into a composition, rather than another panel. |
| 30 | Mario Kart 8 Deluxe ghost actions | Yellow selected action among pale rows; branded patterned ground. Pink instruction, arrow and outline are source-guide markup, not game UI. |

## Exact native evidence inspected

All paths below are under `build/verification/ui-hud/settled-navigation/`, not the earlier studio-navigation or researched-navigation directories:

- `title.png`: large cream condensed italic title, orange primary action, smaller Quick Race action, red Civic on the right, broad grey stage with hard floor/wall division.
- `utility-focus.png`: cream main labels; solid orange Career plate; Options has a thin orange outline; red Civic visible on right in my two direct image reads.
- `quick-dossier.png`: eight repeated event-list boxes, large CIRCUIT lettering, car in center, tall black right dossier with thin course contour and vertical metadata, orange Start Race action.

The car is not covered by the interface in my inspected versions. Orange and cream contrast clearly against soot. The car's paint reflections and big type improve the presentation; the broad flat grey environment and repeated form-like quick-race details remain the most conspicuous presentation-slide cues. These are settled stills, so no animation timing or input responsiveness is assessed.

### Resolved car-visibility inspection error

The parent reported seeing an empty grey stage in utility-focus. I reopened the exact absolute path and again saw the red car. Current reviewed utility file SHA-256: `0673e3963268538360f108f1ff754391042369c63925880104ed5035c5190639`; size 351,497 bytes; mtime epoch 1793819522.

A Pillow read of rectangle `(800,350)-(1800,850)` counted 103,078 pixels satisfying `R > 100`, `R > 1.5*G`, `R > 1.5*B`. Samples `(1200,600)=(174,46,50)`, `(1300,650)=(154,58,60)`, `(1600,600)=(151,62,66)`. The parent confirmed the same image/hash, reopened with original detail and saw the Civic. The discrepancy is resolved as a host image-inspection error, not a product preview defect. No preview-creation change is justified by this evidence. The pixel threshold supports the inspection but does not itself prove object identity; mesh-visible JSON alone would not prove visible pixels either.

## At most three concrete refinements

1. **Make the quick-race dossier an original event poster.** Use the existing right-side footprint for a cream paper field with a cropped oversized `01`, a strong orange course contour, and compact dark metadata along one lower edge. Keep the actual fields and the orange Start Race action; keep the center car unobstructed. Borrow the compositional principle of page 29's giant type/car layering and page 14's destination-specific imagery, not their artwork. This changes the dossier from a form to an authored racing object. A printed number/course motif is a more direct stylistic step than adding another accent line.

2. **Turn the grey stage into a deliberate photographic backdrop.** Within the menu-only environment, make the upper background substantially darker, soften the hard floor/wall division, and confine the brightest floor area to a broad pool beneath the car. Retain its contact shadow and reduce the large near-white hood/roof reflection so red paint and body planes remain readable. Page 13 supplies the clean showroom principle; page 16 supplies selective light and material depth. Preserve camera framing and mesh visibility. Do not hide the model behind fog, vignette or new props.

3. **Let the actual focused action own the racing stripe.** In utility-focus, Career's solid orange currently outranks the outlined Options state. Move the main orange plate emphasis to the true focused action, using a compact cream chevron/diagonal cut as its signature, and let the inactive primary mode return to cream type. Keep the existing action order and hit regions. Pages 17,18,30 support one unmistakable highlight; page 28 supports sparse action lists over the car. This avoids turning every row into a permanent panel and makes the visual system feel reactive rather than like a static slide.

The first two are the main style changes. The third corrects the state hierarchy and gives the graphic motif a functional role. None requires proprietary assets or changes to racing physics/camera.

## Judgment evidence and limitations

A dense transcript covering all twelve pages and all three native images was screened with Jev and four observation records passed audit with zero flagged records. This audits text against the visual transcript, not the underlying pixels. A separate ranking placed the event-poster idea first (0.63 relevance), then sculpted staging (0.41). Other candidates scored low; adding panels was not adopted. The focus refinement is retained on direct visual state-hierarchy evidence rather than presented as a highly ranked aesthetic result.

Remaining verification belongs to implementation: preserve visible car and all actions after any styling edit; inspect actual focus transitions and the smallest supported viewport. The utility PNG disagreement is resolved. This review ran no Oversteer session and makes no new runtime-success claim.

# Racing menu art direction and motion research

Research date: 2026-11-04. Scope: menu composition, typography, staging, motion and licensed source assets. This note proposes presentation experiments; it does not claim that any addon has been run in Oversteer's Godot 4.7/Metal build. No gameplay, AI, physics or racing-camera changes are proposed.

## Direction

Make the menu feel like entering a motorsport broadcast and choosing an event in a living garage. The existing orange/cream/soot direction and condensed italic typography can work, but color and angled rectangles alone cannot supply the missing theatrical depth. Prioritize a large car silhouette, strong foreground/background overlap, one unmistakable selection, and a coordinated response when that selection changes.

This is an original implementation direction, not permission to copy another game's artwork. DiRT Rally 2.0 UI artist Talía Gual describes strong typography, a flexible grid, smooth animation and particles over the game; Michael Murphy independently describes implementing the front-end with consistent art and smooth animation. These are first-person process references, not source packages. Their images, branding and videos are inspiration only; no reuse license was established. [Gual's project](https://taliagual.com/portfolio/dirtrally2/), [Murphy's project](https://murphy5.artstation.com/projects/W28Qd2).

## Eight useful candidates

| Candidate | Status and source | Why it changes the experience | Native proof to require |
| --- | --- | --- | --- |
| 1. Selection choreography with native Tween | Built-in engine mechanism. Sequential and parallel interpolation are documented; avoid simultaneous owners of one property. [Tween](https://docs.godotengine.org/en/stable/classes/class_tween.html) | Selection becomes an event: plate accelerates into position, heading reveals through a mask, secondary details follow, and the preview changes on the same beat. | Hold navigation, reverse direction mid-transition, switch pages repeatedly. Final focus and displayed content must agree; no accumulated offsets or stale callbacks. |
| 2. Procedural editorial graphics | Built-in CanvasItem drawing supports custom controls and animated shapes. [Custom drawing](https://docs.godotengine.org/en/stable/tutorials/2d/custom_drawing_in_2d.html) | Replace equal-weight dashboard boxes with an original track contour, clipped giant event numerals, sparse registration marks and a single consistent diagonal system. These supply hierarchy, scale contrast and recognizable racing context. | Render at small and large windows. Inspect the actual longest labels and clipped shapes. Controls must retain valid hit/focus areas. |
| 3. A staged garage with the actual car | Native WorldEnvironment controls ambient light, tone mapping and effects; camera attributes handle exposure and depth of field. [Environment documentation](https://docs.godotengine.org/en/stable/tutorials/3d/environment_and_post_processing.html) | A substantial vehicle, dark silhouette, controlled rim light and floor contact create real depth. Prefer a menu-only stage or preview world to coupling this to the racing camera. | Inspect vehicle silhouette and paint highlights in the native renderer. Confirm the menu stage disappears on race entry and has no effect on race exposure or camera. |
| 4. Scoped shader finish | Native full-screen CanvasLayer/ColorRect/ShaderMaterial pass can sample the screen. [Custom postprocessing](https://docs.godotengine.org/en/stable/tutorials/shaders/custom_postprocessing.html) | A restrained reveal, directional sweep or fine background texture can bind the composition together. Keep readable text outside aggressive grain, distortion and blur. | Toggle the effect in a native capture; reject if it masks weak composition, reduces type clarity or causes visible aliasing. Profile the pass at the real window resolution. |
| 5. TweenFX | MIT, advertises Godot 4, offers snap/pop/bob/stop functions and a release demo/tutorial. [Repository](https://github.com/EvilBunnyMan/TweenFX) | A compact source of tactile focus feedback and repeatable motion primitives. Best used selectively for focus and confirmation, not constant bouncing. | Run its demo under this project's exact engine first. Prove interruption and node teardown work. Keep its MIT notice; audit bundled demo fonts separately before copying them. |
| 6. Anima | MIT; offers declarative sequences, parallel animation, grids and reusable keyframes. However, the awesome list groups it under Godot 3. [Repository](https://github.com/ceceppa/anima), [list placement](https://github.com/Calinou/awesome-godot#godot-3) | Interesting choreography reference when authoring complex staggered pages. Compatibility evidence is insufficient to recommend immediate adoption. | Identify a Godot 4 release/branch and run a representative page; otherwise use native Tween. Do not infer compatibility from feature descriptions. |
| 7. GDQuest shader demos | Executable shader examples; repository explicitly warns that its Godot 4 port is in progress. [Repository](https://github.com/gdquest-demos/godot-shaders) | Useful technique references for masking, reflection, glow and transitions. Adapt one justified technique rather than importing a general effects pack. | Check the chosen example's source/license and port state, then run it on Metal. Repository-wide licensing was not resolved in this research; do not copy source until checked. |
| 8. Licensed staging assets | Poly Haven HDRIs/materials/models are CC0; Kenney Racing Kit is CC0. [Poly Haven license](https://polyhaven.com/license), [Kenney pack](https://kenney.nl/assets/racing-kit) | A suitable HDRI/material can improve reflection structure and surface quality. Kenney props can help a deliberately stylized garage, but are not automatically a fidelity improvement. | Compare the existing car before/after under identical framing. Inspect material scale, reflections, memory and import size; avoid replacing an established art style with mismatched props. |

Poly Haven's asset license excludes its website content and example renders. Use actual downloadable assets, not preview images scraped from its pages. Preserve source URLs in the asset manifest even where attribution is optional.

### Specific showroom reflection resource

Start with [Studio Small 08](https://polyhaven.com/a/studio_small_08), by Sergej Majboroda. The primary listing describes neutral, low-contrast studio illumination with large softboxes/octabox highlights and 6000K white balance. This is a suitable candidate for clean paint reflections rather than outdoor city imagery; final suitability requires the native car render. The asset is CC0 under the [Poly Haven asset license](https://polyhaven.com/license).

| Variant | Exact download | HEAD validation on 2026-11-04 | Server-provided SHA-1 |
| --- | --- | --- | --- |
| 1K EXR, preferred first trial | [studio_small_08_1k.exr](https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/1k/studio_small_08_1k.exr) | HTTP 200; 1,033,507 bytes | `6665c249380b45052e7ae2453aaf3f455537e7f4` |
| 2K EXR, if reflection detail needs it | [studio_small_08_2k.exr](https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/2k/studio_small_08_2k.exr) | HTTP 200; 3,766,354 bytes | `f7ddc9d79070d1390acd2820ef1319cc3e51b6ff` |

The listing has no semantic asset-version identifier. Record the selected filename and verify the downloaded bytes against the server-provided hash before committing provenance. The HEAD checks establish availability and declared size/hash, not a successful Godot import. Use this for the menu environment only, rotate for a readable body highlight, and preserve the race environment. A restrained separate rim light may add separation; do not brighten the whole UI to compensate for flat vehicle materials.

## Visual evidence

Collected and pixel-inspected on 2026-11-04 around 18:52 UTC. These are source-owned reference images, not Oversteer captures. Local paths are temporary research copies for immediate review; the direct source links are the durable references. No proprietary artwork is licensed for implementation by this collection.

| Visual | Provenance and usable image | Dimensions | Classification and useful observation |
| --- | --- | --- | --- |
| DiRT Rally 2.0 actual screen montage | [Direct image](https://taliagual.com/wp-content/uploads/2019/02/dr25-1.jpg); [UI artist portfolio](https://taliagual.com/portfolio/dirtrally2/); local `/tmp/oversteer-menu-reference/dr25-1.jpg` | 1500 × 6263 | Actual game screen montage: menus, vehicle select, service-area car stage, racing HUD, results and map/loading views. The service-area frame is especially useful for a large car sitting behind sparse menu navigation. The whole montage is long, so inspect it at full resolution before judging text size. |
| DiRT Rally 2.0 HUD/component sheet | [Direct image](https://taliagual.com/wp-content/uploads/2019/02/dr232.jpg); same artist portfolio; local `/tmp/oversteer-menu-reference/dr232.jpg` | 1500 × 1091 | Authored component presentation, not a live gameplay screenshot. Shows dial hierarchy, hand-drawn co-driver symbols, colorblind alternatives and controller icons. Useful evidence of a coherent graphic language beyond rectangular panels. |
| DiRT Rally 2.0 art-direction sheet | [Direct image](https://taliagual.com/wp-content/uploads/2019/02/DR22.png); same artist portfolio; local `/tmp/oversteer-menu-reference/DR22.png` | 1500 × 1355 | Moodboard, type, colors and grid diagrams; **not a shipped menu screenshot**. Useful process evidence for large italic typography and controlled image/graphic relationships. Its source imagery and fonts must not be assumed reusable. |
| TweenFX motion-demo GIF | [Stable source attachment](https://github.com/user-attachments/assets/c3731804-9a2d-478e-bdc4-a8c2b362a9d2); [source README](https://github.com/EvilBunnyMan/TweenFX); local `/tmp/oversteer-menu-reference/tweenfx.gif` | 634 × 357 | Animation-library demo, **not racing UI**. Inspected first frame shows the named effect-button grid. The GIF can illustrate motion vocabulary, but a still frame does not verify timing, interruption, or Godot 4.7 behavior. |

The portfolio was also captured as a full-page Firecrawl browser screenshot with a requested 1440 × 1000 viewport (scrape ID `01a1a7e6-8852-72a0-b581-106511f7a9b8`). Its signed storage URL expires, so prefer the direct images above. No full-page screenshot dimensions are claimed. Web image-open access failed for two direct images; ordinary source downloads and local image inspection succeeded for all four references. No Oversteer build or game session was run.

A dense visual transcript was screened and the three classification records were audited by Jev: pass, zero flagged. This only checks consistency of text derived from the inspection; Jev did not inspect or independently verify the pixels. Native execution and motion quality remain unverified.

## Concrete composition experiment

The following numbers are proposed art-direction starting points, not facts claimed by the sources:

- Give the car roughly half the composition and let it overlap a large background event number. Crop deliberately at an edge rather than shrinking everything into a safe central rectangle.
- Reserve one side for a short vertical event list. Make the active row materially larger and show its event-specific metadata only once. Avoid presenting every choice as a fully populated card.
- Put the strongest cream/orange contrast on the selected event and primary action. Keep the garage and decorative telemetry quieter.
- Enter with a 400–650 ms overall reveal. Stagger supporting layers by around 30–60 ms. Respond to selection within 100–180 ms, while a slower preview/light movement can settle behind it.
- Use three rates of motion: immediate input feedback, a brief coordinated selection transition, and slow atmospheric motion. Constantly animated text and unrelated floating panels would compete with the car.
- A menu-only camera drift or vehicle presentation turn should be subtle enough that the selected label remains the visual anchor. Do not alter the racing camera to create menu spectacle.

The design should remain identifiable and navigable in a still image. Motion should clarify what changed rather than compensate for an unclear hierarchy.

## Dependency decision

[Awesome Godot](https://github.com/Calinou/awesome-godot) was a discovery starting point; its placement of Anima under Godot 3 demonstrates why list membership is not compatibility proof. Native Tween, custom drawing and environment resources cover the first experiment. TweenFX is the most direct optional helper of those examined. Defer Anima and wholesale shader-pack imports pending exact-engine execution.

Jev semantic ranking placed native selection choreography first (0.89 relevance), procedural graphics second (0.87), shader finish third (0.84), and staging fourth (0.83). These close scores are advisory prioritization, not a measured visual-quality result. A bounded Jev decision selected native stage/motion over library-first or static asset swaps, with no contradicted requirements. This supports starting with a concrete native scene while retaining dependencies as tools when they earn their integration cost.

## Verification budget for an implementation pass

Use one continuous native recording covering entry, several interrupted selection changes, page/back navigation and race launch, plus two deliberate still captures: settled menu and representative alternate selection. Count exploratory captures against that budget; add more only to investigate a specific defect.

Check rendering in the actual Godot/Metal runtime, using the project's focus-preserving verification path. A web mockup or screenshot of the reference game cannot establish native animation quality. Record frame timing before/after shader or preview changes and test mouse plus keyboard/controller focus. Inspect the car lighting, heading glyphs, clipping and active action at the smallest supported size. Retain a readable static or reduced-motion state if the project already exposes such a preference.

Research validation: fetched source batches were screened with Jev before use. One batch was rejected as off-purpose and excluded. Seven factual capability/license/compatibility claims were then checked against retained source text: all seven verified, none contradicted or unsupported. Native execution, exact addon-version compatibility and final visual quality remain unverified; this document is research only.

## Three additional games: actual HUD/menu evidence

Collected and pixel-inspected 2026-11-04, approximately 18:54–18:57 UTC. These add three distinct games beyond DiRT Rally 2.0; no reference here counts an engine demo or concept as another game. All are copyright reference material, not implementation assets. Still images do not establish animation quality.

### Gran Turismo 7

Primary source: [official online manual, The Race Screen](https://www.gran-turismo.com/us/gt7/manual/race/02). [Exact image](https://www.gran-turismo.com/images/c/i1B1lEMx5qJnOb.png); local `/tmp/oversteer-menu-reference/gt7-hud.png`, 1920 × 1080.

This is an actual race HUD screenshot annotated for documentation. The large blue numbered circles are **manual callouts**, not shipped HUD elements. Inspection shows position and standings left, map top right, speed/gear low and central, and peripheral dials. Applicable lesson: assign stable spatial homes to information and preserve the road center. This is a HUD clarity reference, not evidence of lively menu motion or an art style to copy wholesale.

### Forza Motorsport (2023)

Primary source: [Dane Egenes, Video Game Art & Design](https://daneegenes.artstation.com/projects/lVK3kG), explicitly labels both images as Forza Motorsport 2023 menus. Other images on that same portfolio include unused older-game concepts; those are not used here.

| Screen | Exact source image and local inspection copy | Dimensions | Observed lesson |
| --- | --- | --- | --- |
| Cars / Buy Cars | [Image](https://cdnb.artstation.com/p/assets/images/images/089/628/141/large/dane-egenes-motorsport11.jpg?1751474602); `/tmp/oversteer-menu-reference/forza2023-cars.jpg` | 1919 × 1079 | Selected green Porsche gains amber outline while other cars dim; specifications occupy a dedicated right panel. Useful selection hierarchy and consistent controller prompts, but the grid is not itself the answer to the user's rejection of dashboards. |
| Career / Tours of Motorsport | [Image](https://cdnb.artstation.com/p/assets/images/images/089/628/057/large/dane-egenes-motorsport27.jpg?1751474476); `/tmp/oversteer-menu-reference/forza2023-career.jpg` | 1919 × 1079 | Large Retro Tuners, Classic Sport and Exotic Speed posters combine different typographic treatment, car cutouts and graphic environments. This is the strongest menu composition reference of this batch: cards contain authored event identities rather than the same rectangle recolored. |

Suggested original application: one hero event poster built from Oversteer's own car/track imagery, huge event name and a restrained graphic motif. Keep the navigation system consistent while allowing the selected event's composition to have character. Do not copy Forza's poster artwork, marks or vehicle images.

### Driveclub

Secondary actual-gameplay evidence: [GTPlanet's Driveclub/VR comparison](https://www.gtplanet.net/french-virtual-reality-preview-gives-a-glimpse-at-driveclub-vr/). [Exact standard-HUD image](https://www.gtplanet.net/wp-content/uploads/2016/03/DRIVECLUB%E2%84%A2_20160321153151-638x359.jpg); local `/tmp/oversteer-menu-reference/driveclub-hud.jpg`, 638 × 359.

The publisher is a secondary games publication; its caption identifies the selected image as the standard HUD in traditional Driveclub. The same article has a separate VR image, which is not counted here. Pixel inspection shows a chase-view car on a wet road, position upper left, progress upper right, map lower left, circular speed and gear lower right. Lesson: low visual mass and edge placement let the actual car/world provide the spectacle. Limited resolution prevents fine typography assessment.

Primary-source limitation: [UI designer Kevin Middelbos's Driveclub portfolio](https://www.behance.net/gallery/5855101/DRIVECLUB-(PlayStation-4)) establishes his UI/experience-design involvement but the retrieved project offered an announcement trailer, not a usable shipped HUD still. It is therefore not cited as proof of the secondary screenshot's pixels. No substitute game was necessary because an inspectable, clearly labeled actual Driveclub HUD was obtained.

All fetched batches were screened before use. A dense inspection transcript and three classification records passed Jev audit with zero flagged records; this checks textual consistency, not pixels. Jev ranked the Forza career-poster lesson highest for this user's menu request (0.81); the car-grid lesson scored 0.40 and the two HUD lessons lower. These scores guide relevance, not objective visual quality. No Oversteer runtime was executed.

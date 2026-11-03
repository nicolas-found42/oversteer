# Source-model sprite generator

Oversteer now bakes its car artwork from the retained carmodels 3D meshes. The
procedural CarVisual grammar, CPU rasterizer and appearance fitter are retired.
Gameplay selects a source-model identity and displays its baked steering poses;
it makes no Jev or network requests.

The source is [nicolas-found42/carmodels](https://github.com/nicolas-found42/carmodels/tree/ce047799fc550cdf92e4f7b62d97ef5c603e53ad)
at `ce047799fc550cdf92e4f7b62d97ef5c603e53ad`. The 1,435-entry ledger accounts for
**904 included cars/trucks and 531 exclusions**: 35 Ford Racing 2, 730 Gran Turismo 4,
79 Midnight Club 3 Remix and 60 Midnight Club Los Angeles player/DLC cars.
All Redline, Gran Turismo 1 and native Midnight Club ambient traffic are excluded,
as are motorcycles, trailers, buses and nonvehicles. Native `va_` traffic is separate
from `vp_`/`vpd_` player packages; police names alone do not establish traffic.
Scope guards apply even when a stale manifest marks an excluded source as included.

## Use and reproduce

In the menu, press **G** to choose a vehicle; arrow keys page, click selects, Escape
returns. Command-line selection is explicit:

```sh
build/release/oversteer --list-models
build/release/oversteer --model GT4_DODG0005
```

Set up Python with the pinned dependencies in `requirements.txt`. The current
verified environment uses Python 3.15, NumPy 2.5.4, Pillow 13.0.0, Node 22+ and
Blender 5.2.2 LTS. Native builds also require the project's raylib toolchain.

```sh
python3 -m venv build/carmodels-venv
build/carmodels-venv/bin/python -m pip install -r tools/carmodels/requirements.txt
make carmodels-train       # compatibility name: offline restore, profiles and checks
make carmodels-sprites     # fetch pinned included GLBs, bake, package and check
make carmodels-calibrate   # rerun the optional production-solver candidate grid
```

`data/carmodels/manifest.json` verifies research inputs, profiles, judgments and all
904 distributed sprite atlases. `OVERSTEER_CARMODELS_WORK` selects an independent
artifact directory. Normal validation uses saved decisions and needs no provider
key, Blender or network. Re-baking downloads only included, checksum-pinned GLBs;
it runs pure vendored material correction code, then Blender. No source-repository
scripts are executed. A temporary clone is not required.

Each atlas has thirteen 256×256 frames: source front-wheel angles −60° to +60° in
10° steps. Nine explicit per-pose mip levels, averaged offline in linear light without
intermediate quantization, prevent cross-pose bleed and darkened fine detail. The game uses
premultiplied sRGB RGBA8 blending. The CPU exporter reads exactly the same PNGs:

```sh
build/tests/oversteer_tests --dump-corpus-cards artifacts/corpus-cards
build/tests/oversteer_tests --dump-corpus-sheet artifacts/gallery
build/tests/oversteer_tests --vehicle-card data/carmodels/profiles/F350.txt artifacts/f350
```

`tools/visual/` provides search, source filters, paging, magnification and physics
inspection. Its images use straight alpha for browsers. Physical scale is shared
across cars, with finer detail rendered at native window resolution.

## Bake and refinement

Only the GLB's selected scene is imported; unreachable nodes and alternative LODs
cannot pile into the bake. The source viewer's documented Ford helmet/ground and
GT4 overlay exclusions are applied. The pinned GT4 material correction restores
paint coverage and uses the viewer's explicitly provisional neutral glass fallback.
Geometry, texture images and variant mappings are otherwise retained.

The adopted recipe renders **512 pixels / 16 Cycles samples**, then box-averages to
256 pixels in **linear light with premultiplied alpha**. Source textures and vertex
colours remain emission inputs. Unlinked flat material colours receive
geometry-derived ambient occlusion, revealing otherwise featureless surfaces.
Applying occlusion everywhere was rejected because it darkened existing texture
detail. Studio lighting was also tested; it shifted paint brightness and produced
noise. These are explicit presentation choices, not reconstructed native shaders.

The experiments include:

- 96 valid initial image calls: counterbalanced material comparisons and 64 known
  negative controls (flip, geometric squeeze, blank and desaturation). Sixteen
  earlier malformed squeeze controls are recorded separately and excluded.
- 2,560 sampling measurements: 32 cars × four resolutions × five filters × two
  colour spaces × two alpha methods, against 1024px/64-sample source projections.
- 88 live sampling-refinement calls with Choice, Score, Noul and Box; identical,
  blank and blurred controls accompany development and held-out comparisons.
- Five shading treatments on 32 cars, including a new 16-car held-out set, and
  88 further image calls. Source colour and surface shape are judged separately.

The initial unlit study reduces mean held-out combined colour/coverage error by
about 90% at 256px and 36% at 128px. A separate study of the final material recipe
and explicit linear-light mipmaps reduces error by approximately **87% at 256px**
and **93% at 128px**, against direct 256px rendering with GPU-generated mips.
These are different held-out sets and controlled sampling measurements. Per-car
values and limitations are in `data/carmodels/sprite-refinement-report.json`.
The frozen decision-input snapshot in `sprite-refinement.json` preserves its
original evidence; a rendered-file counter erratum is recorded in the current report. This measures sampling fidelity to a
controlled Blender projection, not authenticity of native game rendering.
Fractional trilinear sampling and rotated geometry still require native captures.

Jev favours refined sampling in 50/64 detail and 50/64 edge comparisons, but most
differences are subtle or uncertain. Bounded shading has mixed votes; pale geometry
becomes more readable while fully textured surfaces often stay visually identical.
There is **no universal perceptual-win claim**. The deliberately overbroad claim
was rejected. Raw probability distributions, exact image-bearing requests, controls,
receipts and rejected experiments remain under `WORK/sprites/`.

All twelve Jev tools contribute to the offline workflow:

| Capability | Role |
|---|---|
| screen | Inspect fetched viewer code and image transcripts before adoption |
| find | Locate the material rule that explains recovered ground geometry |
| rerank | Check source relevance independently of the single-best selection |
| extract | Select verbatim native and corrected alpha cutoffs |
| audit | Cross-check extracted facts and dense image observations |
| verify | Check scene-selection rules, measured claims and stated limits |
| compare | Distinguish stored material facts from different preview treatments |
| classify | Separate cabin steering controls from road-wheel assemblies |
| noul | Assess pilot defects, presence, visible differences and uncertainty |
| decide | Choose material, sampling and bounded shading policies |
| review | Review actual code changes with real validation logs |
| gate | Check the final patch and completion claims against evidence |

`sprite_judgments.py` contains semantic questions and the adoption truth table;
`refinement_live.py`, `shading_experiments.py` and `refinement_report.py` contain the
experimental questions. Saved typed answers are consumed by the baker. Invalid,
escaped, stale or unresolved consequential answers fail closed. Root inspections
are explicit and bound to request hashes. Image judgments advise; exact scope,
hashes, geometry, alpha coverage and arithmetic stay in code. Box estimates never
crop images or override known mesh/alpha bounds.

Live calls use the pinned public Jev MCP library and `typesafe/jev-1.14` through the
configured OpenRouter provider, including the experimental image endpoint. The
shared runner reserves cost before calls and retains exact requests/responses.
Credentials stay outside artifacts. The authorized session cap is **$5**.

```sh
npm ci --prefix tools/carmodels
build/carmodels-venv/bin/python -m tools.carmodels.sprite_judgments sources
build/carmodels-venv/bin/python -m tools.carmodels.refinement references
build/carmodels-venv/bin/python -m tools.carmodels.refinement compare
build/carmodels-venv/bin/python -m tools.carmodels.refinement production
build/carmodels-venv/bin/python -m tools.carmodels.refinement_live --run
build/carmodels-venv/bin/python -m tools.carmodels.shading_experiments --run
```

The reference stage writes `WORK/sprites/refinement/reference-jobs.json` for
Blender. `shading_experiments --prepare` writes all five shading treatment jobs.
Render these with the same Blender invocation as the main bake, substituting the
job path. Live experiment stages require their saved render inputs. Keep source intake and review separate from adoption; inspect review
results before passing observations to subsequent stages.

## Physical references and limitations

A source-model identity lives beside `VehicleSpec`, outside simulation checksums.
Choosing a model loads its researched profile. Tuning retains the selected artwork.
Profiles preserve the optional `# carmodels.model = CODE` presentation comment;
legacy profiles retain the current appearance. Invalid or duplicate tags reject
loading. This `Game`/entry-point-table change requires a full platform rebuild and
restart before hot reload. See the [identity contract](../../docs/design/CAR_APPEARANCE_IDENTITY.md).

Images uniformly follow physical overall length and the physical CG; mesh
proportions are preserved. Mirrors may extend beyond a reported body-width
convention. Source materials and geometry can be incomplete: some Midnight Club
cars remain neutral white, native glass colour/lighting is unavailable, one source
has no separable named front-wheel assembly, and another has a single assembly.
No wheels, paint, glass or body panels are invented to conceal those gaps.

Every one of the 138 writable physics fields has a documented outcome for every
included vehicle. Many values remain estimates or model priors, and nearby
production-trim proxies are labeled. Hardware fields retain their existing solver
roles. Three-wheel contact, up to eight gears and an equivalent CVT cover observed
requirements; the CVT is an approximation, not a planetary/battery simulation.

The retained physics calibration reduces manufacturer-family-held-out published
performance log loss by 27.3% across 673 entries / 67 groups under the recorded
solver protocol. Test conditions and proxy targets limit that result. The 1886
Benz's target-informed reduction is excluded from the independent held-out metric.
`physics-fit.json` records candidates, folds, coefficients and uncertainty.

Secondary numerical references include
[gor3a/vehicle-makes-models](https://github.com/gor3a/vehicle-makes-models/tree/ee99776470a45214bf524cdfe22e5dbf4bd67f93),
compiled from Autoevolution and licensed under ODbL 1.0. Source URLs, original
numerical strings, JSON pointers, quality flags, proxy identities and other source
classes remain in the research data. Full articles, credentials and GLBs are not
bundled; generated 2D sprite atlases are game assets under `resources/vehicles/`.

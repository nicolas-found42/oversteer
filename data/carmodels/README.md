# Included carmodels data and sprites

Pinned source: [nicolas-found42/carmodels](https://github.com/nicolas-found42/carmodels/tree/ce047799fc550cdf92e4f7b62d97ef5c603e53ad).
The ledger accounts for 1,435 entries: 904 retained cars/trucks and 531 exclusions.
All Redline, Gran Turismo 1, native Midnight Club ambient traffic, bikes, trailers,
buses and nonvehicles are excluded from baking, experiments and the runtime catalog.

`sprites.json` records source hashes, material/sampling recipes, wheel assemblies,
thirteen steering poses per vehicle and atlas checksums. The actual premultiplied
RGBA PNG atlases live in `resources/vehicles/`. `sprite-judgments.json` and
`sprite-refinement.json` preserve typed Jev decisions and explicit adjudications.
`sprite-refinement-report.json` contains the current measurements and limitations;
`sprite-mip-decision.json` records adoption of explicit linear-light mip levels. Rendering uses linked source textures/vertex colours
and bounded geometry shading on flat material colours. Native lighting and missing
glass colours are not reconstructed.

`profiles/` contains all 904 researched tuning profiles, with separate source-model
identity comments. `sources.jsonl` preserves selected factual references, original
numerical strings, URLs and quality limits. Nearby production-trim substitutions
are labeled; unknown physics fields remain estimates or priors. Every writable
field's evidence is reproducible under `WORK/field-research.jsonl`.

`manifest.json` verifies data, profiles and sprite assets. Run `make carmodels-train`
for offline restoration and validation, or `make carmodels-sprites` to fetch pinned
included GLBs and rebuild the sprites with Blender. See the
[workflow](../../tools/carmodels/README.md) for experiments, all twelve Jev roles,
commands, solver calibration, source limitations and budget accounting.

The secondary specification compilation is
[gor3a/vehicle-makes-models](https://github.com/gor3a/vehicle-makes-models/tree/ee99776470a45214bf524cdfe22e5dbf4bd67f93),
compiled from Autoevolution and distributed under
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/).
Selected records retain attribution and original JSON pointers. Other manufacturer,
museum, club and specialist facts retain their own source classes and URLs.
Full articles, credentials and GLBs are not distributed here.

# Source-model sprite results

The procedural CarVisual renderer and fitter have been replaced with sprites baked from all **904 retained carmodels cars and trucks**. All Redline, Gran Turismo 1, native Midnight Club traffic, bikes, trailers, buses and nonvehicles are excluded.

There are **11,752 source-wheel poses** with nine explicit linear-light mip levels each (**105,768 nonempty pose/mip images**). The 904 PNG atlases occupy 176,772,782 bytes. Physical screen scale and the top-down camera are preserved; source identity is independent of physics and survives profile save/load.

## Experiments and adopted settings

All twelve Jev tools participate in source intake, selection, field auditing, wheel classification, material/sampling decisions, code review and completion gating. Choice, Score, Noul and Box were exercised through **272 valid live image experiments**, with counterbalanced comparisons, negative controls and separate held-out sets. The sampling grid contains 2,560 measurements.

The final recipe renders 512px / 16 samples, preserves linked texture and vertex-colour inputs, and uses geometry-derived occlusion on unlinked flat material colours. It builds 256px→1px mip levels by averaging linear-light premultiplied colour without intermediate quantization. Each pose has its own GPU mip chain.

| Display size | Direct 256px / GPU mips error | Actual packed refinement error | Reduction |
|---|---:|---:|---:|
|128px|0.00020880|0.00001555|92.6%|
|256px|0.00040243|0.00005376|86.6%|

These are mean held-out linear-colour/coverage errors against controlled 1024px source projections. They measure sampling fidelity under the recorded compositing approximation. Jev's perceptual votes are mixed and often uncertain; no universal aesthetic improvement is claimed. The frozen decision input has a documented rendered-file counter erratum; the current report counts 160 shading candidate renders.

## Verification

- C suite: 116 scenarios, 114,979 checks, 0 failures.
- ASan/UBSan: 116 scenarios, 114,979 checks, 0 failures.
- Python: 21 tests pass. Browser inspector: 4 tests pass.
- Fresh offline restoration, all 904 profile roundtrips, set/hash checks and full pipeline pass without API calls.
- All 11,752 final source frames are nonempty and clear of the image boundary.
- Native captures confirm 256px textures with 9 mipmaps. The baker worker hash matches all 904 recipes.
- All 46 telemetry comparisons against the original build pass.
- Changed-file formatting/lint and diff whitespace checks pass. Pre-commit normalized the existing core_tests.c formatting and the physics-fit.json final newline.

Jev's final gate verifies all six completion claims, but its overall code-review action remains **escalate** (safe-to-apply 0.30; composite 0.589). The root agent inspected the flagged boundaries and resolved the two low-confidence claims through exact set/decoding checks and retired-file/build-symbol checks. Full judgments and the explicit root sign-off are in [sprite-review.json](sprite-review.json).

## Limits

Some reconstructed materials remain neutral white; native glass colours and original game lighting are unavailable. Geometry-derived shading exposes existing surfaces without inventing missing paint, glass or panels. One source has no separable front-wheel assembly; another has one. Physics profiles retain labeled nearby-trim references, estimates and model priors.

Native captures were inspected. Native picker mouse/key interaction could not be automated because Cua could not address the unbundled executable; its event path was inspected, all 904 selection/profile backends were exercised, and browser controls passed. Windows hot reload was not exercised on this Mac; the Game/API layout change requires a full rebuild and restart.

The shared budget records **$1.84 accounted/reserved of the authorized $5 cap**. Gameplay uses the baked assets offline.

See [current measurements](sprite-refinement-report.json), [catalog validation](validation.json), [workflow](../../tools/carmodels/README.md), and [native gallery capture](../../artifacts/carmodels-research/sprites/final-native-gallery.png). Press **G** from the menu to choose a model, or launch with `--model CODE`.

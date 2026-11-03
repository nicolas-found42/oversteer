# Shared donor preparation helpers

The native Rust/Godot asset pipeline imports `assets.py` for hash verification,
selected-scene GLB decoding and composed node transforms. `preview_materials.mjs`
uses the pinned donor viewer's GT4 material corrections in `source_viewer/`.
`scope.py` records the donor source and ambient-traffic exclusions.

Use [the native asset workflow](../game/assets/README.md) to fetch the accepted
30 donors, prepare 3D assets, and verify them. The retained numeric profiles and
source attribution are described in [data/carmodels](../../data/carmodels/README.md).

Run the shared helper tests through `uv run --frozen python tools/game/dev.py check`.

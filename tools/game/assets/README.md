These tools prepare the accepted 30 donor cars and recover supporting content from
the supplied Juiced 2 Xbox 360 ISO. The original game car bodies are never used as
playable replacements. Source metadata distinguishes native recovery from
adaptation; renderer parity is verified separately by native captures.

Run from the repository root using the pinned Python/NumPy/Pillow environment.
Commands requiring image/array support use `PY` below; define it once:

```sh
PY() { uv run --frozen --group assets python "$@"; }
```

Blender workers run under Blender's own Python, with its `bpy`/`mathutils` modules;
do not install those into the host uv environment. Source checks compile these
workers without importing or executing them. Full recovery/rendering still requires
the local inputs below.

The root `tools/game/bootstrap.py` workflow supplies the native toolchain; media
commands additionally require its pinned vgmstream decoder and an ffmpeg build
with WMA/Bink/Theora support. See the root build instructions for tool setup.

Required inputs:

- `resources/games/juiced-2/juiced-2-hot-import-nights.iso` (user-supplied disc).
- The 30 pinned GLBs in `artifacts/carmodels-research/models`. Exact URLs, SHA256,
  accepted identities, source commit and spec joins are preserved in
  `data/juiced2/accepted-roster.json`; specifications in `accepted-specs.jsonl`.
- Existing tracked `data/carmodels/profiles/<code>.txt` and the donor material
  translation code in `tools/carmodels`.

The complete production sequence is:

```sh
python3 tools/game/assets/inventory_iso.py
python3 tools/game/assets/extract_source_archives.py
# Extract native typed script records; owns evidence output only.
python3 crates/oversteer-core/tools/recover_gameplay_config.py

python3 tools/game/assets/fetch_donors.py
PY tools/game/assets/prepare_cars.py
python3 tools/game/assets/build_content.py
python3 tools/game/assets/bind_profiles.py
PY tools/game/assets/normalize_wheel_sockets.py
PY tools/game/assets/prepare_wheels.py
python3 tools/game/assets/prune_scene_nodes.py
PY tools/game/assets/prepare_paint_masks.py
python3 tools/game/assets/correct_donor_surfaces.py
python3 tools/game/assets/stage_midnight_finish_translation.py --publish
python3 tools/game/assets/bind_mc3_composite_paint.py --publish
PY tools/game/assets/correct_gt4_marker_glass.py
PY tools/game/assets/prepare_gt4_paint_masks.py
python3 tools/game/assets/correct_gt4_window_passes.py
python3 tools/game/assets/stage_gt4_pass_parity.py --publish
PY tools/game/assets/measure_wheel_fit.py --apply
PY tools/game/assets/stage_fr2_stock_rims.py --publish
PY tools/game/assets/stage_gt4_window_geometry.py
# Review staged window-only proof before publication.
python3 tools/game/assets/publish_gt4_window_geometry.py
# Bake mirrored wheel geometry, outward winding/normals and opaque tire alpha.
PY tools/game/assets/bake_inspection_wheels.py --car GT4_HOND0018 --car GT4_MAZD0012 --car GT4_MITS0001

python3 tools/game/assets/recover_courses.py
PY tools/game/assets/recover_world_geometry.py
PY tools/game/assets/correct_road_materials.py
python3 tools/game/assets/apply_world_instances.py
PY tools/game/assets/sample_native_road.py
python3 tools/game/assets/build_native_career.py
python3 tools/game/assets/bind_native_leagues.py
python3 tools/game/assets/bind_native_sponsors.py
python3 tools/game/assets/convert_world_handedness.py
PY tools/game/assets/sample_native_crosssections.py
python3 tools/game/assets/stage_native_collision.py
python3 tools/game/assets/bind_native_collision.py --publish
python3 tools/game/assets/bind_native_physics.py
python3 tools/game/assets/recover_presentation.py
python3 tools/game/assets/stage_world_vertex_uvs.py --publish
# Existing prepared worlds from before the topology fix can be repaired without
# rerunning the material pipeline (repeat --world for each retained track).
python3 tools/game/assets/repair_world_indices.py --world london_circuit1
# Preserve front lettering and give double-sided London signs readable back UVs.
PY tools/game/assets/repair_london_sign_faces.py
PY tools/game/assets/recover_vehicle_kits.py
PY tools/game/assets/recover_plate_sockets.py
PY tools/game/assets/audit_body_geometry.py
python3 tools/game/assets/bind_body_bounds.py --publish
python3 tools/game/assets/bind_decal_repeat.py --publish
python3 tools/game/assets/stage_native_starts.py
python3 tools/game/assets/bind_native_starts.py --publish
# REQUIRED FINAL CONTENT BINDING after all content/career/physics builders.
python3 tools/game/assets/bind_car_classes.py --publish
python3 tools/game/assets/bind_native_goal_routes.py --publish

PY tools/game/assets/ui_textures.py
PY tools/game/assets/ui_fonts.py
python3 tools/game/assets/ui_text_catalog.py
python3 tools/game/assets/ui_layouts.py
python3 tools/game/assets/ui_named_assets.py
python3 tools/game/assets/ui_global_strings.py
PY tools/game/assets/unpack_character_components.py
PY tools/game/assets/recover_characters.py
PY tools/game/assets/skin_characters.py
python3 tools/game/assets/recover_character_anm.py
python3 tools/game/assets/bind_character_animations.py
PY tools/game/assets/stage_character_idle.py --publish
PY tools/game/assets/stage_character_actions.py --publish
# Fixed Oversteer outfit; preserves the prepared rig/motions, corrects bare-arm
# material assignment and binds denim/trainers. Run after character recovery.
python3 tools/game/assets/prepare_fixed_driver.py
python3 tools/game/assets/inventory_avatar_components.py
python3 tools/game/assets/inventory_character_material_slots.py
PY tools/game/assets/recover_avatar_materials.py
python3 tools/game/assets/recover_character_morphs.py
python3 tools/game/assets/recover_avatar_presets.py
PY tools/game/assets/stage_character_components.py
# Run these Blender import/render checks and review the resulting M/F image.
/Applications/Blender.app/Contents/MacOS/Blender --background --python tools/game/assets/probe_character_components_blender.py
/Applications/Blender.app/Contents/MacOS/Blender --background --python tools/game/assets/preview_modular_presets_blender.py
python3 tools/game/assets/publish_character_components.py
python3 tools/game/assets/recover_customization_cameras.py
python3 tools/game/assets/recover_creator_presentation.py
PY tools/game/assets/sample_paintbooth_floor.py
PY tools/game/assets/stage_paintbooth_venue.py
# Source room preview uses explicit inspection lights, not native DLT parity.
/Applications/Blender.app/Contents/MacOS/Blender --background --python tools/game/assets/preview_paintbooth_blender.py
python3 tools/game/assets/publish_presentation_venues.py
PY tools/game/assets/recover_decals.py --publish
python3 tools/game/assets/reference_coverage.py
python3 tools/game/video.py
python3 tools/game/media.py
python3 tools/game/audio_banks.py
PY tools/game/assets/verify_assets.py
```

Replace each `PY` with the command stated above. Coordinate production publication
with native verification: do not mutate runtime assets during an active capture.
`tools/game/build.py` builds and imports already prepared assets; it does not run
this source extraction sequence. `build_content.py` initially assigns the adapted
`index // 3` car availability. The final `bind_car_classes.py --publish` step must
run again after rebuilding content: it assigns three accepted muscle donors to
league 3 and six accepted supercar donors to league 5, allowing purchase by the
first original class-restricted event. This replacement catalog/availability is an
explicit adaptation; the native 4/8 class flag predicate is separately recovered.
Existing prices, physical identities and event assignments are preserved.

 `build_content.py` initializes car definitions only; native career/league/sponsor
builders must run afterward before launching. It no longer invents event assignments. Production data contains 403 native career contests plus 60 native sponsor
contests, ten exact league bindings and 261 original goals. Raw rows, filename
hashes, archive member offsets and provenance are retained.

Worlds preserve original BDL geometry, half-float UVs, original DXT/RGBA texture
art and ZDF instances. PBR material finish and static tarmac layer composition are
translations of native shaders. Complete all-NaN native instance matrices are
omitted as inactive placeholders with explicit per-instance provenance. Partially
invalid matrices fail. Native D3D handedness is converted by reflecting X in
meshes, winding, instance transforms, route samples and contact samples together;
UVs remain original. The final conversion is idempotent. Source raw points and
origins remain available. Rendering fidelity still requires source-frame review.

`sample_native_road.py` separates original BTF AI samples from original triangle
road-contact heights. Five of 10,162 samples retain explicit BTF fallback. Eight
drift arenas have 817 geometry-derived asymmetric floor/wall crosssections, with
per-sample evidence and explicit fallback/censoring. These are geometric
candidates; native CLD surface classification and layered shaders remain incomplete.

All 33 routes now have bounded original CLD decoding and track-local collision
catalogs bound into core content. Native triangles (including source degenerates),
ordered polygons, sixteen-control bicubic patches and four-control splines retain
original surface IDs and source hashes. The native Bernstein patch evaluator is
recovered, and spline walls use the recovered source rule from Y+4m to Y-1m.
Discrete query tessellation and full native surface-property execution are separate
core verification concerns. All 33 whole-file CLD hashes differ; no partial city
geometry deduplication is asserted. Render geometry and road-width crosssections
are no longer claimed to be the original collision primitives.

GT4 arbitrary-paint masks derive from actual factory palette differences; static
lamp/trim texels are excluded. Four FR2 masks are authored atlas masks. MC3/MCLA
use explicit source paint channels, with explicit native glass classes translated
to PBR. All thirty still require stock/modified native visual capture review.

Two complete source actor assemblies retain the shared 86-bone rigs and fourteen
source clips, including exact native M/F idle bindings. The modular catalog adds
111 gender-specific component GLBs from 80 drawable original skins, retaining all
152 drawable chunks, palettes and weights; the 81st source skin is hierarchy-only
and is not replaced with invented geometry. Components share the `NativeAvatar`
normalization and must be rebound to the base skeleton without nesting its root
rotation twice. Full preset assembly replaces the old base meshes while retaining
their skeleton and AnimationPlayer.

Ten exact native `.def` presets retain all 56 raw attributes and source component
IDs. The first source gender-list entries are MPreset2 and FMPreset3; constructor
zero values are not described as actual default appearance. One hundred original
head targets include 45 source geometry-attribute mappings. Exported deltas are
scaled by 100 with the matching native-level-to-render-weight factor `.01`.
Original creator controls retain 82 actions and 46 M/F ramp-bearing actions,
including partial intervals; they are not replaced with uniform invented sliders.
Original replacements resolve 671 of 817 component material-slot references, with
259 unique recovered texture PNGs. Original float3 normals and normal morphs are decoded; the source winding/normal
repair is staged in `normal-proof/` for native capture verification. Cloth shading,
sampler/target color-space processing and eight legacy skin/hair/profile attribute
consumers remain unresolved. Original TextureCombine HSV/Alpha/MattAlpha shader
equations are decoded and checked separately; this is not full skin/cloth shading
parity. Three shipped skeleton scale datasets are proven identity across all
matching archive banks, including the preset FAT=100 case. Source-only helpers
`recover_avatar_body_scales.py` and `recover_avatar_material_ops.py` retain the
exact joint datasets and 461 original component operation graphs; this is distinct
from claiming their complete GPU execution.

The PaintBox venue is an unchanged nine-instance subset of original Garage
geometry: 22 draws and 11,268 triangles. The literal paint menu consumer proves
pose mode 1 and lighting selector 2, with native position (3000,-167,3000) cm.
The donor display ground reference is an explicit adaptation to original floor
triangles, not the original vehicle CG seed. This binding applies to paint only;
vinyl/wheel aliases are not inferred. Creator presentation metadata retains 14
final camera blocks and 20 original marker records. Camera/root composition and
native lighting/shader behavior require separate consumer and capture verification.

`reference-coverage.json` contains observed/proposed reference evidence, not a
claim that every taxonomy state is implemented or visually matched. UI exports
include 2,905 original textures, 138 original bitmap fonts, exact symbolic texture
bindings, original typed layout rows, 2,003 English strings, 40 original loading
tips and the original Xbox 360/shared credits. Native font label/resolution bindings use the recovered `fonts\<label>_<resolution>.xef`
namespace. Menu and HUD aliases now bind exact MainMenu and HIN_Text 1080 fonts.

Original decal recovery binds 1,089 designs in 84 source categories to their
original RGBA texture art. Catalog extraction is distinct from runtime layer and
paint-mask rendering verification. `stage_gt4_pass_parity.py` writes a proposed
donor-viewer pass/culling correction to evidence; `--publish` applies it to the
runtime models and rebuilds variant primitive indices. The source rule removes
45 overlay draws in 17 GT4 models and uses front-facing body materials. Later geometry-ray inspection isolated four window-only surface families in
Integra, Supra, R34 and Delta. `stage_gt4_window_geometry.py` and its hash-checked
publisher apply an explicit translucent PBR translation and remove those exact
surfaces from body paint targets, preserving their geometry bytes. These supersede
the earlier unresolved four-window reports; they do not establish native GS shader
parity or visual acceptance of every lamp/interior/material across all thirty.

`stage_native_starts.py` recovers all 340 original BTF grid records across the
33 courses. `bind_native_starts.py --publish` binds these to the current content
and bundle, preserving collision data. The native placement consumer uses XYZ
as a seed, snaps it to collision within a vertical ±100-source-unit ray, and
aligns the basis to the hit normal; raw BTF Y is not the final vehicle height.

`stage_tree_materials.py` stages exact `BarkTexture`, `FrondTexture` and
`LeafTexture` bindings. `publish_tree_materials.py` verifies all pre-publication
hashes before copying the reviewed world batch. Geometry, UVs and instance
transforms remain byte-identical; native SpeedTree wind and pass behavior remain
unresolved.

Source-only investigations are reproducible with `inventory_avatar_components.py`
(399 active rules, 81 exact skin bindings), `recover_character_morphs.py`
(100 geometric targets), `ui_goal_icons.py` followed by `map_native_goal_icons.py`
(261 exact career goal art bindings), and `recover_native_palette.py`
(264 original 24×11 chart colors and original wheel/overlay art). Source additive morph application, original preset order/levels and per-control
ramps are recovered. Constructor zero values remain distinct from preset selection;
full UI lifecycle, texture-compositor execution and visual parity still require
native verification.

`stage_decal_color_modes.py` classifies constant black/white visible artwork as
alpha masks and retains other RGB artwork. This chosen-color fill is an explicit
renderer adaptation until the native compositor formula is recovered; it does
not rewrite original PNGs.

`decode_texturecombine.py`, `texturecombine_fixtures.py` and
`build_texturecombine_contract.py` are source-only shader recovery steps. They
extract the original six TextureCombine pixel programs, verify their technique
indices and register metadata, and compare HSV/Alpha/MattAlpha ALU execution with
12,000 independently written equation checks. The staged contract retains strict
hue bounds, exact channel order, two-pass hue wrapping and absence of ALU output
saturation. It does not infer sampler sRGB transfer, render-target quantization,
material transparency or execution of the eight legacy avatar attributes.

Original performance recovery is source-only: `python3 tools/game/assets/recover_native_performance.py` retains the ten league package rows, 89 native car performance ranges, twelve supplier categories, active race flag copy chain and prototype package/unlock consumers in `artifacts/juiced2-build/native-performance/catalog.json`. It does not map ambiguous original variants to donors or replace the current runtime upgrade tree.

For the source normal repair, run `PY tools/game/assets/audit_native_character_normals.py`, stage components, then run `PY tools/game/assets/check_character_normal_stage.py` and both Blender component/head probes. `publish_character_normals.py` preserves the previous bundle and patches only the reviewed GLBs plus their current manifest hashes. Original hard edges and sparse normal deltas are retained; no seam welding is used.

The reviewed London banner repair is `PY tools/game/assets/repair_london_sign_faces.py`.
It preserves the front atlas UVs and adds separately culled, readable back faces
only for the two lettering regions in texture 266. Run it after world UV/topology
preparation. Both repair tools are idempotent; reimport before rendering.
`build.py` explicitly enables mipmaps for road shader texture imports, including
markings that Godot does not detect as 3D usage automatically.

# Source-model car identity

Status: implemented. This supersedes the earlier procedural colour-seed contract.

`CarAppearanceSpec.modelCode` identifies one retained carmodels source vehicle. It
lives beside `VehicleSpec` in `Game`; it is excluded from physics, collision, replay
simulation checksums and the tunable physics registry. Empty legacy presentation
state selects the real Focus SVT source sprite. There is no procedural artwork fallback.
An explicit unknown or excluded model cannot be selected.

`game_select_model()` loads both the model's researched physics profile and its
presentation identity atomically. `game_apply_spec()` retains presentation identity
for tuning. Changing mass, grip, engine or gearing cannot change the source paint,
windows, livery or mesh silhouette. Overall physical length uniformly scales the
image; the CG positions the sprite relative to the physics body. Source proportions
are preserved, including mirrors that may extend beyond reported body width.

Profiles store presentation separately as an optional comment:

```text
# carmodels.model = GT4_DODG0005
```

The Physics Lab writes this tag when saving. Loading a legacy profile without it
keeps the current appearance. An invalid, excluded or duplicate tag rejects loading
before either identity or physics changes. The physics registry continues to read
its own numeric fields. Headless vehicle-card exports require the explicit tag.

The runtime catalog contains 904 included cars/trucks and references baked PNG
atlases. Each contains 13 source-mesh front-wheel poses, -60° through +60° in 10°
steps. Runtime selects the nearest pose and rotates the whole car to its heading.
Per-pose textures have separate mip chains; premultiplied alpha prevents tile bleed
and transparent-colour fringes. The baker never invents wheel shapes when a source
has no separable assembly. Source limitations and approximation are documented in
the sprite manifest and workflow report.

Changing `Game` and its hot-reload entry-point table requires a full platform rebuild
and restart. Appearance remains plain value data across compatible module reloads.
The source-identity and source-sprites scenarios verify catalog coverage, profile
loading, failed-selection atomicity, physics independence and actual atlas pixels.

# Collision queries for recovered course geometry

Use **parry3d 0.31.1**, pinned in the Rust core and `Cargo.lock`, for geometric
queries against recovered course geometry. This implements the query-library
choice already permitted by [ADR-0005](../../adr/0005-use-godot-and-rust.md).
It does not replace the recovered vehicle integration, ordered contact response,
or drift assistance with another physics solver.

The immediate requirement is to query a drift arena's actual collision floor
and barriers independently of its AI spline. A lane-width corridor cannot
represent open arena floors or internal barriers. The original CLD loader
`82270218` distinguishes triangles, polygons, splines, and parametric patches;
most of the eight drift CLDs contain no triangle primitives. Retain the native
primitive and surface identity when reconstructing query geometry.

Parry provides [triangle-mesh ray queries](https://docs.rs/parry3d/0.31.1/parry3d/shape/struct.TriMesh.html),
including intersection normals and face culling, and
[non-persistent shape queries](https://docs.rs/parry3d/0.31.1/parry3d/query/index.html).
Version 0.31.1 exposes its math types through `parry3d::math`; use the installed
crate's types rather than older examples based on `nalgebra`. The `parry3d`
variant uses `f32`, consistent with the recovered numerical model.

Dependency resolution and `cargo check -p oversteer-core` passed after adding
the pin. That check establishes dependency compatibility only. Collision-data
reconstruction, query correctness, actual arena driving, and runtime performance
need separate checks before acceptance.

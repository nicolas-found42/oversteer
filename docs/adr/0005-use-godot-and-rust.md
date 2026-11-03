# Use Godot 4.7.2 with gdext 0.5.5

The user explicitly selected Godot 4.7.2 + gdext 0.5.5 after the
[stack comparison](../references/juiced2/rust-stack-research.md), superseding
[ADR-0004](0004-select-bevy-and-independent-handling.md). Use Godot's native Metal
renderer, scene/resources, UI, input, animation and audio facilities; implement
gameplay through Rust GDExtension with `api-4-7`, and keep the recovered numerical
simulation and rules in an independent Rust library.

The comparison identified Godot's integrated authoring/export benefits and the
cost of an engine/Rust boundary. Keep that boundary small: inputs/commands into
the Rust core, snapshots/events out. Use Parry geometric queries in the simulation
where needed to preserve ordered contacts and headless checks; automatic Godot
vehicle or rigid-body integration must not replace the recovered model. Native
Metal, actual donor assets, extension packaging and performance still require
the postapproval proofs in the [integration note](../references/juiced2/godot-rust-integration.md).

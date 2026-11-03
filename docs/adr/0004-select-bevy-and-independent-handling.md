---
status: superseded by ADR-0005
---

# Select Bevy with independent recovered handling

The user subsequently selected Godot 4.7.2 + gdext 0.5.5 explicitly. This
historical research selection is superseded by
[ADR-0005](0005-use-godot-and-rust.md).

The user delegated stack selection after requesting five alternatives to the
Bevy proposal. After the [primary-source comparison](../references/juiced2/rust-stack-research.md),
select Bevy 0.20.1 with its Metal renderer, built-in UI/input/audio, an independent
Rust handling library, Parry for geometric queries, the existing offline
Python/Blender asset workflow, and versioned JSON saves for the proposed plan.

Godot with Rust is the strongest alternative and offers a better integrated
scene/UI editor. Bevy keeps the application and recovered simulation integration
in one Rust stack while supplying the game-engine services this project needs;
the custom-wgpu and Macroquad alternatives require substantially more engine
assembly, stable Fyrox's Metal path is unestablished, and rend3 is archived.
This is a project-fit judgment, not a measured speed or visual-quality advantage.

Preserve original handling integration, stage side effects, contact response and
update ordering. Parry supplies geometry queries, not replacement vehicle dynamics.
Normalize donor material variants offline because native Bevy GLB loading alone
does not preserve them. Pin resolved compatible dependencies and run the report's
native asset/input/audio/packaging and simulation proofs before bulk content work.
Full implementation still awaits the user's approval of the completed plan.

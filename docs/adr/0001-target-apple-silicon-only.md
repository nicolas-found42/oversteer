# Target Apple Silicon only

The existing interactive game targets Windows, but the user explicitly selected
native Apple Silicon macOS as the sole target for the Rust reconstruction. Choose
and validate rendering, input, packaging, and performance for that target; Windows
compatibility is outside this reconstruction's scope. This replaces the proposed
macOS-and-Windows target and avoids carrying the old platform contract into the
new game.

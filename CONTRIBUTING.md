# Contributing to Oversteer

Behavioural rules for AI agents are in [AGENTS.md](AGENTS.md). This file is about the
mechanics: what to install, what to run, and what has to be green before you push.

## Active native game: Apple Silicon

The active stack is Godot 4.7.2 + gdext 0.5.5, Rust 1.99.0, and Python
3.13.16. Install Rust through rustup, uv, and Apple command-line developer tools.
The repository pins the Rust toolchain/components and Python interpreter; uv
resolves Python dependencies from the committed lockfile.

A fresh clone can check tracked sources without the original game disc, donor
models, Godot editor, or generated runtime assets:

```sh
uv run --frozen python tools/game/dev.py doctor
uv run --frozen python tools/game/dev.py check
```

The authoritative entry point is `tools/game/dev.py`: `check` runs the source
gate; `format` explicitly rewrites supported source formatting; `lint` and `test`
run narrower source checks. `reference-tests` additionally requires retained
local recovery fixtures and fails when they are missing. CI runs the same `check`
command on an ARM64 Mac. Source checks do not establish visual or release acceptance.

For a prepared local game workspace, follow [the native workflow](docs/game/README.md)
and [asset preparation](tools/game/assets/README.md), then run
`uv run --frozen python tools/game/dev.py doctor --runtime`. The original disc
and retained local recovery inputs are not supplied by a clone or downloaded by
source-quality CI. Do not run asset publication or rendered scenarios as a
prerequisite for linting.

VS Code defaults to native check and dev-extension build tasks. Recommended
rust-analyzer, CodeLLDB, and Ruff extensions cover Rust/Python editing. The native
LLDB launch profile starts the pinned Godot host with a dev extension and requires
already prepared/imported assets. Its breakpoint behavior has not been verified;
macOS debugger permissions or signing/entitlements may require local setup.
Godot's script LSP/DAP is separate from Rust analysis and native debugging.

Commit hooks remain optional and must be installed explicitly per clone. The
Rust hook checks formatting without rewriting; Python hooks may rewrite supported
sources. Immutable checkpoint evidence is excluded from whitespace rewriting.

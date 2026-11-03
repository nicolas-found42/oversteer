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

## Legacy C11 workflow

The following setup and Makefile checks apply to the retained historical C/Raylib
implementation. They are not the active native game's source gate.

### Setting up

**Windows only.** The supported environment is MSYS2 UCRT64; see the prerequisites section
in the [README](README.md#prerequisites-windows--msys2-ucrt64) and run:

```bash
tools/setup/setup_windows.ps1
```

Expected by `make verify`: `clang`, `clang-tools-extra` (clang-format), and `cppcheck`.
`gcovr` is only needed by `make coverage`, which `make ci` runs and `verify` does not. All
four come from `pacman`, and `make info` prints which of them it found.

**Python is a prerequisite, not an optional extra.** `make regression` compares telemetry
through `tools/telemetry/compare_telemetry.py`, and `make compile-commands` is a Python
script too, so `verify` cannot complete without it. `setup_windows.ps1` does not install it:

```bash
pacman -S mingw-w64-ucrt-x86_64-python
```

The Python *tooling* — ruff and pre-commit — is managed by [uv](https://docs.astral.sh/uv/).
PyPI's ruff ships MSVC wheels only, so it cannot install into MSYS2's mingw python; `uv tool
install` runs the pinned ruff in uv's own managed python instead:

```bash
uv tool install ruff==0.15.20 pre-commit
```

`ruff==0.15.20` must match [requirements-dev.txt](requirements-dev.txt) and
[.pre-commit-config.yaml](.pre-commit-config.yaml) — keep the three in step.

Node and npm are needed only by the vehicle appearance inspector (`make inspect`,
`make visual-diagnose`); nothing else in the toolchain uses them, and the bootstrap script
does not install them. See [tools/visual/README.md](tools/visual/README.md).

The legacy telemetry and appearance checks use the standard library. Native asset
preparation has separate image/array dependencies documented in its asset guide.

Install the commit hooks once per clone:

```bash
pre-commit install
```

## Before you push

```bash
make verify
```

That is format-check, ruff, cppcheck, the clang analyzer, every physics scenario, and the
baseline regression. `make verify-fast` is the quicker format-and-tests subset while
iterating.

### A SKIP is not a pass

Targets whose tool is not installed print `SKIP` and exit 0, so a local run can be green
having checked very little. To find out what actually ran:

```bash
make OVERSTEER_STRICT=1 verify
```

Under `OVERSTEER_STRICT`, a missing tool is a hard failure. This is what CI passes, so if it
fails for you it will fail there too.

The one exception is the sanitizer runtime check. MSYS2 ships ASan/UBSan in CLANG64, not in
the supported UCRT64 environment, so `make sanitize` skips unconditionally on Windows. The
Linux CI job is where the sanitizers actually run.

## CI

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs two jobs on every push and pull
request:

| Job | What it covers |
| --- | --- |
| `windows-ucrt64` | The canonical toolchain: format-check, ruff, cppcheck, clang analyzer, physics scenarios, baseline regression |
| `linux-headless` | ruff, the headless scenarios and regression, and ASan/UBSan |

Both jobs lint Python with the same pinned ruff. It runs through [uv](https://docs.astral.sh/uv/):
MSYS2's mingw python cannot take PyPI's MSVC-only ruff wheels, so the Windows job runs the
pinned Ruff in uv's own managed Python. `pyproject.toml` and `uv.lock` are
authoritative; `requirements-dev.txt` is a generated compatibility export.

## Formatting

C is `clang-format` (`.clang-format`), Python is `ruff` (`pyproject.toml`). `pre-commit`
applies both on commit; `make format` and `make format-py` apply them by hand.

Line endings are LF, enforced by `.gitattributes` rather than by each developer's
`core.autocrlf`. This matters more than it looks: clang-format counts a `\r` toward
`ColumnLimit`, so C formatted on a CRLF worktree wraps its backslash continuations one column
differently and fails `make format-check` on any LF checkout, CI included.

## Baselines

`tests/baselines/` holds reviewed, committed, deterministic telemetry. `make regression`
compares a fresh run against it with tolerances.

Re-recording them with `make baselines` overwrites the thing that would have caught a
physics regression. Do it only when you meant to change physics, and **say so in the commit
message, with what changed and why the new numbers are right**. A baseline update that says
"update baselines" is indistinguishable from a bug being blessed.

**The baselines are platform-specific.** They are recorded on Windows/UCRT64, and the
tolerances are tight enough that a different libm does not reproduce them — the first CI run
breached 13 of 46 comparisons on Linux, all longitudinal, with identical aggregate metrics
but large single-row deltas. That is a discrete event landing one tick apart, not drifting
physics: the scenario assertions pass identically on both hosts. So `make regression` is
gated on the Windows job only, and re-record baselines on Windows.

## Hot reload

The game is a thin platform layer (`build/dev/oversteer.exe`) plus a reloadable module
(`build/dev/game.dll`). Run the executable once, leave it open, and rebuild with `build.bat`
or `./build.sh`; the running game swaps the new module in. A compile error cannot close it —
the link output only moves into place on success.

**Restart is required after** a change to the layout of `Game` or anything reachable from it
(most often: adding a field to `VehicleSpec`), to `src/platform/main.c`, `timestep.c`, or
`hotreload_windows.c`, or to `GAME_ENTRY_POINTS`.

**Reload-safety rules for module code:**

- No pointer in `Game`, or reachable from it, may point into the module's code or static data.
- No function pointers in persistent state.
- `Game` is allocated and owned by the platform layer. Never declare `static Game game;`
  inside the module.
- Anything raylib tracks is released in `game_pre_reload` and re-acquired in
  `game_post_reload`.

Validate it without a window:

```bash
tools/setup/validate_hotreload.sh
```

## Commits and pull requests

Small, reviewable commits, each one doing a single thing. Explain *why* in the body — the
diff already says what. The [PR template](.github/pull_request_template.md) lists what a
review expects.

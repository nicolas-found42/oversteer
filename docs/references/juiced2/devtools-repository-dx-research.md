# Repository developer workflow and CI research

Research date: 2026-11-03. Research only; no implementation, formatting, hooks installation, downloads, builds, or native scenarios performed. Scope: repository workflow, CI, editor integration, onboarding, and evidence boundaries. Godot 4.7.2 + gdext 0.5.5/API 4.7 and Apple Silicon are fixed requirements, not migration candidates.

## Findings from this checkout

| Priority | Actual gap | Bounded recommendation |
| --- | --- | --- |
| P0 | `.github/workflows/ci.yml` runs Windows/UCRT64 and Linux C/Raylib checks; `nightly.yml` is also legacy C. Neither tests the Rust workspace. | Add one explicitly named native-source quality job on an ARM64 Mac, without deleting historical checks in this change. Required-status configuration is outside the YAML and must be reviewed separately. |
| P0 | `Makefile` `verify`, `verify-fast`, and `ci` still mean legacy C verification. `tools/game/build.py test` does run `cargo test --workspace`, without bootstrapping or importing assets. | Document direct commands for the active stack and use them in CI. Do not route native checks through the legacy Makefile: its toolchain discovery and Raylib requirements add irrelevant dependencies. No need for just, mise, a new task-runner package, or a replacement build framework. |
| P1 | `.vscode/tasks.json` defaults to Windows `build.bat`; launch configurations use GDB under `C:/msys64`; recommended extensions omit rust-analyzer/CodeLLDB. | Make native source build/check/test tasks the defaults, retain old tasks with explicit `Legacy C` labels, and add Rust language/debugger recommendations. Keep CLI commands authoritative. |
| P1 | `CONTRIBUTING.md` opens with Windows-only MSYS2 instructions; the root README distinguishes legacy but points to a short native run recipe that needs local assets. | Add a short active-stack section with separate fresh-clone source checks and local runtime preparation; label the remaining instructions historical. Link existing asset and evidence docs rather than copy their long sequence. |
| P1 | Rust has no hook in `.pre-commit-config.yaml`. Existing hooks auto-fix Ruff and trailing whitespace; broad hooks have no exclusion for `docs/game/evidence/`, while current evidence includes hashes/checkpoint manifests. | Add a non-mutating Rust formatting hook only after agreeing the Rust formatting baseline. Keep expensive Clippy/tests outside commit hooks initially. Exclude immutable evidence documents from rewriting hooks if their raw bytes are part of a retained checkpoint contract; do not blindly exempt all docs or all `data/`. |
| P2 | `.gitignore` already excludes `build/`, `target/`, raw `artifacts/`, Godot cache/binaries/assets, disc inputs, and credentials. Large-file hook already caps new additions at 2048 KiB, with one named metadata exception. | Preserve these policies; do not add Git LFS or upload large assets merely for CI. Add missing editor watcher/search exclusions for `godot/.godot`, generated `godot/assets`, and fallback `target` if actual editor indexing warrants them. |

Local sources: [CI](../../../.github/workflows/ci.yml), [nightly](../../../.github/workflows/nightly.yml), [Makefile](../../../Makefile), [VS Code settings](../../../.vscode/settings.json), [tasks](../../../.vscode/tasks.json), [launch](../../../.vscode/launch.json), [extensions](../../../.vscode/extensions.json), [hooks](../../../.pre-commit-config.yaml), [ignore policy](../../../.gitignore), [attributes](../../../.gitattributes), [contributor guide](../../../CONTRIBUTING.md), [native build wrapper](../../../tools/game/build.py), [game workflow](../../game/README.md), [paused handoff](../../game/HANDOFF.md).

Behavioral discovery used `jg` against `tools/game` with four provider requests. It reported incomplete discovery and locations without excerpts; conclusions above come from subsequent direct reads, not assumed complete semantic retrieval.

## Hosted Mac CI: what is justified

GitHub's current runner table lists `macos-15` and `macos-26` as ARM64 M1 standard runners, including private repositories. Prefer explicit `macos-26` over `macos-latest` for an active native-source job; verify `uname -m` equals `arm64`. The label selects an OS family, not an immutable VM image. Record image/toolchain versions. ARM64 runner availability supports compilation/testing, but does not establish this game's Metal4 renderer or M5 Pro performance acceptance. Do not copy old advice that `macos-14` is the appropriate long-lived pin. [GitHub runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

Continue the repository's full-commit-SHA action pins and `contents: read` permission. Add pinned checkout/tool setup only when necessary; record exact Rust/Python versions rather than silently using whatever the hosted image contains. [GitHub secure-use reference](https://docs.github.com/en/actions/reference/security/secure-use)

Start without compilation caching if simpler. If cold timings justify it, use the official cache action with a key containing OS, architecture, exact Rust toolchain, and `Cargo.lock` hash. `.cargo/config.toml` puts build products in `build/rust`, so a default `target/` cache misses the real build output. Cache public Cargo downloads/compiled dependencies only; never cache `resources/games`, the reference vault, generated runtime assets, or raw verification evidence. Fork pull requests may read base-branch caches, so caches are not private artifact storage. [GitHub dependency cache reference](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching), [local Cargo configuration](../../../.cargo/config.toml).

## Editor/debugging plan

Use `rust-lang.rust-analyzer` for Rust navigation, diagnostics, and formatting; `vadimcn.vscode-lldb` supplies macOS native debugging. VS Code documents that rust-analyzer requires a debugger extension for debugging on macOS. Begin with an existing pure core unit test and confirm an actual breakpoint before adding an elaborate launch profile. [VS Code Rust documentation](https://code.visualstudio.com/docs/languages/rust)

For extension breakpoints, launch the pinned Godot executable under CodeLLDB with `--path` pointing to `godot`, or attach to the actual game process. The program is Godot, not the `.dylib`. Verify symbols load and a Rust callback breakpoint resolves. Current `build.py` builds release even for its debug directory, and `reloadable=false` in the extension descriptor means this is not the old C hot-reload workflow. A dedicated unoptimized debug build is a separate small implementation decision if current stepping proves inadequate; do not silently alter release/evidence builds. CodeLLDB supports launch/attach and Rust type formatters. [CodeLLDB manual](https://github.com/vadimcn/codelldb/blob/master/MANUAL.md), [extension descriptor](../../../godot/oversteer.gdextension), [Cargo profiles](../../../Cargo.toml).

Godot's external-editor settings open source locations; its LSP/DAP services require a running project editor and default to 6005/6006. These serve Godot script/editor integration, not Rust type analysis or native Rust breakpoints. Recommend the Godot VS Code extension only for actual GDScript work; do not install a second language/debugging stack as a prerequisite for the Rust core. Keep local editor paths out of shared settings. [Godot external-editor documentation](https://docs.godotengine.org/en/stable/tutorials/editor/external_editor.html)

## Executable implementation sequence after all research is reviewed

1. Establish the non-mutating local baseline with the selected exact toolchain. Run commands below separately, record failures, and agree bounded formatter/linter adoption before changing files. Verify: command exits and complete diagnostics, with no bootstrap or renderer launched.
2. Add one native quality CI job using the same commands and the final Rust/Python policy selected by the other research reports. Verify: fresh checkout succeeds without ignored asset inputs; introduce a temporary deliberate lint/format failure in a throwaway branch to confirm the gate fails, then remove it. Do not claim success from YAML inspection alone.
3. Update active onboarding and native VS Code tasks/recommendations. Verify tasks invoke the same CLI checks from the checkout, including a path containing spaces; confirm one core breakpoint on Apple Silicon. Add game breakpoint configuration only after validating it locally.
4. Add the narrow non-mutating Rust format hook and evidence exclusions if needed. Verify on a temporary modified Rust file, and verify immutable fixture/manifest bytes are unchanged. Never run broad `--all-files` auto-fixes on retained evidence as a research step.

Candidate source-only commands, to run after toolchain/baseline decisions:

```sh
cargo fmt --all -- --check
cargo check --workspace --all-targets --locked
cargo clippy --workspace --all-targets --locked -- -D warnings
cargo test --workspace --locked
python3 -m unittest discover -s tools/game -p 'test_replay_inputs.py'
ruff check .
ruff format --check .
```

These are proposed gates, not claims that today's tree passes. Existing [replay identity tests](../../../tools/game/test_replay_inputs.py) use temporary synthetic inputs and mock the renderer launch; they are an identifiable cheap Python test, not invented test coverage. Ruff is already pinned to 0.15.20 and repository-wide checks already exist; reuse them instead of adding a duplicate formatter. Actual baseline rollout and Rust lint configuration belong to the companion language reports.

## Keep verification classes explicit

| Class | Inputs | What a pass supports |
| --- | --- | --- |
| Fresh-clone source quality | Tracked sources/data, public Rust dependencies, selected Rust/Python tools | Syntax/types/lints and existing unit assertions. Does not prove native launch, playable assets, or legal career acceptance. |
| Asset preparation and native integration | Accepted donor sources, supplied disc, local recovered content, pinned editor/template, Apple tools | Actual import/build/run behavior. `build.py build` includes import; do not put it in the cheap source job. |
| Render/package/release evidence | Actual Metal-rendered app, exact content and extension hashes, retained scenario outputs, human reference review, moved independent app where specified | Only the particular observed render/runtime/package checks. Requires repeating against the exact current build. |

The native asset guide explicitly uses NumPy/Pillow for some preparation commands and requires original local inputs; the older requirements-dev comment claiming every other script is stdlib is no longer an adequate onboarding statement. Document this distinction rather than installing recovery dependencies on every source-check job. [Asset pipeline](../../../tools/game/assets/README.md), [requirements](../../../requirements-dev.txt).

Do not download proprietary assets, run recovery/publication commands, normalize retained evidence bytes, upload `artifacts/` wholesale, or promote technical CI success to visual acceptance. The paused handoff explicitly preserves failed historical captures and states the newest DLL has not had its native scenario run. Research and source-quality work must preserve that boundary. [Paused implementation handoff](../../game/HANDOFF.md).

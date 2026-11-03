# Rust and Godot developer tooling audit

Research date: 2026-11-03. Scope: tooling only; gameplay remains paused. No code, configuration, engine, dependency, or generated asset changes are proposed as part of this report itself.

## Findings

The active native stack already has strong building blocks: committed `Cargo.lock`; exact `godot = 0.5.5` with `api-4-7` and `experimental-threads`; exact `parry3d = 0.31.1`; an ARM64 library mapping in `godot/oversteer.gdextension`; a checksum-verifying Godot 4.7.2 bootstrap; native-renderer import validation that rejects logged errors as well as failed exits; and an extensive local verification pipeline. Preserve these pins and existing validation rather than replacing them with generic setup advice.

The largest gap is that the discoverable default checks and editor tasks still target the former C/Windows game. `Makefile`, `.github/workflows/ci.yml`, `.pre-commit-config.yaml`, and `.vscode/{extensions,settings,tasks,launch}.json` do not provide a Rust/Godot workflow. `.cargo/config.toml` correctly places output in `build/rust`, but there is no checked-in Rust toolchain pin or package `rust-version`. `docs/game/README.md` is the useful native entry point; root README and CONTRIBUTING retain extensive legacy instructions. These are repository observations, not evidence that the legacy checks are intrinsically broken.

## Observed baseline

Commands below ran on the current prepared checkout, native `aarch64-apple-darwin`, Rust 1.99.0 (`b940084d7`, active floating `stable-aarch64-apple-darwin`). They are read-only with respect to tracked source; compilation writes ordinary ignored build outputs.

| Command | Result | Meaning |
|---|---|---|
| `cargo fmt --all -- --check` | Exit 1 | Formatting differences include `examples/record_endurance.rs` and `tests/core.rs`; this is not yet a passing gate. |
| `cargo check --workspace --all-targets --locked` | Exit 0 | Includes examples; reports one unused `label` in `record_endurance.rs` and four deprecated `Resource::duplicate` calls in the Godot crate. |
| `cargo clippy --workspace --all-targets --locked -- -D warnings` | Exit 101 | Stops in core: 61 library diagnostics, 63 library-test diagnostics. Includes excessive precision in recovered constants, manual clamp, needless borrow, range loops. This does not establish the full Godot/example lint count. |
| `cargo test -p oversteer-core --lib --locked` | Exit 0 | Five unit tests pass. This is the current narrow candidate for an asset-independent runtime gate. |
| `cargo test -p oversteer-core --locked` | Exit 0 | Five unit tests, 89 integration tests, zero doctests pass on the prepared checkout; examples compile and emit the unused-variable warning. |
| Pinned Godot executable `--version` | `4.7.2.stable.official.ed1daf0bf` | Installed executable agrees with the requested pin. |
| `file godot/bin/debug/liboversteer_godot.dylib` | Mach-O arm64 dylib | Current deployed debug-path library has native architecture; does not establish debug compilation mode. |

Important boundary: core integration tests are **not** currently clean-checkout checks. `crates/oversteer-core/tests/core.rs` reads ignored `artifacts/juiced2-build` performance mappings, collision records, recorded controls and earned-career saves. Some examples require the same local evidence. Compilation of examples does not execute their `main`, and therefore should remain in the portable check even when example execution is local-only. Cargo documents the distinction between target selection, example compilation and test execution. [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

Jevgrep discovery was attempted first against `crates` with four requests; it reported incomplete discovery due to its request limit and returned only a provenance lead. Exact configuration reads and focused source reads provided the evidence above; missing semantic results were not treated as proof of absence.

## Priorities and smallest changes

### P0: Establish one reproducible, asset-independent native check

1. Add `rust-toolchain.toml` with the **already observed** `1.99.0`, minimal profile, and `rustfmt`/`clippy` components. This stabilizes diagnostics and formatting without altering Godot/gdext pins. Keep native target `aarch64-apple-darwin` explicit in the extension build, as it already is. Rustup supports committed versioned toolchain files and components. [Rustup overrides](https://rust-lang.github.io/rustup/overrides.html)
2. Add one native verification entry point, separate from legacy `make verify`: `cargo fmt --all -- --check`, `cargo check --workspace --all-targets --locked`, and `cargo test -p oversteer-core --lib --locked`. Then run Clippy with all targets. Do not use `--all-features`: it changes the selected gdext API/thread feature contract. Cargo defines lockfile enforcement and target selection; rustfmt and Clippy are toolchain components. [Cargo test](https://doc.rust-lang.org/cargo/commands/cargo-test.html), [cargo fmt](https://doc.rust-lang.org/cargo/commands/cargo-fmt.html), [Clippy](https://doc.rust-lang.org/clippy/usage.html)
3. Record/adopt the existing format and warning baseline in an explicit follow-up before making a strict gate required. Avoid bulk `clippy --fix`. Recovered float literals and expression order are source evidence: review each suggestion against reconstruction intent, especially `max/min` versus `clamp` NaN behavior. Use narrowly scoped documented lint exceptions for intentional constants/algorithms rather than rewriting source mathematics or disabling Clippy globally. Clippy explicitly supports selective allowances. [Clippy lint configuration](https://doc.rust-lang.org/clippy/usage.html)
4. Add a Rust CI job that runs the same entry point without bootstrapping Godot, downloading original inputs, or staging assets. Preserve legacy checks until a separate decision retires them. Start with compiler checking plus unit tests if formatter/lint adoption is deferred; a deliberately failing new required check is not a usable baseline. Cargo check type-checks targets without running the game. [Cargo check](https://doc.rust-lang.org/cargo/commands/cargo-check.html)

Acceptance: a fresh checkout with the pinned Rust toolchain passes the chosen entry point without a Godot install, `godot/assets`, original game image or ignored recovery artifacts. The audit ran on a prepared checkout, so this fresh-checkout criterion remains to be demonstrated during implementation.

### P1: Make the test boundary explicit

Keep `tools/game/build.py test` documented as the existing workspace test command, but stop presenting it as universally asset-independent. Separate evidence-dependent integration cases from pure library tests with an explicit suite/fixture contract. The smallest initial change is documentation plus distinct command names; moving tests or checking in fixtures needs a separate review of provenance and size. Never silently return success when a mandatory fixture is absent. Cargo supports independent integration-test targets and name filters; use those before inventing a custom runner. [Cargo test target selection](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

Do not declare `rust-version = 1.94` merely because gdext requires it. The installed published `godot-0.5.5/Cargo.toml` and `godot-bindings-0.5.5/Cargo.toml` both declare 1.94, confirming the local docs' lower bound, but the whole workspace has not been tested at that minimum. Either declare the verified 1.99 toolchain as current supported minimum, or separately test 1.94 plus the locked graph before claiming that MSRV. Toolchain pin and supported minimum answer different questions. [Cargo rust-version](https://doc.rust-lang.org/cargo/reference/rust-version.html)

### P1: Native Rust editor and debugging path

Add `rust-lang.rust-analyzer` and `vadimcn.vscode-lldb` recommendations; add Rust check/unit-test/build tasks using repository-root paths and Cargo problem matching. Keep settings small: Rust formatter, optional Clippy-on-save after baseline adoption, and existing `build/**`/`artifacts/**` exclusions. Leave build-script/proc-macro defaults enabled for gdext macros. Do not copy a large rust-analyzer configuration template. [rust-analyzer configuration](https://rust-analyzer.github.io/book/configuration.html), [godot-rust debugging](https://godot-rust.github.io/book/toolchain/debugging.html)

Create an LLDB launch configuration whose program is the pinned **Godot executable**, with `--path` pointing to `godot`; the Rust dylib is loaded by the Godot host and is not the launch program. Add a genuinely development-profile extension build/copy task: current `tools/game/build.py build` always compiles `--release` and copies the same release library into both debug/release folders. Merely naming that output debug does not give a normal unoptimized debug experience. Preserve the production release path. [godot-rust debugging](https://godot-rust.github.io/book/toolchain/debugging.html), [Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)

Verify breakpoints in one extension callback, with the correct dylib loaded, before documenting debugging as working. macOS debugging of a downloaded Godot host may require a separate development copy re-signed with debug entitlements; first-party gdext docs describe this. Do not weaken system security or re-sign the checksum-verified production/bootstrap artifact automatically. This was researched, not tested. [godot-rust macOS debugging](https://godot-rust.github.io/book/toolchain/debugging.html)

### P1: Preserve an honest engine validation tier

Retain current native Metal import validation, including log scanning and missing/invalid import checks. `--headless` is useful for selected technical checks, but is not evidence that embedded textures or native rendering work; this repository has already observed dummy-renderer false-success behavior. Godot documents `--import`, `--headless`, `--path`, bounded quit options and runtime version queries; actual pinned binary help is authoritative because latest web documentation may describe newer flags. [Godot command line reference](https://docs.godotengine.org/en/latest/tutorials/editor/command_line_tutorial.html)

Add a non-mutating native doctor command that reports exact Rust/Godot versions, host architecture, expected dylib architecture/path, and whether prepared assets exist. Fail mismatches for the selected operation instead of accepting system `godot` or an x86_64/Rosetta build. Then distinguish: (a) Rust compilation/unit tests, (b) extension load/registration smoke test in a deliberately minimal asset-free project if that proves feasible, (c) prepared-project native import, (d) bounded local gameplay/save/input/capture and packaged-app checks. The minimal project is a candidate, not an existing verified capability: registration might touch runtime resources. Do not claim the full project imports cleanly without its original-derived assets. Godot CLI supplies the relevant process controls. [Godot command line](https://docs.godotengine.org/en/latest/tutorials/editor/command_line_tutorial.html)

Keep `reloadable = false`: existing build/copy operations are not a hot-reload system. Stop Godot before replacing the loaded library in a normal workflow; any future reloadability change needs its own gdext lifecycle review. No automatic gameplay launch or visual recapture is necessary to implement the tooling tier.

### P2: Dependency checks without dependency churn

Use committed `Cargo.lock` and `--locked` in build/test/check paths (the current Python native build/test calls omit it). Add a pinned `cargo-audit` invocation as a separate dependency-advisory check; report findings and decide on fixes explicitly, preserving exact Godot/gdext/parry pins. RustSec defines cargo-audit as scanning the lockfile. No advisory scan was run in this audit, so no clean security result is claimed. [RustSec](https://rustsec.org/), [Cargo test lockfile options](https://doc.rust-lang.org/cargo/commands/cargo-test.html)

Use `cargo-deny` only if an explicit Rust dependency license/source policy is needed; its advisories/licenses/bans/sources checks can replace overlapping tools later. Begin from the actual locked dependency licenses and approved registries, not an arbitrary strict template or blanket duplicate-version ban. Dependency licensing checks do not validate rights or provenance of Juiced 2 assets. [cargo-deny](https://embarkstudios.github.io/cargo-deny/)

Defer cargo-nextest, cargo-hakari, cargo-chef, nightly sanitizers, MSRV matrices, custom linker tuning, sccache and `target-cpu=native` until measurement demonstrates a problem. Five unit tests complete immediately and the full prepared core integration suite completed in roughly eleven seconds here. The current small workspace does not justify a second test runner or host-specific output flags by default.

## Suggested implementation sequence

1. Pin the observed Rust compiler and document pure versus prepared checks. Verify toolchain resolution and clean-checkout `check --all-targets` plus five unit tests.
2. Establish reviewed formatter/lint adoption without changing recovered behavior. Verify no numerical/algorithmic changes and rerun prepared core tests when local evidence is available.
3. Add one shared native check and corresponding CI/editor tasks. Verify exactly the same commands fail on a deliberately introduced check violation and pass after restoration.
4. Add the development dylib build and LLDB launch path, independently from import and release packaging. Verify one live Rust breakpoint on ARM64 Godot 4.7.2.
5. Add doctor/advisory checking only after the basic gate is usable. Verify version/architecture mismatch reporting and document the advisory database fetch requirement.

No engine import, GPU capture, game scenario, export, debugger entitlement change, dependency installation/update, or automatic fix was performed in this research pass. All recommendations are prospective; only the baseline commands above were executed.

### Additional lint inventory

A follow-up diagnostic-only run, `cargo clippy --workspace --all-targets --locked --message-format=json -- -A clippy::excessive_precision -A clippy::manual_clamp`, completed after temporarily allowing those two groups on the command line (no persistent configuration). Remaining groups were `needless_borrow`, `needless_range_loop`, `field_reassign_with_default`, `collapsible_if`, `useless_conversion`, `items_after_test_module`, `let_and_return`, `cmp_owned`, `double_ended_iterator_last`, `map_entry`, `too_many_arguments`, `manual_is_multiple_of`, and `if_same_then_else`, plus the unused example variable and deprecated resource methods. This is an inventory, not a recommendation to allow all those groups: most are ordinary cleanup candidates, while loop/layout/signature choices may deserve local allowances to keep recovered logic readable. Library and library-test diagnostics duplicate many findings. A narrowly documented reconstruction allowance for precision/manual-clamp would therefore still leave substantive work before a strict workspace gate passes. [Clippy allowances](https://doc.rust-lang.org/clippy/usage.html)

## Implemented tooling follow-up

The subsequent authorized implementation pins Rust 1.99.0 with minimal profile, rustfmt/Clippy and the native ARM64 target; both packages inherit `rust-version = 1.99` and workspace lint policy. Editions and exact dependency versions are unchanged. The workspace explicitly permits only `excessive_precision` and `manual_clamp` to preserve recovered IEEE-754 source constants and existing NaN behavior. Scoped source allowances retain indexed recovered equations, staged setup, existing helper signatures, colocated tests, explicit presentation branches and the four existing Godot Resource duplication sites. Ordinary style cleanups use equivalent short-circuit conditions, comparisons, iterator/map APIs and remove a redundant borrow/conversion and unused example binding. No recovered floating-point equation or clamp expression was rewritten.

Rustfmt normalizes all workspace targets, including previously unformatted recovery examples. No custom rustfmt configuration is necessary. Clippy-driven let-chain cleanup changes indentation across some large presentation functions; it does not change the engine API or gameplay equations. Colocated test modules were retained rather than moved simply to satisfy a style diagnostic.

After implementation, `cargo fmt --all -- --check`, `cargo check --workspace --all-targets --locked`, and `cargo clippy --workspace --all-targets --locked -- -D warnings` all pass. Prepared core tests pass again: five unit tests and 89 integration tests, zero doctests. The integration-fixture and GPU-validation limitations above still apply. CI/editor/build-script integration belongs to the coordinating tooling change and was not authored in this Rust-only slice.

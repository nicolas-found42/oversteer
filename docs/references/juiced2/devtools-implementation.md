# Native developer tooling: research and implementation

Completed 2026-11-03 for the Rust/Godot Apple Silicon rebuild. All three delegated
research reports were finished before implementation started:

- [Rust and Godot audit](devtools-rust-godot-research.md)
- [Python and asset tooling audit](devtools-python-assets-research.md)
- [Repository, editor and CI audit](devtools-repository-dx-research.md)

Each report links its primary sources and distinguishes observations from proposals.
Gameplay development remains paused; this change establishes development checks.

## Decisions implemented

| Gap | Implementation |
| --- | --- |
| Floating Rust/Python tools | Rust1.99.0 with rustfmt/Clippy and native ARM64 target; Python3.13.16; uv lockfile; CI uv0.13.6. Godot4.7.2/gdext0.5.5/Parry pins and Cargo.lock unchanged. |
| No native quality entry point | `uv run --frozen python tools/game/dev.py check`: format checks, Python compile-without-execution, strict workspace/all-target Clippy, Ruff, and existing source unit suites. |
| Asset-dependent tests masquerading as generic tests | Default Rust selection is `--workspace --lib`; explicit `reference-tests` checks local prerequisites then runs full workspace tests. Missing fixtures fail, rather than silently skip. |
| Avatar unit fixture unnecessarily ignored | Test helper reads tracked `data/juiced2/native-avatar-components.json`; its1624436 bytes/SHA256b7486def... exactly matched the former generated catalog. No assertion or runtime asset path changed. |
| Recovered numeric code fails generic lints | Documented allowances preserve float literals, max/min NaN behavior and intentional source-indexed operations; routine style fixes and rustfmt adopted. No clamp/equation rewrite. |
| Python recovery corpus style debt | Strict host-tool checks/formatting; fatal correctness lint and compile checks still cover recovery workers. No bulk worker formatting or import-all execution. Four Ruff parser compatibility issues fixed with statement line breaks. |
| Incomplete Python dependencies | Non-installable uv project (`package=false`) with dev/assets/reference groups; existing exact NumPy/Pillow pins reused. Requirements files exported for compatibility. Blender retains its own Python. |
| Native editor defaults | Native Rust check/dev-build tasks, rust-analyzer, CodeLLDB, Ruff, generated-tree exclusions and Godot-host LLDB configuration. |
| Release DLL copied into debug path | Explicit Cargo dev profile updates debug path only; normal release path unchanged. Build refuses an open extension before and after compilation. Export requires release profile. |
| Missing source/runtime preflight | `doctor` checks native host/pinned source tools; `doctor --runtime` additionally verifies Godot version, architecture and prepared import metadata without rendering. |
| No native CI | SHA-pinned Actions, explicit ARM64 macos-26 runner, same local source gate; no original-asset download or renderer/performance claim. |
| Hooks/data conventions | Non-mutating Rustfmt hook, scoped Ruff policy, retained-evidence rewrite exclusions, native resource/binary attributes and ignored uv environment. Hook installation remains an explicit per-clone action. |

Rust toolchain files and selective Clippy configuration follow the
[Rustup override mechanism](https://rust-lang.github.io/rustup/overrides.html) and
[Clippy configuration](https://doc.rust-lang.org/clippy/usage.html). The uv
non-package project is a shared environment for standalone scripts, rather than
an installable library; its lock and dependency groups follow
[uv project management](https://docs.astral.sh/uv/concepts/projects/).
Ruff's nested lint/format policies follow its
[configuration documentation](https://docs.astral.sh/ruff/configuration/).

The hosted runner choice follows the current
[GitHub runner table](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
It establishes a native source-check environment, not the agreed M5 Pro renderer
or1080p60 benchmark. The debugger launches the Godot host, following
[gdext's debugging guidance](https://godot-rust.github.io/book/toolchain/debugging.html);
Godot script LSP/DAP is not the Rust debugger.

## Verified baseline after cleanup and review updates

- At pushed revision `ada2864be4a2225a580ead13ae081c970f88d74f`, `dev.py check`
  passed 27 Rust library tests and 36 Python tests: 16 game-tool, 6 donor-helper and 14
  reference-review tests. Syntax checks compiled 173 owned Python files without
  executing them; root Ruff and all 26 supported host-file format checks passed.
- Earlier tooling adoption also passed in an isolated source copy whose path contains
  spaces, without `godot/assets` or `artifacts`. Initial validation shared the
  public dependency compile cache; a separate cold-output run also passed with
  its own fresh Cargo build directory and no shared compiled workspace outputs.
  Only public source/dependency download caches were reused.
- Deliberate invalid Python, undefined Python name and Rust formatting probes
  failed the appropriate gates in that disposable copy; changes were restored.
  Missing Godot caused an actionable runtime-doctor failure.
- Prepared `reference-tests` passed all116 Rust tests (5 core unit,89 core
  integration,22 frontend unit), with zero failures/ignored tests.
- Source doctor and prepared-runtime doctor passed. The latter only queried
  Godot's version and read architecture/import metadata; it did not run the game.
- All hooks, configuration, lock consistency and whitespace checks passed.
  [Hosted ARM64 source CI passed `ada2864`](https://github.com/nicolas-found42/oversteer/actions/runs/41736476548).
  Interactive LLDB breakpoints remain unverified.
- Cargo.lock, runtime content and both deployed16a65 DLLs remain byte-identical.
  Current source formatting/lint and newline-only embedded-JSON changes require a new build boundary before
  generating new game acceptance evidence.

Earlier adoption logs are local under
`/tmp/oversteer-{dev-check,fresh-source-check,fresh-cold-source-check,reference-tests}.log`;
negative probes are recorded in `/tmp/oversteer-devtools-negative-checks.json`.
The final `ada2864` local checks used `/tmp/oversteer-push-*-final.log`.
These temporary logs are not portable or permanent gameplay evidence; the linked
hosted run provides the durable source-CI result. See `docs/game/HANDOFF.md` for
the paused runtime boundary and the exact local evidence paths.

## Deliberately separate work

The existing147 recovery workers retain style debt; an explicit advisory command
is documented in the native workflow. Broad type checking across Blender APIs,
new numerical fuzzing, dependency-advisory/license policy, nextest, compiler caches
and benchmark automation were not added speculatively. Dependency advisories can
be a separately pinned RustSec task; that does not validate original-asset rights.
No blanket type-check exclusion, paid classification, extraction, publication,
asset regeneration, native scenario, debugger entitlement change or release
performance run is part of the default developer gate.

## Adoption history and reference-review follow-up

The first push exposed one repository-scope mismatch: the native gate linted
`tools/`; repository-root linting found nine style
findings in `crates/oversteer-core/tools/recover_gameplay_config.py`. The gate now
uses `ruff check .` and `ruff format --check .`. That script was formatted and
its imports sorted; its non-import AST was verified unchanged.

The initially added blind-review pilot was included after its ten Python
tests and prepared Playwright UI test passed. Its Python tests now participate
in the shared gate, bringing the Python total at that revision to46. Dedicated
browser verification needs the local corpus and Playwright install.
It passed blind-payload checks, image loading, validation, persistence, annotation
export/import, wrong-pilot rejection and desktop/mobile layout without browser
errors. No gold human judgments or classification acceptance are inferred.

The subsequent pilot-hardening revision passed49 local Python tests and the
prepared116-test Rust suite. It protects existing scoring outputs and ensures
the browser harness builds the current template in a temporary pilot. One
browser-regression Python test is conditional on local corpus/Playwright inputs.
Apple Silicon hosted CI also passed revisions5c55ae0 and1c73755.

Repository cleanup then removed the superseded application and its dedicated
sprite/build/test tooling, retaining shared donor helpers and provenance used by
the native pipeline. The two native JSON catalogs received final newlines without
changing their parsed values. Reference review no longer asks for a reviewer name;
its backup schema remains compatible. Hierarchical category buttons and broader
category answers are covered by Python/browser tests. Broader answers remain
unresolved for exact-label precision and do not enable automatic acceptance.
The current browser harness builds the tracked template in a temporary pilot;
it does not update an existing human pilot or create human gold judgments. One
generic Python browser regression is conditional on local corpus/Playwright inputs;
its dedicated prepared run passed at `ada2864`, including hierarchical navigation,
persistence, broad-category and older exact-label import/export, search,
uncertainty, wrong-pilot rejection and desktop/mobile layout.

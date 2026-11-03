# Python asset and reference tooling: development tooling research

Research date: 2026-11-03. Research only; no source/configuration changes or automatic fixes applied. Scope: Python asset recovery, donor processing, Blender workers, reference vault and cheap validation, within the Apple Silicon / Godot 4.7.2 / gdext 0.5.5 project direction.

## Recommendation

Keep these standalone scripts. Use the existing uv workflow, one explicitly selected CPython 3.13 environment, pinned Ruff, and a small shared NumPy/Pillow dependency manifest. Add a dependency-free compile check across tracked Python files and run the existing two focused unittest suites. Keep extraction, asset publication, media downloads, paid classifications and Blender/GPU rendering out of the default check command. Do not introduce packaging, blanket type checking, mass formatting or imports of every script.

The existing broad lint policy is not a passing baseline. Start with compiler validation and a narrow correctness-rule gate, then enforce formatting only on a documented clean allowlist/new code. Existing findings must remain visible in an advisory audit; silently excluding the entire asset tree would conceal real defects.

## Local evidence

Repository sources inspected: [root configuration](../../../pyproject.toml), [development requirements](../../../requirements-dev.txt), [hooks](../../../.pre-commit-config.yaml), [native CI](../../../.github/workflows/native-quality.yml), [asset operations](../../../tools/game/assets/README.md), [car model requirements](../../../tools/carmodels/requirements.txt), [car model tests](../../../tools/carmodels/test_assets.py), [replay tests](../../../tools/game/test_replay_inputs.py).

- A local inventory found **203 Python files under tools/**, including **147 in tools/game/assets/**. The three primary families tools/game, tools/references and tools/carmodels contain 192 files. Counts describe this checkout, rather than a proposed fixed allowlist. Repository-wide compiler coverage should also include Python under crates/; that extra scope was not measured here.
- Root pyproject has no installable project; its Ruff target is py39 and rules E/F/W/I/B. requirements-dev pins Ruff 0.15.20, allows pre-commit>=4.0 and incorrectly claims all remaining scripts use only the standard library. tools/carmodels/requirements.txt actually pins numpy==2.5.4 and Pillow==13.0.0. Static import inventory finds NumPy in 34 tools files, Pillow in 27, bpy in 13 and mathutils in 12. Other nonstdlib import roots were local sibling/repository modules, not additional observed third-party packages.
- [vault_media.py](../../../tools/references/vault_media.py) uses hashlib.file_digest, imports Unix fcntl and invokes ffprobe/ffmpeg. The declared py39 tooling target does not describe its actual runtime floor; file_digest was added in Python 3.11 ([Python documentation](https://docs.python.org/3/library/hashlib.html#hashlib.file_digest)). CPython 3.13 is the selected tooling runtime, not a claim that every script was tested across Python versions.
- The asset README currently recommends `uv run --no-project --with numpy --with pillow python`, which resolves unpinned dependencies. Its production sequence requires a user-supplied game ISO and downloaded model artifacts, then modifies assets and tracked data. A fresh clone cannot perform complete extraction or parity verification.
- [preview_kits_blender.py](../../../tools/game/assets/preview_kits_blender.py) imports bpy/mathutils, deletes scene objects and renders at module scope. [apply_world_instances.py](../../../tools/game/assets/apply_world_instances.py) reads an inventory, opens the ISO and writes runtime models at module scope. Even [texturecombine_fixtures.py](../../../tools/game/assets/texturecombine_fixtures.py), despite its name and main guards, reads artifacts/programs.json at import time. Neither import-all validation nor globbing fixture scripts as tests is safe.

Discovery used `jg` first with the explicit tools/ root and four-request budget. It returned an incomplete-result notice and location-only leads, so direct source reads and exact searches supplied the evidence above. No claim of exhaustive behavioral discovery rests on that search.

## Measured checks and lint baseline

All commands below were read-only with respect to source. uv downloaded tooling/dependencies into its cache. Python commands used `-B` where applicable to avoid bytecode writes.

| Check | Observed result |
| --- | --- |
| CPython 3.13 `compile(source, filename, 'exec')` over all 203 tools Python files | All compile; none executed |
| CPython 3.15 AST parse over the same files | All parse |
| `python3 -B -m unittest discover -s tools/game -p test_replay_inputs.py` | 8 passed; native launch mocked |
| Ruff **0.15.20** `check tools/game tools/references tools/carmodels --target-version py313 --statistics` | 5,795 findings |
| Same pinned Ruff, `--select E9,F63,F7,F82` | Four parser diagnostics; no other selected findings |
| Same pinned Ruff, `format --check` on those families | 147 would reformat; 41 formatted; four parser errors; exit 2 |

The broad findings comprise E702 3,573; E501 954; E701 679; B023 165; I001 157; E401 127; B905 62; F401 37; E402 21; B007 7; parser diagnostics 4; E741 4; E722/E731 2 each; E703 1. These counts use the proposed py313 target. They are not comparable to a py39 run without accounting for version-sensitive rules.

Pinned Ruff reports parser errors at `audit_performance_globals.py:11:32`, `map_native_goal_icons.py:17:46`, `normalize_wheel_sockets.py:31:29`, and `recover_avatar_body_scales.py:19:69`. Each involves a semicolon followed by assignment to the identifier `match`. **CPython 3.13 compiles all four successfully.** Treat these as a Ruff parser compatibility limitation rather than broken Python; do not claim to have reproduced a Python SyntaxError. The installed unpinned Ruff 0.17.0 also reported these four. Resolve with a verified newer tool release or narrowly scoped statements-on-separate-lines changes if the implementation needs a green Ruff gate. Re-run the compiler check afterward. Do not globally ignore syntax diagnostics.

The test runs used tracked/local data in the present checkout. Replay tests build temporary fixtures, but the car model suite reads tracked policy files. A subsequent implementation must verify these commands from a fresh clone before advertising them as fresh-clone guarantees. No ISO extraction, asset publication, Blender render, game launch, media operation or paid classification was run.

## Concrete implementation plan after research completes

1. **Environment and requirements.** Retain the no-package pyproject. Set Ruff target-version to py313, document CPython 3.13 and pin the chosen interpreter version in the bootstrap/version file used by the parent tooling plan. Separate tool requirements from asset runtime requirements. Reuse the existing exact NumPy/Pillow versions instead of independently floating the same dependencies in asset documentation; ideally move ownership to `tools/requirements-assets.txt` and let the carmodel requirements include it. Keep Pillow's distribution name distinct from its PIL import name. Do not add bpy, mathutils, an SDK for local sibling imports, or pytest merely to run unittest.
2. **Reproducibility.** Pin pre-commit as well as Ruff if retained. For a full reproducible environment, maintain a short input requirements file and a generated, hash-bearing lock using `uv pip compile --python-version 3.13 --generate-hashes`, followed by `uv pip sync --require-hashes`. Verify resolution/wheels on macOS arm64; this report successfully installed the two existing runtime pins locally. Exact Python and uv versions belong in the toolchain manifest/bootstrap so a successful dependency resolution is not mistaken for a fully pinned toolchain. uv documents compiling and syncing requirements separately ([uv locking environments](https://docs.astral.sh/uv/pip/compile/)). A new installable Python project/uv workspace is not needed.
3. **Cheap mandatory checks.** Add one short static compile script over tracked `.py` sources, excluding generated/vendor material by explicit inventory. Compile in memory rather than importing modules or writing pyc files. Python supports compiling parsed source without executing it ([Python AST documentation](https://docs.python.org/3/library/ast.html)). Add the two explicit unittest commands; keep launch mocked and make runtime requirements available only where needed. A third future test should use synthetic bytes for pure parsers such as native_collision rather than an ISO, but adding a large test framework is unnecessary now.
4. **Lint rollout.** Use pinned Ruff and narrow E9/F63/F7/F82 correctness checks across owned Python after handling the four parser limitations. Do not disable F821 to accommodate Blender: bpy/mathutils are explicitly imported, and undefined-name lint does not require their installation ([Ruff F821](https://docs.astral.sh/ruff/rules/undefined-name/)). Preserve broad rules on the already-clean shared tool subset, with a documented advisory full-tree command. Keep formatter rollout separate and bounded. Ruff supports per-file ignores and separate lint/format exclusions; explicit file arguments and hook behavior require care when configuring excludes ([Ruff configuration](https://docs.astral.sh/ruff/configuration/)). Use explicit hook file scopes or force-exclude so a commit cannot unexpectedly rewrite the recovery corpus.
5. **Explicit operational tier.** Provide opt-in commands/documentation for extraction, media preparation, vault classification, Blender and native renderer verification. List required ISO/model paths, writable output locations, external binaries, and credential requirements per operation. A dependency preflight should report what is missing without downloading media, invoking classification, rendering or publishing. The default check must not call each CLI with `--help`: several scripts execute work before parsing arguments.

Example environment setup (proposed, not executed as a repository edit):

```sh
uv venv --python 3.13 .venv
uv pip sync --python .venv/bin/python --require-hashes requirements-dev.lock
uv pip sync --python .venv-assets/bin/python --require-hashes tools/requirements-assets.lock
```

Create `.venv-assets` with `uv venv --python 3.13 .venv-assets` before the last command. Separate environments avoid `sync` deleting the other tier's packages. A single environment with a combined lock is also valid if the parent plan prefers fewer environments. Do not run sequential syncs of unrelated locks into one environment.

uv supports no-project script execution, explicit runtime constraints and script-specific locks ([uv running scripts](https://docs.astral.sh/uv/guides/scripts/)). Shared requirements are the smaller fit here because scripts import one another and use the same NumPy/Pillow pair; adding inline metadata and one lock per script would duplicate ownership across hundreds of files.

## Blender and artifact verification boundary

Blender owns its Python interpreter/API. Keep it outside the uv runtime lock; record and verify its accepted application version and macOS arm64 build separately. Blender's module build is a distinct integration path, not a prerequisite for existing workers ([Blender Python module documentation](https://developer.blender.org/docs/handbook/building_blender/python_module/)). For opt-in worker verification, use the pinned application with `--background --python-exit-code 1 --python path/to/worker.py` and a bounded runtime. Blender documents the exception exit-code switch ([official command-line arguments](https://docs.blender.org/manual/en/3.6/advanced/command_line/arguments.html)); verify flags with the selected installed release rather than assuming the cited older manual fixes its version. Do not add `--factory-startup` indiscriminately where a worker expects saved scene state.

Static compile/lint covers Blender files without GPU work. Successful static checks do not establish glTF export compatibility, native shader parity, material fidelity, Blender operator context or render acceptance. Artifact-backed checks should fail clearly when explicitly requested without prerequisites; the ordinary fresh-clone gate should simply contain no artifact-backed operation. A green cheap gate must describe its limited coverage rather than say all asset tooling works.

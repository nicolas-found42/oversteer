## Change

Describe the observable change and link the specification or issue.

## Verification

- [ ] `uv run --frozen python tools/game/dev.py check`
- [ ] Relevant source tests
- [ ] `uv run --frozen python tools/game/dev.py reference-tests` (when local fixtures are required)
- [ ] Native runtime or rendered scenario (when behavior or presentation changed)

List the checks actually run and their results. Source checks alone do not establish
visual, gameplay, performance, or release acceptance.

## Behavior and evidence

Identify affected simulation invariants, save/replay contracts, or presentation.
For native runs, include input, extension and content identities plus relevant
reference-vault comparisons. Explain any changed baseline; do not regenerate one
merely to hide a regression. Keep original disc assets and credentials local.

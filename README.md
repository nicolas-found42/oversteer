# Oversteer

The active rebuild is a native Apple Silicon racing game in Rust, using
**Godot 4.7.2 + gdext 0.5.5**. It reconstructs Juiced 2's single-player
experience from the local reference vault and recovered game data, with the
accepted 30 donor vehicles. Implementation and acceptance work are in progress
under [the specification](https://github.com/nicolas-found42/oversteer/issues/1).

```sh
uv run --frozen python tools/game/dev.py check

# After preparing the local game assets:
uv run --frozen python tools/game/bootstrap.py
uv run --frozen python tools/game/build.py run
uv run --frozen python tools/game/build.py export --skip-build
```

See [the native game workflow](docs/game/README.md) for asset preparation,
controls, verification and packaging. See [CONTRIBUTING.md](CONTRIBUTING.md) for
source checks and [the documentation index](docs/README.md) for project references.

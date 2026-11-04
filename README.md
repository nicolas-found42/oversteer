# Oversteer

The active rebuild is a native Apple Silicon racing game in Rust, using
**Godot 4.7.2 + gdext 0.5.5**. Oversteer is an independent single-player racing
game with the accepted 30 donor vehicles, arcade handling, car customization,
career progression, betting and pink slips. The existing reference vault informs
quality rather than requiring reconstruction of another game.
Implementation and validation are in progress under the
[accepted pivot plan](docs/design/OVERSTEER_PIVOT_INTERVIEW.md).

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

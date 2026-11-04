"""Exercise repeated settings changes in the native renderer without taking focus."""

import subprocess
import tempfile
from pathlib import Path

import background_window


def main():
    root = Path(__file__).resolve().parents[2]
    godot = root / "build/tools/godot-4.7.2/Godot.app/Contents/MacOS/Godot"
    with tempfile.TemporaryDirectory(prefix="oversteer-menu-focus-") as directory:
        output = Path(directory)
        result = subprocess.run(
            [
                str(godot),
                "--path",
                str(root / "godot"),
                "--rendering-driver",
                "metal",
                "--script",
                str(Path(__file__).with_name("menu_focus.gd")),
                "--",
                "--save-file",
                str(output / "save.json"),
                "--settings-dir",
                str(output / "settings"),
            ],
            env=background_window.environment(godot),
            timeout=60,
        )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

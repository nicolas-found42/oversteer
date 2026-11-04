"""Launch the pinned macOS renderer without activating its app or windows."""

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_suffix(".m")
LIBRARY = ROOT / "build/tools/background-window.dylib"
MARKER = "Oversteer background window guard installed"


def environment(executable):
    """Fail closed if the app cannot load the guard, before opening any window."""
    if not LIBRARY.exists() or SOURCE.stat().st_mtime_ns > LIBRARY.stat().st_mtime_ns:
        LIBRARY.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["clang", "-dynamiclib", "-framework", "AppKit", str(SOURCE), "-o", str(LIBRARY)],
            check=True,
            capture_output=True,
            text=True,
        )
    env = {**os.environ, "DYLD_INSERT_LIBRARIES": str(LIBRARY)}
    probe = subprocess.run(
        [str(executable), "--headless", "--version"],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    if probe.returncode or MARKER not in probe.stderr:
        raise RuntimeError(f"Cannot protect desktop focus; launch cancelled: {probe.stderr}")
    return env

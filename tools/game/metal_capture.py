"""Local diagnostic Godot signing and bounded native Metal frame capture."""

import hashlib
import json
import plistlib
import re
import shutil
import subprocess


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnostic_engine(source):
    """Preserve the pinned app; sign only a separate, identified local copy."""
    source_app = source.parents[2]
    source_hash = digest(source)
    folder = source_app.parent.parent / "godot-metal-diagnostic" / source_hash[:16]
    target_app = folder / "Godot.app"
    target = target_app / "Contents/MacOS/Godot"
    manifest = folder / "identity.json"
    if target_app.exists():
        identity = json.loads(manifest.read_text())
        if identity["source_sha256"] != source_hash or identity["diagnostic_sha256"] != digest(
            target
        ):
            raise RuntimeError("Diagnostic Godot identity changed; inspect before reusing")
    else:
        entitlements = plistlib.loads(
            subprocess.run(
                ["codesign", "-d", "--entitlements", "-", "--xml", str(source_app)],
                check=True,
                capture_output=True,
            ).stdout
        )
        entitlements["com.apple.security.get-task-allow"] = True
        folder.mkdir(parents=True, exist_ok=True)
        entitlement_file = folder / "debug.entitlements"
        entitlement_file.write_bytes(plistlib.dumps(entitlements))
        shutil.copytree(source_app, target_app, symlinks=True)
        signed = subprocess.run(
            [
                "codesign",
                "-s",
                "-",
                "--deep",
                "--force",
                "--options=runtime",
                "--entitlements",
                str(entitlement_file),
                str(target_app),
            ],
            capture_output=True,
            text=True,
        )
        (folder / "codesign.log").write_text(signed.stdout + signed.stderr)
        signed.check_returncode()
        identity = {
            "source": str(source),
            "source_sha256": source_hash,
            "diagnostic": str(target),
            "diagnostic_sha256": digest(target),
            "entitlements": entitlements,
            "scope": "Ad-hoc signed local diagnostic engine; never distribute this copy",
        }
        manifest.write_text(json.dumps(identity, indent=2) + "\n")
    subprocess.run(["codesign", "--verify", "--deep", "--strict", str(target_app)], check=True)
    if digest(source) != source_hash:
        raise RuntimeError("Pinned Godot changed during diagnostic preparation")
    return target, identity


def presented_layer(output):
    """Require one presented Godot frame, never silently capture a device buffer."""
    candidates = re.findall(r"^\s*(\d+)\s+Layer\s+.*GodotContentView.*$", output, re.MULTILINE)
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one GodotContentView layer in capture boundaries")
    return candidates[0]


def capture_boundary(output, window_can_draw):
    if window_can_draw:
        return presented_layer(output), "one presented frame"
    candidates = re.findall(
        r"^\s*(\d+)\s+Queue\s+Godot Main Command Queue.*$", output, re.MULTILINE
    )
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one Godot main command queue")
    return candidates[
        0
    ], "one Godot main-queue command buffer; covered window, not a presented frame"


def capture_frame(pid, folder):
    """Capture one settled inspection view; release the script even on failure."""
    result = {"passed": False, "pid": pid}
    try:
        boundaries = subprocess.run(
            ["/usr/bin/gpucapture", "boundaries", "--pid", str(pid)],
            capture_output=True,
            text=True,
            timeout=15,
        )
        (folder / "metal-boundaries.log").write_text(boundaries.stdout + boundaries.stderr)
        boundaries.check_returncode()
        view = json.loads((folder / "metal-capture-ready.json").read_text())
        boundary, scope = capture_boundary(boundaries.stdout, view["window_can_draw"])
        trace = folder / "frame.gputrace"
        command = [
            "/usr/bin/gpucapture",
            "start",
            "--pid",
            str(pid),
            "--boundary",
            boundary,
            "--count",
            "1",
            "--output",
            str(trace),
        ]
        with (folder / "metal-capture.log").open("w") as log:
            completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=90)
        completed.check_returncode()
        files = [p for p in trace.rglob("*") if p.is_file()] if trace.is_dir() else [trace]
        size = sum(p.stat().st_size for p in files)
        if not size:
            raise RuntimeError("GPU trace is empty")
        result.update(
            {
                "passed": True,
                "command": command,
                "trace_bytes": size,
                "view": view,
                "scope": scope,
            }
        )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result["error"] = str(error)
    finally:
        (folder / "metal-capture.json").write_text(json.dumps(result, indent=2) + "\n")
        (folder / "metal-capture-done").touch()
    return result

"""Sample timestamped reference media and build the local Juiced 2 evidence gallery."""

from __future__ import annotations

import argparse
import concurrent.futures
import fcntl
import hashlib
import html
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VAULT = ROOT / "artifacts/juiced2-vault"
SHOWINFO = re.compile(r"\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([\d.eE+-]+)")


def read_json(path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def classification_status(row):
    status = str(row.get("status", row.get("classification_status", ""))).lower()
    error = str(row.get("error", "")).lower()
    if (
        row.get("error")
        or row.get("pending")
        or any(term in status for term in ["pending", "blocked", "awaiting", "unclassified"])
    ):
        return (
            "awaiting_credits" if "402" in error or "credit" in error + status else "awaiting_jev"
        )
    return "complete" if row.get("screen_state") else "awaiting_jev"


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError(f"{command[0]} failed: {result.stderr[-3000:]}")
    return result


def probe(video):
    return json.loads(
        run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "format=duration:stream=width,height,start_time,duration",
                "-of",
                "json",
                str(video),
            ]
        ).stdout
    )


def platform(info):
    title = info.get("title", "")
    declared = info.get("platform_declared")
    if declared:
        return declared
    matches = [
        name
        for pattern, name in [
            (r"\bPS2\b|PlayStation 2", "PS2"),
            (r"\bPSP\b", "PSP"),
            (r"\bPS3\b|PlayStation 3", "PS3"),
            (r"Xbox 360|X360", "Xbox 360"),
            (r"\bPC\b|Windows", "PC"),
            (r"\bNDS\b|Nintendo DS", "Nintendo DS"),
        ]
        if re.search(pattern, title, re.I)
    ]
    return " / ".join(matches) if matches else "Unspecified by title"


def frame_record(vault, path, source, info, timestamp, sampling):
    with Image.open(path) as image:
        width, height = image.size
    return {
        "id": f"{source}-{round(timestamp * 1000000):012d}",
        "kind": "frame",
        "path": path.relative_to(vault).as_posix(),
        "source_id": source,
        "source_url": info.get("webpage_url", f"https://www.youtube.com/watch?v={source}"),
        "source_title": info.get("title", source),
        "source_video": next(
            p.relative_to(vault).as_posix()
            for p in (vault / "videos").glob(source + ".*")
            if p.suffix in {".mp4", ".webm"}
        ),
        "platform_declared": platform(info),
        "timestamp_seconds": timestamp,
        "sampling": sampling,
        "width": width,
        "height": height,
        "sha256": digest(path),
    }


def scene_candidates(path):
    candidates = []
    timestamp = None
    for line in path.read_text().splitlines():
        match = re.search(r"pts_time:([\d.eE+-]+)", line)
        if match:
            timestamp = float(match.group(1))
        elif line.startswith("lavfi.scene_score=") and timestamp is not None:
            score = float(line.split("=", 1)[1])
            if score > 0.10:
                candidates.append((score, timestamp))
    chosen = []
    for score, timestamp in sorted(candidates, reverse=True):
        if all(abs(timestamp - previous[1]) >= 2 for previous in chosen):
            chosen.append((score, timestamp))
        if len(chosen) == 40:
            break
    return chosen


def sample_video(vault, video, uniform_interval=3.0):
    source = video.stem
    directory = vault / "frames" / source
    directory.mkdir(parents=True, exist_ok=True)
    cache = directory / "sampling.json"
    stat = video.stat()
    identity = {"bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}
    previous = read_json(cache, {})
    if (
        previous.get("video_identity") == identity
        and previous.get("sampling_version") == 2
        and previous.get("requested_uniform_interval_seconds", float("inf")) <= uniform_interval
        and all((vault / row["path"]).exists() for row in previous.get("assets", []))
    ):
        print(f"cached {source}: {len(previous['assets'])} frames", flush=True)
        return previous["assets"]
    info = read_json(video.with_suffix(".info.json"), {})
    metadata = probe(video)
    # Audio can outlast the last video frame; focused seeks must stay inside video.
    duration = float(metadata["streams"][0].get("duration", metadata["format"]["duration"]))
    interval = max(uniform_interval, duration / 2499.0)
    print(f"sampling {source}: {duration:.1f}s, interval {interval:.2f}s", flush=True)
    retained = previous.get("assets", []) if previous.get("video_identity") == identity else []
    records = {round(row["timestamp_seconds"] * 1000000): row for row in retained}
    hashes = {row["sha256"]: vault / row["path"] for row in retained}
    with tempfile.TemporaryDirectory(prefix="sampling-", dir=directory) as work:
        work = Path(work)
        scores = work / "scene-scores.txt"
        graph = (
            "[0:v]split=2[u][s];"
            f"[u]select='isnan(prev_selected_t)+gte(t-prev_selected_t,{interval:.9f})',"
            "scale='min(1280,iw)':-2,showinfo[uniform];"
            "[s]select='isnan(prev_selected_t)+gte(t-prev_selected_t,0.5)',"
            "scale=160:-2,select='gte(scene,0)',"
            f"metadata=mode=print:key=lavfi.scene_score:file='{scores}'[scenes]"
        )
        result = run(
            [
                "ffmpeg",
                "-hide_banner",
                "-nostdin",
                "-threads",
                "2",
                "-i",
                str(video),
                "-filter_complex_threads",
                "2",
                "-filter_complex",
                graph,
                "-map",
                "[uniform]",
                "-fps_mode",
                "vfr",
                "-q:v",
                "3",
                str(work / "uniform-%05d.jpg"),
                "-map",
                "[scenes]",
                "-fps_mode",
                "vfr",
                "-f",
                "null",
                "-",
            ]
        )
        times = [float(value) for value in SHOWINFO.findall(result.stderr)]
        images = sorted(work.glob("uniform-*.jpg"))
        if len(times) != len(images):
            raise RuntimeError(
                f"{source}: showinfo/image count mismatch {len(times)}/{len(images)}"
            )

        def retain(image, timestamp, sampling):
            key = round(timestamp * 1000000)
            if key in records:
                if sampling not in records[key]["sampling"]:
                    records[key]["sampling"].append(sampling)
                return
            checksum = digest(image)
            if checksum in hashes:
                # Identical decoded JPEG bytes share one file; retain each source time.
                destination = hashes[checksum]
            else:
                destination = directory / f"{key:012d}.jpg"
                if destination.exists():
                    if digest(destination) != checksum:
                        raise RuntimeError(f"Existing frame bytes changed: {destination}")
                else:
                    shutil.copyfile(image, destination)
                hashes[checksum] = destination
            records[key] = frame_record(vault, destination, source, info, timestamp, [sampling])

        for image, timestamp in zip(images, times):
            retain(image, timestamp, "uniform")
        strongest = scene_candidates(scores)
        targets = [(timestamp, "scene") for _, timestamp in strongest]
        for _, timestamp in strongest[:5]:
            targets.extend(
                (max(0, min(duration - 0.1, timestamp + delta)), "burst") for delta in [-1, 0, 1]
            )
        for timestamp, sampling in sorted(targets):
            nearby = next(
                (
                    key
                    for key in records
                    if abs(records[key]["timestamp_seconds"] - timestamp) < 0.001
                ),
                None,
            )
            if nearby is not None:
                if sampling not in records[nearby]["sampling"]:
                    records[nearby]["sampling"].append(sampling)
                continue
            output = work / "focused.jpg"
            result = run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-nostdin",
                    "-threads",
                    "2",
                    "-ss",
                    f"{timestamp:.9f}",
                    "-copyts",
                    "-i",
                    str(video),
                    "-an",
                    "-vf",
                    "scale='min(1280,iw)':-2,showinfo",
                    "-frames:v",
                    "1",
                    "-fps_mode",
                    "vfr",
                    "-q:v",
                    "3",
                    str(output),
                ]
            )
            focused_times = SHOWINFO.findall(result.stderr)
            if not focused_times or not output.exists():
                raise RuntimeError(f"{source}: missing focused frame near {timestamp}")
            retain(output, float(focused_times[0]), sampling)
    assets = sorted(records.values(), key=lambda row: row["timestamp_seconds"])
    write_json(
        cache,
        {
            "sampling_version": 2,
            "requested_uniform_interval_seconds": uniform_interval,
            "video_identity": identity,
            "video_duration_seconds": duration,
            "source_video": video.relative_to(vault).as_posix(),
            "uniform_interval_seconds": interval,
            "scene_policy": "2fps maximum; top40 scene scores >0.10; separated >=2s",
            "burst_policy": "five strongest scenes; selected frame plus -1s/+1s",
            "timestamp_authority": "ffmpeg showinfo decoded source PTS (copyts on input seeks)",
            "assets": assets,
        },
    )
    print(f"finished {source}: {len(assets)} frames", flush=True)
    return assets


def sample(vault, workers, uniform_interval=3.0):
    videos = sorted(
        path
        for path in (vault / "videos").iterdir()
        if path.suffix in {".mp4", ".webm"} and ".f" not in path.name
    )
    assets = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        for rows in pool.map(lambda video: sample_video(vault, video, uniform_interval), videos):
            assets.extend(rows)
    merge(vault)


def merge(vault, make_sheets=True):
    """Publish completed per-source caches without starting another decoder."""
    # Independent decoding batches can finish together; publish one coherent snapshot at a time.
    with (vault / "frames/.merge.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        _merge(vault, make_sheets)


def _merge(vault, make_sheets):
    assets = []
    for cache in sorted((vault / "frames").glob("*/sampling.json")):
        assets.extend(read_json(cache)["assets"])
    for screenshot in read_json(vault / "sources/screenshots.json", []):
        path = vault / screenshot["path"]
        with Image.open(path) as image:
            width, height = image.size
        assets.append(
            {
                **screenshot,
                "kind": "press-screenshot",
                "source_id": screenshot["id"],
                "source_url": screenshot["url"],
                "width": width,
                "height": height,
                "sha256": digest(path),
                "sampling": ["press-screenshot"],
            }
        )
    write_json(vault / "assets.json", assets)
    print(f"assets.json: {len(assets)} assets", flush=True)
    if make_sheets:
        contact_sheets(vault, assets)


def focus(vault):
    segments_path = vault / "focus-segments.json"
    segments = read_json(segments_path, [])
    for segment in segments:
        source = segment["source_id"]
        directory = vault / "frames" / source
        cache = read_json(directory / "sampling.json")
        if not cache:
            raise ValueError(f"Sample source first: {source}")
        cached_ids = {row["id"] for row in cache["assets"]}
        if segment.get("samples") and all(
            row["asset_id"] in cached_ids for row in segment["samples"]
        ):
            print(f"cached focused segment: {source} {segment['start_seconds']}", flush=True)
            continue
        video = vault / cache["source_video"]
        info = read_json(video.with_suffix(".info.json"), {})
        start, end = segment["start_seconds"], segment["end_seconds"]
        interval = segment["interval_seconds"]
        records = {round(row["timestamp_seconds"] * 1000000): row for row in cache["assets"]}
        hashes = {row["sha256"]: vault / row["path"] for row in cache["assets"]}
        selected = []
        with tempfile.TemporaryDirectory(prefix="focused-", dir=directory) as work:
            work = Path(work)
            graph = (
                f"select='lte(t,{end:.9f})*(isnan(prev_selected_t)+"
                f"gte(t-prev_selected_t,{interval - 0.000001:.9f}))',"
                "scale='min(1280,iw)':-2,showinfo"
            )
            result = run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-nostdin",
                    "-threads",
                    "2",
                    "-ss",
                    str(start),
                    "-t",
                    str(end - start + 0.1),
                    "-copyts",
                    "-i",
                    str(video),
                    "-an",
                    "-vf",
                    graph,
                    "-fps_mode",
                    "vfr",
                    "-q:v",
                    "3",
                    str(work / "%05d.jpg"),
                ]
            )
            times = [float(value) for value in SHOWINFO.findall(result.stderr)]
            images = sorted(work.glob("*.jpg"))
            if len(times) != len(images) or not times:
                raise RuntimeError(f"Focused showinfo/image mismatch: {source}")
            for image, timestamp in zip(images, times):
                key = round(timestamp * 1000000)
                if key not in records:
                    checksum = digest(image)
                    destination = hashes.get(checksum, directory / f"{key:012d}.jpg")
                    if not destination.exists():
                        shutil.copyfile(image, destination)
                    hashes[checksum] = destination
                    records[key] = frame_record(
                        vault, destination, source, info, timestamp, ["focused"]
                    )
                elif "focused" not in records[key]["sampling"]:
                    records[key]["sampling"].append("focused")
                selected.append({"asset_id": records[key]["id"], "timestamp_seconds": timestamp})
        cache["assets"] = sorted(records.values(), key=lambda row: row["timestamp_seconds"])
        write_json(directory / "sampling.json", cache)
        segment["samples"] = selected
        segment["timestamp_authority"] = "decoded ffmpeg showinfo PTS with copyts input seek"
        segment["source_video"] = cache["source_video"]
        print(f"focused {source} {start}–{end}: {len(selected)} samples", flush=True)
    write_json(segments_path, segments)
    sample(vault, 1)


def contact_sheets(vault, assets):
    directory = vault / "contact-sheets"
    directory.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(size=12)
    sheets = []
    sources = dict.fromkeys(row["source_id"] for row in assets)
    for source in sources:
        rows = [row for row in assets if row["source_id"] == source]
        if rows[0]["kind"] == "press-screenshot":
            continue
        for page in range(math.ceil(len(rows) / 24)):
            batch = rows[page * 24 : (page + 1) * 24]
            sheet = Image.new("RGB", (1280, 6 * 206), "#10151d")
            draw = ImageDraw.Draw(sheet)
            for index, row in enumerate(batch):
                x, y = index % 4 * 320, index // 4 * 206
                with Image.open(vault / row["path"]) as image:
                    image.thumbnail((316, 176))
                    sheet.paste(image, (x + (320 - image.width) // 2, y))
                text = row["id"] + f"\n{row.get('timestamp_seconds', 0):.3f}s"
                draw.text((x + 3, y + 177), text, fill="white", font=font)
            path = directory / f"{source}-{page + 1:03d}.jpg"
            sheet.save(path, quality=88)
            sheets.append(
                {
                    "path": path.relative_to(vault).as_posix(),
                    "source_id": source,
                    "asset_ids": [row["id"] for row in batch],
                }
            )
    screenshots = [row for row in assets if row["kind"] == "press-screenshot"]
    for page in range(math.ceil(len(screenshots) / 24)):
        batch = screenshots[page * 24 : (page + 1) * 24]
        sheet = Image.new("RGB", (1280, 6 * 206), "#10151d")
        draw = ImageDraw.Draw(sheet)
        for index, row in enumerate(batch):
            x, y = index % 4 * 320, index // 4 * 206
            with Image.open(vault / row["path"]) as image:
                image.thumbnail((316, 176))
                sheet.paste(image, (x + (320 - image.width) // 2, y))
            draw.text((x + 3, y + 177), row["id"], fill="white", font=font)
        path = directory / f"press-screenshots-{page + 1:03d}.jpg"
        sheet.save(path, quality=88)
        sheets.append(
            {
                "path": path.relative_to(vault).as_posix(),
                "source_id": "press",
                "asset_ids": [row["id"] for row in batch],
            }
        )
    write_json(directory / "index.json", sheets)
    return sheets


def validate(vault, assets, classifications):
    errors = []
    ids = set()
    durations = {}
    for row in assets:
        if row["id"] in ids:
            errors.append(f"duplicate asset id: {row['id']}")
        ids.add(row["id"])
        path = vault / row["path"]
        if not path.is_file():
            errors.append(f"missing: {row['path']}")
            continue
        if digest(path) != row["sha256"]:
            errors.append(f"hash mismatch: {row['id']}")
        with Image.open(path) as image:
            if image.size != (row["width"], row["height"]):
                errors.append(f"dimension mismatch: {row['id']}")
        if row["kind"] == "frame":
            video = vault / row["source_video"]
            if not video.exists():
                errors.append(f"missing source video: {row['id']}")
                continue
            if str(video) not in durations:
                durations[str(video)] = float(probe(video)["format"]["duration"])
            if not 0 <= row["timestamp_seconds"] <= durations[str(video)]:
                errors.append(f"timestamp out of bounds: {row['id']}")
    unknown = [row.get("id") for row in classifications if row.get("id") not in ids]
    if unknown:
        errors.append(f"classification ids absent from assets: {unknown[:10]}")
    asset_lookup = {row["id"]: row for row in assets}
    classified_ids = set()
    for row in classifications:
        if row["id"] in classified_ids:
            errors.append(f"duplicate classification id: {row['id']}")
        classified_ids.add(row["id"])
        asset = asset_lookup.get(row["id"])
        if asset and row.get("image_sha256") not in {None, asset["sha256"]}:
            errors.append(f"classification image hash mismatch: {row['id']}")
        for key in ["raw_response", "request"]:
            if row.get(key) and not (vault / row[key]).is_file():
                errors.append(f"missing {key}: {row['id']}")
    sheets = read_json(vault / "contact-sheets/index.json", [])
    sheet_ids = []
    for sheet in sheets:
        if not (vault / sheet["path"]).is_file():
            errors.append(f"missing contact sheet: {sheet['path']}")
        sheet_ids.extend(sheet["asset_ids"])
    if set(sheet_ids) != ids or len(sheet_ids) != len(ids):
        errors.append("contact sheet coverage does not match assets")
    result = {
        "status": "pass" if not errors else "fail",
        "assets": len(assets),
        "frames": sum(row["kind"] == "frame" for row in assets),
        "press_screenshots": sum(row["kind"] == "press-screenshot" for row in assets),
        "sources": len(durations),
        "classifications": len(classifications),
        "classification_row_coverage": "complete" if classified_ids == ids else "partial",
        "completed_classifications": sum(
            classification_status(row) == "complete" for row in classifications
        ),
        "classification_coverage": "complete"
        if len(classifications) == len(assets)
        and all(classification_status(row) == "complete" for row in classifications)
        else "partial",
        "unclassified_assets": len(assets)
        - sum(classification_status(row) == "complete" for row in classifications),
        "pending_classifications": len(assets)
        - sum(classification_status(row) == "complete" for row in classifications),
        "pending_credit_classifications": sum(
            classification_status(row) == "awaiting_credits" for row in classifications
        ),
        "classification_errors": sum(
            bool(row.get("error")) and "pending" not in str(row.get("status", ""))
            for row in classifications
        ),
        "screen_states_needing_review": sum(
            bool(row.get("screen_review")) for row in classifications
        ),
        "errors": errors,
        "checks": [
            "unique ids",
            "file existence",
            "SHA-256",
            "image dimensions",
            "source video existence",
            "timestamps within source duration",
            "classification references",
            "classification image hash binding and raw artifact links",
            "contact sheet existence and exact asset coverage",
        ],
        "limitations": [
            "Structural validation does not establish semantic accuracy.",
            "A still frame cannot establish a temporal gameplay rule.",
        ],
    }
    write_json(vault / "validation.json", result)
    return result


def build(vault):
    assets = read_json(vault / "assets.json", [])
    classifications = read_json(vault / "judgments/classifications.json", [])
    if isinstance(classifications, dict):
        classifications = classifications.get("assets", classifications.get("results", []))
    lookup = {row["id"]: row for row in classifications}
    rows = []
    for asset in assets:
        judgment = lookup.get(asset["id"], {})
        if not re.fullmatch(r"[A-Za-z0-9_-]+", asset["id"]):
            raise ValueError("Unsafe asset identifier")
        details = f"judgments/details/{asset['id']}.json"
        write_json(vault / details, {"asset": asset, "classification": judgment})
        compact = {
            key: judgment[key]
            for key in [
                "screen_state",
                "screen_review",
                "tags",
                "uncertain_tags",
                "facets",
                "facet_review",
                "domain",
                "domain_review",
                "scores",
                "raw_response",
                "request",
                "error",
                "game_visible_probability",
            ]
            if key in judgment
        }
        compact["tag_probabilities"] = {
            key: value
            for key, value in judgment.get("tag_probabilities", {}).items()
            if key in judgment.get("tags", []) or key in judgment.get("uncertain_tags", [])
        }
        compact["classification_status"] = classification_status(judgment)
        compact["scores"] = {
            key: {field: value[field] for field in ["score", "confidence"] if field in value}
            if isinstance(value, dict)
            else value
            for key, value in judgment.get("scores", {}).items()
        }
        compact["region_count"] = len(judgment.get("regions", {}))
        if judgment.get("domain"):
            compact["facets"] = {**compact.get("facets", {}), "domain": judgment["domain"]}
        row = {
            key: value
            for key, value in asset.items()
            if key
            not in {
                "sha256",
                "bytes",
                "behavior_authority",
            }
        }
        rows.append({**row, "judgment": compact, "details_path": details})
    sheets = read_json(vault / "contact-sheets/index.json", [])
    sheet_ids = [asset_id for sheet in sheets for asset_id in sheet["asset_ids"]]
    if (
        set(sheet_ids) != {row["id"] for row in assets}
        or len(sheet_ids) != len(assets)
        or not all((vault / sheet["path"]).exists() for sheet in sheets)
    ):
        sheets = contact_sheets(vault, assets)
    category_indexes(vault, assets, lookup)
    data = json.dumps(rows, ensure_ascii=False).replace("<", "\\u003c")
    sheet_links = " ".join(
        f'<a href="{html.escape(row["path"])}">{html.escape(row["source_id"])} · {index + 1}</a>'
        for index, row in enumerate(sheets)
    )
    document = GALLERY.replace("__ASSETS__", data).replace("__SHEETS__", sheet_links)
    (vault / "index.html").write_text(document)
    result = validate(vault, assets, classifications)
    print(json.dumps(result), flush=True)
    if result["errors"]:
        raise RuntimeError("Vault validation failed")


def category_indexes(vault, assets, lookup):
    """Write links into the shared catalog, keeping proposed labels explicit."""
    catalog = read_json(vault / "judgments/catalog.json", {})
    questions = catalog.get("questions", {})
    screens = questions.get("screen", {}).get("criteria", {})
    tags = {
        key: value.get("instructions", "")
        for key, value in questions.items()
        if value.get("type") == "noul" and key != "game_visible"
    }
    for group, definitions in [("categories", screens), ("tags", tags)]:
        root_index = [
            f"# {group.title()}",
            "",
            "Accepted means a classifier threshold was met, not independent verification.",
            "Proposed labels remain unresolved. Empty categories are coverage gaps.",
            "",
        ]
        for label, description in definitions.items():
            if not re.fullmatch(r"[a-z0-9]+(?:[-/][a-z0-9]+)*", label):
                raise ValueError(f"Unsafe catalog path: {label}")
            directory = vault / group / label
            directory.mkdir(parents=True, exist_ok=True)
            lines = [f"# {label}", "", str(description), ""]
            matched = []
            for asset in assets:
                judgment = lookup.get(asset["id"], {})
                if group == "categories":
                    if judgment.get("screen_state") != label:
                        continue
                    proposed = judgment.get("screen_review", True)
                    probability = judgment.get("screen_distribution", {}).get(label)
                else:
                    if label in judgment.get("tags", []):
                        proposed = False
                    elif label in judgment.get("uncertain_tags", []):
                        proposed = True
                    else:
                        continue
                    probability = judgment.get("tag_probabilities", {}).get(label)
                proposed = proposed or classification_status(judgment) != "complete"
                matched.append((asset, proposed, probability, judgment))
            accepted = sum(not row[1] for row in matched)
            proposed_count = len(matched) - accepted
            lines.extend([f"{accepted} accepted · {proposed_count} proposed", ""])
            if not matched:
                lines.extend(
                    ["No matching sampled evidence. This does not prove game absence.", ""]
                )
            for asset, proposed, probability, judgment in matched:
                image = Path(os.path.relpath(vault / asset["path"], directory)).as_posix()
                status = "PROPOSED / REVIEW" if proposed else "ACCEPTED BY THRESHOLD"
                confidence = "" if probability is None else f" · p={probability:.3f}"
                links = [f"[{asset['id']}]({image})"]
                if asset.get("source_video"):
                    timestamp = asset["timestamp_seconds"]
                    video = Path(os.path.relpath(vault / asset["source_video"], directory))
                    links.append(
                        f"[local video {timestamp:.3f}s]({video.as_posix()}#t={timestamp})"
                    )
                    separator = "&" if "?" in asset["source_url"] else "?"
                    links.append(f"[YouTube]({asset['source_url']}{separator}t={int(timestamp)}s)")
                else:
                    links.append(f"[source]({asset.get('source_page', asset['source_url'])})")
                if judgment.get("raw_response"):
                    raw = Path(os.path.relpath(vault / judgment["raw_response"], directory))
                    links.append(f"[raw judgment]({raw.as_posix()})")
                lines.append(f"- **{status}**{confidence} · " + " · ".join(links))
            (directory / "index.md").write_text("\n".join(lines) + "\n")
            root_index.append(
                f"- [{label}]({label}/index.md): {accepted} accepted / {proposed_count} proposed"
            )
        (vault / group / "index.md").write_text("\n".join(root_index) + "\n")


GALLERY = r"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Juiced 2 · Reference vault</title>
<style>
:root{color-scheme:dark;font:15px system-ui;background:#10151d;color:#e9edf4}
body{margin:0;padding:24px}h1{margin:0 0 8px}p{color:#b8c3d4;max-width:1000px}
a{color:#89c6ff}header{position:sticky;top:0;background:#10151df5;padding:12px 0;z-index:1}
input,select{padding:10px;background:#202a38;color:white;border:1px solid #506078;border-radius:6px}
input{min-width:280px}#grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px}
article{background:#1c2633;border:1px solid #36445a;border-radius:8px;overflow:hidden}
article img{width:100%;aspect-ratio:16/9;object-fit:contain;background:black}
.copy{padding:12px}.tags{font-size:12px;line-height:1.7;color:#adc8dd;overflow-wrap:anywhere}
.uncertain{color:#f5c677}small{display:block;color:#adb6c8;margin:6px 0}
summary{cursor:pointer}pre{font-size:11px;white-space:pre-wrap;max-height:300px;overflow:auto}
#sheets{max-height:40vh;overflow:auto}#sheets a{display:inline-block;margin:5px}
header{max-height:35vh;overflow:auto}header select{max-width:280px;margin:3px}
button{padding:10px;cursor:pointer}
</style>
<h1>Juiced 2 reference vault</h1>
<p id="coverage" role="status"></p>
<p>Timestamped video frames and promotional screenshots. Categories and facets are model judgments;
uncertain results remain visible. A frame supports appearance observations;
behavior needs surrounding
footage. Platform labels come from source declarations and are not independently authenticated.</p>
<details><summary>Contact sheets</summary><div id="sheets">__SHEETS__</div></details>
<header><input id="search" placeholder="Search ID, state, tags, source…" aria-label="Search">
<select id="category" aria-label="Primary category">
<option value="">All categories</option></select>
<select id="platform" aria-label="Declared platform">
<option value="">All platforms</option></select>
<select id="tag" aria-label="Positive tag"><option value="">All positive tags</option></select>
<select id="family" aria-label="Category family">
<option value="">All category families</option></select>
<select id="tagfamily" aria-label="Tag family"><option value="">All tag families</option></select>
<select id="source" aria-label="Source"><option value="">All sources</option></select>
<select id="status" aria-label="Jev status"><option value="">All Jev statuses</option></select>
<select id="readability" aria-label="Jev readability score band">
<option value="">All Jev readability scores</option><option value="high">2.5–3</option>
<option value="medium">1.5–2.5</option><option value="low">0–1.5</option>
<option value="unjudged">Unjudged</option></select><span id="facetfilters"></span>
<label><input type="checkbox" id="uncertain" style="min-width:0"> Needs review</label>
<small id="count"></small></header><main id="grid"></main>
<button id="more" hidden>Show 80 more</button>
<script type="application/json" id="assets">__ASSETS__</script>
<script>
const assets=JSON.parse(document.getElementById('assets').textContent);
const el=id=>document.getElementById(id);
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',
'"':'&quot;',"'":'&#39;'}[c]));
const state=a=>a.judgment.screen_state||'Unclassified';
const tags=a=>a.judgment.tags||[];
const status=a=>a.judgment.classification_status||'awaiting_jev';
const readability=a=>{const v=a.judgment.scores?.['score/readability']?.score;
return v===undefined?'unjudged':v>=2.5?'high':v>=1.5?'medium':'low'};
const complete=assets.filter(a=>status(a)==='complete').length;
el('coverage').textContent=`${assets.length} media assets · ${complete} completed Jev records · `+
`${assets.length-complete} awaiting Jev. Pending/API errors are operational status, `+
`not game categories or evidence that a feature is absent. All judgments remain proposed evidence.`;
const review=a=>a.judgment.screen_review||a.judgment.error||
(a.judgment.uncertain_tags||[]).length||(a.judgment.facet_review||[]).length;
function options(id,values){for(const value of [...new Set(values)].filter(Boolean).sort()){
const option=document.createElement('option');option.value=value;
option.textContent=value;el(id).append(option)}}
options('category',assets.map(state));options('platform',assets.map(a=>a.platform_declared));
options('tag',assets.flatMap(tags));
options('family',assets.map(a=>state(a).split('/')[0]));
options('tagfamily',assets.flatMap(tags).map(t=>t.split('/')[0]));
options('source',assets.map(a=>a.source_id));options('status',assets.map(status));
const facetKeys=[...new Set(assets.flatMap(a=>Object.keys(a.judgment.facets||{})))].sort();
for(const key of facetKeys){const select=document.createElement('select');select.id='facet:'+key;
select.setAttribute('aria-label',key);const option=document.createElement('option');
option.value='';option.textContent='All '+key;select.append(option);
el('facetfilters').append(select);
options(select.id,assets.map(a=>a.judgment.facets?.[key]));select.addEventListener('input',filter)}
const searchIndex=new Map(assets.map(a=>[a.id,[a.id,a.source_id,a.source_title,a.platform_declared,
state(a),...tags(a),...(a.judgment.uncertain_tags||[]),
...Object.values(a.judgment.facets||{})].join(' ').toLowerCase()]));
let filtered=[],limit=80;
function render(){el('count').textContent=`${filtered.length} / ${assets.length} assets · `+
`showing ${Math.min(limit,filtered.length)}`;
el('grid').innerHTML=filtered.slice(0,limit).map(a=>{
const j=a.judgment,t=a.timestamp_seconds,video=a.source_video?
`<a href="${escape(a.source_video)}#t=${t}">Local video · ${Number(t).toFixed(3)}s</a>`:'';
const youtube=a.kind==='frame'?
`${a.source_url}${a.source_url.includes('?')?'&':'?'}t=${Math.floor(t)}s`:a.source_url;
return `<article id="${escape(a.id)}"><a href="${escape(a.path)}">
<img loading="lazy" src="${escape(a.path)}" alt="${escape(a.id)}"></a>
<div class="copy"><b>${escape(state(a))}</b>
<small>${!j.screen_state?'Unclassified':j.screen_review?
'Proposed screen label · review':'Screen classifier threshold met'}</small>
<small class="uncertain">Jev status: ${escape(status(a))}</small>
<div class="tags">${Object.entries(j.facets||{}).map(([k,v])=>
`${escape(k)}: ${escape(v)}${(j.facet_review||[]).includes(k)?' ?':''}`).join(' · ')}</div>
<small>${escape(a.id)} · ${escape(a.platform_declared)} · ${a.width}×${a.height}px</small>
<div class="tags">${tags(a).map(t=>escape(t)+
(j.tag_probabilities?.[t]===undefined?'':' ('+j.tag_probabilities[t].toFixed(2)+')'))
.join(' · ')}</div>
<div class="tags uncertain">${(j.uncertain_tags||[]).map(x=>'? '+escape(x)).join(' · ')}
${j.error?'Classification error':''}</div>
<small>${escape(a.source_title||a.source_id)} · ${escape((a.sampling||[]).join(', '))}</small>
${video} · <a href="${escape(youtube)}">${a.kind==='frame'?'YouTube at time':'Source image'}</a>
${a.source_page?` · <a href="${escape(a.source_page)}">Source page</a>`:''}
<details><summary>Evidence and classification details${review(a)?' · review':''}</summary>
<small>Jev score estimates (0–3): ${escape(JSON.stringify(j.scores||{}))}</small>
${j.region_count?`<small>Proposed region locations: ${j.region_count}.
Full coordinates in JSON.</small>`:''}
<a href="${escape(a.details_path)}">Full asset JSON · all probabilities, regions and transitions</a>
${j.raw_response?`<a href="${escape(j.raw_response)}">Raw judgment</a>`:''}
${j.request?` · <a href="${escape(j.request)}">Exact request (.gz)</a>`:''}
</details></div></article>`}).join('');
el('more').hidden=limit>=filtered.length;}
function filter(){const q=el('search').value.toLowerCase();filtered=assets.filter(a=>
(!q||searchIndex.get(a.id).includes(q))&&(!el('category').value||state(a)===el('category').value)&&
(!el('platform').value||a.platform_declared===el('platform').value)&&
(!el('family').value||state(a).split('/')[0]===el('family').value)&&
(!el('tagfamily').value||tags(a).some(t=>t.startsWith(el('tagfamily').value+'/')))&&
(!el('source').value||a.source_id===el('source').value)&&
(!el('status').value||status(a)===el('status').value)&&
(!el('readability').value||readability(a)===el('readability').value)&&
facetKeys.every(k=>!el('facet:'+k).value||a.judgment.facets?.[k]===el('facet:'+k).value)&&
(!el('tag').value||tags(a).includes(el('tag').value))&&(!el('uncertain').checked||review(a)));limit=80;render()}
for(const id of ['search','category','platform','tag','uncertain','family','tagfamily',
'source','status','readability'])
el(id).addEventListener('input',filter);
el('more').addEventListener('click',()=>{limit+=80;render()});filter();
</script></html>"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sample", "focus", "merge", "build"])
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--uniform-interval", type=float, default=3.0)
    parser.add_argument("--skip-contact-sheets", action="store_true")
    args = parser.parse_args()
    vault = args.vault.resolve()
    if args.command == "sample":
        sample(vault, args.workers, args.uniform_interval)
    elif args.command == "focus":
        focus(vault)
    elif args.command == "merge":
        merge(vault, not args.skip_contact_sheets)
    else:
        build(vault)


if __name__ == "__main__":
    main()

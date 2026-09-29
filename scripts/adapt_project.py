#!/usr/bin/env python3
"""Compile a full-scene pack and new narration schedule into a frame-exact plan.

This is deliberately a *planner*, not a source-code text replacer. The pack
runtime consumes each scene's knots to call the original scene at a source
clock, while camera footage and subtitles always use the output clock.
"""

from __future__ import annotations

import argparse
import bisect
from functools import lru_cache
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET


class AdaptError(ValueError):
    """Actionable input or media error, without a Python traceback."""


VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".svg"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AdaptError(message)


def number(value: object, name: str, *, positive: bool = False) -> float:
    require(isinstance(value, (float, int)) and not isinstance(value, bool), f"{name} must be a number")
    x = float(value)
    require(math.isfinite(x), f"{name} must be finite")
    if positive:
        require(x > 0, f"{name} must be positive")
    return x


def integer(value: object, name: str, *, minimum: int = 0) -> int:
    x = number(value, name)
    require(x.is_integer() and x >= minimum, f"{name} must be an integer >= {minimum}")
    return int(x)


def frame_of(seconds: object, fps: int, name: str) -> int:
    return int(math.floor(number(seconds, name) * fps + 0.5))


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AdaptError(f"Cannot read JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def tidy(text: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFKC", text).casefold() if ch.isalnum())


def parse_srt(path: Path) -> list[dict]:
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise AdaptError(f"Cannot read transcript {path}: {exc}") from exc
    rows = []
    stamp = re.compile(r"(?P<h>\d{2}):(?P<m>\d{2}):(?P<s>\d{2})[,.](?P<ms>\d{3})")
    for chunk in re.split(r"\r?\n\s*\r?\n", raw.strip()):
        lines = chunk.strip().splitlines()
        time_index = next((i for i, line in enumerate(lines) if "-->" in line), -1)
        if time_index < 0:
            continue
        matches = stamp.findall(lines[time_index])
        require(len(matches) >= 2, f"Bad SRT timestamp in {path}: {lines[time_index]}")
        def sec(parts: tuple[str, str, str, str]) -> float:
            h, m, s, ms = map(int, parts)
            return h * 3600 + m * 60 + s + ms / 1000
        start, end = sec(matches[0]), sec(matches[1])
        require(0 <= start < end, f"Bad SRT cue span at {lines[time_index]}")
        text = " ".join(line.strip() for line in lines[time_index + 1:] if line.strip())
        require(bool(text), f"Empty SRT cue at {lines[time_index]}")
        cue_id = lines[0].strip() if time_index > 0 else str(len(rows) + 1)
        rows.append({"id": cue_id, "start": start, "end": end, "text": text})
    require(bool(rows), f"No subtitle cues found in {path}")
    return rows


def transcript_rows(value: object, spec_dir: Path) -> list[dict]:
    if value is None:
        return []
    if isinstance(value, str):
        return parse_srt(resolve_path(value, spec_dir))
    require(isinstance(value, list), "transcript must be an SRT path or timed cue array")
    rows = []
    for i, item in enumerate(value):
        require(isinstance(item, dict), f"transcript[{i}] must be an object")
        start = number(item.get("start"), f"transcript[{i}].start")
        end = number(item.get("end"), f"transcript[{i}].end")
        require(0 <= start < end, f"transcript[{i}] has invalid time span")
        text = item.get("text")
        require(isinstance(text, str) and tidy(text), f"transcript[{i}].text is empty")
        words = item.get("words", [])
        require(isinstance(words, list), f"transcript[{i}].words must be an array")
        clean_words = []
        for j, word in enumerate(words):
            require(isinstance(word, dict), f"transcript[{i}].words[{j}] must be an object")
            ws = number(word.get("start"), f"word {i}/{j}.start")
            we = number(word.get("end"), f"word {i}/{j}.end")
            wt = word.get("text")
            require(start <= ws < we <= end + 0.001, f"word {i}/{j} lies outside subtitle")
            require(isinstance(wt, str) and tidy(wt), f"word {i}/{j} has no text")
            clean_words.append({"start": ws, "end": we, "text": wt})
        rows.append({"id": str(item.get("id", i + 1)), "start": start, "end": end, "text": text, "words": clean_words})
    return rows


def resolve_path(raw: str, base: Path) -> Path:
    require(bool(raw.strip()), "A media path cannot be empty")
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def phrase_time(binding: dict, transcript: list[dict], start: float, end: float) -> float:
    phrase = binding.get("phrase")
    line_id = binding.get("line")
    require(bool(phrase) != bool(line_id), "Cue binding needs exactly one of phrase or line")
    candidates = []
    if line_id:
        candidates = [row["start"] for row in transcript if str(row["id"]) == str(line_id)
                      and start - 0.5 <= row["start"] < end + 0.5]
    else:
        target = tidy(str(phrase))
        require(bool(target), "Cue phrase is empty after punctuation removal")
        for row in transcript:
            if not start - 0.5 <= row["start"] < end + 0.5:
                continue
            whole = tidy(row["text"])
            if whole == target:
                candidates.append(row["start"])
                continue
            words = row.get("words", [])
            if not words:
                if target in whole:
                    raise AdaptError(f"'{phrase}' is inside subtitle '{row['text']}' but only line timing exists; provide word timings or an explicit at")
                continue
            joined = ""
            starts: dict[int, float] = {}
            for word in words:
                starts[len(joined)] = word["start"]
                joined += tidy(word["text"])
            pos = joined.find(target)
            while pos >= 0:
                if pos in starts:
                    candidates.append(starts[pos])
                pos = joined.find(target, pos + 1)
    occurrence = binding.get("occurrence")
    if occurrence is not None:
        require(isinstance(occurrence, int) and occurrence >= 1, "occurrence must be a 1-based integer")
        require(len(candidates) >= occurrence, f"Phrase/line has only {len(candidates)} timed matches, occurrence={occurrence}")
        return candidates[occurrence - 1]
    require(len(candidates) == 1, f"Phrase/line needs exactly one timed match within scene; found {len(candidates)}. Set occurrence or explicit at")
    return candidates[0]


@lru_cache(maxsize=8192)
def probe_media(path: Path, expected: str) -> dict:
    require(path.is_file(), f"Missing {expected} file: {path}")
    require(path.stat().st_size > 0, f"Empty {expected} file: {path}")
    suffix = path.suffix.lower()
    allowed = {"image": IMAGE_EXT, "video": VIDEO_EXT, "audio": AUDIO_EXT}[expected]
    require(suffix in allowed, f"{expected} slot needs {sorted(allowed)}, got: {path}")
    if suffix == ".svg":
        try:
            root = ET.parse(path).getroot()
            vb = root.attrib.get("viewBox", "").replace(",", " ").split()
            width, height = (float(vb[2]), float(vb[3])) if len(vb) == 4 else (0, 0)
        except (ET.ParseError, OSError, ValueError) as exc:
            raise AdaptError(f"Invalid SVG image {path}: {exc}") from exc
        require(width > 0 and height > 0, f"SVG must have a positive viewBox: {path}")
        return {"width": width, "height": height}
    require(bool(shutil.which("ffprobe")), "ffprobe is required to validate media slots; run doctor")
    proc = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
                          capture_output=True, text=True, check=False)
    require(proc.returncode == 0, f"Unreadable {expected} media {path}: {proc.stderr.strip()[:280]}")
    try:
        meta = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AdaptError(f"ffprobe returned invalid metadata for {path}") from exc
    want = "audio" if expected == "audio" else "video"
    streams = [s for s in meta.get("streams", []) if s.get("codec_type") == want]
    require(bool(streams), f"{path} has no {want} stream")
    stream = streams[0]
    result = {"width": stream.get("width"), "height": stream.get("height")}
    duration = stream.get("duration") or meta.get("format", {}).get("duration")
    if duration is not None:
        try:
            result["duration"] = float(duration)
        except (TypeError, ValueError):
            pass
    return result


def check_aspect(meta: dict, slot: dict, label: str) -> None:
    aspect = slot.get("aspect")
    if aspect is None or aspect == "preserve":
        return
    if isinstance(aspect, str) and ":" in aspect:
        left, right = aspect.split(":", 1)
        try:
            expected = number(float(left), f"{label}.aspect numerator", positive=True) / number(float(right), f"{label}.aspect denominator", positive=True)
        except ValueError as exc:
            raise AdaptError(f"{label}.aspect must be a ratio such as 16:9") from exc
    else:
        expected = number(aspect, f"{label}.aspect", positive=True)
    width, height = meta.get("width"), meta.get("height")
    require(width and height, f"Cannot determine media aspect for {label}")
    tolerance = number(slot.get("aspectTolerance", 0.12), f"{label}.aspectTolerance")
    require(tolerance >= 0, f"{label}.aspectTolerance must be nonnegative")
    require(abs(width / height / expected - 1) <= tolerance,
            f"{label} aspect {width}:{height} differs from required {aspect} beyond {tolerance:.0%}")


def slot_bindings(scene: dict, target: dict, spec_dir: Path, project: Path | None,
                  asset_definitions: dict | None = None) -> tuple[dict, list[dict]]:
    asset_definitions = asset_definitions or {}
    declared = scene.get("slots", [])
    require(isinstance(declared, list), f"Pack scene {scene['id']}.slots must be an array")
    supplied = target.get("slots", {})
    require(isinstance(supplied, dict), f"{target.get('id', scene['id'])}.slots must be an object")
    ids = {s.get("id") for s in declared if isinstance(s, dict)}
    require(len(ids) == len(declared) and None not in ids, f"Pack scene {scene['id']} has invalid or repeated slot ids")
    unknown = sorted(set(supplied) - ids)
    require(not unknown, f"Unknown slots for {scene['id']}: {', '.join(unknown)}")
    values, details = {}, []
    for slot in declared:
        slot_id = slot["id"]
        kind = slot.get("type", "text")
        require(kind in {"text", "dynamicText", "image", "video", "audio", "sequence", "wall", "wall-sprites", "talk", "number", "color"},
                f"Unknown slot type {kind!r} in {scene['id']}.{slot_id}")
        value = supplied.get(slot_id)
        if value is None and kind == "talk" and project is not None:
            value = "@talk"
        if value is None:
            require(not slot.get("required", True), f"Missing required slot {scene['id']}.{slot_id} ({kind})")
            continue
        label = f"{scene['id']}.{slot_id}"
        if isinstance(value, dict) and kind not in {"sequence", "wall", "wall-sprites"}:
            value = value.get("text") if kind in {"text", "dynamicText"} else value.get("path", value.get("value"))
        if kind in {"text", "dynamicText"}:
            require(isinstance(value, str) and value.strip(), f"{label} needs nonempty text")
            max_chars = slot.get("maxChars")
            if max_chars is not None:
                require(len(value) <= integer(max_chars, f"{label}.maxChars", minimum=1),
                        f"{label} has {len(value)} chars; template allows {max_chars}. Rewrite or choose another scene")
        elif kind == "number":
            value = number(value, label)
            if "min" in slot:
                require(value >= number(slot["min"], f"{label}.min"),
                        f"{label} must be at least {slot['min']}")
            if "max" in slot:
                require(value <= number(slot["max"], f"{label}.max"),
                        f"{label} must be at most {slot['max']}")
        elif kind == "color":
            require(isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value) is not None,
                    f"{label} needs a six-digit #RRGGBB color")
        elif kind == "talk":
            require(value is True or value == "@talk", f"{label} must use @talk after the edited narration is imported")
            require(project is not None, f"{label} needs --project to verify imported narration")
            require((project / "talkmap.js").is_file() and any((project / "talk").rglob("*.jpg")),
                    f"{label}: import the edited narration first; talkmap.js or talk frames are missing in {project}")
            value = "@talk"
        elif kind in {"sequence", "wall", "wall-sprites"}:
            raw = value.get("path") if isinstance(value, dict) else value
            pattern = value.get("glob", "*.jpg" if kind == "wall-sprites" else "*") if isinstance(value, dict) else ("*.jpg" if kind == "wall-sprites" else "*")
            require(isinstance(raw, str) and isinstance(pattern, str), f"{label} needs path and optional glob")
            path = resolve_path(raw, spec_dir)
            require(path.is_dir(), f"{label} sequence directory is missing: {path}")
            files = sorted(p for p in path.glob(pattern) if p.is_file() and p.suffix.lower() in IMAGE_EXT)
            if kind in {"sequence", "wall-sprites"}:
                non_jpeg = [file.name for file in files if file.suffix.lower() != ".jpg"]
                require(not non_jpeg, f"{label} needs prepared JPEG frames; found {non_jpeg[:3]}")
            definition = asset_definitions.get(slot_id, {})
            authored_count = definition.get("originalFrames") if kind == "sequence" else None
            full_wall_count = (definition.get("originalSprites", definition.get("originalItems"))
                               if kind == "wall-sprites" else None)
            if full_wall_count is not None:
                full_wall_count = integer(full_wall_count, f"{label}.originalSprites", minimum=27)
            min_files = integer(slot.get("minFiles", authored_count or (27 if kind == "wall-sprites" else 1)),
                                f"{label}.minFiles", minimum=1)
            require(len(files) >= min_files, f"{label} needs {min_files} images, found {len(files)} in {path}")
            if kind == "sequence" and authored_count:
                expected_frames = [path / f"f_{i:04d}.jpg" for i in range(1, authored_count + 1)]
                missing_frames = [frame.name for frame in expected_frames if not frame.is_file()]
                require(not missing_frames,
                        f"{label} needs contiguous prepared JPEG f_0001.jpg.."
                        f"f_{authored_count:04d}.jpg; missing {missing_frames[:3]}")
            if kind == "wall-sprites":
                require(all(file.parent == path for file in files),
                        f"{label} wall sprite sheets must be directly inside {path}, not nested")
                expected_names = [f"{i:03d}.jpg" for i in range(len(files))]
                actual_names = [file.name for file in files]
                require(actual_names == expected_names,
                        f"{label} wall needs contiguous 000.jpg..{len(files)-1:03d}.jpg; prepare the complete new wall first")
                if full_wall_count is not None:
                    require(len(files) == full_wall_count,
                            f"{label} needs {full_wall_count} prepared sprite sheets for the full choreography; "
                            "run this pack's prepare_media.py. Fewer unique works may be repeated across the "
                            "display only when their real count is retained in wall-meta.json")
                    meta_path = path / "wall-meta.json"
                    wall_meta = read_json(meta_path)
                    unique_works = integer(wall_meta.get("uniqueWorks"),
                                           f"{label}.wall-meta.uniqueWorks", minimum=27)
                    require(unique_works <= full_wall_count,
                            f"{label}.wall-meta.uniqueWorks exceeds {full_wall_count} displayed sheets")
                    if "displayTiles" in wall_meta:
                        require(integer(wall_meta["displayTiles"], f"{label}.wall-meta.displayTiles")
                                == full_wall_count,
                                f"{label}.wall-meta.displayTiles must equal {full_wall_count}")
                    index_path = path / "index.json"
                    try:
                        wall_index = json.loads(index_path.read_text(encoding="utf-8"))
                    except (OSError, json.JSONDecodeError) as exc:
                        raise AdaptError(f"{label} needs prepared index.json beside wall-meta.json: {exc}") from exc
                    require(isinstance(wall_index, list) and len(wall_index) == full_wall_count,
                            f"{label}.index.json must list all {full_wall_count} display sheets")
                    slugs = [entry.get("slug") if isinstance(entry, dict) else None
                             for entry in wall_index]
                    require(all(isinstance(slug, str) and slug.strip() for slug in slugs),
                            f"{label}.index.json needs a nonempty slug for every sheet")
                    require(len(set(slugs)) == unique_works,
                            f"{label}.wall-meta.uniqueWorks={unique_works} does not match "
                            f"{len(set(slugs))} distinct index.json works")
            empty = [file.name for file in files if file.stat().st_size <= 0]
            require(not empty, f"{label} has {len(empty)} empty images such as {empty[:3]}")
            # Full existence/size scan, then representative decode/aspect probes.
            # Thousands of ffprobe launches make even a valid sequence unusably slow.
            probe_indices = sorted({0, len(files) // 4, len(files) // 2, 3 * len(files) // 4, len(files) - 1})
            for file in (files[index] for index in probe_indices):
                meta = probe_media(file, "image")
                check_aspect(meta, slot, label)
                if kind == "wall-sprites":
                    width, height = meta.get("width"), meta.get("height")
                    require(width and height and width % 4 == 0 and height % 4 == 0
                            and abs(width / height / (16 / 9) - 1) <= 0.025,
                            f"{label} sprite {file.name} must be a 4×4 sheet with 16:9 tile ratio")
            value = {"path": str(path), "glob": pattern, "count": len(files),
                     "decodedSamples": len(probe_indices)}
            if kind == "wall-sprites" and full_wall_count is not None:
                value["uniqueWorks"] = unique_works
        else:
            require(isinstance(value, str), f"{label} needs a media path")
            path = resolve_path(value, spec_dir)
            meta = probe_media(path, kind)
            check_aspect(meta, slot, label)
            value = str(path)
        if slot.get("mustChange"):
            baselines = [slot[key] for key in ("sourceText", "demoFallback", "placeholder")
                         if key in slot and slot[key] is not None]
            require(bool(baselines), f"{label} sets mustChange without sourceText, demoFallback or placeholder")
            def unchanged(original: object) -> bool:
                if kind == "number":
                    try:
                        return value == float(original)
                    except (TypeError, ValueError):
                        return False
                return isinstance(original, str) and isinstance(value, str) and value.strip() == original.strip()
            require(not any(unchanged(original) for original in baselines),
                    f"{label} still uses its original placeholder; supply new episode content")
        values[slot_id] = value
        details.append({"id": slot_id, "type": kind, "value": value,
                        **{k: slot[k] for k in ("selector", "sourceText", "sourceSpans", "sourceAsset", "renderContext", "source", "binding", "maxChars") if k in slot}})
    return values, details


def interpolate(x: float, points: list[tuple[float, float]]) -> float:
    sources = [point[0] for point in points]
    idx = bisect.bisect_right(sources, x)
    if idx <= 0:
        return points[0][1]
    if idx >= len(points):
        return points[-1][1]
    a, b = points[idx - 1], points[idx]
    return a[1] + (x - a[0]) * (b[1] - a[1]) / (b[0] - a[0])


def cue_binding(value: object, transcript: list[dict], start: float, end: float, fps: int, label: str) -> int:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return frame_of(value, fps, label)
    if isinstance(value, str):
        value = {"phrase": value}
    require(isinstance(value, dict), f"{label} cue needs at, frame, line or phrase")
    choices = [key for key in ("at", "frame", "line", "phrase") if key in value]
    require(len(choices) == 1, f"{label} cue needs exactly one of at, frame, line, phrase")
    if "frame" in value:
        frame = value["frame"]
        require(isinstance(frame, int) and not isinstance(frame, bool), f"{label}.frame must be integer")
        return frame
    if "at" in value:
        return frame_of(value["at"], fps, f"{label}.at")
    return frame_of(phrase_time(value, transcript, start, end), fps, label)


def motion_windows(source: dict, source_start: float, source_end: float,
                   cue_values: list[dict], src_fps: int) -> list[dict]:
    """Merge overlapping authored action spans; no editable hold exists inside one."""
    scene_id = source["id"]
    raw = source.get("motionWindows", [])
    require(isinstance(raw, list), f"{scene_id}.motionWindows must be an array")
    known_cues = {cue["id"]: cue["sourceAt"] for cue in cue_values}
    spans = []
    ids = set()
    for i, item in enumerate(raw):
        require(isinstance(item, dict), f"{scene_id}.motionWindows[{i}] must be an object")
        window_id = item.get("id", f"motion-{i + 1}")
        require(isinstance(window_id, str) and window_id and window_id not in ids,
                f"{scene_id} motion-window IDs must be unique")
        ids.add(window_id)
        start = number(item.get("start"), f"{scene_id}.{window_id}.start")
        end = number(item.get("end"), f"{scene_id}.{window_id}.end")
        require(source_start <= start < end <= source_end,
                f"{scene_id}.{window_id} must lie inside its original scene")
        require(end - start >= 1 / src_fps - 1e-8,
                f"{scene_id}.{window_id} must protect at least one original frame")
        anchor = item.get("anchorCue")
        if anchor is not None:
            require(anchor in known_cues, f"{scene_id}.{window_id} unknown anchorCue {anchor}")
            require(start <= known_cues[anchor] <= end,
                    f"{scene_id}.{window_id} anchorCue {anchor} falls outside its action window")
        spans.append({"ids": [window_id], "start": start, "end": end,
                      "anchorCues": [anchor] if anchor else []})
    spans.sort(key=lambda x: (x["start"], x["end"]))
    merged = []
    for span in spans:
        if merged and span["start"] <= merged[-1]["end"] + 1e-8:
            previous = merged[-1]
            previous["end"] = max(previous["end"], span["end"])
            previous["ids"].extend(span["ids"])
            previous["anchorCues"].extend(span["anchorCues"])
        else:
            merged.append(span)
    return merged


def timed_scene(source: dict, target: dict, source_index: int, output_start: int, output_end: int,
                fps: int, src_fps: int, transcript: list[dict], slots: dict, binding_details: list[dict]) -> dict:
    scene_id = source["id"]
    src = source.get("source")
    require(isinstance(src, dict), f"{scene_id}.source needs start and end")
    src_start = number(src.get("start"), f"{scene_id}.source.start")
    src_end = number(src.get("end"), f"{scene_id}.source.end")
    require(0 <= src_start < src_end, f"{scene_id}.source must have increasing nonnegative times")
    target_frames = output_end - output_start
    min_frames = integer(source.get("minFrames", 1), f"{scene_id}.minFrames", minimum=1)
    require(target_frames >= min_frames, f"{scene_id} needs at least {min_frames} frames, got {target_frames}; choose fewer beats or more narration")
    max_hold = source.get("maxHoldFrames")
    if max_hold is not None:
        extra = target_frames - frame_of(src_end - src_start, fps, "source length")
        require(extra <= integer(max_hold, f"{scene_id}.maxHoldFrames"),
                f"{scene_id} would add {extra} hold frames (limit {max_hold}); split narration into another scene")
    authored_cues = source.get("cues", [])
    require(isinstance(authored_cues, list), f"{scene_id}.cues must be an array")
    supplied = target.get("cues", {})
    require(isinstance(supplied, dict), f"Target {scene_id}.cues must be an object")
    cue_ids = {cue.get("id") for cue in authored_cues if isinstance(cue, dict)}
    require(len(cue_ids) == len(authored_cues) and None not in cue_ids, f"{scene_id} has invalid or repeated cue ids")
    unknown = sorted(set(supplied) - cue_ids)
    require(not unknown, f"Unknown cues for {scene_id}: {', '.join(unknown)}")
    explicit: list[tuple[float, float]] = [(src_start, output_start), (src_end, output_end)]
    cue_values: list[dict] = []
    for cue in authored_cues:
        cue_id = cue["id"]
        at = number(cue.get("at"), f"{scene_id}.{cue_id}.at")
        require(src_start <= at <= src_end, f"{scene_id}.{cue_id} lies outside source scene")
        if cue_id in supplied:
            out = cue_binding(supplied[cue_id], transcript, output_start / fps, output_end / fps,
                              fps, f"{scene_id}.{cue_id}")
            require(output_start <= out <= output_end, f"{scene_id}.{cue_id} target is outside selected scene")
            explicit.append((at, out))
        else:
            require(not cue.get("required", cue.get("kind") in {"word", "semantic"}),
                    f"Bind semantic cue {scene_id}.{cue_id} to a new spoken word/line or explicit time")
            out = None
        cue_values.append({"id": cue_id, "sourceAt": at, "outputFrame": out, "kind": cue.get("kind", "beat"),
                           "explicit": out is not None, "lockBeforeFrames": cue.get("lockBeforeFrames", 0),
                           "lockAfterFrames": cue.get("lockAfterFrames", cue.get("lockFrames", 0))})
    explicit.sort()
    compact_explicit = []
    for point in explicit:
        if compact_explicit and abs(point[0] - compact_explicit[-1][0]) < 1e-8:
            require(point[1] == compact_explicit[-1][1],
                    f"Cue order for {scene_id} gives different target frames for one source time")
            continue
        compact_explicit.append(point)
    explicit = compact_explicit
    for prev, nxt in zip(explicit, explicit[1:]):
        require(nxt[0] > prev[0] and nxt[1] > prev[1],
                f"Cue order for {scene_id} conflicts with original choreography or leaves no output frames")
    windows = motion_windows(source, src_start, src_end, cue_values, src_fps)
    fixed_points = [{"sourceAt": at, "outputFrame": out} for at, out in explicit]
    placed_windows = []
    for window in windows:
        start, end = window["start"], window["end"]
        inside = [cue for cue in cue_values if start - 1e-8 <= cue["sourceAt"] <= end + 1e-8]
        known = [(cue["sourceAt"], cue["outputFrame"]) for cue in inside if cue["explicit"]]
        if abs(start - src_start) < 1e-8:
            known.append((src_start, output_start))
        if abs(end - src_end) < 1e-8:
            known.append((src_end, output_end))
        if known:
            anchor_at, anchor_output = known[0]
        else:
            preferred = next((cue for cue in inside if cue["id"] in window["anchorCues"]), None)
            anchor_at = preferred["sourceAt"] if preferred else start
            anchor_output = int(math.floor(interpolate(anchor_at, explicit) + 0.5))
        shift = anchor_output - frame_of(anchor_at, fps, "motion anchor")
        def pinned(at: float) -> int:
            predicted = frame_of(at, fps, "source action time") + shift
            for fixed_at, fixed_frame in known:
                if abs(at - fixed_at) < 1e-8:
                    require(abs(predicted - fixed_frame) <= 1,
                            f"{scene_id} motion window {','.join(window['ids'])} cannot keep original action speed: "
                            f"bound spoken cues are {abs(predicted - fixed_frame)} frames apart from the original choreography. "
                            "Move the cue, lengthen the scene, or choose another macro scene")
                    return fixed_frame
            return predicted
        window_start, window_end = pinned(start), pinned(end)
        require(output_start <= window_start < window_end <= output_end,
                f"{scene_id} motion window {','.join(window['ids'])} does not fit in target scene; "
                "lengthen the scene or choose a shorter macro scene")
        original_frames = frame_of(end - start, fps, "motion length")
        require(abs((window_end - window_start) - original_frames) <= 1,
                f"{scene_id} motion window {','.join(window['ids'])} would change original action duration; "
                "lengthen the scene or move its spoken anchor")
        fixed_points.extend(({"sourceAt": start, "outputFrame": window_start},
                             {"sourceAt": end, "outputFrame": window_end}))
        for cue in inside:
            out = pinned(cue["sourceAt"])
            if cue["explicit"]:
                require(abs(out - cue["outputFrame"]) <= 1,
                        f"{scene_id}.{cue['id']} conflicts with motion window {','.join(window['ids'])}")
            else:
                cue["outputFrame"] = out
            fixed_points.append({"sourceAt": cue["sourceAt"], "outputFrame": cue["outputFrame"]})
        placed_windows.append({"ids": window["ids"], "sourceStart": start, "sourceEnd": end,
                               "outputStartFrame": window_start, "outputEndFrame": window_end,
                               "speed": "source-1x", "anchorCues": window["anchorCues"]})
    fixed_points = unique_knots(fixed_points, scene_id)
    fixed_pairs = [(point["sourceAt"], point["outputFrame"]) for point in fixed_points]
    for cue in cue_values:
        if cue["outputFrame"] is None:
            cue["outputFrame"] = int(math.floor(interpolate(cue["sourceAt"], fixed_pairs) + 0.5))
    cue_values.sort(key=lambda c: c["sourceAt"])
    for a, b in zip(cue_values, cue_values[1:]):
        require(a["sourceAt"] < b["sourceAt"] and a["outputFrame"] < b["outputFrame"],
                f"{scene_id} cannot fit all authored beats in target duration; extend this scene or omit a source beat")
    anchors = [{"sourceAt": src_start, "outputFrame": output_start}]
    anchors.extend({"sourceAt": c["sourceAt"], "outputFrame": c["outputFrame"]} for c in cue_values)
    anchors.append({"sourceAt": src_end, "outputFrame": output_end})
    anchors = unique_knots(anchors, scene_id)
    protected = list(anchors) + fixed_points
    for cue in cue_values:
        if any(window["sourceStart"] - 1e-8 <= cue["sourceAt"] <= window["sourceEnd"] + 1e-8
               for window in placed_windows):
            continue  # full original action span supersedes the tiny legacy cue lock
        for direction, field in ((-1, "lockBeforeFrames"), (1, "lockAfterFrames")):
            lock = integer(cue[field], f"{scene_id}.{cue['id']}.{field}")
            if lock:
                src_at = cue["sourceAt"] + direction * lock / src_fps
                out_at = cue["outputFrame"] + direction * round(lock * fps / src_fps)
                require(src_start <= src_at <= src_end and output_start <= out_at <= output_end,
                        f"Protected motion window around {scene_id}.{cue['id']} exceeds scene boundary")
                protected.append({"sourceAt": src_at, "outputFrame": out_at})
    for direction, name in ((1, "entryLockFrames"), (-1, "exitLockFrames")):
        lock = integer(source.get(name, 0), f"{scene_id}.{name}")
        if lock:
            src_at = (src_start if direction == 1 else src_end) + direction * lock / src_fps
            out_at = (output_start if direction == 1 else output_end) + direction * round(lock * fps / src_fps)
            protected.append({"sourceAt": src_at, "outputFrame": out_at})
    knots = unique_knots(protected, scene_id)
    intervals = []
    for a, b in zip(knots, knots[1:]):
        src_seconds = b["sourceAt"] - a["sourceAt"]
        output_seconds = (b["outputFrame"] - a["outputFrame"]) / fps
        intervals.append({"sourceStart": a["sourceAt"], "sourceEnd": b["sourceAt"],
                          "startFrame": a["outputFrame"], "endFrame": b["outputFrame"],
                          "sourceSecondsPerOutputSecond": round(src_seconds / output_seconds, 8)})
    sfx = []
    for event in source.get("sfx", []):
        require(isinstance(event, dict), f"{scene_id}.sfx entries must be objects")
        at = number(event.get("at"), f"{scene_id}.sfx.at")
        require(src_start <= at <= src_end, f"{scene_id}.sfx event outside source scene")
        frame = int(math.floor(interpolate(at, [(k["sourceAt"], k["outputFrame"]) for k in knots]) + 0.5))
        sfx.append({**event, "sourceAt": at, "outputFrame": frame, "at": round(frame / fps, 6)})
    instance_id = target.get("id", scene_id)
    text_slots = {detail["id"]: detail["value"] for detail in binding_details if detail["type"] in {"text", "dynamicText"}}
    time_map = [{"source": knot["sourceAt"], "output_frame": knot["outputFrame"]} for knot in knots]
    return {"id": instance_id, "sceneId": scene_id, "sourceIndex": source_index,
            "sourceSceneIndex": source_index,
            "sourceStart": src_start, "sourceEnd": src_end,
            "startFrame": output_start, "endFrame": output_end,
            "outputStart": round(output_start / fps, 6), "outputEnd": round(output_end / fps, 6),
            "anchors": anchors, "knots": knots, "intervals": intervals,
            "motionWindows": placed_windows, "fidelity": "motion-windows" if placed_windows else "cue-only",
            "sourceBlockSha256": source.get("sourceBlockSha256"),
            "cues": cue_values, "slots": slots, "texts": text_slots, "bindings": binding_details,
            "sfx": sfx, "voiceClock": "output", "sceneClock": "source-via-knots",
            "source_scene_id": scene_id, "source_scene_index": source_index,
            "source_start": src_start, "source_end": src_end,
            "output_start_frame": output_start, "output_end_frame": output_end,
            "time_map": time_map}


def unique_knots(points: list[dict], scene_id: str) -> list[dict]:
    ordered = sorted(points, key=lambda p: (p["sourceAt"], p["outputFrame"]))
    result = []
    for point in ordered:
        if result and abs(point["sourceAt"] - result[-1]["sourceAt"]) < 1e-8:
            require(point["outputFrame"] == result[-1]["outputFrame"],
                    f"{scene_id} has two target times for one source cue")
            continue
        if result:
            require(point["outputFrame"] > result[-1]["outputFrame"],
                    f"Protected action windows overlap in {scene_id}; extend it or move target cue times")
        result.append({"sourceAt": round(point["sourceAt"], 8), "outputFrame": point["outputFrame"]})
    return result


def target_span(item: dict, previous_end: int, fps: int, index: int) -> tuple[int, int]:
    def chosen(frame_key: str, second_key: str) -> int | None:
        require(not (frame_key in item and second_key in item),
                f"scenes[{index}] has both {frame_key} and {second_key}")
        if frame_key in item:
            frame = item[frame_key]
            require(isinstance(frame, int) and not isinstance(frame, bool), f"{frame_key} must be an integer")
            return frame
        if second_key in item:
            return frame_of(item[second_key], fps, f"scenes[{index}].{second_key}")
        return None
    start = chosen("startFrame", "start")
    if start is None:
        start = previous_end
    end = chosen("endFrame", "end")
    if end is None:
        duration = chosen("durationFrames", "duration")
        require(duration is not None, f"scenes[{index}] needs end/endFrame or duration/durationFrames")
        end = start + duration
    require(start == previous_end, f"scenes[{index}] starts at frame {start}; expected {previous_end} (no black gap/overlap)")
    require(end > start, f"scenes[{index}] must have positive duration")
    return start, end


def source_to_output_frame(scene: dict, source_at: float) -> int:
    points = [(point["source"], point["output_frame"]) for point in scene["time_map"]]
    return int(math.floor(interpolate(source_at, points) + 0.5))


def map_audio_timeline(plan: dict, authored: dict) -> dict:
    """Retime the two source arrangement schemas; synthesize afresh at output length."""
    fps = plan["fps"]
    source_sections = authored.get("SEC", authored.get("synthBed", {}).get("sections", []))
    source_gain = authored.get("ENV", authored.get("gainEnvelopeDb", []))
    source_sfx = authored.get("sfxEvents", [])
    require(isinstance(source_sections, list) and isinstance(source_gain, list) and isinstance(source_sfx, list),
            "Audio sections, envelope and SFX must be arrays")
    gain_pairs = sorted((number(item["at"], "gain key time"), number(item["db"], "gain key db"))
                        for item in source_gain)
    legacy_hits = authored.get("HITS", {})
    music_events = authored.get("musicEvents", {})
    require(isinstance(legacy_hits, dict) and isinstance(music_events, dict),
            "HITS/musicEvents must be objects")
    hit_sources = {
        "subDrops": list(legacy_hits.get("drop", [])) + list(music_events.get("subDrops", [])),
        "crashes": list(legacy_hits.get("crash", [])) + list(music_events.get("crashes", [])),
    }
    risers = list(legacy_hits.get("riser", [])) + list(music_events.get("risers", []))
    one_shots = list(authored.get("specialEvents", []))
    for name, events in music_events.items():
        if name in {"subDrops", "crashes", "risers"}:
            continue
        if isinstance(events, dict):
            one_shots.append({"type": name, **events})
        elif isinstance(events, list):
            one_shots.extend({"type": name, **event} for event in events if isinstance(event, dict))
    source_dark = authored.get("DARK", [])
    require(isinstance(source_dark, list), "DARK must be an array")
    external_dark = authored.get("externalTrack", {}).get("darkBand")
    if external_dark:
        source_dark = [*source_dark, external_dark]
    source_fade = authored.get("fade")
    if source_fade is None:
        mix = authored.get("mix", {})
        if "fadeOutSourceStart" in mix:
            begin = number(mix["fadeOutSourceStart"], "fadeOutSourceStart")
            source_fade = {"start": begin, "end": begin + number(mix.get("fadeOutSeconds", 0), "fadeOutSeconds")}

    reference_sfx, mapped_sections, mapped_gain = [], [], []
    mapped_hits, mapped_special, mapped_dark, mapped_fade = [], [], [], []
    diagnostic_music = {name: [] for name in music_events}

    for scene in plan["scenes"]:
        lo, hi = scene["source_start"], scene["source_end"]
        def inside(t: float) -> bool:
            return lo <= t < hi or (t == hi and scene["output_end_frame"] == plan["end_frame"])
        def mapped(t: float) -> tuple[int, float]:
            frame = source_to_output_frame(scene, t)
            return frame, round(frame / fps, 6)
        def clip_span(raw_start: float, raw_end: float) -> tuple[float, float] | None:
            start, end = max(lo, raw_start), min(hi, raw_end)
            return (start, end) if start < end else None
        def span_fields(start: float, end: float) -> dict:
            first_frame, first_t = mapped(start)
            last_frame, last_t = mapped(end)
            return {"sourceStart": start, "sourceEnd": end, "sceneInstanceId": scene["id"],
                    "startFrame": first_frame, "endFrame": last_frame,
                    "start": first_t, "end": last_t}

        for index, section in enumerate(source_sections):
            require(isinstance(section, dict), "Audio section must be an object")
            raw_start = number(section.get("start"), f"section {index}.start")
            raw_end = number(section.get("end"), f"section {index}.end")
            require(raw_start < raw_end, f"Audio section {index} has invalid duration")
            clipped = clip_span(raw_start, raw_end)
            if clipped:
                mapped_sections.append({**section, **span_fields(*clipped),
                                        "sourceSectionId": section.get("id", f"section-{index}"),
                                        "sourceSectionIndex": index,
                                        "originalStart": raw_start, "originalEnd": raw_end})
        if gain_pairs:
            keys = [(lo, interpolate(lo, gain_pairs))]
            keys.extend((t, db) for t, db in gain_pairs if lo < t < hi)
            keys.append((hi, interpolate(hi, gain_pairs)))
            for source_at, db in keys:
                frame, at = mapped(source_at)
                mapped_gain.append({"sourceAt": source_at, "sceneInstanceId": scene["id"],
                                    "outputFrame": frame, "at": at, "db": db})
        for item in source_sfx:
            require(isinstance(item, dict), "sfxEvents entries must be objects")
            t = number(item.get("t"), "audio SFX time")
            if inside(t):
                frame, at = mapped(t)
                reference_sfx.append({**item, "sourceT": t, "sourceSceneId": scene["sceneId"],
                                      "sceneInstanceId": scene["id"], "outputFrame": frame, "t": at})
        for name, values in hit_sources.items():
            for value in values:
                source_at = number(value, f"{name} source time")
                if inside(source_at):
                    frame, at = mapped(source_at)
                    mapped_hits.append({"kind": name, "sourceAt": source_at,
                                        "sceneInstanceId": scene["id"], "outputFrame": frame, "at": at})
                    diagnostic_music.setdefault(name, []).append(at)
        for index, item in enumerate(risers):
            if isinstance(item, dict):
                raw_start = number(item.get("start"), f"riser {index}.start")
                raw_end = number(item.get("end"), f"riser {index}.end")
                extras = {key: value for key, value in item.items() if key not in {"start", "end"}}
            else:
                require(isinstance(item, list) and len(item) == 2, f"riser {index} needs [start,end]")
                raw_start, raw_end = number(item[0], "riser start"), number(item[1], "riser end")
                extras = {}
            clipped = clip_span(raw_start, raw_end)
            if clipped:
                fields = span_fields(*clipped)
                event = {"type": "riser", "at": fields["start"],
                         "duration": fields["end"] - fields["start"],
                         "sourceAt": clipped[0], "sourceEnd": clipped[1],
                         "sourceEventIndex": index, "continued": clipped[0] > raw_start,
                         "outputFrame": fields["startFrame"], "sceneInstanceId": scene["id"], **extras}
                mapped_special.append(event)
                diagnostic_music.setdefault("risers", []).append(event)
        for index, item in enumerate(one_shots):
            require(isinstance(item, dict), f"special event {index} must be an object")
            source_at = number(item.get("at", item.get("start")), f"special event {index}.at")
            if not inside(source_at):
                continue
            frame, at = mapped(source_at)
            event = {**{key: value for key, value in item.items() if key not in {"at", "start"}},
                     "sourceAt": source_at, "sceneInstanceId": scene["id"],
                     "outputFrame": frame, "at": at}
            if "duration" in event:
                event["duration"] = number(event["duration"], f"special event {index}.duration")
            mapped_special.append(event)
            diagnostic_music.setdefault(event["type"], []).append(event)
        for index, dark in enumerate(source_dark):
            require(isinstance(dark, dict), f"dark band {index} must be an object")
            raw_start = number(dark.get("sourceStart", dark.get("start")), f"dark {index}.start")
            raw_end = number(dark.get("sourceEnd", dark.get("end")), f"dark {index}.end")
            clipped = clip_span(raw_start, raw_end)
            if clipped:
                mapped_dark.append({**dark, **span_fields(*clipped),
                                    "originalStart": raw_start, "originalEnd": raw_end})
        if isinstance(source_fade, dict):
            raw_start = number(source_fade.get("start"), "fade start")
            raw_end = number(source_fade.get("end"), "fade end")
            clipped = clip_span(raw_start, raw_end)
            if clipped:
                mapped_fade.append({**source_fade, **span_fields(*clipped),
                                    "originalStart": raw_start, "originalEnd": raw_end})

    reference_sfx.sort(key=lambda item: item["outputFrame"])
    mapped_sections.sort(key=lambda item: item["startFrame"])
    for previous, current in zip(mapped_sections, mapped_sections[1:]):
        require(previous["endFrame"] <= current["startFrame"],
                f"Audio sections overlap at output frames {previous['endFrame']} and {current['startFrame']}")
    mapped_gain.sort(key=lambda item: (item["outputFrame"], item["sceneInstanceId"]))
    # Adjacent scene ends and starts share one output frame; the incoming
    # scene's level wins so an envelope renderer never divides by zero.
    unique_gain = []
    for key in mapped_gain:
        if unique_gain and key["outputFrame"] == unique_gain[-1]["outputFrame"]:
            unique_gain[-1] = key
        else:
            unique_gain.append(key)
    mapped_hits.sort(key=lambda item: item["outputFrame"])
    mapped_special.sort(key=lambda item: item["outputFrame"])
    plan["audio"] = {
        "sections": mapped_sections, "synthBedSections": mapped_sections,
        "envelope": unique_gain, "gainEnvelopeDb": unique_gain,
        "hits": mapped_hits, "dark": mapped_dark, "fade": mapped_fade,
        "specialEvents": mapped_special, "musicEvents": diagnostic_music,
        "sfxReferenceEvents": reference_sfx, "sfxMixSource": "runtime-scene-S-only",
        "sampleRate": authored.get("sampleRate", authored.get("sourceSampleRate", 44100)),
        "voiceClock": "output", "musicRerenderRequired": True,
        "externalTrackNeedsNewDropAlignment": bool(authored.get("externalTrack", {}).get("optional")),
    }
    return plan


def compile_plan(manifest: dict, spec: dict, *, spec_dir: Path | None = None,
                 project: Path | None = None, audio_timeline: dict | None = None) -> dict:
    spec_dir = Path.cwd() if spec_dir is None else Path(spec_dir)
    pack_id = manifest.get("id")
    require(isinstance(pack_id, str) and pack_id, "Pack manifest needs id")
    require(spec.get("pack", pack_id) == pack_id, f"Target pack {spec.get('pack')} differs from manifest {pack_id}")
    src_fps = integer(manifest.get("fps", 60), "manifest.fps", minimum=1)
    fps = integer(spec.get("fps", src_fps), "spec.fps", minimum=1)
    require(fps <= 240 and src_fps <= 240, "Frame rate above 240 is unsupported")
    source_scenes = manifest.get("scenes")
    target_scenes = spec.get("scenes")
    require(isinstance(source_scenes, list) and source_scenes, "Manifest needs nonempty scenes array")
    require(isinstance(target_scenes, list) and target_scenes, "Target needs nonempty scenes array")
    sources = {}
    for i, scene in enumerate(source_scenes):
        require(isinstance(scene, dict) and isinstance(scene.get("id"), str), f"manifest.scenes[{i}] needs id")
        require(scene["id"] not in sources, f"Duplicate pack scene id {scene['id']}")
        sources[scene["id"]] = (i, scene)
    transcript = transcript_rows(spec.get("transcript"), spec_dir)
    result_scenes = []
    seen_instances = set()
    previous_end = 0
    for i, target in enumerate(target_scenes):
        require(isinstance(target, dict), f"spec.scenes[{i}] must be an object")
        source_id = target.get("sceneId", target.get("packSceneId"))
        require(source_id in sources, f"Unknown source scene {source_id!r}; choose one from pack manifest")
        instance_id = target.get("id", f"{source_id}-{i + 1}")
        require(isinstance(instance_id, str) and instance_id and instance_id not in seen_instances,
                f"spec.scenes[{i}].id must be unique and nonempty")
        seen_instances.add(instance_id)
        target = {**target, "id": instance_id}
        start, end = target_span(target, previous_end, fps, i)
        previous_end = end
        source_index, source = sources[source_id]
        if manifest.get("requireMotionWindows") or spec.get("requireMotionWindows"):
            require(bool(source.get("motionWindows")),
                    f"{source_id} has no authored motionWindows; cannot claim full-motion fidelity for this scene")
        slots, details = slot_bindings(source, target, spec_dir, project, manifest.get("assetDefinitions"))
        result_scenes.append(timed_scene(source, target, source_index, start, end, fps, src_fps,
                                         transcript, slots, details))
    duration = previous_end / fps
    narration = spec.get("narrationDuration")
    if narration is not None:
        narr = number(narration, "narrationDuration", positive=True)
        require(duration >= narr - 1 / fps, f"Last scene ends at {duration:.3f}s before narration ends at {narr:.3f}s")
    plan = {"schemaVersion": 1, "pack": pack_id, "pack_id": pack_id, "sourceFps": src_fps, "fps": fps,
            "width": manifest.get("width", 1920), "height": manifest.get("height", 1080),
            "durationFrames": previous_end, "durationSeconds": round(duration, 6), "end_frame": previous_end,
            "voiceClock": "output", "subtitleClock": "output", "sfxClock": "source-mapped-to-output",
            "sfx": [{"scene_instance_id": scene["id"], **event} for scene in result_scenes for event in scene["sfx"]],
            "scenes": result_scenes}
    plan["fidelity"] = "motion-windows" if all(scene["motionWindows"] for scene in result_scenes) else "cue-only"
    if audio_timeline is not None:
        map_audio_timeline(plan, audio_timeline)
    return plan


def write_plan(path: Path, data: dict, *, replace: bool) -> None:
    require(path.parent.is_dir(), f"Output parent does not exist: {path.parent}")
    require(replace or not path.exists(), f"Refusing existing plan {path}; choose a new path or use --replace")
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as handle:
            temp_name = handle.name
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write("\n")
        os.replace(temp_name, path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Adapt a complete authored animation pack to new timed narration")
    parser.add_argument("manifest", nargs="?", type=Path, help="packs/<id>/manifest.json")
    parser.add_argument("spec", nargs="?", type=Path, help="New narration + scene selection JSON")
    parser.add_argument("--manifest", dest="manifest_option", type=Path, help="Pack manifest (named form)")
    parser.add_argument("--spec", dest="spec_option", type=Path, help="Target spec (named form)")
    parser.add_argument("--project", type=Path, help="Imported talk project, required when pack uses talk slots")
    parser.add_argument("--audio-timeline", type=Path, help="Optional authored audio_timeline.json; default is a sibling of the manifest")
    parser.add_argument("--out", required=True, type=Path, help="New plan JSON path")
    parser.add_argument("--replace", action="store_true", help="Replace an earlier generated plan after validation")
    args = parser.parse_args(argv)
    try:
        manifest_input = args.manifest_option or args.manifest
        spec_input = args.spec_option or args.spec
        require(manifest_input is not None and spec_input is not None,
                "Provide PACK_MANIFEST TARGET_SPEC, or --manifest PACK_MANIFEST --spec TARGET_SPEC")
        manifest_path = manifest_input.expanduser().resolve()
        spec_path = spec_input.expanduser().resolve()
        out = args.out.expanduser().absolute()
        project = args.project.expanduser().resolve() if args.project else None
        audio_path = args.audio_timeline.expanduser().resolve() if args.audio_timeline else manifest_path.parent / "audio_timeline.json"
        audio = read_json(audio_path) if audio_path.is_file() else None
        plan = compile_plan(read_json(manifest_path), read_json(spec_path), spec_dir=spec_path.parent,
                            project=project, audio_timeline=audio)
        plan["manifestPath"] = str(manifest_path)
        plan["specPath"] = str(spec_path)
        write_plan(out, plan, replace=args.replace)
    except AdaptError as exc:
        print(f"adapt: {exc}", file=sys.stderr)
        return 2
    print(f"Adapted {len(plan['scenes'])} scene instances / {plan['durationFrames']} frames ({plan['durationSeconds']:.3f}s): {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Freeze a completed local animation source and track evidence-based intake.

The registry belongs in the owner's private QA/output directory, never inside a
public pack. Registration records provenance; it does not certify a template.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

STATES = ("received", "replayable", "candidate", "new-content-verified", "releasable")
GATES = {
    "replayable": {"continuous-source-av", "environment"},
    "candidate": {"recipe-contract", "rights"},
    "new-content-verified": {"continuous-new-av", "reuse-record"},
    "releasable": {"independent-use", "clean-install", "distribution-rights"},
}
CODE = {".html", ".css", ".js", ".mjs", ".py", ".json", ".md", ".txt", ".srt"}
MEDIA = {".jpg", ".jpeg", ".png", ".webp", ".svg", ".mp4", ".mov", ".wav", ".mp3", ".m4a", ".ttf", ".otf", ".woff", ".woff2"}
SKIP = {"node_modules", ".venv", "__pycache__", ".git", "work", ".cache"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    value = json.loads(path.read_text())
    require(isinstance(value, dict), f"Expected JSON object: {path}")
    return value


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(path):
    before = path.stat()
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    after = path.stat()
    require((before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns),
            f"Source changed while being read: {path}; register after Opus finishes")
    return {"sha256": hasher.hexdigest(), "bytes": after.st_size}


def files(root):
    """Include relative media symlinks while rejecting recursive directory links."""
    def walk(folder, ancestors):
        resolved = folder.resolve()
        require(resolved not in ancestors, f"Recursive source directory link: {folder}")
        for path in sorted(folder.iterdir()):
            if path.name.startswith(".") or path.name in SKIP:
                continue
            require(not path.is_symlink() or path.exists(), f"Broken source link: {path}")
            if path.is_dir():
                yield from walk(path, ancestors | {resolved})
            elif path.suffix.lower() in CODE | MEDIA:
                yield path
    yield from walk(root, set())


def probe(path):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                             "-of", "json", str(path)], check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    videos = [s for s in data["streams"] if s["codec_type"] == "video"]
    require(videos, f"Completed render has no video: {path}")
    video = videos[0]
    return {"durationSeconds": float(data["format"]["duration"]),
            "width": video["width"], "height": video["height"],
            "fps": video["avg_frame_rate"], "frames": video.get("nb_frames"),
            "audio": any(s["codec_type"] == "audio" for s in data["streams"])}


def identity(source_id):
    require(re.fullmatch(r"[a-z][a-z0-9-]{0,63}", source_id), "Source ID must be stable lowercase ASCII")
    return source_id


def register(root, final, registry, source_id, entry, context, freeze_media=False):
    identity(source_id)
    root, final = root.resolve(), final.resolve()
    require(root.is_dir() and final.is_file(), "Provide a source project and an explicit completed render")
    require(entry and not Path(entry).is_absolute() and ".." not in Path(entry).parts,
            "Entry must be a relative project path")
    require((root / entry).is_file(), f"Missing entry: {entry}")
    require(not registry.resolve().is_relative_to(root), "Place the registry outside the mutable source project")
    require(context.get("engine") and context.get("completionEvidence"),
            "Context must identify engine and explicit completionEvidence")
    require(isinstance(context.get("rights"), dict) and context.get("environment"),
            "Record rights (unknown is allowed) and known environment before intake")
    source_files, media_files, cache = {}, {}, {}
    for path in files(root):
        real = path.resolve()
        if real not in cache:
            cache[real] = digest(path)
        record = {**cache[real]}
        if path.is_symlink():
            record["symlinkTarget"] = str(real)
        target = media_files if path.suffix.lower() in MEDIA else source_files
        target[path.relative_to(root).as_posix()] = record
    final_fingerprint = digest(final)
    # Personal paths do not affect identity; every render, code and media byte does.
    canonical = {"entry": entry, "code": {k: v["sha256"] for k, v in source_files.items()},
                 "media": {k: v["sha256"] for k, v in media_files.items()}, "render": final_fingerprint["sha256"]}
    revision = hashlib.sha256(json.dumps(canonical, sort_keys=True).encode()).hexdigest()
    target = registry / source_id / revision
    if target.exists():
        existing = read(target / "source.json")
        verify(target)
        return {"sourceId": source_id, "revision": revision, "path": str(target), "duplicate": True,
                "state": existing["state"]}
    registry.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".source-intake-", dir=registry) as tmp:
        stage = Path(tmp) / "record"
        snapshot = stage / "snapshot"
        snapshot.mkdir(parents=True)
        for name, expected in {**source_files, **(media_files if freeze_media else {})}.items():
            dst = snapshot / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, dst)
            require(digest(dst)["sha256"] == expected["sha256"], f"Source changed while freezing: {name}")
        if freeze_media:
            shutil.copy2(final, stage / ("reference" + final.suffix.lower()))
        record = {"schema": "adu-source/1", "sourceId": source_id, "revision": revision,
                  "state": "received", "receivedAt": datetime.now(timezone.utc).isoformat(),
                  "origin": str(root), "entry": entry, "context": context,
                  "sourceFiles": source_files, "mediaFiles": media_files,
                  "mediaStorage": "snapshot" if freeze_media else "fingerprinted-owner-originals",
                  "render": {"path": str(final), **final_fingerprint, "probe": probe(final)},
                  "evidence": [], "recipes": [],
                  "limits": ["Registration does not prove replay, audiovisual quality or distribution permission."]}
        write(stage / "source.json", record)
        target.parent.mkdir(exist_ok=True)
        stage.rename(target)
    refresh_index(registry)
    return {"sourceId": source_id, "revision": revision, "path": str(target), "state": "received",
            "sourceFiles": len(source_files), "mediaFiles": len(media_files), "mediaStorage": record["mediaStorage"]}


def verify(record_dir):
    record = read(record_dir / "source.json")
    for category in ("sourceFiles", "mediaFiles"):
        base = record_dir / "snapshot" if category == "sourceFiles" or record["mediaStorage"] == "snapshot" else Path(record["origin"])
        for name, expected in record[category].items():
            path = base / name
            require(path.is_file() and digest(path)["sha256"] == expected["sha256"],
                    f"Recorded {category} no longer available unchanged: {name}")
    render = record_dir / ("reference" + Path(record["render"]["path"]).suffix.lower()) if record["mediaStorage"] == "snapshot" else Path(record["render"]["path"])
    require(render.is_file() and digest(render)["sha256"] == record["render"]["sha256"], "Reference render changed or missing")
    return {"sourceId": record["sourceId"], "revision": record["revision"], "verified": True,
            "state": record["state"], "qualityCertified": False}


def advance(record_dir, next_state, evidence_path):
    record = read(record_dir / "source.json")
    require(STATES.index(next_state) == STATES.index(record["state"]) + 1, "Intake cannot skip validation states")
    review = read(evidence_path)
    require(review.get("sourceRevision") == record["revision"], "Evidence belongs to a different source revision")
    require(review.get("passed") is True and review.get("reviewer") and review.get("limits") is not None,
            "Evidence must identify reviewer, passed:true and actual validation limits")
    gates = set(review.get("checks", []))
    require(GATES[next_state] <= gates, f"Missing evidence checks: {sorted(GATES[next_state] - gates)}")
    artifacts = review.get("artifacts")
    require(isinstance(artifacts, list) and artifacts, "Provide concrete review artifacts")
    frozen = []
    for artifact in artifacts:
        path = (evidence_path.parent / artifact).resolve()
        require(path.is_file(), f"Missing review artifact: {path}")
        frozen.append({"path": str(path), **digest(path)})
    verify(record_dir)
    seq = len(record["evidence"]) + 1
    evidence_dir = record_dir / "evidence"
    evidence_dir.mkdir(exist_ok=True)
    dst = evidence_dir / f"{seq:02d}-{next_state}.json"
    require(not dst.exists(), "Evidence record already exists")
    write(dst, {**review, "artifacts": frozen})
    record["evidence"].append({"state": next_state, "file": dst.relative_to(record_dir).as_posix(), **digest(dst)})
    record["state"] = next_state
    write(record_dir / "source.json", record)
    refresh_index(record_dir.parent.parent)
    return {"sourceId": record["sourceId"], "state": next_state, "recordedReview": True}


def refresh_index(registry):
    items = []
    for path in sorted(registry.glob("*/*/source.json")):
        record = read(path)
        items.append({"sourceId": record["sourceId"], "revision": record["revision"], "state": record["state"],
                      "record": path.relative_to(registry).as_posix(), "engine": record["context"]["engine"],
                      "recipes": record["recipes"]})
    write(registry / "index.json", {"schema": "adu-source-index/1", "private": True, "sources": items})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    intake = sub.add_parser("register")
    intake.add_argument("project", type=Path); intake.add_argument("render", type=Path)
    intake.add_argument("--registry", type=Path, required=True); intake.add_argument("--id", required=True)
    intake.add_argument("--entry", default="index.html"); intake.add_argument("--context", type=Path, required=True)
    intake.add_argument("--freeze-media", action="store_true")
    check = sub.add_parser("verify"); check.add_argument("record", type=Path)
    promote = sub.add_parser("advance"); promote.add_argument("record", type=Path)
    promote.add_argument("state", choices=STATES[1:]); promote.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "register":
            result = register(args.project, args.render, args.registry, args.id, args.entry, read(args.context), args.freeze_media)
        elif args.command == "verify": result = verify(args.record)
        else: result = advance(args.record, args.state, args.evidence)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Source intake failed: {exc}") from exc


if __name__ == "__main__": main()

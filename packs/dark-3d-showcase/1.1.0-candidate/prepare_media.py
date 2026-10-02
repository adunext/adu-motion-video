#!/usr/bin/env python3
"""Materialize user-supplied media into this complete nine-scene pack's source slots.

No footage, logos, faces or showcase sprites are bundled with the public pack.
The output directory must be new. Input media are never changed or downloaded.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

PACK = Path(__file__).resolve().parent
MANIFEST = json.loads((PACK / 'manifest.json').read_text(encoding='utf-8'))
SKILL = PACK.parents[2]


def fatal(message: str) -> None:
    raise ValueError(message)


def local_file(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        fatal(f'{label}: provide an absolute local file path')
    path = Path(value).expanduser()
    if not path.is_absolute() or not path.is_file():
        fatal(f'{label}: file not found: {value}')
    return path.resolve()


def local_dir(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        fatal(f'{label}: provide an absolute local directory path')
    path = Path(value).expanduser()
    if not path.is_absolute() or not path.is_dir():
        fatal(f'{label}: directory not found: {value}')
    return path.resolve()


def inspect_video(path: Path) -> float:
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)],
        capture_output=True, text=True, check=True,
    )
    try:
        duration = float(probe.stdout.strip())
    except ValueError as exc:
        raise ValueError(f'Cannot read video duration: {path}') from exc
    if duration <= 0.1:
        fatal(f'Video has no usable duration: {path}')
    return duration


def sequence_media(source: Path, definition: dict, destination: Path) -> dict:
    n = definition['originalFrames']
    source_pattern = definition['sourceAsset']
    target_pattern = source_pattern.replace('%04d', '{:04d}')
    target_folder = destination / source_pattern.split('/f_%04d.jpg')[0]
    target_folder.mkdir(parents=True, exist_ok=False)
    if source.is_dir():
        frames = [source / f'f_{i:04d}.jpg' for i in range(1, n + 1)]
        if any(not frame.is_file() for frame in frames):
            fatal(f'{source.name}: expected exactly f_0001.jpg through f_{n:04d}.jpg')
        for frame in frames:
            shutil.copy2(frame, target_folder / frame.name)
        return {'kind': 'existing-sequence', 'frames': n, 'source': str(source)}
    if not source.is_file():
        fatal(f'Sequence source missing: {source}')
    is_still = source.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}
    if not is_still:
        duration = inspect_video(source)
        # A very short clip looped many times visibly breaks the scene. Ask for
        # enough material; a 1/4-length clip can repeat at most four times.
        minimum = n / definition['originalFps'] / 4
        if duration < minimum:
            fatal(f'{source.name}: {duration:.1f}s is too short for this {n / definition["originalFps"]:.1f}s visual slot; provide >= {minimum:.1f}s or an image')
    width, height = definition.get('referenceSize', [1280, 720])
    fps = definition['originalFps']
    vf = f'fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1'
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n']
    cmd += ['-loop', '1', '-i', str(source)] if is_still else ['-stream_loop', '-1', '-i', str(source)]
    cmd += ['-an', '-vf', vf, '-frames:v', str(n), '-q:v', '3', str(target_folder / 'f_%04d.jpg')]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    actual = len(list(target_folder.glob('f_*.jpg')))
    if actual != n:
        fatal(f'{source.name}: FFmpeg created {actual}/{n} frames')
    return {'kind': 'image' if is_still else 'video', 'frames': n, 'source': str(source)}


def wall_media(value: object, destination: Path, workers: int) -> dict:
    if not isinstance(value, dict):
        fatal('wall: supply {"manifest":"/abs/wall.json","videos":"/abs/videos"} or {"sprites":"/abs/wall-sprites"}')
    raw = destination / 'sc' / 'wall_inputs'
    target = destination / 'sc' / 'wall'
    raw.parent.mkdir(parents=True, exist_ok=True)
    if 'sprites' in value:
        source = local_dir(value['sprites'], 'wall.sprites')
        files = sorted(source.glob('[0-9][0-9][0-9].jpg'))
        if len(files) < 27 or any(not (source / f'{i:03d}.jpg').is_file() for i in range(len(files))):
            fatal('wall.sprites: need at least 27 contiguous 000.jpg, 001.jpg ... 4x4 sprite sheets')
        raw.mkdir(exist_ok=False)
        for f in files:
            shutil.copy2(f, raw / f.name)
        if (source / 'index.json').is_file():
            shutil.copy2(source / 'index.json', raw / 'index.json')
        else:
            (raw / 'index.json').write_text(json.dumps([{'i': i, 'slug': f'work_{i:03d}', 'author': '', 'cat': ''} for i in range(len(files))], indent=2) + '\n')
    else:
        manifest = local_file(value.get('manifest'), 'wall.manifest')
        videos = local_dir(value.get('videos'), 'wall.videos')
        items = json.loads(manifest.read_text(encoding='utf-8'))
        if not isinstance(items, list) or len(items) < 27:
            fatal('wall.manifest: provide at least 27 user-authorized works for the full-wall layout')
        subprocess.run([sys.executable, str(SKILL / 'scripts' / 'prep_wall.py'), '--manifest', str(manifest), '--videos', str(videos), '--output', str(raw), '--workers', str(workers)], check=True)
    index = json.loads((raw / 'index.json').read_text(encoding='utf-8'))
    unique = len(index)
    if unique != len(list(raw.glob('[0-9][0-9][0-9].jpg'))):
        fatal('wall sprites and index.json have different counts')
    original_items = MANIFEST['assetDefinitions']['wall']['originalItems']
    if unique > original_items:
        fatal(f'wall supports at most {original_items} unique items; choose a subset for this composition')
    target.mkdir(exist_ok=False)
    grid = []
    for i in range(original_items):
        row = index[i % unique]
        shutil.copy2(raw / f'{i % unique:03d}.jpg', target / f'{i:03d}.jpg')
        grid.append([row.get('slug', f'work_{i % unique:03d}'), row.get('author', '')])
    shutil.rmtree(raw)
    (target / 'index.json').write_text(json.dumps([{'i': i, 'slug': slug, 'author': author} for i, (slug, author) in enumerate(grid)], ensure_ascii=False, indent=2) + '\n')
    (target / 'wall-meta.json').write_text(json.dumps({'uniqueWorks': unique, 'displayTiles': original_items}, indent=2) + '\n')
    (destination / 'wall.js').write_text('const WALL=' + json.dumps(grid, ensure_ascii=False, separators=(',', ':')) + ';\nwindow.PACK_WALL_UNIQUE_COUNT=' + str(unique) + ';\n', encoding='utf-8')
    return {'kind': 'wall-sprites', 'sprites': original_items, 'uniqueWorks': unique, 'source': str(value)}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--inputs', required=True, type=Path, help='JSON: {"sources":{"grid_opus55p":"/abs/video.mp4",...}}')
    ap.add_argument('--output', required=True, type=Path, help='New directory to receive assets/ and sc/')
    ap.add_argument('--scenes', help='Comma-separated scene IDs, e.g. s01,s02; default all nine')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    if not 1 <= args.workers <= 16:
        fatal('--workers must be between 1 and 16')
    if not args.inputs.is_file():
        fatal(f'Input JSON missing: {args.inputs}')
    raw = json.loads(args.inputs.read_text(encoding='utf-8'))
    sources = raw.get('sources') if isinstance(raw, dict) else None
    if not isinstance(sources, dict):
        fatal('Input JSON must be {"sources": {assetId: absoluteLocalPathOrWallDescriptor}}')
    selected = args.scenes.split(',') if args.scenes else [s['id'] for s in MANIFEST['scenes']]
    catalog = {s['id']: s for s in MANIFEST['scenes']}
    if len(set(selected)) != len(selected) or any(s not in catalog for s in selected):
        fatal('Unknown or repeated scene ID; choose s01 through s09')
    needed = sorted({asset for sid in selected for asset in catalog[sid]['assets']})
    missing = [asset for asset in needed if asset not in sources]
    if missing:
        fatal('Missing required media slots: ' + ', '.join(missing))
    # Validate every path before creating output; then never touch the inputs.
    resolved = {}
    for key in needed:
        definition = MANIFEST['assetDefinitions'][key]
        value = sources[key]
        if key == 'wall':
            if not isinstance(value, dict):
                fatal('wall input must be a descriptor object')
            if 'sprites' in value: local_dir(value['sprites'], 'wall.sprites')
            else:
                local_file(value.get('manifest'), 'wall.manifest')
                local_dir(value.get('videos'), 'wall.videos')
            resolved[key] = value
        elif definition['type'] == 'sequence':
            path = Path(value).expanduser() if isinstance(value, str) else Path()
            if not path.is_absolute() or not path.exists() or not (path.is_file() or path.is_dir()):
                fatal(f'{key}: provide an absolute local video, still or f_0001.jpg sequence directory')
            resolved[key] = path.resolve()
        else:
            resolved[key] = local_file(value, key)
    output = args.output.expanduser()
    if output.exists() or not output.parent.is_dir():
        fatal('--output must be a new directory under an existing parent')
    if args.dry_run:
        print(json.dumps({'scenes': selected, 'requiredAssets': needed, 'output': str(output), 'ready': True}, ensure_ascii=False))
        return
    output.mkdir(exist_ok=False)
    report = {}
    try:
        for key in needed:
            definition = MANIFEST['assetDefinitions'][key]
            source = resolved[key]
            if key == 'wall':
                report[key] = wall_media(source, output, args.workers)
            elif definition['type'] == 'sequence':
                report[key] = sequence_media(source, definition, output)
            else:
                target = output / definition['sourceAsset']
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                report[key] = {'kind': 'image', 'source': str(source)}
        if 'wall' not in needed:
            (output / 'wall.js').write_text('const WALL=[];\n', encoding='utf-8')
        (output / 'media-prep.json').write_text(json.dumps({'pack': MANIFEST['id'], 'scenes': selected, 'assets': report}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except Exception:
        shutil.rmtree(output)
        raise
    print(json.dumps({'output': str(output), 'scenes': selected, 'assets': {k: v.get('frames', v.get('sprites', 1)) for k, v in report.items()}}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        raise SystemExit(f'Media preparation failed: {exc}') from exc

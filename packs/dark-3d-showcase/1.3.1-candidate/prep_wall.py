#!/usr/bin/env python3
"""Build local 4x4 video-wall sprites from an explicit media manifest.

The manifest is a JSON array of objects with a unique `slug`; each input video
is VIDEO_DIR/slug.mp4. Optional author/category values remain in index.json.
No media is downloaded. The output directory must not already exist.
The sprites remain local assets for deterministic rendering.
"""
import argparse
import concurrent.futures as cf
import json
from pathlib import Path
import subprocess
from color_management import image_plan


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', required=True, type=Path)
    ap.add_argument('--videos', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    items = json.loads(a.manifest.read_text())
    if not isinstance(items, list) or not items:
        raise SystemExit('Manifest must be a nonempty JSON array.')
    if not 1 <= a.workers <= 16:
        raise SystemExit('Workers must be between 1 and 16.')
    slugs = [x.get('slug') for x in items]
    if any(not isinstance(s, str) or not s or Path(s).name != s or s in {'.', '..'} or '\\' in s for s in slugs):
        raise SystemExit('Each slug must be one filename component.')
    if len(set(slugs)) != len(slugs):
        raise SystemExit('Manifest slugs must be unique.')
    videos = [(a.videos / (s + '.mp4')).resolve(strict=True) for s in slugs]
    if not a.output.parent.is_dir():
        raise SystemExit('Output parent must exist.')
    a.output.mkdir(exist_ok=False)

    def job(pair):
        i, video = pair
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(video)], check=True, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        if duration <= .1:
            raise ValueError(f'Video is too short: {video.name}')
        start = max(0., min(duration * .25, duration - 4.2))
        span = min(4., duration - start - .05)
        color = image_plan(video)
        vf = f'fps={16 / span:.6f},scale=192:108:force_original_aspect_ratio=increase,crop=192:108,' + color['filter'] + ',tile=4x4'
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-ss', f'{start:.6f}', '-t', f'{span:.6f}', '-i', str(video), '-vf', vf, '-frames:v', '1', '-q:v', '4', str(a.output / f'{i:03d}.jpg')], check=True, capture_output=True)
        if not (a.output / f'{i:03d}.jpg').is_file():
            raise RuntimeError(f'Sprite missing for {video.name}')
        return dict(i=i, slug=slugs[i], author=items[i].get('author', ''), cat=items[i].get('category', ''), color=color)

    with cf.ThreadPoolExecutor(a.workers) as executor:
        result = list(executor.map(job, enumerate(videos)))
    (a.output / 'index.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'sprites': len(result), 'output': str(a.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()

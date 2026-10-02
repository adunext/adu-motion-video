#!/usr/bin/env python3
"""Publish a verified local preview with immutable media names and visible versions."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'adu-preview-delivery/1'


def publish(project: Path, video: Path, output: Path, *, update=False) -> dict:
    from verify_delivery import verify_delivery
    if not output.parent.is_dir(): raise ValueError('Preview parent directory must exist')
    if output.is_symlink(): raise ValueError('Preview directory cannot be a symlink')
    if update:
        old = json.loads((output / 'delivery.json').read_text())
        if old.get('schema') != SCHEMA: raise ValueError('Update requires an existing generated preview')
    elif output.exists(): raise ValueError('Refusing existing preview; use --update only for a generated preview')
    verification = verify_delivery(project, video)
    with video.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != verification['output_sha256']:
        raise ValueError('Video changed after delivery verification; export again')
    filename = f'video-{digest}.mp4'
    record = {'schema': SCHEMA, 'version': digest, 'media': filename,
              'title': video.stem, 'verification': verification}
    # Keep old immutable files on update; only the latest pointer changes.
    with tempfile.TemporaryDirectory(prefix='.adu-preview-', dir=output.parent) as temporary:
        stage = Path(temporary) / 'preview'; stage.mkdir()
        shutil.copyfile(video, stage / filename)
        with (stage / filename).open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                raise ValueError('Video changed during preview publication; export again')
        (stage / 'delivery.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        shutil.copyfile(ROOT / 'scripts/preview_player.js', stage / 'player.js')
        (stage / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Cache-Control" content="no-cache">
<title>视频预览</title><style>
body{margin:0;background:#101419;color:#dde3eb;font:16px/1.7 system-ui,sans-serif}main{max-width:1100px;margin:32px auto;padding:0 24px}h1{font-size:24px;font-weight:600}video{display:block;width:100%;max-height:76vh;background:#050609;border-radius:12px}small{color:#98a3b4}a,button{color:#b7cbec}button{background:#24344c;border:1px solid #567197;border-radius:8px;padding:9px 16px;cursor:pointer}#notice{margin:14px 0;padding:12px 16px;border-left:3px solid #81a7de;background:#1a2635}#notice[hidden]{display:none}footer{display:flex;gap:18px;margin-top:14px;flex-wrap:wrap}
</style><main><h1 id="title">视频预览</h1><p><small id="version">正在核对当前版本…</small></p>
<aside id="notice" hidden><span id="message"></span> <button id="update" hidden>载入当前版本</button></aside>
<video id="video" controls playsinline preload="metadata"></video><footer><a id="download" download>下载当前播放版本</a><button id="check">检查新版本</button><small id="status"></small></footer></main><script src="player.js"></script></html>''')
        if update:
            target = output / filename
            if target.exists():
                with target.open('rb') as stream:
                    if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                        raise ValueError('Existing immutable preview media changed')
            else: (stage / filename).replace(target)
            for name in ('index.html', 'player.js', 'delivery.json'):
                (stage / name).replace(output / name)
        else: stage.rename(output)
    return {'preview': str(output / 'index.html'), 'version': digest, 'media': filename}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path); parser.add_argument('video', type=Path)
    parser.add_argument('output', type=Path); parser.add_argument('--update', action='store_true')
    args = parser.parse_args()
    try: print(json.dumps(publish(args.project.resolve(), args.video.resolve(), args.output.absolute(), update=args.update), ensure_ascii=False))
    except (ValueError, OSError) as exc: parser.exit(1, f'Preview publication failed: {exc}\n')


if __name__ == '__main__': main()

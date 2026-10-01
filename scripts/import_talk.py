#!/usr/bin/env python3
"""Import one already edited talk video without speech recognition or raw-clip matching.

Writes talk/clip_000/f_*.jpg, talkmap.js, voice.wav and import.json. Replaces
only the empty talkmap.js stub created by pipeline new. Other media are protected.
Does not rewrite the creative timeline in config.js/scenes.js.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile


def run(args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f'{args[0]} failed: {result.stderr[-4000:]}')
    return result.stdout


def input_timing(probe, fps):
    streams = probe.get('streams', [])
    video = next((s for s in streams if s.get('codec_type') == 'video'), None)
    audio = next((s for s in streams if s.get('codec_type') == 'audio'), None)
    if video is None or audio is None:
        raise ValueError('input needs video and narration audio')
    container = probe.get('format', {})
    origin = float(container.get('start_time') or 0)
    offset = max(0., float(video.get('start_time') or origin) - origin)
    raw_duration = float(video.get('duration') or
                         (float(container.get('duration') or 0) - offset))
    end = offset + raw_duration
    if not math.isfinite(end) or end <= 0:
        raise ValueError('input video has no finite positive duration')
    count = math.floor(end * fps + .5)
    if count < 1:
        raise ValueError('input video is too short')
    return dict(frames=count, duration=count / fps, videoStartSeconds=offset,
                videoStreamDurationSeconds=raw_duration, videoEndSeconds=end,
                audioStartSeconds=max(0., float(audio.get('start_time') or origin) - origin),
                audioStreamDurationSeconds=float(audio.get('duration') or 0),
                frameResampling='nearest source frame on the output grid; edge padding limited to frame quantization',
                maximumEdgeQuantizationSeconds=1 / fps)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('project', type=Path)
    ap.add_argument('video', type=Path)
    ap.add_argument('--fps', type=int, default=60, help='project frame clock; default 60')
    ap.add_argument('--size', default='720x1280', help='frame box; preserves aspect ratio with padding')
    a = ap.parse_args()
    project, video = a.project.expanduser().resolve(), a.video.expanduser().resolve()
    if not project.is_dir() or not video.is_file(): ap.error('project folder and input video must exist')
    try:
        width, height = map(int, a.size.split('x'))
        if not 1 <= a.fps <= 120 or min(width, height) < 2: raise ValueError()
    except ValueError:
        ap.error('--fps must be 1..120; --size must be positive WIDTHxHEIGHT')
    for tool in ('ffmpeg', 'ffprobe'):
        if not shutil.which(tool): ap.error(f'{tool} is required')
    talk, mapping = project / 'talk', project / 'talkmap.js'
    stub = '// Optional data absent. Generated data may replace this stub.'
    if talk.exists() and (not talk.is_dir() or any(talk.iterdir())): ap.error('talk/ already contains media; import into a fresh project')
    if talk.is_symlink() or mapping.is_symlink(): ap.error('refusing a linked media directory or map')
    if mapping.exists() and mapping.read_text().strip() != stub: ap.error('talkmap.js already contains project data; use a fresh project')
    for name in ('voice.wav', 'import.json'):
        target = project / name
        if target.exists() or target.is_symlink(): ap.error(f'{name} already exists; use a fresh project')
    probe = json.loads(run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', video]))
    timing = input_timing(probe, a.fps)
    count, duration = timing['frames'], timing['duration']
    if timing['videoStartSeconds'] > 1 / a.fps + 1e-5:
        ap.error('video starts more than one output frame after the input clock; provide an aligned clip rather than padding a frozen presenter')
    report = dict(source=str(video), fps=a.fps, **timing,
                  frame_width=width, frame_height=height, subtitles='not generated',
                  next_step='Set CONFIG.demo=false, CONFIG.fps=fps, CONFIG.end=duration; author scenes/race/captions for this clip. No creative timeline was rewritten.')
    with tempfile.TemporaryDirectory(prefix='adu-talk-import-') as temporary:
        work = Path(temporary)
        sequence = work / 'talk' / 'clip_000'
        sequence.mkdir(parents=True)
        vf = (f'fps={a.fps}:start_time=0,scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos,'
              f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,tpad=stop_mode=clone:stop_duration={1/a.fps}')
        run(['ffmpeg', '-v', 'error', '-n', '-i', video, '-map', '0:v:0', '-vf', vf,
             '-frames:v', count, '-q:v', '3', sequence / 'f_%05d.jpg'])
        if len(list(sequence.glob('f_*.jpg'))) != count: raise RuntimeError('Extracted frame count mismatch')
        run(['ffmpeg', '-v', 'error', '-n', '-i', video, '-map', '0:a:0', '-vn',
             '-af', f'aresample=48000:first_pts=0,apad,atrim=duration={duration}', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_s16le', work / 'voice.wav'])
        data = 'const TALKF=["clip_000"];const TALKMAP=' + json.dumps([[0, i+1] for i in range(count)], separators=(',', ':')) + ';\n'
        (work / 'talkmap.js').write_text(data)
        (work / 'import.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        # Preflight again before publishing; old media are never replaced.
        if talk.exists() and any(talk.iterdir()): raise RuntimeError('talk/ changed while importing')
        if mapping.exists() and mapping.read_text().strip() != stub: raise RuntimeError('talkmap.js changed while importing')
        created = []
        talk_was_absent = not talk.exists()
        try:
            talk.mkdir(exist_ok=True)
            created.append(talk / 'clip_000')
            shutil.copytree(sequence, talk / 'clip_000')
            for name in ('voice.wav', 'import.json'):
                with (project / name).open('xb') as dst, (work / name).open('rb') as src:
                    created.append(project / name)
                    shutil.copyfileobj(src, dst)
            mapping.write_text(data)
        except Exception:
            for item in reversed(created):
                if item.is_dir(): shutil.rmtree(item)
                else: item.unlink(missing_ok=True)
            if talk_was_absent and talk.is_dir() and not any(talk.iterdir()): talk.rmdir()
            raise
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, ValueError) as exc:
        raise SystemExit(f'Import failed: {exc}') from exc

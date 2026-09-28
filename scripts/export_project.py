#!/usr/bin/env python3
"""Fresh parallel render, verified concat/mux, and exclusive versioned delivery.

All segments and logs live in one OS temporary directory and are removed on
success or failure. No project parts/, .last_out or old video is reused.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SCRIPT = Path(__file__).resolve().parent


def run(args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{Path(str(args[0])).name} failed ({result.returncode}):\n{result.stderr[-6000:]}")
    return result.stdout


def probe(file):
    return json.loads(run(['ffprobe', '-v', 'error', '-count_frames', '-show_streams',
                           '-show_format', '-of', 'json', file]))


def verify(file, count, fps, width, height, audio=False):
    data = probe(file)
    video = next((s for s in data.get('streams', []) if s['codec_type'] == 'video'), {})
    expected = {'frames': count, 'fps': fps, 'width': width, 'height': height,
                'duration': count / fps, 'audio_required': audio}
    actual = {key: video.get(key) for key in ('nb_read_frames', 'width', 'height',
              'avg_frame_rate', 'r_frame_rate', 'time_base', 'start_pts', 'start_time',
              'duration_ts', 'duration')}
    actual['format'] = {key: data.get('format', {}).get(key) for key in ('start_time', 'duration')}
    actual['audio_present'] = any(s['codec_type'] == 'audio' for s in data.get('streams', []))
    errors = []
    try:
        if int(video.get('nb_read_frames', -1)) != count:
            errors.append('frame_count')
    except (TypeError, ValueError):
        errors.append('frame_count')
    if video.get('width') != width or video.get('height') != height:
        errors.append('dimensions')
    try:
        if abs(float(Fraction(video.get('avg_frame_rate', '0/1'))) - fps) > 1e-6:
            errors.append('frame_rate')
    except (TypeError, ValueError, ZeroDivisionError):
        errors.append('frame_rate')
    try:
        duration = float(video.get('duration', 0))
        if not math.isfinite(duration) or abs(duration - count / fps) > 1 / fps + .001:
            errors.append('duration')
    except (TypeError, ValueError):
        errors.append('duration')
    if audio and not actual['audio_present']:
        errors.append('audio_missing')
    if errors:
        raise RuntimeError(f'Media verification mismatch: {file}\n' + json.dumps(
            {'mismatches': errors, 'expected': expected, 'actual': actual}, ensure_ascii=False))
    return data


def concat_video(work, boundaries, fps):
    """Stream-copy on the frame clock, retaining H.264 B-frame display order."""
    # The concat demuxer uses microseconds, while MP4 container durations may be
    # rounded differently. Round cumulative frame boundaries, not each segment,
    # so rounding errors cannot accumulate across a long sequence of parts.
    microseconds = lambda frame: (2 * frame * 1_000_000 + fps) // (2 * fps)
    lines = ['ffconcat version 1.0\n']
    for i, (first, last) in enumerate(zip(boundaries, boundaries[1:])):
        duration_us = microseconds(last) - microseconds(first)
        lines.append(f"file 'part_{i:03}.mp4'\n")
        lines.append(f'duration {duration_us // 1_000_000}.{duration_us % 1_000_000:06d}\n')
    listing = work / 'concat.txt'
    listing.write_text(''.join(lines))
    video = work / 'video.mp4'
    # Quantize each existing PTS and DTS separately. Setting both to packet N
    # would corrupt B-frame presentation order. No video is decoded/re-encoded.
    clock = (f'setts=pts=round(PTS*TB*{fps})/(TB*{fps}):'
             f'dts=round(DTS*TB*{fps})/(TB*{fps}):duration=1/(TB*{fps})')
    run(['ffmpeg', '-n', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', listing,
         '-map', '0:v:0', '-c:v', 'copy', '-bsf:v', clock,
         '-video_track_timescale', fps, video])
    return video


def sources(project):
    """Audit fingerprint of source files, not a claim that all media were hashed."""
    result = {}
    for root, dirs, names in os.walk(project, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and d not in
                         {'node_modules', '__pycache__', 'parts', 'vparts', 'stills', 'talk', 'sc', 'assets'})
        for name in sorted(names):
            p = Path(root) / name
            if p.suffix.lower() in {'.html', '.js', '.mjs', '.css', '.json', '.py'} and p.is_file():
                result[str(p.relative_to(project))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return result


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--html', default='index.html', help='entry relative to project')
    parser.add_argument('--end', type=float, help='override runtime window.END / CONFIG.end')
    parser.add_argument('--fps', type=positive_int, default=60)
    parser.add_argument('--width', type=positive_int, default=1920)
    parser.add_argument('--height', type=positive_int, default=1080)
    parser.add_argument('--segments', type=positive_int, default=5)
    sound = parser.add_mutually_exclusive_group()
    sound.add_argument('--audio', type=Path, help='full-timeline audio; default: project/mix.wav')
    sound.add_argument('--no-audio', action='store_true', help='explicit silent export')
    parser.add_argument('--playwright-module')
    parser.add_argument('--browser')
    parser.add_argument('--query')
    parser.add_argument('--optional-data', help='explicit missing .js allow-list, comma-separated')
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    output = args.output.expanduser().absolute()
    manifest = Path(str(output) + '.manifest.json')
    entry = (project / args.html).resolve()
    if not project.is_dir() or not entry.is_file():
        parser.error('project and entry HTML must exist')
    if output.suffix.lower() != '.mp4' or args.width % 2 or args.height % 2:
        parser.error('output must end in .mp4; dimensions must be even')
    if output.exists() or output.is_symlink() or manifest.exists() or manifest.is_symlink():
        parser.error('refusing to overwrite video or manifest; choose a new version name')
    if not output.parent.is_dir():
        parser.error('output parent directory must already exist')
    if args.end is not None and (not math.isfinite(args.end) or args.end <= 0):
        parser.error('--end must be finite and positive')
    audio = None if args.no_audio else (args.audio or project / 'mix.wav').expanduser().resolve()
    if audio and not audio.is_file():
        parser.error('audio file is missing; provide --audio or explicitly request --no-audio')
    for tool in ('node', 'ffmpeg', 'ffprobe'):
        if not shutil.which(tool):
            parser.error(f'{tool} was not found; no dependencies have been installed')
    common = ['node', SCRIPT / 'render_project.mjs', entry, '--fps', args.fps,
              '--width', args.width, '--height', args.height]
    for key in ('playwright_module', 'browser', 'query', 'optional_data'):
        value = getattr(args, key)
        if value:
            common.extend(['--' + key.replace('_', '-'), value])
    end = args.end
    if end is None:
        end = json.loads(run([*common, '--probe']))['end']
    count = math.floor(end * args.fps + .5)
    if count < 1:
        parser.error('duration must contain at least one frame')
    duration = count / args.fps
    if audio:
        data = probe(audio)
        track = next((s for s in data['streams'] if s['codec_type'] == 'audio'), None)
        audio_duration = float((track or {}).get('duration') or data.get('format', {}).get('duration') or 0)
        if not track or audio_duration + .05 < duration:
            parser.error('audio does not cover the full video; prepare an intentional padded mix first')
    original_sources = sources(project)
    k = min(args.segments, count)
    boundaries = [math.floor(count * i / k + .5) for i in range(k + 1)]
    with tempfile.TemporaryDirectory(prefix='adu-motion-export-') as temporary:
        work = Path(temporary)

        def segment(i):
            first, last = boundaries[i:i + 2]
            part = work / f'part_{i:03}.mp4'
            try:
                renderer_output = run([*common, '--start', first / args.fps, '--end', last / args.fps, '--output', part])
                metadata = verify(part, last - first, args.fps, args.width, args.height)
            except Exception as exc:
                raise RuntimeError(f'Segment {i} (frames {first}..{last - 1}) failed: {exc}') from exc
            print(f'Segment {i + 1}/{k} verified ({last - first} frames)', file=sys.stderr)
            video = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
            return {'index': i, 'first_frame': first, 'end_frame_exclusive': last, 'frames': last - first,
                    'renderer_output': renderer_output.strip(),
                    'format': {key: metadata.get('format', {}).get(key) for key in ('duration', 'start_time')},
                    'video': {key: video.get(key) for key in ('duration', 'duration_ts', 'start_time',
                              'start_pts', 'time_base', 'avg_frame_rate', 'r_frame_rate', 'nb_read_frames')}}

        segments = []
        with ThreadPoolExecutor(max_workers=k) as pool:
            futures = [pool.submit(segment, i) for i in range(k)]
            for future in as_completed(futures):
                segments.append(future.result())
        if sources(project) != original_sources:
            raise RuntimeError('Project source changed during rendering; export rejected. Render again after edits finish.')
        try:
            video = concat_video(work, boundaries, args.fps)
            verify(video, count, args.fps, args.width, args.height)
        except Exception as exc:
            # The temporary parts are intentionally deleted on failure. Preserve
            # their clock evidence in the error as well as successful manifests.
            raise RuntimeError(f'{exc}\nSegment diagnostics: ' + json.dumps(
                sorted(segments, key=lambda s: s['index']), ensure_ascii=False)) from exc
        completed = video
        if audio:
            completed = work / 'complete.mp4'
            run(['ffmpeg', '-n', '-v', 'error', '-i', video, '-i', audio, '-map', '0:v:0', '-map', '1:a:0',
                 '-c:v', 'copy', '-video_track_timescale', args.fps,
                 '-af', 'apad', '-c:a', 'aac', '-b:a', '256k', '-t', duration,
                 '-movflags', '+faststart', completed])
        metadata = verify(completed, count, args.fps, args.width, args.height, bool(audio))
        run(['ffmpeg', '-v', 'error', '-xerror', '-i', completed, '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'])
        report = {'schema': 'adu-motion-video-export/v1', 'created_utc': datetime.now(timezone.utc).isoformat(),
                  'project': str(project), 'entry': str(entry), 'output': str(output), 'fps': args.fps,
                  'width': args.width, 'height': args.height, 'frames': count, 'duration': duration,
                  'audio': str(audio) if audio else None, 'segments': sorted(segments, key=lambda s: s['index']),
                  'source_sha256': original_sources, 'reused_segments': False,
                  'verification': 'all segment exits + frame counts; concat/mux metadata; complete media decode',
                  'visual_review': 'not performed by this command',
                  'media_fingerprints': 'not included; source hashes are not a media dependency manifest',
                  'streams': metadata['streams']}
        created = []
        try:
            # Exclusive opens also protect against an output appearing after preflight.
            with output.open('xb') as dst, completed.open('rb') as src:
                created.append(output)
                shutil.copyfileobj(src, dst)
            with manifest.open('x', encoding='utf-8') as dst:
                created.append(manifest)
                json.dump(report, dst, ensure_ascii=False, indent=2)
                dst.write('\n')
        except Exception:
            for owned in created:
                owned.unlink(missing_ok=True)
            raise
        print(json.dumps({'output': str(output), 'manifest': str(manifest), 'frames': count,
                          'fps': args.fps, 'duration': duration, 'audio': bool(audio)}, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as exc:
        print(f'Export failed: {exc}', file=sys.stderr)
        sys.exit(1)

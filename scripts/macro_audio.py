#!/usr/bin/env python3
"""Render the selected episode track, plus runtime S() action cues.

Never stretch the original episode's waveform or substitute the quick demo's
two-section score. The caller supplies macro_plan.json and runtime sfx.json.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import subprocess
import numpy as np
import audiolib as A
from adaptation_audio import audio_boundary_report


def render_special(buf, event):
    kind, at = event['type'], event['at']
    duration = event.get('duration')
    if kind == 'riser':
        A.add(buf, A.pan(A.riser(duration, event.get('gain', .18 if event.get('sourceAt') == 43.4 else .14)), 0), at)
    elif kind == 'chip-resolution':
        t = A.T(duration or .5); frequency = A.hz(60) * np.exp(-t * 6)
        wave = np.sign(np.sin(2 * np.pi * np.cumsum(frequency) / A.SR)) * np.exp(-t * 3) * .22
        A.add(buf, A.pan(wave, 0), at)
    elif kind == 'powerdown':
        t = A.T(duration or .6); frequency = 220 * np.exp(-t * 5)
        A.add(buf, A.pan(np.sin(2 * np.pi * np.cumsum(frequency) / A.SR) * np.exp(-t * 4) * .25, 0), at)
    elif kind == 'pad-chord':
        A.add(buf, A.pan(A.pad(event['notes'], duration or 3.2, 2600), 0), at, event.get('gain', .32))
    elif kind == 'piano-note':
        source_index = round((event.get('sourceAt', 42.6) - 42.6) / .45)
        A.add(buf, A.pan(A.epiano(event['note'], duration or 1.2, event.get('gain', .16)),
                         (source_index % 2 - .5) * .6), at)
    elif kind in ('bell-chord', 'outro-arpeggio', 'openingBellArpeggio', 'endingElectricPiano'):
        notes = event['notes']
        if kind == 'bell-chord': instrument, octave, d, gain, spacing, pan_step = A.bell, 12, 3., .08, .02, .22
        elif kind == 'outro-arpeggio': instrument, octave, d, gain, spacing, pan_step = A.epiano, 12, 2.2, .18, .02, .2
        elif kind == 'openingBellArpeggio': instrument, octave, d, gain, spacing, pan_step = A.bell, 0, 1.2, .1, .06, .3
        else: instrument, octave, d, gain, spacing, pan_step = A.epiano, 12, (3. if len(notes) == 6 else 2.4), .2, (.04 if len(notes) == 6 else .03), .2
        for i, note in enumerate(notes):
            A.add(buf, A.pan(instrument(note + octave, duration or d, event.get('gain', gain)),
                             (i - (len(notes) - 1) / 2) * pan_step), at + i * event.get('spacing', spacing))
    else:
        raise ValueError(f'Unimplemented source musical event: {kind}')


def load_track(path, offset, end):
    if not math.isfinite(offset) or offset < 0: raise ValueError('Music offset must be finite and nonnegative')
    result = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(offset), '-i', str(path),
                             '-t', str(end), '-ac', '2', '-ar', str(A.SR), '-f', 'f32le', '-'], capture_output=True, check=True)
    raw = np.frombuffer(result.stdout, np.float32).reshape(-1, 2).astype(np.float64)
    if len(raw) < round(end * A.SR) - A.SR / 60:
        raise ValueError('Supplied music is shorter than the output after offset; provide a full-length track or an explicitly edited loop')
    return np.pad(raw, ((0, max(0, A.N - len(raw))), (0, 0)))[:A.N]


def render(project: Path, track: Path | None = None, offset: float = 0, *, music_mode: str | None = None):
    plan = json.loads((project / 'macro_plan.json').read_text())
    cues = json.loads((project / 'sfx.json').read_text())
    end = plan['end_frame'] / plan['fps']
    if abs(cues['end'] - end) > .5 / plan['fps']: raise ValueError('SFX and video duration disagree; recollect S() cues')
    unknown = {c['type'] for c in cues['sfx']} - A.GEN.keys()
    if unknown: raise ValueError(f'Missing source SFX generators: {sorted(unknown)}')
    score = plan.get('audio')
    if not score or score.get('sfxMixSource') != 'runtime-scene-S-only': raise ValueError('Missing mapped source score')
    profile = score.get('mixProfile', 'legacy-macro')
    if profile not in ('legacy-macro', 'opus-five-v1'): raise ValueError(f'Unknown score mix profile: {profile}')
    from music_policy import selection, POLICY, sha
    requested = ({'mode': 'track', 'path': str(track), 'offset': offset} if track is not None else
                 {'mode': music_mode} if music_mode is not None else
                 json.loads((project / 'macro_music.json').read_text()) if (project / 'macro_music.json').is_file() else None)
    music_config, _ = selection(requested, project)
    track = Path(music_config['path']) if music_config['mode'] == 'track' else None
    offset = music_config.get('offset', 0)
    A.init(end); A.rng = np.random.default_rng(11)
    music = np.zeros((A.N, 2)); sections = []
    if track:
        music = load_track(track, offset, end)
        tt = np.arange(A.N) / A.SR
        for dark in score.get('dark', []):
            w = np.clip((tt - dark['start']) / dark.get('fadeIn', .8), 0, 1) * np.clip((dark['end'] - tt) / dark.get('fadeOut', .35), 0, 1)
            filtered = np.stack([A.lowpass(music[:, c], dark.get('cutoffHz', 900)) for c in range(2)], 1)
            music = music * (1 - w[:, None]) + filtered * w[:, None] * dark.get('gain', 1.15)
        music *= .9 / max(1e-9, np.max(np.abs(music)))

    fx = np.zeros_like(music)
    special = score.get('specialEvents', [])
    # Risers crossing an authored scene boundary continue as one sound.
    joined = []
    for event in special:
        previous = joined[-1] if joined else None
        if event['type'] == 'riser' and event.get('continued') and previous and previous['type'] == 'riser' and previous.get('sourceEventIndex') == event.get('sourceEventIndex') and abs(previous['at'] + previous['duration'] - event['at']) < 1e-5:
            previous['duration'] += event['duration']
        else: joined.append(dict(event))
    rendered_special = 0
    for event in joined:
        if track and event['type'] == 'riser':
            render_special(fx, event)
            rendered_special += 1
    crashes = []
    rendered_hits = 0
    for hit in score.get('hits', []) if track else []:
        if hit['kind'] == 'subDrops': A.add(fx, A.pan(A.sub_drop(1.1, .5), 0), hit['at'])
        elif hit['kind'] == 'crashes':
            if profile == 'opus-five-v1':
                A.add(fx, A.pan(A.crash_cym(), (hit['at'] % 2) - .5), hit['at'])
            else: crashes.append(hit)
        else: raise ValueError(f'Unimplemented source hit: {hit["kind"]}')
        rendered_hits += 1
    music += fx * (.6 if track or profile == 'opus-five-v1' else 1.)
    keys = [(e['at'], e['db']) for e in score.get('envelope', [])]
    if keys: music *= A.env_curve(keys)[:, None]
    for hit in crashes: A.add(music, A.pan(A.crash_cym(), (hit['at'] % 2) - .5), hit['at'])
    for fade in score.get('fade', []):
        a, b = round(fade['start'] * A.SR), round(fade['end'] * A.SR)
        if b <= a: raise ValueError('Zero-length musical fade')
        music[a:b] *= np.clip(1 - np.arange(b-a) / (b-a), 0, 1)[:, None] ** 1.3
        if fade['endFrame'] >= plan['end_frame'] - 1: music[b:] = 0
    # Background selection must not change the action-noise sequence.
    A.rng = np.random.default_rng(11)
    sfx = A.render_sfx(cues['sfx'])
    music = A.reverb(music, 1.1, .12); sfx = A.reverb(sfx, .9, .12)
    samples = round(end * A.SR)
    for name, data in (('bgm', music), ('sfx', sfx)):
        data = data[:samples]
        data /= max(np.max(np.abs(data)) * 1.1, 1e-9)
        A.write_wav(str(project / f'{name}.wav'), data)
    report = {'mode': music_config['mode'], 'musicPolicy': POLICY,
              'trackSha256': music_config.get('sha256'), 'bgmSha256': sha(project / 'bgm.wav'),
              'sfxSha256': sha(project / 'sfx.wav'), 'sfxRandomPolicy': 'adu-sfx-stable-event-and-ir/2', 'duration': end, 'sampleRate': A.SR,
              'mixProfile': profile,
              'renderedSections': len(sections), 'bars': sum(s['bars'] for s in sections),
              'specialEvents': rendered_special, 'plannedSpecialEvents': len(joined), 'hits': rendered_hits,
              'plannedHits': len(score.get('hits', [])),
              'sfx': len(cues['sfx']), 'voiceRetimed': False,
              'review': 'Structure rendered; listening and source/reference comparison still required.'}
    imported=json.loads((project/'import.json').read_text()) if (project/'import.json').is_file() else {}
    report.update(cutsApplied=bool(imported.get('cutsApplied')),playbackRateChanged=False,narrationClock=imported.get('clock','edited-narration'),editMapFingerprint=imported.get('editMapFingerprint'))
    from sound_catalog import measure,VERSION
    (project/'sound_recipe_receipt.json').write_text(json.dumps(dict(schema='adu-sound-recipe-receipt/1',version=VERSION,events=[measure(event) for event in cues['sfx']],limits='Measured generated buffers; final mix listening still required'),ensure_ascii=False,indent=2)+'\n')
    (project / 'macro_audio_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    (project / 'audio_boundary_report.json').write_text(json.dumps(audio_boundary_report(plan, cues), ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    music_args = parser.add_mutually_exclusive_group()
    music_args.add_argument('--track', type=Path)
    parser.add_argument('--offset', type=float, default=0)
    music_args.add_argument('--no-music', action='store_true', help='Explicitly omit background music, retain action SFX')
    args = parser.parse_args()
    render(args.project, args.track, args.offset, music_mode='none' if args.no_music else None)

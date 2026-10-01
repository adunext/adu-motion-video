#!/usr/bin/env python3
"""Render a mapped full-pack score at its original tempo, plus runtime S() cues.

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


def merged_sections(sections):
    result = []
    for raw in sections:
        item = dict(raw)
        prev = result[-1] if result else None
        continuous = prev and abs(prev['end'] - item['start']) < 1e-5 and abs(prev['sourceEnd'] - item['sourceStart']) < 1e-5
        same_score = prev and (prev['sourceSectionId'] == item['sourceSectionId'] or
                               prev['mode'] == item['mode'] == 'chip-8bit')
        if continuous and same_score:
            prev.update(end=item['end'], endFrame=item['endFrame'], sourceEnd=item['sourceEnd'])
        else:
            result.append(item)
    return result


def chip_bar(buf, start, index, end):
    progression = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]
    melody = [76, 79, 84, 79, 77, 76, 74, 72, 72, 76, 79, 76, 74, 72, 71, 74]
    root, chord = progression[index % 4]
    for eighth in range(8):
        at = start + eighth * A.B / 2
        if at >= end - .05: break
        A.add(buf, A.pan(A.chip(root + (12 if eighth % 2 else 0), A.B / 2 * .9, .5), 0), at, .45)
        A.add(buf, A.pan(A.chip(chord[eighth % 3] + 12, A.B / 4, .125), .35), at, .16)
        if index >= 1:
            A.add(buf, A.pan(A.chip(melody[(index * 8 + eighth) % 16], A.B / 2 * .8, .25), -.25), at, .3)
        if eighth % 4 == 0: A.add(buf, A.pan(A.kick(.6), 0), at)
        A.add(buf, A.pan(A.hat(.14), .2), at)


def render_bed(buf, sections):
    A.music = buf
    bar = 0
    rendered = []
    for section in merged_sections(sections):
        mode, start, end = section['mode'], section['start'], section['end']
        if mode == 'piano-break':
            # The source deliberately stops the beat here. Individual piano
            # notes and the falling oscillator are specialEvents, not a bed.
            rendered.append({**section, 'bars': 0}); continue
        if mode not in ('synth', 'rhythm', 'reflective-piano', 'chip-8bit'):
            raise ValueError(f'Unknown score mode: {mode}')
        count = 0
        for tb in A.bars(start, end):
            if mode == 'chip-8bit': chip_bar(buf, tb, count, end)
            elif mode == 'reflective-piano': A.piano_bar(tb, bar, end)
            else:
                options = dict(section.get('options', {}))
                instruments = section.get('instruments', {})
                if isinstance(instruments, dict):
                    for src, dst in (('kick', 'kick_on'), ('clap', 'clapon'), ('hats', 'hats'), ('bass', 'bass'), ('arp', 'arp')):
                        if src in instruments: options[dst] = instruments[src]
                unknown = set(options) - {'kick_on', 'clapon', 'hats', 'bass', 'arp'}
                if unknown: raise ValueError(f'Unimplemented score options: {unknown}')
                A.mbar(tb, bar, section.get('energy', section.get('level', .7)), end, **options)
            if mode != 'chip-8bit': bar += 1
            count += 1
        rendered.append({**section, 'bars': count})
    return rendered


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


def render(project: Path, track: Path | None = None, offset: float = 0):
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
    else:
        sections = render_bed(music, score['sections'])
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
        if not track or event['type'] == 'riser':
            render_special(fx, event)
            rendered_special += 1
    crashes = []
    for hit in score.get('hits', []):
        if hit['kind'] == 'subDrops': A.add(fx, A.pan(A.sub_drop(1.1, .5), 0), hit['at'])
        elif hit['kind'] == 'crashes':
            if profile == 'opus-five-v1':
                A.add(fx, A.pan(A.crash_cym(), (hit['at'] % 2) - .5), hit['at'])
            else: crashes.append(hit)
        else: raise ValueError(f'Unimplemented source hit: {hit["kind"]}')
    music += fx * (.6 if track or profile == 'opus-five-v1' else 1.)
    keys = [(e['at'], e['db']) for e in score.get('envelope', [])]
    if keys: music *= A.env_curve(keys)[:, None]
    for hit in crashes: A.add(music, A.pan(A.crash_cym(), (hit['at'] % 2) - .5), hit['at'])
    for fade in score.get('fade', []):
        a, b = round(fade['start'] * A.SR), round(fade['end'] * A.SR)
        if b <= a: raise ValueError('Zero-length musical fade')
        music[a:b] *= np.clip(1 - np.arange(b-a) / (b-a), 0, 1)[:, None] ** 1.3
        if fade['endFrame'] >= plan['end_frame'] - 1: music[b:] = 0
    sfx = A.render_sfx(cues['sfx'])
    music = A.reverb(music, 1.1, .12); sfx = A.reverb(sfx, .9, .12)
    samples = round(end * A.SR)
    for name, data in (('bgm', music), ('sfx', sfx)):
        data = data[:samples]
        data /= max(np.max(np.abs(data)) * 1.1, 1e-9)
        A.write_wav(str(project / f'{name}.wav'), data)
    report = {'mode': 'track' if track else 'source-synth', 'duration': end, 'sampleRate': A.SR,
              'mixProfile': profile,
              'renderedSections': len(sections), 'bars': sum(s['bars'] for s in sections),
              'specialEvents': rendered_special, 'plannedSpecialEvents': len(joined), 'hits': len(score.get('hits', [])),
              'sfx': len(cues['sfx']), 'voiceRetimed': False,
              'review': 'Structure rendered; listening and source/reference comparison still required.'}
    (project / 'macro_audio_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path); parser.add_argument('--track', type=Path)
    parser.add_argument('--offset', type=float, default=0)
    args = parser.parse_args()
    render(args.project, args.track, args.offset)

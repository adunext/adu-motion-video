"""Read-only listening cues for a mapped plan; never edit or synthesize audio.

Durations describe generator buffer support, not perceived audible tails. Runtime
S() capture is authoritative; manifest events are an explicitly partial fallback.
"""
from __future__ import annotations

from copy import deepcopy
import math


# Audited against GEN and the SFX functions in scripts/audiolib.py. Fixed GEN
# functions ignore an event's d field; only DURATION_PARAMETERS consume it.
DEFAULT_DURATIONS = {
    'whoosh': .45, 'swoosh': .3, 'pop': .12, 'ding': 1., 'hit': 1.,
    'boing': .4, 'err': .3, 'win_pop': .16, 'glitch': .45, 'crash': .8,
    'bsod': .9, 'flap': .5, 'squawk': .42, 'peck': .035, 'land': .2,
    'rise': .6, 'notif': .59, 'bubble_pop': .12, 'dock': .18, 'coin': .37,
    'agent': .14, 'powerdown': 1.1, 'record_scratch': .45, 'sparkle': 1.,
    'chime': 2.2, 'thud': .15, 'msg': .56, 'check': .65, 'stamp': 1.,
    'marker': .25, 'achieve': 1.4, 'key_thock': .07, 'click': .02,
    'tick': .03, 'swipe': .25, 'card': .3, 'crack': .6, 'alert': .22,
    'scroll': .14, 'enter': .18, 'fall': .32, 'rep': .15, 'slash': .22,
    'shine': 1.2, 'crt': .9, 'levelup': .6, 'jump': .5, 'rise_s': .35,
}
DURATION_PARAMETERS = {
    'hum': 3., 'snore': 1.5, 'slide': 1., 'steps': .8, 'typing': 1.,
    'tick_run': 1., 'counter': 1., 'game_bleeps': 1., 'creak': .8,
    'write': 1., 'clock': 1., 'suck': 2., 'fill': 1., 'type': .3,
    'hdd': 1., 'dissolve': .5, 'fill_up': .8, 'bleeps': 1., 'ff': 2.,
}
# chirp uses random note count and duration. Its actual length is not asserted.
VARIABLE_DURATION_TYPES = {'chirp'}
GENERATOR_CONTRACT_SHA256 = 'a51e314dd7a19ed4ba341546ba1d7628c083532ff2315bff73173ee9bad0e049'
SFX_REVERB_SECONDS = .9  # macro_audio.render: A.reverb(sfx, .9, .12)
IMPACT_TYPES = {'hit', 'stamp', 'crack', 'crash', 'thud', 'land', 'enter'}
ENTRY_TYPES = {'whoosh', 'swoosh', 'swipe', 'slide', 'card'}


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value))


def _duration(event):
    kind = event.get('type')
    if kind in DEFAULT_DURATIONS:
        return DEFAULT_DURATIONS[kind], 'generator-fixed'
    if kind in DURATION_PARAMETERS:
        value = event.get('d', DURATION_PARAMETERS[kind])
        if _number(value) and value > 0:
            return value, 'generator-d-parameter' if 'd' in event else 'generator-default'
        return None, 'invalid-generator-d-parameter'
    return None, 'variable-generator-duration' if kind in VARIABLE_DURATION_TYPES else 'unknown-generator'


def _scene_bounds(scene, fps):
    start = scene.get('output_start_frame', scene.get('startFrame'))
    end = scene.get('output_end_frame', scene.get('endFrame'))
    if _number(start) and _number(end) and end > start:
        return start / fps, end / fps
    start, end = scene.get('outputStart'), scene.get('outputEnd')
    return (start, end) if _number(start) and _number(end) and end > start else None


def _native_continuity(left, right, tolerance):
    end = left.get('source_end', left.get('sourceEnd'))
    start = right.get('source_start', right.get('sourceStart'))
    # Source ordering only lowers diagnostic noise; it is not AV acceptance.
    return (_number(end) and _number(start) and abs(end - start) <= tolerance
            and left.get('pack', left.get('packId')) == right.get('pack', right.get('packId')))


def audio_boundary_report(plan, runtime_cues=None):
    """Return JSON-safe diagnostics, preserving every original event.

    runtime_cues accepts dump_sfx's {end, sfx} object or its sfx list. An empty
    runtime list means an actual empty capture; it never falls back to manifest
    events. All times are output seconds. Missing event ownership stays unknown.
    """
    fps, end_frame = plan.get('fps'), plan.get('end_frame', plan.get('endFrame'))
    if not _number(fps) or fps <= 0 or not _number(end_frame) or end_frame <= 0:
        raise ValueError('Audio boundary report needs positive fps and end_frame')
    end, tolerance = end_frame / fps, .5 / fps
    capture_end = None
    if runtime_cues is not None:
        if isinstance(runtime_cues, dict):
            raw = runtime_cues.get('sfx')
            capture_end = runtime_cues.get('end')
        else:
            raw = runtime_cues
        source, complete = 'runtime-scene-S', True
    else:
        raw = plan.get('sfx') or plan.get('audio', {}).get('sfxReferenceEvents', [])
        source, complete = 'manifest-planned-SFX-only', False
    if not isinstance(raw, list):
        raise ValueError('Runtime or planned SFX must be an array')

    findings = []
    if capture_end is not None and (not _number(capture_end) or abs(capture_end - end) > tolerance):
        complete = False
        findings.append({'code': 'capture-duration-mismatch', 'level': 'review',
                         'captureEnd': capture_end, 'planEnd': end})
    if runtime_cues is None:
        findings.append({'code': 'runtime-capture-pending', 'level': 'info',
                         'note': 'Manifest events may omit Scene S() calls. Re-run after runtime capture.'})

    scenes = plan.get('scenes', [])
    boundaries = []
    for left, right in zip(scenes, scenes[1:]):
        lb, rb = _scene_bounds(left, fps), _scene_bounds(right, fps)
        if not lb or not rb or abs(lb[1] - rb[0]) > tolerance:
            continue
        boundaries.append({'at': rb[0], 'from': left.get('id'), 'to': right.get('id'),
                           'nativeSourceContinuation': _native_continuity(left, right, tolerance),
                           'crossingEvents': [], 'possibleLeadInEvents': []})

    events = []
    for index, original in enumerate(raw):
        event = original if isinstance(original, dict) else {}
        at = event.get('t', event.get('at'))
        if not _number(at) and _number(event.get('outputFrame')):
            at = event['outputFrame'] / fps
        duration, duration_source = _duration(event)
        item = {'index': index, 'event': deepcopy(original), 'at': at,
                'durationSeconds': duration, 'durationSource': duration_source,
                'sceneInstanceId': event.get('sceneInstanceId', event.get('scene_instance_id')),
                'ownership': 'explicit' if event.get('sceneInstanceId', event.get('scene_instance_id')) else 'unknown',
                'muted': event.get('g') == 0}
        events.append(item)
        if not _number(at):
            findings.append({'code': 'unknown-event-time', 'level': 'review', 'eventIndex': index})
            continue
        if duration is None:
            findings.append({'code': 'unknown-event-duration', 'level': 'review',
                             'eventIndex': index, 'reason': duration_source})
        if item['muted']:
            continue
        if at < -tolerance or at >= end:
            findings.append({'code': 'event-outside-output', 'level': 'review', 'eventIndex': index,
                             'note': 'Possible preroll or mismatched capture; no event was trimmed.'})
        if duration is None:
            continue
        dry_end, tail_end = at + duration, at + duration + SFX_REVERB_SECONDS
        item.update(dryEnd=round(dry_end, 6), potentialTailEnd=round(tail_end, 6))
        if 0 <= at < end and tail_end > end + tolerance:
            findings.append({'code': 'estimated-tail-beyond-output', 'level': 'review',
                             'eventIndex': index, 'dryBeyondSeconds': round(max(0, dry_end - end), 6),
                             'potentialTailBeyondSeconds': round(tail_end - end, 6),
                             'note': 'Generator support reaches beyond delivery end; listen for an intended or abrupt ending. This does not prove an audible cut.'})
        for boundary in boundaries:
            if not at < boundary['at'] < tail_end - tolerance:
                continue
            lead_in = (0 < boundary['at'] - at <= .5 + tolerance
                       and (item['sceneInstanceId'] == boundary['to']
                            or item['ownership'] == 'unknown' and event.get('type') in ENTRY_TYPES))
            boundary['crossingEvents'].append(index)
            if lead_in:
                boundary['possibleLeadInEvents'].append(index)

    for boundary in boundaries:
        if not boundary['crossingEvents']:
            continue
        expected = boundary['nativeSourceContinuation']
        boundary['classification'] = 'native-continuation' if expected else 'reordered-boundary'
        findings.append({'code': 'cross-boundary-tail', 'level': 'info' if expected else 'review',
                         **deepcopy(boundary),
                         'note': 'Continuous source handoff; overlap alone is not a defect.' if expected else
                         'Check outgoing tails against the next scene; possible entry lead-ins are retained.'})

    # Same-frame layered hits count as one authored impact, not a collision.
    impacts = sorted((item['at'], item['index']) for item in events
                     if _number(item['at']) and 0 <= item['at'] < end and not item['muted']
                     and isinstance(item['event'], dict) and item['event'].get('type') in IMPACT_TYPES)
    beats = []
    for at, index in impacts:
        if beats and at - beats[-1]['at'] <= 1 / fps + 1e-8:
            beats[-1]['events'].append(index)
        else:
            beats.append({'at': at, 'events': [index]})
    # Report one cluster rather than every overlapping pair/window.
    through = -1
    for index in range(len(beats)):
        finish = index
        while finish + 1 < len(beats) and beats[finish + 1]['at'] - beats[index]['at'] <= .5:
            finish += 1
        if finish - index >= 2 and finish > through:
            findings.append({'code': 'dense-impact-beats', 'level': 'review',
                             'start': beats[index]['at'], 'end': beats[finish]['at'],
                             'distinctBeats': finish - index + 1,
                             'eventIndices': [i for beat in beats[index:finish + 1] for i in beat['events']],
                             'note': 'Three or more distinct impacts within 0.5s; listen for intentional rhythm and speech masking.'})
            through = finish

    return {'schema': 'adu-audio-boundaries/1', 'status': 'needs-listening',
            'coverage': {'source': source, 'runtimeCaptureComplete': complete,
                         'eventCount': len(events), 'knownDurationCount': sum(e['durationSeconds'] is not None for e in events),
                         'scope': 'SFX timing/support only; no waveform, voice, music phase, loudness or audible-quality verdict'},
            'durationContract': {'source': 'scripts/audiolib.py GEN and SFX functions',
                                 'astSha256': GENERATOR_CONTRACT_SHA256,
                                 'sfxReverbSeconds': SFX_REVERB_SECONDS,
                                 'meaning': 'Full generator support plus potential reverb, not a measured audible tail'},
            'end': end, 'events': events, 'boundaries': boundaries, 'findings': findings,
            'listeningChecks': ['Play each reordered seam continuously with narration and music.',
                                'Check lead-ins, long tails, clustered impacts and the final audible ending.',
                                'Record acceptance after listening to the final encoded file.'],
            'mutations': []}

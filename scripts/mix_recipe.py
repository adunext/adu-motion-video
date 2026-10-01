#!/usr/bin/env python3
"""Persist effective mastering settings and reuse a project's recorded graph."""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

SCHEMA = 'adu-mix/1'


def volume(value):
    if isinstance(value, bool): raise ValueError('Music volume must be a finite nonnegative number')
    try: number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError('Music volume must be a finite nonnegative number') from exc
    if not math.isfinite(number) or number < 0:
        raise ValueError('Music volume must be a finite nonnegative number')
    return number


def initial_settings(spec):
    if 'mix' not in spec: return None
    data = spec['mix']
    if not isinstance(data, dict) or set(data) != {'musicVolume'}:
        raise ValueError('mix must contain only an explicit musicVolume')
    return {'schema': SCHEMA, 'musicVolume': volume(data['musicVolume'])}


def read(project):
    path = project / 'mix_recipe.json'
    if not path.exists(): return {}
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or data.get('schema') != SCHEMA:
        raise ValueError('Unknown mix recipe schema; retain the original recipe')
    return data


def effective_volume(project, explicit=None):
    return volume(explicit if explicit not in (None, '') else read(project).get('musicVolume', .5))


def effective_voice(project, explicit=None):
    mode = explicit if explicit not in (None, '') else read(project).get('voiceMode', 'file')
    if mode not in {'file', 'none'}: raise ValueError('VOICE must be file or none')
    return mode


def graph(project, fallback, duration, music_volume, voice_mode, explicit=False):
    previous = read(project)
    if (not explicit and isinstance(previous.get('filterComplex'), str)
            and previous.get('durationSeconds') == float(duration)
            and previous.get('musicVolume') == volume(music_volume)
            and previous.get('voiceMode') == voice_mode):
        return previous['filterComplex']
    return fallback


def save(project, duration, music_volume, voice_mode, filter_graph):
    hashes = {}
    for name in ['voice.wav', 'showaudio.wav', 'bgm.wav', 'sfx.wav', 'mix.wav']:
        path = project / name
        if path.is_file(): hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result = {'schema': SCHEMA, 'durationSeconds': float(duration),
              'musicVolume': volume(music_volume), 'voiceMode': voice_mode,
              'filterComplex': filter_graph, 'fileSha256': hashes,
              'ffmpegVersion': subprocess.run(['ffmpeg', '-version'], check=True,
                                             capture_output=True, text=True).stdout.splitlines()[0]}
    (project / 'mix_recipe.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['volume', 'voice', 'graph', 'save'])
    p.add_argument('project', type=Path)
    p.add_argument('args', nargs='*')
    a = p.parse_args()
    try:
        if a.command == 'volume': print(effective_volume(a.project, a.args[0] if a.args else None))
        elif a.command == 'voice': print(effective_voice(a.project, a.args[0] if a.args else None))
        elif a.command == 'graph':
            fallback, duration, vol, mode, explicit = a.args
            print(graph(a.project, fallback, duration, vol, mode, explicit == '1'))
        else:
            duration, vol, mode, value = a.args
            save(a.project, duration, vol, mode, value)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f'Mix recipe failed: {exc}') from exc


if __name__ == '__main__': main()

"""Real PCM, frozen project runners and music-independent action-tail checks."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import wave

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from music_policy import selection, sha, RETIRED
from macro_audio import render as macro_render
from auto_audio import render as auto_render
from build_macro_project import write_project_audio
from audiolib import SR


def tone(path, seconds=6, hz=220):
    # Test signal, never offered as the user's replacement soundtrack.
    t = np.arange(round(seconds * 48000)) / 48000
    raw = np.column_stack((np.sin(t * hz * 2 * np.pi), np.cos(t * hz * 2 * np.pi))) * 4000
    with wave.open(str(path), 'wb') as out:
        out.setparams((2, 2, 48000, 0, 'NONE', 'not compressed'))
        out.writeframes(raw.astype('<i2').tobytes())


def samples(path):
    with wave.open(str(path), 'rb') as src:
        return np.frombuffer(src.readframes(src.getnframes()), '<i2').reshape(-1, 2)


class MusicTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='adu-music-tests-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.track = self.root / 'replacement.wav'
        tone(self.track)

    def project(self, name, music, *, composite=False):
        path = self.root / name
        path.mkdir()
        plan = dict(fps=60, end_frame=240, scenes=[
            dict(id='left', startFrame=0, endFrame=120),
            dict(id='right', startFrame=120, endFrame=240)],
            parts=[dict(path='missing-child-a'), dict(path='missing-child-b')],
            audio=dict(sfxMixSource='runtime-scene-S-only', mixProfile='legacy-macro',
                       specialEvents=[dict(type='riser', at=.25, duration=.7)],
                       hits=[dict(kind='crashes', at=1)], envelope=[], dark=[], fade=[]))
        (path / 'macro_plan.json').write_text(json.dumps(plan))
        (path / 'sfx.json').write_text(json.dumps(dict(end=4, sfx=[dict(type='whoosh', t=1.99, g=.8, p=0)])))
        if music is not None:
            normalized, _ = selection(music, path)
            (path / 'macro_music.json').write_text(json.dumps(normalized))
        return path

    def test_retired_identity_all_durations_and_missing_selection_fail(self):
        for config in [dict(mode='synth'), dict(mode='source-synth'),
                       dict(mode='track', id=RETIRED, path=str(self.track), offset=0)]:
            with self.subTest(config=config), self.assertRaisesRegex(ValueError, 'retired'):
                selection(config, self.root, 4)
        config, missing = selection(None, self.root, pending=True)
        self.assertEqual(config['mode'], 'track')
        self.assertEqual(len(missing), 2)
        with self.assertRaisesRegex(ValueError, 'music.path'):
            selection(None, self.root)

    def test_track_offset_duration_and_pinned_bytes(self):
        config = dict(mode='track', path='replacement.wav', offset=1)
        binding, _ = selection(config, self.root, 4)
        self.assertEqual(binding['sha256'], sha(self.track))
        with self.assertRaisesRegex(ValueError, 'shorter'):
            selection(dict(config, offset=3), self.root, 4)
        for offset in [-1, True, float('nan'), float('inf')]:
            with self.subTest(offset=offset), self.assertRaisesRegex(ValueError, 'offset'):
                selection(dict(config, offset=offset), self.root)
        tone(self.track, hz=440)
        with self.assertRaisesRegex(ValueError, 'bytes changed'):
            selection(binding, self.root)

    def test_macro_track_switch_preserves_sfx_bytes_and_explicit_none(self):
        other = self.root / 'other.wav'
        tone(other, hz=660)
        hashes, bgm = [], []
        for i, music in enumerate([dict(mode='track', path=str(self.track), offset=1),
                                    dict(mode='track', path=str(other), offset=0), dict(mode='none')]):
            project = self.project('macro-' + str(i), music)
            with contextlib.redirect_stdout(io.StringIO()):
                macro_render(project)
            hashes.append(sha(project / 'sfx.wav'))
            bgm.append(samples(project / 'bgm.wav'))
            self.assertEqual(len(bgm[-1]), round(4 * SR))
        self.assertEqual(len(set(hashes)), 1)
        self.assertTrue(np.any(bgm[0]) and np.any(bgm[1]))
        self.assertFalse(np.any(bgm[2]))
        self.assertFalse(np.array_equal(bgm[0], bgm[1]))

    def test_composite_has_one_track_no_child_fallback_and_continuous_tail(self):
        hashes = []
        for i, music in enumerate([dict(mode='track', path=str(self.track), offset=1), dict(mode='none')]):
            project = self.project('mixed-' + str(i), music, composite=True)
            with contextlib.redirect_stdout(io.StringIO()):
                auto_render(project)
            hashes.append(sha(project / 'sfx.wav'))
            audio = samples(project / 'sfx.wav')
            self.assertTrue(np.any(audio[round(2.05 * SR):round(2.2 * SR)]))
            self.assertEqual(len(audio), round(4 * SR))
            report = json.loads((project / 'audio_boundary_report.json').read_text())
            self.assertEqual(report['boundaries'][0]['crossingEvents'], [0])
        self.assertEqual(hashes[0], hashes[1])

    def test_frozen_runner_uses_relative_track_and_rechecks_config_hash(self):
        project = self.project('frozen', dict(mode='none'))
        (project / 'assets').mkdir()
        track = project / 'assets/music.wav'
        tone(track)
        write_project_audio(project, dict(mode='track', path='assets/music.wav', offset=0))
        config = json.loads((project / 'macro_music.json').read_text())
        self.assertEqual(config['path'], 'assets/music.wav')
        result = subprocess.run([sys.executable, str(project / 'audio.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        previous = sha(project / 'sfx.wav')
        tone(track, hz=440)
        result = subprocess.run([sys.executable, str(project / 'audio.py')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('bytes changed', result.stderr)
        self.assertEqual(sha(project / 'sfx.wav'), previous)
        (project / 'macro_music.json').write_text(json.dumps(dict(mode='synth')))
        result = subprocess.run([sys.executable, str(project / 'audio.py')], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('retired', result.stderr)
        self.assertEqual(sha(project / 'sfx.wav'), previous)

    def test_direct_and_frozen_runtime_reject_old_mode_before_audio_write(self):
        for mode in [None, 'synth']:
            project = self.project('reject-' + str(mode), None)
            if mode:
                (project / 'macro_music.json').write_text(json.dumps(dict(mode=mode)))
            with self.assertRaisesRegex(ValueError, 'retired|music.path'):
                macro_render(project)
            self.assertFalse((project / 'bgm.wav').exists())

    def test_basic_template_requires_track_and_keeps_action_sfx(self):
        project = self.project('basic', dict(mode='none'))
        source = (ROOT / 'template/audio.py').read_text()
        file = project / 'audio.py'
        file.write_text(source)
        env = dict(os.environ, ADU_MOTION_VIDEO_ROOT=str(ROOT))
        result = subprocess.run([sys.executable, str(file)], env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('music.path', result.stderr)
        file.write_text(source.replace("MUSIC = dict(mode='track', path='', offset=None)", "MUSIC = dict(mode='none')"))
        subprocess.run([sys.executable, str(file)], env=env, check=True, capture_output=True)
        self.assertTrue(np.any(samples(project / 'sfx.wav')))
        self.assertFalse(np.any(samples(project / 'bgm.wav')))
        previous = sha(project / 'sfx.wav')
        file.write_text(source.replace("MUSIC = dict(mode='track', path='', offset=None)",
                                       'MUSIC = ' + repr(dict(mode='track', path=str(self.track), offset=1))))
        subprocess.run([sys.executable, str(file)], env=env, check=True, capture_output=True)
        self.assertTrue(np.any(samples(project / 'bgm.wav')))
        self.assertEqual(sha(project / 'sfx.wav'), previous)

    def test_manual_build_rejects_music_before_media_import(self):
        from build_macro_project import build
        from adapt_project import AdaptError
        pack = self.root / 'pack'
        pack.mkdir()
        (pack / 'manifest.json').write_text(json.dumps(dict(id='music-gate-test', fps=60)))
        talk = self.root / 'talk.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                        'color=size=32x32:rate=60:duration=4', '-f', 'lavfi', '-i',
                        'sine=frequency=330:sample_rate=48000:duration=4', '-c:v', 'libx264',
                        '-c:a', 'aac', '-preset', 'ultrafast', str(talk)], check=True, capture_output=True)
        spec_path = self.root / 'spec.json'
        for i, music in enumerate([None, dict(mode='synth'),
                                    dict(mode='track', path=str(self.track), offset=3)]):
            spec = dict(brand='Synthetic test', fps=60, scenes=[dict(durationFrames=240)])
            if music is not None:
                spec['music'] = music
            spec_path.write_text(json.dumps(spec))
            output = self.root / ('rejected-build-' + str(i))
            with self.subTest(music=music), self.assertRaisesRegex(AdaptError, 'music.path|retired|shorter'):
                build(pack, spec_path, talk, output, None)
            self.assertFalse(output.exists())
        self.assertFalse(list(self.root.glob('.adu-macro-*')))


if __name__ == '__main__':
    unittest.main()

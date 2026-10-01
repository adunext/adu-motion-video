import json
import hashlib
import math
import os
from pathlib import Path
import sys
import shutil
import struct
import subprocess
import tempfile
import unittest
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from mix_recipe import SCHEMA, effective_voice, effective_volume, graph, initial_settings


class MixRecipeTests(unittest.TestCase):
    def test_chosen_gain_survives_without_author_command_history(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary)
            settings = initial_settings({'mix': {'musicVolume': .42}})
            (p / 'mix_recipe.json').write_text(json.dumps(settings))
            self.assertEqual(effective_volume(p), .42)
            self.assertEqual(effective_volume(p, '0.38'), .38)
            self.assertEqual(effective_voice(p), 'file')

    def test_previous_graph_is_reused_only_for_same_duration_and_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary)
            (p / 'mix_recipe.json').write_text(json.dumps({'schema': SCHEMA, 'musicVolume': .42,
                'durationSeconds': 17.05, 'voiceMode': 'file', 'filterComplex': 'original graph'}))
            self.assertEqual(graph(p, 'new graph', 17.05, .42, 'file'), 'original graph')
            self.assertEqual(graph(p, 'new graph', 18, .42, 'file'), 'new graph')
            self.assertEqual(graph(p, 'new graph', 17.05, .42, 'file', explicit=True), 'new graph')

    def test_invalid_values_and_schema_refuse(self):
        for value in [-.1, float('nan'), float('inf'), True, 'loud']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                initial_settings({'mix': {'musicVolume': value}})
        with self.assertRaises(ValueError): initial_settings({'mix': {'volume': .42}})
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary)
            (p / 'mix_recipe.json').write_text('{"schema":"unknown"}')
            with self.assertRaises(ValueError): effective_volume(p)

    @unittest.skipUnless(shutil.which('ffmpeg'), 'FFmpeg is required for actual mixing')
    def test_pipeline_remixes_identical_pcm_using_saved_gain(self):
        with tempfile.TemporaryDirectory() as temporary:
            p = Path(temporary)
            rate = 48000
            for name, frequency, amplitude in [('voice.wav', 230, .25),
                                                ('bgm.wav', 440, .15), ('sfx.wav', 1200, .025)]:
                with wave.open(str(p / name), 'wb') as audio:
                    audio.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
                    samples = (int(amplitude * 32767 * math.sin(2 * math.pi * frequency * i / rate))
                               for i in range(int(rate * 1.5)))
                    audio.writeframes(b''.join(struct.pack('<hh', x, x) for x in samples))
            env = dict(os.environ)
            env['END'] = '1.5'
            env.pop('VOICE', None)
            pipeline = Path(__file__).resolve().parents[1] / 'scripts/pipeline.sh'
            first = subprocess.run(['bash', str(pipeline), 'mix', str(p), '0.42'],
                                   env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = hashlib.sha256((p / 'mix.wav').read_bytes()).hexdigest()
            second = subprocess.run(['bash', str(pipeline), 'mix', str(p)],
                                    env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(before, hashlib.sha256((p / 'mix.wav').read_bytes()).hexdigest())
            recipe = json.loads((p / 'mix_recipe.json').read_text())
            self.assertEqual(recipe['musicVolume'], .42)
            self.assertIn('volume=0.42', recipe['filterComplex'])


if __name__ == '__main__': unittest.main()

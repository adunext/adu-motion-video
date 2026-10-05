"""Real CLI/file/browser paths plus explicit Windows layout simulations."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pipeline import venv_python
from font_policy import install
from face_tracking import auto_face


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='adu-portable-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def cli(self, *args, env=None, okay=True):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/pipeline.py'), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8', env={**os.environ, **(env or {})})
        if okay:
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        return result

    def test_windows_and_posix_virtualenv_layouts_are_not_mixed(self):
        mac = self.root / '.venv/bin/python'; mac.parent.mkdir(parents=True); mac.write_text('posix')
        self.assertEqual(venv_python(self.root, False), mac)
        self.assertIsNone(venv_python(self.root, True))
        windows = self.root / '.venv-windows/Scripts/python.exe'
        windows.parent.mkdir(parents=True); windows.write_text('windows')
        self.assertEqual(venv_python(self.root, True), windows)
        self.assertEqual(mac.read_text(), 'posix')

    def test_real_cli_unicode_metacharacters_and_no_overwrite(self):
        project = self.root / '中文 空格 100% & $ project'
        self.cli('new', project)
        self.assertTrue((project / 'fonts/NotoSansSC.ttf').is_file())
        self.assertTrue((project / 'fonts/notosanssc-OFL.txt').is_file())
        before = (project / 'config.js').read_bytes()
        result = self.cli('new', project, okay=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((project / 'config.js').read_bytes(), before)
        receipt = json.loads((project / 'font_policy.json').read_text())
        self.assertTrue(receipt['portable'])

    def test_real_python_entry_export_and_complete_decode(self):
        project = self.root / '竖屏与字幕 测试'
        self.cli('new', project)
        output = self.root / '新片 & 1.mp4'
        self.cli('render', project, output, '1', env={'SILENT': '1', 'END': '.5', 'W': '320', 'H': '180'})
        self.cli('check', output)
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_streams',
                                                    '-of', 'json', str(output)], text=True))
        self.assertEqual(int(probe['streams'][0]['nb_read_frames']), 30)
        record = json.loads(Path(str(output) + '.manifest.json').read_text())
        self.assertTrue(any('notosanssc-OFL.txt' in name for name in record['source_sha256']))

    def test_check_preserves_loudness_and_peak_on_real_encoded_audio(self):
        output = self.root / '声音 中文 & 1.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i', 'color=s=32x32:r=5:d=1',
                        '-f', 'lavfi', '-i', 'sine=frequency=440:sample_rate=48000:duration=1',
                        '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(output)], check=True)
        result = self.cli('check', output)
        self.assertIn('LUFS', result.stdout)
        self.assertIn('Peak level dB:', result.stdout)

    def test_missing_face_detector_never_requires_swift_or_windows_crop_input(self):
        # A genuine all-black source yields no detected face on either route.
        stage = self.root / 'project'; talk = stage / 'talk/clip_000'; talk.mkdir(parents=True)
        for i in [1, 16, 31]: Image.new('RGB', (72, 128), '#000').save(talk / f'f_{i:05d}.jpg')
        result = auto_face(stage, 60, 31)
        self.assertEqual(result['mode'], 'wide-fixed-fallback')
        self.assertTrue(result['warnings']); self.assertTrue(result['reviewRequired'])
        self.assertTrue((stage / 'face.js').is_file())

    def test_actual_browser_font_loading_is_offline_and_bilingual(self):
        project = self.root / 'fonts'; project.mkdir()
        css, _ = install({}, {}, project, project)
        (project / 'index.html').write_text('<!doctype html><meta charset="utf-8"><style>' + css +
            '</style><div id="sample" style="font:600 42px \'Adu Sans\'">兼容字体 ABC 123</div>', encoding='utf-8')
        result = subprocess.run(['node', str(ROOT / 'tests/test_portability_browser.mjs'), str(project)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__': unittest.main()

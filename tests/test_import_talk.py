from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from import_talk import input_timing


class ImportTalkTimingTest(unittest.TestCase):
    def test_track_duration_excludes_positive_start_offset(self):
        probe = {'format': {'start_time': '0', 'duration': '17.033334'}, 'streams': [
            {'codec_type': 'video', 'start_time': '0.016667', 'duration': '17.016667'},
            {'codec_type': 'audio', 'start_time': '0', 'duration': '17.033333'}]}
        report = input_timing(probe, 60)
        self.assertEqual(report['frames'], 1022)
        self.assertAlmostEqual(report['videoStartSeconds'], 1 / 60, places=5)
        # Container/audio tails must not extend the presenter's actual timeline.
        probe['format']['duration'] = '25'
        probe['streams'][1]['duration'] = '25'
        self.assertEqual(input_timing(probe, 60)['frames'], 1022)

    def test_real_delayed_video_import_preserves_complete_audio_clock(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); clip = root / 'clip.mp4'; project = root / 'project'
            project.mkdir()
            subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                            'testsrc2=size=160x90:rate=60:duration=0.5', '-f', 'lavfi', '-i',
                            'sine=frequency=440:sample_rate=48000:duration=0.516667',
                            '-vf', 'setpts=PTS+1/60/TB', '-c:v', 'libx264', '-pix_fmt',
                            'yuv420p', '-c:a', 'aac', str(clip)], check=True)
            subprocess.run([sys.executable, str(ROOT / 'scripts/import_talk.py'),
                            str(project), str(clip), '--size', '160x90'], check=True,
                           capture_output=True, text=True)
            report = json.loads((project / 'import.json').read_text())
            self.assertEqual(report['frames'], 31)
            self.assertEqual(len(list((project / 'talk/clip_000').glob('f_*.jpg'))), 31)
            with wave.open(str(project / 'voice.wav')) as voice:
                self.assertEqual(voice.getnframes(), 24800)


if __name__ == '__main__': unittest.main()

"""Exercise planner -> actual media import -> frozen project with a synthetic fixture."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adaptation import load_profile
from build_macro_project import build
from plan_macro_project import plan


class AdaptationBuildTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('node'), 'requires FFmpeg and Node')
    def test_real_03_pack_build_revalidates_and_freezes_adaptation(self):
        # This is a timing/runtime fixture, explicitly not a human narration or
        # new-content AV acceptance. All generated media are discarded.
        packdir = ROOT / 'packs/dark-3d-showcase/1.1.1-candidate'
        manifest = json.loads((packdir / 'manifest.json').read_text())
        profile = load_profile(manifest, ROOT / 'adaptation-profiles')
        source = next(s for s in manifest['scenes'] if s['id'] == 's09')
        contract = next(s for s in profile['scenes'] if s['sceneId'] == 's09')
        with tempfile.TemporaryDirectory(prefix='adu-adaptation-build-') as tmp:
            root = Path(tmp)
            from test_music_policy import tone
            tone(root / 'test-track.wav', seconds=7)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                            'color=c=0x203040:s=720x1280:r=60:d=5.483333333',
                            '-f', 'lavfi', '-i', 'sine=frequency=440:duration=5.483333333',
                            '-c:v', 'libx264', '-preset', 'ultrafast', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', '-frames:v', '329', str(root / 'fixture.mp4')], check=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=blue:s=720x720',
                            '-frames:v', '1', str(root / 'fixture.png')], check=True)
            slots = {s['id']: '验证' if s['type'] in ('text', 'dynamicText') else str(root / 'fixture.png')
                     for s in source['slots']}
            segment = {'id': 'regression', 'text': '本次制作记录与片尾署名，自动化测试专用。',
                       'intent': contract['intents'][0], 'phases': contract['requiredPhases'],
                       'durationFrames': 329, 'counts': {k: v['min'] for k, v in contract['cardinality'].items()},
                       'anchors': {contract['cueRoles'][q['id']]: {'frame': round((q['at'] - source['source']['start']) * 60)}
                                   for q in source['cues'] if q['id'] in contract['cueRoles']},
                       'candidates': {'s09': {'slots': slots}}}
            brief = {'schema': 'adu-adaptation-brief/1', 'brand': '适配回归测试', 'fps': 60,
                     'music': {'mode': 'track', 'path': str(root / 'test-track.wav'), 'offset': .5},
                     'faceTracking': {'mode': 'fixed', 'cx': .5, 'cy': .5, 'h': .3}, 'segments': [segment]}
            (root / 'brief.json').write_text(json.dumps(brief, ensure_ascii=False))
            result = plan(packdir, root / 'brief.json', root / 'planning')
            self.assertTrue(result['ready'], (root / 'planning/report.json').read_text())
            with contextlib.redirect_stdout(io.StringIO()):
                build(packdir, root / 'planning/spec.json', root / 'fixture.mp4', root / 'project', None)
            project = root / 'project'
            plan_data = json.loads((project / 'macro_plan.json').read_text())
            self.assertEqual(plan_data['end_frame'], 329)
            self.assertTrue(plan_data['adaptation']['ready'])
            self.assertTrue((project / 'adaptation_profile.json').is_file())
            self.assertTrue((project / 'audio_runtime/adaptation_audio.py').is_file())
            versions = json.loads((project / 'recipe_versions.json').read_text())
            self.assertEqual(versions['adaptation']['profileDigest'], plan_data['adaptation']['profileDigest'])
            result = subprocess.run(['node', str(ROOT / 'scripts/audit_macro_project.mjs'), str(project),
                                     '--output', str(root / 'audit.json')], text=True, capture_output=True)
            self.assertIn(result.returncode, (0, 1), result.stdout + result.stderr)
            audit = json.loads((root / 'audit.json').read_text())
            # A closing scene used alone is deliberately not an accepted
            # narration opening. Retain the first-frame warning; all actual
            # assets/clock knots/random-seek renders must work.
            self.assertEqual({i['kind'] for i in audit['issues']}, {'first-frame-presenter'})
            self.assertGreater(audit['freshCompared'], 0)
            for script, args in [('dump_sfx.mjs', [str(project / 'index.html'), str(project / 'sfx.json')])]:
                result = subprocess.run(['node', str(ROOT / 'scripts' / script), *args], text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertGreater(len(json.loads((project / 'sfx.json').read_text())['sfx']), 0)
            # Execute the frozen per-project sound runner, not repository code.
            result = subprocess.run([sys.executable, str(project / 'audio.py')], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            sound = json.loads((project / 'audio_boundary_report.json').read_text())
            self.assertEqual(sound['status'], 'needs-listening')
            self.assertTrue((project / 'sfx.wav').stat().st_size > 0)
            music = json.loads((project / 'macro_music.json').read_text())
            self.assertEqual(music['path'], 'assets/music.wav')
            self.assertEqual(json.loads((project / 'macro_audio_report.json').read_text())['mode'], 'track')


if __name__ == '__main__': unittest.main()

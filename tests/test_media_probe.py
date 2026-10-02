from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adapt_project import AdaptError, probe_media, check_aspect, slot_bindings
from adaptation import manifest_digest, plan_adaptation


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-3000:])
    return result.stdout


class MediaProbeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='adu-media-probe-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def clip(self, name, size, *, sar='1/1'):
        path = self.root / name
        run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
             f'color=c=red:s={size}:r=30:d=0.2', '-vf', 'setsar=' + sar,
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', path])
        return path

    def test_same_path_replacement_and_in_place_write_invalidate_cache(self):
        path = self.clip('clip.mp4', '160x90')
        other = self.clip('other.mp4', '90x160')
        old_mtime = path.stat().st_mtime_ns
        self.assertEqual(probe_media(path, 'video')['width'], 160)
        os.replace(other, path)
        os.utime(path, ns=(old_mtime, old_mtime))
        self.assertEqual(probe_media(path, 'video')['width'], 90)
        landscape = self.clip('new.mp4', '320x180')
        path.write_bytes(landscape.read_bytes())
        os.utime(path, ns=(old_mtime, old_mtime))
        self.assertEqual(probe_media(path, 'video')['width'], 320)

    def test_cached_result_is_not_mutable_shared_state(self):
        path = self.clip('clip.mp4', '160x90')
        first = probe_media(path, 'video')
        first['width'] = 12345
        first['aspectAssumptions'].append('caller injection')
        again = probe_media(path, 'video')
        self.assertEqual(again['width'], 160)
        self.assertNotIn('caller injection', again['aspectAssumptions'])

    def test_rotation_and_anamorphic_sar_use_displayed_aspect(self):
        path = self.clip('landscape.mp4', '160x90')
        rotated = self.root / 'portrait.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-display_rotation', '90', '-i', path,
             '-c', 'copy', rotated])
        meta = probe_media(rotated, 'video')
        self.assertEqual((meta['codedWidth'], meta['codedHeight']), (160, 90))
        self.assertEqual((meta['width'], meta['height']), (90, 160))
        check_aspect(meta, {'aspect': '9:16', 'aspectTolerance': 0}, 'rotated')
        with self.assertRaisesRegex(AdaptError, 'differs'):
            check_aspect(meta, {'aspect': '16:9'}, 'rotated')
        oblique = self.root / 'oblique.mp4'
        run(['ffmpeg', '-v', 'error', '-n', '-display_rotation', '45', '-i', path, '-c', 'copy', oblique])
        with self.assertRaisesRegex(AdaptError, 'non-orthogonal display rotation'):
            probe_media(oblique, 'video')
        anamorphic = self.clip('anamorphic.mp4', '144x108', sar='4/3')
        meta = probe_media(anamorphic, 'video')
        self.assertEqual(meta['sampleAspectRatio'], '4:3')
        check_aspect(meta, {'aspect': '16:9', 'aspectTolerance': 0}, 'anamorphic')

    def test_invalid_metadata_fails_and_video_review_path_survives_binding(self):
        bad = self.root / 'invalid.svg'
        bad.write_text('<svg viewBox="0 0 inf 20"/>')
        with self.assertRaisesRegex(AdaptError, 'finite viewBox'):
            probe_media(bad, 'image')
        with self.assertRaisesRegex(AdaptError, 'finite'):
            check_aspect({'width': float('nan'), 'height': 90}, {'aspect': '16:9'}, 'bad')
        video = self.clip('clip.mp4', '160x90')
        source = {'id': 'scene', 'slots': [{'id': 'proof', 'type': 'video', 'playback': {'start': 0, 'end': .2}}]}
        values, _ = slot_bindings(source, {'slots': {'proof': {'path': str(video), 'colorReviewFile': 'review.json'}}}, self.root, None)
        self.assertEqual(values['proof']['colorReviewFile'], str(self.root / 'review.json'))

    def test_planner_review_binding_survives_relocating_its_output_spec(self):
        video = self.clip('clip.mp4', '160x90')
        source = {'id': 'proof', 'source': {'start': 0, 'end': .2}, 'sourceBlockSha256': 'a' * 64,
                  'slots': [{'id': 'clip', 'type': 'video', 'sourceAsset': 'evidence',
                             'playback': {'start': 0, 'end': .2, 'fps': 30}}]}
        manifest = {'id': 'test', 'version': '1', 'fps': 30, 'scenes': [source]}
        profile = {'schema': 'adu-adaptation-profile/1', 'id': 'test', 'version': '1',
            'pack': {'id': 'test', 'version': '1', 'manifestDigest': manifest_digest(manifest)},
            'scenes': [{'sceneId': 'proof', 'sourceBlockSha256': 'a' * 64, 'intents': ['evidence'],
                'requiredPhases': [], 'effects': ['display'], 'energy': 1, 'cardinality': {},
                'entry': {'mode': 'independent'}, 'exit': {}, 'cueRoles': {},
                'splitPolicy': {'mode': 'atomic', 'reason': 'full group'},
                'audio': {'mode': 'source-remap', 'tailPolicy': 'preserve'}}]}
        brief = {'schema': 'adu-adaptation-brief/1', 'brand': 'test', 'segments': [
            {'id': 'one', 'text': 'A new evidence clip', 'intent': 'evidence', 'phases': [], 'durationFrames': 6,
             'candidates': {'proof': {'slots': {'clip': {'path': video.name, 'colorReviewFile': 'review.json'}}}}}]}
        result = plan_adaptation(manifest, profile, brief, self.root)
        self.assertTrue(result['report']['ready'])
        target = result['spec']['scenes'][0]
        self.assertEqual(target['slots']['clip']['colorReviewFile'], str(self.root / 'review.json'))
        relocated = self.root / 'new-plan'; relocated.mkdir()
        values, _ = slot_bindings(source, target, relocated, None)
        self.assertEqual(values['clip']['colorReviewFile'], str(self.root / 'review.json'))


if __name__ == '__main__':
    unittest.main()

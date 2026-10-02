"""Local review/apply preserves the input and resolves files across directories."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adaptation import _digest, manifest_digest, plan_adaptation
from adapt_project import AdaptError
from rematch_macro_project import (apply_files, normalize_request, propose_files,
                                   relocate_spec)


class RematchCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='adu-rematch-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.pack = self.root / 'pack'
        self.pack.mkdir()
        self.requests = self.root / 'requests'
        self.requests.mkdir()
        for path in (self.root / 'old.svg', self.requests / 'new.svg'):
            path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 160 90"/>')
        source = {'id': 'a', 'sourceBlockSha256': 'a' * 64,
                  'source': {'start': 0, 'end': 4}, 'minFrames': 120, 'maxHoldFrames': 120,
                  'cues': [], 'slots': [{'id': 'headline', 'type': 'text', 'maxChars': 12},
                                       {'id': 'visual', 'type': 'image', 'aspect': '16:9'}],
                  'motionWindows': [], 'sfx': []}
        self.manifest = {'id': 'test', 'version': '1.0.0', 'fps': 60, 'scenes': [source]}
        self.profile = {'schema': 'adu-adaptation-profile/1', 'id': 'test', 'version': '1',
                        'pack': {'id': 'test', 'version': '1.0.0', 'manifestDigest': manifest_digest(self.manifest)},
                        'scenes': [{'sceneId': 'a', 'sourceBlockSha256': 'a' * 64,
                                    'intents': ['evidence'], 'requiredPhases': ['proof'],
                                    'effects': ['card'], 'energy': 2, 'cardinality': {},
                                    'entry': {'mode': 'independent'}, 'exit': {}, 'cueRoles': {},
                                    'splitPolicy': {'mode': 'atomic', 'reason': 'complete group'},
                                    'audio': {'mode': 'source-remap', 'tailPolicy': 'preserve'}}]}
        (self.pack / 'manifest.json').write_text(json.dumps(self.manifest))
        self.profiles = self.root / 'profiles'
        self.profiles.mkdir()
        (self.profiles / 'profile.json').write_text(json.dumps(self.profile))
        segments = [{'id': sid, 'text': '新的证据支持结论', 'intent': 'evidence', 'phases': ['proof'],
                     'durationFrames': 240, 'counts': {}, 'anchors': {},
                     'candidates': {'a': {'slots': {'headline': '新证据', 'visual': 'old.svg'}}}}
                    for sid in ('one', 'two')]
        self.spec = plan_adaptation(self.manifest, self.profile,
                                   {'schema': 'adu-adaptation-brief/1', 'brand': '本期', 'fps': 60,
                                    'segments': segments}, self.root)['spec']
        # Deliberately exercise a user's relative references and nonstandard JSON spacing.
        for scene in self.spec['scenes']:
            scene['slots']['visual'] = 'old.svg'
        self.spec['music'] = {'path': 'music.wav'}
        self.spec_path = self.root / 'current.json'
        self.original = json.dumps(self.spec, ensure_ascii=False, indent=3).encode()
        self.spec_path.write_bytes(self.original)
        self.request = {'schema': 'adu-local-rematch/1', 'baseSpecDigest': _digest(self.spec),
                        'segmentId': 'one', 'candidates': {}, 'bindings': {'visual': 'new.svg'}}
        self.request_path = self.requests / 'change.json'
        self.request_path.write_text(json.dumps(self.request))

    def propose(self):
        output = self.root / 'review'
        result = propose_files(self.pack, self.spec_path, self.request_path, output, self.profiles)
        self.assertTrue(result['ready'])
        return output, result['readyCandidates'][0]

    def test_roundtrip_relative_media_origin_and_exact_undo_snapshot(self):
        review, cid = self.propose()
        output = self.root / 'applied'
        apply_files(self.pack, self.spec_path, review / 'review.json', cid, output, self.profiles)
        selected = json.loads((output / 'selected-spec.json').read_text())
        saved = json.loads((output / 'spec.json').read_text())
        self.assertEqual(selected['scenes'][1], self.spec['scenes'][1])
        self.assertEqual(selected['music'], self.spec['music'])
        self.assertEqual(selected['adaptation']['segments'], self.spec['adaptation']['segments'])
        self.assertEqual(saved['scenes'][0]['slots']['visual'], str(self.requests / 'new.svg'))
        self.assertEqual(saved['scenes'][1]['slots']['visual'], str(self.root / 'old.svg'))
        self.assertEqual(saved['music']['path'], str(self.root / 'music.wav'))
        self.assertEqual((output / 'before-spec.json').read_bytes(), self.original)
        self.assertEqual(self.spec_path.read_bytes(), self.original)
        self.assertIn('old.svg', (output / 'changes.diff').read_text())

    def test_stale_or_moved_spec_and_existing_output_are_not_overwritten(self):
        review, cid = self.propose()
        with self.assertRaisesRegex(AdaptError, 'existing directory'):
            propose_files(self.pack, self.spec_path, self.request_path, review, self.profiles)
        self.spec_path.write_bytes(self.original + b'\n')
        with self.assertRaisesRegex(AdaptError, 'bytes changed'):
            apply_files(self.pack, self.spec_path, review / 'review.json', cid,
                        self.root / 'stale', self.profiles)
        self.assertFalse((self.root / 'stale').exists())
        moved = self.requests / 'current.json'
        moved.write_bytes(self.original)
        with self.assertRaisesRegex(AdaptError, 'directory changed'):
            apply_files(self.pack, moved, review / 'review.json', cid,
                        self.root / 'moved', self.profiles)

    def test_candidate_inputs_and_per_media_review_resolve_without_consuming_extra_fields(self):
        manifest = deepcopy(self.manifest)
        manifest['scenes'][0]['slots'][1]['inputPath'] = 'items.0.recording'
        request = deepcopy(self.request)
        request['candidates'] = {'a': {'inputs': {'items': [
            {'recording': {'path': 'video.mov', 'colorReviewFile': 'color.json', 'entityId': 'proof'}},
            {'recording': 'unused.mov'}]}}}
        result = normalize_request(request, manifest, self.spec, self.requests)
        value = result['candidates']['a']['inputs']['items'][0]['recording']
        self.assertEqual(value['path'], str(self.requests / 'video.mov'))
        self.assertEqual(value['colorReviewFile'], str(self.requests / 'color.json'))
        self.assertEqual(value['entityId'], 'proof')
        self.assertEqual(result['candidates']['a']['inputs']['items'][1]['recording'], 'unused.mov')
        self.assertEqual(request['candidates']['a']['inputs']['items'][0]['recording']['path'], 'video.mov')

    def test_pipeline_runs_and_returns_draft_exit_code(self):
        self.request['bindings']['visual'] = None
        self.request_path.write_text(json.dumps(self.request))
        output = self.root / 'draft'
        proc = subprocess.run(['bash', str(ROOT / 'scripts/pipeline.sh'), 'macro-rematch',
                               str(self.pack), str(self.spec_path), str(self.request_path), str(output),
                               '--profiles-root', str(self.profiles)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertFalse(json.loads(proc.stdout)['ready'])
        self.assertTrue((output / 'report.md').is_file())
        self.assertEqual(self.spec_path.read_bytes(), self.original)
        self.assertFalse(list(self.root.glob('.adu-rematch-*')))


if __name__ == '__main__':
    unittest.main()

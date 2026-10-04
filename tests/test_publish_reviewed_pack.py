import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from publish_reviewed_pack import COMMON_CHECKS, freeze


class ReviewedPublicationTest(unittest.TestCase):
    def fixture(self, root):
        source = root / 'candidate'
        source.mkdir()
        blobs = {'README.md': b'candidate', 'lib.js': b'original runtime',
                 'units/used.js': b'complete original used unit',
                 'units/unreviewed.js': b'complete unreviewed unit'}
        for name, data in blobs.items():
            p = source / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        m = {'id': 'example', 'version': '0.1.0-candidate', 'sourceRevision': 'a' * 64,
             'sourceFormat': 'authored-unit/1', 'status': 'candidate',
             'scenes': [{'id': name, 'sourceCodeFile': f'units/{name}.js',
                         'sourceBlockSha256': hashlib.sha256(blobs[f'units/{name}.js']).hexdigest()}
                        for name in ['used', 'unreviewed']],
             'files': {name: hashlib.sha256(data).hexdigest() for name, data in blobs.items()}}
        (source / 'manifest.json').write_text(json.dumps(m))
        evidence = root / 'review.json'
        e = {'packId': 'example', 'sourceVersion': m['version'], 'sourceRevision': m['sourceRevision'],
             'manifestSha256': hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest(),
             'version': '1.0.0', 'passed': True, 'reviewer': 'owner', 'scope': 'group',
             'checks': sorted(COMMON_CHECKS), 'recipes': ['used'],
             'limits': ['one reviewed group only'],
             'artifacts': [{'id': 'owner-av-record', 'sha256': 'b' * 64}]}
        evidence.write_text(json.dumps(e))
        readme = root / 'README.md'
        readme.write_text('example@1.0.0; reviewed group only')
        return source, evidence, readme, e

    def test_only_reviewed_units_are_released_without_changing_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, evidence, readme, _ = self.fixture(root)
            before = {p.relative_to(source): p.read_bytes() for p in source.rglob('*') if p.is_file()}
            freeze(source, evidence, readme, root / 'stable')
            stable = root / 'stable'
            m = json.loads((stable / 'manifest.json').read_text())
            self.assertEqual([s['id'] for s in m['scenes']], ['used'])
            self.assertFalse((stable / 'units/unreviewed.js').exists())
            self.assertEqual((stable / 'lib.js').read_bytes(), before[Path('lib.js')])
            self.assertEqual(before, {p.relative_to(source): p.read_bytes()
                                     for p in source.rglob('*') if p.is_file()})
            for name, expected in m['files'].items():
                self.assertEqual(hashlib.sha256((stable / name).read_bytes()).hexdigest(), expected)
            with self.assertRaisesRegex(ValueError, 'already exists'):
                freeze(source, evidence, readme, stable)

    def test_wrong_review_hash_and_missing_gate_refuse_before_output(self):
        for mutation in ['hash', 'gate', 'route']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source, evidence, readme, e = self.fixture(root)
                if mutation == 'hash': e['manifestSha256'] = 'c' * 64
                if mutation == 'gate': e['checks'].remove('continuous-new-av')
                if mutation == 'route': e['scope'] = 'route-subset'
                evidence.write_text(json.dumps(e))
                with self.assertRaises(ValueError): freeze(source, evidence, readme, root / 'stable')
                self.assertFalse((root / 'stable').exists())

    def test_changed_runtime_or_private_artifact_path_refuses(self):
        for mutation in ['runtime', 'private']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source, evidence, readme, e = self.fixture(root)
                if mutation == 'runtime': (source / 'lib.js').write_text('unreviewed edit')
                else:
                    e['artifacts'][0]['path'] = '/private/owner.mp4'
                    evidence.write_text(json.dumps(e))
                with self.assertRaises(ValueError): freeze(source, evidence, readme, root / 'stable')
                self.assertFalse((root / 'stable').exists())

    def test_present_matching_python_cache_is_not_publishable_source(self):
        for name in ['__pycache__/helper.cpython-314.pyc','helper.pyo']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);source,evidence,readme,e=self.fixture(root)
                cached=source/name;cached.parent.mkdir(parents=True,exist_ok=True);cached.write_bytes(b'present matching generated cache')
                m=json.loads((source/'manifest.json').read_text());m['files'][name]=hashlib.sha256(cached.read_bytes()).hexdigest();(source/'manifest.json').write_text(json.dumps(m))
                e['manifestSha256']=hashlib.sha256((source/'manifest.json').read_bytes()).hexdigest();evidence.write_text(json.dumps(e))
                with self.assertRaisesRegex(ValueError,'Generated Python caches'):
                    freeze(source,evidence,readme,root/'stable')
                self.assertFalse((root/'stable').exists())

    def test_embedded_adaptation_subset_keeps_source_locks_and_dependencies(self):
        from adaptation import load_profile
        for dependent in (False, True):
            with self.subTest(dependent=dependent), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source, evidence, readme, record = self.fixture(root)
                manifest = json.loads((source / 'manifest.json').read_text())
                manifest['adaptationProfile'] = {'schema': 'adu-adaptation-profile/1',
                    'id': 'example-adaptation', 'version': '0.1.0', 'scenes': [
                        {'sceneId': s['id'], 'sourceBlockSha256': s['sourceBlockSha256'],
                         'intents': ['claim'], 'requiredPhases': ['claim'], 'effects': ['card'],
                         'energy': 1, 'cardinality': {}, 'entry': {'mode': 'independent'}, 'exit': {},
                         'cueRoles': {}, 'splitPolicy': {'mode': 'atomic', 'reason': 'complete scene'},
                         'audio': {'mode': 'source-remap', 'tailPolicy': 'preserve'}} for s in manifest['scenes']]}
                if dependent:
                    manifest['adaptationProfile']['scenes'][0]['entry'] = {'mode': 'match-cut', 'requiresPrevious': ['unreviewed']}
                (source / 'manifest.json').write_text(json.dumps(manifest))
                record['manifestSha256'] = hashlib.sha256((source / 'manifest.json').read_bytes()).hexdigest()
                evidence.write_text(json.dumps(record))
                if dependent:
                    with self.assertRaisesRegex(ValueError, 'unknown scenes'):
                        freeze(source, evidence, readme, root / 'stable')
                    self.assertFalse((root / 'stable').exists())
                else:
                    freeze(source, evidence, readme, root / 'stable')
                    result = json.loads((root / 'stable/manifest.json').read_text())
                    profile = load_profile(result, root / 'absent')
                    self.assertEqual([s['sceneId'] for s in profile['scenes']], ['used'])
                    self.assertEqual(profile['pack']['version'], '1.0.0')


if __name__ == '__main__': unittest.main()

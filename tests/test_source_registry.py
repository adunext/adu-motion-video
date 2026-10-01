import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from source_registry import digest, verify, advance, register, link_recipes


class SourceRegistryTest(unittest.TestCase):
    def make_record(self, base):
        record = base / 'registry' / 'new-source' / ('a' * 64)
        snapshot = record / 'snapshot'; snapshot.mkdir(parents=True)
        (snapshot / 'index.html').write_text('<h1>new source</h1>')
        original = base / 'original'; original.mkdir()
        (original / 'media.png').write_bytes(b'owner-media')
        render = base / 'render.mp4'; render.write_bytes(b'reference')
        data = {'sourceId':'new-source','revision':'a'*64,'state':'received','entry':'index.html',
                'sourceFiles':{'index.html':digest(snapshot/'index.html')},
                'mediaFiles':{'media.png':digest(original/'media.png')},'mediaStorage':'fingerprinted-owner-originals',
                'origin':str(original),'render':{'path':str(render),**digest(render)},
                'context':{'engine':'html'},'evidence':[],'recipes':[]}
        (record/'source.json').write_text(json.dumps(data))
        return record, original

    def test_media_changes_cannot_silently_pass_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            record, original = self.make_record(Path(tmp))
            self.assertTrue(verify(record)['verified'])
            (original/'media.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'no longer available'): verify(record)

    def test_source_stages_require_matching_review_and_cannot_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);record,_=self.make_record(base)
            evidence=base/'review.json';artifact=base/'comparison.md';artifact.write_text('reviewed continuous AV; not distribution')
            data={'sourceRevision':'a'*64,'passed':True,'reviewer':'QA','limits':['macOS only'],
                  'checks':['continuous-source-av','environment'],'artifacts':['comparison.md']}
            evidence.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'cannot skip'): advance(record,'releasable',evidence)
            self.assertEqual(advance(record,'replayable',evidence)['state'],'replayable')
            self.assertTrue((record/'evidence/01-replayable.json').is_file())

    def test_duplicate_cannot_claim_requested_media_were_frozen(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); source = base / 'source'; source.mkdir()
            (source / 'index.html').write_text('<h1>complete</h1>')
            render = source / 'complete.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                            'color=size=160x90:rate=30:duration=0.1', '-c:v',
                            'libx264', '-pix_fmt', 'yuv420p', str(render)], check=True)
            context = {'engine': 'DOM', 'completionEvidence': 'explicit final render',
                       'rights': {'media': 'private'}, 'environment': {'platform': 'macOS'}}
            item = register(source, render, base / 'registry', 'example', 'index.html', context)
            duplicate = register(source, render, base / 'registry', 'example', 'index.html', context)
            self.assertEqual(duplicate['mediaStorage'], 'fingerprinted-owner-originals')
            with self.assertRaisesRegex(ValueError, 'cannot upgrade'):
                register(source, render, base / 'registry', 'example', 'index.html', context, True)
            self.assertEqual(json.loads((Path(item['path']) / 'source.json').read_text())['mediaStorage'],
                             'fingerprinted-owner-originals')


    def test_links_reject_wrong_lineage_and_same_version_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); record, _ = self.make_record(base)
            manifest = base / 'manifest.json'
            data = {'id': 'example-pack', 'version': '0.1.0', 'sourceRevision': 'a' * 64,
                    'scenes': [{'id': 'one', 'sourceRevision': 'a' * 64}]}
            manifest.write_text(json.dumps(data))
            self.assertEqual(link_recipes(record, manifest)['addedRecipes'], 1)
            self.assertEqual(link_recipes(record, manifest)['addedRecipes'], 0)
            data['title'] = 'mutated same version'; manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'existing recipe version changed'):
                link_recipes(record, manifest)
            data['version'] = '0.2.0'; manifest.write_text(json.dumps(data))
            self.assertEqual(link_recipes(record, manifest)['addedRecipes'], 1)
            data['sourceRevision'] = 'b' * 64; manifest.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'different source revision'):
                link_recipes(record, manifest)


if __name__ == '__main__': unittest.main()

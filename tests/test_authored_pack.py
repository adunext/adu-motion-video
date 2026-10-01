import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_macro_project import pack_scene_parts
from adapt_project import AdaptError
from extract_authored_pack import audio_recipe
from replay_authored_pack import replay


class AuthoredPackTest(unittest.TestCase):
    def test_candidate_freezes_runtime_as_well_as_selected_scene(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'unit.js').write_text('(()=>{new Scene(0,2);})();')
            (root/'motion.js').write_text('const MOTION={};')
            fingerprints={n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ('unit.js','motion.js')}
            pack={'sourceFormat':'authored-unit/1','files':fingerprints,
                  'scenes':[{'id':'claim','sourceCodeFile':'unit.js','sourceBlockSha256':fingerprints['unit.js']}]}
            _,blocks=pack_scene_parts(root,pack)
            self.assertEqual(len(blocks),1)
            (root/'motion.js').write_text('const MOTION={changed:true};')
            with self.assertRaisesRegex(AdaptError,'Frozen pack file changed'):pack_scene_parts(root,pack)

    def test_reading_score_constants_never_executes_source_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'audio.py'
            path.write_text("raise RuntimeError('must never run')\nSEC=[(0,5,.66,dict(arp=True)),('piano',5,END)]\nENV=[(0,-2),(END,0)]\nHITS=dict(drop=[1],crash=[2],riser=[(3,4)])\nDARK=[]\n")
            score=audio_recipe(path,10)
            self.assertEqual(score['SEC'][1]['mode'],'reflective-piano')
            self.assertEqual(score['ENV'][-1],{'at':10,'db':0})

    def test_replay_rejects_absolute_provenance_before_any_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp);origin=base/'original';origin.mkdir();original=origin/'scenes.js';original.write_text('keep source')
            record=base/'record';record.mkdir();pack=base/'pack';pack.mkdir()
            (record/'source.json').write_text(json.dumps({'revision':'source-v1','origin':str(origin),
                'sourceFiles':{},'mediaFiles':{},'entry':'index.html'}))
            (pack/'manifest.json').write_text(json.dumps({'sourceRevision':'source-v1',
                'scenes':[{'provenance':{'sourceFile':str(original)}}]}))
            with self.assertRaisesRegex(ValueError,'project-relative'):
                replay(record,pack,base/'result')
            self.assertEqual(original.read_text(),'keep source')
            self.assertFalse((base/'result').exists())


if __name__=='__main__': unittest.main()

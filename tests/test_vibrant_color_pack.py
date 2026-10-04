import json
import hashlib
from pathlib import Path
import sys
import unittest
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pack_layout import resolve_layout
from auto_templates import library,requirements
from adaptation import load_profile,validate_profile
from semantic_inputs import expand_inputs,SemanticInputError
from adapt_project import AdaptError,timed_scene,following_tail_issue
from build_macro_project import bind_authored_block

class VibrantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack=ROOT/'packs/vibrant-color-performance/0.1.0-candidate'
        cls.m=json.loads((cls.pack/'manifest.json').read_text())

    def test_frozen_files_contract_and_public_media_boundary(self):
        m=self.m
        for name,digest in m['files'].items():self.assertEqual(hashlib.sha256((self.pack/name).read_bytes()).hexdigest(),digest)
        p=load_profile(m,ROOT/'adaptation-profiles');validate_profile(p,m)
        self.assertEqual(len(p['scenes']),7);self.assertEqual(len(m['externalFonts']),3)
        self.assertFalse(any(p.suffix in ('.mp4','.wav','.woff2','.png','.jpg') for p in self.pack.rglob('*')))
        for file in self.pack.rglob('*'):
            if file.is_file():
                self.assertNotIn('/Volumes/',file.read_text());self.assertNotIn('/Users/',file.read_text())
                text=file.read_text()
                for token in ('阿杜','ADUNEXT','AduNext','不要用数字人','adunext.com'):
                    self.assertNotIn(token,text)

    def test_portrait_only_rejects_accidental_default_landscape(self):
        self.assertEqual(resolve_layout(self.m,{'layout':'portrait'})['height'],1920)
        with self.assertRaisesRegex(ValueError,'no landscape contract'):resolve_layout(self.m,{})
        entry=next(e for e in library() if e['styleId']=='06-A')
        self.assertTrue(any('no landscape contract' in s for s in requirements(entry,{'layout':'landscape'})))
        self.assertFalse(any('layout:' in s for s in requirements(entry,{'layout':'portrait'})))

    def test_truthful_named_fields_bind_and_excess_items_are_rejected(self):
        for sc in self.m['scenes']:
            values=expand_inputs(sc,{'inputs':sc['inputExample']})['slots']
            values={k:v for k,v in values.items() if k!='grainTexture'}
            body,_=bind_authored_block((self.pack/sc['sourceCodeFile']).read_text(),sc,values,sc['id'])
            self.assertNotIn('ADUNEXT — REAL HUMAN',body)
            if any(k in sc['inputExample'] for k in ('steps','items','points')):
                inputs=deepcopy(sc['inputExample']);inputs[next(k for k in ('steps','items','points') if k in inputs)].append('多余')
                with self.assertRaisesRegex(SemanticInputError,'Unconsumed'):expand_inputs(sc,{'inputs':inputs})

    def test_motion_cannot_be_shortened_or_extended_and_tails_cannot_be_cut(self):
        for sc in self.m['scenes']:
            n=round((sc['source']['end']-sc['source']['start'])*60)
            cues={c['id']:{'frame':round((c['at']-sc['source']['start'])*60)} for c in sc['cues']}
            timed_scene(sc,{'cues':cues},0,0,n,60,60,[],{},[])
            if sc.get('maxHoldFrames'):
                timed_scene(sc,{'cues':cues},0,0,n+600,60,60,[],{},[])
            for size in [1,n-60,n+sc.get('maxHoldFrames',0)+1,36000]:
                with self.assertRaises(AdaptError):timed_scene(sc,{'cues':cues},0,0,size,60,60,[],{},[])
            if sc['minFollowingFrames']:
                self.assertIsNotNone(following_tail_issue(sc,n,n,60,60,'last'))
                self.assertIsNone(following_tail_issue(sc,n,n+sc['minFollowingFrames'],60,60,'with-support'))
            else:self.assertIsNone(following_tail_issue(sc,n,n,60,60,'last'))

if __name__=='__main__':unittest.main()

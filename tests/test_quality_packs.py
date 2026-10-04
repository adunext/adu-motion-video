"""Contracts and actual bound source code for new quality candidate units."""
from pathlib import Path
import unittest
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_macro_project import pack_scene_parts,bind_authored_block
from adaptation import load_profile,validate_profile
from semantic_inputs import expand_inputs,unused_inputs

PACKS=[('doubao-console-performance','0.3.0-candidate'),('vivid-sticker-performance','0.2.0-candidate'),('kinetic-performance','1.2.0-candidate'),('editorial-performance','1.2.0-candidate'),('dark-3d-showcase','1.3.0-candidate')]
class QualityPackTests(unittest.TestCase):
    def test_all_candidates_bind_reviewed_text_spans_without_overlap(self):
        for family,version in PACKS:
            folder=ROOT/'packs'/family/version;m=json.loads((folder/'manifest.json').read_text());_,blocks=pack_scene_parts(folder,m)
            validate_profile(load_profile(m,ROOT/'adaptation-profiles'),m)
            for scene,body in zip(m['scenes'],blocks):
                values={s['id']:'新' if s['type'] in ['text','dynamicText'] else 3 for s in scene['slots'] if s['type'] in ['text','dynamicText','number']}
                with self.subTest(family=family,scene=scene['id']):
                    bound,_=bind_authored_block(body,scene,values,'instance');self.assertTrue(bound)

    def test_three_item_choreography_has_three_real_card_events(self):
        p=ROOT/'packs/kinetic-performance/1.2.0-candidate';m=json.loads((p/'manifest.json').read_text());sc=m['scenes'][-1];body=(p/sc['sourceCodeFile']).read_text();profile=load_profile(m,ROOT/'adaptation-profiles')
        c=next(x for x in profile['scenes'] if x['sceneId']==sc['id']);self.assertEqual(c['cardinality']['parts'],dict(min=3,max=3));self.assertNotIn('parts.3.label',[s.get('inputPath') for s in sc['slots']]);self.assertNotIn('91.14',body)
        inputs=sc['inputExample'];self.assertFalse(unused_inputs(sc,inputs));self.assertEqual(len(inputs['parts']),3)
        changed=json.loads(json.dumps(inputs));changed['parts'].append(dict(label='第四项'))
        self.assertIn('parts.3.label',unused_inputs(sc,changed))

    def test_editorial_source_coverage_is_ten_distinct_original_units(self):
        m=json.loads((ROOT/'packs/editorial-performance/1.2.0-candidate/manifest.json').read_text())
        original=[s for s in m['scenes'] if s.get('authorship')!='newly-authored-style-extension']
        self.assertEqual(len(original),10);self.assertEqual(set(s.get('source_scene_index') for s in original if s.get('source_scene_index') is not None),set(range(1,10))-{4,5})
        self.assertEqual(len([s for s in m['scenes'] if s.get('authorship')=='newly-authored-style-extension']),3)
        # Claimed coverage is checked against actual disjoint source intervals.
        spans=sorted((s['source']['start'],s['source']['end']) for s in original)
        self.assertEqual(spans[0][0],0)
        for a,b in zip(spans,spans[1:]):self.assertAlmostEqual(a[1],b[0],places=3)
        self.assertAlmostEqual(spans[-1][1],163.23333333333332)

    def test_showcase_nine_named_mappings_and_independent_entry(self):
        m=json.loads((ROOT/'packs/dark-3d-showcase/1.3.0-candidate/manifest.json').read_text());profile=load_profile(m,ROOT/'adaptation-profiles')
        for scene in m['scenes'][:9]:self.assertTrue(all(s.get('inputPath') or s.get('inputTemplate') for s in scene['slots']))
        new=m['scenes'][-1];c=profile['scenes'][-1]
        self.assertEqual(c['entry']['mode'],'independent');self.assertNotIn('requiresPrevious',c['entry']);self.assertEqual(c['cardinality']['artifacts'],dict(min=1,max=1))
        self.assertNotIn('PASS',pack_scene_parts(ROOT/'packs/dark-3d-showcase/1.3.0-candidate',m)[1][-1])
        old=profile['scenes'][2];self.assertEqual(old['entry']['continuityBindings'][0]['previousSlot'],'grid_opus55')

if __name__=='__main__':unittest.main()

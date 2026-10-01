import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from adapt_project import AdaptError,compile_plan
from build_macro_project import pack_scene_parts,bind_authored_block


class PaperBallContractTest(unittest.TestCase):
    def setUp(self):
        self.dir=ROOT/'packs/paper-ball-performance/0.1.3-candidate'
        self.pack=json.loads((self.dir/'manifest.json').read_text())
        self.spec={'pack':self.pack['id'],'fps':60,'scenes':[]}
        offset=0
        for scene,frames in zip(self.pack['scenes'],[334,762]):
            self.spec['scenes'].append({'id':scene['id']+'-new','sceneId':scene['id'],'durationFrames':frames,
                'inputs':copy.deepcopy(scene['inputExample']),
                'cues':{c['id']:{'frame':offset+round((c['at']-scene['source']['start'])*60)} for c in scene['cues']}})
            offset+=frames

    def test_two_complete_groups_keep_motion_and_parameterize_symbols(self):
        plan=compile_plan(self.pack,self.spec)
        self.assertEqual(plan['end_frame'],1096)
        for scene in plan['scenes']:
            for w in scene['motionWindows']:
                self.assertLessEqual(abs(w['outputEndFrame']-w['outputStartFrame']-round((w['sourceEnd']-w['sourceStart'])*60)),1)
        _,blocks=pack_scene_parts(self.dir,self.pack)
        for scene,block,item in zip(self.pack['scenes'],blocks,plan['scenes']):
            bound,_=bind_authored_block(block,scene,item['slots'],scene['id'])
            self.assertNotIn('on air · 阿杜Next',bound)
            if scene['id']=='calendar-to-delivery':
                self.assertNotIn('EP ${String(11 + i)',bound)
                self.assertNotIn('DAY ${i + 1}',bound)
                self.assertIn('STEP ${i + 1}',bound)

    def test_missing_semantic_cue_overflow_and_short_duration_refuse(self):
        missing=copy.deepcopy(self.spec);missing['scenes'][0]['cues'].pop('conclusion')
        with self.assertRaisesRegex(AdaptError,'Bind semantic cue'):compile_plan(self.pack,missing)
        long=copy.deepcopy(self.spec);long['scenes'][0]['inputs']['conclusion']='七个汉字就太长'
        with self.assertRaisesRegex(AdaptError,'allows 6'):compile_plan(self.pack,long)
        short=copy.deepcopy(self.spec);short['scenes'][0]['durationFrames']=296
        with self.assertRaises(AdaptError):compile_plan(self.pack,short)

    def test_ast_inventory_cannot_select_a_different_source_range(self):
        path=ROOT/'adapters/paper-ball/extract.py'
        spec=importlib.util.spec_from_file_location('paper_ball_adapter',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        inventory={'sourceScenesSha256':module.HASHES['scenes.js'],'units':[{} for _ in range(35)]}
        for i,(start,end,sha) in module.REVIEWED_UNITS.items():
            inventory['units'][i]={'index':i,'startCodepoint':start,'endCodepoint':end,'sha256':sha}
        inventory['units'][13]['endCodepoint']-=1
        with self.assertRaisesRegex(ValueError,'AST selection changed'):module.source_units('',inventory)

    def test_owner_title_font_and_source_media_are_not_bundled(self):
        self.assertEqual(self.pack['externalFonts'][0]['family'],'YSBT')
        self.assertFalse(any(p.suffix.lower() in {'.ttf','.mp4','.mov','.jpg','.png','.wav','.mp3'} for p in self.dir.rglob('*')))
        self.assertIn('fonts_ready.js',self.pack['runtimeFiles'])
        self.assertEqual(self.pack['scenes'][0]['provenance']['originalElementIdSeed'],116)
        self.assertEqual(self.pack['scenes'][1]['provenance']['originalElementIdSeed'],281)


if __name__=='__main__':unittest.main()

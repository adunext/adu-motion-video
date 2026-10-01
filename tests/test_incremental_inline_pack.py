import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from adapt_project import AdaptError, compile_plan
from build_macro_project import pack_scene_parts


class IncrementalInlinePackTest(unittest.TestCase):
    def setUp(self):
        self.pack=ROOT/'packs/paper-balance/0.1.6-candidate'
        self.manifest=json.loads((self.pack/'manifest.json').read_text())
        self.tmp=tempfile.TemporaryDirectory(prefix='adu-inline-contract-test-')
        self.addCleanup(self.tmp.cleanup)
        self.image=Path(self.tmp.name)/'symbol.svg'
        self.image.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="700" height="600" viewBox="0 0 700 600"><rect width="700" height="600" fill="teal"/></svg>')
        inputs=copy.deepcopy(self.manifest['scenes'][0]['inputExample'])
        inputs['illustration']=str(self.image)
        self.spec={'pack':'paper-balance','fps':60,'scenes':[{
            'id':'new-half-product','sceneId':'apparent-tension-to-value','durationFrames':834,
            'inputs':inputs,'cues':{'value':{'frame':278},'illustration':{'frame':510},'steps':{'frame':706}}}]}

    def test_increment_keeps_complete_motion_and_cannot_omit_the_recap(self):
        plan=compile_plan(self.manifest,self.spec)
        scene=plan['scenes'][0]
        self.assertEqual(plan['end_frame'],834)
        for window in scene['motionWindows']:
            original=round((window['sourceEnd']-window['sourceStart'])*60)
            self.assertLessEqual(abs(window['outputEndFrame']-window['outputStartFrame']-original),1)
        self.spec['scenes'][0]['cues'].pop('steps')
        with self.assertRaisesRegex(AdaptError,'Bind semantic cue'):
            compile_plan(self.manifest,self.spec)

    def test_new_input_rejects_missing_media_and_capacity_overflow(self):
        self.spec['scenes'][0]['inputs']['illustration']=''
        with self.assertRaises(AdaptError):compile_plan(self.manifest,self.spec)
        self.spec['scenes'][0]['inputs']['illustration']=str(self.image)
        self.spec['scenes'][0]['inputs']['steps'][0]['label']='五个汉字长'
        with self.assertRaisesRegex(AdaptError,'allows 4'):
            compile_plan(self.manifest,self.spec)

    def test_pack_has_no_owner_media_and_embedded_fonts_keep_their_notices(self):
        _,blocks=pack_scene_parts(self.pack,self.manifest)
        self.assertEqual(len(blocks),1)
        self.assertFalse(any(p.suffix.lower() in {'.mp4','.mov','.jpg','.png','.wav','.mp3'} for p in self.pack.rglob('*')))
        css=(self.pack/'style.css').read_text()
        self.assertIn('data:font/woff2;base64,',css)
        for family in ['anton','caveat','geist','geistmono']:
            notice=(self.pack/'licenses'/f'OFL-{family}.txt').read_text()
            self.assertIn(notice,css)

    def test_unreviewed_source_is_rejected_before_any_output_or_source_mutation(self):
        path=ROOT/'adapters/paper-balance/extract.py'
        spec=importlib.util.spec_from_file_location('reviewed_inline_adapter',path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        root=Path(self.tmp.name);record=root/'record';record.mkdir()
        original=root/'owner.html';original.write_text('owner project must remain unchanged')
        (record/'source.json').write_text(json.dumps({'revision':'unreviewed','origin':str(root)}))
        output=root/'new-pack'
        with self.assertRaisesRegex(ValueError,'reviewed source revision'):module.extract(record,output)
        self.assertFalse(output.exists())
        self.assertEqual(original.read_text(),'owner project must remain unchanged')


if __name__=='__main__':unittest.main()

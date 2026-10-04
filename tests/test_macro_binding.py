import hashlib
import sys
from pathlib import Path
import unittest
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_macro_project import bind_authored_block
from adapt_project import AdaptError

class MacroBindingTests(unittest.TestCase):
    def test_manual_scaffold_requires_episode_cues_before_compilation(self):
        import json
        from build_macro_project import scaffold
        from adapt_project import compile_plan
        # A structurally valid scene must not compile with demo seconds
        # supplied by the scaffolder as if they were episode observations.
        pack = {'id': 'cue-test', 'fps': 60, 'scenes': [{
            'id': 'claim', 'source': {'start': 0, 'end': 4},
            'cues': [{'id': 'proof', 'at': 1, 'kind': 'semantic', 'required': True},
                     {'id': 'beat', 'at': 3, 'kind': 'beat', 'required': False}],
            'slots': []}]}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'draft.json'
            scaffold(pack, path)
            spec = json.loads(path.read_text())
            self.assertNotIn('beat', spec['scenes'][0]['cues'])
            with self.assertRaisesRegex(AdaptError, 'proof cue needs'):
                compile_plan(pack, spec)
            spec['scenes'][0]['cues']['proof'] = {'at': 2}
            plan = compile_plan(pack, spec)
            self.assertEqual(plan['scenes'][0]['cues'][0]['outputFrame'], 120)
            self.assertFalse(plan['scenes'][0]['cues'][1]['explicit'])
            self.assertEqual(pack['scenes'][0]['cues'][0]['at'], 1)
            with self.assertRaises(AdaptError):
                scaffold(pack, path)

    def test_copied_media_bindings_are_relative_to_exported_project(self):
        from build_macro_project import copy_media
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); stage=root/'project'; (stage/'assets').mkdir(parents=True)
            source=root/'private-photo.png'; source.write_bytes(b'test image payload')
            item={'id':'one', 'slots':{'photo':str(source)},
                  'bindings':[{'id':'photo','type':'image','value':str(source)}]}
            scene={'slots':[{'id':'photo','type':'image','sourceAsset':'assets/original.png'}]}
            block,_=copy_media(stage,{},item,scene,"img('original.png')",set())
            value=item['slots']['photo']
            self.assertFalse(Path(value).is_absolute())
            self.assertEqual((stage/value).read_bytes(),source.read_bytes())
            self.assertEqual(item['bindings'][0]['value'],value)
            self.assertNotIn(str(root),block)

    def test_selected_square_scene_requires_explicit_or_automatic_tracking(self):
        import json
        from build_macro_project import needs_face_tracking, prepare_face
        root=Path(__file__).resolve().parents[1]
        pack=json.loads((root/'packs/anim3/manifest.json').read_text())
        prelude=(root/'packs/anim3/scenes.js').read_text().split('/* ---------- S1')[0]
        self.assertFalse(needs_face_tracking(pack,{'scenes':[{'source_scene_index':0}]},prelude))
        self.assertTrue(needs_face_tracking(pack,{'scenes':[{'source_scene_index':5}]},prelude))
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(AdaptError):
                prepare_face(Path(tmp),{'faceTracking':{'mode':'none'}},True,60,120)
            result=prepare_face(Path(tmp),{'faceTracking':{'mode':'fixed','cx':.5,'cy':.7,'h':.2}},True,60,120)
            self.assertEqual(result['mode'],'explicit-fixed')

    def test_audio_recipe_is_saved_with_project(self):
        from build_macro_project import write_project_audio
        with tempfile.TemporaryDirectory() as tmp:
            stage=Path(tmp)
            write_project_audio(stage,{'mode':'none'})
            self.assertTrue((stage/'audio_runtime/macro_audio.py').is_file())
            self.assertTrue((stage/'audio_runtime/audiolib.py').is_file())
            self.assertNotIn('ADU_MOTION_VIDEO_ROOT',(stage/'audio.py').read_text())

    def test_media_names_do_not_collide_after_unicode_normalization(self):
        from build_macro_project import safe_name
        self.assertNotEqual(safe_name('开场\0photo'), safe_name('结尾\0photo'))
        self.assertNotEqual(safe_name('a_b\0c'), safe_name('a\0b_c'))

    def test_short_text_changes_only_reviewed_span(self):
        block = "const css='overflow:hidden;width:60px'; const label='low';"
        start = block.rindex("low")
        scene = {"sourceBlockSha256": hashlib.sha256(block.encode()).hexdigest(), "slots": [{"id":"status","type":"text","sourceText":"low","sourceSpans":[{"start":start,"end":start+3}]}]}
        result, _ = bind_authored_block(block, scene, {"status":"ready"}, "test")
        self.assertIn("overflow:hidden;width:60px", result)
        self.assertIn("label='ready'", result)
        with self.assertRaises(AdaptError): bind_authored_block(block + " ", scene, {"status":"ready"}, "test")

    def test_overlapping_spans_fail_instead_of_guessing(self):
        block = "const label='example';"
        start=block.index("example")
        slot={"id":"a","type":"text","sourceText":"example","sourceSpans":[{"start":start,"end":start+7}]}
        scene={"sourceBlockSha256":hashlib.sha256(block.encode()).hexdigest(),"slots":[slot,{**slot,"id":"b"}]}
        with self.assertRaises(AdaptError):bind_authored_block(block,scene,{"a":"one","b":"two"},"test")

    def test_one_semantic_binding_preserves_html_and_plain_text_contexts(self):
        block="const html='<b>Old label</b>'; const text='Old label';"
        starts=[block.index('Old label'),block.rindex('Old label')]
        scene={'sourceBlockSha256':hashlib.sha256(block.encode()).hexdigest(),
               'slots':[{'id':'evidence.title','type':'dynamicText','sourceText':'Old label','renderContext':'html',
                         'sourceSpans':[{'start':starts[0],'end':starts[0]+9},
                                        {'start':starts[1],'end':starts[1]+9,'renderContext':'text'}]}]}
        bound,_=bind_authored_block(block,scene,{'evidence.title':'A & B < 3'},'test')
        self.assertIn("html='<b>A &amp; B &lt; 3</b>'",bound)
        self.assertIn("text='A & B < 3'",bound)
        bound,_=bind_authored_block(block,scene,{'evidence.title':'第一行\n第二行 <br>'},'test')
        self.assertIn("html='<b>第一行<br>第二行 &lt;br&gt;</b>'",bound)
        self.assertIn("text='第一行\\n第二行 <br>'",bound)

    def test_all_public_text_ranges_match_and_are_disjoint(self):
        import json
        from build_macro_project import scene_parts
        root=Path(__file__).resolve().parents[1]
        for pack in ("anim3","anim4"):
            folder=root/"packs"/pack
            manifest=json.loads((folder/"manifest.json").read_text())
            _,blocks=scene_parts((folder/"scenes.js").read_text())
            self.assertEqual(len(blocks),len(manifest["scenes"]))
            for scene,block in zip(manifest["scenes"],blocks):
                values={}
                for slot in scene["slots"]:
                    if slot["type"] in ("text","dynamicText"):values[slot["id"]]="Test"
                    elif slot["type"]=="number":values[slot["id"]]=7
                bound,_=bind_authored_block(block,scene,values,pack+"."+scene["id"])
                self.assertTrue(bound)

if __name__ == "__main__":unittest.main()

import hashlib
import sys
from pathlib import Path
import unittest
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_macro_project import bind_authored_block
from adapt_project import AdaptError

class MacroBindingTests(unittest.TestCase):
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

    def test_audio_recipe_is_saved_with_project(self):
        from build_macro_project import write_project_audio
        with tempfile.TemporaryDirectory() as tmp:
            stage=Path(tmp)
            write_project_audio(stage,{'mode':'synth'})
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

import hashlib
from pathlib import Path
import sys
import tempfile
import shutil
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from adapt_project import AdaptError
from build_macro_project import copy_external_fonts


class ExternalFontsTest(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='adu-owner-font-test-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.stage=self.root/'project';self.stage.mkdir()
        self.font=self.root/'owner.ttf';shutil.copy2(ROOT/'assets/fonts/NotoSansSC.ttf',self.font)
        self.pack={'externalFonts':[{'id':'title','family':'YSBT','sha256':hashlib.sha256(self.font.read_bytes()).hexdigest(),
                                    'format':'truetype','extension':'.ttf','required':True}]}

    def test_missing_or_invalid_recommendation_uses_bundled_fonts(self):
        css, report=copy_external_fonts(self.pack,{},self.root,self.stage)
        self.assertEqual(report[0]['mode'],'bundled-fallback')
        self.assertIn('fonts/NotoSansSC.ttf',css)
        self.font.write_bytes(b'not a font')
        _, report=copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        self.assertEqual(report[0]['mode'],'bundled-fallback')
        self.assertTrue((self.stage/'fonts/notosanssc-OFL.txt').is_file())
        with self.assertRaisesRegex(AdaptError,'Exact font requested'):
            copy_external_fonts(self.pack,{'fontPolicy':'exact'},self.root,self.stage)

    def test_different_valid_owner_font_is_accepted_and_pinned(self):
        shutil.copy2(ROOT/'assets/fonts/NotoSansMono.ttf',self.font)
        css,report=copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        self.assertEqual(report[0]['mode'],'user-substitute')
        self.assertEqual(report[0]['sha256'],hashlib.sha256(self.font.read_bytes()).hexdigest())
        self.assertIn('unicode-range:',css)

    def test_verified_owner_font_becomes_local_project_asset(self):
        css,report=copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        self.assertIn('fonts/title.ttf',css)
        self.assertEqual((self.stage/'fonts/title.ttf').read_bytes(),self.font.read_bytes())
        self.assertEqual(report[0]['sha256'],self.pack['externalFonts'][0]['sha256'])
        self.assertNotIn(str(self.root),str(report))

    def test_distinct_weights_are_declared_for_a_shared_variable_font(self):
        item=self.pack['externalFonts'][0];item['id']='title-700'
        css,_=copy_external_fonts(self.pack,{'externalFontFiles':{'title-700':'owner.ttf'}},self.root,self.stage)
        self.assertIn('font-weight:700;',css)
        item['weight']='700 400'
        with self.assertRaisesRegex(AdaptError,'weight'):
            copy_external_fonts(self.pack,{'externalFontFiles':{'title-700':'owner.ttf'}},self.root,self.stage)

    def test_invalid_declaration_and_unknown_input_rejected(self):
        self.pack['externalFonts'][0]['family']="font');bad"
        with self.assertRaisesRegex(AdaptError,'Invalid external font family'):
            copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        with self.assertRaisesRegex(AdaptError,'Unknown externalFontFiles'):
            copy_external_fonts({}, {'externalFontFiles':{'unknown':'owner.ttf'}},self.root,self.stage)


if __name__=='__main__':unittest.main()

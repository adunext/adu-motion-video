import hashlib
from pathlib import Path
import sys
import tempfile
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
        self.font=self.root/'owner.ttf';self.font.write_bytes(b'reviewed font fixture')
        self.pack={'externalFonts':[{'id':'title','family':'YSBT','sha256':hashlib.sha256(self.font.read_bytes()).hexdigest(),
                                    'format':'truetype','extension':'.ttf','required':True}]}

    def test_missing_or_changed_font_refuses_substitution(self):
        with self.assertRaisesRegex(AdaptError,'Provide externalFontFiles.title'):
            copy_external_fonts(self.pack,{},self.root,self.stage)
        self.font.write_bytes(b'different font fixture')
        with self.assertRaisesRegex(AdaptError,'differs from the reviewed'):
            copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        self.assertFalse((self.stage/'fonts').exists())

    def test_verified_owner_font_becomes_local_project_asset(self):
        css,report=copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        self.assertIn('fonts/title.ttf',css)
        self.assertEqual((self.stage/'fonts/title.ttf').read_bytes(),self.font.read_bytes())
        self.assertEqual(report[0]['sha256'],self.pack['externalFonts'][0]['sha256'])
        self.assertNotIn(str(self.root),str(report))

    def test_invalid_declaration_and_unknown_input_rejected(self):
        self.pack['externalFonts'][0]['family']="font');bad"
        with self.assertRaisesRegex(AdaptError,'Invalid external font family'):
            copy_external_fonts(self.pack,{'externalFontFiles':{'title':'owner.ttf'}},self.root,self.stage)
        with self.assertRaisesRegex(AdaptError,'Unknown externalFontFiles'):
            copy_external_fonts({}, {'externalFontFiles':{'unknown':'owner.ttf'}},self.root,self.stage)


if __name__=='__main__':unittest.main()

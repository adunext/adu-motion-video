"""Portrait geometry must not alter the choreography or media/audio timeline."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from pack_layout import resolve_layout,install_layout,project_dimensions
from adapt_project import compile_plan,AdaptError
from adaptation import load_profile,validate_profile
from build_macro_project import pack_scene_parts
from portrait_fixture import PACKS
from extract_authored_pack import copy_layout_contract

class PortraitContractTests(unittest.TestCase):
 def test_new_extraction_preserves_only_reviewed_layout_assets(self):
  with tempfile.TemporaryDirectory() as tmp:
   source=Path(tmp)/'source';stage=Path(tmp)/'stage';source.mkdir();stage.mkdir()
   for name,data in [('portrait.js','window.PACK_LAYOUT={};'),('portrait.css','#stage{width:1080px}')]:
    (source/name).write_text(data)
   proposal={'layouts':{'landscape':{'width':1920,'height':1080},'portrait':{'width':1080,'height':1920,'runtime':'portrait.js','stylesheet':'portrait.css'}},'sourceFiles':{n:hashlib.sha256((source/n).read_bytes()).hexdigest() for n in ['portrait.js','portrait.css']}}
   result=copy_layout_contract(proposal,source,stage)
   self.assertEqual(result,proposal['layouts']);self.assertEqual((source/'portrait.js').read_bytes(),(stage/'portrait.js').read_bytes())
   (source/'portrait.js').write_text('changed after review')
   with self.assertRaisesRegex(ValueError,'fingerprint'):copy_layout_contract(proposal,source,stage)
   proposal['layouts']['portrait'].pop('runtime')
   with self.assertRaisesRegex(ValueError,'runtime and stylesheet'):copy_layout_contract(proposal,source,stage)
   self.assertIsNone(copy_layout_contract({},source,stage))
 def test_all_nine_routes_cover_29_groups_without_source_or_audio_edits(self):
  count=0
  for family,version in PACKS:
   p=ROOT/'packs'/family/version;m=json.loads((p/'manifest.json').read_text());base=p.parent/m['portraitBase']['version']
   old=json.loads((base/'manifest.json').read_text());count+=len(m['scenes'])
   self.assertEqual(m['scenes'],old['scenes'],family)
   for name in m['files']:
    self.assertEqual(hashlib.sha256((p/name).read_bytes()).hexdigest(),m['files'][name],(family,name))
   for name in ['lib.js','style.css','scenes.js','audio_timeline.json']:
    if (base/name).is_file():self.assertEqual((p/name).read_bytes(),(base/name).read_bytes(),(family,name))
   if m.get('sourceFormat')=='authored-unit/1':pack_scene_parts(p,m)
   profile=load_profile(m,ROOT/'adaptation-profiles')
   self.assertTrue(validate_profile(profile,m)['ready'],family)
   self.assertEqual(resolve_layout(m,{'layout':'portrait'})['height'],1920)
   self.assertEqual(m['status'],'candidate')
  self.assertEqual(count,29)
 def test_output_layout_changes_only_geometry_not_timing_audio_or_video_clocks(self):
  m={'id':'test','fps':60,'layouts':{'landscape':{'width':1920,'height':1080},'portrait':{'width':1080,'height':1920}},'scenes':[{'id':'group','source':{'start':0,'end':4},'minFrames':180,'maxHoldFrames':120,'motionWindows':[{'start':.5,'end':1.5}],'slots':[],'cues':[{'id':'proof','at':1,'required':True}],'sfx':[{'at':1,'type':'hit','d':.2}]}]}
  spec={'scenes':[{'id':'one','sceneId':'group','durationFrames':300,'cues':{'proof':{'at':1}},'slots':{}}]}
  a=compile_plan(m,spec);b=compile_plan(m,{**spec,'layout':'portrait'})
  self.assertEqual((b['width'],b['height']),(1080,1920));self.assertEqual(a['scenes'],b['scenes']);self.assertEqual(a['sfx'],b['sfx']);self.assertEqual(a['end_frame'],b['end_frame'])
 def test_legacy_or_unknown_layout_requires_an_explicit_supported_version(self):
  with self.assertRaisesRegex(ValueError,'no portrait'):resolve_layout({'width':1920,'height':1080},{'layout':'portrait'})
  with self.assertRaisesRegex(ValueError,'landscape or portrait'):resolve_layout({}, {'layout':'vertical'})
 def test_installed_adapter_is_frozen_and_leaves_audio_unchanged(self):
  p=ROOT/'packs/classic-performance/1.1.0-candidate';m=json.loads((p/'manifest.json').read_text())
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp);(out/'config.js').write_text('window.CONFIG={};');(out/'voice.wav').write_bytes(b'unchanged narration')
   layout=resolve_layout(m,{'layout':'portrait'});css,script,files=install_layout(p,m,{'layout':layout},out)
   self.assertIn('portrait.css',css);self.assertIn('portrait.js',script);self.assertEqual((out/'voice.wav').read_bytes(),b'unchanged narration');self.assertEqual(files,['portrait.js','portrait.css']);self.assertIn('CONFIG.height=1920',(out/'config.js').read_text())
   tampered={**m,'files':{**m['files'],'portrait.js':'0'*64}}
   with self.assertRaisesRegex(ValueError,'frozen fingerprint'):install_layout(p,tampered,{'layout':layout},out)
 def test_wrong_export_viewport_is_rejected_before_rendering(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);(p/'index.html').write_text('<html>');(p/'macro_plan.json').write_text(json.dumps({'width':1080,'height':1920}))
   self.assertEqual(project_dimensions(p),(1080,1920))
   for command in [[sys.executable,str(ROOT/'scripts/export_project.py'),str(p),str(p/'wrong.mp4'),'--width','1920'],['node',str(ROOT/'scripts/render_project.mjs'),str(p/'index.html'),'--probe','--width','1920']]:
    result=subprocess.run(command,capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('layout',result.stderr)
   self.assertFalse((p/'wrong.mp4').exists())
   (p/'macro_plan.json').write_text(json.dumps({'width':1920,'height':1080}))
   result=subprocess.run(['bash',str(ROOT/'scripts/pipeline.sh'),'vert',str(p),str(p/'wrong.mp4')],capture_output=True,text=True)
   self.assertNotEqual(result.returncode,0);self.assertIn('portrait project layout',result.stderr)
if __name__=='__main__':unittest.main()

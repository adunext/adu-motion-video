"""New scene contracts reject lost copy, shortened actions and unconsumed inputs."""
import copy,hashlib,json,sys,tempfile,unittest
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from adapt_project import compile_plan,AdaptError
from adaptation import load_profile
from build_macro_project import bind_authored_block,pack_scene_parts
from semantic_inputs import expand_inputs,SemanticInputError
PACK=ROOT/'packs/vivid-sticker-performance/0.1.1-candidate'
class VividStickerTests(unittest.TestCase):
 def setUp(self):
  self.m=json.loads((PACK/'manifest.json').read_text());self.temp=tempfile.TemporaryDirectory(prefix='adu-vivid-contract-');self.addCleanup(self.temp.cleanup);self.asset=Path(self.temp.name)/'new.svg';self.asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280" viewBox="0 0 720 1280"/>');self.project=Path(self.temp.name);(self.project/'talkmap.js').write_text('const TALKMAP=[[0,1]];');(self.project/'talk').mkdir();Image.new('RGB',(720,1280)).save(self.project/'talk/f_0001.jpg')
 def target(self,sc,start=0):
  inputs=copy.deepcopy(sc['inputExample']);inputs['illustrations']={'giver':str(self.asset),'transfer':str(self.asset),'receiver':str(self.asset)} if sc['id']=='prepared-to-reuse' else inputs.get('illustrations',{})
  if not inputs['illustrations']:inputs.pop('illustrations')
  return {'id':sc['id']+'-new','sceneId':sc['id'],'durationFrames':sc['minFrames'],'inputs':inputs,'slots':{'grainTexture':str(self.asset),'presenter':'@talk'},'cues':{c['id']:{'frame':start+round((c['at']-sc['source']['start'])*60)} for c in sc['cues']}}
 def test_frozen_private_runtime_and_all_semantic_profiles(self):
  _,blocks=pack_scene_parts(PACK,self.m);profile=load_profile(self.m,ROOT/'adaptation-profiles');self.assertEqual(len(profile['scenes']),3)
  for sc,body in zip(self.m['scenes'],blocks):
   self.assertEqual(hashlib.sha256(body.encode()).hexdigest(),sc['sourceBlockSha256'])
   for old in ['window.SFX =','window.renderAt =','window.PRELOAD =','/Volumes/','/Users/','REC · 阿杜Next','>AduNext</b>']:self.assertNotIn(old,body)
   self.assertIn('t = window.MACRO_OUTPUT_T ?? t;',body);self.assertIn('sc.fg(fgx, t)',body)
  self.assertFalse(any(p.suffix in ['.png','.jpg','.mp4','.mp3','.woff2'] for p in PACK.rglob('*')))
 def test_repeated_reordered_groups_keep_protected_motion_and_output_geometry(self):
  for layout in ['landscape','portrait']:
   scenes=[];start=0
   for index in [2,1,0,1,0]:
    sc=self.m['scenes'][index];item=self.target(sc,start);item['id']+='-'+str(len(scenes));scenes.append(item);start+=sc['minFrames']
   plan=compile_plan(self.m,{'pack':self.m['id'],'layout':layout,'scenes':scenes},spec_dir=Path(self.temp.name),project=self.project,audio_timeline=json.loads((PACK/'audio_timeline.json').read_text()))
   self.assertEqual(plan['durationFrames'],start);self.assertEqual(plan['width'],1080 if layout=='portrait' else 1920);self.assertEqual(plan['voiceClock'],'output');self.assertEqual(len(plan['scenes']),5)
 def test_each_group_refuses_shortened_motion_missing_cue_and_extra_quantity(self):
  for sc in self.m['scenes']:
   target=self.target(sc);target['durationFrames']-=60
   with self.assertRaises(AdaptError):compile_plan(self.m,{'scenes':[target]},spec_dir=Path(self.temp.name),project=self.project)
   target=self.target(sc);target['cues'].pop(next(iter(target['cues'])))
   with self.assertRaises(AdaptError):compile_plan(self.m,{'scenes':[target]},spec_dir=Path(self.temp.name),project=self.project)
  sc=self.m['scenes'][0];target=self.target(sc);target['inputs']['keywords'].append('extra')
  with self.assertRaises(SemanticInputError):expand_inputs(sc,target)
 def test_manual_plan_cannot_end_on_handoff_or_feedback_and_tail_scales_with_fps(self):
  for sc in self.m['scenes'][1:]:
   with self.assertRaisesRegex(AdaptError,'following output frames'):
    compile_plan(self.m,{'scenes':[self.target(sc)]},spec_dir=self.project,project=self.project)
  before=self.m['scenes'][1];after=self.m['scenes'][0]
  plan=compile_plan(self.m,{'scenes':[self.target(before),self.target(after,before['minFrames'])]},spec_dir=self.project,project=self.project)
  self.assertGreater(plan['end_frame']-plan['scenes'][0]['output_end_frame'],73)

 def test_tail_frames_are_resampled_on_target_frame_grid(self):
  m={'id':'tail-fixture','fps':60,'scenes':[{'id':'action','source':{'start':0,'end':2},'minFollowingFrames':73},{'id':'outro','source':{'start':2,'end':4}}]}
  for frames in [36,37]:
   spec={'fps':30,'scenes':[{'sceneId':'action','durationFrames':60},{'sceneId':'outro','durationFrames':frames}]}
   if frames==36:
    with self.assertRaisesRegex(AdaptError,'37 following output frames'):compile_plan(m,spec)
   else:self.assertEqual(compile_plan(m,spec)['durationFrames'],97)

 def test_new_copy_binds_dynamic_keywords_and_versions_and_refuses_oversize(self):
  for sc in self.m['scenes']:
   values=expand_inputs(sc,self.target(sc))['slots'];body=(PACK/sc['sourceCodeFile']).read_text();bound,_=bind_authored_block(body,sc,values,'test')
   self.assertNotEqual(body,bound)
   for slot in sc['slots']:
    if slot['type'] in ['text','dynamicText']:
     values[slot['id']]='长'*(slot['maxChars']+1)
     with self.assertRaises(AdaptError):compile_plan(self.m,{'scenes':[{**self.target(sc),'inputs':{},'slots':values}]},spec_dir=Path(self.temp.name),project=self.project)
     break
if __name__=='__main__':unittest.main()

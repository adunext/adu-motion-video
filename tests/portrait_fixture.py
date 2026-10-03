"""Synthetic geometry fixtures. These are never production-media acceptance."""
from pathlib import Path
import sys,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_macro_project import scene_parts
PACKS=[(n,'1.1.0-candidate') for n in ['classic-performance','continuous-performance','stage-performance','editorial-performance','kinetic-performance','paper-balance','paper-ball-performance']]+[('doubao-console-performance','0.2.0-candidate'),('dark-3d-showcase','1.2.0-candidate')]
PLACEHOLDER='''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280"><rect width="720" height="1280" fill="#34445c"/><circle cx="360" cy="410" r="130" fill="#87b3c9"/><path d="M100 1150 Q80 570 360 570 Q640 570 620 1150" fill="#6781a5"/><text x="360" y="1030" text-anchor="middle" fill="white" font-size="38">布局测试 · 无真人</text></svg>'''
def create(directory):
 directory=Path(directory);directory.mkdir(exist_ok=True)
 for family,version in PACKS:
  pack=ROOT/'packs'/family/version;m=json.loads((pack/'manifest.json').read_text());out=directory/family;out.mkdir()
  (out/'assets').mkdir();(out/'assets/demo-presenter.svg').write_text(PLACEHOLDER)
  if m.get('sourceFormat')=='authored-unit/1':
   pre='';blocks=[(pack/sc['sourceCodeFile']).read_text() for sc in m['scenes']];lib=(pack/'lib.js').read_text()
  else:
   pre,blocks=scene_parts((pack/'scenes.js').read_text());lib=(ROOT/'template/lib.js').read_text()
   pre=re.sub(r'function faceAt\(t\) \{[\s\S]*?\n\}(?=\nfunction camAt)','',pre,count=1);pre=pre.replace('RACE_K','PACK_RACE_K')
  (out/'lib.js').write_text(lib)
  (out/'scenes.js').write_text('window.MACRO_SOURCE_SFX=[];\n'+pre+'\n'+''.join('{const before=SFX.length;'+body+';window.MACRO_SOURCE_SFX.push(SFX.slice(before));}\n' for body in blocks))
  for name in ['style.css','portrait.css',m['layouts']['portrait']['runtime']]:shutil.copy2(pack/name,out/name)
  # This fixture explicitly checks local system-font geometry; no private font.
  (out/'style.css').write_text(re.sub(r'@font-face\s*\{[^}]*\}', '', (out/'style.css').read_text(), flags=re.I))
  runtime=''
  for name in m.get('runtimeFiles',[]):
   if 'font' not in name:
    shutil.copy2(pack/name,out/name);runtime+='<script src="'+name+'"></script>'
  plan=[];frame=0
  for i,sc in enumerate(m['scenes']):
   n=round((sc['source']['end']-sc['source']['start'])*60)
   plan.append({'id':str(i),'sceneId':sc['id'],'output_start_frame':frame,'output_end_frame':frame+n,'time_map':[{'output_frame':frame,'source':sc['source']['start']},{'output_frame':frame+n,'source':sc['source']['end']} ]});frame+=n
  config={'demo':True,'fps':60,'width':1080,'height':1920,'end':frame/60,'subtitles':False,'talkFrames':0,'brand':'LAYOUT QA','race':{'keys':[0,frame/60,frame/60+1],'labels':['test','end']}}
  boot='window.CONFIG='+json.dumps(config)+';window.PACK_LAYOUT='+json.dumps({'name':'portrait','width':1080,'height':1920,'pack':m['id']})+';window.PACK_BRAND_HTML="LAYOUT QA";window.PACK_PRESENTER_LABEL="NO PERSON";window.DOUBAO_OUTPUT_VOX=Array(20000).fill(0);window.PACK_NUMBERS={};window.MACRO_IS_OPENING_SCENE=true;window.MACRO_OUTPUT_T=0;const WALL=Array.from({length:389},(_,i)=>["QA"+i,""]);const FACE={};const SUBS=[];window.MACRO_PLAN='+json.dumps({'fps':60,'end_frame':frame,'scenes':plan})+';'
  shutil.copy2(ROOT/'scripts/macro_runtime.js',out/'macro_main.js')
  harness='<script src="macro_main.js"></script>'
  entry='<meta charset="utf-8"><link rel="stylesheet" href="style.css"><link rel="stylesheet" href="portrait.css"><div id="stage"><div id="world"></div><div id="fx"></div><div id="ov"></div></div><script>'+boot+'</script><script src="lib.js"></script>'+runtime+'<script src="scenes.js"></script>'+harness+'<script src="'+m['layouts']['portrait']['runtime']+'"></script>'
  if family=='dark-3d-showcase':entry=entry.replace('window.PACK_LAYOUT=', 'window.SHOWCASE_LAYOUT={layout:"portrait",width:1080,height:1920,presenterEndSeconds:null};window.PACK_LAYOUT=')
  (out/'index.html').write_text(entry);(out/'manifest.json').write_text(json.dumps(m));(out/'plan.json').write_text(json.dumps(plan))
def create_gallery(directory):
 directory=Path(directory)
 for file in (ROOT/'examples/portrait-catalog').iterdir():
  if file.suffix in ['.js','.html','.svg']:shutil.copy2(file,directory/file.name)
 # The optional encoded QA movie is a separate export, not generated here.
 index=directory/'index.html';index.write_text(re.sub(r'<hr><a id="export"[\s\S]*?</small>', '', index.read_text()))
 for family,_ in PACKS:
  manifest=directory/family/'manifest.json';m=json.loads(manifest.read_text())
  # Preview metadata is not a buildable frozen pack or an acceptance receipt.
  (directory/family/'preview-catalog.json').write_text(json.dumps({'id':m['id'],'version':m['version'],'scenes':[{'id':s['id'],'title':s.get('title',s.get('role',s['id']))} for s in m['scenes']],'scope':'synthetic-preview-only'},ensure_ascii=False))
  manifest.unlink()
  entry=directory/family/'index.html'
  entry.write_text(entry.read_text().replace('<meta charset="utf-8">','<meta charset="utf-8"><script src="../demo-media.js"></script>',1)+'<script src="../demo-loop.js"></script>')
if __name__=='__main__':
 create(sys.argv[1])
 if '--gallery' in sys.argv[2:]:create_gallery(sys.argv[1])

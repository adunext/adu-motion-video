"""Source-native macro fixture; synthetic media unless explicit private controls supplied."""
import hashlib,json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from build_macro_project import bind_authored_block
import portrait_fixture
PACK=ROOT/'packs/vivid-sticker-performance/0.1.1-candidate'
def create(parent,layout='portrait',case='new',font_source=None,source_media=None):
 parent=Path(parent);parent.mkdir(exist_ok=True)
 saved=portrait_fixture.PACKS;portrait_fixture.PACKS=[('vivid-sticker-performance','0.1.1-candidate')]
 try:portrait_fixture.create(parent)
 finally:portrait_fixture.PACKS=saved
 out=parent/'vivid-sticker-performance';m=json.loads((PACK/'manifest.json').read_text());blocks=[]
 for sc in m['scenes']:
  slots={s['id']:s.get('sourceText') for s in sc['slots'] if s['type'] in ('text','dynamicText')}
  if case!='source':
   from semantic_inputs import expand_inputs
   example=expand_inputs(sc,{'id':sc['id'],'inputs':sc['inputExample'],'slots':{}})['slots'];slots.update({k:v for k,v in example.items() if k in slots})
   if case in ('near-cjk','near-latin'):
    for s in sc['slots']:
     if s['type'] in ('text','dynamicText'):slots[s['id']]=('方法'*(s['maxChars']//2)+'新'*(s['maxChars']%2)) if case=='near-cjk' else 'W'*s['maxChars']
  body=(PACK/sc['sourceCodeFile']).read_text()
  body,_=bind_authored_block(body,{**sc,'slots':[{**s,'mustChange':case!='source'} for s in sc['slots']]},slots,sc['id']);blocks.append(body)
 (out/'scenes.js').write_text('window.MACRO_SOURCE_SFX=[];\n'+''.join('{const before=SFX.length;'+b+';window.MACRO_SOURCE_SFX.push(SFX.slice(before));}\n' for b in blocks))
 html=(out/'index.html').read_text();html=re.sub(r'const WALL=Array.from\([^;]+;', 'const WALL=[];', html);(out/'index.html').write_text(html)
 assets=out/'assets';assets.mkdir(exist_ok=True)
 placeholder=(assets/'demo-presenter.svg').read_text();demo={'p_handover.png':'giver.svg','x_notebook.png':'notebook.svg','x_robot.png':'receiver.svg'}
 for name,label in [('p_handover.png','准备者示意'),('x_notebook.png','交接物示意'),('x_robot.png','接收者示意'),('noise.png','纹理示意')]:
  if source_media:shutil.copy2(Path(source_media)/('assets/noise.png' if name=='noise.png' else 'assets/gen/'+name),assets/name)
  else:
   target=name.replace('.png','.svg');asset=ROOT/'examples/vivid-sticker-preview'/demo[name] if name in demo else ROOT/'examples/portrait-catalog/noise.svg';shutil.copy2(asset,assets/target)
   file=out/'scenes.js';file.write_text(file.read_text().replace(name,target))
 if font_source:
  (out/'style.css').write_text((PACK/'style.css').read_text());(out/'fonts').mkdir()
  for f in m['externalFonts']:
   src=Path(font_source)/Path(f['sourceFile']).name
   if hashlib.sha256(src.read_bytes()).hexdigest()!=f['sha256']:raise ValueError('Owner font hash differs')
   shutil.copy2(src,out/'fonts'/ (f['id']+'.woff2'))
  shutil.copy2(PACK/'sticker_fonts.js',out/'sticker_fonts.js')
  html=(out/'index.html').read_text().replace('<script src="scenes.js">','<script src="sticker_fonts.js"></script><script src="scenes.js">');(out/'index.html').write_text(html)
 if layout=='landscape':
  html=(out/'index.html').read_text().replace('"width": 1080, "height": 1920','"width": 1920, "height": 1080').replace('"name": "portrait"','"name": "landscape"').replace('<link rel="stylesheet" href="portrait.css">','').replace('<script src="portrait.js"></script>','')
  (out/'index.html').write_text(html)
 (out/'fixture-scope.json').write_text(json.dumps({'case':case,'layout':layout,'media':'private-source-illustrations-and-synthetic-presenter' if source_media else 'synthetic-no-person','fonts':'owner-sha-verified' if font_source else 'system-font-only','scope':'silent-geometry-binding-not-av-acceptance'}))
 return out
if __name__=='__main__':
 print(create(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else None,sys.argv[5] if len(sys.argv)>5 else None))

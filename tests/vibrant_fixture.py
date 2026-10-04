"""Silent native portrait fixture; owner-font controls never enter public files."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from build_macro_project import bind_authored_block
from semantic_inputs import expand_inputs
from test_template_stress import target
from adapt_project import timed_scene
PACK=ROOT/'packs/vibrant-color-performance/0.1.0-candidate'

def create(parent,case='new',font_source=None):
    out=Path(parent)/('vibrant-'+case);out.mkdir();(out/'assets').mkdir()
    shutil.copy2(ROOT/'examples/portrait-catalog/presenter.svg',out/'assets/demo-presenter.svg')
    shutil.copy2(ROOT/'examples/portrait-catalog/noise.svg',out/'assets/noise.svg')
    m=json.loads((PACK/'manifest.json').read_text());plan=[];code=[];offset=0
    order=[0,1,3,4,5,6,2]
    for i in order:
        sc=m['scenes'][i];base=round((sc['source']['end']-sc['source']['start'])*60)
        if case=='source':values={s['id']:s['sourceText'] for s in sc['slots'] if s['type'] in ('text','dynamicText')}
        else:
            values=expand_inputs(sc,{'inputs':sc['inputExample']})['slots']
            if case in ('near-cjk','near-latin'):
                for s in sc['slots']:
                    if s['type'] in ('text','dynamicText'):values[s['id']]=('新' if case=='near-cjk' else 'W')*s['maxChars']
        body,_=bind_authored_block((PACK/sc['sourceCodeFile']).read_text(),{**sc,'slots':[{**s,'mustChange':case!='source'} for s in sc['slots']]},values,sc['id'])
        body=body.replace('assets/noise.png','assets/noise.svg')
        code.append('{const before=SFX.length;'+body+';window.MACRO_SOURCE_SFX.push(SFX.slice(before));}\n')
        frames=base+(sc.get('maxHoldFrames',0) if case=='hold' else 0)
        item=timed_scene(sc,target(sc,frames,{}),i,0,frames,60,60,[],{},[])
        item['output_start_frame']+=offset;item['output_end_frame']+=offset
        for knot in item['time_map']:knot['output_frame']+=offset
        offset=item['output_end_frame'];plan.append(item)
    css=(PACK/'style.css').read_text()
    if font_source:
        from hashlib import sha256
        (out/'fonts').mkdir()
        for f in m['externalFonts']:
            src=Path(font_source)/Path(f['sourceFile']).name
            assert sha256(src.read_bytes()).hexdigest()==f['sha256']
            shutil.copy2(src,out/'fonts'/ (f['id']+'.woff2'))
    else:
        import re
        css=re.sub(r'@font-face\s*\{[^}]*\}','',css)
    (out/'style.css').write_text(css)
    for name in ['lib.js','typography.js','portrait.js']:shutil.copy2(PACK/name,out/name)
    shutil.copy2(ROOT/'scripts/macro_runtime.js',out/'macro_main.js')
    (out/'scenes.js').write_text('window.MACRO_SOURCE_SFX=[];\n'+''.join(code))
    boot='window.CONFIG='+json.dumps(dict(demo=True,fps=60,width=1080,height=1920,end=offset/60,talkFrames=0,subtitles=False,race=dict(keys=[0,offset/60,offset/60+1],labels=["test","end"])))+';window.PACK_LAYOUT={name:"portrait",width:1080,height:1920};window.PACK_BRAND_HTML="LAYOUT QA";window.PACK_PRESENTER_LABEL="无真人 · 布局示意";const WALL=[];const FACE={};const SUBS=[];window.MACRO_PLAN='+json.dumps(dict(fps=60,end_frame=offset,scenes=plan))+';'
    (out/'index.html').write_text('<meta charset="utf-8"><link rel="stylesheet" href="style.css"><div id="stage"><div id="world"></div><div id="fx"></div><div id="ov"></div></div><script>'+boot+'</script><script src="lib.js"></script><script src="typography.js"></script><script src="scenes.js"></script><script src="macro_main.js"></script><script src="portrait.js"></script>')
    (out/'plan.json').write_text(json.dumps(plan));(out/'macro_plan.json').write_text(json.dumps(dict(width=1080,height=1920,fps=60,end_frame=offset,scenes=plan)))
    return out

if __name__=='__main__':print(create(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'new',sys.argv[3] if len(sys.argv)>3 else None))

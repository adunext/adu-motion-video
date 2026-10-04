#!/usr/bin/env python3
"""Version-pinned native portrait islands; no source private media or recording."""
import argparse
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_macro_project import bind_authored_block
from extract_authored_pack import attach_adaptation_profile, literal
from source_registry import verify

def sha(data): return hashlib.sha256(data).hexdigest()
def require(ok, why):
    if not ok: raise ValueError(why)
def replace(text, old, new):
    require(text.count(old) == 1, 'Reviewed port changed: ' + old[:90])
    return text.replace(old, new)
def write(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def ports(texts):
    lib = replace(texts['lib.js'], 'const $ = id => document.getElementById(id);', 'const $ = id => nodes[id];')
    lib = replace(lib, 'const SFX = []; window.SFX = SFX;', 'const SFX = [];')
    lib = replace(lib, 'window.imgWait = () => Promise.all([..._pending].map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; }))).then(() => _pending.clear());', '')
    lib = replace(lib, 'function setFrame(imgEl, src) { if (imgEl._src !== src) { imgEl._src = src; imgEl.src = src; _pending.add(imgEl); } }', 'function setFrame(imgEl, src) { OUTPUT_FRAME(imgEl, src); }')
    lib = replace(lib, 'const talkSrc = t => {', 'const talkSrc = t => { t = window.MACRO_OUTPUT_T ?? t;')
    lib = replace(lib, 'function faceAt(t) {', 'function faceAt(t) { t = window.MACRO_OUTPUT_T ?? t;')
    core = texts['core.js']
    core = re.sub(r'^/\* core\.js[\s\S]*?\*/', '/* Native portrait style helpers. */', core, count=1)
    core = replace(core, 'REC · 阿杜 · 真人', '${window.PACK_PRESENTER_LABEL}')
    core = replace(core, 'ADUNEXT — REAL HUMAN ’26', '${window.PACK_BRAND_HTML}')
    core = replace(core, 'HUD.tc.textContent = tc(t);', 'HUD.tc.textContent = OUTPUT_TC(window.MACRO_OUTPUT_T);')
    core = replace(core, 't / (window.END || CONFIG.end)', 'window.MACRO_OUTPUT_T / (window.END || CONFIG.end)')
    core = replace(core, 'const voxAt = t => VOX[clamp(Math.floor(t * 60), 0, VOX.length - 1)] || 0;', 'const voxAt = () => 0; // these groups never use the source voice envelope')
    # No selected unit uses source video sequences. Fail closed if one is added.
    core = re.sub(r'const NF = [^\n]+;', 'const NF = {};', core, count=1)
    core = replace(core, 'assets/img/noise.png', 'assets/noise.png')
    core = replace(core, '1080×1920 · 60P · 98 BPM&nbsp;', '1080×1920 · 60P&nbsp;')
    main = texts['main.js'].split('(function () {', 1)[1].split('  window.READY =', 1)[0]
    main = replace(main, 'const lbT = lb.querySelector', "lb.style.display = 'none'; // unused source opening matte\n  const lbT = lb.querySelector")
    main = replace(main, 'window.renderAt = function (t) {', 'const drawAt = function (t) {')
    main = replace(main, 'tkUpdate(t); trans(t); letterbox(t); hudUpdate(t);', 'tkUpdate(t); hudUpdate(t);')
    main = replace(main, 'fade.style.opacity = clamp((t - (E - .7)) / .65).toFixed(3);', "fade.style.opacity = '0'; // output host owns the final fade")
    main = replace(main, 'if (window.OVERLAY) window.OVERLAY(t);', '// output host owns new subtitles')
    return lib, core, main

def wrap(raw, spec, inventory, texts):
    start, end = raw['source']['start'], raw['source']['end']
    before = [k for k in inventory['talkKeys'] if k['at'] < start]
    initial = spec['adapter']['initialTalkKey']
    require(before and initial.strip() == before[-1]['source'].strip(), 'Review the actual preceding presenter state')
    statement = raw['statement']
    require(not re.search(r'\b(frameSrc|clipAt|cutout|lwin|voxAt|TK_FX|WALL)\b', statement), 'This group needs a separate media/filter adapter')
    lib, core, main = ports(texts)
    # Source pose is a local initial state, never inherited from a new neighbour.
    prefix = f'''((OUTPUT_SCENE,OUTPUT_FRAME,OUTPUT_TC,FORWARD_S)=>{{
const outer=new OUTPUT_SCENE({start!r},{end!r},'#0A0A0C',{{}});
const host=document.createElement('div');host.className='vibrant-host';host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML='<div data-vibrant-node="world"></div><div data-vibrant-node="tk"></div><div data-vibrant-node="front"></div><div data-vibrant-node="fx"></div><div data-vibrant-node="hud"></div><div data-vibrant-node="ov" style="position:absolute;inset:0;pointer-events:none"></div>';
const nodes=Object.fromEntries([...host.querySelectorAll('[data-vibrant-node]')].map(e=>[e.dataset.vibrantNode,e]));nodes.stage=host;
{texts['beats.js']}
{lib}
{core}
const SUBPOS=[];
tkKey({start!r},(()=>{{const privateKeys=[];const tkKey=(t,L,d)=>privateKeys.push({{L}});{initial}return privateKeys[0].L;}})(),.01);
'''
    # Seed with the last reviewed pose. Original current-group tkKeys interpolate
    # against it; the future neighbour does not become a hidden input.
    prefix = prefix.replace(f'tkKey({start!r},', f'tkKey({start-2!r},', 1)
    body = prefix + statement + '\n' + main + '\n' + (HERE/'bridge.js').read_text()
    body += f'''
outer.opt={{...SCENES[0].opt}};let lastSource=outer.s;
outer.update=t=>{{lastSource=t;drawAt(t);window.VIBRANT_FIT(host,'{spec['id']}');}};
outer.macroTransition=context=>vibrantTransition({{wipe,circ,flash,world:nodes.world}},FLASH,lastSource,{{...context,scene:outer}});
SFX.forEach(c=>{{const {{t,type,g,p,...extra}}=c;FORWARD_S(t,type,g,p,extra);}});
outer.vibrantDiagnostics={{sourceScenes:SCENES.length,sourceSfx:SFX.length,clock:'source-geometry/output-presenter',initialPose:TKK[0].L}};
}})(Scene,setFrame,tc,S);
'''
    contract = deepcopy(spec['contract']); occupied=[]
    for slot in contract['slots']:
        if slot['type'] not in ('text','dynamicText'): continue
        matches = [m for m in re.finditer(re.escape(slot['sourceText']), statement)
                   if not any(m.start()<b and a<m.end() for a,b in occupied)]
        require(matches, 'Reviewed text missing: '+slot['id'])
        occupied += [(m.start(),m.end()) for m in matches]
        slot['sourceSpans']=[dict(start=len(prefix)+m.start(),end=len(prefix)+m.end(),renderContext=slot.get('renderContext','html')) for m in matches]
    contract['slots'] += [dict(id='presenter',type='talk',required=True),dict(id='grainTexture',type='image',inputPath='grainTexture',required=True,sourceAsset='assets/noise.png')]
    return body, {**contract,'id':spec['id'],'source':raw['source'],'sourceCodeFile':f"units/{spec['id']}.js",'sourceBlockSha256':sha(body.encode()),'requiresFaceTracking':True,
        'provenance':dict(adapter='adapters/vibrant-color/extract.py',adapterSha256=sha(Path(__file__).read_bytes()),sourceFile='scenes.js',sourceLines=raw['sourceLines'],sourceStatementSha256=raw['sourceStatementSha256'],initialTalkKey=initial,
        ports=['native portrait private DOM/Canvas state','output-clock narration/face/HUD progress','source-clock choreography and beat pulse','source-native vertical wipe/wipex/circle/flash','once-only SFX forwarding','explicit texture/fonts'])}

def score(text, duration, groups):
    values={}
    for n in ast.parse(text).body:
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Name) and t.id in ('CUTS','CLIMAX','DIP','HITS'): values[t.id]=literal(n.value,duration)
    require(set(values)=={'CUTS','CLIMAX','DIP','HITS'},'Reviewed score descriptors missing')
    # Freeze the actual piecewise source envelope without executing audio.py or
    # copying its private path/commercial recording/loop recipe.
    def env(t):
        import math
        v=-5.5 if t>4.6 else 1.5
        for c in values['CUTS']:
            x=(t-(c-.3))/.9
            if 0<=x<=1:v=max(v,-5.5+4*math.sin(math.pi*x))
        for a,b,g in values['CLIMAX']:
            if a-.1<=t<=b:v=max(v,-5.5+g+(4 if g>=3 else 2))
        for a,b,g in values['DIP']:
            if a<=t<=b:v+=g
        return 2 if t>=146.4 else v
    return dict(schema='adu-authored-score/1',sourceSha256=sha(text.encode()),SEC=[dict(id=g['id'],start=g['source']['start'],end=g['source']['end'],mode='synth',energy=.25,options=dict(kick_on=False,clapon=False)) for g in groups],ENV=[dict(at=round(i*.05,3),db=env(i*.05)) for i in range(round(duration/.05)+1)]+[dict(at=t,db=-5.5) for g in groups if g['source']['start']>duration for t in (g['source']['start'],g['source']['end'])],HITS=values['HITS'],DARK=[],sfxEvents=[],mix=dict(profile='opus-five-v1'),limits=['Default synthesized bed replaces the excluded source recording. Visual source beats remain authored; supplied music needs beat review.'])

def extract(record, proposal_path, output):
    proposal=json.loads(proposal_path.read_text());source=json.loads((record/'source.json').read_text())
    require(not output.exists() and output.parent.is_dir(),'Use a fresh pack path')
    require(proposal['sourceRevision']==source['revision'],'Source revision changed')
    require(verify(record)['verified'],'Frozen source verification failed')
    texts={}
    for name,expected in proposal['sourceFiles'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Source path escaped')
        data=(record/'snapshot'/name).read_bytes()
        require(sha(data)==expected==source['sourceFiles'][name]['sha256'],'Source SHA changed: '+name);texts[name]=data.decode()
    require({'lib.js','core.js','main.js','scenes.js','beats.js','audio.py','style.css','config.js','index.html'}<=texts.keys(),'Pin every runtime source')
    with tempfile.TemporaryDirectory(prefix='adu-vibrant-extract-') as tmp:
        temp=Path(tmp);subprocess.run(['node',str(HERE/'inventory.mjs'),str(record/'snapshot/scenes.js'),str(temp/'inventory.json')],check=True,capture_output=True)
        inventory=json.loads((temp/'inventory.json').read_text());stage=temp/'pack';(stage/'units').mkdir(parents=True);scenes=[]
        for spec in proposal['units']:
            require(re.fullmatch(r'[a-z][a-z0-9-]{0,63}',spec['id']),'Invalid group id')
            raw=inventory['units'][spec['index']]
            require(raw['sourceStatementSha256']==spec['expectedStatementSha256'],'Statement SHA changed')
            body,sc=wrap(raw,spec,inventory,texts);sc['sourceRevision']=source['revision']
            bind_authored_block(body,{**sc,'slots':[{**s,'mustChange':False} for s in sc['slots']]},{s['id']:s['sourceText'] for s in sc['slots'] if s['type'] in ('text','dynamicText')},sc['id'])
            (stage/sc['sourceCodeFile']).write_text(body);scenes.append(sc)
        extension = proposal.get('extension')
        if extension:
            path = HERE / extension['file']
            require(path.parent == HERE and sha(path.read_bytes()) == extension['sha256'], 'Authored extension SHA changed')
            subprocess.run(['node',str(HERE/'inventory.mjs'),str(path),str(temp/'extension.json')],check=True,capture_output=True)
            inv = json.loads((temp/'extension.json').read_text())
            for spec in extension['units']:
                raw=inv['units'][spec['index']]
                require(raw['sourceStatementSha256']==spec['expectedStatementSha256'],'Authored extension statement changed')
                body,sc=wrap(raw,spec,inv,texts);sc['sourceRevision']=source['revision']
                sc['provenance'].update(origin='newly-authored-style-extension',sourceFile='adapters/vibrant-color/'+extension['file'])
                bind_authored_block(body,{**sc,'slots':[{**s,'mustChange':False} for s in sc['slots']]},{s['id']:s['sourceText'] for s in sc['slots'] if s['type'] in ('text','dynamicText')},sc['id'])
                (stage/sc['sourceCodeFile']).write_text(body);scenes.append(sc)
        fonts=[];rules=[]
        for name,meta in source['mediaFiles'].items():
            match=re.fullmatch(r'fonts/(?:(Geist|GeistMono)-normal-(400|500|600|700|800)|Anton-(400))\.woff2',name)
            if not match:continue
            base,weight,anton=match.groups()
            if not anton and (base!='GeistMono' or weight not in ('500','600')):continue
            family='Anton' if anton else 'Geist Mono' if base=='GeistMono' else 'Geist';weight=anton or weight
            fid=family.lower().replace(' ','-')+'-'+weight
            fonts.append(dict(id=fid,family=family,weight=int(weight),sha256=meta['sha256'],format='woff2',extension='.woff2',required=True,sourceFile=name,distribution='owner-supplied; not bundled'))
            rules.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};src:url(fonts/{fid}.woff2) format('woff2')}}")
        require(len(fonts)==3,'Reviewed Anton/Geist font set changed')
        css=[]
        for selectors,declarations in re.findall(r'([^{}]+)\{([^{}]*)\}',texts['style.css']):
            mapped=[]
            for selector in selectors.split(','):
                s=selector.strip()
                if s in ('html','body',':root','#stage'):mapped.append('.vibrant-host')
                else:mapped.append('.vibrant-host '+re.sub(r'#([\w-]+)',r'[data-vibrant-node="\1"]',s))
            css.append(','.join(mapped)+'{'+declarations+'}')
        (stage/'style.css').write_text('\n'.join(rules)+'\nhtml,body,#stage{width:1080px;height:1920px;overflow:hidden;margin:0;background:#000}\n#stage{position:relative}#world,#fx{position:absolute;inset:0;transform-origin:540px 960px}.sc{position:absolute;inset:0;display:none;overflow:hidden}\n'+'\n'.join(css))
        lib=(ROOT/'packs/classic-performance/1.0.0/lib.js').read_text()
        lib=replace(lib,'AduNext&nbsp;&nbsp;',"${window.PACK_BRAND_HTML || ''}&nbsp;&nbsp;")
        lib=replace(lib,"label = '// on air · 阿杜'", "label = '// on air · ' + (CONFIG.account || 'Presenter')")
        (stage/'lib.js').write_text(lib)
        (stage/'config.js').write_text('window.CONFIG={brand:"",account:"",repoUrl:"",fps:60,width:1080,height:1920,end:0,talkFrames:0,subtitles:false,race:{labels:["start","end"],keys:[0,1,2]}};\n')
        for name in ('portrait.js','typography.js'):shutil.copy2(HERE/name,stage/name)
        write(stage/'audio_timeline.json',score(texts['audio.py'],proposal['sourceDuration'],scenes))
        shutil.copy2(HERE/'pack-readme.md',stage/'README.md')
        manifest=dict(id=proposal['id'],version=proposal['version'],title=proposal['title'],status='candidate',sourceFormat='authored-unit/1',sourceRevision=source['revision'],source=dict(engine='native-portrait DOM/Canvas/private-source-host',assetPolicy='Private media and commercial recording excluded; bind new narration, texture and fonts.'),fps=60,width=1080,height=1920,requireMotionWindows=True,runtimeFiles=['typography.js'],layouts=dict(portrait=dict(width=1080,height=1920,runtime='portrait.js',status='candidate')),runtimeHooks=['macroTransition/1'],scenes=scenes,assetDefinitions={},externalFonts=fonts,environment=dict(platform='Windows/WSL, macOS, Linux; executable assistant and licensed CJK font required',systemFonts=['PingFang SC or owner-specified CJK font'],format='1080x1920/60'),validation=dict(sourceReplay='pending',newContent='pending',independentUse='pending'),files={p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()})
        attach_adaptation_profile(manifest,proposal['adaptationProfile']);write(stage/'manifest.json',manifest);shutil.copytree(stage,output)
    return dict(pack=manifest['id'],version=manifest['version'],units=len(scenes),status='candidate',path=str(output))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('record',type=Path);p.add_argument('proposal',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    print(json.dumps(extract(a.record.resolve(),a.proposal.resolve(),a.output.resolve()),ensure_ascii=False))

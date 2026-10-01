#!/usr/bin/env python3
"""Normalize one reviewed inline DOM performance; not a general HTML compiler.

The exact frozen source revision guards every range. The adapter wraps the
source's balance, value, illustration, handwritten note, presenter and ball
handoff in the existing Scene host. It never executes the source during intake.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from source_registry import verify
from build_macro_project import bind_authored_block

REVISION = '279ffaa155c59ae35940c31fa09b9d85c960c2148a20368f146563fc70069d4b'
ENTRY_SHA = '4f14cbd5178d5a0f25cfed8afbc920711c68d9e56dadc3e3c67700c654df8062'
FONTS = {
    'Anton.woff2': 'fbe5c43983d4a583cd9c760a5c124451505dad21d9a74cd2ae957fd3f7358ac4',
    'Caveat.woff2': '594b089a80408340296b9ef2f5b589c8c752d1021994ab4707b202462a42249b',
    'Geist-normal-500.woff2': '0c855f7567881c1f3c41738616d4274cea4afbd2bf6aa198be467aefc157ee6d',
    'Geist-normal-700.woff2': '0c855f7567881c1f3c41738616d4274cea4afbd2bf6aa198be467aefc157ee6d',
    'GeistMono-normal-500.woff2': '5f3d6ad60f29d6cb708414ec6887163d63bf197377ef5417d2483ff31ace6c3b',
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def extract(record: Path, output: Path, version: str = '0.1.6-candidate') -> dict:
    if not re.fullmatch(r'\d+\.\d+\.\d+-candidate', version):
        raise ValueError('Choose an explicit candidate semantic version')
    if output.exists() or not output.parent.is_dir():
        raise ValueError('Output must be fresh and its parent must exist')
    source = json.loads((record / 'source.json').read_text())
    if source['revision'] != REVISION:
        raise ValueError('This adapter supports only its reviewed source revision')
    checked = verify(record)
    if not checked['verified']:
        raise ValueError('Frozen source verification failed')
    entry = record / 'snapshot/index.html'
    text = entry.read_text()
    if sha(entry.read_bytes()) != ENTRY_SHA:
        raise ValueError('Source entry differs from the reviewed inline renderer')
    ranges = []

    def segment(a: str, b: str, name: str) -> str:
        if text.count(a) != 1 or text.count(b) != 1:
            raise ValueError(f'{name}: reviewed source range is ambiguous')
        start, end = text.index(a), text.index(b)
        if start >= end:
            raise ValueError(f'{name}: source range is reversed')
        raw = text[start:end]
        ranges.append({'id': name, 'sourceFile': 'index.html', 'startCodepoint': start,
                       'endCodepoint': end, 'sha256': sha(raw.encode()),
                       'sourceLines': [text.count('\n', 0, start) + 1,
                                       text.count('\n', 0, end) + 1]})
        return raw

    core = segment("const INK =", "const $ =", 'colors-and-easing')
    helpers = segment("const P3 =", "const gen =", 'source-transform-functions')
    ink = segment("const SVGNS =", "// ======================= 背景/明暗", 'annotation-functions')
    camera = segment("const camE =", "function faceAt(t)", 'presenter-and-pose-keys')
    camera += segment("function drawCam(t)", "// ======================= 主线小球", 'presenter-draw')
    camera = camera.replace('fr(\'talk\', t * 30 + 1, 4131)', 'talkSrc(window.MACRO_OUTPUT_T ?? t)')
    camera = camera.replace('const f = faceAt(t),', 'const f = faceAt(window.MACRO_OUTPUT_T ?? t),')
    ball = segment("const ball =", "// ======================= A ·", 'ball-and-trail')
    elements = segment("const bQ =", "// ======================= C ·", 'balance-value-and-recap-elements')
    original_asset = "const bMirror = gen('mirror', 560);"
    if elements.count(original_asset) != 1:
        raise ValueError('Reviewed illustration call changed')
    # Make the existing generated sprite an explicit required input. The same
    # wrapper, height, shadow and P3 transform are retained.
    elements = elements.replace(original_asset, '''const bMirror = mk('world', `<div class="o"><img src="assets/mirror_cut.png" style="height:560px;display:block;filter:drop-shadow(0 24px 30px rgba(0,0,0,.14))"></div>`); imgs.push(bMirror.querySelector('img')); bMirror.style.display = 'none';''')
    motion = segment("  // ---------- B ----------", "  // ---------- C ----------", 'balance-value-and-recap-motion')
    wrapper = '''(() => {
const A=13.73,Z=25.57,sc=new Scene(A,Z,'#F4F2EC',{});
const host=document.createElement('div');host.className='nd-host';host.style.cssText='position:absolute;inset:0;overflow:hidden';sc.el.appendChild(host);
const nodes={};
for(const [id,cls,style] of [['paper','nd-paper','position:absolute;inset:0'],['dark','nd-dark','position:absolute;inset:0'],['cam','nd-camera','position:absolute;inset:0;perspective:1600px'],['ov','ov','position:absolute;inset:0'],['flash','ov','position:absolute;inset:0;background:#fff;opacity:0;z-index:15']]){const e=document.createElement('div');e.className=cls;e.style.cssText=style;host.appendChild(e);nodes[id]=e;}
const world=document.createElement('div');world.className='nd-world';world.style.cssText='position:absolute;left:960px;top:540px;width:0;height:0;transform-style:preserve-3d';nodes.cam.appendChild(world);nodes.world=world;
const inkRoot=document.createElementNS('http://www.w3.org/2000/svg','svg');inkRoot.setAttribute('width',1920);inkRoot.setAttribute('height',1080);inkRoot.style.cssText='position:absolute;left:0;top:0;z-index:5';host.insertBefore(inkRoot,nodes.flash);nodes.ink=inkRoot;
const $=id=>nodes[id];
const mk=(par,html)=>{const d=document.createElement('div');d.innerHTML=html.trim();const e=d.firstElementChild;(typeof par==='string'?$(par):par).appendChild(e);return e;};
const imgs=[];const setSrc=(im,s)=>{if(im._s!==s){im._s=s;im.src=s;}};
const TALK_END=137.77,END=143.5;
'''
    # The preceding chapter's flash still releases after this group's first
    # frame. Retain that boundary state without instantiating its old content.
    dark = "const DARK=[[11.37,13.73],[23.43,25.57]];const darkK=t=>Math.max(...DARK.map(([a,b])=>Math.min(pr(t,a-.04,a+.06),1-pr(t,b-.12,b))),0);\n"
    body = wrapper + core + helpers + ink + dark + camera + ball + elements
    body += '''sc.update=t=>{
 const dk=darkK(t);$('dark').style.opacity=dk;
 $('world').style.transform=`rotateY(${Math.sin(t*.23)*1.5}deg)`;
 $('ov').style.transform='translate(0px,0px)';
 $('flash').style.opacity=Math.max(...DARK.map(([a,b])=>t>b-.05?.5*(1-pr(t,b-.05,b+.25)):0));
 drawCam(t);drawBall(t);
'''+motion+'''};
// Complete source action cues, including the recap's three confirmations.
[[13.7,'whoosh',.6],[13.8,'swoosh',.4],[14.5,'pop',.4],[15.4,'creak',.4,0,{d:.6}],[16.9,'creak',.4,0,{d:.6}],[17.7,'hit',.7],[20.6,'pop',.5],[21.3,'write',.5,0,{d:.7}],[23.45,'hit',.9],[23.6,'check',.6,0,{n:0}],[24.1,'check',.6,0,{n:1}],[24.6,'check',.6,0,{n:2}]].forEach(a=>S(a[0],a[1],a[2],a[3]||0,a[4]||{}));
})();
'''
    slots = []

    def bind(key: str, old: str, field: str, capacity: int, *, context='html') -> None:
        spans = [{'start': m.start(), 'end': m.end(), 'renderContext': context}
                 for m in re.finditer(re.escape(old), body)]
        if not spans:
            raise ValueError(f'Missing reviewed string: {key}')
        slots.append({'id': key, 'type': 'text', 'sourceText': old, 'sourceSpans': spans,
                      'maxChars': capacity, 'required': True, 'mustChange': True,
                      'renderContext': context, 'inputPath': field})

    bind('presenter', 'on air · 阿杜Next', 'presenterLabel', 20)
    bind('context', 'Q · 很多人问', 'context', 18)
    for i, field in enumerate(['opposition.leftLead','opposition.rightLead']):
        starts=[m.start()+1 for m in re.finditer(re.escape('>一边<span'),body)]
        if len(starts)!=2:raise ValueError('Question lead spans changed')
        slots.append({'id':f'lead-{i}','type':'text','sourceText':'一边',
                      'sourceSpans':[{'start':starts[i],'end':starts[i]+2,'renderContext':'html'}],
                      'maxChars':3,'required':True,'mustChange':True,'renderContext':'html','inputPath':field})
    bind('left', '吐槽', 'opposition.left', 4)
    bind('subject', 'OpenAI', 'opposition.subject', 6)
    bind('right', '还在用', 'opposition.right', 4)
    # The scale's right label is a separate occurrence of the same semantic idea.
    bind('right-scale', '在用', 'opposition.rightShort', 4)
    # Avoid overlapping bindings in the question's 还在用 occurrence.
    right_span = slots[-2]['sourceSpans'][0]
    slots[-1]['sourceSpans'] = [s for s in slots[-1]['sourceSpans']
                               if not right_span['start'] <= s['start'] < right_span['end']]
    bind('heading', 'PRODUCTIVITY', 'value.heading', 12)
    bind('lead', '它是', 'value.lead', 3)
    bind('value', '生产力工具', 'value.label', 8)
    bind('annotation', '学它 → 复刻它', 'annotation', 12)
    # Step labels are JS string values inserted by the unchanged source map.
    for i, old in enumerate(['用它', '学它', '复刻它']):
        spans = [{'start': m.start()+1, 'end': m.end()-1, 'renderContext': 'html'}
                 for m in re.finditer(re.escape("'"+old+"'"), body)]
        slots.append({'id': f'step-{i}', 'type': 'text', 'sourceText': old,
                      'sourceSpans': spans, 'maxChars': 4, 'required': True,
                      'mustChange': True, 'renderContext': 'html', 'inputPath': f'steps.{i}.label'})
    bind('step-summary', 'USE · LEARN · REPLICATE', 'stepSummary', 34)
    slots.append({'id': 'illustration', 'type': 'image', 'sourceAsset': 'assets/mirror_cut.png',
                  'required': True, 'inputPath': 'illustration',
                  'purpose': 'transparent symbolic illustration supporting the same subject; not evidence'})
    example = {'presenterLabel':'on air · 本期讲述者','context':'Q · 本期问题',
               'opposition':{'leftLead':'继续','left':'分享','subject':'项目','rightLead':'同时','right':'经营','rightShort':'经营'},
               'value':{'heading':'VALUE','lead':'先看','label':'真实需求'},
               'annotation':'接触 → 验证 → 打磨','steps':[{'label':'接触'},{'label':'验证'},{'label':'打磨'}],
               'stepSummary':'CONTACT · VALIDATE · REFINE','illustration':''}
    scene = {'id':'apparent-tension-to-value','role':'表面矛盾 → 实际用途 → 可执行三步',
             'source':{'start':13.73,'end':25.57},'sourceCodeFile':'units/apparent-tension-to-value.js',
             'sourceBlockSha256':sha(body.encode()),'sourceRevision':REVISION,
             'requiresFaceTracking':True,'minFrames':710,'maxHoldFrames':360,
             'motionWindows':[{'start':13.73,'end':14.9},{'start':15.4,'end':17.6},
                              {'start':17.7,'end':18.1},{'start':19.7,'end':20.1},
                              {'start':20.6,'end':21.0},{'start':21.3,'end':22.0},
                              {'start':23.43,'end':25.57}],
             'cues':[{'id':'value','at':17.7,'kind':'semantic','required':True},
                     {'id':'illustration','at':20.6,'kind':'semantic','required':True},
                     {'id':'steps','at':23.43,'kind':'semantic','required':True}],
             'slots':slots,'inputExample':example,
             'boundaries':{'entry':'retains source presenter return, question and balance entrance',
                           'exit':'includes all three recap confirmations, ball trail and release',
                           'connection':'self-contained continuation; other connections unverified',
                           'openingPresenterDelaySeconds':.37},
             'limits':['Not for two unrelated subjects or a factual comparison with measured values.',
                       'The opening has a source-authored 0.37s presenter return, not a title-card opening.',
                       'The illustration is symbolic; real proof needs another evidence group.',
                       'The source 25.55s whoosh belongs to the next group and is excluded from this standalone group.',
                       'Source music track is private; a new full-length track or the declared synth alternative is required.',
                       'Output-clock captions remain visible beneath the recap; the original suppressed captions in dark chapters.'],
             'provenance':{'sourceFile':'index.html','sourceEntrySha256':ENTRY_SHA,'ranges':ranges,
                           'adapter':'adapters/paper-balance/extract.py','adapterSha256':sha(Path(__file__).read_bytes()),
                           'ports':['Scene host and scoped layer IDs','presenter pixels and crop use output clock',
                                    'generated sprite becomes required image input',
                                    'source shake is zero throughout this protected interval']}}
    # Span validation happens before any deliverable is created.
    values={s['id']:s['sourceText'] for s in slots if s['type']=='text'}
    bind_authored_block(body,{**scene,'slots':[{**s,'mustChange':False} for s in slots]},values,scene['id'])
    css = re.search(r'<style>([\s\S]*?)</style>', text).group(1)
    origin = Path(source['origin'])
    font_meta=[]
    for name, expected in FONTS.items():
        data=(origin/'fonts'/name).read_bytes()
        if sha(data)!=expected:raise ValueError(f'Font changed: {name}')
        css=css.replace('fonts/'+name,'data:font/woff2;base64,'+base64.b64encode(data).decode())
        font_meta.append({'sourceFile':name,'sha256':expected,'license':'SIL-OFL-1.1',
                          'storage':'unmodified source WOFF2 embedded in CSS'})
    css=re.sub(r'#subs[^}]*}', '', css)
    for a,b in [('#paper','.nd-paper'),('#dark','.nd-dark'),('#cam','.nd-camera'),('#world','.nd-world'),('#ink','.nd-ink')]:
        css=css.replace(a,b)
    # Keep the existing output host and caption layer; source layers live inside it.
    css=css.replace('#stage{', '.nd-host{')
    css += '''\n/* Source caption geometry stays below the source portrait card. */
.sz{padding:0 26px!important;line-height:1.22!important;-webkit-text-stroke:7px rgba(14,15,16,.95)!important}
.se{padding:0 20px!important;line-height:normal!important;font-family:Geist,-apple-system,sans-serif!important;letter-spacing:normal!important;-webkit-text-stroke:4.5px rgba(14,15,16,.92)!important}
'''
    # The generated project copies this CSS, so its embedded font bytes travel
    # with their human-readable copyright and license notices as OFL requires.
    notice_paths=[Path(__file__).parent/'licenses'/f'OFL-{family}.txt' for family in ['anton','caveat','geist','geistmono']]
    notices='\n'.join(p.read_text() for p in notice_paths)
    if '*/' in notices:raise ValueError('License notice cannot be embedded safely in a CSS comment')
    css='/* Embedded font copyright and license notices\n'+notices+'\n*/\n'+css
    core_pack=ROOT/'packs/classic-performance/0.2.1-candidate'
    core_manifest=json.loads((core_pack/'manifest.json').read_text())
    for name in ['lib.js','config.js']:
        if sha((core_pack/name).read_bytes())!=core_manifest['files'][name]:
            raise ValueError(f'Frozen host helper changed: {name}')
    with tempfile.TemporaryDirectory(prefix='adu-inline-pack-') as tmp:
        stage=Path(tmp)/'pack';(stage/'units').mkdir(parents=True);(stage/'licenses').mkdir()
        (stage/scene['sourceCodeFile']).write_text(body)
        # Only the Scene host layout is shared. A's full style sheet would
        # leak its font smoothing, label backdrop filter and generic .e rules
        # into this different source contract.
        host_css = '#stage{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden}\n#world,#fx{position:absolute;inset:0}\n#fx{pointer-events:none}\n.sc{position:absolute;inset:0;overflow:hidden;display:none}\n'
        (stage/'style.css').write_text(host_css+css)
        for name in ['lib.js','config.js']:
            shutil.copy2(core_pack/name,stage/name)
        with (stage/'config.js').open('a') as f:
            f.write('\nCONFIG.subtitleStyle={top:948,gap:6,zhSize:42,enSize:27,compact:true};\n')
        for license in (Path(__file__).parent/'licenses').glob('OFL-*.txt'):
            shutil.copy2(license,stage/'licenses'/license.name)
        shutil.copy2(ROOT/'LICENSE',stage/'LICENSE')
        (stage/'README.md').write_text((Path(__file__).parent/'pack-readme.md').read_text().replace('{PACK_VERSION}',version))
        # Synth alternative is deliberate and distinct from the owner's music.
        # All action SFX retain source types, gains, pan and event durations.
        audio={'schema':'adu-authored-score/1','SEC':[
                    {'id':'tension','start':13.73,'end':23.43,'mode':'synth','energy':.3,'options':{'kick_on':False,'clapon':False}},
                    {'id':'steps','start':23.43,'end':25.57,'mode':'synth','energy':.65,'options':{}}],
               'ENV':[{'at':13.73,'db':-4},{'at':23.43,'db':-4},{'at':23.5,'db':-1},{'at':25.57,'db':-1}],
               'HITS':{},'DARK':[],'sfxEvents':[],
               'mix':{'profile':'opus-five-v1','fadeOutSourceStart':25.3,'fadeOutSeconds':.27},
               'limits':['Synth is a disclosed new-score alternative. The original external track is not bundled.',
                         'Provide music.mode=track with an explicit full-length owner track for source-like music.']}
        save(stage/'audio_timeline.json',audio)
        manifest={'id':'paper-balance','version':version,'status':'candidate',
                  'title':'纸面透视 · 矛盾转用途','sourceFormat':'authored-unit/1',
                  'sourceRevision':REVISION,'source':{'engine':'DOM/CSS perspective','assetPolicy':'Owner media are not bundled; bind a new symbolic illustration and narration.'},
                  'fps':60,'width':1920,'height':1080,'requireMotionWindows':True,
                  'runtimeFiles':[],'scenes':[scene],'assetDefinitions':{},
                  'environment':{'platform':'macOS','fonts':font_meta,'systemFonts':['PingFang SC','SFNSMono.ttf'],
                                 'runtimeBase':'classic-performance@0.2.1-candidate helpers; no A performance is imported'},
                  'validation':{'sourceReplay':'pending','newContent':'pending','independentUse':'pending'},
                  'files':{p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()}}
        save(stage/'manifest.json',manifest);shutil.copytree(stage,output)
    return {'pack':manifest['id'],'version':manifest['version'],'units':1,'path':str(output),'status':'candidate'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--version',default='0.1.6-candidate')
    args=parser.parse_args()
    try: print(json.dumps(extract(args.record.resolve(),args.output.resolve(),args.version),ensure_ascii=False))
    except (ValueError,OSError,KeyError) as exc:raise SystemExit(f'Inline pack extraction failed: {exc}') from exc

#!/usr/bin/env python3
"""Reviewed adapter for two groups in one custom scene()/Canvas source.

This is deliberately revision-specific. Source helpers, particle physics,
presenter poses and complete callback bodies stay together in each closure.
It is not a compiler for arbitrary source projects.
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

REVISION = '1d9087a4b3eb01c18a2e7960dfa2a2eaaa047257e03d5aebb6ca882fd063f753'
HASHES = {
    'index.html': '5782e0ba5628abf393703a1ff90be75ae93d29cfdb1b12e4f921e67443a3b4fa',
    'lib.js': '2f2012656793c7ae4e3710ddec2f9cfc52101603723f08703fe003ccb7c2f6f9',
    'scenes.js': '43d2ad3f706c5f867f9930be25386d946d160ce4fe6311e4219d582695064772',
    'main.js': '36f79194c1f202a204c0229b92a14eb3ce6472662991cdb74bbddb580f6cf09e',
}
FONT_SHA = 'dab883d69fb713233ea5d9aff8d1f27ccc2b71e249143edf6ea08367784c5dba'
REVIEWED_UNITS = {
    0: (4230, 5651, 'a886d6da829e45d431fa5703e0914c783b97b6e928fe6b60b91756523be6adf9'),
    13: (29942, 33140, '4174d9e57840b5a9d9a93a88b73dde00f22e8ee9d49392874d3da01ae06a66b2'),
    30: (64970, 69892, 'e60f7b988d35ba741f9517a8160e6354e47fe91835ac90541230f9496c319213'),
    31: (70086, 71537, 'ea8e60ef39661abb94dbb2aa62db8325dc0438fb25856878ab4366ef474848a1'),
}
GROUPS = [
    {'id': 'cards-to-network', 'indices': [13], 'start': 2429 / 60, 'end': 2726 / 60,
     'seed': 116, 'role': '六类资料 → 吸入聚合 → 网络 → 一句结论',
     'windows': [(2429 / 60, 44.9)], 'cues': [('network', 42.6), ('conclusion', 43.45)]},
    {'id': 'calendar-to-delivery', 'indices': [30, 31], 'start': 6950 / 60, 'end': 7626 / 60,
     'seed': 281, 'role': '七步日历 → 六类能力 → 开箱三项 → 内容交付堆叠',
     'windows': [(6950 / 60, 118.45), (118.6, 121.2), (121.9, 126.6)],
     'cues': [('capabilities', 118.85), ('unbox', 122.35), ('deliveries', 124.82)]},
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f'Reviewed adapter range changed: {old[:80]}')
    return text.replace(old, new)


def source_units(text: str, inventory: dict) -> list[str]:
    if inventory['sourceScenesSha256'] != HASHES['scenes.js'] or len(inventory['units']) != 35:
        raise ValueError('Reviewed AST inventory differs from the frozen source')
    for i, expected in REVIEWED_UNITS.items():
        unit = inventory['units'][i]
        actual = (unit['startCodepoint'], unit['endCodepoint'], unit['sha256'])
        if unit['index'] != i or actual != expected:
            raise ValueError('Reviewed AST selection changed')
    result = []
    for unit in inventory['units']:
        raw = text[unit['startCodepoint']:unit['endCodepoint']]
        if sha(raw.encode()) != unit['sha256']:
            raise ValueError('AST source range hash differs')
        result.append(raw)
    return result


def extract(record: Path, inventory_path: Path, output: Path, version='0.1.0-candidate') -> dict:
    if not re.fullmatch(r'\d+\.\d+\.\d+-candidate', version):
        raise ValueError('Use an explicit candidate semantic version')
    if output.exists() or not output.parent.is_dir():
        raise ValueError('Output must be fresh and its parent must exist')
    source = json.loads((record / 'source.json').read_text())
    if source['revision'] != REVISION:
        raise ValueError('This adapter supports only its reviewed source revision')
    if not verify(record)['verified']:
        raise ValueError('Frozen source verification failed')
    texts = {}
    for name, expected in HASHES.items():
        file = record / 'snapshot' / name
        if sha(file.read_bytes()) != expected:
            raise ValueError(f'Reviewed source changed: {name}')
        texts[name] = file.read_text()
    inventory = json.loads(inventory_path.read_text())
    units = source_units(texts['scenes.js'], inventory)
    for group, state in zip(GROUPS, inventory['runtime']['groups'], strict=True):
        if abs(state['start'] - (40.47 if group['seed'] == 116 else 115.83)) > 1e-8:
            raise ValueError('Source group inventory order differs')
        # Both source boundaries were reviewed: preceding effects end before
        # entry. A non-empty carry needs a newly reviewed adapter revision.
        if any(state['carry'].values()):
            raise ValueError('Boundary effects differ from reviewed empty carry')
        first = inventory['runtime']['scenes'][group['indices'][0]]
        if first['minimumId'] - 1 != group['seed']:
            raise ValueError('Source element seed differs')
    prelude = texts['scenes.js'][:inventory['units'][0]['startCodepoint']]
    source_lib = replace_once(texts['lib.js'], 'const $ = id => document.getElementById(id);',
                              'const $ = id => nodes[id];')
    source_lib = replace_once(source_lib, 'const SFX = []; window.SFX = SFX;', 'const SFX = [];')
    source_lib = replace_once(source_lib, 'im._s = s; im.src = s; PEND.add(im);',
                              'im._s = s; OUTPUT_FRAME(im, s); PEND.add(im);')
    # Binding text is JS escaped, and each visible glyph is HTML escaped here.
    # This changes string construction, not source character motion or timing.
    old = "for (const ch of [...txt]) html += ch === ' ' ? `<span class=\"${cls}\">&nbsp;</span>` : `<span class=\"${cls}\">${ch}</span>`;"
    new = "for (const ch of [...txt]) html += ch === ' ' ? `<span class=\"${cls}\">&nbsp;</span>` : `<span class=\"${cls}\">${ch.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span>`;"
    source_lib = replace_once(source_lib, old, new)
    main = texts['main.js'].split('window.renderAt = async t => {')[0]
    main = replace_once(main, 'window.END = 139.7;', '')
    start, end = main.index('function faceAt(t)'), main.index('function drawCam(t, dark)')
    main = main[:start] + main[end:]
    main = replace_once(main, "setSrc(camI, fr('talk', t * 30 + 1, TALK_N));",
                         'setSrc(camI, OUTPUT_TALK(window.MACRO_OUTPUT_T));')
    main = replace_once(main, 'const f = faceAt(t),', 'const f = OUTPUT_FACE(window.MACRO_OUTPUT_T),')
    main = main.replace("document.querySelector('#subs .z')", "nodes.subs.querySelector('.z')")
    main = main.replace("document.querySelector('#subs .e')", "nodes.subs.querySelector('.e')")
    main = replace_once(main, 'subs(t);', 'if(typeof SUBS!==\'undefined\'&&CONFIG.subtitles!==false) subs(window.MACRO_OUTPUT_T); else nodes.subs.style.opacity=0;')
    main = replace_once(main, 'AduNext&nbsp;&nbsp;${tc(t)}', '${window.PACK_BRAND_HTML}&nbsp;&nbsp;${OUTPUT_TC(window.MACRO_OUTPUT_T)}')
    html = texts['index.html'].split('<div id="stage">', 1)[1].split('<script src=', 1)[0]
    html = re.sub(r'id="([^"]+)"', r'data-pb-node="\1"', html)
    if not html.rstrip().endswith('</div>'):
        raise ValueError('Reviewed source host markup differs')
    # The final </div> belongs to source #stage, represented by the host.
    html = html.rstrip()[:-6]
    css = re.search(r'<style>([\s\S]*?)</style>', texts['index.html']).group(1)
    css = re.sub(r'@font-face\s*\{[^}]*\}', '', css)
    rules = []
    for selectors, declarations in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        selected = []
        for selector in selectors.split(','):
            selector = selector.strip()
            if selector in ('html', 'body'):
                continue
            if selector == '#stage':
                selected.append('.pb-host')
            else:
                selector = re.sub(r'#([A-Za-z0-9_]+)', r'[data-pb-node="\1"]', selector)
                selected.append('.pb-host ' + selector)
        if selected:
            rules.append(','.join(selected) + '{' + declarations + '}')
    css = '\n'.join(rules)
    font_css = []
    font_meta = []
    notices_dir = ROOT / 'adapters/paper-balance/licenses'
    baseline = json.loads((ROOT / 'packs/paper-balance/1.0.0/manifest.json').read_text())
    known = {x['sourceFile']: x['sha256'] for x in baseline['environment']['fonts']}
    for name in ['Anton.woff2','Caveat.woff2','Geist-normal-500.woff2','Geist-normal-700.woff2','GeistMono-normal-500.woff2']:
        data = (Path(source['origin']) / 'fonts' / name).read_bytes()
        if sha(data) != known[name]:
            raise ValueError(f'OFL source font differs: {name}')
        family = {'Anton.woff2':'Anton','Caveat.woff2':'Caveat','GeistMono-normal-500.woff2':'Geist Mono'}.get(name,'Geist')
        weight = '400 700' if family == 'Caveat' else '700' if '-700' in name else '500' if family in ('Geist','Geist Mono') else '400'
        font_css.append(f"@font-face{{font-family:'{family}';font-weight:{weight};src:url(data:font/woff2;base64,{base64.b64encode(data).decode()})}}")
        font_meta.append({'sourceFile':name,'sha256':sha(data),'license':'SIL-OFL-1.1','storage':'embedded-unmodified'})
    notices = '\n'.join(p.read_text() for p in sorted(notices_dir.glob('OFL-*.txt')))
    css = '/* Embedded font copyright and OFL notices\n' + notices + '\n*/\n' + '\n'.join(font_css) + '\n' + css
    css = '#stage,#world,#fx{position:absolute;inset:0;width:1920px;height:1080px;overflow:hidden}\n.sc{position:absolute;inset:0;display:none;overflow:hidden}\n#ov{display:none}\n' + css
    scenes = []
    bodies = []
    for group in GROUPS:
        start, end = group['start'], group['end']
        raw = '\n'.join(units[i] for i in group['indices'])
        adapted = raw.replace('kinBox(k, 0, 5)', "kinBox(k, 0, k._c.filter(c=>!c.classList.contains('kdot')).length-1)")
        body = '''((OUTPUT_TALK,OUTPUT_FACE,OUTPUT_TC,FORWARD_S,OUTPUT_FRAME) => {
const outer=new Scene(START,END,'#1B2220',{});
const host=document.createElement('div');host.className='pb-host';host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML=MARKUP;
const nodes=Object.fromEntries([...host.querySelectorAll('[data-pb-node]')].map(e=>[e.dataset.pbNode,e]));
'''.replace('START',repr(start)).replace('END',repr(end)).replace('MARKUP',json.dumps(html,ensure_ascii=False))
        body += source_lib + f'\n_id={group["seed"]};\n' + prelude + adapted + '\n' + main
        body += f'''\nSFX.filter(c=>c.t>={start}-.02&&c.t<{end}).forEach(c=>{{const {{t,type,g,p,...x}}=c;FORWARD_S(t,type,g,p,x);}});
outer.update=t=>drawAt(t);
}})(talkSrc,faceAt,tc,S,setFrame);
'''
        slots = []
        unit_start = body.index(adapted)
        unit_end = unit_start + len(adapted)

        def bind(key, old, field, cap, *, context='html', occurrence=None):
            matches = list(re.finditer(re.escape(old),body))
            if key != 'presenter':
                matches = [m for m in matches if unit_start <= m.start() and m.end() <= unit_end]
            occupied = [span for slot in slots for span in slot.get('sourceSpans', [])]
            matches = [m for m in matches if not any(m.start()<s['end'] and s['start']<m.end() for s in occupied)]
            if occurrence is not None:
                matches = matches[occurrence:occurrence+1]
            if not matches:
                raise ValueError(f'Missing reviewed field {field}')
            slots.append({'id':key,'type':'text','sourceText':old,'sourceSpans':[{'start':m.start(),'end':m.end(),'renderContext':context} for m in matches],
                          'maxChars':cap,'required':True,'mustChange':True,'inputPath':field})

        bind('presenter','on air · 阿杜Next','presenterLabel',24)
        if group['id'] == 'cards-to-network':
            bind('chapter','// 05 — 你的数据去哪了','chapter',28,context='text')
            for i,(old,icon) in enumerate([('聊天记录','💬'),('上传的文件','PDF'),('代码仓库','</>'),('照片','IMG'),('语音','•ılı•'),('工作文档','DOC')]):
                bind(f'card-{i}',old,f'cards.{i}.label',5)
                bind(f'icon-{i}',icon,f'cards.{i}.icon',5,occurrence=0)
            bind('input-label','你的数据 →','inputLabel',12)
            bind('output-label','→ 训练模型','outputLabel',12)
            bind('conclusion','根本不用怀疑','conclusion',6,context='text')
            example={'presenterLabel':'on air · 本期讲述者','chapter':'01 — 从素材到方法','cards':[{'label':s,'icon':c} for s,c in [('原始记录','RAW'),('成片画面','VID'),('镜头代码','JS'),('对白字幕','TXT'),('动作音效','SFX'),('时序配方','MAP')]],'inputLabel':'六类输入 →','outputLabel':'→ 完整编舞','conclusion':'把素材变方法'}
        else:
            bind('chapter-plan','// 19 — 这几天全盘托出','chapters.plan',28,context='text')
            bind('chapter-delivery','// 20 — 更新会比较多','chapters.delivery',28,context='text')
            bind('calendar-month','OCT','calendar.heading',3)
            bind('calendar-label','国庆假期','calendar.label',4)
            bind('calendar-unit','DAY ${i + 1}','calendar.unit',8)
            bind('calendar-note','这几天 →','calendar.note',10)
            bind('timeframe','最近一两年 · 2025 → 2026','timeframe',28)
            bind('topic-left','AI','topic.lead',2,context='text')
            bind('topic-right','内容制作','topic.label',4,context='text')
            for i,old in enumerate(['口播剪辑','动效','字幕','配乐音效','工作流','Skill']):
                bind(f'capability-{i}',old,f'capabilities.{i}',5)
            for i,old in enumerate(['经验','观点','干货']):
                bind(f'deliverable-{i}',old,f'deliverables.{i}',2)
            bind('unbox-conclusion','全盘托出','conclusion',4,context='text')
            bind('stack-heading','更新会比较多！','stack.heading',9)
            bind('stack-disclosure','集数为示意','stack.disclosure',16)
            bind('stack-prefix','EP ${String','stack.prefix',5)
            slots[-1]['sourceText']='EP '
            for span in slots[-1]['sourceSpans']:span['end']=span['start']+3
            slots.append({'id':'first-index','type':'number','sourceCode':'11 + i','valueTemplate':'{value} + i','min':1,'max':90,'required':True,'inputPath':'stack.firstIndex'})
            # Keep the original seven-page count and ten illustrative cards.
            example={'presenterLabel':'on air · 本期讲述者','chapters':{'plan':'02 — 七步制作计划','delivery':'03 — 本期交付示意'},'calendar':{'heading':'RUN','label':'制作计划','unit':'STEP ${i + 1}','note':'七步推进 →'},'timeframe':'从试片 · 走向持续制作','topic':{'lead':'MP','label':'动效制作'},'capabilities':['编排','人物','节奏','声音','核验','导出'],'deliverables':['源码','配方','成片'],'conclusion':'一起交付','stack':{'heading':'按批次持续交付','disclosure':'卡片数量与编号为示意','prefix':'NO ','firstIndex':1}}
            # Prefix binds only the letters, preserving reviewed interpolation.
            slots[-2]['inputPath']='stack.prefix'
            calendar_slot=next(s for s in slots if s['id']=='calendar-unit')
            calendar_slot['sourceText']='DAY '
            for span in calendar_slot['sourceSpans']:span['end']=span['start']+4
            example['calendar']['unit']='STEP '
        scene={'id':group['id'],'role':group['role'],'source':{'start':start,'end':end},'sourceRevision':REVISION,
               'sourceCodeFile':f'units/{group["id"]}.js','sourceBlockSha256':sha(body.encode()),
               'requiresFaceTracking':True,'minFrames':round((end-start)*60),'maxHoldFrames':180,
               'motionWindows':[{'start':a,'end':b} for a,b in group['windows']],
               'cues':[{'id':id,'at':at,'kind':'semantic','required':True} for id,at in group['cues']],
               'slots':slots,'inputExample':example,
               'boundaries':{'entry':'source cut and presenter pose continuation retained; no preceding scene is instantiated','exit':'includes complete ball/particle/ink release within reviewed source range','connection':'standalone source groups; new cross-group connection requires review'},
               'limits':['macOS 1920x1080/60; source camera pose may continue from its preceding chapter at entry',
                         'Source narration/media and original music are not bundled',
                         'Seven calendar pages and ten illustrative delivery cards are fixed choreography, not factual quantities'] if group['id']=='calendar-to-delivery' else ['macOS 1920x1080/60; six cards and eleven network nodes are fixed symbolic choreography','Conclusion allows at most six glyphs; shorter underline tracks the complete replacement phrase'],
               'provenance':{'adapter':'adapters/paper-ball/extract.py','adapterSha256':sha(Path(__file__).read_bytes()),'sourceFiles':HASHES,
                             'statements':[inventory['units'][i] for i in group['indices']],'originalElementIdSeed':group['seed'],'boundaryCarry':'reviewed-empty',
                             'ports':['scoped host and nodes','presenter/captions/timecode use output clock','source image requests join the host imgWait queue','source SFX forwarded to macro timeline','kinetic phrase underline follows replacement glyph count','escape visible kinetic glyphs without changing motion']}}
        bind_authored_block(body,{**scene,'slots':[{**s,'mustChange':False} for s in slots]},
                            {s['id']:s['sourceText'] for s in slots if s['type']=='text'},scene['id'])
        scenes.append(scene);bodies.append(body)
    with tempfile.TemporaryDirectory(prefix='adu-paper-ball-pack-') as tmp:
        stage=Path(tmp)/'pack';(stage/'units').mkdir(parents=True);(stage/'licenses').mkdir()
        for scene,body in zip(scenes,bodies,strict=True):(stage/scene['sourceCodeFile']).write_text(body)
        (stage/'style.css').write_text(css)
        # As in the source READY, start all font loads before macro READY
        # awaits document.fonts.ready. Hidden groups do not otherwise request
        # their fonts until a later seek, which can cache fallback glyph widths.
        (stage/'fonts_ready.js').write_text('''window.PAPER_BALL_FONT_READY=Promise.all(
['100px Anton','700 60px Caveat','500 30px Geist','500 20px "Geist Mono"','100px YSBT','40px "Hannotate SC"']
.map(f=>document.fonts.load(f,'阿杜ABC')));
''')
        for name in ['lib.js','config.js']:shutil.copy2(ROOT/'packs/classic-performance/1.0.0'/name,stage/name)
        for license in notices_dir.glob('OFL-*.txt'):shutil.copy2(license,stage/'licenses'/license.name)
        shutil.copy2(ROOT/'LICENSE',stage/'LICENSE')
        (stage/'README.md').write_text((Path(__file__).parent/'pack-readme.md').read_text().replace('{PACK_VERSION}',version))
        save(stage/'audio_timeline.json',{'schema':'adu-authored-score/1','SEC':[{'id':g['id'],'start':g['start'],'end':g['end'],'mode':'synth','energy':.35,'options':{'kick_on':False,'clapon':False}} for g in GROUPS],
             'ENV':[{'at':0,'db':-6},{'at':140,'db':-6}],'HITS':{},'DARK':[],'sfxEvents':[],
             'mix':{'profile':'opus-five-v1'},'limits':['Synth is a disclosed new score; source external BGM is not reproduced. Runtime action SFX retain authored generators/gains/pan/durations.']})
        manifest={'id':'paper-ball-performance','version':version,'status':'candidate','title':'纸面聚合 · 小球与内容交付',
                  'sourceFormat':'authored-unit/1','sourceRevision':REVISION,'fps':60,'width':1920,'height':1080,'requireMotionWindows':True,
                  'runtimeFiles':['fonts_ready.js'],'scenes':scenes,'assetDefinitions':{},
                  'externalFonts':[{'id':'title','family':'YSBT','sha256':FONT_SHA,'format':'truetype','extension':'.ttf','required':True,
                                    'licenseSource':'https://www.uisdc.com/uisdc-first-free-font','distribution':'user-supplied; binary not bundled'}],
                  'environment':{'platform':'macOS','fonts':font_meta,'systemFonts':['PingFang SC','Hannotate SC'],'runtimeBase':'classic-performance@1.0.0 Scene host only; source custom physics remain private per instance'},
                  'validation':{'sourceReplay':'pending','newContent':'pending','independentUse':'pending'},
                  'files':{p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file()}}
        save(stage/'manifest.json',manifest);shutil.copytree(stage,output)
    return {'pack':manifest['id'],'version':version,'units':2,'path':str(output),'status':'candidate'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path);parser.add_argument('inventory',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--version',default='0.1.0-candidate')
    args=parser.parse_args()
    try:print(json.dumps(extract(args.record.resolve(),args.inventory.resolve(),args.output.resolve(),args.version),ensure_ascii=False))
    except (ValueError,OSError,KeyError) as exc:raise SystemExit(f'Paper ball extraction failed: {exc}') from exc

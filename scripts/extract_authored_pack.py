#!/usr/bin/env python3
"""Turn reviewed source units into a versioned candidate pack.

The proposal selects complete performances and supplies their semantic contract,
motion windows, reviewed text spans and media slots. No scene code is redesigned.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

from build_macro_project import bind_authored_block

ROOT = Path(__file__).resolve().parent.parent


def sha(data): return hashlib.sha256(data).hexdigest()


def require(ok, message):
    if not ok: raise ValueError(message)


def literal(node, end):
    """Read recipe constants without executing owner's audio script/imports."""
    if isinstance(node, ast.Constant): return node.value
    if isinstance(node, (ast.List, ast.Tuple)): return [literal(x, end) for x in node.elts]
    if isinstance(node, ast.Dict): return {literal(k, end): literal(v, end) for k,v in zip(node.keys,node.values)}
    if isinstance(node, ast.Name) and node.id == 'END': return end
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = literal(node.operand, end); return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'dict' and not node.args:
        return {kw.arg: literal(kw.value, end) for kw in node.keywords}
    raise ValueError(f'Unsupported recipe expression at audio source line {getattr(node, "lineno", "?")}; review rather than execute source code')


def audio_recipe(path, end):
    tree = ast.parse(path.read_text())
    values = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {'SEC', 'ENV', 'HITS', 'DARK'}:
                    values[target.id] = literal(node.value, end)
    require({'SEC','ENV','HITS'} <= values.keys(), 'Audio source needs reviewed SEC, ENV and HITS')
    sections=[]
    for index, row in enumerate(values['SEC']):
        if row[0] == 'piano':
            section={'start':row[1],'end':row[2],'mode':'reflective-piano'}
        else:
            section={'start':row[0],'end':row[1],'energy':row[2],'options':row[3],'mode':'synth'}
        sections.append({'id':f'score-{index:02d}',**section})
    return {'schema':'adu-authored-score/1','sourceSha256':sha(path.read_bytes()),'SEC':sections,
            'ENV':[{'at':at,'db':db} for at,db in values['ENV']], 'HITS':values['HITS'],
            'DARK':[{'start':a,'end':b} for a,b in values.get('DARK',[])],
            'mix':{'profile':'opus-five-v1','fadeOutSourceStart':end-.8,'fadeOutSeconds':.8},
            'sfxEvents':[], 'limits':['Runtime S() owns action cues; do not mix reference SFX twice.']}


def source_styles(source, entry, reviewed_files=None):
    """Preserve explicitly reviewed stylesheet/inline order from the source head.

    Existing proposals keep their original style.css + inline recipe. New routes
    can name hashed CSS files; font resources remain an environment decision.
    """
    html=(source/entry).read_text()
    if reviewed_files is None:
        css=(source/'style.css').read_text()+'\n'+'\n'.join(
            re.findall(r'<style[^>]*>([\s\S]*?)</style>',html,flags=re.I))
    else:
        require(isinstance(reviewed_files,dict) and reviewed_files,
                'styleFiles must name reviewed CSS files and their hashes')
        styles={}
        for name, expected in reviewed_files.items():
            require(isinstance(name,str) and not Path(name).is_absolute()
                    and '..' not in Path(name).parts and name.endswith('.css'),
                    'Stylesheet files must be project-relative CSS paths')
            path=(source/name).resolve()
            require(path.is_relative_to(source.resolve()) and sha(path.read_bytes())==expected,
                    f'Reviewed stylesheet changed or escaped project: {name}')
            styles[name]=path.read_text()

        class OrderedHead(HTMLParser):
            def __init__(self):
                super().__init__();self.parts=[];self.used=set();self.in_style=False;self.in_head=False
            def handle_starttag(self,tag,attrs):
                attrs=dict(attrs)
                if tag=='head':self.in_head=True
                if not self.in_head:return
                if tag=='style':self.in_style=True;self.parts.append('')
                if tag=='link' and 'stylesheet' in attrs.get('rel','').lower().split():
                    name=attrs.get('href')
                    if name in styles:self.parts.append(styles[name]);self.used.add(name)
            def handle_data(self,data):
                if self.in_head and self.in_style:self.parts[-1]+=data
            def handle_endtag(self,tag):
                if tag=='style':self.in_style=False
                if tag=='head':self.in_head=False
        parser=OrderedHead();parser.feed(html)
        require(parser.used==set(styles), 'Every reviewed stylesheet must be linked in the source head')
        css='\n'.join(parser.parts)
    return re.sub(r'@font-face\s*\{[^}]*\}', '', css, flags=re.I)


def copy_layout_contract(proposal, source, stage):
    """Keep reviewed portrait assets in the pack instead of dropping them."""
    from copy import deepcopy
    from pack_layout import resolve_layout
    layouts = proposal.get('layouts')
    if layouts is None:
        return None
    require(isinstance(layouts, dict) and 'landscape' in layouts,
            'layouts must declare the landscape baseline')
    require(not set(layouts) - {'landscape', 'portrait'}, 'Unknown layout name')
    for name, item in layouts.items():
        require(isinstance(item, dict), 'Layout descriptor must be an object')
        try:
            resolve_layout({'layouts': layouts}, {'layout': name})
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if name == 'portrait':
            require(item.get('runtime') and item.get('stylesheet'),
                    'Portrait extraction needs reviewed runtime and stylesheet')
        for key, extension in [('runtime', '.js'), ('stylesheet', '.css')]:
            file = item.get(key)
            if file is None:
                continue
            require(isinstance(file, str) and '/' not in file and file.endswith(extension),
                    'Layout files must be explicit top-level ' + extension)
            require(file not in {'lib.js', 'config.js', 'style.css'} and file not in proposal.get('runtimeFiles', []),
                    'Layout assets must be separate from the source runtime')
            require(file in proposal.get('sourceFiles', {}) and sha((source/file).read_bytes()) == proposal['sourceFiles'][file],
                    'Layout asset needs a reviewed sourceFiles fingerprint: ' + file)
            shutil.copy2(source/file, stage/file)
    return deepcopy(layouts)


def attach_adaptation_profile(manifest, descriptor, *, legacy=False):
    """Freeze semantic/port requirements with new extraction, before publication."""
    from copy import deepcopy
    from adaptation import load_profile
    if descriptor is None:
        require(legacy, 'New extraction requires proposal.adaptationProfile; --legacy is only for replaying historical proposals')
        manifest['adaptationStatus'] = 'unprofiled-legacy'
        return
    require(isinstance(descriptor, dict), 'adaptationProfile must be an object')
    require('pack' not in descriptor, 'Embedded adaptationProfile omits pack; binding is derived from the frozen manifest')
    manifest['adaptationProfile'] = deepcopy(descriptor)
    declared = descriptor.get('scenes', [])
    require(isinstance(declared, list) and all(isinstance(s, dict) for s in declared),
            'adaptationProfile.scenes must be objects')
    require({s.get('sceneId') for s in declared} == {s['id'] for s in manifest['scenes']},
            'New extraction needs an adaptation contract for every extracted scene')
    # Hashes come from the reviewed AST blocks, never from a copied proposal.
    hashes = {s['id']: s['sourceBlockSha256'] for s in manifest['scenes']}
    for item in manifest['adaptationProfile']['scenes']:
        supplied = item.get('sourceBlockSha256')
        require(supplied is None or supplied == hashes[item['sceneId']],
                'adaptationProfile sourceBlockSha256 differs from extracted source')
        item['sourceBlockSha256'] = hashes[item['sceneId']]
    manifest['adaptationStatus'] = 'contract-validated-not-av-accepted'
    load_profile(manifest, ROOT / 'adaptation-profiles')


def extract(source, proposal_path, output, *, legacy=False):
    proposal=json.loads(proposal_path.read_text())
    require(not output.exists(), f'Refusing existing pack: {output}')
    require(output.parent.is_dir(), 'Output parent must exist')
    require(proposal.get('id') and proposal.get('version') and proposal.get('sourceRevision'),
            'Proposal needs pack id, version and frozen sourceRevision')
    require(proposal.get('adaptationProfile') is not None or legacy,
            'New extraction requires proposal.adaptationProfile; --legacy is only for replaying historical proposals')
    inventories={}
    with tempfile.TemporaryDirectory(prefix='adu-pack-extract-') as tmp:
        for file, expected in proposal['sourceFiles'].items():
            require(isinstance(file,str) and not Path(file).is_absolute() and '..' not in Path(file).parts,
                    'Source files must use project-relative paths')
            path=(source/file).resolve()
            require(path.is_relative_to(source.resolve()) and sha(path.read_bytes())==expected,
                    f'Source file changed or escaped project: {file}')
            dest=Path(tmp)/(sha(file.encode())+'.json')
            subprocess.run(['node',str(ROOT/'scripts/authored_units.mjs'),str(path),str(dest)],check=True,capture_output=True)
            inventories[file]=json.loads(dest.read_text())
        stage=Path(tmp)/'pack';(stage/'units').mkdir(parents=True)
        scenes=[]
        for spec in proposal['units']:
            require(isinstance(spec.get('id'),str) and re.fullmatch(r'[a-z][a-z0-9-]{0,63}',spec['id']),
                    'Recipe IDs must be stable lowercase ASCII, without path separators')
            raw=inventories[spec['file']]['units'][spec['index']]
            require(spec.get('expectedStatementSha256')==raw['sourceStatementSha256'],
                    f'{spec["id"]}: source statement differs from reviewed proposal')
            contract=spec['contract']
            require(contract.get('role') and contract.get('boundaries') and contract.get('motionWindows'),
                    f'{spec["id"]}: review role, complete AV edges and protected motion windows')
            scene={**contract,'id':spec['id'],'source':raw['source'],'sourceCodeFile':f'units/{spec["id"]}.js',
                   'sourceBlockSha256':raw['sourceBlockSha256'],
                   'provenance':{k:raw[k] for k in ('sourceFile','sourceLines','sourceStatementSha256','helperSha256')},
                   'sourceRevision':proposal['sourceRevision']}
            # The parser CLI receives an absolute filename for reading. Pack
            # provenance must retain the reviewed project-relative identity.
            scene['provenance']['sourceFile']=spec['file']
            scene.setdefault('slots',[]);scene.setdefault('cues',[])
            # Validate reviewed spans transactionally even for reference replay.
            values={s['id']:s['sourceText'] for s in scene['slots'] if s['type'] in ('text','dynamicText')}
            bind_authored_block(raw['block'], {**scene,'slots':[{**s,'mustChange':False} for s in scene['slots']]}, values, scene['id'])
            (stage/scene['sourceCodeFile']).write_text(raw['block'])
            scenes.append(scene)
        css=source_styles(source,proposal.get('entry','index.html'),proposal.get('styleFiles'))
        # Environment fonts remain external. Public packs must document and check
        # fonts; never copy system or personal font binaries while extracting.
        (stage/'style.css').write_text(css)
        for file in ['lib.js','config.js',*proposal.get('runtimeFiles',[])]:
            require('/' not in file and file.endswith('.js'), 'Runtime files must be explicit top-level JavaScript')
            shutil.copy2(source/file,stage/file)
        # A public candidate is instantiated by macro-build, which requires
        # this episode's brand. Keep source values as provenance, never defaults.
        with (stage/'config.js').open('a') as stream:
            stream.write('\nCONFIG.brand="";CONFIG.account="";CONFIG.repoUrl="";\n')
        audio=audio_recipe(source/'audio.py',proposal['sourceDuration'])
        (stage/'audio_timeline.json').write_text(json.dumps(audio,ensure_ascii=False,indent=2)+'\n')
        layouts=copy_layout_contract(proposal,source,stage)
        manifest={'id':proposal['id'],'version':proposal['version'],'sourceFormat':'authored-unit/1',
                  'status':'candidate','title':proposal['title'],'sourceRevision':proposal['sourceRevision'],
                  'source':{'engine':'DOM/CSS/JavaScript','assetPolicy':'Owner media are not bundled; bind new assets.'},
                  'fps':60,'width':1920,'height':1080,'requireMotionWindows':True,
                  'runtimeFiles':proposal.get('runtimeFiles',[]),'scenes':scenes,
                  'assetDefinitions':proposal.get('assetDefinitions',{}),'environment':proposal.get('environment',{}),
                  'validation':{'sourceReplay':'pending','newContent':'pending','independentUse':'pending'},
                  'files':{p.relative_to(stage).as_posix():sha(p.read_bytes()) for p in sorted(stage.rglob('*')) if p.is_file() and '__pycache__' not in p.relative_to(stage).parts and p.suffix.lower() not in {'.pyc','.pyo'}}}
        if layouts is not None: manifest['layouts']=layouts
        attach_adaptation_profile(manifest, proposal.get('adaptationProfile'), legacy=legacy)
        (stage/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
        shutil.copytree(stage,output,ignore=shutil.ignore_patterns('__pycache__','*.pyc','*.pyo'))
    return {'pack':proposal['id'],'version':proposal['version'],'units':len(scenes),'status':'candidate','path':str(output)}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path);parser.add_argument('proposal',type=Path);parser.add_argument('output',type=Path)
    parser.add_argument('--legacy', action='store_true', help='Replay an old proposal without an adaptation contract; output stays unprofiled')
    args=parser.parse_args()
    try: print(json.dumps(extract(args.source.resolve(),args.proposal.resolve(),args.output.resolve(),legacy=args.legacy),ensure_ascii=False))
    except (ValueError,KeyError,IndexError,OSError,subprocess.CalledProcessError) as exc:
        raise SystemExit(f'Pack extraction failed: {exc}') from exc

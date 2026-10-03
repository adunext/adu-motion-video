"""Repeat and retime real scene code with synthetic media for browser stress."""
import json
from pathlib import Path
import re
import sys

import portrait_fixture
import vivid_fixture
from test_template_stress import target
from adapt_project import AdaptError, timed_scene
from build_macro_project import bind_authored_block, pack_scene_parts

ROOT = Path(__file__).resolve().parents[1]


def create(root):
    root = Path(root)
    root.mkdir(exist_ok=True)
    portrait_fixture.create(root)
    vivid_parent = root / 'vivid'
    vivid_parent.mkdir()
    vivid = vivid_fixture.create(vivid_parent)
    vivid.rename(root / vivid.name)
    vivid_parent.rmdir()
    for out in root.iterdir():
        if not out.is_dir():
            continue
        manifest = json.loads((out / 'manifest.json').read_text())
        pack = ROOT / 'packs' / out.name / manifest['version']
        prefix = (out / 'scenes.js').read_text().split('{const before=SFX.length;')[0]
        _, blocks = pack_scene_parts(pack, manifest)
        order = list(range(len(blocks)))
        if out.name == 'vivid-sticker-performance':
            order = [1, 2, 0]  # preserve generator tail support at video end
        code, plan, offset = [], [], 0
        for cycle in range(3):
            for source_index in order:
                source = manifest['scenes'][source_index]
                base = round((source['source']['end'] - source['source']['start']) * 60)
                shift = source.get('maxHoldFrames', 0) if cycle == 1 else 0
                t = target(source, base + shift, {}, shift)
                try:
                    item = timed_scene(source, t, source_index, 0, base + shift, 60, 60, [], {}, [])
                except AdaptError:
                    # No hold exists in a protected all-motion scene. This is
                    # an explicit base-time test, not hidden production fallback.
                    shift = 0
                    item = timed_scene(source, target(source, base, {}), source_index, 0, base, 60, 60, [], {}, [])
                item['id'] = f'{source["id"]}-cycle-{cycle}'
                item['output_start_frame'] += offset
                item['output_end_frame'] += offset
                for knot in item['time_map']:
                    knot['output_frame'] += offset
                offset = item['output_end_frame']
                body = blocks[source_index]
                if manifest.get('sourceFormat') == 'authored-unit/1':
                    slots = {s['id']: '新' for s in source['slots'] if s['type'] in ['text', 'dynamicText']}
                    body, _ = bind_authored_block(body, source, slots, item['id'])
                if out.name == 'vivid-sticker-performance':
                    for name in ['p_handover', 'x_notebook', 'x_robot', 'noise']:
                        body = body.replace(name + '.png', name + '.svg')
                code.append('{const before=SFX.length;' + body + ';window.MACRO_SOURCE_SFX.push(SFX.slice(before));}\n')
                plan.append(item)
        (out / 'scenes.js').write_text(prefix + ''.join(code))
        html = (out / 'index.html').read_text()
        # Original fixture inlines the JSON plan before the runtime scripts.
        start = html.index('window.MACRO_PLAN=')
        end = html.index(';</script>', start)
        html = html[:start] + 'window.MACRO_PLAN=' + json.dumps({'fps': 60, 'end_frame': offset, 'scenes': plan}) + html[end:]
        html = html.replace('const FACE={};', 'const FACE={};const PACK_PLAIN_TEXT=(()=>{const decoder=document.createElement("textarea"),cache=new Map();return value=>{if(!cache.has(value)){decoder.innerHTML=value;cache.set(value,decoder.value);}return cache.get(value);};})();')
        html = html.replace('<script src="lib.js">', '<script>CONFIG.end=' + str(offset / 60) + ';CONFIG.talkFrames=0;</script><script src="lib.js">')
        (out / 'index.html').write_text(html)
        (out / 'plan.json').write_text(json.dumps(plan))
        # Landscape uses its own native stage and omits portrait adapters.
        landscape = html.replace('"width": 1080, "height": 1920', '"width": 1920, "height": 1080')
        landscape = landscape.replace('"name": "portrait"', '"name": "landscape"')
        landscape = landscape.replace('<link rel="stylesheet" href="portrait.css">', '')
        if out.name == 'dark-3d-showcase':
            landscape = landscape.replace('"layout":"portrait","width":1080,"height":1920', '"layout":"landscape","width":1920,"height":1080')
        landscape = re.sub(r'<script src="(?:portrait.js|showcase-layout.js)"></script>', '', landscape)
        (out / 'landscape.html').write_text(landscape)


if __name__ == '__main__':
    create(sys.argv[1])

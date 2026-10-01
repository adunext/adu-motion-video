#!/usr/bin/env python3
"""Instantiate an entire authored scene pack for new narration and supplied media.

The output is a new browser video project with copied media and audio recipes.
It needs the documented system tools and fonts; raster acceptance is separate. No
source media or prior project is changed. The script rejects missing bindings
and assets instead of silently leaving a source episode's content on screen.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

from adapt_project import AdaptError, compile_plan, read_json
from mix_recipe import initial_settings

ROOT = Path(__file__).resolve().parent.parent


def fail(message: str) -> None:
    raise AdaptError(message)


def scene_parts(source: str) -> tuple[str, list[str]]:
    """Extract the original top-level authored IIFEs in scene order.

    The two packs use one `(() => {` / `})();` pair per Scene; anim4 also has
    one subtitles IIFE, which is replaced by the shared output-clock layer.
    """
    starts = list(re.finditer(r"(?m)^\(\(\) => \{\s*$", source))
    ends = list(re.finditer(r"(?m)^\}\)\(\);\s*$", source))
    if not starts or len(starts) != len(ends):
        fail('Pack scenes.js must have paired top-level scene IIFEs')
    prelude = source[:starts[0].start()]
    blocks = [source[a.start():b.end()] for a, b in zip(starts, ends)]
    scenes = [block for block in blocks if re.search(r"\bnew Scene\s*\(", block)]
    return prelude, scenes


def pack_scene_parts(pack_dir: Path, pack: dict) -> tuple[str, list[str]]:
    """Load reviewed independent closures without instantiating unused siblings."""
    if pack.get('sourceFormat') != 'authored-unit/1':
        return scene_parts((pack_dir / 'scenes.js').read_text())
    fingerprints = pack.get('files')
    if not isinstance(fingerprints, dict) or not fingerprints:
        fail('Independent authored pack needs frozen runtime and source file hashes')
    for relative, expected in fingerprints.items():
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            fail('Pack fingerprint path must be local and relative')
        path = (pack_dir / relative).resolve()
        if not path.is_relative_to(pack_dir.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            fail(f'Frozen pack file changed: {relative}; create a reviewed new pack version')
    blocks = []
    for scene in pack['scenes']:
        relative = scene.get('sourceCodeFile')
        if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts:
            fail(f'{scene["id"]}: sourceCodeFile must be a relative pack file')
        path = (pack_dir / relative).resolve()
        if not path.is_relative_to(pack_dir.resolve()): fail('Source code escaped pack directory')
        block = path.read_text()
        if hashlib.sha256(block.encode()).hexdigest() != scene.get('sourceBlockSha256'):
            fail(f'{scene["id"]}: independent authored source hash changed')
        blocks.append(block)
    return '', blocks


def js_content(value: str, *, html_context: bool) -> str:
    if html_context: value = html.escape(value, quote=True)
    # A single escaped representation is safe inside ', ", and ` strings.
    return ''.join({'\\': '\\\\', "'": "\\'", '"': '\\"', '`': '\\`', '$': '\\u0024',
                    '\n': '\\n', '\r': '\\r', '\u2028': '\\u2028', '\u2029': '\\u2029'}.get(c, c) for c in value)


def bind_authored_block(block: str, scene: dict, values: dict, instance_id: str) -> tuple[str, dict]:
    """Apply reviewed source spans in one transaction against the source hash.

    Finding a word in a JavaScript string is insufficient: the same word may
    occur in CSS, font names, media IDs or another visible label. Full packs
    therefore carry reviewed ranges for each text binding.
    """
    expected = scene.get('sourceBlockSha256')
    actual = hashlib.sha256(block.encode('utf-8')).hexdigest()
    if not expected or expected != actual:
        fail(f'{instance_id}: source block hash changed or is absent; regenerate and review pack bindings')
    changes: list[tuple[int, int, str, str]] = []
    numbers = {}
    for expression in scene.get('plainTextExpressions', []):
        source = '.textContent=' + expression + ';'
        if not isinstance(expression, str) or block.count(source) != 1:
            fail(f'{instance_id}: reviewed plain-text expression changed')
        start = block.index(source)
        changes.append((start, start + len(source),
                        '.textContent=PACK_PLAIN_TEXT(' + expression + ');', instance_id + '.plainText'))
    for slot in scene.get('slots', []):
        if slot['id'] not in values: continue
        kind, value = slot['type'], values[slot['id']]
        label = instance_id + '.' + slot['id']
        if kind in ('text', 'dynamicText'):
            old = slot['sourceText']; spans = slot.get('sourceSpans')
            if not spans: fail(f'{label}: a full pack needs reviewed sourceSpans for every text field')
            if slot.get('mustChange') and value == old:
                fail(f'{label}: replace the source placeholder {old!r} with this episode\'s content')
            for span in spans:
                start, end = span.get('start'), span.get('end')
                if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(block):
                    fail(f'{label}: invalid source span')
                if block[start:end] != old: fail(f'{label}: source span no longer matches its declared text')
                context = span.get('renderContext', slot.get('renderContext'))
                if context not in ('html', 'text', None): fail(f'{label}: invalid render context')
                new = js_content(str(value), html_context=context == 'html')
                changes.append((start, end, new, label))
        elif kind == 'number':
            if slot.get('binding'):
                numbers[slot['binding']] = value
            else:
                old, template = slot.get('sourceCode'), slot.get('valueTemplate')
                if not old or not template or len(old) < 3 or old.isdigit() or block.count(old) != 1:
                    fail(f'{label}: numeric slot needs one unique source expression')
                if template.count('{value}') != 1: fail(f'{label}: invalid numeric valueTemplate')
                start = block.index(old)
                changes.append((start, start + len(old), template.replace('{value}', str(value)), label))
    changes.sort()
    for a, b in zip(changes, changes[1:]):
        if a[1] > b[0]: fail(f'Overlapping source bindings: {a[3]} and {b[3]}')
    for start, end, new, _ in reversed(changes): block = block[:start] + new + block[end:]
    return block, numbers


def safe_name(value: str) -> str:
    result = re.sub(r'[^A-Za-z0-9_-]', '_', value)
    if not result or result in ('.', '..'): fail(f'Unsafe generated asset name: {value!r}')
    return result[:64] + '-' + hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]


def copy_external_fonts(pack: dict, spec: dict, spec_dir: Path, stage: Path) -> tuple[str, list[dict]]:
    """Require explicit, fingerprinted fonts instead of silently substituting.

    Font binaries excluded from a public pack can travel in the owner's new
    project. This records the input; it does not grant redistribution rights.
    """
    requirements = pack.get('externalFonts', [])
    if not isinstance(requirements, list): fail('externalFonts must be an array')
    inputs = spec.get('externalFontFiles', {})
    if not isinstance(inputs, dict): fail('externalFontFiles must be an object')
    declared = [item.get('id') for item in requirements if isinstance(item, dict)]
    if len(declared) != len(requirements) or any(not isinstance(id, str) for id in declared) or len(set(declared)) != len(declared):
        fail('External font IDs must be distinct')
    if set(inputs) - set(declared): fail('Unknown externalFontFiles ID')
    verified = []
    for item in requirements:
        id = item.get('id'); family = item.get('family'); expected = item.get('sha256')
        format = item.get('format'); extension = item.get('extension')
        if not isinstance(id, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', id): fail('Invalid external font ID')
        if not isinstance(family, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 _-]*', family): fail('Invalid external font family')
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected): fail('External font needs a frozen SHA256')
        if (format, extension) not in {('truetype','.ttf'),('opentype','.otf'),('woff','.woff'),('woff2','.woff2')}:
            fail('Unsupported external font format/extension')
        value = inputs.get(id)
        if value is None and not item.get('required', True): continue
        if not isinstance(value, str) or not value.strip(): fail(f'Provide externalFontFiles.{id}; source font substitution is not automatic')
        source = (spec_dir / value).resolve()
        if not source.is_file() or source.suffix.lower() != extension: fail(f'External font {id} must be a supplied {extension} file')
        actual = hashlib.sha256(source.read_bytes()).hexdigest()
        if actual != expected: fail(f'External font {id} differs from the reviewed source font; review a new pack version')
        verified.append((source, item))
    css = []; report = []
    for source, item in verified:
        target = stage / 'fonts' / (item['id'] + item['extension'])
        target.parent.mkdir(exist_ok=True); shutil.copy2(source, target)
        css.append(f"@font-face{{font-family:'{item['family']}';src:url(fonts/{target.name}) format('{item['format']}')}}")
        report.append({'id':item['id'],'family':item['family'],'sha256':item['sha256'],
                       'projectFile':target.relative_to(stage).as_posix(),'mode':'explicit-owner-supplied'})
    return '\n'.join(css) + ('\n' if css else ''), report


def prepare_face(stage: Path, spec: dict, needed: bool, fps: int, frames: int) -> dict:
    """Face-aware crops must never silently become a centre crop on a new clip."""
    setting = spec.get('faceTracking', {'mode': 'auto' if needed else 'none'})
    if not isinstance(setting, dict): fail('faceTracking must be an object with mode auto, fixed or none')
    mode = setting.get('mode')
    if mode == 'none':
        if needed: fail('This pack uses face crops: select auto tracking or supply an explicit fixed cx/cy/h crop')
        return {'mode': 'none', 'reason': 'selected pack uses uncropped portrait cards'}
    if mode == 'auto':
        if sys.platform != 'darwin' or not shutil.which('swiftc'):
            fail('Automatic face tracking needs macOS Vision and Swift; supply faceTracking:{mode:fixed,cx,cy,h} and inspect every cropped shot')
        subprocess.run(['bash', str(ROOT / 'scripts' / 'face_track.sh'), str(stage)], check=True)
        script = (stage / 'face.js').read_text()
        match = re.fullmatch(r'\s*const FACE\s*=\s*(\{.*\})\s*;\s*', script, flags=re.S)
        if not match: fail('Face tracking did not produce valid FACE data')
        data = json.loads(match[1]); face = data.get('clip_000', {})
        samples = face.get('f', [])
        if not samples or samples[0] > fps or frames - samples[-1] > fps:
            fail('Face tracking lacks samples near the clip boundaries; inspect the shot or specify a reviewed fixed crop')
        if any(b - a > fps for a, b in zip(samples, samples[1:])):
            fail('Face tracking lost the presenter for over one second; inspect the shot before cropping')
        return {'mode': 'vision', 'samples': len(samples), 'maxGapFrames': max((b-a for a,b in zip(samples,samples[1:])), default=0)}
    if mode == 'fixed':
        values = {k: setting.get(k) for k in ('cx', 'cy', 'h')}
        if any(not isinstance(x, (float, int)) or isinstance(x, bool) or not 0 < x <= 1 for x in values.values()):
            fail('A fixed crop needs normalized cx,cy,h in (0,1], measured from the new 720x1280 talk frame')
        face = {'f': [1, frames], **{k: [v, v] for k, v in values.items()}}
        (stage / 'face.js').write_text('const FACE=' + json.dumps({'clip_000': face}) + ';\n')
        return {'mode': 'explicit-fixed', **values, 'review': 'Check every crop; this is not tracking'}
    fail('faceTracking.mode must be auto, fixed or none')


def needs_face_tracking(pack: dict, plan: dict, prelude: str) -> bool:
    return ('function faceAt(' in prelude or
            any(pack['scenes'][item['source_scene_index']].get('requiresFaceTracking', False)
                for item in plan['scenes']))


def copy_media(stage: Path, pack: dict, item: dict, source_scene: dict, block: str,
               wall_sources: set[str]) -> tuple[str, dict]:
    alias: dict[str, str] = {}
    definitions = pack.get('assetDefinitions', {})
    for slot in source_scene.get('slots', []):
        kind, slot_id = slot.get('type'), slot['id']
        if kind not in ('image', 'sequence', 'wall-sprites', 'video'): continue
        if slot_id not in item['slots']: fail(f'{item["id"]}.{slot_id}: missing required media')
        value = item['slots'][slot_id]
        authored = slot.get('sourceAsset')
        if not isinstance(authored, str): fail(f'{item["id"]}.{slot_id}: missing sourceAsset')
        name = safe_name(item['id'] + '\0' + slot_id)
        if kind == 'image':
            original = Path(authored).name
            source = Path(value)
            target = stage / 'assets' / (name + source.suffix.lower())
            shutil.copy2(source, target)
            if original not in block: fail(f'{item["id"]}.{slot_id}: image {original} is absent from its scene code')
            block = block.replace(original, target.name)
            exported_value = target.relative_to(stage).as_posix()
        elif kind == 'video':
            clocks = [clock for clock in item.get('mediaClocks', []) if clock['slot'] == slot_id]
            if len(clocks) != 1: fail(f'{item["id"]}.{slot_id}: video needs one reviewed playback contract')
            clock = clocks[0]
            original_dir = clock['sourceDirectory']
            if f"'{original_dir}'" not in block and f'"{original_dir}"' not in block:
                fail(f'{item["id"]}.{slot_id}: source video directory is absent from its scene')
            source = Path(value['path'])
            target = stage / 'sc' / name; target.mkdir()
            subprocess.run(['ffmpeg', '-v', 'error', '-n', '-ss', str(clock['offset']),
                            '-i', str(source), '-an', '-vf',
                            f'fps={clock["fps"]},scale=1280:720:force_original_aspect_ratio=decrease:flags=lanczos,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
                            '-frames:v', str(clock['preparedFrames']), '-q:v', '3',
                            str(target / 'f_%04d.jpg')], check=True)
            frames = sorted(target.glob('f_*.jpg'))
            if len(frames) != clock['preparedFrames']:
                fail(f'{item["id"]}.{slot_id}: media decoder produced {len(frames)} of {clock["preparedFrames"]} frames')
            alias[original_dir] = name
            clock['directory'] = name
            exported_value = {**value, 'path': target.relative_to(stage).as_posix(),
                              'preparedFrames': len(frames), 'clock': 'output'}
        elif kind == 'sequence':
            original_dir = Path(authored).parent.name
            definition = definitions.get(slot_id, {})
            expected = definition.get('originalFrames', slot.get('originalFrames'))
            if not isinstance(expected, int) or expected <= 0:
                fail(f'{item["id"]}.{slot_id}: pack must declare originalFrames')
            directory = Path(value['path'])
            files = [directory / f'f_{i:04d}.jpg' for i in range(1, expected + 1)]
            if any(not p.is_file() for p in files):
                fail(f'{item["id"]}.{slot_id}: need contiguous JPEG f_0001.jpg through f_{expected:04d}.jpg; use the pack media preparer')
            target = stage / 'sc' / name; target.mkdir()
            for i, file in enumerate(files[:expected], 1):
                shutil.copy2(file, target / f'f_{i:04d}.jpg')
            alias[original_dir] = name
            exported_value = {**value, 'path': target.relative_to(stage).as_posix()}
        else:
            source = Path(value['path'] if isinstance(value, dict) else value)
            wall_sources.add(str(source))
            if len(wall_sources) > 1:
                fail('All wall scenes in one project must use the same wall-sprite directory')
            exported_value = {**value, 'path': 'sc/wall'} if isinstance(value, dict) else 'sc/wall'
        # Export a relocatable project, not the user's private input locations.
        item['slots'][slot_id] = exported_value
        for binding in item.get('bindings', []):
            if binding['id'] == slot_id: binding['value'] = exported_value
    return block, alias


def scaffold(pack: dict, output: Path) -> None:
    if output.exists(): fail(f'Refusing existing file: {output}')
    data: dict = {'pack': pack['id'], 'fps': pack['fps'], 'brand': '',
                  'presenterLabel': '// on air · 主讲人', 'scenes': []}
    if pack.get('externalFonts'):
        data['externalFontFiles'] = {item['id']: '' for item in pack['externalFonts']}
    for scene in pack['scenes']:
        start, end = scene['source']['start'], scene['source']['end']
        slots = {}
        for slot in scene.get('slots', []):
            kind = slot['type']
            if kind in ('text', 'dynamicText'): slots[slot['id']] = slot.get('sourceText', '')
            elif kind == 'number': slots[slot['id']] = None
            elif kind in ('image', 'sequence', 'wall-sprites'): slots[slot['id']] = None
        data['scenes'].append({'id': scene['id'] + '-01', 'sceneId': scene['id'],
                               'durationFrames': round((end - start) * pack['fps']),
                               'cues': {cue['id']: {'at': cue['at']} for cue in scene.get('cues', [])},
                               'slots': slots})
        if scene.get('inputExample'):
            data['scenes'][-1]['inputs'] = scene['inputExample']
            for slot in scene.get('slots', []):
                if slot.get('inputPath') or slot.get('inputTemplate'):
                    data['scenes'][-1]['slots'].pop(slot['id'], None)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def write_project_audio(stage: Path, music: dict) -> None:
    """Freeze the sound recipe with the project so future skill updates cannot alter it."""
    runtime = stage / 'audio_runtime'
    runtime.mkdir(exist_ok=True)
    for name in ('macro_audio.py', 'audiolib.py'):
        shutil.copy2(ROOT / 'scripts' / name, runtime / name)
    (stage / 'macro_music.json').write_text(json.dumps(music, ensure_ascii=False, indent=2) + '\n')
    (stage / 'audio.py').write_text('''import sys, json
from pathlib import Path
project = Path(__file__).resolve().parent
sys.path.insert(0, str(project / "audio_runtime"))
from macro_audio import render
music = json.loads((project / "macro_music.json").read_text())
render(project, project / music["path"] if music["mode"] == "track" else None, music.get("offset", 0))
''')


def build(pack_dir: Path, spec_path: Path, talk: Path, output: Path, subs_js: Path | None) -> None:
    if output.exists() or output.is_symlink(): fail(f'Refusing existing project: {output}')
    if not output.parent.is_dir(): fail(f'Project parent does not exist: {output.parent}')
    pack = read_json(pack_dir / 'manifest.json'); spec = read_json(spec_path)
    try:
        mix_settings = initial_settings(spec)
    except ValueError as exc:
        raise AdaptError(str(exc)) from exc
    if not talk.is_file(): fail(f'Missing edited talk video: {talk}')
    brand = spec.get('brand')
    if not isinstance(brand, str) or not brand.strip():
        fail('Set spec.brand to your own brand/account name before building')
    presenter_label = spec.get('presenterLabel', '// on air · 主讲人')
    if not isinstance(presenter_label, str) or not presenter_label.strip():
        fail('spec.presenterLabel must be nonempty text')
    subtitle_preset = spec.get('subtitlePreset', 'large-en')
    if subtitle_preset not in ('standard', 'large-en'):
        fail('subtitlePreset must be standard or large-en')
    prelude, authored_scenes = pack_scene_parts(pack_dir, pack)
    if len(authored_scenes) != len(pack['scenes']):
        fail(f'Pack scene count mismatch: manifest={len(pack["scenes"])} source={len(authored_scenes)}')
    with tempfile.TemporaryDirectory(prefix='.adu-macro-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'project'
        shutil.copytree(ROOT / 'template', stage)
        external_font_css, external_font_report = copy_external_fonts(pack, spec, spec_path.parent, stage)
        (stage / 'sc').mkdir(); (stage / 'talk').mkdir()
        for data in ('talkmap.js', 'face.js', 'subs.js'):
            (stage / data).write_text('// Optional data absent. Generated data may replace this stub.\n')
        subprocess.run([sys.executable, str(ROOT / 'scripts' / 'import_talk.py'), str(stage), str(talk),
                        '--fps', str(spec.get('fps', pack['fps']))], check=True)
        audio_timeline_path = pack_dir / 'audio_timeline.json'
        audio_timeline = read_json(audio_timeline_path) if audio_timeline_path.is_file() else None
        plan = compile_plan(pack, spec, spec_dir=spec_path.parent, project=stage,
                            audio_timeline=audio_timeline)
        imported = read_json(stage / 'import.json')
        if imported['frames'] != plan['end_frame']:
            fail(f'Edited talk has {imported["frames"]} frames but timeline has {plan["end_frame"]}; match the edited narration exactly. Silent trimming or frozen presenter tails are not allowed')
        imported.pop('source', None)
        imported.update(narrationAssets={'frames': 'talk/clip_000', 'audio': 'voice.wav'},
                        sourceEmbedded=False)
        (stage / 'import.json').write_text(json.dumps(imported, ensure_ascii=False, indent=2) + '\n')
        face_report = prepare_face(stage, spec, needs_face_tracking(pack, plan, prelude), plan['fps'], imported['frames'])
        if subs_js:
            if not subs_js.is_file(): fail(f'Missing generated subtitle data: {subs_js}')
            shutil.copy2(subs_js, stage / 'subs.js')
        css = (pack_dir / 'style.css').read_text()
        font_report = {'mode': 'system-font-stack'}
        if re.search(r"['\"]SFM['\"]", css):
            css = re.sub(r"@font-face\s*\{[^}]*font-family\s*:\s*['\"]SFM['\"][^}]*\}", '', css)
            custom_font = spec.get('monoFontFile')
            if custom_font:
                font = (spec_path.parent / custom_font).resolve()
                if not font.is_file() or font.suffix.lower() not in ('.ttf', '.otf', '.woff', '.woff2'):
                    fail('monoFontFile must be a supplied font file with redistribution rights')
                target_font = stage / 'assets' / ('mono' + font.suffix.lower())
                shutil.copy2(font, target_font)
                font_url = 'assets/' + target_font.name
                font_report = {'mode': 'supplied', 'file': font_url}
            else:
                font = Path('/System/Library/Fonts/SFNSMono.ttf')
                if not font.is_file(): fail('The source uses SFM; provide a licensed monoFontFile and visually check the font substitution')
                font_url = font.as_uri()
                font_report = {'mode': 'macOS-system-SFM', 'portable': False}
            css = "@font-face{font-family:'SFM';src:url(" + json.dumps(font_url) + ");}\n" + css
        if external_font_report: font_report['externalFonts'] = external_font_report
        (stage / 'style.css').write_text(external_font_css + css)
        # Use the hardened shared library: missing talk/wall media fail explicitly,
        # 60fps timecode, deterministic frame readiness, optional face fallback.
        lib = ((pack_dir / 'lib.js') if pack.get('sourceFormat') == 'authored-unit/1'
               else (ROOT / 'template' / 'lib.js')).read_text()
        lib = lib.replace('const talkSrc = t => {', 'const talkSrc = t => {\n  t = window.MACRO_OUTPUT_T ?? t;')
        lib = lib.replace('function faceAt(t) {', 'function faceAt(t) {\n  t = window.MACRO_OUTPUT_T ?? t;')
        lib = lib.replace('const tc = t => {', 'const tc = t => { t = window.MACRO_OUTPUT_T ?? t;')
        lib = lib.replace('const seqSrc = (dir, i, n) => `sc/${dir}/',
                          'const seqSrc = (dir, i, n) => `sc/${window.MACRO_MEDIA_ALIAS?.[dir] || dir}/')
        if any(item.get('mediaClocks') for item in plan['scenes']):
            signature = 'function seqAt(dir, n, fps, t, t0, loop = true) {'
            if lib.count(signature) != 1: fail('Output-clock video requires the supported seqAt function signature')
            lib = lib.replace(signature, signature + '''
  const clock = window.MACRO_VIDEO_CLOCKS?.find(c => c.sourceDirectory === dir);
  if (clock) {
    if (!Number.isFinite(window.MACRO_OUTPUT_T)) throw Error('Video needs the output clock');
    const elapsed = Math.max(0, window.MACRO_OUTPUT_T - clock.start);
    const frame = Math.min(clock.preparedFrames - 1, Math.floor(elapsed * clock.rate * clock.fps + 1e-6));
    return seqSrc(dir, frame + 1, clock.preparedFrames);
  }
''')
        if any(scene.get('plainTextExpressions') for scene in pack['scenes']):
            lib += '''
const PACK_PLAIN_TEXT = (() => {
  const decoder = document.createElement('textarea'), cache = new Map();
  return value => {
    if (!cache.has(value)) { decoder.innerHTML = value; cache.set(value, decoder.value); }
    return cache.get(value);
  };
})();
'''
        if pack.get('sourceFormat') == 'authored-unit/1':
            # Route helpers keep source geometry, but identity and progress use
            # this project. Never globally replace literal episode text.
            lib = lib.replace('AduNext&nbsp;&nbsp;<span>', '${window.PACK_BRAND_HTML}&nbsp;&nbsp;<span>')
            lib = lib.replace("label = '// on air · 阿杜'", 'label = window.PACK_PRESENTER_LABEL')
            lib = lib.replace('function raceAt(e, t, o = 1) {',
                              'function raceAt(e, t, o = 1) { t = window.MACRO_OUTPUT_T ?? t;')
        (stage / 'lib.js').write_text(lib)
        # anim4's authored faceAt assumes tracking is always present. Shared
        # fallback preserves the geometry while accepting projects without it.
        prelude = re.sub(r'function faceAt\(t\) \{[\s\S]*?\n\}(?=\nfunction camAt)', '', prelude, count=1)
        # The showcase pack retains its authored progress bar. Its source
        # `const RACE_K` would collide with the shared library's declaration.
        prelude = re.sub(r'\bRACE_K\b', 'PACK_RACE_K', prelude)
        if 'function race(' in prelude:
            # Keep the original line/dot geometry, but chapters and progress
            # belong to the newly selected/reordered scene instances.
            race_start = prelude.index('function race(')
            prelude = prelude[:race_start] + '''function race(parent, dark = true) {
  const c = dark ? 'rgba(255,255,255,.14)' : 'rgba(10,10,10,.10)';
  const count = Math.max(1, window.MACRO_RACE_SEGMENTS.length);
  const e = mk(parent, `<div style="width:1628px;height:2px;background:${c};position:relative">
    ${Array.from({length:count+1},(_,i)=>`<div style="position:absolute;left:${i/count*100}%;top:-5px;width:2px;height:12px;background:${c}"></div>`).join('')}
    <div class="rp" style="position:absolute;left:0;top:-7px;width:16px;height:16px;border-radius:50%;background:var(--blue);box-shadow:0 0 18px rgba(36,98,234,.9);transform:translateX(-50%)"></div></div>`,146,1058);
  e._p=e.querySelector('.rp'); return e;
}
function raceAt(e, sourceTime, opacity=1) {
  const segments=window.MACRO_RACE_SEGMENTS, frame=(window.MACRO_OUTPUT_T || 0)*window.MACRO_PLAN.fps;
  let i=segments.findIndex(s=>frame<s.endFrame); if(i<0)i=segments.length-1;
  const segment=segments[i], p=segment ? (i+clamp((frame-segment.startFrame)/(segment.endFrame-segment.startFrame)))/segments.length : 0;
  e._p.style.left=(p*100)+'%'; place(e,{o:opacity});
}
'''
        # Both authored wall helpers and in-scene wall loops use this fixed
        # directory; a project may use the same supplied wall in several scenes.
        wall_sources: set[str] = set()
        generated: list[str] = [prelude, '\nwindow.MACRO_SOURCE_SFX = [];\n']
        media_aliases = []
        number_maps = []
        race_segments = []
        for index, item in enumerate(plan['scenes']):
            authored = pack['scenes'][item['source_scene_index']]
            block = authored_scenes[item['source_scene_index']]
            if re.search(r'\brace\(sc\.el', block) or authored.get('hasProgressRail'):
                race_segments.append({'startFrame': item['output_start_frame'], 'endFrame': item['output_end_frame']})
            block, instance_numbers = bind_authored_block(block, authored, item['slots'], item['id'])
            block, aliases = copy_media(stage, pack, item, authored, block, wall_sources)
            media_aliases.append(aliases)
            number_maps.append(instance_numbers)
            generated.append(f'\n{{ const __before = SFX.length; window.PACK_NUMBERS = '
                             f'{json.dumps(instance_numbers)}; window.MACRO_MEDIA_ALIAS = '
                             f'{json.dumps(aliases)};\n{block}\n'
                             'window.MACRO_SOURCE_SFX.push(SFX.splice(__before)); }\n')
        if wall_sources:
            source_wall = Path(next(iter(wall_sources)))
            count = 0
            while (source_wall / f'{count:03d}.jpg').is_file(): count += 1
            if count != 389 or sorted(source_wall.glob('[0-9][0-9][0-9].jpg')) != [source_wall / f'{i:03d}.jpg' for i in range(count)]:
                fail(f'Full wall choreography needs 389 contiguous 4x4 sprite sheets; prepare_media.py expands 27–389 supplied works: {source_wall}')
            target_wall = stage / 'sc' / 'wall'; target_wall.mkdir()
            for i in range(count):
                asset = source_wall / f'{i:03d}.jpg'
                if not asset.is_file(): fail(f'Missing wall sprite {asset}')
                shutil.copy2(asset, target_wall / asset.name)
            metadata = source_wall / 'index.json'
            if metadata.is_file():
                entries = json.loads(metadata.read_text())
                if not isinstance(entries, list) or len(entries) != count:
                    fail(f'Wall index.json count must equal the {count} sprite sheets')
                wall = [[str(entry.get('slug', f'work_{i:03d}')), str(entry.get('author', ''))]
                        for i, entry in enumerate(entries)]
            else:
                wall = [[f'work_{i:03d}', ''] for i in range(count)]
            meta_file = source_wall / 'wall-meta.json'
            if not meta_file.is_file():
                fail('Wall needs wall-meta.json with the actual uniqueWorks count; do not present repeated sheets as distinct works')
            meta = read_json(meta_file); unique = meta.get('uniqueWorks')
            if not isinstance(unique, int) or isinstance(unique, bool) or not 27 <= unique <= count:
                fail('wall-meta.json uniqueWorks must be an integer from 27 through 389')
            (stage / 'wall.js').write_text('const WALL = ' + json.dumps(wall, ensure_ascii=False) + ';\n'
                                          f'window.PACK_WALL_UNIQUE_COUNT={unique};\n')
        else:
            (stage / 'wall.js').write_text('const WALL = [];\n')
        (stage / 'scenes.js').write_text(''.join(generated))
        (stage / 'macro_plan.js').write_text('window.MACRO_PLAN = ' + json.dumps(plan, ensure_ascii=False) + ';\n'
                                             'window.MACRO_MEDIA_BY_INSTANCE = ' + json.dumps(media_aliases) + ';\n'
                                             'window.MACRO_NUMBERS_BY_INSTANCE = ' + json.dumps(number_maps) + ';\n'
                                             'window.MACRO_RACE_SEGMENTS = ' + json.dumps(race_segments) + ';\n')
        (stage / 'macro_plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
        (stage / 'macro_main.js').write_text((ROOT / 'scripts' / 'macro_runtime.js').read_text())
        runtime_scripts = []
        for relative in pack.get('runtimeFiles', []):
            if not isinstance(relative, str) or Path(relative).is_absolute() or '..' in Path(relative).parts or not relative.endswith('.js'):
                fail('runtimeFiles must contain local JavaScript paths')
            path = (pack_dir / relative).resolve()
            if not path.is_relative_to(pack_dir.resolve()): fail('Runtime escaped pack directory')
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
            runtime_scripts.append('<script src=' + json.dumps(relative) + '></script>')
        if pack.get('sourceFormat') == 'authored-unit/1':
            (stage / 'config.js').write_text((pack_dir / 'config.js').read_text())
        config = (stage / 'config.js').read_text() + (f'\nCONFIG.demo=false; CONFIG.fps={plan["fps"]}; '
                  f'CONFIG.end={plan["durationSeconds"]}; CONFIG.subtitles={str(bool(subs_js)).lower()};\n'
                  f'CONFIG.brand={json.dumps(brand, ensure_ascii=False)}; '
                  f'CONFIG.account={json.dumps(brand, ensure_ascii=False)};\n'
                  f'CONFIG.subtitlePreset={json.dumps(subtitle_preset)};\n'
                  f'window.PACK_BRAND={json.dumps(brand, ensure_ascii=False)}; '
                  f'window.PACK_BRAND_HTML={json.dumps(html.escape(brand, quote=True), ensure_ascii=False)}; '
                  f'window.PACK_PRESENTER_LABEL={json.dumps(html.escape(presenter_label, quote=True), ensure_ascii=False)};\n')
        if pack.get('sourceFormat') == 'authored-unit/1':
            race = spec.get('progressRail')
            if race is None:
                race = {'labels': [item['id'] for item in plan['scenes']] + ['end'],
                        'keys': [item['output_start_frame'] / plan['fps'] for item in plan['scenes']] +
                                [plan['durationSeconds'], plan['durationSeconds'] + 1 / plan['fps']]}
            if not isinstance(race, dict): fail('progressRail must be an object')
            keys, labels = race.get('keys', []), race.get('labels', [])
            if len(keys) != len(labels) + 1 or len(labels) < 2 or any(not isinstance(v, (int, float)) for v in keys) or any(a >= b for a,b in zip(keys,keys[1:])):
                fail('progressRail needs increasing keys and len(keys) = len(labels) + 1')
            config += 'CONFIG.race=' + json.dumps(race, ensure_ascii=False) + ';\n'
        (stage / 'config.js').write_text(config)
        fade_seconds = spec.get('fadeEndSeconds', 0)
        if not isinstance(fade_seconds, (int, float)) or isinstance(fade_seconds, bool) or not 0 <= fade_seconds <= 2:
            fail('fadeEndSeconds must be between 0 and 2; use only for a deliberate silent tail')
        with (stage / 'config.js').open('a') as stream: stream.write(f'CONFIG.fadeEndSeconds={fade_seconds};\n')
        # Build a clean load order. The source subtitle IIFE is deliberately
        # omitted: its absolute source clock would desync new narration.
        (stage / 'index.html').write_text('''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<link rel="stylesheet" href="style.css"></head><body>
<div id="stage"><div id="world"></div><div id="fx"></div><div id="ov" style="position:absolute;inset:0;pointer-events:none"></div></div>
<script src="config.js"></script><script src="talkmap.js"></script><script src="face.js"></script>
<script src="subs.js"></script><script src="wall.js"></script><script src="macro_plan.js"></script>
<script src="lib.js"></script>''' + ''.join(runtime_scripts) + '''<script src="scenes.js"></script><script src="subtitles.js"></script>
<script src="macro_main.js"></script></body></html>\n''')
        # Recompose the complete mapped score, never the generic starter score.
        music = spec.get('music', {'mode': 'synth'})
        if not isinstance(music, dict) or music.get('mode') not in ('synth', 'track'):
            fail('music must be an object with mode synth or track')
        music = dict(music)
        if music['mode'] == 'track':
            path = music.get('path'); offset = music.get('offset')
            if not isinstance(path, str) or not (spec_path.parent / path).is_file(): fail('music.path must name the new supplied music track')
            if not isinstance(offset, (float, int)) or isinstance(offset, bool) or not 0 <= offset < float('inf'):
                fail('music.offset must be an explicit nonnegative number aligned for this new track')
            src_music = (spec_path.parent / path).resolve()
            dst_music = stage / 'assets' / ('music' + src_music.suffix.lower())
            shutil.copy2(src_music, dst_music); music['path'] = 'assets/' + dst_music.name
        write_project_audio(stage, music)
        shutil.copy2(ROOT / 'scripts' / 'mix_recipe.py', stage / 'audio_runtime' / 'mix_recipe.py')
        if mix_settings is not None:
            (stage / 'mix_recipe.json').write_text(json.dumps(mix_settings, indent=2) + '\n')
        (stage / 'macro_build_report.json').write_text(json.dumps({'face': face_report, 'font': font_report,
             'narrationFrames': imported['frames'], 'outputFrames': plan['end_frame'], 'subtitlePreset': subtitle_preset,
             'status': 'built-not-visually-accepted'}, ensure_ascii=False, indent=2) + '\n')
        provenance = {'pack': pack['id'], 'version': pack.get('version'), 'manifestSha256': hashlib.sha256((pack_dir / 'manifest.json').read_bytes()).hexdigest(),
                      'scenes': [{ 'instance': item['id'], 'sceneId': item['sceneId'],
                                  'sourceBlockSha256': pack['scenes'][item['source_scene_index']].get('sourceBlockSha256'),
                                  'startFrame': item['output_start_frame'], 'endFrame': item['output_end_frame'],
                                  'reuse': 'reviewed-parameter-binding' } for item in plan['scenes']],
                      'frozenRuntime': {name: hashlib.sha256((stage / name).read_bytes()).hexdigest()
                                        for name in ['lib.js', 'macro_main.js', 'style.css', 'audio_runtime/mix_recipe.py', *pack.get('runtimeFiles', [])]},
                      'qualityStatus': 'built-not-visually-accepted'}
        (stage / 'recipe_versions.json').write_text(json.dumps(provenance, ensure_ascii=False, indent=2) + '\n')
        (stage / 'macro_source_audio.json').write_text((pack_dir / 'audio_timeline.json').read_text()
                                                      if (pack_dir / 'audio_timeline.json').exists() else '{}\n')
        stage.rename(output)
    print(json.dumps({'project': str(output), 'pack': pack['id'], 'scenes': len(plan['scenes']),
                      'frames': plan['end_frame'], 'fps': plan['fps']}, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    skeleton = sub.add_parser('scaffold', help='Write an editable target-spec skeleton for all scenes')
    skeleton.add_argument('pack', type=Path); skeleton.add_argument('output', type=Path)
    project = sub.add_parser('build', help='Create a new project from an edited talk video and target spec')
    project.add_argument('pack', type=Path); project.add_argument('spec', type=Path)
    project.add_argument('talk', type=Path); project.add_argument('output', type=Path)
    project.add_argument('--subs-js', type=Path, help='New narration-aligned bilingual subtitle data')
    args = parser.parse_args()
    try:
        if args.command == 'scaffold': scaffold(read_json(args.pack / 'manifest.json'), args.output)
        else: build(args.pack.resolve(), args.spec.resolve(), args.talk.resolve(), args.output.resolve(), args.subs_js)
    except (AdaptError, OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f'Macro project failed: {exc}') from exc


if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Build a catalog-selected composition with one unchanged narration master."""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from adapt_project import AdaptError, read_json, require
from adaptation import validate_adapted_spec
from auto_templates import ROOT, choose, library
from build_macro_project import build, pack_scene_parts, preflight_narration
from mix_recipe import initial_settings
from pack_catalog import resolve


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def global_scene(item, offset, fps):
    value = deepcopy(item)
    # Schema-owned OUTPUT fields only. Source clocks, slot data, evidence,
    # asset offsets and edit maps are never visited recursively.
    for key in ('output_start_frame','output_end_frame','startFrame','endFrame'):
        if key in value: value[key] += offset
    for key in ('outputStart','outputEnd'):
        if key in value: value[key] += offset/fps
    for collection, keys in [
        ('knots',('outputFrame',)), ('anchors',('outputFrame',)),
        ('cues',('outputFrame',)), ('intervals',('startFrame','endFrame')),
        ('motionWindows',('outputStartFrame','outputEndFrame')),
        ('time_map',('output_frame',)), ('sfx',('outputFrame',)),
        ('mediaClocks',('startFrame','endFrame'))]:
        for node in value.get(collection, []):
            for key in keys:
                if key in node: node[key] += offset
    for event in value.get('sfx', []): event['at'] = event['outputFrame']/fps
    for clock in value.get('mediaClocks', []):
        clock['start'] = clock['startFrame']/fps
        clock['end'] = clock['endFrame']/fps
    value['outputClock'] = 'final-output'
    return value


def build_auto(plan_path, talk, output, subs_js=None, *, edit_map=None):
    require(not output.exists() and not output.is_symlink(), 'Refusing existing auto project')
    require(output.parent.is_dir(), 'Auto project parent must exist')
    saved = read_json(plan_path)
    require(saved.get('schema') == 'adu-auto-plan/1', 'Not an auto plan')
    # Stored success/source/profile flags are never authority. Recompute all
    # choices from the saved episode brief and current real input files.
    bindings = saved.get('catalogBindings')
    if bindings is None:
        bindings = {e['styleId']: e['selection'] for e in library() if e['selection'] in saved['sourceDigests']}
        require(set(bindings.values()) == set(saved['sourceDigests']), 'Legacy plan needs replan: frozen catalog bindings unavailable')
    pinned = library(layout=saved['brief'].get('layout','landscape'), bindings=bindings)
    require({e['styleId']: e['selection'] for e in pinned} == bindings, 'Pinned style removed; replan explicitly')
    result = choose(saved['brief'], Path(saved['sourceDirectory']), pinned)
    require(result['sourceDigests'] == saved['sourceDigests'], 'Catalog source changed; replan')
    require(result['spec'] == saved['spec'] and result['runs'] == saved['runs'],
            'Auto choices or run bindings changed; replan instead of editing generated specs')
    require(result['report']['ready'], 'Auto plan still has unbound or blocked episode content')
    runs = result['runs']
    require(runs, 'Auto plan needs selected complete groups')
    require(subs_js is None or subs_js.is_file(), 'Missing generated subtitle data')
    repair_mode=result['spec'].get('repairPolicy',{}).get('mode','off')
    if repair_mode=='off':edit_map=None
    if repair_mode not in {'off','basic'}:raise ValueError('Invalid repairPolicy.mode')
    if repair_mode=='basic':
        require(edit_map is not None,'Basic mode requires a prepared --edit-map for this invocation')
        require(result['spec'].get('narrationClock')=='edited-narration','Replan in edited-narration after repair')
        from repair_talk import validate_master
        edited,_=validate_master(edit_map,talk)
        require(result['spec'].get('narrationEditMap',{}).get('fingerprint') in (None,edited['fingerprint']),'Prepared edit map differs from the plan; replan')
        require(edited['editedFrames']==result['report']['durationFrames'],'Edited master duration differs; replan before building')
    else:preflight_narration(result['manifest'], result['spec'], talk)
    verified_packs=set()
    for run in runs:
        directory=resolve(run['selection'], ROOT/'packs')
        pack = read_json(directory/'manifest.json')
        if run['selection'] not in verified_packs:
            pack_scene_parts(directory,pack)
            verified_packs.add(run['selection'])
        validate_adapted_spec(pack,run['spec'],plan_path.parent,ROOT/'adaptation-profiles',allow_pending_talk=True,
                              composition_context=dict(startFrame=run['startFrame'],durationFrames=result['report']['durationFrames']))
    if len(runs) == 1:
        with tempfile.TemporaryDirectory(prefix='adu-auto-spec-') as tmp:
            path=Path(tmp)/'spec.json';write(path,runs[0]['spec'])
            build(resolve(runs[0]['selection'],ROOT/'packs'),path,talk,output,subs_js,edit_map=edit_map)
        write(output/'auto_selection.json',result['report'])
        return
    with tempfile.TemporaryDirectory(prefix='.adu-auto-build-', dir=output.parent) as tmp:
        stage=Path(tmp)/'project';stage.mkdir()
        # Import once with the original source color pipeline. Child frames and
        # PCM audio slices derive from this exact output grid, never re-encode.
        command=[sys.executable,str(ROOT/'scripts/import_talk.py'),str(stage),str(talk),'--fps','60']
        if result['spec'].get('colorReviewFile'): command.extend(['--color-review',result['spec']['colorReviewFile']])
        if edit_map is not None:
            from repair_talk import install_master
            install_master(edit_map,talk,stage)
            if subs_js is None and (stage/'edited.srt').is_file():
                from build_subs import build as subtitle_data
                subs_js=stage/'subs.js'
                subs_js.write_text('const SUBS='+json.dumps(subtitle_data(stage/'edited.srt'),ensure_ascii=False)+';\n')
        else:subprocess.run(command,check=True,capture_output=True)
        (stage/'compositions').mkdir()
        parts=[]; scenes=[]; receipts=[]; provenance=[]
        width,height=(1080,1920) if result['spec'].get('layout')=='portrait' else (1920,1080)
        total=result['report']['durationFrames']
        for i,run in enumerate(runs):
            spec=deepcopy(run['spec']); spec['music']={'mode':'none'} # one global episode track owns music
            # Only final part owns deliberate global fade; narrator is never
            # faded/reset merely because a style boundary was reached.
            if i<len(runs)-1: spec.pop('fadeEndSeconds',None)
            file=Path(tmp)/f'part-{i:02d}.json';write(file,spec)
            child=stage/'compositions'/f'part-{i:02d}'
            build(resolve(run['selection'],ROOT/'packs'),file,talk,child,subs_js,
                  _narration_slice=(stage,run['startFrame'],run['endFrame']),
                  _composition_context=dict(startFrame=run['startFrame'],durationFrames=total))
            prefix=child.relative_to(stage).as_posix()
            part=dict(path=prefix,style=run['style'],selection=run['selection'],startFrame=run['startFrame'],endFrame=run['endFrame'])
            parts.append(part)
            # Preserve pre-roll and post-part event onsets on the global clock.
            text=(child/'config.js').read_text()
            text+=f'\nwindow.MACRO_GLOBAL_START_FRAME={run["startFrame"]};window.MACRO_GLOBAL_END_FRAME={total};\n'
            (child/'config.js').write_text(text)
            if subs_js:
                # Keep full subtitle data unchanged, execute its overlay on the
                # global narration clock after the child's layout is installed.
                (child/'global_subtitles.js').write_text('const AUTO_NATIVE_OVERLAY=window.OVERLAY;\n'+
                    f'if(AUTO_NATIVE_OVERLAY)window.OVERLAY=t=>AUTO_NATIVE_OVERLAY(t+{run["startFrame"]/60});\n')
                html=(child/'index.html').read_text().replace('</body>','<script src="global_subtitles.js"></script></body>')
                (child/'index.html').write_text(html)
            plan=read_json(child/'macro_plan.json')
            for item in plan['scenes']:
                merged=global_scene(item,run['startFrame'],60)
                merged.update(pack=spec['pack'],packId=spec['pack'],part=prefix,
                              output_start_frame=item['output_start_frame']+run['startFrame'],
                              output_end_frame=item['output_end_frame']+run['startFrame'])
                scenes.append(merged)
            receipt=child/'media_color.json'
            if receipt.is_file():
                for item in read_json(receipt)['entries']:
                    item['files']={prefix+'/'+p:v for p,v in item['files'].items()}
                    item['preparation']['directory']=prefix+'/'+item['preparation']['directory']
                    receipts.append(item)
            child_provenance=read_json(child/'recipe_versions.json')
            # These controlled composite additions are frozen too, not left
            # inconsistent with the child's original build receipts.
            for p in ['config.js','index.html','global_subtitles.js']:
                if (child/p).is_file(): child_provenance['frozenRuntime'][p]=hashlib.sha256((child/p).read_bytes()).hexdigest()
            child_provenance['compositionClock']=dict(startFrame=run['startFrame'],endFrame=run['endFrame'],masterFrames=total)
            write(child/'recipe_versions.json',child_provenance)
            provenance.append(dict(**part,manifestSha256=child_provenance['manifestSha256'],scenes=child_provenance['scenes']))
        plan=dict(schema='adu-auto-composition/1',fps=60,end_frame=total,durationSeconds=total/60,
                  width=width,height=height,layout=dict(name=result['spec'].get('layout','landscape'),width=width,height=height),
                  scenes=scenes,parts=parts,clock='one unchanged narration master; integer frame slices',
                  boundaryPolicy='independent entries only; explicit cut between styles')
        write(stage/'macro_plan.json',plan)
        write(stage/'auto_selection.json',result['report'])
        write(stage/'auto_plan.json',saved)
        if receipts:write(stage/'media_color.json',dict(schema='adu-macro-media-color/1',entries=receipts))
        imported=read_json(stage/'import.json');imported.pop('source',None)
        imported.update(narrationAssets=dict(frames='talk/clip_000',audio='voice.wav'),sourceEmbedded=False)
        write(stage/'import.json',imported)
        shutil.copy2(ROOT/'scripts/auto_runtime.js',stage/'auto_runtime.js')
        (stage/'auto_plan.js').write_text('window.AUTO_PLAN='+json.dumps(plan,ensure_ascii=False)+';\n')
        (stage/'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8">'+
            f'<style>html,body{{margin:0;background:#000;overflow:hidden}}#stage{{position:relative;width:{width}px;height:{height}px}}</style>'+
            '<div id="stage"></div><script src="auto_plan.js"></script><script src="auto_runtime.js"></script></html>\n')
        runtime=stage/'audio_runtime';runtime.mkdir()
        for name in ['auto_audio.py','macro_audio.py','audiolib.py','sound_catalog.py','adaptation_audio.py','mix_recipe.py','music_policy.py']:
            shutil.copy2(ROOT/'scripts'/name,runtime/name)
        from music_policy import selection
        music,_=selection(result['spec'].get('music'),Path(saved['sourceDirectory']),total/60)
        if music['mode']=='track':
            source=Path(music['path']);(stage/'assets').mkdir()
            target=stage/'assets'/('music'+source.suffix);shutil.copy2(source,target)
            music['path']=target.relative_to(stage).as_posix()
        write(stage/'macro_music.json',music)
        (stage/'audio.py').write_text('from pathlib import Path\nimport sys\np=Path(__file__).resolve().parent\n'+
                                    'sys.path.insert(0,str(p/"audio_runtime"))\nfrom auto_audio import render\nrender(p)\n')
        settings=initial_settings(result['spec'])
        if settings:write(stage/'mix_recipe.json',settings)
        write(stage/'recipe_versions.json',dict(schema='adu-multi-pack-provenance/1',parts=provenance,
              qualityStatus='experimental-built-not-visually-accepted',layout=plan['layout'],
              frozenRuntime={p:hashlib.sha256((stage/p).read_bytes()).hexdigest() for p in
                             ['auto_runtime.js','auto_plan.js','audio_runtime/auto_audio.py','audio_runtime/audiolib.py','audio_runtime/music_policy.py', 'audio_runtime/sound_catalog.py','macro_music.json']}))
        write(stage/'macro_build_report.json',dict(status='experimental-built-not-visually-accepted',
              narrationFrames=total,outputFrames=total,parts=len(parts),voiceRetimed=False,
              subtitleClock='global',musicBoundary='one episode track; no per-pack background fallback; continuous listening required'))
        stage.rename(output)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('plan',type=Path);p.add_argument('talk',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--subs-js',type=Path);p.add_argument('--edit-map',type=Path)
    a=p.parse_args()
    try:
        build_auto(a.plan.expanduser().resolve(),a.talk.expanduser().resolve(),a.output.expanduser().absolute(),
                   a.subs_js.expanduser().resolve() if a.subs_js else None,edit_map=a.edit_map)
        print(json.dumps(dict(output=str(a.output),status='built-not-visually-accepted'),ensure_ascii=False))
    except (AdaptError,ValueError,OSError,subprocess.CalledProcessError) as exc:p.exit(1,f'Auto build failed: {exc}\n')


if __name__=='__main__':main()

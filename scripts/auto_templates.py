#!/usr/bin/env python3
"""Catalog-wide, version-locked planning from Agent-authored semantic annotations.

No keyword classifier, invented facts, source example copy or external model API.
Every offered group goes through the same semantic/timing/media/seam validator.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile

from adapt_project import AdaptError, integer, number, probe_media, read_json, require, transcript_rows
from adaptation import (BRIEF_SCHEMA, candidate_segment, load_profile, manifest_digest,
                        plan_adaptation, profile_digest, validate_profile)
from pack_catalog import resolve
from plan_macro_project import markdown_report, resolve_project_paths

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 'adu-auto-brief/1'


def library(root=ROOT):
    result = []
    catalog = read_json(root / 'references/template-catalog.json')
    for template in catalog['templates']:
        for style in template['styles']:
            selection = style.get('portraitSelection', style['selection'])
            path = resolve(selection, root / 'packs')
            manifest = read_json(path / 'manifest.json')
            profile = load_profile(manifest, root / 'adaptation-profiles')
            validate_profile(profile, manifest)
            result.append(dict(styleId=style['id'], title=style['title'], selection=selection,
                               path=path, manifest=manifest, profile=profile))
    return result


def capabilities(entries):
    groups = []
    for entry in entries:
        manifest = entry['manifest']
        contracts = {x['sceneId']: x for x in entry['profile']['scenes']}
        for source in manifest['scenes']:
            contract = contracts[source['id']]
            groups.append(dict(id=entry['styleId'] + ':' + source['id'], style=entry['styleId'],
                               selection=entry['selection'], status=manifest.get('status', 'candidate'),
                               intents=contract['intents'], phases=contract['requiredPhases'],
                               counts=contract.get('cardinality', {}), cueRoles=contract['cueRoles'],
                               entry=contract['entry'], exit=contract['exit'], effects=contract['effects'],
                               duration=dict(sourceSeconds=source['source']['end'] - source['source']['start'],
                                             minFrames=source.get('minFrames'), maxHoldFrames=source.get('maxHoldFrames', 0),
                                             followingFrames=source.get('minFollowingFrames', 0)),
                               motionWindows=source.get('motionWindows', []),
                               fields=[{k: deepcopy(v) for k, v in slot.items() if k not in
                                        {'sourceText', 'sourceRanges', 'ranges', 'bindings', 'sourceCode', 'sourceSpans', 'sourceAsset'}}
                                       for slot in source.get('slots', [])],
                               externalFonts=manifest.get('externalFonts', []),
                               layouts=list(manifest.get('layouts', {'landscape': {}})),
                               manifestDigest=manifest_digest(manifest)))
    return dict(schema='adu-auto-capabilities/1', styles=len(entries), groups=groups,
                semanticAuthor='current-assistant; must inspect whole narration and real timestamps',
                selection='hard constraints before style coherence and variety',
                status='experimental; source candidates retain their maturity')


def requirements(entry, brief):
    missing = []
    layouts = entry['manifest'].get('layouts', {'landscape': {}})
    if brief.get('layout', 'landscape') not in layouts:
        missing.append('layout: this style has no ' + brief.get('layout', 'landscape') + ' contract')
    supplied = brief.get('styleSettings', {}).get(entry['styleId'], {})
    require(isinstance(supplied, dict), 'styleSettings entries must be objects')
    fonts = supplied.get('externalFontFiles', brief.get('externalFontFiles', {}))
    require(isinstance(fonts, dict), 'externalFontFiles must be an object')
    for font in entry['manifest'].get('externalFonts', []):
        raw = fonts.get(font['id'])
        path = Path(raw) if isinstance(raw, str) and raw else None
        if path is None or not path.is_file():
            if font.get('required', True): missing.append('externalFontFiles.' + font['id'])
        elif path.suffix.lower() != font['extension']:
            missing.append('externalFontFiles.' + font['id'] + ': incorrect font extension')
        elif hashlib.sha256(path.read_bytes()).hexdigest() != font['sha256']:
            missing.append('externalFontFiles.' + font['id'] + ': SHA differs from frozen font')
    if 'SFM' in (entry['path'] / 'style.css').read_text():
        raw = supplied.get('monoFontFile', brief.get('monoFontFile'))
        if raw and not Path(raw).is_file(): missing.append('monoFontFile: missing supplied file')
        elif not raw and not Path('/System/Library/Fonts/SFNSMono.ttf').is_file():
            missing.append('monoFontFile: source SFM requires an explicitly supplied licensed font on this platform')
    return missing


def universe(entries, brief):
    manifest = dict(id='auto-template-library', version='1', fps=60, requireMotionWindows=True,
                    layouts={'landscape': dict(width=1920, height=1080),
                             'portrait': dict(width=1080, height=1920)}, scenes=[], assetDefinitions={})
    contracts = []
    index = {}
    for entry in entries:
        m = entry['manifest']
        require(m['fps'] == 60, 'Auto library currently requires the shared 60fps source clock')
        names = {s['id']: entry['styleId'] + ':' + s['id'] for s in m['scenes']}
        for key, value in m.get('assetDefinitions', {}).items():
            require(key not in manifest['assetDefinitions'] or manifest['assetDefinitions'][key] == value,
                    'Conflicting library asset definitions: ' + key)
            manifest['assetDefinitions'][key] = deepcopy(value)
        for source in m['scenes']:
            sid = names[source['id']]
            clone = deepcopy(source); clone['id'] = sid
            manifest['scenes'].append(clone)
            index[sid] = (entry, source['id'])
        for contract in entry['profile']['scenes']:
            clone = deepcopy(contract); clone['sceneId'] = names[contract['sceneId']]
            clone['styleId'] = entry['styleId']
            clone['unmetRequirements'] = requirements(entry, brief)
            for block, key in [('entry', 'requiresPrevious'), ('exit', 'requiresNext')]:
                if key in clone[block]: clone[block][key] = [names[x] for x in clone[block][key]]
            for binding in clone['entry'].get('continuityBindings', []):
                binding['previousSceneId'] = names[binding['previousSceneId']]
            contracts.append(clone)
    profile = dict(schema='adu-adaptation-profile/1', id='auto-library', version='1',
                   pack=dict(id=manifest['id'], version=manifest['version'], manifestDigest=manifest_digest(manifest)),
                   scenes=contracts)
    validate_profile(profile, manifest)
    return manifest, profile, index


def prepare_brief(brief, directory):
    require(brief.get('schema') == SCHEMA, 'Auto brief schema must be ' + SCHEMA)
    require(brief.get('stylePolicy', 'coherent-first') in {'coherent-first', 'mixed'},
            'stylePolicy must be coherent-first or mixed')
    require(brief.get('fps', 60) == 60, 'Auto planning currently requires fps=60')
    require(isinstance(brief.get('styleSettings', {}), dict), 'styleSettings must be an object')
    result = resolve_project_paths(brief, directory)
    for key, value in result.get('styleSettings', {}).items():
        require(isinstance(value, dict) and set(value) <= {'monoFontFile', 'externalFontFiles'},
                'styleSettings only supports font binding objects')
    result['styleSettings'] = {key: resolve_project_paths(value, directory)
                               for key, value in result.get('styleSettings', {}).items()}
    return result


def child_runs(spec, index, directory):
    """Executable, validated single-pack specs with rebased real output anchors."""
    runs = []
    offset = 0
    transcript = transcript_rows(spec.get('transcript'), directory)
    for segment, target in zip(spec['adaptation']['segments'], spec['scenes']):
        entry, real_id = index[target['sceneId']]
        if not runs or runs[-1]['style'] != entry['styleId']:
            runs.append(dict(style=entry['styleId'], selection=entry['selection'], startFrame=offset,
                             endFrame=offset, targets=[], segments=[], entry=entry))
        run = runs[-1]
        local = deepcopy(target); local['sceneId'] = real_id
        local['startFrame'] -= run['startFrame']; local['endFrame'] -= run['startFrame']
        for cue in local['cues'].values():
            if 'frame' in cue: cue['frame'] -= run['startFrame']
        annotated = candidate_segment(segment, target['sceneId'])
        annotated = {k: deepcopy(v) for k, v in annotated.items() if k not in
                     {'candidateInterpretations', 'candidates', 'preferredScenes'}}
        # Save resolved cues as segment-local frames; phrase references cannot
        # be naively reused in a sliced transcript with a different origin.
        annotated['anchors'] = {}
        contracts = {x['sceneId']: x for x in entry['profile']['scenes']}
        from adapt_project import cue_binding
        for cue_id, cue in target['cues'].items():
            frame = cue_binding(cue, transcript, target['startFrame'] / 60, target['endFrame'] / 60,
                                60, segment['id'] + '.' + cue_id)
            annotated['anchors'][contracts[real_id]['cueRoles'][cue_id]] = dict(frame=frame - offset)
            local['cues'][cue_id] = dict(frame=frame - run['startFrame'])
        run['targets'].append(local); run['segments'].append(annotated)
        offset += segment['durationFrames']; run['endFrame'] = offset
    globals_ = {k: deepcopy(v) for k, v in spec.items() if k not in
                {'pack', 'version', 'scenes', 'adaptation', 'transcript', 'narrationDuration'}}
    for run in runs:
        e = run.pop('entry'); profile = e['profile']
        run['spec'] = {**globals_, 'pack': e['manifest']['id'], 'version': e['manifest']['version'],
                       'scenes': run.pop('targets'), 'narrationDuration': (run['endFrame']-run['startFrame'])/60,
                       'adaptation': dict(schema='adu-adapted-spec/1', profileId=profile['id'],
                                          profileVersion=profile['version'], profileDigest=profile_digest(profile),
                                          segments=run.pop('segments'), ready=True, validationStage='pre-import')}
    return runs


def choose(brief, directory, entries=None):
    brief = prepare_brief(brief, directory)
    entries = entries or library()
    known = {e['styleId'] for e in entries}
    allowed = brief.get('allowedStyles', sorted(known))
    require(isinstance(allowed, list) and allowed and all(isinstance(x, str) for x in allowed)
            and len(set(allowed)) == len(allowed) and set(allowed) <= known,
            'allowedStyles must contain known, distinct style IDs')
    require(set(brief.get('styleSettings', {})) <= known, 'styleSettings contains an unknown style ID')
    entries = [e for e in entries if e['styleId'] in allowed]
    manifest, profile, index = universe(entries, brief)
    routes = brief.get('segmentations', [{'id': 'original', 'segments': brief.get('segments')}])
    require(isinstance(routes, list) and routes and len(routes) <= 16, 'Provide 1..16 complete semantic segmentations')
    require(all(isinstance(r, dict) and isinstance(r.get('id'), str) for r in routes),
            'Segmentation entries must be objects with string IDs')
    require(len({r.get('id') for r in routes}) == len(routes), 'Segmentation IDs must be unique')
    expected = None
    results = []
    for route in routes:
        require(isinstance(route.get('id'), str) and route['id'].strip(), 'Segmentation needs an id')
        require(isinstance(route.get('segments'), list) and route['segments'], 'Segmentation needs segments')
        frames = sum(integer(s.get('durationFrames'), 'durationFrames', minimum=1) for s in route['segments'])
        if expected is None: expected = frames
        require(frames == expected, 'Alternative segmentations must preserve the entire narration frame clock')
        current = {**brief, 'schema': BRIEF_SCHEMA, 'segments': route['segments']}
        for segment in current['segments']:
            require(isinstance(segment, dict), 'Segment must be an object')
            require(isinstance(segment.get('candidates', {}), dict) and
                    isinstance(segment.get('candidateInterpretations', {}), dict), 'Candidate bindings and interpretations must be objects')
            require(set(segment.get('candidates', {})) <= set(index), 'Use qualified candidate IDs from auto-capabilities')
            require(set(segment.get('candidateInterpretations', {})) <= set(index), 'Unknown interpretation candidate')
        profiles = [(e['styleId'], {**profile, 'scenes': [x for x in profile['scenes'] if x['styleId'] == e['styleId']]})
                    for e in entries] + [('mixed', profile)]
        for style, subset in profiles:
            result = plan_adaptation(manifest, subset, current, directory, allow_pending_talk=True)
            results.append(dict(route=route['id'], style=style, profile=subset, **result))
    def rank(result):
        report = result['report']
        # Complete bindings always outrank coherence; mixed is a recovery when
        # no single family covers the real whole-film rhetorical structure.
        state = 0 if report['ready'] else 1 if report['status'] == 'needs-binding' else 2
        coherence = int(result['style'] == 'mixed') if brief.get('stylePolicy', 'coherent-first') == 'coherent-first' else 0
        return (state, len(report['missing']) + len(report['blocking']), coherence,
                report['score'] if report['score'] is not None else float('inf'), result['route'], result['style'])
    selected = min(results, key=rank)
    from music_policy import apply
    for result in results:
        apply(result, brief.get('music'), directory)
    runs = child_runs(selected['spec'], index, directory) if selected['report']['ready'] else []
    for run in runs:
        run['spec'].update(brief.get('styleSettings', {}).get(run['style'], {}))
        require(set(brief.get('styleSettings', {}).get(run['style'], {})) <=
                {'monoFontFile', 'externalFontFiles'}, 'styleSettings only supports font bindings')
    report = {**selected['report'], 'schema': 'adu-auto-report/1', 'selectedStyle': selected['style'],
              'selectedSegmentation': selected['route'], 'stylesCompared': len(entries),
              'groupsCompared': len(profile['scenes']), 'stylePolicy': brief.get('stylePolicy', 'coherent-first'),
              'alternatives': [dict(style=x['style'], segmentation=x['route'], status=x['report']['status'],
                                    missing=x['report']['missing'], score=x['report']['score']) for x in results],
              'nextActions': []}
    if not report['ready']:
        report['nextActions'] = ['Inspect rejected candidates and capability fields; the assistant must revise genuine semantic segmentation, short display copy or real media bindings, then replan.',
                                 'Never invent missing phases, keyword timestamps, evidence or extra items; never loop animations or stretch protected action windows.']
    return dict(schema='adu-auto-plan/1', brief=brief, sourceDirectory=str(directory.resolve()),
                sourceDigests={e['selection']: manifest_digest(e['manifest']) for e in entries},
                manifest=manifest, profile=selected['profile'], spec=selected['spec'], report=report, runs=runs)


def save(brief_path, output):
    require(not output.exists() and not output.is_symlink(), 'Refusing existing auto plan directory')
    require(output.parent.is_dir(), 'Auto plan parent must exist')
    result = choose(read_json(brief_path), brief_path.parent)
    with tempfile.TemporaryDirectory(prefix='.adu-auto-plan-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'plan'; stage.mkdir()
        for name, value in [('auto_plan.json', result), ('report.json', result['report']),
                            ('spec.json', result['spec']), ('capabilities.json', capabilities(library()))]:
            (stage / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        (stage / 'report.md').write_text(markdown_report(result['report'], result['spec']))
        for i, run in enumerate(result['runs']):
            (stage / f'part-{i:02d}-spec.json').write_text(json.dumps(run['spec'], ensure_ascii=False, indent=2) + '\n')
        stage.rename(output)
    return result['report']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('capabilities')
    p = sub.add_parser('plan'); p.add_argument('brief', type=Path); p.add_argument('output', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'capabilities':
            print(json.dumps(capabilities(library()), ensure_ascii=False, indent=2)); return 0
        report = save(args.brief.expanduser().resolve(), args.output.expanduser().absolute())
        print(json.dumps({k: report[k] for k in ('ready', 'status', 'selectedStyle', 'selectedSegmentation')}, ensure_ascii=False))
        return 0 if report['ready'] else 2
    except (AdaptError, ValueError, OSError) as exc:
        parser.exit(1, f'Auto planning failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Private source-fidelity replay of extracted closures with original media.

This diagnostic preserves the source clock and complete original soundtrack.
It is not a new-content build and its personal media must not enter public packs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from build_macro_project import pack_scene_parts
from source_registry import verify, digest

ROOT = Path(__file__).resolve().parent.parent


def replay(record_dir, pack_dir, output):
    record=json.loads((record_dir/'source.json').read_text())
    pack=json.loads((pack_dir/'manifest.json').read_text())
    if pack['sourceRevision'] != record['revision']: raise ValueError('Candidate pack and source revision differ')
    if output.exists(): raise ValueError(f'Refusing existing replay project: {output}')
    if not output.parent.is_dir(): raise ValueError('Output parent must exist')
    source=Path(record['origin'])
    if output.resolve().is_relative_to(source.resolve()) or source.resolve().is_relative_to(output.resolve()):
        raise ValueError('Replay output must be separate from the original source')
    # Complete replay, including original closing/credits, is deliberately
    # different from selecting a subset for a new narration.
    source_files={s['provenance']['sourceFile'] for s in pack['scenes']}
    for name in source_files | set(record['sourceFiles']) | set(record['mediaFiles']) | {record['entry']}:
        if not isinstance(name,str) or Path(name).is_absolute() or '..' in Path(name).parts or not name:
            raise ValueError('Replay paths must be project-relative; refusing absolute or escaping provenance')
    verify(record_dir)
    _, blocks=pack_scene_parts(pack_dir,pack)
    with tempfile.TemporaryDirectory(prefix='.adu-source-replay-',dir=output.parent) as tmp:
        stage=Path(tmp)/'project';stage.mkdir()
        for category in ('sourceFiles','mediaFiles'):
            base=record_dir/'snapshot' if category=='sourceFiles' or record['mediaStorage']=='snapshot' else source
            for name in record[category]:
                dst=stage/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/name,dst)
                if digest(dst)['sha256'] != record[category][name]['sha256']:
                    raise ValueError(f'Source changed while preparing replay: {name}')
        entry=stage/record['entry'];html=entry.read_text()
        for name in source_files | {'scenes.js'}:
            html=re.sub(r'<script\s+src=["\']'+re.escape(name)+r'["\']\s*></script>', '', html)
        # Route motion helpers must load before all independent scene closures.
        ending='<script src="ending.js"></script>'
        insertion='<script src="scenes.js"></script>\n'
        if ending in html: html=html.replace(ending,insertion+ending)
        else: html=html.replace('<script src="subtitles.js"></script>',insertion+'<script src="subtitles.js"></script>')
        entry.write_text(html)
        (stage/'scenes.js').write_text('\n'.join(blocks))
        for name in source_files:
            if name!='scenes.js':
                path=(stage/name).resolve()
                if not path.is_relative_to(stage.resolve()): raise ValueError('Refusing to remove a file outside replay staging')
                path.unlink(missing_ok=True)
        # Freeze the synth library locally; preserve the source score's exact
        # orchestration, phase, envelopes, effects and mix rather than remapping it.
        audio=(stage/'audio.py').read_text()
        old="sys.path.insert(0, os.path.expanduser('~/.claude/skills/adu-motion-video/scripts'))"
        if old not in audio: raise ValueError('Source audio import needs a reviewed adapter')
        audio=audio.replace(old,"sys.path.insert(0, os.path.join(HERE, 'audio_runtime'))")
        runtime=stage/'audio_runtime';runtime.mkdir()
        shutil.copy2(ROOT/'scripts/audiolib.py',runtime/'audiolib.py')
        (stage/'audio.py').write_text(audio)
        report={'mode':'private-source-replay','sourceRevision':record['revision'],
                'pack':pack['id'],'packVersion':pack['version'],'groups':len(blocks),
                'sceneHashes':[s['sourceBlockSha256'] for s in pack['scenes']],
                'referenceRenderSha256':record['render']['sha256'],
                'voiceClock':'unchanged-source','audio':'unchanged-source-recipe-local-import',
                'audioLibrarySha256':hashlib.sha256((runtime/'audiolib.py').read_bytes()).hexdigest(),
                'personalMedia':'private QA only','qualityStatus':'replay-prepared-not-accepted'}
        (stage/'source_replay.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        stage.rename(output)
    return {'project':str(output),'pack':pack['id'],'groups':len(blocks),'status':'prepared-not-accepted'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record',type=Path);parser.add_argument('pack',type=Path);parser.add_argument('output',type=Path)
    args=parser.parse_args()
    try: print(json.dumps(replay(args.record.resolve(),args.pack.resolve(),args.output.resolve()),ensure_ascii=False))
    except (ValueError,OSError,KeyError) as exc: raise SystemExit(f'Source replay failed: {exc}') from exc

#!/usr/bin/env python3
"""Locate frozen dependency/slot/motion/tail omissions, without certifying visuals."""
import argparse
import hashlib
import json
from pathlib import Path

from adapt_project import read_json
from build_macro_project import pack_scene_parts
from adaptation import load_profile, validate_profile
from adaptation_audio import _duration, SFX_REVERB_SECONDS


def audit(pack, inventory=None):
    manifest=read_json(pack/'manifest.json');findings=[]
    try:
        _,blocks=pack_scene_parts(pack,manifest)
    except (ValueError,OSError) as exc:
        return dict(status='failed',findings=[dict(file='manifest.json',code='closure',detail=str(exc))])
    profile=load_profile(manifest,Path(__file__).resolve().parents[1]/'adaptation-profiles')
    validate_profile(profile,manifest)
    for relative,digest in manifest.get('files',{}).items():
        if '__pycache__' in Path(relative).parts or Path(relative).suffix.lower() in {'.pyc','.pyo'}:
            findings.append(dict(file=relative,code='generated-cache-dependency'))
            continue
        file=pack/relative
        if not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest()!=digest:
            findings.append(dict(file=relative,code='frozen-file-drift'))
    scenes=[]
    for scene,body in zip(manifest['scenes'],blocks):
        for slot in scene.get('slots',[]):
            for span in slot.get('sourceSpans',[]):
                expected=slot.get('sourceCode') if slot['type']=='number' else slot.get('sourceText')
                if body[span['start']:span['end']]!=expected:
                    findings.append(dict(scene=scene['id'],slot=slot['id'],code='source-span-drift'))
        if not scene.get('motionWindows'):
            findings.append(dict(scene=scene['id'],code='motion-windows-unrecorded'))
        tails=[]
        for event in scene.get('sfx',[]):
            d,kind=_duration(event)
            if d is None:tails.append(dict(type=event['type'],status=kind));continue
            end=event.get('at',event.get('t',0))+d+SFX_REVERB_SECONDS
            tails.append(dict(type=event['type'],estimatedSupportEnd=end))
        estimated=max([t.get('estimatedSupportEnd',0) for t in tails],default=0)
        available=scene['source']['end']+scene.get('minFollowingFrames',0)/manifest['fps']
        if estimated>available+1/manifest['fps']:
            findings.append(dict(scene=scene['id'],code='tail-contract-short',estimatedExtraFrames=round((estimated-available)*manifest['fps']),
                note='Conservative buffer support estimate; generate and listen before judging audible truncation'))
        scenes.append(dict(id=scene['id'],source=scene['source'],variantOf=scene.get('variantOf'),
            slots=len(scene.get('slots',[])),mediaRoles=[dict(id=s['id'],role=s.get('role'),inputPath=s.get('inputPath')) for s in scene.get('slots',[]) if s['type'] in ['image','video','sequence','wall-sprites']],
            sourceBlockSha256=scene.get('sourceBlockSha256'),soundSupport=tails))
    source_count=len(inventory['units']) if inventory and 'units' in inventory else manifest.get('originalSceneCount')
    return dict(schema='adu-pack-closure-audit/1',pack=manifest['id'],version=manifest['version'],
        status='review-findings' if findings else 'structural-checks-passed',findings=findings,scenes=scenes,
        sourceSceneCount=source_count,extractedGroups=len(scenes),
        limits=['Static closure and declared spans only; browser typography, Canvas, image/font readiness, reverse seek and continuous AV must be checked in built projects.',
                'No inference that extracted group count equals full original source coverage.'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pack',type=Path);p.add_argument('--inventory',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();r=audit(a.pack,read_json(a.inventory) if a.inventory else None);s=json.dumps(r,ensure_ascii=False,indent=2)+'\n'
    if a.output:
        if a.output.exists():p.error('Refusing existing audit output')
        a.output.write_text(s)
    else:print(s)


if __name__=='__main__':main()

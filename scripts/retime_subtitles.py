#!/usr/bin/env python3
"""Preserve source SRT bytes; move whole cues through one narration edit map."""
from pathlib import Path
import argparse
import hashlib
import json
from decimal import Decimal, ROUND_HALF_UP
from adapt_project import parse_srt
from narration_edit_map import map_span, validate_edit_map


def identity(path):
    data=Path(path).read_bytes()
    return dict(sha256=hashlib.sha256(data).hexdigest(),sizeBytes=len(data))


def stamp(seconds):
    ms=int((Decimal(str(seconds))*1000).to_integral_value(rounding=ROUND_HALF_UP))
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def retime(source,edit_map):
    validate_edit_map(edit_map)
    expected=edit_map.get('transcriptIdentity')
    if expected is None or identity(source)!=expected:raise ValueError('SRT identity differs from repair plan')
    cues=parse_srt(Path(source));output=[];records=[]
    for i,cue in enumerate(cues):
        a,b=map_span(edit_map,cue['start'],cue['end'])
        if b-a<.001:raise ValueError('Derived cue would be invisible in millisecond SRT')
        output.append(f'{i+1}\n{stamp(a)} --> {stamp(b)}\n{cue["text"]}\n')
        records.append(dict(id=f'{expected["sha256"][:16]}:{i}',sourceStart=cue['start'],sourceEnd=cue['end'],editedStart=a,editedEnd=b,text=cue['text']))
    return '\n'.join(output),dict(schema='adu-subtitle-edit-receipt/1',sourceIdentity=expected,mapFingerprint=edit_map['fingerprint'],clock='edited-narration',cues=records,wordTimes='absent; complete cues protected')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('edit_map',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();text,record=retime(a.source,json.loads(a.edit_map.read_text()))
    with a.output.open('x') as f:f.write(text)
    with Path(str(a.output)+'.map.json').open('x') as f:json.dump(record,f,ensure_ascii=False,indent=2)

if __name__=='__main__':main()

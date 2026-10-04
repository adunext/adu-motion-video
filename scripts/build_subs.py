#!/usr/bin/env python3
"""Preserve SRT cues; optional explicitly authored bilingual grouping."""
import argparse
import json
from pathlib import Path
import runpy
from adapt_project import parse_srt, require


def build(srt, source=None):
    cues = parse_srt(srt)
    if source is None:
        return [dict(id=c['id'], t0=c['start'], t1=c['end'], zh=c['text'], en='',
                     sourceCueIds=[c['id']], wordTimesReliable=False, formatting='srt-basic',
                     sp=[[c['start'],c['end'],len(c['text'])]]) for c in cues]
    groups = runpy.run_path(str(source))['G']
    output, consumed = [], []
    for s0,s1,zh,en in groups:
        require(type(s0) is int and type(s1) is int and 1<=s0<=s1<=len(cues), 'Invalid subtitle group indices')
        selected=cues[s0-1:s1];consumed.extend(range(s0-1,s1))
        output.append(dict(id='group-'+str(s0), t0=min(c['start'] for c in selected),
            t1=max(c['end'] for c in selected), zh=zh, en=en,
            originalText='\n'.join(c['text'] for c in selected),sourceCueIds=[c['id'] for c in selected],
            wordTimesReliable=False,sp=[[c['start'],c['end'],len(c['text'])] for c in selected]))
    require(consumed==list(range(len(cues))), 'Subtitle groups drop, repeat or reorder source cues')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--srt',required=True,type=Path);p.add_argument('--src',type=Path);p.add_argument('--out',required=True,type=Path)
    a=p.parse_args(); result=build(a.srt,a.src)
    a.out.write_text('const SUBS='+json.dumps(result,ensure_ascii=False)+';\n',encoding='utf-8')
    print(f'{len(result)} 组字幕 → {a.out}')


if __name__=='__main__':main()

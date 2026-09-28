#!/usr/bin/env python3
"""双语字幕：SRT + 分组文案 → subs.js
subs_src.py 里定义 G = [(第一条cue序号, 最后一条cue序号, "中文（可润色）", "English"), ...]
用法：python3 build_subs.py --srt 口播.srt --src subs_src.py --out <anim目录>/subs.js
没有 subs_src.py 时：每条 SRT cue 单独成组、只有中文（英文留空），先跑起来再补。"""
import argparse, json, re
ap = argparse.ArgumentParser(); ap.add_argument('--srt', required=True); ap.add_argument('--src'); ap.add_argument('--out', required=True)
a = ap.parse_args()
def ts(x): h, m, r = x.split(':'); s, ms = r.split(','); return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
C = [(ts(x), ts(y), t.strip()) for x, y, t in re.findall(r'(\S+) --> (\S+)\n(.+?)(?:\n\n|\n*$)', open(a.srt, encoding='utf-8').read(), re.S)]
if a.src:
    ns = {}; exec(open(a.src, encoding='utf-8').read(), ns); G = ns['G']
else:
    G = [(i + 1, i + 1, re.sub(r'[呃啊嗯]', '', c[2]), '') for i, c in enumerate(C)]
out = []
for s0, s1, zh, en in G:
    cues = C[s0 - 1:s1]
    out.append(dict(t0=round(cues[0][0], 3), t1=round(cues[-1][1], 3), zh=zh, en=en,
                    sp=[[round(x, 3), round(y, 3), len(re.sub(r'[\s呃啊嗯]', '', t))] for x, y, t in cues]))
for i in range(len(out) - 1):
    if 0 < out[i + 1]['t0'] - out[i]['t1'] < .6: out[i]['t1'] = out[i + 1]['t0']
open(a.out, 'w', encoding='utf-8').write('const SUBS=' + json.dumps(out, ensure_ascii=False) + ';')
print(f'{len(out)} 组字幕 → {a.out}')

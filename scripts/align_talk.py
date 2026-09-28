#!/usr/bin/env python3
"""口播对齐：把"口播成片"（通常是原片 1.1 倍速剪辑，可能已烧字幕）映射回"原片"逐帧。
产出：talk/<clip4>/f_00001.jpg …（原片逐帧图）、talkmap.js（每个输出帧 → 原片帧）、sync_segs.json、voice.wav

用法：
  python3 align_talk.py --master 成片.mov --raw 原片1.MOV 原片2.MOV … --out <anim目录> [--speed auto|1.1] [--fps 60] [--size 720x1280]

原理（来自 EP02/EP03/EP04 历史工作流；新素材需重新验证）：
  1) 音频：40 段对数频带特征，每 0.25s 取一个 1.5s 窗口，在全部原片里滑窗互相关 → 得到 (clip, offset) 的片段
  2) 切点：放在相邻片段交界附近最安静的 10ms
  3) 视频偏移：原片音轨比视频晚 0.16–0.20s，每段用画面逐帧比对求出（不能用 stream start_time 直接替代）
  4) 验证：报告可辨识运动采样点中，预测帧与局部最佳匹配误差 ≤1 帧的比例；不是逐帧完全一致验证
"""
import argparse, json, os, subprocess, sys
import numpy as np

def sh(*a, **k): return subprocess.run(a, check=True, capture_output=True, **k)
def audio(path, sr=16000):
    return np.frombuffer(sh('ffmpeg', '-v', 'error', '-i', path, '-map', '0:a:0', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-').stdout, np.float32)
def gray(path, crop_h_ratio=.68, w=72, h=88):
    vf = f"crop=iw:ih*{crop_h_ratio}:0:0,scale={w}:{h},format=gray"
    b = sh('ffmpeg', '-v', 'error', '-i', path, '-vf', vf, '-f', 'rawvideo', '-').stdout
    return np.frombuffer(b, np.uint8).reshape(-1, h, w).astype(np.float32)
def fps_of(path):
    r = sh('ffprobe', '-v', 'error', '-select_streams', 'v', '-show_entries', 'stream=r_frame_rate', '-of', 'csv=p=0', path).stdout.decode().strip()
    a, b = r.split('/'); return float(a) / float(b)

SR = 16000
def feat(x, hop):
    nf = 512; n = int((len(x) - nf) / hop)
    idx = (np.arange(n) * hop).astype(int)[:, None] + np.arange(nf)[None, :]
    S = np.abs(np.fft.rfft(x[idx] * np.hanning(nf), axis=1)) ** 2
    f = np.fft.rfftfreq(nf, 1 / SR); edges = np.geomspace(80, 6000, 41)
    B = np.stack([S[:, (f >= edges[i]) & (f < edges[i + 1])].sum(1) for i in range(40)], 1)
    B = np.log(B + 1e-6); B -= B.mean(1, keepdims=True); B /= B.std(1, keepdims=True) + 1e-6
    return B.astype(np.float32), np.log(S.sum(1) + 1e-9)

def match_points(master, raws, speed):
    FV, EV = feat(master, 160)
    srcs = {k: feat(v, 160 * speed)[0] for k, v in raws.items()}
    def best(q, F):
        W = len(q); q = (q - q.mean()) / q.std(); n = len(F)
        if n <= W: return -9, 0
        L = 1 << (n + W).bit_length(); num = np.zeros(n - W + 1)
        for b in range(F.shape[1]):
            num += np.fft.irfft(np.fft.rfft(F[:, b], L) * np.conj(np.fft.rfft(q[:, b], L)), L)[:n - W + 1]
        cs = np.cumsum(np.concatenate([[0], (F ** 2).sum(1)]))
        r = num / (np.sqrt(cs[W:] - cs[:n - W + 1]) * np.sqrt((q ** 2).sum()) + 1e-6); i = int(np.argmax(r)); return float(r[i]), i
    W, H = 150, 25; pts = []; voiced = EV > np.percentile(EV, 35)
    for s in range(0, len(FV) - W, H):
        if voiced[s:s + W].mean() < .35: continue
        r, i, k = max(((*best(FV[s:s + W], F), k) for k, F in srcs.items()), key=lambda z: z[0])
        pts.append(dict(t=s / 100, r=r, k=k, c=i * .01 * speed - speed * s / 100))
    return pts

def runs_from(pts):
    runs = []
    for p in pts:
        if runs and runs[-1]['k'] == p['k'] and abs(np.median(runs[-1]['cs']) - p['c']) < .15:
            runs[-1]['b'] = p['t'] + 1.5; runs[-1]['cs'].append(p['c'])
        else: runs.append(dict(k=p['k'], a=p['t'], b=p['t'] + 1.5, cs=[p['c']]))
    runs = [r for r in runs if len(r['cs']) >= 3]          # drop 1–2 point spurious matches
    if runs: runs[0]['a'] = 0.0
    for r in runs: r['c'] = float(np.median(r['cs']))
    return runs

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--master', required=True); ap.add_argument('--raw', nargs='+', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--speed', default='auto'); ap.add_argument('--fps', type=int, default=60); ap.add_argument('--size', default='720x1280')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    names = {os.path.basename(p)[:4]: p for p in a.raw}
    print('· 读取音频'); master = audio(a.master); raws = {k: audio(p) for k, p in names.items()}
    speeds = [1.0, 1.05, 1.1, 1.15, 1.2] if a.speed == 'auto' else [float(a.speed)]
    best = None
    for sp in speeds:
        pts = match_points(master, raws, sp); med = float(np.median([p['r'] for p in pts]))
        print(f'  speed {sp}: median r={med:.3f}')
        if not best or med > best[0]: best = (med, sp, pts)
    _, speed, pts = best; print(f'· 倍速 = {speed}')
    runs = runs_from(pts)
    # cut points at quietest 10 ms near boundaries
    h = 160; n = len(master) // h; e = np.sqrt((master[:n * h].reshape(n, h) ** 2).mean(1)); e = np.convolve(e, np.ones(5) / 5, 'same')
    cuts = [0.0]
    for r0, r1 in zip(runs[:-1], runs[1:]):
        lo, hi = min(r1['a'], r0['b']) - .3, max(r1['a'], r0['b']) + .3
        i0, i1 = max(int(lo * 100), int(cuts[-1] * 100) + 10), min(int(hi * 100), len(e) - 1)
        if i1 <= i0: i0, i1 = int(r1['a'] * 100) - 35, int(r1['a'] * 100) + 35
        cuts.append((i0 + int(np.argmin(e[i0:i1]))) / 100)
    cuts.append(len(master) / SR)
    segs = [dict(k=r['k'], t0=cuts[i], t1=cuts[i + 1], c=r['c']) for i, r in enumerate(runs)]
    # video offset per segment (frame matching)
    print('· 画面偏移校准'); M = gray(a.master); mfps = fps_of(a.master)
    G = {}; rf = {}
    for k in set(s['k'] for s in segs): G[k] = gray(names[k]); rf[k] = fps_of(names[k])
    for s in segs:
        S = G[s['k']]; ts = np.arange(np.ceil(s['t0'] * mfps) + 3, np.floor(s['t1'] * mfps) - 3)[::4] / mfps; best = None
        for d in np.arange(-.40, .401, 1 / 120):
            err = []
            for t in ts:
                sf = (speed * t + s['c'] + d) * rf[s['k']]; i = int(np.floor(sf)); w = sf - i
                if 0 <= i < len(S) - 1: err.append(np.abs(M[int(round(t * mfps))] - (S[i] * (1 - w) + S[i + 1] * w)).mean())
            if err and (not best or np.mean(err) < best[0]): best = (np.mean(err), d)
        s['c'] = round(s['c'] + best[1], 4); print(f"  {s['t0']:7.2f}-{s['t1']:7.2f} {s['k']} offset {best[1] * 1000:+.0f}ms")
    json.dump(dict(speed=speed, segs=segs), open(os.path.join(a.out, 'sync_segs.json'), 'w'), indent=1)
    # extract raw frames
    W, Hh = a.size.split('x'); F = sorted(set(s['k'] for s in segs))
    for k in F:
        d = os.path.join(a.out, 'talk', k); os.makedirs(d, exist_ok=True)
        if not os.listdir(d): sh('ffmpeg', '-v', 'error', '-y', '-i', names[k], '-vf', f'scale={W}:{Hh}:flags=lanczos', '-q:v', '3', os.path.join(d, 'f_%05d.jpg'))
    # talkmap
    N = int(len(master) / SR * a.fps) + 1; arr = []
    for i in range(N):
        v = i / a.fps; s = next((x for x in segs if x['t0'] <= v < x['t1']), segs[-1])
        arr.append([F.index(s['k']), max(1, int(round((speed * v + s['c']) * rf[s['k']])) + 1)])
    open(os.path.join(a.out, 'talkmap.js'), 'w').write('const TALKF=' + json.dumps(F) + ';const TALKMAP=' + json.dumps(arr, separators=(',', ':')) + ';')
    sh('ffmpeg', '-v', 'error', '-y', '-i', a.master, '-map', '0:a:0', '-ar', '44100', '-ac', '2', os.path.join(a.out, 'voice.wav'))
    # verify
    ok = tot = 0
    for s in segs:
        S = G[s['k']]
        for mi in range(int(np.ceil(s['t0'] * mfps)) + 1, int(np.floor(s['t1'] * mfps)) - 1, 2):
            t = mi / mfps; j = int(round((speed * t + s['c']) * rf[s['k']]))
            e2 = sorted((np.abs(M[mi] - S[q]).mean(), q) for q in range(j - 4, j + 5) if 0 <= q < len(S))
            if len(e2) > 1 and e2[1][0] - e2[0][0] > .15: tot += 1; ok += abs(e2[0][1] - j) <= 1
    print(f'· 验证：{ok}/{tot} 个运动采样点误差 ≤1 帧 ({ok / max(tot, 1) * 100:.1f}%)')
    print('· 完成：talkmap.js / sync_segs.json / talk/ / voice.wav')
if __name__ == '__main__': main()

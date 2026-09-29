"""每集配乐 + 音效。只改这里的 MUSIC / SEC / ENV / HITS 四块。
运行前：node scripts/dump_sfx.mjs index.html sfx.json（从 scenes.js 里的 S() 调用导出音效点）
输出：bgm.wav（配乐，已带音量曲线）、sfx.wav（音效）"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
skill_root = os.environ.get('ADU_MOTION_VIDEO_ROOT')
if skill_root:
    sys.path.insert(0, os.path.join(skill_root, 'scripts'))
import numpy as np
try:
    import audiolib as A
except ModuleNotFoundError as exc:
    raise SystemExit('Run audio.py through pipeline.sh audio, or set ADU_MOTION_VIDEO_ROOT to the installed skill directory.') from exc

D = json.load(open(os.path.join(HERE, 'sfx.json'))); END = D['end']; N = A.init(END); SR = A.SR

# ---------------- 1) 配乐来源 ----------------
# 'track'：用户提供的配乐（优先用这个）；'synth'：代码合成的原创配乐（没有提供配乐时用）
MUSIC = dict(mode='synth', path=os.path.join(HERE, 'assets', 'music.mp3'), offset=0.0)
#   offset：从歌曲第几秒开始。把歌曲的起鼓点对齐到画面第一个大切点：offset = 起鼓秒数 - 画面切点秒数

# ---------------- 2) synth 模式的段落：(开始, 结束, 能量 0–1, 选项) 或 ('piano', 开始, 结束) ----------------
SEC = [
    (0.0, 6.0, .5, dict(kick_on=False, clapon=False)),
    (6.0, END, .85, dict()),
]
# ---------------- 3) 音量曲线 [(秒, dB)]：说话密集处 -3…-5，段落转换/高潮 +4…+7，情绪低落段整段 -3 ----------------
ENV = [(0, 0), (END, 0)]
# ---------------- 4) 重拍：镲片 + 重低音下沉 + 上升音（不带音高的效果，可以叠加在用户配乐上） ----------------
HITS = dict(crash=[], drop=[], riser=[])     # riser 写成 (开始, 结束)
DARK = []                                    # [(开始, 结束)]：这段低通处理，声音变暗（比如"打击"类情绪段）

music = np.zeros((N, 2))
if MUSIC['mode'] not in ('track', 'synth'):
    raise SystemExit('MUSIC.mode must be track or synth')
if MUSIC['mode'] == 'track':
    if not os.path.isfile(MUSIC['path']):
        raise SystemExit('Requested music track is missing: ' + MUSIC['path'])
    ext = A.load_track(MUSIC['path'], MUSIC['offset'])
    tt = np.arange(N) / SR
    for a0, b0 in DARK:
        w = np.clip((tt - a0) / .8, 0, 1) * np.clip((b0 - tt) / .35, 0, 1)
        dark = np.stack([A.lowpass(ext[:, c], 900) for c in range(2)], 1)
        ext = ext * (1 - w[:, None]) + dark * w[:, None] * 1.15
    music = ext / (np.max(np.abs(ext)) + 1e-9) * .9
else:
    A.music = music; bar = 0
    for sec in SEC:
        if sec[0] == 'piano':
            for tb in A.bars(sec[1], sec[2]): A.piano_bar(tb, bar, sec[2]); bar += 1
            continue
        a0, b0, lvl, kw = sec
        for tb in A.bars(a0, b0): A.mbar(tb, bar, lvl, b0, **kw); bar += 1
fx = np.zeros((N, 2))
for t in HITS['drop']: A.add(fx, A.pan(A.sub_drop(1.1, .5), 0), t)
for a0, b0 in HITS['riser']: A.add(fx, A.pan(A.riser(b0 - a0, .14), 0), a0)
for t in HITS['crash']: A.add(fx, A.pan(A.crash_cym(), (t % 2) - .5), t)
music = (music + fx * .6) * A.env_curve(ENV)[:, None]
fade = np.ones(N); i0 = max(0, int((END - .8) * SR)); fade[i0:] = np.clip(1 - (np.arange(N - i0) / SR) / .8, 0, 1) ** 1.3
music *= fade[:, None]

sfx = A.render_sfx(D['sfx'])
music = A.reverb(music, 1.1, .12); sfx = A.reverb(sfx, .9, .12)
music /= np.max(np.abs(music)) * 1.1 + 1e-9; sfx /= np.max(np.abs(sfx)) * 1.1 + 1e-9
A.write_wav(os.path.join(HERE, 'bgm.wav'), music); A.write_wav(os.path.join(HERE, 'sfx.wav'), sfx)
print('ok', N / SR)

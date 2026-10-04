"""本期配乐与动作音效；明确选择新配乐，旧默认合成底乐已停用。
先导出 sfx.json。输出 bgm.wav / sfx.wav，保留动作起音、长度与尾音。
"""
import json
import os
from pathlib import Path
import sys
import numpy as np
HERE = Path(__file__).resolve().parent
skill_root = os.environ.get('ADU_MOTION_VIDEO_ROOT')
if skill_root:
    sys.path.insert(0, str(Path(skill_root) / 'scripts'))
try:
    import audiolib as A
    from music_policy import selection, POLICY, sha
    from macro_audio import load_track
except ModuleNotFoundError as exc:
    raise SystemExit('Use pipeline.sh audio, or set ADU_MOTION_VIDEO_ROOT to the installed skill directory.') from exc

# Choose the episode's registered/licensed track and measured start.
# Explicit MUSIC=dict(mode='none') omits background only; action SFX remain.
MUSIC = dict(mode='track', path='', offset=None)
ENV = []                      # measured episode gain envelope [(second, dB)]
HITS = dict(crash=[], drop=[], riser=[])
DARK = []

D = json.loads((HERE / 'sfx.json').read_text())
END = D['end']; N = A.init(END); SR = A.SR
music_config, _ = selection(MUSIC, HERE, END)
A.rng = np.random.default_rng(11)
music = np.zeros((N, 2))
if music_config['mode'] == 'track':
    music = load_track(Path(music_config['path']), music_config['offset'], END)
    tt = np.arange(N) / SR
    for a, b in DARK:
        w = np.clip((tt-a)/.8,0,1) * np.clip((b-tt)/.35,0,1)
        dark = np.stack([A.lowpass(music[:,c],900) for c in range(2)],1)
        music = music * (1-w[:,None]) + dark * w[:,None] * 1.15
    for t in HITS['drop']: A.add(music,A.pan(A.sub_drop(1.1,.5),0),t,.6)
    for a,b in HITS['riser']: A.add(music,A.pan(A.riser(b-a,.14),0),a,.6)
    for t in HITS['crash']: A.add(music,A.pan(A.crash_cym(),(t%2)-.5),t,.6)
if ENV: music *= A.env_curve(ENV)[:,None]
# Keep deterministic action sound independent of track/filters/music accents.
A.rng = np.random.default_rng(11)
sfx = A.reverb(A.render_sfx(D['sfx']),.9,.12)
music = A.reverb(music,1.1,.12)
samples = round(END*SR)
for name,data in [('bgm',music),('sfx',sfx)]:
    data=data[:samples];data/=max(np.max(np.abs(data))*1.1,1e-9)
    A.write_wav(str(HERE/(name+'.wav')),data)
report=dict(mode=music_config['mode'],musicPolicy=POLICY,trackSha256=music_config.get('sha256'),
            bgmSha256=sha(HERE/'bgm.wav'),sfxSha256=sha(HERE/'sfx.wav'),
            sfxRandomPolicy='adu-sfx-independent-seed11/1',duration=END,sfx=len(D['sfx']),
            review='Structure rendered; continuous listening still required')
(HERE/'macro_audio_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report))

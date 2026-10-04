"""Bind one episode track and globally synthesize untruncated action SFX tails."""
import json
from pathlib import Path
import numpy as np
import audiolib as A
from macro_audio import load_track
from adaptation_audio import audio_boundary_report


def render(project: Path):
    plan = json.loads((project / 'macro_plan.json').read_text())
    cues = json.loads((project / 'sfx.json').read_text())
    end = plan['end_frame']/plan['fps']
    if abs(cues['end']-end) > .5/plan['fps']: raise ValueError('Composite SFX clock differs from narration')
    unknown = {c['type'] for c in cues['sfx']} - A.GEN.keys()
    if unknown: raise ValueError('Unknown composite SFX generators: ' + str(unknown))
    from music_policy import selection, POLICY, sha
    music_config,_ = selection(json.loads((project/'macro_music.json').read_text()), project)
    A.init(end); A.rng = np.random.default_rng(11)
    total = round(end*A.SR)
    music = np.zeros((total,2))
    if music_config['mode'] == 'track':
        music = load_track(project/music_config['path'], music_config['offset'], end)[:total]
    # Root output includes full tails,
    # even when an effect's generator extends into a different authored pack.
    A.init(end); A.rng=np.random.default_rng(11)
    sfx=A.reverb(A.render_sfx(cues['sfx']),.9,.12)[:total]
    for name,data in [('bgm',music),('sfx',sfx)]:
        data/=max(np.max(np.abs(data))*1.1,1e-9)
        A.write_wav(str(project/(name+'.wav')),data)
    report=dict(mode=music_config['mode'], musicPolicy=POLICY, trackSha256=music_config.get('sha256'),
                bgmSha256=sha(project/'bgm.wav'),sfxSha256=sha(project/'sfx.wav'),
                sfxRandomPolicy='adu-sfx-independent-seed11/1',duration=end,
                parts=len(plan['parts']),sfx=len(cues['sfx']),sampleRate=A.SR,voiceRetimed=False,
                boundaryPolicy='one explicit full-timeline track; global SFX tails; no per-pack BGM fallback',
                review='experimental; continuous viewing/listening still required')
    (project/'macro_audio_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (project/'audio_boundary_report.json').write_text(json.dumps(audio_boundary_report(plan,cues),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

"""Compose frozen per-pack scores and globally synthesize untruncated SFX tails."""
import json
from pathlib import Path
import subprocess
import sys
import wave
import numpy as np
import audiolib as A
from macro_audio import load_track
from adaptation_audio import audio_boundary_report


def read_wav(path):
    with wave.open(str(path), 'rb') as src:
        if src.getsampwidth() != 2 or src.getnchannels() != 2 or src.getframerate() != A.SR:
            raise ValueError('Part music needs stereo PCM at the frozen score sample rate')
        return np.frombuffer(src.readframes(src.getnframes()), '<i2').reshape(-1,2).astype(float)/32768


def render(project: Path):
    plan = json.loads((project / 'macro_plan.json').read_text())
    cues = json.loads((project / 'sfx.json').read_text())
    end = plan['end_frame']/plan['fps']
    if abs(cues['end']-end) > .5/plan['fps']: raise ValueError('Composite SFX clock differs from narration')
    unknown = {c['type'] for c in cues['sfx']} - A.GEN.keys()
    if unknown: raise ValueError('Unknown composite SFX generators: ' + str(unknown))
    music_config = json.loads((project/'macro_music.json').read_text())
    A.init(end); A.rng = np.random.default_rng(11)
    total = round(end*A.SR)
    music = np.zeros((total,2))
    if music_config['mode'] == 'track':
        music = load_track(project/music_config['path'], music_config['offset'], end)[:total]
    else:
        # Keep each group's frozen instrumentation/mix profile. Style boundaries
        # are explicit editorial cuts with 120ms gain ramps, no time shift.
        for part in plan['parts']:
            child = project/part['path']
            events = [{'t':c['t']-part['startFrame']/plan['fps'], **{k:v for k,v in c.items() if k!='t'}}
                      for c in cues['sfx'] if part['startFrame']/plan['fps'] <= c['t'] < part['endFrame']/plan['fps']]
            (child/'sfx.json').write_text(json.dumps(dict(end=(part['endFrame']-part['startFrame'])/plan['fps'],sfx=events)))
            subprocess.run([sys.executable,str(child/'audio.py')],check=True,capture_output=True)
            data=read_wav(child/'bgm.wav')
            a,b=round(part['startFrame']/plan['fps']*A.SR),round(part['endFrame']/plan['fps']*A.SR)
            if len(data)!=b-a: raise ValueError('Part music clock differs from its output frames')
            ramp=min(round(.12*A.SR),len(data))
            if a: data[:ramp]*=np.linspace(0,1,ramp)[:,None]
            if b<total: data[-ramp:]*=np.linspace(1,0,ramp)[:,None]
            music[a:b]=data
    # Reinitialize after child subprocesses; root output includes full tails,
    # even when an effect's generator extends into a different authored pack.
    A.init(end); A.rng=np.random.default_rng(11)
    sfx=A.reverb(A.render_sfx(cues['sfx']),.9,.12)[:total]
    for name,data in [('bgm',music),('sfx',sfx)]:
        data/=max(np.max(np.abs(data))*1.1,1e-9)
        A.write_wav(str(project/(name+'.wav')),data)
    report=dict(mode='track' if music_config['mode']=='track' else 'per-pack-source-scores',duration=end,
                parts=len(plan['parts']),sfx=len(cues['sfx']),sampleRate=A.SR,voiceRetimed=False,
                boundaryPolicy='independent visual cut; source music 120ms gain ramps; global SFX tails',
                review='experimental; continuous viewing/listening still required')
    (project/'macro_audio_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (project/'audio_boundary_report.json').write_text(json.dumps(audio_boundary_report(plan,cues),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

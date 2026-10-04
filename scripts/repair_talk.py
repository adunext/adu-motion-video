#!/usr/bin/env python3
"""Conservative optional narration repair. Off does no media I/O or scanning.

Basic only cuts explicitly confirmed blank windows after full normalized-image,
individual-channel digital-silence, subtitle, PTS-support and anchor checks.
Low volume, static pictures and ASR gaps never authorize a cut.
"""
from pathlib import Path
from copy import deepcopy
import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import tempfile
import wave

from adapt_project import parse_srt
from color_management import fingerprint_file
from import_talk import run, input_timing
from narration_edit_map import create_map, fingerprint, validate_edit_map, quantize_cut, normalize_intake_anchors
from retime_subtitles import identity as subtitle_identity, retime

ROOT=Path(__file__).resolve().parents[1]
RECIPE='adu-confirmed-black-digital-silence-60-48/1'


def require(ok,message):
    if not ok:raise ValueError(message)


def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def tree_identity(root):
    h=hashlib.sha256();count=0
    for p in sorted(Path(root).rglob('*.jpg')):
        record=p.relative_to(root).as_posix()+':'+fingerprint_file(p)['sha256']+'\n'
        h.update(record.encode());count+=1
    return dict(sha256=h.hexdigest(),frames=count)


def probe_source(source):
    p=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',source]))
    video=[s for s in p['streams'] if s['codec_type']=='video'];audio=[s for s in p['streams'] if s['codec_type']=='audio']
    require(len(video)==1 and len(audio)==1,'Basic keeps sources with ambiguous/missing video or audio tracks')
    require(audio[0].get('channels') in (1,2),'Basic requires an explicitly selected mono/stereo narration track')
    timing=input_timing(p,60);require(timing['frames']<=36000,'Basic scan budget is 10 minutes; keep this source or use a reviewed shorter input')
    require(timing['videoStartSeconds']<=1/60 and timing['audioStartSeconds']<=1/60,'Basic keeps unmatched A/V start offsets; align the source first')
    frames=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,duration_time','-of','json',source]))['frames']
    origin=float(p['format'].get('start_time') or 0)
    pts=[float(f['best_effort_timestamp_time'])-origin for f in frames]
    require(pts and all(math.isfinite(t) for t in pts) and all(b>a for a,b in zip(pts,pts[1:])),'Source presentation PTS are not ordered')
    end=pts[-1]+float(frames[-1].get('duration_time') or 1/60)
    require(abs(end-timing['duration'])<=1/60+.00001,'Source PTS endpoint differs from normalization clock; keep this input')
    return p,timing,pts,end


def normalize(source,target):
    target.mkdir()
    run([os.environ.get('ADU_PYTHON') or __import__('sys').executable,ROOT/'scripts/import_talk.py',target,source,'--fps','60'])
    imported=json.loads((target/'import.json').read_text());n=imported['frames']
    channels=target/'channels.f32'
    run(['ffmpeg','-v','error','-n','-i',source,'-map','0:a:0','-vn','-af',f'aresample=48000:first_pts=0,apad,atrim=end_sample={800*n}','-ar','48000','-c:a','pcm_f32le','-f','f32le',channels])
    return imported


def read_pcm(path):
    import numpy as np
    with wave.open(str(path),'rb') as f:
        require(f.getframerate()==48000 and f.getsampwidth()==2,'Repair PCM must be 48kHz signed 16-bit')
        return np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').reshape(-1,f.getnchannels()).copy()


def plan(source,*,mode='off',confirmed_blank=None,srt=None,anchors=None):
    if mode=='off':return dict(schema='adu-repair-plan/1',mode='off',status='off',cutsApplied=False,scanPerformed=False)
    require(mode=='basic','Repair mode must be off or basic')
    source=Path(source).resolve();require(source.is_file(),'Missing narration source')
    anchors=deepcopy(anchors or []);windows=confirmed_blank or []
    if not windows:return dict(schema='adu-repair-plan/1',mode='basic',status='no-change',cutsApplied=False,reason='No explicitly confirmed blank windows; low-volume or black candidates alone are insufficient',scanPerformed=False)
    for w in windows:
        require(isinstance(w,dict) and w.get('confirmedNoMeaningfulContent') is True and isinstance(w.get('reason'),str) and w['reason'].strip(),'Each blank window needs explicit content confirmation and reason')
        require(0<=w['start']<w['end'],'Invalid blank window')
    initial=fingerprint_file(source)
    try:p,timing,pts,pts_end=probe_source(source)
    except ValueError as exc:return dict(schema='adu-repair-plan/1',mode='basic',status='no-change',cutsApplied=False,source=initial,reason=str(exc),scanPerformed=False)
    cues=parse_srt(Path(srt)) if srt else []
    transcript=subtitle_identity(srt) if srt else None
    cuts=[];checks=[]
    from PIL import Image
    import numpy as np
    with tempfile.TemporaryDirectory(prefix='adu-repair-plan-') as temp:
        master=Path(temp)/'normalized';report=normalize(source,master);pcm=np.fromfile(master/'channels.f32',dtype='<f4').reshape(-1,next(s for s in p['streams'] if s['codec_type']=='audio')['channels']);voice=read_pcm(master/'voice.wav')
        require(len(pcm)==len(voice)==timing['frames']*800,'Normalized PCM does not match frame grid')
        for w in windows:
            # Margins around interior pauses are preserved; a confirmed leading
            # black head may start at zero. Quantization only shrinks approval.
            a,b=quantize_cut(w['start']+(0 if w['start']==0 else .2),w['end']-.2)
            reason=None
            if a>=b or b>timing['frames']:reason='Too short or outside source grid'
            elif any(c['start']<b/60 and c['end']>a/60 for c in cues):reason='Complete subtitle cue protected'
            elif any(x.get('clock')=='narration-source' and ((a/60<=x.get('point',-1)<b/60) or ('span' in x and x['span'][0]<b/60 and x['span'][1]>a/60)) for x in anchors):reason='Locked narration anchor protected'
            elif not np.isfinite(pcm[a*800:b*800]).all() or np.max(np.abs(pcm[a*800:b*800]))>0:reason='Original audio channels contain content; digital silence required'
            else:
                # All source display supports touched by removal must be wholly
                # in approval, including VFR/nearest-frame resampling edges.
                for j,start in enumerate(pts):
                    stop=pts[j+1] if j+1<len(pts) else pts_end
                    if start<b/60 and stop>a/60 and not (w['start']<=start and stop<=w['end']+1e-9):
                        reason='Actual source display support extends beyond confirmed blank';break
                if not reason:
                    for f in range(a+1,b+1):
                        with Image.open(master/'talk/clip_000'/f'f_{f:05d}.jpg') as image:
                            if max(image.convert('RGB').getextrema(),key=lambda q:q[1])[1]>8:
                                reason='Meaningful/non-black picture retained (full frame checked)';break
                if not reason and a and b<len(pcm)//800:
                    jump=np.abs(voice[a*800-1].astype(np.int32)-voice[b*800].astype(np.int32))
                    if max(jump)>64:reason='Cut would create a PCM discontinuity; cut cancelled'
            checks.append(dict(request=w,quantizedFrames=[a,b],status='kept' if reason else 'cut',reason=reason))
            if not reason:cuts.append((a,b))
        normalized=dict(recipe=RECIPE,frames=tree_identity(master/'talk'),voice=fingerprint_file(master/'voice.wav'),channels=fingerprint_file(master/'channels.f32'),color=report['color'],ptsSha256=hashlib.sha256(json.dumps(pts).encode()).hexdigest())
    require(fingerprint_file(source)==initial,'Source changed during repair plan')
    if srt:require(subtitle_identity(srt)==transcript,'SRT changed during plan')
    # Reject overlapping approvals rather than silently merging user windows.
    require(all(b<=c for (_,b),(c,_) in zip(sorted(cuts),sorted(cuts)[1:])),'Confirmed cuts overlap')
    if not cuts:return dict(schema='adu-repair-plan/1',mode='basic',status='no-change',source=initial,cutsApplied=False,scanPerformed=True,checks=checks)
    metadata=dict(**initial,path=str(source),streamIdentity=p['streams'],commonOrigin=p['format'].get('start_time','0'),normalization=normalized)
    edit=create_map(metadata,timing['frames'],cuts,transcript_identity=transcript,anchors=anchors)
    # Rounding of an anchor into another kept span cancels that cut; it never
    # moves the user's event to a different spoken moment.
    try:mapped=normalize_intake_anchors(edit,anchors)
    except ValueError as exc:return dict(schema='adu-repair-plan/1',mode='basic',status='no-change',source=initial,cutsApplied=False,scanPerformed=True,checks=checks,reason=str(exc))
    edit.update(requestedWindows=windows,subtitleSource=str(Path(srt).resolve()) if srt else None)
    edit['fingerprint']=fingerprint(edit);validate_edit_map(edit)
    mapped=normalize_intake_anchors(edit,anchors)
    return dict(schema='adu-repair-plan/1',mode='basic',status='ready',cutsApplied=False,scanPerformed=True,checks=checks,editMap=edit,normalizedAnchors=mapped)


def validate_master(map_path,source=None):
    path=Path(map_path).resolve();edit=validate_edit_map(json.loads(path.read_text()))
    root=path.parent;receipt=json.loads((root/'repair_receipt.json').read_text())
    require(receipt.get('mapFingerprint')==edit['fingerprint'],'Repair receipt uses a different map')
    if source is not None:require(fingerprint_file(Path(source))=={k:edit['source'][k] for k in ['sha256','sizeBytes']},'Original narration differs from edit map')
    require(tree_identity(root/'talk')==receipt['framesIdentity'],'Edited frames changed')
    require(fingerprint_file(root/'voice.wav')==receipt['voiceIdentity'],'Edited PCM changed')
    pcm=read_pcm(root/'voice.wav');require(len(pcm)==edit['editedSamples'],'Edited PCM length mismatch')
    if edit.get('subtitleSource'):
        require(subtitle_identity(edit['subtitleSource'])==edit['transcriptIdentity'],'Original SRT changed since repair')
        require(fingerprint_file(root/'edited.srt')==receipt['editedSubtitleIdentity'],'Edited SRT changed')
    return edit,root


def apply(plan_value,target,*,mode='off'):
    if mode=='off':return dict(status='off',cutsApplied=False,scanPerformed=False)
    require(mode=='basic' and plan_value.get('mode')=='basic','Explicit basic mode required for this invocation')
    if plan_value.get('status')=='no-change':return dict(status='no-change',cutsApplied=False)
    require(plan_value.get('status')=='ready','Not a ready repair plan')
    edit=validate_edit_map(deepcopy(plan_value['editMap']));source=Path(edit['source']['path']);target=Path(target).absolute()
    require(not target.exists() and not target.is_symlink(),'Refusing existing repair target')
    require(target.parent.is_dir(),'Repair target parent missing')
    require(fingerprint_file(source)=={k:edit['source'][k] for k in ['sha256','sizeBytes']},'Source changed since repair plan')
    if edit.get('subtitleSource'):require(subtitle_identity(edit['subtitleSource'])==edit['transcriptIdentity'],'SRT changed since repair plan')
    with tempfile.TemporaryDirectory(prefix='.adu-repair-',dir=target.parent) as temp:
        temp=Path(temp);master=temp/'normalized';report=normalize(source,master)
        norm=edit['source']['normalization']
        require(tree_identity(master/'talk')==norm['frames'] and fingerprint_file(master/'voice.wav')==norm['voice'] and fingerprint_file(master/'channels.f32')==norm['channels'],'Normalization changed since plan; replan')
        stage=temp/'edited';(stage/'talk/clip_000').mkdir(parents=True);index=1
        with wave.open(str(master/'voice.wav'),'rb') as src, wave.open(str(stage/'voice.wav'),'wb') as dst:
            dst.setparams(src.getparams())
            for k in edit['kept']:
                src.setpos(k['sourceStartSample']);dst.writeframes(src.readframes(k['sourceEndSample']-k['sourceStartSample']))
                for f in range(k['sourceStartFrame']+1,k['sourceEndFrame']+1):
                    shutil.copy2(master/'talk/clip_000'/f'f_{f:05d}.jpg',stage/'talk/clip_000'/f'f_{index:05d}.jpg');index+=1
        require(index-1==edit['editedFrames'],'Edited frame count mismatch')
        report.update(frames=edit['editedFrames'],duration=edit['editedFrames']/60,editMapFingerprint=edit['fingerprint'],clock='edited-narration',cutsApplied=True,playbackRateChanged=False)
        write(stage/'import.json',report);write(stage/'narration_edit_map.json',edit)
        (stage/'talkmap.js').write_text('const TALKF=["clip_000"];const TALKMAP='+json.dumps([[0,i+1] for i in range(edit['editedFrames'])],separators=(',',':'))+';\n')
        receipt=dict(schema='adu-repair-receipt/1',mapFingerprint=edit['fingerprint'],framesIdentity=tree_identity(stage/'talk'),voiceIdentity=fingerprint_file(stage/'voice.wav'),cutsApplied=True,playbackRateChanged=False,pcmPolicy='unchanged kept normalized samples; no fades or crossfades',subtitles='absent',normalizedAnchors=normalize_intake_anchors(edit,edit['anchors']))
        if edit.get('subtitleSource'):
            original=Path(edit['subtitleSource']);shutil.copy2(original,stage/'original.srt')
            text,mapping=retime(original,edit);(stage/'edited.srt').write_text(text);write(stage/'subtitle_edit_receipt.json',mapping)
            receipt.update(editedSubtitleIdentity=fingerprint_file(stage/'edited.srt'),subtitles='whole cues mapped; original bytes retained')
        write(stage/'repair_receipt.json',receipt)
        require(fingerprint_file(source)=={k:edit['source'][k] for k in ['sha256','sizeBytes']},'Source changed during repair apply')
        validate_master(stage/'narration_edit_map.json',source)
        require(not target.exists(),'Repair target appeared during apply');stage.rename(target)
    return dict(status='applied',output=str(target),editMap=str(target/'narration_edit_map.json'),frames=edit['editedFrames'],samples=edit['editedSamples'],cutsApplied=True,playbackRateChanged=False)


def install_master(map_path,source,stage):
    edit,master=validate_master(map_path,source);stage=Path(stage)
    mapping=stage/'talkmap.js'
    if mapping.is_file():
        require(mapping.read_text().strip()=='// Optional data absent. Generated data may replace this stub.', 'Existing narration mapping is protected')
    for name in ['voice.wav','import.json','narration_edit_map.json','repair_receipt.json']:
        require(not (stage/name).exists(),'Refusing to apply repair twice: '+name);shutil.copy2(master/name,stage/name)
    require(not (stage/'talk/clip_000').exists(),'Narration already imported')
    shutil.copytree(master/'talk/clip_000',stage/'talk/clip_000');shutil.copy2(master/'talkmap.js',stage/'talkmap.js')
    for name in ['original.srt','edited.srt','subtitle_edit_receipt.json']:
        if (master/name).is_file():shutil.copy2(master/name,stage/name)
    return edit


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('plan');q.add_argument('source',type=Path);q.add_argument('output',type=Path);q.add_argument('--mode',choices=['off','basic'],default='off');q.add_argument('--confirmed-blank',type=Path);q.add_argument('--srt',type=Path);q.add_argument('--anchors',type=Path)
    q=sub.add_parser('apply');q.add_argument('plan',type=Path);q.add_argument('output',type=Path);q.add_argument('--mode',choices=['off','basic'],default='off')
    a=p.parse_args()
    if a.command=='plan':
        # Off must not open even an invalid old map, subtitle or candidate file.
        data=plan(a.source,mode=a.mode,confirmed_blank=json.loads(a.confirmed_blank.read_text()) if a.mode=='basic' and a.confirmed_blank else None,srt=a.srt if a.mode=='basic' else None,anchors=json.loads(a.anchors.read_text()) if a.mode=='basic' and a.anchors else None)
        with a.output.open('x') as f:json.dump(data,f,ensure_ascii=False,indent=2)
        print(json.dumps(dict(status=data['status'],cutsApplied=False)))
    else:
        data=apply(json.loads(a.plan.read_text()) if a.mode=='basic' else {},a.output,mode=a.mode);print(json.dumps(data,ensure_ascii=False))

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.CalledProcessError) as exc:raise SystemExit('Repair failed: '+str(exc)) from exc

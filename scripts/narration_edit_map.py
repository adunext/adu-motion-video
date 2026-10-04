"""One immutable 60fps/48kHz narration edit map, separate from scene clocks."""
from copy import deepcopy
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP
import hashlib
import json
import math

SCHEMA='adu-narration-edit-map/1'


def check(condition,message):
    if not condition:raise ValueError(message)


def fingerprint(value):
    core={k:v for k,v in value.items() if k not in {'fingerprint','receipt','outputs'}}
    return hashlib.sha256(json.dumps(core,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def create_map(source,total_frames,removed,*,transcript_identity=None,anchors=None):
    check(type(total_frames) is int and total_frames>0,'Source needs positive normalized frame count')
    check(isinstance(source,dict) and isinstance(source.get('sha256'),str) and len(source['sha256'])==64,'Source identity is required')
    removed=sorted(removed);previous=0;kept=[];output=0
    for a,b in removed:
        check(type(a) is int and type(b) is int and previous<=a<b<=total_frames,'Cuts must be ordered disjoint normalized frame spans')
        if a>previous:
            kept.append(dict(sourceStartFrame=previous,sourceEndFrame=a,editedStartFrame=output,editedEndFrame=output+a-previous,
                sourceStartSample=800*previous,sourceEndSample=800*a,editedStartSample=800*output,editedEndSample=800*(output+a-previous)))
            output+=a-previous
        previous=b
    if previous<total_frames:
        kept.append(dict(sourceStartFrame=previous,sourceEndFrame=total_frames,editedStartFrame=output,editedEndFrame=output+total_frames-previous,
            sourceStartSample=800*previous,sourceEndSample=800*total_frames,editedStartSample=800*output,editedEndSample=800*(output+total_frames-previous)))
        output+=total_frames-previous
    check(output>0,'Refusing empty narration')
    result=dict(schema=SCHEMA,source=deepcopy(source),fps=60,sampleRate=48000,samplesPerFrame=800,
        sourceFrames=total_frames,editedFrames=output,editedSamples=output*800,
        kept=kept,removed=[dict(startFrame=a,endFrame=b) for a,b in removed],
        transcriptIdentity=transcript_identity,anchors=deepcopy(anchors or []))
    result['fingerprint']=fingerprint(result)
    validate_edit_map(result);return result


def validate_edit_map(value):
    check(isinstance(value,dict) and value.get('schema')==SCHEMA,'Invalid narration map schema')
    check(value.get('fps')==60 and value.get('sampleRate')==48000 and value.get('samplesPerFrame')==800,'Basic repair only supports 60fps/48kHz')
    check(value.get('fingerprint')==fingerprint(value),'Narration map core identity changed')
    previous=0;edited=0;partition=[]
    for k in value.get('kept',[]):
        a,b=k['sourceStartFrame'],k['sourceEndFrame']
        check(type(a) is int and type(b) is int and previous<=a<b<=value['sourceFrames'],'Invalid kept source spans')
        n=b-a
        check(k['editedStartFrame']==edited and k['editedEndFrame']==edited+n,'Edited spans are not contiguous')
        for field,expected in [('sourceStartSample',800*a),('sourceEndSample',800*b),('editedStartSample',800*edited),('editedEndSample',800*(edited+n))]:
            check(k[field]==expected,'Frame/PCM boundary mismatch: '+field)
        partition.append((a,b));previous=b;edited+=n
    check(edited==value['editedFrames']>0 and value['editedSamples']==edited*800,'Edited totals mismatch')
    for cut in value.get('removed',[]):partition.append((cut['startFrame'],cut['endFrame']))
    cursor=0
    for a,b in sorted(partition):
        check(type(a) is int and type(b) is int and a==cursor and a<b,'Kept/removed spans do not partition source')
        cursor=b
    check(cursor==value['sourceFrames'],'Source coverage incomplete')
    return value


def quantize_cut(start,end):
    """Shrink proposed deletions; never remove content outside approval."""
    check(math.isfinite(start) and math.isfinite(end) and 0<=start<end,'Invalid proposed cut')
    return int((Decimal(str(start))*60).to_integral_value(rounding=ROUND_CEILING)),int((Decimal(str(end))*60).to_integral_value(rounding=ROUND_FLOOR))


def map_point(value,seconds):
    validate_edit_map(value);frame=Decimal(str(seconds))*60
    for k in value['kept']:
        if k['sourceStartFrame']<=frame<k['sourceEndFrame']:
            return float((frame-k['sourceStartFrame']+k['editedStartFrame'])/60)
    raise ValueError('Point lies in deleted narration or at exclusive endpoint')


def map_span(value,start,end):
    validate_edit_map(value);a,b=Decimal(str(start))*60,Decimal(str(end))*60
    check(a<b,'Invalid anchor span')
    for k in value['kept']:
        if k['sourceStartFrame']<=a<b<=k['sourceEndFrame']:
            delta=k['editedStartFrame']-k['sourceStartFrame'];return float((a+delta)/60),float((b+delta)/60)
    raise ValueError('Span crosses deleted content; protect the whole requested window')


def inverse_point(value,seconds,*,side='entering'):
    validate_edit_map(value);check(side in {'entering','leaving'},'Inverse side must be entering or leaving')
    frame=Decimal(str(seconds))*60
    check(0<=frame<=value['editedFrames'],'Point outside edited narration')
    units=value['kept'] if side=='entering' else list(reversed(value['kept']))
    for k in units:
        inside=k['editedStartFrame']<=frame<k['editedEndFrame'] if side=='entering' else k['editedStartFrame']<frame<=k['editedEndFrame']
        if inside:return float((frame-k['editedStartFrame']+k['sourceStartFrame'])/60)
    raise ValueError('Exclusive endpoint has no entering frame')


def normalize_intake_anchors(value,anchors):
    validate_edit_map(value);output=[]
    for original in anchors:
        a=deepcopy(original);clock=a.get('clock');check(a.get('id'),'Anchor needs stable id')
        if clock=='asset-source':output.append(a);continue
        if clock=='edited-narration':
            check(a.get('mapFingerprint') in {None,value['fingerprint']},'Anchor uses a different edit map')
            output.append(a);continue
        check(clock=='narration-source','Declare narration-source/edited-narration/asset-source clock')
        check(a.get('sourceSha256')==value['source']['sha256'],'Anchor source identity differs')
        check(not a.get('mapFingerprint'),'Refusing double mapping')
        if 'point' in a:
            point=map_point(value,a['point']);f=int((Decimal(str(point))*60).to_integral_value(rounding=ROUND_HALF_UP))
            # The actual rendered frame must remain in the same kept segment.
            k=next(k for k in value['kept'] if k['sourceStartFrame']/60<=a['point']<k['sourceEndFrame']/60)
            check(k['editedStartFrame']<=f<k['editedEndFrame'],'Anchor rounds across a cut; cancel or explicitly revise that cut')
            a['point']=point;a['outputFrame']=f
        elif 'span' in a:
            a['span']=list(map_span(value,*a['span']))
        else:raise ValueError('Anchor requires point or span')
        a['original']=deepcopy(original);a['clock']='edited-narration';a['mapFingerprint']=value['fingerprint'];output.append(a)
    return output

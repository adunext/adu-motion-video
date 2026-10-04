"""Actual FFmpeg/PCM safety cases; synthetic media, not speech quality approval."""
from pathlib import Path
import tempfile
import unittest
import json
import sys
import subprocess
from copy import deepcopy
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from repair_talk import plan,apply,validate_master,read_pcm,normalize
from retime_subtitles import retime
from narration_edit_map import create_map

class RepairTests(unittest.TestCase):
    def test_antiphase_low_voice_and_black_picture_content_are_kept(self):
        with tempfile.TemporaryDirectory(prefix='adu-repair-content-test-') as d:
            root=Path(d)
            cases=[('antiphase','aevalsrc=0.02*sin(440*2*PI*t)|-0.02*sin(440*2*PI*t):s=48000:d=2',None),
                   ('low-voice','aevalsrc=0.0000001*sin(440*2*PI*t):s=48000:d=2',None),
                   ('black-text','anullsrc=r=48000:cl=stereo:d=2','drawbox=x=0:y=0:w=12:h=12:color=white:t=fill')]
            for name,audio,filter in cases:
                source=root/(name+'.mov')
                cmd=['ffmpeg','-v','error','-n','-f','lavfi','-i','color=c=black:s=128x128:r=24:d=2','-f','lavfi','-i',audio]
                if filter:cmd+=['-vf',filter]
                cmd+=['-c:v','libx264','-preset','ultrafast','-c:a','pcm_f32le',str(source)]
                subprocess.run(cmd,check=True)
                with self.subTest(case=name):
                    result=plan(source,mode='basic',confirmed_blank=[dict(start=0,end=1.8,confirmedNoMeaningfulContent=True,reason='Synthetic candidate; safety checks must retain actual content')])
                    self.assertEqual(result['status'],'no-change',result)
                    self.assertIn('channels' if name!='black-text' else 'picture',result['checks'][0]['reason'])

    def test_off_never_opens_source_candidates_or_old_map(self):
        self.assertEqual(plan('/does/not/exist',mode='off',confirmed_blank='bad',srt='/missing')['status'],'off')
        self.assertEqual(apply({},'/does/not/exist',mode='off')['status'],'off')
        self.assertEqual(plan('/does/not/exist',mode='off')['scanPerformed'],False)

    def test_without_confirmation_does_not_scan_or_cut(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'unknown.mp4';p.write_bytes(b'not media')
            self.assertEqual(plan(p,mode='basic')['status'],'no-change')

    def test_source_srt_literal_multiline_and_overlapping_cues_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.srt';raw='1\n00:00:04,000 --> 00:00:06,000\n嗯，不是四项 <文字>&\n第二行\n\n2\n00:00:05,000 --> 00:00:07,000\n条件成立才交付。\n';p.write_text(raw)
            import hashlib
            m=create_map(dict(sha256='a'*64),600,[(0,180)],transcript_identity=dict(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sizeBytes=p.stat().st_size))
            out,receipt=retime(p,m)
            self.assertIn('00:00:01,000 --> 00:00:03,000',out);self.assertIn('嗯，不是四项 <文字>&\n第二行',out);self.assertEqual(p.read_text(),raw);self.assertEqual(len(receipt['cues']),2)
            p.write_text(raw.replace('不是','就是'))
            with self.assertRaisesRegex(ValueError,'identity'):retime(p,m)

    def test_real_twenty_seconds_three_second_cut_exact_pcm_frames(self):
        with tempfile.TemporaryDirectory(prefix='adu-repair-test-') as d:
            root=Path(d);source=root/'original.mov'
            graph="[0:v][1:v]concat=n=2:v=1:a=0[v];[2:a][3:a]concat=n=2:v=0:a=1[a]"
            command=['ffmpeg','-v','error','-f','lavfi','-i','color=c=black:s=128x128:r=60:d=3.2','-f','lavfi','-i','color=c=0x345678:s=128x128:r=60:d=16.8','-f','lavfi','-i','anullsrc=r=48000:cl=stereo:d=3.2','-f','lavfi','-i','sine=frequency=440:sample_rate=48000:duration=16.8','-filter_complex',graph,'-map','[v]','-map','[a]','-c:v','libx264','-preset','ultrafast','-c:a','pcm_s16le',str(source)]
            subprocess.run(command,check=True)
            srt=root/'original.srt';srt.write_text('1\n00:00:04,000 --> 00:00:06,000\n真实测试，原文不改。\n')
            windows=[dict(start=0,end=3.2,confirmedNoMeaningfulContent=True,reason='Synthetic black head with exact silence')]
            from color_management import fingerprint_file
            anchors=[dict(id='hero',clock='narration-source',sourceSha256=fingerprint_file(source)['sha256'],point=10),dict(id='asset-offset',clock='asset-source',point=10)]
            result=plan(source,mode='basic',confirmed_blank=windows,srt=srt,anchors=anchors)
            self.assertEqual(result['status'],'ready',result);self.assertEqual(result['editMap']['editedFrames'],1020)
            receipt=apply(result,root/'edited',mode='basic');self.assertEqual(receipt['samples'],816000)
            edit,_=validate_master(root/'edited/narration_edit_map.json',source)
            from verify_delivery import repaired_narration
            from export_project import sources
            self.assertEqual(repaired_narration(root/'edited',sources(root/'edited'))['samples'],816000)
            from repair_intake import prepare
            brief={'repairPolicy':{'mode':'basic'},'narrationClock':'edited-narration','narrationDuration':17,'segments':[dict(id='new-segment',durationFrames=1020,anchors={'observe':dict(intakeId='hero')})]}
            prepared=prepare(brief,root/'edited/narration_edit_map.json')
            self.assertEqual(prepared['narrationEditMap']['fingerprint'],edit['fingerprint'])
            self.assertEqual(prepared['transcript'],str((root/'edited/edited.srt').resolve()))
            self.assertEqual(prepared['segments'][0]['anchors']['observe']['frame'],420)
            self.assertEqual(prepared['segments'][0]['intakeBindings']['observe']['original']['point'],10)
            self.assertEqual(result['normalizedAnchors'][1]['point'],10)
            invalid=deepcopy(brief);invalid['narrationClock']='narration-source'
            with self.assertRaisesRegex(ValueError,'edited-narration'):prepare(invalid,root/'edited/narration_edit_map.json')
            self.assertEqual(len(list((root/'edited/talk/clip_000').glob('*.jpg'))),1020)
            normalize(source,root/'reference');np.testing.assert_array_equal(read_pcm(root/'edited/voice.wav'),read_pcm(root/'reference/voice.wav')[144000:])
            self.assertIn('00:00:01,000', (root/'edited/edited.srt').read_text())
            with self.assertRaisesRegex(ValueError,'existing'):apply(result,root/'edited',mode='basic')
            protected=root/'protected.srt';protected.write_text('1\n00:00:01,000 --> 00:00:04,000\n黑底字幕和跨口内容必须保留。\n')
            blocked=plan(source,mode='basic',confirmed_blank=windows,srt=protected)
            self.assertEqual(blocked['status'],'no-change');self.assertIn('subtitle',blocked['checks'][0]['reason'])
            (root/'edited/talk/clip_000/f_00001.jpg').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'frames changed'):validate_master(root/'edited/narration_edit_map.json',source)

if __name__=='__main__':unittest.main()

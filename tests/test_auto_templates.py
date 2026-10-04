"""Executable full-catalog selection, whole-clock segmentation and build rechecks."""
from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from adapt_project import AdaptError, read_json
from adaptation import manifest_digest, validate_adapted_spec
from auto_templates import capabilities, choose, library, save
from build_auto_project import build_auto
from test_template_stress import StressAssets


class AutoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='adu-auto-tests-');cls.addClassCleanup(cls.temp.cleanup)
        cls.root=Path(cls.temp.name);cls.assets=StressAssets(cls.root)
        cls.entries=library()

    def segment(self,entry,source,index=0,frames=None):
        contract=next(x for x in entry['profile']['scenes'] if x['sceneId']==source['id'])
        sid=entry['styleId']+':'+source['id']
        return dict(id=f's-{index}',text='合成测试：新内容展示与验证，不是实际新口播语义验收',
                    intent=contract['intents'][0],phases=contract['requiredPhases'],
                    counts={k:v['min'] for k,v in contract.get('cardinality',{}).items()},
                    anchors={role:dict(frame=round((next(c['at'] for c in source['cues'] if c['id']==key)-source['source']['start'])*60))
                             for key,role in contract['cueRoles'].items()},
                    durationFrames=frames or round((source['source']['end']-source['source']['start'])*60),
                    candidates={sid:dict(slots=self.assets.slots(entry['manifest'],source))})

    def brief(self,segments,**kw):
        return dict(schema='adu-auto-brief/1',brand='合成测试账号',fps=60,layout='portrait',segments=segments,
                    narrationDuration=sum(s['durationFrames'] for s in segments)/60,music={'mode':'none'},**kw)

    def entry(self,style):return next(x for x in self.entries if x['styleId']==style)

    def test_all_real_contracts_and_independent_full_style_paths(self):
        caps=capabilities(self.entries)
        self.assertEqual(caps['styles'],11);self.assertEqual(len(caps['groups']),39)
        for entry in self.entries:
            with self.subTest(style=entry['styleId']):
                segments=[self.segment(entry,s,i) for i,s in enumerate(entry['manifest']['scenes'])]
                # 05 handoffs require a closing group, not an arbitrary video end.
                if entry['styleId'] in ('05-A','06-A'):segments.append(self.segment(entry,entry['manifest']['scenes'][2 if entry['styleId']=='06-A' else 0],len(segments)))
                result=choose(self.brief(segments,allowedStyles=[entry['styleId']]),self.root,self.entries)
                self.assertNotEqual(result['report']['status'],'blocked',result['report'])
                if entry['manifest'].get('externalFonts'):
                    self.assertFalse(result['report']['ready'])
                    self.assertIn('externalFontFiles',str(result['report']['missing']))
                else:
                    self.assertTrue(result['report']['ready'],result['report'])
                    for run in result['runs']:
                        self.assertTrue(validate_adapted_spec(entry['manifest'],run['spec'],self.root,
                                                            ROOT/'adaptation-profiles',allow_pending_talk=True)['ready'])

    def test_complete_cross_style_route_beats_unbound_coherent_route(self):
        a=self.entry('01-A');b=self.entry('02-A')
        segments=[self.segment(a,a['manifest']['scenes'][2]),self.segment(b,b['manifest']['scenes'][0],1)]
        result=choose(self.brief(segments,allowedStyles=['01-A','02-A']),self.root,self.entries)
        self.assertTrue(result['report']['ready'],result['report'])
        self.assertEqual(result['report']['selectedStyle'],'mixed')
        self.assertEqual([r['style'] for r in result['runs']],['01-A','02-A'])
        self.assertEqual(result['runs'][1]['spec']['scenes'][0]['startFrame'],0)
        for run in result['runs']:
            entry=self.entry(run['style'])
            validate_adapted_spec(entry['manifest'],run['spec'],self.root,ROOT/'adaptation-profiles',allow_pending_talk=True)

    def test_short_long_overflow_and_invalid_style_never_loop_or_fallback(self):
        e=self.entry('01-A');source=e['manifest']['scenes'][0]
        for frames in [1,12000]:
            with self.subTest(frames=frames):
                result=choose(self.brief([self.segment(e,source,frames=frames)],allowedStyles=['01-A']),self.root,self.entries)
                self.assertFalse(result['report']['ready']);self.assertEqual(result['report']['status'],'blocked')
                self.assertEqual(result['runs'],[]);self.assertTrue(result['report']['nextActions'])
        segment=self.segment(e,source)
        list(segment['candidates'].values())[0]['slots'][source['slots'][0]['id']]='新'*1000
        result=choose(self.brief([segment],allowedStyles=['01-A']),self.root,self.entries)
        self.assertEqual(result['report']['status'],'blocked')
        with self.assertRaisesRegex(AdaptError,'allowedStyles'):
            choose(self.brief([segment],allowedStyles=['nonexistent']),self.root,self.entries)

    def test_actual_semantic_segmentation_recovers_whole_long_narration_clock(self):
        e=self.entry('01-A');source=e['manifest']['scenes'][2]
        segments=[self.segment(e,source,i) for i in range(3)]
        brief=self.brief(segments,allowedStyles=['01-A'])
        bad=self.segment(e,source,frames=sum(s['durationFrames'] for s in segments))
        brief['segmentations']=[dict(id='too-long-one-group',segments=[bad]),dict(id='three-real-units',segments=segments)]
        result=choose(brief,self.root,self.entries)
        self.assertTrue(result['report']['ready']);self.assertEqual(result['report']['selectedSegmentation'],'three-real-units')
        brief['segmentations'][1]['segments'][0]['durationFrames']+=1
        with self.assertRaisesRegex(AdaptError,'entire narration'):
            choose(brief,self.root,self.entries)

    def test_locked_style_cannot_silently_change_or_missing_font_be_ready(self):
        e=self.entry('02-B');source=e['manifest']['scenes'][0]
        result=choose(self.brief([self.segment(e,source)],allowedStyles=['02-B']),self.root,self.entries)
        self.assertFalse(result['report']['ready']);self.assertEqual(result['report']['selectedStyle'],'02-B')
        self.assertIn('externalFontFiles.title',result['report']['missing'])

    def test_ready_alternatives_reduce_adjacent_repeat_within_one_style(self):
        # Controlled one-intent fixtures verify the optimizer without claiming
        # that unrelated real rhetorical groups are interchangeable.
        entries=deepcopy([self.entry('01-A')]);e=entries[0]
        first=e['manifest']['scenes'][0]; second=deepcopy(first)
        second['id']='alternate';second['sourceBlockSha256']='b'*64
        e['manifest']['scenes']=[first,second]
        c=deepcopy(e['profile']['scenes'][0]);d=deepcopy(c)
        d.update(sceneId=second['id'],sourceBlockSha256=second['sourceBlockSha256'],effects=['different-motion'])
        e['profile']['scenes']=[c,d];e['profile']['pack']['manifestDigest']=manifest_digest(e['manifest'])
        segments=[self.segment(e,first,i) for i in range(10)]
        for s in segments:s['candidates']['01-A:alternate']=deepcopy(s['candidates']['01-A:'+first['id']])
        result=choose(self.brief(segments,allowedStyles=['01-A']),self.root,entries)
        self.assertTrue(result['report']['ready'])
        ids=result['report']['selectedScenes']
        self.assertTrue(all(a!=b for a,b in zip(ids,ids[1:])),ids)
        self.assertIn('repeated-scene-cycle',str(result['report']['rhythm']))

    def test_build_saved_choices_rechecks_tampering_before_import(self):
        e=self.entry('01-A');brief=self.brief([self.segment(e,e['manifest']['scenes'][2])],allowedStyles=['01-A'])
        with tempfile.TemporaryDirectory(dir=self.root) as tmp:
            tmp=Path(tmp);file=tmp/'brief.json';file.write_text(json.dumps(brief))
            save(file,tmp/'plan');p=tmp/'plan/auto_plan.json';data=read_json(p)
            data['runs'][0]['spec']['brand']='伪造更改';p.write_text(json.dumps(data))
            with self.assertRaisesRegex(AdaptError,'choices or run bindings'):
                build_auto(p,tmp/'missing.mp4',tmp/'project')
            self.assertFalse((tmp/'project').exists())

    def test_twenty_minute_narration_keeps_complete_bindings_and_reports_repetition(self):
        e=self.entry('01-A');source=e['manifest']['scenes'][0]
        count=80
        segments=[self.segment(e,source,i) for i in range(count)]
        result=choose(self.brief(segments,allowedStyles=['01-A']),self.root,self.entries)
        self.assertTrue(result['report']['ready'])
        self.assertEqual(len(result['spec']['scenes']),count)
        self.assertGreater(result['report']['durationSeconds'],1200)
        self.assertEqual(result['report']['rhythm']['uniqueSceneCount'],1)
        self.assertIn('dominant-scene',str(result['report']['rhythm']))
        self.assertIn('adjacent-scene-repeat',str(result['report']['rhythm']))
        self.assertTrue(all(s['slots'] for s in result['spec']['scenes']))

    def test_supplied_music_offset_must_cover_the_entire_output(self):
        import wave
        e=self.entry('01-A');segment=self.segment(e,e['manifest']['scenes'][0])
        with tempfile.TemporaryDirectory(dir=self.root) as tmp:
            tmp=Path(tmp)
            for seconds in [2,40]:
                file=tmp/f'music-{seconds}.wav'
                with wave.open(str(file),'wb') as out:
                    out.setnchannels(2);out.setsampwidth(2);out.setframerate(48000)
                    out.writeframes(bytes(seconds*48000*4))
                brief=self.brief([segment],allowedStyles=['01-A'])
                brief['music']=dict(mode='track',path=str(file),offset=1)
                result=choose(brief,self.root,self.entries)
                self.assertEqual(result['report']['ready'],seconds==40)
                if seconds==2:
                    self.assertEqual(result['runs'],[])
                    self.assertIn('music is shorter',str(result['report']['blocking']))
                    self.assertTrue(all(x['status']=='blocked' for x in result['report']['alternatives']))
            brief['music']['offset']=39
            self.assertFalse(choose(brief,self.root,self.entries)['report']['ready'])

    def test_missing_or_retired_music_does_not_build_or_choose_silent_fallback(self):
        e=self.entry('01-A'); segment=self.segment(e,e['manifest']['scenes'][0])
        brief=self.brief([segment],allowedStyles=['01-A'])
        del brief['music']
        result=choose(brief,self.root,self.entries)
        self.assertEqual(result['report']['status'],'needs-binding')
        self.assertFalse(result['report']['ready']); self.assertEqual(result['runs'],[])
        self.assertEqual(result['spec']['music']['mode'],'track')
        brief['music']=dict(mode='synth')
        result=choose(brief,self.root,self.entries)
        self.assertEqual(result['report']['status'],'blocked')
        self.assertIn('retired',str(result['report']['blocking']))

    def test_long_post_protected_span_is_a_review_metric_not_a_static_verdict(self):
        from adaptation import rhythm_diagnostics
        entry=self.entry('01-A'); scene=entry['manifest']['scenes'][0]
        segment=self.segment(entry,scene,frames=600)
        candidate=dict(sceneId=scene['id'],contract=entry['profile']['scenes'][0],
                       planned=dict(endFrame=600,motionWindows=[dict(outputStartFrame=0,outputEndFrame=180)]))
        report=rhythm_diagnostics([candidate],[segment],60)
        self.assertEqual(report['actionSpans'][0]['postProtectedSeconds'],7)
        self.assertEqual(report['actionSpans'][0]['protectedSeconds'],3)
        self.assertEqual(report['findings'][0]['code'],'long-post-protected-span')
        self.assertIn('not a static',report['actionSpanScope'])
        candidate['planned']['motionWindows'][0]['outputEndFrame']=420
        self.assertEqual(rhythm_diagnostics([candidate],[segment],60)['findings'],[])

    def test_real_mixed_build_browser_audio_and_frame_exact_narration(self):
        import wave
        a=self.entry('01-A');b=self.entry('02-A')
        segments=[self.segment(a,a['manifest']['scenes'][1]),self.segment(b,b['manifest']['scenes'][0],1)]
        brief=self.brief(segments,allowedStyles=['01-A','02-A'])
        brief['faceTracking']=dict(mode='fixed',cx=.5,cy=.5,h=.6)
        with tempfile.TemporaryDirectory(prefix='adu-auto-integration-') as tmp:
            tmp=Path(tmp)
            from test_music_policy import tone
            music=tmp/'replacement.wav'
            tone(music,seconds=brief['narrationDuration']+2)
            brief['music']=dict(mode='track',path=str(music),offset=1)
            video_asset=tmp/'evidence.mp4'
            subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i','testsrc2=size=160x90:rate=2:duration=30',
                '-vf','setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                '-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709',
                '-color_trc','bt709','-color_primaries','bt709',str(video_asset)],check=True,capture_output=True)
            for value in segments[0]['candidates'].values():
                for slot in a['manifest']['scenes'][1]['slots']:
                    if slot['type']=='video':value['slots'][slot['id']]=dict(path=str(video_asset),offset=10)
            brief_path=tmp/'brief.json';brief_path.write_text(json.dumps(brief))
            save(brief_path,tmp/'plan')
            total=sum(s['durationFrames'] for s in segments);boundary=segments[0]['durationFrames']/60
            talk=tmp/'talk.mp4'
            subprocess.run(['ffmpeg','-v','error','-n','-f','lavfi','-i',
                f'testsrc2=size=160x90:rate=60:duration={total/60}','-f','lavfi','-i',
                f'sine=frequency=330:sample_rate=48000:duration={total/60}',
                '-vf','setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                '-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac',str(talk)],check=True,capture_output=True)
            subs=tmp/'subs.js';subs.write_text('const SUBS='+json.dumps([dict(t0=boundary-.4,t1=boundary+1,
                zh='跨场字幕保持全局时钟',en='One continuous subtitle clock',sp=[[boundary-.4,boundary+1,10]])],ensure_ascii=False)+';')
            project=tmp/'project';build_auto(tmp/'plan/auto_plan.json',talk,project,subs)
            plan=read_json(project/'macro_plan.json')
            self.assertEqual(plan['end_frame'],total);self.assertEqual(len(plan['parts']),2)
            from export_project import sources
            from verify_delivery import prepared_media_color
            receipt=prepared_media_color(project,sources(project))
            self.assertEqual(len(receipt['entries']),3)
            self.assertTrue(all(r['preparedFrames']>0 for r in receipt['entries']))
            subprocess.run(['node',str(ROOT/'scripts/dump_sfx.mjs'),str(project/'index.html'),str(project/'sfx.json')],check=True,capture_output=True)
            runtime=subprocess.run(['node',str(ROOT/'tests/test_auto_runtime.mjs'),str(project)],capture_output=True,text=True)
            self.assertEqual(runtime.returncode,0,runtime.stderr)
            evidence=json.loads(runtime.stdout);self.assertTrue(evidence['deterministic']);self.assertGreater(evidence['seeks'],20)
            subprocess.run([sys.executable,str(project/'audio.py')],check=True,capture_output=True)
            self.assertEqual(read_json(project/'macro_audio_report.json')['parts'],2)
            self.assertEqual(read_json(project/'macro_audio_report.json')['mode'],'track')
            self.assertEqual(read_json(project/'macro_music.json')['path'],'assets/music.wav')
            for part in plan['parts']:
                self.assertEqual(read_json(project/part['path']/'macro_music.json')['mode'],'none')
            with wave.open(str(project/'voice.wav'),'rb') as voice:
                params=voice.getparams();original=voice.readframes(voice.getnframes())
            slices=[]
            for part in plan['parts']:
                with wave.open(str(project/part['path']/'voice.wav'),'rb') as voice:
                    self.assertEqual(voice.getframerate(),params.framerate)
                    slices.append(voice.readframes(voice.getnframes()))
            self.assertEqual(b''.join(slices),original,'No omitted/duplicated/retimed voice samples at style boundaries')
            # Exercise real encoded output over the cross-style seam. Full-film
            # encode/listening is not asserted by this short integration test.
            output=tmp/'seam.mp4'
            subprocess.run(['node',str(ROOT/'scripts/render_project.mjs'),str(project/'index.html'),
                '--start',str(boundary-.25),'--end',str(boundary+.25),'--output',str(output),
                '--audio',str(project/'voice.wav')],check=True,capture_output=True)
            metadata=json.loads(subprocess.run(['ffprobe','-v','error','-show_streams','-of','json',str(output)],check=True,capture_output=True,text=True).stdout)
            video=next(x for x in metadata['streams'] if x['codec_type']=='video')
            self.assertEqual(int(video['nb_frames']),30);self.assertEqual((video['width'],video['height']),(1080,1920))
            subprocess.run(['ffmpeg','-v','error','-i',str(output),'-f','null','-'],check=True,capture_output=True)
            if os.environ.get('ADU_AUTO_REPORT'):
                Path(os.environ['ADU_AUTO_REPORT']).write_text(json.dumps(dict(
                    schema='adu-auto-test-evidence/1',source='tests/test_auto_templates.py',
                    styles=11,groups=39,composition=dict(frames=total,fps=60,parts=len(plan['parts']),
                    width=1080,height=1920,seeks=evidence['seeks'],repeatRoundTrips=evidence['repeatRoundTrips'],
                    softwareRaster=True,deterministicPixels=True,
                    subtitleGlobalClock=True,voicePCMRejoinIdentical=True,
                    preparedMedia=[dict(slot=x['slotId'],frames=x['preparedFrames']) for x in receipt['entries']],
                    seamEncodedFrames=int(video['nb_frames']),seamDecodePassed=True),
                    audio=read_json(project/'macro_audio_report.json'),
                    scope='synthetic source and selected test track, truthful test annotations, global action SFX and half-second seam encoding; no human whole-film AV acceptance'
                ),ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':unittest.main()

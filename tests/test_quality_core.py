"""Regression cases from the quality plan, separate from artistic acceptance."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from adapt_project import AdaptError, following_tail_issue
from auto_templates import capabilities, library
from build_auto_project import global_scene
from content_evidence import from_text, validate_coverage, derive_from_transcript
from subtitle_position import resolve_position
import audiolib as A


class QualityCoreTests(unittest.TestCase):
    def test_layout_uses_actual_frozen_selection_and_reports_unsupported(self):
        land = library(layout='landscape'); port = library(layout='portrait')
        self.assertEqual(next(e for e in land if e['styleId']=='01-A')['selection'], 'classic-performance@1.0.0')
        self.assertEqual(next(e for e in port if e['styleId']=='01-A')['selection'], 'classic-performance@1.1.0-candidate')
        self.assertEqual(capabilities(land,'landscape')['availableStyles'],10)
        self.assertEqual(capabilities(port,'portrait')['availableStyles'],11)

    def test_tail_uses_real_root_end_but_standalone_child_cannot_claim_it(self):
        source=dict(id='close',minFollowingFrames=73)
        self.assertIsNotNone(following_tail_issue(source,120,120,60,60,'close'))
        self.assertIsNone(following_tail_issue(source,120,120,60,60,'close',composition_context=dict(startFrame=300,durationFrames=500)))
        self.assertIsNotNone(following_tail_issue(source,120,120,60,60,'close',composition_context=dict(startFrame=380,durationFrames=500)))
        with self.assertRaises(AdaptError):following_tail_issue(source,120,120,60,60,'close',composition_context=dict(startFrame=400,durationFrames=500))

    def test_typed_rebase_never_moves_asset_source_or_evidence_frames(self):
        source=dict(startFrame=0,endFrame=120,sourceStart=50,sourceEnd=52,
            knots=[dict(sourceAt=50,outputFrame=0)],time_map=[dict(source=50,output_frame=0)],
            slots=dict(video=dict(offset=10,startFrame=12)),
            mediaClocks=[dict(startFrame=10,endFrame=30,start=10/60,end=.5,offset=10)],
            evidence=dict(startFrame=60,endFrame=120),narrationEditMap=dict(startFrame=0),
            sfx=[dict(outputFrame=10,sourceAt=50.1,at=10/60)])
        before=deepcopy(source);result=global_scene(source,300,60)
        self.assertEqual(source,before)
        self.assertEqual(result['evidence'],before['evidence']);self.assertEqual(result['slots'],before['slots'])
        self.assertEqual(result['sourceStart'],50);self.assertEqual(result['knots'][0]['sourceAt'],50)
        self.assertEqual(result['mediaClocks'][0]['offset'],10)
        self.assertEqual(result['mediaClocks'][0]['startFrame'],310)
        self.assertEqual(result['sfx'][0]['at'],310/60)

    def test_ownership_exclusive_support_many_to_many_and_preserves_negation(self):
        text='不是四项，是三项。只有验证通过才交付。'
        evidence=from_text(text,[dict(start=0,end=10),dict(start=10,end=len(text))])
        refs=[u['id'] for u in evidence['units']]
        segments=[dict(id='first',ownershipRefs=[refs[0]],supportingRefs=dict(title=[refs[0]],number=[refs[0]])),dict(id='last',ownershipRefs=[refs[1]])]
        self.assertEqual(validate_coverage(evidence,segments)['ownedUnits'],2)
        for owned in [[refs[0],refs[0]],[refs[1],refs[0]],[refs[0]]]:
            with self.assertRaises(AdaptError):validate_coverage(evidence,[dict(id='bad',ownershipRefs=owned)])
        changed=deepcopy(evidence);changed['text']=changed['text'].replace('不是','就是')
        with self.assertRaisesRegex(AdaptError,'identity'):validate_coverage(changed,segments)

    def test_subtitle_default_and_custom_ratios_leave_landscape_preset(self):
        self.assertIsNone(resolve_position(None,1920,1080))
        self.assertEqual(resolve_position(None,1080,1920)['bottomRatio'],.18)
        self.assertEqual(resolve_position(dict(bottomRatio=.3),1080,1920)['bottomRatio'],.3)
        with self.assertRaises(ValueError):resolve_position(dict(leftRatio=.5,rightRatio=.5),1080,1920)

    def test_event_dry_and_wet_survive_insertions_and_bgm_random_consumption(self):
        cue=dict(eventId='handbook:accept',type='typing',d=.16,t=1,g=.6,p=.1)
        dry=A.render_event(cue);wet=A.render_event(cue,wet=True)
        A.render_event(dict(eventId='new:impact',type='crash',t=0))
        A.rng.standard_normal(10000)
        A.reverb(np.ones((100,2)),.1)
        np.testing.assert_array_equal(dry,A.render_event(cue))
        np.testing.assert_array_equal(wet,A.render_event(cue,wet=True))
        A.init(3)
        first=A.render_sfx([cue,dict(eventId='other',type='pop',t=1.2)])
        second=A.render_sfx([dict(eventId='other',type='pop',t=1.2),cue])
        np.testing.assert_array_equal(first,second)
        with self.assertRaisesRegex(ValueError,'Duplicate'):A.render_sfx([cue,cue])

    def test_facts_check_actual_count_and_entity_consumption(self):
        e=from_text('三项结果属于项目甲。',[dict(start=0,end=10)])
        r=e['units'][0]['id']
        e['facts']=[dict(id='count',type='count',value=3,supportingRefs=[r]),dict(id='owner',type='entity',value='project-a',supportingRefs=[r])]
        segment=dict(id='one',ownershipRefs=[r],counts=dict(items=3),inputs=dict(entityId='project-a'),factBindings={'counts.items':'count','inputs.entityId':'owner'})
        self.assertEqual(len(validate_coverage(e,[segment])['factChecks']),2)
        for path,value in [('counts',dict(items=4)),('inputs',dict(entityId='project-b'))]:
            changed=deepcopy(segment);changed[path]=value
            with self.assertRaisesRegex(AdaptError,'differs'):validate_coverage(e,[changed])
        segment['factBindings'].pop('inputs.entityId')
        with self.assertRaisesRegex(AdaptError,'Unconsumed'):validate_coverage(e,[segment])

    def test_transcript_derivation_never_invents_word_times_at_boundary(self):
        brief=dict(transcript=[dict(id='a',start=0,end=2,text='不是四项'),dict(id='b',start=2,end=4,text='确实三项')])
        segments=[dict(id='a',durationFrames=120),dict(id='b',durationFrames=120)]
        b,s,n=derive_from_transcript(brief,segments,ROOT,60)
        self.assertEqual(validate_coverage(b['contentEvidence'],s)['ownedUnits'],2)
        self.assertEqual(b['contentEvidence']['text'],'不是四项\n确实三项\n')
        segments[0]['durationFrames']=90;segments[1]['durationFrames']=150
        b,s,n=derive_from_transcript(brief,segments,ROOT,60)
        self.assertNotIn('contentEvidence',b);self.assertIn('crosses',n)


if __name__=='__main__':unittest.main()

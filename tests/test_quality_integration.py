"""Quality-chain regressions against actual manifests and decoded local media."""
from copy import deepcopy
from pathlib import Path
import json
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
from adapt_project import AdaptError, compile_plan
from auto_templates import library, choose
import test_auto_templates as auto_test
from test_template_stress import StressAssets
from repair_intake import prepare


class QualityIntegration(unittest.TestCase):
    def test_off_planning_ignores_missing_or_stale_edit_map(self):
        value={'repairPolicy':{'mode':'off'}}
        self.assertIs(prepare(value,Path('/missing/map.json')),value)
        with self.assertRaisesRegex(AdaptError,'--edit-map'):
            prepare({'repairPolicy':{'mode':'basic'}})

    def test_new_real_groups_compile_source_media_and_root_tail_contracts(self):
        from test_quality_packs import PACKS
        with tempfile.TemporaryDirectory(prefix='adu-quality-integration-') as tmp:
            root=Path(tmp);assets=StressAssets(root)
            for family,version in PACKS:
                p=ROOT/'packs'/family/version;m=json.loads((p/'manifest.json').read_text())
                for scene in m['scenes']:
                    if not (scene.get('variantOf') or scene.get('authorship') or scene['id']=='independent-artifact-review'):
                        continue
                    frames=round((scene['source']['end']-scene['source']['start'])*60)
                    target=dict(id='actual-group',sceneId=scene['id'],startFrame=0,endFrame=frames,
                        cues={c['id']:{'frame':round((c['at']-scene['source']['start'])*60)} for c in scene.get('cues',[])},
                        slots=assets.slots(m,scene))
                    spec=dict(pack=m['id'],version=m['version'],fps=60,scenes=[target],layout='portrait')
                    with self.subTest(family=family,scene=scene['id']):
                        plan=compile_plan(m,spec,spec_dir=root,project=root,
                            composition_context={'startFrame':0,'durationFrames':frames+scene.get('minFollowingFrames',0)})
                        self.assertEqual(plan['end_frame'],frames)
                        for clock in plan['scenes'][0].get('mediaClocks',[]):
                            self.assertEqual(clock['offset'],0)
                            self.assertEqual(clock.get('playbackRate',1),1)

    def test_saved_binding_rebuild_does_not_compare_new_unrelated_catalog(self):
        with tempfile.TemporaryDirectory(prefix='adu-pinned-plan-') as tmp:
            root=Path(tmp);assets=StressAssets(root);entries=library(layout='portrait')
            helper=auto_test.AutoTests(methodName='test_build_saved_choices_rechecks_tampering_before_import')
            helper.assets=assets;helper.entries=entries
            e=next(x for x in entries if x['styleId']=='01-A')
            brief=helper.brief([helper.segment(e,e['manifest']['scenes'][2])],allowedStyles=['01-A'])
            saved=choose(brief,root,entries)
            pinned=library(layout='portrait',bindings=saved['catalogBindings'])
            replay=choose(saved['brief'],root,pinned)
            self.assertEqual(replay['sourceDigests'],saved['sourceDigests'])
            self.assertEqual(replay['spec'],saved['spec']);self.assertEqual(replay['runs'],saved['runs'])


if __name__=='__main__':unittest.main()

from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from adapt_project import AdaptError, compile_plan
from semantic_inputs import SemanticInputError, expand_inputs
from build_macro_project import copy_media


class SemanticMediaTest(unittest.TestCase):
    def test_nested_semantics_drive_repeated_and_derived_visible_labels(self):
        scene = {'slots': [{'id': 'main', 'inputPath': 'result.title'},
                           {'id': 'echo', 'inputPath': 'result.title'},
                           {'id': 'tag', 'inputTemplate': '// {parts.0.label} → {result.title}'}]}
        target = expand_inputs(scene, {'inputs': {'result': {'title': '训练'}, 'parts': [{'label': '回车'}]}})
        self.assertEqual(target['slots'], {'main': '训练', 'echo': '训练', 'tag': '// 回车 → 训练'})
        with self.assertRaisesRegex(SemanticInputError, 'Missing'):
            expand_inputs(scene, {'inputs': {'result': {'title': '训练'}}})
        with self.assertRaisesRegex(SemanticInputError, 'both'):
            expand_inputs(scene, {'inputs': {}, 'slots': {'main': 'conflict'}})

    def test_semantic_templates_cannot_inspect_python_attributes(self):
        with self.assertRaises(SemanticInputError):
            expand_inputs({'slots': [{'id': 'x', 'inputTemplate': '{parts.__class__}'}]},
                          {'inputs': {'parts': []}})

    def test_output_media_keeps_real_playback_through_extended_reading(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); video = root / 'evidence.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                            'testsrc2=size=160x90:rate=30:duration=8', '-c:v', 'libx264',
                            '-pix_fmt', 'yuv420p', str(video)], check=True)
            source = {'id': 'proof', 'source': {'start': 0, 'end': 4},
                      'motionWindows': [{'start': 0, 'end': 1}, {'start': 3, 'end': 4}],
                      'slots': [{'id': 'clip', 'type': 'video', 'sourceAsset': 'preview',
                                 'inputPath': 'evidence', 'aspect': '16:9',
                                 'playback': {'start': 0, 'end': 4, 'fps': 30}}]}
            pack = {'id': 'sample', 'fps': 60, 'scenes': [source]}
            target = {'scenes': [{'sceneId': 'proof', 'duration': 6,
                                 'inputs': {'evidence': {'path': str(video), 'offset': 1}}}]}
            plan = compile_plan(pack, target)
            item = plan['scenes'][0]; clock = item['mediaClocks'][0]
            self.assertEqual(clock['preparedFrames'], 180)
            self.assertEqual(clock['endFrame'], 360)
            self.assertEqual(clock['clock'], 'output')
            self.assertEqual(clock['terminalHoldSeconds'], 0)
            stage = root / 'project'; (stage / 'sc').mkdir(parents=True)
            _, aliases = copy_media(stage, pack, item, source, "seqAt('preview',120,30,t,0,false)", set())
            self.assertEqual(len(list((stage / 'sc' / aliases['preview']).glob('f_*.jpg'))), 180)
            self.assertFalse(Path(item['slots']['clip']['path']).is_absolute())
            target['scenes'][0]['duration'] = 9
            with self.assertRaisesRegex(AdaptError, 'longer recording'):
                compile_plan(pack, target)
            source['slots'][0]['playback']['terminalHoldSeconds'] = 2
            held = compile_plan(pack, target)['scenes'][0]['mediaClocks'][0]
            self.assertEqual(held['terminalHoldSeconds'], 2)

    def test_semantic_expansion_retains_capacity_failure(self):
        pack = {'id': 'sample', 'fps': 60, 'scenes': [{'id': 'one', 'source': {'start': 0, 'end': 2},
                'slots': [{'id': 'headline', 'type': 'text', 'maxChars': 4, 'inputPath': 'claim'}]}]}
        with self.assertRaisesRegex(AdaptError, 'allows 4'):
            compile_plan(pack, {'scenes': [{'sceneId': 'one', 'duration': 2, 'inputs': {'claim': '超出字数容量'}}]})


if __name__ == '__main__': unittest.main()

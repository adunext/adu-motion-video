"""A fixed-capacity group must not silently omit newly supplied content."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from semantic_inputs import SemanticInputError, expand_inputs


class InputConsumptionTests(unittest.TestCase):
    def test_extra_media_or_misspelled_caption_is_rejected(self):
        scene = {'slots': [{'id': 'title', 'inputTemplate': '{heading}：{items.0.caption}'},
                           {'id': 'recording', 'inputPath': 'items.0.video'}]}
        inputs = {'heading': '真实示例', 'items': [{'caption': '步骤一',
                  'video': {'path': 'new.mp4', 'offset': 1, 'colorReviewFile': 'review.json'}}]}
        result = expand_inputs(scene, {'inputs': inputs})
        self.assertEqual(result['slots']['recording'], inputs['items'][0]['video'])
        for key in ('extra-media', 'typo'):
            changed = deepcopy(inputs)
            if key == 'extra-media':
                changed['items'].append({'caption': '不得丢弃', 'video': 'fourth.mp4'})
                expected = 'items.1.video'
            else:
                changed['heding'] = '未消费的字段'
                expected = 'heding'
            with self.assertRaisesRegex(SemanticInputError, expected):
                expand_inputs(scene, {'inputs': changed})

    def test_existing_frozen_examples_have_no_silently_ignored_fields(self):
        count = 0
        for path in (ROOT / 'packs').rglob('manifest.json'):
            manifest = json.loads(path.read_text())
            for scene in manifest.get('scenes', []):
                if not scene.get('inputExample'):
                    continue
                with self.subTest(pack=manifest['id'], version=manifest.get('version'), scene=scene['id']):
                    expand_inputs(scene, {'inputs': scene['inputExample']})
                    count += 1
        self.assertGreaterEqual(count, 41)


if __name__ == '__main__':
    unittest.main()

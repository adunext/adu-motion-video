from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from narration_edit_map import *


class EditMapTests(unittest.TestCase):
    def test_twenty_minus_three_frames_samples_and_typed_anchors(self):
        m=create_map(dict(sha256='a'*64),1200,[(0,180)])
        self.assertEqual((m['editedFrames'],m['editedSamples']),(1020,816000))
        self.assertEqual(map_point(m,10),7)
        refs=normalize_intake_anchors(m,[dict(id='source10',clock='narration-source',sourceSha256='a'*64,point=10),dict(id='edited10',clock='edited-narration',point=10),dict(id='asset10',clock='asset-source',point=10,offset=10)])
        self.assertEqual([a['point'] for a in refs],[7,10,10]);self.assertEqual(refs[0]['outputFrame'],420)

    def test_multiple_cuts_inverse_sides_and_exclusive_end(self):
        m=create_map(dict(sha256='a'*64),1200,[(0,180),(360,480)])
        self.assertEqual(map_point(m,10),5);self.assertEqual(map_point(m,5),2)
        self.assertEqual(inverse_point(m,3,side='leaving'),6);self.assertEqual(inverse_point(m,3),8)
        with self.assertRaises(ValueError):map_point(m,7)
        with self.assertRaises(ValueError):map_span(m,5,9)
        self.assertEqual(map_span(m,8,20),(3,15))

    def test_5999_anchor_cannot_round_into_next_kept_segment(self):
        m=create_map(dict(sha256='a'*64),1200,[(360,480)])
        with self.assertRaisesRegex(ValueError,'rounds across'):normalize_intake_anchors(m,[dict(id='near',clock='narration-source',sourceSha256='a'*64,point=5.999)])
        self.assertEqual(quantize_cut(6.001,7.999),(361,479))

    def test_map_tamper_empty_overlap_and_wrong_identity_fail(self):
        m=create_map(dict(sha256='a'*64),1200,[(0,180)]);m['kept'][0]['editedEndSample']+=1
        with self.assertRaises(ValueError):validate_edit_map(m)
        for cuts in [[(0,1200)],[(0,180),(120,240)]]:
            with self.assertRaises(ValueError):create_map(dict(sha256='a'*64),1200,cuts)

    def test_long_multicut_uses_integer_totals_without_drift(self):
        removed=[(i*6000+60,i*6000+121) for i in range(1000)]
        m=create_map(dict(sha256='a'*64),6000000,removed)
        self.assertEqual(m['editedFrames'],6000000-61000)
        self.assertEqual(m['editedSamples'],(6000000-61000)*800)


if __name__=='__main__':unittest.main()

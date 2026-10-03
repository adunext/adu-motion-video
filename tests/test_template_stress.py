"""Current catalog timing/media stress, with real decoded synthetic assets.

This checks all declared groups and real media metadata. It does not constitute
human narration, font, semantic truth or full-episode listening acceptance.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from PIL import Image
from adapt_project import (AdaptError, media_clocks, slot_bindings,
                           timed_scene)
from build_macro_project import build, copy_media, preflight_narration
from pack_catalog import resolve


def run(args):
    subprocess.run([str(x) for x in args], check=True, capture_output=True)


def catalog_packs():
    catalog = json.loads((ROOT / 'references/template-catalog.json').read_text())
    return [(style['id'], resolve(style['portraitSelection'], ROOT / 'packs'))
            for template in catalog['templates'] for style in template['styles']]


class StressAssets:
    def __init__(self, root):
        self.root = root
        (root / 'talk').mkdir()
        (root / 'talkmap.js').write_text('window.TALK_MAP=[];')
        Image.new('RGB', (72, 128), '#345678').save(root / 'talk/f_0001.jpg')
        self.images = {}
        for aspect, size in [('16:9', (256, 144)), ('9:16', (90, 160)), ('1:1', (96, 96))]:
            file = root / (aspect.replace(':', '-') + '.jpg')
            Image.new('RGB', size, '#345678').save(file)
            self.images[aspect] = file
        self.clips = {}
        for duration in [1, 30, 1200]:
            video = root / f'{duration}s.mp4'
            # Moving test signal, deliberately sparse 2fps to keep long fixture
            # small; output sampling is still declared by each frozen recipe.
            run(['ffmpeg', '-v', 'error', '-n', '-f', 'lavfi', '-i',
                 f'testsrc2=size=160x90:rate=2:duration={duration}', '-c:v', 'libx264',
                 '-preset', 'ultrafast', '-pix_fmt', 'yuv420p', video])
            self.clips[duration] = video
        self.directories = {}

    def sequence(self, aspect, count, wall=False):
        key = (aspect, count, wall)
        if key not in self.directories:
            folder = self.root / f'frames-{len(self.directories)}'
            folder.mkdir()
            for i in range(count):
                name = f'{i:03d}.jpg' if wall else f'f_{i + 1:04d}.jpg'
                os.link(self.images[aspect], folder / name)
            if wall:
                (folder / 'wall-meta.json').write_text(json.dumps({'uniqueWorks': 27, 'displayTiles': count}))
                (folder / 'index.json').write_text(json.dumps([{'slug': f'synthetic-{i % 27}'} for i in range(count)]))
            self.directories[key] = folder
        return self.directories[key]

    def slots(self, manifest, source, *, near=False, short=False, video_duration=30, offset=0):
        values = {}
        for slot in source['slots']:
            kind = slot['type']
            if kind in ['text', 'dynamicText']:
                values[slot['id']] = '新' * (slot.get('maxChars', 4) if near else 1 if short else min(4, slot.get('maxChars', 4)))
            elif kind == 'talk':
                values[slot['id']] = '@talk'
            elif kind == 'number':
                value = max(slot.get('min', 0), 1)
                if value == slot.get('sourceText'):
                    value += 1
                values[slot['id']] = min(slot.get('max', value), value)
            elif kind == 'video':
                values[slot['id']] = {'path': str(self.clips[video_duration]), 'offset': offset}
            elif kind == 'image':
                values[slot['id']] = str(self.images.get(slot.get('aspect'), self.images['1:1']))
            elif kind in ['sequence', 'wall-sprites']:
                definition = manifest.get('assetDefinitions', {}).get(slot['id'], {})
                wall = kind == 'wall-sprites'
                count = definition.get('originalSprites', definition.get('originalItems', 389)) if wall else definition.get('originalFrames', slot.get('minFiles', 1))
                aspect = slot.get('aspect', '16:9')
                if aspect not in self.images:
                    aspect = '16:9'
                values[slot['id']] = {'path': str(self.sequence(aspect, count, wall)), 'entityId': 'synthetic-shared-work'}
            else:
                raise AssertionError(f'Fixture does not handle {kind}')
        return values


def target(source, frames, slots, shift=0):
    # A test-only retiming shifts all cues after a legal reading gap. It is
    # explicitly not a proposal of real keyword timestamps for a new episode.
    windows = source.get('motionWindows', [])
    start, end = source['source']['start'], source['source']['end']
    merged = []
    for window in sorted(windows, key=lambda x: x['start']):
        if merged and window['start'] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], window['end'])
        else:
            merged.append([window['start'], window['end']])
    gaps = [(a, b) for a, b in zip([start] + [w[1] for w in merged], [w[0] for w in merged] + [end]) if b - a > .03]
    gap_end = max(gaps, key=lambda x: x[1] - x[0])[1] if gaps else end
    cues = {cue['id']: {'frame': round((cue['at'] - start) * 60) + (shift if cue['at'] >= gap_end - 1e-8 else 0)}
            for cue in source.get('cues', [])}
    return {'id': 'stress', 'sceneId': source['id'], 'durationFrames': frames, 'slots': slots, 'cues': cues}


class TemplateStressTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='adu-template-stress-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.assets = StressAssets(cls.root)
        cls.rows = []

    @classmethod
    def tearDownClass(cls):
        report = os.environ.get('ADU_STRESS_REPORT')
        if report:
            Path(report).write_text(json.dumps({'scope': 'synthetic timing, capacity and decoded media; not human AV acceptance',
                'cases': cls.rows}, ensure_ascii=False, indent=2))
        cls.temp.cleanup()

    def evaluate(self, manifest, source, frames, slots, shift=0):
        t = target(source, frames, slots, shift)
        values, details = slot_bindings(source, t, self.root, self.root, manifest.get('assetDefinitions'))
        planned = timed_scene(source, t, 0, 0, frames, 60, manifest['fps'], [], values, details)
        planned['mediaClocks'] = media_clocks(source, planned, 60)
        return planned

    def test_all_current_groups_short_original_extended_and_overlong(self):
        groups = 0
        for style, pack in catalog_packs():
            manifest = json.loads((pack / 'manifest.json').read_text())
            self.assertEqual(manifest['fps'], 60)
            for source in manifest['scenes']:
                groups += 1
                base = round((source['source']['end'] - source['source']['start']) * 60)
                limit = source.get('maxHoldFrames', 0)
                slots = self.assets.slots(manifest, source)
                for layout in ['landscape', 'portrait']:
                    cases = [('original', base, True, 0), ('short-text', base, True, 0),
                             ('capacity-text', base, True, 0), ('oversize-text', base, False, 0), ('below-min', source.get('minFrames', 1) - 1, False, 0),
                             ('one-frame', 1, False, 0), ('over-hold', base + limit + 1, False, 0),
                             ('ten-minute-single-group', 36000, False, 0)]
                    for case, frames, expected, shift in cases:
                        with self.subTest(style=style, scene=source['id'], layout=layout, case=case):
                            current = self.assets.slots(manifest, source, near=case == 'capacity-text', short=case == 'short-text')
                            if case == 'oversize-text':
                                text_slot = next(s for s in source['slots'] if s['type'] in ['text', 'dynamicText'] and 'maxChars' in s)
                                current[text_slot['id']] = '长' * (text_slot['maxChars'] + 1)
                            try:
                                item = self.evaluate(manifest, source, frames, current, shift)
                                # Layout is resolved from the real frozen manifest,
                                # not inferred from a portrait CSS file.
                                from pack_layout import resolve_layout
                                geometry = resolve_layout(manifest, {'layout': layout})
                                self.assertEqual(geometry['height'], 1920 if layout == 'portrait' else 1080)
                                observed, reason = True, ''
                                for window in item['motionWindows']:
                                    seconds = (window['outputEndFrame'] - window['outputStartFrame']) / 60
                                    self.assertLessEqual(abs(seconds - (window['sourceEnd'] - window['sourceStart'])), 1 / 60 + 1e-6)
                            except AdaptError as exc:
                                observed, reason = False, str(exc)
                            self.rows.append({'style': style, 'scene': source['id'], 'layout': layout, 'case': case,
                                              'frames': frames, 'accepted': observed, 'reason': reason})
                            self.assertEqual(observed, expected, reason)
                if limit:
                    # Contract permission is not an automatic arbitrary cue
                    # placement: preserve original speed around the longest gap.
                    try:
                        item = self.evaluate(manifest, source, base + limit, slots, limit)
                        accepted, reason = True, ''
                    except AdaptError as exc:
                        accepted, reason = False, str(exc)
                    self.rows.append({'style': style, 'scene': source['id'], 'case': 'max-hold-retimed-cues',
                                      'accepted': accepted, 'reason': reason})
        self.assertEqual(groups, 32)

    def test_real_one_second_and_twenty_minute_recordings_with_offsets(self):
        clips = 0
        for style, pack in catalog_packs():
            manifest = json.loads((pack / 'manifest.json').read_text())
            for source in manifest['scenes']:
                if not any(s['type'] == 'video' for s in source['slots']):
                    continue
                clips += 1
                base = round((source['source']['end'] - source['source']['start']) * 60)
                for duration, offset, expected in [(1, 0, False), (30, 0, True), (1200, 1180, True), (1200, 1199.8, False), (1200, 1201, False)]:
                    with self.subTest(style=style, duration=duration, offset=offset):
                        try:
                            item = self.evaluate(manifest, source, base, self.assets.slots(manifest, source, video_duration=duration, offset=offset))
                            observed, reason = True, ''
                            self.assertTrue(all(clock['loop'] is False for clock in item['mediaClocks']))
                            self.assertLess(sum(clock['preparedFrames'] for clock in item['mediaClocks']), 1500)
                        except AdaptError as exc:
                            observed, reason = False, str(exc)
                        self.rows.append({'style': style, 'scene': source['id'], 'case': 'real-video-duration-offset',
                                          'sourceSeconds': duration, 'offset': offset, 'accepted': observed, 'reason': reason})
                        self.assertEqual(observed, expected, reason)
        self.assertEqual(clips, 5)

    def test_long_source_decodes_only_used_window_and_retains_motion(self):
        pack = resolve('classic-performance@1.1.0-candidate', ROOT / 'packs')
        manifest = json.loads((pack / 'manifest.json').read_text())
        source = next(s for s in manifest['scenes'] if s['id'] == 'evidence-focus')
        base = round((source['source']['end'] - source['source']['start']) * 60)
        item = self.evaluate(manifest, source, base, self.assets.slots(manifest, source, video_duration=1200, offset=1180))
        out = self.root / 'long-source-slice'; (out / 'sc').mkdir(parents=True)
        # Real decoder and real prepared frame names, no probe mocks.
        copy_media(out, manifest, item, source, (pack / source['sourceCodeFile']).read_text(), set())
        saved = list((out / 'sc').rglob('f_*.jpg'))
        expected = sum(clock['preparedFrames'] for clock in item['mediaClocks'])
        self.assertEqual(len(saved), expected)
        self.assertLess(len(saved), 1000)
        self.assertGreater(len({p.read_bytes() for p in saved}), 5)
        self.rows.append({'case': 'real-decoding-twenty-minute-source', 'preparedFrames': len(saved), 'wholeSourceFramesAt30fps': 36000, 'accepted': True})

    def test_actual_talk_length_is_rejected_before_heavy_frame_extraction(self):
        pack = resolve('classic-performance@1.1.0-candidate', ROOT / 'packs')
        manifest = json.loads((pack / 'manifest.json').read_text())
        source = manifest['scenes'][0]
        base = round((source['source']['end'] - source['source']['start']) * 60)
        spec = {'pack': manifest['id'], 'brand': '压力检查', 'fps': 60,
                'scenes': [target(source, base, self.assets.slots(manifest, source))]}
        path = self.root / 'wrong-talk-spec.json'; path.write_text(json.dumps(spec))
        for duration in [1, 30, 1200]:
            with self.subTest(duration=duration):
                talk = self.root / f'{duration}s-talk.mp4'
                run(['ffmpeg', '-v', 'error', '-n', '-i', self.assets.clips[duration],
                     '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', duration,
                     '-c:v', 'copy', '-c:a', 'aac', talk])
                # The actual public builder is called with a real video+audio
                # file. There is no mocked import or ffprobe.
                with self.assertRaisesRegex(AdaptError, 'Stopped before frame extraction'):
                    build(pack, path, talk, self.root / f'refused-{duration}', None)
                self.assertFalse((self.root / f'refused-{duration}').exists())
                self.assertFalse(list(self.root.glob('.adu-macro-*')))
                matched = {**spec, 'scenes': [{'sceneId': source['id'], 'durationFrames': duration * 60}]}
                # A matching length passes only this preflight, not the scene's
                # motion/hold capacity. The matrix independently rejects long
                # single groups and accepts multi-group long plans.
                checked = preflight_narration(manifest, matched, talk)
                self.assertEqual(checked['expectedFrames'], duration * 60)
                self.rows.append({'case': 'real-narration-preflight', 'sourceSeconds': duration,
                                  'mismatchedPlanRejectedBeforeExtraction': True,
                                  'matchingFrameClock': checked['frames'], 'accepted': True})


if __name__ == '__main__':
    unittest.main()

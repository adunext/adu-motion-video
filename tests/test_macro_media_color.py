from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adapt_project import compile_plan
from build_macro_project import copy_media
from color_management import export_plan, fingerprint_file
from export_project import probe, sources, verify_frame_clock
from verify_delivery import verify_delivery


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result.stdout


class MacroMediaColorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='adu-macro-media-color-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.stage = self.root / 'project'
        (self.stage / 'sc').mkdir(parents=True)
        (self.stage / 'index.html').write_text('<body><script>window.END=.2;window.READY=Promise.resolve();window.renderAt=t=>{};</script>')

    def make_video(self, path, *, hdr=False):
        matrix, primaries, transfer = ('bt2020nc', 'bt2020', 'arib-std-b67') if hdr else ('bt709', 'bt709', 'bt709')
        run(['ffmpeg', '-n', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=0xbf7e5b:s=160x90:r=30:d=0.2',
             '-vf', f'setparams=range=limited:colorspace={matrix}:color_primaries={primaries}:color_trc={transfer}',
             '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', matrix,
             '-color_primaries', primaries, '-color_trc', transfer, path])

    def prepare(self, *, hdr=False, review=None):
        video = self.root / ('hdr.mp4' if hdr else 'sdr.mp4')
        self.make_video(video, hdr=hdr)
        if callable(review):
            review = review(video)
        scene = {'id': 'proof', 'source': {'start': 0, 'end': .2},
                 'slots': [{'id': 'clip', 'type': 'video', 'sourceAsset': 'evidence',
                            'playback': {'start': 0, 'end': .2, 'fps': 30}}]}
        pack = {'id': 'test', 'fps': 30, 'width': 160, 'height': 90, 'scenes': [scene]}
        value = {'path': str(video)}
        if review is not None:
            value['colorReviewFile'] = str(review)
        spec = {'scenes': [{'id': 'one', 'sceneId': 'proof', 'durationFrames': 6, 'slots': {'clip': value}}]}
        plan = compile_plan(pack, spec)
        copy_media(self.stage, pack, plan['scenes'][0], scene, "seqAt('evidence',6,30,t,0,false)", set())
        (self.stage / 'macro_plan.json').write_text(json.dumps(plan))
        self.receipt_path = self.stage / 'media_color.json'
        self.receipt = json.loads(self.receipt_path.read_text())
        return video, next(iter(self.receipt['entries'][0]['files']))

    def export_record(self):
        self.output = self.root / 'output.mp4'
        self.make_video(self.output)
        identity = fingerprint_file(self.output)
        self.record = dict(schema='adu-motion-video-export/v1', created_utc='2026-10-03T12:00:00+08:00',
            project=str(self.stage), entry=str(self.stage / 'index.html'), output=str(self.output),
            output_sha256=identity['sha256'], output_size_bytes=identity['sizeBytes'], fps=30, frames=6,
            width=160, height=90, duration=.2, audio=None, reused_segments=False, verification='complete media decode',
            segments=[dict(index=0, first_frame=0, end_frame_exclusive=6, frames=6)],
            frame_clock=verify_frame_clock(self.output, 6, 30), color=export_plan(),
            streams=probe(self.output)['streams'], source_sha256=sources(self.stage))
        self.save_record()

    def save_record(self):
        Path(str(self.output) + '.manifest.json').write_text(json.dumps(self.record))

    def test_real_hdr_frames_are_converted_and_require_their_own_review(self):
        source, prepared = self.prepare(hdr=True)
        color = self.receipt['entries'][0]['color']
        self.assertTrue(color['toneMapped'])
        self.assertEqual(color['source_sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
        self.assertEqual(color['sourceEvidence']['bitDepth'], 8)
        naive = self.root / 'naive.jpg'
        run(['ffmpeg', '-n', '-v', 'error', '-i', source, '-frames:v', '1', '-q:v', '3', naive])
        with Image.open(naive) as before, Image.open(self.stage / prepared) as after:
            delta = max(abs(a - b) for a, b in zip(ImageStat.Stat(before.convert('RGB')).mean, ImageStat.Stat(after.convert('RGB')).mean))
        self.assertGreater(delta, 10, 'HDR conversion must change pixels, not only metadata')
        self.export_record()
        with self.assertRaisesRegex(ValueError, 'reviewEvidence is required'):
            verify_delivery(self.stage, self.output)
        # A different source's review cannot stand in for this evidence video.
        color['reviewEvidence'] = dict(sourceSha256='a' * 64, decision='accepted', reviewer='test fixture',
            reviewedAt='2026-10-03T12:00:00+08:00', reference='/private/reference', notes='Explicit test fixture only',
            acceptedSignals=[s['code'] for s in color['reviewSignals']])
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.record['source_sha256'] = sources(self.stage); self.save_record()
        with self.assertRaisesRegex(ValueError, 'sourceSha256 does not match'):
            verify_delivery(self.stage, self.output)
        color['reviewEvidence']['sourceSha256'] = color['source_sha256']
        self.receipt_path.write_text(json.dumps(self.receipt))
        self.record['source_sha256'] = sources(self.stage); self.save_record()
        result = verify_delivery(self.stage, self.output)
        self.assertTrue(result['preparedMediaColor']['entries'][0]['comparisonRecorded'])
        self.assertNotIn('/private/', json.dumps(result))

    def test_receipt_frames_and_export_binding_cannot_be_omitted_or_changed(self):
        _, prepared = self.prepare()
        self.export_record()
        self.assertTrue(verify_delivery(self.stage, self.output)['preparedMediaColor']['present'])
        original = self.receipt_path.read_bytes()
        self.receipt_path.write_text('{}')
        with self.assertRaisesRegex(ValueError, 'source changed'):
            verify_delivery(self.stage, self.output)
        self.receipt_path.write_bytes(original)
        digest = self.record['source_sha256'].pop(prepared); self.save_record()
        with self.assertRaisesRegex(ValueError, 'does not bind prepared media'):
            verify_delivery(self.stage, self.output)
        self.record['source_sha256'][prepared] = digest; self.save_record()
        image = self.stage / prepared
        image.write_bytes(image.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'Prepared media changed'):
            sources(self.stage)
        with self.assertRaisesRegex(ValueError, 'source changed'):
            verify_delivery(self.stage, self.output)

    def test_explicit_media_review_is_loaded_from_its_own_file(self):
        def review_for(video):
            path = self.root / 'review.json'
            path.write_text(json.dumps(dict(sourceSha256=fingerprint_file(video)['sha256'],
                decision='accepted', reviewer='explicit test fixture', reviewedAt='2026-10-03T12:00:00+08:00',
                reference='fixture-only comparison', notes='Not a real user or an appearance acceptance',
                acceptedSignals=['low-bit-depth-hdr'])))
            return path
        self.prepare(hdr=True, review=review_for)
        self.assertEqual(self.receipt['entries'][0]['color']['reviewEvidence']['reviewer'], 'explicit test fixture')
        self.export_record()
        self.assertTrue(verify_delivery(self.stage, self.output)['preparedMediaColor']['entries'][0]['comparisonRecorded'])

    def test_clock_video_without_receipt_cannot_pass_as_pure_motion(self):
        self.prepare()
        self.export_record()
        self.receipt_path.unlink()
        self.record['source_sha256'] = sources(self.stage); self.save_record()
        with self.assertRaisesRegex(ValueError, 'requires media_color.json'):
            verify_delivery(self.stage, self.output)

    def test_actual_exporter_binds_prepared_frames_and_gate_rechecks_receipt(self):
        self.prepare()
        output = self.root / 'rendered.mp4'
        run([sys.executable, ROOT / 'scripts/export_project.py', self.stage, output,
             '--fps', '30', '--width', '160', '--height', '90', '--segments', '1', '--no-audio'])
        record = json.loads(Path(str(output) + '.manifest.json').read_text())
        self.assertIn('media_color.json', record['source_sha256'])
        self.assertEqual(sum(k.startswith('sc/') for k in record['source_sha256']), 6)
        self.assertEqual(verify_delivery(self.stage, output)['status'], 'verified')


if __name__ == '__main__':
    unittest.main()

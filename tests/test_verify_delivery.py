from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from color_management import EXPORT_COLOR, export_plan, fingerprint_file, image_plan
from export_project import probe, sources, verify_frame_clock
from verify_delivery import verify_delivery


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-4000:])
    return result.stdout


class DeliveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='adu-delivery-test-')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.project = self.base / 'project'; self.project.mkdir()
        (self.project / 'index.html').write_text('<body style="background:#bf7e5b"><script>window.END=.2;window.READY=Promise.resolve();window.renderAt=t=>{};</script>')
        self.video = self.base / 'new.mp4'
        self.make_video(self.video)
        self.manifest = Path(str(self.video) + '.manifest.json')
        identity = fingerprint_file(self.video)
        self.record = dict(schema='adu-motion-video-export/v1', created_utc='2026-10-03T12:00:00+08:00',
                           project=str(self.project), entry=str(self.project/'index.html'), output=str(self.video),
                           output_sha256=identity['sha256'], output_size_bytes=identity['sizeBytes'],
                           fps=30, frames=6, width=64, height=64, duration=.2, audio=None,
                           reused_segments=False, verification='complete media decode',
                           segments=[dict(index=0, first_frame=0, end_frame_exclusive=6, frames=6)],
                           frame_clock=verify_frame_clock(self.video,6,30), color=export_plan(),
                           source_sha256=sources(self.project), streams=probe(self.video)['streams'])
        self.save()

    def make_video(self, path, *, transfer='bt709', primaries='bt709', matrix='bt709', offset=False):
        args=['ffmpeg','-n','-v','error','-f','lavfi','-i','color=c=0xbf7e5b:s=64x64:r=30:d=0.2']
        filters = f'setparams=range=limited:colorspace={matrix}:color_primaries={primaries}:color_trc={transfer}'
        if offset: filters += ',setpts=PTS+1/TB'
        args += ['-vf',filters]
        run(args+['-c:v','libx264','-pix_fmt','yuv420p','-color_range','tv','-colorspace',matrix,
                  '-color_trc',transfer,'-color_primaries',primaries, path])

    def save(self):
        self.manifest.write_text(json.dumps(self.record))

    def add_import(self, *, hdr=False, review=False):
        source = self.base / 'source.mp4'
        self.make_video(source, transfer='arib-std-b67' if hdr else 'bt709',
                        primaries='bt2020' if hdr else 'bt709', matrix='bt2020nc' if hdr else 'bt709')
        color = image_plan(source)
        if review:
            color['reviewEvidence'] = dict(sourceSha256=color['source_sha256'], decision='accepted',
                reviewer='explicit test reviewer', reviewedAt='2026-10-03T12:00:00+08:00',
                reference='/private/real-source-and-native-reference', notes='Recorded comparison fixture',
                acceptedSignals=[s['code'] for s in color['reviewSignals']])
        (self.project/'import.json').write_text(json.dumps(dict(source='/private/input-original.mov',color=color)))
        self.record['source_sha256'] = sources(self.project); self.save()
        return color

    def test_real_sdr_video_verified_and_return_is_portable(self):
        self.add_import()
        result=verify_delivery(self.project,self.video)
        self.assertEqual(result['status'],'verified')
        self.assertEqual(result['output_sha256'],self.record['output_sha256'])
        self.assertEqual(result['color'],EXPORT_COLOR)
        self.assertTrue(result['importedColor']['present'])
        self.assertNotIn(str(self.base),json.dumps(result))
        self.assertNotIn('/private/',json.dumps(result))

    def test_missing_identity_rejected_without_backfilling_old_manifest(self):
        del self.record['output_sha256']; self.save()
        before=self.manifest.read_bytes()
        with self.assertRaisesRegex(ValueError,'output_sha256 is required'):
            verify_delivery(self.project,self.video)
        self.assertEqual(self.manifest.read_bytes(),before)

    def test_changed_output_or_project_source_is_rejected(self):
        original=self.video.read_bytes()
        self.video.write_bytes(original+b'changed')
        with self.assertRaisesRegex(ValueError,'Video bytes'):
            verify_delivery(self.project,self.video)
        self.video.write_bytes(original)
        (self.project/'index.html').write_text('different generation')
        with self.assertRaisesRegex(ValueError,'source changed'):
            verify_delivery(self.project,self.video)

    def test_unrecorded_talk_and_incomplete_import_are_rejected(self):
        talk=self.project/'talk'; talk.mkdir(); (talk/'frame.jpg').write_bytes(b'fixture')
        with self.assertRaisesRegex(ValueError,'requires import.json'):
            verify_delivery(self.project,self.video)
        (self.project/'import.json').write_text(json.dumps({'color':{'toneMapped':True}}))
        self.record['source_sha256']=sources(self.project); self.save()
        with self.assertRaisesRegex(ValueError,'sourceEvidence'):
            verify_delivery(self.project,self.video)

    def test_hdr_risk_requires_source_bound_comparison_record(self):
        self.add_import(hdr=True)
        with self.assertRaisesRegex(ValueError,'reviewEvidence is required'):
            verify_delivery(self.project,self.video)
        receipt=json.loads((self.project/'import.json').read_text()); color=receipt['color']
        color['reviewEvidence']=dict(sourceSha256=color['source_sha256'], decision='accepted',
            reviewer='explicit test reviewer', reviewedAt='2026-10-03T12:00:00+08:00', reference='/private/native-reference',
            notes='Recorded comparison fixture',acceptedSignals=['low-bit-depth-hdr'])
        (self.project/'import.json').write_text(json.dumps(receipt))
        self.record['source_sha256']=sources(self.project); self.save()
        result=verify_delivery(self.project,self.video)
        self.assertTrue(result['importedColor']['comparisonRecorded'])
        self.assertNotIn('/private/',json.dumps(result))

    def test_actual_wrong_color_rejected_even_if_manifest_claims_bt709(self):
        wrong=self.base/'wrong.mp4'
        self.make_video(wrong,transfer='arib-std-b67',primaries='bt2020',matrix='bt2020nc')
        self.video.write_bytes(wrong.read_bytes())
        identity=fingerprint_file(self.video)
        self.record.update(output_sha256=identity['sha256'],output_size_bytes=identity['sizeBytes']); self.save()
        with self.assertRaisesRegex(ValueError,'color mismatch'):
            verify_delivery(self.project,self.video)

    def test_discontinuous_clock_rejected_even_with_valid_frame_count(self):
        wrong=self.base/'offset.mp4'; self.make_video(wrong,offset=True)
        self.video.write_bytes(wrong.read_bytes())
        identity=fingerprint_file(self.video)
        self.record.update(output_sha256=identity['sha256'],output_size_bytes=identity['sizeBytes']); self.save()
        with self.assertRaisesRegex(ValueError,'Frame clock discontinuity'):
            verify_delivery(self.project,self.video)

    def test_missing_clock_and_import_changed_since_export_are_rejected(self):
        clock=self.record.pop('frame_clock'); self.save()
        with self.assertRaisesRegex(ValueError,'frame clock evidence'):
            verify_delivery(self.project,self.video)
        self.record['frame_clock']=clock; self.add_import()
        receipt=self.project/'import.json'; receipt.write_text(receipt.read_text()+'\n')
        with self.assertRaisesRegex(ValueError,'source changed.*import.json'):
            verify_delivery(self.project,self.video)

    def test_actual_exporter_emits_content_identity_and_passes_gate(self):
        output=self.base/'rendered.mp4'
        run([sys.executable,ROOT/'scripts/export_project.py',self.project,output,'--fps','30',
             '--width','64','--height','64','--segments','2','--no-audio'])
        record=json.loads(Path(str(output)+'.manifest.json').read_text())
        self.assertEqual(record['output_sha256'],hashlib.sha256(output.read_bytes()).hexdigest())
        self.assertEqual(record['output_size_bytes'],output.stat().st_size)
        self.assertEqual(verify_delivery(self.project,output)['status'],'verified')


if __name__ == '__main__':
    unittest.main()

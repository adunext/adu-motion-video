from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from color_management import image_plan, verify_color
from PIL import Image, ImageStat


def run(args):
    p = subprocess.run([str(x) for x in args], capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode()[-4000:])
    return p.stdout


class ColorPipelineTests(unittest.TestCase):
    def test_hlg_and_pq_import_convert_pixels_and_keep_neutral_ramp(self):
        # Encoded neutral ramps span the HDR signal range, including highlights.
        # A tags-only fix would leave the centre patches equal to the old ramp.
        with tempfile.TemporaryDirectory(prefix='adu-color-test-') as temp:
            p = Path(temp)
            im = Image.new('RGB', (256, 64))
            im.putdata([(x, x, x) for _ in range(64) for x in range(256)])
            im.save(p / 'ramp.png')
            for trc in ('arib-std-b67', 'smpte2084'):
                clip = p / (trc + '.mp4')
                run(['ffmpeg', '-v', 'error', '-loop', '1', '-i', p/'ramp.png', '-f', 'lavfi',
                     '-i', 'anullsrc=r=48000:cl=stereo', '-t', '0.2', '-vf',
                     'scale=out_color_matrix=bt2020:out_range=limited,format=yuv420p,'
                     'setparams=range=limited:colorspace=bt2020nc:color_primaries=bt2020:color_trc='+trc,
                     '-c:v', 'libx264', '-color_range', 'tv', '-colorspace', 'bt2020nc',
                     '-color_primaries', 'bt2020', '-color_trc', trc, '-c:a', 'aac', clip])
                project = p/trc
                project.mkdir()
                run([sys.executable, ROOT/'scripts/import_talk.py', project, clip, '--fps', '30', '--size', '256x64'])
                receipt = json.loads((project/'import.json').read_text())
                self.assertTrue(receipt['color']['toneMapped'])
                mapped = Image.open(project/'talk/clip_000/f_00001.jpg').convert('RGB')
                samples = [mapped.getpixel((x, 32)) for x in (32, 64, 96, 128, 160, 192, 224)]
                self.assertTrue(all(max(c)-min(c) <= 2 for c in samples), samples)
                self.assertEqual(sorted(c[0] for c in samples), [c[0] for c in samples])
                self.assertGreater(max(abs(c[0]-x) for c,x in zip(samples,(32,64,96,128,160,192,224))), 8)

    def test_browser_export_srgb_roundtrip_and_video_color_contract(self):
        # Exercises the actual Chrome capture and encoder, including skin,
        # middle grey, blue, black and white, rather than checking filter text.
        colors = [(0,0,0),(255,255,255),(128,128,128),(191,126,91),(36,98,234),(224,34,52)]
        with tempfile.TemporaryDirectory(prefix='adu-color-render-test-') as temp:
            p=Path(temp)
            boxes=''.join('<div style="width:96px;height:128px;background:rgb'+str(c)+'"></div>' for c in colors)
            (p/'index.html').write_text('<body style="margin:0;display:flex">'+boxes+
                '<script>window.END=.2;window.READY=Promise.resolve();window.renderAt=t=>{};</script>')
            run(['node',ROOT/'scripts/render_project.mjs',p/'index.html','--output',p/'out.mp4',
                 '--fps','60','--width','576','--height','128'])
            s=json.loads(run(['ffprobe','-v','error','-select_streams','v:0','-show_streams','-of','json',p/'out.mp4']))['streams'][0]
            verify_color(s)
            plan=image_plan(p/'out.mp4')
            self.assertFalse(plan['toneMapped'])
            run(['ffmpeg','-v','error','-i',p/'out.mp4','-vf',plan['filter'],'-frames:v','1',p/'decoded.png'])
            im=Image.open(p/'decoded.png').convert('RGB')
            for i,color in enumerate(colors):
                mean=ImageStat.Stat(im.crop((i*96+32,32,i*96+64,96))).mean
                self.assertLessEqual(max(abs(a-b) for a,b in zip(mean,color)), 4, (color,mean))

    def test_wrong_matrix_or_range_is_rejected(self):
        with self.assertRaisesRegex(ValueError,'color mismatch'):
            verify_color(dict(pix_fmt='yuvj420p',color_range='pc',color_space='bt470bg',
                              color_primaries='bt709',color_transfer='bt709'))


if __name__ == '__main__':
    unittest.main()

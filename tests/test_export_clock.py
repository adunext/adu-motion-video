import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from export_project import verify, verify_frame_clock

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'requires ffmpeg and ffprobe')
class ExportClockTests(unittest.TestCase):
    def test_internal_timestamp_jump_is_rejected_even_when_metadata_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            for jitter in (False, True):
                p=Path(tmp)/('jitter.mp4' if jitter else 'good.mp4')
                vf='settb=1/6000,setpts=PTS'
                if jitter: vf += '+if(eq(N\\,6)\\,50\\,0)'
                subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','testsrc2=size=64x64:rate=60',
                                '-vf',vf,'-frames:v','12','-fps_mode','passthrough','-enc_time_base','1:6000',
                                '-c:v','libx264','-video_track_timescale','6000',str(p)],check=True)
                # Both pass the old count/rate/duration verification.
                verify(p,12,60,64,64)
                if jitter:
                    with self.assertRaisesRegex(RuntimeError,'Frame clock discontinuity'):
                        verify_frame_clock(p,12,60)
                else:
                    self.assertLess(verify_frame_clock(p,12,60)['max_error_seconds'],2e-6)

if __name__=='__main__': unittest.main()

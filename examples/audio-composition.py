"""Episode audio example using the shared track/SFX policy.

Supply sfx.json in the episode directory and choose a licensed replacement track.
No source melody/default synth is generated. For a silent layout fixture only,
set MUSIC={'mode':'none'} explicitly. Full macro builds freeze the runtime;
this starter example uses the explicitly located current skill implementation.
"""
from pathlib import Path
import os

# Edit these episode inputs; do not infer keywords or music offsets from a demo.
MUSIC = {'mode': 'track', 'path': '', 'offset': None}
ENV = []
HITS = {'crash': [], 'drop': [], 'riser': []}
DARK = []

skill = Path(os.environ.get('ADU_MOTION_VIDEO_ROOT', Path(__file__).resolve().parents[1]))
source = skill / 'template/audio.py'
if not source.is_file():
    raise SystemExit('Point ADU_MOTION_VIDEO_ROOT to the actual installed skill.')
# Execute the owned shared recipe with this episode's variables and directory;
# replacement music validation happens before any output is written.
code = source.read_text()
for assignment, value in [('MUSIC = dict(mode=\'track\', path=\'\', offset=None)', MUSIC),
                           ('ENV = []', ENV),
                           ('HITS = dict(crash=[], drop=[], riser=[])', HITS),
                           ('DARK = []', DARK)]:
    if code.count(assignment) != 1:
        raise SystemExit('Shared audio example changed; review the episode adapter.')
    code = code.replace(assignment, assignment.split(' = ', 1)[0] + ' = ' + repr(value))
os.environ['ADU_MOTION_VIDEO_ROOT'] = str(skill)
exec(compile(code, str(source), 'exec'), {'__file__': __file__, '__name__': '__main__'})

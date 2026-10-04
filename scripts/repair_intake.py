"""Consume one prepared repair master when explicitly planning in basic mode."""
from copy import deepcopy
from pathlib import Path
import json

from adapt_project import require


def prepare(brief, map_path=None):
    if brief.get('repairPolicy', {}).get('mode', 'off') == 'off':
        return brief  # Never read an old map or inherit previous permission.
    require(brief['repairPolicy']['mode'] == 'basic', 'Repair mode must be off or basic')
    require(map_path is not None, 'Basic planning requires --edit-map from a prepared master')
    from repair_talk import validate_master
    from narration_edit_map import normalize_intake_anchors
    path = Path(map_path).expanduser().resolve()
    raw = json.loads(path.read_text())
    edit, master = validate_master(path, Path(raw['source']['path']))
    result = deepcopy(brief)
    require(result.get('narrationClock') == 'edited-narration', 'Replan segments in edited-narration; source-time segments cannot be moved automatically')
    require(abs(result.get('narrationDuration', 0) * 60 - edit['editedFrames']) < .001,
            'Replan complete segments for the exact edited master duration')
    if (master / 'edited.srt').is_file():
        expected = master / 'edited.srt'
        if result.get('transcript'):
            from retime_subtitles import identity
            require(isinstance(result['transcript'], str) and identity(result['transcript']) == identity(expected),
                    'Use the derived edited SRT for basic planning')
        result['transcript'] = str(expected)
    anchors = {a['id']: a for a in normalize_intake_anchors(edit, edit.get('anchors', []))}
    require(len(anchors) == len(edit.get('anchors', [])), 'Duplicate intake anchor identity')
    routes = [result] + result.get('segmentations', [])
    for route in routes:
        offset = 0
        for segment in route.get('segments', []):
            for role, binding in segment.get('anchors', {}).items():
                if not isinstance(binding, dict) or 'intakeId' not in binding:
                    continue
                require(set(binding) == {'intakeId'}, 'intakeId cannot mix with local at/frame/phrase')
                anchor = anchors.get(binding['intakeId'])
                require(anchor is not None and anchor.get('clock') == 'edited-narration' and 'point' in anchor,
                        'Cue needs a protected narration point anchor')
                frame = anchor.get('outputFrame', round(anchor['point'] * 60)) - offset
                require(0 <= frame < segment['durationFrames'], 'Mapped anchor is outside its replanned segment')
                segment.setdefault('intakeBindings', {})[role] = deepcopy(anchor)
                segment['anchors'][role] = {'frame': frame}
            offset += segment['durationFrames']
    result['narrationEditMap'] = {'path': str(path), 'fingerprint': edit['fingerprint'], 'sourceSha256': edit['source']['sha256']}
    return result

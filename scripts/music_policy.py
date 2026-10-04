"""Episode music binding and retirement gate for new macro compositions."""
from copy import deepcopy
import hashlib
import math
from pathlib import Path

POLICY = 'adu-episode-music/1'
RETIRED = 'adu-source-score-synth-v1'
# Known historical rendition is also excluded when renamed and supplied as track.
RETIRED_SHA256 = {'6d7507eaec5974a02bd8bbbc9912a89e216521428a9b498da10db8bccaf39e65'}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def selection(value, base, duration=None, *, pending=False):
    """Return normalized binding + missing fields; never choose silent fallback."""
    if value is None:
        value = {'mode': 'track', 'path': '', 'offset': None}
    if not isinstance(value, dict):
        raise ValueError('music must specify the episode track, or explicit mode none')
    result = deepcopy(value)
    if result.get('mode') in ('synth', 'source-synth') or result.get('id') == RETIRED:
        raise ValueError(f'Music {RETIRED} is retired; select a replacement track with path/offset. '
                         'Explicit mode none is available only when no background music is intended.')
    mode = result.get('mode')
    if mode not in ('track', 'none'):
        raise ValueError('music must specify mode track or explicit mode none; no synthesized fallback')
    if mode == 'none':
        if any(key in result for key in ('path', 'offset', 'sha256')):
            raise ValueError('music mode none cannot carry an ignored track binding')
        return {'mode': 'none', 'policy': POLICY}, []
    missing = []
    path = result.get('path')
    if not isinstance(path, str) or not path.strip():
        missing.append('music.path: select a replacement episode track')
    offset = result.get('offset')
    if offset is None:
        missing.append('music.offset: align the replacement track explicitly')
    elif isinstance(offset, bool) or not isinstance(offset, (int, float)) or not math.isfinite(offset) or offset < 0:
        raise ValueError('music.offset must be an explicit finite nonnegative number')
    if missing:
        if pending:
            result['policy'] = POLICY
            return result, missing
        raise ValueError('; '.join(missing))
    path = Path(path).expanduser()
    path = (Path(base) / path).resolve()
    if not path.is_file():
        raise ValueError('music.path must name an existing replacement audio file')
    digest = sha(path)
    if digest in RETIRED_SHA256:
        raise ValueError(f'Supplied track is a retired {RETIRED} rendition; renaming it does not select replacement music')
    if result.get('sha256') and result['sha256'] != digest:
        raise ValueError('Selected music bytes changed; reselect/replan before rebuilding')
    if duration is not None:
        from adapt_project import probe_media
        metadata = probe_media(path, 'audio')
        length = metadata.get('duration')
        if not isinstance(length, (int, float)) or not math.isfinite(length) or length - offset < duration - 1 / 60:
            raise ValueError('music is shorter than the whole output after offset; supply a complete track, never silently loop')
    result.update(path=str(path), offset=offset, sha256=digest, policy=POLICY)
    return result, []


def apply(result, value, base):
    """Music is a global binding, separate from semantic group selection."""
    report, spec = result['report'], result['spec']
    try:
        music, missing = selection(value, base, report.get('durationSeconds'), pending=True)
        spec['music'] = music
        report['missing'].extend(missing)
        report['music'] = {'policy': POLICY, 'mode': music['mode'], 'missing': missing}
        if missing:
            report['ready'] = False
            if report['status'] != 'blocked':
                report['status'] = 'needs-binding'
    except ValueError as exc:
        report['blocking'].append(str(exc))
        report.update(ready=False, status='blocked')
        report['music'] = {'policy': POLICY, 'rejected': str(exc)}
    spec['adaptation']['ready'] = report['ready']
    return result

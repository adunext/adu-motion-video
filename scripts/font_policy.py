"""Portable fonts: original faces are recommendations, not material blockers."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
FORMATS = {'.ttf': 'truetype', '.otf': 'opentype', '.woff': 'woff', '.woff2': 'woff2'}
ALIASES = ['Adu Sans', 'PingFang SC', 'Hannotate SC', 'STKaiti', 'YSBT', 'Geist',
           'Adu Mono', 'SFM', 'Geist Mono']


def policy(spec):
    mode = spec.get('fontPolicy', 'preferred')
    if not isinstance(mode, str) or mode not in {'preferred', 'exact'}:
        raise ValueError('fontPolicy must be preferred or exact')
    return mode


def weight(item):
    value = str(item.get('weight', item['id'].rsplit('-', 1)[-1]
                        if re.search(r'-[1-9]00$', item['id']) else '400'))
    if not re.fullmatch(r'[1-9]00(?: [1-9]00)?', value) or int(value.split()[0]) > int(value.split()[-1]):
        raise ValueError('Invalid external font weight')
    return value


def declarations(pack, spec):
    items = pack.get('externalFonts', [])
    inputs = spec.get('externalFontFiles', {})
    if not isinstance(items, list) or not isinstance(inputs, dict):
        raise ValueError('externalFonts must be an array; externalFontFiles must be an object')
    ids = [x.get('id') for x in items if isinstance(x, dict)]
    if len(ids) != len(items) or any(not isinstance(x, str) for x in ids) or len(set(ids)) != len(ids):
        raise ValueError('External font IDs must be distinct')
    if set(inputs) - set(ids):
        raise ValueError('Unknown externalFontFiles ID')
    for item in items:
        if not re.fullmatch(r'[a-z][a-z0-9-]*', item.get('id', '')):
            raise ValueError('Invalid external font ID')
        if not isinstance(item.get('family'), str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 _-]*', item['family']):
            raise ValueError('Invalid external font family')
        if not isinstance(item.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', item['sha256']):
            raise ValueError('External font needs a frozen SHA256 recommendation')
        if not isinstance(item.get('extension'), str) or FORMATS.get(item.get('extension')) != item.get('format'):
            raise ValueError('Unsupported external font format/extension')
        weight(item)
    return items, inputs


def inspect_file(raw, directory):
    if raw in (None, ''):
        return None, None, 'recommended font not supplied'
    if not isinstance(raw, str):
        raise ValueError('Font path must be a string')
    file = (directory / Path(raw).expanduser()).resolve()
    if not file.is_file():
        return None, None, 'recommended font file unavailable'
    if file.suffix.lower() not in FORMATS:
        return None, None, 'unsupported font file format'
    try:
        from fontTools.ttLib import TTFont
        with file.open('rb') as stream:
            with TTFont(stream, lazy=True) as face:
                cmap = face.getBestCmap()
                if not cmap:
                    return None, None, 'font has no usable Unicode character map'
                points = sorted(cmap)
        return file, points, None
    except Exception as exc:
        # Unreadable recommendations never prevent the bundled font route.
        return None, None, 'font unavailable or invalid (' + type(exc).__name__ + ')'


def choices(pack, spec, directory):
    mode = policy(spec)
    items, inputs = declarations(pack, spec)
    result = []
    for item in items:
        file, points, reason = inspect_file(inputs.get(item['id']), directory)
        actual = hashlib.sha256(file.read_bytes()).hexdigest() if file else None
        if mode == 'exact' and (not file or actual != item['sha256']):
            raise ValueError('Exact font requested: provide externalFontFiles.' + item['id'] +
                             ' with the reviewed SHA256; default preferred mode permits fallback')
        result.append(dict(item=item, file=file, points=points, actual=actual, reason=reason,
                           mode='recommended' if actual == item['sha256'] else 'user-substitute' if file else 'bundled-fallback'))
    return result


def recommendations(pack, spec, directory):
    return [dict(id=c['item']['id'], family=c['item']['family'], mode=c['mode'],
                 reason=c['reason'] or 'selected font differs from the source recommendation',
                 action='Use actual rendered text bounds; original font is optional')
            for c in choices(pack, spec, directory) if c['mode'] != 'recommended']


def unicode_ranges(points):
    ranges = []
    for p in points:
        if ranges and p == ranges[-1][1] + 1:
            ranges[-1][1] = p
        else:
            ranges.append([p, p])
    return ','.join('U+' + f'{a:X}' + ('-' + f'{b:X}' if b != a else '') for a, b in ranges)


def install(pack, spec, directory, stage):
    selected = choices(pack, spec, directory)
    source = ROOT / 'assets/fonts'
    lock = json.loads((source / 'sources.json').read_text(encoding='utf-8'))
    target = stage / 'fonts'; target.mkdir(exist_ok=True)
    for record in lock['files']:
        file = source / record['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Bundled font installation is damaged: ' + record['file'])
        shutil.copy2(file, target / file.name)
    shutil.copy2(source / 'sources.json', target / 'sources.json')
    families = list(dict.fromkeys(ALIASES + [c['item']['family'] for c in selected]))
    css = []
    # Alias the source family names without editing frozen scene code. Each
    # generated project carries the same OFL fallback files on either OS.
    for family in families:
        mono = 'mono' in family.lower() or family == 'SFM'
        css.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:100 900;src:url(fonts/NotoSansSC.ttf) format('truetype')}}")
        if mono:
            css.append(f"@font-face{{font-family:'{family}';font-style:normal;font-weight:100 900;unicode-range:U+0000-024F,U+2000-206F;src:url(fonts/NotoSansMono.ttf) format('truetype')}}")
    report = []
    for c in selected:
        item = c['item']
        relative = 'fonts/' + ('NotoSansMono.ttf' if 'mono' in item['family'].lower() else 'NotoSansSC.ttf')
        if c['file']:
            destination = target / (item['id'] + c['file'].suffix.lower())
            shutil.copy2(c['file'], destination); relative = destination.relative_to(stage).as_posix()
            css.append(f"@font-face{{font-family:'{item['family']}';font-style:normal;font-weight:{weight(item)};unicode-range:{unicode_ranges(c['points'])};src:url({relative}) format('{FORMATS[c['file'].suffix.lower()]}')}}")
        report.append(dict(id=item['id'], family=item['family'], mode=c['mode'],
                           sha256=c['actual'] or hashlib.sha256((stage / relative).read_bytes()).hexdigest(),
                           recommendedSha256=item['sha256'], projectFile=relative, reason=c['reason']))
    mono, points, reason = inspect_file(spec.get('monoFontFile'), directory)
    if spec.get('monoFontFile') and not mono and policy(spec) == 'exact':
        raise ValueError('Exact monoFontFile is unavailable or invalid')
    if mono:
        destination = target / ('source-mono' + mono.suffix.lower()); shutil.copy2(mono, destination)
        relative = destination.relative_to(stage).as_posix()
        css.append(f"@font-face{{font-family:'SFM';font-weight:100 900;unicode-range:{unicode_ranges(points)};src:url({relative}) format('{FORMATS[mono.suffix.lower()]}')}}")
        report.append(dict(id='source-mono', family='SFM', mode='user-supplied', projectFile=relative,
                           sha256=hashlib.sha256(mono.read_bytes()).hexdigest()))
    warnings = recommendations(pack, spec, directory)
    if spec.get('monoFontFile') and reason:
        warnings.append(dict(id='source-mono', family='SFM', mode='bundled-fallback', reason=reason,
                             action='Original mono font is optional; inspect actual text layout'))
    receipt = dict(schema='adu-portable-fonts/1', policy=policy(spec), portable=True,
                   source=lock, fonts=report, warnings=warnings,
                   review='Actual final fonts, glyph coverage, wrapping and text bounds; substitution is not original-font fidelity')
    (stage / 'font_policy.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return '\n'.join(css) + '\n', report

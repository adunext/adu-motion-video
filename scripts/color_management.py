#!/usr/bin/env python3
"""Explicit pixel conversion: input video -> browser sRGB -> limited BT.709 video.

Uses FFmpeg 9's libswscale perceptual color mapper (HLG/PQ EOTF, tone and
gamut mapping). Older builds fail before extraction, never silently relabel HDR.
"""
import argparse
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import subprocess

POLICY = 'adu-srgb-bt709/1'
COLOR_KEYS = ('color_range', 'color_space', 'color_transfer', 'color_primaries')
EXPORT_COLOR = dict(pix_fmt='yuv420p', color_range='tv', color_space='bt709',
                    color_transfer='bt709', color_primaries='bt709')
SOURCE_SCHEMA = 'adu-source-color/v1'


def fingerprint_file(source):
    """Hash the exact supplied bytes, without retaining a private absolute path."""
    source = Path(source)
    before = source.stat()
    digest = hashlib.sha256()
    with source.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    after = source.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Media changed while computing its fingerprint')
    return dict(sha256=digest.hexdigest(), sizeBytes=after.st_size)


@lru_cache(maxsize=1)
def pixel_depths():
    data = json.loads(subprocess.check_output(
        ['ffprobe', '-v', 'error', '-show_pixel_formats', '-of', 'json'], text=True))
    return {p['name']: [c['bit_depth'] for c in p.get('components', [])]
            for p in data.get('pixel_formats', [])}


def source_evidence(stream, *, still=False):
    """Record observable tags; never infer a lost HDR/DV history from skin colour."""
    depths = pixel_depths().get(stream.get('pix_fmt'), [])
    depth = min(depths) if depths else None
    hdr = stream.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    dovi = [{k: x[k] for k in ('dv_profile', 'dv_level', 'rpu_present_flag',
             'el_present_flag', 'bl_present_flag', 'dv_bl_signal_compatibility_id') if k in x}
            for x in stream.get('side_data_list', []) if 'DOVI' in x.get('side_data_type', '')]
    signals = []
    if hdr and depth is None:
        signals.append(dict(code='hdr-bit-depth-unknown', message='HDR component depth is unknown; inspect the source and a native SDR reference.'))
    elif hdr and depth < 10:
        signals.append(dict(code='low-bit-depth-hdr', message='HDR is stored below 10 bits per component; verify the supplied derivative against its original/native SDR reference. Lost precision or earlier conversions cannot be recovered by tagging.'))
    if dovi:
        signals.append(dict(code='dolby-vision-base-layer-only', message='This converter uses the HDR base layer, not Dolby Vision dynamic metadata; compare skin, neutral and highlight regions with a native SDR reference.'))
    if not still and not hdr and any(stream.get(k) in (None, 'unknown', 'unspecified', 'reserved') for k in COLOR_KEYS):
        signals.append(dict(code='assumed-sdr-metadata', message='Some video colour tags are missing; SDR defaults are assumptions. Verify the supplied media rather than treating missing HDR tags as proof of SDR.'))
    return dict(schema=SOURCE_SCHEMA, codec=stream.get('codec_name', 'unknown'),
                pixelFormat=stream.get('pix_fmt', 'unknown'), bitDepth=depth,
                componentDepths=depths, dolbyVisionRecords=dovi,
                metadataLimit='Describes supplied bytes only; cannot detect upstream tone mapping, discarded Dolby Vision metadata, or lost precision.'), signals


def validate_review_evidence(color, review):
    """An explicit comparison record is required for each source risk signal."""
    codes = {s['code'] for s in color.get('reviewSignals', [])}
    if not codes:
        return
    if not isinstance(review, dict):
        raise ValueError('Color reviewEvidence is required for: ' + ', '.join(sorted(codes)))
    if review.get('sourceSha256') != color.get('source_sha256'):
        raise ValueError('Color reviewEvidence.sourceSha256 does not match the imported input')
    if review.get('decision') != 'accepted':
        raise ValueError('Color reviewEvidence.decision must explicitly be accepted after comparison')
    for key in ('reviewer', 'reference', 'notes', 'reviewedAt'):
        if not isinstance(review.get(key), str) or not review[key].strip():
            raise ValueError('Color reviewEvidence.' + key + ' is required')
    try:
        timestamp = datetime.fromisoformat(review['reviewedAt'].replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise ValueError('timezone missing')
    except ValueError as exc:
        raise ValueError('Color reviewEvidence.reviewedAt needs an ISO timestamp with timezone') from exc
    accepted = review.get('acceptedSignals')
    if not isinstance(accepted, list) or not all(isinstance(x, str) for x in accepted) or set(accepted) != codes:
        raise ValueError('Color reviewEvidence.acceptedSignals must cover exactly the source reviewSignals')


@lru_cache(maxsize=1)
def engine():
    version = subprocess.check_output(['ffmpeg', '-version'], text=True).splitlines()[0]
    options = subprocess.check_output(['ffmpeg', '-hide_banner', '-h', 'filter=scale'], text=True)
    match = re.search(r'ffmpeg version (\d+)', version)
    if not match or int(match[1]) < 9 or not all(x in options for x in ('in_transfer', 'out_primaries', 'perceptual tone mapping')):
        raise ValueError('Color conversion needs FFmpeg 9+ with libswscale color mapping. Install a capable build; HDR cannot be imported by changing tags.')
    return dict(policy=POLICY, engine='libswscale-perceptual', ffmpeg=version,
                runtimeSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def image_plan(source):
    streams = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
                        '-show_streams', '-of', 'json', str(source)], text=True))['streams']
    if not streams:
        raise ValueError('Input has no video stream')
    s = streams[0]
    hdr = s.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    known = lambda k: s.get(k) not in (None, 'unknown', 'unspecified', 'reserved')
    if hdr and not all(known(k) for k in COLOR_KEYS):
        raise ValueError('HDR input needs explicit range, matrix, transfer and primaries; supply a correctly tagged source.')
    still = Path(source).suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')
    jpeg = s.get('pix_fmt', '').startswith('yuvj')
    assumptions = {}
    def prop(k, fallback):
        if known(k):
            return s[k]
        assumptions[k] = fallback
        return fallback
    p = prop('color_primaries', 'bt709')
    t = prop('color_transfer', 'iec61966-2-1' if still or jpeg or s.get('color_range') == 'pc' else 'bt709')
    r = prop('color_range', 'pc' if still or jpeg or s.get('pix_fmt', '').startswith(('rgb', 'gbr', 'rgba')) else 'tv')
    m = prop('color_space', 'bt470bg' if jpeg else 'bt709')
    # RGB has no YCbCr matrix; do not force a matrix onto a PNG input.
    matrix = '' if s.get('pix_fmt', '').startswith(('rgb', 'gbr', 'rgba', 'bgr')) else f':in_color_matrix={m}'
    intent = 'perceptual' if hdr or p != 'bt709' else 'relative_colorimetric'
    vf = (f'scale=in_primaries={p}:in_transfer={t}:in_range={r}{matrix}'
          f':out_primaries=bt709:out_transfer=iec61966-2-1:out_range=full:intent={intent},'
          'format=rgb24,sidedata=mode=delete')
    # For SDR use the analytic colorspace transform. Applying the HDR mapper's
    # IPT gamut conversion to ordinary SDR introduces avoidable hue errors.
    if not hdr:
        if not matrix:
            begin = f'scale=in_primaries={p}:out_primaries={p}:in_transfer={t}:out_transfer={t}:in_range={r}:out_range=full:out_color_matrix=bt709,format=yuv444p,'
            m, r = 'bt709', 'pc'
        else:
            begin = 'format=yuv444p,'
        vf = (begin + f'colorspace=ispace={m}:irange={r}:iprimaries={p}:itrc={t}:'
              'space=bt709:range=pc:primaries=bt709:trc=srgb:format=yuv444p,'
              'scale=in_color_matrix=bt709:out_color_matrix=bt709:in_range=full:out_range=full:'
              'in_transfer=iec61966-2-1:out_transfer=iec61966-2-1:in_primaries=bt709:out_primaries=bt709,'
              'format=rgb24,sidedata=mode=delete')
    evidence, signals = source_evidence(s, still=still)
    identity = fingerprint_file(source)
    return dict(**engine(), sourceColor={k: s.get(k, 'unknown') for k in COLOR_KEYS},
                sourceEvidence=evidence, source_sha256=identity['sha256'], source_size_bytes=identity['sizeBytes'],
                reviewSignals=signals,
                assumptions=assumptions, hdr=hdr, toneMapped=hdr,
                target='sRGB / Rec.709 primaries / full-range RGB', filter=vf,
                dolbyVision='base-layer only' if any('DOVI' in x.get('side_data_type', '') for x in s.get('side_data_list', [])) else 'absent')


def export_plan():
    return dict(**engine(), input='Chrome forced sRGB, lossless RGB PNG', output=EXPORT_COLOR,
                conversion='analytic SDR colorspace transform',
                filter='scale=in_primaries=bt709:in_transfer=iec61966-2-1:in_range=full:'
                'out_primaries=bt709:out_transfer=iec61966-2-1:out_color_matrix=bt709:out_range=full,'
                'format=yuv444p,colorspace=ispace=bt709:irange=pc:iprimaries=bt709:itrc=srgb:'
                'space=bt709:range=tv:primaries=bt709:trc=bt709:format=yuv420p,sidedata=mode=delete')


def verify_color(stream):
    mismatch = {k: stream.get(k) for k, v in EXPORT_COLOR.items() if stream.get(k) != v}
    if mismatch:
        raise ValueError('Export color mismatch: ' + json.dumps(mismatch))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--export-plan', action='store_true')
    ap.add_argument('--image', type=Path)
    a = ap.parse_args()
    if a.export_plan:
        print(json.dumps(export_plan()))
    elif a.image:
        print(json.dumps(image_plan(a.image)))
    else:
        ap.error('Choose --export-plan or --image FILE')

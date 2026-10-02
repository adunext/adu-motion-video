#!/usr/bin/env python3
"""Explicit pixel conversion: input video -> browser sRGB -> limited BT.709 video.

Uses FFmpeg 9's libswscale perceptual color mapper (HLG/PQ EOTF, tone and
gamut mapping). Older builds fail before extraction, never silently relabel HDR.
"""
import argparse
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
    return dict(**engine(), sourceColor={k: s.get(k, 'unknown') for k in COLOR_KEYS},
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

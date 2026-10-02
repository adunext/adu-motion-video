#!/usr/bin/env python3
"""Read-only delivery gate for new exports, with portable colour provenance.

This validates technical evidence, not appearance or editorial approval. Old
exports without byte identities must not be retroactively blessed by this tool.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from color_management import (COLOR_KEYS, EXPORT_COLOR, POLICY, SOURCE_SCHEMA,
                              fingerprint_file, validate_review_evidence, verify_color)
from export_project import run, verify, verify_frame_clock


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def read_object(path, label):
    try:
        value = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError(label + ' is missing or invalid JSON') from exc
    require(isinstance(value, dict), label + ' must be a JSON object')
    return value


def imported_color(project, hashes):
    path = project / 'import.json'
    talk = project / 'talk'
    has_media = talk.is_dir() and any(p.is_file() for p in talk.rglob('*'))
    mapping = project / 'talkmap.js'
    has_media = has_media or (mapping.is_file() and re.search(r'\bTALKMAP\s*=', mapping.read_text()) is not None)
    if not path.exists():
        require(not has_media, 'Talk media requires import.json with source colour evidence')
        return dict(present=False, reviewSignals=[])
    require('import.json' in hashes, 'Export source_sha256 must bind import.json')
    imported = read_object(path, 'import.json')
    color = imported.get('color')
    return validated_color(color, hashes['import.json'], 'import.json.color')


def validated_color(color, receipt_sha256, label):
    """One source, one receipt, one source-bound comparison when indicated."""
    require(isinstance(color, dict), label + ' is required')
    evidence = color.get('sourceEvidence')
    require(isinstance(evidence, dict) and evidence.get('schema') == SOURCE_SCHEMA,
            label + '.sourceEvidence is missing or unsupported; prepare a new source with the current pipeline')
    require(sha(color.get('source_sha256')), label + '.source_sha256 is required')
    require(type(color.get('source_size_bytes')) is int and color['source_size_bytes'] > 0,
            label + '.source_size_bytes is required')
    require(color.get('policy') == POLICY and sha(color.get('runtimeSha256')) and color.get('filter'),
            label + ' needs policy, runtimeSha256 and conversion filter')
    require(all(k in evidence for k in ('codec', 'pixelFormat', 'bitDepth', 'componentDepths', 'dolbyVisionRecords')),
            label + '.sourceEvidence lacks codec/pixel format/depth/Dolby Vision evidence')
    require(isinstance(evidence['componentDepths'], list) and isinstance(evidence['dolbyVisionRecords'], list),
            'Source componentDepths and dolbyVisionRecords must be lists')
    source_color = color.get('sourceColor')
    require(isinstance(source_color, dict) and all(k in source_color for k in COLOR_KEYS),
            label + '.sourceColor needs range, matrix, transfer and primaries')
    hdr = source_color.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    require(color.get('hdr') is hdr and color.get('toneMapped') is hdr,
            label + ' HDR/toneMapped evidence contradicts the input transfer')
    require(not hdr or all(source_color[k] not in (None, 'unknown', 'unspecified', 'reserved') for k in COLOR_KEYS),
            'HDR import is missing explicit source colour tags')
    signals = color.get('reviewSignals')
    require(isinstance(signals, list) and all(isinstance(s, dict) and isinstance(s.get('code'), str) for s in signals),
            label + '.reviewSignals is required')
    codes = {s['code'] for s in signals}
    depth = evidence['bitDepth']
    require(depth is None or (type(depth) is int and depth > 0), 'Source bitDepth must be a positive integer or null')
    if hdr and depth is None:
        require('hdr-bit-depth-unknown' in codes, 'Unknown HDR depth requires a review signal')
    if hdr and depth is not None and depth < 10:
        require('low-bit-depth-hdr' in codes, 'Low-bit-depth HDR review signal is missing')
    if not hdr and any(source_color[k] in (None, 'unknown', 'unspecified', 'reserved') for k in COLOR_KEYS):
        require('assumed-sdr-metadata' in codes, 'Assumed SDR colour metadata review signal is missing')
    if evidence['dolbyVisionRecords']:
        require(color.get('dolbyVision') == 'base-layer only' and 'dolby-vision-base-layer-only' in codes,
                'Dolby Vision base-layer conversion must be declared and reviewed')
    validate_review_evidence(color, color.get('reviewEvidence'))
    # Whitelist only shareable fields; never return source paths or free-form
    # review notes/reference paths from a private input or project.
    return dict(present=True, receipt_sha256=receipt_sha256,
                source_sha256=color['source_sha256'], source_size_bytes=color['source_size_bytes'],
                sourceColor=source_color, pixelFormat=evidence['pixelFormat'], bitDepth=depth,
                hdr=hdr, toneMapped=color['toneMapped'], reviewSignals=sorted(codes),
                comparisonRecorded=bool(codes),
                coverage='Supplied input byte identity and its conversion receipt; original private source need not travel with the project.')


def prepared_media_color(project, hashes):
    """Verify every output-clock video binding and its actual prepared JPEG bytes."""
    plan_path = project / 'macro_plan.json'
    expected = {}
    if plan_path.exists():
        require('macro_plan.json' in hashes, 'Export source_sha256 must bind macro_plan.json')
        plan = read_object(plan_path, 'macro_plan.json')
        for scene in plan.get('scenes', []):
            for clock in scene.get('mediaClocks', []):
                key = (scene.get('id'), clock.get('slot'))
                require(key not in expected and all(isinstance(x, str) and x for x in key),
                        'Duplicate or invalid media clock binding')
                expected[key] = clock
    receipt_path = project / 'media_color.json'
    if not receipt_path.exists():
        require(not expected, 'Output-clock video media requires media_color.json; rebuild with colour evidence')
        return dict(present=False, entries=[])
    require('media_color.json' in hashes, 'Export source_sha256 must bind media_color.json')
    receipt = read_object(receipt_path, 'media_color.json')
    require(receipt.get('schema') == 'adu-macro-media-color/1' and isinstance(receipt.get('entries'), list)
            and receipt['entries'], 'Unsupported or empty media_color.json receipt')
    seen, results = set(), []
    for item in receipt['entries']:
        require(isinstance(item, dict), 'Media colour entry must be an object')
        key = (item.get('instanceId'), item.get('slotId'))
        require(all(isinstance(x, str) and x for x in key) and key not in seen,
                'Duplicate or invalid media colour binding')
        seen.add(key)
        label = '.'.join(key)
        color = validated_color(item.get('color'), hashes['media_color.json'], label + '.color')
        preparation, files = item.get('preparation'), item.get('files')
        require(isinstance(preparation, dict) and isinstance(files, dict) and files,
                label + ': preparation and file identities are required')
        count, directory = preparation.get('frames'), preparation.get('directory')
        require(type(count) is int and count > 0 and isinstance(directory, str) and directory,
                label + ': invalid frame count/directory')
        require(not Path(directory).is_absolute() and '..' not in Path(directory).parts,
                label + ': invalid prepared media directory')
        wanted = {f'{directory}/f_{i:04d}.jpg' for i in range(1, count + 1)}
        require(set(files) == wanted, label + ': prepared frame coverage is incomplete')
        require(isinstance(preparation.get('filter'), str) and item['color']['filter'] in preparation['filter'],
                label + ': preparation filter is not bound to the source colour conversion')
        clock = expected.get(key)
        if plan_path.exists():
            require(clock is not None, label + ': colour receipt has no media clock binding')
            require(clock.get('colorReceipt') == 'media_color.json' and clock.get('sourceSha256') == color['source_sha256']
                    and clock.get('directory') == Path(directory).name and clock.get('preparedFrames') == count
                    and clock.get('fps') == preparation.get('fps') and clock.get('offset') == preparation.get('offset'),
                    label + ': media clock and colour receipt disagree')
        for relative, identity in files.items():
            media = (project / relative).resolve()
            require(media.is_relative_to(project.resolve()) and media.is_file(), label + ': prepared media is missing or outside project')
            require(isinstance(identity, dict) and sha(identity.get('sha256'))
                    and type(identity.get('sizeBytes')) is int and identity['sizeBytes'] > 0,
                    label + ': invalid prepared frame identity')
            require(hashes.get(relative) == identity['sha256'], label + ': export source_sha256 does not bind prepared media')
            require(fingerprint_file(media) == identity, label + ': prepared media changed after conversion')
        results.append(dict(instanceId=key[0], slotId=key[1], preparedFrames=count, **color))
    require(set(expected) <= seen, 'Some output-clock video media lack colour receipts')
    return dict(present=True, receipt_sha256=hashes['media_color.json'], entries=results)


def verify_delivery(project: Path, video: Path) -> dict:
    project, video = Path(project).resolve(), Path(video).resolve()
    require(project.is_dir() and video.is_file(), 'Project directory and output video must exist')
    manifest_path = Path(str(video) + '.manifest.json')
    record = read_object(manifest_path, 'Video export manifest')
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    require(record.get('schema') == 'adu-motion-video-export/v1', 'Unsupported or missing export manifest schema')
    require(sha(record.get('output_sha256')), 'Export manifest output_sha256 is required; do not relabel an old export as verified')
    require(type(record.get('output_size_bytes')) is int and record['output_size_bytes'] > 0,
            'Export manifest output_size_bytes is required')
    identity = fingerprint_file(video)
    require(identity == dict(sha256=record['output_sha256'], sizeBytes=record['output_size_bytes']),
            'Video bytes do not match export manifest output_sha256/size')
    for key in ('fps', 'width', 'height', 'frames'):
        require(type(record.get(key)) is int and record[key] > 0, 'Export manifest ' + key + ' must be a positive integer')
    fps, count = record['fps'], record['frames']
    require(isinstance(record.get('duration'), (int, float)) and math.isfinite(record['duration']) and
            abs(record['duration'] - count / fps) < 1e-6, 'Export manifest duration does not match frames/fps')
    require('audio' in record and record.get('reused_segments') is False,
            'Export manifest must declare audio and fresh (not reused) segments')
    require(isinstance(record.get('created_utc'), str) and record['created_utc'], 'Export manifest created_utc is required')
    require('complete media decode' in str(record.get('verification', '')), 'Export manifest lacks complete decode evidence')
    segments = record.get('segments')
    require(isinstance(segments, list) and segments, 'Export manifest segment evidence is required')
    cursor = 0
    for i, segment in enumerate(segments):
        require(isinstance(segment, dict) and segment.get('index') == i and
                segment.get('first_frame') == cursor and type(segment.get('frames')) is int and segment['frames'] > 0,
                'Export manifest has missing, overlapping or out-of-order segments')
        cursor += segment['frames']
        require(segment.get('end_frame_exclusive') == cursor, 'Export segment endpoint disagrees with frame count')
    require(cursor == count, 'Export segment coverage does not match frames')
    clock = record.get('frame_clock', {})
    require(isinstance(clock, dict) and clock.get('frames') == count and clock.get('fps') == fps and
            isinstance(clock.get('max_error_seconds'), (int, float)) and 0 <= clock['max_error_seconds'] <= 2e-6,
            'Export manifest lacks matching per-frame clock evidence')
    color = record.get('color', {})
    require(isinstance(color, dict) and color.get('policy') == POLICY and color.get('output') == EXPORT_COLOR and
            sha(color.get('runtimeSha256')) and color.get('filter'), 'Export manifest colour conversion contract is incomplete')
    streams = record.get('streams', [])
    require(isinstance(streams, list), 'Export manifest streams must be a list')
    stream = next((s for s in streams if isinstance(s, dict) and s.get('codec_type') == 'video'), None)
    require(stream is not None, 'Export manifest video stream evidence is missing')
    verify_color(stream)
    require(stream.get('width') == record['width'] and stream.get('height') == record['height'] and
            str(stream.get('nb_read_frames')) == str(count), 'Export manifest video dimensions/frame count disagree')
    hashes = record.get('source_sha256')
    require(isinstance(hashes, dict) and hashes, 'Export source_sha256 is required')
    for name, digest in hashes.items():
        require(isinstance(name, str) and not Path(name).is_absolute() and sha(digest), 'Invalid export source_sha256 entry')
        source = (project / name).resolve()
        require(source.is_relative_to(project) and source.is_file(), 'Export source file is missing or outside the project: ' + name)
        require(hashlib.sha256(source.read_bytes()).hexdigest() == digest, 'Project source changed after export: ' + name)
    try:
        entry = Path(record['entry'])
        if entry.is_absolute():
            entry = entry.relative_to(Path(record['project']))
        require(str(entry) in hashes, 'Export entry HTML is not bound by source_sha256')
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError('Export manifest entry/project identity is missing or invalid') from exc
    imported = imported_color(project, hashes)
    prepared = prepared_media_color(project, hashes)
    try:
        actual = verify(video, count, fps, record['width'], record['height'], bool(record['audio']))
        actual_video = next(s for s in actual['streams'] if s['codec_type'] == 'video')
        verify_color(actual_video)
        actual_clock = verify_frame_clock(video, count, fps)
        run(['ffmpeg', '-v', 'error', '-xerror', '-i', video, '-map', '0:v:0', '-map', '0:a?', '-f', 'null', '-'])
    except (RuntimeError, OSError, StopIteration) as exc:
        raise ValueError('Delivery media verification failed: ' + str(exc)) from exc
    require(fingerprint_file(video) == identity, 'Video changed during delivery verification')
    require(hashlib.sha256(manifest_path.read_bytes()).hexdigest() == manifest_digest,
            'Export manifest changed during delivery verification')
    for name, digest in hashes.items():
        require(hashlib.sha256((project / name).read_bytes()).hexdigest() == digest,
                'Project source changed during delivery verification: ' + name)
    return dict(schema='adu-delivery-verification/v1', status='verified', video=video.name,
                output_sha256=identity['sha256'], output_size_bytes=identity['sizeBytes'],
                manifest_sha256=manifest_digest,
                frames=count, fps=fps, width=record['width'], height=record['height'],
                duration=count / fps, audio=bool(record['audio']), color=EXPORT_COLOR.copy(),
                frame_clock=actual_clock, importedColor=imported, preparedMediaColor=prepared,
                scope='Byte identity, source receipt, output colour tags, decoded frames, frame clock and complete decode.',
                limits='Technical verification does not certify appearance, skin colour, listening quality or unrecorded upstream conversions. Media outside the explicit prepared-video receipts are not fingerprinted by this gate.',
                visual_review='Not performed by this verifier.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('video', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(verify_delivery(args.project, args.video), ensure_ascii=False, indent=2))
    except (ValueError, OSError) as exc:
        parser.exit(1, 'Delivery rejected: ' + str(exc) + '\n')


if __name__ == '__main__':
    main()

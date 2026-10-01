#!/usr/bin/env python3
"""Freeze a new pack version containing only recipes covered by recorded review.

This records a human review; it does not watch films or certify supplied claims.
The source version and its runtime bytes remain unchanged. Private review files
stay outside the public pack; only labels and hashes of evidence are copied.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

COMMON_CHECKS = {
    'continuous-source-av', 'continuous-new-av', 'reuse-record',
    'clean-install', 'distribution-rights',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def freeze(source: Path, evidence_path: Path, readme_path: Path, target: Path):
    source, target = source.resolve(), target.resolve()
    require(not target.exists(), 'Publication target already exists; use a new version')
    require(target.parent.is_dir(), 'Publication parent must already exist')
    require(not target.is_relative_to(source) and not source.is_relative_to(target),
            'Publication target must be separate from the source version')
    manifest_bytes = (source / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    evidence = json.loads(evidence_path.read_text())
    require(manifest.get('sourceFormat') == 'authored-unit/1',
            'This publisher supports reviewed independent authored packs only')
    require(evidence.get('passed') is True and evidence.get('reviewer'),
            'Publication requires a passed review identifying the reviewer')
    for key, expected in [('packId', manifest['id']), ('sourceVersion', manifest['version']),
                          ('sourceRevision', manifest['sourceRevision']),
                          ('manifestSha256', sha(manifest_bytes))]:
        require(evidence.get(key) == expected, f'Review does not match frozen {key}')
    version = evidence.get('version', '')
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', version) and version != manifest['version'],
            'Provide a new explicit stable semantic version')
    scope = evidence.get('scope')
    require(scope in {'group', 'route-subset'}, 'Declare group or route-subset review scope')
    required = COMMON_CHECKS | ({'independent-use'} if scope == 'route-subset' else set())
    require(required <= set(evidence.get('checks', [])),
            f'Missing review checks: {sorted(required - set(evidence.get("checks", [])))}')
    limits = evidence.get('limits')
    require(isinstance(limits, list) and limits, 'Record actual validation limits')
    ids = evidence.get('recipes')
    require(isinstance(ids, list) and ids and len(ids) == len(set(ids)),
            'List unique reviewed recipe IDs')
    known = {scene['id']: scene for scene in manifest['scenes']}
    require(set(ids) <= set(known), 'Review names an unknown recipe')
    artifacts = evidence.get('artifacts')
    require(isinstance(artifacts, list) and artifacts, 'Provide labeled evidence hashes')
    for item in artifacts:
        require(isinstance(item, dict) and set(item) == {'id', 'sha256'}
                and re.fullmatch(r'[a-z][a-z0-9-]{0,95}', item['id'])
                and re.fullmatch(r'[a-f0-9]{64}', item['sha256']),
                'Public evidence must contain labels and SHA256 values, not private paths')

    selected = [copy.deepcopy(scene) for scene in manifest['scenes'] if scene['id'] in ids]
    omitted_files = {scene['sourceCodeFile'] for scene in manifest['scenes'] if scene['id'] not in ids}
    blobs = {}
    for relative, expected in manifest.get('files', {}).items():
        p = Path(relative)
        require(not p.is_absolute() and '..' not in p.parts, 'Frozen file path must be local')
        path = (source / p).resolve()
        require(path.is_relative_to(source), 'Frozen file escaped the source pack')
        data = path.read_bytes()
        require(sha(data) == expected, f'Frozen source changed: {relative}')
        if relative not in omitted_files:
            blobs[relative] = data
    require(blobs and 'README.md' in blobs, 'Source pack needs frozen files and a README')
    for scene in selected:
        require(scene['sourceCodeFile'] in blobs
                and sha(blobs[scene['sourceCodeFile']]) == scene['sourceBlockSha256'],
                f'Wrong reviewed source bytes: {scene["id"]}')
    readme = readme_path.read_bytes()
    require(f'{manifest["id"]}@{version}'.encode() in readme,
            'The reviewed README must name the new explicit pack version')
    public_review = {key: evidence[key] for key in
                     ['reviewer', 'passed', 'scope', 'checks', 'limits', 'recipes', 'artifacts']}
    if evidence.get('date'):
        public_review['date'] = evidence['date']
    blobs['README.md'] = readme
    blobs['review.json'] = (json.dumps(public_review, ensure_ascii=False, indent=2) + '\n').encode()
    promoted = copy.deepcopy(manifest)
    promoted.update(version=version, status='stable', scenes=selected)
    promoted['title'] = evidence.get('title', manifest.get('title', manifest['id']))
    promoted['promotedFrom'] = {'version': manifest['version'], 'manifestSha256': sha(manifest_bytes)}
    promoted.setdefault('environment', {})['status'] = 'stable'
    promoted['validation'] = {'review': 'review.json', 'scope': scope,
                              'sourceAndNewContent': 'owner-accepted',
                              'independentUse': 'recorded in review checks' if 'independent-use' in required
                              else 'not required for this single-group increment; no full-route claim',
                              'limits': limits}
    promoted.setdefault('distribution', {})['status'] = 'stable within recorded scope and environment'
    promoted['files'] = {name: sha(data) for name, data in sorted(blobs.items())}
    require((source / 'manifest.json').read_bytes() == manifest_bytes,
            'Source manifest changed during publication')
    with tempfile.TemporaryDirectory(prefix='adu-reviewed-pack-') as temporary:
        stage = Path(temporary) / 'pack'
        stage.mkdir()
        for name, data in blobs.items():
            path = stage / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        (stage / 'manifest.json').write_text(json.dumps(promoted, ensure_ascii=False, indent=2) + '\n')
        shutil.copytree(stage, target)
    return {'packId': manifest['id'], 'version': version, 'recipes': [s['id'] for s in selected],
            'sourceVersionPreserved': True, 'runtimeBytesUnchanged': True,
            'path': str(target), 'recordedHumanReview': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('evidence', type=Path)
    parser.add_argument('readme', type=Path)
    parser.add_argument('target', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(freeze(args.source, args.evidence, args.readme, args.target), ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        raise SystemExit(f'Pack publication failed: {exc}') from exc


if __name__ == '__main__':
    main()

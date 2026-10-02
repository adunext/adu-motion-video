#!/usr/bin/env python3
"""Review and adopt a local scene rematch without changing the original plan."""
from __future__ import annotations

import argparse
from copy import deepcopy
import difflib
import hashlib
import json
from pathlib import Path
import tempfile

from adapt_project import AdaptError, read_json, require
from adaptation import load_profile
from pack_catalog import resolve
from plan_macro_project import resolve_project_paths
from rematch import apply_rematch, propose_rematch

ROOT = Path(__file__).resolve().parents[1]
MEDIA_TYPES = {'image', 'video', 'audio', 'sequence', 'wall', 'wall-sprites'}
REVIEW_SCHEMA = 'adu-local-rematch-review/1'


def absolute_media(value, directory: Path):
    def absolute(path):
        return str((directory / Path(path).expanduser()).resolve())
    if isinstance(value, str) and value.strip() and value != '@talk':
        return absolute(value)
    if isinstance(value, dict) and isinstance(value.get('path'), str) and value['path'].strip():
        result = {**value, 'path': absolute(value['path'])}
        if isinstance(value.get('colorReviewFile'), str) and value['colorReviewFile'].strip():
            result['colorReviewFile'] = absolute(value['colorReviewFile'])
        return result
    return value


def normalize_target(target: dict, source: dict, directory: Path) -> dict:
    """Resolve only declared media references; leave semantic inputs intact."""
    target = deepcopy(target)
    for slot in source.get('slots', []):
        if slot.get('type') not in MEDIA_TYPES:
            continue
        sid = slot['id']
        if isinstance(target.get('slots'), dict) and sid in target['slots']:
            target['slots'][sid] = absolute_media(target['slots'][sid], directory)
        path = slot.get('inputPath')
        if isinstance(path, str) and isinstance(target.get('inputs'), dict):
            parts = path.split('.')
            container = target['inputs']
            try:
                for part in parts[:-1]:
                    container = container[int(part)] if isinstance(container, list) else container[part]
                key = int(parts[-1]) if isinstance(container, list) else parts[-1]
                container[key] = absolute_media(container[key], directory)
            except (KeyError, IndexError, TypeError, ValueError):
                pass  # Core validation reports the missing/invalid field.
    return target


def normalize_request(request: dict, manifest: dict, spec: dict, directory: Path) -> dict:
    result = deepcopy(request)
    sources = {s['id']: s for s in manifest['scenes']}
    target = next((s for s in spec.get('scenes', []) if s.get('id') == request.get('segmentId')), None)
    if target and isinstance(result.get('bindings'), dict):
        result['bindings'] = normalize_target({'slots': result['bindings']},
                                             sources.get(target['sceneId'], {}), directory)['slots']
    if isinstance(result.get('candidates'), dict):
        for sid, candidate in result['candidates'].items():
            if sid in sources and isinstance(candidate, dict):
                result['candidates'][sid] = normalize_target(candidate, sources[sid], directory)
    return result


def relocate_spec(spec: dict, manifest: dict, directory: Path) -> dict:
    result = resolve_project_paths(spec, directory)
    if isinstance(result.get('transcript'), str):
        result['transcript'] = absolute_media(result['transcript'], directory)
    sources = {s['id']: s for s in manifest['scenes']}
    result['scenes'] = [normalize_target(s, sources[s['sceneId']], directory) for s in result['scenes']]
    return result


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def diff_text(before, after) -> str:
    return ''.join(difflib.unified_diff(json_text(before).splitlines(keepends=True),
                                      json_text(after).splitlines(keepends=True),
                                      fromfile='before-spec.json', tofile='selected-spec.json'))


def report_markdown(bundle: dict) -> str:
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    lines = ['# 当前分镜重新匹配', '',
             '仅检查指定分镜。其余分镜、文案、时长、关键词锚点和全片声音设置保持原样。', '',
             '| 候选 | 状态 | 说明 |', '| --- | --- | --- |']
    for candidate in bundle.get('candidates', []):
        detail = candidate.get('reasons', []) + candidate.get('missing', [])
        state = {'ready': '可进入构建检查', 'needs-binding': '待补绑定', 'rejected': '不适配'}.get(candidate['status'], candidate['status'])
        lines.append('| ' + ' | '.join(cell(x) for x in (
            candidate.get('candidateId', candidate.get('sceneId')), state,
            '；'.join(detail) or '语义、动作窗、媒体与两侧连接合同通过')) + ' |')
    for candidate in bundle.get('candidates', []):
        lines += ['', '## ' + cell(candidate['candidateId']), '',
                  '动作家族：' + cell('、'.join(candidate.get('effects', []))) +
                  '；全片重复/强弱代价：' + cell(candidate.get('score', '未计算')) +
                  '（越低越优先，仅用于合法候选间比较）。', '']
        if candidate.get('mediaBindings'):
            lines += ['| 使用槽位 | 素材 | 来源 |', '| --- | --- | --- |']
            for binding in candidate['mediaBindings']:
                value = binding['value']
                path = value.get('path') if isinstance(value, dict) else value
                lines.append('| ' + ' | '.join(cell(x) for x in (
                    binding['slotId'], path, '、'.join(binding['origins']))) + ' |')
        for missing in candidate.get('unconsumedRequestBindings', []):
            lines += ['', '- 尚无消费位置：' + cell(missing['slotId'])]
        for check in candidate.get('deferred', []):
            lines += ['', '- 构建后检查：' + cell(check.get('reason', check.get('check')))]
    lines += ['', '完整候选、素材消费情况、效果评分和摘要见 `review.json`。', '',
              '应用时会再次检查原配置、合同和实际素材。原配置已变化、素材被覆盖或候选遭修改时，需要重新生成建议。', '',
              '可用候选可能仍是原镜头组。没有语义兼容的替代组时，不会为了多一种效果强行换动画。', '',
              '此报告不证明素材的事实含义或最终观感。共享 entityId 仍需核对真实来源；构建后重查接缝、色彩和完整音轨，音效尾音继续走原编舞重映。', '']
    return '\n'.join(lines)


def save_directory(output: Path, files: dict[str, str | bytes]) -> None:
    require(not output.exists() and not output.is_symlink(), f'Refusing existing directory: {output}')
    require(output.parent.is_dir(), f'Output parent does not exist: {output.parent}')
    with tempfile.TemporaryDirectory(prefix='.adu-rematch-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'result'
        stage.mkdir()
        for name, content in files.items():
            (stage / name).write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))
        # Do not replace an output another process created while validation ran.
        require(not output.exists() and not output.is_symlink(), f'Refusing existing directory: {output}')
        stage.rename(output)


def load_plan(pack_dir: Path, spec_path: Path, profiles_root: Path):
    manifest = read_json(pack_dir / 'manifest.json')
    raw = spec_path.read_bytes()
    spec = json.loads(raw)
    require(isinstance(spec, dict) and isinstance(spec.get('adaptation'), dict),
            'Local rematch requires a semantic macro-plan spec with adaptation metadata')
    metadata = spec['adaptation']
    profile = load_profile(manifest, profiles_root, metadata.get('profileId'), metadata.get('profileVersion'))
    return manifest, spec, profile, raw


def propose_files(pack_dir: Path, spec_path: Path, request_path: Path, output: Path,
                  profiles_root: Path = ROOT / 'adaptation-profiles', project: Path | None = None) -> dict:
    manifest, spec, profile, raw = load_plan(pack_dir, spec_path, profiles_root)
    request = normalize_request(read_json(request_path), manifest, spec, request_path.parent)
    bundle = propose_rematch(manifest, profile, spec, request, spec_path.parent,
                             project=project, allow_pending_talk=project is None)
    require(spec_path.read_bytes() == raw, 'Current spec changed while preparing the rematch')
    review = {'schema': REVIEW_SCHEMA,
              'origin': {'specDirectory': str(spec_path.parent.resolve()),
                         'specFileSha256': hashlib.sha256(raw).hexdigest()},
              'proposal': bundle}
    save_directory(output, {'before-spec.json': raw, 'request.json': json_text(request),
                            'profile.json': json_text(profile), 'review.json': json_text(review),
                            'report.md': report_markdown(bundle)})
    ready = [c['candidateId'] for c in bundle['candidates'] if c['status'] == 'ready']
    return {'output': str(output), 'ready': bool(ready), 'readyCandidates': ready,
            'status': 'ready' if ready else 'needs-attention'}


def apply_files(pack_dir: Path, spec_path: Path, review_path: Path, candidate_id: str, output: Path,
                profiles_root: Path = ROOT / 'adaptation-profiles', project: Path | None = None) -> dict:
    manifest, spec, profile, raw = load_plan(pack_dir, spec_path, profiles_root)
    review = read_json(review_path)
    require(review.get('schema') == REVIEW_SCHEMA, 'Unsupported rematch review schema')
    origin = review.get('origin', {})
    require(origin.get('specFileSha256') == hashlib.sha256(raw).hexdigest(),
            'Current spec bytes changed after rematch; prepare a new review')
    require(origin.get('specDirectory') == str(spec_path.parent.resolve()),
            'Current spec directory changed; relative bindings require a new review')
    selected = apply_rematch(manifest, profile, spec, review.get('proposal'), candidate_id,
                             spec_path.parent, project=project, allow_pending_talk=project is None)
    relocated = relocate_spec(selected, manifest, spec_path.parent)
    require(spec_path.read_bytes() == raw, 'Current spec changed while applying the rematch')
    report = {'schema': 'adu-local-rematch-application/1', 'candidateId': candidate_id,
              'baseSpecFileSha256': hashlib.sha256(raw).hexdigest(),
              'selectedSpecSha256': hashlib.sha256(json_text(selected).encode()).hexdigest(),
              'outputSpecSha256': hashlib.sha256(json_text(relocated).encode()).hexdigest(),
              'pathRelocation': 'Declared file references are absolute in spec.json so the new directory keeps the same inputs.',
              'validationStage': selected['adaptation']['validationStage'],
              'next': 'Build a new project, inspect seams and media, then regenerate and audition the complete audio recipe.'}
    save_directory(output, {'before-spec.json': raw, 'selected-spec.json': json_text(selected),
                            'spec.json': json_text(relocated), 'profile.json': json_text(profile),
                            'application.json': json_text(report), 'changes.diff': diff_text(spec, selected),
                            'path-relocation.diff': diff_text(selected, relocated),
                            'report.md': '# 已采用局部分镜方案\n\n'
                            '新配置：`spec.json`。原始配置完整保留在 `before-spec.json`，原工程未修改。\n\n'
                            '分镜改动见 `changes.diff`；为支持新目录构建而绝对化的文件引用另见 `path-relocation.diff`。\n\n'
                            '下一步构建新工程，检查本期素材、相邻画面与音效尾音，再进行连续声画验收。\n'})
    return {'output': str(output), 'ready': True, 'candidateId': candidate_id, 'status': 'applied'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for command in ('propose', 'apply'):
        child = commands.add_parser(command)
        child.add_argument('pack')
        child.add_argument('spec', type=Path)
        child.add_argument('request' if command == 'propose' else 'review', type=Path)
        if command == 'apply':
            child.add_argument('candidate')
        child.add_argument('output', type=Path)
        child.add_argument('--project', type=Path, help='Existing imported project for strict talk-media checks')
        child.add_argument('--profiles-root', type=Path, default=ROOT / 'adaptation-profiles')
    args = parser.parse_args()
    try:
        pack = resolve(args.pack, ROOT / 'packs')
        spec, output = args.spec.expanduser().resolve(), args.output.expanduser().absolute()
        options = {'profiles_root': args.profiles_root.resolve(),
                   'project': args.project.expanduser().resolve() if args.project else None}
        if args.command == 'propose':
            result = propose_files(pack, spec, args.request.expanduser().resolve(), output, **options)
        else:
            result = apply_files(pack, spec, args.review.expanduser().resolve(), args.candidate, output, **options)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['ready'] else 2
    except (AdaptError, ValueError, OSError, TypeError) as exc:
        parser.exit(1, f'Local rematch failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())

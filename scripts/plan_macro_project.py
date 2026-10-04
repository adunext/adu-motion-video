#!/usr/bin/env python3
"""Plan complete authored groups from a timed semantic brief, without rendering."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from adaptation import load_profile, plan_adaptation, validate_profile
from adapt_project import AdaptError, read_json, require
from pack_catalog import resolve

ROOT = Path(__file__).resolve().parents[1]


def resolve_project_paths(brief: dict, directory: Path) -> dict:
    """The emitted spec lives elsewhere; episode files retain their identity."""
    from copy import deepcopy
    result = deepcopy(brief)
    def absolute(value):
        return str((directory / Path(value).expanduser()).resolve()) if isinstance(value, str) and value.strip() else value
    if 'monoFontFile' in result:
        result['monoFontFile'] = absolute(result['monoFontFile'])
    if 'colorReviewFile' in result:
        result['colorReviewFile'] = absolute(result['colorReviewFile'])
    if isinstance(result.get('transcript'), str):
        result['transcript'] = absolute(result['transcript'])
    if isinstance(result.get('externalFontFiles'), dict):
        result['externalFontFiles'] = {key: absolute(value) for key, value in result['externalFontFiles'].items()}
    if isinstance(result.get('music'), dict) and 'path' in result['music']:
        result['music']['path'] = absolute(result['music']['path'])
    return result


def markdown_report(report: dict, spec: dict) -> str:
    labels = {'ready': '绑定检查通过，待构建与声画验收', 'needs-binding': '已选场，待补本期绑定',
              'blocked': '未找到满足约束的完整组合'}
    lines = ['# 文案适配报告', '', labels.get(report['status'], report['status']), '',
             '语义由创作者/Agent 根据整段文案明确标注；此工具不从关键词猜测意图。检查通过不代表最终声画已验收。', '',
             '| 段落 | 文案 | 选用镜头组 | 时长 |', '| --- | --- | --- | --- |']
    selected = {s['id']: s for s in spec.get('scenes', [])}
    def cell(value):
        return str(value).replace('|', '\\|').replace('\n', ' ')
    for segment in spec['adaptation']['segments']:
        scene = selected.get(segment['id'], {})
        lines.append(f"| {cell(segment['id'])} | {cell(segment['text'])} | {cell(scene.get('sceneId', '待调整'))} | {segment['durationFrames'] / spec['fps']:.2f}s |")
    lines += ['', '## 待解决项', '']
    for reason in report.get('blocking', []) + report.get('missing', []):
        lines.append('- ' + cell(reason))
    if not report.get('missing') and not report.get('blocking'):
        lines.append('具体候选和接缝诊断如下。完整机器报告见 `report.json`。')
    rhythm = report.get('rhythm', {})
    if rhythm.get('sceneUsage'):
        lines += ['', '## 全片重复与停留检查', '',
                  f"{rhythm['segmentCount']} 段使用 {rhythm['uniqueSceneCount']} 种镜头组；以下是节奏复核提示，不会为减少重复而更改语义、动作或声音。", '',
                  '| 镜头组 | 次数 | 总时长 |', '| --- | --- | --- |']
        for row in rhythm['sceneUsage']:
            lines.append(f"| {cell(row['sceneId'])} | {row['count']} | {row['durationFrames'] / spec['fps']:.2f}s |")
        if rhythm.get('actionSpans'):
            lines += ['', '| 段落 | 声明动作保护窗 | 最后保护窗至段尾 |',
                      '| --- | --- | --- |']
            for row in rhythm['actionSpans']:
                lines.append(f"| {cell(row['segmentId'])} | {row['protectedSeconds']:.2f}s | {row['postProtectedSeconds']:.2f}s |")
            lines += ['', '保护窗之外不等于静止，须检查真实阅读、口播与动态证据。容量上限不是推荐时长。']
        for finding in rhythm.get('findings', []):
            location = ', '.join(finding.get('segmentIds', [])) or finding.get('segmentId', finding.get('sceneId', ''))
            lines.append(f"- **{cell(finding['code'])} {cell(location)}**：{cell(finding['suggestion'])}")
    if report.get('selection'):
        lines += ['', '## 动作与强弱', '', '| 段落 | 动作家族 | 强度（1–3） |', '| --- | --- | --- |']
        for item in report['selection']:
            lines.append(f"| {cell(item['segmentId'])} | {cell('、'.join(item['effects']))} | {item['energy']} |")
    lines += ['', '## 候选检查', '']
    for segment in report.get('segments', []):
        lines += ['### ' + cell(segment['segmentId']), '']
        for candidate in segment.get('candidates', []):
            state = {'ready': '可用', 'needs-binding': '待补绑定', 'rejected': '不匹配'}.get(candidate['status'], candidate['status'])
            detail = candidate.get('reasons', []) + candidate.get('missing', [])
            lines.append(f"- **{cell(candidate['sceneId'])} · {state}**：" + ('；'.join(cell(x) for x in detail) or '语义、绑定和时长检查通过'))
        lines.append('')
    if report.get('contentEvidence'):
        evidence = report['contentEvidence']
        lines += ['## 内容依据', '', '状态：' + cell(evidence['status']), '']
        for item in evidence.get('displayEvidence', []):
            lines.append('- ' + cell(item['segmentId']) + '.' + cell(item['field']) + ' ← ' + cell('、'.join(item['refs'])))
        lines.append('')
    if report.get('seamRejections'):
        lines += ['## 被排除的接缝', '']
        lines += ['- ' + cell(x) for x in report['seamRejections']]
        lines.append('')
    if report.get('deferred'):
        lines += ['## 构建时继续检查', ''] + ['- ' + cell(x) for x in report['deferred']] + ['']
    if report.get('search', {}).get('truncated'):
        lines += ['搜索达到候选数量上限；当前结果不代表穷尽所有组合。', '']
    lines += ['缺项补在原 brief 后，重新规划到新目录；不要只修改 ready 标记。构建时还会重验语义、槽位、时间窗和接缝。', '',
              '当前保持完整镜头组。效果多样性只在合法候选内优化；必要的重复不会被强制替换。音乐和动作音效继续由源编舞重映，最终仍需连续观看与试听。', '']
    return '\n'.join(lines)


def plan(pack_dir: Path, brief_path: Path, output: Path, profiles_root: Path = ROOT / 'adaptation-profiles', *, edit_map=None) -> dict:
    require(not output.exists() and not output.is_symlink(), f'Refusing existing plan directory: {output}')
    require(output.parent.is_dir(), f'Output parent does not exist: {output.parent}')
    manifest = read_json(pack_dir / 'manifest.json')
    profile = load_profile(manifest, profiles_root)
    validate_profile(profile, manifest)
    brief = resolve_project_paths(read_json(brief_path), brief_path.parent)
    from repair_intake import prepare
    brief = prepare(brief, edit_map)
    result = plan_adaptation(manifest, profile, brief, brief_path.parent, allow_pending_talk=True)
    from music_policy import apply
    apply(result, brief.get('music'), brief_path.parent)
    with tempfile.TemporaryDirectory(prefix='.adu-plan-', dir=output.parent) as tmp:
        stage = Path(tmp) / 'plan'
        stage.mkdir()
        for name, data in (('spec.json', result['spec']), ('report.json', result['report']),
                           ('profile.json', profile)):
            (stage / name).write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        (stage / 'report.md').write_text(markdown_report(result['report'], result['spec']))
        stage.rename(output)
    return {'output': str(output), 'status': result['report']['status'],
            'ready': result['report']['ready'], 'scenes': result['report']['selectedScenes']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pack', help='Explicit pack ID@version or pack directory')
    parser.add_argument('brief', type=Path)
    parser.add_argument('output', type=Path, help='New directory for spec and diagnostic reports')
    parser.add_argument('--edit-map', type=Path, help='Prepared basic-repair master; replan on edited clock')
    args = parser.parse_args()
    try:
        result = plan(resolve(args.pack, ROOT / 'packs'), args.brief.expanduser().resolve(), args.output.expanduser().absolute(), edit_map=args.edit_map)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['ready'] else 2
    except (AdaptError, ValueError, OSError) as exc:
        parser.exit(1, f'Adaptation planning failed: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())

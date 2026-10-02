# 新增素材后，只重新匹配当前分镜

`macro-rematch` 接收已保存的语义计划和一次明确的素材变更，检查当前分镜的候选；`macro-apply-rematch` 重新验证后，将选定方案保存到新目录。两步均为本地运算，不调用模型，不改原工程，不重新选择其它分镜。

## 使用范围

- 原计划须来自 `macro-plan`，包含 `adaptation`、稳定段落 ID、语义阶段、真实动作锚点和明确时长。历史 `macro-spec` 不能凭空补出这些信息。
- `bindings` 只更新当前组声明的视觉素材槽。原文字、数量、阶段、时间、音乐与音效设置保持原样。
- 换成其它组必须明确提供那个组自己的 `inputs` / `slots`。没有兼容组时，可以保留原动画、更换素材；不会把“图换成视频”当作改变文案意图的理由。
- 锁定组拒绝重配。需要同时改相邻组才能成立的连接返回受阻；工具不自行扩大修改范围。
- 实际文件类型、显示比例、可播放时长、受保护动作窗、两侧接缝均重验。未消费的额外输入、无槽可接的素材、超长文字或缺少锚点不能被静默丢弃。

## 准备一次变更

读取当前 spec，使用规范化 JSON 摘要锁定基线。下面示例假设当前分镜 ID 为 `evidence-1`，选用了 `classic-performance` 的 `evidence-focus`，其中 `overview` 是真实视频槽。请替换成实际存在的段落 ID 与本期路径。

```python
import json, sys
from pathlib import Path
sys.path.insert(0, '/已安装的/adu-motion-video/scripts')
from rematch import spec_digest

spec = json.loads(Path('/本期/规划/spec.json').read_text())
change = {
    'schema': 'adu-local-rematch/1',
    'baseSpecDigest': spec_digest(spec),
    'segmentId': 'evidence-1',
    'bindings': {'overview': {'path': '/本期/素材/新录屏.mp4', 'offset': 1.2}},
    'candidates': {}
}
Path('/本期/变更.json').write_text(json.dumps(change, ensure_ascii=False, indent=2))
```

请求中的相对素材路径相对于变更 JSON 所在目录；原 spec 的相对引用仍相对于原 spec。视频若有独立色彩核验记录，可在该绑定里提供 `colorReviewFile`，不能套用口播的记录。

```bash
bash scripts/pipeline.sh macro-rematch classic-performance@1.0.0 \
  /本期/规划/spec.json /本期/变更.json /本期/重配建议

# 检查 report.md / review.json，使用其中精确的 ready candidateId
bash scripts/pipeline.sh macro-apply-rematch classic-performance@1.0.0 \
  /本期/规划/spec.json /本期/重配建议/review.json evidence-focus /本期/采用方案
```

输出目录须尚不存在。提出建议时退出码 `0` 表示存在可构建前检查的候选，`2` 表示已保存待补/受阻报告，`1` 表示输入无效。应用只接受 `ready` 候选；`ready` 不代表最终声画通过。

默认仍处于口播导入前阶段，缺少导入后的真实人物帧会单列为延后检查。两个命令都可传入 `--project /本期/已有工程`，对已导入的 talk 帧和映射执行更严格的验证；不能在两次调用间更换验证上下文。

## 确保晚到结果不会覆盖新操作

建议绑定原 spec、包、profile、请求、候选和实际输入媒体的摘要。应用时重跑完整检查并比对摘要。同名文件被替换、原分镜被编辑、合同改变或建议文件遭修改，都要求重新提出建议。即使仅修改原 JSON 的字节排版，CLI 也保守地要求刷新建议。

`before-spec.json` 保留原文件的完整字节。采用目录的 `selected-spec.json` 是内核原样选择，`changes.diff` 列出分镜改动；最终 `spec.json` 将文件引用绝对化，以便在新目录构建，路径改动另列在 `path-relocation.diff`。原 spec 和已有成片始终由使用者保留。

## 声音、多样性与人工检查

候选评分考虑完整序列的重复动作和强弱，但只在语义、时长、素材与接缝合法的候选里比较。当前多数风格对一个意图仅有一个组，不能宣称已经生成了另一套动画。扩展效果需要真正提炼并验证同意图的新变体。

所有起止帧、原段文案和全片混音参数保持不变；新组的动作音效仍按其原编舞映射。建议记录清单级声音边界诊断。采用后用新 spec 构建新工程，重新生成 `audio / mix`，核对实际采集的音效及跨界尾音，再连续观看和试听最终编码文件。

`entityId` 只验证调用方声明的对象一致性。媒体 SHA 能防止文件在检查后被替换，不能证明两个不同文件确属同一作品或同一事实；真实来源、连接观感与肤色仍需对照。

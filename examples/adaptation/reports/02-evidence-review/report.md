# 文案适配报告

已选场，待补本期绑定

语义由创作者/Agent 根据整段文案明确标注；此工具不从关键词猜测意图。检查通过不代表最终声画已验收。

| 段落 | 文案 | 选用镜头组 | 时长 |
| --- | --- | --- | --- |
| meeting-evidence | 先看本次会议的原始记录，再看整理过程和最终行动表。三处变化值得检查：记录是否汇总，责任是否明确，后续是否有人跟进。 | evidence-focus | 16.00s |
| meeting-method | 将复盘拆成三步：把事实列出来，把决定写清楚，再给行动定日期。把这三步收进复盘卡，下一次开会前接着用。 | decompose-and-consolidate | 20.00s |

## 待解决项

- anchor overview (overview)
- anchor result (result)
- anchor focus (focus)
- slot overview
- slot detail
- slot result
- anchor concept (concept)
- anchor decompose (decompose)
- anchor result (result)

## 动作与强弱

| 段落 | 动作家族 | 强度（1–3） |
| --- | --- | --- |
| meeting-evidence | video-relay、sequential-focus、conclusion-reveal | 2 |
| meeting-method | keyword-impact、three-part-demo、card-archive、container-reveal | 3 |

## 候选检查

### meeting-evidence

- **claim-into-container · 不匹配**：intent 'evidence-result-observations' is not supported；required semantic phases missing or out of order: claim → method → distribution → proof → response；cardinality receivers needs an explicit count
- **evidence-focus · 待补绑定**：anchor overview (overview)；anchor result (result)；anchor focus (focus)；slot overview；slot detail；slot result
- **decompose-and-consolidate · 不匹配**：intent 'evidence-result-observations' is not supported；required semantic phases missing or out of order: concept → parts → consolidation → result；cardinality parts needs an explicit count

### meeting-method

- **claim-into-container · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: claim → method → distribution → proof → response；cardinality receivers needs an explicit count
- **evidence-focus · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: overview → detail → result → observations → conclusion；cardinality observations needs an explicit count；cardinality evidence needs an explicit count
- **decompose-and-consolidate · 待补绑定**：anchor concept (concept)；anchor decompose (decompose)；anchor result (result)

## 构建时继续检查

- {'sceneId': 'evidence-focus', 'instanceId': 'meeting-evidence', 'slot': 'presenter', 'check': 'imported-narration', 'stage': 'after-macro-build-import', 'reason': '本期 talk 在 macro-build 导入后验证；当前仅通过导入前检查'}
- {'sceneId': 'decompose-and-consolidate', 'instanceId': 'meeting-method', 'slot': 'presenter', 'check': 'imported-narration', 'stage': 'after-macro-build-import', 'reason': '本期 talk 在 macro-build 导入后验证；当前仅通过导入前检查'}

缺项补在原 brief 后，重新规划到新目录；不要只修改 ready 标记。构建时还会重验语义、槽位、时间窗和接缝。

当前保持完整镜头组。效果多样性只在合法候选内优化；必要的重复不会被强制替换。音乐和动作音效继续由源编舞重映，最终仍需连续观看与试听。

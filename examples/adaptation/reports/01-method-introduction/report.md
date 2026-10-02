# 文案适配报告

已选场，待补本期绑定

语义由创作者/Agent 根据整段文案明确标注；此工具不从关键词猜测意图。检查通过不代表最终声画已验收。

| 段落 | 文案 | 选用镜头组 | 时长 |
| --- | --- | --- | --- |
| care-method | 别靠记性照料阳台，先做一张照料卡。香草、观叶和多肉分别记录，每天根据这张卡调整。出差回来也有据可查。 | claim-into-container | 16.00s |
| care-checklist | 记录可以拆成三个支点：看叶片，量土壤，记变化。把三个支点归到照料卡里，下次调整时就有依据。 | decompose-and-consolidate | 18.00s |

## 待解决项

- anchor container (container)
- anchor proof (proof)
- anchor response (response)
- anchor concept (concept)
- anchor decompose (decompose)
- anchor result (result)

## 动作与强弱

| 段落 | 动作家族 | 强度（1–3） |
| --- | --- | --- |
| care-method | title-impact、container-reveal、staggered-distribution、presenter-reaction | 3 |
| care-checklist | keyword-impact、three-part-demo、card-archive、container-reveal | 3 |

## 候选检查

### care-method

- **claim-into-container · 待补绑定**：anchor container (container)；anchor proof (proof)；anchor response (response)
- **evidence-focus · 不匹配**：intent 'claim-method-proof-response' is not supported；required semantic phases missing or out of order: overview → detail → result → observations → conclusion；cardinality observations needs an explicit count；cardinality evidence needs an explicit count
- **decompose-and-consolidate · 不匹配**：intent 'claim-method-proof-response' is not supported；required semantic phases missing or out of order: concept → parts → consolidation → result；cardinality parts needs an explicit count

### care-checklist

- **claim-into-container · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: claim → method → distribution → proof → response；cardinality receivers needs an explicit count
- **evidence-focus · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: overview → detail → result → observations → conclusion；cardinality observations needs an explicit count；cardinality evidence needs an explicit count
- **decompose-and-consolidate · 待补绑定**：anchor concept (concept)；anchor decompose (decompose)；anchor result (result)

## 构建时继续检查

- {'sceneId': 'claim-into-container', 'instanceId': 'care-method', 'slot': 'presenter', 'check': 'imported-narration', 'stage': 'after-macro-build-import', 'reason': '本期 talk 在 macro-build 导入后验证；当前仅通过导入前检查'}
- {'sceneId': 'decompose-and-consolidate', 'instanceId': 'care-checklist', 'slot': 'presenter', 'check': 'imported-narration', 'stage': 'after-macro-build-import', 'reason': '本期 talk 在 macro-build 导入后验证；当前仅通过导入前检查'}

缺项补在原 brief 后，重新规划到新目录；不要只修改 ready 标记。构建时还会重验语义、槽位、时间窗和接缝。

当前保持完整镜头组。效果多样性只在合法候选内优化；必要的重复不会被强制替换。音乐和动作音效继续由源编舞重映，最终仍需连续观看与试听。

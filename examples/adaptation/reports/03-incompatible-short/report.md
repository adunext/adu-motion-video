# 文案适配报告

未找到满足约束的完整组合

语义由创作者/Agent 根据整段文案明确标注；此工具不从关键词猜测意图。检查通过不代表最终声画已验收。

| 段落 | 文案 | 选用镜头组 | 时长 |
| --- | --- | --- | --- |
| too-short-and-incomplete | 五个技巧，两秒讲完。 | 待调整 | 2.00s |

## 待解决项

具体候选和接缝诊断如下。完整机器报告见 `report.json`。

## 候选检查

### too-short-and-incomplete

- **claim-into-container · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: claim → method → distribution → proof → response；cardinality receivers needs an explicit count；claim-into-container needs at least 836 frames, got 120
- **evidence-focus · 不匹配**：intent 'concept-decomposition' is not supported；required semantic phases missing or out of order: overview → detail → result → observations → conclusion；cardinality observations needs an explicit count；cardinality evidence needs an explicit count；evidence-focus needs at least 880 frames, got 120
- **decompose-and-consolidate · 不匹配**：required semantic phases missing or out of order: concept → parts → consolidation → result；cardinality parts=5 is outside 3..3；decompose-and-consolidate needs at least 882 frames, got 120

缺项补在原 brief 后，重新规划到新目录；不要只修改 ready 标记。构建时还会重验语义、槽位、时间窗和接缝。

当前保持完整镜头组。效果多样性只在合法候选内优化；必要的重复不会被强制替换。音乐和动作音效继续由源编舞重映，最终仍需连续观看与试听。

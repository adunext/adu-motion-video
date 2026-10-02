# 冻结模板的适配能力

这里的 sidecar 为现有完整组增加规划合同，不修改 `packs/`。每份 profile 的 `pack` 锁定 ID、版本与完整 manifest 摘要，各 scene 再锁定 `sourceBlockSha256`。摘要算法是将 JSON 按键排序、UTF-8、`ensure_ascii=False`、分隔符 `,` / `:`、禁止 NaN 后计算 SHA-256。

全部为 `adaptation-experimental`，只做了源码与清单核对；已有原演出的稳定性不等于新重排组合通过声画验收。

| 模板 | Profile | 完整组数 |
| --- | --- | --- |
| 01-A 原片节奏 | [classic-performance@1.0.0](classic-performance/1.0.0.json) | 3 |
| 01-B 连续形变 | [continuous-performance@1.0.0](continuous-performance/1.0.0.json) | 2 |
| 01-C 纵深舞台 | [stage-performance@1.0.0](stage-performance/1.0.0.json) | 3 |
| 01-D 杂志分屏 | [editorial-performance@1.0.0](editorial-performance/1.0.0.json) | 3 |
| 01-E 节拍字效 | [kinetic-performance@1.0.0](kinetic-performance/1.0.0.json) | 3 |
| 02-A 纸面天平 | [paper-balance@1.0.0](paper-balance/1.0.0.json) | 1 |
| 02-B 纸面聚合 | [paper-ball-performance@1.0.0](paper-ball-performance/1.0.0.json) | 2 |
| 03-A 多屏展陈 | [anim4-showcase-macro@1.1.1-candidate](anim4-showcase-macro/1.1.1-candidate.json) | 9 |

`intents`、`requiredPhases`、`cardinality` 和 `cueRoles` 是机器匹配字段；brief 必须使用所选 profile 中的准确名字。`requiredPhases` 按顺序检查，`cardinality` 记录源码真实数量范围。`effects` / `energy` 是合法候选之间的全片规划偏好，不自动创造新变体。`entry` / `exit` 记录依赖和媒体实体接力；`splitPolicy` 全部是 `atomic`，并给出具体理由。

`sourceEvidence` 和 `audio.notes` 保留代码来源、原转场或声音限制，供连续声画核验。机器规划不能代替读这些限制，更不能把 `sourceEvidence.adjacencyValidation` 中的历史范围解释为任意新接缝通过验收。

使用与新模板提炼要求见[适配说明](../references/adaptive-composition.md)，具体输入和诊断见[公开示例](../examples/adaptation/README.md)。

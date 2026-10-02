# 同一模板，不同文案的规划示例

这三份 brief 都用于 `classic-performance@1.0.0`，不是可直接生成成片的素材包。文案为新写内容示意，没有真实录音或私人素材路径。关键词锚点保持空值，证据视频保持 `null`；对应报告必须明确未解决，不能回填原片文字和源时间。

| 文件 | 段落和预计选择 | 时长 / 数量 | 预期诊断 |
| --- | --- | --- | --- |
| [01-method-introduction.brief.json](01-method-introduction.brief.json) | 阳台照料：`claim-into-container` → `decompose-and-consolidate` | 16秒 + 18秒；3对象、3支点 | 表达与容量可规划；仍缺真实关键词时码和本期口播 |
| [02-evidence-review.brief.json](02-evidence-review.brief.json) | 会议复盘：`evidence-focus` → `decompose-and-consolidate` | 16秒 + 20秒；3证据、3观察、3支点 | 表达与容量可规划；仍缺3段真实证据、关键词时码和口播 |
| [03-incompatible-short.brief.json](03-incompatible-short.brief.json) | 两秒讲五个技巧 | 2秒、5项 | 不满足最短动作时间、固定3项、收束语义与输入要求；拒绝硬套 |

实际运行的报告：[方法介绍](reports/01-method-introduction/report.md) · [证据复盘](reports/02-evidence-review/report.md) · [不适配短稿](reports/03-incompatible-short/report.md)。报告是示例规划的可复现输出，不是成片验收。

第一份主张分发与第二份证据聚焦具有不同动画家族，归纳段复用同组是因为表达关系相同。规划器不为凑足效果数量而把证据演成无根据的主张，也不随机打乱方法顺序。

`decompose-and-consolidate` 只有第一项声明 `sample` 展示位，第二、第三项用各自的 `label` / `record` 表达。示例严格按这些真实字段填写；新增未被槽位消费的字段或数组项现在会受阻，不能假定写进 JSON 就一定出现在视频里。

```bash
bash scripts/pipeline.sh macro-plan classic-performance@1.0.0 \
  examples/adaptation/01-method-introduction.brief.json \
  /路径/本期工程/方法介绍规划
```

第三个参数是尚不存在的输出目录，生成 `spec.json`、`report.json`、`report.md`。第一、第二份预期 `needs-binding`，第三份预期 `blocked`；三份均为 `ready: false`，不能直接构建。保留报告中的淘汰原因和未解决项。补入真实媒体及人工标注或逐词对齐后的 cue，审核规划后再构建；示例自带的时长只是分镜预算，并非真实配音时间。

完整说明：[从一套模板适配不同文案](../../references/adaptive-composition.md)。

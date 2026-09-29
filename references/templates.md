# 基础模板目录（Quick-start）

这里的 9 个 `TPL` 是轻量组件，方便快速试画面或从零组合新场景。它们**不是** `packs/anim3` 的 12 场、`packs/anim4` 的 9 场完整编舞提取结果。希望保留原工程的多阶段运动、镜头、录屏与音效时，默认使用[完整工程包工作流](full-project-templating.md)。

每个基础函数生成一段短场景，自带入场、出场、音效和转场。所有时间都是**全片绝对秒数**，从新口播时间码取；SRT 仅有整句时间时，句内关键词需另行准确标注。文字里写 `*强调*` 会变成科技蓝。

通用参数（每个模板都有）：`t0` 开始 · `t1` 结束 · `bg` 底色 `paper|ink|blue` · `cam` 口播位置 `right|corner|none` · `tag` 左上角标签 · `trans` 转场 `wipe|circle|flash|blur|null`

| # | 模板 | 用在哪句话 | 专有参数 | 默认 |
|---|---|---|---|---|
| 01 | `TPL.hero` | 第一句 / 标题 | `lines:[[文字,秒]...]` `sub` | 纸白 · 右侧口播卡 · 砸入 + 震动 |
| 02 | `TPL.point` | 观点 + 2~4 个要点 | `words:[[词,秒,'slam'?]]` `cards:[[文字,秒]]` | 墨黑 · 闪屏 |
| 03 | `TPL.number` | 出现一个关键数字 | `label` `at` `value` `from` `unit` `sub` `dur` `fill` `fmt` | 科技蓝 · 擦除 |
| 04 | `TPL.compare` | 以前 vs 现在、A vs B | `left/right:{title,items}` `leftAt` `rightAt` `strikeAt` `stamp` | 纸白 · 圆形遮罩 · 划掉 + 盖章 |
| 05 | `TPL.steps` | 步骤、流程、教程 | `title` `steps:[[文字,秒]]`（2~5 步） | 纸白 · 时间线逐段点亮 |
| 06 | `TPL.quote` | 金句、高潮、结论 | `at` `lines:[...]` 或 `text` `by` `size` | 科技蓝 · 无人 · 砸下慢推 |
| 07 | `TPL.demo` | 软件 / 产品演示 | `title` `features:[[文字,秒]]` `seq:{dir,n,fps}` 或 `image` | 墨黑 · 窗口 + 打勾卡 |
| 08 | `TPL.checklist` | 盘点、总结、注意事项 | `title` `items:[[文字,秒]]`（≤5 条） | 纸白 · 逐条打勾 |
| 09 | `TPL.outro` | 口播结束后约 5 秒 | `title` `lines` `prompt` | 墨黑 · 终端打字 |

## 选基础模板的节奏

- 3 分钟口播 ≈ 12~20 个场景，单个场景 4~12 秒；同一个模板不要连续用两次
- 底色交替：纸白 → 墨黑 → 蓝 → 纸白…，整屏硬切
- 需要真人开场时可选 `hero`；结尾可用 `outro`，按本期内容安排高潮
- 数字、日期、评分必须来自文案；示意数据写进 `sub`：“示意数据”
- 模板不够用时再按 [api.md](api.md) 手写 `new Scene(...)`，写好后可以提炼成新模板加进 `templates.js`

## 新增模板的规则

1. 函数签名 `TPL.name = o => {...}`，只读 `o`，调用 `base(o, 默认值)` 拿场景、标签、口播和进度线
2. 所有状态由 `t` 计算（可跳帧、可倒退），不在 update 里累加状态
3. 自带 `S()` 音效，入场用 `show(..., {out: b.out})` 统一出场
4. 在 `template/scenes.js` 演示里加一行，跑 `stills` 截图检查后再提交

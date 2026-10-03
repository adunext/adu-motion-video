# 杂志分屏：分栏交接与遮罩 · 横竖屏候选

新版本 `editorial-performance@1.1.0-candidate` 保留 `1.0.0` 的原始镜头组源码与全部音效、动作窗。横屏沿用原几何；竖屏通过各内容层的布局适配器构建。

在 brief / spec 的顶层添加 `"layout": "portrait"`，经过 macro-plan → macro-build，输出自动为 1080×1920。省略 layout 使用横屏 1920×1080。不能只修改导出 W/H。

竖屏为 candidate；需根据本期文案、人物与素材完成连续声画检查。原稳定版本的验收不自动覆盖竖屏。字体、媒体、cue 和绑定规则见清单及[横竖屏说明](../../../references/portrait.md)。

本版媒体、字体、输入与源演出要求沿用[横屏基线说明](../1.0.0/README.md)。布局不会放宽语义阶段、固定数量或本期 cue 要求。

# 字幕可选方案

3.13.0-rc.1 共享字幕层保留原句、换行、Unicode 及合理重叠，按 `[t0,t1)` 显示。没有可信词时码时不估算逐字高亮。普通文本用 textContent；只有 SRT 明确标记 srt-basic 才解析 b/i/u，其他标签和属性保留为文字。

| 选项 | 配置 | 横屏 1920×1080 起点 |
| --- | --- | --- |
| 标准 | `subtitlePreset: 'standard'` | 中文 44px、英文 26px、top 872、gap 8 |
| 英文加大 | `subtitlePreset: 'large-en'` | 中文 44px、英文 30px、top 940、gap 6 |

竖屏默认按整块定位：底部留 18%、左右各 15%，多行向上展开，入场位移也计入包围盒。它是可调项目起点，并非官方平台安全线；须检查人物、关键标题和实际平台覆盖。没有复杂自动人脸避让，测量报告发现遮挡后需调整布局。

```js
subtitlePreset: 'standard',
subtitlePosition: {bottomRatio: .18, leftRatio: .15, rightRatio: .15},
subtitleStyle: {}, // 字号、gap 等；不得以旧 CSS 强制 top/bottom 覆盖比例
```

`subtitlePosition=null` 时，竖屏用上述默认比例，横屏沿用位置预设和可选 `subtitleXByStart`。显式比例模式不再应用旧工程的绝对 x 偏移。cue 内位置稳定，空间调整不改 SRT 文字/时间、素材 offset 或真人时钟。最长文本需用最终字体/画幅实测，超出可读区时调整短标题/排版或分段，不无限缩字。

旧工程接入共享 `template/subtitles.js` 时需有 CONFIG、SUBS、ov 挂载点，每帧调用 OVERLAY(t)。检查源片是否已有烧录字幕。换共享运行时须重渲新工程，不能称为原视频逐像素无损。

如需保留声音，核对实际帧数/时钟并保留原轨，不用 -shortest 意外截断；存在音轨不等于声音原样保留。本次三组完整 A/B 已单独核对原混音和最终解码音轨相同，新增声音配方另外回放，[范围见说明](quality-upgrade.md)。

`examples/subtitle-options.html` 是无私人媒体的短示例，不代表完整口播或声学同步验收。

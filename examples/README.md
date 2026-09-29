# 示例与动作配方

先运行不依赖用户媒体的示例，再把所需动作带入自己的工程。所有演示文案、评论和数字都是布局占位，发布前替换为自己的内容与真实数据。

## 可独立打开的示例

- `handdrawn-continuity.html`：8 秒 Canvas2D 手绘续接示例，无外部素材；点击/空格播放，`?t=2.8` 查看指定时间。
- `silent-demo.html`：图文动效最小示例，不含真人、配乐与字幕。
- `subtitle-options.html`：标准字幕、英文加大、长句与局部避让。加 `?preset=standard` 比较标准版。

其他独立示例与运行命令见仓库 README 和 [手绘动画方法](../references/handdrawn-animation.md)。

## 需要适配到工程的配方

| 文件 | 可学习的内容 | 使用边界 |
| --- | --- | --- |
| `card-layout-scenes.js` | 12 组实拍卡片、对比、时间线、终端和评论动作 | 需要运行时与所引用的图片/口播帧；不是独立网页 |
| `showcase-scenes.js` | 多格展陈、作品墙、主卡放大、镜头与字幕关系 | 需要运行时、媒体、字幕和新时间表 |
| `audio-composition.py` | 分段配器、音量包络、声点与素材原声 | 源码阅读配方，需提供所引用文件；新项目优先用 `template/audio.py` |
| `subtitle-groups.py` | 中英文分组与 SRT 序号映射 | 搭配自己的 SRT；示例句子不是转录结果 |
| `portrait-shell.html` | 横版内容与竖屏人物/字幕分区 | 放入匹配工程后修改标题、媒体、时长与布局，不独立运行 |

场景片段沿用全片绝对时间，复用时核对 `lib.js` API 与媒体依赖。片段里的局部辅助函数可能已在通用运行时内存在，需要去重。完整人物照片、视频帧与外部音乐不随包分发；`assets/presenter.png`、`assets/app-logo.png` 等是由用户提供的路径。

两大视觉家族与子方案见 [visual-routes.md](../references/visual-routes.md)，无需寻找任何私人视频题目或历史集数。

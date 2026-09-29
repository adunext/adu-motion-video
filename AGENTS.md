# adu-motion-video（通用 Agent 入口）

> 给不支持 Skill 机制的模型（Kimi、豆包、GLM、Qwen 等）使用：把本文件内容作为系统提示，或让模型先读它。`SKILL_DIR` 就是本仓库目录。模型需要能读写本地文件、执行 Bash 命令。


目标：**1 小时内**把一条口播做成能发布的动效视频。靠的是模板：每个场景是一行 `TPL.xxx({...})`，你只需要按字幕时间填参数。

`SKILL_DIR` = 本 skill 目录；`PL="$SKILL_DIR/scripts/pipeline.sh"`；`D` = 本次新工程目录（不存在的新路径）。

## 流程（按顺序做，不要跳）

| 步骤 | 命令 / 动作 | 产出 |
|---|---|---|
| 1 检查 | `bash "$PL" doctor`，缺依赖才 `bash "$PL" setup` | 环境 OK |
| 2 建工程 | `bash "$PL" new "$D"` | 36 秒演示工程（9 个模板各一次） |
| 3 导入口播 | `bash "$PL" import "$D" 口播.mp4` | `talk/` 帧、`talkmap.js`、`voice.wav`、`import.json` |
| 4 配置 | 改 `config.js`：`demo:false`、`end`=口播时长+5、`brand`、`account`、`race` | |
| 5 字幕 | 有 SRT：`python3 "$SKILL_DIR/scripts/build_subs.py" --srt 口播.srt --src subs_src.py --out "$D/subs.js"`（`subs_src.py` 写中英分组，见 [subtitle-options](references/subtitle-options.md)）；没有就 `subtitles:false` | `subs.js` |
| 6 分镜 | 先写一张表：时间 · 台词 · 模板 · 参数。模板选择见 [templates.md](references/templates.md) | 表给用户看 |
| 7 写场景 | 把 `scenes.js` 全部换成本集的 `TPL.xxx()` 调用 | |
| 8 抽帧 | `bash "$PL" stills "$D" 1.0,5.2,...`（每个场景取中点 + 最长字幕） | 看图修问题 |
| 9 声音 | 改 `audio.py`（有配乐放 `assets/music.mp3` 设 `mode='track'`）→ `bash "$PL" audio "$D"` → `bash "$PL" mix "$D" 0.5` | `mix.wav` |
| 10 导出 | `bash "$PL" render "$D" 输出/新片_v1_16x9_60fps.mp4` → `bash "$PL" check 该文件` | 成片 + 核验 |

改旧片：复制出新版本目录，在原工程里改，**保持原引擎**（DOM / Canvas / p5.brush 不互换）。

## 硬规则

1. **时间是口播绝对秒数**，从 SRT/`import.json` 读，不要估。分段渲染起止必须是整帧（t×fps 为整数）
2. **口型**：真人画面只从 `talkSrc(t)` 取帧，不改速、不冻结；补漏句用新口播帧
3. **第一帧就有人**：开场用 `TPL.hero`，标题左、口播卡右，第一句砸入
4. **字幕**：白字 + 深色描边（`paint-order:stroke fill`），无底板、无光晕，逐字变色
5. **配乐听得见**：说话时比人声低约 17dB、停顿约 13dB、高潮约 9dB；成片约 -15 LUFS，真峰值 ≤ -0.5dB
6. **不编数据**：数字、日期、结果只来自文案；示意数据在画面上标"示意"
7. **不覆盖**：输出新文件 `_v2/_v3`，用户原件不动

## 审美（阿杜标准，详见 [style.md](references/style.md)）

- 配色只用：纸白 `#F7F7F5` / 墨黑 `#0A0A0A` / 科技蓝 `#2462EA` / 中灰 `#8C8C8C`，场景间整屏硬切
- 字体：苹方 Semibold + Geist + 等宽标签。**禁止**书法/毛笔字、荧光绿、中英混搭强调词
- 动效：大字砸下、逐词打字、卡片侧滑回弹、数字滚动、划掉盖章、圆形遮罩。每个场景至少一个"有因果的状态变化"，不要只是元素淡入
- 卡通人物全片 ≤ 5 次，靠整体移动表演（弹入、探头、滑入），不做手部骨骼动画

## 汇报

给出：成片路径、工程路径、规格（宽高/帧率/帧数/LUFS）、实际检查范围（"抽了 N 帧 / 没有完整播放"），请用户看完整片。未核实的事实单独列出。

## 按需查阅

[templates.md](references/templates.md) 模板参数 · [api.md](references/api.md) 手写场景 · [audio.md](references/audio.md) 配乐 · [subtitle-options.md](references/subtitle-options.md) 字幕 · [portrait.md](references/portrait.md) 竖屏 · [handdrawn-animation.md](references/handdrawn-animation.md) 手绘续接 · [tooling.md](references/tooling.md) 导出参数 · [troubleshooting.md](references/troubleshooting.md) 排错 · [compatibility.md](references/compatibility.md) 多条原片对齐 · [scene-patterns.md](references/scene-patterns.md) 更多历史配方

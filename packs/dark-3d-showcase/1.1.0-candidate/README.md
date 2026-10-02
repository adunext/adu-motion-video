# 03-A · 深色 3D · 多屏展陈

调用版本：`anim4-showcase-macro@1.1.0-candidate`。完整保留旧 1.0.0 的九场源码、66 个语义节点、42 个动作保护窗和 175 个音效事件，新增 **1080×1920 原生竖屏布局**；横屏为 1920×1080，均按 60fps 制作。旧包保持原字节。

这是待最终声画确认的候选版本。不同内容九场样片与公开包复现的实际结果见[验证记录](../../../docs/validation.md)，不计入已有十七个稳定组。动画保持原引擎；人物口型和字幕使用输出时钟，源动作按保护窗口运行。

## 完整制作

先根据新口播选择有意义的完整场景。`s02` 与 `s03` 的持续视频整场保持 1×，不能压缩；其它场景只调整允许持留区。九场不必每次全部使用，场景 ID、输入槽与素材要求见 [manifest](manifest.json) 和 [模板说明](../../../references/dark-3d-template.md)。

```bash
bash scripts/pipeline.sh macro-spec anim4-showcase-macro@1.1.0-candidate inputs.json
# 填写本期文案、实际素材、数值和 cues；总帧数须与剪好口播相同
bash scripts/pipeline.sh macro-build anim4-showcase-macro@1.1.0-candidate inputs.json talk.mp4 project --subs-js subs.js
bash scripts/pipeline.sh audio project
bash scripts/pipeline.sh mix project

# 创建新的竖屏工程，不覆盖 project
node packs/dark-3d-showcase/1.1.0-candidate/apply-layout.mjs project project-portrait --layout portrait
W=1080 H=1920 bash scripts/pipeline.sh render project-portrait portrait.mp4
bash scripts/pipeline.sh check portrait.mp4
```

横屏直接导出基础工程。若输入包含真人结束后独立制作的信息卡片尾，可以在 `apply-layout.mjs` 中显式传入 `--presenter-end 真人结束秒数`；该时刻后隐藏人物窗，不展示冻结的真人帧。旁白音轨仍由输入和混音决定。输入尾段应是实际信息卡或无人物画面，不能用这一选项掩盖口型错位。

## 竖屏如何保留演出

标题与人物采用上下布局；大人物卡缩到右上方；九屏错峰入场保持三列，比较与计数面板移到下方。重点视频仍从小卡放大，再交给报告与前作。四类材料排成两列；软件窗口保持纵深、入场和离场，信息卡移到窗口下方。时间线、赛道、统计卡、工作窗口、行动按钮与片尾继续使用原动作时钟。

适配器绑定冻结版本的结构角色与节点数，不按演示文案匹配位置。所选场景变化或使用旧版本时会拒绝。源场景内的内部录像速度依然保留：软件段有约 0.88× 和 2.4×，其它循环、终帧停留以源码和素材契约为准；“保护动作 1×”不等于所有素材视频都按原速播放。需验证素材内容与屏幕标签。

## 素材与环境

媒体准备器沿用旧包的帧数、路径与画幅契约，参见[完整素材说明](../../anim4/README.md#媒体准备)。九屏需要九路独立视频；作品墙至少 27 件独立作品，铺满的 389 个格子不能作为独立作品数量。它们和头像、录屏、字幕、系统字体均不随公开包分发。

`prepare_media.py` 接受本地合法素材，只创建新目录。支持 macOS、本机 Chrome/FFmpeg、PingFang SC 和 SF Mono；系统字体作为外部环境。不同文案、其它平台和其它字体仍需实际审片。

`showcase-layout.json` 保存布局、运行代码摘要和原声音摘要，`recipe_versions.json` 保存使用的九场来源与输出帧。更新模板不改变已生成工程。源代码与接口血缘见 [SOURCE_AUDIT.md](SOURCE_AUDIT.md)。

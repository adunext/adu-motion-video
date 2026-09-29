# 完整多场景动效包：作品展示与口播

本包保留原 HTML/CSS/JavaScript 工程的 **9 个完整 Scene 和 175 个音效事件**。它包含开场标题与剪辑时间线、人物从大卡缩成圆形窗并交给满屏作品墙、九宫格与分组高亮、九宫格中心作品放大、审片报告、四品类展示与镜头语言、软件窗口录屏、动态赛道、账号卡、日常工作录屏、行动号召和逐字打出的片尾。`scenes.js` 以已公开 `examples/showcase-scenes.js` 为底稿，保留原编舞，增加文字/媒体参数和倒序取帧修复。原始动效引擎结构与音效配方保存在同目录供对照；具体差异及验证边界见 [SOURCE_AUDIT.md](SOURCE_AUDIT.md)。

这是**整片级宏场景素材**，不是把每个镜头压缩为一张可填字的卡片。`manifest.json` 描述场景、66 个语义动作节点、42 个原速保护窗、文字/数值/媒体槽和原始时码；`audio_timeline.json` 保留 21 段音乐编排、66 个音量包络键、175 个音效点，以及降调、上扬、鼓点和片尾渐弱位置。

## 用新文案适配

1. 导入新口播，先取得逐句或逐词时间。按意义挑选本包场景；新文案可以少于 9 场、重排或复用某场。不要把“审片报告”“软件录屏”等硬套在没有相应事实的台词上。
2. 将每个目标片段与 manifest 中对应的 `role` 和 `cues` 配对。26 个 `required:true` 节点需要绑定到本期口播里的准确词或句。适配器据此生成整帧的目标起止和分段时间映射；动作保护窗按原速运行，其余细节按原顺序重排。S2 九路视频和 S3 放大的作品视频全场锁定 1×，因为它们始终在播放；台词过长或过短时拆分、增加场景或另写镜头，不要拉伸这两个场景。
3. 填每场使用到的全部 `slots`。`sourceSpans` 在 Scene 源码里精确定位画面字，构建器先校验 `sourceBlockSha256`，再替换；`sourceCode` + `valueTemplate` 定位必须由真实数据替换的动态计数，保留计数动画。带 `mustChange` 的“示例/请填写”占位词不能沿用。使用者应核实数字；仅作演示时在画面上标“示意”。英文字幕和中英逐字字幕来自新 `subs.js`，不是原片字幕。
4. 提供媒体素材。人物口播帧始终以**目标输出时钟**取帧，场景动作以映射后的**原编舞时钟**求值；两条时钟不得混为一条。构建阶段从新口播生成 `talkmap.js`，从本期作品生成 `wall.js`；字幕须使用本期时间轴。macOS 上的构建器默认通过系统 Vision 生成人脸跟踪；也可明确提供经过检查的固定裁切。若绕过构建器直接运行源码且没有 `face.js`，共用引擎会用固定中心，必须检查圆形人物窗内的脸是否居中。场景原图序列路径保持不变，故连贯的移动、放大和场景交接不会丢。
5. 以相同映射逐个重排 175 个音效事件与音乐包络。新视频的配乐应按实际时长重建；直接拉伸原 108.4 秒 WAV 会使节拍和变调变形。

如果目标片段明显比原场短，优先省去不相关的宏场景或选择更短的段落；`minFrames` 保护关键动作免于挤成闪屏。如果更长，增加词间持留或相邻场景；`maxHoldFrames` 限制无内容的长时间定格。每次生成后仍要查看首帧、所有转场、人物口型、最长文字、数值、完整音轨和片尾。

## 媒体准备

公开仓库**不包含**原作者头像、软件录屏、作品墙、音乐、原口播或第三方作品。必须提供自己有权使用的视频、图像、作品墙来源和作品墙来源图标。`assetDefinitions` 给出每个媒体槽原工程的帧数、路径和画幅；`prepare_media.py` 生成相同的帧序列命名，已有合法素材序列目录也可直接复制。九宫格是 9 路独立视频，不会自动用同一段重复伪装成 9 个结果。作品墙原版有 389 张 4×4 视频精灵；新素材至少需要 27 个独立作品，画面会将它们循环铺到 389 格，计数仍显示独立作品数。

输入文件格式：

```json
{
  "sources": {
    "grid_opus55p": "/absolute/path/to/展示A.mp4",
    "grid_gpt6pro": "/absolute/path/to/展示B.mp4",
    "opus_hero": "/absolute/path/to/重点成片.mp4",
    "presenter": "/absolute/path/to/授权头像.png",
    "app_logo": "/absolute/path/to/软件标识.png",
    "wall_badge_icon": "/absolute/path/to/作品来源图标.png",
    "wall": {
      "manifest": "/absolute/path/to/作品清单.json",
      "videos": "/absolute/path/to/作品视频目录"
    }
  }
}
```

以上只示范字段；所选场景的其他 `sources` 也必须填。作品清单采用 `scripts/prep_wall.py` 的 `[{"slug":"unique-name","author":"署名","category":"分类"}, ...]`，视频目录包含对应的 `unique-name.mp4`。也可让 `wall` 指向已有的 `{"sprites":"/absolute/path/to/4x4精灵目录"}`。准备命令：

```bash
python3 packs/anim4/prepare_media.py \
  --inputs /absolute/path/to/media-inputs.json \
  --output /absolute/path/to/new-media-output \
  --scenes s01,s02 --dry-run
python3 packs/anim4/prepare_media.py \
  --inputs /absolute/path/to/media-inputs.json \
  --output /absolute/path/to/new-media-output \
  --scenes s01,s02
```

`--output` 必须是不存在的新目录；缺媒体、序列不完整或原视频过短会直接报错。单张图片可以做静止的序列输入，但若目标是原片的视频运动感，应提供真实运动素材。输出 `sc/`、`assets/`、`wall.js`、`media-prep.json` 交给完整场景构建器使用；其中 `wall-meta.json` 记录真实独立作品数。未选场景不会要求其媒体，但场景构建阶段要只实例化选中的 Scene，避免浏览器加载未选场景的静态图片。

## 文件说明

- `index.html`、`lib.js`、`scenes.js`、`main.js`、`style.css`：原 DOM 动效引擎及全场景源码。`index.html` 是源工程快照，直接打开时仍要求新 `talkmap.js`、`wall.js`、`face.js`、`subs.js` 和所有媒体；适配器生成可渲染的入口。
- `manifest.json`、`text-inventory.json`：可机器读取的内容/动作/媒体接口。文本清单由浏览器对 9 个 Scene 实际 DOM 提取；运行时变动的文案和计数另列在 manifest。
- `audio.py`、`sfx.json`、`audio_timeline.json`：原音效合成器、原事件清单、便于改时长的音乐结构。`audio.py` 原样运行仍是固定原时长，仅作为配方；导出新片需按目标时间重新编译。
- `prepare_media.py`：从用户本地素材产生符合原工程命名和帧数的媒体目录。

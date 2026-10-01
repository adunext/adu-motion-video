![Adu-motion-video 动画模板库](assets/cover.jpg)

# Adu-motion-video

**阿杜开源的高质量动画动效模板 Skill。选好模板和风格，把口播与素材交给 AI，就能开始剪辑。**

## 一、Adu-motion-video 是什么？

Adu-motion-video（简称 **adumotion**）是阿杜开源的一个**模板级 Skill**。它不是一段提示词，也不只是参考视频，而是经过**阿杜与 Opus 5.5 细致筛选、精心制作的完整动画动效模板**。

场景、动作、转场和音效已经做好。Codex、Claude Code 可以在这些模板上，按你的口播、文案和素材制作新视频，交付 **MP4 和可继续修改的工程**。

### 先看模板，再选风格

**一级选模板，二级选风格。** 同一个模板的不同风格放在一起；使用时直接告诉 AI 完整编号，例如 **01-B**。

**模板 01 · 现代图文口播**

适合真人讲解、知识拆解、工具演示。同一套讲解内容，可以选择不同的画面表现。

| 编号 · 二级风格 | 动画预览 · 点击下载有声 demo | 需要准备的素材 |
| --- | --- | --- |
| **01-A · 原片节奏**<br>已发布 · 错峰入场、人物回应、三项拆解 | [![01-A 原片节奏动画预览](assets/demos/01-A.gif)](assets/demos/01-A.mp4?raw=true) | 口播、文案；证据镜头另备三段录屏或视频 |
| **01-B · 连续形变**<br>已发布 · 同一物件变形、拆开、收拢 | [![01-B 连续形变动画预览](assets/demos/01-B.gif)](assets/demos/01-B.mp4?raw=true) | 口播、文案；演示镜头另备一段录屏或视频 |
| **01-C · 纵深舞台**<br>已发布 · 前后层次、主体聚焦 | [![01-C 纵深舞台风格预览](assets/demos/01-C.gif)](assets/demos/01-C.mp4?raw=true) | 口播、文案；演示或证据画面需要自己的录屏、视频 |
| **01-D · 杂志分屏**<br>已发布 · 人物与资料并排、编辑版式 | [![01-D 杂志分屏风格预览](assets/demos/01-D.gif)](assets/demos/01-D.mp4?raw=true) | 口播、文案；资料窗口需要自己的录屏、视频 |
| **01-E · 节拍字效**<br>已发布 · 关键词重音、字块接力 | [![01-E 节拍字效风格预览](assets/demos/01-E.gif)](assets/demos/01-E.mp4?raw=true) | 口播、文案；演示或证据画面需要自己的录屏、视频 |

**模板 02 · 纸面透视讲解**

适合解释两难选择、抽象观点和行动步骤。

| 编号 · 二级风格 | 动画预览 · 点击下载有声 demo | 需要准备的素材 |
| --- | --- | --- |
| **02-A · 纸面天平**<br>已发布 · 天平回稳、手写批注、三步确认 | [![02-A 纸面天平动画预览](assets/demos/02-A.gif)](assets/demos/02-A.mp4?raw=true) | 口播、文案，以及一张用于说明观点的透明插图 |

动图为压缩后的 8 秒静音预览，点击可下载有声 demo。01-A、01-B、02-A 展示的是已发布模板制作的新内容；01-C、01-D、01-E 展示原工程的风格短段，其三个组已完成各自新内容整片与独立使用验收，并随 3.2.0 发布；预览不代表来源的所有演出已进入稳定库。更多模板与风格持续更新。

## 二、主要用在哪些场景？

| 场景 | 可以怎么用 |
| --- | --- |
| **口播视频** | 为真人讲解加重点、图解、动画和字幕 |
| **知识讲解 / 科普** | 把抽象概念、关系和步骤讲清楚 |
| **AI 工具 / 软件教程** | 用录屏配合动画，突出操作与实际效果 |
| **产品介绍 / 功能演示** | 展示卖点、使用流程和前后变化 |
| **观点解读 / 方法分享** | 用对比、拆解、归纳和行动步骤组织内容 |

## 三、怎么使用？

1. **添加 Skill。** 在 Codex 或 Claude Code 中安装本仓库，也可以让 AI 帮你添加。
2. **准备素材。** 录好并剪好口播，准备对应文案，以及所选风格需要的录屏、图片等；有字幕文件也一起提供。
3. **报编号，让 AI 剪辑。** 说清喜欢的模板风格、素材位置和输出目录即可。

安装时，可以把这句话发给 AI：

```text
请添加 adu-motion-video Skill：
https://github.com/adunext/adu-motion-video
安装后确认能找到这个 Skill，并检查制作视频需要的环境。
```

制作时，可以这样说：

```text
使用 adu-motion-video，选模板 01 的 B 风格（01-B · 连续形变），
帮我剪辑这条口播。

口播、文案、字幕和录屏都在：/我的素材目录
请按我的内容安排动画，输出 MP4 和可编辑工程到：/我的输出目录
```

需要小图标或动画素材时，也可以加一句：**“从阿杜导演的动画素材 API 中挑选合适的素材。”** 真人、产品画面和实际操作录屏仍由你提供。

目前支持 **Codex、Claude Code**；**豆包、WorkBuddy** 的支持在后续计划中。

## 四、有什么优点？

- **模板级开源，Token 消耗低。** 完整动画已经做好，AI 主要处理文案、素材和时间安排，减少从零编写动画与反复试错的消耗。
- **输出更稳定。** 复用精心制作并检查过的动作与转场，让同一系列视频更容易保持一致的质量。
- **阿杜逐个精选，持续更新。** 阿杜每天逐个筛选新的高质量动画，和 Opus 5.5 一起精心制作更多模板与风格。
- **自带动画素材来源。** 接入阿杜导演的公开素材 API，可按需获取阿杜精选整理的 **11,028 个 Lottie 动画**，用于图标、点缀和辅助讲解，无需 API Key。[查看动画目录](https://adudir.com/api/lottie-catalog/manifest)。
- **成片与工程都交给你。** 导出 MP4 后仍能修改文字、素材和动画，继续做下一版。

**未来，素材 API 也计划支持按需生成图片、动画等所需素材。** 当前开放的是现有动画的查询与下载。

---

## 技术说明

以下内容供需要安装命令、接口调用、模板版本和开发细节的用户查阅。

**3.2.0** 的稳定范围为 A「原片节奏」三个组、B「连续形变」两个组、C「舞台镜头」/D「杂志分屏」/E「节拍字效」各三个组，以及试点外来源的纸面透视续接组，限 macOS、横屏 1080p60。五条路线的源演出与对应新内容已经作者确认；B/C/D/E 的完整新片由未参与提炼的执行者从冻结公开包和本期输入独立制作。每条路线保留自己的运动、人物与声音，通过命名语义字段绑定新内容。逐组范围与限制见[能力与验收矩阵](docs/capability-matrix.md)。B 的计划干扰组与旧候选原字节保留；旧 `anim3/anim4` 的 21 个宏场景仍为 experimental，9 个基础 `TPL` 为 quick-start。

### 模板编号与实际版本

编号表示“一级模板－二级风格”，不随话题或案例名称变化。AI 遇到编号时，先查[模板与风格目录](references/template-catalog.md)，再读取相应包；已发布模板的具体镜头范围见[能力与验收矩阵](docs/capability-matrix.md)。

| 编号 | 实际包版本 | 状态 |
| --- | --- | --- |
| 01-A | `classic-performance@1.0.0` | 已发布 |
| 01-B | `continuous-performance@1.0.0` | 已发布 |
| 01-C | `stage-performance@1.0.0` | 已发布；三个完整组 |
| 01-D | `editorial-performance@1.0.0` | 已发布；三个完整组 |
| 01-E | `kinetic-performance@1.0.0` | 已发布；三个完整组 |
| 02-A | `paper-balance@1.0.0` | 已发布；一个段落镜头组 |

3.2.0 已发布六个风格中的十五个完整镜头组。完整实测范围为 macOS、横屏 1920×1080、60fps。竖屏需重新布局，其它系统与字体组合需另行验证。新稿要留足动作与读字时间；实际 Token 消耗随素材处理、片长和修改量变化，尚无统一量化基准。

### 公开动画素材 API

- 动画目录：`GET https://adudir.com/api/lottie-catalog/manifest`
- 动画说明：`GET https://adudir.com/api/lottie-catalog/annotations`
- 下载单个动画：`GET https://adudir.com/api/lottie-catalog/file/{preset}.json`

**无需登录或 API Key。** 截至 2026-10-01，线上目录返回 `total: 11028`；目录、注解和单文件下载均已实测。先查目录与注解，再按返回的 `preset` 下载需要的 JSON，保存到本期工程的素材目录。获取方法和使用边界见[动画素材 API](references/lottie-assets.md)。

**请求额度：每个 IP 每天 20 次，全接口每天合计 2,000 次，北京时间零点重置。** 查询目录、注解和下载素材共用额度，请缓存后按需使用。超额返回 `429`；每日额度用完时按 `Retry-After` 等待，避免反复重试。

```bash
# 查询目录；避免每条视频都重新拉全库
curl -fsS https://adudir.com/api/lottie-catalog/manifest -o lottie-manifest.json

# 示例：下载一个已核实存在的加载动画
curl -fsS https://adudir.com/api/lottie-catalog/file/insider_loading.json -o insider_loading.json
```

素材 API 提供可用动画文件；各模板仍按自己的素材与渲染要求接入。生成素材接口尚未开放。第三方动画沿用各自原始许可，仓库 MIT 许可不替代素材许可。

<details>
<summary><strong>展开安装、制作命令与验收说明</strong></summary>

### 先准备什么

- 一条已经剪好、长度确定的口播视频，以及对应文案；带时间码的字幕（SRT）有助于绑定动作，关键字最好有逐词时间。
- 本期要展示的录屏、图片、头像、标识、作品视频和可用配乐。公开 demo 仅供观看，不提供可复用的原始真人或第三方素材。选用需要这些素材的场景时，必须提供本期有权使用的素材。
- 期望的画幅、账号名、字幕语言和交付目录。当前完整场景包按 **1920×1080、60fps** 制作；竖屏需要另做布局，不能直接裁切。
- 本机 Node.js 18+、FFmpeg/ffprobe、Chrome，以及可运行本地命令的 Agent。当前稳定组合在 macOS / CPython 3.14.7 / 1080p60 验证，Python 包固定在 requirements-runtime.txt；其它平台、字体与 Python 组合需单独验证。

最终可得到一个可再编辑的项目目录、带音乐与音效的 MP4，以及帧数、解码和响度检查结果。画面质量仍须观看完整成片并与原工程关键动作对照；命令通过不等于视觉验收通过。

### 选择制作路线

| 路线 | 内容与用途 | 当前边界 |
| --- | --- | --- |
| [A 原片节奏](packs/classic-performance/1.0.0/README.md) | 主张与人物、真实证据聚焦、三项分解归纳 | Stable；三个组，已验收的 macOS 1080p60 |
| [B 连续形变](packs/continuous-performance/1.0.0/README.md) | 同一容器改变角色、拆解与闭合 | Stable；两个组，计划干扰组仍为 candidate |
| [C 舞台镜头](packs/stage-performance/1.0.0/README.md) | 前中后层、人物让位、实际证据与概念归纳 | Stable；三个组，完整新片与独立使用已确认 |
| [D 杂志分屏](packs/editorial-performance/1.0.0/README.md) | 版心、人物与证据分栏、跨栏交接 | Stable；三个组，本期新片按用户要求无背景配乐 |
| [E 节拍字效](packs/kinetic-performance/1.0.0/README.md) | 整词推动实体、撞击回稳、四项收拢 | Stable；三个组，完整新片与独立使用已确认 |
| [纸面透视组](packs/paper-balance/1.0.0/README.md) | 疑问、天平、用途、批注与三步确认 | Stable；一个续接组，保留约 0.37 秒的源入场 |
| [完整场景包 `anim3`](packs/anim3/README.md) | 12 个连续编辑卡片场景，保留人物、道具、数字、镜头、转场与原场景音效编舞 | 实验性；新文案与素材需逐场绑定和验收 |
| [完整场景包 `anim4`](packs/anim4/README.md) | 9 个作品展示与口播场景，保留作品墙、九宫格、软件窗口、赛道等完整编舞 | 实验性；作品墙、录屏等需要本期素材 |
| [基础 `TPL`](references/templates.md) | 9 个短场景函数，用于快速原型或从零组合较轻的片段 | Quick-start；不代表上述原工程的全部动画 |
| [手绘卡通叙事](references/handdrawn-animation.md) | 角色与道具表演、同镜头续接的方法 | 目前是制作方法和既有示例，尚未提取为完整场景包 |

`anim3`、`anim4` 是工程包 ID，不是用户视频标题或两种固定品牌风格。完整场景包可挑选、重排、重复场景，但必须尊重动作顺序、素材含义和片长。短到容不下原动作的片段会拒绝构建；多出的时间优先给可停留的画面，不会把所有动画整段慢放。作品墙需要先把至少 27 个真实独立作品制备为 389 张展示精灵，并如实保留独立作品数；不能直接拿 27 张精灵输入构建器。指定模板后，素材目录中的其他现成工程不会自动成为动画底稿。跨包逐场组合目前需要额外编排，见[来源与多包编排](references/full-project-templating.md#来源与多包编排)。详见[完整工程复用与验收](references/full-project-templating.md)。

![视觉家族与场景选择示意](assets/tutorials/02-style-map.png)

### 用 Codex 或 Claude Code 开始

```bash
# 任选与你的 Agent 对应的位置；也可以克隆到其他路径并让 Agent 读取 SKILL.md
git clone https://github.com/adunext/adu-motion-video.git ~/.claude/skills/adu-motion-video
# Codex 可用：git clone https://github.com/adunext/adu-motion-video.git ~/.codex/skills/adu-motion-video

PL="$HOME/.claude/skills/adu-motion-video/scripts/pipeline.sh"
# 若装在 Codex 目录：PL="$HOME/.codex/skills/adu-motion-video/scripts/pipeline.sh"
bash "$PL" doctor
bash "$PL" setup
```

让 Agent 先阅读 [SKILL.md](SKILL.md)、[制作约定](references/rules.md) 和所选包说明。先发现包，选显式版本；以下以稳定的 A 包为例：

```bash
bash "$PL" packs
bash "$PL" macro-spec classic-performance@1.0.0 /已有目录/本期配置.json
# 编辑配置：挑场景、填账号及每场文案/数字/素材路径、绑定关键台词时间
bash "$PL" macro-build classic-performance@1.0.0 /已有目录/本期配置.json /已有目录/剪好口播.mp4 /已有目录/新工程
bash "$PL" stills /已有目录/新工程 0,4,12
bash "$PL" audio /已有目录/新工程
bash "$PL" mix /已有目录/新工程
bash "$PL" render /已有目录/新工程 /已有目录/新片_v1_16x9_60fps.mp4
bash "$PL" check /已有目录/新片_v1_16x9_60fps.mp4
```

以上路径只是格式示例，`macro-spec` 输出和新工程路径必须事先不存在。可传 `--subs-js /路径/新口播字幕.js` 给 `macro-build`；字幕必须与新口播对齐。`macro-spec` 列出所选包的全部组，使用前删去不需要的组，按新口播顺序排列，并补齐必填输入。配置还可指定本期音乐 `music:{mode:"track",path,offset}`，以及本期混音增益 `mix:{musicVolume:0.42}`；完成后会把实际选择、处理图和声音摘要保存为 `mix_recipe.json`，详见[声音与重现](references/audio.md)。`anim4` 和 `anim3/s06` 默认在 macOS 使用 Vision 跟踪新口播人脸，其他系统要显式提供审核过的固定裁切。构建器要求目标场景总帧数与剪好口播相符，按输出帧网格量化后必须完全一致。长短差异和动作锚点的处理见[完整工程复用与验收](references/full-project-templating.md)。

可以直接对 Agent 说：

> 使用 adu-motion-video 的完整场景包制作这条新口播。口播、SRT、文案和本期录屏在 `/实际路径/素材目录`。先运行 packs，按语义选择显式版本的完整镜头组或场景，列出所需替代素材和关键台词时间，补齐配置后生成工程；检查首帧、转场、文字裁切、口型、音乐和音效，再导出新 MP4。不要把原工程的示例文字、数字或第三方素材带进新片。

Agent 缺少 Skill 机制时，先读 [AGENTS.md](AGENTS.md)。基础模板只需运行 `bash "$PL" demo /不存在的新目录` 查看 36 秒示例；参数见[模板目录](references/templates.md)。

### 验收与扩展

至少检查第一帧有人物时人物是否可见、所有关键动作前后帧、最长文案的字体与安全区、录屏和图片裁切、场景交接、全段口型、字幕、音乐层次、音效位置及片尾。再与原工程的对应动作连续播放对照。任何一项未完成，只能标记为 experimental 或局部通过，不能宣称完整复刻验收通过。[教程：检查连续动作](assets/tutorials/03-continuity.png) · [验证记录](docs/validation.md)。

已完成的新 Opus 工程可按[持续模板接入](references/template-intake.md)登记与冻结。按新增价值区分案例、预设、变体、镜头组、路线与引擎；接收、候选和稳定发布各有证据状态。包 ID/版本和运行代码固定在新工程，后续升级不会自动改变旧片。候选提炼保留完整因果、人物、进退与声音，经过新内容及独立使用再扩大稳定库。仓库结构与贡献要求见[完整工程复用与验收](references/full-project-templating.md)。

MIT License · 第三方说明见 [THIRD_PARTY.md](THIRD_PARTY.md)。

</details>

[AI 执行入口](SKILL.md) · [模板与风格目录](references/template-catalog.md) · [动画素材 API](references/lottie-assets.md) · [更新与下载](https://github.com/adunext/adu-motion-video/releases) · [MIT License](LICENSE) · [第三方说明](THIRD_PARTY.md)

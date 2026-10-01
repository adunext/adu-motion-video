---
name: adu-motion-video
description: 使用完整动画工程包，把新口播、文案与自有素材制作成可编辑动效视频和 60fps MP4；也支持轻量 TPL、手绘续接、字幕与改旧片。需要可读写本地文件并运行命令的 Agent。
metadata:
  version: "3.3.0-rc.1"
---

# adu-motion-video

用户提供剪好的口播视频、文案，最好还有新口播的时间码字幕；选用含录屏、作品墙、头像、标识或配乐的场景时，还须提供本期有权使用的素材。你负责把**完整场景编舞**适配到新台词与片长，生成可编辑工程，核查后导出新 MP4。先读 [制作约定](references/rules.md)。`SKILL_DIR` 是本文件目录，`PL="$SKILL_DIR/scripts/pipeline.sh"`。

## 选择入口

用户指定模板编号（如 `01-B`）或要求选风格时，先读[模板与风格目录](references/template-catalog.md)，按“一级模板 → 二级风格”映射到显式包版本。未发布风格不能按已发布包承诺制作。需要辅助动画素材时，按[公开动画素材 API](references/lottie-assets.md)检索并下载到本期工程，再核对所选包的媒体与渲染要求。

用户新增完成工程、提炼新镜头组或更新模板库时，读[持续模板接入](references/template-intake.md)。先登记来源和实际状态，再按价值提炼；收到工程不代表已经有可发布模板。`bash "$PL" packs` 只列包的语义与版本元数据，按任务加载相关清单；同一 ID 有多个版本时显式选择 `id@version`。

1. 默认运行 `bash "$PL" packs`，按表达目的选择显式版本，读取相关包的 `README.md` 与 `manifest.json`，并查看[完整工程复用说明](references/full-project-templating.md)。`classic-performance@1.0.0` 保留错峰、人物回应与回稳，共三个已验证组；`continuous-performance@1.0.0` 保留同物件变形、拆解与闭合，共两个已验证组。`paper-balance@1.0.0` 是一个纸面透视续接组。稳定范围限于已验收的 macOS 1080p60，不代表整份来源或任意文案已模板化；逐组边界见[能力矩阵](docs/capability-matrix.md)。旧候选版本保留，B 的计划干扰组仍在候选中。旧 `anim3/anim4` 分别有 12/9 个完整场景，仍为 experimental。包 ID 与原片标题、品牌无关。
   C/D/E 的 `stage-performance@1.0.0`、`editorial-performance@1.0.0` 与 `kinetic-performance@1.0.0` 各有三个稳定组，分别保留前后层与人物让位、分栏与跨栏交接、整词与实体回应。每条路线都由未参与提炼的执行者从冻结公开包和本期输入独立制作一部 99.5 秒新片，作者确认成立。旧候选原字节保留；本期桥接不计作公开稳定组。
2. 只需轻量短片、探索版式时，使用 9 个基础 [`TPL`](references/templates.md)；它们是 quick-start，不包含完整工程包里的全部动作。
3. 手绘角色、补录同镜头续接，读[手绘动画方法](references/handdrawn-animation.md)。目前没有对应完整工程包，不要把方法文档称为已自动模板化。

本地 3.3.0-rc.1 新增 `paper-ball-performance@0.1.3-candidate` 两个纸面小球候选组：六类资料聚合成网络，以及七步日历、六类能力、三项开箱和交付卡堆叠。需要本期真人口播/文案，并显式提供源标题字体；尚未获连续声画认可，不占用已发布风格编号。见[候选说明](adapters/paper-ball/README.md)。已发布 3.2.0 的十五个稳定组保持原字节。

## 完整工程包流程

1. `bash "$PL" doctor` 检查 Node、Python、FFmpeg 和 Chrome；缺依赖且允许安装时再 `bash "$PL" setup`。保持源工程和原成片只读，输出到不存在的新路径。
2. 先锁定用户指定的模板来源。素材目录里的其他 `anim`、新工程或旧成片不自动成为动画底稿；不能只插入少数模板片段就称整片使用了指定模板。逐场记录来源包与场景 ID，混用完整包见[来源与多包编排](references/full-project-templating.md#来源与多包编排)。对齐新口播和文案，取得关键台词的准确时间。SRT 只有整句时间时，不可臆测句内某个词的时间；用逐词对齐数据或人工标注。读包的 `role`、`cues`、`motionWindows`、`slots`，按意义挑选、重排或重复完整场景。先列出分镜和缺少的素材。
3. `bash "$PL" macro-spec 包ID@版本 /路径/本期配置.json` 生成配置草稿。删去不选的场景，调整顺序和每场 `durationFrames`；有 `inputs` 的组填写命名语义字段，必填事件 `cues` 另绑定真实台词落点。`brand` 填本期账号。本期音乐可用 `music:{mode:"track",path,offset}` 指定；未指定时按原编曲结构重合成。人物窗默认在 macOS 使用 Vision 跟踪新口播人脸；不能自动跟踪时须显式配置审核过的 `faceTracking:{mode:"fixed",cx,cy,h}`。任何来源演示数据与示例文字都须替换或明确标“示意”。素材的空路径代表缺项；媒体准备与容量限制看包目录中的 `README.md`。
4. `bash "$PL" macro-build 包ID@版本 /路径/本期配置.json /路径/剪好口播.mp4 /路径/新工程 [--subs-js /路径/字幕.js]`。新口播长度应与计划总帧数相符。适配器把关键动作窗口锁在原速，较长段落只伸展可停留区；如果时间不够，会报错，改分镜或片段长度，不靠全片线性拉伸。缺文字、数字、媒体或关键 cue 也会报错。
5. `bash "$PL" stills /路径/新工程 0,4,12,...` 抽查首帧、每个 cue 前中后、最长文字、场景接缝和片尾；再播放所有复杂运动区间，与原工程对照。检查字体、媒体比例/裁切、真实口型、字幕、SFX 与音乐。修订配置或工程并重新验证。
6. `bash "$PL" audio /路径/新工程` → `bash "$PL" mix /路径/新工程` → `bash "$PL" render /路径/新工程 /路径/新片_v1.mp4` → `bash "$PL" check /路径/新片_v1.mp4`。完整观看并听取最终编码文件；`check` 的帧数、解码和响度不能替代视觉与内容验收。

快速体验基础模板可用 `bash "$PL" demo /不存在的新目录`。为真实口播从零组合 `TPL` 时，按[模板目录](references/templates.md)和[字幕方案](references/subtitle-options.md)制作，仍须完整验收。

## 不可省略的检查

- 口播取帧以**目标输出时钟**为准；源场景动画以映射后的**原编舞时钟**运行。不能让原场景时钟控制真人口型，也不能用冻结的真人帧补足缺失时长。
- 第一帧若是口播开场，应看见真人与主题；检查字幕白字描边、字号和安全区，不能把模板源视频的品牌、日期、数值或占位字留在新片。
- 检查每个动作保护窗口的连续片段，而不只抽一张图；录屏、九宫格、作品墙按本期真实素材检查。音乐和音效随新时间线重编，不直接变速旧成品音轨。
- 新文案不能保证自动无损适配。短段容不下动作就拒绝、拆分或换场景；长段只在允许停留的位置延长。新场景仍需针对本期内容设计，不按句子硬套宏场景。
- 输出新工程和新版本成片，不覆盖用户原工程；报告实际检查范围。`anim3` 与 `anim4` 在完整新文案逐帧对照和成片声画验收前保持 **experimental**，不要称已完整验证。

更多细节：[完整工程复用](references/full-project-templating.md) · [制作约定](references/rules.md) · [字幕](references/subtitle-options.md) · [配乐](references/audio.md) · [手绘](references/handdrawn-animation.md) · [排错](references/troubleshooting.md)。

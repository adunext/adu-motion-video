---
name: adu-motion-video
description: 使用完整动画工程包，把新口播、文案与自有素材制作成可编辑动效视频和 60fps MP4；也支持轻量 TPL、手绘续接、字幕与改旧片。支持 Windows、macOS、Linux，以及 Codex、Claude Code、豆包、DeepSeek、WorkBuddy 等可读写文件并运行命令的助手。
metadata:
  version: "3.10.0"
---

# adu-motion-video

用户提供剪好的口播视频、文案，最好还有新口播的时间码字幕；选用含录屏、作品墙、头像、标识或配乐的场景时，还须提供本期有权使用的素材。你负责把**完整场景编舞**适配到新台词与片长，生成可编辑工程，核查后导出新 MP4。先读 [制作约定](references/rules.md)。`SKILL_DIR` 是本文件目录，`PL="$SKILL_DIR/scripts/pipeline.sh"`。 制作记录保存实际 Skill 路径、版本和所用入口；同名旧安装、仓库版本与已生成工程的冻结运行代码可能不同，不能用最新版说明追认旧工程。

## 平台与助手

同一份 Skill 面向 Windows、macOS、Linux，可由 Codex、Claude Code、豆包、DeepSeek、WorkBuddy 等助手使用。先确认助手执行环境能读写素材并运行命令；有 Skill 机制就加载本文件，否则先读取本文件和 [AGENTS.md](AGENTS.md)。不凭助手名称推定当前客户端具备本地执行能力。

命令入口使用 Bash：Windows 当前通过 WSL 运行，并在 WSL 内安装依赖、使用该环境的素材路径；macOS/Linux 直接使用 Bash。按 [兼容说明](references/compatibility.md#平台与助手接入)检查路径、字体、浏览器及可选人脸跟踪。已有 macOS 验收记录描述的是实测环境，不能据此拒绝其他平台的制作请求。

## 选择入口

用户指定模板编号（如 `01-B`）或要求选风格时，先读[模板与风格目录](references/template-catalog.md)，按“一级模板 → 二级风格”映射到显式包版本。未发布风格不能按已发布包承诺制作。需要辅助动画素材时，按[公开动画素材 API](references/lottie-assets.md)检索并下载到本期工程，再核对所选包的媒体与渲染要求。

用户要求竖屏时，按目录的 **portraitSelection** 选择对应候选版本，并读取[竖屏契约](references/portrait.md)。目前十种风格、32 个完整组均支持 `brief.layout="portrait"` → macro-plan → macro-build → render，画幅自动为 1080×1920；旧 1.0.0 稳定包不获得追认。原动作、素材、字幕与音效时钟保持；标题、人物与内容层重排，控制台连接线按原激活落点重绘。候选必须做本期真实素材连续声画检查，几何测试不能当作新路线已验收。

用户新增完成工程、提炼新镜头组或更新模板库时，读[持续模板接入](references/template-intake.md)。先登记来源和实际状态，再按价值提炼；收到工程不代表已经有可发布模板。`bash "$PL" packs` 只列包的语义与版本元数据，按任务加载相关清单；同一 ID 有多个版本时显式选择 `id@version`。

用户指定 **03 · 深色 3D / 03-A · 多屏展陈** 时，读[深色 3D 模板](references/dark-3d-template.md)，横屏基线选择 `anim4-showcase-macro@1.1.1-candidate`；新竖屏按目录选 `anim4-showcase-macro@1.2.0-candidate` 并声明 layout。它保留九场作品墙、多屏比较、重点放大与软件窗口编舞，新增 1080×1920 原生竖屏布局。1.1.1 补齐 HDR 抽帧和 SDR 导出色彩核验；此前冷安装记录属于 1.1.0，当前仍待作者连续声画确认；按本期材料选择完整场景，不计入十七个稳定组。旧 1.0.0 保持原字节。

1. 默认运行 `bash "$PL" packs`，按表达目的选择显式版本，读取相关包的 `README.md` 与 `manifest.json`，并查看[完整工程复用说明](references/full-project-templating.md)。`classic-performance@1.0.0` 保留错峰、人物回应与回稳，共三个已验证组；`continuous-performance@1.0.0` 保留同物件变形、拆解与闭合，共两个已验证组。`paper-balance@1.0.0` 是一个纸面透视续接组。既有稳定验收记录使用 macOS 1080p60，不代表整份来源或任意文案已模板化；逐组边界见[能力矩阵](docs/capability-matrix.md)。旧候选版本保留，B 的计划干扰组仍在候选中。旧 `anim3/anim4` 分别有 12/9 个完整场景，仍为 experimental。包 ID 与原片标题、品牌无关。
   C/D/E 的 `stage-performance@1.0.0`、`editorial-performance@1.0.0` 与 `kinetic-performance@1.0.0` 各有三个稳定组，分别保留前后层与人物让位、分栏与跨栏交接、整词与实体回应。每条路线都由未参与提炼的执行者从冻结公开包和本期输入独立制作一部 99.5 秒新片，作者确认成立。旧候选原字节保留；本期桥接不计作公开稳定组。
2. 只需轻量短片、探索版式时，使用 9 个基础 [`TPL`](references/templates.md)；它们是 quick-start，不包含完整工程包里的全部动作。
3. 手绘角色、补录同镜头续接，读[手绘动画方法](references/handdrawn-animation.md)。目前没有对应完整工程包，不要把方法文档称为已自动模板化。

3.3.0 新增 **02-B · 纸面聚合** `paper-ball-performance@1.0.0`：六类资料聚合成网络，以及七步日历、六类能力、三项开箱和交付卡堆叠两个稳定组。源/重放对照与 18.2667 秒不同内容样片已获作者声画确认。需要本期真人口播/文案，并显式提供固定 SHA 的标题字体；详见[包说明](packs/paper-ball-performance/1.0.0/README.md)。这是组级增量，不是新整片路线；严格栅格问题保留在 review.json。3.2.0 的十五个稳定组与旧候选均保持原字节，当前七个风格共十七个稳定组。

3.8.0 新增 **05-A · 鲜色角色叙事** `vivid-sticker-performance@0.1.1-candidate`，读取[专门说明](references/vivid-sticker-template.md)。三组分别为关键词递进到结论、两准备者向三接收者交接成果、三反馈汇入后升级。首版已提供横竖屏、命名槽、固定数量和完整动作窗；源码局部、静音文案与真实构建检查不等于新口播连续声画或独立复用已验收。

## 完整工程包流程

3.6.0 新增当前分镜局部重配和素材版本检查，并为通用视频抽帧接入共享色彩处理。**04-A · 仪器台演示** 当前候选 `doubao-console-performance@0.1.2-candidate` 增加有界文字布局，原 0.1.1 三组的同内容技术重放仍保留；静音新文案检查不代替新口播完整声画或独立复用验收，详见[模板说明](references/doubao-console-template.md)。新预览统一使用带导出证据与版本检查的 `preview` 命令。

用户未锁定单一风格，或要求自动比较全部模板时，先读[全库自动选型](references/automatic-selection.md)，运行 `auto-capabilities`。助手根据整篇台词整理语义阶段、短标题、真实媒体和准确落点，形成 `adu-auto-brief/1`，再执行 `auto-plan → auto-build`。当前 10 种风格、32 组参与横竖屏比较，优先完整可用的统一风格；必要时仅在有独立入场合同的组间组合。长段提供有实际内容依据的完整分段路线，不循环补时长。用户锁定风格就设置 `allowedStyles`；不要让用户手填各套字段。构建会重验选型和素材，混合工程保持全片口播/字幕时钟与音效尾音，默认跨风格配乐坡道须连续试听。机器检查仍为 experimental，详见[本轮测试](docs/template-auto-selection-3.10.md)。

新文案先按[系统适配机制](references/adaptive-composition.md)形成 `brief.json`，运行 `bash "$PL" macro-plan 包ID@版本 brief.json 新规划目录`。该入口按语义阶段、数量、原速动作窗和前后场依赖筛选，再在合法组合内减少效果重复。当前横竖屏版本的 10 个风格、32 个完整组已有代码核对的适配 profile，能力仍为 adaptation-experimental。输出 `spec.json/report.json/report.md/profile.json`；退出码 0 为绑定检查通过，2 为已保存待补或受阻草稿，1 为无效输入。媒体或真实关键词时码缺失时修改 brief 并重新规划，不填源演示时码。`macro-spec` 保留为历史/人工配方入口，它不提供这层语义与邻接诊断；新制作优先沿用带 `adaptation` 的计划，构建会重新验证。

已有计划新增素材时，按[局部分镜重配](references/local-rematch.md)运行 `macro-rematch`，检查建议后通过 `macro-apply-rematch` 保存到新目录。固定原段语义、时间和其它分镜，重验媒体与双侧接缝；基线或素材已改变则拒绝应用。没有兼容新组时保留原组，不随机换效果、不猜其它模板的文案映射。此接口供制作工具调用，尚不等于已接入 ADuDir 拖放界面。

1. `bash "$PL" doctor` 检查 Node、Python、FFmpeg 和 Chrome；缺依赖且允许安装时再 `bash "$PL" setup`。保持源工程和原成片只读，输出到不存在的新路径。
2. 先锁定用户指定的模板来源。素材目录里的其他 `anim`、新工程或旧成片不自动成为动画底稿；不能只插入少数模板片段就称整片使用了指定模板。逐场记录来源包与场景 ID，混用完整包见[来源与多包编排](references/full-project-templating.md#来源与多包编排)。对齐新口播和文案，取得关键台词的准确时间。SRT 只有整句时间时，不可臆测句内某个词的时间；用逐词对齐数据或人工标注。读包的 `role`、`cues`、`motionWindows`、`slots`，按意义挑选、重排或重复完整场景。先列出分镜和缺少的素材。
3. 按新口播编写 brief，运行 `bash "$PL" macro-plan 包ID@版本 /路径/本期brief.json /已有父目录/新规划目录`；查看报告，缺项回到 brief 补齐后重新规划，使用生成的 `spec.json` 构建。在渲染前按[复用内容核对](references/adaptive-composition.md#复用前核对实际表达)核对阶段与真实台词、关键事件落点、素材身份及全片重复。规划器检查声明的结构，不会判断填写的阶段是否忠于台词。仅人工维护历史配方时使用 `macro-spec`，它的 cue 留空，示例文字及原片时长只供认识接口；必须填写本期内容与实际时码，不能给每个重复组机械加同一偏移。`brand` 填本期账号。本期音乐可用 `music:{mode:"track",path,offset}` 指定；未指定时按原编曲结构重合成。人物窗默认在 macOS 使用 Vision 跟踪新口播人脸；不能自动跟踪时须显式配置审核过的 `faceTracking:{mode:"fixed",cx,cy,h}`。任何来源演示数据与示例文字都须替换或明确标“示意”。素材的空路径代表缺项；媒体准备与容量限制看包目录中的 `README.md`。
4. `bash "$PL" macro-build 包ID@版本 /路径/新规划目录/spec.json /路径/剪好口播.mp4 /路径/新工程 [--subs-js /路径/字幕.js]`。新口播长度应与计划总帧数相符。适配器把关键动作窗口锁在原速，较长段落只伸展可停留区；如果时间不够，会报错，改分镜或片段长度，不靠全片线性拉伸。缺文字、数字、媒体或关键 cue 也会报错。
5. `bash "$PL" stills /路径/新工程 0,4,12,...` 抽查首帧、每个 cue 前中后、最长文字、场景接缝和片尾；小圆窗需看到双眼、嘴巴和下巴，fixed 参数须从本期素材确定并检查低头、抬头等极端姿态；再播放所有复杂运动区间，与原工程对照。检查字体、媒体比例/裁切、真实口型、字幕、SFX 与音乐。修订配置或工程并重新验证。
6. `bash "$PL" audio /路径/新工程` → `bash "$PL" mix /路径/新工程` → `bash "$PL" render /路径/新工程 /路径/新片_v1.mp4` → `bash "$PL" check /路径/新片_v1.mp4`。完整观看并听取最终编码文件；`check` 的帧数、解码和响度不能替代视觉与内容验收。新预览统一通过 `bash "$PL" preview /路径/新工程 /路径/新片_v1.mp4 /已有父目录/新预览目录` 发布，绑定真实成片 SHA，显示播放版本并提示旧标签页更新。HDR/DV、源位深和元数据风险须按[素材色彩与预览](references/color-and-preview.md)留下实际对照证据，不只检查标签。

快速体验基础模板可用 `bash "$PL" demo /不存在的新目录`。为真实口播从零组合 `TPL` 时，按[模板目录](references/templates.md)和[字幕方案](references/subtitle-options.md)制作，仍须完整验收。

## 长短素材与重复检查

先用本期剪好口播的实际视频时钟填写 `brief.narrationDuration`，让分镜总帧数与口播一致；这个时长不提供关键词落点。构建还会读取实际音视频元数据，在不匹配时先停止，不抽完整条长口播。长录屏按所需片段及明确 offset 使用，不受整条素材长度限制；剩余素材不够时调整区间、补录或换组，不能偷偷循环。

规划后读取 `report.rhythm` 及报告的“全片重复与停留检查”：连续同组、两三组固定循环、同类动作连续使用和新增超过四秒的停留都要核对本期表达。`ready` 仍只代表绑定检查通过；同一合法组反复出现时，补充语义成立的候选、调整表达分段或另做并验收变体，不为换效果选缺素材的组。动作不足时拒绝硬塞，长段在允许的 hold 容量内延长；镜头数不是随机动画数。

共享运行时只移动 SFX 起音点，保留原生成器的 `d` 和音色；片尾后的尾音支持在规划及构建都复核。本轮范围见[长短素材压力测试](docs/template-stress-3.9.md)。

## 不可省略的检查

- 口播取帧以**目标输出时钟**为准；源场景动画以映射后的**原编舞时钟**运行。不能让原场景时钟控制真人口型，也不能用冻结的真人帧补足缺失时长。
- 第一帧若是口播开场，应看见真人与主题；检查字幕白字描边、字号和安全区，不能把模板源视频的品牌、日期、数值或占位字留在新片。
- 检查每个动作保护窗口的连续片段，而不只抽一张图；录屏、九宫格、作品墙按本期真实素材检查。音乐和音效随新时间线重编，不直接变速旧成品音轨。
- 新文案不能保证自动无损适配。短段容不下动作就拒绝、拆分或换场景；长段只在允许停留的位置延长。新场景仍需针对本期内容设计，不按句子硬套宏场景。
- 输出新工程和新版本成片，不覆盖用户原工程；报告实际检查范围。`anim3` 与 `anim4` 在完整新文案逐帧对照和成片声画验收前保持 **experimental**，不要称已完整验证。

更多细节：[完整工程复用](references/full-project-templating.md) · [制作约定](references/rules.md) · [字幕](references/subtitle-options.md) · [配乐](references/audio.md) · [手绘](references/handdrawn-animation.md) · [排错](references/troubleshooting.md)。

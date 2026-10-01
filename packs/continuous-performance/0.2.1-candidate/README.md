# B · 连续形变

`continuous-performance@0.2.1-candidate`

保留同一物件变换角色、容器与字块各自进退、三层拆解与收回。整组保持对象身份，不能只留下几张切换卡片。

| 组 | 何时用 | 何时换组 | 必要素材 | 当前新内容证据 |
|---|---|---|---|---|
| claim-into-container | 一个主张进入持久容器，三个对象接力，容器继续承担证据与回应 | 没有可持续的对象或结果；三标签不能贯穿全组 | 本期真人口播；文字 | 待新内容验证 |
| decompose-and-consolidate | 展示真实素材，将同一对象拆成三层，归纳规则，再闭合容器 | 并列内容不构成分解与归纳；缺真实素材 | 一段 16:9 本期视频；口播；文字 | 日常练习 17.033 秒，作者确认短段成立 |
| simplify-plan-disrupt | 多项要求压为一个目标、展开四步，再被三次干扰打散并收回 | 新稿没有实际干扰与后果；纯四步教程 | 本期真人口播；文字 | 待新内容验证 |

开场 inputs：claim，container，parts[3]、receivers[3]、proof、response；同一三标签会在前后状态复用。分解 inputs：evidence、question/concept/explanation、parts[3]、ruleHeading/resultHeading/result、container。计划 inputs：many[4]、goal、steps[4]、interruptions[3]、consequence、container。共同字段为 chapter/label/context；精确结构看 macro-spec 的示意输入与清单。

分解内的文字样例、运动路径、波形是源组的三种抽象演示。新内容必须适合这些视觉关系；换标签本身不能证明适配。源组的微幅漂移与装饰波形保留源相位，阅读区扩展不等于将全部装饰运动重新定时。

环境：macOS，横屏 1920×1080，60fps；Node/Chrome/FFmpeg 与本 Skill 的 requirements-runtime.txt。中文使用本机 PingFang SC，等宽字使用本机 `/System/Library/Fonts/SFNSMono.ttf`；包不分发这两种系统字体。未验证 Windows/Linux、其它画幅或替代字体。

包内只有代码、样式、声音配方与示意配置，按仓库 MIT 许可分发。原作者的口播、人脸、头像、录屏、字幕、作品墙和字体文件均不随包分发。来源修订与单元哈希在 manifest 中；代码中的 sourceText 是跨度校验依据，不是新片文案默认值。

先运行 `bash scripts/pipeline.sh setup` 与 `doctor`，再 `macro-spec 包ID@版本 新配置.json`。保留需要的组，填写本期品牌、总帧数和各组 inputs/cues，用 `macro-build` 创建新工程。所有文字容量、最短帧数、额外停留上限与受保护窗口在清单；超过容量会拒绝。事件 at 为整片输出秒数，不能为匹配台词而强行改变原速动作。inputExample 是读书笔记的内容示意；缺素材的 null 必须换成本期有权使用的素材。

口播与真实视频按输出时钟运行；保护动作按源编舞时钟运行。video 输入 `{path,offset}` 的 offset 是原视频秒数。播放区间在槽的 playback 中，准备的真实帧数与允许的末帧停留写入新工程 mediaClocks。长度不够须换录屏或换分镜，不自动循环。

新字幕使用本期 SUBS 数据：`[{t0,t1,zh,en,sp:[[start,end,weight],...]}]`，写入 `const SUBS=...;` 的本地 JS，以 `--subs-js` 传入。sp 是显示进度，不是自动取得的词级对齐；只有句级时间时不声称某个词的实际起点。

每组原样运行、参数调整、新桥接与内部重写应分别记入本片复用记录。若需要桥接，可在生成工程写有边界的本期片段并记录来源与检查；不要改包中已冻结的单位或绕过容量错误。各组可独立起始，但跨组接缝仍须按完整新稿检查；没有默认保证任意相邻组都连续。声音会按选择重合成、SFX 绑定原动作并重映；最终混音与编码文件要实际试听和测量。

当前成熟度为 candidate。源演出全片由作者确认保留；仅下面写明的新内容短段得到作者确认。其它组的新内容、全片接缝、独立制作与干净安装尚待验收，不能将整个包称为已稳定。

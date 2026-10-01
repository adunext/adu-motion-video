# 完成工程与持续模板接入

用户提供新的已完成 Opus 工程后，先接收完整来源，再按复用价值选择演出。不把新片标题作为模板身份；五版不是来源白名单。原片与用户仍在编辑的草稿保持可恢复。

## 私人来源记录

`source_registry.py register SOURCE FINAL --registry OWNER_QA/sources --id stable-source-id --context CONTEXT.json` 登记显式指定的完成渲染、源码快照、媒体与字体指纹。Context 记录 `engine`、`completionEvidence`、`rights`、`environment`、已知问题。未知许可可以登记，不能据此公开分发。

默认 `mediaStorage=fingerprinted-owner-originals`：源码已经冻结，媒体仍依赖原文件。需要脱离原工程保存时加 `--freeze-media`，复制媒体和参考成片。注册器不执行源 JS/Python，不改变源工程，也不登记当前目录中其它草稿。相同修订重复接收会核验并返回既有记录；修改后的源代码/媒体/成片产生新修订。

记录目录、索引、个人字幕和验收视频放在用户的私人输出目录；公共 Skill 仅包含有权分发的配方源码、无个人路径的来源版本与示例素材。`verify RECORD` 检查记录仍可取回相同字节；不证明媒体质量。

来源状态依次为 `received → replayable → candidate → new-content-verified → releasable`。`advance RECORD STATE --evidence REVIEW.json` 保存对应修订的评审证据，不能跳级。证据包含 reviewer、passed、checks、limits 和实际 artifacts；状态表示记录的评审，脚本不会代替观看和试听。

## 判断新增价值

- 同动作只换内容：使用案例或容量证据。
- 参数范围内变化：预设。
- 同因果关系的新动作/空间解法：有来源的新变体。
- 新的完整因果或对象接力：新镜头组。
- 稳定的主体、空间、连接、声音语法：新路线，另验整片与独立使用。
- 不同引擎契约：保留来源和适配需求；先核对复用价值。

依据连续声画与表达关系分类。没有独立起止状态的镜头保留成组；没有必要每次把整片所有部分都参数化。

## 提炼候选包

`node scripts/authored_units.mjs SCENES.js NEW-inventory.json` 按 JS 语法识别完整 Scene 单元，保存原代码、辅助函数、源区间、哈希和可审查字符串跨度。AST 只能建议代码边界；持续运动、声音尾音、入场前状态和离场接力必须实际审片。没有适配契约的工程保留完整来源，不用正则猜大括号来拆演出。

审查 proposal 后运行 `python3 scripts/extract_authored_pack.py SOURCE PROPOSAL.json NEW_PACK`。Proposal 固定 sourceRevision、各 scene 文件 SHA、单元 index 与 expectedStatementSha256；每组 contract 提供 role、boundaries、motionWindows、cues、slots、内容容量、素材条件及限制。slots 使用经过复核的源码跨度；源码变化会拒绝绑定。包保存独立闭包，选一组时不会实例化未选作品墙或其它场景。

`authored-unit/1` 包沿用 macro-spec/macro-build 的输出口播时钟、保护动作窗、输入检查、音效重映和导出流程；runtimeFiles 保留路线运动函数。生成工程的 `recipe_versions.json` 固定包版本、源哈希、场景来源、输出帧和运行代码哈希。旧工程内已经保存 runtime，更新库不会自动改变它。

`python3 scripts/source_registry.py link SOURCE_RECORD PACK/manifest.json` 将清单哈希与每组 ID/版本关联到来源。来源修订不符或同一 ID/版本内容变化会拒绝；关联本身不晋级质量状态。修改配方或公开元数据时创建新版本，旧版本保持可追溯。

镜头组可用 `inputPath` 声明有名的语义字段，例如 `claim.line1`、`parts.0.label`、`evidence.video`。多个可见位置可以绑定同一个字段；`inputTemplate` 只插入文本值，例如 `// {chapter} — {label}`，不运行代码。配方内部仍固定经过核对的源码跨度，使用者在目标 spec 的 `inputs` 提供内容；不要同时填同一字段生成的内部 `slots`。`inputExample` 是可编辑的内容示意，媒体的空值表示缺项。

真实视频槽声明 `playback:{start,end,fps,rate,terminalHoldSeconds}`；start/end 在源编舞时钟内，rate 默认为 1。目标 `inputs` 提供 `{path,offset}`。实际播放以映射后的输出起点和输出经过时间取帧，阅读区变长时不会随动画时钟慢放视频。媒体不够长会拒绝；仅配方明确支持的末帧停留可以使用，实际停留写入 `mediaClocks`。人物口播也必须与工程总帧数完全一致。输入轨道的一帧起始偏移按输出帧网格重采样并记入 import.json；更大的视频起始空缺须先提供对齐后的素材。

默认登记只冻结源码、保存媒体指纹并依赖原素材；独立完整快照要在首次登记时使用 `--freeze-media`。已有修订不会因重复命令而升级为媒体快照，若需要另一份完整冻结，使用独立 registry。

源码重放、新内容表达、独立安装使用分别记录。正常速度连续声画、最终编码文件、真实字幕/取帧/响度/真峰与对照证据缺一项就只报告已验证范围。候选包不得仅凭测试通过而标稳定；发布按实际通过的路线与环境增量进行。

## 冻结已评审的发布版本

已有候选保持原字节。用 `python3 scripts/publish_reviewed_pack.py CANDIDATE REVIEW.json REVIEWED-README.md NEW_VERSION_DIR` 创建新版本，只包含评审列出的完整组。这个入口记录人工判断，不会代替观看、许可核对或独立使用。

Review 固定 `packId`、`sourceVersion`、`sourceRevision`、`manifestSha256`，提供新的稳定 `version`、`reviewer`、`passed:true`、`recipes:[组ID]`、`limits`、`scope` 和 `checks`。scope 为 `group` 或 `route-subset`；共同检查为 `continuous-source-av`、`continuous-new-av`、`reuse-record`、`clean-install`、`distribution-rights`，路线范围另需 `independent-use`。按实际计划注明独立证据覆盖一条路线还是本轮共享生产流程，不能把一个独立影片称为所有路线都独立验证。

`artifacts` 只提供 `{id:"evidence-label",sha256:"64位小写摘要"}`。公共版本保存这些标签、摘要与限制，不附私人路径或影片。新的 README 必须写明确的 `包ID@新版本`。错误源哈希、缺门槛、未识别组、被改写的冻结文件或已存在输出会拒绝；未列出的单位不随新版晋级。新版本保存 `promotedFrom`、原单位/运行字节和重新冻结的文件清单。

## 已实施的不同契约接入实例

`paper-balance` 来自另一份完成的 inline DOM/perspective 工程，属于“新叙事组 + 不同运行契约适配”，并非新增稳定路线。它将疑问、天平、用途、插图批注与三步小球确认保留成一个完整组。实际新内容短段为 13.9 秒；原演出区间的同内容重放为 11.833 秒。原/新对照已获作者认可，1.0.0 为这一个续接组的稳定版本；0.1.6-candidate 保持原样供追溯。

这份来源没有 Scene 闭包，不能直接运行通用 authored-unit 提取器。专用 [adapter](../adapters/paper-balance/README.md) 固定来源修订、入口哈希和已审查代码区间；只把该组接到 Scene 宿主，沿用目录发现、语义绑定、音效重映与导出。其它 inline 工程不由它自动支持。

只共用运行所需的宿主布局。原来源的字体平滑、字幕位置、层级、人物标签滤镜和前组闪光尾段应对照实际像素核查；把另一条路线整张样式表叠上去，可能保住几何却改变观感。此实例的未改动字体字节与完整 OFL 通知随 CSS 保存，系统中文字体仍是外部依赖。

公共包只保存该组源码、输入边界和声音配方。原人物、生成插图、完整字幕和原混音仅用于私人同内容控制；新内容使用新的原声、明确的示意插图与重合成配乐。原片深色段隐藏字幕，新内容字幕在三步下方保持可见，差异已声明。当前单行字幕位置须以实际文案检查，较长字幕应先拆句或另审布局。

关联这一个候选组不会把整份来源标为 replayable 或新路线稳定。旧 A 新片从保存配方重新构建后，运行/数据文件、媒体与时间计划仍一致；接入过程中未修改公共构建器、播放器或 A/B 包。其它来源继续保留各自状态与未提炼区间。

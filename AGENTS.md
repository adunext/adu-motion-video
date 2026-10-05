# adu-motion-video：通用 Agent 入口

用户选择“模板 01 的 B 风格”或 `01-B` 等编号时，先按[模板与风格目录](references/template-catalog.md)查找一级模板、二级风格和对应版本。需要辅助动画素材时，可使用[阿杜导演公开素材 API](references/lottie-assets.md)，下载到本期工程并检查渲染与来源；素材库不代替本期真人或真实证据。

支持 Windows、macOS、Linux，以及 Codex、Claude Code、豆包、DeepSeek、WorkBuddy 等助手。自动制作要求当前助手环境能读写素材并执行命令；没有 Skill 加载机制时，可直接读取本仓库说明。Windows 可原生使用 `python scripts/pipeline.py`，macOS/Linux 使用 `python3 scripts/pipeline.py`；旧 Bash/WSL 入口仍保留，依赖与素材路径以实际执行环境为准；平台差异见[兼容说明](references/compatibility.md)。请先完整阅读本仓库的 [SKILL.md](SKILL.md) 和 [制作约定](references/rules.md)，再按 [完整工程复用说明](references/full-project-templating.md)工作。用户当前要求优先；不要把仓库中的历史账号、数据或示例素材当作本期内容。

默认通过 `bash scripts/pipeline.sh packs` 找到相关包与显式版本，读取清单和 README，复用**完整镜头组或场景**。A 的三个组、B 的两个组、C/D/E 各三个组、02-A 纸面天平续接组和 02-B 纸面聚合两个组在 1.0.0 为 stable，既有验收记录使用 macOS 1080p60；旧候选与未验证的 B 计划干扰组保留，旧 anim3/anim4 为 experimental。各自的成熟度与验证范围按清单和[能力矩阵](docs/capability-matrix.md)。先依据新口播与文案选择有意义的宏场景，填准时间、文字、数值和本期媒体，再构建工程并做连续声画检查。9 个 `TPL` 仅供 quick-start；它们不代表完整工程效果。手绘角色续接沿用[手绘方法](references/handdrawn-animation.md)，目前尚未形成完整包。

运行命令见 [README](README.md) 和 `scripts/pipeline.sh`。明确告知用户输入素材、生成工程与 MP4 的路径，以及首帧、字体、裁切、字幕、口型、音乐、音效、完整解码和原工程对照的实际检查结果。未完整验收的结果标记 **experimental**；不要保证任意新文案能自动无损套用。

新文案复用先读[系统适配机制](references/adaptive-composition.md)，将整段表达标注意图、阶段、数量与真实落点，再运行 `macro-plan 包@版本 brief.json 新目录`。当前横屏 10 风格/47 组、竖屏 11 风格/54 组都有版本绑定 profile；先校验语义、容量、动作和接缝，再优化效果重复度。`needs-binding/blocked` 必须补 brief 或调整分镜并重新规划；不能删除 spec.adaptation 或修改 ready 来跳过检查。新提炼必须提供结构化 adaptationProfile；`--legacy` 仅重放历史提案。动作窗间隙不是自动剪点，细拆须另做独立入/出场与声画验证的新变体。

03-A「深色 3D · 多屏展陈」横屏基线选择 `anim4-showcase-macro@1.1.1-candidate`，读取[专门说明](references/dark-3d-template.md)。九场源码沿用旧包，新增原生竖屏，本期 1.1.1 色彩修正版已保存；冷安装历史属于 1.1.0，当前待作者连续声画确认；旧 1.0.0 和十七个稳定组保持原字节。不能把候选技术检查报告成新路线稳定或独立作者验收。

用户要求竖屏时按目录 portraitSelection 选新候选，在 brief 顶层设置 layout=portrait；当前竖屏十一种风格、54 个完整组均有布局契约。macro-plan/build/render 自动传递 1080×1920；不要只改 W/H。旧稳定包保留，竖屏候选的几何检查不等于真实口播声画验收。参见[竖屏说明](references/portrait.md)。

05-A「鲜色角色叙事」用 `vivid-sticker-performance@0.1.1-candidate`，横竖屏均可选；读[范围与数量合同](references/vivid-sticker-template.md)。三个原子组不要拆成单独入场/飞行/印章。公共动图使用新矢量示意，不是原人物/贴纸或新片声画验收。

长短素材先核对真实口播时长与分镜总帧数，读 `report.rhythm` 的全片重复/轮换/同类效果/停留提示；优先补内容与合法候选，不用缺素材的组换取变化。长证据素材按明确 offset 抽取所需区间，剩余时长不足不循环。构建在大规模抽帧前复核真实口播元数据；新运行时保留 SFX 生成器长度。范围见[长短素材压力测试](docs/template-stress-3.9.md)。

自动比较风格、长短文案与不同素材时，读取[全库选型](references/automatic-selection.md)，由当前助手整理真实语义与候选字段，不让用户手填复杂配置。`auto-plan` 同时比较完整单风格和合法混合路线；`auto-build` 重验后沿用一次口播导入、全局字幕和 SFX 尾音。缺真实素材、超容量、错误数量及无独立跨风格入口不能绕过；有实际含义的分段路线保持整片帧数一致。

3.11.0 新增 06-A「活力色彩 · 原生竖屏」七个完整组，选择 `vibrant-color-performance@0.1.0-candidate` 并显式 layout=portrait。当前竖屏11风格/39组，横屏仍10风格/32组；不得为新包猜横屏。读[模板说明](references/vibrant-color-template.md)与实际验证记录。

3.12.0 新工程配乐必须显式绑定 track/path/offset；旧 source synth 全部时长变体淘汰，缺配乐待补，不回退静音。只有明确无BGM才用 none。当前 SFX 独立种子不等于历史 synth 字节；换乐已交付影片应保留旧 stems。最后动作保护窗后的时间只作阅读/人物/证据连续性复核，不判作静止。提炼 Skill 仅本地维护，不加入公开分发。

## 新口播的质量流程

先理解完整台词、真实数量和素材身份，再按所求画幅选型；`auto-capabilities --layout landscape|portrait` 分别显示全目录与所求画幅可用规模。不支持画幅是能力不匹配，不能要求用户补素材解决。保存的 auto-plan 锁定原包版本，新增无关目录项目不触发隐式换组。

提供原文 `contentEvidence` 与每段 `ownershipRefs`，覆盖所有保留台词且不重复、不错序；显示文案的 `supportingRefs` 可多对多。助手核对否定、条件、数字、单位和实体，代码验证来源摘要与声明归属。旧工程缺依据会明确报告 `source-unrecorded`，不能称已经验证台词匹配。使用有名输入；规划、素材重配、构建使用同一组选场校验。

口播修剪默认关闭；本次用户明确开启 `repairPolicy.mode=basic` 才能尝试基础修剪，旧工程或 map 不代表开启。空间字幕位置不改变字幕时间。先构建并检查真实字体、媒体、动作与声尾，再完整导出与连续看听；最后由用户对同输入 A/B 确认效果。技术 ready、静帧和短接缝不替代最终验收。

当前候选目录、变体合同、字幕比例与可选 basic 修剪以[3.13.0-rc.1 升级说明](references/quality-upgrade.md)为准；旧版本号段落为历史记录。只按实际路径的版本运行，不自动替换另一安装或桌面内嵌副本。最终升级接受由所有者连续看听 A/B 决定。

用户说“加载这个 skill，引导我开始创作”时，读取 references/start-creating.md，清楚说明先发素材、方向/画幅和可选补充，再推荐匹配模板；不要只说已加载、不告诉用户下一步。已有素材直接核对推进，不能重复要求用户填写复杂配置。

3.14.0-rc.1：字体为优先推荐项，默认 preferred，缺少原字体时自动使用随包 Noto 字体并记录替换；不得因原字体 SHA、macOS SF Mono 或 Vision 缺失要求用户停工。检查实际文字布局与裁切，只有明确要求精确字体时启用 exact。运行入口、依赖选择与验证边界见 references/compatibility.md。

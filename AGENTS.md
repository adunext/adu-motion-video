# adu-motion-video：通用 Agent 入口

用户选择“模板 01 的 B 风格”或 `01-B` 等编号时，先按[模板与风格目录](references/template-catalog.md)查找一级模板、二级风格和对应版本。需要辅助动画素材时，可使用[阿杜导演公开素材 API](references/lottie-assets.md)，下载到本期工程并检查渲染与来源；素材库不代替本期真人或真实证据。

适用于没有 Skill 加载机制、但能读写本地文件并执行命令的 Agent。请先完整阅读本仓库的 [SKILL.md](SKILL.md) 和 [制作约定](references/rules.md)，再按 [完整工程复用说明](references/full-project-templating.md)工作。用户当前要求优先；不要把仓库中的历史账号、数据或示例素材当作本期内容。

默认通过 `bash scripts/pipeline.sh packs` 找到相关包与显式版本，读取清单和 README，复用**完整镜头组或场景**。A 的三个组、B 的两个组、C/D/E 各三个组、02-A 纸面天平续接组和 02-B 纸面聚合两个组在 1.0.0 为 stable，限于已验收的 macOS 1080p60；旧候选与未验证的 B 计划干扰组保留，旧 anim3/anim4 为 experimental。各自的成熟度与验证范围按清单和[能力矩阵](docs/capability-matrix.md)。先依据新口播与文案选择有意义的宏场景，填准时间、文字、数值和本期媒体，再构建工程并做连续声画检查。9 个 `TPL` 仅供 quick-start；它们不代表完整工程效果。手绘角色续接沿用[手绘方法](references/handdrawn-animation.md)，目前尚未形成完整包。

运行命令见 [README](README.md) 和 `scripts/pipeline.sh`。明确告知用户输入素材、生成工程与 MP4 的路径，以及首帧、字体、裁切、字幕、口型、音乐、音效、完整解码和原工程对照的实际检查结果。未完整验收的结果标记 **experimental**；不要保证任意新文案能自动无损套用。

新文案复用先读[系统适配机制](references/adaptive-composition.md)，将整段表达标注意图、阶段、数量与真实落点，再运行 `macro-plan 包@版本 brief.json 新目录`。当前横竖屏版本的 10 个风格、32 个完整组都有版本绑定 profile；先校验语义、容量、动作和接缝，再优化效果重复度。`needs-binding/blocked` 必须补 brief 或调整分镜并重新规划；不能删除 spec.adaptation 或修改 ready 来跳过检查。新提炼必须提供结构化 adaptationProfile；`--legacy` 仅重放历史提案。动作窗间隙不是自动剪点，细拆须另做独立入/出场与声画验证的新变体。

03-A「深色 3D · 多屏展陈」横屏基线选择 `anim4-showcase-macro@1.1.1-candidate`，读取[专门说明](references/dark-3d-template.md)。九场源码沿用旧包，新增原生竖屏，本期 1.1.1 色彩修正版已保存；冷安装历史属于 1.1.0，当前待作者连续声画确认；旧 1.0.0 和十七个稳定组保持原字节。不能把候选技术检查报告成新路线稳定或独立作者验收。

用户要求竖屏时按目录 portraitSelection 选新候选，在 brief 顶层设置 layout=portrait；十种风格、32 个完整组均有布局契约。macro-plan/build/render 自动传递 1080×1920；不要只改 W/H。旧稳定包保留，竖屏候选的几何检查不等于真实口播声画验收。参见[竖屏说明](references/portrait.md)。

05-A「鲜色角色叙事」用 `vivid-sticker-performance@0.1.1-candidate`，横竖屏均可选；读[范围与数量合同](references/vivid-sticker-template.md)。三个原子组不要拆成单独入场/飞行/印章。公共动图使用新矢量示意，不是原人物/贴纸或新片声画验收。

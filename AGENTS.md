# adu-motion-video：通用 Agent 入口

适用于没有 Skill 加载机制、但能读写本地文件并执行命令的 Agent。请先完整阅读本仓库的 [SKILL.md](SKILL.md) 和 [制作约定](references/rules.md)，再按 [完整工程复用说明](references/full-project-templating.md)工作。用户当前要求优先；不要把仓库中的历史账号、数据或示例素材当作本期内容。

默认通过 `bash scripts/pipeline.sh packs` 找到相关包与显式版本，读取清单和 README，复用**完整镜头组或场景**。A/B 为候选，旧 anim3/anim4 为 experimental；各自的成熟度与验证范围按清单。先依据新口播与文案选择有意义的宏场景，填准时间、文字、数值和本期媒体，再构建工程并做连续声画检查。9 个 `TPL` 仅供 quick-start；它们不代表完整工程效果。手绘角色续接沿用[手绘方法](references/handdrawn-animation.md)，目前尚未形成完整包。

运行命令见 [README](README.md) 和 `scripts/pipeline.sh`。明确告知用户输入素材、生成工程与 MP4 的路径，以及首帧、字体、裁切、字幕、口型、音乐、音效、完整解码和原工程对照的实际检查结果。未完整验收的结果标记 **experimental**；不要保证任意新文案能自动无损套用。

# 鲜色角色叙事提炼器

只接入已登记的vivid-sticker-response修订。`python3 adapters/vivid-sticker/extract.py SOURCE_RECORD adapters/vivid-sticker/proposal.json NEW_PACK` 固定全部运行源码、原块和前置口播姿态；抽取三个独立初始化的完整演出，保留source-time绘制/output-time口播、Canvas、源效果与SFX。人物/贴纸/纹理/字体/原曲不分发。

新增portrait/typography运行文件随manifest冻结；提案包含数量、阶段、动作保护、声音尾音和新内容容量，不支持未审核源文件或作品墙。静态inventory沿用scene-helper AST方法；不会执行原audio.py。

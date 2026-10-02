# 豆包暗黑仪器台适配器

当前使用 `doubao-console-performance@0.1.1-candidate`。`0.1.0-candidate` 是本轮诊断版本，存在外层页面默认边距问题，不作为公开推荐版本。

`extract.py RECORD PROPOSAL FRESH_OUTPUT` 验证来源登记及源码哈希，复用 `authored_units` 提取完整声明，依据审查后的提案生成原子场景与 `adaptationProfile`。不得用未审查的源码、前置 TKK 或拆分点替代合同。

`prepare_episode.py PROJECT` 从本期导入的 `voice.wav` 生成 `doubao_episode.js`，由构建器白名单 `doubao-voice-rms/1` 检查实现哈希后调用。转场桥接保留原 FX 层级；每个实例独立持有 Canvas、主讲人卡片和全局状态。

运行 `python3 -m unittest discover -s tests -p test_doubao_pack.py -v` 核查固定的 `0.1.1-candidate`。这些结构与计算检查不代替连续声画、字幕、尾音、真实字体和独立复用验收；候选的实际状态以版本清单及对应证据为准。

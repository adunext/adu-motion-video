# 暗黑仪器台 · 候选模板

每组保留完整源码编舞、Canvas 背景与粒子、玻璃面板、主讲人卡片及 HUD。每次复用拥有私有 DOM、Scene、TKK、SHK、FLASH 和 Canvas 状态；重复同一组不会共享上一实例的状态。

动画几何、章节和音效触发沿用源时钟；口播画面、跟脸裁切、时间码、进度与本期语音光晕使用输出时钟。组选起点的前置 TKK 在提案中明确记录。转场通过 `macroTransition/1` 留在原先位于主讲人卡片下面的 FX 层。

使用前提供本期文案、真实锚点、图片、已剪辑口播、显式 `grainTexture` 图片及冻结版本对应的 `externalFontFiles`。原视频、口播、作品、纹理图片、字体和外部 BGM 均不随包分发。`macro-build` 导入口播后执行白名单 `doubao-voice-rms/1` 预处理，生成新的语音光晕采样；不复用原片 `vox.js`。

原片配乐是外部音乐文件，默认合成底乐属于明确的新配乐。源 ENV/HITS 和每组 S() 动作音效保留并按实际输出重新映射，不能声称默认合成音乐等同原曲。新的语音光晕采用逐帧 RMS 与 95 分位归一化，也不声称和源片旧语音采样完全一致。

当前仅为 1920×1080、60 fps 的候选路线。各场完整动作窗口保护，尚未声明任意拆分点、原生竖屏、独立作者使用或发布验收通过。源起点转场在独立片头没有前镜头，采用清楚的首帧；组间仍需连续核查主讲人姿态、转场、尾音和实际媒体。


## 0.1.2 typography review

This candidate adds bounded text layout after silent short/medium/near-limit copy tests found clipped manual names, a manual title hidden by its card, long fusion status values colliding with the result chip, and chat step labels entering the message area. It retains the same complete action groups, source times, cues, media slots, narration requirements and sound events.

Glyph width is measured using the loaded font. Single-line titles shrink only when they exceed their reserved region. Status values, chat step labels, the method icon and manual name may wrap within explicit line and font-size bounds. Text is never truncated or replaced with an ellipsis. The minimum-size failure asks for a shorter slot instead of silently hiding text. The `typography` manifest block records the region limits; `maxChars` is still the input ceiling, not a guarantee for every possible Unicode string.

The 0.1.1 frozen pack is unchanged. New source span offsets, source block hashes, file fingerprints and the embedded adaptation profile are versioned together. The candidate remains **not accepted for new narration or audiovisual delivery**. Private no-person silent typography fixtures prove only display-copy layout; they contain no old presenter footage or copied voice.

Observed review: four new display-copy sets (short, medium, near-limit Chinese, and Latin/CJK mixed words) were sampled at 198 frames each in Chromium 154, using all 8 owner-supplied font files with manifest-matching hashes. All 208 text bindings became visible; no clipped text, missing resources or presenter frames were found in these 792 samples. Fixed-region comparisons and reverse-seek geometry passed with those fonts. Separate browser tests exercise maximum-length CJK and wide Latin strings, readable size floors, and explicit rejection beyond the minimum size. These are typography observations, not new narration or audiovisual acceptance.

For future extraction, **maxChars alone is not geometric acceptance evidence**. A fixed text region needs its pixel width, line allowance and minimum font size recorded, followed by real-font short/medium/maximum CJK and Latin/mixed-copy tests. Check neighbouring objects as well as clipping: visible text can remain inside the canvas while covering another object. If the region cannot fit at its readable minimum, rewrite that slot or select another group; do not shrink indefinitely, truncate, or silently hide words.

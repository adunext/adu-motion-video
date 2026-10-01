# 纸面透视 · 矛盾转用途

`paper-balance@0.1.6-candidate` 含一个完整叙事组 `apparent-tension-to-value`：提出看似矛盾的选择，天平先倾斜再回稳，转到实际用途，带出象征插图与逐写批注，最后用小球串联三步确认并离场。

这是一个新增镜头组候选，尚未声明为完成整片验证的第三条路线。源工程是已登记的国庆 v1；没有附带原口播、原插图、录屏或外部音乐。来源版本和准确源码区间见清单。

适合“表面两难 → 解释用途 → 三步行动”。例如完整产品与先试半成品的关系。不适合两个互不相关的主题、需要数据证据的定量比较或省略最后三步的短标题。插图是象征画面；展示真实证据应另选证据组。

## 输入与时钟

- `context`：问题背景，最多 18 字。
- `opposition`：`leftLead/rightLead` 最多 3 字，`left/right/rightShort` 最多 4 字，`subject` 最多 6 字。right 是问句用语，rightShort 是天平上的短标签。
- `value.heading`：最多 12 个字符的大号英文标题；`lead` 最多 3 字，`label` 最多 8 字。
- `annotation`：最多 12 字的批注。
- `steps`：恰好三个 `{label}`，每个最多 4 字；`stepSummary` 最多 34 个英文字符。
- `presenterLabel`：本期人物署名，最多 20 字。
- `illustration`：本期有权使用的透明 PNG/SVG 等图片路径。它随原 3D 插图动作入场，不是录屏或测量证据。

三个必填事件是 `value`、`illustration`、`steps`，分别对应用途出现、插图出现和三步确认开始。按本期真实语义阶段设置全片帧或秒数；句级字幕不证明词级起点。

源组为 13.73–25.57 秒；1080p60 的原长网格为 710 帧。允许长度为 710–1070 帧，受保护动作必须保持 1×。延长只发生在清单允许的读字区；事件的相对时序仍需通过规划器。真人使用输出帧钟，字体和插图用本期输入，禁止静默循环或冻结真人。

此组是段落续接，保留了原来约 0.37 秒的人物返回动作；起点不是完整人物已出现的开场标题。末端包含三次确认与小球收势。源 25.55 秒的 whoosh 属于下一组入场，不在这个独立组中播放。其它镜头组连接仍需审片。

## 调用

```bash
bash "$PL" macro-spec paper-balance@0.1.6-candidate 本期.json
# 填好命名 inputs、三处 cues，提供总帧数吻合的剪好口播。
bash "$PL" macro-build paper-balance@0.1.6-candidate 本期.json 口播.mp4 新工程 --subs-js 本期字幕.js
```

字幕 JS 沿用 `SUBS` 合同：每组包含 t0/t1/zh/en/sp；只有句级字幕时可用 `sp:[[t0,t1,字数]]` 表示显示进度，不能称为逐词对齐。字幕保留原文字大小与底部位置，用本期输出钟，后三步期间保持可见；这是相对原片深色章节隐藏字幕的有意适配。继续按 Skill 的 audio → mix → render → check 完成声音与导出，并正常速度完整观看试听。

原片使用私人外部音乐。默认提供明确标注的合成配乐替代，动作音效保留源类型、增益、声像和时长，并随事件映射。需要原片式配乐时显式传 `music:{mode:"track",path,offset}`；音乐长度不足会拒绝，不附带、不自动查找原片音乐。替代编曲的听感需单独验收。

## 字体与环境

Anton、Caveat、Geist、Geist Mono 的原 WOFF2 字节嵌入 CSS。已核对字体内名称、版权与许可元数据；每份 CSS 内保留四份完整 OFL 版权及许可文字，生成工程也会保留。文件哈希与来源版本见清单。许可原文另见 `licenses/` 与官方 [Anton](https://github.com/google/fonts/blob/main/ofl/anton/OFL.txt)、[Caveat](https://github.com/google/fonts/blob/main/ofl/caveat/OFL.txt)、[Geist](https://github.com/google/fonts/blob/main/ofl/geist/OFL.txt)、[Geist Mono](https://github.com/google/fonts/blob/main/ofl/geistmono/OFL.txt)。

中文仍使用 macOS PingFang SC；现有口播宿主使用系统 SF Mono。这些系统字体不分发。实际验证目标为 macOS、1920×1080、60fps；其它平台没有一致性承诺。

## 来源与适配

完整来源修订 `279ffaa155c59ae35940c31fa09b9d85c960c2148a20368f146563fc70069d4b`，入口 SHA `4f14cbd5178d5a0f25cfed8afbc920711c68d9e56dadc3e3c67700c654df8062`。

该工程使用 inline DOM 帧渲染器。专用 adapter 仅转换这一已复核修订：新增 Scene 宿主与局部图层 ID，人物取帧/裁切接到输出时钟，原插图变成必填媒体；原天平、字、3D 插图、批注、小球、拖尾与姿态函数保留在独立闭包。adapter 和各原始代码段哈希记在 manifest。主构建器和 A/B 包未为该组改写。

复核和状态按源演出、新内容、外部复现分别记录。清单当前仍为 candidate；静帧、自动解码和状态检查不能代替连续声画判断。

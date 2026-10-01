# 舞台镜头：前后层与人物让位

Candidate `stage-performance@0.2.2-candidate`. 三个完整组从已认可的 C 源路线冻结，保留独立闭包、路线专属 helper/样式、人物移动、原速动作窗口和声音配方。公开包不含人物、私人录屏、作品墙或系统字体。源码状态/媒体时钟检查与正常速度审片分别记录；目前尚未证明新内容整片或独立使用。

## 表达目的与输入

- `claim-and-response`：完整主张、方法、对象与回应。适合“提出方法 → 面向对象 → 本期验证 → 面对阻力”的叙述；无需沿用原片的平台事件。分别填写 claim、method、audience、proof、response。两行标题每行不超过六字，巨字主体以四至六字起步，长内容交给字幕。
- `evidence-and-focus`：实际材料、结果与三处观察；需要本人可用素材。evidence.overview/detail/result 均为实际视频对象 `{"path":"/本期视频.mp4","offset":0}`。材料走新输出时钟；detail 按显式 2.4× 播放，不偷偷变速原声。标题与注释如实写明素材/示意身份，三个窗口可使用同一份本人记录，不代表三次独立实验。
- `decompose-and-consolidate`：概念展开为步骤，再整理成方法。三个 parts必须有真实的分解关系；不要将无关关键词塞进槽。context 明确示意/经验边界，result 提供本期归纳。

## 制作与容量

1. 按主 Skill 读完整新口播，再选择、重排或重复组。`bash scripts/pipeline.sh macro-spec stage-performance@0.2.2-candidate /不存在的/配置.json` 提供命名 inputs 草稿；只填写本期内容。品牌用当前账号；chapter/label 控制本期角标。
2. 逐组查看 manifest 的 motionWindows、cues 与 maxChars。cue 的 `at` 是新片全局秒数，按真实台词或明确导演动作落点填写；不是按字数估算的词级对齐。时间太短会拒绝，过长只伸展允许停留区。不要通过内部改源码去躲开容量检查。
3. 运行 macro-build、stills、audio、mix、render、check。公共组内部不改；必要本期桥接单列来源并保持路线风格。保存复用/桥接/内部修改的逐镜记录。
4. 与源演出的连续动作对照，正常速度完整听看新 MP4。首帧、字幕、真实口型、转场、文字容量、素材裁切与音乐都须检查，DOM/解码/测试不能代替质量判断。

支持边界为当前 macOS、PingFang/SF Mono、1920×1080、60fps，当前依赖锁另随 Skill 保存。C/D/E 的字体和几何均沿用各自来源；不是 A/B 的换肤。源 CSS 按已审查的 HTML 级联顺序合并。旧包和旧工程不随此新增改变；包的 files 与 sourceBlockSha256 固定实际字节。

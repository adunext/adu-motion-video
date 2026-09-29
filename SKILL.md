---
name: adu-motion-video
description: 制作或修改 HTML/JavaScript 口播动效视频、手绘卡通动画、双语字幕与横竖屏成片。用于新素材成片、沿用旧工程风格、补漏句与同镜头动画续接、按时间点修改；保留用户指定的 DOM、Canvas 或 p5.brush 引擎。
metadata:
  version: "1.4.0"
---

# adu-motion-video

面向可读写本地文件、执行命令的 Codex / Claude Code。输入是用户口播或配音、文案和可选字幕/录屏；输出是独立版本 MP4、可编辑工程及核验记录。只有文案时先做明确标注的无配音样片，配音和语音识别须另有工具。初次使用看 [README](README.md)：工具、安装、素材清单和可复制请求。

## 1. 确定任务与环境

先读 [公共约定](references/rules.md)。用户本次要求优先；品牌、账号、颜色、画幅从本次输入或项目配置读取，不把作者个人视频内容当成模板分类。若本地存在 `references/local-profile.md`，仅作为该用户的历史偏好读取，不公开复制。

- **首次试用 / 检查能否运行**：先 `doctor`，缺依赖才 `setup`；用 `demo` 或媒体齐全的独立示例验证。缺少用户素材时不要把演示人物包装成用户成片。
- **新片**：读 [文案与时间轴](references/authoring.md)，以新口播为主时钟，按新内容编排；若采用 DOM 起始模板，`CONFIG.demo` 须在接好正式媒体后改为 `false`；独立 Canvas 工程按自身入口接入声音和时钟。
- **改旧片**：检查成片、可编辑工程、声音和依赖，在新版本里改。保持原引擎；不要因为本 Skill 的起始模板是 DOM 就重写 Canvas / p5.brush 工程。
- **手绘卡通 / 续接上一镜**：读 [手绘动画与续接](references/handdrawn-animation.md)。延续主体位置、道具状态、准备动作与收势，分别管理原片、输出与插入段时钟。

令 `SKILL_DIR` 为当前 Skill 目录，`PL="$SKILL_DIR/scripts/pipeline.sh"`，`D` 为用户本次新工程目录。路径始终引用。临时帧写系统临时目录，最终文件写用户指定目录。

```bash
bash "$PL" doctor
python3 "$SKILL_DIR/scripts/inspect_project.py" "$D"
# 仅在缺依赖且本任务需要安装时执行；联网安装，不捆绑系统浏览器/FFmpeg：
bash "$PL" setup
# 无个人素材演示，必须使用新的目录：
bash "$PL" demo "$D"
```

Node.js 18+、Python 3.10+、FFmpeg / ffprobe、Chrome / Chromium；Shell 入口使用 Bash。人脸追踪另需 macOS Vision / Swift。不要宣称未实测的平台已全流程兼容。

## 2. 选择画面语言，不混淆分类

按需读 [视觉分类](references/visual-routes.md)。先选大类，再选下级方案：

- **现代图文动效**：实拍卡片、编辑分栏、纵深舞台。
- **手绘卡通叙事**：角色与道具表演、同镜头续接。

错峰入场、连续形变、关键词 / 节拍字效是可组合的动作手法；字幕方案、画幅和渲染引擎单独确定。不要恢复 A～F 平铺分类或个人选题名称。默认只做一版；用户要求比较才做多版。

## 3. 接入素材并编排动作

新片用 `bash "$PL" new "$D"` 创建独立工程；已有工程改版另存，勿覆盖。新建模板带演示内容，不代表正式分镜已完成。

已剪好的单条口播优先直接导入，不必再对齐一次：

```bash
bash "$PL" import "$D" "剪好的口播.mov"
```

读取生成的 `import.json`，按实际时长设置 `CONFIG.demo=false`、帧率/片长并重排 `scenes.js` 与字幕；导入不会自动修改创意时间轴。已有媒体输出会拒绝覆盖。

仅当剪好口播需要匹配多条原始素材时运行对齐：

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/scripts/align_talk.py" \
  --master "剪好的口播.mov" --raw "原片1.mov" "原片2.mov" --out "$D"
# 可选，仅 macOS：
bash "$SKILL_DIR/scripts/face_track.sh" "$D"
```

`align_talk` 生成帧序列、`talkmap.js`、`sync_segs.json` 和 `voice.wav`。只有一条剪好的口播可同时作为 master/raw；先核对烧录字幕。对齐分数不是逐帧口型保证，检查切点和大人物画面。接口差异见 [兼容说明](references/compatibility.md)。

先写“时间—台词—主体动作—结果—转场”的简洁分镜，读 [动作设计](references/motion-quality.md)，按需查 [场景配方](references/scene-patterns.md) / [API](references/api.md)。所有状态从绝对时间计算；新增漏句不能用不对应台词的旧口型。补音频时可延续动画，但不能冻结上一帧代替新动作。

将品牌、时长、素材和字幕写入项目配置；需要竖屏时重新布局，改宽高不会自动重排固定坐标。历史片段仅作配方，不能带入旧话题、私有路径、媒体或旧时间轴。

双语字幕按真实口播分组，明确用户修订原文；标准 / 英文加大独立选择，见 [字幕方案](references/subtitle-options.md)。加入片段后统一移动后续字幕、口播、音效和动画，不分别手工猜偏移。

## 4. 先验证短段，再输出成片

对于模板 / 相同 DOM 合约，使用 [严格导出工具](references/tooling.md)：

```bash
bash "$PL" stills "$D" 1.2,3.4,5.6
bash "$PL" audio "$D"
bash "$PL" mix "$D" 0.50
bash "$PL" render "$D" "输出目录/新片_v1.mp4"
bash "$PL" check "输出目录/新片_v1.mp4"
```

纯静音任务显式 `SILENT=1`；已有合格混音且只改画面时复用声轨。配乐规则见 [音频](references/audio.md)，目标约 -15 至 -16 LUFS、真峰值不超过 -0.5 dB。人脸、音乐、字幕、作品墙缺失时区分可选能力和必要输入，不悄悄替换成虚构用户素材。

Canvas2D 示例使用同一 `renderAt(t)` / `READY` 接口可直接导出；原生 p5.brush 工程可能需要自己的完整画布导出适配器，先核对预览缩放、异步 `redraw()`、纹理和时钟，再按手绘指南导出。遇到 WebGL 长时间运行卡住，可分批重启浏览器，逐帧按序合成；不要忽略失败帧。

1. 看关键帧：主体边界、最长字幕、进入/退出状态。
2. 渲染包含新动作及前后转场的短段，检查准备、主动作、结果与收势。60fps 接点核对连续帧。
3. 验证同时间重复跳转、倒退和重载的一致性。
4. 完整导出到新文件，检查宽高、帧率、总帧数、音视频长度、响度与完整解码。失败不能拼上不明来源的历史缓存。
5. 给成片、工程路径和实际核验范围；静帧检查不写成全片观看。清理本次临时目录，保留用户原件。

## 按需查阅

[引擎与项目地图](references/projects.md) · [手绘续接](references/handdrawn-animation.md) · [视觉系统](references/style.md) · [竖屏布局](references/portrait.md) · [排错](references/troubleshooting.md)。首次使用先跑通 [自带示例](examples/README.md)，不要要求新用户取得作者私人工程。

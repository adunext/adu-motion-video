# adu-motion-video

阿杜Next 的 HTML / JavaScript 动效视频 Skill。把真人口播或新文案编排为标题、卡片、软件窗口、作品墙、双语字幕与声音，并通过本地浏览器逐帧导出 MP4。

A local HTML / JavaScript motion-video skill from AduNext. Author talking-head layouts, kinetic titles, cards, software demos, video walls, bilingual captions and sound, then render frames through Chromium and encode MP4 with FFmpeg.

**MIT 开源、可安装。** 自有工具代码和方法采用 [MIT 许可证](LICENSE)，第三方依赖保留各自许可，详见 [来源与依赖声明](THIRD_PARTY.md)。本包不包含真人素材、头像、音乐、历史成片或字体二进制；不会自动生成新口型、配音或三维素材。

**Open source under MIT and installable.** The toolkit code and documentation use the [MIT License](LICENSE); third-party dependencies retain their own licenses. See [provenance and dependency notices](THIRD_PARTY.md). Personal media, music, historical renders and font binaries are excluded. New voice, lip-sync and 3D generation require separate tools and authorization.

## 安装 / Install

选择一个尚不存在的目标目录，保留已有安装。下面的命令仅获取 Skill 源码；依赖另行准备。

Choose one destination that does not already exist. These commands fetch the skill source; dependencies are installed separately.

**Claude Code**

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/adunext/adu-motion-video.git "$HOME/.claude/skills/adu-motion-video"
```

**Codex**

```bash
mkdir -p "$HOME/.codex/skills"
git clone https://github.com/adunext/adu-motion-video.git "$HOME/.codex/skills/adu-motion-video"
```

也可只保留一份安装，在另一工具的 skills 目录显式创建符号链接。不要覆盖已有同名文件夹或链接。重新开始会话后，在请求中明确写 `$adu-motion-video`，并提供文案、SRT、口播和素材路径。

You may keep a single installation and explicitly link it into the other tool's skills directory. Do not replace an existing folder or link. Start a new session and mention `$adu-motion-video`, together with the script, SRT, talking-head footage and asset paths.

## 依赖 / Requirements

- Node.js 18+、Python 3、FFmpeg / ffprobe，以及已安装的 Chromium 或 Chrome。
- Node dependency: `playwright-core`（版本记录在 lockfile）。音频和对齐工具需要 NumPy；setup 还准备 Pillow、OpenCV 和 SciPy。
- 人脸追踪单独需要 macOS 的 Vision / AppKit 与 Swift 编译器。其余步骤需在目标系统验证；Shell 入口面向 Bash 环境。
- 使用系统可用字体。中文需要已安装的中文字体；不同系统的字形和排版可能不同，必须检查换行和安全区。

Set `SKILL_DIR` to your actual installation. If the required dependencies are missing, run the explicit setup command. **Setup downloads packages. Rendering does not install packages or fetch remote assets.**

```bash
SKILL_DIR="$HOME/.codex/skills/adu-motion-video"   # or the Claude installation
bash "$SKILL_DIR/scripts/pipeline.sh" setup
```

If Chrome is not found, set `CHROME` to an existing browser executable. The strict renderer also accepts `--browser` and `--playwright-module`. No browser binary, virtual environment, `node_modules` or font package is bundled.

## 六秒静音演示 / Six-second silent demo

This small example uses the same scene runtime as the talking-head template and needs no media files. It demonstrates title motion on white, black and blue backgrounds; it is not a talking-head or alignment test.

```bash
node "$SKILL_DIR/scripts/render_project.mjs" \
  "$SKILL_DIR/examples/silent-demo.html" \
  --output "$PWD/adu-demo-6s.mp4" --width 1920 --height 1080 --fps 60
```

输出目录须已存在，目标 MP4 须为新文件。浏览器直接打开页面只显示指定时刻；使用 `?t=2.8` 查看静帧，导出 MP4 查看完整动画。 / The parent directory must exist and the output must be a new file. Opening the HTML displays a still; use `?t=2.8` to inspect a time or render MP4 for motion.

## 制作新片 / Create a video

Read [SKILL.md](SKILL.md) first. Start from the template, supply footage, author scenes for the new script, inspect stills and short segments, then export a new version.

```bash
PL="$SKILL_DIR/scripts/pipeline.sh"
D="$PWD/my-video"                      # new project; parent must exist
bash "$PL" new "$D"
```

The talking-head template requires real local footage. With raw and edited talking-head clips available:

```bash
"$SKILL_DIR/.venv/bin/python" "$SKILL_DIR/scripts/align_talk.py" \
  --master "edited-talk.mov" --raw "raw-01.mov" "raw-02.mov" --out "$D"
# macOS only, optional face tracking:
bash "$SKILL_DIR/scripts/face_track.sh" "$D"
```

Edit `config.js`, `scenes.js`, subtitle groups and `audio.py` for this video's content. `config.js` width/height do **not** automatically reflow fixed scene coordinates. Vertical video needs a separately authored layout; the historical portrait HTML is a reference, not a drop-in converter.

```bash
bash "$PL" stills "$D" 1.2,3.4,5.6
bash "$PL" audio "$D"
bash "$PL" mix "$D" 0.50
bash "$PL" render "$D" "$PWD/my-video-v1.mp4"
bash "$PL" check "$PWD/my-video-v1.mp4"
```

For a silent composition, remove talking-head dependencies and explicitly use `export_project.py --no-audio`. Video-wall sprites use explicit paths:

```bash
python3 "$SKILL_DIR/scripts/prep_wall.py" \
  --manifest videos.json --videos ./videos --output ./wall-sprites
```

The manifest is a JSON array containing unique `slug` values for local `slug.mp4` files. Keep attribution metadata for third-party source media. Configure the resulting sprite paths and wall data in your own project.

## 能力与验证边界 / Scope and verification

- `renderAt(t)` calculates frames from absolute time. Export checks page/resource errors, subprocess failures, final frame count and duration, and decoding. New output paths prevent accidental replacement of an existing render.
- Alignment reports the proportion of distinguishable motion samples whose predicted source frame is within one frame of a local best match. It is not proof of perfect per-frame lip-sync. Historical percentages are not promised performance for a new video.
- Inspect cut points, readable text, face crop, subtitles, audio and final media parameters. A correct still does not establish a correct full video.
- Historical EP02/EP04 code is provided for design patterns. It contains old content, timings and example asset names; adapt those before reuse. Original footage, voices, music and third-party showcase videos are not included.
- No guarantee is made that any model will consistently produce a finished video without creative and technical review.

## 文件 / Files

| Path | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Agent workflow and routing |
| `template/` | Talking-head runtime and editable project skeleton |
| `scripts/` | Alignment, subtitles, face tracking, audio and strict export tools |
| `references/` | Layout, scene API, audio, compatibility and verification guidance |
| `examples/` | Historical code references plus a media-free silent demo |
| [THIRD_PARTY.md](THIRD_PARTY.md) | Provenance, exclusions and dependency notices |

## 本发布包检查 / Release checks

The public copy passed skill-frontmatter validation, Python/JavaScript/Shell syntax checks, local Markdown-link checks and a pattern-based credential/private-path scan. The included silent demo was rendered locally as 1920×1080, 60 fps, 360 decoded frames, 6 seconds, with no audio. The parameterized wall utility produced a 768×432 sprite from a synthetic clip and refused an existing output directory.

These checks do not establish full talking-head alignment, face-tracking accuracy, subjective creative quality or cross-platform equivalence. Real voice/media alignment and macOS face tracking were not rerun for this public packaging.

# 本地导出与检查工具

下列路径相对本 skill 根目录；在其他目录执行时加上安装目录前缀，或沿用 README 的 `SKILL_DIR` / `PL` 变量。所有带空格的路径加引号。优先使用 Python 入口：Windows 原生 `python scripts/pipeline.py 命令`，macOS/Linux `python3 scripts/pipeline.py 命令`。下文 Bash 示例在 Windows 可替换为 Python 的同名命令；直接 Python 工具也以 `python -X utf8` 执行。常规导出不会联网安装工具，Bash/WSL 入口仍可使用。多助手加载与平台差异见[兼容说明](compatibility.md)。

## 第一次使用

```bash
bash scripts/pipeline.sh doctor
# 缺少 Skill 依赖时安装；Node、Python、FFmpeg 和浏览器需预先可用：
bash scripts/pipeline.sh setup
bash scripts/pipeline.sh doctor
bash scripts/pipeline.sh demo '/用户指定目录/首次演示'
```

`doctor` 只读取环境并报告缺项。`demo` 使用随包插画与动作音效，在新目录生成 36 秒演示，明确没有口播和背景音乐；不需要私人媒体。验证成功后，正式项目需接入本次口播、文案和素材并关闭 `CONFIG.demo`。静音独立示例另见 [examples/README.md](../examples/README.md)。

## 工程检查和建新片

```sh
python3 scripts/inspect_project.py '/用户/工程目录'
bash scripts/pipeline.sh new '/本集/新工程目录'
```

盘点是静态线索，不证明素材齐全或实际渲染成功。动态场景需要在浏览器核对。新建目标必须不存在；模板的演示场景是起点，需要填入本条口播与分镜，正式导出前将 `CONFIG.demo` 设为 `false`。

已有剪好的单条口播可以直接导入：

```bash
bash scripts/pipeline.sh import '/本集/新工程目录' '/素材/剪好的口播.mp4'
```

生成 `talk/clip_000/`、`talkmap.js`、48kHz `voice.wav` 和 `import.json`。按报告中的帧率/时长设置配置并关闭演示，再重排场景、进度、字幕和配乐；导入不会改写创意内容。要匹配多条原始拍摄素材时才使用 `align_talk.py`。

首次缺少依赖时显式执行 `scripts/pipeline.sh setup`，不要在常规制作中重新安装。Python 入口自动识别 skill 自带 `.venv/bin/python`（macOS/Linux）或 `.venv/Scripts/python.exe`（Windows）；基础检查和导出编排只用标准库。Playwright 优先查找 skill 自带 `node_modules`，其次已有本机安装；浏览器可显式指定。

## 关键帧与短片段

```sh
node scripts/render_project.mjs '/本集/工程/index.html' \
  --stills-dir '/本集/新审片目录' --times 0,3.8,7.2

node scripts/render_project.mjs '/本集/工程/index.html' \
  --output '/本集/局部审片_v1.mp4' --start 12 --end 15 \
  --audio '/本集/工程/mix.wav' --fps 60 --width 1920 --height 1080
```

截图目录和成片必须是新路径。短片工具只有传 `--audio` 才含声音；完整流程要求提供声音或显式 `--no-audio`。音轨参数表示完整时间轴音轨，短片自动按 start 取对应声音。

当前需要 `window.renderAt(t)` 和 `READY` Promise 或 title=done。Canvas2D 示例实现这个合约即可使用；已有 p5.brush 工程先按 [手绘适配说明](handdrawn-animation.md)核对初始化与真实画布输出，不直接假设它具有相同接口。可等待 `imgWait()` 与字体/图片解码。资源加载失败、脚本异常与编码失败会中止。远程资源和原生 video/audio 元素默认不支持，需先实现确定性适配。

## 完整导出

```sh
python3 scripts/export_project.py '/本集/工程' '/本集/成片_v1.mp4' \
  --audio '/本集/工程/mix.wav' --fps 60 --width 1920 --height 1080

python3 scripts/export_project.py '/本集/工程' '/本集/竖屏_v1.mp4' \
  --html vert.html --audio '/本集/工程/mix.wav' --width 1080 --height 1920
```

等价便捷入口为 `pipeline.sh render PROJECT NEW.mp4` 和 `pipeline.sh vert PROJECT NEW.mp4`。

- 默认5段并行，`--segments N` 可调。END从运行时读取，也可用 `--end SECONDS`；帧数为 round(end×fps)，当前只支持整数fps。
- 所有分段放系统唯一临时目录。每段失败即停止交付，不使用旧 `parts/` 或 `.last_out`。
- 合并后检查可读帧数、尺寸、帧率、时长和应有的声轨，再独占创建新文件；不覆盖旧输出。
- 同目录保存 `成片.mp4.manifest.json`，记录源码指纹和导出规格。它不等于全部媒体都已逐文件哈希，也不证明内容语义正确。
- 声音不足需主动准备补尾混音，不用 `-shortest` 悄悄截掉结尾。纯动效明确传 `--no-audio`。
- 导出中不要修改源文件；片长、字幕、素材与声音变更需一起更新。
- `--optional-data` 仅供已确认不参与当前画面的缺失数据脚本，不能用于忽略实际所需媒体错误。新模板已提供可选数据占位脚本，常规任务无需该选项。

旧版 seg 依赖无来源记录的缓存。新流程不沿用它；局部查看用上面的 start/end。对整片修改采用新文件重渲，当前不承诺缓存分段加速。

## 参数与局限

可通过 `--playwright-module '/已有/node_modules/playwright-core/index.mjs'` 和 `--browser '/浏览器可执行文件'` 指定本地工具。也可通过 `CHROME` 环境变量指定浏览器。查询参数仅在明确了解页面含义时使用；部分旧源码的 `?vert` 会禁用字幕。

改变 width/height 只设置视口，不能自动重排画面。先完成竖屏设计再导出。

`pipeline.sh check FILE.mp4` 检查媒体信息、响度和峰值；它不代替实际画面和声音审查。切点、人物口型和长字幕需看关键帧与短动态片段。检查后如实报告范围。

需要保留旧成片原有声音时，可以额外用 FFmpeg 复制音轨并核对时长与包数据。任意 `-ss -c copy` 不是帧准确视频切割，精确局部拼接需按帧trim或核实关键帧条件。

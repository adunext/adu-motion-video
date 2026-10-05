# 平台、助手与字体兼容

同一份 Skill 支持 Windows、macOS、Linux，可用于 Codex、Claude Code、豆包、DeepSeek、WorkBuddy 等能够读取文件并执行命令的助手。仅对话客户端可以规划，实际构建需要可访问素材的执行环境；不根据助手名称猜测权限或安装目录。

## 命令入口

在实际 Skill 目录运行：

| 平台 | 环境检查 | 安装 Skill 依赖 |
| --- | --- | --- |
| Windows 原生 PowerShell/CMD | `python scripts/pipeline.py doctor` | `python scripts/pipeline.py setup` |
| macOS/Linux | `python3 scripts/pipeline.py doctor` | `python3 scripts/pipeline.py setup` |
| 已有 Bash/WSL | `bash scripts/pipeline.sh doctor` | `bash scripts/pipeline.sh setup` |

三种入口调用同一实现，支持 packs、new、import、macro-plan/build、auto-plan/build、audio、mix、stills、render、check、preview 和可选 repair。推荐字体不属于 doctor 的缺项。Node 18+、Python 3.10+、浏览器及具备所需转换/编码能力的 FFmpeg 是执行工具；setup 安装 Node/Python 包，不安装系统软件。依赖范围由 pip 选择当前 Python/OS 可用的轮子，不强装作者 Python 3.14 的固定版本。

所有包含空格的路径加引号。入口以参数数组调用工具，不让素材路径成为 shell 代码；Windows 使用 `os.pathsep`、Scripts/python.exe 和 UTF-8。旧 Mac 虚拟环境搬到 Windows 时，setup 另建当前系统的环境，不覆盖另一系统环境。Chrome/Chromium/Edge 自动查找，也可设置 CHROME 为浏览器可执行文件；不自动下载浏览器。

WSL 仍可使用，但需要在 WSL 中安装依赖，使用 `/mnt/c/...` 等 WSL 可读路径，不混用原生 Windows 与 WSL 的 Python/浏览器。

## 字体是推荐项

默认 `fontPolicy="preferred"`：优先使用用户提供的有效推荐字体；用户提供不同的有效字体也可使用并记录实际 SHA。没有、损坏或不支持的推荐字体会回退至随包未修改的 Noto Sans SC / Noto Sans Mono，生成的工程包含字体、来源摘要与 OFL 许可证，渲染不依赖联网取字体，不要求安装 PingFang、SF Mono、Geist 或原标题字体。

源字体的指纹保留用于追溯，不作为默认选型/构建前置条件；模板原有 externalFonts.required 是历史提炼元数据。auto-plan 输出 fontWarnings 作为建议；构建记录 font_policy.json 与 macro_build_report.json。只有用户明确要精确字体复刻时才使用 `fontPolicy="exact"`，不能由助手默认开启。

字体替换可能改变字形、字重和行宽。使用实际字体检查中英文字形、断行、标题与字幕安全区；通过短标题、合法换行、布局或合理字号调整解决溢出。推荐字体缺失不等于排版失败；排版实际溢出也不能因已经回退就忽略。少见字符和 Emoji 还须检查实际系统字形，随包字体不宣称覆盖全部 Unicode。

## 人物与素材

macOS 优先使用 Vision/Swift；其他环境使用本地 OpenCV 检测。没有可靠检测结果时使用宽幅固定构图，报告 reviewRequired 和警告，继续保留实际口播帧；检查全段眼睛、嘴巴、下巴及接缝，再调整固定裁切。回退不是身份识别或裁切验收，也不能用旧人物帧补空白。

真实口播、图片、证据视频、字体回退资产、脚本与时间轴必须存在且有效。HDR/DV 沿用色彩探测与核验，不因跨平台改成只写标签。缺少真实媒体、错误数量、素材时长不足或动作窗口装不下仍需要修订输入/分镜。

## 实测与旧工程

本期实测与局限见[3.14 兼容验证](../docs/compatibility-3.14.md)。macOS 验证不等于 Windows 真机已经导出验收，也不作为拒绝 Windows 用户使用的资格限制。字体回退、命令执行、几何检查与真人整片声画分别描述。

旧冻结工程保留自身运行代码，不自动换字体或裁切；升级另存新工程。旧 adu-video-studio 为兼容入口，其 mk/Scene/update 合同不同，不能混装运行时。Canvas/p5 同样须等待实际字体、图片与纹理就绪，见[手绘方法](handdrawn-animation.md)。

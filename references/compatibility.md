# 兼容与验证边界

## 同一份 skill

同一份 Skill 可在 Windows、macOS、Linux 使用，支持 Codex、Claude Code、豆包、DeepSeek、WorkBuddy 等助手。接入方式取决于当前助手环境提供的文件与命令能力。

## 平台与助手接入

| 助手 | 接入方式 |
| --- | --- |
| Codex / Claude Code | 安装到对应的 skills 目录，加载 `SKILL.md`；也可显式读取仓库 |
| 豆包 / DeepSeek / WorkBuddy | 有 Skill 机制时加载本仓库；否则将仓库放入可读取的工作区，让助手先读 `SKILL.md` 和 `AGENTS.md` |
| 其他助手 | 能读取说明、读写素材并执行命令，即可沿用通用 Agent 入口 |

助手名称不等于执行能力：仅能对话的客户端可协助规划，自动生成工程和导出需要连接可访问素材的命令执行环境。不要编造未确认的安装目录、插件接口或本地权限。

| 平台 | 当前命令接入方式 |
| --- | --- |
| Windows | 通过 WSL 使用 Bash；在 WSL 内安装和运行 Node、Python、FFmpeg、Chrome/Chromium 与 Skill 依赖 |
| macOS | 使用 Bash 和本机依赖；可选 Vision 人脸跟踪需要 Swift |
| Linux | 使用 Bash 和本机依赖；人物窗可配置经审核的固定裁切 |

Windows 的 `C:\素材` 在 WSL 中通常为 `/mnt/c/素材`；仓库、素材和输出都使用命令执行环境可访问的路径。WSL 流程不直接套用 Windows 原生命令、Python 虚拟环境或浏览器路径。原生 PowerShell/CMD 的完整命令链尚未验收。所有含空格的路径都加引号。

更换平台先运行 `doctor`，再核对浏览器、字体、素材裁切、HDR/SDR 色彩和最终声音。Vision 自动跟踪只适用于 macOS；需要人物窗的包在其他平台显式配置审核过的 `faceTracking:{mode:"fixed",cx,cy,h}`，不可把缺少 Vision 当作整个 Skill 不支持该平台。包使用 macOS 系统字体时，其他平台按该包说明提供有使用权的替代字体。

既有 macOS 验收记录保留为实际证据；平台支持与特定系统上的声画验收分别记录，不将历史环境写成使用资格限制，也不把接入说明当作 Windows/Linux 已完成整片验收。

Codex 与 Claude Code 可分别安装，也可显式创建符号链接共享同一目录；不要覆盖现有安装。依赖和媒体不会由符号链接自动搬运。

旧 `adu-video-studio` 保留为兼容入口。其最小无声 starter 是此前的独立验证样例，不是本口播模板的第二套默认实现。

## 运行时不可混装

| 项目 | DOM/SVG 口播模板 | 旧 studio 最小 starter |
|---|---|---|
| mk | mk(parent, html, x, y, opt) | mk(parent, className, x, y, width, height) |
| show | show(element, t, t0, opt) | show(element, t, at, duration, distance) |
| Scene | Scene(start, end, bg, opt) | Scene(start, end, theme) |
| update 的 t | 全片绝对时间 | 场景局部时间 |

Canvas/p5 还需要等待画笔、字体与纹理初始化，并按实际输出画布取帧；不能把 DOM 的 `mk/Scene` 函数直接搬进画布绘制。见 [handdrawn-animation.md](handdrawn-animation.md)。

同一个场景要匹配整套运行时。复用视觉配方时改写签名和时间，不把函数文件机械拼接。

## 对齐指标

`align_talk.py` 从 1.0 / 1.05 / 1.1 / 1.15 / 1.2 选择全片共同速度，不能宣称任意逐段变速识别。验证比例来自有运动辨识度的采样点：预测帧与局部最佳匹配帧误差不超过一帧。它不包含每一帧，也不验证所有字幕、声音或切点。

每个新项目都要保存实际对齐日志与抽查结果。过去某条视频的匹配率或倍速不能作为新素材的保证，也不能把少量采样通过说成整片逐帧验证。

## 可选数据与媒体

- 没有字幕数据可以关闭字幕，不代表带字幕交付已完成。
- 没有人脸轨迹时固定中心裁切；这是默认位置，不是人脸追踪。
- 没有 TALKMAP 时仍需模板所用的 talk 图片序列。纯动效片需移除人物依赖。
- 没有 WALL 时不要调用作品墙组件。缺失实际图片、字体或脚本是错误，不统一当作可选文件忽略。
- 新工程可生成空的可选数据脚本以保证入口可加载，作者仍需按画面所用组件补齐素材。
- Vision 人脸追踪依赖 macOS；其它阶段另行验证目标系统、字体与浏览器。

## 尺寸与示例

`config.js` 的宽高不会自动重排绝对坐标。横竖屏各自检查正文、人物、字幕、安全区和片尾。

`examples/` 是提炼的场景/声音/字幕/竖屏源码，不包含完整原始媒体。结构与可运行范围见 [projects.md](projects.md)。不要把本地字体、照片和网络作品自动当作可分发资产。

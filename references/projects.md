# 工程结构与示例地图

公开包包含可运行的最小示例、通用制作模板、以及用于学习动作的源码配方。源码配方不包含原始人物、录屏、音乐或完整历史成片；新用户不需要寻找维护者的旧视频目录。

## 先找适合自己的入口

| 目的 | 入口 | 已提供什么 | 仍需什么 |
| --- | --- | --- | --- |
| 验证本机能否渲染 | `examples/silent-demo.html` | 无私人素材的图文动态示例 | 本地渲染依赖 |
| 看字幕差异 | `examples/subtitle-options.html` | 两种字号、长句与避让示例 | 本地浏览器；导出需渲染依赖 |
| 新建真人口播项目 | `template/` + `scripts/pipeline.sh new` | 共享 DOM/SVG 运行时、初始场景和音频/字幕工具 | 用户口播、文案及按内容重新设计的分镜 |
| 学习实拍卡片与对比 | `examples/card-layout-scenes.js` | 卡片换位、时间线、节点、数字、终端与评论等场景配方 | 匹配的运行时、所引用媒体以及新时间表 |
| 学习展陈与重点放大 | `examples/showcase-scenes.js` | 多格展示、作品墙、窗口、主卡放大、镜头与片尾配方 | 所引用媒体、字体、字幕和新时间表 |
| 制作手绘角色动画 | [手绘动画方法](handdrawn-animation.md) | 角色/道具动作、同镜头续接与验证方法 | 新角色设计；复杂画笔项目需要匹配其 Canvas/p5 依赖 |

`examples/README.md` 区分可直接打开的示例与需要适配的源码。显示的比较、评论、计数均为示意内容，不是测试结论，也不应直接带入用户成片。

## DOM/SVG 项目

```text
index.html + style.css     舞台、字体和组件样式
config.js                 品牌、画幅、时长与字幕选项
lib.js                    图层、缓动、Scene、SFX、素材帧加载
scenes.js                 本条视频的分镜、布局、动作与音效时间
main.js                   renderAt(t)、镜头、转场与 READY
subtitles.js + subs.js     字幕绘制与当前口播数据
audio.py + sfx.json        配乐/音效及声音落点
assets / talk / sc         图像、口播与录屏帧
```

主要画面由 DOM/CSS 与 SVG 组成；真人/视频常以 JPEG 序列嵌入。它不是 AE、剪映、Remotion 或 HyperFrames 原生工程。浏览器负责绘制，由编码助手根据内容组织场景。

共享接口是 `renderAt(t)`。`Scene(start,end,bg,opt)` 注册全局时间区间，`sc.update(t)` 接收**全片绝对秒数**。`mk/place/show/words/wordsAt` 创建并更新图层。旧 `adu-video-studio` starter 的 update 接收局部时间，不能直接混装；见 [compatibility.md](compatibility.md)。

`talkmap.js` 把输出帧映射到人物来源帧；`face.js` 提供脸部中心与高度；`wall.js` 索引作品墙；`subs.js` 是实际字幕数据。源 SRT 只有经过生成工具或当前工程显式读取才生效，不能只改一个没有被读取的字幕文件。

## Canvas/p5 项目

保留已工作的画布、画笔纹理、随机种子与绘制顺序。常见结构为 `studio.html`、`src/core.js`、`src/scenes/`、配置、字幕层及本地媒体。具体接口由工程决定，不假定它具备 DOM 模板的 `READY`、`window.END` 或图层选择器。

导出需要等待字体、纹理和画笔初始化，按输出整数帧调用确定性绘制，并从真正的输出画布取图。页面预览可能经过 CSS 缩放，直接截图预览区域会得到错误尺寸。接入与续镜检查见 [handdrawn-animation.md](handdrawn-animation.md)。

## 复用源码前检查

- 配方文件可能包含同名共享函数。按当前 `lib.js` API 适配后删去重复定义，不机械拼接整文件。
- 所有秒数、来源帧数、音量曲线、人物裁切都只服务示例长度，不能作为新口播的对齐数据。
- 字体、CSS 背景图与所有实际可见媒体需要加载成功。系统字体不能未经许可重新打包。
- 旧 renderer 中的浏览器路径、临时音轨和缓存不可直接沿用。优先使用 [导出工具](tooling.md)，独立保存新版，遇到错误停止导出。
- 横竖屏分别安排正文、人物、字幕与片尾；只修改编码尺寸不能完成布局适配。
- 新交付的验证记录只证明这次生成结果，不沿用某个历史工程的通过结论。

# examples
- `ep04_claude_opus55_scenes.js`：EP04 最终版（v7，108.4s），9 个场景 + 双语字幕 + 竖屏开关
- `ep04_audio.py`：EP04 的配乐（用户配乐 + ENV + 效果音）
- `ep04_subs_src.py`：双语字幕分组的写法
- `ep04_vert.html`：竖屏 9:16 外壳
- `ep02_huan_mac_scenes.js`：EP02「换 Mac」V3（用户评价"非常棒"），12 个场景
本目录仅包含历史源码片段；完整工程、人物照片、视频帧和音乐不随公开包分发。`assets/presenter.png` 与 `assets/app-logo.png` 等均是待用户提供的示例路径。
注意：examples 里的 scenes.js 依赖当时那一版的 lib（顶部还有 camCard 等本地定义）。现在这些都已并入 template/lib.js，复用时核对 API、时间语义与媒体依赖，再删除重复定义。

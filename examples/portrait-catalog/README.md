# 九风格竖屏布局预览

这是开发检查用的占位素材预览。用真实 macro runtime 播放 29 个完整组，保留原动作时间；人物和证据均为自制 SVG，占位页没有原口播声音或私人影片。

在仓库根目录执行：

```bash
python3 tests/portrait_fixture.py /不存在的预览目录 --gallery
python3 -m http.server 8913 --bind 127.0.0.1 --directory /预览目录
```

浏览生成目录的 index.html。一次只运行当前模板，可切换完整组、播放和拖动时间线。demo-media.js 的图片替换只存在于此检查页；正式 build/import/export 不加载它。字体检查使用本机系统字体，预览不证明所选外部字体、真人裁切或新文案整片声画验收。独立导出的 01-A 技术样片不由此生成器制作。

生成目录由调用者选择并负责清理，不要放在用户项目容器根目录。

# 纸面小球的已审查契约适配

此适配器只接受来源修订 `1d9087a4b3eb01c18a2e7960dfa2a2eaaa047257e03d5aebb6ca882fd063f753` 的四个固定代码文件 SHA，并检查 Acorn 得到的已审查源码跨度。不是通用 `scene()` 引擎转换器，也不扩展旧 paper-balance 适配器的来源白名单。

完整来源使用 35 个 `scene(..., callback)`、Canvas 和全局粒子/人物状态。选择回调 13，以及保持连续的 30/31：生成 `cards-to-network` 与 `calendar-to-delivery` 两个独立闭包。每个闭包携带原 helper、人物位姿序列、画布特效、主线小球与完整回调。原元素 ID 种子分别为 116/281；初始化不能重置为零。两个入口的源边界 carry 经记录为空，出现不同 carry 会拒绝。

适配只改变宿主与节点作用域、输出口播/字幕/角标时钟、动作 SFX 的收集、结论划线的替换字数和安全文字构造。原 SVG、物理、运动参数与因果关系保留。`fonts_ready.js` 按源 READY 提前请求六种字体；不能等隐藏场景出现后才载字体，否则缓存的字宽可能来自替代字体。

私人来源登记和运行状态 inventory 仍由所有者保存。调用：

```bash
python3 adapters/paper-ball/extract.py SOURCE_RECORD REVIEWED_INVENTORY.json NEW_PACK --version 0.1.3-candidate
```

`SOURCE_RECORD` 是登记目录，`REVIEWED_INVENTORY.json` 包含固定源码哈希、35 个 Acorn 单元及同修订源运行中的元素 ID/边界 carry。输入不会随公共包分发。提炼器不执行来源脚本，也不复制所有者人物、新闻、往期作品、生成插图或音乐。

优设标题黑的源字节不在公共包内。官方页面说明其免费商用，见 [优设说明](https://www.uisdc.com/uisdc-first-free-font)；公开再分发/应用内嵌条款未据此推定。构建者通过 `externalFontFiles.title` 显式提供已审查字体，构建器固定摘要并复制到其私人新工程。OFL 字体及完整通知延续已审查来源。

0.1.3-candidate 的同内容控制包含原人物、原裁切、原字幕、原 24fps 角标和源最终成片的无人声声轨；新内容演示使用不同原声、字段和字幕，不能把两种证明混在一起。人物图片请求加入宿主 `imgWait` 队列。两个完整组仍待作者连续声画确认与安装记录，未晋级稳定，也不把完整 35 场来源一起晋级。

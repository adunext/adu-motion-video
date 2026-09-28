# 踩过的坑

## 口型
- **症状**：前半段口型对得上，后半段慢 1–2 帧。**原因**：分段渲染的起止时间没落在整帧上。**解决**：render.mjs 用整数帧索引 `(f0+i)/fps`；pipeline 的分段按 `round(END*60*i/K)` 帧切。
- **症状**：所有段都慢 2–3 帧（约 40ms）。**原因**：用 stream start_time 当音画偏移。**解决**：align_talk.py 用画面逐帧比对来求每段的视频偏移。
- **症状**：某一段对不上。看 align_talk 输出的 median r：低于 0.85 通常是这段口播用了别的原片，或者剪辑时加了变速。先用 `--speed` 固定倍速重跑，再检查 `--raw` 是否漏了某段原片。
- 验证时 30fps 原片放到 60fps 输出，相邻两帧本来就是同一张图，所以 ±1 帧属于正常。

## 渲染
- **`-shortest` 会截掉结尾**：mix.wav 比视频短几十毫秒就会少 2 帧。一律用 `-af apad -t <END>`。
- **Chrome 截图在大量图片时变慢**：精灵图（4×4 一张）比 16 张单独的图快很多；作品墙 389 格就是这样做的。
- **数据文件缺失报 ERR_FILE_NOT_FOUND**：可选数据（talkmap/face/subs/wall.js）不存在时会出现，render.mjs 已经过滤掉这类报错，属于正常。
- **圆形转场在旧画面上留下一个白点**：main.js 里圆刚出现时透明度要是 0（`Math.min(1-q, clamp(p*25))`）。
- **ffmpeg 没有 drawtext/subtitles**：所有文字都在 HTML 里画。

## 布局
- 字幕区 y 870–1040：大卡片缩到 .9 并上移到 y 505，九宫格和窗口也要缩小。
- 缩放的元素在"弹入"时可能会扫过口播卡片：把放大倍数调小（1.0–1.3），或者把标题放在左半屏。
- 在 `show()` 之后又用 `place()` 改缩放会覆盖 show 的效果：要缩放就用 show 的 `s` 参数。

## 封面
```js
await p.evaluate(()=>{ window.OVERLAY=null; document.getElementById('ov').style.display='none'; });
// 用 deviceScaleFactor:2 截图得到 3840×2160
// 只要作品墙、不要文字：把当前场景里除了墙和网格以外的子元素都设成 visibility:hidden，墙的格子 opacity 设为 1
```

## 其他
- 生成 GitHub 网页截图、下载素材时，用户要求"全部"就要检查数量是否有更新（EP04 时作品从 282 条涨到 389 条）。
- 事实类内容（发布日期、持股比例、显存）不确定时标"待核实"，不要编造。

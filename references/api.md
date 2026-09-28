# lib.js API 速查

## 基础
| 函数 | 说明 |
|---|---|
| `clamp(x,a=0,b=1)` `lerp(a,b,x)` `pr(t,a,b)` | pr = t 在 [a,b] 区间里的进度（0–1） |
| `EZ.out/out5/expo/inout/in/back/spring` | 缓动函数，spring 带苹果风的回弹 |
| `mk(parent, html, x, y, {ax,ay,cls,style})` | 创建绝对定位元素；ax/ay 是锚点（0–1） |
| `place(e,{x,y,s,sx,sy,r,o,blur})` | 设置位置、缩放、旋转、透明度、模糊 |
| `show(e,t,t0,{k,d,out,od,dist,s,x,y,o})` | 入场加出场：k=up/down/left/right/pop/zoom/slam/blur/mask；out=出场时刻 |
| `words(parent,[{h,t,k,d,st}],x,y,cls,{style,ax})` + `wordsAt(e,t,{out})` | 逐词出现；h 末尾加 `<br>` 换行；st 是这个词的样式 |
| `counter(t,t0,t1,v0,v1)` `fmt(n)` | 数字滚动、千分位格式 |
| `shake(t,t0,dur,amp)` → [sx,sy] | 画面震动 |
| `hopIn` `bob` `breathe` | 卡通人物用的小动作 |

## 场景
```js
const sc = new Scene(t0, t1, '#0A0A0A' | 'var(--paper)' | 'var(--blue)', { grid:'grid'|'gridD'|'gridB', trans:'wipe'|'circle'|'flash'|'blur', td, tc, fa, cx, cy });
const tag = tags(sc, '// 02 — 名称', '', dark);   // 左上角标签 + 右上角时间码；在 update 里调用 tag(t)
sc.update = t => { ... };
sc.cam = t => ({ x:960, y:540, z:1.02, sx, sy });  // 整个画面的镜头（推拉、震动）
```

## 口播与素材
| 函数 | 说明 |
|---|---|
| `camCard(parent,w,h,label?,round?)` + `camAt(e,t,{x,y,s,o})` | 口播卡片；round=true 是小圆圈，会按人脸自动居中 |
| `e._sm = 0..1` | 让方卡在缩小的过程中也逐步按人脸居中（大卡缩成小卡时用） |
| `faceAt(t)` → {cx,cy,h} | 当前帧的人脸位置 |
| `talkSrc(t)` | 当前帧对应的口播图片路径 |
| `vtile(parent,w,h,r,extra)` → e._img | 视频卡片；每帧 `setFrame(e._img, seqAt('dir', n, fps, t, t0, loop))` |
| `macWin(parent,w,h,titleHtml)` | macOS 窗口外框（软件录屏用） |
| `buildWall(parent,cols,tw,th,gap)` + `wallTick(w,t,t0)` | 作品墙（精灵图来自 prep_wall.py；WALL 定义在 wall.js） |
| `race(parent,dark)` + `raceAt(e,t,o)` | 底部赛道进度线（段落来自 CONFIG.race） |
| `seqAt(dir,n,fps,t,t0,loop=true)` | 序列帧 `sc/<dir>/f_0001.jpg` |

## 音效
`S(t, type, gain=1, pan=0, {d, n})`：d = 持续时长（typing、counter、ff 这类会用到），n = 变体。
可用类型（68 种）：
achieve, agent, alert, bleeps, boing, bsod, bubble_pop, card, check, chime, chirp, click, clock, coin, counter, crack, crash, creak, crt, ding, dissolve, dock, enter, err, fall, ff, fill, fill_up, flap, game_bleeps, glitch, hdd, hit, hum, jump, key_thock, land, levelup, marker, msg, notif, peck, pop, powerdown, record_scratch, rep, rise, rise_s, scroll, shine, slash, slide, snore, sparkle, squawk, stamp, steps, suck, swipe, swoosh, thud, tick, tick_run, type, typing, whoosh, win_pop, write

常用搭配：元素弹出 → pop/card/swipe；强调词 → hit；划掉 → slash；盖章 → stamp；打勾 → check(n)；数字滚动 → counter(d)；转场 → whoosh；高潮 → hit+crash；打字 → typing(d)；回车 → enter；开关 → click+ding。

## 全局
- `window.END`（默认取 CONFIG.end）
- `window.OVERLAY = t => {}`：每帧最后调用，字幕层就是通过它实现的
- URL 带 `?t=12.3` 打开时直接定位到这一秒；`renderAt(t)` 由 render.mjs 调用

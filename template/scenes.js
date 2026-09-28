/* ============================================================
   scenes.js — 每集的画面。一个 IIFE = 一个场景。
   这是起始模板，只有 3 个示例场景，演示最常用的写法。完整参考见 examples/：
     ep04_claude_opus55_scenes.js  (白/蓝/黑三底色 + 九宫格 + 作品墙 + 软件窗口 + 片尾提示词卡)
     ep02_huan_mac_scenes.js       (实拍口播卡片 + 知识点动效)
   规则：
   - 时间一律用“口播秒数”。口播中间插入展示段时，用 EP03 的 O()/vT() 做时间映射
   - 每个场景：new Scene(开始, 结束, 底色, {grid, trans}) → 在 sc.el 里 mk()/words() 建元素 → sc.update=t=>{...} 按时间摆放
   - 音效：在元素出现的那一刻写 S(时间, '类型', 音量, 声像)，由 audio.py 合成（类型见 references/api.md）
   ============================================================ */
window.END = CONFIG.end;

/* ---------- S1 开场：大标题左 + 口播卡片右（第一帧就有口播） ---------- */
(() => {
  const T0 = 0, T1 = 6;
  const sc = new Scene(T0, T1, 'var(--paper)', { grid: 'grid' });
  const tag = tags(sc, '// 01 — 开场');
  const cam = camCard(sc.el, 470, 836);
  const t1 = mk(sc.el, `<div style="font:700 150px -apple-system,'PingFang SC';letter-spacing:-4px;line-height:1">第一行标题</div>`, 690, 330, { ax: .5, ay: .5 });
  const t2 = mk(sc.el, `<div style="font:800 190px -apple-system,'PingFang SC';letter-spacing:-6px;line-height:1">第二行<span style="color:var(--blue)">重点</span></div>`, 690, 560, { ax: .5, ay: .5 });
  const R = race(sc.el, false);
  sc.update = t => {
    tag(t);
    camAt(cam, t, { x: 1570, y: 510, s: .9 * (.94 + .06 * EZ.spring(pr(t, 0, .45))) });
    const p1 = pr(t, 0, .28), p2 = pr(t, 1.2, 1.46);
    place(t1, { s: 1 + 1.0 * (1 - EZ.out5(p1)), o: clamp(p1 * 4), blur: (1 - EZ.out5(p1)) * 14 });
    place(t2, { s: 1 + 1.3 * (1 - EZ.out5(p2)), o: clamp(p2 * 4), blur: (1 - EZ.out5(p2)) * 16 });
    raceAt(R, t);
  };
  sc.cam = t => { const [sx, sy] = shake(t, 1.2, .3, 16); return { x: 960, y: 540, sx, sy }; };
  S(0, 'hit', .9); S(1.2, 'hit', 1);
})();

/* ---------- S2 黑底：左侧逐词大字 + 右上角小圆口播 + 卡片依次滑入 ---------- */
(() => {
  const T0 = 6, T1 = 14;
  const sc = new Scene(T0, T1, '#0A0A0A', { grid: 'gridD', trans: 'flash', td: .3, fa: .35 });
  const tag = tags(sc, '// 02 — 论点', '', true);
  const cam = camCard(sc.el, 250, 250, '', true);
  const h = words(sc.el, [{ h: '关键的', t: 6.3 }, { h: '一句话。', t: 6.8, k: 'slam', st: 'color:#6d9bff' }], 146, 260, 'h1', { style: 'color:#fff' });
  const cards = ['要点一', '要点二', '要点三'].map((s, i) => mk(sc.el, `<div class="dcard" style="width:480px;height:150px"><div class="lb">// 0${i + 1}</div><div style="position:absolute;left:28px;top:66px;font:600 44px -apple-system,'PingFang SC'">${s}</div></div>`, 146 + i * 510, 560));
  const R = race(sc.el);
  sc.update = t => {
    tag(t);
    camAt(cam, t, { x: 1745, y: 180, o: EZ.out(pr(t, T0, T0 + .4)), s: .75 });
    wordsAt(h, t, { out: T1 - .35 });
    cards.forEach((c, i) => show(c, t, 8 + i * .5, { k: 'right', out: T1 - .35 }));
    raceAt(R, t);
  };
  S(T0, 'whoosh', .6); S(6.8, 'hit', .8); [0, 1, 2].forEach(i => S(8 + i * .5, 'card', .5, -.4 + i * .4));
})();

/* ---------- S3 蓝底：数字滚动 + 进度条 ---------- */
(() => {
  const T0 = 14, T1 = CONFIG.end;
  const sc = new Scene(T0, T1, 'var(--blue)', { grid: 'gridB', trans: 'wipe', tc: '#2462EA' });
  const tag = tags(sc, '// 03 — 数据');
  const cam = camCard(sc.el, 250, 250, '', true);
  const num = mk(sc.el, `<div class="mono" style="font-size:180px;font-weight:700;color:#fff">0</div>`, 146, 300);
  const R = race(sc.el);
  sc.update = t => {
    tag(t);
    camAt(cam, t, { x: 1745, y: 180, s: .75 });
    show(num, t, 14.3, { k: 'up' }); num.firstChild.textContent = fmt(counter(t, 14.4, 16, 0, 12345));
    raceAt(R, t);
  };
  S(14.3, 'counter', .4, 0, { d: 1.6 }); S(16, 'ding', .6);
})();

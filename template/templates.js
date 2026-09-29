/* ============================================================
   templates.js — 阿杜审美精选动效模板。一个函数 = 一个完整场景。
   用法（scenes.js）：TPL.hero({ t0: 0, t1: 5, lines: [['把想法', .0], ['做成*画面*', 1.2]] })
   - 时间全部是全片绝对秒数（口播时钟）。每句话的 at 取字幕/SRT 的起始时间。
   - 文字里 *xx* 会变成科技蓝强调色。
   - cam: 'right' 右侧大口播卡 | 'corner' 右上角小圆 | 'none' 不放人
   - 每个模板自带音效 S()，由 audio.py 合成。参数表见 references/templates.md
   ============================================================ */
const TPL = {};
(() => {
  const A = s => String(s).replace(/\*(.+?)\*/g, '<span style="color:var(--blue2)">$1</span>');
  const AL = s => String(s).replace(/\*(.+?)\*/g, '<span style="color:var(--blue)">$1</span>');
  const BG = { paper: 'var(--paper)', ink: '#0A0A0A', blue: 'var(--blue)' };
  const GRID = { paper: 'grid', ink: 'gridD', blue: 'gridB' };
  const FONT = "-apple-system,'SF Pro Display','PingFang SC',sans-serif";

  function base(o, def) {
    const theme = o.bg || def.bg;
    const sc = new Scene(o.t0, o.t1, BG[theme], { grid: GRID[theme], trans: o.trans === undefined ? def.trans : o.trans, tc: BG[theme] === 'var(--blue)' ? '#2462EA' : BG[theme] });
    const tag = tags(sc, o.tag || def.tag || '', '', theme === 'ink');
    const hasRace = CONFIG.race && CONFIG.race.keys && CONFIG.race.keys.length > 2 && o.race !== false;
    const R = hasRace ? race(sc.el, theme !== 'paper') : null;
    const camMode = o.cam || def.cam || 'corner';
    let cam = null;
    if (camMode === 'right') cam = camCard(sc.el, 470, 836);
    if (camMode === 'corner') cam = camCard(sc.el, 250, 250, '', true);
    const tick = t => {
      tag(t); if (R) raceAt(R, t);
      if (camMode === 'right') camAt(cam, t, { x: 1570, y: 510, s: .9 * (.94 + .06 * EZ.spring(pr(t, o.t0, o.t0 + .45))) });
      if (camMode === 'corner') camAt(cam, t, { x: 1745, y: 180, s: .75 * (.8 + .2 * EZ.spring(pr(t, o.t0, o.t0 + .5))), o: EZ.out(pr(t, o.t0, o.t0 + .3)) });
    };
    if (def.whoosh !== false && o.t0 > 0) S(o.t0, 'whoosh', .5);
    return { sc, tick, theme, textX: camMode === 'right' ? 690 : 960, out: o.t1 - .35 };
  }

  /* 01 开场大标题：第一句砸入 + 闪屏 + 震动，右侧口播卡（第一帧就有人） */
  TPL.hero = o => {
    const b = base(o, { bg: 'paper', tag: '// 01 — 开场', cam: 'right', trans: null, whoosh: false });
    const n = o.lines.length, gap = n > 1 ? 230 : 0;
    const L = o.lines.map(([s], i) => mk(b.sc.el, `<div style="font:800 ${i === n - 1 ? 190 : 150}px ${FONT};letter-spacing:-6px;line-height:1">${AL(s)}</div>`, b.textX, 540 - gap * (n - 1) / 2 + i * gap, { ax: .5, ay: .5 }));
    const sub = o.sub ? mk(b.sc.el, `<div class="tag" style="font-size:26px">${o.sub}</div>`, b.textX, 900, { ax: .5 }) : null;
    b.sc.update = t => {
      b.tick(t);
      L.forEach((e, i) => { const at = o.lines[i][1], p = pr(t, at, at + .28), q = 1 - EZ.out5(p); place(e, { s: 1 + (1 + i * .3) * q, o: clamp(p * 4), blur: q * 15 }); });
      if (sub) show(sub, t, o.lines[n - 1][1] + .6, { k: 'up' });
    };
    b.sc.cam = t => { let sx = 0, sy = 0; o.lines.forEach(([, at]) => { const [a, c] = shake(t, at, .3, 16); sx += a; sy += c; }); return { x: 960, y: 540, sx, sy }; };
    o.lines.forEach(([, at], i) => S(at, 'hit', .85 + i * .1));
  };

  /* 02 论点：逐词大字 + 依次滑入的要点卡 */
  TPL.point = o => {
    const b = base(o, { bg: 'ink', tag: '// 02 — 论点', trans: 'flash' });
    const dark = b.theme !== 'paper';
    const h = words(b.sc.el, o.words.map(([s, at, k]) => ({ h: A(s), t: at, k })), 146, 230, 'h1', { style: dark ? 'color:#fff' : '' });
    const W = Math.min(520, (1628 - 30 * ((o.cards || []).length - 1)) / Math.max(1, (o.cards || []).length));
    const cards = (o.cards || []).map(([s], i) => mk(b.sc.el, `<div class="${dark ? 'dcard' : 'card'}" style="width:${W}px;height:170px"><div class="lb">// 0${i + 1}</div><div style="position:absolute;left:28px;top:72px;font:600 46px ${FONT}">${AL(s)}</div></div>`, 146 + i * (W + 30), 600));
    b.sc.update = t => { b.tick(t); wordsAt(h, t, { out: b.out }); cards.forEach((c, i) => show(c, t, o.cards[i][1], { k: 'right', out: b.out })); };
    o.words.forEach(([, at, k]) => k === 'slam' && S(at, 'hit', .8));
    (o.cards || []).forEach(([, at], i) => S(at, 'card', .5, -.4 + i * .4));
  };

  /* 03 数字滚动：大数字 + 单位 + 说明 + 进度条填满 */
  TPL.number = o => {
    const b = base(o, { bg: 'blue', tag: '// 03 — 数据', trans: 'wipe' });
    const fg = b.theme === 'paper' ? 'var(--ink)' : '#fff';
    const lab = mk(b.sc.el, `<div style="font:600 56px ${FONT};color:${fg};opacity:.85">${o.label || ''}</div>`, 146, 250);
    const num = mk(b.sc.el, `<div class="mono" style="font-size:230px;font-weight:700;color:${fg};letter-spacing:-8px"><span>0</span><span style="font-size:90px;letter-spacing:0;margin-left:18px">${o.unit || ''}</span></div>`, 140, 330);
    const bar = mk(b.sc.el, `<div style="width:1200px;height:14px;border-radius:7px;background:rgba(255,255,255,.2);overflow:hidden"><div style="height:100%;width:100%;background:${b.theme === 'blue' ? '#fff' : 'var(--blue)'};transform-origin:0 50%"></div></div>`, 146, 640);
    const sub = o.sub ? mk(b.sc.el, `<div style="font:500 40px ${FONT};color:${fg};opacity:.75">${A(o.sub)}</div>`, 146, 700) : null;
    const d = o.dur || 1.6, at = o.at;
    b.sc.update = t => {
      b.tick(t); show(lab, t, at - .3, { k: 'up', out: b.out }); show(num, t, at, { k: 'up', out: b.out }); show(bar, t, at, { k: 'up', out: b.out });
      num.firstChild.firstChild.textContent = (o.fmt || fmt)(counter(t, at, at + d, o.from || 0, o.value));
      bar.firstChild.firstChild.style.transform = `scaleX(${EZ.out(pr(t, at, at + d)) * (o.fill == null ? 1 : o.fill)})`;
      if (sub) show(sub, t, at + d, { k: 'up', out: b.out });
    };
    S(at, 'counter', .4, 0, { d }); S(at + d, 'ding', .6);
  };

  /* 04 对比：左边旧做法被划掉 + 盖章，右边新做法亮起 */
  TPL.compare = o => {
    const b = base(o, { bg: 'paper', tag: '// 04 — 对比', cam: 'none', trans: 'circle' });
    const col = (side, blue) => mk(b.sc.el, `<div class="card" style="width:760px;height:600px;${blue ? 'background:var(--blue);color:#fff;border:none' : ''}"><div class="lb" style="${blue ? 'color:rgba(255,255,255,.7)' : ''}">// ${blue ? 'after' : 'before'}</div><div style="position:absolute;left:44px;top:80px;font:700 70px ${FONT}">${side.title}</div>${side.items.map((s, i) => `<div style="position:absolute;left:44px;top:${210 + i * 90}px;font:500 42px ${FONT};opacity:${blue ? 1 : .6}">${blue ? '→ ' : '· '}${s}</div>`).join('')}</div>`, 0, 0, { ax: .5, ay: .5 });
    const L = col(o.left, false), Rt = col(o.right, true);
    L._x = 530; L._y = 560; Rt._x = 1390; Rt._y = 560;
    const strike = mk(b.sc.el, `<div style="width:700px;height:10px;background:#E5484D;border-radius:5px"></div>`, 180, 560, { ay: .5 });
    const stamp = o.stamp ? mk(b.sc.el, `<div style="border:8px solid #E5484D;color:#E5484D;border-radius:18px;padding:6px 34px;font:800 96px ${FONT}">${o.stamp}</div>`, 530, 560, { ax: .5, ay: .5 }) : null;
    const [la, ra, sa] = [o.leftAt, o.rightAt, o.strikeAt];
    b.sc.update = t => {
      b.tick(t);
      show(L, t, la, { k: 'left', out: b.out }); show(Rt, t, ra, { k: 'right', out: b.out, s: 1 + .03 * EZ.spring(pr(t, ra, ra + .6)) });
      const p = EZ.out5(pr(t, sa, sa + .25)); place(strike, { sx: p, o: p > 0 ? 1 - pr(t, b.out, b.out + .3) : 0, r: -8 });
      if (stamp) show(stamp, t, sa + .35, { k: 'slam', r: -12, out: b.out });
    };
    b.sc.cam = t => { const [sx, sy] = shake(t, sa + .35, .3, 12); return { x: 960, y: 540, sx, sy }; };
    S(la, 'card', .5, -.5); S(ra, 'card', .6, .5); S(sa, 'slash', .7); if (stamp) S(sa + .35, 'stamp', .9);
  };

  /* 05 步骤：横向时间线逐段点亮（知识讲解、教程） */
  TPL.steps = o => {
    const b = base(o, { bg: 'paper', tag: '// 05 — 步骤', trans: 'wipe' });
    const dark = b.theme !== 'paper', n = o.steps.length, X0 = 200, X1 = 1720, gx = (X1 - X0) / Math.max(1, n - 1);
    const title = mk(b.sc.el, `<div class="h2" style="${dark ? 'color:#fff' : ''}">${AL(o.title || '')}</div>`, 146, 200);
    const line = mk(b.sc.el, `<div style="width:${X1 - X0}px;height:6px;border-radius:3px;background:${dark ? '#262626' : 'var(--line)'}"><div style="height:100%;background:var(--blue);border-radius:3px;transform-origin:0 50%"></div></div>`, X0, 560, { ay: .5 });
    const nodes = o.steps.map(([s, at], i) => mk(b.sc.el, `<div style="display:flex;flex-direction:column;align-items:center;gap:26px"><div style="width:84px;height:84px;border-radius:50%;background:var(--blue);color:#fff;display:flex;align-items:center;justify-content:center;font:700 40px ${FONT}">${i + 1}</div><div style="font:600 44px ${FONT};${dark ? 'color:#fff' : ''};text-align:center;white-space:normal;width:${Math.min(420, gx - 20)}px">${AL(s)}</div></div>`, X0 + gx * i, 518, { ax: .5, ay: 0 }));
    b.sc.update = t => {
      b.tick(t); show(title, t, o.t0 + .15, { k: 'up', out: b.out }); show(line, t, o.t0 + .2, { k: 'up', out: b.out });
      let p = 0; o.steps.forEach(([, at], i) => { if (i > 0) p = Math.max(p, (i - 1 + EZ.inout(pr(t, at - .4, at))) / Math.max(1, n - 1)); });
      line.firstChild.firstChild.style.transform = `scaleX(${p})`;
      nodes.forEach((e, i) => show(e, t, o.steps[i][1], { k: 'pop', out: b.out }));
    };
    o.steps.forEach(([, at], i) => S(at, 'pop', .6, -.6 + 1.2 * i / Math.max(1, n - 1)));
  };

  /* 06 金句：整屏大字砸下，慢推，缓出（观点高潮） */
  TPL.quote = o => {
    const b = base(o, { bg: 'blue', tag: '', cam: 'none', trans: 'flash' });
    const fg = b.theme === 'paper' ? 'var(--ink)' : '#fff';
    const lines = o.lines || [o.text];
    const acc = s => String(s).replace(/\*(.+?)\*/g, b.theme === 'blue' ? '<span style="color:#0A0A0A">$1</span>' : '<span style="color:var(--blue)">$1</span>');
    const q = mk(b.sc.el, `<div style="font:800 ${o.size || 150}px/1.15 ${FONT};color:${fg};letter-spacing:-5px;text-align:center">${lines.map(acc).join('<br>')}</div>`, 960, 520, { ax: .5, ay: .5 });
    const by = o.by ? mk(b.sc.el, `<div class="tag" style="font-size:28px;color:${fg};opacity:.7">${o.by}</div>`, 960, 860, { ax: .5 }) : null;
    b.sc.update = t => { b.tick(t); const push = 1 + .04 * pr(t, o.at, o.t1); show(q, t, o.at, { k: 'slam', d: .45, s: push, out: b.out }); if (by) show(by, t, o.at + .5, { k: 'up', out: b.out }); };
    b.sc.cam = t => { const [sx, sy] = shake(t, o.at + .1, .35, 18); return { x: 960, y: 540, sx, sy }; };
    S(o.at, 'hit', 1); S(o.at, 'crash', .5);
  };

  /* 07 软件演示：mac 窗口放录屏 + 右侧功能卡依次打勾（工具测评） */
  TPL.demo = o => {
    const b = base(o, { bg: 'ink', tag: '// 07 — 演示', cam: 'none', trans: 'circle' });
    const win = macWin(b.sc.el, 1080, 640, o.title || 'App');
    win._x = 700; win._y = 560;
    if (!o.seq && !o.image) win._img.outerHTML = `<div style="position:absolute;inset:0;background:linear-gradient(135deg,#1f2a44,#0f1320);display:flex;flex-direction:column;gap:22px;padding:60px">${[.7, .45, .9, .55, .35].map(w => `<div style="height:26px;width:${w * 100}%;border-radius:13px;background:rgba(255,255,255,.12)"></div>`).join('')}<div class="tag" style="margin-top:auto;color:#6d9bff">// 录屏占位：传 seq 或 image</div></div>`;
    else if (o.image) win._img.src = o.image;
    const img = win.querySelector('.body img');
    const feats = (o.features || []).map(([s]) => mk(b.sc.el, `<div class="dcard" style="width:520px;height:120px;display:flex;align-items:center;gap:22px;padding:0 28px"><div class="check">✓</div><div style="font:600 38px ${FONT}">${AL(s)}</div></div>`, 1300, 0));
    feats.forEach((f, i) => { f._y = 560 - (feats.length * 140 - 20) / 2 + i * 140; });
    b.sc.update = t => {
      b.tick(t); show(win, t, o.t0 + .1, { k: 'zoom', out: b.out });
      if (o.seq && img) setFrame(img, seqAt(o.seq.dir, o.seq.n, o.seq.fps || 30, t, o.t0, true));
      feats.forEach((f, i) => show(f, t, o.features[i][1], { k: 'right', out: b.out }));
    };
    (o.features || []).forEach(([, at], i) => S(at, 'check', .6, .4, { n: i }));
  };

  /* 08 清单：逐条出现并打勾（盘点、要点总结） */
  TPL.checklist = o => {
    const b = base(o, { bg: 'paper', tag: '// 08 — 清单', trans: 'wipe' });
    const dark = b.theme !== 'paper';
    const title = mk(b.sc.el, `<div class="h2" style="${dark ? 'color:#fff' : ''}">${AL(o.title || '')}</div>`, 146, 170);
    const rows = o.items.map(([s], i) => mk(b.sc.el, `<div style="display:flex;align-items:center;gap:30px"><div class="check" style="width:64px;height:64px;font-size:36px">✓</div><div style="font:600 58px ${FONT};${dark ? 'color:#fff' : ''}">${AL(s)}</div></div>`, 146, 340 + i * 118));
    b.sc.update = t => {
      b.tick(t); show(title, t, o.t0 + .1, { k: 'up', out: b.out });
      rows.forEach((r, i) => { const at = o.items[i][1]; show(r, t, at, { k: 'left', out: b.out }); const c = r.firstChild.firstChild; c.style.transform = `scale(${(.3 + .7 * EZ.spring(pr(t, at + .15, at + .6))).toFixed(3)})`; });
    };
    o.items.forEach(([, at], i) => { S(at, 'swipe', .4); S(at + .15, 'check', .5, 0, { n: i }); });
  };

  /* 09 片尾制作说明：终端逐字打出（口播结束后约 5 秒） */
  TPL.outro = o => {
    const b = base(o, { bg: 'ink', tag: '// 制作说明', cam: 'none', trans: 'blur' });
    const head = mk(b.sc.el, `<div style="font:700 72px ${FONT};color:#fff">${AL(o.title || '本视频制作说明')}</div>`, 160, 200);
    const lines = mk(b.sc.el, `<div style="font:500 40px/1.8 ${FONT};color:#bbb">${(o.lines || []).map(A).join('<br>')}</div>`, 160, 320);
    const term = mk(b.sc.el, `<div class="term" style="width:1600px;min-height:220px;white-space:pre-wrap"><span style="color:#6d9bff">$</span> <span class="ty"></span><span class="cur">▍</span></div>`, 160, 640);
    const ty = term.querySelector('.ty'), cur = term.querySelector('.cur'), P = o.prompt || '', t2 = o.t0 + 1.0, t3 = Math.min(o.t1 - .8, t2 + P.length * .045);
    b.sc.update = t => {
      b.tick(t); show(head, t, o.t0 + .15, { k: 'up' }); show(lines, t, o.t0 + .4, { k: 'up' }); show(term, t, o.t0 + .7, { k: 'up' });
      ty.textContent = P.slice(0, Math.round(P.length * pr(t, t2, t3))); cur.style.opacity = Math.floor(t * 2) % 2 ? 1 : .2;
    };
    if (P) S(t2, 'typing', .35, 0, { d: t3 - t2 });
  };
})();

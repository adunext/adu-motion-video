/* ============================================================
   Showcase motion recipes — illustrative copy; no benchmark claims
   时间全部是口播时间（= 输出时间）。
   ============================================================ */
window.END = 108.40;

/* ---------- shared builders ---------- */
function camCard(parent, w, h, label = (window.PACK_PRESENTER_LABEL || '// on air · 主讲人'), round = false) {
  const e = mk(parent, `<div class="cam${round ? ' round' : ''}" style="width:${w}px;height:${h}px"><img>${round ? '' : `<div class="lab"><span style="color:#6d9bff">●</span> ${label}</div>`}</div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('img'); return e;
}
function faceAt(t) {                       // smoothed face centre (0..1) of the talk frame shown at t
  const m = TALKMAP[clamp(Math.floor(t * 60 + 1e-6), 0, TALK_N - 1)], F = FACE[TALKF[m[0]]];
  let lo = 0, hi = F.f.length - 1; while (hi - lo > 1) { const md = (lo + hi) >> 1; if (F.f[md] <= m[1]) lo = md; else hi = md; }
  const a = F.f[lo], b = F.f[hi], x = b > a ? clamp((m[1] - a) / (b - a)) : 0;
  return { cx: lerp(F.cx[lo], F.cx[hi], x), cy: lerp(F.cy[lo], F.cy[hi], x), h: lerp(F.h[lo], F.h[hi], x) };
}
function camAt(e, t, o) {
  setFrame(e._img, talkSrc(t)); place(e, o);
  const round = e.firstChild.classList.contains('round');
  const sm = e._sm != null ? e._sm : (e._sm = 0);          // S5 small-card mode is set by caller via e._sm (0..1)
  const k = round ? 1 : sm;
  if (k > 0) {
    const f = faceAt(t), W = e.firstChild.offsetWidth, H = e.firstChild.offsetHeight;
    // image is object-fit:cover of a 720x1280 frame; zoom so the face height ≈ 58% of the box, then centre on the face
    const cover = Math.max(W / 720, H / 1280), want = (H * .44) / (f.h * 1280 * cover);
    const z = lerp(1, clamp(want, 1, 2.6), k);
    const iw = 720 * cover * z, ih = 1280 * cover * z;
    const ox = clamp(W / 2 - f.cx * iw, W - iw, 0), oy = clamp(H * .56 - f.cy * ih, H - ih, 0);
    e._img.style.cssText = `position:absolute;left:${ox.toFixed(1)}px;top:${oy.toFixed(1)}px;width:${iw.toFixed(1)}px;height:${ih.toFixed(1)}px;max-width:none;object-fit:fill`;
  } else if (e._img.style.position) e._img.style.cssText = '';
}
function vtile(parent, w, h, r = 16, extra = '') {
  const e = mk(parent, `<div class="vt" style="width:${w}px;height:${h}px;border-radius:${r}px;${extra}"><img></div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('img'); return e;
}
function macWin(parent, w, h, title) {
  const e = mk(parent, `<div class="macwin" style="width:${w}px"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span style="margin-left:14px;display:flex;align-items:center;gap:10px">${title}</span></div><div class="body" style="height:${h}px"><img></div></div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('.body img'); return e;
}
function buildWall(parent, COLS = 27, TW = 128, TH = 72, GP = 6) {
  const N = WALL.length, ROWS = Math.ceil(N / COLS);
  const W = COLS * (TW + GP) - GP, H = ROWS * (TH + GP) - GP;
  const e = mk(parent, `<div style="position:relative;width:${W}px;height:${H}px"></div>`, 960, 540, { ax: .5, ay: .5 });
  const cells = [];
  for (let i = 0; i < N; i++) {
    const d = document.createElement('div');
    d.style.cssText = `position:absolute;left:${(i % COLS) * (TW + GP)}px;top:${Math.floor(i / COLS) * (TH + GP)}px;width:${TW}px;height:${TH}px;border-radius:5px;background-image:url(sc/wall/${String(i).padStart(3, '0')}.jpg);background-size:${TW * 4}px ${TH * 4}px;background-color:#111`;
    e.firstChild.appendChild(d); cells.push(d);
  }
  e._cells = cells; e._cols = COLS; e._rows = ROWS; e._tw = TW; e._th = TH; return e;
}
function wallTick(w, t, t0, rate = 8) {       // animate sprite frames + ripple-in from the centre
  const fi = Math.floor(t * rate);
  w._cells.forEach((c, i) => {
    const k = (fi + i * 5) % 16;
    c.style.backgroundPosition = `${-(k % 4) * w._tw}px ${-Math.floor(k / 4) * w._th}px`;
    const d = Math.hypot((i % w._cols) - w._cols / 2, Math.floor(i / w._cols) - w._rows / 2) / 16;
    c.style.opacity = clamp((t - t0 - d * .5) * 5);
  });
}
function race(parent, dark = true) {   // thin race progress line at the bottom
  const c = dark ? 'rgba(255,255,255,.14)' : 'rgba(10,10,10,.10)';
  const e = mk(parent, `<div style="width:1628px;height:2px;background:${c};position:relative">
     ${['钩子', '示意', '终结', '全品类', '打击', '快车道', '一小时', '行动'].map((n, i) => `<div style="position:absolute;left:${i / 7 * 100}%;top:-5px;width:2px;height:12px;background:${c}"></div>`).join('')}
     <div class="rp" style="position:absolute;left:0;top:-7px;width:16px;height:16px;border-radius:50%;background:var(--blue);box-shadow:0 0 18px rgba(36,98,234,.9);transform:translateX(-50%)"></div></div>`, 146, 1058);
  e._p = e.querySelector('.rp'); return e;
}
const RACE_K = [0, 8.8, 25.9, 40.4, 52.8, 69.4, 78.2, 89.8, 103];
function raceAt(e, t, o = 1) {
  let i = 0; while (i < 7 && t >= RACE_K[i + 1]) i++;
  const p = i + clamp((t - RACE_K[i]) / (RACE_K[i + 1] - RACE_K[i]));
  e._p.style.left = Math.min(100, p / 7 * 100) + '%'; place(e, { o });
}

/* =========================================================
   S1  0 – 8.80  钩子：进入下一个阶段 · 别再死磕手动剪辑 · 示意 · 离谱
   ========================================================= */
(() => {
  const sc = new Scene(0, 8.80, 'var(--paper)', { grid: 'grid' });
  const T = tags(sc, '// 01 — 下一个阶段');
  const cam = camCard(sc.el, 470, 836);
  // opening TITLE — two lines, centred, punched in fast
  const tt1 = mk(sc.el, `<div style="font:700 150px -apple-system,'PingFang SC',sans-serif;letter-spacing:-4px;color:#0A0A0A;text-align:center;line-height:1">视频内容创作</div>`, 690, 330, { ax: .5, ay: .5 });
  const tt2 = mk(sc.el, `<div style="font:800 190px -apple-system,'PingFang SC',sans-serif;letter-spacing:-6px;color:#0A0A0A;text-align:center;line-height:1">进入<span style="color:var(--blue)">下一阶段</span></div>`, 690, 560, { ax: .5, ay: .5 });
  const ttk = mk(sc.el, `<div class="mono" style="font-size:26px;color:#8C8C8C;letter-spacing:6px">AI · VIDEO · 2026</div>`, 690, 175, { ax: .5, ay: .5 });
  const flashW = mk(sc.el, `<div style="width:1920px;height:1080px;background:#2462EA"></div>`, 0, 0);
  // stage indicator 01 -> 02
  const stg = mk(sc.el, `<div style="display:flex;align-items:center;gap:22px">
     <div class="mono" style="font-size:24px;color:#8C8C8C">STAGE</div>
     <div style="position:relative;width:118px;height:84px;overflow:hidden;border-radius:14px;background:#0A0A0A">
       <div class="sn" style="position:absolute;left:0;top:0;width:100%">${['01', '02'].map(n => `<div class="mono" style="height:84px;line-height:84px;text-align:center;font-size:54px;font-weight:600;color:#fff">${n}</div>`).join('')}</div></div>
     <div style="width:420px;height:10px;border-radius:5px;background:#E7E7E4;overflow:hidden"><div class="sb" style="height:100%;width:50%;background:var(--blue);border-radius:5px"></div></div></div>`, 690, 770, { ax: .5, ay: .5 });
  const sn = stg.querySelector('.sn'), sb = stg.querySelector('.sb');
  // NLE timeline, crammed with clips; playhead crawls frame by frame
  const tl = mk(sc.el, `<div class="card" style="width:1040px;height:300px;padding:64px 26px 20px;overflow:hidden">
     <div class="lb">// 手动剪辑 · timeline</div><div class="ix fc">frame 000000</div>
     ${[0, 1, 2, 3].map(r => `<div style="position:relative;height:44px;margin-bottom:10px">${Array.from({ length: 16 }, (_, i) => { const w = 30 + ((i * 37 + r * 13) % 70); const x = (i * 61 + r * 23) % 960; return `<div style="position:absolute;left:${x}px;top:0;width:${w}px;height:44px;border-radius:7px;background:${r === 3 ? '#cfe0ff' : ['#e8e8e5', '#dcdcd8', '#d2d2ce'][r % 3]};border:1.5px solid rgba(0,0,0,.06)"></div>`; }).join('')}</div>`).join('')}
     <div class="ph" style="position:absolute;top:52px;left:120px;width:3px;height:230px;background:#E5484D"><div style="position:absolute;top:-10px;left:-9px;width:21px;height:14px;border-radius:3px;background:#E5484D"></div></div>
     </div>`, 146, 560);
  const ph = tl.querySelector('.ph'), fc = tl.querySelector('.fc');
  const strike = mk(sc.el, `<div style="width:1100px;height:10px;background:#E5484D;border-radius:5px;transform-origin:0 50%"></div>`, 120, 712);
  const stop = mk(sc.el, `<div style="border:7px solid #E5484D;color:#E5484D;border-radius:18px;padding:6px 26px;font:800 74px -apple-system,'PingFang SC';letter-spacing:6px;transform:rotate(-8deg)">别再死磕</div>`, 900, 700, { ax: .5, ay: .5 });
  // black flash: 示意 REC + 离谱
  const blk = mk(sc.el, `<div style="width:1920px;height:1080px;background:#0A0A0A"><div class="gridD" style="position:absolute;inset:0"></div></div>`, 0, 0);
  const wbg = buildWall(sc.el);
  const shade = mk(sc.el, `<div style="width:1920px;height:1080px;background:linear-gradient(90deg,rgba(10,10,10,.92) 0%,rgba(10,10,10,.78) 38%,rgba(10,10,10,.30) 72%,rgba(10,10,10,.15) 100%)"></div>`, 0, 0);
  const bot = mk(sc.el, `<div style="width:1920px;height:1080px;background:linear-gradient(0deg,rgba(10,10,10,.96) 0%,rgba(10,10,10,.88) 16%,rgba(10,10,10,0) 36%)"></div>`, 0, 0);
  const rec = mk(sc.el, `<div style="display:flex;align-items:center;gap:18px"><div class="rd" style="width:30px;height:30px;border-radius:50%;background:#E5484D;box-shadow:0 0 26px #E5484D"></div><div class="mono" style="font-size:34px;color:#fff;letter-spacing:4px">REC · 示意</div></div>`, 146, 250);
  const rd = rec.querySelector('.rd');
  const k1 = words(sc.el, [{ h: '看完你就知道', t: 5.45 }], 146, 360, 'h2', { style: 'color:#fff' });
  const k2 = words(sc.el, [{ h: '现在的 AI 剪辑', t: 6.1 }], 146, 470, 'h2', { style: 'color:#fff' });
  const k3 = words(sc.el, [{ h: '有多', t: 7.2 }, { h: '离谱。', t: 7.75, k: 'slam', d: .5, st: 'color:#6d9bff' }], 146, 600, 'h1', { style: 'color:#fff;font-size:150px' });
  const camR = camCard(sc.el, 250, 250, '', true);
  const R = race(sc.el, false);
  sc.update = t => {
    T(t);
    const B = pr(t, 3.85, 4.1);                                 // to black
    const c = EZ.spring(pr(t, 0, .9));
    const toC = EZ.inout(pr(t, 3.7, 4.2));                   // big card flies into the top-right circle as the wall appears
    const camIn = 1, camPop = .94 + .06 * EZ.spring(pr(t, 0, .45));   // talk card fully on screen at frame 1, gentle pop
    // The crop is derived from this frame's clock, including after a reverse seek.
    cam._sm = toC;
    camAt(cam, t, { x: lerp(1570, 1745, toC), y: lerp(510, 180, toC), o: 1 - pr(t, 4.1, 4.25), s: lerp(.9 * camPop, .3, toC) });
    cam.firstChild.style.borderRadius = lerp(28, 120, toC) + 'px';
    camAt(camR, t, { x: 1745, y: 180, o: pr(t, 4.1, 4.25) * (1 - pr(t, 8.6, 8.8)), s: .75 });
    // title punch: line 1 zooms in from huge (0.0–0.28s), line 2 slams at 1.2s; subtle 1.0→1.04 drift; both shrink up & out at 2.35s
    const p1 = pr(t, 0.0, 0.28), p2 = pr(t, 1.18, 1.44), up = EZ.inout(pr(t, 2.3, 2.75));
    const drift = 1 + .04 * pr(t, 0, 2.4);
    place(tt1, { s: (1 + 1.0 * (1 - EZ.out5(p1))) * drift * (1 - .55 * up), o: clamp(p1 * 4) * (1 - pr(t, 2.55, 2.75)), blur: (1 - EZ.out5(p1)) * 14, y: 330 - 170 * up, x: 690 - 300 * up });
    place(tt2, { s: (1 + 1.3 * (1 - EZ.out5(p2))) * drift * (1 - .55 * up), o: clamp(p2 * 4) * (1 - pr(t, 2.55, 2.75)), blur: (1 - EZ.out5(p2)) * 16, y: 560 - 250 * up, x: 690 - 300 * up });
    place(ttk, { o: pr(t, .15, .4) * (1 - pr(t, 2.3, 2.5)) });
    place(flashW, { o: .55 * Math.max(0, 1 - Math.abs(t - 1.3) / .12) });     // blue flash on "下一阶段"
    show(stg, t, 1.55, { k: 'pop', out: 2.4 });
    const f = EZ.inout(pr(t, 1.55, 2.0)); sn.style.transform = `translateY(${-84 * f}px)`; sb.style.width = (50 + 50 * f) + '%';
    show(tl, t, 2.5, { k: 'up', dist: 80, out: 3.72 });
    const fr = Math.floor(clamp(t - 2.6, 0, 9) * 24 * 1.0); ph.style.left = (120 + Math.floor((t - 2.6) * 6) * 2.2) + 'px'; fc.textContent = 'frame ' + String(Math.max(0, fr)).padStart(6, '0');
    const sx = EZ.expo(pr(t, 3.05, 3.3)); strike.style.transform = `scaleX(${sx})`; place(strike, { o: sx > 0 ? 1 - pr(t, 3.7, 3.9) : 0 });
    show(stop, t, 3.28, { k: 'slam', out: 3.72 });
    place(blk, { o: B });
    // wall background: ripples in right after the cut to black, slow push-in + drift, flares on "离谱"
    const W0 = 3.9, wz = lerp(1.32, 1.06, EZ.out(pr(t, W0, 8.8))), fl = Math.max(0, 1 - Math.abs(t - 7.85) / .45);
    if (t >= W0 - .1) wallTick(wbg, t, W0);
    place(wbg, { o: clamp((t - W0) * 4) * (1 - pr(t, 8.55, 8.8)), s: wz, x: 960 + (t - W0) * -14, y: 540 + (t - W0) * 6, r: lerp(-3, 0, EZ.out(pr(t, W0, 6))) });
    wbg.style.filter = `brightness(${(.62 + .5 * fl).toFixed(3)}) saturate(${(1 + .3 * fl).toFixed(2)})`;
    place(shade, { o: clamp((t - W0) * 4) * (1 - pr(t, 8.55, 8.8)) * (1 - .2 * fl) });
    place(bot, { o: clamp((t - W0) * 4) * (1 - pr(t, 8.55, 8.8)) });
    show(rec, t, 4.0, { k: 'left' }); rd.style.opacity = .35 + .65 * (Math.floor(t * 2.2) % 2);
    wordsAt(k1, t); wordsAt(k2, t); wordsAt(k3, t, { out: 8.55 });
    [k1, k2, rec].forEach(e => { e.style.opacity *= 1 - pr(t, 8.5, 8.75); });
    raceAt(R, t, 1 - B);
  };
  sc.cam = t => { const [sx, sy] = shake(t, 7.75, .35, 14), [ax, ay] = shake(t, 1.3, .3, 16); return { x: 960, y: 540, sx: sx + ax, sy: sy + ay, z: 1 + .025 * EZ.out(pr(t, 7.75, 8.8)) }; };
  S(0, 'hit', .9); S(0, 'whoosh', .6); S(1.3, 'hit', 1); S(1.55, 'levelup', .7); S(2.3, 'swoosh', .5); S(2.5, 'card', .6); S(2.6, 'clock', .5, 0, { d: 1.0 }); S(3.05, 'slash', .8); S(3.28, 'stamp', .9);
  S(3.85, 'whoosh', .7); S(3.9, 'sparkle', .45); S(4.0, 'alert', .6); S(5.45, 'tick', .4); S(6.1, 'tick', .4); S(7.75, 'hit', 1);
})();

/* =========================================================
   S2  8.80 – 25.90  示意：九宫格 · GPT/对比组 A 高亮 · 型号 · 全部试了 · 推理拉满 · Token 成本
   ========================================================= */
(() => {
  const sc = new Scene(8.80, 25.90, '#0A0A0A', { grid: 'gridD', trans: 'flash', td: .3, fa: .3 });
  const T = tags(sc, '// 02 — 示意 · 同一段口播 · 9 个展示卡片', '', true);
  const G = [['opus55p', '示例方案 A', '详细提示词', 'c'], ['gpt6pro', '示例方案 B', '', 'g'], ['gpt6astra', '示例方案 C', '', 'g'],
             ['grok47', '示例方案 D', '', 'x'], ['opus55', '示例方案 A', '一句话提示词', 'c', 1], ['gpt6sol', '示例方案 E', '', 'g'],
             ['gpt56sol', '示例方案 F', '', 'g'], ['gpt56', '示例方案 G', '', 'g'], ['claude50', '示例方案 H', '', 'c']];
  const CW = 356, CH = 200, GAP = 14, LBL = 38;
  const X0 = 150, Y0 = 110;
  const pos = i => [X0 + (i % 3) * (CW + GAP) + CW / 2, Y0 + Math.floor(i / 3) * (CH + LBL + GAP) + CH / 2];
  const tiles = G.map((g, i) => {
    const e = mk(sc.el, `<div style="width:${CW}px;position:relative">
      <div class="fr" style="position:relative;width:${CW}px;height:${CH}px;border-radius:12px;overflow:hidden;background:#111;box-shadow:0 0 0 1.5px #262626"><img style="width:100%;height:100%;object-fit:cover;display:block">
        <div class="ok" style="position:absolute;right:10px;top:10px;width:38px;height:38px;border-radius:50%;background:#28c840;color:#fff;display:flex;align-items:center;justify-content:center;font:700 22px -apple-system;opacity:0">✓</div></div>
      <div style="display:flex;justify-content:space-between;align-items:baseline;height:${LBL}px;padding-top:8px"><div class="nm" style="font-size:23px;font-weight:600;color:#bbb">${g[1]}</div><div class="mono" style="font-size:16px;color:#666">${g[2]}</div></div>
      <div class="ring" style="position:absolute;left:-7px;top:-7px;width:${CW + 14}px;height:${CH + 14}px;border-radius:17px;border:4px solid #fff;opacity:0"></div></div>`, pos(i)[0], pos(i)[1] + LBL / 2, { ax: .5, ay: .5 });
    e._img = e.querySelector('img'); e._ring = e.querySelector('.ring'); e._ok = e.querySelector('.ok'); e._fr = e.querySelector('.fr'); e._nm = e.querySelector('.nm'); return e;
  });
  // right panel
  const PX = 1500;
  const cam = camCard(sc.el, 250, 250, '', true);
  const hdr = mk(sc.el, `<div class="mono" style="font-size:22px;color:#777">// 同一段口播 · 9 个模型</div>`, PX - 130, 176);
  const vend = mk(sc.el, `<div style="display:flex;gap:12px"><div class="chip vg" style="background:#1d1d1d;color:#bbb;border:1.5px solid #333">对比组 B</div><div class="chip vc" style="background:#1d1d1d;color:#bbb;border:1.5px solid #333">对比组 A</div></div>`, PX - 130, 218);
  const VG = vend.querySelector('.vg'), VC = vend.querySelector('.vc');
  const MOD = [['5.6', 15.2], ['6', 16.6], ['Pro', 17.75], ['Ultra', 18.62]];
  const mods = MOD.map((m, i) => mk(sc.el, `<div class="chip" style="background:var(--blue);color:#fff;font-size:30px;padding:10px 26px">${m[0]}</div>`, PX - 130 + [0, 104, 176, 290][i], 296));
  const all = mk(sc.el, `<div style="display:flex;align-items:center;gap:14px"><div class="check">✓</div><div style="font:600 40px -apple-system,'PingFang SC';color:#fff">所有的，全部试了</div></div>`, PX - 130, 386);
  const ok = mk(sc.el, `<div style="font:500 30px -apple-system,'PingFang SC';color:#8C8C8C">总的来说 · <span style="color:#fff">还可以</span></div>`, PX - 130, 456);
  // reasoning slider
  const rs = mk(sc.el, `<div class="dcard" style="width:440px;height:150px"><div class="lb">// 推理程度</div>
     <div style="position:absolute;left:28px;right:28px;top:78px;height:10px;border-radius:5px;background:#2a2a2a"><div class="rf" style="height:100%;width:30%;border-radius:5px;background:linear-gradient(90deg,#2462EA,#E5484D)"></div>
       <div class="rk" style="position:absolute;top:-11px;left:30%;width:32px;height:32px;margin-left:-16px;border-radius:50%;background:#fff;box-shadow:0 4px 12px rgba(0,0,0,.5)"></div></div>
     <div class="mono rv" style="position:absolute;right:28px;top:104px;font-size:22px;color:#fff">medium</div>
     <div class="mono" style="position:absolute;left:28px;top:104px;font-size:18px;color:#555">low</div></div>`, PX - 130, 524);
  const rf = rs.querySelector('.rf'), rk = rs.querySelector('.rk'), rv = rs.querySelector('.rv');
  const tok = mk(sc.el, `<div class="dcard" style="width:440px;height:170px"><div class="lb">// token 消耗</div>
     <div class="mono tv" style="position:absolute;left:28px;top:62px;font-size:64px;font-weight:600;color:#fff">0</div>
     <div class="mono" style="position:absolute;left:28px;top:138px;font-size:18px;color:#777">成本 <span class="cv" style="color:#fff">$0.00</span></div></div>`, PX - 130, 698);
  const tv = tok.querySelector('.tv'), cv = tok.querySelector('.cv');
  const R = race(sc.el);
  sc.update = t => {
    T(t); place(sc._tags[1], { o: 0 });
    const src = t - 8.8;
    tiles.forEach((e, i) => {
      const t0 = 8.9 + [4, 1, 3, 5, 7, 0, 2, 6, 8].indexOf(i) * .06;
      const a = EZ.spring(pr(t, t0, t0 + .7));
      setFrame(e._img, seqAt('g_' + G[i][0], 780, 30, t, 8.8));
      const g = G[i][3];
      const litG = g === 'g' && t >= 12.13 && t < 13.37, litC = g === 'c' && t >= 13.37 && t < 15.0;
      const modLit = (G[i][0] === 'gpt56' || G[i][0] === 'gpt56sol') && t >= 15.2 && t < 16.6 || (G[i][0] === 'gpt6sol') && t >= 16.6 && t < 17.75 || (G[i][0] === 'gpt6pro') && t >= 17.75 && t < 18.62 || (G[i][0] === 'gpt6astra') && t >= 18.62 && t < 19.3;
      const lit = litG || litC || modLit;
      e._ring.style.opacity = lit ? 1 : 0; e._ring.style.borderColor = g === 'c' ? '#6d9bff' : '#fff';
      e._nm.style.color = lit ? '#fff' : '#bbb';
      const dim = (t >= 12.13 && t < 19.3 && !lit) ? .45 : 1;
      e._fr.style.opacity = dim * (1 - .25 * pr(t, 22.0, 22.6));
      const ck = pr(t, 19.35 + i * .07, 19.6 + i * .07); e._ok.style.opacity = ck; e._ok.style.transform = `scale(${.4 + .6 * EZ.spring(ck)})`;
      const exit = EZ.inout(pr(t, 25.35, 25.9));
      place(e, { o: clamp(a * 3) * (1 - exit * (i === 4 ? 0 : 1)), s: (.75 + .25 * a) * (i === 4 ? 1 + exit * .3 : 1 - .1 * exit), blur: i === 4 ? 0 : exit * 10 });
    });
    setFrame(cam._img, talkSrc(t)); place(cam, { x: 1760, y: 130, o: EZ.out(pr(t, 8.9, 9.4)) * (1 - pr(t, 25.4, 25.8)), s: .62 });
    show(hdr, t, 9.2, { k: 'left', out: 25.3 }); show(vend, t, 9.4, { k: 'left', out: 25.3 });
    const gL = t >= 12.13, cL = t >= 13.37;
    // Assign all three properties every frame. Appending cssText leaked both
    // highlight states across repeated or out-of-order renderAt() calls.
    VG.style.background = gL ? '#fff' : '#1d1d1d';
    VG.style.color = gL ? '#0A0A0A' : '#bbb';
    VG.style.borderColor = gL ? '#fff' : '#333';
    VC.style.background = cL ? 'var(--blue)' : '#1d1d1d';
    VC.style.color = cL ? '#fff' : '#bbb';
    VC.style.borderColor = cL ? 'var(--blue)' : '#333';
    mods.forEach((m, i) => show(m, t, MOD[i][1], { k: 'pop', out: 25.3 }));
    show(all, t, 19.3, { k: 'up', out: 25.3 }); show(ok, t, 20.25, { k: 'up', out: 25.3 });
    show(rs, t, 22.0, { k: 'up', out: 25.3 });
    const rp = EZ.inout(pr(t, 22.7, 23.6)); rf.style.width = (30 + 70 * rp) + '%'; rk.style.left = (30 + 70 * rp) + '%';
    rv.textContent = rp < .5 ? 'medium' : rp < .98 ? 'high' : 'Ultra'; rv.style.color = rp >= .98 ? '#E5484D' : '#fff';
    show(tok, t, 23.75, { k: 'up', out: 25.3 });
    const tk = Math.pow(pr(t, 23.8, 25.5), 1.6) * 4.8e6; tv.textContent = fmt(tk); tv.style.color = tk > 3e6 ? '#E5484D' : '#fff'; cv.textContent = '$' + (tk * 1.5e-5).toFixed(2);
    raceAt(R, t, pr(t, 8.9, 9.3));
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 + .02 * EZ.out(pr(t, 8.8, 25)) });
  S(8.8, 'whoosh', .7); for (let i = 0; i < 9; i++) S(8.9 + i * .06, 'tick', .3, -.6 + (i % 3) * .4);
  S(12.13, 'pop', .6); S(13.37, 'pop', .6, .2); MOD.forEach(m => S(m[1], 'pop', .7, .5));
  for (let i = 0; i < 9; i++) S(19.35 + i * .07, 'check', .35, 0, { n: i });
  S(20.25, 'tick', .4); S(22.0, 'card', .5); S(22.7, 'rise_s', .8); S(23.6, 'alert', .6); S(23.8, 'counter', .5, 0, { d: 1.7 });
})();

/* =========================================================
   S3  25.90 – 40.40  演示总结 · 方案 A 放大 · 审片报告 · 30 分钟 · 上一条作品
   ========================================================= */
(() => {
  const sc = new Scene(25.90, 40.40, '#0A0A0A', { grid: 'gridD' });
  const T = tags(sc, '// 03 — 示例方案 A', '', true);
  const hero = vtile(sc.el, 1440, 810, 20, 'box-shadow:0 0 0 2px rgba(109,155,255,.55),0 40px 120px rgba(36,98,234,.35)');
  hero.firstChild.insertAdjacentHTML('beforeend', `<div class="scan" style="position:absolute;left:0;top:0;bottom:0;width:4px;background:#6d9bff;box-shadow:0 0 30px 6px rgba(109,155,255,.8);opacity:0"></div>
     <div class="tg mono" style="position:absolute;left:22px;top:18px;background:rgba(10,10,10,.7);color:#fff;font-size:20px;padding:6px 14px;border-radius:8px">示例方案 A · 一句话提示词 · 成片</div>`);
  const scan = hero.querySelector('.scan');
  const end = words(sc.el, [{ h: '终结', t: 29.0, k: 'slam', d: .45 }, { h: '比赛。', t: 30.3, k: 'slam', d: .45, st: 'color:#6d9bff' }], 960, 230, 'h1', { ax: .5, style: 'color:#fff;font-size:170px;text-align:center' });
  const board = mk(sc.el, `<div style="background:#0A0A0A;border:2px solid #333;border-radius:20px;padding:26px 40px;display:flex;align-items:center;gap:36px;box-shadow:0 30px 90px rgba(0,0,0,.6)">
     <div><div class="mono" style="font-size:20px;color:#777;letter-spacing:3px">DEMO · 示意比较</div><div style="font:700 70px -apple-system,'PingFang SC';color:#fff;margin-top:6px">对比组 A <span style="color:#6d9bff">方案 A</span></div></div>
     <div style="width:2px;height:110px;background:#333"></div>
     <div class="mono" style="font-size:96px;font-weight:700;color:#6d9bff">No.1</div></div>`, 960, 660, { ax: .5, ay: .5 });
  const vs = mk(sc.el, `<div style="display:flex;align-items:center;gap:26px">
     <div class="dcard" style="width:400px;height:140px"><div class="lb">// 多年专业剪辑师</div><div style="position:absolute;left:28px;top:64px;font:600 44px -apple-system,'PingFang SC';color:#fff">人类 · 专业</div></div>
     <div style="font:600 34px -apple-system,'PingFang SC';color:#6d9bff">完全不输</div>
     <div class="dcard" style="width:400px;height:140px;border-color:#2462EA"><div class="lb" style="color:#6d9bff">// AI</div><div style="position:absolute;left:28px;top:64px;font:600 44px -apple-system,'PingFang SC';color:#fff">方案 A</div></div></div>`, 650, 810, { ax: .5, ay: .5 });
  const ring = mk(sc.el, `<div style="position:relative;width:250px;height:250px">
     <svg width="250" height="250" viewBox="0 0 250 250" style="position:absolute;inset:0;transform:rotate(-90deg)"><circle cx="125" cy="125" r="108" fill="none" stroke="#2a2a2a" stroke-width="12"/><circle class="rc" cx="125" cy="125" r="108" fill="none" stroke="#2462EA" stroke-width="12" stroke-linecap="round" stroke-dasharray="678.6" stroke-dashoffset="678.6"/></svg>
     <div class="mono rt" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:56px;font-weight:600;color:#fff">00:00</div>
     <div class="mono" style="position:absolute;left:0;right:0;top:164px;text-align:center;font-size:17px;color:#888">分钟 · 出片</div></div>`, 1450, 300, { ax: .5, ay: .5 });
  const rc = ring.querySelector('.rc'), rt = ring.querySelector('.rt');
  const rpt = mk(sc.el, `<div class="mono" style="font-size:22px;color:#777">// 审片报告</div>`, 1320, 470);
  const NOTE = [['转场细节', 33.9], ['画面流畅度', 34.6], ['文案 · 情绪逻辑', 35.7]];
  const notes = NOTE.map((n, i) => mk(sc.el, `<div style="display:flex;align-items:center;gap:16px;width:540px;padding:14px 20px;border-radius:16px;background:#141414;border:1.5px solid #262626">
     <div class="check" style="width:42px;height:42px;font-size:22px">✓</div><div style="font:600 34px -apple-system,'PingFang SC';color:#fff">${n[0]}</div><div class="mono" style="margin-left:auto;font-size:20px;color:#6d9bff">PASS</div></div>`, 1320, 515 + i * 88));
  const acc = words(sc.el, [{ h: '精准得', t: 37.1 }, { h: '离谱。', t: 37.7, k: 'slam', st: 'color:#6d9bff' }], 1320, 780, 'h1', { style: 'color:#fff;font-size:88px' });
  const prev = mk(sc.el, `<div style="position:relative;width:600px"><div class="mono" style="font-size:20px;color:#6d9bff;margin-bottom:12px">// 上一条作品 · 感兴趣可以翻</div>
     <div class="vt" style="width:600px;height:338px;border-radius:18px;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 0 2px #2a2a2a"><img></div></div>`, 1880, 880, { ax: 1, ay: 1 });
  const prevImg = prev.querySelector('img');
  const cam = camCard(sc.el, 300, 300, '', true);
  const R = race(sc.el);
  sc.update = t => {
    T(t); place(sc._tags[1], { o: 0 });
    setFrame(hero._img, seqAt('opus_hero', 960, 60, t, 25.9, false));
    const g = EZ.inout(pr(t, 25.9, 26.9));                       // grow from grid centre tile
    const L = EZ.inout(pr(t, 31.0, 31.7));                       // to left layout
    const dim = EZ.inout(pr(t, 28.75, 29.1)) * (1 - L);
    const x = lerp(lerp(718, 960, g), 650, L), y = lerp(lerp(514, 480, g), 430, L);
    const s = lerp(lerp(372 / 1440, 1, g), 1000 / 1440, L);
    place(hero, { x, y, s, o: 1 - .75 * pr(t, 39.4, 40.1) });
    hero.style.filter = `brightness(${(1 - .78 * dim).toFixed(3)})${dim > .01 ? ` blur(${(4 * dim).toFixed(1)}px)` : ''}`;
    // scan sweeps per review note
    let sp = -1; NOTE.forEach(n => { const q = pr(t, n[1] - .15, n[1] + .55); if (q > 0 && q < 1) sp = q; });
    scan.style.opacity = sp >= 0 ? Math.sin(sp * Math.PI) : 0; scan.style.left = (Math.max(0, sp) * 100) + '%';
    wordsAt(end, t, { out: 30.95 });
    show(board, t, 29.3, { k: 'pop', out: 30.95 });
    show(vs, t, 31.4, { k: 'up', out: 33.0 });
    show(ring, t, 33.1, { k: 'pop', out: 38.35 });
    const rp = EZ.inout(pr(t, 33.15, 34.3)); rc.setAttribute('stroke-dashoffset', (678.6 * (1 - rp)).toFixed(1)); rt.textContent = String(Math.round(rp * 30)).padStart(2, '0') + ':00';
    show(rpt, t, 33.8, { k: 'left', out: 38.35 });
    notes.forEach((n, i) => show(n, t, NOTE[i][1], { k: 'right', dist: 80, out: 38.35 }));
    wordsAt(acc, t, { out: 38.35 });
    show(prev, t, 38.5, { k: 'right', dist: 300, out: 40.15 }); setFrame(prevImg, seqAt('prev', 210, 30, t, 38.5, false));
    camAt(cam, t, { x: 1790, y: 190, o: EZ.out(pr(t, 26.0, 26.5)) * (1 - pr(t, 40.1, 40.4)), s: .72 });
    raceAt(R, t, .7);
  };
  sc.cam = t => { const [sx, sy] = shake(t, 29.0, .35, 12), [sx2, sy2] = shake(t, 30.3, .35, 12); return { x: 960, y: 540, sx: sx + sx2, sy: sy + sy2, z: 1 + .02 * EZ.out(pr(t, 31.6, 38.5)) }; };
  S(25.9, 'whoosh', .8); S(26.9, 'shine', .5); S(28.8, 'powerdown', .35); S(29.0, 'hit', 1); S(29.3, 'stamp', .6); S(30.3, 'hit', .9);
  S(31.0, 'whoosh', .5); S(31.4, 'card', .5); S(33.1, 'pop', .5); S(33.15, 'fill', .4, 0, { d: 1.1 }); S(34.3, 'ding', .5);
  NOTE.forEach((n, i) => { S(n[1] - .15, 'swipe', .35); S(n[1], 'check', .5, .5, { n: i }); }); S(37.7, 'hit', .8); S(38.5, 'swipe', .6, .6);
})();

/* =========================================================
   S4  40.40 – 52.70  全品类：四品类 · 389 条 方案 A 作品墙（GitHub） · 不是流水线 · 镜头语言 · 叙事节奏
   ========================================================= */
(() => {
  const sc = new Scene(40.40, 52.70, 'var(--paper)', { grid: 'grid', trans: 'circle', tc: '#F7F7F5', td: .55, cx: 1600, cy: 820 });
  const T = tags(sc, '// 04 — 全品类');
  const cam = camCard(sc.el, 260, 260, '', true);
  const h = words(sc.el, [{ h: '不止', t: 40.5 }, { h: '口播。', t: 40.9 }, { h: '全品类', t: 41.55, st: 'color:var(--blue)' }, { h: '测了个遍。', t: 42.3 }], 146, 250, 'h2');
  const CAT = [['知识讲解', 'cat_explain', 43.17, '// explainer'], ['趣味解说', 'cat_fun', 43.75, '// commentary'], ['剧情短片', 'cat_story', 44.33, '// short film'], ['音乐 MV', 'cat_mv', 45.1, '// music video']];
  const CWD = 395, CHT = 222;
  const cats = CAT.map((c, i) => {
    const e = mk(sc.el, `<div style="width:${CWD}px"><div class="vt" style="width:${CWD}px;height:${CHT}px;border-radius:16px;box-shadow:0 22px 50px rgba(0,0,0,.18)"><img></div>
       <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:14px"><div style="font:600 38px -apple-system,'PingFang SC'">${c[0]}</div><div class="mono" style="font-size:18px;color:#8C8C8C">${c[3]}</div></div></div>`, 146 + CWD / 2 + i * (CWD + 16), 610, { ax: .5, ay: .5 });
    e._img = e.querySelector('img'); return e;
  });
  // ---- the wall: all 方案 A videos from github (389) ----
  const N = WALL.length, COLS = 27, TW = 128, TH = 72, GP = 6;
  const ROWS = Math.ceil(N / COLS);
  const wallW = COLS * (TW + GP) - GP, wallH = ROWS * (TH + GP) - GP;
  const wall = mk(sc.el, `<div style="position:relative;width:${wallW}px;height:${wallH}px"></div>`, 960, 540, { ax: .5, ay: .5 });
  const cells = [];
  for (let i = 0; i < N; i++) {
    const d = document.createElement('div');
    d.style.cssText = `position:absolute;left:${(i % COLS) * (TW + GP)}px;top:${Math.floor(i / COLS) * (TH + GP)}px;width:${TW}px;height:${TH}px;border-radius:5px;background-image:url(sc/wall/${String(i).padStart(3, '0')}.jpg);background-size:${TW * 4}px ${TH * 4}px;background-color:#111`;
    wall.firstChild.appendChild(d); cells.push(d);
  }
  const gh = mk(sc.el, `<div style="display:flex;align-items:center;gap:16px;background:#0A0A0A;color:#fff;border-radius:18px;padding:16px 28px;box-shadow:0 20px 60px rgba(0,0,0,.35)">
     <img src="assets/wall-badge.png" style="width:38px;height:38px;object-fit:contain">
     <div><div class="mono" style="font-size:20px;color:#aaa">// 网络优秀作品收集 · 非个人原创</div>
     <div style="font:600 34px -apple-system,'PingFang SC';margin-top:2px"><span class="wn" style="color:#6d9bff">0</span> 条 · 示例素材 · 请填写实际来源</div></div></div>`, 960, 150, { ax: .5, ay: .5 });
  const wn = gh.querySelector('.wn');
  const qa = words(sc.el, [{ h: '全能靠 AI', t: 45.9 }, { h: '共创出', t: 46.6 }, { h: '高质量成片。', t: 47.3, st: 'color:#6d9bff' }], 960, 470, 'h1', { ax: .5, style: 'color:#fff;text-align:center;font-size:100px;text-shadow:0 10px 60px rgba(0,0,0,.9)' });
  // template conveyor (not this)
  const conv = mk(sc.el, `<div style="position:relative;width:1628px;height:190px;overflow:hidden">
     <div class="cv" style="position:absolute;left:0;top:20px;display:flex;gap:18px">${Array.from({ length: 18 }, () => `<div style="width:200px;height:120px;border-radius:12px;background:#E7E7E4;border:1.5px solid #d5d5d0;display:flex;align-items:center;justify-content:center;font:500 22px ui-monospace,monospace;color:#9a9a9a">template_01</div>`).join('')}</div>
     <div style="position:absolute;left:0;right:0;top:152px;height:10px;border-radius:5px;background:repeating-linear-gradient(90deg,#c9c9c4 0 26px,#dededa 26px 52px)"></div></div>`, 146, 470);
  const cvI = conv.querySelector('.cv');
  const cvX = mk(sc.el, `<div style="width:1660px;height:10px;background:#E5484D;border-radius:5px;transform-origin:0 50%"></div>`, 130, 560);
  const notT = mk(sc.el, `<div style="font:600 76px -apple-system,'PingFang SC';color:#8C8C8C">不是套模板的<span style="color:#0A0A0A">流水线</span></div>`, 146, 300);
  // lens language + narrative rhythm
  const lens = mk(sc.el, `<div style="position:relative;width:760px;height:428px;border-radius:18px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.2)"><img style="width:100%;height:100%;object-fit:cover;display:block">
     <div class="g3" style="position:absolute;inset:0;background:linear-gradient(90deg,transparent calc(33.33% - 1px),rgba(255,255,255,.7) calc(33.33% - 1px),rgba(255,255,255,.7) 33.33%,transparent 33.33%,transparent calc(66.66% - 1px),rgba(255,255,255,.7) calc(66.66% - 1px),rgba(255,255,255,.7) 66.66%,transparent 66.66%),linear-gradient(0deg,transparent calc(33.33% - 1px),rgba(255,255,255,.7) calc(33.33% - 1px),rgba(255,255,255,.7) 33.33%,transparent 33.33%,transparent calc(66.66% - 1px),rgba(255,255,255,.7) calc(66.66% - 1px),rgba(255,255,255,.7) 66.66%,transparent 66.66%)"></div>
     <div class="sh mono" style="position:absolute;left:18px;top:16px;background:var(--blue);color:#fff;font-size:22px;padding:4px 14px;border-radius:8px">远景 · WS</div></div>`, 146 + 380, 610, { ax: .5, ay: .5 });
  const lensImg = lens.querySelector('img'), lensSh = lens.querySelector('.sh');
  const lensT = mk(sc.el, `<div style="font:600 62px -apple-system,'PingFang SC'">有<span style="color:var(--blue)">镜头语言</span></div>`, 146, 290);
  const arc = mk(sc.el, `<div style="position:relative;width:700px;height:428px">
     <div style="font:600 62px -apple-system,'PingFang SC';position:absolute;left:0;top:-120px">有<span style="color:var(--blue)">叙事节奏</span></div>
     <svg width="700" height="360" viewBox="0 0 700 360" style="position:absolute;left:0;top:40px"><path d="M10 320 C 140 300, 180 220, 260 200 S 420 40, 520 30 S 640 220, 690 250" fill="none" stroke="#E7E7E4" stroke-width="8" stroke-linecap="round"/>
     <path class="ap" d="M10 320 C 140 300, 180 220, 260 200 S 420 40, 520 30 S 640 220, 690 250" fill="none" stroke="#2462EA" stroke-width="8" stroke-linecap="round" stroke-dasharray="1000" stroke-dashoffset="1000"/></svg>
     ${[['起', 10, 330], ['承', 250, 210], ['转', 510, 40], ['合', 680, 260]].map(([n, x, y], i) => `<div class="an" style="position:absolute;left:${x}px;top:${y + 40}px;transform:translate(-50%,-50%);width:66px;height:66px;border-radius:50%;background:#0A0A0A;color:#fff;display:flex;align-items:center;justify-content:center;font:600 30px 'PingFang SC';opacity:0">${n}</div>`).join('')}</div>`, 1030, 402);
  const ap = arc.querySelector('.ap'), ans = [...arc.querySelectorAll('.an')];
  const R = race(sc.el, false);
  sc.update = t => {
    T(t);
    camAt(cam, t, { x: 1745, y: 180, o: EZ.out(pr(t, 40.5, 41)) * (1 - pr(t, 45.5, 45.8)) + pr(t, 48.3, 48.6) * (1 - pr(t, 52.4, 52.7)), s: .75 });
    wordsAt(h, t, { out: 45.4 });
    cats.forEach((e, i) => {
      show(e, t, CAT[i][2], { k: 'up', dist: 70, out: 45.55 + i * .03 });
      setFrame(e._img, seqAt(CAT[i][1], 360, 30, t, CAT[i][2]));
    });
    // wall: fly-in and zoom-out reveal, then dim for the headline
    const W0 = 45.55, W1 = 48.3;
    const w = pr(t, W0, W1);
    const z = lerp(2.6, .98, EZ.out5(pr(t, W0, W0 + 1.5)));
    place(wall, { o: clamp((t - W0) * 5) * (1 - pr(t, W1 - .2, W1)), s: z, r: lerp(-4, 0, EZ.out(pr(t, W0, W0 + 1.5))) });
    const fi = Math.floor(t * 8);
    cells.forEach((c, i) => {
      const k = (fi + i * 5) % 16;
      c.style.backgroundPosition = `${-(k % 4) * TW}px ${-Math.floor(k / 4) * TH}px`;
      const d = Math.hypot((i % COLS) - COLS / 2, Math.floor(i / COLS) - ROWS / 2) / 16;
      c.style.opacity = clamp((t - W0 - d * .5) * 5) * (1 - .55 * pr(t, 45.85, 46.3));
    });
    sc.el.style.background = t >= W0 && t < W1 ? '#0A0A0A' : 'var(--paper)';
    if (sc.gridEl) sc.gridEl.style.opacity = t >= W0 && t < W1 ? 0 : .6;
    show(gh, t, W0 + .45, { k: 'down', out: W1 - .3 });
    wn.textContent = fmt(counter(t, W0 + .5, W0 + 1.8, 0, window.PACK_WALL_UNIQUE_COUNT || N));
    wordsAt(qa, t, { out: W1 - .35 });
    // not a conveyor
    show(notT, t, 48.25, { k: 'up', out: 49.6 });
    show(conv, t, 48.3, { k: 'up', out: 49.62 }); cvI.style.transform = `translateX(${-((t - 48.3) * 260) % 218}px)`;
    const sx = EZ.expo(pr(t, 49.0, 49.25)); cvX.style.transform = `scaleX(${sx})`; place(cvX, { o: sx > 0 ? 1 - pr(t, 49.55, 49.7) : 0 });
    // lens language
    show(lensT, t, 49.73, { k: 'up', out: 52.4 });
    show(lens, t, 49.75, { k: 'up', dist: 60, out: 52.45 });
    const shot = t < 50.35 ? 0 : t < 50.95 ? 1 : 2;
    setFrame(lensImg, seqAt('mv_lens', 345, 30, t, 49.75 - [0.8, 3.6, 8.4][shot], false));
    lensImg.style.transform = 'none';
    lensSh.textContent = ['推镜 · Dolly', '跟拍 · Tracking', '特写 · CU'][shot];
    show(arc, t, 50.93, { k: 'up', out: 52.45 });
    ap.setAttribute('stroke-dashoffset', (1000 * (1 - EZ.inout(pr(t, 51.0, 52.3)))).toFixed(1));
    ans.forEach((a, i) => { const x = pr(t, 51.05 + i * .36, 51.3 + i * .36); a.style.opacity = x; a.style.transform = `translate(-50%,-50%) scale(${.5 + .5 * EZ.spring(x)})`; });
    raceAt(R, t, t >= W0 && t < W1 ? 0 : 1);
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 + .02 * EZ.out(pr(t, 45.55, 48.3)) });
  S(40.4, 'whoosh', .6); S(41.55, 'tick', .4); CAT.forEach((c, i) => S(c[2], 'card', .55, -.6 + i * .4));
  S(45.55, 'whoosh', .9); S(45.6, 'sparkle', .6); S(45.85, 'counter', .45, 0, { d: 1.3 }); S(47.3, 'hit', .8);
  S(48.3, 'slide', .4, 0, { d: .7 }); S(49.0, 'slash', .8); S(49.75, 'card', .5); S(50.35, 'click', .6); S(50.95, 'click', .6);
  [0, 1, 2, 3].forEach(i => S(51.05 + i * .36, 'pop', .5, -.4 + i * .25));
})();

/* =========================================================
   S5  52.70 – 69.40  打击：震撼也是打击 · AI 产品开发者 · 示例软件 · 格局改写
   ========================================================= */
(() => {
  const sc = new Scene(52.70, 69.40, '#0A0A0A', { grid: 'gridD', trans: 'blur', td: .5 });
  const T = tags(sc, '// 05 — 震撼，也是打击', '', true);
  const cam = camCard(sc.el, 470, 836);
  const camR = camCard(sc.el, 250, 250, '', true);
  const s1 = words(sc.el, [{ h: '不仅是', t: 54.1 }, { h: '震撼，', t: 54.45, st: 'color:#fff' }], 146, 320, 'h1', { style: 'color:#6B6B6B;font-size:120px' });
  const s2 = mk(sc.el, `<div class="h1" style="color:#fff;font-size:180px;position:relative">也是打击。<svg class="ck" width="560" height="220" viewBox="0 0 560 220" style="position:absolute;left:30px;top:10px"><path d="M220 0 L250 70 L210 100 L270 150 L240 220" fill="none" stroke="#E5484D" stroke-width="7" stroke-dasharray="300" stroke-dashoffset="300"/><path d="M250 70 L320 90" fill="none" stroke="#E5484D" stroke-width="5" stroke-dasharray="100" stroke-dashoffset="100"/></svg></div>`, 146, 470);
  const ckP = [...s2.querySelectorAll('path')];
  const id = mk(sc.el, `<div style="display:flex;align-items:center;gap:22px">
     <img src="assets/app-logo.png" style="width:120px;height:120px;border-radius:28px;box-shadow:0 12px 30px rgba(0,0,0,.5)">
     <div><div class="mono" style="font-size:24px;color:#777">// 示例身份标签</div><div style="font:600 96px -apple-system,'PingFang SC';color:#fff;letter-spacing:-1px">示例创作者</div></div></div>`, 146, 400);
  // software window
  const win = macWin(sc.el, 1040, 668, `<img src="assets/app-logo.png" style="width:24px;height:24px;border-radius:6px">示例软件 · Example App`);
  const FEAT = [['AI 匹配', '镜头 · 动画 · 音效 · 素材 · 一键自动匹配', 58.3], ['模板库', '预设 / 素材模板 / Lottie 动效 / 定制动画', 61.3]];
  const fts = FEAT.map((f, i) => { const e = mk(sc.el, `<div class="glassD" style="width:540px;padding:18px 26px;border-radius:18px"><div style="font:600 32px -apple-system,'PingFang SC';color:#fff">${f[0]}</div><div class="mono" style="font-size:19px;color:#8C8C8C;margin-top:4px">${f[1]}</div></div>`, 1262, 300 + i * 118); return e; });
  const ffb = mk(sc.el, `<div class="chip" style="background:rgba(36,98,234,.18);color:#6d9bff;border:1.5px solid rgba(109,155,255,.4);font:600 22px ui-monospace,monospace">▶▶ 2.4×</div>`, 1262, 566);
  const tl = mk(sc.el, `<div class="mono" style="font-size:22px;color:#777">// 今年年初 · 一直在死磕</div>`, 146, 140);
  const ttl = mk(sc.el, `<div style="font:600 64px -apple-system,'PingFang SC';color:#fff">AI 自动剪辑工具</div>`, 146, 175);
  const why = mk(sc.el, `<div class="chip" style="background:#1d1d1d;color:#ddd;border:1.5px solid #333;font-size:28px">示例痛点 · 制作<span style="color:#E5484D">太费时间</span></div>`, 1262, 640);
  // takeover
  const opus = vtile(sc.el, 1180, 664, 16, 'box-shadow:0 0 0 3px #2462EA,0 40px 120px rgba(36,98,234,.45)');
  const upd = mk(sc.el, `<div class="chip" style="background:var(--blue);color:#fff;font-size:30px;padding:12px 28px">对比组 A · 这波版本更新</div>`, 960, 150, { ax: .5, ay: .5 });
  const lanes = mk(sc.el, `<div style="position:relative;width:1628px;height:300px">${['示例方案 A', '示例软件', '传统剪辑'].map((n, i) => `<div class="ln" style="position:absolute;left:0;top:${i * 100}px;width:100%;height:80px;border-radius:14px;background:#141414;border:1.5px solid #262626">
      <div class="lf" style="position:absolute;left:0;top:0;bottom:0;border-radius:14px;background:${i === 0 ? 'var(--blue)' : i === 1 ? '#3a3a3a' : '#262626'};width:0"></div>
      <div style="position:absolute;left:24px;top:0;line-height:80px;font:600 32px -apple-system,'PingFang SC';color:#fff">${n}</div><div class="mono lp" style="position:absolute;right:24px;top:0;line-height:80px;font-size:26px;color:#fff">P${i + 1}</div></div>`).join('')}</div>`, 146, 500);
  const lf = [...lanes.querySelectorAll('.lf')];
  const gj = words(sc.el, [{ h: '赛道格局，', t: 67.5 }, { h: '改写。', t: 68.3, k: 'slam', st: 'color:#6d9bff' }], 146, 290, 'h1', { style: 'color:#fff;font-size:120px' });
  const R = race(sc.el);
  sc.update = t => {
    T(t);
    // intro: cam big centre-right, words left
    const toSmall = EZ.inout(pr(t, 57.4, 58.1));
    const hand = pr(t, 57.85, 58.1);
    cam._sm = toSmall; camAt(cam, t, { x: lerp(1520, 1745, toSmall), y: lerp(505, 880, toSmall), o: 1 - hand, s: lerp(.9, .3, toSmall) });
    cam.firstChild.style.borderRadius = lerp(28, 120, toSmall) + 'px';
    camAt(camR, t, { x: 1745, y: 880, o: hand, s: .75 });
    wordsAt(s1, t, { out: 55.3 });
    show(s2, t, 54.87, { k: 'slam', out: 55.3 });
    ckP.forEach((p, i) => p.setAttribute('stroke-dashoffset', ((i ? 100 : 300) * (1 - EZ.out(pr(t, 54.95 + i * .1, 55.2 + i * .1)))).toFixed(1)));
    show(id, t, 55.4, { k: 'left', out: 57.45 });
    show(tl, t, 57.63, { k: 'left', out: 66.2 }); show(ttl, t, 57.9, { k: 'up', out: 66.2 });
    // window
    const wIn = EZ.spring(pr(t, 57.9, 58.8)), wOut = EZ.inout(pr(t, 66.3, 67.0));
    // recording 14–17s (AI 匹配) at 1×, then 34–46s (模板库) sped up to fit 61.3 → 66.3 (12s in 5s ≈ 2.4×)
    if (t < 61.3) setFrame(win._img, seqAt('soft_match', 90, 30 * (3 / 3.4), t, 57.9, false));
    else setFrame(win._img, seqAt('soft_tpl', 360, 30 * 12 / 5, t, 61.3, false));
    place(win, { x: 640 + (1 - wIn) * -80, y: 600 + (1 - wIn) * 120, o: clamp(wIn * 3) * (1 - wOut), s: (.80 + .06 * wIn) * (1 - .12 * wOut), blur: wOut * 10 });
    fts.forEach((e, i) => { show(e, t, FEAT[i][2], { k: 'right', dist: 90, out: 66.2 }); if (t >= (FEAT[i + 1] || [0, 0, 999])[2]) e.style.opacity = (+e.style.opacity * .45).toFixed(3); });
    show(ffb, t, 61.45, { k: 'pop', out: 66.2 });
    show(why, t, 61.27, { k: 'up', out: 66.2 });
    // takeover by 对比组 A update
    const oIn = EZ.inout(pr(t, 66.37, 67.0));
    setFrame(opus._img, seqAt('opus_hero', 960, 60, t, 66.37 - 4));
    place(opus, { x: 960, y: 560, o: clamp(oIn * 2) * (1 - pr(t, 67.3, 67.6)), s: lerp(1.25, .9, oIn) - .1 * pr(t, 67.3, 67.6), blur: (1 - oIn) * 12 });
    show(upd, t, 66.55, { k: 'pop', out: 67.35 });
    show(lanes, t, 67.4, { k: 'up' });
    const L = [EZ.out(pr(t, 67.6, 68.6)) * 1, .56 + 0 * t, .3];
    lf.forEach((e, i) => { const p = i === 0 ? L[0] : i === 1 ? .56 * clamp((t - 67.45) * 4) : .3 * clamp((t - 67.5) * 4); e.style.width = (p * 100) + '%'; });
    wordsAt(gj, t);
    raceAt(R, t, 1 - pr(t, 57.8, 58.2) + pr(t, 66.3, 66.8));
  };
  sc.cam = t => { const [sx, sy] = shake(t, 54.87, .4, 16); return { x: 960, y: 540, sx, sy, z: 1 + .02 * EZ.out(pr(t, 58, 66)) }; };
  S(52.7, 'whoosh', .5); S(54.1, 'tick', .4); S(54.87, 'crack', 1); S(54.87, 'hit', .8); S(55.4, 'swipe', .5);
  S(57.9, 'card', .6); FEAT.forEach((f, i) => S(f[2], 'click', .6, .5)); FEAT.forEach((f, i) => S(f[2] + .05, 'card', .4, .6)); S(61.27, 'pop', .4); S(61.45, 'ff', .35, 0, { d: 1.2 });
  S(66.37, 'whoosh', .9); S(66.4, 'shine', .6); S(67.4, 'slide', .4, 0, { d: .6 }); S(67.6, 'fill_up', .5, 0, { d: 1.0 }); S(68.3, 'hit', .9);
})();

/* =========================================================
   S6  69.40 – 78.10  快车道：迭代速度 · 对比组 B 和对比组 C跟上 · 启动 AI 账号
   ========================================================= */
(() => {
  const sc = new Scene(69.40, 78.10, 'var(--blue)', { grid: 'gridB', trans: 'wipe', tc: '#2462EA' });
  const T = tags(sc, '// 06 — 快车道');
  const cam = camCard(sc.el, 250, 250, '', true);
  const h = words(sc.el, [{ h: '大模型的', t: 69.45 }, { h: '迭代速度', t: 70.2 }], 146, 140, 'h2', { style: 'color:#fff' });
  // release timeline, ticks getting denser
  const TICKS = [0, .22, .38, .5, .6, .68, .75, .8, .85, .89, .92, .95, .97, .99];
  const tlx = mk(sc.el, `<div style="position:relative;width:1628px;height:120px"><div style="position:absolute;left:0;right:0;top:58px;height:3px;background:rgba(255,255,255,.35)"></div>
     ${TICKS.map((p, i) => `<div class="tk" style="position:absolute;left:${p * 100}%;top:40px;width:4px;height:40px;background:#fff;border-radius:2px;opacity:0"></div>`).join('')}
     <div class="mono" style="position:absolute;left:0;top:92px;font-size:18px;color:rgba(255,255,255,.7)">2023</div><div class="mono" style="position:absolute;right:0;top:92px;font-size:18px;color:#fff">NOW</div></div>`, 146, 270);
  const tks = [...tlx.querySelectorAll('.tk')];
  // highway lanes
  const LN = [['示例方案 A', '#fff', '#2462EA', .82], ['对比组 B', 'rgba(255,255,255,.2)', '#fff', .64], ['对比组 C', 'rgba(255,255,255,.2)', '#fff', .55]];
  const hw = mk(sc.el, `<div style="position:relative;width:1628px;height:330px;overflow:hidden;border-radius:22px;background:rgba(10,10,10,.22)">
     <div class="sl" style="position:absolute;inset:0"></div>
     ${LN.map((l, i) => `<div style="position:absolute;left:0;right:0;top:${20 + i * 104}px;height:84px;border-bottom:2px dashed rgba(255,255,255,.18)"></div>
       <div class="car" style="position:absolute;left:0;top:${30 + i * 104}px;height:64px;border-radius:32px;padding:0 28px;display:flex;align-items:center;gap:12px;background:${l[1]};color:${l[2]};font:600 30px -apple-system,'PingFang SC';white-space:nowrap">${i === 0 ? '<span class="mono" style="font-size:22px">▶▶</span>' : '<span class="mono" style="font-size:22px">▶</span>'}${l[0]}</div>`).join('')}</div>`, 146, 420);
  const cars = [...hw.querySelectorAll('.car')], slEl = hw.querySelector('.sl');
  for (let i = 0; i < 26; i++) { const d = document.createElement('div'); d.style.cssText = `position:absolute;top:${(i * 53) % 330}px;height:2px;width:${120 + (i * 71) % 260}px;background:rgba(255,255,255,.5);border-radius:1px`; d._k = i; slEl.appendChild(d); }
  const sls = [...slEl.children];
  const fast = words(sc.el, [{ h: 'AI + 内容创作，', t: 73.43 }, { h: '驶入快车道。', t: 74.87, k: 'slam' }], 146, 790, 'h2', { style: 'color:#fff' });
  // account switch
  const acct = mk(sc.el, `<div style="width:1180px;background:#fff;border-radius:34px;padding:40px 46px 36px;box-shadow:0 40px 100px rgba(0,0,0,.35)">
     <div style="display:flex;align-items:center;gap:34px">
       <img src="assets/presenter.png" style="width:170px;height:170px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 6px #fff,0 0 0 9px #2462EA">
       <div style="flex:1"><div class="mono" style="font-size:20px;color:#8C8C8C">// 第一时间 · 启动</div>
         <div style="font:700 76px -apple-system,'PingFang SC';letter-spacing:-1.5px;line-height:1.1">示例<span style="color:var(--blue)">品牌</span></div>
         <div style="font:500 27px -apple-system,'PingFang SC';color:#3a3a3a;margin-top:6px">创作者简介 · 请按本期内容填写</div></div>
       <div class="sw" style="width:130px;height:74px;border-radius:37px;background:#E7E7E4;position:relative;flex:none"><div class="kn" style="position:absolute;top:7px;left:7px;width:60px;height:60px;border-radius:50%;background:#fff;box-shadow:0 4px 12px rgba(0,0,0,.25)"></div></div></div>
     <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:34px">
       ${[['开始时间', '第 <b class="sv0">0</b> 天'], ['消耗时间', '<b class="sv1">0</b> 小时'], ['粉丝数', '<b class="sv2">0</b>'], ['收入', '¥ <b class="sv3">0</b>']].map(([k, v], i) => `<div class="stc" style="background:#F4F4F2;border-radius:20px;padding:18px 22px;opacity:0"><div class="mono" style="font-size:19px;color:#8C8C8C">// ${k}</div><div style="font:600 46px -apple-system,'PingFang SC';margin-top:4px;color:${i === 2 ? 'var(--blue)' : '#0A0A0A'}">${v}</div></div>`).join('')}</div></div>`, 960, 560, { ax: .5, ay: .5 });
  const stc = [...acct.querySelectorAll('.stc')], sv = [0, 1, 2, 3].map(i => acct.querySelector('.sv' + i));
  const sw = acct.querySelector('.sw'), kn = acct.querySelector('.kn');
  const R = race(sc.el);
  sc.update = t => {
    T(t);
    camAt(cam, t, { x: 1745, y: 180, o: window.MACRO_IS_OPENING_SCENE ? 1 : EZ.out(pr(t, 69.5, 70)), s: .75 });
    wordsAt(h, t, { out: 75.75 });
    show(tlx, t, 69.6, { k: 'up', out: 75.75 });
    tks.forEach((e, i) => { const x = pr(t, 70.2 + i * .06 * (1 - i / 20), 70.35 + i * .06 * (1 - i / 20)); e.style.opacity = x; e.style.transform = `scaleY(${.3 + .7 * EZ.spring(x)})`; });
    show(hw, t, 70.95, { k: 'up', dist: 60, out: 75.75 });
    const sp = 1 + 5 * EZ.in(pr(t, 73.4, 74.9));
    cars.forEach((c, i) => {
      const p = i === 0 ? EZ.out(pr(t, 71.0, 72.2)) * LN[0][3] : EZ.out(pr(t, 71.0 + i * .5, 72.3 + i * .5)) * LN[i][3] + (i ? pr(t, 72.3, 73.4) * .08 : 0);
      c.style.transform = `translateX(${(p * 1628 - (i === 0 ? 400 : 260)) + Math.sin(t * 9 + i) * 2}px)`;
    });
    sls.forEach(d => { const L = 1628 + 400; const x = L - (((t - 70) * 380 * sp + d._k * 181) % L); d.style.transform = `translateX(${x - 300}px)`; d.style.opacity = .15 + .6 * pr(t, 73.4, 74.9); });
    wordsAt(fast, t, { out: 75.75 });
    show(acct, t, 75.85, { k: 'pop' });
    stc.forEach((e, i) => { const x = pr(t, 76.4 + i * .18, 76.75 + i * .18); e.style.opacity = x; e.style.transform = `translateY(${(1 - EZ.expo(x)) * 24}px)`; });
    sv[0].textContent = Math.round(counter(t, 76.4, 77.0, 0, 3)); sv[1].textContent = Math.round(counter(t, 76.6, 77.2, 0, 5)); sv[2].textContent = Math.round(counter(t, 76.8, 77.7, 0, 5822)); sv[3].textContent = '0';
    const on = EZ.spring(pr(t, 77.0, 77.45)); kn.style.left = (7 + 56 * on) + 'px'; sw.style.background = on > .5 ? '#28c840' : '#E7E7E4';
    raceAt(R, t);
  };
  sc.cam = t => { const [sx, sy] = shake(t, 74.87, .35, 10); return { x: 960, y: 540, sx, sy, z: 1 + .02 * EZ.in(pr(t, 73.4, 75.7)) }; };
  S(69.4, 'whoosh', .7); for (let i = 0; i < 14; i++) S(70.2 + i * .06 * (1 - i / 20), 'tick', .25, -.8 + i * .12);
  S(70.95, 'slide', .5, 0, { d: .9 }); S(71.0, 'whoosh', .5, .5); S(71.5, 'whoosh', .4, -.3); S(73.4, 'rise_s', .8); S(73.5, 'ff', .5, 0, { d: 1.4 });
  S(74.87, 'hit', .9); S(75.85, 'pop', .7); [0, 1, 2, 3].forEach(i => S(76.4 + i * .18, 'tick', .4, -.5 + i * .33)); S(76.8, 'counter', .35, 0, { d: .9 }); S(77.0, 'click', 1); S(77.05, 'ding', .7);
})();

/* =========================================================
   S7  78.10 – 89.70  一小时：以前一两天 → 现在一小时 · AI 开发之余 · 前沿技术 + 工作日常
   ========================================================= */
(() => {
  const sc = new Scene(78.10, 89.70, 'var(--paper)', { grid: 'grid', trans: 'circle', tc: '#F7F7F5', td: .5, cx: 1745, cy: 180 });   // expands out of the small cam
  const T = tags(sc, '// 07 — 一小时');
  const cam = camCard(sc.el, 250, 250, '', true);
  const h = words(sc.el, [{ h: '放在以前，', t: 78.2 }, { h: '做一条视频', t: 79.1 }], 146, 150, 'h2');
  const STEPS = [['写稿', 80.3], ['拍摄', 80.75], ['剪辑', 81.15]];
  const bar = mk(sc.el, `<div style="position:relative;width:1628px;height:130px">
     <div class="bb" style="position:absolute;left:0;top:0;height:130px;border-radius:22px;background:#0A0A0A;display:flex;overflow:hidden;width:0">
       <div class="one" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:700 44px -apple-system,'PingFang SC';color:#fff;opacity:0">1h</div>
       ${STEPS.map((s, i) => `<div class="st" style="flex:${[1, 1.2, 2.3][i]};display:flex;align-items:center;justify-content:center;font:600 42px -apple-system,'PingFang SC';color:#fff;border-right:${i < 2 ? '2px solid #333' : '0'};opacity:0">${s[0]}</div>`).join('')}</div>
     <div class="bl mono" style="position:absolute;right:0;top:150px;font-size:36px;font-weight:600;color:#0A0A0A">≈ 1–2 天</div></div>`, 146, 330);
  const one = bar.querySelector('.one'), bb = bar.querySelector('.bb'), sts = [...bar.querySelectorAll('.st')], bl = bar.querySelector('.bl');
  const now = mk(sc.el, `<div style="display:flex;align-items:baseline;gap:26px"><div class="mono" style="font-size:26px;color:#8C8C8C">现在 →</div><div style="font:700 150px -apple-system,'PingFang SC';letter-spacing:-4px;color:var(--blue)">1 小时</div></div>`, 146, 560);
  // 24h ring
  const ring = mk(sc.el, `<div style="position:relative;width:520px;height:520px">
     <svg width="520" height="520" viewBox="0 0 520 520" style="position:absolute;inset:0;transform:rotate(-90deg)">
       <circle cx="260" cy="260" r="210" fill="none" stroke="#E7E7E4" stroke-width="54"/>
       <circle class="rw" cx="260" cy="260" r="210" fill="none" stroke="#0A0A0A" stroke-width="54" stroke-dasharray="1319.5" stroke-dashoffset="1319.5"/>
       <circle class="ra" cx="260" cy="260" r="210" fill="none" stroke="#2462EA" stroke-width="64" stroke-dasharray="0 1319.5"/></svg>
     <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="mono" style="font-size:22px;color:#8C8C8C">// 每天 24h</div><div style="font:600 50px -apple-system,'PingFang SC'">AI 开发工作</div><div style="font:600 40px -apple-system,'PingFang SC';color:var(--blue)">+ 1h 示例创作者</div></div></div>`, 1470, 560, { ax: .5, ay: .5 });
  const rw = ring.querySelector('.rw'), ra = ring.querySelector('.ra');
  const work = mk(sc.el, `<div style="position:relative;width:420px;height:747px;border-radius:26px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.25)"><img style="width:100%;height:100%;object-fit:cover;display:block">
     <div class="mono" style="position:absolute;left:18px;top:16px;background:rgba(10,10,10,.6);color:#fff;font-size:19px;padding:6px 14px;border-radius:30px">// 日常 · AI 开发工作</div></div>`, 640, 520, { ax: .5, ay: .5 });
  const workImg = work.querySelector('img');
  // 6. coding.mov (1.97s) on "工作的日常" 87.47–89.4 — slides in over the right side
  const cod = mk(sc.el, `<div style="position:relative;width:880px;height:495px;border-radius:24px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.3)"><img style="width:100%;height:100%;object-fit:cover;display:block">
     <div class="mono" style="position:absolute;left:18px;top:16px;background:rgba(10,10,10,.6);color:#fff;font-size:19px;padding:6px 14px;border-radius:30px">// 工作的日常</div></div>`, 1400, 540, { ax: .5, ay: .5 });
  const codImg = cod.querySelector('img');
  const out1 = mk(sc.el, `<div style="font:600 64px -apple-system,'PingFang SC'">每天一小时，输出：</div>`, 146, 330);
  const tg = [['前沿 AI 技术分享', 86.27], ['工作的日常', 87.47]].map((x, i) => mk(sc.el, `<div class="card" style="width:720px;height:150px"><div class="lb">// ${String(i + 1).padStart(2, '0')}</div><div style="position:absolute;left:28px;top:62px;font:600 52px -apple-system,'PingFang SC'">${x[0]}</div></div>`, 146, 470 + i * 176));
  const R = race(sc.el, false);
  sc.update = t => {
    T(t);
    camAt(cam, t, { x: 1745, y: 180, o: EZ.out(pr(t, 78.2, 78.7)), s: .75 });
    wordsAt(h, t, { out: 83.2 });
    show(bar, t, 80.25, { k: 'up', out: 83.2 });
    const g = EZ.out(pr(t, 80.3, 81.8)), cmp = EZ.inout(pr(t, 82.15, 82.9));
    bb.style.width = (1628 * g * (1 - .88 * cmp)) + 'px';
    sts.forEach((e, i) => e.style.opacity = pr(t, STEPS[i][1], STEPS[i][1] + .25) * (1 - cmp));
    bb.style.background = cmp > .5 ? 'var(--blue)' : '#0A0A0A'; one.style.opacity = pr(cmp, .7, 1);
    bl.style.opacity = pr(t, 81.43, 81.7) * (1 - cmp); bl.style.textDecoration = t > 82.0 ? 'line-through' : 'none';
    show(now, t, 82.4, { k: 'slam', out: 83.25 });
    show(ring, t, 83.37, { k: 'pop', out: 87.3 });
    show(work, t, 83.3, { k: 'up', dist: 90, out: 85.05, oy: 60, s: .9 }); setFrame(workImg, seqAt('work', 122, 122 / 2.0, t, 83.3, false));
    show(cod, t, 87.4, { k: 'right', dist: 200, out: 89.45 }); setFrame(codImg, seqAt('coding', 59, 30 * 59 / 30 / 2.0, t, 87.4, false));
    rw.setAttribute('stroke-dashoffset', (1319.5 * (1 - EZ.inout(pr(t, 83.45, 84.6)))).toFixed(1));
    const a = EZ.spring(pr(t, 85.1, 85.7)); ra.setAttribute('stroke-dasharray', `${(1319.5 / 24 * a).toFixed(1)} 1319.5`);
    show(out1, t, 85.2, { k: 'up', out: 89.4 });
    tg.forEach((e, i) => show(e, t, [86.27, 87.47][i], { k: 'left', out: 89.4 }));
    raceAt(R, t);
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 + .02 * EZ.out(pr(t, 78, 89)) });
  S(78.1, 'whoosh', .6); STEPS.forEach(s => S(s[1], 'pop', .5)); S(81.43, 'tick', .5); S(82.0, 'slash', .5); S(82.15, 'suck', .6, 0, { d: .8 }); S(82.4, 'hit', .9);
  S(83.37, 'pop', .6); S(83.37, 'card', .5, -.2); S(83.45, 'fill', .35, 0, { d: 1.1 }); S(87.4, 'swipe', .6, .5); S(85.1, 'ding', .7); S(86.27, 'card', .5, -.4); S(87.47, 'card', .5, -.4);
})();

/* =========================================================
   S8  89.70 – 102.92  收尾：新时代 · 对手产能×10 vs 一帧一帧 · 行动 · 留言
   ========================================================= */
(() => {
  const sc = new Scene(89.70, 102.92, '#0A0A0A', { grid: 'gridD', trans: 'flash', td: .3, fa: .5 });
  const T = tags(sc, '// 08 — 行动', '', true);
  const cam = camCard(sc.el, 470, 836);
  const k0 = mk(sc.el, `<div class="mono" style="font-size:26px;color:#777">// 最后，掏句心窝子</div>`, 146, 290);
  const n1 = words(sc.el, [{ h: '内容创作的', t: 91.85 }, { h: '新时代，', t: 92.3 }], 146, 350, 'h1', { style: 'color:#fff' });
  const n2 = words(sc.el, [{ h: '真的', t: 92.85 }, { h: '来了。', t: 93.15, k: 'slam', st: 'color:#6d9bff' }], 146, 480, 'h1', { style: 'color:#fff;font-size:150px' });
  // rival x10 vs frame by frame
  const riv = mk(sc.el, `<div style="position:relative;width:1080px;height:560px">
     <div class="mono" style="position:absolute;left:0;top:0;font-size:22px;color:#777">// 产能对比</div>
     <div style="position:absolute;left:0;top:60px;width:300px;font:600 36px -apple-system,'PingFang SC';color:#fff">你的对手 <span class="mono" style="font-size:22px;color:#6d9bff">+ AI</span></div>
     <div class="rb" style="position:absolute;left:300px;top:60px;height:70px;border-radius:14px;background:var(--blue);width:0"></div>
     <div class="rx mono" style="position:absolute;left:320px;top:66px;font-size:48px;font-weight:700;color:#fff">×1</div>
     <div style="position:absolute;left:0;top:250px;width:300px;font:600 36px -apple-system,'PingFang SC';color:#fff">你</div>
     <div style="position:absolute;left:300px;top:230px;width:760px;height:110px;border-radius:12px;background:#141414;border:1.5px solid #2a2a2a;overflow:hidden">
       <div class="fs" style="position:absolute;top:14px;left:14px;display:flex;gap:8px">${Array.from({ length: 30 }, (_, i) => `<div style="width:118px;height:80px;border-radius:6px;background:#222;border:1.5px solid #333"></div>`).join('')}</div></div>
     <div class="fc mono" style="position:absolute;left:300px;top:352px;font-size:22px;color:#777">frame 0001 · 还在一帧一帧地磕</div></div>`, 146, 290);
  const rb = riv.querySelector('.rb'), rx = riv.querySelector('.rx'), fsE = riv.querySelector('.fs'), fcE = riv.querySelector('.fc');
  // action button
  const btn = mk(sc.el, `<div style="display:flex;align-items:center;gap:22px;background:var(--blue);color:#fff;border-radius:60px;padding:30px 60px;box-shadow:0 30px 90px rgba(36,98,234,.6);font:700 64px -apple-system,'PingFang SC'"><span class="mono" style="font-size:44px">▶</span>和 AI 一起，行动起来</div>`, 700, 540, { ax: .5, ay: .5 });
  // end card
  const endc = mk(sc.el, `<div style="width:1920px;height:1080px;background:var(--paper)"><div class="grid" style="position:absolute;inset:0"></div></div>`, 0, 0);
  const lg = mk(sc.el, `<div style="display:flex;align-items:center;gap:34px">
     <img src="assets/presenter.png" style="width:220px;height:220px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 7px #fff,0 0 0 10px #2462EA,0 20px 60px rgba(36,98,234,.3)">
     <div><div style="font:700 110px -apple-system,'PingFang SC';letter-spacing:-3px;line-height:1">示例<span style="color:var(--blue)">品牌</span></div>
     <div style="font:500 34px -apple-system,'PingFang SC';color:#6B6B6B;margin-top:14px">创作与技术 · 示例品牌说明</div></div></div>`, 146, 330);
  const cm = mk(sc.el, `<div style="display:flex;align-items:center;gap:18px;background:#fff;border:1.5px solid #E7E7E4;border-radius:22px;padding:22px 30px;box-shadow:0 20px 50px rgba(0,0,0,.08)">
     <div style="width:56px;height:56px;border-radius:50%;background:#0A0A0A;color:#fff;display:flex;align-items:center;justify-content:center;font:600 28px -apple-system">💬</div>
     <div><div style="font:600 34px -apple-system,'PingFang SC'">有问题，评论区留言</div><div class="mono" style="font-size:20px;color:#8C8C8C">// 我会尽量解答</div></div></div>`, 146, 640);
  const bye = mk(sc.el, `<div style="font:700 72px -apple-system,'PingFang SC'">拜拜 <span style="color:var(--blue)">👋</span></div>`, 146, 800);
  const R = race(sc.el);
  sc.update = t => {
    T(t);
    const toEnd = EZ.inout(pr(t, 99.95, 100.5));
    const toSide = EZ.inout(pr(t, 93.55, 94.1)), back = EZ.inout(pr(t, 98.4, 98.9));
    camAt(cam, t, { x: lerp(lerp(1520, 1700, toSide), 1520, back) + lerp(0, 40, toEnd), y: lerp(lerp(505, 330, toSide), 505, back), o: 1, s: lerp(lerp(.9, .5, toSide), .9, back) });
    show(k0, t, 90.4, { k: 'left', out: 93.45 });
    wordsAt(n1, t, { out: 93.45 }); wordsAt(n2, t, { out: 93.47 });
    show(riv, t, 93.6, { k: 'up', out: 98.45 });
    const g = EZ.expo(pr(t, 95.4, 96.4)); rb.style.width = (40 + 720 * g) + 'px'; rx.textContent = '×' + Math.max(1, Math.round(1 + 9 * g)); rx.style.left = (320 + 720 * g) + 'px';
    const fr = Math.floor(clamp(t - 96.5, 0, 3) * 3); fsE.style.transform = `translateX(${-fr * 126}px)`; fcE.textContent = `frame ${String(1 + fr).padStart(4, '0')} · 还在一帧一帧地磕`;
    show(btn, t, 98.6, { k: 'pop', out: 99.95 });
    btn.style.transform += ` scale(${1 - .06 * Math.max(0, Math.sin(clamp((t - 99.2) / .25) * Math.PI))})`;
    place(endc, { o: toEnd });
    show(lg, t, 100.1, { k: 'up' }); show(cm, t, 100.4, { k: 'up' }); show(bye, t, 101.4, { k: 'pop' });
    cam.style.zIndex = toEnd > 0 ? '5' : '';
    raceAt(R, t, 1 - toEnd);
  };
  sc.cam = t => { const [sx, sy] = shake(t, 93.15, .35, 12); return { x: 960, y: 540, sx, sy, z: 1 + .02 * EZ.out(pr(t, 89.7, 99)) }; };
  S(89.7, 'whoosh', .5); S(90.4, 'tick', .4); S(91.85, 'tick', .4); S(93.15, 'hit', 1); S(93.6, 'card', .6);
  S(95.4, 'rise_s', .8); S(95.4, 'counter', .45, 0, { d: 1.0 }); S(96.4, 'ding', .6); for (let i = 0; i < 9; i++) S(96.5 + i / 3, 'tick', .3);
  S(98.6, 'pop', .8); S(99.2, 'enter', .9); S(99.25, 'hit', .9); S(100.1, 'swoosh', .5); S(100.4, 'msg', .6); S(101.4, 'chime', .7);
})();

/* =========================================================
   双语字幕（中 / 英）— 卡拉 OK 逐字变色，跟随口播进度
   位于底部，赛道进度条上方；背景自适应（白底用深字，黑/蓝底用浅字）
   ========================================================= */
(() => {
  const ov = $('ov');
  const box = document.createElement('div');
  box.style.cssText = 'position:absolute;left:0;right:0;top:872px;display:flex;flex-direction:column;align-items:center;gap:8px;pointer-events:none';
  box.innerHTML = `<div class="sz" style="display:inline-block;padding:8px 26px 6px;border-radius:14px;font:600 44px -apple-system,'PingFang SC',sans-serif;letter-spacing:1px;white-space:nowrap"></div>
                   <div class="se" style="display:inline-block;padding:4px 20px;border-radius:10px;font:500 26px -apple-system,'SF Pro Text',sans-serif;letter-spacing:.2px;white-space:nowrap"></div>`;
  ov.appendChild(box);
  const zE = box.querySelector('.sz'), eE = box.querySelector('.se');
  zE.style.cssText += ";-webkit-text-stroke:4px rgba(10,10,10,.9);paint-order:stroke fill;text-shadow:none;background:transparent";
  eE.style.cssText += ";-webkit-text-stroke:2.6px rgba(10,10,10,.85);paint-order:stroke fill;text-shadow:none;background:transparent";
  let cur = -1, zc = [], ew = [];
  const clean = s => s.replace(/\s+/g, ' ');
  // progress of a group at time t, 0..1 over its characters, following SRT cue spans
  function prog(g, t) {
    const tot = g.sp.reduce((a, s) => a + Math.max(1, s[2]), 0); let acc = 0;
    for (const [a, b, n] of g.sp) {
      const w = Math.max(1, n);
      if (t < a) return acc / tot;
      if (t < b) return (acc + w * (t - a) / (b - a)) / tot;
      acc += w;
    }
    return 1;
  }
  function bgAt(t) {                       // which background is under the subtitle band
    const sc = SCENES.filter(s => t >= s.s && t < s.e).pop(); if (!sc) return 'dark';
    const bg = sc.el.style.background;
    if (bg.includes('36, 98, 234') || bg.includes('--blue')) return 'blue';
    if (bg.includes('paper') || bg.includes('247')) return 'light';
    return 'dark';
  }
  window.OVERLAY = t => {
    const i = SUBS.findIndex(g => t >= g.t0 - .05 && t < g.t1 + .05);
    if (i < 0) { box.style.opacity = 0; return; }
    const g = SUBS[i];
    if (i !== cur) {
      cur = i;
      zE.innerHTML = [...clean(g.zh)].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join('');
      eE.innerHTML = clean(g.en).split(' ').map(w => `<span>${w}</span>`).join(' ');
      zc = [...zE.children]; ew = [...eE.children];
    }
    // unified style everywhere: solid white text + thin dark stroke (no plate, no halo).
    // karaoke = spoken chars white, current char accent, upcoming chars light grey — all stay opaque and outlined
    const hot = '#6d9bff';
    const n = zc.length, pos = prog(g, t) * n;
    zc.forEach((c, k) => {
      const x = clamp(pos - k);
      c.style.color = x >= 1 ? '#FFFFFF' : x > 0 ? hot : '#C9C9C9';
      c.style.display = 'inline-block';
      c.style.transform = x > 0 && x < 1 ? `translateY(${(-3 * Math.sin(x * Math.PI)).toFixed(1)}px)` : '';
    });
    const m = ew.length, pe = prog(g, t) * m;
    ew.forEach((w, k) => { const x = clamp(pe - k); w.style.color = x >= 1 ? '#FFFFFF' : x > 0 ? hot : '#C9C9C9'; });
    // group in/out
    const a = pr(t, g.t0 - .05, g.t0 + .12), b = 1 - pr(t, g.t1 - .08, g.t1 + .05);
    box.style.opacity = Math.min(a, b).toFixed(3);
    box.style.transform = `translateY(${((1 - EZ.out(a)) * 10).toFixed(1)}px)`;
    // hide during the full-screen end card last beat? keep; hide only when opacity of fade overlay is high
  };
})();

/* =========================================================
   S9  102.92 – 108.40  本视频制作说明 · 核心提示词（口播结束后）
   ========================================================= */
(() => {
  const sc = new Scene(102.92, 108.40, '#0A0A0A', { grid: 'gridD', trans: 'flash', td: .3, fa: .4 });
  const T = tags(sc, '// 09 — 制作说明', '', true);
  const head = words(sc.el, [{ h: '制作工具：&nbsp;', t: 103.15 }, { h: '示例方案 A', t: 103.45, st: 'color:#6d9bff' }, { h: '&nbsp;制作', t: 103.85 }], 146, 170, 'h2', { style: 'color:#fff' });
  const chips = mk(sc.el, `<div style="display:flex;gap:14px">
     <div class="chip" style="background:var(--blue);color:#fff;font-size:28px">adu-motion-video</div>
     <div class="chip" style="background:#1d1d1d;color:#ddd;border:1.5px solid #333;font-size:28px">动画 · 配乐 · 音效 全部由代码生成</div></div>`, 150, 300);
  const PROMPT = '使用 adu-motion-video，根据提供的文案、口播与素材制作横屏视频。选择现代图文动效，按语义编排动作，保留清楚的中英字幕，先检查短片再导出成片。';
  const term = mk(sc.el, `<div class="glassD" style="width:1628px;padding:30px 40px 36px">
     <div style="display:flex;align-items:center;gap:9px;margin-bottom:22px"><i style="width:13px;height:13px;border-radius:50%;background:#ff5f57;display:block"></i><i style="width:13px;height:13px;border-radius:50%;background:#febc2e;display:block"></i><i style="width:13px;height:13px;border-radius:50%;background:#28c840;display:block"></i>
       <span class="mono" style="margin-left:16px;font-size:20px;color:#777">// 核心提示词 · prompt</span></div>
     <div style="display:flex;gap:18px;align-items:flex-start"><span class="mono" style="font-size:40px;color:#6d9bff;line-height:1.55">›</span>
       <div class="pt" style="font:500 40px -apple-system,'PingFang SC';color:#fff;line-height:1.55;white-space:normal;letter-spacing:.5px;min-height:186px"></div></div></div>`, 146, 400);
  const pt = term.querySelector('.pt');
  const sig = mk(sc.el, `<div style="display:flex;align-items:center;gap:16px">
     <img src="assets/presenter.png" style="width:64px;height:64px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 3px #2462EA">
     <div style="font:600 32px -apple-system,'PingFang SC';color:#fff">示例<span style="color:#6d9bff">品牌</span><span class="mono" style="font-size:20px;color:#777;margin-left:18px">// 提示词可以直接复制去试</span></div></div>`, 146, 850);
  const T0 = 104.35, T1 = 106.75;
  sc.update = t => {
    T(t); place(sc._tags[1], { o: pr(t, 102.95, 103.2) });
    wordsAt(head, t); show(chips, t, 103.95, { k: 'up' });
    show(term, t, 104.1, { k: 'up', dist: 60 });
    const n = Math.floor(clamp((t - T0) / (T1 - T0)) * PROMPT.length);
    const cur = (t < T1 + .2 || Math.floor(t * 2.4) % 2) ? '<span style="display:inline-block;width:3px;height:40px;background:#6d9bff;vertical-align:-6px;margin-left:4px"></span>' : '';
    pt.innerHTML = PROMPT.slice(0, n).replace(/(对比组 A|16:9)/g, '<span style="color:#6d9bff">$1</span>') + (t >= T0 - .2 ? cur : '');
    show(sig, t, 107.0, { k: 'up' });
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 + .015 * EZ.out(pr(t, 102.92, 108.4)) });
  S(102.92, 'whoosh', .6); S(103.15, 'tick', .4); S(103.45, 'pop', .5); S(103.95, 'card', .5); S(104.1, 'card', .5);
  S(T0, 'typing', .45, 0, { d: T1 - T0 }); S(T1 + .05, 'enter', .6); S(107.0, 'ding', .5);
})();

/* VERT_MODE: ?vert → panel render for the 9:16 version (talk cards + subtitles hidden) */
if (new URLSearchParams(location.search).has('vert')) {
  const st = document.createElement('style'); st.textContent = '.cam{visibility:hidden!important} #ov{display:none!important}'; document.head.appendChild(st);
  window.OVERLAY = null;
}

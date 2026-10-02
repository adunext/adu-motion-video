((OUTPUT_SCENE,OUTPUT_FRAME,OUTPUT_TC,FORWARD_S) => {
const outer = new OUTPUT_SCENE(0,3.9,'#06070A',{});
const host = document.createElement('div');host.className='doubao-host';
host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML='<div data-doubao-node="world"></div><div data-doubao-node="fx"></div><div data-doubao-node="tk"></div><div data-doubao-node="front"></div><div data-doubao-node="hud"></div><div data-doubao-node="ov" style="position:absolute;inset:0;pointer-events:none"></div>';
const nodes=Object.fromEntries([...host.querySelectorAll('[data-doubao-node]')].map(e=>[e.dataset.doubaoNode,e]));
const HITS=[]; // selected groups do not use source-track beatK()
/* ---------- core helpers ---------- */
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, x) => a + (b - a) * x;
const pr = (t, a, b) => clamp((t - a) / (b - a));
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const noise = t => { const i = Math.floor(t), f = t - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };
const EZ = {
  out: x => 1 - Math.pow(1 - x, 3),
  out5: x => 1 - Math.pow(1 - x, 5),
  expo: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
  inout: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
  in: x => x * x * x,
  back: x => { const c1 = 1.6, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
  // critically-damped spring feel (Apple-like)
  spring: x => x >= 1 ? 1 : 1 - Math.exp(-7 * x) * Math.cos(8.5 * x) * (1 - x * 0.2),
};
const $ = id => nodes[id];
const fmt = n => Math.round(n).toLocaleString('en-US');

function mk(parent, html, x = 0, y = 0, opt = {}) {
  const d = document.createElement('div');
  d.className = 'e ' + (opt.cls || '');
  if (opt.style) d.style.cssText += opt.style;
  d.innerHTML = html; parent.appendChild(d);
  d._x = x; d._y = y; d._ax = opt.ax == null ? 0 : opt.ax; d._ay = opt.ay == null ? 0 : opt.ay;
  place(d, { o: 0 }); return d;
}
function img(parent, src, x, y, h, opt = {}) {
  return mk(parent, `<img src="assets/${src}" class="${opt.ic || 'ch'}" style="height:${h}px;display:block">`, x, y, Object.assign({ ax: .5, ay: 1 }, opt));
}
function place(e, o = {}) {
  const x = o.x == null ? e._x : o.x, y = o.y == null ? e._y : o.y;
  const s = o.s == null ? 1 : o.s, sx = (o.sx == null ? 1 : o.sx) * s, sy = (o.sy == null ? 1 : o.sy) * s;
  e.style.transform = `translate(${x.toFixed(2)}px,${y.toFixed(2)}px) translate(${-e._ax * 100}%,${-e._ay * 100}%) rotate(${(o.r || 0).toFixed(3)}deg) scale(${sx.toFixed(4)},${sy.toFixed(4)})`;
  e.style.transformOrigin = `${e._ax * 100}% ${e._ay * 100}%`;
  const op = o.o == null ? 1 : o.o;
  e.style.opacity = op.toFixed(3);
  e.style.visibility = op <= 0.002 ? 'hidden' : 'visible';
  e.style.filter = o.blur ? `blur(${o.blur.toFixed(2)}px)` : '';
}
/* entrance/exit presets */
function show(e, t, t0, opt = {}) {
  const d = opt.d || 0.55, x = pr(t, t0, t0 + d), k = opt.k || 'up';
  let o = clamp(x * 3), tx = 0, ty = 0, s = 1, r = opt.r || 0, blur = 0;
  const E = EZ.expo(x), dist = opt.dist || 50;
  if (k === 'up') { ty = (1 - E) * dist; blur = (1 - E) * 6; }
  if (k === 'down') { ty = -(1 - E) * dist; }
  if (k === 'left') { tx = -(1 - E) * (opt.dist || 160); }
  if (k === 'right') { tx = (1 - E) * (opt.dist || 160); }
  if (k === 'pop') { s = 0.6 + 0.4 * EZ.spring(x); o = clamp(x * 5); }
  if (k === 'zoom') { s = 1 + (1 - E) * 0.25; blur = (1 - E) * 14; }
  if (k === 'slam') { s = 1 + (1 - EZ.out5(x)) * 1.2; o = clamp(x * 5); blur = (1 - x) * 10; }
  if (k === 'blur') { blur = (1 - E) * 18; s = 1 + (1 - E) * .05; }
  if (k === 'mask') { o = 1; e.style.clipPath = `inset(${(1 - E) * 100}% 0 0 0)`; ty = (1 - E) * 30; }
  if (opt.out != null) {
    const y = pr(t, opt.out, opt.out + (opt.od || 0.35)), Y = EZ.in(y);
    o *= 1 - y; ty -= Y * (opt.oy || 0); tx += Y * (opt.ox || 0); s *= 1 - (opt.os || 0) * Y; blur += (opt.ob == null ? 8 : opt.ob) * Y;
  }
  place(e, { x: (opt.x == null ? e._x : opt.x) + tx, y: (opt.y == null ? e._y : opt.y) + ty, s: s * (opt.s || 1), r, o: o * (opt.o == null ? 1 : opt.o), blur, sx: opt.sx, sy: opt.sy });
  return x;
}
/* word-by-word text reveal. html segments separated by '|' ; returns element */
function words(parent, segs, x, y, cls = 'h1', opt = {}) {
  const e = mk(parent, `<div class="${cls}" style="${opt.style || ''}">${segs.map((s, i) => { const br = /<br>$/.test(s.h); const h = s.h.replace(/<br>$/, ''); return `<span class="w" style="display:inline-block;${s.st || ''}">${h}</span>${br ? '<br>' : ''}`; }).join('')}</div>`, x, y, { ax: opt.ax || 0, ay: opt.ay || 0 });
  e._w = [...e.querySelectorAll('.w')]; e._segs = segs; return e;
}
function wordsAt(e, t, opt = {}) {
  place(e, { o: opt.o == null ? 1 : opt.o, x: opt.x, y: opt.y, s: opt.s });
  e._w.forEach((w, i) => {
    const s = e._segs[i], t0 = s.t, x = pr(t, t0, t0 + (s.d || .45)), E = EZ.expo(x);
    let op = clamp(x * 3);
    let tf = `translateY(${((1 - E) * (s.k === 'slam' ? 0 : 38)).toFixed(1)}px)`;
    if (s.k === 'slam') tf += ` scale(${(1 + (1 - EZ.out5(x)) * .9).toFixed(3)})`;
    if (s.k === 'pop') tf = `scale(${(0.5 + 0.5 * EZ.spring(x)).toFixed(3)})`;
    if (opt.out != null) { const y = pr(t, opt.out + i * (opt.stag || 0.02), opt.out + i * (opt.stag || 0.02) + .3); op *= 1 - y; tf += ` translateY(${(-EZ.in(y) * 30).toFixed(1)}px)`; }
    w.style.opacity = op.toFixed(3); w.style.transform = tf;
    w.style.filter = x < 1 ? `blur(${((1 - E) * 10).toFixed(1)}px)` : '';
  });
}
/* scenes */
const SCENES = [];
class Scene {
  constructor(s, e, bg, opt = {}) {
    this.s = s; this.e = e; this.opt = opt;
    this.el = document.createElement('div'); this.el.className = 'sc'; this.el.style.background = bg; $('world').appendChild(this.el);
    if (opt.grid) { const g = document.createElement('div'); g.className = opt.grid; this.el.appendChild(g); this.gridEl = g; }
    SCENES.push(this);
  }
  update(t) { }
  cam(t) { return null; }
}
function tags(sc, left, time, dark = false) {
  const c = dark ? 'color:#5c5c5c' : sc.el.style.background.includes('36, 98, 234') ? 'color:rgba(255,255,255,.65)' : '';
  const a = mk(sc.el, `<div class="tag" style="${c}">${left}</div>`, 64, 52);
  const b = mk(sc.el, `<div class="tag tc" style="${c}"><b class="brand" style="font-weight:inherit"></b>&nbsp;&nbsp;<span></span></div>`, 1856, 52, { ax: 1 });
  b.querySelector('.brand').textContent = CONFIG.brand || '';
  sc._tags = [a, b];
  return (t) => { place(a, { o: pr(t, sc.s + .05, sc.s + .3) }); place(b, { o: pr(t, sc.s + .05, sc.s + .3) }); b.querySelector('span').textContent = tc(t); };
}
const tc = t => { const fps = CONFIG.fps || 60, frame = Math.floor(t * fps + 1e-6), sec = Math.floor(frame / fps); return [Math.floor(sec / 3600), Math.floor(sec / 60) % 60, sec % 60, frame % fps].map(n => String(n).padStart(2, '0')).join(':'); };
// idle bob for characters
const bob = (t, k = 0, a = 5) => Math.sin(t * 2.2 + k) * a;
const breathe = (t, k = 0) => 1 + Math.sin(t * 2.0 + k) * 0.006;
/* character "hop-swap": when pose changes, squash & pop. returns scale factors */
function hopIn(t, t0, dur = .45) { const x = pr(t, t0, t0 + dur); return { s: 0.85 + 0.15 * EZ.spring(x), o: clamp(x * 6), y: (1 - EZ.spring(x)) * 40 }; }
function shake(t, t0, dur = .4, amp = 10) { const x = pr(t, t0, t0 + dur); if (x <= 0 || x >= 1) return [0, 0]; const k = (1 - x) * amp; return [k * noise(t * 45), k * noise(t * 45 + 9)]; }
function counter(t, t0, t1, v0, v1, ease = EZ.out) { return lerp(v0, v1, ease(pr(t, t0, t1))); }

/* SFX cue list collected from scenes (read by audio synth) */
const SFX = [];
function S(t, type, g = 1, p = 0, x = {}) { SFX.push(Object.assign({ t: +t.toFixed(3), type, g, p }, x)); }

/* ---- video-frame helper: returns promise when all pending frame imgs loaded ---- */
const _pending = new Set();

function setFrame(imgEl, src) { OUTPUT_FRAME(imgEl, src); }
/* ---- talk (口播) frame mapping ----
   Preferred: talkmap.js defines TALKF (folder names) + TALKMAP[frame60] = [folderIdx, srcFrame1based]  (scripts/align_talk.py)
   Fallback:  a single pre-built sequence talk/t_00001.jpg … at CONFIG.fps (legacy single-sequence layout) */
const HAS_MAP = typeof TALKMAP !== 'undefined' && Array.isArray(TALKMAP) && TALKMAP.length > 0;
const TALK_N = HAS_MAP ? TALKMAP.length : (CONFIG.talkFrames || 0);
const talkSrc = t => { t = window.MACRO_OUTPUT_T ?? t;
  if (!TALK_N) {
    if (CONFIG.demo === true) return 'assets/demo-presenter.svg';
    throw Error('No talk frames: prepare talkmap.js + talk/ or set talkFrames for a legacy sequence. Use demo:true only for an explicitly labeled preview.');
  }
  const i = clamp(Math.floor(t * CONFIG.fps + 1e-6), 0, TALK_N - 1);
  if (!HAS_MAP) return `talk/t_${String(i + 1).padStart(5, '0')}.jpg`;
  const m = TALKMAP[i]; return `talk/${TALKF[m[0]]}/f_${String(m[1]).padStart(5, '0')}.jpg`;
};
/* frame-sequence helper: dir, frame count, fps, time, start time, loop */
const seqSrc = (dir, i, n) => `sc/${dir}/f_${String(clamp(i, 1, n)).padStart(4, '0')}.jpg`;
function seqAt(dir, n, fps, t, t0, loop = true) { let i = Math.floor((t - t0) * fps + 1e-6); i = loop ? ((i % n) + n) % n : clamp(i, 0, n - 1); return seqSrc(dir, i + 1, n); }

/* ================= shared layout and motion building blocks ================= */
function camCard(parent, w, h, label = '// on air · ' + (CONFIG.account || 'Presenter'), round = false) {
  const e = mk(parent, `<div class="cam${round ? ' round' : ''}" style="width:${w}px;height:${h}px"><img>${round ? '' : `<div class="lab"><span style="color:#6d9bff">●</span> ${label}</div>`}</div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('img'); return e;
}
function faceAt(t) { t = window.MACRO_OUTPUT_T ?? t;
  const fallback = { cx: .5, cy: .42, h: .28 };
  if (typeof FACE === 'undefined' || !HAS_MAP || !TALK_N) return fallback;
  const m = TALKMAP[clamp(Math.floor(t * CONFIG.fps + 1e-6), 0, TALK_N - 1)];
  const F = m && FACE[TALKF[m[0]]];
  if (!F || !Array.isArray(F.f) || !F.f.length ||
      !['cx', 'cy', 'h'].every(k => Array.isArray(F[k]) && F[k].length === F.f.length)) return fallback;
  let lo = 0, hi = F.f.length - 1;
  while (hi - lo > 1) { const md = (lo + hi) >> 1; if (F.f[md] <= m[1]) lo = md; else hi = md; }
  const a = F.f[lo], b = F.f[hi], x = b > a ? clamp((m[1] - a) / (b - a)) : 0;
  const value = { cx: lerp(F.cx[lo], F.cx[hi], x), cy: lerp(F.cy[lo], F.cy[hi], x), h: lerp(F.h[lo], F.h[hi], x) };
  return Object.values(value).every(Number.isFinite) && value.h > 0 ? value : fallback;
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
  if (typeof WALL === 'undefined' || !Array.isArray(WALL) || !WALL.length) throw Error('Video wall needs prepared wall.js / sc/wall assets; omit this scene when no wall media is supplied');
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
     ${(CONFIG.race.labels).map((n, i) => `<div style="position:absolute;left:${i / (CONFIG.race.labels.length - 1) * 100}%;top:-5px;width:2px;height:12px;background:${c}"></div>`).join('')}
     <div class="rp" style="position:absolute;left:0;top:-7px;width:16px;height:16px;border-radius:50%;background:var(--blue);box-shadow:0 0 18px rgba(36,98,234,.9);transform:translateX(-50%)"></div></div>`, 146, 1058);
  e._p = e.querySelector('.rp'); return e;
}
const RACE_K = CONFIG.race.keys;
function raceAt(e, t, o = 1) {
  const NS = RACE_K.length - 2; let i = 0; while (i < NS && t >= RACE_K[i + 1]) i++;
  const p = i + clamp((t - RACE_K[i]) / (RACE_K[i + 1] - RACE_K[i]));
  e._p.style.left = Math.min(100, p / NS * 100) + '%'; place(e, { o });
}

/* core.js — 豆包集共享层：暗黑科技风「仪器台」
   画布发光（球体 / 地平线 / 弧环 / 尘埃 / 光束）、玻璃面板、全片同一张口播卡（弹簧形变）、HUD、颗粒 */
const BG = '#06070A', TX = '#EDEEF2', DIM = '#8B8F9A', CY = '#7CC8FF', BL = '#2462EA', BL2 = '#5B8CFF', AM = '#FFB648', RED = '#FF5A5F', GRN = '#3DDC84';
const FZ = "-apple-system,'PingFang SC',sans-serif";
const FE = "'Geist',-apple-system,'PingFang SC',sans-serif";
const FM = "'Geist Mono',ui-monospace,'PingFang SC',monospace";
const NF = {};
const EPS = [];
const FLASH = [];   // [t, amount, dur]：闪白
const frameIdx = t => Math.floor(t * 60 + 1e-6);
const rnd = (i, k = 0) => hash(i * 13.37 + k * 71.1);

/* ---------- 小工具 ---------- */
function tx(parent, html, x, y, o = {}) {
  const st = `font:${o.w || 600} ${o.size || 40}px/${o.lh || 1.15} ${o.ff || FZ};color:${o.col || TX};letter-spacing:${o.ls == null ? 0 : o.ls}px;${o.style || ''}`;
  return mk(parent, `<div style="${st}">${html}</div>`, x, y, { ax: o.ax || 0, ay: o.ay || 0 });
}
function mono(parent, html, x, y, o = {}) { return tx(parent, html, x, y, Object.assign({ ff: FM, w: 500, size: 18, col: DIM, ls: 2.5 }, o)); }
function scene(s, e, opt = {}) {
  const sc = new Scene(s, e, 'transparent', opt);
  sc.fr = document.createElement('div'); sc.fr.className = 'sc'; $('front').appendChild(sc.fr);
  return sc;
}
function clip(parent, dir, w, h, r = 14, extra = '') { const e = vtile(parent, w, h, r, extra); e._dir = dir; return e; }
function clipAt(e, t, t0, o, opt = {}) {
  if (o) place(e, o);
  if (o && (o.o == null ? 1 : o.o) <= .002) return;
  const n = NF[e._dir], fps = opt.fps || 30; let i = Math.floor((t - t0) * fps + 1e-6) + (opt.off || 0);
  if (opt.hold) i = clamp(i, 0, n - 1);
  else if (opt.pp) { const m = 2 * (n - 1); i = ((i % m) + m) % m; if (i >= n) i = m - i; } else i = ((i % n) + n) % n;
  setFrame(e._img, `sc/${e._dir}/f_${String(i + 1).padStart(4, '0')}.jpg`);
}
function setHTML(el, s) { if (el._h !== s) { el._h = s; el.innerHTML = s; } }
function typeAt(el, full, t, t0, t1, cur = true) {
  const ch = [...full].map(c => c === '\n' ? '<br>' : c), n = Math.floor(clamp((t - t0) / (t1 - t0)) * ch.length + 1e-6);
  const c = cur && t >= t0 - .2 && t < t1 + .7 && Math.floor(t * 3.2) % 2 === 0 ? `<span style="color:${CY}">▍</span>` : '';
  setHTML(el, ch.slice(0, n).join('') + c);
}
function slamAt(e, t, t0, o = {}) {
  const x = pr(t, t0, t0 + (o.d || .3)), E = EZ.out5(x);
  let op = clamp(x * 5);
  if (o.out != null) op *= 1 - pr(t, o.out, o.out + (o.od || .3));
  place(e, { x: o.x, y: o.y, s: (1 + (o.k || 1.3) * (1 - E)) * (o.s || 1), o: op * (o.o == null ? 1 : o.o), blur: (1 - E) * 14 + (o.out != null ? pr(t, o.out, o.out + .3) * 8 : 0), r: o.r || 0 });
  return x;
}
function stamp(parent, text, x, y, o = {}) {
  return mk(parent, `<div style="border:${o.bw || 6}px solid ${o.col || AM};color:${o.col || AM};border-radius:${o.br || 14}px;padding:${o.pad || '2px 26px'};font:700 ${o.size || 72}px/1.15 ${o.ff || FZ};letter-spacing:${o.ls == null ? 4 : o.ls}px;text-shadow:0 0 24px ${o.col || AM}66;box-shadow:0 0 30px ${o.col || AM}33,inset 0 0 20px ${o.col || AM}22">${text}</div>`, x, y, { ax: .5, ay: .5 });
}
function stampAt(e, t, t0, rot, o = {}) {
  const x = pr(t, t0, t0 + .26); let op = clamp(x * 6);
  if (o.out != null) op *= 1 - pr(t, o.out, o.out + .3);
  place(e, { x: o.x, y: o.y, s: (1 + 1.4 * (1 - EZ.out5(x))) * (o.s || 1), r: rot, o: op * (o.o == null ? 1 : o.o) });
}
function pill(html, o = {}) {
  return `<span style="display:inline-flex;align-items:center;gap:8px;padding:${o.pad || '7px 16px'};border-radius:${o.br || 40}px;background:${o.bg || 'rgba(255,255,255,.06)'};border:1px solid ${o.bd || 'rgba(255,255,255,.12)'};color:${o.col || TX};font:${o.w || 500} ${o.size || 20}px ${o.ff || FM};letter-spacing:${o.ls == null ? 1 : o.ls}px;white-space:nowrap;${o.style || ''}">${html}</span>`;
}
/* 双色大标题（参考视频左上角 THE SHAPE / OF A BOND） */
function title2(parent, a, b, x, y, o = {}) {
  const sz = o.size || 92;
  return mk(parent, `<div style="font:700 ${sz}px/1.08 ${FZ};letter-spacing:${o.ls == null ? -1 : o.ls}px">
    ${o.kick ? `<div style="font:500 16px ${FM};letter-spacing:4px;color:${DIM};margin-bottom:14px">${o.kick}</div>` : ''}
    <div class="l1" style="color:${TX}">${a}</div><div class="l2" style="background:linear-gradient(90deg,${o.c1 || CY},${o.c2 || BL2});-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 0 22px ${o.c1 || CY}55)">${b}</div></div>`, x, y, { ax: o.ax || 0, ay: o.ay || 0 });
}
function title2At(e, t, t0, out, o = {}) {      // 两行错峰：第一行上推，第二行稍后砸入
  const l1 = e.querySelector('.l1'), l2 = e.querySelector('.l2'), k = e.querySelector('div > div:first-child');
  place(e, { o: out == null ? 1 : 1 - pr(t, out, out + .3), blur: out == null ? 0 : pr(t, out, out + .3) * 10, x: o.x, y: o.y, s: o.s });
  const a = pr(t, t0, t0 + .5), b = pr(t, t0 + (o.gap || .18), t0 + (o.gap || .18) + .42);
  l1.style.transform = `translateY(${((1 - EZ.expo(a)) * 40).toFixed(1)}px)`; l1.style.opacity = clamp(a * 3).toFixed(3);
  l1.style.filter = a < 1 ? `blur(${((1 - EZ.expo(a)) * 10).toFixed(1)}px)` : '';
  const sl = o.slam ? 1 + (1 - EZ.out5(b)) * .7 : 1;
  l2.style.transform = `translateY(${((1 - EZ.expo(b)) * (o.slam ? 0 : 40)).toFixed(1)}px) scale(${sl.toFixed(3)})`; l2.style.transformOrigin = '0 60%';
  l2.style.opacity = clamp(b * 3).toFixed(3);
}

/* ---------- 玻璃面板 / 数据块 / 分段按钮 ---------- */
function glass(parent, w, h, x, y, o = {}) {
  return mk(parent, `<div class="gl" style="width:${w}px;height:${h}px;${o.style || ''}">${o.head ? `<div class="gh"><span>${o.head}</span><span style="color:#5d626d">${o.keys || ''}</span></div>` : ''}<div class="gb" style="${o.bst || ''}">${o.html || ''}</div></div>`, x, y, { ax: o.ax == null ? .5 : o.ax, ay: o.ay == null ? .5 : o.ay });
}
const statHTML = (k, v, o = {}) => `<div class="st" style="${o.style || ''}"><div class="k">${k}</div><div class="v" style="color:${o.col || CY}">${v}</div></div>`;
const segHTML = (items, o = {}) => `<div class="seg">${items.map((s, i) => `<span data-i="${i}">${s}</span>`).join('')}</div>`;
function segAt(root, idx) { root.querySelectorAll('.seg span').forEach((s, i) => { const on = i === idx; if (s._on !== on) { s._on = on; s.className = on ? 'on' : ''; } }); }
function slider(label, o = {}) {
  return `<div class="sl"><div class="slh"><span>${label}</span><b>${o.v || ''}</b></div><div class="slt"><i></i><u></u></div><div class="sll"><span>${o.a || ''}</span><span>${o.b || ''}</span></div></div>`;
}
function sliderAt(root, k, p, v) {
  const s = root.querySelectorAll('.sl')[k]; if (!s) return;
  s.querySelector('i').style.width = (p * 100).toFixed(1) + '%'; s.querySelector('u').style.left = (p * 100).toFixed(1) + '%';
  if (v != null) setHTML(s.querySelector('b'), v);
}

/* ---------- 画布：背景层（世界内）与前景层（粒子） ---------- */
const BGC = document.createElement('canvas'); BGC.width = 1920; BGC.height = 1080; BGC.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px';
$('world').appendChild(BGC); const bgx = BGC.getContext('2d');
let fgx = null;                                 // main.js 创建（叠在所有场景之上）

function bgBase(c, t, o = {}) {
  c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
  const g = c.createRadialGradient(o.cx || 960, o.cy || 600, 40, o.cx || 960, o.cy || 600, 1250);
  g.addColorStop(0, o.c0 || '#141821'); g.addColorStop(.55, o.c1 || '#0a0c11'); g.addColorStop(1, '#030405');
  c.fillStyle = g; c.fillRect(0, 0, 1920, 1080);
}
/* 地平线：亮线 + 地面反光 + 透视网格（参考视频的台面） */
function floor(c, t, y, k = 1, col = '255,196,120', o = {}) {
  if (k <= .002) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  const cx = o.cx || 960;
  let g = c.createRadialGradient(cx, y, 0, cx, y, 900); g.addColorStop(0, `rgba(${col},${.22 * k})`); g.addColorStop(1, `rgba(${col},0)`);
  c.setTransform(1, 0, 0, .16, 0, y * .84); c.fillStyle = g; c.fillRect(0, y - 900, 1920, 1800); c.setTransform(1, 0, 0, 1, 0, 0);
  g = c.createLinearGradient(cx - 900, 0, cx + 900, 0);
  g.addColorStop(0, `rgba(${col},0)`); g.addColorStop(.5, `rgba(${col},${.95 * k})`); g.addColorStop(1, `rgba(${col},0)`);
  c.fillStyle = g; c.fillRect(cx - 900, y - 1, 1800, 2.2);
  if (o.grid !== false) {
    c.strokeStyle = `rgba(${o.gcol || '120,170,255'},${.10 * k})`; c.lineWidth = 1;
    for (let i = -14; i <= 14; i++) { c.beginPath(); c.moveTo(cx + i * 22, y + 2); c.lineTo(cx + i * 260, 1100); c.stroke(); }
    const sp = (o.speed == null ? .35 : o.speed), ph = (t * sp) % 1;
    for (let j = 0; j < 9; j++) { const z = (j + ph) / 9, yy = y + Math.pow(z, 2.2) * (1100 - y); c.globalAlpha = clamp(z * 2) * k; c.beginPath(); c.moveTo(0, yy); c.lineTo(1920, yy); c.stroke(); }
    c.globalAlpha = 1;
  }
  c.restore();
}
/* 玻璃发光球（参考视频的轨道体） */
function ball(c, x, y, r, col, a = 1, o = {}) {
  if (a <= .002 || r <= .5) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  let g = c.createRadialGradient(x, y, r * .2, x, y, r * (o.halo || 2.1));
  g.addColorStop(0, `rgba(${col},${.30 * a})`); g.addColorStop(.5, `rgba(${col},${.10 * a})`); g.addColorStop(1, `rgba(${col},0)`);
  c.fillStyle = g; c.beginPath(); c.arc(x, y, r * (o.halo || 2.1), 0, 7); c.fill();
  g = c.createRadialGradient(x - r * .32, y - r * .38, r * .02, x, y, r);
  g.addColorStop(0, `rgba(255,255,255,${.85 * a})`); g.addColorStop(.22, `rgba(${col},${.55 * a})`); g.addColorStop(.75, `rgba(${col},${.16 * a})`); g.addColorStop(.96, `rgba(${col},${.55 * a})`); g.addColorStop(1, `rgba(${col},0)`);
  c.fillStyle = g; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill();
  if (o.lat) {               // 经纬线（玻璃壳）
    c.strokeStyle = `rgba(255,255,255,${.12 * a})`; c.lineWidth = 1;
    for (let i = 1; i < 4; i++) { c.beginPath(); c.ellipse(x, y, r, r * Math.abs(Math.cos(i * .78 + o.lat)), 0, 0, 7); c.stroke(); }
  }
  c.restore();
}
/* 点状弧环 + 刻度（参考视频的金色轨道弧） */
function arcRing(c, cx, cy, R, a0, a1, col, a = 1, o = {}) {
  if (a <= .002) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  const n = Math.max(2, Math.floor((a1 - a0) * R / (o.step || 9)));
  for (let i = 0; i <= n; i++) {
    const an = a0 + (a1 - a0) * i / n, big = i % (o.major || 6) === 0, rr = R + (big ? 10 : 0);
    c.strokeStyle = `rgba(${col},${(big ? .75 : .35) * a})`; c.lineWidth = big ? 2 : 1.2;
    c.beginPath(); c.moveTo(cx + Math.cos(an) * R, cy + Math.sin(an) * R); c.lineTo(cx + Math.cos(an) * (rr + 8), cy + Math.sin(an) * (rr + 8)); c.stroke();
  }
  c.strokeStyle = `rgba(${col},${.5 * a})`; c.lineWidth = 1.5; c.beginPath(); c.arc(cx, cy, R - 6, a0, a1); c.stroke();
  c.restore();
}
/* 漂浮尘埃（确定性，随 t 上漂） */
function dust(c, t, n, a = 1, o = {}) {
  if (a <= .002) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < n; i++) {
    const sx = rnd(i, 1) * 1920, sp = 8 + rnd(i, 2) * 26, y = ((rnd(i, 3) * 1200 - t * sp) % 1200 + 1200) % 1200 - 60;
    const x = sx + Math.sin(t * .4 + i) * 18, r = .6 + rnd(i, 4) * 1.8, tw = .45 + .55 * Math.sin(t * (1 + rnd(i, 5) * 2) + i);
    c.fillStyle = `rgba(${o.col || '170,205,255'},${(.25 + .5 * rnd(i, 6)) * tw * a})`; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill();
  }
  c.restore();
}
/* 光束：两点间渐亮线 + 流动光点 */
function beam(c, x1, y1, x2, y2, col, a = 1, t = 0, o = {}) {
  if (a <= .002) return;
  const p = o.p == null ? 1 : o.p, xe = lerp(x1, x2, p), ye = lerp(y1, y2, p);
  c.save(); c.globalCompositeOperation = 'lighter'; c.lineCap = 'round';
  c.strokeStyle = `rgba(${col},${.16 * a})`; c.lineWidth = (o.w || 2) * 5; c.beginPath(); c.moveTo(x1, y1); c.lineTo(xe, ye); c.stroke();
  c.strokeStyle = `rgba(${col},${.8 * a})`; c.lineWidth = o.w || 2; c.beginPath(); c.moveTo(x1, y1); c.lineTo(xe, ye); c.stroke();
  if (p >= 1 && o.flow !== false) for (let k = 0; k < (o.n || 3); k++) {
    const q = ((t * (o.speed || .8) + k / (o.n || 3)) % 1), qx = lerp(x1, x2, q), qy = lerp(y1, y2, q);
    const g = c.createRadialGradient(qx, qy, 0, qx, qy, 14); g.addColorStop(0, `rgba(255,255,255,${a})`); g.addColorStop(.3, `rgba(${col},${.7 * a})`); g.addColorStop(1, `rgba(${col},0)`);
    c.fillStyle = g; c.beginPath(); c.arc(qx, qy, 14, 0, 7); c.fill();
  }
  c.restore();
}
/* 爆散火花（t0 起，确定性） */
function burst(c, t, t0, x, y, o = {}) {
  const lt = t - t0; if (lt < 0 || lt > (o.life || 1.1)) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  const n = o.n || 40;
  for (let i = 0; i < n; i++) {
    const an = rnd(i, 7 + (o.seed || 0)) * 6.283, sp = (o.sp || 900) * (.35 + .65 * rnd(i, 8 + (o.seed || 0))), life = (o.life || 1.1) * (.5 + .5 * rnd(i, 9));
    if (lt > life) continue;
    const d = sp * (1 - Math.exp(-lt * 3)) / 3, px = x + Math.cos(an) * d, py = y + Math.sin(an) * d + lt * lt * (o.g || 120), al = 1 - lt / life;
    c.strokeStyle = `rgba(${o.col || '255,200,120'},${al})`; c.lineWidth = 2;
    c.beginPath(); c.moveTo(px, py); c.lineTo(px - Math.cos(an) * 14 * al, py - Math.sin(an) * 14 * al); c.stroke();
  }
  const g = c.createRadialGradient(x, y, 0, x, y, 220 * (1 - pr(lt, 0, .5) * .5)); g.addColorStop(0, `rgba(${o.col || '255,200,120'},${.55 * (1 - pr(lt, 0, .45))})`); g.addColorStop(1, 'rgba(0,0,0,0)');
  c.fillStyle = g; c.beginPath(); c.arc(x, y, 230, 0, 7); c.fill();
  c.restore();
}
/* 光柱 / 焦散（水下） */
function rays(c, t, a, o = {}) {
  if (a <= .002) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 9; i++) {
    const x = 160 + i * 210 + Math.sin(t * .5 + i * 1.7) * 60, w = 60 + rnd(i, 3) * 90, al = (.05 + .07 * (.5 + .5 * Math.sin(t * .8 + i * 2.3))) * a;
    const g = c.createLinearGradient(0, o.top || 0, 0, 1080); g.addColorStop(0, `rgba(150,210,255,${al})`); g.addColorStop(1, 'rgba(150,210,255,0)');
    c.fillStyle = g; c.beginPath(); c.moveTo(x - w * .3, o.top || 0); c.lineTo(x + w * .3, o.top || 0); c.lineTo(x + w * 1.6 + 120, 1080); c.lineTo(x - w * .6 + 120, 1080); c.fill();
  }
  c.restore();
}
const beatK = (t, win = .22) => { let k = 0; for (const [b, h] of HITS) { if (b > t) break; if (t - b < win) k = Math.max(k, h * (1 - (t - b) / win)); } return k; };
const voxAt = () => {
  const vox = window.DOUBAO_OUTPUT_VOX;
  if (!Array.isArray(vox) || !vox.length) throw Error('Run reviewed Doubao episode preparation on the imported voice');
  const frame = Math.floor((window.MACRO_OUTPUT_T || 0) * 60 + 1e-6);
  return vox[clamp(frame, 0, vox.length - 1)];
};

/* ---------- 口播主卡：全片同一张，关键帧之间弹簧形变 ---------- */
const LAY = {
  R: { x: 1500, y: 468, w: 470, h: 790, r: 26 },
  RS: { x: 1610, y: 470, w: 380, h: 640, r: 24 },
  L: { x: 400, y: 468, w: 470, h: 790, r: 26 },
  C: { x: 960, y: 450, w: 470, h: 790, r: 26 },
  RC: { x: 1716, y: 214, w: 230, h: 230, r: 115 },
  LC: { x: 210, y: 214, w: 230, h: 230, r: 115 },
  BIG: { x: 960, y: 452, w: 1100, h: 820, r: 30 },
};
const TKK = [];
function tkKey(t, L, d = .7, extra = {}) { TKK.push({ t, d, L: Object.assign({ o: 1, s: 1, rx: 0, ry: 0 }, typeof L === 'string' ? LAY[L] : L, extra) }); TKK.sort((a, b) => a.t - b.t); }
const TK = (() => {
  const e = document.createElement('div'); e.className = 'tkc'; $('tk').appendChild(e);
  e.innerHTML = `<img><div class="tsh"></div><div class="tlab"><i></i><span>${window.PACK_PRESENTER_LABEL}</span></div><div class="tcor"><b></b><b></b><b></b><b></b></div>`;
  return { e, im: e.querySelector('img'), lab: e.querySelector('.tlab'), dot: e.querySelector('.tlab i'), cor: e.querySelector('.tcor') };
})();
function tkLayout(t) {
  let i = -1; for (let k = 0; k < TKK.length; k++) if (t >= TKK[k].t) i = k;
  if (i < 0) return Object.assign({}, TKK[0].L);
  const K = TKK[i], P = i > 0 ? TKK[i - 1].L : K.L, x = pr(t, K.t, K.t + K.d), sp = EZ.spring(x), ou = EZ.out(x);
  const o = {};
  for (const k of ['x', 'y', 'rx', 'ry']) o[k] = lerp(P[k], K.L[k], sp);
  for (const k of ['w', 'h', 'r']) o[k] = Math.max(1, lerp(P[k], K.L[k], k === 'r' ? ou : sp));
  o.o = lerp(P.o, K.L.o, ou); o.s = lerp(P.s, K.L.s, sp);
  return o;
}
function tkUpdate(t) {
  const L = tkLayout(t), { e } = TK;
  const v = voxAt(t), w = L.w, h = L.h, s = L.s;
  e.style.width = w.toFixed(1) + 'px'; e.style.height = h.toFixed(1) + 'px'; e.style.borderRadius = Math.min(L.r, w / 2).toFixed(1) + 'px';
  e.style.transform = `translate(${(L.x - w / 2).toFixed(2)}px,${(L.y - h / 2).toFixed(2)}px) perspective(1600px) rotateX(${L.rx.toFixed(2)}deg) rotateY(${L.ry.toFixed(2)}deg) scale(${s.toFixed(4)})`;
  e.style.opacity = clamp(L.o).toFixed(3); e.style.visibility = L.o < .003 ? 'hidden' : 'visible';
  e.style.boxShadow = `0 0 0 1px rgba(255,255,255,.16),0 0 ${(26 + v * 40).toFixed(0)}px rgba(124,200,255,${(.10 + v * .22).toFixed(3)}),0 40px 90px rgba(0,0,0,.6)`;
  if (L.o < .003) return;
  setFrame(TK.im, talkSrc(t));
  const f = faceAt(t), a = h / w, kr = clamp((1.4 - a) / .4);
  const cover = Math.max(w / 720, h / 1280), want = (h * .42) / (f.h * 1280 * cover);
  const z = clamp(lerp(1, want, kr), 1, 2.4), iw = 720 * cover * z, ih = 1280 * cover * z;
  const ox = clamp(w / 2 - f.cx * iw, w - iw, 0), oy = clamp(h * lerp(.42, .55, kr) - f.cy * ih, h - ih, 0);
  TK.im.style.cssText = `left:${ox.toFixed(1)}px;top:${oy.toFixed(1)}px;width:${iw.toFixed(1)}px;height:${ih.toFixed(1)}px`;
  TK.lab.style.opacity = (1 - kr).toFixed(3); TK.cor.style.opacity = ((1 - kr) * .9).toFixed(3);
  TK.dot.style.background = Math.floor(t * 1.6) % 2 ? 'rgba(255,90,95,.35)' : RED;
}

/* ---------- HUD：章节标签 / 录制条 / 时间码 / 进度轨 / 颗粒 ---------- */
const CHAP = [];   // [t, '// 01 — 开场']，scenes.js 填写
const HUD = (() => {
  const h = $('hud');
  const scr = document.createElement('div'); scr.style.cssText = 'position:absolute;left:0;right:0;bottom:0;height:290px;background:linear-gradient(0deg,rgba(3,4,6,.82),rgba(3,4,6,.55) 45%,rgba(3,4,6,0))'; h.appendChild(scr);
  const vig = document.createElement('div'); vig.style.cssText = 'position:absolute;inset:0;background:radial-gradient(ellipse 75% 70% at 50% 48%,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)'; h.appendChild(vig);
  const grain = document.createElement('div'); grain.style.cssText = 'position:absolute;inset:0;background:url(assets/noise.png);opacity:.045;mix-blend-mode:screen'; h.appendChild(grain);
  const tag = mk(h, `<div style="font:500 19px ${FM};letter-spacing:2px;color:${DIM}"></div>`, 64, 46);
  const tcd = mk(h, `<div style="font:500 19px ${FM};letter-spacing:2px;color:${DIM}"><b style="font-weight:600;color:${TX}">${window.PACK_BRAND_HTML}</b>&nbsp;&nbsp;<span></span></div>`, 1856, 46, { ax: 1 });
  const rec = mk(h, `<div style="display:flex;align-items:center;gap:14px;padding:8px 18px;border-radius:40px;background:rgba(14,16,21,.72);border:1px solid rgba(255,255,255,.10);font:500 17px ${FM};color:${TX};letter-spacing:1.5px">
    <i style="width:10px;height:10px;border-radius:50%;background:${RED};display:block"></i><span class="rt">00:00</span><span style="color:#444">|</span><span style="color:${DIM}">TEMPLATE</span><span class="tp" style="color:${CY}">DARK·TECH</span></div>`, 960, 46, { ax: .5, ay: 0 });
  const tr = mk(h, `<div style="width:1792px;height:2px;background:rgba(255,255,255,.08);position:relative"><div class="tf" style="position:absolute;left:0;top:0;height:2px;background:linear-gradient(90deg,${BL},${CY});box-shadow:0 0 12px ${CY}"></div><div class="ticks"></div></div>`, 64, 1062);
  return { grain, tag, tcd, tcs: tcd.querySelector('span'), rec, rt: rec.querySelector('.rt'), dot: rec.querySelector('i'), tr, tf: tr.querySelector('.tf'), ticks: tr.querySelector('.ticks') };
})();
let HUD_OFF = [];   // [[t0,t1]] HUD 隐藏区间
function hudUpdate(t) {
  if (!HUD.ticks._done && CHAP.length) {
    HUD.ticks._done = 1; const E = window.END || CONFIG.end;
    HUD.ticks.innerHTML = window.MACRO_PLAN.scenes.map(s => `<i style="position:absolute;left:${(s.output_start_frame / window.MACRO_PLAN.end_frame * 100).toFixed(2)}%;top:-4px;width:2px;height:10px;background:rgba(255,255,255,.18)"></i>`).join('');
  }
  let c = CHAP[0]; for (const k of CHAP) if (t >= k[0]) c = k;
  setHTML(HUD.tag.firstChild, c ? c[1] : '');
  HUD.tcs.textContent = OUTPUT_TC(window.MACRO_OUTPUT_T);
  const sec = Math.floor(window.MACRO_OUTPUT_T); setHTML(HUD.rt, `${String(Math.floor(sec / 60)).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`);
  HUD.dot.style.opacity = Math.floor(t * 1.6) % 2 ? .3 : 1;
  HUD.tf.style.width = (window.MACRO_OUTPUT_T / (window.END || CONFIG.end) * 100).toFixed(2) + '%';
  let off = 0; for (const [a, b] of HUD_OFF) off = Math.max(off, Math.min(pr(t, a, a + .3), 1 - pr(t, b - .3, b)));
  for (const el of [HUD.tag, HUD.tcd, HUD.rec, HUD.tr]) place(el, { o: 1 - off });
  const fi = frameIdx(t); HUD.grain.style.backgroundPosition = `${Math.floor(rnd(fi, 1) * 256)}px ${Math.floor(rnd(fi, 2) * 256)}px`;
}

/* scenes.js — 豆包 · 自动剪辑实测（暗黑科技风）
   口播 129.93s；切点贴原曲重音（beats.js，原曲 80.83s 处跳回 61.24s 循环 32 拍）
   时间均为全片绝对秒；口播时间来自 口播及 srt/10月2日 (1).srt */
const chap = (t, s) => CHAP.push([t, s]);
const SHK = []; const shk = (t, amp = 12, d = .4) => SHK.push([t, amp, d]);
function shakeSum(t) { let x = 0, y = 0; for (const [a, amp, d] of SHK) { const s = shake(t, a, d, amp); x += s[0]; y += s[1]; } return [x, y]; }
const FL = (t, k = .6, d = .35) => FLASH.push([t, k, d]);
function drift(sc, o = {}) {
  sc.cam = t => { const lt = t - sc.s, [sx, sy] = shakeSum(t); return { x: 960 + Math.sin(lt * .31) * (o.dx == null ? 5 : o.dx), y: 540 + Math.cos(lt * .27) * 4, z: (o.z0 || 1) + lt * (o.zr == null ? .0035 : o.zr), sx, sy }; };
}
function persp(e, ry = 0, rx = 0, p = 1800) { e.firstChild.style.transform = `perspective(${p}px) rotateY(${ry.toFixed(2)}deg) rotateX(${rx.toFixed(2)}deg)`; }
const ARROW = `<svg width="34" height="44" viewBox="0 0 34 44"><path d="M3 3 L3 34 L11 27 L17 41 L23 38 L17 25 L28 25 Z" fill="#fff" stroke="#0A0B0E" stroke-width="2.5" stroke-linejoin="round"/></svg>`;
const PRELOAD = [];
function preImg(src) { const im = new Image(); im.src = src; PRELOAD.push(im.decode().catch(() => { throw Error('preload failed ' + src); })); return im; }
const AFLAT = null; // unselected wall catalogue deliberately not loaded
const SAMPLE = [0, 5, 9, 17, 22, 40, 61, 77, 103, 128, 150, 171, 199, 230, 262, 301, 333, 371];   // 作品墙抽样格

/* =============== S1 · 0–3.90 开场：两颗球体合成一次成功的剪辑 =============== */


{
  const sc = scene(0, 3.90); chap(0, '// 01 — 实测'); drift(sc, { zr: .006 });
  tkKey(0, 'R', .01);
  const T = title2(sc.el, '豆包 × WorkBuddy', '自动剪辑，成功了', 146, 168, { kick: '// AI AUTO-EDIT · 实测', size: 98 });
  const ST = mk(sc.el, `<div style="display:flex;gap:14px">${statHTML('ENGINE', '豆包')}${statHTML('AGENT', 'WorkBuddy', { col: AM })}${statHTML('STATUS', '<span class="ss">EDITING…</span>', { col: TX })}</div>`, 146, 452);
  const ss = ST.querySelector('.ss');
  const c1 = mk(sc.el, `<div class="chipA"><i style="background:${CY};box-shadow:0 0 10px ${CY}"></i>豆包</div>`, 0, 0, { ax: .5, ay: .5 });
  const c2 = mk(sc.el, `<div class="chipA"><i></i>WorkBuddy</div>`, 0, 0, { ax: .5, ay: .5 });
  const c3 = mk(sc.el, `<div class="chipA" style="border-color:${GRN}66"><i style="background:${GRN};box-shadow:0 0 10px ${GRN}"></i>成片 · 1920×1080</div>`, 0, 0, { ax: .5, ay: .5 });
  const O = t => { const m = EZ.inout(pr(t, 2.05, 2.95)); return { x1: lerp(830, 985, m), y1: 650 + Math.sin(t * 1.3) * 7, x2: lerp(1150, 995, m), y2: 668 + Math.cos(t * 1.1) * 7, m }; };
  sc.update = t => {
    title2At(T, t, .1, null, { gap: 2.5, slam: true });
    show(ST, t, 1.46, { k: 'up' });
    setHTML(ss, t < 3.0 ? 'EDITING…' : `<span style="color:${GRN}">SUCCESS ✓</span>`);
    const o = O(t);
    show(c1, t, .55, { k: 'pop', x: o.x1, y: o.y1 - 150, out: 2.85 }); show(c2, t, .75, { k: 'pop', x: o.x2, y: o.y2 - 140, out: 2.85 });
    show(c3, t, 3.05, { k: 'pop', x: 990, y: 520 });
  };
  sc.bg = (c, t) => {
    bgBase(c, t, { cx: 960, cy: 640 }); floor(c, t, 760, 1, '255,190,120'); dust(c, t, 70, .8);
    const o = O(t), m = o.m, after = pr(t, 2.95, 3.2);
    ball(c, o.x1, o.y1, 92 + after * 30, after > 0 ? '170,225,255' : '124,200,255', 1, { lat: t * .6 });
    ball(c, o.x2, o.y2, 78 * (1 - after), '255,182,72', 1 - after * .9, { lat: -t * .5 });
    if (m > 0 && m < 1) beam(c, o.x1, o.y1, o.x2, o.y2, '255,220,170', m, t, { flow: false });
    arcRing(c, 990, 690, 260, Math.PI * 1.08, Math.PI * (1.08 + .84 * EZ.out(pr(t, .3, 1.6))), '255,196,120', .8);
  };
  sc.fg = (c, t) => burst(c, t, 2.95, 990, 660, { n: 60, col: '200,235,255' });
  FL(.12, .55); shk(.12, 10); FL(2.6, .45); shk(2.95, 14, .5); FL(2.95, .35);
  S(.1, 'whoosh', .8); S(.14, 'hit', 1); S(.55, 'pop', .5, -.2); S(.75, 'pop', .5, .2); S(1.46, 'card', .6); S(2.6, 'hit', .9); S(2.95, 'crash', .7); S(3.05, 'check', .7);
}

  const Q = new URLSearchParams(location.search);
  const FGC = document.createElement('canvas'); FGC.width = 1920; FGC.height = 1080; FGC.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px;pointer-events:none';
  $('world').appendChild(FGC); fgx = FGC.getContext('2d');
  const fx = $('fx');
  const wipe = document.createElement('div'); wipe.style.cssText = 'position:absolute;inset:0;transform:translateX(100%)'; fx.appendChild(wipe);
  const circ = document.createElement('div'); circ.style.cssText = 'position:absolute;left:960px;top:540px;width:10px;height:10px;border-radius:50%;transform:translate(-50%,-50%) scale(0)'; fx.appendChild(circ);
  const flash = document.createElement('div'); flash.style.cssText = 'position:absolute;inset:0;background:#fff;opacity:0;mix-blend-mode:screen'; fx.appendChild(flash);
  const fade = document.createElement('div'); fade.style.cssText = 'position:absolute;inset:0;background:#000;opacity:0'; $('ov').appendChild(fade);
  function trans(t) {
    wipe.style.transform = 'translateX(100%)'; circ.style.transform = 'translate(-50%,-50%) scale(0)';
    let fl = 0, wf = '';
    for (const [a, k, d] of FLASH) { const x = (t - a) / (d || .35); if (x >= 0 && x < 1) fl = Math.max(fl, k * Math.pow(1 - x, 2)); }
    for (const sc of SCENES) {
      const tr = sc.opt.trans; if (!tr) continue;
      const d = sc.opt.td || .5, x = (t - (sc.s - d / 2)) / d;
      if (x < 0 || x > 1) continue;
      if (tr === 'wipe') { wipe.style.background = sc.opt.tc || '#0A0B0E'; wipe.style.transform = `translateX(${lerp(100, -100, EZ.inout(x))}%)`; }
      if (tr === 'circle') {
        circ.style.background = sc.opt.tc || '#0A0B0E'; const p = x < .5 ? EZ.in(x * 2) : 1, q = x < .5 ? 0 : EZ.out((x - .5) * 2);
        circ.style.left = (sc.opt.cx || 960) + 'px'; circ.style.top = (sc.opt.cy || 540) + 'px';
        circ.style.transform = `translate(-50%,-50%) scale(${p * 460})`; circ.style.opacity = Math.min(1 - q, clamp(p * 25));
      }
      if (tr === 'flash') fl = Math.max(fl, Math.max(0, 1 - Math.abs(x - .5) * 2.2) * (sc.opt.fa || .8));
      if (tr === 'blur') wf = `blur(${(Math.sin(x * Math.PI) * 22).toFixed(1)}px)`;
    }
    flash.style.opacity = fl.toFixed(3);
    $('world').style.filter = wf;
  }
  const drawAt = function (t) {
    const active = SCENES.filter(sc => t >= sc.s - 1e-4 && t < sc.e);
    for (const sc of SCENES) { const on = active.includes(sc); sc.el.style.display = on ? 'block' : 'none'; if (sc.fr) sc.fr.style.display = on ? 'block' : 'none'; }
    bgx.setTransform(1, 0, 0, 1, 0, 0); bgx.clearRect(0, 0, 1920, 1080);
    fgx.setTransform(1, 0, 0, 1, 0, 0); fgx.clearRect(0, 0, 1920, 1080);
    let cam = null, drewBg = false;
    for (const sc of active) {
      sc.update(t);
      if (sc.bg) { sc.bg(bgx, t); drewBg = true; }
      if (sc.fg) sc.fg(fgx, t);
      const c = sc.cam(t); if (c) cam = c;
    }
    if (!drewBg) bgBase(bgx, t);
    const tf = cam ? `translate(${(cam.sx || 0).toFixed(2)}px,${(cam.sy || 0).toFixed(2)}px) scale(${(cam.z || 1).toFixed(4)}) translate(${(960 - (cam.x || 960)).toFixed(2)}px,${(540 - (cam.y || 540)).toFixed(2)}px)` : '';
    $('world').style.transform = tf; $('front').style.transform = tf;
    $('tk').style.transform = cam ? `translate(${(cam.sx || 0).toFixed(2)}px,${(cam.sy || 0).toFixed(2)}px)` : '';
    tkUpdate(t); hudUpdate(t);
    const E = window.END || CONFIG.end;
    fade.style.opacity = '0'; // output host owns deliberate final fade
    // Output host owns this episode's captions.
  };

/* Source-native transition plane. The shared runtime calls this hook after
   source-clock drawing, while all planes remain inside their instance host. */
function doubaoTransition(planes, flashes, sourceTime, context) {
  const {wipe, circ, flash, world} = planes;
  wipe.style.transform = 'translateX(100%)';
  circ.style.transform = 'translate(-50%,-50%) scale(0)';
  circ.style.opacity = '0'; world.style.filter = '';
  let fl = 0;
  for (const [at, amount, seconds] of flashes) {
    const x = (sourceTime - at) / (seconds || .35);
    if (x >= 0 && x < 1) fl = Math.max(fl, amount * Math.pow(1 - x, 2));
  }
  let selected = context.scene, item = context.item;
  if (context.nextScene?.opt?.trans &&
      context.frame >= context.nextItem.output_start_frame - (context.nextScene.opt.td || .5) * context.fps / 2) {
    selected = context.nextScene; item = context.nextItem;
  }
  const opt = selected.opt, d = (opt.td || .5) * context.fps;
  const x = (context.frame - (item.output_start_frame - d / 2)) / d;
  if (opt.trans && item.output_start_frame > 0 && x >= 0 && x <= 1) {
    if (opt.trans === 'wipe') {
      wipe.style.background = opt.tc || '#0A0B0E';
      wipe.style.transform = `translateX(${lerp(100, -100, EZ.inout(x))}%)`;
    }
    if (opt.trans === 'circle') {
      const p = x < .5 ? EZ.in(x * 2) : 1, q = x < .5 ? 0 : EZ.out((x - .5) * 2);
      circ.style.background = opt.tc || '#0A0B0E';
      circ.style.left = (opt.cx || 960) + 'px'; circ.style.top = (opt.cy || 540) + 'px';
      circ.style.transform = `translate(-50%,-50%) scale(${p * 460})`;
      circ.style.opacity = String(Math.min(1 - q, clamp(p * 25)));
    }
    if (opt.trans === 'flash') fl = Math.max(fl, Math.max(0, 1 - Math.abs(x - .5) * 2.2) * (opt.fa || .8));
    if (opt.trans === 'blur') world.style.filter = `blur(${(Math.sin(x * Math.PI) * 22).toFixed(1)}px)`;
  }
  flash.style.opacity = fl.toFixed(3);
}

outer.opt={...SCENES[0].opt};
let lastSource=outer.s;
outer.update=t=>{lastSource=t;drawAt(t);};
outer.macroTransition=context=>doubaoTransition({wipe,circ,flash,world:nodes.world},FLASH,lastSource,{...context,scene:outer});
SFX.forEach(c=>{const {t,type,g,p,...extra}=c;FORWARD_S(t,type,g,p,extra);});
outer.doubaoDiagnostics={clock:'source-geometry/output-media',sourceScenes:SCENES.length,sourceSfx:SFX.length,initialTalkKey:TKK[0]};
})(Scene,setFrame,tc,S);

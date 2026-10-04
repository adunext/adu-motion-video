((OUTPUT_SCENE,OUTPUT_FRAME,OUTPUT_TC,FORWARD_S) => {
const outer = new OUTPUT_SCENE(50.87,58.93,'#06070A',{});
const host = document.createElement('div');host.className='sticker-host';
host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML='<div data-sticker-node="world"></div><div data-sticker-node="fx"></div><div data-sticker-node="tk"></div><div data-sticker-node="front"></div><div data-sticker-node="hud"></div><div data-sticker-node="ov" style="position:absolute;inset:0;pointer-events:none"></div>';
const nodes=Object.fromEntries([...host.querySelectorAll('[data-sticker-node]')].map(e=>[e.dataset.stickerNode,e]));
const HITS=[[4.94, 0.56], [5.23, 0.8], [6.05, 0.85], [6.24, 0.32], [6.46, 0.71], [7.27, 0.58], [7.89, 0.7], [8.06, 0.33], [8.5, 0.77], [8.91, 0.73], [9.84, 0.78], [10.34, 0.28], [10.96, 0.78], [11.41, 0.8], [11.58, 0.3], [11.78, 0.28], [12.19, 0.48], [12.44, 0.28], [12.73, 0.3], [13.4, 0.76], [13.58, 0.47], [13.84, 0.69], [14.04, 0.29], [14.21, 0.28], [14.62, 0.46], [14.77, 0.75], [14.95, 0.26], [15.14, 0.33], [15.37, 0.25], [15.86, 0.86], [16.01, 0.5], [16.33, 0.73], [16.55, 0.32], [16.8, 0.29], [17.09, 0.65], [17.3, 0.42], [17.59, 0.35], [18.31, 0.87], [18.73, 0.68], [18.95, 0.36], [19.34, 0.36], [19.66, 0.45], [20.17, 0.31], [20.59, 0.28], [20.8, 0.98], [21.2, 0.67], [21.39, 0.39], [21.85, 0.53], [22.01, 0.69], [22.21, 0.44], [22.52, 0.31], [22.92, 0.28], [23.21, 0.73], [23.64, 0.71], [23.81, 0.25], [24.29, 0.31], [24.57, 0.6], [24.98, 0.33], [25.68, 0.64], [26.1, 0.62], [26.3, 0.41], [26.61, 0.74], [27.02, 0.48], [27.63, 0.75], [28.13, 0.86], [28.55, 0.63], [29.17, 0.38], [29.48, 0.73], [29.99, 0.36], [30.31, 0.31], [30.59, 0.84], [31.01, 0.83], [31.66, 0.5], [31.93, 0.66], [32.35, 0.34], [32.76, 0.25], [33.04, 0.67], [33.46, 0.67], [33.62, 0.29], [33.82, 0.35], [34.1, 0.29], [34.29, 0.71], [34.56, 0.27], [34.89, 0.37], [35.22, 0.3], [35.5, 0.87], [35.92, 0.81], [36.09, 0.34], [36.28, 0.34], [36.44, 0.4], [36.74, 0.78], [36.9, 0.53], [37.23, 0.38], [37.67, 0.3], [37.94, 0.63], [38.36, 0.61], [39.31, 0.62], [39.8, 0.37], [40.23, 0.29], [40.41, 1.0], [40.62, 0.46], [40.83, 0.65], [41.34, 0.31], [41.74, 0.8], [42.26, 0.36], [42.67, 0.29], [42.85, 0.79], [43.28, 0.46], [43.62, 0.31], [43.81, 0.35], [44.1, 0.53], [44.29, 0.41], [44.71, 0.33], [45.06, 0.3], [45.32, 0.76], [45.48, 0.57], [45.74, 0.84], [45.97, 0.29], [46.24, 0.98], [46.65, 0.4], [48.8, 0.48], [49.1, 0.56], [49.34, 0.31], [49.62, 0.28], [49.97, 0.32], [50.22, 0.75], [50.66, 0.6], [51.55, 0.5], [51.75, 0.28], [51.97, 0.35], [52.48, 0.43], [52.69, 0.74], [53.1, 0.5], [54.01, 0.74], [54.23, 0.26], [54.52, 0.44], [54.89, 0.36], [55.14, 0.73], [55.55, 0.74], [56.18, 0.3], [56.47, 0.56], [56.7, 0.37], [56.9, 0.36], [57.4, 0.46], [57.6, 0.64], [57.76, 0.35], [58.01, 0.64], [58.63, 0.61], [58.93, 0.56], [59.2, 0.36], [59.44, 0.36], [59.8, 0.37], [60.05, 0.83], [60.47, 0.69], [60.69, 0.3], [61.14, 0.36], [61.43, 0.54], [61.63, 0.29], [61.85, 0.3], [62.24, 0.29], [62.49, 0.79], [62.93, 0.74], [63.44, 0.39], [63.73, 0.65], [63.98, 0.42], [64.34, 0.49], [64.95, 0.86], [65.11, 0.26], [65.37, 0.69], [65.6, 0.56], [66.03, 0.25], [66.2, 0.72], [68.44, 0.51], [68.74, 0.76], [69.25, 0.44], [69.86, 0.6], [70.02, 0.5], [70.28, 0.66], [70.55, 0.3], [70.94, 0.47], [71.22, 0.79], [71.48, 0.45], [71.68, 0.55], [72.06, 0.28], [72.3, 0.71], [72.73, 0.44], [73.28, 0.42], [73.65, 0.61], [73.9, 0.27], [74.16, 0.43], [74.77, 0.64], [74.95, 0.33], [75.21, 0.71], [75.46, 0.45], [75.85, 0.34], [76.13, 0.88], [76.28, 0.53], [76.57, 0.47], [76.97, 0.39], [77.21, 0.72], [77.54, 0.38], [78.27, 0.36], [78.56, 0.6], [78.76, 0.28], [79.06, 0.39], [79.41, 0.25], [79.68, 0.63], [79.84, 0.36], [80.1, 0.77], [80.35, 0.35], [81.04, 0.93], [81.28, 0.42], [81.48, 0.42], [81.93, 0.52], [82.12, 0.68], [82.57, 0.58], [83.08, 0.31], [83.36, 0.63], [83.98, 0.47], [84.37, 0.32], [84.58, 0.49], [84.77, 0.25], [85.03, 0.78], [85.26, 0.31], [85.51, 0.66], [85.93, 0.6], [88.07, 0.54], [88.39, 0.58], [90.52, 0.6], [90.84, 0.91], [91.0, 0.34], [91.2, 0.41], [91.36, 0.3], [91.95, 0.74], [92.13, 0.29], [92.37, 0.63], [92.6, 0.32], [93.18, 0.57], [93.34, 0.79], [93.56, 0.38], [93.73, 0.41], [94.41, 0.6], [94.57, 0.5], [94.83, 0.66], [95.1, 0.3], [95.49, 0.47], [95.77, 0.79], [96.03, 0.45], [96.23, 0.55], [96.61, 0.28], [96.85, 0.71], [97.28, 0.44], [97.83, 0.42], [98.2, 0.61], [98.45, 0.27], [98.71, 0.43], [99.32, 0.64], [99.5, 0.33], [99.76, 0.71], [100.01, 0.45], [100.4, 0.34], [100.68, 0.88], [100.92, 0.48], [101.12, 0.47], [101.52, 0.39], [101.76, 0.72], [102.09, 0.38], [102.82, 0.36], [103.11, 0.6], [103.31, 0.28], [103.61, 0.39], [103.96, 0.25], [104.23, 0.63], [104.39, 0.36], [104.65, 0.77], [104.9, 0.35], [105.59, 0.93], [105.83, 0.42], [106.03, 0.42], [106.48, 0.52], [106.67, 0.68], [107.12, 0.58], [107.63, 0.31], [107.91, 0.63], [108.53, 0.47], [108.92, 0.32], [109.13, 0.49], [109.32, 0.25], [109.58, 0.78], [109.81, 0.31], [110.06, 0.66], [110.48, 0.6], [112.62, 0.54], [112.94, 0.58], [115.07, 0.6], [115.39, 0.91], [115.55, 0.34], [115.75, 0.41], [115.9, 0.3], [116.5, 0.74], [116.68, 0.29], [116.92, 0.63], [117.15, 0.32], [117.73, 0.57], [117.89, 0.79], [118.11, 0.38], [118.28, 0.41], [118.79, 0.5], [118.95, 0.78], [119.38, 0.66], [119.53, 0.39], [119.83, 0.46], [120.3, 0.58], [120.56, 0.48], [120.73, 0.51], [120.93, 0.28], [121.4, 0.78], [121.88, 0.51], [122.06, 0.38], [122.52, 0.68], [122.8, 0.8], [123.02, 0.42], [123.19, 0.44], [123.71, 0.48], [123.97, 0.7], [124.3, 0.77], [125.07, 0.71], [125.22, 0.68], [125.6, 0.49], [126.08, 0.33], [126.4, 0.51], [126.83, 0.31], [127.14, 0.48], [127.41, 0.38], [127.63, 0.35], [127.92, 0.39], [128.09, 0.41], [128.57, 0.58], [128.92, 0.6], [129.1, 0.34], [129.32, 0.25], [129.6, 0.34], [129.79, 0.31], [130.48, 0.37], [130.63, 0.48], [131.1, 0.51], [131.25, 0.31], [131.54, 0.39], [131.69, 0.44], [131.88, 0.39], [132.14, 0.66], [132.29, 0.25], [132.57, 0.46], [132.82, 0.41], [133.18, 0.82], [133.43, 0.34], [133.8, 0.72], [134.1, 0.81], [134.71, 0.53], [135.02, 0.89], [135.27, 0.47], [137.16, 0.58], [137.48, 0.75], [137.67, 0.31]]; // source visual pulse clock is preserved, not new track analysis
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

/* core.js — 回应技术含量：明亮多彩版共享层
   参考视频语言：橙红大色块 + 流动模糊色团、白底、高亮便签字、胶囊滚动行、黑底金色光环、实景天空 + 浮动卡片、logo 收尾
   全片同一张口播卡（关键帧之间弹簧形变）；HUD 随底色明暗切换 */
const P = { red: '#FF4D1F', red2: '#E5381B', org: '#FF8A1F', yel: '#FFC83A', pink: '#FF5C8A', vio: '#7B5CFF', blue: '#2462EA', sky: '#5BB8FF', paper: '#F7F7F5', ink: '#0A0A0A', gray: '#8C8C8C', claude: '#D97757', cream: '#FFF4E6' };
const RGB = { red: '255,77,31', org: '255,138,31', yel: '255,200,58', pink: '255,92,138', vio: '123,92,255', blue: '36,98,234', sky: '91,184,255', white: '255,255,255', claude: '217,119,87', deep: '150,20,10' };
const FZ = "-apple-system,'PingFang SC',sans-serif";
const FE = "'Geist',-apple-system,'PingFang SC',sans-serif";
const FM = "'Geist Mono',ui-monospace,'PingFang SC',monospace";
const FLASH = [];
const frameIdx = t => Math.floor(t * 60 + 1e-6);
const rnd = (i, k = 0) => hash(i * 13.37 + k * 71.1);
const NF = {};
const EPS = [];
const VERT = { ep10: 1, ep11: 1 };

/* ---------- 文字与小件 ---------- */
function tx(parent, html, x, y, o = {}) {
  const st = `font:${o.w || 600} ${o.size || 40}px/${o.lh || 1.15} ${o.ff || FZ};color:${o.col || P.ink};letter-spacing:${o.ls == null ? 0 : o.ls}px;${o.style || ''}`;
  return mk(parent, `<div style="${st}">${html}</div>`, x, y, { ax: o.ax || 0, ay: o.ay || 0 });
}
function mono(parent, html, x, y, o = {}) { return tx(parent, html, x, y, Object.assign({ ff: FM, w: 500, size: 18, col: P.gray, ls: 2 }, o)); }
function scene(s, e, opt = {}) {
  const sc = new Scene(s, e, 'transparent', opt);
  sc.fr = document.createElement('div'); sc.fr.className = 'sc'; $('front').appendChild(sc.fr);
  sc.dark = !!opt.dark;           // dark=true：浅色底，HUD 用深色字
  return sc;
}
function setHTML(el, s) { if (el._h !== s) { el._h = s; el.innerHTML = s; } }
function typeAt(el, full, t, t0, t1, cur = true, cc = P.red) {
  const ch = [...full].map(c => c === '\n' ? '<br>' : c), n = Math.floor(clamp((t - t0) / (t1 - t0)) * ch.length + 1e-6);
  const c = cur && t >= t0 - .2 && t < t1 + .7 && Math.floor(t * 3.2) % 2 === 0 ? `<span style="color:${cc}">▍</span>` : '';
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
  const c = o.col || P.red;
  return mk(parent, `<div style="border:${o.bw || 7}px solid ${c};color:${c};border-radius:${o.br || 16}px;padding:${o.pad || '0 26px'};font:800 ${o.size || 72}px/1.2 ${o.ff || FZ};letter-spacing:${o.ls == null ? 4 : o.ls}px;background:${o.bg || 'transparent'}">${text}</div>`, x, y, { ax: .5, ay: .5 });
}
function stampAt(e, t, t0, rot, o = {}) {
  const x = pr(t, t0, t0 + .26); let op = clamp(x * 6);
  if (o.out != null) op *= 1 - pr(t, o.out, o.out + .3);
  place(e, { x: o.x, y: o.y, s: (1 + 1.4 * (1 - EZ.out5(x))) * (o.s || 1), r: rot, o: op * (o.o == null ? 1 : o.o) });
}
function pill(html, o = {}) {
  return `<span style="display:inline-flex;align-items:center;gap:10px;padding:${o.pad || '10px 22px'};border-radius:${o.br || 60}px;background:${o.bg || '#fff'};border:${o.bd || '0'};color:${o.col || P.ink};font:${o.w || 600} ${o.size || 26}px ${o.ff || FZ};letter-spacing:${o.ls == null ? 0 : o.ls}px;white-space:nowrap;box-shadow:${o.sh || '0 10px 30px rgba(0,0,0,.12)'};${o.style || ''}">${o.dot ? `<i style="width:${o.ds || 14}px;height:${o.ds || 14}px;border-radius:50%;background:${o.dot};display:block;flex:none"></i>` : ''}${html}</span>`;
}
/* 工具胶囊（不用第三方 logo，只用色点 + 名称） */
const TOOL = { 豆包: P.org, WorkBuddy: P.vio, DeepSeek: P.blue, Claude: P.claude, Codex: P.ink, 'Claude Code': P.claude };
const toolPill = (n, o = {}) => pill(n, Object.assign({ dot: TOOL[n] || P.gray }, o));
/* 高亮便签：色块先横向擦入，字随后出现（参考视频 Feels Complicated） */
function hlBox(parent, html, x, y, o = {}) {
  const e = mk(parent, `<div style="position:relative;display:inline-block;padding:${o.pad || '4px 22px 8px'}"><div class="hb" style="position:absolute;inset:0;background:${o.bg || P.yel};border-radius:${o.br || 10}px;transform-origin:0 50%"></div><div class="ht" style="position:relative;font:${o.w || 700} ${o.size || 64}px/1.2 ${o.ff || FZ};color:${o.col || P.ink};letter-spacing:${o.ls == null ? 0 : o.ls}px">${html}</div></div>`, x, y, { ax: o.ax || 0, ay: o.ay || 0 });
  e._b = e.querySelector('.hb'); e._t = e.querySelector('.ht'); return e;
}
function hlAt(e, t, t0, o = {}) {
  const a = pr(t, t0, t0 + (o.d || .32)), b = pr(t, t0 + .12, t0 + .45);
  let op = 1; if (o.out != null) op = 1 - pr(t, o.out, o.out + .3);
  place(e, { x: o.x, y: o.y, s: o.s, r: o.r, o: (a > 0 ? 1 : 0) * op });
  e._b.style.transform = `scaleX(${EZ.out5(a).toFixed(4)})`;
  e._t.style.opacity = clamp(b * 2).toFixed(3); e._t.style.transform = `translateX(${((1 - EZ.expo(b)) * -24).toFixed(1)}px)`;
  e._t.style.filter = b < 1 ? `blur(${((1 - b) * 6).toFixed(1)}px)` : '';
}
/* 逐词模糊显现（参考视频 What if one platform…）：segs=[{h,t}] */
function blurWords(parent, segs, x, y, o = {}) {
  const e = words(parent, segs, x, y, 'bw', { ax: o.ax || 0, ay: o.ay || 0, style: `font:${o.w || 600} ${o.size || 64}px/1.15 ${o.ff || FZ};color:${o.col || '#fff'};letter-spacing:${o.ls == null ? 0 : o.ls}px;white-space:nowrap` });
  e._w.forEach(w => { w.style.marginRight = (o.gap == null ? 18 : o.gap) + 'px'; });
  return e;
}
function blurWordsAt(e, t, o = {}) {
  place(e, { o: o.o == null ? 1 : o.o, x: o.x, y: o.y, s: o.s });
  e._w.forEach((w, i) => {
    const s = e._segs[i], x = pr(t, s.t, s.t + (s.d || .5)), E = EZ.out(x);
    let op = clamp(x * 2), tf = `translateX(${((1 - E) * 30).toFixed(1)}px)`;
    if (s.k === 'slam') { op = clamp(x * 5); tf = `scale(${(1 + (1 - EZ.out5(x)) * 1.1).toFixed(3)})`; }
    if (o.out != null) { const y = pr(t, o.out + i * .03, o.out + i * .03 + .3); op *= 1 - y; tf += ` translateY(${(-EZ.in(y) * 30).toFixed(1)}px)`; }
    w.style.opacity = op.toFixed(3); w.style.transform = tf;
    w.style.filter = x < 1 ? `blur(${((1 - E) * 16).toFixed(1)}px)` : '';
  });
}
/* 卡通形象 / 道具（生成图） */
const gen = (parent, f, x, y, h, o = {}) => img(parent, 'gen/' + f, x, y, h, Object.assign({ ic: 'ch' }, o));
function popAt(e, t, t0, o = {}) {      // 弹入 + 呼吸 + 可选出场
  const a = pr(t, t0, t0 + (o.d || .5)); let op = clamp(a * 6);
  if (o.out != null) op *= 1 - pr(t, o.out, o.out + .3);
  const by = o.bob === false ? 0 : Math.sin(t * 2.2 + (o.k || 0)) * (o.ba || 5);
  const os = o.out != null ? 1 - .2 * EZ.in(pr(t, o.out, o.out + .3)) : 1;
  place(e, { x: (o.x == null ? e._x : o.x) + (o.dx || 0) * (1 - EZ.spring(a)), y: (o.y == null ? e._y : o.y) + (1 - EZ.spring(a)) * (o.dy == null ? 60 : o.dy) + by, s: (.6 + .4 * EZ.spring(a)) * (o.s || 1) * os, r: (o.r || 0) + (1 - EZ.spring(a)) * (o.rr || 0), o: op });
  return a;
}
/* 视频小卡（往期成片帧序列） */
function clip(parent, dir, w, h, r = 16, extra = '') { const e = vtile(parent, w, h, r, extra); e._dir = dir; return e; }
function clipAt(e, t, t0, o, opt = {}) {
  if (o) place(e, o);
  if (o && (o.o == null ? 1 : o.o) <= .002) return;
  const n = NF[e._dir], fps = opt.fps || 30; let i = Math.floor((t - t0) * fps + 1e-6) + (opt.off || 0);
  if (opt.hold) i = clamp(i, 0, n - 1); else i = ((i % n) + n) % n;
  setFrame(e._img, `sc/${e._dir}/f_${String(i + 1).padStart(4, '0')}.jpg`);
}
function macWin(parent, w, h, title, o = {}) {
  const e = mk(parent, `<div class="macwin" style="width:${w}px"><div class="tb"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i><span style="margin-left:14px;display:flex;align-items:center;gap:10px;flex:1">${title}</span></div><div class="body" style="height:${h}px;${o.bst || ''}">${o.body == null ? '<img>' : o.body}</div></div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('.body img'); e._body = e.querySelector('.body'); return e;
}
const ARROW = `<svg width="38" height="48" viewBox="0 0 34 44"><path d="M3 3 L3 34 L11 27 L17 41 L23 38 L17 25 L28 25 Z" fill="#fff" stroke="#0A0A0A" stroke-width="2.5" stroke-linejoin="round"/></svg>`;
const HAND = `<svg width="46" height="54" viewBox="0 0 46 54"><path d="M16 4c3 0 5 2 5 5v14l2-1c2-1 5 0 5 3 2-1 5 0 5 3 2-1 6 0 6 4v9c0 7-6 12-13 12h-4c-5 0-9-3-11-7L4 33c-1-3 0-5 3-6 2 0 4 1 5 3l1 2V9c0-3 1-5 3-5z" fill="#fff" stroke="#0A0A0A" stroke-width="2.6" stroke-linejoin="round"/></svg>`;

/* ---------- 画布背景 ---------- */
const BGC = document.createElement('canvas'); BGC.width = 1920; BGC.height = 1080; BGC.style.cssText = 'position:absolute;left:0;top:0;width:1920px;height:1080px';
$('world').appendChild(BGC); const bgx = BGC.getContext('2d');
let fgx = null;
function fill(c, col) { c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1; c.fillStyle = col; c.fillRect(0, 0, 1920, 1080); }
function bgBase(c, t) { fill(c, P.paper); }
/* 流动色团：list=[[rgb, x, y, r, a, speed, phase]] */
function blobs(c, t, base, list, k = 1) {
  fill(c, base);
  c.save();
  for (const [col, x, y, r, a, sp, ph] of list) {
    const cx = x + Math.sin(t * (sp || .35) + (ph || 0)) * 140, cy = y + Math.cos(t * (sp || .35) * .8 + (ph || 0)) * 100;
    const g = c.createRadialGradient(cx, cy, 0, cx, cy, r);
    g.addColorStop(0, `rgba(${col},${(a == null ? 1 : a) * k})`); g.addColorStop(.55, `rgba(${col},${(a == null ? 1 : a) * .45 * k})`); g.addColorStop(1, `rgba(${col},0)`);
    c.fillStyle = g; c.fillRect(0, 0, 1920, 1080);
  }
  c.restore();
}
const WARM = t => [[RGB.yel, 1300, 760, 760, .95, .3, 0], [RGB.org, 520, 300, 700, .9, .25, 2], [RGB.deep, 1650, 140, 600, .8, .4, 4], [RGB.pink, 200, 900, 520, .5, .3, 1]];
/* 网格线（参考视频红底细白线格） */
function gridLines(c, xs, ys, col = 'rgba(255,255,255,.55)', a = 1) {
  if (a <= .002) return;
  c.save(); c.strokeStyle = col; c.globalAlpha = a; c.lineWidth = 1.5;
  for (const x of xs) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, 1080); c.stroke(); }
  for (const y of ys) { c.beginPath(); c.moveTo(0, y); c.lineTo(1920, y); c.stroke(); }
  c.restore();
}
/* 金色光环（参考视频黑底黄色光环 + 斜向光带） */
function glowRing(c, t, cx, cy, R, k = 1, o = {}) {
  if (k <= .002) return;
  c.save(); c.globalCompositeOperation = 'lighter';
  const rot = t * (o.spin || .6);
  for (let L = 0; L < 5; L++) {
    const w = [70, 34, 16, 7, 2.5][L], a = [.08, .14, .3, .6, .95][L] * k;
    for (let s = 0; s < 3; s++) {
      const a0 = rot + s * 2.094, a1 = a0 + 1.7 + Math.sin(t * 1.3 + s) * .3;
      const g = c.createLinearGradient(cx + Math.cos(a0) * R, cy + Math.sin(a0) * R, cx + Math.cos(a1) * R, cy + Math.sin(a1) * R);
      g.addColorStop(0, `rgba(255,120,20,0)`); g.addColorStop(.5, `rgba(255,${200 + L * 10},${60 + L * 35},${a})`); g.addColorStop(1, `rgba(255,120,20,0)`);
      c.strokeStyle = g; c.lineWidth = w; c.beginPath(); c.ellipse(cx, cy, R, R * (o.squash || .92), 0, a0, a1); c.stroke();
    }
    c.strokeStyle = `rgba(255,190,70,${a * .35})`; c.lineWidth = w; c.beginPath(); c.ellipse(cx, cy, R, R * (o.squash || .92), 0, 0, 7); c.stroke();
  }
  // 斜向光带
  const sw = o.streak == null ? 1 : o.streak;
  if (sw > 0) {
    c.translate(cx, cy); c.rotate(-.42);
    const g = c.createLinearGradient(-R * 1.6, 0, R * 1.6, 0);
    g.addColorStop(0, 'rgba(255,90,20,0)'); g.addColorStop(.35, `rgba(255,120,30,${.5 * k * sw})`); g.addColorStop(.5, `rgba(255,240,180,${.9 * k * sw})`); g.addColorStop(.65, `rgba(255,120,30,${.5 * k * sw})`); g.addColorStop(1, 'rgba(255,90,20,0)');
    c.fillStyle = g; c.beginPath(); c.ellipse(0, 0, R * 1.6, 10 + 6 * Math.sin(t * 2), 0, 0, 7); c.fill();
  }
  c.restore();
}
/* 放射光 */
function sunRays(c, t, cx, cy, col, a = 1, n = 18) {
  if (a <= .002) return;
  c.save(); c.translate(cx, cy); c.rotate(t * .12); c.globalAlpha = a;
  for (let i = 0; i < n; i++) { c.fillStyle = `rgba(${col},${i % 2 ? .10 : .18})`; c.beginPath(); c.moveTo(0, 0); c.arc(0, 0, 1800, i * 6.283 / n, (i + .5) * 6.283 / n); c.fill(); }
  c.restore();
}
/* 彩纸 / 爆散 */
function confetti(c, t, t0, x, y, o = {}) {
  const lt = t - t0; if (lt < 0 || lt > (o.life || 1.8)) return;
  const cols = o.cols || [P.yel, P.pink, P.blue, P.vio, '#fff', P.org];
  c.save();
  for (let i = 0; i < (o.n || 70); i++) {
    const an = -Math.PI / 2 + (rnd(i, 3 + (o.seed || 0)) - .5) * (o.spread || 2.6), sp = (o.sp || 1300) * (.4 + .6 * rnd(i, 4));
    const px = x + Math.cos(an) * sp * lt * .9, py = y + Math.sin(an) * sp * lt * .9 + 900 * lt * lt;
    const al = 1 - pr(lt, (o.life || 1.8) * .6, o.life || 1.8);
    c.globalAlpha = al; c.fillStyle = cols[i % cols.length];
    c.save(); c.translate(px, py); c.rotate(lt * (6 + rnd(i, 5) * 10) + i); c.fillRect(-7, -4, 14, 8); c.restore();
  }
  c.restore();
}
function burst(c, t, t0, x, y, o = {}) {
  const lt = t - t0; if (lt < 0 || lt > (o.life || .8)) return;
  c.save(); c.globalCompositeOperation = o.add ? 'lighter' : 'source-over';
  const n = o.n || 14, al = 1 - lt / (o.life || .8);
  c.strokeStyle = o.col || P.ink; c.lineCap = 'round'; c.lineWidth = o.w || 6; c.globalAlpha = al;
  for (let i = 0; i < n; i++) {
    const an = i / n * 6.283 + (o.rot || 0), r0 = (o.r || 60) + EZ.out(lt / (o.life || .8)) * (o.len || 90), r1 = r0 + 30 * al;
    c.beginPath(); c.moveTo(x + Math.cos(an) * r0, y + Math.sin(an) * r0); c.lineTo(x + Math.cos(an) * r1, y + Math.sin(an) * r1); c.stroke();
  }
  c.restore();
}
const beatK = (t, win = .22) => { let k = 0; for (const [b, h] of HITS) { if (b > t) break; if (t - b < win) k = Math.max(k, h * (1 - (t - b) / win)); } return k; };
const voxAt = () => 0; // selected groups never consume the source voice envelope

/* ---------- 口播主卡：全片同一张，关键帧之间弹簧形变 ---------- */
const LAY = {
  R: { x: 1480, y: 480, w: 500, h: 740, r: 34 },
  RS: { x: 1610, y: 470, w: 380, h: 600, r: 30 },
  L: { x: 440, y: 480, w: 500, h: 740, r: 34 },
  C: { x: 960, y: 470, w: 520, h: 800, r: 34 },
  RC: { x: 1716, y: 240, w: 250, h: 250, r: 125 },
  LC: { x: 204, y: 240, w: 250, h: 250, r: 125 },
  BC: { x: 960, y: 560, w: 520, h: 520, r: 260 },
  BIG: { x: 960, y: 470, w: 1240, h: 800, r: 36 },
};
const TKK = [];
function tkKey(t, L, d = .7, extra = {}) { TKK.push({ t, d, L: Object.assign({ o: 1, s: 1, rx: 0, ry: 0, rz: 0 }, typeof L === 'string' ? LAY[L] : L, extra) }); TKK.sort((a, b) => a.t - b.t); }
const TK = (() => {
  const e = document.createElement('div'); e.className = 'tkc'; $('tk').appendChild(e);
  e.innerHTML = `<img><div class="tlab"><i></i><span>${window.PACK_PRESENTER_LABEL}</span></div>`;
  return { e, im: e.querySelector('img'), lab: e.querySelector('.tlab'), dot: e.querySelector('.tlab i') };
})();
function tkLayout(t) {
  let i = -1; for (let k = 0; k < TKK.length; k++) if (t >= TKK[k].t) i = k;
  if (i < 0) return Object.assign({}, TKK[0].L);
  const K = TKK[i], Pv = i > 0 ? TKK[i - 1].L : K.L, x = pr(t, K.t, K.t + K.d), sp = EZ.spring(x), ou = EZ.out(x);
  const o = {};
  for (const k of ['x', 'y', 'rx', 'ry', 'rz']) o[k] = lerp(Pv[k], K.L[k], sp);
  for (const k of ['w', 'h', 'r']) o[k] = Math.max(1, lerp(Pv[k], K.L[k], k === 'r' ? ou : sp));
  o.o = lerp(Pv.o, K.L.o, ou); o.s = lerp(Pv.s, K.L.s, sp);
  return o;
}
let TK_SHAKE = t => [0, 0];
function tkUpdate(t) {
  const L = tkLayout(t), { e } = TK;
  const w = L.w, h = L.h, s = L.s * (1 + beatK(t, .15) * .006), [sx, sy] = TK_SHAKE(t);
  e.style.width = w.toFixed(1) + 'px'; e.style.height = h.toFixed(1) + 'px'; e.style.borderRadius = Math.min(L.r, w / 2).toFixed(1) + 'px';
  e.style.transform = `translate(${(L.x - w / 2 + sx).toFixed(2)}px,${(L.y - h / 2 + sy).toFixed(2)}px) perspective(1600px) rotateX(${L.rx.toFixed(2)}deg) rotateY(${L.ry.toFixed(2)}deg) rotate(${L.rz.toFixed(2)}deg) scale(${s.toFixed(4)})`;
  e.style.opacity = clamp(L.o).toFixed(3); e.style.visibility = L.o < .003 ? 'hidden' : 'visible';
  e.style.boxShadow = `0 0 0 ${w < 300 ? 6 : 5}px rgba(255,255,255,.95),0 36px 80px rgba(0,0,0,.30)`;
  if (L.o < .003) return;
  setFrame(TK.im, talkSrc(t));
  const f = faceAt(t), a = h / w, kr = clamp((1.4 - a) / .4);
  const cover = Math.max(w / 720, h / 1280), want = (h * .44) / (f.h * 1280 * cover);
  const z = clamp(lerp(1, want, kr), 1, 2.4), iw = 720 * cover * z, ih = 1280 * cover * z;
  const ox = clamp(w / 2 - f.cx * iw, w - iw, 0), oy = clamp(h * lerp(.42, .55, kr) - f.cy * ih, h - ih, 0);
  TK.im.style.cssText = `left:${ox.toFixed(1)}px;top:${oy.toFixed(1)}px;width:${iw.toFixed(1)}px;height:${ih.toFixed(1)}px`;
  TK.lab.style.opacity = (1 - kr).toFixed(3);
  TK.dot.style.background = Math.floor(t * 1.6) % 2 ? 'rgba(255,77,31,.35)' : P.red;
}

/* ---------- HUD：章节标签 / 角标 + 时间码 / 进度线（随底色明暗） ---------- */
const CHAP = [];
const HUD = (() => {
  const h = $('hud');
  const grain = document.createElement('div'); grain.style.cssText = 'position:absolute;inset:0;background:url(assets/noise.png);opacity:.035;mix-blend-mode:overlay'; h.appendChild(grain);
  const tag = mk(h, `<div style="font:500 20px ${FM};letter-spacing:1.5px"></div>`, 64, 48);
  const tcd = mk(h, `<div style="font:500 20px ${FM};letter-spacing:1.5px"><b style="font-weight:700">${window.PACK_BRAND_HTML}</b>&nbsp;&nbsp;<span></span></div>`, 1856, 48, { ax: 1 });
  const tr = mk(h, `<div style="width:1792px;height:3px;border-radius:2px;position:relative"><div class="tf" style="position:absolute;left:0;top:0;height:3px;border-radius:2px"></div></div>`, 64, 1060);
  return { grain, tag, tcd, tcs: tcd.querySelector('span'), tr, tf: tr.querySelector('.tf') };
})();
let HUD_OFF = [];
function hudUpdate(t) {
  let c = CHAP[0]; for (const k of CHAP) if (t >= k[0]) c = k;
  setHTML(HUD.tag.firstChild, c ? c[1] : '');
  HUD.tcs.textContent = OUTPUT_TC(window.MACRO_OUTPUT_T);
  const act = SCENES.filter(sc => t >= sc.s - 1e-4 && t < sc.e); const sc = act[act.length - 1];
  const dk = sc && sc.dark;
  const col = dk ? 'rgba(10,10,10,.62)' : 'rgba(255,255,255,.85)';
  HUD.tag.firstChild.style.color = col; HUD.tcd.firstChild.style.color = col;
  HUD.tr.firstChild.style.background = dk ? 'rgba(10,10,10,.10)' : 'rgba(255,255,255,.22)';
  HUD.tf.style.background = dk ? P.red : '#fff';
  HUD.tf.style.width = (window.MACRO_OUTPUT_T / (window.END || CONFIG.end) * 100).toFixed(2) + '%';
  let off = 0; for (const [a, b] of HUD_OFF) off = Math.max(off, Math.min(pr(t, a, a + .3), 1 - pr(t, b - .3, b)));
  for (const el of [HUD.tag, HUD.tcd, HUD.tr]) place(el, { o: 1 - off });
  const fi = frameIdx(t); HUD.grain.style.backgroundPosition = `${Math.floor(rnd(fi, 1) * 256)}px ${Math.floor(rnd(fi, 2) * 256)}px`;
}

const chap = (t, s) => CHAP.push([t, s]);
const SHK = []; const shk = (t, amp = 12, d = .4) => SHK.push([t, amp, d]);
function shakeSum(t) { let x = 0, y = 0; for (const [a, amp, d] of SHK) { const s = shake(t, a, d, amp); x += s[0]; y += s[1]; } return [x, y]; }
TK_SHAKE = t => { const [x, y] = shakeSum(t); return [x * .5, y * .5]; };
const FL = (t, k = .6, d = .35) => FLASH.push([t, k, d]);
function drift(sc, o = {}) {
  sc.cam = t => { const lt = t - sc.s, [sx, sy] = shakeSum(t), bk = beatK(t, .18) * (o.pulse == null ? .004 : o.pulse); return { x: 960 + Math.sin(lt * .31) * (o.dx == null ? 5 : o.dx), y: 540 + Math.cos(lt * .27) * 4, z: (o.z0 || 1) + lt * (o.zr == null ? .003 : o.zr) + bk, sx, sy }; };
}
const PRELOAD = [];
function preImg(src) { const im = new Image(); im.src = src; PRELOAD.push(im.decode().catch(() => { throw Error('preload failed ' + src); })); return im; }
const IM_MEADOW=null, IM_FLAT=null; // unselected catalogues are not loaded
function sty(el, o = {}) {
  el.style.opacity = (o.o == null ? 1 : clamp(o.o)).toFixed(3);
  el.style.transform = `translate(${(o.x || 0).toFixed(1)}px,${(o.y || 0).toFixed(1)}px) scale(${(o.s == null ? 1 : o.s).toFixed(4)}) rotate(${(o.r || 0).toFixed(2)}deg)`;
  el.style.filter = o.f || '';
}
const kids = e => [...e.querySelectorAll(':scope > div > *')];
const sprY = (t, t0, d = .5, dist = 40) => (1 - EZ.spring(pr(t, t0, t0 + d))) * dist;
/* 一行内胶囊逐个弹入 */
function rowPop(cs, t, t0, gap = .12, o = {}) { const pa = cs[0] && cs[0].parentElement.parentElement; if (pa && pa._x != null && pa.style.opacity !== '1.000') place(pa, { o: 1 }); cs.forEach((c, i) => { const a = pr(t, t0 + i * gap, t0 + i * gap + .45); sty(c, { o: clamp(a * 5) * (o.o == null ? 1 : o.o), s: .5 + .5 * EZ.spring(a), y: (1 - EZ.spring(a)) * 20 }); }); }

/* =============== S1 · 0–5.23 一条私信：没有技术含量？ =============== */

tkKey(44.63, 'RS', .6);
{
  const sc = scene(50.87, 58.93, { trans: 'circle', td: .5, cx: 860, cy: 470, tc: '#000' }); chap(50.87, '// 09 — 讲清楚');
  sc.cam = t => { const [sx, sy] = shakeSum(t), z = 1 + (t - 50.87) * .004 + EZ.out(pr(t, 57.03, 57.6)) * .04; return { x: 960, y: 540, z, sx, sy }; };
  tkKey(50.87, 'RC', .6);
  const CX = 860, CY = 470;
  const pl = mk(sc.el, `<div style="width:560px;height:110px;border-radius:60px;background:rgba(255,255,255,.08);border:2px solid rgba(255,255,255,.55);box-shadow:inset 0 0 30px rgba(255,255,255,.12),0 0 40px rgba(255,180,60,.25);display:flex;align-items:center;gap:22px;padding:0 30px;overflow:hidden"><i style="width:56px;height:56px;border-radius:50%;background:radial-gradient(circle at 35% 35%,#fff,#ffd27a 60%,#ff8a1f);display:block;flex:none"></i><span class="w" style="font:700 54px ${FZ};color:#fff;white-space:nowrap"></span></div>`, CX, CY, { ax: .5, ay: .5 });
  const pw = pl.querySelector('.w');
  const SEQ = [[50.9, '讲清楚'], [52.47, '为什么？'], [53.9, '豆包'], [54.6, 'WorkBuddy'], [55.33, '国产大模型'], [56.1, '写 skill']];
  const big = mk(sc.el, `<div style="text-align:center"><div style="font:600 34px ${FZ};color:rgba(255,255,255,.8);letter-spacing:6px">反而</div><div style="font:900 156px/1.1 ${FZ};letter-spacing:-4px;background:linear-gradient(180deg,#fff 10%,#FFD27A 55%,#FF8A1F);-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 0 40px rgba(255,160,40,.55))">更考验技术</div></div>`, CX, CY, { ax: .5, ay: .5 });
  sc.update = t => {
    let i = -1; for (let k = 0; k < SEQ.length; k++) if (t >= SEQ[k][0]) i = k;
    const t0 = i >= 0 ? SEQ[i][0] : 50.9, a = pr(t, t0, t0 + .45), word = i >= 0 ? SEQ[i][1] : '';
    const shown = [...word].slice(0, Math.ceil(EZ.out(a) * [...word].length + 1e-6)).join('');
    setHTML(pw, shown); pw.style.filter = a < 1 ? `blur(${((1 - a) * 8).toFixed(1)}px)` : ''; pw.style.opacity = clamp(a * 3).toFixed(3);
    const o = pr(t, 50.95, 51.4), out = pr(t, 56.9, 57.1);
    place(pl, { o: o * (1 - out), s: (.8 + .2 * EZ.spring(o)) * (1 + beatK(t) * .03) });
    slamAt(big, t, 57.03, { k: 1.4, d: .32 });
  };
  sc.bg = (c, t) => {
    fill(c, '#000'); const k = pr(t, 50.9, 51.6), z = 1 + EZ.out(pr(t, 57.03, 57.8)) * .5;
    glowRing(c, t, CX, CY, 300 * z, k * (1 + .4 * pr(t, 57.03, 57.3)), { streak: 1 });
  };
  sc.fg = (c, t) => confetti(c, t, 57.05, CX, CY + 40, { n: 70, sp: 1400, cols: ['#FFD27A', '#fff', P.org, P.yel] });
  FL(57.03, .7, .4); shk(57.03, 18, .5);
  S(50.87, 'whoosh', .6); S(50.95, 'rise_s', .4); SEQ.forEach(([t0], i) => { if (i) S(t0, 'swipe', .35); }); S(57.03, 'hit', 1); S(57.03, 'crash', .5);
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
    fade.style.opacity = '0'; // output host owns final fade
    // Output host owns new captions.
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
outer.update=t=>{lastSource=t;drawAt(t);window.STICKER_FIT?.(host,'keyword-to-conclusion');};
outer.macroTransition=context=>doubaoTransition({wipe,circ,flash,world:nodes.world},FLASH,lastSource,{...context,scene:outer});
SFX.forEach(c=>{const {t,type,g,p,...extra}=c;FORWARD_S(t,type,g,p,extra);});
outer.stickerDiagnostics={clock:'source-geometry/output-media',sourceScenes:SCENES.length,sourceSfx:SFX.length,initialTalkKey:TKK[0]};
})(Scene,setFrame,tc,S);

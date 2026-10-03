((OUTPUT_TALK,OUTPUT_FACE,OUTPUT_TC,FORWARD_S,OUTPUT_FRAME) => {
const outer=new Scene(115.83333333333333,127.1,'#1B2220',{});
const host=document.createElement('div');host.className='pb-host';host.style.cssText='position:absolute;inset:0;overflow:hidden';outer.el.appendChild(host);
host.innerHTML="\n  <div data-pb-node=\"main\">\n    <div data-pb-node=\"bgP\"></div><div data-pb-node=\"bgD\"></div>\n    <canvas data-pb-node=\"cv0\" width=\"1920\" height=\"1080\"></canvas>\n    <div data-pb-node=\"scenes\"></div>\n    <div data-pb-node=\"halo\"></div>\n    <div data-pb-node=\"cam\" class=\"cam\"><img data-pb-node=\"camI\"><div class=\"lab\"><b>●</b> on air · 阿杜Next</div></div>\n    <div data-pb-node=\"ball\"></div>\n    <canvas data-pb-node=\"cv1\" width=\"1920\" height=\"1080\"></canvas>\n  </div>\n  <canvas data-pb-node=\"cv2\" width=\"1920\" height=\"1080\"></canvas>\n  <div data-pb-node=\"meta\"></div>\n  <div data-pb-node=\"flash\"></div>\n  <div data-pb-node=\"tagL\"></div><div data-pb-node=\"tagR\"></div><div data-pb-node=\"disc\">观点来自口播 · 相关新闻请自行查证</div>\n  <div data-pb-node=\"subs\"><div class=\"z\"></div><div class=\"e\"></div></div>\n";
const nodes=Object.fromEntries([...host.querySelectorAll('[data-pb-node]')].map(e=>[e.dataset.pbNode,e]));
/* 国庆第一天 · v2 — 基础库：时间函数、元素摆放、物理、动态大字、手写、粒子、转场 */
const W = 1920, H = 1080;
const PAP = '#F1EFE9', INK = '#17191A', TE = '#35D0B0', TED = '#1C9A82', RD = '#D9573C', CR = '#EFE8DA', GY = '#8C8A84', YL = '#F3E3A0', DKC = '#1B2220';
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, x) => a + (b - a) * x, pr = (t, a, b) => clamp((t - a) / (b - a));
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const noise = t => { const i = Math.floor(t), f = t - i, u = f * f * (3 - 2 * f); return lerp(hash(i), hash(i + 1), u) * 2 - 1; };
const EZ = {
  out: x => 1 - Math.pow(1 - x, 3), out5: x => 1 - Math.pow(1 - x, 5), expo: x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x),
  inout: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2, in: x => x * x * x, in2: x => x * x,
  back: x => { const c1 = 1.7, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
  spring: x => x >= 1 ? 1 : 1 - Math.exp(-7 * x) * Math.cos(8.5 * x) * (1 - x * .2),
};
const $ = id => nodes[id];
const SVGNS = 'http://www.w3.org/2000/svg';
const SFX = [];
const S = (t, type, g = 1, p = 0, x = {}) => SFX.push(Object.assign({ t: +t.toFixed(3), type, g, p }, x));
const IMGS = [], PEND = new Set();
function setSrc(im, s) { if (im._s !== s) { im._s = s; OUTPUT_FRAME(im, s); PEND.add(im); } }
const fr = (dir, i, n) => `${dir}/f_${String(clamp(Math.floor(i), 1, n)).padStart(4, '0')}.jpg`;
const wsrc = (ep, t) => `works/${ep}/f_${String(Math.floor(((t * 12) % 19 + 19) % 19) + 1).padStart(4, '0')}.jpg`;
let CUR = null, _id = 0;

/* ---------- 元素 ---------- */
function E(par, html, x = 0, y = 0, ax = .5, ay = .5) {
  const d = document.createElement('div'); d.innerHTML = html.trim(); const e = d.firstElementChild; e.classList.add('it'); e.style.position = 'absolute'; e.style.left = '0'; e.style.top = '0';
  (par.root || par).appendChild(e); e._x = x; e._y = y; e._ax = ax; e._ay = ay; e._id = ++_id; e.style.visibility = 'hidden';
  e.querySelectorAll('img').forEach(im => IMGS.push(im)); return e;
}
function put(e, o = {}) {
  const op = o.o ?? 1;
  if (op <= .002) { e.style.visibility = 'hidden'; return; }
  const x = o.x ?? e._x, y = o.y ?? e._y, s = o.s ?? 1, sx = (o.sx ?? 1) * s, sy = (o.sy ?? 1) * s;
  e.style.visibility = 'visible'; e.style.opacity = op.toFixed(3);
  e.style.transformOrigin = `${e._ax * 100}% ${e._ay * 100}%`;
  e.style.transform = `translate(${x.toFixed(1)}px,${y.toFixed(1)}px) translate(${-e._ax * 100}%,${-e._ay * 100}%) rotate(${(o.r || 0).toFixed(2)}deg) scale(${sx.toFixed(4)},${sy.toFixed(4)})`;
  e.style.filter = (o.blur || 0) > .1 ? `blur(${o.blur.toFixed(1)}px)` : '';
}
/* 入场/出场预设 */
function show(e, t, t0, o = {}) {
  if (t < t0 || (o.out != null && o.ok !== 'fall' && t > o.out + (o.od ?? .3))) { put(e, { o: 0 }); return 0; }
  const d = o.d ?? .5, k = pr(t, t0, t0 + d), kind = o.k || 'pop';
  let x = o.x ?? e._x, y = o.y ?? e._y, s = o.s ?? 1, r = o.r ?? 0, op = 1, blur = 0, sx = 1, sy = 1;
  if (kind === 'pop') { s *= .15 + .85 * EZ.back(k); r += (1 - EZ.out(k)) * (o.rr ?? -16); op = clamp(k * 5); }
  else if (kind === 'up') { const q = EZ.expo(k); y += (1 - q) * (o.dist ?? 60); op = clamp(k * 3); blur = (1 - q) * 6; }
  else if (kind === 'down') { const q = EZ.expo(k); y -= (1 - q) * (o.dist ?? 60); op = clamp(k * 3); }
  else if (kind === 'left' || kind === 'right') { const q = EZ.spring(k), dir = kind === 'left' ? -1 : 1; x += dir * (1 - q) * (o.dist ?? 900); r += dir * (1 - EZ.out(k)) * (o.rr ?? 6); }
  else if (kind === 'slam') { s *= 1 + (1 - EZ.out5(k)) * (o.amt ?? 1.3); op = clamp(k * 6); blur = (1 - k) * 10; }
  else if (kind === 'drop') { const dist = o.dist ?? 800, b = dropY(t - t0, dist, o.g ?? 5200, o.e ?? .35, 3); y -= b.h; sx = 1 + b.sq * .16; sy = 1 - b.sq * .16; r += (o.rr ?? 10) * clamp(b.h / dist); }
  else if (kind === 'fade') { op = EZ.out(k); }
  if (o.out != null && t > o.out) {
    const u = pr(t, o.out, o.out + (o.od ?? .3)), tt = t - o.out;
    if (o.ok === 'fall') { y += (o.vy ?? -250) * tt + 1900 * tt * tt; x += (o.vx ?? ((hash(e._id) - .5) * 400)) * tt; r += (o.vr ?? ((hash(e._id * 3) - .5) * 260)) * tt; }
    else if (o.ok === 'pop') { s *= 1 - EZ.in(u) * .85; op *= 1 - EZ.in(u); }
    else if (o.ok === 'left') x -= EZ.in(u) * 1400;
    else if (o.ok === 'right') x += EZ.in(u) * 1400;
    else { op *= 1 - u; y -= EZ.in(u) * (o.oy ?? 20); blur += u * 5; }
  }
  put(e, { x, y, s, r, o: op * (o.o ?? 1), blur, sx, sy }); return k;
}

/* ---------- 物理 ---------- */
// 从高度 h 自由落下，弹几次；返回离地高度和压扁量
function dropY(tt, h, g = 5200, e = .42, n = 4) {
  if (tt <= 0) return { h, sq: 0 };
  const tf = Math.sqrt(2 * h / g);
  if (tt < tf) return { h: h - .5 * g * tt * tt, sq: 0 };
  let t = tt - tf, imp = g * tf, v = imp * e;
  for (let i = 0; i < n; i++) { const T = 2 * v / g; if (t < T) return { h: v * t - .5 * g * t * t, sq: Math.exp(-t * 28) * Math.min(1, imp / 3000) }; t -= T; imp = v; v *= e; }
  return { h: 0, sq: Math.exp(-t * 28) * Math.min(1, imp / 3000) };
}
// 抛物线跳点序列 L=[[t,x,y,arcH],...]；arcH=0 为滚动
function hops(t, L) {
  if (t <= L[0][0]) return { x: L[0][1], y: L[0][2], sq: 0 };
  for (let i = 0; i < L.length - 1; i++) {
    const a = L[i], b = L[i + 1];
    if (t < b[0]) {
      const k = (t - a[0]) / (b[0] - a[0]), hh = b[3] ?? 0, kk = hh > 0 ? k : EZ.inout(k);
      const land = i > 0 && (a[3] ?? 0) > 0;
      return { x: lerp(a[1], b[1], kk), y: lerp(a[2], b[2], kk) - 4 * hh * k * (1 - k), sq: land ? Math.exp(-(t - a[0]) * 26) * .85 : 0 };
    }
  }
  const z = L[L.length - 1]; return { x: z[1], y: z[2], sq: (z[3] ?? 0) > 0 ? Math.exp(-(t - z[0]) * 26) * .85 : 0 };
}
function hopSfx(L, type = 'thud', g = .5) { L.slice(1).forEach(p => { if ((p[3] ?? 0) > 0) S(p[0], type, g, (p[1] / W - .5) * .8); }); }
// 抛出后落到地面 yF 并弹跳
function fallTo(tau, y0, vy0, yF, g = 3200, e = .3) {
  if (tau <= 0) return { y: y0, land: 0, t1: 1e9 };
  const a = .5 * g, b = vy0, c = y0 - yF, t1 = (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a);
  if (tau < t1) return { y: y0 + vy0 * tau + a * tau * tau, land: 0, t1 };
  let t = tau - t1, v = (vy0 + g * t1) * e;
  for (let i = 0; i < 3; i++) { const T = 2 * v / g; if (t < T) return { y: yF - (v * t - .5 * g * t * t), land: 1, t1 }; t -= T; v *= e; }
  return { y: yF, land: 1, t1 };
}

/* ---------- 动态大字：逐字从上方落下，可散落 ---------- */
function kin(par, segs, x, y, size, o = {}) {
  let html = '';
  for (const [txt, cls] of segs) {
    if (cls === 'dot') { html += `<span class="kdot"></span>`; continue; }
    for (const ch of [...txt]) html += ch === ' ' ? `<span class="${cls}">&nbsp;</span>` : `<span class="${cls}">${ch.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</span>`;
  }
  const e = E(par, `<div class="kin" style="font-size:${size}px;${o.style || ''}">${html}</div>`, x, y, o.ax ?? 0, o.ay ?? .5);
  e._c = [...e.querySelectorAll('span')]; e._dot = e.querySelector('.kdot'); return e;
}
function kinAt(e, t, t0, o = {}) {
  if (t < t0 - .001) { put(e, { o: 0 }); return; }
  put(e, { o: o.o ?? 1, x: o.x, y: o.y, s: o.s });
  const st = o.st ?? .06, dist = o.dist ?? 520;
  e._c.forEach((c, i) => {
    const tt = t - (t0 + i * st); let tx = 0, ty = 0, r = 0, sx = 1, sy = 1, op = 1;
    if (tt < 0) op = 0;
    else if (o.mode === 'slam') { const k = pr(tt, 0, .32); const s = 1 + (1 - EZ.out5(k)) * 1.6; sx = sy = s; op = clamp(k * 6); }
    else { const b = dropY(tt, dist, 6200, .28, 2); ty = -b.h; r = (hash(i * 3.7 + e._id * .13) - .5) * (o.rot ?? 70) * clamp(b.h / dist); sx = 1 + b.sq * .28; sy = 1 - b.sq * .3; }
    if (o.out != null) { const u = t - (o.out + i * (o.ost ?? .022)); if (u > 0) { tx += (hash(i * 9.1 + e._id) - .5) * 700 * u; ty += (-150 - hash(i * 5.3 + e._id) * 380) * u + .5 * 4200 * u * u; r += (hash(i * 2.2 + e._id) - .5) * 520 * u; } }
    c.style.opacity = op; c.style.transform = `translate(${tx.toFixed(1)}px,${ty.toFixed(1)}px) rotate(${r.toFixed(1)}deg) scale(${sx.toFixed(3)},${sy.toFixed(3)})`;
  });
}
function kinSfx(e, t0, o = {}) {
  const st = o.st ?? .06, land = o.mode === 'slam' ? .06 : Math.sqrt(2 * (o.dist ?? 520) / 6200); const n = e._c.length;
  e._c.forEach((c, i) => { if (c.classList.contains('kdot') || c.innerHTML === '&nbsp;') return; S(t0 + i * st + land, o.type ?? 'key_thock', o.g ?? .45, (i / Math.max(1, n - 1) - .5) * .7); });
}
function kinBox(e, i0, i1 = i0) {
  const a = e._c[i0], b = e._c[i1], ox = e._x - e._ax * e.offsetWidth, oy = e._y - e._ay * e.offsetHeight;
  return { x0: ox + a.offsetLeft, x1: ox + b.offsetLeft + b.offsetWidth, y0: oy + a.offsetTop, y1: oy + a.offsetTop + a.offsetHeight, w: e.offsetWidth, h: e.offsetHeight, ox, oy };
}
function kinDot(e, s = 1, base = .84) { const d = e._dot, ox = e._x - e._ax * e.offsetWidth, oy = e._y - e._ay * e.offsetHeight; return { x: ox + d.offsetLeft + d.offsetWidth / 2, y: oy + e.offsetHeight * base - 26 * s }; }

/* ---------- 手写批注 ---------- */
function hw(par, txt, x, y, size, col = RD, rot = -4, o = {}) { const e = E(par, `<div class="hw" style="font-size:${size}px;color:${col}">${txt}</div>`, x, y, o.ax ?? 0, o.ay ?? .5); e._r = rot; return e; }
function hwAt(e, t, t0, o = {}) {
  const od = o.od ?? .3; if (t < t0 || (o.out != null && t > o.out + od)) { put(e, { o: 0 }); return; }
  const op = o.out != null ? 1 - pr(t, o.out, o.out + od) : 1; put(e, { o: op, r: e._r, x: o.x, y: o.y, s: o.s });
  const k = pr(t, t0, t0 + (o.d ?? .5)); e.style.clipPath = `inset(-60% ${(100 - 100 * k).toFixed(1)}% -60% -8%)`;
}
const hwS = (t0, d = .5, g = .5) => S(t0, 'write', g, 0, { d });
function ink(par, d, col = RD, w = 4, o = {}) {
  const svg = par.svg || par, p = document.createElementNS(SVGNS, 'path');
  p.setAttribute('fill', 'none'); p.setAttribute('stroke', col); p.setAttribute('stroke-width', w); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round');
  svg.appendChild(p); p._o = o; p._svg = svg; p.style.display = 'none';
  if (typeof d === 'function') p._fn = d; else inkSet(p, d); return p;
}
function inkSet(p, d) {
  p.setAttribute('d', d); p._L = p.getTotalLength() || 1; p.style.strokeDasharray = `${p._L} ${p._L + 20}`; p.style.strokeDashoffset = p._L;
  if (p._o.arrow) {
    const L = p._L, e1 = p.getPointAtLength(L), e0 = p.getPointAtLength(Math.max(0, L - 12)), an = Math.atan2(e1.y - e0.y, e1.x - e0.x), a = p._o.arrow;
    let h = p._head; if (!h) { h = document.createElementNS(SVGNS, 'path'); ['fill', 'stroke', 'stroke-width', 'stroke-linecap', 'stroke-linejoin'].forEach(k => h.setAttribute(k, p.getAttribute(k))); p._svg.appendChild(h); p._head = h; h.style.display = 'none'; }
    h.setAttribute('d', `M ${(e1.x - a * Math.cos(an - .55)).toFixed(1)} ${(e1.y - a * Math.sin(an - .55)).toFixed(1)} L ${e1.x.toFixed(1)} ${e1.y.toFixed(1)} L ${(e1.x - a * Math.cos(an + .55)).toFixed(1)} ${(e1.y - a * Math.sin(an + .55)).toFixed(1)}`);
    h._L = h.getTotalLength(); h.style.strokeDasharray = `${h._L} ${h._L + 20}`;
  }
}
function inkAt(p, t, t0, o = {}) {
  const od = o.od ?? .3, vis = t >= t0 && !(o.out != null && t > o.out + od);
  p.style.display = vis ? '' : 'none'; if (p._head) p._head.style.display = p.style.display; if (!vis) return;
  if (p._fn && !p._set) { inkSet(p, p._fn()); p._set = 1; if (p._head) p._head.style.display = ''; }
  const op = o.out != null ? 1 - pr(t, o.out, o.out + od) : 1, d = o.d ?? .45, k = (o.ease ?? EZ.out)(pr(t, t0, t0 + d));
  p.style.opacity = op; p.style.strokeDashoffset = (p._L * (1 - k)).toFixed(1);
  if (p._head) { const kh = pr(t, t0 + d * .9, t0 + d + .12); p._head.style.opacity = op; p._head.style.strokeDashoffset = (p._head._L * (1 - kh)).toFixed(1); }
}
const scribEll = (cx, cy, rx, ry, rot = -6, seed = 1, turn = 1.12) => {
  let d = ''; const N = 60, c = Math.cos(rot * Math.PI / 180), s = Math.sin(rot * Math.PI / 180);
  for (let i = 0; i <= N; i++) { const a = -2.5 + i / N * turn * Math.PI * 2, w = 1 + (hash(seed + i * .37) - .5) * .04 + (i / N) * .07, x = Math.cos(a) * rx * w, y = Math.sin(a) * ry * w; d += (i ? 'L' : 'M') + (cx + x * c - y * s).toFixed(1) + ' ' + (cy + x * s + y * c).toFixed(1) + ' '; }
  return d;
};
const uline = (x1, y, x2, a = 7) => `M ${x1} ${y} C ${x1 + (x2 - x1) * .3} ${y + a} ${x1 + (x2 - x1) * .65} ${y - a} ${x2} ${y + 3}`;
const zig = (x1, y1, x2, y2, n = 7, a = 26) => { let d = `M ${x1} ${y1}`; for (let i = 1; i <= n; i++) { const k = i / n; d += ` L ${(lerp(x1, x2, k) + (i % 2 ? a * .3 : -a * .3)).toFixed(1)} ${(lerp(y1, y2, k) + (i % 2 ? -a : a)).toFixed(1)}`; } return d; };
const qc = (x1, y1, x2, y2, b = .25) => { const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1; return `M ${x1} ${y1} Q ${(mx - dy * b).toFixed(1)} ${(my + dx * b).toFixed(1)} ${x2} ${y2}`; };
const check = (x, y, s = 1) => `M ${x - 22 * s} ${y} L ${x - 6 * s} ${y + 18 * s} L ${x + 28 * s} ${y - 26 * s}`;

/* ---------- 粒子 / 吸入流 / 方块故障 / 震动 / 闪白 ---------- */
const PARTS = [];
function burst(t0, x, y, o = {}) {
  const n = o.n ?? 16, cols = o.cols || [o.col ?? '#fff'];
  for (let i = 0; i < n; i++) {
    const h1 = hash(t0 * 7.13 + i * 1.37 + x * .011), h2 = hash(t0 * 3.31 + i * 2.71 + y * .013), h3 = hash(t0 * 1.7 + i * 5.93);
    const ang = (o.ang ?? -Math.PI / 2) + (h1 - .5) * (o.spread ?? 6.283), sp = (o.spd ?? 650) * (.3 + .7 * h2);
    PARTS.push({ t0, x: x + (hash(i * 3.3 + t0) - .5) * (o.jx ?? 0), y: y + (hash(i * 4.1 + t0) - .5) * (o.jy ?? 0), vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp, g: o.g ?? 1500, life: (o.life ?? 1.1) * (.6 + .6 * h3), kind: o.kind ?? 'paper', col: cols[i % cols.length], sz: (o.sz ?? 11) * (.55 + .9 * h2), spin: (h1 - .5) * 18, drag: o.drag ?? 1.6, until: o.until ?? (CUR ? CUR.t1 : 1e9) });
  }
}
function drawParts(ctx, t) {
  for (const p of PARTS) {
    const tt = t - p.t0; if (tt < 0 || tt > p.life || t >= p.until) continue;
    const k = p.drag, f = (1 - Math.exp(-k * tt)) / k, x = p.x + p.vx * f, y = p.y + p.vy * f + .5 * p.g * tt * tt;
    ctx.globalAlpha = clamp((p.life - tt) / (p.life * .35)); ctx.fillStyle = p.col;
    if (p.kind === 'dot') { ctx.beginPath(); ctx.arc(x, y, p.sz * .4, 0, 6.283); ctx.fill(); }
    else if (p.kind === 'spark') { const e = Math.exp(-k * tt), vx = p.vx * e, vy = p.vy * e + p.g * tt; ctx.strokeStyle = p.col; ctx.lineWidth = 3; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - vx * .035, y - vy * .035); ctx.stroke(); }
    else { ctx.save(); ctx.translate(x, y); ctx.rotate(p.spin * tt + p.spin); const sq = Math.abs(Math.cos(p.spin * tt * 1.3)); ctx.fillRect(-p.sz / 2, -p.sz * .35 * sq - .5, p.sz, p.sz * .7 * sq + 1); ctx.restore(); }
  }
  ctx.globalAlpha = 1;
}
const STREAMS = [];
function stream(t0, t1, cx, cy, o = {}) { STREAMS.push({ t0, t1, cx, cy, n: o.n ?? 160, col: o.col ?? TE, dur: o.dur ?? .8, until: o.until ?? (CUR ? CUR.t1 : 1e9), seed: t0 * 1.37 }); }
function drawStreams(ctx, t) {
  for (const s of STREAMS) {
    if (t < s.t0 || t > s.t1 + s.dur || t >= s.until) continue;
    ctx.strokeStyle = s.col; ctx.lineCap = 'round';
    for (let i = 0; i < s.n; i++) {
      const st = s.t0 + (s.t1 - s.t0) * hash(s.seed + i * .731), k = (t - st) / s.dur; if (k < 0 || k > 1) continue;
      const gx = Math.round(hash(s.seed + i * 1.31) * 60) * 32, gy = Math.round(hash(s.seed + i * 2.17) * 34) * 32;
      const q = k * k * k, q2 = Math.pow(Math.max(0, k - .1), 3);
      ctx.globalAlpha = .2 + .7 * k; ctx.lineWidth = 1.5 + 2.5 * k; ctx.beginPath(); ctx.moveTo(lerp(gx, s.cx, q2), lerp(gy, s.cy, q2)); ctx.lineTo(lerp(gx, s.cx, q) + .1, lerp(gy, s.cy, q)); ctx.stroke();
    }
  }
  ctx.globalAlpha = 1;
}
const GL = []; const glitch = (t0, cols = [PAP, DKC, DKC, TE]) => { GL.push({ t0, cols }); S(t0 - .06, 'glitch', .35); };
function drawGlitch(ctx, t) {
  for (const g of GL) {
    const d = t - g.t0; if (d < -.1 || d > .12) continue;
    const p = (1 - Math.abs(d) / .11) * .55, fi = Math.round(t * 60);
    for (let i = 0; i < 16 * 9; i++) {
      if (hash(i * 1.7 + fi * 3.1) > p) continue;
      ctx.fillStyle = g.cols[Math.floor(hash(i * 2.3 + fi) * g.cols.length)];
      ctx.fillRect((i % 16) * 120, Math.floor(i / 16) * 120, hash(i * 5.1 + fi) < .3 ? 240 : 120, hash(i + fi * .7) < .4 ? 60 : 120);
    }
  }
}
const SHK = []; const shake = (t0, amp = 12, dur = .35) => SHK.push([t0, amp, dur]);
const shakeAt = t => { let x = 0, y = 0; for (const [t0, a, d] of SHK) { const k = pr(t, t0, t0 + d); if (k <= 0 || k >= 1) continue; const m = (1 - k) * a; x += m * noise(t * 47 + t0); y += m * noise(t * 47 + t0 + 9); } return [x, y]; };
const FL = []; const flash = (t0, a = .5) => FL.push([t0, a]);
const flashAt = t => Math.max(0, ...FL.map(([t0, a]) => t >= t0 ? a * (1 - pr(t, t0, t0 + .16)) : 0));

/* ---------- 场景 ---------- */
const SC = [];
function scene(t0, t1, mode, label, build) {
  const root = document.createElement('div'); root.className = 'scn'; $('scenes').appendChild(root);
  const svg = document.createElementNS(SVGNS, 'svg'); svg.setAttribute('class', 'ink'); svg.setAttribute('width', W); svg.setAttribute('height', H); root.appendChild(svg);
  const sc = { t0, t1, mode, label, root, svg, update: () => { } }; CUR = sc; build(sc); CUR = null; SC.push(sc); return sc;
}

_id=281;
/* 国庆第一天 · 复刻进度汇报 v3 — Claude / 新字幕 / 新闻截图 / 开源署名
   参考片手法：纸面画布 / 手写批注逐笔画出 / 真实物理（落体、压扁、洋葱皮）/ 大号动态字逐字落下再散落 /
   深浅整屏硬切 / 卡片被吸进发光球 + 碎纸 / 放射网络线 / 天花板线 + S 曲线 / 方块故障转场 / 手画圈住网址 */

/* ---------- 主持人卡位 [x, y, w, h, radius, opacity] ---------- */
const POSE = {
  R: [1500, 470, 440, 782, 26, 1], L: [420, 470, 440, 782, 26, 1], CIR: [1700, 236, 280, 280, 140, 1], BR: [1690, 728, 300, 300, 150, 1],
  CC: [960, 440, 300, 300, 150, 1], BL: [250, 680, 300, 300, 150, 1], CC2: [960, 420, 420, 420, 210, 1], HIDE: [2300, 470, 440, 782, 26, 0], HIDEL: [-380, 470, 440, 782, 26, 0],
};
const CK = []; const CAM = (t, p) => CK.push([t, p]);
[[-1, 'R'], [2.9, 'CC'], [9.2, 'R'], [11.37, 'HIDE'], [13.73, 'R'], [20.63, 'L'], [23.43, 'HIDEL'], [25.0, 'HIDE'], [25.57, 'R'], [30.77, 'CIR'], [33.1, 'L'],
 [40.47, 'BR'], [45.43, 'CIR'], [57.2, 'CC2'], [58.17, 'BR'], [63.63, 'R'], [69.83, 'BL'], [78.07, 'R'], [88.4, 'CIR'], [92.43, 'R'], [98.53, 'HIDE'], [99.87, 'R'],
 [109.4, 'L'], [113.73, 'R'], [133.83, 'HIDE']].forEach(([t, p]) => CAM(t, p));

/* ---------- 贴纸零件 ---------- */
const tape = (r = -3, l = '50%') => `<i style="position:absolute;left:${l};top:-15px;width:100px;height:30px;margin-left:-50px;background:rgba(255,255,255,.62);transform:rotate(${r}deg);box-shadow:0 1px 3px rgba(0,0,0,.08)"></i>`;
const note = (html, w = 260, fs = 40) => `<div class="note" style="position:relative;width:${w}px;padding:30px 24px 30px;font:400 ${fs}px 'Hannotate SC',Caveat;color:#2b2616;line-height:1.22;white-space:normal">${tape(-4)}${html}</div>`;
const lines = (n, w0 = 100, seed = 1) => Array.from({ length: n }, (_, i) => `<i class="ln" style="width:${(w0 - hash(seed + i) * 40).toFixed(0)}%"></i>`).join('');
const gimg = (n, h, extra = '') => `<img src="gen/${n}_cut.png" style="height:${h}px;display:block;filter:drop-shadow(0 26px 30px rgba(40,30,10,.16));${extra}">`;
const person = (col = INK, bg = '#fff', d = 70) => `<div style="width:${d}px;height:${d}px;border-radius:50%;background:${bg};box-shadow:0 10px 22px rgba(0,0,0,.18);display:flex;align-items:flex-end;justify-content:center;overflow:hidden"><svg width="${d * .64}" height="${d * .74}" viewBox="0 0 44 50"><circle cx="22" cy="16" r="11" fill="${col}"/><path d="M1 52 C1 30, 43 30, 43 52" fill="${col}"/></svg></div>`;
const stamp = (txt, col = RD, fs = 70, cls = 'ys') => `<div class="${cls}" style="border:7px solid ${col};color:${col};padding:4px 26px 8px;font-size:${fs}px;border-radius:12px;opacity:.92;mix-blend-mode:multiply">${txt}</div>`;
const doc = (title, n = 5, w = 300, seed = 1, extra = '') => `<div class="ppr" style="width:${w}px;padding:24px 26px 26px">${title ? `<div class="mono" style="font-size:17px;color:${GY};letter-spacing:2px">${title}</div>` : ''}${extra}${lines(n, 100, seed)}</div>`;
const redact = (w = 190, seed = 1) => `<div class="ppr" style="width:${w}px;padding:18px 18px 20px">${Array.from({ length: 4 }, (_, i) => `<i style="display:block;height:12px;margin-top:9px;border-radius:2px;width:${(100 - hash(seed * 7 + i) * 45).toFixed(0)}%;background:${i % 2 ? '#E2DED3' : '#17191A'}"></i>`).join('')}</div>`;
// 吸入：沿螺旋飞进 (cx,cy)
function absorb(e, t, t0, x0, y0, cx, cy, d = .5, o = {}) {
  const k = pr(t, t0, t0 + d); if (k >= 1) { put(e, { o: 0 }); return 1; }
  const q = EZ.in2(k), dir = o.dir ?? 1, ang = q * 1.4 * dir, dx = (x0 - cx) * (1 - q), dy = (y0 - cy) * (1 - q), ca = Math.cos(ang), sa = Math.sin(ang);
  put(e, { x: cx + dx * ca - dy * sa, y: cy + dx * sa + dy * ca, s: (o.s ?? 1) * (1 - q * .93), r: (o.r ?? 0) + q * 420 * dir }); return k;
}
const proj = (tt, x0, y0, vx, vy, g = 2600) => [x0 + vx * tt, y0 + vy * tt + .5 * g * tt * tt];
function typeAt(e, t, t0, t1) { if (e._full == null) e._full = e.textContent; const n = Math.round(e._full.length * pr(t, t0, t1)); e.textContent = e._full.slice(0, n) + (t > t0 && n < e._full.length && Math.floor(t * 4) % 2 ? '|' : ''); }
const ballOnDot = (D, t, t0, h = 560, g = 5200, e = .42) => { const b = dropY(t - t0, h, g, e, 3); return { x: D.x, y: D.y - b.h, sq: b.sq, s: 1 }; };

/* =====================================================================
   01 · 开场 0 – 2.9  大标题砸入 + 小球落成句点
   ===================================================================== */
scene(115.83, 124.77, 'P', '// 19 — 这几天全盘托出', sc => {
  const hdr = E(sc, `<div style="width:380px;height:96px;background:${RD};border-radius:14px 14px 0 0;color:#fff;display:flex;align-items:center;justify-content:center;gap:14px"><span class="an" style="font-size:44px">OCT</span><span class="zh" style="font-size:38px">国庆假期</span></div>`, 340, 300, .5, 1);
  const PG = Array.from({ length: 7 }, (_, i) => E(sc, `<div class="ppr" style="width:380px;height:330px;border-radius:0 0 14px 14px;display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="an" style="font-size:200px;line-height:1">${i + 1}</div><div class="mono" style="font-size:20px;color:${GY}">DAY ${i + 1}</div></div>`, 340, 300, .5, 0)).reverse();
  const td = hw(sc, '这几天 →', 600, 230, 58, RD, -5);
  const yrs = E(sc, `<div class="mono" style="font-size:24px;color:${GY};letter-spacing:3px">最近一两年 · 2025 → 2026</div>`, 110, 230, 0, .5);
  const k1 = kin(sc, [['AI', 'an xt'], [' + ', 'an xi'], ['内容制作', 'ys xi']], 110, 380, 160);
  const CH = ['口播剪辑', '动效', '字幕', '配乐音效', '工作流', 'Skill'];
  const chips = CH.map((s, i) => E(sc, `<span class="pill" style="background:#fff;box-shadow:0 8px 18px rgba(0,0,0,.08);font-size:28px">${s}</span>`, 110 + (i % 3) * 240, 560 + Math.floor(i / 3) * 80, 0, .5));
  const box = E(sc, `<div style="position:relative;width:340px;height:200px"><div style="position:absolute;inset:0;background:#C99A5B;border-radius:6px;box-shadow:0 22px 40px rgba(60,40,0,.2)"></div><div style="position:absolute;left:0;right:0;top:0;height:30px;background:#B5864A;border-radius:6px 6px 0 0"></div><div style="position:absolute;left:150px;top:0;width:40px;height:200px;background:rgba(255,255,255,.25)"></div></div>`, 620, 860, .5, 1);
  const flL = E(sc, `<div style="width:170px;height:26px;background:#B5864A;border-radius:4px"></div>`, 450, 660, 0, .5), flR = E(sc, `<div style="width:170px;height:26px;background:#B5864A;border-radius:4px"></div>`, 790, 660, 1, .5);
  const GS = [['经验', 'note', 250, 260, -8], ['观点', 'card', 620, 210, 4], ['干货', 'teal', 990, 270, -4]];
  const gs = GS.map(([s, k, x, y, r]) => { const bg = k === 'note' ? `background:${YL}` : k === 'teal' ? `background:${TE};color:#fff` : 'background:#fff'; const e = E(sc, `<div style="${bg};width:250px;height:190px;border-radius:${k === 'note' ? 3 : 18}px;box-shadow:0 22px 40px rgba(30,25,15,.18);display:flex;align-items:center;justify-content:center"><span class="ys" style="font-size:96px">${s}</span></div>`, x, y); e._r = r; return e; });
  const kk = kin(sc, [['全盘托出', 'ys xr']], 620, 560, 150, { ax: .5 });
  const TT = i => 116.05 + i * .36, GT = [122.35, 122.75, 123.15];
  sc.update = t => {
    const out1 = 118.6;
    show(hdr, t, 115.88, { k: 'drop', dist: 700, g: 8000, e: .25, out: out1, ok: 'left', od: .35 });
    PG.forEach((e, j) => { const i = 6 - j; if (t > out1 + .35) { put(e, { o: 0 }); return; } const base = show(e, t, 115.88, { k: 'drop', dist: 700, g: 8000, e: .25, out: out1, ok: 'left', od: .35 }); if (i < 6 && t > TT(i)) { const tt = t - TT(i), [x, y] = proj(tt, 340 + 20, 300, (hash(i) - .3) * 600, -500, 3600); put(e, { x, y, r: tt * (hash(i * 3) - .2) * 500, o: 1 - pr(tt, .5, .7) }); } });
    hwAt(td, t, 116.0, { d: .4, out: out1 });
    show(yrs, t, 118.75, { k: 'up', out: 121.95 }); kinAt(k1, t, 118.85, { st: .06, dist: 480, out: 121.95 }); chips.forEach((e, i) => show(e, t, 119.8 + i * .14, { k: 'pop', out: 121.95, ok: 'fall' }));
    const bk = pr(t, 122.1, 122.3); show(box, t, 121.9, { k: 'up', r: Math.sin(bk * Math.PI * 3) * 4 * (bk < 1 ? 1 : 0) });
    show(flL, t, 121.95, { k: 'fade', r: -lerp(0, 120, EZ.back(pr(t, 122.2, 122.5))) }); show(flR, t, 121.95, { k: 'fade', r: lerp(0, 120, EZ.back(pr(t, 122.2, 122.5))) });
    gs.forEach((e, i) => { const t0 = GT[i]; if (t < t0) { put(e, { o: 0 }); return; } const k = pr(t, t0, t0 + .55), x0 = 620, y0 = 700; const q = EZ.out(k); const land = k >= 1 ? Math.exp(-(t - t0 - .55) * 16) * .2 : 0; put(e, { x: lerp(x0, e._x, q), y: lerp(y0, e._y, k) - Math.sin(k * Math.PI) * 260, r: lerp((i - 1) * 90, e._r, q), s: lerp(.3, 1, EZ.back(k)), sx: 1 + land, sy: 1 - land }); });
    kinAt(kk, t, 123.65, { mode: 'slam', st: .06 });
  };
  hwS(116.0, .4); S(115.88 + Math.sqrt(1400 / 8000), 'thud', .7); for (let i = 0; i < 6; i++) S(TT(i), 'slash', .25, -.2); S(118.6, 'swoosh', .5);
  kinSfx(k1, 118.85, { st: .06, dist: 480, g: .4 }); CH.forEach((s, i) => S(119.8 + i * .14, 'pop', .3, (i % 3 - 1) * .4)); S(121.9, 'card', .4); S(122.12, 'rep', .5); S(122.2, 'boing', .4);
  GT.forEach((t0, i) => { S(t0, 'jump', .3, (i - 1) * .5); S(t0 + .55, 'thud', .6, (i - 1) * .5); }); burst(122.3, 620, 680, { n: 26, cols: [RD, YL, TE, '#fff'], spd: 900, g: 1500, life: 1.3, ang: -Math.PI / 2, spread: 1.8 });
  [0, 1, 2, 3].forEach(i => S(123.67 + i * .06, 'key_thock', .45)); S(123.85, 'hit', .9); flash(123.85, .2); shake(123.85, 12);
});
scene(124.77, 127.1, 'P', '// 20 — 更新会比较多', sc => {
  const PS = [[260, 790], [500, 800], [740, 790], [980, 800], [380, 660], [620, 670], [860, 660], [500, 530], [740, 540], [620, 410]];
  const cs = PS.map(([x, y], i) => { const e = E(sc, `<div class="ppr" style="width:230px;height:130px;padding:14px;position:relative;overflow:hidden"><div style="position:absolute;inset:0;background:linear-gradient(135deg,${['#E4F6F1', '#F6E7DF', '#ECEAE3'][i % 3]},#fff)"></div><div class="mono" style="position:relative;font-size:18px;color:${GY}">EP ${String(11 + i).padStart(2, '0')}</div><div style="position:absolute;left:50%;top:50%;margin:-20px 0 0 -16px;border-left:34px solid ${i % 2 ? TE : RD};border-top:20px solid transparent;border-bottom:20px solid transparent"></div></div>`, x, y); e._r = (hash(i * 7) - .5) * 16; return e; });
  const hd = hw(sc, '更新会比较多！', 110, 200, 84, RD, -4);
  const ns = E(sc, `<div class="mono" style="font-size:17px;color:${GY}">集数为示意</div>`, 60, 880, 0, .5);
  sc.update = t => {
    cs.forEach((e, i) => { const t0 = 124.82 + i * .14; if (t < t0) { put(e, { o: 0 }); return; } const f = fallTo(t - t0, -200, 0, e._y, 5600, .28); put(e, { y: f.y, r: e._r + (f.land ? 0 : (t - t0) * 60) }); });
    hwAt(hd, t, 125.9, { d: .5 }); show(ns, t, 125.0, { k: 'fade' });
  };
  PS.forEach(([x, y], i) => { const t1 = Math.sqrt(2 * (y + 200) / 5600); S(124.82 + i * .14 + t1, 'thud', .35, (x / W - .5)); }); hwS(125.9, .5);
});
/* 国庆第一天 v3 — 渲染主循环：场景切换、主持人卡、主线小球（洋葱皮/压扁/拖影）、画布特效、角标、字幕 */

const TALK_N = 4189;
const main = $('main'), bgP = $('bgP'), bgD = $('bgD'), camE = $('cam'), camI = $('camI'), ballE = $('ball'), haloE = $('halo');
const c0 = $('cv0').getContext('2d'), c1 = $('cv1').getContext('2d'), c2 = $('cv2').getContext('2d');
IMGS.push(camI);

/* ---------- 场景 15：整个画面缩成一块"屏"，外面写批注 ---------- */
const MR = { root: $('meta') }; MR.svg = document.createElementNS(SVGNS, 'svg'); MR.svg.setAttribute('width', W); MR.svg.setAttribute('height', H); $('meta').appendChild(MR.svg);
const mFrame = ink(MR, 'M 176 118 L 1404 112 L 1408 826 L 172 830 Z', RD, 6);
const mA = hw(MR, '↖ 这条视频', 1440, 190, 64, '#EFE8DA', -4), mB = hw(MR, '如果还不错……', 1440, 420, 56, '#EFE8DA', -3);
const mC = ink(MR, check(1610, 600, 2.4), TE, 12), mD = hw(MR, '= 进展还不错', 1440, 760, 60, TE, -3);
const mScale = t => 1 - .38 * EZ.inout(pr(t, 102.75, 103.3)) + .38 * EZ.inout(pr(t, 105.3, 105.85));
S(102.75, 'whoosh', .5); S(103.3, 'thud', .5); S(103.35, 'marker', .5); hwS(103.5, .5); hwS(103.85, .5); S(104.53, 'check', .9, 0, { n: 3 }); S(104.55, 'achieve', .4); hwS(104.8, .5); S(105.3, 'whoosh', .5);
function drawMeta(t) {
  const on = t > 102.7 && t < 105.9;
  inkAt(mFrame, t, 103.3, { d: .45, out: 105.25, od: .15 }); hwAt(mA, t, 103.5, { d: .45, out: 105.25, od: .15 }); hwAt(mB, t, 103.85, { d: .5, out: 105.25, od: .15 });
  inkAt(mC, t, 104.53, { d: .25, out: 105.25, od: .15 }); hwAt(mD, t, 104.8, { d: .5, out: 105.25, od: .15 });
  return on;
}

/* ---------- 主持人卡 ---------- */
function camPose(t) {
  let i = 0; while (i + 1 < CK.length && t >= CK[i + 1][0]) i++;
  const [tk, pk] = CK[i], prev = i > 0 ? POSE[CK[i - 1][1]] : POSE[pk], cur = POSE[pk];
  const k = pr(t, tk, tk + .6), q = EZ.spring(k), qs = EZ.out(pr(t, tk, tk + .45));
  const hideTo = cur[5] === 0, hideFrom = prev[5] === 0;
  let x = lerp(prev[0], cur[0], hideTo ? EZ.in(pr(t, tk, tk + .3)) : q), y = lerp(prev[1], cur[1], q);
  const w = lerp(prev[2], cur[2], hideTo ? 0 : qs), h = lerp(prev[3], cur[3], hideTo ? 0 : qs), r = lerp(prev[4], cur[4], hideTo ? 0 : qs);
  let o = hideTo ? 1 - pr(t, tk, tk + .08) : 1;
  if (hideTo && hideFrom) o = 0;
  const vx = cur[0] - prev[0], rot = (1 - q) * clamp(vx / 200, -6, 6) * (k > 0 && k < 1 ? 1 : 0);
  return { x, y, w, h, r, o, rot, sq: Math.abs(w - h) < 30 };
}
function drawCam(t, dark) {
  const p = camPose(t); if (p.o <= .002 || t > 133.83 + .35) { camE.style.visibility = 'hidden'; return; }
  camE.style.visibility = 'visible'; camE.classList.toggle('dk', dark);
  camE.style.width = p.w + 'px'; camE.style.height = p.h + 'px'; camE.style.borderRadius = p.r + 'px'; camE.style.opacity = p.o;
  const bob = Math.sin(t * 1.3) * 5;
  camE.style.transform = `translate(${(p.x - p.w / 2).toFixed(1)}px,${(p.y - p.h / 2 + bob).toFixed(1)}px) rotate(${(p.rot + Math.sin(t * .6) * .6).toFixed(2)}deg)`;
  setSrc(camI, OUTPUT_TALK(window.MACRO_OUTPUT_T));
  const f = OUTPUT_FACE(window.MACRO_OUTPUT_T), sc0 = Math.max(p.w / 720, p.h / 1280), zoom = p.sq ? (p.h * .46) / (f.h * 1280 * sc0) : 1;
  const s = sc0 * Math.max(1, zoom), iw = 720 * s, ih = 1280 * s;
  const ox = clamp(p.w / 2 - f.cx * iw, p.w - iw, 0), oy = clamp(p.h * (p.sq ? .5 : .42) - f.cy * ih, p.h - ih, 0);
  camI.style.width = iw.toFixed(1) + 'px'; camI.style.height = ih.toFixed(1) + 'px'; camI.style.left = ox.toFixed(1) + 'px'; camI.style.top = oy.toFixed(1) + 'px';
  camE.querySelector('.lab').style.display = p.w > 400 && p.h > 600 ? '' : 'none';
}

/* ---------- 主线小球 ---------- */
function ballOf(sc, t) { if (!sc || !sc.ball || t < sc.t0 || t >= sc.t1) return null; const b = sc.ball(t); return b ? Object.assign({ s: 1, sq: 0, glow: 0 }, b) : null; }
function drawBall(sc, t, dark) {
  const b = ballOf(sc, t);
  if (!b || b.s <= .01) { ballE.style.visibility = 'hidden'; haloE.style.visibility = 'hidden'; return; }
  const pb = ballOf(sc, t - 1 / 60) || b, vx = (b.x - pb.x) * 60, vy = (b.y - pb.y) * 60, sp = Math.hypot(vx, vy);
  const st = 1 + clamp((sp - 500) / 4000, 0, .45), an = Math.atan2(vy, vx) * 180 / Math.PI;
  const R = 26 * b.s, sx = 1 + b.sq * .45, sy = 1 - b.sq * .4;
  ballE.style.visibility = 'visible';
  ballE.style.transformOrigin = '50% 100%';
  ballE.style.transform = `translate(${(b.x - 26).toFixed(1)}px,${(b.y - 26).toFixed(1)}px) translate(0,${(26 * (b.s - 1)).toFixed(1)}px) scale(${b.s.toFixed(3)}) scale(${sx.toFixed(3)},${sy.toFixed(3)})` + (st > 1.01 && b.sq < .05 ? ` rotate(${an.toFixed(1)}deg) scale(${st.toFixed(3)},${(1 / st).toFixed(3)}) rotate(${(-an).toFixed(1)}deg)` : '');
  ballE.style.transformOrigin = st > 1.01 && b.sq < .05 ? '50% 50%' : '50% 100%';
  if (b.glow > .01 || dark) { const hs = b.s * 3.4 * (1 + .06 * Math.sin(t * 7)); haloE.style.visibility = 'visible'; haloE.style.opacity = Math.max(b.glow, dark ? .6 : 0); haloE.style.transform = `translate(${(b.x - 50).toFixed(1)}px,${(b.y - 50).toFixed(1)}px) scale(${hs.toFixed(3)})`; }
  else haloE.style.visibility = 'hidden';
  // 洋葱皮：过去 0.4s 的位置画成虚线圆
  c1.save(); c1.setLineDash([4, 5]); c1.lineWidth = 1.6; c1.strokeStyle = dark ? 'rgba(239,232,218,.42)' : 'rgba(40,60,56,.38)';
  let lx = b.x, ly = b.y;
  for (let i = 1; i <= 12; i++) {
    const g = ballOf(sc, t - i * .034); if (!g || g.s <= .01) break;
    if (Math.hypot(g.x - lx, g.y - ly) < 16) continue; lx = g.x; ly = g.y;
    if (Math.hypot(g.x - b.x, g.y - b.y) < 30) continue;
    c1.globalAlpha = 1 - i / 13; c1.beginPath(); c1.ellipse(g.x, g.y, 26 * g.s * (1 + g.sq * .45), 26 * g.s * (1 - g.sq * .4), 0, 0, 6.283); c1.stroke();
  }
  c1.restore();
}

/* ---------- 角标 ---------- */
const tagL = $('tagL'), tagR = $('tagR'), disc = $('disc');
const tc = t => { const f = Math.floor((t % 1) * 24), s = Math.floor(t); return `00:${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}:${String(f).padStart(2, '0')}`; };

/* ---------- 字幕 ---------- */
const sz = nodes.subs.querySelector('.z'), se = nodes.subs.querySelector('.e'); let curS = -1;
const subCol = x => x >= 1 ? '#FFFFFF' : x > 0 ? '#9FF3E0' : '#E4E2DC';
function subs(t) {
  const i = SUBS.findIndex(g => t >= g.t0 - .05 && t < g.t1 + .2); if (i < 0) { $('subs').style.opacity = 0; return; }
  const g = SUBS[i]; if (i !== curS) { curS = i; sz.innerHTML = [...g.zh].map(c => `<span>${c === ' ' ? '&nbsp;' : c}</span>`).join(''); se.innerHTML = g.en.split(' ').map(w => `<span>${w}</span>`).join(' '); }
  const tot = g.sp.reduce((a, s) => a + Math.max(1, s[2]), 0); let acc = 0, p = 1;
  for (const [a, b, n] of g.sp) { const w = Math.max(1, n); if (t < a) { p = acc / tot; break; } if (t < b) { p = (acc + w * (t - a) / (b - a)) / tot; break; } acc += w; }
  [...sz.children].forEach((c, k, A) => c.style.color = subCol(clamp(p * A.length - k))); [...se.children].forEach((c, k, A) => c.style.color = subCol(clamp(p * A.length - k)));
  const long = g.zh.length > 34; sz.style.fontSize = long ? '37px' : '42px'; $('subs').style.top = (long ? 930 : 948) + 'px';
  $('subs').style.opacity = Math.min(pr(t, g.t0 - .05, g.t0 + .1), 1 - pr(t, g.t1 + .05, g.t1 + .2));
}

/* ---------- 每帧 ---------- */
function drawAt(t) {
  const sc = SC.find(s => t >= s.t0 && t < s.t1) || SC[SC.length - 1];
  const dark = sc.mode === 'D';
  bgP.style.opacity = dark ? 0 : 1; bgD.style.opacity = dark ? 1 : 0;
  SC.forEach(s => { const on = s === sc; s.root.style.display = on ? '' : 'none'; });
  c0.clearRect(0, 0, W, H); c1.clearRect(0, 0, W, H); c2.clearRect(0, 0, W, H);
  sc.update(t);
  // 镜头：切场时轻推 + 震动 + 场景 15 的缩屏
  const punch = 1 + .035 * (1 - EZ.out(pr(t, sc.t0, sc.t0 + .3))), [shx, shy] = shakeAt(t), ms = mScale(t), isMeta = ms < .999;
  main.style.transform = `translate(${(shx - 170 * (1 - ms) / .38).toFixed(1)}px,${(shy - 30 * (1 - ms) / .38).toFixed(1)}px) scale(${(punch * ms).toFixed(4)})`;
  main.style.borderRadius = isMeta ? '18px' : '0'; main.style.boxShadow = isMeta ? '0 40px 90px rgba(0,0,0,.5)' : 'none';
  drawMeta(t);
  drawStreams(c0, t); drawCam(t, dark); drawBall(sc, t, dark); drawParts(c1, t); drawGlitch(c2, t);
  $('flash').style.opacity = flashAt(t);
  // 角标
  const tcol = dark || isMeta ? 'rgba(239,232,218,.55)' : 'rgba(23,25,26,.45)';
  tagL.textContent = t >= 133.83 ? '' : sc.label; tagL.style.color = tcol; tagR.innerHTML = `${window.PACK_BRAND_HTML}&nbsp;&nbsp;${OUTPUT_TC(window.MACRO_OUTPUT_T)}`; tagR.style.color = tcol;
  const dOn = t > 69.9 && t < 92.4; disc.style.opacity = dOn ? 1 : 0; disc.style.color = dark ? '#cfd6d3' : '#5b5a55'; disc.style.background = dark ? 'rgba(255,255,255,.07)' : 'rgba(23,25,26,.06)';
  if(typeof SUBS!=='undefined'&&CONFIG.subtitles!==false) subs(window.MACRO_OUTPUT_T); else nodes.subs.style.opacity=0;
}

/* ---------- 音效里没有的类型 ---------- */


SFX.filter(c=>c.t>=115.83333333333333-.02&&c.t<127.1).forEach(c=>{const {t,type,g,p,...x}=c;FORWARD_S(t,type,g,p,x);});
outer.update=t=>drawAt(t);
})(talkSrc,faceAt,tc,S,setFrame);

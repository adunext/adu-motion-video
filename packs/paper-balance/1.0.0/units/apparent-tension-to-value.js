(() => {
const A=13.73,Z=25.57,sc=new Scene(A,Z,'#F4F2EC',{});
const host=document.createElement('div');host.className='nd-host';host.style.cssText='position:absolute;inset:0;overflow:hidden';sc.el.appendChild(host);
const nodes={};
for(const [id,cls,style] of [['paper','nd-paper','position:absolute;inset:0'],['dark','nd-dark','position:absolute;inset:0'],['cam','nd-camera','position:absolute;inset:0;perspective:1600px'],['ov','ov','position:absolute;inset:0'],['flash','ov','position:absolute;inset:0;background:#fff;opacity:0;z-index:15']]){const e=document.createElement('div');e.className=cls;e.style.cssText=style;host.appendChild(e);nodes[id]=e;}
const world=document.createElement('div');world.className='nd-world';world.style.cssText='position:absolute;left:960px;top:540px;width:0;height:0;transform-style:preserve-3d';nodes.cam.appendChild(world);nodes.world=world;
const inkRoot=document.createElementNS('http://www.w3.org/2000/svg','svg');inkRoot.setAttribute('width',1920);inkRoot.setAttribute('height',1080);inkRoot.style.cssText='position:absolute;left:0;top:0;z-index:5';host.insertBefore(inkRoot,nodes.flash);nodes.ink=inkRoot;
const $=id=>nodes[id];
const mk=(par,html)=>{const d=document.createElement('div');d.innerHTML=html.trim();const e=d.firstElementChild;(typeof par==='string'?$(par):par).appendChild(e);return e;};
const imgs=[];const setSrc=(im,s)=>{if(im._s!==s){im._s=s;im.src=s;}};
const TALK_END=137.77,END=143.5;
const INK = '#16181A', PAP = '#F4F2EC', TE = '#2FD3B4', RD = '#D9573C', GY = '#8C8C8C';
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)), lerp = (a, b, x) => a + (b - a) * x, pr = (t, a, b) => clamp((t - a) / (b - a));
const hash = n => { const s = Math.sin(n * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
const EZ = { out: x => 1 - Math.pow(1 - x, 3), io: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2, in: x => x * x * x, back: x => { const c = 1.7; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
  spring: x => x >= 1 ? 1 : 1 - Math.exp(-7 * x) * Math.cos(8.5 * x) * (1 - x * .2), elastic: x => x <= 0 ? 0 : x >= 1 ? 1 : Math.pow(2, -10 * x) * Math.sin((x * 10 - .75) * 2.094) + 1 };
const win = (t, a, b, fi = .4, fo = .35) => Math.min(EZ.out(pr(t, a, a + fi)), 1 - pr(t, b - fo, b));
const P3 = (e, x, y, z, ry = 0, rx = 0, s = 1, o = 1, rz = 0) => { if (o <= .002) { e.style.display = 'none'; return; } e.style.display = ''; e.style.opacity = o; e.style.transform = `translate(-50%,-50%) translate3d(${x}px,${y}px,${z}px) rotateY(${ry}deg) rotateX(${rx}deg) rotateZ(${rz}deg) scale(${s})`; };
const V2 = (e, o, dx = 0, dy = 0, s = 1, r = 0) => { if (e._d === undefined) e._d = getComputedStyle(e).display === 'none' ? '' : e.style.display; if (o <= .002) { e.style.display = 'none'; return; } e.style.display = e._d; e.style.opacity = o; e.style.transform = `translate(${dx}px,${dy}px) scale(${s}) rotate(${r}deg)`; };
const SVGNS = 'http://www.w3.org/2000/svg';
function inkPath(d, col = RD, w = 4) { const p = document.createElementNS(SVGNS, 'path'); p.setAttribute('d', d); p.setAttribute('fill', 'none'); p.setAttribute('stroke', col); p.setAttribute('stroke-width', w); p.setAttribute('stroke-linecap', 'round'); p.setAttribute('stroke-linejoin', 'round'); $('ink').appendChild(p); p._L = p.getTotalLength(); p.style.strokeDasharray = p._L; p.style.strokeDashoffset = p._L; return p; }
function inkText(txt, x, y, size, col = RD, rot = -4) { const e = mk('ov', `<div class="ov hand" style="left:${x}px;top:${y}px;font-size:${size}px;color:${col};transform-origin:0 50%;white-space:nowrap;z-index:6"><span>${txt}</span></div>`); e._rot = rot; e.style.display = 'none'; return e; }
// 手写文字"写出来"：用从左到右的 clip
function inkTextAt(e, t, a, b, wDur = .6, rot) { const o = win(t, a, b, .05, .3); if (o <= .002) { e.style.display = 'none'; return; } e.style.display = ''; e.style.opacity = o; e.style.transform = `rotate(${rot ?? e._rot}deg)`; e.style.clipPath = `inset(-30% ${100 - 100 * EZ.out(pr(t, a, a + wDur))}% -30% -5%)`; }
function inkAt(p, t, a, b, d = .5) { const o = win(t, a, b, .02, .3); p.style.display = o <= .002 ? 'none' : ''; p.style.opacity = o; p.style.strokeDashoffset = p._L * (1 - EZ.out(pr(t, a, a + d))); }

const DARK=[[11.37,13.73],[23.43,25.57]];const darkK=t=>Math.max(...DARK.map(([a,b])=>Math.min(pr(t,a-.04,a+.06),1-pr(t,b-.12,b))),0);
const camE = mk('world', `<div class="o cam" style="width:460px;height:818px"><img><div class="lab"><b>●</b> on air · 阿杜Next</div></div>`); const camI = camE.querySelector('img'); imgs.push(camI);
// 形态关键帧 [t, x, y, z, ry, w, h, radius, opacity]
const RCARD = [560, -20, 0, -16, 460, 818, 26, 1], LCARD = [-560, -20, 0, 16, 460, 818, 26, 1], SMALL = [690, -270, 40, -10, 300, 300, 150, 1], CENTER = [-20, -40, 60, 0, 420, 420, 210, 1], HIDE = [560, -20, -900, -40, 460, 818, 26, 0], MID = [0, -20, 40, 0, 460, 818, 26, 1];
const CK = [[0, ...RCARD], [11.2, ...RCARD], [11.45, ...HIDE], [13.7, ...HIDE], [14.1, ...RCARD], [23.2, ...RCARD], [23.45, ...HIDE], [25.55, ...HIDE], [25.95, ...LCARD],
  [32.9, ...LCARD], [33.5, ...RCARD], [45.3, ...RCARD], [45.9, ...SMALL], [56.9, ...SMALL], [57.25, ...HIDE], [58.85, ...HIDE], [59.3, ...CENTER], [66.0, ...CENTER], [66.25, ...HIDE], [67.45, ...HIDE],
  [67.9, ...RCARD], [92.0, ...RCARD], [92.6, ...LCARD], [102.2, ...LCARD], [102.45, ...HIDE], [103.7, ...HIDE], [104.1, ...MID], [109.3, ...MID], [109.9, ...SMALL], [117.3, ...SMALL], [117.9, ...RCARD],
  [135.6, ...RCARD], [TALK_END, ...RCARD], [TALK_END + .5, ...HIDE], [END, ...HIDE]];
function camPose(t) { let i = 0; while (i + 1 < CK.length && t >= CK[i + 1][0]) i++; const a = CK[i], b = CK[Math.min(i + 1, CK.length - 1)], k = b[0] > a[0] ? EZ.io(pr(t, a[0], b[0])) : 1; return a.map((v, j) => lerp(v, b[j], k)).slice(1); }
function drawCam(t) {
  const [x, y, z, ry, w, h, r, o] = camPose(t), oo = o * (1 - darkK(t) * .999);
  camE.style.width = w + 'px'; camE.style.height = h + 'px'; camE.style.borderRadius = r + 'px';
  P3(camE, x, y + Math.sin(t * 1.2) * 6, z, ry + Math.sin(t * .5) * 1.5, 2, 1, oo);
  if (oo <= .002) return;
  setSrc(camI, talkSrc(window.MACRO_OUTPUT_T ?? t));
  // 竖屏原片 720x1280：按卡片宽高 cover；方/圆卡按人脸居中放大
  const f = faceAt(window.MACRO_OUTPUT_T ?? t), sq = Math.min(1, Math.abs(w - h) < 20 ? 1 : 0), sc0 = Math.max(w / 720, h / 1280), zoom = lerp(1, (h * .42) / (f.h * 1280 * sc0), sq);
  const s = sc0 * Math.max(1, zoom), iw = 720 * s, ih = 1280 * s;
  const ox = clamp(w / 2 - f.cx * iw, w - iw, 0), oy = clamp(h * (sq ? .5 : .42) - f.cy * ih, h - ih, 0);
  camI.style.width = iw + 'px'; camI.style.height = ih + 'px'; camI.style.left = ox + 'px'; camI.style.top = oy + 'px';
  camE.querySelector('.lab').style.display = w > 400 ? '' : 'none';
}

const ball = mk('ov', `<div class="ov" style="width:44px;height:44px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#8ff0dc,${TE} 55%,#159c84);box-shadow:0 0 30px rgba(47,211,180,.6);z-index:7"></div>`);
const trail = []; for (let i = 0; i < 10; i++) trail.push(mk('ov', `<div class="ov" style="width:44px;height:44px;border-radius:50%;border:2px solid rgba(47,211,180,.45);z-index:6"></div>`));
// 小球关键路径：[t, x, y, scale]（屏幕坐标中心）
const BK = [[0, 300, -80, 1], [.45, 300, 470, 1], [.62, 300, 380, 1], [.78, 300, 470, 1], [.95, 300, 430, 1], [1.1, 300, 470, 1], [1.6, 300, 470, 0],
  [11.37, 160, 600, 0], [11.5, 160, 600, 1], [12.9, 1700, 600, 1], [13.3, 1780, 600, 0],
  [23.43, 330, 560, 0], [23.6, 330, 560, 1], [24.2, 960, 560, 1], [24.9, 1590, 560, 1], [25.3, 1590, 560, 0],
  [102.4, 960, -60, 0], [102.5, 960, -60, 1], [102.95, 960, 470, 1], [103.15, 960, 400, 1], [103.35, 960, 470, 1], [103.7, 960, 470, 0],
  [136.3, 1700, -80, 0], [136.4, 1700, -80, 1], [136.9, 1700, 300, 1], [137.05, 1700, 250, 1], [137.2, 1700, 300, 1], [137.6, 1700, 300, 0]];
function ballAt(t) { let i = 0; while (i + 1 < BK.length && t >= BK[i + 1][0]) i++; const a = BK[i], b = BK[Math.min(i + 1, BK.length - 1)]; const k = b[0] > a[0] ? pr(t, a[0], b[0]) : 1; const fall = b[2] > a[2]; const ky = fall ? EZ.in(k) : EZ.out(k); return [lerp(a[1], b[1], k), lerp(a[2], b[2], ky), lerp(a[3], b[3], k), b[2] - a[2]]; }
function drawBall(t) {
  const [x, y, s, dy] = ballAt(t); const sq = Math.abs(dy) > 40 ? clamp(Math.abs(dy) / 900, 0, .35) : 0;
  V2(ball, s > .01 ? 1 : 0, x - 22, y - 22, 1); ball.style.transform += ` scale(${s * (1 - sq * .5)},${s * (1 + sq)})`;
  trail.forEach((e, i) => { const [tx, ty, ts] = ballAt(t - (i + 1) * .045); V2(e, ts > .01 && s > .01 ? (.45 - i * .04) : 0, tx - 22, ty - 22, ts * .9); });
}

const bQ = mk('ov', `<div class="ov" style="left:120px;top:200px"><div class="mono" style="font-size:20px;color:${GY};letter-spacing:3px">Q · 很多人问</div><div class="zh" style="font-size:78px;margin-top:12px;line-height:1.2">一边<span style="color:${RD}">吐槽</span> OpenAI<br>一边<span style="color:${TE}">还在用</span>？</div></div>`);
const scale = mk('ov', `<div class="ov" style="left:150px;top:560px;width:640px;height:260px"><div style="position:absolute;left:316px;top:40px;width:8px;height:200px;background:${INK};border-radius:4px"></div><div style="position:absolute;left:240px;top:232px;width:160px;height:16px;background:${INK};border-radius:8px"></div>
  <div class="beam" style="position:absolute;left:20px;top:34px;width:600px;height:10px;border-radius:5px;background:${INK};transform-origin:50% 50%"><div class="pl" style="position:absolute;left:-30px;top:10px;width:120px;text-align:center"><div style="height:2px;background:${INK};margin:0 30px"></div><div class="cardp zh" style="padding:10px 0;font-size:30px;color:${RD}">吐槽</div></div>
  <div class="pr" style="position:absolute;right:-30px;top:10px;width:120px;text-align:center"><div style="height:2px;background:${INK};margin:0 30px"></div><div class="cardp zh" style="padding:10px 0;font-size:30px;color:${TE}">在用</div></div></div></div>`);
const bTool = mk('ov', `<div class="ov" style="left:120px;top:250px"><div class="anton" style="font-size:150px">PRODUCTIVITY</div><div class="zh" style="font-size:64px;margin-top:6px">它是<span style="color:${TE}">生产力工具</span></div></div>`);
const bMirror = mk('world', `<div class="o"><img src="assets/mirror_cut.png" style="height:560px;display:block;filter:drop-shadow(0 24px 30px rgba(0,0,0,.14))"></div>`); imgs.push(bMirror.querySelector('img')); bMirror.style.display = 'none';
const bN = inkText('学它 → 复刻它', 160, 780, 72, RD, -3);
// ======================= G2 · 留白 2 23.43–25.57 =======================
const g2 = mk('ov', `<div class="ov" style="left:0;right:0;top:420px;display:flex;justify-content:center;gap:60px">${['用它', '学它', '复刻它'].map((s, i) => `<div class="g2c" style="width:360px;height:200px;border-radius:20px;border:3px solid rgba(255,255,255,.18);display:flex;flex-direction:column;align-items:center;justify-content:center"><div class="anton" style="font-size:40px;color:rgba(255,255,255,.45)">0${i + 1}</div><div class="zh" style="font-size:72px;color:${PAP}">${s}</div></div>`).join('')}</div>`);
const g2h = mk('ov', `<div class="ov" style="left:0;right:0;top:250px;text-align:center"><div class="anton" style="font-size:72px;color:${TE}">USE · LEARN · REPLICATE</div></div>`);
sc.update=t=>{
 const dk=darkK(t);$('dark').style.opacity=dk;
 $('world').style.transform=`rotateY(${Math.sin(t*.23)*1.5}deg)`;
 $('ov').style.transform='translate(0px,0px)';
 $('flash').style.opacity=Math.max(...DARK.map(([a,b])=>t>b-.05?.5*(1-pr(t,b-.05,b+.25)):0));
 drawCam(t);drawBall(t);
  // ---------- B ----------
  V2(bQ, win(t, 13.8, 17.6), (1 - EZ.out(pr(t, 13.8, 14.2))) * -40);
  V2(scale, win(t, 14.5, 17.6)); const tilt = -8 * EZ.out(pr(t, 15.4, 16.0)) + 8 * EZ.out(pr(t, 16.9, 17.5)) + Math.sin(t * 3) * 1.5 * (t > 16 ? 1 : 0);
  scale.querySelector('.beam').style.transform = `rotate(${tilt}deg)`; scale.querySelector('.pl').style.transform = `rotate(${-tilt}deg)`; scale.querySelector('.pr').style.transform = `rotate(${-tilt}deg)`;
  V2(bTool, win(t, 17.7, 20.6), (1 - EZ.out(pr(t, 17.7, 18.1))) * -60, 0, lerp(1.15, 1, EZ.out(pr(t, 19.7, 20.1))));
  P3(bMirror, -470, -60, 0, 8, 0, 1, win(t, 20.6, 23.4) * EZ.out(pr(t, 20.6, 21.0))); inkTextAt(bN, t, 21.3, 23.4, .7);
  // ---------- G2 ----------
  V2(g2, win(t, 23.45, 25.55, .05, .2)); V2(g2h, win(t, 23.5, 25.55, .15, .2));
  g2.querySelectorAll('.g2c').forEach((e, i) => { const a = 23.6 + i * .5, k = pr(t, a, a + .2); e.style.borderColor = k > .5 ? TE : 'rgba(255,255,255,.18)'; e.style.background = k > .5 ? 'rgba(47,211,180,.14)' : 'transparent'; e.style.transform = `translateY(${-14 * Math.sin(k * Math.PI)}px)`; });
};
// Complete source action cues, including the recap's three confirmations.
[[13.7,'whoosh',.6],[13.8,'swoosh',.4],[14.5,'pop',.4],[15.4,'creak',.4,0,{d:.6}],[16.9,'creak',.4,0,{d:.6}],[17.7,'hit',.7],[20.6,'pop',.5],[21.3,'write',.5,0,{d:.7}],[23.45,'hit',.9],[23.6,'check',.6,0,{n:0}],[24.1,'check',.6,0,{n:1}],[24.6,'check',.6,0,{n:2}]].forEach(a=>S(a[0],a[1],a[2],a[3]||0,a[4]||{}));
})();

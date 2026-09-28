/* ============================================================
   AI 时代，为什么一定要换 Mac   —  82s  —  voice: 9月26日.mp3
   Design: white / blue / black system; real talking-head "on air" card
   travels between layouts; cartoon Adu & parrot appear only as accents.
   ============================================================ */
window.END = 81.9;

/* shared: persistent on-air cam card lives in every scene (own instance) */
function camCard(parent, w, h, label = '// on air · 阿杜') {
  const e = mk(parent, `<div class="cam" style="width:${w}px;height:${h}px"><img><div class="lab"><span style="color:#6d9bff">●</span> ${label}</div></div>`, 0, 0, { ax: .5, ay: .5 });
  e._img = e.querySelector('img'); return e;
}
function camAt(e, t, o) { setFrame(e._img, talkSrc(t)); place(e, o); }

/* ---------- S1  0 – 3.3  HOOK : 为什么一定要把电脑换成 Mac ---------- */
(() => {
  const sc = new Scene(0, 3.3, 'var(--paper)', { grid: 'grid' });
  const T = tags(sc, '// 01 — 开场');
  const cam = camCard(sc.el, 540, 960);
  const k = mk(sc.el, `<div class="tag" style="font-size:26px">// AI 时代</div>`, 146, 300);
  const l1 = words(sc.el, [{ h: '为什么', t: .6 }, { h: '一定要', t: .95 }], 146, 350, 'h1');
  const l2 = words(sc.el, [{ h: '把电脑换成&nbsp;', t: 1.95 }, { h: '<span class="acc" style="font-size:190px;font-weight:700;letter-spacing:-6px">Mac</span>', t: 2.35, k: 'slam', d: .5 }], 146, 480, 'h1', { style: 'display:flex;align-items:baseline' });
  const mac = img(sc.el, 'x_macbook.png', 1100, 930, 250);
  sc.update = t => {
    T(t);
    // cam slides in from right with spring, sits right
    const c = EZ.spring(pr(t, 0, .8));
    camAt(cam, t, { x: 1490 + (1 - c) * 700, y: 540, r: (1 - c) * 6, o: 1 });
    show(k, t, .45); wordsAt(l1, t); wordsAt(l2, t);
    const m = pr(t, 2.35, 2.9); place(mac, { o: clamp(m * 3), s: .6 + .4 * EZ.spring(m), y: 1000 + bob(t, 0, 5), x: 900, r: -6 + 6 * EZ.spring(m) });
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1.02 - .02 * EZ.out(pr(t, 0, 3.3)) });
  S(0, 'swoosh', .6, .6); S(.45, 'tick', .35); S(.6, 'tick', .35); S(.95, 'tick', .35); S(1.95, 'tick', .35); S(2.35, 'hit', 1); S(2.4, 'shine', .5); S(2.75, 'pop', .6);
})();

/* ---------- S2  3.3 – 11.9  老用户 · Win95 · 学习网站 · 杀毒重装 ---------- */
(() => {
  const sc = new Scene(3.3, 11.9, '#0A0A0A', { grid: 'gridD', trans: 'wipe', td: .45, tc: '#0A0A0A' });
  const T = tags(sc, '// 02 — 我的 Windows 年代', '', true);
  const cam = camCard(sc.el, 360, 640);
  const y1 = mk(sc.el, `<div style="color:#fff"><div class="mono" style="font-size:26px;color:#777">// Windows 老用户 · 从</div><div style="font-size:250px;font-weight:600;letter-spacing:-10px;line-height:1">19<span class="yy">95</span></div></div>`, 146, 230);
  const yy = y1.querySelector('.yy');
  // CRT with Win95 desktop, pop-ups swarm
  const crt = img(sc.el, 'x_crt.png', 1180, 1000, 640, { ic: 'chD' });
  const pops = [['恭喜中奖！', '点击领取 iPhone'], ['警告', '发现 23 个病毒'], ['系统提示', '电脑运行缓慢'], ['免费下载', '高速下载器'], ['错误', 'explorer.exe 已停止'], ['安全中心', '立即修复！'], ['屠龙宝刀', '点击就送']];
  const pe = pops.map((p, i) => mk(sc.el, `<div class="win95" style="width:330px"><div class="tb"><span>${p[0]}</span><span class="bt"><span>_</span><span>□</span><span>×</span></span></div><div style="padding:12px 14px;font-size:22px">⚠ ${p[1]}<div style="text-align:center;margin-top:8px"><span class="b95">确定</span></div></div></div>`, 0, 0, { ax: .5, ay: .5 }));
  const PP = [[980, 330], [1400, 290], [1040, 520], [1500, 520], [1200, 420], [960, 700], [1450, 740]];
  const lb = mk(sc.el, `<div class="pill" style="background:#E5484D;color:#fff;font-size:30px">十几岁 · 不小心点开了「学习网站」</div>`, 146, 560);
  const skills = mk(sc.el, `<div style="color:#fff"><div class="mono" style="font-size:26px;color:#777">// 被迫学会的技能</div>
     <div style="display:flex;gap:18px;margin-top:16px"><div class="dcard" style="width:300px;height:170px"><div class="lb">// skill 01</div><div style="position:absolute;left:24px;bottom:22px;font-size:52px;font-weight:600">杀毒</div></div>
     <div class="dcard" style="width:300px;height:170px"><div class="lb">// skill 02</div><div style="position:absolute;left:24px;bottom:22px;font-size:52px;font-weight:600">重装系统</div></div></div>
     <div style="margin-top:22px;width:618px;height:14px;border-radius:7px;background:#222;overflow:hidden"><div class="rb" style="height:100%;width:0;background:repeating-linear-gradient(90deg,#1084d0 0 18px,#000080 18px 22px)"></div></div>
     <div class="mono rt" style="font-size:22px;color:#777;margin-top:8px">正在重装系统… 0%</div></div>`, 146, 600);
  const rb = skills.querySelector('.rb'), rt = skills.querySelector('.rt');
  const stress = img(sc.el, 'p_crt_stress.png', 1520, 1110, 700, { ic: 'chD' });
  sc.update = t => {
    T(t);
    camAt(cam, t, { x: 1690, y: 400, o: 1 - pr(t, 10.0, 10.3), s: .9 + .1 * EZ.spring(pr(t, 3.3, 3.9)) });
    show(y1, t, 3.45, { k: 'up', out: 6.2 });
    yy.textContent = String(Math.round(counter(t, 3.6, 4.7, 26, 95))).padStart(2, '0');
    show(crt, t, 5.9, { k: 'pop', y: 1000, out: 10.0 });
    show(lb, t, 6.4, { k: 'left', out: 9.8 });
    pe.forEach((e, i) => { const t0 = 7.1 + i * .17; show(e, t, t0, { k: 'pop', d: .3, x: PP[i][0] + shake(t, t0, .25, 8)[0], y: PP[i][1], out: 9.8, od: .25 }); });
    show(skills, t, 10.05, { k: 'up' });
    const p = pr(t, 10.5, 11.8); rb.style.width = (p * 100) + '%'; rt.textContent = '正在重装系统… ' + Math.floor(p * 87) + '%';
    const st = hopIn(t, 10.1); place(stress, { o: st.o, s: st.s, x: 1500, y: 1110 + st.y });
  };
  sc.cam = t => { const s = shake(t, 7.1, 1.3, 7); return { x: 960, y: 540, z: 1 + .03 * pr(t, 3.3, 11.9), sx: s[0], sy: s[1] }; };
  S(3.25, 'swoosh', .7); S(3.6, 'counter', .5, -.4, { d: 1.1 }); S(4.7, 'thud', .6); S(5.9, 'crt', .9, .3); S(6.4, 'swoosh', .5, -.5);
  pops.forEach((p, i) => S(7.1 + i * .17, 'err', .8, (i % 3 - 1) * .5)); S(9.8, 'whoosh', .5); S(10.05, 'card', .6); S(10.1, 'pop', .6, .5); S(10.5, 'hdd', .6, 0, { d: 1.3 });
})();

/* ---------- S3  11.9 – 20.67  00/90/80后 · C盘已满 · 文件崩溃 · 重装 · 浪费时间 ---------- */
(() => {
  const sc = new Scene(11.9, 20.67, 'var(--paper)', { grid: 'grid', trans: 'wipe', td: .45, tc: '#F7F7F5' });
  const T = tags(sc, '// 03 — 共同记忆');
  const cam = camCard(sc.el, 420, 746);
  const g = words(sc.el, [{ h: '00 后，', t: 12.05 }, { h: '90 后，', t: 12.45 }, { h: '80 后，', t: 12.85 }], 146, 170, 'h1');
  const g2 = words(sc.el, [{ h: '<span style="color:var(--g1)">很多人都感受过——</span>', t: 14.27 }], 146, 300, 'h2');
  // three pain cards as big UI
  const disk = mk(sc.el, `<div class="card" style="width:560px;height:250px"><div class="lb">// 本地磁盘 (C:)</div><div class="ix">01</div>
     <div style="position:absolute;left:26px;right:26px;top:80px;height:34px;border-radius:17px;background:#EEE;overflow:hidden"><div class="f" style="height:100%;width:0;background:#E5484D"></div></div>
     <div class="n" style="position:absolute;left:26px;bottom:28px;font-size:60px;font-weight:600;letter-spacing:-2px">0%</div><div style="position:absolute;right:26px;bottom:38px;font-size:30px;font-weight:600;color:#E5484D">C 盘已满</div></div>`, 146, 430);
  const df = disk.querySelector('.f'), dn = disk.querySelector('.n');
  const crash = mk(sc.el, `<div class="card" style="width:560px;height:250px"><div class="lb">// 毕业论文_final_最终版.doc</div><div class="ix">02</div>
     <div style="position:absolute;left:26px;top:80px;font-size:56px;font-weight:600">文件崩溃</div><div class="mono" style="position:absolute;left:26px;bottom:30px;font-size:24px;color:#E5484D">（未响应）</div></div>`, 740, 430);
  const re = mk(sc.el, `<div class="card" style="width:560px;height:250px;background:#0A0A0A;border:none;color:#fff"><div class="lb" style="color:#777">// 重装系统</div><div class="ix">03</div>
     <div style="position:absolute;left:26px;bottom:26px;font-size:130px;font-weight:600;letter-spacing:-4px;line-height:1"><span class="n">1</span><span style="font-size:40px;color:#777">&nbsp;次</span></div></div>`, 1334, 430);
  const rn = re.querySelector('.n');
  const waste = mk(sc.el, `<div style="display:flex;align-items:baseline;gap:22px"><div class="mono" style="font-size:26px;color:var(--g1)">// 浪费掉的时间</div><div class="n" style="font-size:170px;font-weight:600;letter-spacing:-6px;color:#E5484D">0</div><div style="font-size:60px;font-weight:600">小时+</div></div>`, 146, 740);
  const wn = waste.querySelector('.n');
  sc.update = t => {
    T(t);
    camAt(cam, t, { x: 1600, y: 540, o: 1 - pr(t, 15.6, 15.9), s: 1 - .1 * EZ.in(pr(t, 15.6, 15.9)) });
    wordsAt(g, t, { out: 15.6 }); wordsAt(g2, t, { out: 15.6 });
    show(disk, t, 15.9, { k: 'up', y: 430 - 130 * EZ.inout(pr(t, 15.9, 16.3)) });
    const d = EZ.out(pr(t, 16.0, 16.8)); df.style.width = (d * 99.6) + '%'; dn.textContent = (d * 99.6).toFixed(1) + '%';
    const sh = shake(t, 16.97, .5, 16); show(crash, t, 16.97, { k: 'up', x: 740 + sh[0], y: 300 });
    show(re, t, 17.87, { k: 'up', y: 300 });
    rn.textContent = 1 + Math.floor(clamp((t - 18.0) * 8, 0, 11));
    show(waste, t, 18.77, { k: 'up' });
    wn.textContent = fmt(counter(t, 18.9, 20.3, 0, 1000));
  };
  sc.cam = t => { const s = shake(t, 16.97, .4, 8); return { x: 960, y: 540, z: 1, sx: s[0], sy: s[1] }; };
  [12.05, 12.45, 12.85].forEach((tt, i) => S(tt, 'tick', .45, -.3 + i * .3)); S(14.27, 'swipe', .4); S(15.9, 'card', .6, -.6); S(16.0, 'fill_up', .5, -.6, { d: .8 });
  S(16.97, 'crash', 1); S(17.87, 'card', .6, .6); S(18.0, 'counter', .5, .6, { d: 1.4 }); S(18.77, 'thud', .7); S(18.9, 'counter', .45, -.4, { d: 1.4 });
})();

/* ---------- S4  20.67 – 28.37  换成 Mac · 用户系统完整保存 ---------- */
(() => {
  const sc = new Scene(20.67, 28.37, 'var(--paper)', { grid: 'grid', trans: 'flash', td: .35, fa: 1 });
  const T = tags(sc, '// 04 — 换成 Mac');
  const hello = mk(sc.el, `<div style="font-family:'Snell Roundhand','Apple Chancery',cursive;font-size:280px;color:var(--ink);line-height:1">hello</div>`, 960, 460, { ax: .5, ay: .5 });
  const ten = mk(sc.el, `<div style="text-align:center"><div class="mono" style="font-size:26px;color:var(--g1)">// 十几年前 · 我换成了 Mac</div></div>`, 960, 700, { ax: .5, ay: .5 });
  const cam = camCard(sc.el, 400, 711);
  // migration timeline: 4 Macs, one account card travels through
  const yrs = [['2013', 'MacBook Air'], ['2017', 'MacBook Pro'], ['2021', 'M1 Pro'], ['2025', 'M4 Max']];
  const ms = yrs.map((y, i) => mk(sc.el, `<div style="text-align:center;width:280px"><img src="assets/x_macbook.png" style="width:240px;filter:drop-shadow(0 16px 20px rgba(0,0,0,.14))"><div style="font-size:44px;font-weight:600;letter-spacing:-1px;margin-top:6px">${y[0]}</div><div class="mono" style="font-size:20px;color:var(--g1)">${y[1]}</div></div>`, 190 + i * 310, 610, { ax: .5, ay: .5 }));
  const line = mk(sc.el, `<div style="width:930px;height:4px;background:var(--line);border-radius:2px"><div class="f" style="height:100%;width:0;background:var(--blue);border-radius:2px"></div></div>`, 190, 640, { ay: .5 });
  const lf = line.querySelector('.f');
  const acct = mk(sc.el, `<div class="card" style="width:240px;padding:18px 20px;border:2px solid var(--blue);box-shadow:0 16px 36px rgba(36,98,234,.25)"><div class="mono" style="font-size:17px;color:var(--g1)">// 我的用户系统</div><div style="font-size:30px;font-weight:600;margin-top:4px">阿杜 · 2013 →</div><div class="mono" style="font-size:17px;color:var(--blue);margin-top:4px">照片 · 设置 · 软件</div></div>`, 0, 0, { ax: .5, ay: .5 });
  const t1 = words(sc.el, [{ h: '十几年前的用户系统，', t: 23.8 }], 146, 150, 'h2');
  const t2 = words(sc.el, [{ h: '至今', t: 25.5 }, { h: '<span class="acc">完整保存。</span>', t: 25.8 }], 146, 260, 'h1');
  const mig = mk(sc.el, `<div class="pill" style="background:#0A0A0A;color:#fff;font-size:26px">迁移助理 · 一键搬到新 Mac</div>`, 146, 930);
  const bird = img(sc.el, 'b_fly.png', 0, 0, 150);
  sc.update = t => {
    T(t);
    const h = pr(t, 20.8, 22.2);
    place(hello, { o: clamp(h * 4) * (1 - pr(t, 23.4, 23.7)), s: .96 + .04 * EZ.out(h), blur: (1 - EZ.out(h)) * 12 * 0 });
    hello.firstChild.style.clipPath = `inset(0 ${(100 - h * 100).toFixed(1)}% 0 0)`;
    show(ten, t, 21.4, { k: 'up', out: 23.4 });
    wordsAt(t1, t); wordsAt(t2, t);
    const L = EZ.inout(pr(t, 24.3, 27.3)); lf.style.width = (L * 100) + '%'; place(line, { o: pr(t, 24.0, 24.3) });
    ms.forEach((m, i) => show(m, t, 24.0 + i * .18, { k: 'up' }));
    // account card hops above each Mac as the line reaches it
    const seg = L * 3, i0 = Math.min(2, Math.floor(seg)), f = seg - i0;
    const ax = 190 + (i0 + EZ.inout(clamp(f))) * 310, ay = 540 - Math.sin(clamp(f) * Math.PI) * 60;
    place(acct, { o: pr(t, 24.3, 24.6), x: t < 24.3 ? 190 : ax, y: t < 24.3 ? 540 : ay });
    show(mig, t, 26.6, { k: 'up' });
    camAt(cam, t, { x: 1620, y: 560, o: pr(t, 23.6, 23.9), s: .9 + .1 * EZ.spring(pr(t, 23.6, 24.2)) });
    // parrot flies across as the account migrates
    const bf = pr(t, 24.5, 27.4); place(bird, { o: bf > 0 && bf < 1 ? 1 : 0, x: 100 + bf * 1100, y: 900 - Math.sin(bf * Math.PI * 3) * 20, sx: -1 });
  };
  sc.cam = t => ({ x: 960, y: 540, z: t < 23.6 ? 1.06 - .06 * EZ.out(pr(t, 20.67, 23.6)) : 1 });
  S(20.66, 'chime', 1); S(20.8, 'write', .5, 0, { d: 1.4 }); S(21.4, 'tick', .3); S(23.6, 'swoosh', .6, .6); S(23.8, 'tick', .4); S(25.5, 'tick', .4); S(25.8, 'ding', .6);
  [24.0, 24.18, 24.36, 24.54].forEach((tt, i) => S(tt, 'pop', .5, -.6 + i * .3)); S(24.3, 'slide', .5, 0, { d: 3 }); S(24.5, 'flap', .7, -.6); S(26.6, 'pop', .5);
})();

/* ---------- S5  28.37 – 36.8  专注 · 大佬清一色 Mac · 专业软件 · 注意力 ---------- */
(() => {
  const sc = new Scene(28.37, 36.8, 'var(--paper)', { grid: 'grid', trans: 'wipe', td: .45, tc: '#2462EA' });
  const T = tags(sc, '// 05 — 专注');
  const cam = camCard(sc.el, 440, 782);
  const nts = [['🔔', '#FF9F0A', '有 12 条新通知'], ['🔄', '#0A84FF', '需要重启以安装更新'], ['🧹', '#30D158', '磁盘空间不足'], ['📢', '#FF375F', '弹窗广告'], ['⚙️', '#8E8E93', '驱动程序已过期'], ['🛡️', '#5E5CE6', '安全软件拦截']];
  const ne = nts.map(n => mk(sc.el, `<div class="notif glass"><div class="ic" style="background:${n[1]}">${n[0]}</div>${n[2]}</div>`, 0, 0, { ax: .5, ay: .5 }));
  const f1 = words(sc.el, [{ h: 'Mac 最大的优点：', t: 28.45 }], 146, 200, 'h2', { style: 'color:var(--g1)' });
  const f2 = words(sc.el, [{ h: '让你', t: 29.5 }, { h: '<span class="acc">专注</span>', t: 29.8, k: 'pop' }, { h: '工作。', t: 30.2 }], 146, 310, 'h1');
  const focus = mk(sc.el, `<div class="pill" style="background:#0A0A0A;color:#fff;font-size:28px">🌙 专注模式 · 已开启</div>`, 150, 500);
  // big shots
  const who = ['科技博主', '程序员', '设计师', '创业者', '投资人', '剪辑师'];
  const we = who.map((w, i) => mk(sc.el, `<div class="card" style="width:250px;height:140px"><div class="lb">// ${String(i + 1).padStart(2, '0')}</div><div style="position:absolute;left:22px;bottom:18px;font-size:38px;font-weight:600">${w}</div><div style="position:absolute;right:20px;bottom:22px;width:56px;height:36px;border-radius:6px 6px 2px 2px;background:#d8dade;border:3px solid #c7c9ce"></div></div>`, 146 + (i % 3) * 270, 470 + Math.floor(i / 3) * 160));
  const bs = words(sc.el, [{ h: '博主大牛、商业大佬，', t: 31.27 }], 146, 200, 'h2');
  const bs2 = words(sc.el, [{ h: '清一色&nbsp;', t: 34.2 * 0 + 32.55 }, { h: '<span class="acc">Mac。</span>', t: 32.9, k: 'pop' }], 146, 310, 'h1');
  // pro apps dock
  const apps = [['Final Cut Pro', '#1c1c1e,#3a3a3c', '🎬'], ['Logic Pro', '#2b2b2b,#4a4a4a', '🎹'], ['Xcode', '#0a84ff,#5ac8fa', '🛠️'], ['Motion', '#6e3cff,#b388ff', '✨'], ['Keynote', '#0a6cff,#2ac3ff', '📊']];
  const dock = mk(sc.el, `<div class="glass" style="display:flex;gap:22px;padding:22px 26px;border-radius:44px">${apps.map(a => `<div class="ap" style="text-align:center;width:150px"><div class="appic" style="margin:0 auto;background:linear-gradient(135deg,${a[1]})"><span style="font-size:70px">${a[2]}</span></div><div style="font-size:20px;font-weight:600;margin-top:10px">${a[0]}</div></div>`).join('')}</div>`, 146, 850, { ay: .5 });
  const apE = [...dock.querySelectorAll('.ap')];
  const dockT = mk(sc.el, `<div class="mono" style="font-size:24px;color:var(--g1)">// 专业软件生态 · 很多只在 Mac 上</div>`, 150, 720);
  const blue = mk(sc.el, `<div style="width:1920px;height:1080px;background:var(--blue)"></div>`, 0, 0);
  // attention
  const at1 = words(sc.el, [{ h: '他们最清楚：', t: 34.97 }], 960, 330, 'h2', { ax: .5, style: 'color:#fff' });
  const at2 = words(sc.el, [{ h: '最贵的是', t: 35.95 }], 960, 450, 'h2', { ax: .5, style: 'color:rgba(255,255,255,.7)' });
  const at3 = mk(sc.el, `<div style="font-size:300px;font-weight:700;letter-spacing:-12px;color:#fff;line-height:1">注意力</div>`, 960, 700, { ax: .5, ay: .5 });
  sc.update = t => {
    T(t);
    // cam at right; notifications orbit it then dissolve when 专注 pops
    const cx = 1500, cy = 540;
    camAt(cam, t, { x: cx, y: cy, o: 1 - pr(t, 34.7, 34.95), s: 1 });
    ne.forEach((n, i) => {
      const a0 = pr(t, 28.5 + i * .12, 28.9 + i * .12), gone = pr(t, 29.8 + i * .05, 30.25 + i * .05);
      const ang = -Math.PI / 2 + i * Math.PI / 3 + t * .25;
      const R = 430 * (1 + .6 * EZ.in(gone));
      place(n, { x: cx + Math.cos(ang) * R * .95, y: cy + Math.sin(ang) * R * .8, o: EZ.out(a0) * (1 - gone), s: (.8 + .2 * EZ.spring(a0)) * (1 - .2 * gone), blur: gone * 14 });
    });
    wordsAt(f1, t, { out: 31.1 }); wordsAt(f2, t, { out: 31.1 }); show(focus, t, 30.3, { k: 'pop', out: 31.1 });
    wordsAt(bs, t, { out: 34.7 }); wordsAt(bs2, t, { out: 34.7 });
    we.forEach((w, i) => show(w, t, 31.4 + i * .1, { k: 'up', out: 32.25 + 0 * i, od: .25 }));
    show(dock, t, 32.3, { k: 'up', out: 34.7 }); show(dockT, t, 32.4, { k: 'up', out: 34.7 });
    apE.forEach((e, i) => { const hv = Math.max(0, 1 - Math.abs(t - (32.9 + i * .3)) * 3.2); e.style.transform = `translateY(${-30 * hv}px) scale(${1 + .3 * hv})`; });
    // blue circle expands from cam position
    const b = EZ.inout(pr(t, 34.6, 35.2)); place(blue, { o: b > 0 ? 1 : 0, x: 0, y: 0 }); blue.firstChild.style.clipPath = `circle(${(b * 2000).toFixed(0)}px at ${cx}px ${cy}px)`;
    wordsAt(at1, t); wordsAt(at2, t); show(at3, t, 36.1, { k: 'slam', d: .4 });
  };
  sc.cam = t => ({ x: 960, y: 540, z: t > 35.9 ? 1 + .04 * EZ.out(pr(t, 36.1, 36.8)) : 1 });
  S(28.4, 'swoosh', .6); nts.forEach((n, i) => S(28.5 + i * .12, 'notif', .5, .5)); S(29.8, 'pop', .8); S(29.85, 'dissolve', .6, .5, { d: .5 }); S(30.3, 'pop', .5, -.5);
  S(31.27, 'swipe', .4); who.forEach((w, i) => S(31.4 + i * .1, 'tick', .35, -.5 + i * .2)); S(32.9, 'hit', .7); S(32.3, 'card', .5);
  apps.forEach((a, i) => S(32.9 + i * .3, 'dock', .5, -.6 + i * .3)); S(34.6, 'whoosh', .8, .5); S(34.97, 'tick', .4); S(35.95, 'tick', .4); S(36.1, 'hit', 1.1); S(36.15, 'shine', .5);
})();

/* ---------- S6  36.8 – 44.53  AI 指挥部 · 你一停 全队等你 ---------- */
(() => {
  const sc = new Scene(36.8, 44.53, '#0A0A0A', { grid: 'gridD', trans: 'circle', td: .5, tc: '#0A0A0A' });
  const T = tags(sc, '// 06 — 指挥部', '', true);
  const cam = camCard(sc.el, 300, 300, '// 你');
  cam.querySelector('img').style.objectPosition = '50% 28%';
  const CX = 960, CY = 600;
  const ag = [['写代码', '#5b8cff'], ['做设计', '#ff7eb3'], ['写文案', '#ffb347'], ['做调研', '#3fe0a8'], ['剪视频', '#2fc4ff'], ['跑数据', '#b388ff']];
  const AP = ag.map((a, i) => { const an = Math.PI + i * Math.PI / 5; return [CX + 640 * Math.cos(an), CY + 330 * Math.sin(an) * .95 + (i === 0 || i === 5 ? 0 : 0)]; });
  const svg = mk(sc.el, `<svg width="1920" height="1080">${AP.map((p, i) => `<path class="ln" d="M${CX} ${CY} Q ${(CX + p[0]) / 2} ${CY - 60} ${p[0]} ${p[1]}" stroke="${ag[i][1]}" stroke-width="3" fill="none" stroke-dasharray="8 12" stroke-linecap="round"/>`).join('')}</svg>`, 0, 0);
  const lines = [...svg.querySelectorAll('.ln')];
  const pk = ag.map((a, i) => mk(sc.el, `<div style="width:14px;height:14px;border-radius:50%;background:${a[1]};box-shadow:0 0 16px ${a[1]}"></div>`, 0, 0, { ax: .5, ay: .5 }));
  const ae = ag.map((a, i) => mk(sc.el, `<div class="dcard" style="width:250px;height:150px"><div class="lb">// agent ${String(i + 1).padStart(2, '0')}</div>
     <div style="position:absolute;left:22px;top:56px;font-size:36px;font-weight:600">${a[0]}</div>
     <div style="position:absolute;left:22px;right:22px;bottom:26px;height:6px;border-radius:3px;background:#262626"><div class="pb" style="height:100%;width:0;border-radius:3px;background:${a[1]}"></div></div>
     <div class="st mono" style="position:absolute;right:22px;top:20px;font-size:17px;color:#777"></div></div>`, AP[i][0], AP[i][1], { ax: .5, ay: .5 }));
  const t1 = words(sc.el, [{ h: 'AI 时代，更是这样。', t: 36.85 }], 146, 150, 'h2', { style: 'color:#fff' });
  const t2 = words(sc.el, [{ h: '你，指挥一群 AI 干活。', t: 37.85 }], 146, 150, 'h2', { style: 'color:#fff' });
  const t3 = words(sc.el, [{ h: '电脑，就是你的', t: 40.45 }, { h: '<span style="color:#6d9bff">指挥部。</span>', t: 41.1 }], 146, 150, 'h2', { style: 'color:#fff' });
  const stop = mk(sc.el, `<div style="text-align:center"><div style="font-size:150px;font-weight:700;letter-spacing:-5px;color:#fff">你一停，</div><div style="font-size:64px;font-weight:600;color:#E5484D">整支 AI 队伍都得停下来等你</div></div>`, 960, 560, { ax: .5, ay: .5 });
  const pause = mk(sc.el, `<div style="width:110px;height:110px;border-radius:50%;background:#E5484D;display:flex;align-items:center;justify-content:center;gap:14px"><div style="width:14px;height:44px;background:#fff;border-radius:3px"></div><div style="width:14px;height:44px;background:#fff;border-radius:3px"></div></div>`, CX, CY, { ax: .5, ay: .5 });
  const FZ = 42.2;
  sc.update = t => {
    T(t);
    const tf = Math.min(t, FZ), fr = pr(t, FZ, FZ + .3);
    camAt(cam, t, { x: CX, y: CY, s: (.4 + .6 * EZ.spring(pr(t, 37.9, 38.5))) * (1 + .03 * Math.sin(t * 3) * (1 - fr)), o: pr(t, 37.9, 38.1) * (1 - pr(t, 42.35, 42.5)) });
    cam.style.borderRadius = '50%'; cam.style.boxShadow = `0 0 0 6px #0A0A0A,0 0 0 9px rgba(109,155,255,${.8 * (1 - fr)}),0 0 60px rgba(109,155,255,${.5 * (1 - fr)})`;
    wordsAt(t1, t, { out: 37.7 }); wordsAt(t2, t, { out: 40.3 }); wordsAt(t3, t, { out: 42.1 });
    ae.forEach((e, i) => {
      const t0 = 38.3 + i * .16;
      show(e, t, t0, { k: 'pop', y: AP[i][1] + (fr < 1 ? 6 * Math.sin(tf * 2 + i) : 0), o: 1 - .55 * fr * (t < 42.35 ? 1 : 1) });
      e.style.filter = `grayscale(${fr})`;
      lines[i].style.opacity = pr(t, t0, t0 + .3) * (1 - .75 * fr); lines[i].setAttribute('stroke-dashoffset', (-tf * 60).toFixed(1));
      const p = clamp((tf - t0 - .3) * (.2 + .05 * i)); e.querySelector('.pb').style.width = (p * 100) + '%';
      e.querySelector('.st').textContent = fr > 0 ? '等待中' + '.'.repeat(1 + Math.floor(t * 3) % 3) : p >= 1 ? '✓ 完成' : Math.floor(p * 100) + '%';
      e.querySelector('.st').style.color = fr > 0 ? '#E5484D' : '#777';
      // packets flowing along paths
      const k = ((tf * .8 + i * .17) % 1), p0 = [CX, CY], c = [(CX + AP[i][0]) / 2, CY - 60], p1 = AP[i];
      const bx = (1 - k) ** 2 * p0[0] + 2 * (1 - k) * k * c[0] + k * k * p1[0], by = (1 - k) ** 2 * p0[1] + 2 * (1 - k) * k * c[1] + k * k * p1[1];
      place(pk[i], { x: bx, y: by, o: pr(t, t0 + .3, t0 + .5) * (1 - fr) });
    });
    show(stop, t, 42.35, { k: 'slam', d: .35 });
    place(pause, { o: fr * (1 - pr(t, 42.35, 42.5)), s: .5 + .5 * EZ.spring(fr) });
  };
  sc.cam = t => { const s = shake(t, FZ, .4, 12); return { x: 960, y: 540, z: t < 38.3 ? 1.1 - .1 * EZ.out(pr(t, 36.8, 38.3)) : 1 + .04 * pr(t, FZ, 44.5), sx: s[0], sy: s[1] }; };
  S(36.85, 'tick', .4); S(37.85, 'tick', .4); S(37.9, 'pop', .7); ag.forEach((a, i) => S(38.3 + i * .16, 'agent', .6, (AP[i][0] - 960) / 800)); S(38.8, 'hum', .5, 0, { d: 3.4 }); S(40.45, 'tick', .4); S(41.1, 'ding', .6);
  S(FZ, 'powerdown', 1); S(42.35, 'hit', .9);
})();

/* ---------- S7  44.53 – 55.67  ChatGPT 先上 Mac · 晚 5 个月 · 微软 · 一整轮机会 ---------- */
(() => {
  const sc = new Scene(44.53, 55.67, 'var(--paper)', { grid: 'grid', trans: 'wipe', td: .45, tc: '#F7F7F5' });
  const T = tags(sc, '// 07 — 先上 Mac');
  const t1 = words(sc.el, [{ h: '连 ChatGPT 电脑版，', t: 44.6 }], 146, 150, 'h2');
  const t2 = words(sc.el, [{ h: '都是', t: 45.4 }, { h: '<span class="acc">先上 Mac。</span>', t: 45.75, k: 'pop' }], 146, 260, 'h1');
  // release timeline
  const tl = mk(sc.el, `<div style="position:relative;width:1628px;height:300px">
     <div style="position:absolute;left:0;right:0;top:150px;height:4px;background:var(--line)"></div>
     ${['2024.05', '06', '07', '08', '09', '2024.10'].map((m, i) => `<div style="position:absolute;left:${i * 325.6}px;top:142px;width:2px;height:20px;background:#ccc"></div><div class="mono" style="position:absolute;left:${i * 325.6 - 40}px;top:176px;width:80px;text-align:center;font-size:20px;color:var(--g1)">${m}</div>`).join('')}
     <div class="gap" style="position:absolute;left:0;top:140px;height:24px;width:0;border-radius:12px;background:repeating-linear-gradient(45deg,#E5484D 0 12px,#ff8a8f 12px 24px)"></div>
     <div class="m1" style="position:absolute;left:-10px;top:40px"><div class="pill" style="background:#0A0A0A;color:#fff">Mac 版 · 首发</div></div>
     <div class="m2" style="position:absolute;right:-10px;top:40px"><div class="pill" style="background:#fff;border:1.5px solid var(--line)">Windows 版</div></div>
     <div class="lt" style="position:absolute;left:640px;top:220px;font-size:64px;font-weight:600;color:#E5484D;letter-spacing:-1px">晚了 5 个月</div></div>`, 146, 420);
  const gap = tl.querySelector('.gap'), m1 = tl.querySelector('.m1'), m2 = tl.querySelector('.m2'), lt = tl.querySelector('.lt');
  // twist: Microsoft
  const tw = mk(sc.el, `<div class="card" style="width:1628px;height:330px;background:#0A0A0A;border:none;color:#fff"><div class="lb" style="color:#777">// 反转</div>
     <div style="position:absolute;left:40px;top:80px;font-size:44px;color:#999">而 OpenAI 最大的投资人——</div>
     <div style="position:absolute;left:40px;top:150px;font-size:120px;font-weight:600;letter-spacing:-3px">就是 <span style="color:#6d9bff">微软</span><span style="font-size:44px;color:#777;letter-spacing:0">&nbsp;&nbsp;Windows 的亲爹 · 约 27%</span></div></div>`, 146, 380);
  const qm = mk(sc.el, `<div style="font-size:200px;font-weight:700;color:#E5484D">?!</div>`, 1640, 560, { ax: .5, ay: .5 });
  // opportunity race: two lanes
  const r0 = words(sc.el, [{ h: '别人第一天就用上新工具，', t: 52.03 }], 146, 150, 'h2');
  const r1 = words(sc.el, [{ h: '你还在', t: 53.3 }, { h: '<span style="color:#E5484D">等适配。</span>', t: 53.6 }], 146, 260, 'h1');
  const lane = (who, col) => `<div class="card" style="width:1628px;height:150px"><div class="lb">// ${who}</div><div style="position:absolute;left:180px;right:60px;top:74px;height:4px;background:var(--line)"></div><div class="dot" style="position:absolute;left:170px;top:58px;width:36px;height:36px;border-radius:50%;background:${col}"></div><div class="tx" style="position:absolute;right:30px;top:20px;font-size:26px;font-weight:600;color:${col}"></div></div>`;
  const la = mk(sc.el, lane('别人 · Mac', '#2462EA'), 146, 470), lb = mk(sc.el, lane('你 · Windows', '#E5484D'), 146, 650);
  const r3 = words(sc.el, [{ h: '差的是', t: 54.27 }, { h: '<span class="hl">一整轮机会。</span>', t: 54.6, k: 'pop' }], 146, 860, 'h2');
  const cam = camCard(sc.el, 330, 587);
  sc.update = t => {
    T(t);
    wordsAt(t1, t, { out: 48.5 }); wordsAt(t2, t, { out: 48.5 });
    show(tl, t, 45.3, { k: 'up', out: 48.5 });
    m1.style.transform = `scale(${.4 + .6 * EZ.spring(pr(t, 45.8, 46.4))})`; m1.style.opacity = pr(t, 45.8, 45.9);
    gap.style.width = (EZ.inout(pr(t, 46.9, 48.3)) * 1628) + 'px';
    m2.style.transform = `scale(${.4 + .6 * EZ.spring(pr(t, 48.1, 48.6))})`; m2.style.opacity = pr(t, 48.1, 48.2);
    lt.style.opacity = pr(t, 47.3, 47.5); lt.style.transform = `translateY(${(1 - EZ.expo(pr(t, 47.3, 47.8))) * 30}px)`;
    show(tw, t, 48.6, { k: 'up', out: 51.9 }); show(qm, t, 50.35, { k: 'pop', r: 10, out: 51.9 });
    wordsAt(r0, t); wordsAt(r1, t); wordsAt(r3, t);
    show(la, t, 52.1, { k: 'left' }); show(lb, t, 52.3, { k: 'left' });
    const ra = EZ.inout(pr(t, 52.4, 53.4)); la.querySelector('.dot').style.left = (170 + ra * 1380) + 'px'; la.querySelector('.tx').textContent = ra >= 1 ? '✓ 已上手 · 已产出' : '';
    lb.querySelector('.tx').textContent = t > 52.8 ? '等待适配' + '.'.repeat(1 + Math.floor(t * 3) % 3) : '';
    lb.querySelector('.dot').style.left = (170 + 8 * Math.sin(t * 8) * (t > 52.8 ? 1 : 0)) + 'px';
    camAt(cam, t, { x: 1640, y: 460, o: pr(t, 44.6, 44.9) * (1 - pr(t, 45.2, 45.4)) });
  };
  sc.cam = t => { const s = shake(t, 50.35, .35, 8); return { x: 960, y: 540, z: 1, sx: s[0], sy: s[1] }; };
  S(44.55, 'swoosh', .6); S(44.6, 'tick', .4); S(45.75, 'pop', .8); S(45.8, 'pop', .6, -.7); S(46.9, 'slide', .6, 0, { d: 1.4 }); S(47.3, 'thud', .7); S(48.1, 'pop', .6, .7);
  S(48.6, 'card', .6); S(50.35, 'record_scratch', .9); S(52.0, 'whoosh', .5); S(52.1, 'swipe', .4, -.5); S(52.3, 'swipe', .4, -.5); S(52.4, 'slide', .5, 0, { d: 1 }); S(53.45, 'ding', .7, .6); S(54.6, 'hit', .9);
})();

/* ---------- S8  55.67 – 59.9  游戏 vs AI · 统一内存 ---------- */
(() => {
  const sc = new Scene(55.67, 59.9, '#0A0A0A', { grid: 'gridD', trans: 'wipe', td: .45, tc: '#0A0A0A' });
  const T = tags(sc, '// 08 — 公道话', '', true);
  const g = mk(sc.el, `<div class="dcard" style="width:500px;height:260px"><div class="lb">// 缺点</div><div style="position:absolute;left:26px;bottom:26px"><div style="font-size:56px;font-weight:600">打游戏</div><div style="font-size:30px;color:#777">不如 Windows</div></div></div>`, 146, 240);
  const gp = img(sc.el, 'p_gamepad.png', 820, 740, 480, { ic: 'chD' });
  const ai = words(sc.el, [{ h: '但，', t: 57.37 }, { h: '<span style="color:#6d9bff">AI 时代了。</span>', t: 57.7 }], 146, 150, 'h1', { style: 'color:#fff' });
  const mem = mk(sc.el, `<div class="dcard" style="width:1628px;height:400px"><div class="lb">// 知识点 · 统一内存</div>
     <div style="position:absolute;left:30px;top:70px;font-size:28px;color:#999">本地跑大模型，先看能装进多少内存</div>
     <div style="position:absolute;left:30px;top:150px;right:30px">
       <div style="display:flex;align-items:center;gap:20px"><div style="width:320px;font-size:28px">旗舰游戏显卡 · 显存</div><div style="flex:1;height:44px;border-radius:10px;background:#1f1f1f;overflow:hidden"><div class="b1" style="height:100%;width:0;background:#666;border-radius:10px"></div></div><div style="width:140px;font-size:40px;font-weight:600">32GB</div></div>
       <div style="display:flex;align-items:center;gap:20px;margin-top:22px"><div style="width:320px;font-size:28px">Mac Studio · 统一内存</div><div style="flex:1;height:44px;border-radius:10px;background:#1f1f1f;overflow:hidden"><div class="b2" style="height:100%;width:0;background:linear-gradient(90deg,#2462EA,#6d9bff);border-radius:10px"></div></div><div style="width:140px;font-size:40px;font-weight:600;color:#6d9bff">512GB</div></div>
       <div class="mono nn" style="margin-top:26px;font-size:22px;color:#777">CPU · GPU · 神经网络引擎 共用同一池内存 · 超大模型可以整个放进本机</div></div></div>`, 146, 400);
  const b1 = mem.querySelector('.b1'), b2 = mem.querySelector('.b2'), nn = mem.querySelector('.nn');
  sc.update = t => {
    T(t);
    show(g, t, 55.8, { k: 'up', out: 57.2 });
    const gh = hopIn(t, 56.0); place(gp, { o: gh.o * (1 - pr(t, 57.1, 57.3)), s: gh.s, x: 820, y: 740 + gh.y });
    wordsAt(ai, t);
    show(mem, t, 57.9, { k: 'up' });
    b1.style.width = (EZ.out(pr(t, 58.2, 58.6)) * 6.25) + '%'; b2.style.width = (EZ.expo(pr(t, 58.5, 59.5)) * 100) + '%'; nn.style.opacity = pr(t, 59.2, 59.5);
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 });
  S(55.7, 'swoosh', .6); S(55.8, 'card', .5); S(56.0, 'bleeps', .4, .3, { d: 1 }); S(57.37, 'tick', .4); S(57.7, 'hit', .8); S(57.9, 'card', .5); S(58.5, 'rise', .5, 0, { d: 1 }); S(59.5, 'ding', .7);
})();

/* ---------- S9  59.9 – 63.0  Codex / Claude ---------- */
(() => {
  const sc = new Scene(59.9, 63.0, 'var(--paper)', { grid: 'grid', trans: 'flash', td: .3, fa: .6 });
  const T = tags(sc, '// 09 — 试试看');
  const t1 = words(sc.el, [{ h: '试试&nbsp;', t: 59.95 }, { h: '<span class="acc">Codex</span>', t: 60.2 }, { h: '&nbsp;或&nbsp;', t: 60.6 }, { h: '<span class="acc">Claude</span>', t: 61.0 }], 146, 150, 'h1');
  const win = mk(sc.el, `<div class="card" style="width:1100px;height:520px;background:#0E0E0E;border:none;overflow:hidden">
     <div style="height:54px;background:#1c1c1c;display:flex;align-items:center;gap:10px;padding:0 20px"><i style="width:14px;height:14px;border-radius:50%;background:#ff5f57;display:block"></i><i style="width:14px;height:14px;border-radius:50%;background:#febc2e;display:block"></i><i style="width:14px;height:14px;border-radius:50%;background:#28c840;display:block"></i><span class="mono tab" style="margin-left:20px;font-size:18px;color:#999">Terminal — codex</span></div>
     <div class="tx term" style="background:transparent;font-size:28px;padding:30px 34px"></div></div>`, 146, 330);
  const tx = win.querySelector('.tx'), tab = win.querySelector('.tab');
  const L = [[60.3, '❯ 帮我做一个作品集网站', '#fff'], [60.8, '  ✓ 已生成页面 · 已部署上线', '#6d9bff'], [61.2, '❯ 把这期视频剪好，配上字幕', '#fff'], [61.9, '  ✓ 粗剪完成', '#6d9bff'], [62.3, '  ✓ 字幕已生成', '#6d9bff']];
  const kid = img(sc.el, 'p_typing_excited.png', 1560, 1000, 560);
  sc.update = t => {
    T(t);
    wordsAt(t1, t); show(win, t, 60.0, { k: 'up' });
    tab.textContent = t > 61.0 ? 'Terminal — claude' : 'Terminal — codex';
    tx.innerHTML = L.filter(l => t >= l[0]).map(l => `<div style="color:${l[2]}">${l[2] === '#fff' ? l[1].slice(0, Math.floor(pr(t, l[0], l[0] + .5) * l[1].length)) : l[1]}</div>`).join('') + (Math.floor(t * 2.5) % 2 ? '<span style="color:#fff">▍</span>' : '');
    const k = hopIn(t, 60.4); place(kid, { o: k.o, s: k.s * breathe(t), x: 1560, y: 1000 + k.y });
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 + .02 * pr(t, 59.9, 63) });
  S(59.95, 'tick', .4); S(60.2, 'pop', .6); S(61.0, 'pop', .6); S(60.3, 'type', .6, -.3, { d: .5 }); S(60.8, 'ding', .5); S(61.2, 'type', .6, -.3, { d: .6 }); S(61.9, 'ding', .5); S(62.3, 'ding', .6); S(60.4, 'pop', .5, .6);
})();

/* ---------- S10  63.0 – 69.6  创造 > 游戏 · 正反馈 ---------- */
(() => {
  const sc = new Scene(63.0, 69.6, 'var(--blue)', { grid: 'gridB', trans: 'circle', td: .5, tc: '#2462EA', cx: 1560, cy: 700 });
  const T = tags(sc, '// 10 — 创造');
  const t1 = words(sc.el, [{ h: '制造一些东西，', t: 63.0 }, { h: '创造一些内容，', t: 64.1 }], 146, 150, 'h2', { style: 'color:#fff' });
  const made = ['个人网站', '小程序', '短视频', '公众号文章', '效率工具', '原创音乐'];
  const me = made.map((m, i) => mk(sc.el, `<div class="card" style="width:250px;height:130px;border:none"><div class="lb">// made ${String(i + 1).padStart(2, '0')}</div><div style="position:absolute;left:22px;bottom:18px;font-size:36px;font-weight:600">${m}</div></div>`, 146 + (i % 3) * 270, 330 + Math.floor(i / 3) * 150));
  // balance: create vs game
  const t2 = words(sc.el, [{ h: '它的乐趣，', t: 65.5 }, { h: '远大于游戏。', t: 66.3 }], 146, 150, 'h2', { style: 'color:#fff' });
  const bal = mk(sc.el, `<div style="position:relative;width:900px;height:420px">
     <div style="position:absolute;left:446px;top:90px;width:8px;height:320px;background:rgba(255,255,255,.6);border-radius:4px"></div>
     <div class="beam" style="position:absolute;left:50px;top:84px;width:800px;height:10px;border-radius:5px;background:#fff;transform-origin:50% 50%"></div>
     <div class="pl" style="position:absolute"><div class="card" style="width:260px;height:120px;border:none"><div class="lb">// 创造</div><div style="position:absolute;left:22px;bottom:16px;font-size:44px;font-weight:600;color:var(--blue)">🛠 创造</div></div></div>
     <div class="pr" style="position:absolute"><div class="card" style="width:260px;height:120px;border:none;opacity:.8"><div class="lb">// 游戏</div><div style="position:absolute;left:22px;bottom:16px;font-size:44px;font-weight:600">🎮 游戏</div></div></div></div>`, 146, 380);
  const beam = bal.querySelector('.beam'), pl = bal.querySelector('.pl'), prr = bal.querySelector('.pr');
  // feedback metrics
  const t3 = words(sc.el, [{ h: '而且，能产生很多', t: 67.37 }, { h: '<span style="background:#fff;color:var(--blue);border-radius:18px;padding:0 16px">正面回馈。</span>', t: 68.4, k: 'pop' }], 146, 150, 'h2', { style: 'color:#fff' });
  const st = [['点赞', 12480], ['评论', 864], ['新粉丝', 2315]];
  const se = st.map((s, i) => mk(sc.el, `<div class="card" style="width:500px;height:200px;border:none"><div class="lb">// ${s[0]}</div><div class="v" style="position:absolute;left:24px;bottom:22px;font-size:90px;font-weight:600;letter-spacing:-3px;color:var(--blue)">+0</div></div>`, 146 + i * 530, 420));
  const bird = img(sc.el, 'b_squawk.png', 1650, 980, 300);
  const bub = mk(sc.el, `<div class="bubble" style="border:none">好玩！</div>`, 1560, 640, { ax: .5, ay: .5 });
  sc.update = t => {
    T(t);
    wordsAt(t1, t, { out: 65.3 });
    me.forEach((m, i) => show(m, t, 63.2 + i * .2, { k: 'pop', out: 65.3 }));
    wordsAt(t2, t, { out: 67.2 }); show(bal, t, 65.5, { k: 'up', out: 67.2 });
    const tl = -12 * EZ.spring(pr(t, 66.3, 67.1)), r = tl * Math.PI / 180;
    beam.style.transform = `rotate(${tl}deg)`;
    pl.style.transform = `translate(${450 - 340 * Math.cos(r) - 130}px,${89 - 340 * Math.sin(r) + 16}px)`;
    prr.style.transform = `translate(${450 + 340 * Math.cos(r) - 130}px,${89 + 340 * Math.sin(r) + 16}px)`;
    wordsAt(t3, t);
    se.forEach((e, i) => { show(e, t, 67.5 + i * .2, { k: 'up' }); e.querySelector('.v').textContent = '+' + fmt(counter(t, 67.7 + i * .2, 69.2, 0, st[i][1])); });
    const bh = hopIn(t, 66.35); place(bird, { o: bh.o, s: bh.s, x: 1650 + 6 * Math.sin(t * 5), y: 980 + bh.y, sx: -1 });
    show(bub, t, 66.45, { k: 'pop', out: 67.5 });
  };
  sc.cam = t => ({ x: 960, y: 540, z: 1 });
  S(62.95, 'whoosh', .7); made.forEach((m, i) => S(63.2 + i * .2, 'pop', .45, -.6 + (i % 3) * .5)); S(65.5, 'card', .5); S(66.3, 'creak', .6, 0, { d: .7 }); S(66.35, 'squawk', .8, .6); S(67.1, 'thud', .7);
  S(67.5, 'card', .5); S(67.7, 'counter', .45, 0, { d: 1.5 }); S(68.4, 'pop', .8); S(69.2, 'coin', .7, .4);
})();

/* ---------- S11  69.6 – 73.25  所以：第一件事，把电脑换成 Mac ---------- */
(() => {
  const sc = new Scene(69.6, 73.25, 'var(--paper)', { grid: 'grid', trans: 'wipe', td: .45, tc: '#F7F7F5' });
  const T = tags(sc, '// 11 — 结论');
  const rc = [['专注', '系统稳 · 数据十几年不丢'], ['首发', 'AI 新工具往往先上 Mac'], ['内存', '统一内存 · 本地跑大模型'], ['生态', '专业软件 · 体验更好']];
  const re = rc.map((r, i) => mk(sc.el, `<div class="card" style="width:390px;height:210px"><div class="lb">// ${String(i + 1).padStart(2, '0')}</div><div class="ck" style="position:absolute;right:22px;top:18px;width:36px;height:36px;border-radius:50%;border:2px solid var(--line);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:22px"></div><div style="position:absolute;left:24px;top:70px;font-size:56px;font-weight:600">${r[0]}</div><div style="position:absolute;left:24px;bottom:22px;font-size:22px;color:var(--g1)">${r[1]}</div></div>`, 146 + i * 412, 250));
  const TT = [69.9, 70.3, 70.7, 71.1];
  const k = mk(sc.el, `<div class="tag" style="font-size:26px">// 所以 AI 时代，想跟上进程——第一件事</div>`, 146, 600);
  const big = words(sc.el, [{ h: '把电脑换成&nbsp;', t: 72.0 }, { h: '<span class="acc" style="font-size:220px;font-weight:700;letter-spacing:-8px">Mac。</span>', t: 72.3, k: 'slam', d: .45 }], 146, 650, 'h1', { style: 'display:flex;align-items:baseline;font-size:120px' });
  sc.update = t => {
    T(t);
    re.forEach((e, i) => { show(e, t, TT[i], { k: 'up' }); const c = pr(t, TT[i] + .25, TT[i] + .4), ck = e.querySelector('.ck'); ck.style.background = c > 0 ? 'var(--blue)' : ''; ck.style.borderColor = c > 0 ? 'var(--blue)' : 'var(--line)'; ck.textContent = c > 0 ? '✓' : ''; ck.style.transform = `scale(${c > 0 ? EZ.spring(c) : 1})`; });
    show(k, t, 69.7, { k: 'up' }); wordsAt(big, t);
  };
  sc.cam = t => { const s = shake(t, 72.3, .3, 10); return { x: 960, y: 540, z: 1 + .03 * EZ.out(pr(t, 72.3, 73.25)), sx: s[0], sy: s[1] }; };
  S(69.6, 'swoosh', .6); TT.forEach((tt, i) => { S(tt, 'card', .45, -.6 + i * .4); S(tt + .25, 'check', .7, -.6 + i * .4, { n: i }); }); S(72.0, 'tick', .4); S(72.3, 'hit', 1.1); S(72.35, 'shine', .6);
})();

/* ---------- S12  73.25 – 81.9  评论区 · 打破误区 · 我是阿杜 ---------- */
(() => {
  const sc = new Scene(73.25, 82.0, '#0A0A0A', { grid: 'gridD', trans: 'circle', td: .5, tc: '#0A0A0A', cx: 960, cy: 540 });
  const T = tags(sc, '// 12 — 你呢？', '', true);
  const t1 = words(sc.el, [{ h: '如果你已经换了，', t: 73.3 }], 146, 150, 'h2', { style: 'color:#fff' });
  const t2 = words(sc.el, [{ h: '评论区', t: 74.2 }, { h: '<span style="color:#6d9bff">聊一聊。</span>', t: 74.9 }], 146, 260, 'h1', { style: 'color:#fff' });
  const cm = [['已经换了三年，再也没重装过系统', 328], ['M 芯片续航太顶了，一天不插电', 215], ['用 Claude 写代码，Mac 上真顺', 196]];
  const ce = cm.map((c, i) => mk(sc.el, `<div class="dcard" style="width:760px;height:120px"><div style="position:absolute;left:22px;top:30px;width:60px;height:60px;border-radius:50%;background:${['#ff7eb3', '#6d9bff', '#ffb347'][i]}"></div><div style="position:absolute;left:104px;top:26px;font-size:30px">${c[0]}</div><div class="mono" style="position:absolute;left:104px;bottom:20px;font-size:19px;color:#777">♥ <span class="lk">${c[1]}</span></div></div>`, 146, 440 + i * 140));
  const myth = words(sc.el, [{ h: '2026 年了，', t: 75.8 }, { h: '还有人觉得', t: 77.3 }], 146, 170, 'h2', { style: 'color:#fff' });
  const m2 = mk(sc.el, `<div style="position:relative;font-size:150px;font-weight:700;letter-spacing:-5px;color:#fff">Mac 办公不行？<div class="st" style="position:absolute;left:-10px;top:52%;height:14px;width:0;background:#E5484D;border-radius:7px"></div></div>`, 146, 300);
  const stl = m2.querySelector('.st');
  const stamp = mk(sc.el, `<div class="pill" style="background:#E5484D;color:#fff;font-size:44px;font-weight:700;padding:10px 34px">误区 ✕</div>`, 1180, 540, { ax: .5, ay: .5 });
  // outro
  const end = mk(sc.el, `<div style="width:1920px;height:1080px;background:var(--paper);position:relative;overflow:hidden"><div class="grid"></div></div>`, 0, 0);
  const ew = words(end.firstChild, [{ h: '我是&nbsp;', t: 79.55 }, { h: 'Vibe coder&nbsp;', t: 79.8 }, { h: '<span class="acc">阿杜</span>', t: 80.1 }], 146, 380, 'h1');
  const eb = words(end.firstChild, [{ h: '下期见。', t: 80.95 }], 146, 520, 'h2', { style: 'color:var(--g1)' });
  const cam = camCard(end.firstChild, 420, 746);
  const wave = img(end.firstChild, 'c_a.png', 1180, 1130, 560);
  const bird = img(end.firstChild, 'b_fly.png', 0, 0, 170);
  sc.update = t => {
    T(t);
    wordsAt(t1, t, { out: 75.6 }); wordsAt(t2, t, { out: 75.6 });
    ce.forEach((e, i) => { show(e, t, 74.0 + i * .3, { k: 'left', out: 75.6 }); e.querySelector('.lk').textContent = Math.round(cm[i][1] + 40 * pr(t, 74.4, 75.5)); });
    wordsAt(myth, t, { out: 79.3 }); show(m2, t, 77.6, { k: 'up', out: 79.3 });
    stl.style.width = (EZ.expo(pr(t, 78.45, 78.75)) * 104) + '%';
    show(stamp, t, 78.55, { k: 'slam', d: .3, r: -8, out: 79.3 });
    const ep = EZ.expo(pr(t, 79.3, 79.85)); place(end, { o: pr(t, 79.3, 79.32), x: 0, y: (1 - ep) * 1080 });
    wordsAt(ew, t); wordsAt(eb, t);
    camAt(cam, t, { x: 1560, y: 520, o: pr(t, 79.5, 79.8), s: .9 + .1 * EZ.spring(pr(t, 79.5, 80.1)) });
    const w = hopIn(t, 80.9); place(wave, { o: w.o, s: w.s, x: 1180, y: 1130 + w.y });
    const bf = pr(t, 80.6, 81.9); place(bird, { o: bf > 0 && bf < 1 ? 1 : 0, x: 1900 - bf * 800, y: 260 - Math.sin(bf * Math.PI) * 80 });
  };
  sc.cam = t => { const s = shake(t, 78.55, .35, 14); return { x: 960, y: 540, z: 1, sx: s[0], sy: s[1] }; };
  S(73.25, 'whoosh', .7); S(73.3, 'tick', .4); [74.0, 74.3, 74.6].forEach((tt, i) => S(tt, 'msg', .6, -.5)); S(74.9, 'pop', .6); S(75.8, 'tick', .4); S(77.3, 'tick', .4); S(77.6, 'card', .5);
  S(78.45, 'slash', .8); S(78.55, 'stamp', 1.1); S(79.3, 'swoosh', .8); S(79.55, 'tick', .3); S(80.1, 'ding', .6); S(80.6, 'flap', .7, .5); S(80.9, 'pop', .6); S(80.95, 'chirp', .8, .3);
})();

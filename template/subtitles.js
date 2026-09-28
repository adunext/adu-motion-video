/* 双语字幕层：需要 subs.js（scripts/build_subs.py 生成）。CONFIG.subtitles=false 时关闭 */
if (typeof SUBS !== 'undefined' && CONFIG.subtitles !== false)
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

/* main runtime */
(function () {
  const Q = new URLSearchParams(location.search);
  // transition overlays
  const fx = $('fx');
  const wipe = document.createElement('div'); wipe.style.cssText = 'position:absolute;inset:0;transform:translateX(100%)'; fx.appendChild(wipe);
  const circ = document.createElement('div'); circ.style.cssText = 'position:absolute;left:960px;top:540px;width:10px;height:10px;border-radius:50%;transform:translate(-50%,-50%) scale(0)'; fx.appendChild(circ);
  const flash = document.createElement('div'); flash.style.cssText = 'position:absolute;inset:0;background:#fff;opacity:0'; fx.appendChild(flash);
  const fade = document.createElement('div'); fade.style.cssText = 'position:absolute;inset:0;background:#000;opacity:0'; fx.appendChild(fade);

  function trans(t) {
    wipe.style.transform = 'translateX(100%)'; circ.style.transform = 'translate(-50%,-50%) scale(0)'; flash.style.opacity = 0;
    let wf = '';
    for (const sc of SCENES) {
      const tr = sc.opt.trans; if (!tr) continue;
      const d = sc.opt.td || .5, x = (t - (sc.s - d / 2)) / d;
      if (x < 0 || x > 1) continue;
      if (tr === 'wipe') { // colour panel sweeps across
        wipe.style.background = sc.opt.tc || sc.el.style.background;
        const p = EZ.inout(x); wipe.style.transform = `translateX(${lerp(100, -100, p)}%)`;
      }
      if (tr === 'circle') {
        circ.style.background = sc.opt.tc || sc.el.style.background; const p = x < .5 ? EZ.in(x * 2) : 1; const q = x < .5 ? 0 : EZ.out((x - .5) * 2);
        circ.style.left = (sc.opt.cx || 960) + 'px'; circ.style.top = (sc.opt.cy || 540) + 'px';
        circ.style.transform = `translate(-50%,-50%) scale(${p * 460})`; circ.style.opacity = Math.min(1 - q, clamp(p * 25));   // invisible while it's a dot (no stray white spot on the outgoing scene)
      }
      if (tr === 'flash') flash.style.opacity = Math.max(0, 1 - Math.abs(x - .5) * 2.2) * (sc.opt.fa || .9);
      if (tr === 'blur') { const k = Math.sin(x * Math.PI); wf = `blur(${(k * 24).toFixed(1)}px)`; }
    }
    $('world').style.filter = wf;
  }

  window.renderAt = function (t) {
    const active = SCENES.filter(sc => t >= sc.s - 1e-4 && t < sc.e);
    for (const sc of SCENES) sc.el.style.display = active.includes(sc) ? 'block' : 'none';
    let cam = null;
    for (const sc of active) { sc.update(t); const c = sc.cam(t); if (c) cam = c; }
    const w = $('world');
    if (cam) w.style.transform = `translate(${(cam.sx || 0).toFixed(2)}px,${(cam.sy || 0).toFixed(2)}px) scale(${(cam.z || 1).toFixed(4)}) translate(${(960 - (cam.x || 960)).toFixed(2)}px,${(540 - (cam.y || 540)).toFixed(2)}px)`;
    else w.style.transform = '';
    trans(t);
    fade.style.opacity = clamp((t - ((window.END || CONFIG.end) - .45)) / .4);
    if (window.OVERLAY) window.OVERLAY(t);
  };
  window.READY = (async () => {
    await document.fonts.ready;
    await Promise.all([...document.images].map(im => im.complete ? 0 : new Promise(r => { im.onload = im.onerror = r; })));
    renderAt(parseFloat(Q.get('t') || '1'));
    document.title = 'done';
  })();
})();

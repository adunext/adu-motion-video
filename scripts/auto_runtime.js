/* Isolated authored pack runtimes, driven by one integer output frame clock. */
(() => {
  const plan = window.AUTO_PLAN, fps = plan.fps;
  window.CONFIG = {demo:false, fps, end:plan.end_frame/fps, width:plan.width, height:plan.height};
  window.END = CONFIG.end;
  const frames = plan.parts.map(part => {
    const frame = document.createElement('iframe');
    frame.style.cssText = `position:absolute;inset:0;border:0;width:${plan.width}px;height:${plan.height}px;visibility:hidden`;
    frame.src = part.path + '/index.html';
    const ready = new Promise((resolve, reject) => {
      frame.onerror = () => reject(Error('Missing composition part: ' + part.path));
      frame.onload = async () => {
        try {
          const child = frame.contentWindow;
          if (!child.READY || typeof child.renderAt !== 'function') throw Error('Part has no deterministic render contract');
          await child.READY;
          resolve(child);
        } catch(error) { reject(error); }
      };
    });
    document.getElementById('stage').append(frame);
    return {frame, ready, part};
  });
  async function waitChild(child) {
    if (child.imgWait) await child.imgWait();
    // A newly shown iframe can start font/layout work only after visibility
    // changes. Flush layout before observing fonts.ready, not before it.
    child.document.documentElement.getBoundingClientRect();
    await child.document.fonts.ready;
    if (child.document.querySelector('video,audio')) throw Error('Part has unsupported native video/audio');
    const visible = [...child.document.images].filter(im => {
      if (!(im.getAttribute('src') || im.currentSrc)) return false;
      for (let el = im; el; el = el.parentElement) {
        const style = child.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
      }
      return true;
    });
    await Promise.all(visible.map(async im => {
      try { await im.decode(); } catch (error) { throw Error('Part image decode failed: ' + im.src); }
      if (!im.naturalWidth) throw Error('Missing part image: ' + im.src);
    }));
  }
  let active;
  window.renderAt = async t => {
    if (!Number.isFinite(t)) throw Error('renderAt needs a finite output time');
    const index = Math.max(0, Math.min(plan.end_frame-1, Math.floor(t*fps+1e-6)));
    const previous = active;
    active = frames.find(x => index >= x.part.startFrame && index < x.part.endFrame);
    if (!active) throw Error('No authored composition at frame ' + index);
    frames.forEach(x => { x.frame.style.visibility = x === active ? 'visible' : 'hidden'; });
    const child = await active.ready;
    await child.renderAt((index-active.part.startFrame)/fps);
    await waitChild(child);
    if (previous !== active) {
      // Commit visibility/layer changes before a parent screenshot. No video
      // time advances here; both paint turns display the same integer frame.
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
    }
    window.MACRO_OUTPUT_T = index/fps;
    window.AUTO_ACTIVE_PART = active.part.path;
  };
  window.imgWait = async () => { if (active) await waitChild(await active.ready); };
  window.READY = (async () => {
    const children = await Promise.all(frames.map(x => x.ready));
    window.SFX = frames.flatMap((x,i) => children[i].SFX.map(cue => ({...cue,t:cue.t+x.part.startFrame/fps})))
      .filter(cue => cue.t >= 0 && cue.t < window.END).sort((a,b)=>a.t-b.t);
    await window.renderAt(0);
    document.title = 'done';
  })();
})();

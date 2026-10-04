/* Full-scene pack playback. Each authored scene retains its source clock; the
   presenter, subtitles, audio and edit timeline always use output time. */
(() => {
  const plan = window.MACRO_PLAN;
  if (!plan || !Array.isArray(plan.scenes) || SCENES.length !== plan.scenes.length) {
    throw Error('Macro plan/scene count mismatch');
  }
  const fps = plan.fps;
  window.END = plan.end_frame / fps;
  const fx = $('fx');
  const wipe = document.createElement('div');
  wipe.style.cssText = 'position:absolute;inset:0;transform:translateX(100%)'; fx.appendChild(wipe);
  const circle = document.createElement('div');
  circle.style.cssText = 'position:absolute;left:960px;top:540px;width:10px;height:10px;border-radius:50%;opacity:0'; fx.appendChild(circle);
  const flash = document.createElement('div');
  flash.style.cssText = 'position:absolute;inset:0;background:#fff;opacity:0'; fx.appendChild(flash);
  const fade = document.createElement('div');
  fade.style.cssText = 'position:absolute;inset:0;background:#000;opacity:0'; fx.appendChild(fade);

  function sourceAt(item, outputFrame) {
    const points = item.time_map;
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1], b = points[i];
      if (outputFrame <= b.output_frame || i === points.length - 1) {
        const x = clamp((outputFrame - a.output_frame) / (b.output_frame - a.output_frame));
        return lerp(a.source, b.source, x);
      }
    }
    return points[0].source;
  }

  function outputAt(item, source) {
    const points = item.time_map;
    if (source < points[0].source) return points[0].output_frame + Math.round((source - points[0].source) * fps);
    if (source > points.at(-1).source) return points.at(-1).output_frame + Math.round((source - points.at(-1).source) * fps);
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1], b = points[i];
      if (source <= b.source) return Math.round(lerp(a.output_frame, b.output_frame, (source - a.source) / (b.source - a.source)));
    }
    return points.at(-1).output_frame;
  }

  // Source S() calls are captured once for each instantiated block. The final
  // SFX list is retimed to the new scene arrangement, including repeated scenes.
  if (!Array.isArray(window.MACRO_SOURCE_SFX) || window.MACRO_SOURCE_SFX.length !== SCENES.length)
    throw Error('Source SFX capture is incomplete');
  SFX.length = 0;
  plan.scenes.forEach((item, i) => {
    const occurrences=new Map();
    for (const cue of window.MACRO_SOURCE_SFX[i]) {
      const authoredFrame = outputAt(item, cue.t);
      // A reused opening scene has no preceding shot for its transition
      // lead-in. Keep that sound at frame zero instead of silently dropping it.
      const globalStart = window.MACRO_GLOBAL_START_FRAME || 0;
      const globalEnd = window.MACRO_GLOBAL_END_FRAME ?? plan.end_frame;
      const frame = i === 0 && globalStart === 0 ? Math.max(0, authoredFrame) : authoredFrame;
      if (frame + globalStart < 0 || frame + globalStart >= globalEnd) continue;
      const key=JSON.stringify([cue.t,cue.type,cue.d??null,cue.n??null]);
      const ordinal=occurrences.get(key)||0;occurrences.set(key,ordinal+1);
      const packId=plan.pack||window.PACK_LAYOUT?.pack||'performance';
      const family=packId.includes('paper')?'paper':packId.includes('editorial')?'editorial':packId.includes('console')?'instrument':packId.includes('showcase')?'depth':packId.includes('sticker')?'sticker':packId.includes('kinetic')?'kinetic':'performance';
      const mapped = {...cue, t: frame / fps, sourceAt:cue.t,sceneInstanceId:item.id,
        eventId:JSON.stringify([packId,item.id,key,ordinal]),soundFamily:family};
      // d is generator time, not a second choreography anchor. A sound may
      // cross a retimed reading gap; preserve its original duration/timbre.
      // Only the onset follows the mapped action clock.
      SFX.push(mapped);
    }
  });
  SFX.sort((a, b) => a.t - b.t);

  function transition(frame, current) {
    wipe.style.transform = 'translateX(100%)';
    circle.style.opacity = '0'; circle.style.transform = 'translate(-50%,-50%) scale(0)';
    flash.style.opacity = '0'; $('world').style.filter = '';
    if (!current) return;
    const currentScene = SCENES[current.index];
    if (typeof currentScene.macroTransition === 'function') {
      currentScene.macroTransition({frame, fps, item: plan.scenes[current.index],
        nextItem: plan.scenes[current.index + 1] || null,
        nextScene: SCENES[current.index + 1] || null});
      return;
    }
    let transitionIndex = current.index;
    const nextIndex = transitionIndex + 1;
    if (nextIndex < SCENES.length) {
      const next = SCENES[nextIndex], nextStart = plan.scenes[nextIndex].output_start_frame;
      if (next.opt.trans && frame >= nextStart - (next.opt.td || .5) * fps / 2)
        transitionIndex = nextIndex;
    }
    const item = plan.scenes[transitionIndex], sc = SCENES[transitionIndex], tr = sc.opt.trans;
    if (!tr || transitionIndex === 0) return; // no outgoing shot before this project's first frame
    const duration = (sc.opt.td || .5) * fps;
    const x = (frame - (item.output_start_frame - duration / 2)) / duration;
    if (x < 0 || x > 1) return;
    if (tr === 'wipe') {
      wipe.style.background = sc.opt.tc || sc.el.style.background;
      wipe.style.transform = `translateX(${lerp(100, -100, EZ.inout(x))}%)`;
    } else if (tr === 'circle') {
      const p = x < .5 ? EZ.in(x * 2) : 1;
      const q = x < .5 ? 0 : EZ.out((x - .5) * 2);
      circle.style.background = sc.opt.tc || sc.el.style.background;
      circle.style.left = (sc.opt.cx || 960) + 'px'; circle.style.top = (sc.opt.cy || 540) + 'px';
      circle.style.transform = `translate(-50%,-50%) scale(${p * 460})`;
      circle.style.opacity = String(Math.min(1 - q, clamp(p * 25)));
    } else if (tr === 'flash') {
      flash.style.opacity = String(Math.max(0, 1 - Math.abs(x - .5) * 2.2) * (sc.opt.fa || .9));
    } else if (tr === 'blur') {
      $('world').style.filter = `blur(${(Math.sin(x * Math.PI) * 24).toFixed(1)}px)`;
    }
  }

  window.renderAt = function (t) {
    if (!Number.isFinite(t)) throw Error('renderAt needs a finite output time');
    const frame = Math.max(0, Math.min(plan.end_frame - 1, Math.floor(t * fps + 1e-6)));
    const index = plan.scenes.findIndex(item => frame >= item.output_start_frame && frame < item.output_end_frame);
    if (index < 0) throw Error(`No macro scene at output frame ${frame}`);
    const item = plan.scenes[index], sc = SCENES[index], source = sourceAt(item, frame);
    window.MACRO_OUTPUT_T = frame / fps;
    window.MACRO_TEMPLATE_SOURCE_T = source;
    window.PACK_OUTPUT_TIME = frame / fps;
    window.MACRO_IS_OPENING_SCENE = index === 0;
    window.PACK_NUMBERS = window.MACRO_NUMBERS_BY_INSTANCE?.[index] || {};
    window.MACRO_MEDIA_ALIAS = window.MACRO_MEDIA_BY_INSTANCE?.[index] || {};
    window.MACRO_VIDEO_CLOCKS = item.mediaClocks || [];
    for (let i = 0; i < SCENES.length; i++) SCENES[i].el.style.display = i === index ? 'block' : 'none';
    sc.update(source);
    // A few legacy hidden helpers return before resetting their transform and
    // then append scale(0,0). Identical trailing zero scales are algebraically
    // idempotent; canonicalize them so reverse seeks cannot grow CSS history.
    // Keep every nonzero transform and the source choreography unchanged.
    for (const element of sc.el.querySelectorAll?.('[style]') || []) {
      const transform = element.style.transform;
      if (transform) {
        const normalized = transform.replace(/(?:\s+scale\(0(?:,\s*0)?\)){2,}$/, ' scale(0, 0)');
        if (normalized !== transform) element.style.transform = normalized;
      }
    }
    const cam = sc.cam(source), world = $('world');
    if (cam) world.style.transform = `translate(${(cam.sx || 0).toFixed(2)}px,${(cam.sy || 0).toFixed(2)}px) scale(${(cam.z || 1).toFixed(4)}) translate(${(960 - (cam.x || 960)).toFixed(2)}px,${(540 - (cam.y || 540)).toFixed(2)}px)`;
    else world.style.transform = '';
    transition(frame, {index});
    const fadeSeconds = CONFIG.fadeEndSeconds || 0;
    fade.style.opacity = String(fadeSeconds ? clamp((t - (window.END - fadeSeconds)) / fadeSeconds) : 0);
    if (window.OVERLAY) window.OVERLAY(frame / fps);
  };
  window.READY = (async () => {
    await document.fonts.ready;
    // CSS sprites are absent from document.images. Decode them in bounded
    // batches so a complete source wall is neither skipped nor loaded in one
    // memory-heavy burst. This also makes missing source sheets explicit.
    const wallItems = typeof WALL !== 'undefined' ? WALL : [];
    window.WALL_READY_COUNT = 0;
    for (let a = 0; a < wallItems.length; a += 12) {
      await Promise.all(wallItems.slice(a, a + 12).map((_, j) => new Promise((resolve, reject) => {
        const i = a + j, img = new Image();
        img.onload = () => img.decode().then(() => { window.WALL_READY_COUNT++; resolve(); },
          error => reject(new Error(`Wall ${i}: ${error.message}`)));
        img.onerror = () => reject(new Error(`Missing video-wall sprite ${i}`));
        img.src = `sc/wall/${String(i).padStart(3, '0')}.jpg`;
      })));
    }
    await Promise.all([...document.images].map(im => im.complete ? 0 : new Promise(resolve => { im.onload = im.onerror = resolve; })));
    await window.renderAt(0);
    document.title = 'done';
  })();
})();

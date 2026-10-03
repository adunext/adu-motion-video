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

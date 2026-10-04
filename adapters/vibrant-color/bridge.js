// Native plane axes: wipe is vertical, wipex horizontal. Output cuts stay on
// the new frame clock; internal flashes retain source action time.
function vibrantTransition(planes, flashes, sourceTime, context) {
  const {wipe,circ,flash,world}=planes;
  wipe.style.transform='translateY(100%)';circ.style.opacity='0';
  circ.style.transform='translate(-50%,-50%) scale(0)';world.style.filter='';
  let fl=0;
  for(const [at,amount,seconds] of flashes){const x=(sourceTime-at)/(seconds||.3);if(x>=0&&x<1)fl=Math.max(fl,amount*Math.pow(1-x,2));}
  let selected=context.scene,item=context.item;
  if(context.nextScene?.opt?.trans&&context.frame>=context.nextItem.output_start_frame-(context.nextScene.opt.td||.5)*context.fps/2){selected=context.nextScene;item=context.nextItem;}
  const o=selected.opt,x=(context.frame-(item.output_start_frame-(o.td||.5)*context.fps/2))/((o.td||.5)*context.fps);
  if(o.trans&&item.output_start_frame>0&&x>=0&&x<=1){
    if(o.trans==='wipe'||o.trans==='wipex'){wipe.style.background=o.tc||P.ink;wipe.style.transform=`translate${o.trans==='wipe'?'Y':'X'}(${lerp(100,-100,EZ.inout(x))}%)`;}
    if(o.trans==='circle'){const p=x<.5?EZ.in(x*2):1,q=x<.5?0:EZ.out((x-.5)*2);circ.style.background=o.tc||P.ink;circ.style.left=(o.cx??540)+'px';circ.style.top=(o.cy??960)+'px';circ.style.transform=`translate(-50%,-50%) scale(${p*460})`;circ.style.opacity=String(Math.min(1-q,clamp(p*25)));}
    if(o.trans==='flash')fl=Math.max(fl,Math.max(0,1-Math.abs(x-.5)*2.2)*(o.fa||.8));
    if(o.trans==='blur')world.style.filter=`blur(${(Math.sin(x*Math.PI)*22).toFixed(1)}px)`;
  }
  flash.style.opacity=fl.toFixed(3);
}

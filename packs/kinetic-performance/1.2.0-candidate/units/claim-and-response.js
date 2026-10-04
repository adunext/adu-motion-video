(() => {

const F="-apple-system,'PingFang SC',sans-serif",B='#2462EA',P='#F7F7F5',K='#0A0A0A',L='#91B5FF';
const q=(t,a,b)=>MOTION.at(t,a,b), live=(t,a,b,d=.18)=>pr(t,a,a+d)*(1-pr(t,b-d,b));
const pulse=(t,a,d=.48)=>{const p=pr(t,a,a+d);return p>0&&p<1?Math.sin(p*Math.PI*2)*(1-p):0};
const ty=(pa,h,x,y,s=96,c=K,w=1320,align='left')=>mk(pa,`<div class="kt" style="width:${w}px;font:800 ${s}px ${F};line-height:1.05;letter-spacing:-3px;color:${c};text-align:${align};white-space:nowrap">${h}</div>`,x,y);
const small=(pa,h,x,y,c='#777',w=1200)=>mk(pa,`<div style="width:${w}px;font:500 29px ${F};line-height:1.3;letter-spacing:.3px;color:${c};white-space:nowrap">${h}</div>`,x,y);
const box=(pa,w,h,bg='#fff',border='#ddd',r=22)=>mk(pa,`<div style="position:relative;width:${w}px;height:${h}px;overflow:hidden;border:1.5px solid ${border};border-radius:${r}px;background:${bg}"></div>`,0,0);
const card=(pa,label,w=300,h=100,bg='#fff',c=K,size=43)=>{const e=box(pa,w,h,bg,bg==='#fff'?'#ddd':'#555',18);e.firstChild.innerHTML=`<div style="height:100%;display:flex;align-items:center;justify-content:center;font:700 ${size}px ${F};color:${c}">${label}</div>`;return e};
const strip=(pa,w,h,c=B)=>mk(pa,`<div style="width:${w}px;height:${h}px;background:${c};border-radius:${Math.min(h/2,10)}px"></div>`);
function word(e,t,a,b,opt={}){
  const z=q(t,a,a+(opt.d||.46)),out=q(t,b-.2,b),stamp=opt.kind==='hit';
  let op=live(t,a,b,.12);if(a===0)op=1-out;
  const dy=stamp?-(1-EZ.out5(pr(t,a,a+.40)))*(opt.dist||75):(1-z)*(opt.dist||60);
  place(e,{x:opt.x??e._x,y:(opt.y??e._y)+dy-25*out,o:op*(opt.o??1),s:(opt.s??1)*(stamp?1+.10*(1-z):1),sx:stamp?1+.055*pulse(t,a,.5):1,sy:stamp?1-.07*pulse(t,a,.5):1,r:opt.r||0});
  e.firstChild.style.clipPath=stamp?'none':`inset(${(1-z)*100}% 0 0 0)`;
 }
function cam(e,t,x,y,w,h,round=0,o=1){
  const a=e.firstChild;a.style.width=w+'px';a.style.height=h+'px';a.style.borderRadius=lerp(27,Math.min(w,h)/2,round)+'px';e._sm=round;
  const lab=e.querySelector('.lab');if(lab)lab.style.opacity=String(1-round);
  camAt(e,t,{x,y,o,s:1});
 }
function scene(a,b,bg,label){const sc=new Scene(a,b,bg,{grid:bg===P?'grid':bg===B?'gridB':'gridD'});const tag=tags(sc,label,'',bg===K);sc.cam=()=>({x:960,y:540,z:1});return{sc,tag}}
const cues=xs=>xs.forEach(a=>S(...a));
{
  const{sc,tag}=scene(0,15.466,P,'// 01 — 公开，开箱，即用');const person=camCard(sc.el,410,686);
  const a=ty(sc.el,'公开蒸馏',128,202,162),b=ty(sc.el,'剪辑能力',128,423,170,B);
  const rule=strip(sc.el,1110,9),note=small(sc.el,'把制作方法，交给更多创作者',135,712);
  const opening=ty(sc.el,'开箱',136,183,184,B,600),closing=ty(sc.el,'即用',705,183,184,K,600);
  const pack=box(sc.el,1116,202,K,'#333',24);pack.firstChild.innerHTML=`<div style="padding:29px 35px;color:white;font:750 62px ${F}">adu-motion-video</div><div style="padding-left:39px;color:#91B5FF;font:500 30px ${F}">场景 / 字幕 / 音效 / 导出</div>`;
  const names=['Codex','豆包','更多助手'].map(s=>card(sc.el,s,328,95));
  const proof=ty(sc.el,'这条，就是。',135,168,146,B),proofNote=small(sc.el,'本片正在使用这一套制作方法',140,747,B);
  const black=strip(sc.el,1150,255,K),joke=ty(sc.el,'永久黑名单？',164,409,139,'#fff',1120);
  const disclaimer=small(sc.el,'个人吐槽 · 非平台通知',140,239),resolve=ty(sc.el,'照样公开',141,713,75,B);
  sc.update=t=>{
   tag(t);const p=q(t,3.4,4.2),returning=q(t,11.1,11.8);cam(person,t,lerp(1632,1716,p)-80*returning,lerp(489,248,p)+240*returning,lerp(410,250,p)+100*returning,lerp(686,250,p)+260*returning,p*(1-returning));
   word(a,t,0,3.39,{kind:'hit',dist:14});word(b,t,0,3.39,{kind:'hit',dist:20});place(rule,{x:137,y:664,sx:q(t,1.2,2.1),o:1-q(t,3.15,3.4)});word(note,t,1.7,3.39,{dist:18});
   word(opening,t,3.4,8.55,{kind:'hit',x:136-18*pulse(t,5.933)});word(closing,t,5.933,8.55,{kind:'hit'});
   const hit=pulse(t,5.933);place(pack,{x:136,y:456+12*hit,o:live(t,4.56,10.9),s:1,r:-.4*hit});
   names.forEach((e,i)=>{const z=q(t,6.05+i*.22,6.7+i*.22);place(e,{x:136+i*382,y:709+48*(1-z),o:live(t,6.05+i*.22,8.55),s:.92+.08*z});});
   word(proof,t,8.566,10.98,{kind:'hit'});word(proofNote,t,9.566,10.98,{dist:20});
   place(black,{x:136,y:348,sx:q(t,11.14,11.75),o:live(t,11.14,15.466),r:-1.4*q(t,13.133,13.46)});
   word(joke,t,12.166,15.466,{kind:'hit'});word(disclaimer,t,11.1,15.466,{dist:20});word(resolve,t,14.2,15.466,{kind:'hit',dist:30});
  };
  cues([[.05,'hit',.55],[1.2,'whoosh',.3],[3.4,'hit',.48],[4.56,'card',.34],[5.933,'hit',.45],[6.05,'click',.25,-.5],[6.27,'click',.25],[6.49,'click',.25,.5],[8.566,'ding',.35],[11.14,'whoosh',.38],[12.166,'hit',.48],[14.2,'ding',.34]]);
 }
})();
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
  const{sc,tag}=scene(68.6,84.3,K,'// 05 — 创作，回到细节');const person=camCard(sc.el,350,630);
  const head=ty(sc.el,'本期软件',143,138,108,'#fff'),info=small(sc.el,'AI 自动剪辑 · 真实软件录屏',722,195,'#aaa');
  const win=macWin(sc.el,1060,531,'本期软件 · AI 自动剪辑');win._img.style.objectFit='contain';win.querySelector('.tb').style.fontSize='25px';
  const speed=card(sc.el,'▶▶ 2.4×',220,61,K,'#fff',29),replay=small(sc.el,'上一集画面 · 创作效果回看',147,177,'#aaa');
  const labels=['排版','动效','音效'].map((s,i)=>ty(sc.el,s,1158,327+i*161,126,'#fff',420));
  const line=strip(sc.el,830,5,B),frame=mk(sc.el,'<svg width="880" height="470"><path d="M292 0V470M588 0V470M0 155H880M0 313H880" stroke="#91B5FF" stroke-width="2" stroke-dasharray="10 9" fill="none"/></svg>',151,299);
  const ending=ty(sc.el,'细节',146,306,210,L,1150),conclusion=ty(sc.el,'决定完成度',147,579,111,'#fff',1280);
  sc.update=t=>{
   tag(t);const sm=q(t,74.966,75.9),big=q(t,82.266,83.12);cam(person,t,lerp(1668,1734,sm)-53*big,lerp(504,255,sm)+213*big,lerp(350,245,sm)+74*big,lerp(630,245,sm)+300*big,sm*(1-big));
   word(head,t,68.64,74.9,{kind:'hit',dist:50});word(info,t,69.2,74.9,{dist:15});word(replay,t,74.966,82.25,{dist:18});
   const analysis=q(t,77.7,78.3),kick=pulse(t,78.133)*5+pulse(t,79.35)*8+pulse(t,80.166)*6;
   place(win,{x:lerp(681,602,analysis)-kick,y:548+12*(1-q(t,69.2,69.7)),s:lerp(1,.83,analysis),o:live(t,69.2,82.34,.2)});
   if(t<82.34){if(t<72.2)setFrame(win._img,seqAt('soft_match',90,30,t,69.2,false));else if(t<74.966)setFrame(win._img,seqAt('soft_tpl',360,72,t,72.2,false));else setFrame(win._img,seqAt('prev',240,30,t,74.966,false));}
   win.querySelector('.tb span').textContent=t<74.966?'本期软件 · AI 自动剪辑':'上一集画面 · 创作效果回看';
   win._img.style.transform=`scale(${t<74.966?1+.055*q(t,70,71.9):1+.04*q(t,79.35,80.0)})`;
   place(speed,{x:967,y:294,o:live(t,72.2,74.95)});
   labels.forEach((e,i)=>word(e,t,[78.133,79.35,80.166][i],82.25,{kind:'hit',dist:64,x:1158+10*pulse(t,[78.133,79.35,80.166][i])}));
   place(frame,{x:163,y:314,o:live(t,78.133,79.3),s:.99});place(line,{x:157,y:791,sx:q(t,80.166,81.5),o:live(t,80.166,82.2)});
   word(ending,t,82.266,84.3,{kind:'hit',dist:65});word(conclusion,t,82.7,84.3,{dist:65});
  };
  cues([[68.64,'hit',.4],[69.2,'card',.4],[72.2,'click',.3],[74.966,'whoosh',.4],[78.133,'hit',.41],[79.35,'hit',.43],[80.166,'hit',.4],[82.266,'ding',.4]]);
 }
})();
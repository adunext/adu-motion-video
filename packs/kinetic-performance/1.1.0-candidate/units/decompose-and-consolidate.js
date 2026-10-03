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
  const{sc,tag}=scene(84.3,101.666,P,'// 06 — 方法类比');const person=camCard(sc.el,358,604);
  const simpler=ty(sc.el,'逻辑，很简单',144,160,118),distill=ty(sc.el,'蒸馏',146,350,288,B,1200);
  const note=small(sc.el,'个人观察 · 方法类比，不代表模型训练事实',148,807);
  const cards=['字效','镜头','转场','排版'].map((s,i)=>card(sc.el,s,239,116,i%2?K:'#fff',i%2?'#fff':K,53));
  const sink=box(sc.el,1120,222,B,B,24);sink.firstChild.innerHTML=`<div style="padding:24px 35px;font:750 59px ${F};color:white">剪辑方法</div><div style="padding-left:37px;font:500 29px ${F};color:#DCE8FF">识别规律　→　组织配方　→　重复使用</div>`;
  const skill=ty(sc.el,'形成 Skill',150,174,133),out=ty(sc.el,'方法，留下来',152,699,83,B);
  sc.update=t=>{
   tag(t);const sm=q(t,89.966,90.8);cam(person,t,lerp(1667,1733,sm),lerp(505,246,sm),lerp(358,250,sm),lerp(604,250,sm),sm);place(note);
   word(simpler,t,84.3,86.45,{kind:'hit',dist:45});
   const press=q(t,96.133,98.7),exit=q(t,99.3,99.4);cards.forEach((e,i)=>{const z=q(t,90.06+i*.36,90.75+i*.36);place(e,{x:146+i*288,y:365+65*(1-z)+195*press,s:1-.29*press,o:live(t,90.06+i*.36,98.9),r:(i-1.5)*2*(1-z)});});
   place(sink,{x:147,y:533-110*press,sy:.62+.38*press,o:live(t,94.466,101.666)});
   word(skill,t,99.4,101.666,{kind:'hit'});word(out,t,98.5,101.666,{dist:30});
   // Masked whole-word press closes above the real recipe cards, then retreats.
   const compact=q(t,89.45,90.4);word(distill,t,86.533,99.22,{kind:'hit',x:146,y:lerp(350,173,compact),s:lerp(1,.59,compact)});
  };
  cues([[84.3,'whoosh',.35],[86.533,'hit',.6],[87.933,'tick',.24],[90.06,'card',.34,-.5],[90.42,'card',.34],[90.78,'card',.34,.5],[91.14,'card',.34],[94.466,'whoosh',.38],[96.133,'hit',.35],[99.4,'ding',.39]]);
 }
})();
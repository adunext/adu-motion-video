(() => {

const W='#F7F7F5', K='#0A0A0A', B='#2462EA', F="-apple-system,'PingFang SC',sans-serif";
const q=(t,a,b)=>MOTION.at(t,a,b), v=(t,a,b,d=.2)=>pr(t,a,a+d)*(1-pr(t,b-d,b));
const text=(p,s,x,y,n=72,c=K,w=650,width=0)=>mk(p,`<div style="font:${w} ${n}px/1.13 ${F};letter-spacing:-1.5px;color:${c};${width?'width:'+width+'px;white-space:normal;':''}">${s}</div>`,x,y);
const rect=(p,x,y,w,h,c,r=0)=>mk(p,`<div style="width:${w}px;height:${h}px;background:${c};border-radius:${r}px;overflow:hidden;position:relative"></div>`,x,y);
const line=(p,x,y,w,c=K)=>rect(p,x,y,w,2,c);
const cap=(e,t,a,b=999,d=.46)=>{const z=q(t,a,a+d),o=v(t,a,b,.18);place(e,{o,y:e._y+34*(1-z)-18*q(t,b-.2,b)});e.style.clipPath=`inset(${(1-z)*100}% 0 0 0)`;};
const rule=(e,t,a,b=999)=>place(e,{sx:q(t,a,a+.7),o:v(t,a,b,.15)});
const human=(p,w=600,h=696)=>{const c=camCard(p,w,h,'// on air · 阿杜Next');c.firstChild.style.borderRadius='6px';c.firstChild.style.boxShadow='none';return c;};
const face=(c,t,x,y,w,h,sm=.1,o=1,r=6)=>{c.firstChild.style.width=w+'px';c.firstChild.style.height=h+'px';c.firstChild.style.borderRadius=r+'px';c._sm=sm;c.querySelector('.lab').style.opacity=1-sm;camAt(c,t,{x,y,o});};
const folio=(s,no,title,dark=false)=>{const col=dark?'#b8b8b8':'#747474';const tag=text(s.el,`阿杜Next　／　${title}`,96,52,25,col,500);const num=text(s.el,`${no}　/　10`,1819,51,25,col,500);num._ax=1;const r=line(s.el,96,107,1728,dark?'#444':'#c8c8c4');return t=>{place(tag);place(num);place(r,{sx:q(t,s.s-.1,s.s+.6)});};};
const note=(p,s,x,y,c='#777')=>text(p,s,x,y,28,c,450);
const cue=arr=>arr.forEach(x=>S(...x));
const win=(p,w,h,title)=>{const e=macWin(p,w,h,title);e.firstChild.style.borderRadius='6px';e.firstChild.style.boxShadow='none';e.querySelector('.tb').style.fontSize='23px';e.querySelectorAll('.tb i').forEach(i=>i.style.background='#888');e._img.style.objectFit='contain';return e;};
const seq=(e,dir,n,fps,t,start)=>setFrame(e._img,seqAt(dir,n,fps,t,start,false));
(()=>{
  const s=new Scene(84.3,101.666,W,{trans:'wipe',td:.4,tc:W}),f=folio(s,'06','观察与类比'),c=human(s.el,612,700);
  const seam=line(s.el,767,144,2,'#bcbcb8');seam.firstChild.style.height='680px';
  const lead=text(s.el,'实现逻辑',817,170,94),word=text(s.el,'蒸馏',816,337,185,B,780),claim=note(s.el,'个人观察 · 方法类比',822,779),h=text(s.el,'拆开看，留下方法',815,172,84);
  const labels=['排版','动作','声音'];const panels=labels.map((name,i)=>{const e=rect(s.el,814,313+i*148,986,122,i===1?K:B);const label=text(e.firstChild,`0${i+1}　${name}`,24,34,48,'#fff');return{e,label};});
  const type=text(panels[0].e.firstChild,'标题',499,30,58,'#fff',780),typeLine=line(panels[0].e.firstChild,505,98,355,'#fff');
  const motion=mk(panels[1].e.firstChild,'<svg width="420" height="106"><path d="M12 75C110 -5 260 115 396 35" fill="none" stroke="#91b4ff" stroke-width="3" pathLength="1" stroke-dasharray="1"/><circle r="12" cx="12" cy="75" fill="white"/></svg>',498,7);
  const waves=Array.from({length:15},(_,i)=>rect(panels[2].e.firstChild,510+i*22,24,9,71,'#fff',4));
  const finalTitle=text(s.el,'编成一页，反复使用',816,174,80),page=rect(s.el,841,323,903,421,B),pHead=text(page.firstChild,'SKILL.md',37,35,47,'#bed2ff'),pBody=text(page.firstChild,'规则 · 配方 · 工具',37,133,63,'#fff',700),pFoot=text(page.firstChild,'从观察，到可复用的制作步骤',39,299,35,'#dce7ff');
  s.update=t=>{f(t);face(c,t,402,484,612,700,.08);place(seam);place(claim);cap(lead,t,84.43,89.81);const z=EZ.out5(pr(t,86.533,86.87));place(word,{o:v(t,86.533,89.81),s:1+.19*(1-z),y:337-30*(1-z)});cap(h,t,89.966,96.82);cap(finalTitle,t,97.0,101.666);
   panels.forEach(({e,label},i)=>{const a=90.15+i*.75,fold=q(t,94.8+i*.42,96.9+i*.42);place(e,{x:814+24*fold,y:313+i*148-30*fold,sx:1-.03*fold,sy:1-.82*fold,o:pr(t,a,a+.22)*(1-fold),r:-1.5*Math.sin(fold*Math.PI)});place(label);});
   place(type,{y:30+28*(1-q(t,90.35,90.88))});rule(typeLine,t,90.72,99);place(motion);motion.querySelector('path').style.strokeDashoffset=1-q(t,91.12,92.86);const mp=q(t,91.3,93.16),xy=MOTION.bezier([12,75],[110,-5],[260,115],[396,35],mp);motion.querySelector('circle').setAttribute('cx',xy[0]);motion.querySelector('circle').setAttribute('cy',xy[1]);waves.forEach((w,i)=>place(w,{sy:.3+.7*Math.abs(Math.sin((t-92.3)*4+i*.58)),y:24}));
   const pe=q(t,97.25,98.3);place(page,{x:841,y:323+110*(1-pe),o:pr(t,97.25,97.45),sy:.4+.6*pe});cap(pHead,t,98.5,101.666);cap(pBody,t,99.05,101.666);cap(pFoot,t,99.4,101.666);
  };
  cue([[84.3,'whoosh',.35],[86.533,'hit',.5],[89.966,'card',.3],[91,'tick',.2],[91.8,'tick',.2],[94.8,'whoosh',.3],[95.64,'whoosh',.2],[97.25,'card',.35],[99.4,'ding',.3]]);
 })();
})();
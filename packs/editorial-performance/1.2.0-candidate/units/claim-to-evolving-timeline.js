(() => {

const W='#F7F7F5', K='#0A0A0A', B='#2462EA', F="-apple-system,'PingFang SC',sans-serif";
const q=(t,a,b)=>MOTION.at(t,a,b), v=(t,a,b,d=.2)=>pr(t,a,a+d)*(1-pr(t,b-d,b));
const text=(p,s,x,y,n=72,c=K,w=650,width=0)=>mk(p,`<div style="font:${w} ${n}px/1.13 ${F};letter-spacing:-1.5px;color:${c};${width?'width:'+width+'px;white-space:normal;':''}">${s}</div>`,x,y);
const rect=(p,x,y,w,h,c,r=0)=>mk(p,`<div style="width:${w}px;height:${h}px;background:${c};border-radius:${r}px;overflow:hidden;position:relative"></div>`,x,y);
const line=(p,x,y,w,c=K)=>rect(p,x,y,w,2,c);
const cap=(e,t,a,b=999,d=.46)=>{const z=q(t,a,a+d),o=v(t,a,b,.18);place(e,{o,y:e._y+34*(1-z)-18*q(t,b-.2,b)});e.style.clipPath=`inset(${(1-z)*100}% 0 0 0)`;};
const rule=(e,t,a,b=999)=>place(e,{sx:q(t,a,a+.7),o:v(t,a,b,.15)});
const human=(p,w=600,h=696)=>{const c=camCard(p,w,h,'// on air · 本期品牌');c.firstChild.style.borderRadius='6px';c.firstChild.style.boxShadow='none';return c;};
const face=(c,t,x,y,w,h,sm=.1,o=1,r=6)=>{c.firstChild.style.width=w+'px';c.firstChild.style.height=h+'px';c.firstChild.style.borderRadius=r+'px';c._sm=sm;c.querySelector('.lab').style.opacity=1-sm;camAt(c,t,{x,y,o});};
const folio=(s,no,title,dark=false)=>{const col=dark?'#b8b8b8':'#747474';const tag=text(s.el,`本期品牌　／　${title}`,96,52,25,col,500);const num=text(s.el,`${no}　/　10`,1819,51,25,col,500);num._ax=1;const r=line(s.el,96,107,1728,dark?'#444':'#c8c8c4');return t=>{place(tag);place(num);place(r,{sx:q(t,s.s-.1,s.s+.6)});};};
const note=(p,s,x,y,c='#777')=>text(p,s,x,y,28,c,450);
const cue=arr=>arr.forEach(x=>S(...x));
const win=(p,w,h,title)=>{const e=macWin(p,w,h,title);e.firstChild.style.borderRadius='6px';e.firstChild.style.boxShadow='none';e.querySelector('.tb').style.fontSize='23px';e.querySelectorAll('.tb i').forEach(i=>i.style.background='#888');e._img.style.objectFit='contain';return e;};
const seq=(e,dir,n,fps,t,start)=>setFrame(e._img,seqAt(dir,n,fps,t,start,false));
(()=>{
  const s=new Scene(48.233,68.6,W),f=folio(s,'04','优势会变化'),c=human(s.el,500,690);
  const headline=text(s.el,'技术领先',96,163,118),permanent=text(s.el,'永久胜利？',96,351,118,B),slash=line(s.el,90,436,859,K),n=note(s.el,'观点示意 · 非模型排名或性能实测',101,807);
  const h2=text(s.el,'竞争，按天推进',97,161,100),h3=text(s.el,'差距，也会变化',97,161,100),h4=text(s.el,'竞争还在继续',97,161,100,B);
  const labels=['阶段一','阶段二','阶段三'],cols=labels.map((x,i)=>{const e=rect(s.el,101+i*395,363,358,345,i===2?B:K);const a=text(e.firstChild,`0${i+1}`,24,24,37,i===2?'#d0dfff':'#aaa',450);const b=text(e.firstChild,x,24,89,55,'#fff');const l=[0,1,2,3].map(j=>rect(e.firstChild,25,186+j*27,305,9,'#fff'));return{e,a,b,l};});
  const capLine=line(s.el,98,340,1159,B),small=note(s.el,'阶段性上限',985,295,B),endRule=line(s.el,97,767,1158,B);
  s.update=t=>{f(t);face(c,t,1554,479,500,690,.12);place(n);cap(headline,t,48.33,54.34);cap(permanent,t,51.7,54.34);place(slash,{o:v(t,53,54.34),sx:q(t,53,53.8),r:-5});cap(h2,t,54.5,61.37);cap(h3,t,61.566,65.34);cap(h4,t,65.54,68.6);
   cols.forEach(({e,a,b,l},i)=>{const st=54.8+i*.42,limit=q(t,61.56,64.3);place(e,{x:101+i*395,y:363+76*(1-q(t,st,st+.8))-24*limit,s:1,o:pr(t,st,st+.2)});place(a);place(b);l.forEach((x,j)=>place(x,{sx:(.24+.17*j+.20*q(t,st+.5,st+3.1))*(i===2?.5+.5*q(t,58.03,61.35):1),o:.3+.16*j}));});
   rule(capLine,t,61.566,65.35);cap(small,t,63.5,65.35);rule(endRule,t,65.54,68.6);
  };
  cue([[48.33,'card',.3],[51.7,'hit',.35],[53,'whoosh',.25],[54.5,'whoosh',.35],[55.22,'tick',.2],[55.64,'tick',.2],[58.03,'ding',.3],[61.566,'tick',.25],[65.54,'ding',.3]]);
 })();
})();
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
  const s=new Scene(101.666,118.2,B,{trans:'wipe',td:.4,tc:B}),f=folio(s,'07','提示词体验',true),c=human(s.el,566,698);
  const title=text(s.el,'删繁，留下目标',772,151,88,'#fff'),paper=rect(s.el,772,286,1051,481,W),noteE=note(s.el,'个人体验示意 · 不是通用效果保证',773,812,'#d4e1ff');
  const longLines=['画面这样排，镜头那样切。','这里突出，那里也突出。','再加动效，再换一种节奏。','再叠一些指令和更多要求。'].map((x,i)=>text(paper.firstChild,x,34,33+i*102,43));
  const marks=longLines.map((_,i)=>line(paper.firstChild,31,65+i*102,900,B));
  const goal=text(paper.firstChild,'根据这段口播，<br>制作配套动画视频。',35,136,66,B,700),goalN=note(paper.firstChild,'一句清楚的目标',39,45);
  const planTitle=text(s.el,'把表达，排成计划',771,151,88,'#fff'),labels=['开场','说明','演示','收尾'];
  const rows=labels.map((x,i)=>{const e=rect(s.el,774,308+i*114,1042,89,W);const label=text(e.firstChild,`0${i+1}`,22,22,36,'#888',450),body=text(e.firstChild,x,141,14,53),lineE=line(e.firstChild,302,46,669,'#b7b7b4');return{e,label,body,lineE};});
  const disrupt=['再叠 Skill','再加指令','再换节奏'].map((x,i)=>{const e=rect(s.el,1457,324+i*129,352,78,K);const t=text(e.firstChild,x,23,20,34,'#fff');return{e,t};});
  const result=text(s.el,'原来的编排，被打断',794,790,40,'#fff',600);
  s.update=t=>{f(t);face(c,t,379,483,566,698,.09);place(noteE);cap(title,t,101.76,108.08);place(paper,{o:v(t,102.1,108.16),sx:q(t,102.1,102.78)});
   longLines.forEach((x,i)=>{cap(x,t,102.35+i*.24,105.88);place(marks[i],{sx:q(t,104.14+i*.2,104.75+i*.2),o:v(t,104.14+i*.2,105.94)});});cap(goalN,t,106.1,108.16);cap(goal,t,106.22,108.16);
   cap(planTitle,t,108.28,118.2);rows.forEach(({e,label,body,lineE},i)=>{const a=108.72+i*.28,dis=q(t,112.566,116.65),dy=[0,-14,14,4][i],dx=[0,-20,36,-4][i];place(e,{x:774+dx*dis,y:308+i*114+45*(1-q(t,a,a+.64))+dy*dis,o:pr(t,a,a+.2),r:dis*[0,-1.1,.8,-.8][i]});place(label);place(body);place(lineE,{sx:q(t,a+.4,a+1.65)});});
   disrupt.forEach(({e,t:tx},i)=>{const a=[112.566,114.566,115.733][i],z=q(t,a,a+.55);place(e,{x:1457+77*(1-z),y:324+i*129-85*(1-z),o:pr(t,a,a+.18),r:2*(1-z)});place(tx);});cap(result,t,116.55,118.2,.28);noteE.style.opacity=t>108.16?'0':'1';
  };
  cue([[101.666,'whoosh',.35],[102.1,'card',.3],[104.14,'tick',.25],[105.966,'whoosh',.3],[106.22,'ding',.25],[108.72,'card',.3],[109.28,'tick',.2],[112.566,'card',.3],[114.566,'card',.3],[115.733,'card',.3],[116.55,'hit',.3]]);
 })();
})();
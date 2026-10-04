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
  const s=new Scene(15.466,33.066,K,{trans:'wipe',td:.45,tc:K}),f=folio(s,'02','个人经历',true),c=human(s.el,610,698);
  const heading=text(s.el,'上一条，<br>夸上天。',96,170,122,'#fff',750),model=note(s.el,'本期工具',101,509,'#91b4ff');
  const prev=win(s.el,850,230,'上期成片 · 回顾'),prevN=note(s.el,'创作能力，值得认真研究',100,805,'#aaa');
  const wallWrap=rect(s.el,0,0,1920,1080,K),wall=buildWall(wallWrap.firstChild,27,128,72,6);
  const wallTag=rect(s.el,85,142,490,109,K),wallH=text(s.el,'全新的阶段',107,162,62,'#fff');
  const wallNote=note(s.el,'网络优秀作品收集 · 非个人原创',96,814,'#fff');
  const white=rect(s.el,88,147,1059,670,W),diary=note(s.el,'个人叙述 · 图形演绎',119,183),done=text(s.el,'刚剪完视频',121,263,94),seal=text(s.el,'账号被封',121,402,114,B,760),money=text(s.el,'本期费用',125,571,142,K,750),again=note(s.el,'而且，不是第一次。',516,675,B);
  s.update=t=>{f(t);const wo=v(t,19.866,25.94,.16);face(c,t,1506,483,610,698,.1,1-wo);cap(heading,t,15.55,19.72);cap(model,t,17.5,19.72);cap(prevN,t,18.85,19.72);
   place(prev,{x:523,y:677,o:v(t,17.83,19.72)});if(t<19.86)seq(prev,'prev',240,30,t,17.83);
   place(wallWrap,{o:t>=19.866?1-pr(t,25.6,25.95):0});if(t>=19.866&&t<25.96){wallTick(wall,t,19.866,8);place(wall,{x:960+23*q(t,20,25.6),y:540,s:1.045-.035*q(t,20,24.8)});}
   place(wallTag,{o:v(t,22.2,25.6)});cap(wallH,t,22.26,25.6);cap(wallNote,t,20.35,25.6);
   place(white,{o:pr(t,25.76,26.02),sx:q(t,25.65,26.4)});cap(diary,t,25.98,33.066);cap(done,t,26.1,33.066);cap(seal,t,26.933,33.066,.27);cap(money,t,28.5,33.066,.5);cap(again,t,30.733,33.066);
  };
  cue([[15.466,'whoosh',.4],[17.83,'card',.35],[19.866,'whoosh',.5],[22.266,'ding',.3],[25.7,'card',.4],[26.933,'hit',.6],[28.5,'hit',.4],[30.733,'tick',.3]]);
 })();
})();
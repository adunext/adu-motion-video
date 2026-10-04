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
  const s=new Scene(149.4,9794/60,B,{trans:'wipe',td:.4,tc:B}),f=folio(s,'10','一起建设',true),c=human(s.el,590,698);
  const paper=rect(s.el,96,145,1092,654,W),h=text(paper.firstChild,'Skill 与模板库',35,38,76,K,700),name=note(paper.firstChild,'项目主页',39,159),repo=text(paper.firstChild,(CONFIG.repoUrl||'本期项目链接').replace('https://','').replace('github.com/','github.com/<br>'),35,219,57,B,650),under=line(paper.firstChild,37,384,1014,B);
  const flow=['上传模板','整理说明','共享方法'].map((x,i)=>{const n=text(paper.firstChild,x,39+i*344,524,39,K,600),r=line(paper.firstChild,38+i*344,586,275,B),d=rect(paper.firstChild,39+i*344,473,15,15,B);return{n,r,d};});
  const invite=note(paper.firstChild,'欢迎把你生成的模板留下来',39,438,B),label=text(s.el,'创作者',111,194,42,'#d0deff'),brand=text(s.el,'本期品牌',101,321,146,'#fff',750),bye=text(s.el,'谢谢观看，拜拜',106,562,68,'#fff');
  s.update=t=>{f(t);const close=q(t,160.2,160.85);face(c,t,lerp(1515,1460,close),483,lerp(590,680,close),698,.1);place(paper,{x:96-95*close,o:1-close,sx:1-.18*close});cap(h,t,149.57,160.15);cap(name,t,150.2,160.15);cap(repo,t,150.5,160.15);rule(under,t,151.73,160.15);cap(invite,t,152.933,160.15);
   flow.forEach(({n,r,d},i)=>{const a=153.2+i*1.3;cap(n,t,a,160.15);rule(r,t,a+.2,160.15);place(d,{x:d._x+259*q(t,a,a+1.1),o:v(t,a,a+1.22)});});cap(label,t,160.433,9794/60);cap(brand,t,160.65,9794/60);cap(bye,t,161.8,9794/60);
  };
  cue([[149.4,'whoosh',.4],[150.5,'card',.3],[151.73,'ding',.3],[153.2,'tick',.25],[154.5,'tick',.25],[155.8,'tick',.25],[160.433,'whoosh',.3],[161.8,'ding',.3]]);
 })();
})();
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
  const s=new Scene(118.2,142.4,K,{trans:'wipe',td:.4,tc:K}),f=folio(s,'08','打开制作过程',true),c=human(s.el,588,698);
  const intro=text(s.el,'从成片，<br>读懂方法。',96,173,118,'#fff'),sub=note(s.el,'从可以查看的本地工程开始',103,548,'#aaa'),folder=rect(s.el,102,626,892,152,B),folderT=text(folder.firstChild,'Animation　／　工程文件夹',25,47,45,'#fff');
  const h=text(s.el,'真实工程，就是说明书',96,141,70,'#fff'),w=win(s.el,1212,499,'原项目录屏 · Animation 工程'),lab=note(s.el,'真实工程录屏 · 编辑放大',102,809,'#aaa');
  const n1=text(s.el,'制作过程',1401,441,55,'#fff'),n2=text(s.el,'可见结果',1401,589,55,'#fff'),nr=[line(s.el,1403,522,402,B),line(s.el,1403,670,402,B)];
  const packageH=text(s.el,'把方法，编成手册',96,141,82,'#fff'),method=rect(s.el,102,299,1232,444,W),mLabel=text(method.firstChild,'SKILL.md',28,28,40,B),mTitle=text(method.firstChild,'规则　／　配方　／　工具',29,115,60,K,700);
  const items=['场景代码','声音方法','媒体规则'].map((x,i)=>{const el=rect(s.el,1299,425+i*123,492,90,B),tx=text(el.firstChild,x,22,23,42,'#fff');return{el,tx};});
  const apps=text(method.firstChild,'Codex　／　豆包　／　其它助手',29,252,49,B),end=text(s.el,'少重复描述，多复用。',103,781,48,'#a6c3ff');
  s.update=t=>{f(t);const shrink=q(t,121.15,121.98);face(c,t,lerp(1512,1687,shrink),lerp(483,267,shrink),lerp(588,232,shrink),lerp(698,232,shrink),lerp(.08,1,shrink),1,lerp(6,116,shrink));cap(intro,t,118.32,121.3);cap(sub,t,119.1,121.3);place(folder,{o:v(t,120.08,121.3),sx:q(t,120.08,120.65)});place(folderT);
   cap(h,t,121.45,135.33);const fold=q(t,134.8,136.1);place(w,{x:708-130*fold,y:515,o:v(t,122,136.1),sx:1-.25*fold});if(t>=122&&t<136.1){seq(w,t<126.7?'folder_intro':'folder_code',t<126.7?150:360,30,t,t<126.7?122:126.7);w._img.style.objectFit=t<126.7?'contain':'cover';w._img.style.objectPosition='55% 35%';w._img.style.transform=`scale(${1+.18*q(t,128.3,131)*(1-fold)})`;w._img.style.transformOrigin='55% 38%';}
   place(lab,{o:v(t,122.2,135.5)});cap(n1,t,129.05,134.22);cap(n2,t,130.55,134.22);nr.forEach((r,i)=>rule(r,t,129.4+i*1.5,134.22));cap(packageH,t,135.5,142.4);
   place(method,{o:pr(t,136.24,136.48),sx:q(t,136.2,137.0)});cap(mLabel,t,136.65,142.4);cap(mTitle,t,138.03,142.4);cap(apps,t,138.64,142.4);cap(end,t,140.43,142.4);
   items.forEach(({el,tx},i)=>{const a=134.4+i*.42,m=q(t,a+.9,a+2.7);place(el,{x:1299-350*m,y:425+i*123-105*m,s:1-.36*m,o:pr(t,a,a+.15)*(1-pr(t,a+2.3,a+2.7))});place(tx);});
  };
  cue([[118.2,'whoosh',.35],[120.08,'card',.3],[122,'card',.4],[126.7,'click',.3],[129.05,'tick',.25],[130.55,'tick',.25],[134.4,'whoosh',.3],[135.24,'whoosh',.25],[136.2,'card',.35],[138.64,'ding',.3],[140.43,'ding',.25]]);
 })();
})();
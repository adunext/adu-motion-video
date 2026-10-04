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
  const s=new Scene(68.6,84.3,K,{trans:'wipe',tc:K,td:.42}),f=folio(s,'05','从开发者视角',true),c=human(s.el,420,640);
  const header=text(s.el,'创作能力，毋庸置疑',96,139,70,'#fff'),w=win(s.el,1212,510,'真实素材 · 本期工具软件演示'),foot=note(s.el,'真实软件录屏 · 原速',99,809,'#aaa');
  const noteNames=['画面排版','动效路径','声音节拍'];const aside=noteNames.map((x,i)=>({n:text(s.el,x,1408,424+i*127,47,'#fff'),r:line(s.el,1410,492+i*127,396,B)}));
  const proof=text(s.el,'细节，会改变观感',139,416,107,'#fff'),proof2=note(s.el,'排版　／　动效　／　动画　／　音效',145,587,'#a9c6ff');
  s.update=t=>{f(t);const small=q(t,77.84,78.52);face(c,t,lerp(1594,1678,small),lerp(487,267,small),lerp(420,232,small),lerp(640,232,small),lerp(.08,1,small),1,lerp(6,116,small));cap(header,t,68.68,83.02);
   const exit=q(t,82.65,83.15);place(w,{x:708-83*exit,y:510,o:v(t,69.2,83.16),sx:1-.14*exit});
   if(t>=69.2&&t<83.16){if(t<72.2){seq(w,'soft_match',90,30,t,69.2);w.querySelector('.tb span').textContent='真实软件录屏 · 本期软件';foot.firstChild.textContent='真实软件录屏 · 原速';}else if(t<74.966){seq(w,'soft_tpl',360,72,t,72.2);w.querySelector('.tb span').textContent='真实软件录屏 · 模板选择';foot.firstChild.textContent='真实软件录屏 · ▶▶ 2.4×';}else{seq(w,'prev',240,30,t,74.966);w.querySelector('.tb span').textContent='上期成片 · 细节观察';foot.firstChild.textContent='原成片回顾 · 非本次软件操作';}}
   place(foot,{o:v(t,69.2,83.03)});aside.forEach(({n,r},i)=>{cap(n,t,78.42+i*.74,83.06);rule(r,t,78.69+i*.74,83.06);});cap(proof,t,83.05,84.3,.35);cap(proof2,t,83.22,84.3,.3);
  };
  cue([[68.6,'whoosh',.4],[69.2,'card',.3],[72.2,'click',.25],[74.966,'card',.4],[78.42,'tick',.25],[79.16,'tick',.25],[79.9,'tick',.25],[83.05,'ding',.3]]);
 })();
})();
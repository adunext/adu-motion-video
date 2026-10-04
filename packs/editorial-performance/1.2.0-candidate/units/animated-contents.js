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
  const s=new Scene(142.4,149.4,W,{trans:'wipe',td:.4,tc:W}),f=folio(s,'09','模板目录'),c=human(s.el,572,698);
  const head=text(s.el,'把好方法，留下来',762,151,85),small=note(s.el,'模板分类示意 · 每一格都可以继续扩写',764,267);
  const labels=['开场标题','人物构图','软件演示','镜头转场','配乐音效','收尾署名'];const tiles=labels.map((label,i)=>{const e=rect(s.el,761+(i%2)*541,329+Math.floor(i/2)*164,518,146,i===4?B:K),n=text(e.firstChild,label,225,54,36,'#fff',600),ln=line(e.firstChild,220,113,269,'#777');return{e,n,ln};});
  const type=text(tiles[0].e.firstChild,'大字',18,43,68,'#fff',800),camMini=human(tiles[1].e.firstChild,157,119),soft=win(tiles[2].e.firstChild,188,106,'回顾');soft.querySelector('.tb').style.height='15px';soft.querySelector('.tb').style.fontSize='8px';
  const page1=rect(tiles[3].e.firstChild,14,20,178,106,'#fff'),page2=rect(tiles[3].e.firstChild,14,20,178,106,B);const wave=Array.from({length:8},(_,i)=>rect(tiles[4].e.firstChild,21+i*22,34,10,78,'#fff',3)),brand=text(tiles[5].e.firstChild,'品牌',18,25,45,'#fff',750);
  s.update=t=>{f(t);face(c,t,382,483,572,698,.08);cap(head,t,142.52,149.4);cap(small,t,142.95,149.4);tiles.forEach(({e,n,ln},i)=>{const a=143.25+i*.4,z=q(t,a,a+.58);place(e,{x:e._x+54*(1-z),y:e._y,o:pr(t,a,a+.18)});place(n);place(ln,{sx:q(t,a+.2,a+.85)});});
   const z=EZ.out5(pr(t,143.45,143.9));place(type,{s:1+.35*(1-z),y:43-28*(1-z)});face(camMini,t,101,73,157,119,.7,1,lerp(4,55,q(t,144,145.6)));camMini.querySelector('.lab').style.opacity='0';place(soft,{x:106,y:74,o:1});if(t>=144.05)seq(soft,'prev',240,30,t,144.05);place(page1);place(page2,{sx:q(t,144.9,146.0)});wave.forEach((e,i)=>place(e,{sy:.27+.73*Math.abs(Math.sin((t-145)*4+i*.65))}));place(brand,{y:25+15*(1-q(t,145.5,146.1))});
  };
  cue([[142.4,'whoosh',.35],[143.25,'card',.25],[144.05,'card',.25],[144.85,'card',.25],[145.65,'card',.25],[147.9,'ding',.3]]);
 })();
})();
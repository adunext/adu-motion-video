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
  const s=new Scene(33.066,48.233,W,{trans:'wipe',tc:W,td:.4}),f=folio(s,'03','一个比方'),c=human(s.el,580,698);
  const gutter=line(s.el,742,149,2,'#bcbcb8');gutter.firstChild.style.height='676px';
  const h1=text(s.el,'帮甲方，打广告',802,173,90),h2=text(s.el,'钱包，也被拿走',802,173,87),h3=text(s.el,'技术与体验',802,173,91);
  const ad=rect(s.el,820,358,366,307,B),adText=text(ad.firstChild,'广告',35,54,107,'#fff',700),adLines=[0,1,2].map(i=>line(ad.firstChild,35,216+i*20,295,'#9bb9ff'));
  const receiver=rect(s.el,1375,390,388,250,K),recT=text(receiver.firstChild,'甲方',34,75,99,'#fff',700);
  const path=mk(s.el,'<svg width="650" height="120"><path d="M0 100Q320 -30 620 100" fill="none" stroke="#2462EA" stroke-width="3" pathLength="1" stroke-dasharray="1"/></svg>',1075,301);
  const wallet=mk(s.el,`<svg width="352" height="249" viewBox="0 0 352 249"><rect x="4" y="31" width="328" height="202" rx="16" fill="${K}"/><path d="M17 31L280 6V31" fill="${B}"/><rect x="261" y="90" width="86" height="85" rx="10" fill="${B}"/><circle cx="290" cy="132" r="8" fill="white"/><text x="30" y="152" font-family="PingFang SC" font-size="43" fill="white">我的钱包</text></svg>`,0,0,{ax:.5,ay:.5});
  const hit=text(s.el,'啪',1053,335,223,B,780),tech=text(s.el,'技术很强',804,359,118),feel=text(s.el,'体验很痛',804,574,118,B),divider=line(s.el,807,524,932),n=note(s.el,'比喻示意 · 个人使用感受',803,808);
  s.update=t=>{f(t);face(c,t,386,483,580,698,.08);place(gutter);place(n);cap(h1,t,33.9,38.03);cap(h2,t,38.18,40.95);cap(h3,t,41.17,48.233);
   const tr=q(t,35.2,37.4),ex=pr(t,37.8,38.1);place(ad,{x:820+490*tr,y:358-68*Math.sin(tr*Math.PI),s:1-.37*tr,o:v(t,34.82,38.1),r:-4*Math.sin(tr*Math.PI)});place(adText);adLines.forEach((x,i)=>place(x,{sx:q(t,35+i*.12,35.5+i*.12)}));
   place(receiver,{o:v(t,36.4,41),sx:q(t,36.4,37.05)});place(recT);place(path,{o:v(t,35.2,38.05)});path.querySelector('path').style.strokeDashoffset=1-q(t,35.2,36.5);
   const wp=q(t,38.48,39.62);place(wallet,{x:lerp(990,1562,wp),y:555-125*Math.sin(wp*Math.PI),r:8*Math.sin(wp*Math.PI),s:1-.18*wp,o:v(t,38.17,41.03)});
   const hp=EZ.out5(pr(t,39.8,40.08));place(hit,{o:v(t,39.8,40.99),s:1+.38*(1-hp),y:335-47*(1-hp)});
   cap(tech,t,41.2,48.233);rule(divider,t,43.44,48.233);cap(feel,t,44.97,48.233,.35);
  };
  cue([[33.9,'whoosh',.3],[34.82,'card',.3],[35.4,'whoosh',.25],[36.4,'tick',.25],[38.18,'card',.3],[38.5,'whoosh',.35],[39.8,'hit',.6],[41.2,'whoosh',.3],[44.97,'hit',.35]]);
 })();
})();
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
  const s=new Scene(0,15.466,W),f=folio(s,'01','公开方法'),c=human(s.el,660,700);
  const seam=line(s.el,798,147,2,'#bcbcb8');seam.firstChild.style.height='676px';
  const cover=text(s.el,'公开蒸馏<br><span style="color:#2462EA">剪辑能力</span>',856,198,118,K,780);
  const coverN=note(s.el,'从一支成片，到一套制作方法',860,555),coverRule=line(s.el,860,622,916,B);
  const issue=text(s.el,'方法索引',860,169,89),skill=text(s.el,'adu-motion-video',862,287,59,B,700);
  const rows=['01　场景与动画','02　声音与节奏','03　导出与复用'].map((x,i)=>text(s.el,x,864,399+i*119,49,K,600));
  const bars=rows.map((_,i)=>line(s.el,861,474+i*119,915,'#bbb'));
  const apps=note(s.el,'Codex　／　豆包　／　更多助手',861,756,B);
  const proofBand=rect(s.el,833,319,974,278,B),proof=text(s.el,'这条视频\n就在使用它'.replace('\n','<br>'),870,350,87,'#fff',700);
  const proofN=note(s.el,'把方法，落实到这支成片',863,700,B);
  const aside=rect(s.el,834,219,974,483,K),aLabel=note(s.el,'个人吐槽 · 不是平台通知',867,253,'#bcbcbc'),joke=text(s.el,'永久<br>黑名单？',870,340,110,'#fff',750),resolve=text(s.el,'方法，照样公开。',868,753,51,B);
  s.update=t=>{f(t);face(c,t,430,483,660,700,.08);place(seam,{o:1});
   const slam=EZ.out5(pr(t,0,.35));place(cover,{o:1-pr(t,3.1,3.4),s:1+.13*(1-slam),y:198-20*(1-slam)});cap(coverN,t,1.56,3.35);rule(coverRule,t,2.15,3.35);
   cap(issue,t,3.5,8.45);cap(skill,t,4.45,8.45);rows.forEach((e,i)=>{cap(e,t,4.95+i*.32,8.45);rule(bars[i],t,5.05+i*.32,8.45);});cap(apps,t,6.2,8.45);
   const z=q(t,8.55,9.3);place(proofBand,{o:v(t,8.55,10.98),sx:z});cap(proof,t,8.78,10.98);cap(proofN,t,9.95,10.98);
   place(aside,{o:v(t,11.13,15.466),sx:q(t,11.1,11.8)});cap(aLabel,t,11.5,15.466);cap(joke,t,12.13,15.466,.36);cap(resolve,t,14.2,15.466,.3);
  };
  cue([[0,'hit',.6],[2.15,'tick',.2],[3.5,'whoosh',.35],[4.95,'card',.3],[6.2,'ding',.25],[8.55,'whoosh',.4],[11.13,'card',.4],[13.133,'hit',.45],[14.2,'ding',.25]]);
 })();
})();
(() => {

const P='#F7F7F5',B='#2462EA',K='#0A0A0A',L='#79a1ff',R='#E5484D';
const E=(t,a,b)=>MOTION.at(t,a,b),SP=(t,a,d=.65)=>EZ.spring(pr(t,a,a+d));
const V=(t,a,b,fade=.22)=>pr(t,a,a+fade)*(b==null?1:1-pr(t,b-fade,b));
const tx=(p,s,x,y,size=90,c=K,w=700)=>mk(p,`<div style="font-size:${size}px;line-height:1.14;font-weight:${w};letter-spacing:-1.6px;color:${c}">${s}</div>`,x,y);
const nt=(p,s,x,y,c='#808389',size=27)=>tx(p,s,x,y,size,c,450);
const pn=(p,html,x,y,w,h,dark=false)=>mk(p,`<div class="stage-panel ${dark?'dark':''}" style="width:${w}px;height:${h}px">${html}</div>`,x,y,{ax:.5,ay:.5});
const txtPanel=(p,k,s,f,x,y,w,h,dark=false)=>pn(p,`<div class="kicker">${k}</div><div class="main-label">${s}</div><div class="foot-label">${f}</div>`,x,y,w,h,dark);
function depth(e,o={}){place(e,o);e.style.transform+=` perspective(1600px) rotateY(${(o.ry||0).toFixed(3)}deg)`;e.style.zIndex=String(o.z||0);}
function reveal(e,t,a,b,dy=28,d=.48){const q=pr(t,a,a+d),out=b==null?0:pr(t,b-.22,b);place(e,{y:e._y+(1-EZ.out5(q))*dy-20*EZ.in(out),o:clamp(q*5)*(1-out),blur:(1-EZ.out5(q))*3+3*out});}
function head(sc,items,dark=false,size=94,x=146){const nodes=items.map(([s,a,b])=>({e:tx(sc.el,s,x,137,size,dark?'#fff':K),a,b}));return t=>nodes.forEach(({e,a,b})=>reveal(e,t,a,b));}
function stage(sc,label,dark=false){
 const tag=tags(sc,label,'',dark), floor=mk(sc.el,'<div class="stage-floor"><div class="stage-floor-lines"></div></div>',-190,786);
 const wing=mk(sc.el,`<div style="width:192px;height:666px;border:2px solid ${dark?'#252933':'#e0e2df'};border-radius:28px;background:${dark?'#101217':'rgba(255,255,255,.6)'}"></div>`,-102,130);
 const rail=mk(sc.el,`<div style="width:3px;height:582px;background:${dark?'#272c36':'#dfe1de'}"></div>`,1840,187);
 return(t,pan=0)=>{tag(t);place(floor,{x:-190-pan*.8,o:1});depth(wing,{x:-102-pan*.2,ry:13,o:1});place(rail,{x:1840-pan*.35,o:1});};
}
function camera(c,t,x,y,w,h,o=1,face=0,r=0){c.firstChild.style.width=w+'px';c.firstChild.style.height=h+'px';c.firstChild.style.borderRadius=(face?34:26)+'px';c._sm=face;camAt(c,t,{x,y,o,s:1,r});}
const cues=xs=>xs.forEach(x=>S(...x));
const line=(p,w,x,y,c=B)=>mk(p,`<div class="stage-line" style="width:${w}px;background:${c}"></div>`,x,y);
(()=>{
 const sc=new Scene(0,15.466,P), st=stage(sc,'// C01 — 方法登台');
 const c=camCard(sc.el,480,730),title=tx(sc.el,'公开蒸馏<br><span style="color:#2462EA">剪辑能力</span>',140,218,152);
 const titleLine=line(sc.el,795,148,589),intro=nt(sc.el,'把一支成片，变成可复用的方法',148,657);
 const h=head(sc,[['把方法，装进 Skill',4.24,8.50],['这条视频，就在用它',8.566,10.94]],false,92,640);
 const pack=txtPanel(sc.el,'可编辑工程 · 制作方法','adu-motion-video','场景　·　声音　·　导出',1100,460,1040,278);
 const models=['Codex','豆包','更多助手'].map((s,i)=>pn(sc.el,`<div style="padding-top:31px;text-align:center;font-size:40px;font-weight:650;color:${i===0?B:K}">${s}</div>`,735+i*348,710,315,106));
 const paths=mk(sc.el,'<svg width="1050" height="132"><path class="route" d="M520 0V48H173V132M520 48V132M520 48H870V132" pathLength="1" fill="none" stroke="#2462EA" stroke-width="3" stroke-dasharray="1"/></svg>',563,589);
 const seals=nt(sc.el,'✓ 本片正在使用',1240,549,B,31);seals.style.zIndex='6';
 const joke=txtPanel(sc.el,'个人吐槽 · 不是平台通知','发完这条之后……','但方法，照样公开',1110,491,1030,372,true);
 const stamp=tx(sc.el,'永久黑名单？',682,456,103,R,750);stamp.style.zIndex='8';
 sc.update=t=>{
  const p=E(t,3.4,4.18),pan=E(t,3.4,5.2)*52;st(t,pan);h(t);
  camera(c,t,lerp(1580+65*(1-SP(t,0,.75)),335,p),lerp(466,486,p),lerp(480,390,p),lerp(730,690,p));
  const out=E(t,3.15,3.48),slam=EZ.out5(pr(t,0,.37));place(title,{x:140,y:218-28*out,s:1+.075*(1-slam),o:1-out,blur:out*5});place(titleLine,{sx:EZ.expo(pr(t,1.1,1.7)),o:1-out});reveal(intro,t,2.033,3.35);
  const a=SP(t,4.40,.72),b=E(t,10.52,11.1);depth(pack,{x:1100,y:460+132*(1-a)-25*b,ry:-9*(1-a),s:.93+.07*a,o:V(t,4.4,11.1),z:2});
  models.forEach((e,i)=>{const q=SP(t,5.933+i*.34,.62),exit=E(t,10.4+i*.055,10.82+i*.055);depth(e,{x:e._x+30*(1-q),y:e._y+70*(1-q)+38*exit,ry:-7*(1-q),o:clamp((t-5.933-i*.34)*8)*(1-exit),s:.94+.06*q,z:3});});
  place(paths,{o:V(t,5.44,10.62)});paths.querySelector('.route').style.strokeDashoffset=1-E(t,5.44,6.68);
  reveal(seals,t,9.566,10.62,12,.35);
  const j=SP(t,11.1,.68);depth(joke,{x:1110,y:491+100*(1-j),ry:5*(1-j),o:pr(t,11.1,11.3),z:4});
  const q=pr(t,13.133,13.56);place(stamp,{y:456-130*(1-EZ.out5(q)),s:1+.38*(1-EZ.out5(q)),r:-5*(1-EZ.spring(q)),o:clamp(q*7),blur:6*(1-EZ.out5(q))});
 };
 cues([[0,'whoosh',.4],[.12,'hit',.58],[1.1,'tick',.28],[4.55,'card',.43],[5.933,'click',.28],[6.27,'click',.28],[6.61,'click',.3],[8.566,'hit',.4],[9.566,'ding',.3],[11.24,'card',.4],[13.22,'hit',.6]]);
})();
})();
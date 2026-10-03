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
 const sc=new Scene(68.6,84.3,K,{trans:'wipe',tc:K,td:.44}),st=stage(sc,'// C05 — 回到创作',true),c=camCard(sc.el,370,655);
 const h=head(sc,[['回到创作本身',68.61,74.90],['创作能力，确实出色',74.966,82.55],['细节，决定完成度',82.65,84.3]],true,82,620);
 const win=macWin(sc.el,1120,460,'阿杜导演 · AI 自动剪辑');
 const speed=nt(sc.el,'▶▶ 2.4×',1540,278,'#fff',29);speed.style.zIndex='9';
 const labels=['画面排版','动效动画','音效细节'].map((s,i)=>pn(sc.el,`<div style="text-align:center;padding:21px;font-size:33px;color:white">${s}</div>`,782+i*355,270,321,82,true));
 const underline=labels.map((e,i)=>{const l=line(sc.el,259,e._x-129,306,L);l.style.zIndex='7';return l;});
 const conclusion=tx(sc.el,'画面 · 运动 · 声音',711,479,87,'#fff');
 const replayNote=nt(sc.el,'上一集画面 · 创作效果回看',689,810,'#9aa2af',24);
 sc.update=t=>{
  st(t,22*E(t,78.13,80.5));h(t);camera(c,t,325,490,370,655);
  const q=SP(t,69.2,.75),turn=E(t,74.966,76.5);depth(win,{x:1170,y:554+85*(1-q),s:1-.028*turn,ry:-5*(1-q),o:pr(t,69.2,69.42)*(1-E(t,82.56,83.05)),z:2});
  if(t<72.2)setFrame(win._img,seqAt('soft_match',90,30,t,69.2,false));else if(t<74.966)setFrame(win._img,seqAt('soft_tpl',360,72,t,72.2,false));else if(t<83.05)setFrame(win._img,seqAt('prev',240,30,t,74.966,false));
  win.querySelector('.tb span').textContent=t<74.966?'阿杜导演 · AI 自动剪辑':'上一集画面 · 创作效果回看';place(speed,{o:V(t,72.2,74.94,.1)});place(replayNote,{o:V(t,74.966,82.98)});
  labels.forEach((e,i)=>{const at=[78.133,79.14,80.166][i],q=SP(t,at,.52);depth(e,{y:270+35*(1-q),s:.96+.04*q,o:pr(t,at,at+.18),z:5});place(underline[i],{sx:E(t,at+.2,at+.7),o:pr(t,at+.2,at+.35)});});
  reveal(conclusion,t,83.05,null,25,.42);
 };
 cues([[68.61,'whoosh',.35],[69.35,'card',.42],[72.2,'click',.28],[74.966,'whoosh',.37],[78.22,'card',.35],[79.22,'card',.35],[80.24,'card',.35],[82.75,'ding',.36]]);
})();
})();
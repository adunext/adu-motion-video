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
 const sc=new Scene(84.3,101.666,P,{trans:'wipe',tc:P,td:.42}),st=stage(sc,'// C06 — 拆开效果'),c=camCard(sc.el,392,700);
 const h=head(sc,[['实现逻辑，可以拆开',84.31,86.45],['从效果，提炼方法',89.966,98.02],['把方法，整理成 Skill',98.133,101.666]],false,89);
 const word=tx(sc.el,'蒸馏',295,336,223,B,800),shadow=tx(sc.el,'蒸馏',326,357,223,'#dce5fa',800);shadow.style.zIndex='0';word.style.zIndex='2';
 const opinion=nt(sc.el,'个人推断 · 从视觉效果出发的观察',150,803,'#82858d',25);
 const panels=['字效','排版','路径'].map((s,i)=>txtPanel(sc.el,'动作样例',s,'方法示意，不是模型内部证据',353+i*365,550,326,385));
 panels.forEach((p,i)=>{p.querySelector('.foot-label').style.fontSize='19px';});
 const glyph=tx(panels[0].firstChild,'动',180,175,93,B),grid=mk(panels[1].firstChild,'<div style="display:grid;grid-template-columns:repeat(2,80px);gap:10px">'+Array.from({length:4},(_,i)=>`<div class="tile" style="height:50px;background:${i===0?B:'#ccd8f1'};border-radius:7px"></div>`).join('')+'</div>',101,178);
 const path=mk(panels[2].firstChild,'<svg width="225" height="142"><path d="M8 113C87 113 65 15 137 21S150 115 215 32" stroke="#2462EA" stroke-width="6" fill="none" pathLength="1" stroke-dasharray="1"/></svg>',53,181);
 const archive=txtPanel(sc.el,'可复用的方法','剪辑手法 → Skill','归纳动作、参数、素材与声音',712,535,910,362);
 sc.update=t=>{
  st(t,30*E(t,94.466,98.1));h(t);camera(c,t,1536,482,392,700);
  const q=SP(t,86.533,.62),gone=E(t,89.48,89.95);place(shadow,{x:326,y:357+60*(1-q),o:pr(t,86.533,86.7)*(1-gone),s:.9+.1*q});place(word,{x:295,y:336+70*(1-q),o:pr(t,86.533,86.7)*(1-gone),s:.9+.1*q});place(opinion,{o:1});
  panels.forEach((e,i)=>{const a=90.1+i*.21,p=SP(t,a,.73),fold=E(t,95.7+i*.18,97.65+i*.14);depth(e,{x:lerp(e._x,713,fold),y:550+110*(1-p)-37*fold,s:1-.14*fold,ry:(i-1)*5+fold*(i-1)*8,o:pr(t,a,a+.22)*(1-E(t,97.42,98.03)),z:3-i});});
  place(glyph,{y:175+36*(1-SP(t,91.0,.64)),s:1+.07*(1-SP(t,91.0,.64)),o:pr(t,91,91.2)});place(grid,{o:1});grid.querySelectorAll('.tile').forEach((e,i)=>{const a=91.6+i*.17;e.style.transform=`translateY(${(28*(1-E(t,a,a+.5))).toFixed(2)}px)`;e.style.opacity=pr(t,a,a+.2);});place(path,{o:1});path.querySelector('path').style.strokeDashoffset=1-E(t,92.2,94.0);
  const a=SP(t,98.02,.72);depth(archive,{y:535+90*(1-a),ry:-5*(1-a),o:pr(t,98.02,98.24),z:5});
 };
 sc.cam=t=>({x:960-34*E(t,94.466,98.5),y:540,z:1});
 cues([[84.31,'whoosh',.38],[86.62,'hit',.57],[90.18,'card',.3],[90.39,'card',.3],[90.6,'card',.3],[91.1,'pop',.3],[92.2,'whoosh',.28],[95.7,'whoosh',.35],[98.18,'card',.43]]);
})();
})();
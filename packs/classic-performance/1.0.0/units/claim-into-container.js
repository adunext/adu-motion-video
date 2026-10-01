(() => {

const F="-apple-system,'PingFang SC',sans-serif", B='#2462EA', L='#6d9bff', P='#F7F7F5';
const text=(pa,s,x,y,size=80,c='#0A0A0A',w=700,extra='')=>mk(pa,`<div style="font:${w} ${size}px ${F};line-height:1.13;letter-spacing:-1.6px;color:${c};${extra}">${s}</div>`,x,y);
const note=(pa,s,x,y,c='#888')=>text(pa,s,x,y,27,c,500,'letter-spacing:.2px');
const box=(pa,html,x,y,w,h,dark=false,extra='')=>mk(pa,`<div style="position:relative;width:${w}px;height:${h}px;border-radius:24px;background:${dark?'#161616':'#fff'};border:1.5px solid ${dark?'#333':'#E4E4E1'};overflow:hidden;${extra}">${html}</div>`,x,y);
const visible=(t,a,b,d=.24)=>pr(t,a,a+d)*(b==null?1:1-pr(t,b,b+d));
const spring=(t,a,d=.65)=>EZ.spring(pr(t,a,a+d));
const reveal=(e,t,a,b,dy=36,d=.5)=>{
    const q=pr(t,a,a+d),p=EZ.expo(q),out=b==null?0:pr(t,b,b+.24);
    place(e,{o:clamp(q*4)*(1-out),y:e._y+(1-p)*dy-26*EZ.in(out),blur:(1-p)*5+out*5});
  };
const cues=xs=>xs.forEach(x=>S(...x));
(()=>{
    const sc=new Scene(0,15.466,P,{grid:'grid'}), tag=tags(sc,'// 01 — 把方法公开');
    const cam=camCard(sc.el,460,740);
    const opening=text(sc.el,'公开蒸馏<br><span style="color:#2462EA">剪辑能力</span>',146,219,159,'#0A0A0A',800);
    const underline=mk(sc.el,'<div style="width:792px;height:8px;background:#2462EA;border-radius:6px"></div>',151,600);
    const intro=note(sc.el,'从一支成片，提炼成可复用的方法',151,656,'#777');
    const hSkill=text(sc.el,'把方法，装进 Skill',146,149,94);
    const pack=box(sc.el,`<div style="position:absolute;left:32px;top:26px;font:500 27px ${F};color:#888">可编辑工程 · 制作方法</div><div style="position:absolute;left:32px;top:79px;font:750 67px ${F};letter-spacing:-2px">adu-motion-video</div><div style="position:absolute;left:34px;bottom:27px;font:500 31px ${F};color:#2462EA">场景　·　声音　·　导出</div><div class="ready" style="position:absolute;right:25px;bottom:24px;border-radius:30px;background:#2462EA;color:#fff;padding:9px 18px;font:600 26px ${F};opacity:0">✓ 本片正在使用</div>`,146,353,1122,235,false,'box-shadow:0 22px 55px rgba(0,0,0,.09)');
    const paths=mk(sc.el,'<svg width="1122" height="86"><path class="p" d="M561 0V33H174V86M561 33V86M561 33H948V86" fill="none" stroke="#2462EA" stroke-width="3" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/></svg>',146,587);
    const models=['Codex','豆包','更多助手'].map((s,i)=>box(sc.el,`<div style="height:100%;display:flex;align-items:center;justify-content:center;font:650 43px ${F};color:${i===0?B:'#222'}">${s}</div>`,146+i*386,675,350,106));
    const packets=models.map(()=>mk(sc.el,'<div style="width:15px;height:15px;border-radius:5px;background:#2462EA;box-shadow:0 0 16px rgba(36,98,234,.35)"></div>',0,0,{ax:.5,ay:.5}));
    const proof=text(sc.el,'这条视频，就在用它',146,150,100);
    const proofLine=note(sc.el,'文案 → 画面 → 可编辑成片',151,734,B);
    const jokeLabel=note(sc.el,'个人吐槽 · 不是平台通知',151,218,'#777');
    const joke=box(sc.el,`<div style="position:absolute;left:38px;top:32px;font:500 31px ${F};color:#a6a6a6">发出这条视频之后……</div><div class="question" style="position:absolute;right:46px;top:13px;font:750 183px ${F};color:#2b2b2b">?</div>`,146,307,1122,324,true);
    const stamp=text(sc.el,'永久黑名单？',200,410,110,L,800);
    const resolve=text(sc.el,'方法，照样公开。',151,724,54,B,650);
    const resolveLine=mk(sc.el,'<div style="width:481px;height:6px;border-radius:5px;background:#2462EA"></div>',151,794);
    sc.update=t=>{
      tag(t);
      const inP=spring(t,0,.8), k=EZ.inout(pr(t,3.4,4.12));
      cam.firstChild.style.width=lerp(460,266,k)+'px';cam.firstChild.style.height=lerp(740,266,k)+'px';
      cam.firstChild.style.borderRadius=lerp(26,133,k)+'px';cam._sm=k;cam.querySelector('.lab').style.opacity=1-k;
      const hit=pr(t,13.133,13.62), recoil=hit>0&&hit<1?Math.sin(hit*Math.PI*2)*10*(1-hit):0;
      camAt(cam,t,{x:lerp(1570+(1-inP)*108,1692,k)+recoil,y:lerp(454,246,k),s:1,o:1,r:recoil*.07});
      const out=pr(t,3.30,3.57), land=EZ.out5(pr(t,0,.43));
      place(opening,{o:1-out,s:1+.09*(1-land),x:146-20*(1-land),y:219-10*(1-land)-35*EZ.in(out),blur:3*(1-land)+out*4});
      place(underline,{sx:EZ.expo(pr(t,1.46,2.1)),o:1-out});reveal(intro,t,2.033,3.3);
      reveal(hSkill,t,3.56,8.30);
      const pa=spring(t,4.52,.62), hand=EZ.inout(pr(t,8.6,9.35)), po=pr(t,10.88,11.18);
      place(pack,{x:146-145*EZ.in(po),y:353-18*hand,s:.92+.08*pa,o:clamp((t-4.52)*7)*(1-po),r:-1.3*(1-pa)});
      pack.querySelector('.ready').style.opacity=pr(t,9.566,9.88);
      place(paths,{o:visible(t,5.6,9.45)});paths.querySelector('.p').style.strokeDashoffset=1-EZ.inout(pr(t,5.6,6.4));
      models.forEach((e,i)=>{
        const st=5.93+i*.35,p=spring(t,st,.6),ex=pr(t,9.65+i*.035,10.03+i*.035);
        place(e,{x:e._x,y:e._y+38*(1-p)-50*EZ.in(ex),s:.94+.06*p,o:clamp((t-st)*9)*(1-ex),blur:ex*5});
        const z=pr(t,5.77+i*.35,6.28+i*.35),x1=707,x2=321+i*386;
        const horizontal=EZ.inout(pr(z,.20,.78));
        place(packets[i],{x:lerp(x1,x2,horizontal),y:587+Math.min(z/.2,1)*33+pr(z,.78,1)*55,o:z>0&&z<1?1:0,s:1+.15*Math.sin(z*Math.PI)});
      });
      reveal(proof,t,8.566,10.85,30,.38);reveal(proofLine,t,10.13,10.85,18,.3);
      reveal(jokeLabel,t,11.15,null);
      const j=spring(t,11.22,.64);place(joke,{o:pr(t,11.22,11.4),x:146+(1-j)*95,y:307,s:1,r:1.5*(1-j)});
      joke.querySelector('.question').style.transform=`rotate(${12*(1-EZ.out(pr(t,12.166,12.67)))}deg)`;
      const sp=pr(t,13.133,13.61), sv=EZ.out5(sp);
      place(stamp,{x:200,y:410-125*(1-sv),s:1+.48*(1-sv),r:-5*(1-EZ.spring(sp)),o:clamp(sp*7),blur:9*(1-sv)});
      reveal(resolve,t,14.2,null,25,.38);place(resolveLine,{sx:EZ.expo(pr(t,14.3,14.85)),o:pr(t,14.3,14.38)});
    };
    sc.cam=t=>({x:960,y:540,z:1+.012*EZ.out(pr(t,1.8,3.3))*(1-EZ.out(pr(t,3.4,4.1)))});
    cues([[0,'swoosh',.48,.6],[.16,'hit',.58],[1.46,'swipe',.28],[3.4,'whoosh',.42],[4.64,'card',.5],[5.93,'tick',.3,-.5],[6.28,'tick',.3],[6.63,'tick',.3,.5],[8.566,'hit',.45],[9.7,'ding',.42],[11.22,'card',.42],[13.2,'stamp',.65],[14.3,'slash',.35]]);
  })();
})();
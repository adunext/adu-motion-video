(() => {

const BLUE = '#2462EA', LIGHT = '#78A2FF', INK = '#0A0A0A', PAPER = '#F7F7F5';
const FONT = "-apple-system,'PingFang SC',sans-serif";
const ease = x => { x = clamp(x); return x*x*x*(x*(x*6-15)+10); };
const q = (t,a,b) => ease(pr(t,a,b));
const on = (t,a,b=1e6,d=.35) => q(t,a,a+d)*(1-q(t,b,b+d));
const el = (p,h,x=0,y=0,w=0,hg=0,center=false) => mk(p,h,x,y,{ax:center?.5:0,ay:center?.5:0,style:`${w?`width:${w}px;`:''}${hg?`height:${hg}px;`:''}`});
const txt = (p,h,x,y,size=68,c=INK,weight=700) => el(p,`<div style="font:${weight} ${size}px/1.16 ${FONT};color:${c};letter-spacing:${size>=70?-2:0}px;white-space:nowrap">${h}</div>`,x,y);
const box = (p,x,y,w,h,bg=INK,border='#333',r=24) => el(p,`<div style="width:100%;height:100%;background:${bg};border:1.5px solid ${border};border-radius:${r}px;overflow:hidden"></div>`,x,y,w,h,true);
const enter = (e,t,a,b=1e6,{d=.6,dy=32,x=e._x,y=e._y,s=1}={}) => place(e,{x,y:y+(1-q(t,a,a+d))*dy,o:on(t,a,b,Math.min(.3,d)),s});
const travel = (a,c,b,p) => [(1-p)*(1-p)*a[0]+2*(1-p)*p*c[0]+p*p*b[0],(1-p)*(1-p)*a[1]+2*(1-p)*p*c[1]+p*p*b[1]];
const group = p => el(p,'',960,540,1920,1080,true);
const moveRig = (rig,t,a,b,dx=0,dy=0,z=.022) => { const p=q(t,a,b);place(rig,{x:960+dx*p,y:540+dy*p,s:1+z*p}); };
const waveHTML = (n=20,color=BLUE) => `<div style="display:flex;align-items:center;justify-content:center;gap:7px;height:112px">${Array.from({length:n},(_,i)=>`<i class="wavebar" style="width:8px;height:${20+(i%6)*14}px;background:${color};border-radius:4px;transform-origin:center"></i>`).join('')}</div>`;
const waveAt = (e,t,start,amp=1) => [...e.querySelectorAll('.wavebar')].forEach((b,i)=>{const z=.25+.75*Math.abs(Math.sin((t-start)*3.7+i*.61)*Math.cos((t-start)*1.1+i*.17));b.style.transform=`scaleY(${(.2+z*amp).toFixed(4)})`;});
const kit = (p,x=790,y=505,w=470,h=280) => {
    const e=box(p,x,y,w,h,BLUE,'#80A7FF',28),ks=Math.min(w/470,h/280);
    e.firstChild.innerHTML=`<div class="kit-lid" style="position:absolute;left:0;top:0;width:100%;height:45px;background:#5A8AFF;transform-origin:top center"></div><div style="position:absolute;left:34px;top:${69*h/280}px;font:600 ${31*ks}px ${FONT};color:#dbe6ff">adu-motion-video</div><div style="position:absolute;left:32px;top:${112*h/280}px;font:750 ${78*ks}px ${FONT};color:white;letter-spacing:-2px">Skill</div><div class="kit-bits" style="position:absolute;left:34px;bottom:${26*h/280}px;display:flex;gap:${10*ks}px">${['排版','运动','声音'].map(a=>`<span style="padding:${7*ks}px ${15*ks}px;border:1px solid #A6C1FF;border-radius:8px;font:500 ${26*ks}px ${FONT};color:#fff">${a}</span>`).join('')}</div>`;
    return e;
  };
const kitAt=(e,t,o,open=0)=>{place(e,o);e.querySelector('.kit-lid').style.transform=`perspective(600px) rotateX(${(-70*open).toFixed(3)}deg) translateY(${(-20*open).toFixed(3)}px)`;};
const footer=(sc,text,dark=true)=>txt(sc.el,text,146,818,27,dark?'#979797':'#777',500);
function scene(a,b,bg,n,title,dark=true){
    const sc=new Scene(a,b,bg,{grid:dark?'gridD':'grid'}),rig=group(sc.el),cam=camCard(sc.el,250,250,'',true),tag=tags(sc,`// ${n} — ${title}`,'',dark),R=race(sc.el,dark);
    return {sc,rig,cam,base:t=>{tag(t);raceAt(R,t);},person:(t,x=1730,y=220,s=.9)=>camAt(cam,t,{x,y,s,o:1})};
  }
{
    const {sc,rig,base,person}=scene(84.3,101.666,INK,'06','把方法拆开');
    const note=footer(sc,'个人观察 · 方法类比');
    const lead=txt(rig,'它的实现逻辑？',146,148,77,'#fff');
    const distill=txt(rig,'蒸馏',1090,389,151,LIGHT,800);
    const explain=txt(rig,'把熟悉的方法，<br>变成可重复的步骤',1090,636,33,'#aaa',500);
    const preview=macWin(rig,850,478,'原片动效 · 视觉配方');
    const h=txt(rig,'把画面，拆成<span style="color:#78A2FF">可复用的配方</span>',146,148,74,'#fff');
    const layerNames=['排版','运动','声音'];
    const layers=layerNames.map((n,i)=>{
      const e=box(rig,350+i*446,490,390,318,i===1?'#151d2d':'#171717','#414141',22);
      e.firstChild.innerHTML=`<div style="position:absolute;left:24px;top:21px;font:500 26px ${FONT};color:#aaa">0${i+1} / ${n}</div><div class="demo" style="position:absolute;left:24px;right:24px;top:79px;height:159px;overflow:hidden"></div><div style="position:absolute;left:24px;bottom:20px;font:600 32px ${FONT};color:white">${['标题 · 构图','时序 · 曲线','配乐 · 音效'][i]}</div>`;
      const d=e.querySelector('.demo');
      if(i===0)d.innerHTML=`<div class="layout-word" style="position:absolute;font:800 73px ${FONT};color:white;left:0;top:8px">动画</div><div class="layout-line" style="position:absolute;left:0;top:108px;width:285px;height:8px;background:${LIGHT};transform-origin:left"></div><div class="layout-chip" style="position:absolute;right:8px;top:16px;width:61px;height:61px;border:2px solid ${LIGHT};border-radius:15px"></div>`;
      if(i===1)d.innerHTML=`<svg width="342" height="145" viewBox="0 0 342 145"><path d="M20 112 C110 112 210 18 320 18" fill="none" stroke="#4D5B76" stroke-width="3"/><path class="motion-path" d="M20 112 C110 112 210 18 320 18" fill="none" stroke="${LIGHT}" stroke-width="5" pathLength="1" stroke-dasharray="1"/></svg><div class="motion-dot" style="position:absolute;width:38px;height:38px;background:white;border-radius:11px;left:0;top:0;box-shadow:0 8px 22px #0008"></div>`;
      if(i===2)d.innerHTML=waveHTML(22,LIGHT);
      return e;
    });
    const code=box(rig,790,510,820,343,'#161a22','#566784',24);
    code.firstChild.innerHTML=`<div style="padding:27px 35px;font:500 27px ${FONT};color:#A3BCEB">视觉配方 → 可执行的步骤</div>${['layout  →  标题 / 人物 / 素材','motion  →  曲线 / 时序 / 转场','audio   →  配乐 / 节拍 / 音效'].map((s,i)=>`<div class="recipe-line" style="position:absolute;left:35px;top:${93+i*70}px;font:500 37px 'SFM',${FONT};color:${i===1?LIGHT:'#E4E9F1'};white-space:nowrap">${s}</div>`).join('')}`;
    const packet=kit(rig);
    const finalH=txt(rig,'从视觉配方，到<span style="color:#78A2FF">可复用 Skill</span>',146,148,75,'#fff');
    const result=txt(rig,'规则 + 配方 + 工具',790,723,44,'#C4D5F8');result._ax=.5;
    sc.update=t=>{
      base(t);person(t,1730-25*q(t,89.7,92),220+25*q(t,89.7,92),.9-.05*q(t,89.7,92));place(note,{o:1});
      moveRig(rig,t,84.3,89.4,-5,-3,.017);
      enter(lead,t,84.3,89.65);enter(explain,t,87.8,89.65,{dy:18});
      const slam=pr(t,86.533,87.15);place(distill,{o:on(t,86.533,89.65),s:1+.23*(1-EZ.out(slam)),y:389+14*(1-q(t,86.533,87.15))});
      setFrame(preview._img,seqAt('prev',240,30,t,84.3,false));
      const unfold=q(t,89.7,90.7);place(preview,{x:lerp(614,790,unfold),y:506,s:lerp(1,.65,unfold),o:1-q(t,89.85,90.6),r:-2*(1-q(t,84.3,86.3))});
      enter(h,t,89.85,94.55,{dy:20});
      layers.forEach((e,i)=>{
        const split=q(t,89.86+i*.12,91.15+i*.1),join=q(t,94.7+i*.31,96.2+i*.31);
        const from=[lerp(790,350+i*446,split),lerp(503,490,split)],pos=travel(from,[610+i*150,250+i*50],[790,510],join);
        place(e,{x:pos[0],y:pos[1],r:(1-split)*[-7,0,7][i]+Math.sin(join*Math.PI)*[-12,8,15][i],s:lerp(.85,1,split)*(1-.72*join),o:on(t,89.9,96.05+i*.31,.24)});
        if(i===0){e.querySelector('.layout-word').style.transform=`translateX(${lerp(72,0,q(t,91.1,92.8))}px) scale(${lerp(.72,1,q(t,91.1,92.8))})`;e.querySelector('.layout-line').style.transform=`scaleX(${q(t,91.6,93.2)})`;e.querySelector('.layout-chip').style.transform=`translateY(${lerp(45,0,q(t,92.1,93.5))}px) rotate(${lerp(25,0,q(t,92.1,93.5))}deg)`;}
        if(i===1){const p=q(t,91.9,94.25),v=travel([20,112],[160,112],[320,18],p);e.querySelector('.motion-dot').style.transform=`translate(${v[0]-19}px,${v[1]-19}px) rotate(${p*90}deg)`;e.querySelector('.motion-path').style.strokeDashoffset=1-p;}
        if(i===2)waveAt(e,t,92.0);
      });
      const fold=q(t,98.55,100.02);place(code,{o:on(t,95.72,99.77,.4),x:790,y:510,sx:1-.51*fold,sy:1-.18*fold,r:-3*Math.sin(fold*Math.PI)});
      code.querySelectorAll('.recipe-line').forEach((e,i)=>{const p=q(t,96.25+i*.53,97.2+i*.53);e.style.clipPath=`inset(0 ${(1-p)*100}% 0 0)`;e.style.transform=`translateX(${(1-p)*22}px)`;});
      kitAt(packet,t,{x:790,y:505,s:.92+.08*q(t,99.4,100.5),o:on(t,99.45)},1-q(t,99.45,100.45));
      enter(finalH,t,94.83,1e6,{dy:22});enter(result,t,100.05,1e6,{dy:20});
    };
    [[86.533,'hit',.7],[89.9,'whoosh',.55],[91.25,'card',.35],[92.4,'click',.25],[94.8,'whoosh',.45],[96.7,'click',.25],[99.55,'card',.5],[100.15,'ding',.4]].forEach(a=>S(...a));
  }
})();
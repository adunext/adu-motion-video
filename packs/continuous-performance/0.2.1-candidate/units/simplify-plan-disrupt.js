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
    const {sc,rig,base,person}=scene(101.666,118.2,PAPER,'07','提示词体验',false);
    const note=footer(sc,'个人体验示意 · 不是通用效果保证',false);
    const packet=kit(rig);
    const h0=txt(rig,'提示词，怎么写？',146,148,82);
    const h1=txt(rig,'越长 <span style="color:#2462EA">≠</span> 越好',146,148,87);
    const h2=txt(rig,'让目标进入<span style="color:#2462EA">模板计划</span>',146,148,77);
    const prompt=box(rig,790,480,1280,409,'#fff','#BFC8D6',25);
    const pl=prompt.firstChild;
    pl.innerHTML=`<div class="prompt-label" style="position:absolute;left:32px;top:24px;font:600 29px ${FONT};color:#71809A">很多指令</div>${['画面这样排，镜头那样切。','再加一种动效，再换一种节奏。','这里突出，那里也要突出。','把每个想法都塞进去……'].map((v,i)=>`<div class="prompt-line" style="position:absolute;left:35px;top:${83+i*65}px;font:500 40px ${FONT};color:#404651">${v}</div>`).join('')}<div class="goal" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#0A0A0A"><div style="font:600 29px ${FONT};color:#2462EA;margin-bottom:14px">一句目标</div><div style="font:700 53px ${FONT}">根据这段口播，制作配套动画视频。</div></div>`;
    const rail=el(rig,'<div style="height:4px;background:#BFC8D6;width:1270px"></div>',160,542,1270,4);
    const runner=el(rig,'<div style="width:5px;height:235px;background:#2462EA;box-shadow:0 0 0 5px #2462EA10"></div>',190,420);
    const parts=['开场','说明','演示','收尾'].map((a,i)=>{
      const e=box(rig,315+i*330,551,270,206,i===2?BLUE:'#fff',i===2?BLUE:'#C6CDD8',19);
      e.firstChild.innerHTML=`<div style="position:absolute;left:20px;top:18px;font:500 23px ${FONT};color:${i===2?'#B7CCFF':'#828B9B'}">0${i+1}</div><div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:700 51px ${FONT};color:${i===2?'#fff':INK}">${a}</div><div class="part-meter" style="position:absolute;left:20px;right:20px;bottom:22px;height:5px;background:${i===2?'#fff':BLUE};transform-origin:left"></div>`;return e;
    });
    const instructions=['再加一套 Skill','再叠更多指令','再换一种节奏'].map((a,i)=>{const e=box(rig,650+i*240,360,235,82,'#E9EFFF','#7296E7',14);e.firstChild.innerHTML=`<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font:600 29px ${FONT};color:#1A459F">${a}</div>`;return e;});
    const breakLine=el(rig,'<div style="width:116px;height:6px;background:#F7F7F5;border-left:18px solid #2462EA;border-right:18px solid #2462EA"></div>',713,540);
    const disrupted=txt(rig,'原来的编排，被打断了',146,746,52,BLUE);
    const folder=kit(rig,1180,470,370,230);
    sc.update=t=>{
      base(t);person(t,1705+25*q(t,102.1,104.4),245-25*q(t,102.1,104.4),.85+.05*q(t,102.1,104.4));place(note,{o:1});
      moveRig(rig,t,104.7,107.8,0,0,.018);
      const start=q(t,101.666,102.7);kitAt(packet,t,{x:lerp(790,1370,start),y:lerp(505,390,start),s:1-.72*start,o:1-q(t,102.18,102.7)},0);
      enter(h0,t,101.7,103.88);enter(h1,t,104.08,107.98,{dy:15});enter(h2,t,108.23);
      const compress=q(t,105.15,106.6),intoPlan=q(t,108.05,109.15);
      place(prompt,{x:790,y:lerp(480,360,intoPlan),o:on(t,102.04,108.87,.35),s:1-.15*intoPlan});
      prompt.style.height=`${lerp(409,179,compress)}px`;
      pl.querySelector('.prompt-label').style.opacity=1-q(t,104.95,105.4);
      pl.querySelectorAll('.prompt-line').forEach((e,i)=>{const p=q(t,105.07+i*.08,106.25+i*.08);e.style.opacity=on(t,102.2+i*.45,105.45+i*.08,.3);e.style.transform=`translate(${p*(440-i*65)}px,${p*(80-i*65)}px) scale(${1-.8*p})`;e.style.clipPath=`inset(0 ${(1-q(t,102.2+i*.45,102.9+i*.45))*100}% 0 0)`;});
      const goal=pl.querySelector('.goal');goal.style.opacity=on(t,105.85,108.65,.45);goal.style.transform=`translateY(${(1-q(t,105.85,106.5))*20}px)`;
      place(rail,{o:on(t,108.6,117.0),sx:q(t,108.6,110.0)});
      const disruption=q(t,112.566,114.15),more=q(t,114.566,115.45),last=q(t,115.733,116.55),closing=q(t,117.15,118.19);
      parts.forEach((e,i)=>{
        const spread=q(t,108.48+i*.11,110.0+i*.11),position=[lerp(790,315+i*330,spread)+[0,-28,88,148][i]*disruption,lerp(375,551,spread)+[0,-50,48,-32][i]*disruption+[0,0,20,30][i]*more];
        const pp=travel(position,[1130,290],[1180,470],closing);
        place(e,{x:pp[0],y:pp[1],s:(.35+.65*spread)*(1-.8*closing),r:[0,-8,8,-6][i]*disruption*(1-closing),o:on(t,108.49+i*.11,117.9,.22)});
        e.querySelector('.part-meter').style.transform=`scaleX(${q(t,110.0+i*.44,111.0+i*.44)*(1-.62*disruption*(i>0))})`;
      });
      const progress=q(t,110.05,116.45),halt=lerp(190,1430,progress)-455*disruption-140*more;
      place(runner,{x:halt,y:420,o:on(t,110.1,116.8,.2),sy:1-.4*last});
      instructions.forEach((e,i)=>{const a=[112.566,114.566,115.733][i],p=q(t,a,a+.76),v=travel([490+i*325,320],[680+i*245,320],[625+i*260,519+(i%2)*50],p);place(e,{x:v[0],y:v[1],r:lerp(-10,[-5,6,-3][i],p),s:.8+.2*p,o:on(t,a,117.15,.2)});});
      place(breakLine,{o:on(t,113.05,117),sx:.7+.3*last});enter(disrupted,t,116.25,117.42,{dy:18});
      kitAt(folder,t,{x:1180,y:470,s:.9+.1*q(t,117.55,118.2),o:on(t,117.65,1e6,.32)},1-q(t,117.6,118.2));
    };
    [[102.1,'card',.4],[104.13,'hit',.48],[105.35,'whoosh',.45],[106.35,'ding',.35],[108.55,'whoosh',.42],[110.2,'click',.3],[112.566,'card',.4],[114.566,'card',.4],[115.733,'card',.36],[117.6,'whoosh',.4]].forEach(a=>S(...a));
  }
})();
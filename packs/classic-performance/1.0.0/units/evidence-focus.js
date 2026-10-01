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
    const sc=new Scene(68.6,84.3,'#0A0A0A',{grid:'gridD',trans:'wipe',td:.45,tc:'#0A0A0A'}),tag=tags(sc,'// 05 — 回到创作本身','',true);
    const cam=camCard(sc.el,288,288,'',true);
    const intro=text(sc.el,'回到创作本身',146,135,96,'#fff'),title=text(sc.el,'创作能力，确实出色',146,135,89,'#fff');
    const win=macWin(sc.el,1000,530,'阿杜导演 · AI 自动剪辑');win._x=146;win._y=284;win._ax=0;win._ay=0;
    win.querySelector('.tb').style.fontSize='22px';
    const view=win.querySelector('.body'),img=win._img;
    const guides=document.createElement('div');guides.style.cssText='position:absolute;inset:0;pointer-events:none;opacity:0;';
    guides.innerHTML='<svg width="1000" height="530" viewBox="0 0 1000 530"><path class="g" d="M333 0V530M666 0V530M0 177H1000M0 354H1000" fill="none" stroke="#6d9bff" stroke-width="2" stroke-dasharray="9 10"/><rect x="6" y="6" width="988" height="518" rx="8" fill="none" stroke="#6d9bff" stroke-width="4"/></svg>';view.appendChild(guides);
    const focus=document.createElement('div');focus.style.cssText='position:absolute;left:35%;top:22%;width:41%;height:53%;border:3px solid #6d9bff;border-radius:10px;opacity:0;pointer-events:none;box-shadow:0 0 0 2000px rgba(0,0,0,.14)';view.appendChild(focus);
    const names=['画面排版','动效动画','音效细节'];
    const cards=names.map((s,i)=>box(sc.el,`<div class="label" style="position:absolute;left:25px;top:24px;font:650 39px ${F};color:#fff">${s}</div><div class="bar" style="position:absolute;left:25px;right:25px;bottom:21px;height:3px;background:#6d9bff;transform-origin:left center;transform:scaleX(0)"></div>`,1210,431+i*125,325,102,true));
    const former=['研发自动剪辑','真实软件画面','从专业角度看'];
    const speed=box(sc.el,`<div style="font:600 26px ${F};color:white;display:flex;align-items:center;justify-content:center;height:100%">▶▶ 2.4×</div>`,912,342,195,50,true,'background:rgba(0,0,0,.8);border-color:#666');
    const waves=mk(sc.el,`<svg width="310" height="49">${Array.from({length:26},(_,i)=>`<rect class="w" x="${i*12}" y="10" width="6" height="29" rx="3" fill="#6d9bff"/>`).join('')}</svg>`,1221,798);
    const finale=note(sc.el,'细节，决定完成度。',1210,350,L);
    sc.update=t=>{
      tag(t);camAt(cam,t,{x:1720,y:250,s:.94});reveal(intro,t,68.64,74.70);reveal(title,t,74.966,null,25,.4);
      const p=spring(t,69.2,.7),shift=EZ.inout(pr(t,78.05,78.7));
      place(win,{x:146,y:284+(1-p)*50,s:.93+.07*p-0.012*shift,o:pr(t,69.2,69.38),r:.65*(1-p)});
      if(t<72.2)setFrame(img,seqAt('soft_match',90,30,t,69.2,false));
      else if(t<74.966)setFrame(img,seqAt('soft_tpl',360,72,t,72.2,false));
      else setFrame(img,seqAt('prev',240,30,t,74.966,false));
      win.querySelector('.tb span').textContent=t<74.966?'阿杜导演 · AI 自动剪辑':'上一集画面 · 创作效果回看';
      reveal(speed,t,72.2,74.75,15,.35);
      cards.forEach((e,i)=>{
        const a=[71.166,72.9,74.966][i],hit=[78.133,79.35,80.166][i],s=spring(t,a,.65),q=pr(t,hit,hit+.6),sel=EZ.spring(q);
        place(e,{x:e._x+(1-s)*125-15*sel,y:e._y,s:1+.028*Math.sin(q*Math.PI),o:pr(t,a,a+.18)});
        e.querySelector('.label').textContent=t>=hit?names[i]:former[i];
        e.firstChild.style.background=t>=hit?'#15233e':'#161616';e.firstChild.style.borderColor=t>=hit?'#6d9bff':'#333';
        e.querySelector('.bar').style.transform=`scaleX(${EZ.expo(q)})`;
      });
      guides.style.opacity=(visible(t,78.133,79.25,.18)*.88).toFixed(3);
      focus.style.opacity=visible(t,79.35,80.06,.15).toFixed(3);focus.style.transform=`translateX(${12*EZ.inout(pr(t,79.35,80.06))}px)`;
      reveal(waves,t,80.4,null,12,.4);
      waves.querySelectorAll('.w').forEach((e,i)=>{const a=12+24*(.5+.5*Math.sin(t*7+i*.65));e.setAttribute('height',a.toFixed(2));e.setAttribute('y',((49-a)/2).toFixed(2));});
      reveal(finale,t,82.266,null,20,.5);
    };
    sc.cam=t=>({x:960,y:540,z:1});
    cues([[68.64,'whoosh',.4],[69.34,'card',.44],[71.3,'click',.28],[72.2,'ff',.25,0,{d:.65}],[72.9,'click',.28],[74.966,'hit',.48],[78.133,'card',.37],[79.35,'swipe',.37],[80.166,'tick',.36],[82.266,'ding',.39]]);
  })();
})();
(() => {

const F="-apple-system,'PingFang SC',sans-serif", BLUE='#2462EA', LIGHT='#6d9bff';
const text=(p,s,x,y,z=80,c='#0A0A0A',w=700,extra='')=>mk(p,`<div style="font:${w} ${z}px/1.12 ${F};letter-spacing:-2px;color:${c};${extra}">${s}</div>`,x,y);
const at=MOTION.at, vis=MOTION.vis;
(()=>{
  const sc=new Scene(0,15.466,'#F7F7F5',{grid:'grid'}), tag=tags(sc,'// 01 — 把方法公开');
  const title=text(sc.el,'公开复用',142,202,148), title2=text(sc.el,'剪辑能力',142,382,166,BLUE,800);
  const line=mk(sc.el,'<div style="width:840px;height:8px;background:#2462EA"></div>',150,585);
  const deck=['画面','动作','声音'].map((s,i)=>mk(sc.el,`<div style="width:178px;height:53px;border:1px solid #b5c8ef;color:#2462EA;display:flex;align-items:center;justify-content:center;border-radius:9px;background:#edf2fc;font:600 26px ${F}">${s}</div>`,154+i*202,660));
  const intro=text(sc.el,'从动画工程，提炼出制作方法',151,617,30,'#727272',500,'letter-spacing:0');
  // Single camera element changes shape and location; its source never changes clocks.
  const cam=camCard(sc.el,470,740,'// on air · 阿杜Next');
  const label=cam.querySelector('.lab');
  const heading=text(sc.el,'把方法，装进 Skill',146,145,100);
  const pack=mk(sc.el,`<div class="pack-body" style="position:relative;width:1190px;height:300px;border-radius:25px;background:white;border:1.5px solid #ccd5e6;overflow:hidden;box-shadow:0 22px 65px #10234416">
    <div class="pack-top" style="height:47px;border-bottom:1px solid #e7e9ec;display:flex;align-items:center;gap:8px;padding:0 24px"><i style="width:10px;height:10px;border-radius:50%;background:#b8c5da"></i><i style="width:10px;height:10px;border-radius:50%;background:#b8c5da"></i><i style="width:10px;height:10px;border-radius:50%;background:#b8c5da"></i><span class="mono" style="font-size:20px;color:#777;margin-left:12px">Animation → SKILL.md</span></div>
    <div class="package-title" style="position:absolute;left:35px;top:77px;font:750 67px ${F};letter-spacing:-2px">adu-motion-video</div>
    <div class="package-sub" style="position:absolute;left:39px;top:166px;font:500 31px ${F};color:#777">场景配方　＋　声音编排　＋　导出工具</div>
    <div class="package-mark" style="position:absolute;right:33px;top:79px;width:78px;height:100px;background:#2462EA;border-radius:12px;color:white;display:flex;align-items:center;justify-content:center;font:650 26px ${F}">Skill</div>
    <div style="position:absolute;left:39px;right:39px;bottom:32px;height:7px;background:#e7edf8;border-radius:5px;overflow:hidden"><div class="pack-progress" style="height:100%;background:#2462EA;transform-origin:left"></div></div>
   </div>`,740,450,{ax:.5,ay:.5});
  const routes=mk(sc.el,'<svg width="1220" height="114" viewBox="0 0 1220 114"><path d="M610 0V42Q610 54 598 54H186Q174 54 174 66V110M610 0V110M610 54H1034Q1046 54 1046 66V110" fill="none" stroke="#2462EA" stroke-width="3.5"/></svg>',130,599);
  const path=routes.querySelector('path');
  const nodes=['Codex','豆包','更多助手'].map((s,i)=>mk(sc.el,`<div class="model" style="position:relative;width:354px;height:102px;border-radius:20px;border:1.5px solid #cbd7ed;background:#fff;display:flex;justify-content:center;align-items:center;font:650 43px ${F};color:${i===0?BLUE:'#171717'}"><span>${s}</span><b style="position:absolute;right:24px;top:39px;width:20px;height:20px;background:#2462EA;border-radius:50%;transform:scale(0)"></b></div>`,146+i*423,705));
  const packets=nodes.map((_,i)=>mk(sc.el,'<div style="width:13px;height:13px;border:3px solid #fff;background:#2462EA;border-radius:50%;box-shadow:0 0 0 2px #2462EA"></div>',740,605,{ax:.5,ay:.5}));
  const proof=text(sc.el,'这条视频，就在用它',146,148,100);
  const proofLabel=text(sc.el,'本集正在验证这套流程',176,346,30,'#dce6ff',550,'letter-spacing:0');
  const proofTracks=['画面','动作','声音'].map((s,i)=>mk(sc.el,`<div style="width:1035px;height:58px;position:relative"><span style="color:#fff;font:550 28px ${F}">${s}</span><div style="position:absolute;left:102px;right:0;top:0;height:44px;background:#ffffff1c;border-radius:7px;overflow:hidden">${Array.from({length:8},(_,j)=>`<i style="position:absolute;left:${j*119}px;top:${7+(j%2)*3}px;width:${80+j%3*8}px;height:${28-(j%2)*6}px;background:${i===0?'#f6f8ff':i===1?'#b9cffa':'#80a8fc'};border-radius:4px"></i>`).join('')}<div class="scan" style="position:absolute;left:0;top:0;bottom:0;width:3px;background:#fff;box-shadow:0 0 12px #fff"></div></div></div>`,176,417+i*80));
  const proofChip=mk(sc.el,`<div style="font:650 27px ${F};color:#fff;border:1.5px solid #ffffff88;border-radius:20px;padding:8px 21px">本片实践</div>`,1040,341);
  const jokeTop=text(sc.el,'个人吐槽',181,289,28,'#989da8',500,'letter-spacing:0');
  const jokeA=text(sc.el,'可能进入',181,375,76,'#fff');
  const jokeB=text(sc.el,'永久黑名单？',181,480,101,LIGHT,800);
  const jokeC=text(sc.el,'但方法，还是想分享给大家。',187,711,35,'#b7bcc5',500);
  const stamp=mk(sc.el,`<div style="width:272px;height:159px;border:6px solid #6d9bff;border-radius:12px;display:flex;align-items:center;justify-content:center;font:750 68px ${F};color:#6d9bff;letter-spacing:5px">？</div>`,1095,500,{ax:.5,ay:.5});
  const R=race(sc.el,false);
  sc.update=t=>{
   tag(t);raceAt(R,t); const opening=1-at(t,3.03,3.62),p=pr(t,0,.34),m=at(t,3.02,4.02);
   place(title,{x:142,y:202-95*at(t,3.03,3.63),s:1+.13*(1-EZ.out5(p)),o:opening});
   place(title2,{x:142,y:382-64*at(t,3.16,3.67),s:1+.2*(1-EZ.out5(p)),o:opening,blur:4*(1-p)});
   place(line,{x:lerp(150,184,at(t,2.8,3.9)),y:lerp(585,687,at(t,2.8,3.9)),sx:at(t,.6,1.45),o:opening});
   place(intro,{o:vis(t,1.75,3.39,.22),y:617+14*(1-at(t,1.75,2.35))});
   deck.forEach((e,i)=>{const q=at(t,2.07+i*.12,2.72+i*.12),collect=at(t,3.14+i*.06,4.04+i*.06);place(e,{x:lerp(154+i*202,980,collect),y:lerp(675,468,collect)+36*(1-q),r:(i-1)*3*(1-collect),s:lerp(1,.15,collect),o:q*(1-collect)});});
   const body=cam.firstChild;body.style.width=lerp(470,290,m)+'px';body.style.height=lerp(740,290,m)+'px';body.style.borderRadius=lerp(28,145,m)+'px';cam._sm=m;label.style.opacity=1-m;
   camAt(cam,t,{x:lerp(1640,1725,m),y:lerp(479,262,m),s:.9,o:1});
   place(heading,{y:145+35*(1-at(t,3.63,4.18)),o:vis(t,3.63,8.52,.25)});
   const packIn=at(t,3.9,4.9), proofP=at(t,8.48,9.2), joke=at(t,11.03,11.76);
   const packY=lerp(450,496,proofP);place(pack,{x:740,y:packY+80*(1-packIn),sx:lerp(.75,1,packIn),sy:lerp(.08,1,packIn),o:packIn});
   const pb=pack.querySelector('.pack-body');pb.style.height=lerp(300,lerp(386,588,joke),proofP)+'px';pb.style.background=joke>.01?`rgb(${Math.round(36*(1-joke)+10*joke)},${Math.round(98*(1-joke)+10*joke)},${Math.round(234*(1-joke)+10*joke)})`:proofP>.01?`rgb(${Math.round(255-219*proofP)},${Math.round(255-157*proofP)},${Math.round(255-21*proofP)})`:'#fff';pb.style.borderColor=joke>.5?'#343943':proofP>.5?'#2462EA':'#ccd5e6';
   ['.pack-top','.package-title','.package-sub','.package-mark'].forEach((k,i)=>{let e=pack.querySelector(k);e.style.opacity=at(t,4.1+i*.13,4.68+i*.13)*(1-proofP);e.style.transform=`translateY(${18*(1-at(t,4.1+i*.13,4.68+i*.13))}px)`;});
   pack.querySelector('.pack-progress').style.transform=`scaleX(${at(t,4.8,6.2)})`;pack.querySelector('.pack-progress').parentNode.style.opacity=1-proofP;
   place(routes,{o:vis(t,5.65,9.0,.2)});MOTION.stroke(path,at(t,5.65,6.65));
   nodes.forEach((e,i)=>{const n=at(t,6.08+i*.34,6.7+i*.34),out=at(t,8.6+i*.06,9.2+i*.06);place(e,{x:146+i*423,y:705+25*(1-n)+90*out,s:1-.16*out,o:n*(1-out)});e.querySelector('b').style.transform=`scale(${at(t,7.3+i*.15,7.75+i*.15)*.7})`;});
   packets.forEach((e,i)=>{const q=at(t,6.2+i*.3,7.25+i*.3);const xy=MOTION.bezier([740,604],[740,674],[323+i*423,653],[323+i*423,710],q);place(e,{x:xy[0],y:xy[1],o:vis(t,6.2+i*.3,7.5+i*.3,.16)});});
   place(proof,{y:148+18*(1-at(t,8.566,9.13)),o:vis(t,8.566,11.11,.2)});place(proofLabel,{o:vis(t,8.98,11.08,.18)});place(proofChip,{o:vis(t,9.38,11.08,.18)});
   proofTracks.forEach((e,i)=>{place(e,{o:vis(t,9.06+i*.12,11.08,.2),x:176+24*(1-at(t,9.06+i*.12,9.6+i*.12))});e.querySelector('.scan').style.left=`${at(t,9.26,11)*910}px`;});
   place(jokeTop,{o:at(t,11.5,12),y:289+20*(1-at(t,11.5,12))});place(jokeA,{o:at(t,11.66,12.22),y:375+20*(1-at(t,11.66,12.22))});
   place(jokeB,{o:at(t,12.13,12.56),x:181,s:1+.13*(1-at(t,12.13,12.67))});
   const hit=MOTION.settle(t,12.53,.8);place(stamp,{o:at(t,12.53,12.65),r:-11+7*(1-hit),s:1+.55*(1-hit),x:1095,y:500+42*(1-hit)});
   place(jokeC,{o:at(t,13.28,13.9),y:711+25*(1-at(t,13.28,13.9))});
  };
  sc.cam=t=>{const[sx,sy]=shake(t,.03,.3,6);return{x:960,y:540,sx,sy};};
  [[0,'hit',.7],[2.07,'tick',.24],[3.35,'whoosh',.42],[4.65,'card',.4],[6.25,'click',.25],[6.59,'click',.25],[6.93,'click',.25],[8.566,'whoosh',.4],[9.38,'ding',.28],[11.06,'whoosh',.46],[12.53,'hit',.52],[13.28,'tick',.22]].forEach(a=>S(...a));
 })();
})();
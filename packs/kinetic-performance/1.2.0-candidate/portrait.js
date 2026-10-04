/* Per-object output geometry. Source elements, timing, media sampling and SFX
   remain untouched; wrappers carry only native positions and uniform sizes. */
(()=>{'use strict';
const cfg=window.PACK_LAYOUT;if(!cfg||cfg.name!=='portrait')return;
const id=cfg.pack;
const profiles={
 'classic-performance':{x0:146,sx:.70,y0:130,sy:1.5,y:430,k:.70},
 'continuous-performance':{x0:146,sx:.70,y0:130,sy:1.5,y:430,k:.70},
 'stage-performance':{x0:560,sx:.84,y0:130,sy:1.5,y:430,k:.78},
 'editorial-performance':{x0:834,sx:.96,y0:130,sy:1.5,y:430,k:.94},
 'kinetic-performance':{x0:128,sx:.76,y0:130,sy:1.5,y:430,k:.76},
 'paper-balance':{x0:100,sx:.72,y0:100,sy:.72,y:580,k:.72},
 'paper-ball-performance':{x0:100,sx:.65,y0:0,sy:.65,y:500,k:.65},
 'doubao-console-performance':{x0:100,sx:.70,y0:0,sy:.70,y:500,k:.70}
};
const p=profiles[id];if(!p)throw Error('No reviewed portrait profile for '+id);
const states=[],nativeConsole=[];let initialized=false;
const original=window.renderAt;
const lerp=(a,b,k)=>a+(b-a)*k;
function point(x,y){return[64+(x-p.x0)*p.sx,p.y+(y-p.y0)*p.sy];}
function translate(e){const s=e.style.transform,m=s.match(/translate(?:3d)?\(\s*(-?[\d.]+)px\s*,\s*(-?[\d.]+)px/);return m?[+m[1],+m[2]]:[0,0];}
function wrap(e,map,k=p.k,offset=[0,0]){const w=document.createElement('div');w.className='portrait-island';e.parentNode.insertBefore(w,e);w.appendChild(e);const state={e,w,map,k,offset};states.push(state);return state;}
function camera(e,parent=[0,0]){const body=e.querySelector('.cam')||e;const a=wrap(e,(x,y)=>[900+(x-(e._x||x))*.08,240+(y-(e._y||y))*.08],1,parent);a.camera=body;return a;}
function fixed(x,y,sx=.35,sy=.5,source=null){return (a,b,e)=>[x+(a-(source?.[0]??e._x??a))*sx,y+(b-(source?.[1]??e._y??b))*sy];}
function setup(sc,sceneId){
 const pb=sc.el.querySelector('.pb-host'),nd=sc.el.querySelector('.nd-host'),db=sc.el.querySelector('.doubao-host');
 if(pb){setupPaperBall(pb,sceneId);return;}
 if(nd){setupBalance(nd);return;}
 if(db){setupConsole(db,sceneId);return;}
 const sp={...p,...(id==='stage-performance'&&sceneId==='decompose-and-consolidate'?{x0:146,sx:.8,k:.8}:{}),...(id==='editorial-performance'&&sceneId==='evidence-and-focus'?{x0:96,sx:.62,k:.72}: {})};
 const native=(x,y)=>[64+(x-sp.x0)*sp.sx,sp.y+(y-sp.y0)*sp.sy];
 const all=[...sc.el.querySelectorAll('.e')].filter(e=>typeof e._x==='number'&&(!e.parentElement.closest('.e')||(e.parentElement.closest('.e').style.width==='1920px'&&e.parentElement.closest('.e').style.height==='1080px')));
 for(const e of all){
  if(e.style.width==='1920px'&&e.style.height==='1080px'&&e.querySelector('.e')){e._portraitRig=true;continue;}
  const b=e.firstElementChild;
  if(b?.classList.contains('cam')){camera(e);continue;}
  if(b?.classList.contains('tag')){wrap(e,fixed(e._ax?740:64,e._ax?88:48,0,0),.9);continue;}
  if(e._p){wrap(e,fixed(64,1872,0,0),936/1628);continue;}
  if(id==='stage-performance'&&e._x<0){wrap(e,(x,y)=>[x*.55,y*1.65],.85);continue;}
  if(id==='stage-performance'&&e._x>=1800){wrap(e,fixed(1020,410),.7);continue;}
  if(id==='editorial-performance'&&e._y>=40&&e._y<=55){wrap(e,fixed(e._ax?740:64,e._ax?88:48,0,0),.9);continue;}
  if(id==='editorial-performance'&&[798,767].includes(e._x)){e.style.display='none';e._portraitDecoration=true;continue;}
  if(id==='editorial-performance'&&e._y===107){wrap(e,fixed(64,140,0,0),936/1728);continue;}
  let k=sp.k,map=(x,y)=>native(x,y);
  if(b?.tagName==='SVG'){wrap(e,map,[sp.sx,sp.sy]);continue;}
  const body=b||e,width=Math.max(body.offsetWidth,body.scrollWidth,e.offsetWidth,e.scrollWidth),font=parseFloat(getComputedStyle(body).fontSize);
  if(!body.querySelector('img,svg')&&font>=55){k=Math.min(.9,936/Math.max(1,width));}
  if(width>1350)k=Math.min(k,936/width);
  if(font>=70&&!body.querySelector('img,svg')&&font*k<44)throw Error('Portrait headline below 44px: '+sceneId+'; shorten this slot or choose a different group');
  if(id==='editorial-performance'&&sceneId==='evidence-and-focus'){
   if(b?.classList.contains('macwin')){map=fixed(540,1000,.5,.8,[708,510]);k=936/1212;}
   if(e._x>=1400&&e._y>=400&&e._y<=810){const row=Math.min(2,Math.max(0,Math.floor((e._y-424)/127)));map=fixed(64+row*312,e._y%127>100?1475:1410,.6,.8);k=.75;}
  }
  if(id==='kinetic-performance'&&sceneId==='evidence-and-focus'&&e._x>=1150){const j=Math.round((e._y-327)/161);map=fixed(64+j*312,1420,.6,.8);k=.65;}
  if(id==='stage-performance'&&sceneId==='decompose-and-consolidate'&&e._x===146)k=Math.min(k,.78);
  wrap(e,map,k);
 }
}
function setupBalance(host){
 const world=host.querySelector('.nd-world');
 for(const e of [...world.children]){
  if(e.classList.contains('cam')){camera(e,[960,540]);continue;}
  // The illustration's aspect ratio is episode-owned, so fit its actual width.
  const width=Math.max(e.offsetWidth,e.scrollWidth);
  wrap(e,(x,y)=>[540+(x+470)*.72,1050+(y+60)*.72],Math.min(.82,936/Math.max(1,width)),[960,540]);
 }
 const ov=host.querySelector('.nd-camera')?.parentElement.querySelector('.ov');
 if(ov)for(const e of [...ov.children]){
  const left=parseFloat(e.style.left)||0,top=parseFloat(e.style.top)||0;
  const centered=e.style.right==='0px'&&left===0,cards=centered&&!!e.querySelector('.g2c');
  if(centered){e.style.width=cards?'1101px':'1920px';if(cards){e.style.flexDirection='column';e.style.alignItems='center';e.style.gap='44px';}}
  const w=parseFloat(e.style.width)||e.offsetWidth;
  let k=Math.min(.85,936/Math.max(1,w));
  const map=e.classList.contains('hand')?fixed(64,1450,.72,.72,[left,top]):centered?(x,y)=>[64+(x-left)*.72,point(x,y)[1]]:(x,y)=>point(x,y);
  wrap(e,map,k);
  e._portraitOffset=[left,top];
 }
 // Hand-drawn paths are an independent paper overlay, retaining circular strokes.
 const ink=host.querySelector('svg');if(ink)wrap(ink,(x,y)=>point(x,y),p.k);
}
function setupPaperBall(host,sceneId){
 for(const e of [...host.querySelectorAll('.it')]){
  const k=e.classList.contains('kin')?p.k:(e.querySelector('.ln')?.parentElement||e).classList.contains('dcard')?.9:p.k;
  wrap(e,(x,y)=>point(x,y),k);
 }
 for(const c of host.querySelectorAll('canvas'))wrap(c,(x,y)=>point(x,y),p.k);
 for(const svg of host.querySelectorAll('.scn>svg.ink'))wrap(svg,(x,y)=>point(x,y),p.k);
 const cam=host.querySelector('[data-pb-node=cam]');if(cam)camera(cam);
 for(const key of ['ball','halo']){const e=host.querySelector('[data-pb-node='+key+']');if(e)wrap(e,(x,y)=>point(x,y),p.k);}
 const meta=host.querySelector('[data-pb-node=meta]');if(meta)meta.style.display='none';
}
function setupConsole(host,sceneId){
 const root=host.querySelector('[data-doubao-node=world] .sc');
 const n=[...root.children].filter(e=>e.classList.contains('e'));
 const expected={'fusion-success':5,'three-step-chat':9,'manual-agents-delivery':6};
 if(n.length!==expected[sceneId])throw Error('Console portrait structure changed: '+sceneId+':'+n.length);
 const at=(i,x,y,k=.9,source=null)=>wrap(n[i],fixed(x,y,.7,.7,source),k);
 if(sceneId==='fusion-success'){
  at(0,64,430,.86);at(1,64,1470,1.06);
  for(let i=2;i<5;i++)wrap(n[i],(x,y)=>point(x,y),.9);
 }
 if(sceneId==='three-step-chat'){
  at(0,540,700,1.08);
  for(let i=0;i<3;i++)at(i+1,82+i*318,510,1);
  at(4,940,850,1);at(5,940,1050,1);at(6,780,1260,1);at(7,940,1360,1);at(8,140,1470,1.08);
 }
 if(sceneId==='manual-agents-delivery'){
  at(0,64,430,.9);at(1,670,1050,1.02);
  for(let i=0;i<3;i++)at(i+2,110,920+i*180,.98);
  at(5,540,1450,1,[1100,500]);
 }
 if(sceneId==='fusion-success'){for(const c of host.querySelectorAll('canvas'))wrap(c,(x,y)=>point(x,y),p.k);}
 else{
  for(const c of host.querySelectorAll('canvas'))c.style.display='none';
  const canvas=document.createElement('canvas');canvas.width=1080;canvas.height=1920;canvas.style.cssText='position:absolute;inset:0;pointer-events:none';
  host.querySelector('[data-doubao-node=world]').prepend(canvas);nativeConsole.push({sc:host.closest('.sc'),id:sceneId,ctx:canvas.getContext('2d')});
 }
 const tk=host.querySelector('.tkc');if(tk)camera(tk);
 const hud=host.querySelector('[data-doubao-node=hud]');
 const h=[...hud.children].filter(e=>e.classList.contains('e'));
 h.forEach((e,i)=>wrap(e,fixed(i===1?740:i===2?540:64,i===0?48:i===1?88:i===2?150:1872,0,0),i===3?936/1792:.9));
 // Inner depth/drift camera is recentered after source update, not removed.
 root._portraitInner=true;
}
// These two console scenes change column topology in portrait. Their native
// connectors use the original activation/impact times, retaining source SFX.
function sourceTime(sc){const index=SCENES.findIndex(s=>s.el===sc),item=MACRO_PLAN.scenes[index],f=window.MACRO_OUTPUT_T*MACRO_PLAN.fps,a=item.time_map;for(let j=1;j<a.length;j++)if(f<=a[j].output_frame||j===a.length-1){const q=Math.max(0,Math.min(1,(f-a[j-1].output_frame)/(a[j].output_frame-a[j-1].output_frame)));return lerp(a[j-1].source,a[j].source,q);}return a[0].source;}
function drawConsole(view){
 if(view.sc.style.display==='none')return;
 const t=sourceTime(view.sc),c=view.ctx,manual=view.id==='manual-agents-delivery';
 const q=(a,b)=>Math.max(0,Math.min(1,(t-a)/(b-a))),hash=i=>{const v=Math.sin(i*127.1+311.7)*43758.5453;return v-Math.floor(v);};
 c.clearRect(0,0,1080,1920);c.fillStyle='#06070A';c.fillRect(0,0,1080,1920);
 const glow=c.createRadialGradient(600,1050,0,600,1050,850);glow.addColorStop(0,'#142031');glow.addColorStop(1,'#06070A');c.fillStyle=glow;c.fillRect(0,0,1080,1920);
 c.strokeStyle='rgba(124,200,255,.06)';c.lineWidth=1;
 for(let i=0;i<13;i++){c.beginPath();c.moveTo(540,1550);c.lineTo(i*100-100,1920);c.stroke();}
 for(let i=0;i<8;i++){const y=1550+i*i*7;c.beginPath();c.moveTo(0,y);c.lineTo(1080,y);c.stroke();}
 for(let i=0;i<50;i++){c.globalAlpha=.12+.22*hash(i+4);c.fillStyle='#8fc9ed';c.beginPath();c.arc(hash(i)*1080,(hash(i+8)*1920+t*(4+hash(i+7)*8))%1920,1+hash(i+2),0,Math.PI*2);c.fill();}c.globalAlpha=1;
 function beam(x0,y0,x1,y1,k,col){if(k<=0)return;c.strokeStyle=col;c.shadowColor=col;c.shadowBlur=12;c.lineWidth=2;c.beginPath();c.moveTo(x0,y0);c.lineTo(lerp(x0,x1,k),lerp(y0,y1,k));c.stroke();c.shadowBlur=0;for(let j=0;j<4;j++){const p=((t*1.1+j/4)%1)*k;c.fillStyle=col;c.beginPath();c.arc(lerp(x0,x1,p),lerp(y0,y1,p),3,0,Math.PI*2);c.fill();}}
 function sphere(x,y,k,col){if(k<=0)return;const r=31*(.4+.6*k),g=c.createRadialGradient(x-r*.3,y-r*.35,0,x,y,r*3);g.addColorStop(0,'#fff');g.addColorStop(.12,col);g.addColorStop(.34,col+'88');g.addColorStop(1,col+'00');c.fillStyle=g;c.beginPath();c.arc(x,y,r*3,0,Math.PI*2);c.fill();c.strokeStyle=col;c.lineWidth=1;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.stroke();}
 if(manual){const times=[53.13,53.93,54.87],colors=['#7CC8FF','#FFB648','#BEA0FF'];for(let i=0;i<3;i++){const k=q(times[i]-.1,times[i]+.3),y=920+i*180;sphere(64,y,k,colors[i]);beam(98,y,384,928+i*122,q(times[i]+.1,times[i]+.6)*(1-q(60.5,61)),colors[i]);}}
 else{beam(154,510,360,510,q(20.07,20.47),'#7CC8FF');beam(472,510,678,510,q(25.03,25.43),'#7CC8FF');}
 for(const [time,x,y,col] of manual?[[58.73,670,1254,'#3DDC84'],[60.8,771,1534,'#3DDC84']]:[[19.95,780,900,'#7CC8FF'],[26.7,400,1510,'#3DDC84']]){const age=t-time;if(age<0||age>1)continue;c.globalAlpha=(1-age)*.8;c.fillStyle=col;for(let i=0;i<40;i++){const ang=hash(i+time)*Math.PI*2,d=age*(150+hash(i)*400);c.fillRect(x+Math.cos(ang)*d,y+Math.sin(ang)*d+age*age*100,2+hash(i+5)*3,2+hash(i+5)*3);}c.globalAlpha=1;}
}
function tick(){
 for(const a of states){
  const e=a.e,[tx,ty]=translate(e),off=e._portraitOffset||[0,0],x=tx+off[0],y=ty+off[1];
  let [nx,ny]=a.map(x,y,e),k=a.k;
  if(a.camera){const w=a.camera.offsetWidth;k=220/Math.max(1,w);if(typeof e._x!=='number'&&!e.style.transform.startsWith('translate(-50%')){nx-=110;ny-=a.camera.offsetHeight*k/2;}}
  const [kx,ky]=Array.isArray(k)?k:[k,k];
  a.w.style.transform=`translate(${(nx-a.offset[0]-kx*x).toFixed(4)}px,${(ny-a.offset[1]-ky*y).toFixed(4)}px) scale(${kx},${ky})`;
 }
 for(const sc of SCENES){
  for(const rig of sc.el.querySelectorAll('.e'))if(rig._portraitRig){const [x,y]=translate(rig),s=rig.style.transform.match(/scale\(([^,)]+)/);rig.style.transformOrigin='540px 960px';rig.style.transform=`translate(${(x-960)*.6}px,${(y-540)*1.5}px) scale(${s?+s[1]:1})`;}
  for(const e of sc.el.querySelectorAll('[data-doubao-node=world],[data-doubao-node=front]')){e.style.transformOrigin='540px 960px';const [x,y]=translate(e);e.style.transform=e.style.transform.replace(/translate\([^)]*\)/,`translate(${x*.7}px,${y*.7}px)`);}
  for(const e of sc.el.querySelectorAll('[data-pb-node=main]'))e.style.transformOrigin='540px 960px';
 }
 for(const view of nativeConsole)drawConsole(view);
 const world=document.getElementById('world');
 if(world?.style.transform){world.style.transform=world.style.transform.replace(/translate\(960px,\s*540px\)/g,'translate(540px,960px)').replace(/translate\(-960px,\s*-540px\)/g,'translate(-540px,-960px)');}
 const circle=document.getElementById('fx')?.children[1];if(circle){circle.style.left='540px';circle.style.top='960px';}
 for(const sc of SCENES){const circle=sc.el.querySelector('[data-doubao-node=fx]')?.children[1];if(circle){circle.style.left='900px';circle.style.top='240px';}}
}
// Source procedural canvases clear pixels but can leave blend/alpha state.
// Reset before seeking so a prior impact cannot tint the next requested frame.
function resetCanvas(){for(const sc of SCENES)for(const canvas of sc.el.querySelectorAll('canvas')){const ctx=canvas.getContext('2d');if(ctx.reset)ctx.reset();else canvas.width=canvas.width;}}
window.renderAt=async function(t){if(!initialized)return original(t);resetCanvas();const result=await original(t);tick();return result;};
const ready=window.READY||Promise.resolve();
window.READY=Promise.resolve(ready).then(async()=>{
 const plans=window.MACRO_PLAN?.scenes||[];
 if(plans.length!==SCENES.length)throw Error('Portrait scene/plan count differs');
 for(let i=0;i<SCENES.length;i++){await original(plans[i].output_start_frame/(MACRO_PLAN.fps||60));setup(SCENES[i],plans[i].layoutSceneId||plans[i].sceneId);}
 initialized=true;await window.renderAt(0);
 window.PORTRAIT_REPORT={schema:'adu-native-portrait/1',pack:id,width:1080,height:1920,
  scenes:plans.map(s=>s.sceneId),islands:states.length,sourceClock:'unchanged',audioClock:'unchanged',
  status:'geometry-ready-needs-episode-audiovisual-review'};
});
})();

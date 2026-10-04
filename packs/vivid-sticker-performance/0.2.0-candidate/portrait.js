/* Native composition islands retain source trajectories and spring timing.
   Separate maps carry object, Canvas and presenter planes, never a stage scale. */
(()=>{'use strict';if(window.PACK_LAYOUT?.name!=='portrait')return;
const states=[],hosts=[];let initialized=false;const original=window.renderAt;
const translate=e=>{const m=e.style.transform.match(/translate\(\s*(-?[\d.]+)px\s*,\s*(-?[\d.]+)px/);return m?[+m[1],+m[2]]:[0,0];};
const fixed=(nx,ny,source,slope=.7)=>(x,y)=>[nx+(x-source[0])*slope,ny+(y-source[1])*slope];
function wrap(e,map,k=1){const w=document.createElement('div');w.className='sticker-island';e.parentNode.insertBefore(w,e);w.appendChild(e);states.push({e,w,map,k});}
function setup(sc,id){
 const host=sc.el.querySelector('.sticker-host'),root=host.querySelector('[data-sticker-node=world] .sc');
 const n=[...root.children].filter(e=>e.classList.contains('e'));
 const counts={'keyword-to-conclusion':2,'prepared-to-reuse':8,'feedback-to-update':5};
 if(n.length!==counts[id])throw Error('Reviewed portrait structure changed: '+id+':'+n.length);
 const at=(i,x,y,k=.9,source=null)=>wrap(n[i],fixed(x,y,source||[n[i]._x,n[i]._y]),k);
 const canvases=[...host.querySelectorAll('canvas')];
 if(id==='keyword-to-conclusion'){
  host.style.background='#000';at(0,540,840,1);at(1,540,1120,.78);
  canvases.forEach(c=>wrap(c,fixed(540,940,[860,470],.9),.9));
 }
 if(id==='prepared-to-reuse'){
  host.style.background='#F7F7F5';at(0,64,410,.95);at(1,64,540,.85);
  at(2,280,1140,.78);at(3,0,0,.9,[0,0]);states[states.length-1].map=(x,y)=>[440+(x-700)*.56,850+(y-560)*.7+(x-700)*.5];
  at(4,0,0,.9,[0,0]);states[states.length-1].map=(x,y)=>[440+(x-700)*.56,850+(y-560)*.7+(x-700)*.5];
  at(5,800,1370,.8);at(6,540,1510,.85);at(7,540,680,.8);
  canvases.forEach((c,i)=>{wrap(c,(x,y)=>[440+(x-700)*.56,850+(y-560)*.7],[.56,.7]);if(i===1)states[states.length-1].shear=.5;});
 }
 if(id==='feedback-to-update'){
  host.style.background='#F7F7F5';at(0,64,430,.93);
  const start=[[220,680],[620,800],[270,980]],target=[560,1260];
  for(let i=0;i<3;i++){
   const e=n[i+1],sx=e._x,sy=e._y,[nx,ny]=start[i];
   wrap(e,(x,y)=>[nx+(x-sx)*(target[0]-nx)/(1150-sx),ny+(y-sy)*(target[1]-ny)/(560-sy)],.9);
  }
  at(4,560,1260,1.05);
  canvases.forEach(c=>wrap(c,fixed(560,1220,[1150,520],.8),.8));
 }
 const tk=host.querySelector('.tkc');wrap(tk,(x,y)=>[880,250],1);states[states.length-1].camera=true;
 const hud=[...host.querySelector('[data-sticker-node=hud]').children].filter(e=>e.classList.contains('e'));
 wrap(hud[0],fixed(64,58,[64,48],0),1.05);wrap(hud[1],fixed(64,115,[1856,48],0),1.05);hud[1]._ax=0;
 wrap(hud[2],fixed(64,1880,[64,1060],0),952/1792);
 hosts.push(host);
}
function tick(){
 for(const s of states){const [x,y]=translate(s.e);let[nx,ny]=s.map(x,y),k=s.k;
  if(s.camera){const w=s.e.offsetWidth,h=s.e.offsetHeight;k=240/Math.max(w,h);nx-=w*k/2;ny-=h*k/2;}
  const[kx,ky]=Array.isArray(k)?k:[k,k];s.w.style.transform=s.shear?`matrix(${kx},${s.shear},0,${ky},${nx-kx*x},${ny-ky*y-s.shear*x})`:`translate(${nx-kx*x}px,${ny-ky*y}px) scale(${kx},${ky})`;
 }
 for(const host of hosts){
  for(const key of ['world','front']){const e=host.querySelector('[data-sticker-node='+key+']');e.style.transformOrigin='540px 960px';}
  const circ=host.querySelector('[data-sticker-node=fx]')?.children[1];if(circ){circ.style.left='540px';circ.style.top='960px';}
 }
 const world=document.getElementById('world');if(world.style.transform)world.style.transform=world.style.transform.replace(/translate\(960px,\s*540px\)/g,'translate(540px,960px)').replace(/translate\(-960px,\s*-540px\)/g,'translate(-540px,-960px)');
}
window.renderAt=async t=>{if(!initialized)return original(t);for(const host of hosts)for(const c of host.querySelectorAll('canvas')){if(c.getContext('2d').reset)c.getContext('2d').reset();else c.width=c.width;}await original(t);tick();};
window.READY=Promise.resolve(window.READY).then(async()=>{
 const plan=window.MACRO_PLAN.scenes;if(plan.length!==SCENES.length)throw Error('Portrait plan/scene count differs');
 for(let i=0;i<SCENES.length;i++){await original(plan[i].output_start_frame/60);setup(SCENES[i],plan[i].layoutSceneId||plan[i].sceneId);}
 initialized=true;await renderAt(0);window.PORTRAIT_REPORT={schema:'adu-native-portrait/1',pack:'vivid-sticker-performance',scenes:plan.map(s=>s.sceneId),islands:states.length,status:'geometry-only-needs-real-episode-av-review'};
});
})();

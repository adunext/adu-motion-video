/* Native geometry for the frozen nine showcase scenes. Authored motion and
   source-clock media run first; this adapter preserves their timing and state. */
(()=>{'use strict';
const cfg=window.SHOWCASE_LAYOUT;if(!cfg)throw Error('Missing showcase layout');
const portrait=cfg.layout==='portrait',W=cfg.width,H=cfg.height,originalPlace=place,originalRender=window.renderAt;
const states=[],fit=[];let initialized=false;
place=function(el,o={}){const a=el._nativeShowcase;if(!a)return originalPlace(el,o);const x=o.x??el._x,y=o.y??el._y,p=a.fn?a.fn(x,y,window.SHOWCASE_SOURCE_TIME,o):[a.x+(x-a.sx)*a.mx,a.y+(y-a.sy)*a.my];return originalPlace(el,{...o,x:p[0],y:p[1]});};
function setup(sc,id){
 const n=[...sc.el.children].filter(e=>e.classList.contains('e')),post=[];
 const expected={s01:21,s02:23,s03:15,s04:18,s05:19,s06:9,s07:13,s08:13,s09:6,"independent-artifact-review":11};
 if(n.length!==expected[id])throw Error('Showcase structural contract changed: '+id);
 const e=i=>typeof i==='number'?n[i]:i,b=i=>e(i).firstElementChild;
 function at(i,x,y,mx=.45,my=.55,sx=e(i)._x,sy=e(i)._y){const v=e(i);v._nativeShowcase={x,y,mx,my,sx,sy};v.classList.add('native-portrait-node');return v;}
 function custom(i,fn){at(i,0,0);e(i)._nativeShowcase.fn=fn;}
 function size(i,w,h){b(i).style.width=w+'px';if(h)b(i).style.height=h+'px';return b(i);}
 function text(i,x,y,z=84,w=936,one=false){at(i,x,y);const v=b(i);Object.assign(v.style,{fontSize:z+'px',lineHeight:'1.16',whiteSpace:one?'nowrap':'normal',width:w+'px'});if(one)fit.push({el:v,max:z,width:w});return v;}
 function group(i,x,y,w=936){at(i,x,y);const v=e(i),body=b(i),ow=body.offsetWidth,oh=body.offsetHeight;if(!ow||!oh)throw Error('Unmeasurable group '+id+':'+i);const k=w/ow;Object.assign(v.style,{width:w+'px',height:oh*k+'px'});Object.assign(body.style,{transformOrigin:'0 0',transform:'scale('+k+')'});return body;}
 function cover(i){at(i,0,0,0,0);size(i,W,H);}
 function windowAt(i,x,y,w=936,h=527){at(i,x,y,.35,.5,720,575);const v=size(i,w);const content=v.querySelector('.body');if(content)content.style.height=h+'px';return v;}
 function video(i,x,y,w=936,h=527,sx=e(i)._x,sy=e(i)._y){at(i,x,y,.35,.5,sx,sy);size(i,w,h);}
 function camera(i,mode='small',start=0,end=0){const v=e(i);v._showcaseCamera=true;post.push(t=>{let w=246,h=246,x=885,y=255,k=1;
  if(mode==='hero'){k=EZ.inout(pr(t,start,end));w=lerp(840,246,k);h=lerp(840,246,k);x=lerp(540,885,k);y=lerp(1030,255,k);}
  if(mode==='large'){w=780;h=1100;x=540;y=960;k=0;}
  const opacity=Number(v.style.opacity);Object.assign(v.firstElementChild.style,{width:w+'px',height:h+'px',borderRadius:lerp(36,123,k)+'px'});originalPlace(v,{x,y,s:1,o:opacity});
  const im=v._img;if(im){const f=faceAt(window.MACRO_OUTPUT_T),cover=Math.max(w/720,h/1280),zoom=Math.max(1,(h*.43)/(f.h*1280*cover)),scale=cover*lerp(1,Math.min(2.6,zoom),k),iw=720*scale,ih=1280*scale;Object.assign(im.style,{position:'absolute',width:iw+'px',height:ih+'px',left:clamp(w/2-f.cx*iw,w-iw,0)+'px',top:clamp(h*.53-f.cy*ih,h-ih,0)+'px',objectFit:'fill',maxWidth:'none'});}
 });}
 function tags(){at(0,72,64,0,0).classList.add('portrait-top-tag');at(1,1008,64,0,0).classList.add('portrait-time-tag');b(0).style.maxWidth='650px';}
 function rail(){const v=n.find(x=>x._p);if(v){at(v,72,1872,0,0);v.firstElementChild.style.width='936px';}}
 tags();rail();
 if(id==='independent-artifact-review'){
  video(2,540,800,936,527,820,600);text(3,72,350,74);text(4,72,1090,24);[5,6,7].forEach((i,j)=>{size(i,936);at(i,72,1140+j*95);});text(8,72,350,70);camera(9);
 }
 if(id==='s01'){
  camera(2,'hero',2.35,3.85);camera(19);
  text(3,540,310,128,936,true);text(4,540,510,144,936,true);text(5,540,160,26,850,true);
  [6,11,13,14].forEach(cover);group(7,540,720,820);
  group(8,72,820,936);group(9,72,955,936);group(10,540,960,500);
  at(12,540,980,.45,.8);text(15,72,440,35);text(16,72,620,66);text(17,72,785,65);text(18,72,1080,132);
 }
 if(id==='s02'){
  camera(11);for(let j=0;j<9;j++){const i=j+2;at(i,224+(j%3)*316,545+Math.floor(j/3)*247,.4,.5);const box=size(i,300);box.querySelector('.fr').style.width='300px';box.querySelector('.fr').style.height='169px';const ring=box.querySelector('.ring');ring.style.width='314px';ring.style.height='183px';box.querySelector('.nm').style.fontSize='22px';box.querySelector('.mono').style.fontSize='16px';}
  text(12,72,385,26);group(13,72,1190,520);[14,15,16,17].forEach((i,j)=>at(i,72+j*230,1280));
  group(18,72,1380,936);text(19,72,1480,42);size(20,452,150);at(20,72,1480);size(21,452,170);at(21,556,1480);b(21).querySelector('.tv').style.fontSize='48px';
 }
 if(id==='s03'){
  camera(13);video(2,540,890,936,527,960,480);e(2)._nativeShowcase.fn=(x,y,t)=>{const g=EZ.inout(pr(t,25.9,26.9)),l=EZ.inout(pr(t,31,31.7));return[lerp(540,430,l),lerp(930,815,l)+(y-480)*.6]};
  text(3,540,520,135);group(4,540,1050,900);group(5,540,1360,936);
  at(6,885,520);group(6,885,520,200);text(7,72,1180,28);[8,9,10].forEach((i,j)=>{size(i,936);at(i,72,1240+j*94);});text(11,72,1490,73);
  group(12,1008,1515,840);e(12)._nativeShowcase.mx=.45;
 }
 if(id==='s04'){
  camera(2);text(3,72,465,84);[4,5,6,7].forEach((i,j)=>{at(i,300+(j%2)*480,900+Math.floor(j/2)*360);size(i,456);const vt=b(i).querySelector('.vt');Object.assign(vt.style,{width:'456px',height:'257px'});const label=vt.nextElementSibling;label.style.flexDirection='column';label.style.gap='4px';label.firstElementChild.style.fontSize='36px';label.lastElementChild.style.fontSize='23px';});
  at(8,540,960,.4,.8);group(9,540,340,900);text(10,540,890,95);group(11,72,850,936);group(12,72,1020,936);group(13,72,560,900);
  group(14,540,1080,936);text(15,72,470,84);group(16,72,1220,800);
 }
 if(id==='s05'){
  camera(2,'hero',55.3,57.4);camera(3);text(4,72,455,122);text(5,72,710,125);group(6,72,830,936);
  windowAt(7,540,820,936,527);custom(7,(x,y)=>[540+(x-720)*.25,820+(y-575)*.35]);
  [8,9].forEach((i,j)=>{size(i,452,140);at(i,72+j*484,1120);b(i).style.padding='18px';b(i).querySelectorAll('div').forEach(v=>{if(v.style.fontSize)v.style.fontSize=(v===b(i).firstElementChild?'30':'25')+'px';v.style.whiteSpace='normal';v.style.overflowWrap='anywhere';});});
  group(10,72,1265,310);text(11,72,380,25);text(12,72,430,77);group(13,580,1265,428);
  video(14,540,930,936,527,960,560);group(15,540,455,860);group(16,72,1090,936);text(17,72,530,126);
 }
 if(id==='s06'){
  camera(2);text(3,72,480,84);group(4,72,750,936);group(5,72,1000,936);b(5).querySelectorAll('.car').forEach(v=>{v.style.fontSize='52px';v.style.padding='0 36px';});text(6,72,1450,77);
  const box=size(7,936);at(7,540,1000);box.style.padding='28px';const grid=box.lastElementChild;grid.style.gridTemplateColumns='repeat(2,1fr)';grid.style.gap='20px';box.querySelectorAll('.stc').forEach(v=>{v.style.padding='24px';});box.firstElementChild.style.gap='20px';const pic=box.querySelector('img');pic.style.width='128px';pic.style.height='128px';box.querySelector('.sw').style.transform='scale(.7)';
 }
 if(id==='s07'){
  camera(2);text(3,72,480,86);group(4,72,815,936);post.push(t=>{const body=b(4),bar=body.querySelector('.bb');const g=EZ.out(pr(t,80.3,81.8)),cmp=EZ.inout(pr(t,82.15,82.9));bar.style.width=(936*g*(1-.88*cmp))+'px';body.style.transform='none';body.style.width='936px';});
  group(5,72,1080,936);group(6,740,1170,470);video(7,340,1020,470,837,640,520);video(8,650,1130,720,405,1400,540);
  text(9,72,480,74);[10,11].forEach((i,j)=>{size(i,936,142);at(i,72,650+j*174);});
 }
 if(id==='s08'){
  camera(2,'hero',91.2,92);text(3,72,415,28);text(4,72,525,100);text(5,72,790,130);group(6,72,750,936);group(7,540,970,900);cover(8);
  group(9,72,850,936);group(10,72,1200,936);text(11,72,1470,88);
 }
 if(id==='s09'){
  text(2,72,350,76);group(3,72,610,936);size(4,936,500);at(4,72,865);const prompt=b(4).querySelector('.prompt');if(prompt){prompt.style.fontSize='35px';prompt.style.lineHeight='1.4';}group(5,72,1490,936);
 }
 return{sc,id,post};
}
function update(t){
 if(initialized){const f=Math.max(0,Math.min(MACRO_PLAN.end_frame-1,Math.floor(t*MACRO_PLAN.fps+1e-6))),item=MACRO_PLAN.scenes.find(s=>f>=s.output_start_frame&&f<s.output_end_frame);window.SHOWCASE_SOURCE_TIME=sourceAt(item,f);}
 originalRender(t);if(!initialized)return;
 const i=MACRO_PLAN.scenes.findIndex(s=>window.MACRO_OUTPUT_T*MACRO_PLAN.fps>=s.output_start_frame&&window.MACRO_OUTPUT_T*MACRO_PLAN.fps<s.output_end_frame),state=states[i];
 if(!state)throw Error('Missing native scene state');
 if(portrait){const source=sourceAt(MACRO_PLAN.scenes[i],window.MACRO_OUTPUT_T*MACRO_PLAN.fps);window.SHOWCASE_SOURCE_TIME=source;state.post.forEach(fn=>fn(source));
  const cam=state.sc.cam(source);$('world').style.transform=cam?`translate(${(cam.sx||0)*.6}px,${(cam.sy||0)*.6}px) scale(${cam.z||1})`:'';
  const circle=$('fx').children[1];if(circle){circle.style.left='885px';circle.style.top='255px';}
  fit.forEach(v=>{v.el.style.fontSize=v.max+'px';if(v.el.scrollWidth>v.width)v.el.style.fontSize=Math.max(44,v.max*v.width/v.el.scrollWidth)+'px';if(v.el.scrollWidth>v.width+2)throw Error('Portrait title exceeds readable capacity; shorten this display slot');});
 }
 if(cfg.presenterEndSeconds!==null&&window.MACRO_OUTPUT_T>=cfg.presenterEndSeconds){state.sc.el.querySelectorAll('.cam').forEach(el=>{const root=el.parentElement;root.style.opacity='0';root.style.visibility='hidden';});}
}
function sourceAt(item,f){const a=item.time_map;for(let j=1;j<a.length;j++){if(f<=a[j].output_frame||j===a.length-1){const p=clamp((f-a[j-1].output_frame)/(a[j].output_frame-a[j-1].output_frame));return lerp(a[j-1].source,a[j].source,p);}}return a[0].source;}
window.renderAt=update;
const ready=window.READY;window.READY=Promise.resolve(ready).then(()=>{
 for(let i=0;i<SCENES.length;i++){originalRender(MACRO_PLAN.scenes[i].output_start_frame/MACRO_PLAN.fps);states.push(portrait?setup(SCENES[i],MACRO_PLAN.scenes[i].sceneId):{sc:SCENES[i],post:[]});}
 if(portrait)$('ov').querySelectorAll('div').forEach(v=>{if(v.querySelector('.sz'))v.classList.add('native-subtitles');});
 initialized=true;update(0);
});
})();

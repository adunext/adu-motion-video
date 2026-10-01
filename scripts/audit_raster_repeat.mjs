#!/usr/bin/env node
/** Diagnose an existing raster warning without changing its acceptance limits. */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright-core';
import {chrome} from './chrome.mjs';

const [projectArg, framesArg, outputArg, clockFlag, fpsArg, endArg] = process.argv.slice(2);
if (!projectArg || !framesArg || !outputArg) throw Error('Usage: audit_raster_repeat.mjs PROJECT FRAMES_COMMA_SEPARATED NEW_DIRECTORY [--clock FPS END_FRAMES]');
const project=path.resolve(projectArg), output=path.resolve(outputArg);
if(clockFlag&&clockFlag!=='--clock')throw Error('Unknown option');
const plan=clockFlag?{fps:Number(fpsArg),end_frame:Number(endArg),width:1920,height:1080}:JSON.parse(fs.readFileSync(path.join(project,'macro_plan.json')));
if(!Number.isInteger(plan.fps)||!Number.isInteger(plan.end_frame)||plan.fps<1||plan.end_frame<1)throw Error('Invalid explicit clock');
const frames=framesArg.split(',').map(Number);
if (!frames.every(f=>Number.isInteger(f)&&f>=0&&f<plan.end_frame)) throw Error('Frames must be inside the output clock');
if (fs.existsSync(output)||!fs.statSync(path.dirname(output)).isDirectory()) throw Error('A fresh output directory with an existing parent is required');
fs.mkdirSync(output);
const report={project,frames,fps:plan.fps,comparisons:[],limits:'Diagnostic only; it does not override or pass the original audit.',ok:false};
const errors=[];
const browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files']});
const ctx=await browser.newContext({viewport:{width:plan.width||1920,height:plan.height||1080},deviceScaleFactor:1,serviceWorkers:'block'});
await ctx.route('**/*',route=>/^(https?|wss?):/i.test(route.request().url())?route.abort():route.continue());
async function page(){
  const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
  await p.goto(pathToFileURL(path.join(project,'index.html')).href,{waitUntil:'load'});
  await p.waitForFunction(()=>window.READY&&typeof window.renderAt==='function');
  await p.evaluate(async()=>{await window.READY;await document.fonts.ready;});return p;
}
async function snap(p,frame,id){
  const state=await p.evaluate(async({frame,fps})=>{
    await window.renderAt(frame/fps);if(window.imgWait)await window.imgWait();await document.fonts.ready;
    for(const im of document.images){if(im.getAttribute('src')&&im.complete&&im.naturalWidth)await im.decode();}
    // Match the original auditor's visible node styles and media identity.
    const root=document.querySelector('#stage'), bounds=root.getBoundingClientRect(), nodes=[];
    for(const el of root.querySelectorAll('*')){
      let visible=true,o=1;for(let e=el;e;e=e.parentElement){const s=getComputedStyle(e);o*=Number(s.opacity||1);if(s.display==='none'||s.visibility==='hidden'||o<.005){visible=false;break;}}
      const r=el.getBoundingClientRect();if(!visible||r.right<=bounds.left||r.left>=bounds.right||r.bottom<=bounds.top||r.top>=bounds.bottom)continue;
      const s=getComputedStyle(el);nodes.push([el.tagName,el.className?.baseVal||el.className||'', [...el.childNodes].filter(n=>n.nodeType===Node.TEXT_NODE).map(n=>n.textContent).join('').trim(),[r.x,r.y,r.width,r.height].map(v=>Math.round(v*100)/100),s.opacity,s.transform,s.filter,s.clipPath,s.color,s.backgroundColor,s.fontSize,el.tagName==='IMG'?[el.currentSrc,el.naturalWidth,el.naturalHeight]:null]);
    }return nodes;
  },{frame,fps:plan.fps});
  const png=await p.screenshot({type:'png'});fs.writeFileSync(path.join(output,`${id}.png`),png);
  return {id,frame,domHash:crypto.createHash('sha256').update(JSON.stringify(state)).digest('hex'),pngHash:crypto.createHash('sha256').update(png).digest('hex'),png};
}
async function diff(p,a,b){
  return p.evaluate(async([a,b])=>{
    async function pixels(src){const im=new Image();im.src='data:image/png;base64,'+src;await im.decode();const c=document.createElement('canvas');c.width=im.width;c.height=im.height;const x=c.getContext('2d',{willReadFrequently:true});x.drawImage(im,0,0);return {data:x.getImageData(0,0,c.width,c.height).data,width:c.width};}
    const x=await pixels(a),y=await pixels(b);let changed=0,over1=0,over10=0,max=0,total=0;const box=[1920,1080,-1,-1];
    for(let i=0;i<x.data.length;i+=4){let peak=0;for(let c=0;c<4;c++){const d=Math.abs(x.data[i+c]-y.data[i+c]);total+=d;peak=Math.max(peak,d);}max=Math.max(max,peak);if(peak)changed++;if(peak>10)over10++;if(peak>1){over1++;const n=i/4,px=n%x.width,py=Math.floor(n/x.width);box[0]=Math.min(box[0],px);box[1]=Math.min(box[1],py);box[2]=Math.max(box[2],px);box[3]=Math.max(box[3],py);}}
    return {changedPixels:changed,pixelsOverOne:over1,pixelsOverTen:over10,maxChannelDifference:max,meanAbsoluteDifference:total/x.data.length,bounds:over1?box:null};
  },[a.png.toString('base64'),b.png.toString('base64')]);
}
try{
  for(const frame of frames){
    const p=await page(),base=await snap(p,frame,`${frame}_fresh_0`);
    const same=await snap(p,frame,`${frame}_same_page_repeat`);
    report.comparisons.push({frame,mode:'same-page-same-frame',a:base.id,b:same.id,domSame:base.domHash===same.domHash,pixels:await diff(p,base,same)});
    for(const f of [0,Math.floor(plan.end_frame/2),plan.end_frame-1,Math.floor(plan.end_frame/4)])await p.evaluate(t=>window.renderAt(t),f/plan.fps);
    const seek=await snap(p,frame,`${frame}_after_seeks`);
    report.comparisons.push({frame,mode:'same-page-after-seeks',a:base.id,b:seek.id,domSame:base.domHash===seek.domHash,pixels:await diff(p,base,seek)});
    for(let i=1;i<=3;i++){const fresh=await page(),s=await snap(fresh,frame,`${frame}_fresh_${i}`);report.comparisons.push({frame,mode:'fresh-vs-fresh',a:base.id,b:s.id,domSame:base.domHash===s.domHash,pixels:await diff(p,base,s)});await fresh.close();}
    await p.close();
  }
  report.errors=errors;report.allDomSame=report.comparisons.every(c=>c.domSame);report.samePageRasterStable=report.comparisons.filter(c=>c.mode.startsWith('same-page')).every(c=>c.pixels.changedPixels===0);
  report.freshRasterVaries=report.comparisons.some(c=>c.mode==='fresh-vs-fresh'&&c.pixels.changedPixels>0);
}finally{await ctx.close();await browser.close();fs.writeFileSync(path.join(output,'report.json'),JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({...report,comparisons:report.comparisons.map(c=>({frame:c.frame,mode:c.mode,domSame:c.domSame,pixels:c.pixels}))}));

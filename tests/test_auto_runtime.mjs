import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright-core';
import {chrome} from '../scripts/chrome.mjs';
const project=process.argv[2];
if(!project)throw Error('Pass a generated auto composition project');
const plan=JSON.parse(fs.readFileSync(path.join(project,'macro_plan.json')));
const browser=await chromium.launch({executablePath:chrome(),args:['--allow-file-access-from-files','--force-color-profile=srgb','--disable-gpu','--disable-accelerated-2d-canvas']});
try{
 const page=await browser.newPage({viewport:{width:plan.width,height:plan.height}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()));
 await page.goto(pathToFileURL(path.join(project,'index.html')).href);
 await page.evaluate(async()=>{await window.READY;await window.imgWait();});
 const indices=new Set([0,plan.end_frame-1]);
 for(const part of plan.parts){
  for(const f of [part.startFrame-2,part.startFrame-1,part.startFrame,part.startFrame+1,part.endFrame-1])if(f>=0&&f<plan.end_frame)indices.add(f);
  const child=JSON.parse(fs.readFileSync(path.join(project,part.path,'macro_plan.json')));
  for(const scene of child.scenes)for(const knot of scene.time_map)for(const delta of [-1,0,1]){
   const f=part.startFrame+knot.output_frame+delta;if(f>=0&&f<plan.end_frame)indices.add(f);
  }
 }
 const evidence=[];
 for(const f of [...indices].sort((a,b)=>a-b)){
  const state=await page.evaluate(async({f,plan})=>{
   await window.renderAt(f/plan.fps);await window.imgWait();
   const part=plan.parts.find(p=>f>=p.startFrame&&f<p.endFrame);
   const iframe=[...document.querySelectorAll('iframe')].find(e=>e.style.visibility==='visible');
   const child=iframe.contentWindow;
   return {clock:window.MACRO_OUTPUT_T,part:window.AUTO_ACTIVE_PART,local:child.MACRO_OUTPUT_T,
           missing:[...child.document.images].filter(im=>im.offsetWidth>0&&(!im.complete||im.naturalWidth===0)).map(im=>im.src),
           subtitle:child.document.querySelector('.sz')?.textContent,
           expected:part.path,expectedLocal:(f-part.startFrame)/plan.fps};
  },{f,plan});
  assert.equal(state.part,state.expected);assert.equal(state.clock,f/plan.fps);assert.equal(state.local,state.expectedLocal);
  assert.deepEqual(state.missing,[]);evidence.push({frame:f,part:state.part,subtitle:state.subtitle});
 }
 for(let repeat=0;repeat<8;repeat++)for(const part of plan.parts){
  await page.evaluate(async f=>{await window.renderAt(f/60);await window.imgWait();},part.startFrame+1);
  const first=await page.screenshot();
  const firstDOM=await page.evaluate(()=>[...document.querySelectorAll('iframe')].find(e=>e.style.visibility==='visible').contentWindow.document.documentElement.outerHTML);
  await page.evaluate(async f=>{await window.renderAt(f/60);await window.imgWait();},plan.end_frame-1);
  await page.evaluate(async f=>{await window.renderAt(f/60);await window.imgWait();},part.startFrame+1);
  const second=await page.screenshot();
  const secondDOM=await page.evaluate(()=>[...document.querySelectorAll('iframe')].find(e=>e.style.visibility==='visible').contentWindow.document.documentElement.outerHTML);
  if(process.env.ADU_AUTO_DEBUG&&Buffer.compare(first,second)){
    const name=part.path.replaceAll('/','_');
    fs.writeFileSync(path.join(process.env.ADU_AUTO_DEBUG,name+'-first.png'),first);
    fs.writeFileSync(path.join(process.env.ADU_AUTO_DEBUG,name+'-second.png'),second);
    fs.writeFileSync(path.join(process.env.ADU_AUTO_DEBUG,name+'-first.html'),firstDOM);
    fs.writeFileSync(path.join(process.env.ADU_AUTO_DEBUG,name+'-second.html'),secondDOM);
  }
  assert.equal(crypto.createHash('sha256').update(second).digest('hex'),crypto.createHash('sha256').update(first).digest('hex'),'Repeated seek '+part.path+' must produce identical pixels; DOM equal='+String(firstDOM===secondDOM));
 }
 const subs=await page.evaluate(async()=>{
  const boundary=window.AUTO_PLAN.parts[1].startFrame/60;
  await window.renderAt(boundary+.2);await window.imgWait();
  const child=[...document.querySelectorAll('iframe')].find(e=>e.style.visibility==='visible').contentWindow;
  return child.document.querySelector('.sz')?.textContent;
 });
 assert.equal(subs,'跨场字幕保持全局时钟');
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({seeks:evidence.length,parts:plan.parts.length,deterministic:true,repeatRoundTrips:16,subtitleGlobalClock:true,evidence}));
}finally{await browser.close();}

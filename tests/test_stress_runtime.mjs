// Repeated groups and extended holds use the actual frozen scene/runtime code.
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL,fileURLToPath} from 'node:url';import {spawnSync} from 'node:child_process';
import {chromium} from 'playwright-core';import {chrome} from '../scripts/chrome.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'adu-stress-browser-'));
let browser,seeks=0,groups=0,totalSeconds=0;const results=[];
try{
 const made=spawnSync(process.env.ADU_TEST_PYTHON||'python3',[root+'/tests/stress_runtime_fixture.py',temp],{encoding:'utf8'});assert.equal(made.status,0,made.stderr);
 browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files','--disable-accelerated-2d-canvas','--force-color-profile=srgb']});
 const placeholder=fs.readFileSync(temp+'/classic-performance/assets/demo-presenter.svg');
 for(const family of fs.readdirSync(temp).sort()){
  const folder=temp+'/'+family;if(!fs.existsSync(folder+'/index.html'))continue;
  const plan=JSON.parse(fs.readFileSync(folder+'/plan.json')),manifest=JSON.parse(fs.readFileSync(folder+'/manifest.json'));totalSeconds+=plan.at(-1).output_end_frame/60;
  for(const layout of ['landscape','portrait']){
   const page=await browser.newPage({viewport:layout==='portrait'?{width:1080,height:1920}:{width:1920,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.route('**/*',r=>/\.(jpg|jpeg|png|svg|webp)(\?|$)/.test(r.request().url())?r.fulfill({body:placeholder,contentType:'image/svg+xml'}):r.continue());
   await page.goto(pathToFileURL(folder+'/'+(layout==='portrait'?'index.html':'landscape.html')).href);await page.evaluate(()=>window.READY);
   assert.deepEqual(await page.evaluate(()=>[CONFIG.width,CONFIG.height]),layout==='portrait'?[1080,1920]:[1920,1080]);
   const initialSound=await page.evaluate(()=>JSON.stringify(SFX));
   const sound=JSON.parse(initialSound),sourceSound=await page.evaluate(()=>MACRO_SOURCE_SFX);
   assert.equal(sound.length,sourceSound.flat().length,family+' missing/extra events across repeated groups');
   assert.deepEqual(sound.map(s=>s.d).filter(x=>x!==undefined).sort(),sourceSound.flat().map(s=>s.d).filter(x=>x!==undefined).sort(),family+' generator durations changed');
   async function state(t){seeks++;return page.evaluate(async t=>{await renderAt(t);await imgWait();return{output:window.MACRO_OUTPUT_T,active:SCENES.map(s=>s.el.style.display),dom:[...document.querySelectorAll('.e,.it')].filter(e=>e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})).map(e=>[e.textContent,e.style.transform,e.style.opacity,e.parentElement.style.transform]),canvas:[...document.querySelectorAll('canvas')].map(c=>{if(!c.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))return null;const data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<data.length;i+=1021)h=Math.imul(h^data[i],16777619);return h>>>0;})};},t);}
   for(const item of plan){
    const start=item.output_start_frame,n=item.output_end_frame-start;
    const a=(start+Math.floor(n*.37))/60,b=(start+Math.floor(n*.91))/60;
    const first=await state(a),last=await state(b);assert.deepEqual(await state(a),first,family+' '+layout+' '+item.id+' reverse');assert.deepEqual(await state(b),last,family+' '+layout+' '+item.id+' re-entry');
    for(const window of item.motionWindows){
     const outputStart=window.outputStartFrame+start,outputEnd=window.outputEndFrame+start;
     const points=item.time_map,at=f=>{for(let i=1;i<points.length;i++){const p=points[i-1],q=points[i];if(f<=q.output_frame)return p.source+(q.source-p.source)*(f-p.output_frame)/(q.output_frame-p.output_frame);}return points.at(-1).source;};
     assert.ok(Math.abs((at(outputEnd)-at(outputStart))-(outputEnd-outputStart)/60)<=1/60+1e-6,'protected motion slowed down');
     await state(outputStart/60);await state((outputEnd-1)/60);
    }
    await state((item.output_end_frame-1)/60);groups++;
   }
   assert.equal(await page.evaluate(()=>JSON.stringify(SFX)),initialSound,'seeks duplicated SFX');assert.deepEqual(errors,[],family+' '+layout+' browser errors');
   results.push({family,layout,instances:plan.length,endSeconds:plan.at(-1).output_end_frame/60,sfx:sound.length});await page.close();
  }
 }
 assert.equal(groups,192);const report={passed:true,styles:10,sourceGroups:32,layouts:2,cycles:3,instances:groups,seeks,totalTimelineSeconds:totalSeconds,results,scope:'Synthetic replacement images and short copy, system fonts; actual repeated scene code, retimed holds, reversible Canvas/DOM and SFX durations. No human narration/listening acceptance.'};
 if(process.env.ADU_STRESS_RUNTIME_REPORT)fs.writeFileSync(process.env.ADU_STRESS_RUNTIME_REPORT,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}

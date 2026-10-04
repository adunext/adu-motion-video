import assert from 'node:assert/strict';
import fs from 'node:fs';import path from 'node:path';import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';import {spawnSync} from 'node:child_process';
import {chromium} from 'playwright-core';import {chrome} from '../scripts/chrome.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'adu-vibrant-browser-'));let browser,seeks=0;const cases=[];
try{
 browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files','--disable-gpu','--disable-accelerated-2d-canvas','--force-color-profile=srgb']});
 for(const mode of ['source','new','near-cjk','near-latin','hold']){
  const made=spawnSync(process.env.ADU_TEST_PYTHON||'python3',[root+'/tests/vibrant_fixture.py',temp,mode,...(process.env.ADU_VIBRANT_FONTS?[process.env.ADU_VIBRANT_FONTS]:[])],{encoding:'utf8'});assert.equal(made.status,0,made.stderr);
  const dir=made.stdout.trim(),plan=JSON.parse(fs.readFileSync(dir+'/plan.json'));
  const page=await browser.newPage({viewport:{width:1080,height:1920}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(dir+'/index.html').href);await page.evaluate(()=>window.READY);
  const originalSound=await page.evaluate(()=>JSON.stringify(SFX));
  assert.equal(await page.evaluate(()=>SCENES.length),7);
  const sound=JSON.parse(originalSound),source=await page.evaluate(()=>MACRO_SOURCE_SFX);
  assert.equal(sound.length,27);assert.deepEqual(sound.map(x=>x.d).filter(x=>x!==undefined).sort(),source.flat().map(x=>x.d).filter(x=>x!==undefined).sort());
  async function state(t){seeks++;await page.evaluate(async t=>{renderAt(t);await imgWait();},t);return page.evaluate(()=>({clock:MACRO_OUTPUT_T,active:SCENES.map(s=>s.el.style.display),dom:[...document.querySelectorAll('.e')].filter(e=>e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})).map(e=>[e.textContent,e.style.transform,e.style.opacity]),canvas:[...document.querySelectorAll('canvas')].map(c=>{if(!c.checkVisibility())return null;const d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<d.length;i+=1021)h=Math.imul(h^d[i],16777619);return h>>>0;}),src:[...document.images].filter(e=>e.checkVisibility()).map(e=>e.getAttribute('src'))}));}
  for(const item of plan){
   const n=item.output_end_frame-item.output_start_frame,a=(item.output_start_frame+Math.floor(n*.37))/60,b=(item.output_start_frame+Math.floor(n*.92))/60;
   const first=await state(a),last=await state(b);assert.deepEqual(await state(a),first);assert.deepEqual(await state(b),last);
   for(const cue of item.cues||[])for(const delta of [-1,0,1])await state(Math.max(0,Math.min(plan.at(-1).output_end_frame-1,cue.outputFrame+delta))/60);
   await state((item.output_end_frame-1)/60);
  }
  assert.equal(await page.evaluate(()=>[...document.querySelectorAll('.lc')].some(e=>e.checkVisibility())),false,'Unused source opening matte must remain hidden');
  assert.equal(await page.evaluate(()=>JSON.stringify(SFX)),originalSound);assert.deepEqual(errors,[]);
  cases.push({mode,seeks,sfx:sound.length});await page.close();
 }
 const report={passed:true,groups:7,layouts:['portrait'],cases,seeks,fonts:process.env.ADU_VIBRANT_FONTS?'owner-SHA-verified':'system-only',scope:'Synthetic presenter and texture; source-control/new/near-CJK/near-Latin/max-hold reversible DOM/Canvas and SFX. Not new-narration AV acceptance.'};
 if(process.env.ADU_VIBRANT_REPORT)fs.writeFileSync(process.env.ADU_VIBRANT_REPORT,JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}

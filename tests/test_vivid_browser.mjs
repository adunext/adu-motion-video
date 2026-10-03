// Real browser macro playback: new copy/maximum word widths and reversible state.
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import assert from 'node:assert/strict';import {fileURLToPath,pathToFileURL} from 'node:url';import {spawnSync} from 'node:child_process';
import {chromium} from 'playwright-core';import {chrome} from '../scripts/chrome.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'adu-vivid-browser-'));let browser;let seeks=0;
try{
 browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files','--disable-accelerated-2d-canvas','--force-color-profile=srgb']});
 for(const layout of ['landscape','portrait'])for(const copy of ['new','near-cjk','near-latin']){
  const parent=temp+'/'+layout+'-'+copy;const args=[root+'/tests/vivid_fixture.py',parent,layout,copy];if(process.env.VIVID_FONT_SOURCE)args.push(process.env.VIVID_FONT_SOURCE);
  const made=spawnSync('python3',args,{encoding:'utf8'});assert.equal(made.status,0,made.stderr);
  const folder=parent+'/vivid-sticker-performance',manifest=JSON.parse(fs.readFileSync(folder+'/manifest.json')),plan=JSON.parse(fs.readFileSync(folder+'/plan.json'));
  const page=await browser.newPage({viewport:layout==='portrait'?{width:1080,height:1920}:{width:1920,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(folder+'/index.html').href);await page.evaluate(()=>window.READY);assert.deepEqual(await page.evaluate(()=>[CONFIG.width,CONFIG.height]),layout==='portrait'?[1080,1920]:[1920,1080]);
  const sound=await page.evaluate(()=>JSON.stringify(SFX));assert.equal(JSON.parse(sound).length,27);
  const state=async t=>{seeks++;return page.evaluate(async t=>{await renderAt(t);await imgWait();return {output:window.MACRO_OUTPUT_T,dom:[...document.querySelectorAll('.sticker-host .e,.sticker-island,.tkc')].filter(e=>e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})).map(e=>[e.textContent,e.style.transform,e.style.opacity,e.style.filter]),canvas:[...document.querySelectorAll('canvas')].map(c=>{if(!c.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))return null;const data=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<data.length;i+=513)h=Math.imul(h^data[i],16777619);return h>>>0;})};},t);};
  for(let i=0;i<plan.length;i++){
   const item=plan[i],sc=manifest.scenes[i],start=item.output_start_frame/60,n=(item.output_end_frame-item.output_start_frame)/60;
   const a=await state(start+n*.35),b=await state(start+n*.92);assert.deepEqual(await state(start+n*.35),a,layout+' '+copy+' reverse');assert.deepEqual(await state(start+n*.92),b,layout+' '+copy+' repeat');
   for(const cue of sc.cues)for(const offset of [-1/60,.25,.65]){const t=start+cue.at-sc.source.start+offset;if(t>=start&&t<start+n)await state(t);}
  }
  assert.equal(await page.evaluate(()=>JSON.stringify(SFX)),sound);assert.deepEqual(errors,[],layout+' '+copy);
  if(layout==='portrait'){
   await state(20.6);const box=await page.locator('[data-sticker-node=world] .sc').nth(2).locator('.e').last().evaluate(e=>{const b=e.getBoundingClientRect();return[b.left,b.top,b.right,b.bottom];});assert.ok(box[0]>60&&box[2]<1020&&box[3]<1630,'updated container inside portrait safe area');
  }
  await page.close();
 }
 console.log(JSON.stringify({passed:true,layouts:2,copySets:3,groups:3,seeks,sfx:27,fontScope:process.env.VIVID_FONT_SOURCE?'eight-owner-fonts-sha-verified':'system-font',limits:'Silent synthetic presenter/media; no new episode AV acceptance'}));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}

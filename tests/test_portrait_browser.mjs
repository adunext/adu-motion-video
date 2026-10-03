// Synthetic geometry/media regression, using the real macro playback runtime.
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';import assert from 'node:assert/strict';import {pathToFileURL,fileURLToPath} from 'node:url';import {spawnSync} from 'node:child_process';
import {chromium} from 'playwright-core';import {chrome} from '../scripts/chrome.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),temp=fs.mkdtempSync(path.join(os.tmpdir(),'adu-portrait-browser-'));
let browser;
try{
 const made=spawnSync('python3',[root+'/tests/portrait_fixture.py',temp],{encoding:'utf8'});if(made.status)throw Error(made.stderr);
 // Readback switches accelerated Canvas to software after several samples.
 // Use one raster backend throughout this pixel regression.
 browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files','--disable-accelerated-2d-canvas']});
 const placeholder=fs.readFileSync(temp+'/classic-performance/assets/demo-presenter.svg');let groups=0,seeks=0;
 for(const family of fs.readdirSync(temp).filter(n=>fs.existsSync(temp+'/'+n+'/index.html'))){
  const page=await browser.newPage({viewport:{width:1080,height:1920}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.route('**/*',r=>/\.(jpg|jpeg|png|svg|webp)(\?|$)/.test(r.request().url())?r.fulfill({body:placeholder,contentType:'image/svg+xml'}):r.continue());
  await page.goto(pathToFileURL(temp+'/'+family+'/index.html').href);await page.evaluate(()=>window.READY);
  assert.deepEqual(await page.evaluate(()=>[document.querySelector('#stage').offsetWidth,document.querySelector('#stage').offsetHeight]),[1080,1920]);
  const plan=JSON.parse(fs.readFileSync(temp+'/'+family+'/plan.json')),manifest=JSON.parse(fs.readFileSync(temp+'/'+family+'/manifest.json'));
  const sourceAudio=await page.evaluate(()=>JSON.stringify(SFX));
  async function state(t){seeks++;return page.evaluate(async t=>{await renderAt(t);await imgWait();return{output:window.MACRO_OUTPUT_T,scene:SCENES.map(s=>s.el.style.display),nodes:[...document.querySelectorAll('.portrait-island>.e,.portrait-island>.it')].map(e=>{const visible=e.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});return visible?{text:e.textContent,transform:e.style.transform,wrapper:e.parentElement.style.transform,visibility:e.style.visibility,opacity:e.style.opacity}:{visible:false};}),canvases:[...document.querySelectorAll('canvas')].map(c=>{if(!c.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))return null;const b=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let h=2166136261;for(let i=0;i<b.length;i+=257)h=Math.imul(h^b[i],16777619);return h>>>0;})};},t);}
  for(let i=0;i<plan.length;i++){
   const item=plan[i],n=item.output_end_frame-item.output_start_frame,first=(item.output_start_frame+Math.floor(n*.32))/60,last=(item.output_start_frame+Math.floor(n*.9))/60;
   const a=await state(first),b=await state(last);assert.deepEqual(await state(first),a,family+' '+item.sceneId+' reverse seek');assert.deepEqual(await state(last),b,family+' '+item.sceneId+' repeated seek');
   const scene=manifest.scenes[i];
   for(const cue of scene.cues||[]){for(const offset of [-1/60,.25,.65]){const f=item.output_start_frame+Math.round((cue.at-scene.source.start+offset)*60);if(f>=item.output_start_frame&&f<item.output_end_frame)await state(f/60);}}
   groups++;
  }
  assert.equal(await page.evaluate(()=>JSON.stringify(SFX)),sourceAudio,family+' sound events mutated by seeking');
  assert.deepEqual(errors,[],family+' runtime errors');
  if(family==='paper-balance'){
   await state(24.75-manifest.scenes[0].source.start);
   const cards=await page.locator('.g2c').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return [r.left,r.top,r.right,r.bottom];}));
   assert.equal(cards.length,3);for(const [x,y,right,bottom]of cards)assert.ok(x>=60&&right<=1020&&y>=650&&bottom<=1520,'portrait recap cards must stay readable and inside the canvas');
  }
  const html=fs.readFileSync(temp+'/'+family+'/index.html','utf8').replace('<link rel="stylesheet" href="portrait.css">','').replace(/<script src="(?:portrait.js|showcase-layout.js)"><\/script>/,'');
  fs.writeFileSync(temp+'/'+family+'/landscape.html',html);
  await page.goto(pathToFileURL(temp+'/'+family+'/landscape.html').href);await page.evaluate(()=>window.READY);
  assert.equal(await page.evaluate(()=>JSON.stringify(SFX)),sourceAudio,family+' portrait/landscape SFX differ');
  if(family==='classic-performance'){
   const runtime=fs.readFileSync(temp+'/'+family+'/portrait.js','utf8');
   await page.route('**/portrait.js',r=>r.fulfill({body:`window.READY=Promise.resolve(window.READY).then(()=>{const e=[...document.querySelectorAll('.e')].find(e=>e.firstElementChild&&parseFloat(getComputedStyle(e.firstElementChild).fontSize)>=70);e.firstElementChild.textContent='超长标题'.repeat(40);});\n`+runtime,contentType:'text/javascript'}));
   await page.goto(pathToFileURL(temp+'/'+family+'/index.html').href);
   const failure=await page.evaluate(async()=>{try{await READY;return '';}catch(e){return e.message;}});
   assert.match(failure,/headline below 44px/,'oversized changed copy must fail instead of becoming unreadable');
  }
  await page.close();
 }
 assert.equal(groups,29);console.log(JSON.stringify({passed:true,styles:9,groups,seeks,checks:['real macro runtime','native output dimensions','cue neighbourhoods','forward/reverse deterministic DOM and Canvas','same landscape/portrait sound events'],limits:'Synthetic images; system-font geometry, no real presenter or narration/music listening acceptance'}));
}finally{if(browser)await browser.close();fs.rmSync(temp,{recursive:true,force:true});}

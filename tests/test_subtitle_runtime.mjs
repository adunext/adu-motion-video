import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright-core';
import {chrome} from '../scripts/chrome.mjs';
const directory=fs.mkdtempSync(path.join(os.tmpdir(),'adu-caption-quality-'));
let browser;
try {
  browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files']});
  let checks=0;
  for(const geometry of [[1080,1920,null],[1080,1920,{bottomRatio:.35,leftRatio:.08,rightRatio:.18}],[1920,1080,null]]) {
    const [width,height,position]=geometry;
    const file=path.join(directory,`${width}-${position?.bottomRatio??0}.html`);
    fs.writeFileSync(file,`<!doctype html><style>body{margin:0}.native-subtitles{bottom:110px!important;top:auto!important;left:68px!important;right:68px!important}</style><div id="ov"></div><script>const CONFIG=${JSON.stringify({width,height,subtitlePreset:'standard',subtitlePosition:position})};const SUBS=[{id:'a',t0:0,t1:1,zh:'呃，不是四项。\\n<内容>& é👩‍💻',en:'No four items.\\nKeep literal < and &.'},{id:'b',t0:.5,t1:1.5,zh:'重叠字幕也完整显示',en:'Overlap remains.'}];</script><script src="${pathToFileURL(path.resolve('template/subtitles.js'))}"></script>`);
    const page=await browser.newPage({viewport:{width,height}});await page.goto(pathToFileURL(file).href);await page.evaluate(()=>document.fonts.ready);
    for(const time of [0,.1,.6,.999,1,1.49,1.5,.6]) {
      const state=await page.evaluate(t=>{OVERLAY(t);const b=document.querySelector('.native-subtitles'),r=b.getBoundingClientRect();return {text:b.textContent,opacity:b.style.opacity,cues:JSON.parse(b.dataset.cueIds||'[]'),cssTop:b.style.top,rect:{left:r.left,right:r.right,top:r.top,bottom:r.bottom},html:b.innerHTML};},time);
      if(time===1.5){assert.equal(state.opacity,'0');continue;}
      assert.equal(state.cues.includes('a'),time<1);assert.equal(state.cues.includes('b'),time>=.5);
      if(time<1){assert.ok(state.text.includes('<内容>& é👩‍💻'));assert.ok(!state.html.includes('<内容>'));assert.ok(state.text.includes('\n'));}
      if(height>width){const ratios=position??{bottomRatio:.18,leftRatio:.06,rightRatio:.15};assert.ok(state.rect.bottom<=height*(1-ratios.bottomRatio)+.1);assert.ok(state.rect.left>=width*ratios.leftRatio-.1);assert.ok(state.rect.right<=width*(1-ratios.rightRatio)+.1);}
      else {assert.equal(state.cssTop,'872px');assert.ok(state.rect.top>=862&&state.rect.top<=872);}
      assert.ok(state.rect.top>=0);checks++;
    }
    const formatted=await page.evaluate(()=>{SUBS.push({id:'formatted',t0:2,t1:3,zh:'<b>重点</b> <img src=x onerror=alert(1)> <i>斜体</i> <u>下划线</u>',formatting:'srt-basic'});CONFIG.subtitleXByStart={'2':1500};OVERLAY(2.2);const b=document.querySelector('.native-subtitles');return {bold:b.querySelector('b')?.textContent,italic:b.querySelector('i')?.textContent,underline:b.querySelector('u')?.textContent,img:!!b.querySelector('img'),text:b.textContent,transform:b.style.transform};});
    assert.equal(formatted.bold,'重点');assert.equal(formatted.italic,'斜体');assert.equal(formatted.underline,'下划线');assert.equal(formatted.img,false);assert.ok(formatted.text.includes('<img src=x onerror=alert(1)>'));
    if(height>width)assert.ok(formatted.transform.startsWith('translate(0px,'));checks++;
    await page.close();
  }
  console.log(JSON.stringify({passed:true,checks,scope:'Caption literal text, overlapping half-open cues, custom/default portrait block bounds, legacy CSS override, safe SRT formatting, ratio-mode absolute-X rejection, landscape preset and reverse seek. No artistic AV acceptance.'}));
} finally {if(browser)await browser.close();fs.rmSync(directory,{recursive:true,force:true});}

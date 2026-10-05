import assert from 'node:assert/strict';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {chromium} from 'playwright-core';
import {chrome} from '../scripts/chrome.mjs';
const project=process.argv[2], failures=[];
const browser=await chromium.launch({executablePath:chrome(),args:['--allow-file-access-from-files','--disable-gpu']});
try {
  const page=await browser.newPage();
  page.on('pageerror',e=>failures.push(e.message));page.on('requestfailed',r=>failures.push(r.url()));
  await page.route('**/*',r=>/^https?:/.test(r.request().url())?r.abort():r.continue());
  await page.goto(pathToFileURL(path.join(project,'index.html')).href);
  const receipt=await page.evaluate(async()=>{
    const sample='兼容字体 ABC 123', loaded={};
    for(const family of ['Adu Sans','Adu Mono','Geist','Geist Mono','YSBT','SFM']) {
      const faces=await document.fonts.load(`600 42px '${family}'`,sample);
      loaded[family]=faces.map(f=>({family:f.family,status:f.status}));
    }
    await document.fonts.ready;
    const bounds=document.querySelector('#sample').getBoundingClientRect();
    return {loaded,width:bounds.width,height:bounds.height};
  });
  assert.deepEqual(failures,[]);
  for(const rows of Object.values(receipt.loaded))assert.ok(rows.length&&rows.every(f=>f.status==='loaded'));
  assert.ok(receipt.height>20);
  console.log(JSON.stringify(receipt));
} finally {await browser.close();}

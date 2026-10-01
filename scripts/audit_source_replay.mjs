#!/usr/bin/env node
/** Compare source-clock DOM states, scene boundaries and SFX after extraction.
 * This is sampled structural fidelity, not a substitute for continuous AV review.
 */
import { chromium } from 'playwright-core';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { chrome } from './chrome.mjs';

const [source,replay,output,strideArg='6']=process.argv.slice(2);
if(!source||!replay||!output)throw Error('Usage: audit_source_replay.mjs SOURCE.html REPLAY.html NEW-report.json [strideFrames]');
const stride=Number(strideArg);
if(!Number.isInteger(stride)||stride<1)throw Error('Frame stride must be a positive integer');
const hash=value=>createHash('sha256').update(value).digest('hex');
let browser;
try{
  browser=await chromium.launch({executablePath:chrome(),headless:true,args:['--allow-file-access-from-files']});
  const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,serviceWorkers:'block'});
  await context.route('**/*',r=>/^https?:/i.test(r.request().url())?r.abort():r.continue());
  const errors=[];
  async function pageFor(file){
    const page=await context.newPage();
    page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
    await page.goto(pathToFileURL(file).href,{waitUntil:'load'});
    await page.evaluate(async()=>{await window.READY;await document.fonts.ready;});
    if(errors.length)throw Error(errors.join('\n'));
    return page;
  }
  const original=await pageFor(source),copy=await pageFor(replay);
  const header=async p=>p.evaluate(()=>({end:window.END||CONFIG.end,fps:CONFIG.fps,
    scenes:SCENES.map(s=>({start:s.s,end:s.e,opt:s.opt})),sfx:window.SFX}));
  const [before,after]=await Promise.all([header(original),header(copy)]);
  if(JSON.stringify(before)!==JSON.stringify(after))throw Error('Source scene boundaries/options/SFX changed');
  const frames=Math.round(before.end*before.fps),indices=new Set([0,frames-1]);
  for(let f=0;f<frames;f+=stride)indices.add(f);
  for(const sc of before.scenes)for(const t of[sc.start,sc.end])for(const delta of[-1,0,1]){
    const f=Math.round(t*before.fps)+delta;if(f>=0&&f<frames)indices.add(f);
  }
  async function state(page,f){
    return page.evaluate(async({f,fps})=>{
      await window.renderAt(f/fps);if(window.imgWait)await window.imgWait();
      return ['world','fx','ov'].map(id=>document.getElementById(id)?.outerHTML||'').join('\n');
    },{f,fps:before.fps});
  }
  const sampled=[];let changed=0;const differences=[];
  for(const f of [...indices].sort((a,b)=>a-b)){
    const [a,b]=await Promise.all([state(original,f),state(copy,f)]);
    const same=a===b;if(!same){changed++;if(differences.length<12)differences.push({frame:f,source:a.slice(0,1000),replay:b.slice(0,1000)});}
    sampled.push({frame:f,sourceSha256:hash(a),replaySha256:hash(b),same});
  }
  // Repeat reverse seeks to catch stateful closures that happened to match a
  // forward playback but retained different transforms when revisited.
  const reverse=[];
  for(const f of [...indices].sort((a,b)=>b-a).filter((_,i)=>i%31===0)){
    const [a,b]=await Promise.all([state(original,f),state(copy,f)]);reverse.push({frame:f,same:a===b});if(a!==b)changed++;
  }
  if(errors.length)throw Error(errors.join('\n'));
  const result={schema:'adu-source-replay-audit/1',source,replay,frames,fps:before.fps,strideFrames:stride,
    sourceScenes:before.scenes.length,sfx:before.sfx.length,sceneAndSfxEqual:true,
    sampledStates:sampled.length,reverseSeeks:reverse.length,changedStates:changed,
    status:changed?'different':'sampled-structure-equal',limits:['DOM state at sampled frames and reverse seeks only; raster and continuous final audiovisual review remain separate.'],
    sourceEntrySha256:hash(readFileSync(source)),replayEntrySha256:hash(readFileSync(replay)),sampled,reverse,differences};
  writeFileSync(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify({sourceScenes:result.sourceScenes,sfx:result.sfx,sampledStates:result.sampledStates,changedStates:changed,status:result.status}));
  if(changed)process.exitCode=1;
}finally{await browser?.close();}

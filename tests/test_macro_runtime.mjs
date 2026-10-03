import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

test('reused opening retains early SFX and later scenes retain pre-roll', async () => {
  const element=()=>({style:{},appendChild(){}});
  const ctx={console,Math,Number,Promise}; ctx.window=ctx;
  ctx.document={createElement:element,fonts:{ready:Promise.resolve()},images:[]};
  const els=new Map();ctx.$=id=>{if(!els.has(id))els.set(id,element());return els.get(id);};
  ctx.clamp=x=>Math.min(1,Math.max(0,x));ctx.lerp=(a,b,p)=>a+(b-a)*p;
  ctx.CONFIG={};ctx.SFX=[];
  ctx.SCENES=[0,1].map(()=>({el:element(),opt:{},update(){},cam(){return null;}}));
  ctx.MACRO_PLAN={fps:60,end_frame:600,scenes:[
    {output_start_frame:0,output_end_frame:300,time_map:[{source:3.3,output_frame:0},{source:8.3,output_frame:300}]},
    {output_start_frame:300,output_end_frame:600,time_map:[{source:20,output_frame:300},{source:25,output_frame:600}]}]};
  ctx.MACRO_SOURCE_SFX=[[{t:3.25,type:'swoosh',d:.5}],[{t:19.95,type:'whoosh',d:.5}]];
  vm.runInNewContext(fs.readFileSync(new URL('../scripts/macro_runtime.js',import.meta.url),'utf8'),ctx);
  await ctx.READY;
  assert.equal(ctx.SFX.length,2);
  assert.equal(ctx.SFX[0].t,0);
  assert.equal(ctx.SFX[0].d,.5);
  assert.equal(ctx.SFX[1].t,4.95);
  assert.equal(ctx.SFX[1].d,.5);
});

test('square presenter crop follows the new narration clock and contains the face', () => {
  const source=fs.readFileSync(new URL('../packs/anim3/scenes.js',import.meta.url),'utf8').split('/* ---------- S1')[0];
  const face={cx:.42,cy:.70,h:.22};
  const ctx={CONFIG:{end:8},PACK_OUTPUT_TIME:2.5,Math};ctx.window=ctx;
  ctx.clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));ctx.place=()=>{};
  ctx.talkSrc=t=>{assert.equal(t,2.5);return 'new-frame.jpg'};
  ctx.setFrame=(im,src)=>{im.src=src};ctx.faceAt=t=>{assert.equal(t,2.5);return face};
  vm.runInNewContext(source,ctx);
  const e={_faceCrop:true,_img:{style:{}},firstChild:{offsetWidth:300,offsetHeight:300}};
  ctx.camAt(e,39,{x:960,y:600});
  const css=e._img.style.cssText;
  const value=key=>Number(css.match(new RegExp(`(?:^|;)${key}:(-?[0-9.]+)px`))[1]);
  const top=value('top')+(face.cy-face.h/2)*value('height');
  const bottom=value('top')+(face.cy+face.h/2)*value('height');
  assert.ok(top>50 && bottom<300,`face ${top}..${bottom} must fit below the label`);
  assert.ok(Math.abs(value('width')/value('height')-720/1280)<.001);
  assert.equal(e._img.src,'new-frame.jpg');
});

test('an extended reading gap shifts an SFX onset without stretching its generator', async () => {
  const element=()=>({style:{},appendChild(){}});
  const ctx={console,Math,Number,Promise};ctx.window=ctx;
  ctx.document={createElement:element,fonts:{ready:Promise.resolve()},images:[]};
  const els=new Map();ctx.$=id=>{if(!els.has(id))els.set(id,element());return els.get(id);};
  ctx.clamp=x=>Math.min(1,Math.max(0,x));ctx.lerp=(a,b,p)=>a+(b-a)*p;
  ctx.CONFIG={};ctx.SFX=[];
  ctx.SCENES=[{el:element(),opt:{},update(){},cam(){return null;}}];
  ctx.MACRO_PLAN={fps:60,end_frame:600,scenes:[{output_start_frame:0,output_end_frame:600,
    time_map:[{source:0,output_frame:0},{source:1,output_frame:60},
              {source:2,output_frame:480},{source:4,output_frame:600}]}]};
  ctx.MACRO_SOURCE_SFX=[[{t:.9,type:'typing',d:.5},{t:2.2,type:'hit',d:.2}]];
  vm.runInNewContext(fs.readFileSync(new URL('../scripts/macro_runtime.js',import.meta.url),'utf8'),ctx);
  await ctx.READY;
  assert.deepEqual(Array.from(ctx.SFX,e=>[e.t,e.d]),[[.9,.5],[8.2,.2]]);
});

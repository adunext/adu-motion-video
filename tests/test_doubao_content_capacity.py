"""Bounded copy layout; private source media and fonts are never test fixtures.

Browser tests use the supported macOS system fallback. Owner-supplied Geist
font fidelity and no-person silent display-copy samples are a separate review.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from adaptation import load_profile, validate_profile
from build_macro_project import bind_authored_block, pack_scene_parts
from adapt_project import slot_bindings

PACK = ROOT / 'packs/doubao-console-performance/0.1.2-candidate'
PREVIOUS = ROOT / 'packs/doubao-console-performance/0.1.1-candidate'


class DoubaoCapacityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pack = json.loads((PACK / 'manifest.json').read_text())
        cls.previous = json.loads((PREVIOUS / 'manifest.json').read_text())

    def test_fingerprints_spans_profile_and_original_action_contracts(self):
        for directory, pack in ((PACK, self.pack), (PREVIOUS, self.previous)):
            _, blocks = pack_scene_parts(directory, pack)
            for scene, body in zip(pack['scenes'], blocks):
                self.assertEqual(hashlib.sha256(body.encode()).hexdigest(), scene['sourceBlockSha256'])
                for slot in scene['slots']:
                    for span in slot.get('sourceSpans', []):
                        self.assertEqual(body[span['start']:span['end']], slot['sourceText'])
        profile = load_profile(self.pack, ROOT / 'adaptation-profiles')
        self.assertTrue(validate_profile(profile, self.pack)['ready'])
        self.assertEqual(profile['pack']['version'], '0.1.2-candidate')
        for old, new in zip(self.previous['scenes'], self.pack['scenes']):
            for key in ('source', 'minFrames', 'maxHoldFrames', 'motionWindows', 'cues', 'boundaries'):
                self.assertEqual(new[key], old[key], (new['id'], key))
        self.assertEqual((PACK / 'audio_timeline.json').read_bytes(), (PREVIOUS / 'audio_timeline.json').read_bytes())
        self.assertEqual(self.pack['externalFonts'], self.previous['externalFonts'])

    def test_every_maximum_length_binding_stays_bound_and_valid(self):
        _, blocks = pack_scene_parts(PACK, self.pack)
        for scene, body in zip(self.pack['scenes'], blocks):
            text_slots = [slot for slot in scene['slots'] if slot['type'] == 'text']
            values = {slot['id']: '全' * slot['maxChars'] for slot in text_slots}
            checked, _ = slot_bindings({**scene, 'slots': text_slots}, {'slots': values}, ROOT, None)
            bound, _ = bind_authored_block(body, scene, checked, scene['id'] + '-capacity')
            for slot in text_slots:
                self.assertIn(values[slot['id']], bound)

    @unittest.skipUnless(sys.platform == 'darwin' and shutil.which('node'), 'Supported macOS browser/system-font geometry check')
    def test_browser_maximum_cjk_latin_readability_and_reverse_seek(self):
        if not (ROOT / 'node_modules/playwright-core/index.mjs').is_file():
            self.skipTest('Install the project browser-test dependency before this optional raster check')
        _, blocks = pack_scene_parts(PACK, self.pack)
        with tempfile.TemporaryDirectory(prefix='adu-doubao-capacity-') as temp:
            directory = Path(temp)
            (directory / 'assets').mkdir()
            (directory / 'assets/test.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="1280"><rect width="720" height="1280" fill="#10243a"/></svg>')
            shutil.copy2(directory / 'assets/test.svg', directory / 'assets/demo-presenter.svg')
            (directory / 'style.css').write_text((PACK / 'style.css').read_text() + '\n.doubao-host [data-doubao-node="tk"]{display:none!important}\n')
            shutil.copy2(PACK / 'lib.js', directory / 'lib.js')
            configuration = {'demo': True, 'fps': 60, 'end': 65, 'talkFrames': 0, 'race': {'keys': [0, 65, 66], 'labels': ['test', 'end']}}
            fixture_labels = []
            for kind in ('cjk', 'latin'):
                generated = []
                for scene, body in zip(self.pack['scenes'], blocks):
                    values = {slot['id']: ('全' if kind == 'cjk' else 'W') * slot['maxChars']
                              for slot in scene['slots'] if slot['type'] == 'text'}
                    # Exercise both wrapped and short states of the same status
                    # element; reverse seeks must restore the same geometry.
                    values['status-done'] = 'READY ✓'
                    if 'status-done' not in {slot['id'] for slot in scene['slots']}:
                        values.pop('status-done')
                    bound, _ = bind_authored_block(body, scene, values, scene['id'] + '-' + kind)
                    for slot in scene['slots']:
                        if slot['type'] == 'image':
                            bound = bound.replace(Path(slot['sourceAsset']).name, 'test.svg')
                    generated.append(bound)
                    fixture_labels.append((kind, scene['id']))
                (directory / f'{kind}.js').write_text('\n'.join(generated))
                (directory / f'{kind}.html').write_text('''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="style.css"><div id="stage"><div id="world"></div><div id="fx"></div><div id="ov"></div></div><script>window.CONFIG=''' + json.dumps(configuration) + ''';window.PACK_BRAND_HTML='TYPE QA';window.PACK_PRESENTER_LABEL='NO PERSON';window.DOUBAO_OUTPUT_VOX=Array(4000).fill(0);window.MACRO_PLAN={end_frame:3900,scenes:[{output_start_frame:0},{output_start_frame:234},{output_start_frame:778}]};window.MACRO_OUTPUT_T=0;</script><script src="lib.js"></script><script src="''' + kind + '''.js"></script><script>window.renderQa=(i,t)=>{SCENES.forEach((s,n)=>s.el.style.display=n===i?'block':'none');window.MACRO_OUTPUT_T=t;SCENES[i].update(t);};</script>''')
            script = r'''
import fs from 'node:fs';import {pathToFileURL} from 'node:url';
import assert from 'node:assert/strict';
const [root,dir]=process.argv.slice(2);
const {chromium}=await import(pathToFileURL(root+'/node_modules/playwright-core/index.mjs'));
const {chrome}=await import(pathToFileURL(root+'/scripts/chrome.mjs'));
let executable;try{executable=chrome();}catch(e){console.log('SKIP: '+e.message);process.exit(77);}
const browser=await chromium.launch({executablePath:executable,headless:true,args:['--allow-file-access-from-files']});
try {
 for(const kind of ['cjk','latin']){
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(dir+'/'+kind+'.html').href);
  await page.evaluate(()=>document.fonts.ready);
  async function sample(i,t){return page.evaluate(async({i,t})=>{
   window.renderQa(i,t);await document.fonts.ready;
   const host=document.querySelectorAll('.doubao-host')[i];
   const textBox=e=>{const r=document.createRange();r.selectNodeContents(e);return r.getBoundingClientRect().toJSON();};
   const fit=[...host.querySelectorAll('[data-type-fit]')].map(e=>({label:e.dataset.typeFit,font:parseFloat(getComputedStyle(e).fontSize),width:e.scrollWidth,maxWidth:+e.dataset.typeMaxWidth,box:textBox(e),style:e.style.cssText,text:e.textContent}));
   const manual=[...host.querySelectorAll('div')].find(e=>e.style.width==='560px'&&e.style.height==='640px')?.getBoundingClientRect().toJSON();
   const status=host.querySelector('.st')?.parentElement.getBoundingClientRect().toJSON();
   const output=host.querySelectorAll('.chipA')[2]?.getBoundingClientRect().toJSON();
   const chat=host.querySelector('.gl')?.getBoundingClientRect().toJSON();
   return {fit,manual,status,output,chat};
  },{i,t});}
  for(const [i,t] of [[0,3.7],[1,26.6],[2,56],[2,61.8]]){
   const s=await sample(i,t);
   for(const f of s.fit){
    const min=f.label.startsWith('fusion-title')?52:f.label.startsWith('manual-title')?48:f.label==='manual-name'?28:f.label.startsWith('status-value')?22:f.label.startsWith('status-label')?12:f.label.startsWith('chat-step')?18:12;
    assert(f.font>=min,`${kind} ${f.label}: below readable minimum`);
    // A title's block width is shared with its sibling; its ink is measured
    // separately below. Wrapped regions must not scroll horizontally.
    if(!f.label.includes('title'))assert(f.width<=f.maxWidth+1,`${kind} ${f.label}: ${f.width}>${f.maxWidth}`);
    if(f.label.startsWith('manual-title'))assert(f.box.right<=s.manual.x-8,`${kind} ${f.label}: title meets manual`);
    if(f.label.startsWith('chat-step'))assert(f.box.right<=s.chat.x+1,`${kind} ${f.label}: step enters chat`);
    if(f.label==='manual-name')assert(f.box.right<s.manual.right-8&&f.box.bottom<s.manual.bottom,`${kind}: name clipped`);
   }
   if(i===0)assert(s.status.right<s.output.x-8,`${kind}: status meets output chip`);
  }
  const first=await sample(0,2),finished=await sample(0,3.7),again=await sample(0,2),finishedAgain=await sample(0,3.7);
  assert.deepEqual(first,again,`${kind}: wrapped status reverse seek drift`);
  assert.deepEqual(finished,finishedAgain,`${kind}: short status reverse seek drift`);
  assert.deepEqual(errors,[]);
  const rejection=await page.evaluate(()=>{
   renderQa(0,3.7);document.querySelectorAll('.doubao-host')[0].querySelector('.l1').textContent='W'.repeat(120);
   try{renderQa(0,3.7);return 'unexpected pass';}catch(e){return e.message;}
  });
  assert.match(rejection,/minimum 52px; shorten this slot/,`${kind}: hard capacity must reject rather than shrink forever`);
  await page.close();
 }
 console.log('PASS: maximum CJK/Latin widths, readable font floors, reserved regions, reverse seeks');
}finally{await browser.close();}
'''
            (directory / 'probe.mjs').write_text(script)
            run = subprocess.run(['node', str(directory / 'probe.mjs'), str(ROOT), str(directory)], capture_output=True, text=True)
            if run.returncode == 77:
                self.skipTest(run.stdout.strip())
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()

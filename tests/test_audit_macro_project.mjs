import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { chrome } from '../scripts/chrome.mjs';
import { collectAuditFrames, representativeFrames } from '../scripts/audit_macro_project.mjs';

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const AUDITOR = path.join(ROOT, 'scripts', 'audit_macro_project.mjs');

const plan = {
  pack: 'fixture', fps: 30, width: 64, height: 64, end_frame: 12,
  scenes: [
    { output_start_frame: 0, output_end_frame: 6,
      time_map: [{ source: 0, output_frame: 0 }, { source: .1, output_frame: 3 }, { source: .2, output_frame: 6 }] },
    { output_start_frame: 6, output_end_frame: 12,
      time_map: [{ source: .2, output_frame: 6 }, { source: .3, output_frame: 9 }, { source: .4, output_frame: 12 }] },
  ],
};

test('samples each clock knot on adjacent frames, midpoints, and scene edges', () => {
  const frames = collectAuditFrames(plan);
  assert.deepEqual(frames.map(x => x.frame), [...Array(12).keys()]);
  assert.ok(frames.find(x => x.frame === 2).reasons.some(x => x.startsWith('knot:0:1:-1')));
  assert.ok(frames.find(x => x.frame === 10).reasons.some(x => x.startsWith('knot:1:1:1')));
  assert.deepEqual(representativeFrames(plan), [0, 2, 8, 11]);
});

test('browser audit accepts deterministic local media and rejects a broken image', t => {
  try { chrome(); } catch { t.skip('No local Chrome/Chromium is installed'); return; }
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'adu-macro-audit-test-'));
  try {
    fs.writeFileSync(path.join(directory, 'macro_plan.json'), JSON.stringify(plan));
    fs.writeFileSync(path.join(directory, 'talk.svg'), '<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"><rect width="8" height="8" fill="blue"/></svg>');
    const html = (broken, hideFirstPresenter = false) => `<!doctype html><html><head><style>
      html,body{margin:0;width:64px;height:64px}#stage,#world,.sc{position:absolute;inset:0}
      .sc{display:none}.cam{position:absolute;left:4px;top:4px;width:20px;height:20px}
      img{width:20px;height:20px}
      </style></head><body><div id="stage"><div id="world">
      <div class="sc"><div class="cam"><img src="${broken ? 'missing.svg' : 'talk.svg'}"></div><span>A</span></div>
      <div class="sc"><div class="cam"><img src="${broken ? 'missing.svg' : 'talk.svg'}"></div><span>B</span></div>
      </div></div><script>
      window.renderAt=t=>{const f=Math.floor(t*30+1e-6);document.querySelectorAll('.sc').forEach((e,i)=>{
        e.style.display=i===(f<6?0:1)?'block':'none';e.style.transform='translateX('+((f%6)*2)+'px)';
        e.querySelector('img').style.opacity=${hideFirstPresenter ? 'f===0?0:1' : '1'};});};
      window.READY=Promise.resolve();window.renderAt(0);document.title='done';
      </script></body></html>`;
    fs.writeFileSync(path.join(directory, 'index.html'), html(false));
    const goodFile = path.join(directory, 'good.json');
    const good = spawnSync(process.execPath, [AUDITOR, directory, '--output', goodFile], { encoding: 'utf8', timeout: 90000 });
    const report = JSON.parse(fs.readFileSync(goodFile, 'utf8'));
    const goodSummary = JSON.parse(good.stdout);
    assert.equal(goodSummary.framesSampled, 12);
    assert.equal(goodSummary.reportFile, goodFile);
    assert.ok(['passed', 'needs-raster-review'].includes(report.status), good.stdout + good.stderr);
    assert.equal(report.issues.length, 0, good.stdout + good.stderr);
    assert.equal(good.status, report.ok ? 0 : 1);
    assert.equal(report.framesSampled, 12);
    assert.equal(report.freshCompared, 4);
    assert.ok(report.visibleImageChecks > 0);

    fs.writeFileSync(path.join(directory, 'index.html'), html(false, true));
    const hiddenFile = path.join(directory, 'hidden.json');
    const hidden = spawnSync(process.execPath, [AUDITOR, directory, '--output', hiddenFile], { encoding: 'utf8', timeout: 90000 });
    const hiddenReport = JSON.parse(fs.readFileSync(hiddenFile, 'utf8'));
    assert.equal(hidden.status, 1, hidden.stdout + hidden.stderr);
    assert.ok(hiddenReport.issues.some(x => x.kind === 'first-frame-presenter'));
    assert.equal(hiddenReport.freshCompared, 4, 'local first-frame issue must not skip seek comparison');

    fs.writeFileSync(path.join(directory, 'index.html'), html(true));
    const badFile = path.join(directory, 'bad.json');
    const bad = spawnSync(process.execPath, [AUDITOR, directory, '--output', badFile], { encoding: 'utf8', timeout: 90000 });
    assert.equal(bad.status, 1, bad.stdout + bad.stderr);
    const failure = JSON.parse(fs.readFileSync(badFile, 'utf8'));
    assert.equal(failure.ok, false);
    assert.ok(failure.issues.some(x => /image|Resource request failed/i.test(x.message || '')));
  } finally { fs.rmSync(directory, { recursive: true, force: true }); }
});

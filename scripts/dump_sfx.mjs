// 从 scenes.js 导出音效点 + 片长 → sfx.json
// 用法：node dump_sfx.mjs <abs/index.html> <out/sfx.json>
import { chromium } from 'playwright-core';
import fs from 'fs';
import { chrome } from './chrome.mjs';
const b = await chromium.launch({ executablePath: chrome(), args: ['--allow-file-access-from-files'] });
const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
await p.goto('file://' + process.argv[2]); await p.waitForFunction(() => document.title === 'done', null, { timeout: 90000 });
const d = await p.evaluate(() => ({ end: window.END || CONFIG.end, sfx: window.SFX }));
fs.writeFileSync(process.argv[3], JSON.stringify(d)); console.log(d.sfx.length, 'cues, end', d.end); await b.close();

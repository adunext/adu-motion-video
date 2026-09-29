// Collect local scene sound cues and duration; do not install dependencies.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import { chrome } from './chrome.mjs';
const [entry, output] = process.argv.slice(2);
if (!entry || !output) throw Error('Usage: dump_sfx.mjs PROJECT/index.html PROJECT/sfx.json');
let browser;
try {
  browser = await chromium.launch({ executablePath: chrome(), args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('requestfailed', request => errors.push(`Resource failed: ${request.url()}`));
  await page.route('**/*', route => /^https?:/i.test(route.request().url()) ? route.abort() : route.continue());
  await page.goto(pathToFileURL(path.resolve(entry)).href);
  await page.waitForFunction(() => window.READY || document.title === 'done', null, {timeout: 90000});
  await page.evaluate(async () => { await window.READY; if (window.imgWait) await window.imgWait(); });
  if (errors.length) throw Error(errors.join('\n'));
  const data = await page.evaluate(() => ({end: Number(window.END ?? window.CONFIG?.end), sfx: window.SFX || []}));
  if (!Number.isFinite(data.end) || data.end <= 0 || !Array.isArray(data.sfx)) throw Error('Invalid runtime END/SFX');
  fs.writeFileSync(output, JSON.stringify(data));
  console.log(data.sfx.length, 'cues, end', data.end);
} finally { await browser?.close(); }

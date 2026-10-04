#!/usr/bin/env node
/** Browser acceptance for a generated full-scene macro project.
 *
 * Every authored clock knot is sampled at -1/0/+1 output frame, as is each
 * interval midpoint. Representative frames are then rendered again from a
 * fresh page and compared with the random-seek result. This catches stateful
 * scene updates, missing media, broken images and silent script failures.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { chromium } from 'playwright-core';
import { chrome } from './chrome.mjs';
import {measureTypography} from './typography_audit.mjs';

const HELP = `Usage: node scripts/audit_macro_project.mjs PROJECT [--output NEW.json]
       [--screenshots NEW_DIR] [--browser CHROME_PATH]
Checks every plan knot +/-1 frame and interval midpoint, then compares one
fresh-load render per scene with a deterministic random-seek render. Local
assets only; no dependencies, browsers, or remote media are installed.`;

function parse(argv) {
  if (!argv.length || argv.includes('--help')) { console.log(HELP); return null; }
  const project = path.resolve(argv.shift());
  const opt = { project };
  while (argv.length) {
    const key = argv.shift();
    if (!['--output', '--screenshots', '--browser'].includes(key) || !argv.length)
      throw Error(`Unknown or incomplete option: ${key}`);
    opt[key.slice(2)] = argv.shift();
  }
  opt.entry = path.join(project, 'index.html');
  opt.planFile = path.join(project, 'macro_plan.json');
  for (const file of [opt.entry, opt.planFile])
    if (!fs.existsSync(file) || !fs.statSync(file).isFile()) throw Error(`Missing generated project file: ${file}`);
  for (const name of ['output', 'screenshots']) if (opt[name]) {
    opt[name] = path.resolve(opt[name]);
    if (fs.existsSync(opt[name])) throw Error(`Refusing to overwrite: ${opt[name]}`);
    if (!fs.existsSync(path.dirname(opt[name]))) throw Error(`Output parent is missing: ${opt[name]}`);
  }
  return opt;
}

function integer(value, label) {
  if (!Number.isInteger(value)) throw Error(`${label} must be an integer`);
  return value;
}

export function collectAuditFrames(plan) {
  const fps = integer(plan.fps, 'plan.fps');
  const end = integer(plan.end_frame ?? plan.durationFrames, 'plan.end_frame');
  if (fps < 1 || end < 1 || !Array.isArray(plan.scenes) || !plan.scenes.length)
    throw Error('Invalid macro plan: fps, end frame and scenes are required');
  const frames = new Map();
  const add = (frame, reason) => {
    if (!Number.isInteger(frame) || frame < 0 || frame >= end) return;
    if (!frames.has(frame)) frames.set(frame, new Set());
    frames.get(frame).add(reason);
  };
  for (const [i, scene] of plan.scenes.entries()) {
    const start = integer(scene.output_start_frame ?? scene.startFrame, `scene ${i} start`);
    const stop = integer(scene.output_end_frame ?? scene.endFrame, `scene ${i} end`);
    if (!(0 <= start && start < stop && stop <= end)) throw Error(`Invalid scene ${i} frame range`);
    for (const f of [start, start + 1, stop - 2, stop - 1, Math.floor((start + stop - 1) / 2)])
      add(f, `scene:${i}`);
    const map = scene.time_map || (scene.knots || []).map(k => ({ output_frame: k.outputFrame }));
    if (!Array.isArray(map) || map.length < 2) throw Error(`Scene ${i} has no source/output time map`);
    const knots = map.map((point, j) => integer(point.output_frame, `scene ${i} knot ${j}`));
    if (knots[0] !== start || knots.at(-1) !== stop) throw Error(`Scene ${i} time map misses its boundaries`);
    for (let j = 0; j < knots.length; j++) {
      if (j && knots[j] <= knots[j - 1]) throw Error(`Scene ${i} has non-increasing time map`);
      for (const offset of [-1, 0, 1]) {
        const f = knots[j] + offset;
        if (f >= start && f < stop) add(f, `knot:${i}:${j}:${offset}`);
      }
      if (j) add(Math.floor((knots[j - 1] + knots[j]) / 2), `interval:${i}:${j - 1}`);
    }
  }
  return [...frames].sort((a, b) => a[0] - b[0]).map(([frame, reasons]) => ({ frame, reasons: [...reasons] }));
}

export function representativeFrames(plan) {
  const samples = new Set([0, integer(plan.end_frame ?? plan.durationFrames, 'end') - 1]);
  for (const scene of plan.scenes) {
    const start = scene.output_start_frame ?? scene.startFrame;
    const end = scene.output_end_frame ?? scene.endFrame;
    samples.add(Math.floor((start + end - 1) / 2));
  }
  return [...samples].sort((a, b) => a - b);
}

function shuffled(items) {
  const result = [...items];
  let state = 0x5eed1234;
  const random = () => { state ^= state << 13; state ^= state >>> 17; state ^= state << 5; return (state >>> 0) / 4294967296; };
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

function digest(value) { return crypto.createHash('sha256').update(value).digest('hex'); }

async function pixelDifference(page, first, second) {
  return page.evaluate(async ([a, b]) => {
    const decoded = async base64 => {
      const image = new Image(); image.src = `data:image/png;base64,${base64}`;
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
      const context = canvas.getContext('2d', { willReadFrequently: true });
      context.drawImage(image, 0, 0);
      return { width: canvas.width, height: canvas.height,
        pixels: context.getImageData(0, 0, canvas.width, canvas.height).data };
    };
    const x = await decoded(a), y = await decoded(b);
    if (x.width !== y.width || x.height !== y.height) return { geometryMismatch: true };
    let changedChannels = 0, maxChannelDifference = 0, totalAbsoluteDifference = 0;
    let changedPixels = 0, pixelsOverOne = 0, pixelsOverTen = 0;
    const overOneBounds = [x.width, x.height, -1, -1];
    for (let i = 0; i < x.pixels.length; i += 4) {
      let largest = 0;
      for (let channel = 0; channel < 4; channel++) {
        const difference = Math.abs(x.pixels[i + channel] - y.pixels[i + channel]);
        if (difference) changedChannels++;
        largest = Math.max(largest, difference);
        maxChannelDifference = Math.max(maxChannelDifference, difference);
        totalAbsoluteDifference += difference;
      }
      if (largest) changedPixels++;
      if (largest > 1) {
        pixelsOverOne++;
        const point = i / 4, px = point % x.width, py = Math.floor(point / x.width);
        overOneBounds[0] = Math.min(overOneBounds[0], px);
        overOneBounds[1] = Math.min(overOneBounds[1], py);
        overOneBounds[2] = Math.max(overOneBounds[2], px);
        overOneBounds[3] = Math.max(overOneBounds[3], py);
      }
      if (largest > 10) pixelsOverTen++;
    }
    return { geometryMismatch: false, changedChannels, changedPixels,
      pixelsOverOne, pixelsOverTen, overOneBounds: pixelsOverOne ? overOneBounds : null,
      maxChannelDifference,
      changedChannelFraction: changedChannels / x.pixels.length,
      meanAbsoluteDifference: totalAbsoluteDifference / x.pixels.length };
  }, [first.toString('base64'), second.toString('base64')]);
}

async function sample(page, frame, fps, screenshot = false) {
  const data = await page.evaluate(async ({ frame, fps }) => {
    await Promise.race([(async () => {
      await window.renderAt(frame / fps);
      if (window.imgWait) await window.imgWait();
      await document.fonts.ready;
      const stage = document.querySelector('#stage');
      if (!stage) throw Error('Missing #stage');
      const stageRect = stage.getBoundingClientRect();
      const paintable = element => {
        let opacity = 1;
        for (let e = element; e; e = e.parentElement) {
          const style = getComputedStyle(e);
          if (style.display === 'none' || style.visibility === 'hidden') return false;
          opacity *= Number(style.opacity || 1);
          if (opacity < .005) return false;
        }
        const rect = element.getBoundingClientRect();
        return rect.right > stageRect.left && rect.left < stageRect.right &&
               rect.bottom > stageRect.top && rect.top < stageRect.bottom;
      };
      const allImages = [...document.images].filter(im => im.getAttribute('src'));
      const broken = [];
      for (const im of allImages) {
        if (im.complete && im.naturalWidth === 0) broken.push(im.src);
        if (!paintable(im)) continue;
        const expected = im.src;
        try { await im.decode(); }
        catch (error) {
          if (error.name !== 'EncodingError' || !im.complete || !im.naturalWidth || im.src !== expected)
            broken.push(`${expected}: ${error.message}`);
          else {
            await new Promise(resolve => requestAnimationFrame(resolve));
            try { await im.decode(); } catch (retry) { broken.push(`${expected}: ${retry.message}`); }
          }
        }
        if (!im.naturalWidth) broken.push(expected);
      }
      if (broken.length) throw Error('Broken image: ' + [...new Set(broken)].join(', '));
    })(), new Promise((_, reject) => setTimeout(() => reject(Error('Frame/image readiness timed out')), 30000))]);

    const stage = document.querySelector('#stage');
    const stageRect = stage.getBoundingClientRect();
    const visible = element => {
      let opacity = 1;
      for (let e = element; e; e = e.parentElement) {
        const style = getComputedStyle(e);
        if (style.display === 'none' || style.visibility === 'hidden') return false;
        opacity *= Number(style.opacity || 1);
        if (opacity < .005) return false;
      }
      const rect = element.getBoundingClientRect();
      return rect.right > stageRect.left && rect.left < stageRect.right &&
             rect.bottom > stageRect.top && rect.top < stageRect.bottom;
    };
    const active = [...document.querySelectorAll('#world > .sc')].filter(el => getComputedStyle(el).display !== 'none');
    if (active.length !== 1) throw Error(`Expected one visible scene, found ${active.length}`);
    const nodes = [];
    for (const el of stage.querySelectorAll('*')) {
      if (!visible(el)) continue;
      const s = getComputedStyle(el), r = el.getBoundingClientRect();
      const rect = [r.x, r.y, r.width, r.height].map(v => Math.round(v * 100) / 100);
      const directText = [...el.childNodes].filter(n => n.nodeType === Node.TEXT_NODE).map(n => n.textContent).join('').trim();
      nodes.push([el.tagName, el.className?.baseVal || el.className || '', directText,
                  rect, s.opacity, s.transform, s.filter, s.clipPath, s.color, s.backgroundColor, s.fontSize,
                  el.tagName === 'IMG' ? [el.currentSrc, el.naturalWidth, el.naturalHeight] : null]);
    }
    const images = [...document.images].filter(im => im.getAttribute('src') && im.complete && im.naturalWidth > 0);
    const visibleImages = images.filter(visible);
    // The source-host adapter retains the original .tkc presenter container.
    const presenter = [...active[0].querySelectorAll('.cam img, .tkc img')].filter(visible);
    return { frame, activeScene: [...document.querySelectorAll('#world > .sc')].indexOf(active[0]),
             nodes, decodedImages: images.length, visibleImages: visibleImages.length,
             visiblePresenter: presenter.length };
  }, { frame, fps });
  const { nodes, ...summary } = data;
  const result = { ...summary, domHash: digest(JSON.stringify(nodes)), nodeCount: nodes.length };
  if (screenshot) {
    const png = await page.screenshot({ type: 'png' });
    result.screenshotHash = digest(png);
    result.png = png;
  }
  return result;
}

async function loadedPage(context, entry, errors) {
  const page = await context.newPage();
  page.on('pageerror', e => errors.add(`Page script error: ${e.message}`));
  page.on('console', m => { if (m.type() === 'error') errors.add(`Page console error: ${m.text()}`); });
  page.on('requestfailed', r => errors.add(`Resource request failed: ${r.failure()?.errorText || 'unknown'} (${r.url()})`));
  await page.goto(pathToFileURL(entry).href, { waitUntil: 'load', timeout: 90000 });
  await page.waitForFunction(() => typeof window.renderAt === 'function' && (window.READY || document.title === 'done'), null, { timeout: 90000 });
  await page.evaluate(async () => { await window.READY; if (window.imgWait) await window.imgWait(); });
  return page;
}

async function audit(opt) {
  const plan = JSON.parse(fs.readFileSync(opt.planFile, 'utf8'));
  const samples = collectAuditFrames(plan), representatives = representativeFrames(plan);
  const report = { project: opt.project, pack: plan.pack || plan.pack_id, fps: plan.fps,
    durationFrames: plan.end_frame ?? plan.durationFrames, sceneCount: plan.scenes.length,
    framesSampled: samples.length, sampledFrames: samples, representativeFrames: representatives,
    knotsChecked: plan.scenes.reduce((n, scene) => n + (scene.time_map || scene.knots || []).length, 0),
    checks: ['each time-map knot +/-1 frame', 'each time-map interval midpoint',
      'each scene edge and midpoint', 'fresh-load vs random-seek visible DOM and screenshot',
      'local resource failures, script errors, decoded images, first-frame presenter'],
    randomSeekOrderSeed: '0x5eed1234', freshCompared: 0, decodedImageReferences: 0,
    visibleImageChecks: 0, warnings: [], issues: [], ok: false };
  const errors = new Set();
  let browser;
  try {
    browser = await chromium.launch({ executablePath: chrome(opt.browser), headless: true,
      args: ['--allow-file-access-from-files', '--force-color-profile=srgb', '--disable-gpu', '--disable-accelerated-2d-canvas'] });
    const context = await browser.newContext({ viewport: { width: plan.width || 1920, height: plan.height || 1080 },
      deviceScaleFactor: 1, serviceWorkers: 'block' });
    await context.route('**/*', route => {
      if (/^(?:https?|wss?):/i.test(route.request().url())) {
        errors.add(`Remote asset blocked: ${route.request().url()}`);
        return route.abort();
      }
      return route.continue();
    });
    if (context.routeWebSocket) await context.routeWebSocket('**/*', socket => {
      errors.add('WebSocket asset blocked'); socket.close();
    });
    const randomPage = await loadedPage(context, opt.entry, errors);
    report.typography={schema:'adu-actual-typography/1',frames:[],findings:[],status:'measured-needs-visual-review',canvas:'renderer-owned bounds or visual review; DOM scan does not measure Canvas glyphs'};
    const resultByFrame = new Map();
    const reps = new Set(representatives);
    for (const item of shuffled(samples)) {
      try {
        const state = await sample(randomPage, item.frame, plan.fps, reps.has(item.frame));
        report.decodedImageReferences += state.decodedImages;
        report.visibleImageChecks += state.visibleImages;
        resultByFrame.set(item.frame, state);
        const type=await measureTypography(randomPage,item.frame,plan.fps);
        report.typography.frames.push(type);report.typography.findings.push(...type.findings);
        for(const f of type.findings)if(['font-not-ready','caption-safe-space'].includes(f.kind))report.issues.push({kind:f.kind,frame:item.frame,detail:f});
        if (item.frame === 0 && !state.visiblePresenter)
          report.issues.push({ frame: 0, kind: 'first-frame-presenter', message: 'The narration image is not visible on the first frame' });
      } catch (error) {
        report.issues.push({ frame: item.frame, kind: 'random-seek', message: error.message });
        break;
      }
    }
    await randomPage.close();
    // A local visual defect such as an offscreen opening presenter should not
    // suppress the independent seek-determinism audit for the whole project.
    // A genuinely unrenderable page is caught by loadedPage/sample above.
    {
      for (const frame of representatives) {
        const sought = resultByFrame.get(frame);
        if (!sought) continue;
        let page;
        try {
          page = await loadedPage(context, opt.entry, errors);
          const fresh = await sample(page, frame, plan.fps, true);
          report.freshCompared++;
          let pixels;
          if (sought.screenshotHash !== fresh.screenshotHash)
            pixels = await pixelDifference(page, sought.png, fresh.png);
          const pixelCount = (plan.width || 1920) * (plan.height || 1080);
          // Chromium can quantize anti-aliased edges/backdrop blur differently
          // across fresh pages. The evidence is recorded as a warning, never
          // silently treated as pixel-identical success. A broad or high-energy
          // difference remains an error even when DOM styles happen to match.
          const rasterQuantization = pixels && !pixels.geometryMismatch &&
            pixels.meanAbsoluteDifference <= .03 &&
            pixels.pixelsOverOne <= Math.max(8, pixelCount * .0001) &&
            pixels.pixelsOverTen <= Math.max(2, pixelCount * .000001);
          if (sought.domHash !== fresh.domHash || (pixels && !rasterQuantization)) {
            report.issues.push({ frame, kind: 'seek-nondeterminism',
              randomDom: sought.domHash, freshDom: fresh.domHash,
              randomPng: sought.screenshotHash, freshPng: fresh.screenshotHash,
              pixelDifference: pixels });
            if (opt.screenshots) {
              fs.mkdirSync(opt.screenshots, { recursive: true });
              fs.writeFileSync(path.join(opt.screenshots, `frame_${frame}_random.png`), sought.png);
              fs.writeFileSync(path.join(opt.screenshots, `frame_${frame}_fresh.png`), fresh.png);
            }
          } else if (pixels) {
            report.warnings.push({ frame, kind: 'raster-variance',
              message: 'Visible DOM matches, but the browser raster differs. Review source and output screenshots; this is not pixel-perfect proof.',
              pixelDifference: pixels });
            if (opt.screenshots) {
              fs.mkdirSync(opt.screenshots, { recursive: true });
              fs.writeFileSync(path.join(opt.screenshots, `frame_${frame}_random.png`), sought.png);
              fs.writeFileSync(path.join(opt.screenshots, `frame_${frame}_fresh.png`), fresh.png);
            }
          }
        } catch (error) {
          report.issues.push({ frame, kind: 'fresh-load', message: error.message });
          break;
        } finally { await page?.close(); }
      }
    }
    await context.close();
  } catch (error) {
    report.issues.push({ kind: 'fatal', message: error.message });
  } finally { await browser?.close(); }
  for (const message of errors) report.issues.push({ kind: 'browser', message });
  if (report.freshCompared !== representatives.length)
    report.issues.push({ kind: 'incomplete-comparison', message: `Compared ${report.freshCompared} of ${representatives.length} representative frames` });
  if (!report.decodedImageReferences || !report.visibleImageChecks)
    report.issues.push({ kind: 'missing-media', message: 'No decoded/visible image frames were verified; visual fidelity cannot pass' });
  report.status = report.issues.length ? 'failed' : report.warnings.length ? 'needs-raster-review' : 'passed';
  report.ok = report.status === 'passed' && report.freshCompared === representatives.length;
  return report;
}

const invoked = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (invoked) {
  try {
    const opt = parse(process.argv.slice(2));
    if (opt) {
      const report = await audit(opt);
      const json = JSON.stringify(report, null, 2) + '\n';
      if (opt.output) fs.writeFileSync(opt.output, json, { flag: 'wx' });
      const summary = { status: report.status, ok: report.ok, project: report.project,
        sceneCount: report.sceneCount, framesSampled: report.framesSampled,
        knotsChecked: report.knotsChecked, freshCompared: report.freshCompared,
        decodedImageReferences: report.decodedImageReferences,
        visibleImageChecks: report.visibleImageChecks,
        issueCount: report.issues.length, warningCount: report.warnings.length,
        issues: report.issues.slice(0, 3), warnings: report.warnings.slice(0, 2),
        reportFile: opt.output || null };
      process.stdout.write(JSON.stringify(summary) + '\n');
      if (!report.ok) process.exitCode = 1;
    }
  } catch (error) {
    process.stdout.write(JSON.stringify({ ok: false, issues: [{ kind: 'fatal', message: error.message }] }, null, 2) + '\n');
    process.exitCode = 1;
  }
}

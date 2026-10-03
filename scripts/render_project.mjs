#!/usr/bin/env node
// Local deterministic renderAt(t) export. No package installation or remote assets.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { pathToFileURL, fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { spawn, spawnSync } from 'node:child_process';
import { chrome } from './chrome.mjs';
const help = `Usage: node render_project.mjs ENTRY.html [options]
  --output FILE.mp4                 Export a new MP4 (never overwrite)
  --probe                          Read runtime END without exporting
  --query STRING                   Optional URL query, without leading ?
  --optional-data face.js,subs.js   Explicit missing local script allow-list
  --stills-dir NEW_DIR --times 1,4  Save PNG keyframes in a new directory
  --start 0 --end SECONDS           Video range; end defaults to window.END
  --fps 60 --width 1920 --height 1080
  --audio FILE                      Local full-timeline audio, trimmed at start
  --playwright-module PATH          Existing playwright/core module or directory
  --browser PATH                    Existing Chromium/Chrome executable
Only one output mode. Video uses integer frame indices round(time*fps).
Dimensions set the viewport; they do not redesign a fixed-size composition.
Audio must be passed explicitly. Embedded <video>/<audio> playback is unsupported.
Local renderAt(t), READY Promise or document.title='done', and optional imgWait()
are supported. HTTP/WebSocket assets are blocked. No dependencies are installed.`;

function parse() {
  const argv = process.argv.slice(2), opt = { fps: 60, start: 0 };
  if (argv.includes('--help') || !argv.length) { console.log(help); process.exit(0); }
  opt.entry = path.resolve(argv.shift());
  const allowed = ['probe', 'query', 'optional-data', 'output', 'stills-dir', 'times', 'start', 'end', 'fps', 'width', 'height', 'audio', 'playwright-module', 'browser'];
  while (argv.length) {
    const key = argv.shift().replace(/^--/, '');
    if (key === 'probe') { opt.probe = true; continue; }
    if (!allowed.includes(key) || !argv.length) throw Error(`Unknown or incomplete option: ${key}`);
    opt[key] = argv.shift();
  }
  const directory=path.dirname(opt.entry);let dimensions;
  for(const name of ['showcase-layout.json','macro_plan.json']){
    const file=path.join(directory,name);if(!fs.existsSync(file))continue;
    const data=JSON.parse(fs.readFileSync(file,'utf8'));
    if(![data.width,data.height].every(v=>Number.isInteger(v)&&v>0))throw Error(name+' needs positive integer dimensions');
    dimensions=[data.width,data.height];break;
  }
  if(dimensions&&((opt.width!==undefined&&+opt.width!==dimensions[0])||(opt.height!==undefined&&+opt.height!==dimensions[1])))throw Error('Viewport differs from project layout; rebuild the native layout first');
  opt.width??=dimensions?.[0]??1920;opt.height??=dimensions?.[1]??1080;
  for (const key of ['start', 'end', 'fps', 'width', 'height']) {
    if (opt[key] !== undefined && (!Number.isFinite(opt[key] = Number(opt[key])) || opt[key] < 0)) throw Error(`Invalid --${key}`);
  }
  if (![opt.fps, opt.width, opt.height].every(x => Number.isInteger(x) && x > 0)) throw Error('fps/width/height must be positive integers');
  if (!fs.statSync(opt.entry).isFile()) throw Error('Entry must be a local HTML file');
  if ([!!opt.output, !!opt['stills-dir'], !!opt.probe].filter(Boolean).length !== 1) throw Error('Choose exactly one of --output, --stills-dir or --probe');
  opt.optional = new Set((opt['optional-data'] || '').split(',').filter(Boolean).map(relative => {
    const candidate = path.resolve(path.dirname(opt.entry), relative);
    if (path.isAbsolute(relative) || !relative.endsWith('.js') || path.relative(path.dirname(opt.entry), candidate).startsWith('..')) throw Error('Optional data must be relative local .js paths inside the entry directory');
    if (fs.existsSync(candidate)) throw Error('Optional allow-list is only for missing data scripts: ' + relative);
    return pathToFileURL(candidate).href;
  }));
  if (opt.probe) return opt;
  opt.target = path.resolve(opt.output || opt['stills-dir']);
  if (fs.existsSync(opt.target)) throw Error(`Refusing to overwrite: ${opt.target}`);
  if (!fs.statSync(path.dirname(opt.target)).isDirectory()) throw Error('Output parent directory must exist');
  if (opt.output && (!opt.target.toLowerCase().endsWith('.mp4') || opt.width % 2 || opt.height % 2)) throw Error('MP4 requires .mp4 extension and even dimensions');
  if (opt.output && opt.times) throw Error('--times is only for stills');
  if (opt['stills-dir'] && (!opt.times || opt.audio)) throw Error('Stills require --times and do not support --audio');
  opt.times = opt.times?.split(',').map(Number);
  if (opt.times?.some(t => !Number.isFinite(t) || t < 0)) throw Error('Invalid --times');
  if (opt.audio) { opt.audio = path.resolve(opt.audio); if (!fs.statSync(opt.audio).isFile()) throw Error('Audio must be a local file'); }
  return opt;
}
function probe(file, count = false) {
  const result = spawnSync('ffprobe', ['-v', 'error', ...(count ? ['-count_frames'] : []), '-show_streams', '-show_format', '-of', 'json', file], { encoding: 'utf8' });
  if (result.error || result.status !== 0) throw Error(`ffprobe failed: ${result.error?.message || result.stderr}`);
  return JSON.parse(result.stdout);
}
async function playwright(opt) {
  const require = createRequire(path.join(path.dirname(opt.entry), 'package.json'));
  const skillRequire = createRequire(import.meta.url);
  const candidates = opt['playwright-module'] ? [path.resolve(opt['playwright-module'])] : [];
  if (!candidates.length) {
    for (const resolver of [skillRequire, require]) {
      for (const name of ['playwright-core', 'playwright']) { try { candidates.push(resolver.resolve(name)); } catch {} }
    }
    if (process.env.ADU_PLAYWRIGHT_MODULE) candidates.push(path.resolve(process.env.ADU_PLAYWRIGHT_MODULE));
  }
  for (let candidate of candidates) {
    if (!fs.existsSync(candidate)) continue;
    if (fs.statSync(candidate).isDirectory()) candidate = require.resolve(candidate);
    const module = await import(pathToFileURL(candidate).href);
    if (module.chromium || module.default?.chromium) return module.chromium || module.default.chromium;
  }
  throw Error('Existing Playwright module not found. Supply --playwright-module PATH; nothing was installed.');
}
function executable(chromium, explicit) {
  if (explicit) return chrome(explicit);
  try { return chrome(); }
  catch (error) {
    const bundled = chromium.executablePath();
    if (fs.existsSync(bundled)) return chrome(bundled);
    throw error;
  }
}

async function main() {
  const opt = parse(), chromium = await playwright(opt), browserPath = executable(chromium, opt.browser || process.env.CHROME);
  let browser, ff, ffDone, temporary, report;
  let color;
  const errors = new Set();
  const check = () => { if (errors.size) throw Error([...errors].join('\n')); };
  try {
    if (opt.output && spawnSync('ffmpeg', ['-version'], { stdio: 'ignore' }).status !== 0) throw Error('ffmpeg executable not found');
    if (opt.output) {
      const plan = spawnSync(process.env.ADU_PYTHON || 'python3', [path.join(path.dirname(fileURLToPath(import.meta.url)), 'color_management.py'), '--export-plan'], { encoding: 'utf8' });
      if (plan.status !== 0) throw Error(`Color preflight failed: ${plan.stderr || plan.error?.message}`);
      color = JSON.parse(plan.stdout);
    }
    temporary = fs.mkdtempSync(path.join(os.tmpdir(), 'adu-video-render-'));
    browser = await chromium.launch({ executablePath: browserPath, headless: true, args: ['--allow-file-access-from-files', '--force-color-profile=srgb'] });
    const context = await browser.newContext({ viewport: { width: opt.width, height: opt.height }, deviceScaleFactor: 1, serviceWorkers: 'block' });
    await context.route('**/*', route => {
      if (/^https?:/i.test(route.request().url())) { errors.add('Remote request blocked; local assets are required'); return route.abort(); }
      return route.continue();
    });
    if (context.routeWebSocket) await context.routeWebSocket('**/*', socket => { errors.add('WebSocket blocked'); socket.close(); });
    const page = await context.newPage();
    page.on('pageerror', e => errors.add(`Page script error: ${e.message}`));
    page.on('console', m => {
      if (m.type() === 'error' && !(opt.optional.has(m.location().url) && /ERR_FILE_NOT_FOUND/.test(m.text()))) errors.add(`Page console error: ${m.text()} (${m.location().url || opt.entry})`);
    });
    page.on('requestfailed', r => {
      if (!(r.resourceType() === 'script' && opt.optional.has(r.url()) && /ERR_FILE_NOT_FOUND/.test(r.failure()?.errorText || ''))) errors.add(`Resource request failed: ${r.failure()?.errorText || 'unknown'} (${r.url()})`);
    });
    const entryURL = new URL(pathToFileURL(opt.entry).href);
    if (opt.query) entryURL.search = opt.query;
    await page.goto(entryURL.href, { waitUntil: 'load', timeout: 90000 });
    check();
    await page.waitForFunction(() => typeof window.renderAt === 'function' && (window.READY || document.title === 'done'), null, { timeout: 90000 });
    await page.evaluate(async () => {
      await Promise.race([Promise.resolve(window.READY), new Promise((_, reject) => setTimeout(() => reject(Error('READY timed out')), 90000))]);
    });
    async function frame(t = null) {
      await page.evaluate(async time => {
        await Promise.race([(async () => {
          if (time !== null) await window.renderAt(time);
          if (window.imgWait) await window.imgWait();
          await document.fonts.ready;
          if (document.querySelector('video,audio')) throw Error('Native video/audio elements require a separate deterministic adapter');
          const visibleImages = [...document.images].filter(im => {
            if (!(im.getAttribute('src') || im.currentSrc)) return false;
            for (let el = im; el; el = el.parentElement) {
              const style = getComputedStyle(el);
              if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
            }
            return true;
          });
          // A hidden outgoing sequence can have its decode cancelled by Chromium.
          // Only painted images are frame requirements; failed resource requests
          // still fail the render, including requests made by hidden elements.
          for (const im of visibleImages) {
            const expected = im.src;
            if (im._aduDecodedSource !== expected) {
              try { await im.decode(); }
              catch (error) {
                // Chromium can cancel a decode during a same-frame visibility
                // change. Retry the unchanged, successfully loaded image once;
                // never advance time or substitute an earlier video frame.
                if (error.name !== 'EncodingError' || im.src !== expected || !im.complete || !im.naturalWidth) {
                  throw Error(`Image decode failed: ${expected} (${error.message})`);
                }
                await new Promise(resolve => requestAnimationFrame(resolve));
                try { await im.decode(); }
                catch (retryError) { throw Error(`Image decode retry failed: ${expected} (${retryError.message})`); }
                window.ADU_DECODE_RETRIES = (window.ADU_DECODE_RETRIES || 0) + 1;
              }
              if (im.src !== expected) throw Error('Image source changed while decoding: ' + expected);
              im._aduDecodedSource = expected;
            }
            if (!im.naturalWidth) throw Error('Broken image resource');
          }
        })(), new Promise((_, reject) => setTimeout(() => reject(Error('Font/image/frame readiness timed out')), 30000))]);
      }, t);
      check();
    }
    await frame();
    const end = opt.end ?? await page.evaluate(() => Number(window.END ?? window.CONFIG?.end));
    if (!Number.isFinite(end) || end <= 0) throw Error('Set --end or provide a positive window.END');
    if (opt.probe) {
      check(); report = { entry: opt.entry, end, fps: opt.fps, width: opt.width, height: opt.height, browser: browserPath }; return;
    }
    if (opt['stills-dir']) {
      if (opt.times.some(t => t >= end)) throw Error('Still times must precede END/--end');
      for (let i = 0; i < opt.times.length; i++) {
        await frame(opt.times[i]);
        await page.screenshot({ path: path.join(temporary, `frame_${String(i).padStart(3, '0')}_${opt.times[i].toFixed(3)}s.png`) });
        check();
      }
      fs.mkdirSync(opt.target);
      for (const file of fs.readdirSync(temporary)) fs.copyFileSync(path.join(temporary, file), path.join(opt.target, file), fs.constants.COPYFILE_EXCL);
      report = { output: opt.target, times: opt.times, browser: browserPath };
      return;
    }
    const first = Math.round(opt.start * opt.fps), last = Math.round(end * opt.fps), count = last - first, duration = count / opt.fps;
    if (count <= 0) throw Error('End must be after start by at least one frame');
    if (opt.audio) {
      const input = probe(opt.audio), track = input.streams.find(s => s.codec_type === 'audio');
      const audioDuration = Number(track?.duration || input.format?.duration);
      if (!track || !Number.isFinite(audioDuration) || audioDuration + 0.05 < last / opt.fps) throw Error('Audio does not cover the requested full-timeline range');
    }
    const output = path.join(temporary, 'render.mp4');
    const args = ['-n', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(opt.fps), '-c:v', 'png', '-i', 'pipe:0'];
    if (opt.audio) args.push('-protocol_whitelist', 'file,pipe', '-ss', String(first / opt.fps), '-i', opt.audio);
    args.push('-map', '0:v:0', '-map_metadata', '-1', '-vf', color.filter, '-c:v', 'libx264', '-preset', 'medium', '-crf', '15', '-pix_fmt', 'yuv420p', '-color_range', 'tv', '-colorspace', 'bt709', '-color_trc', 'bt709', '-color_primaries', 'bt709', '-frames:v', String(count));
    if (opt.audio) args.push('-map', '1:a:0', '-c:a', 'aac', '-ar', '48000', '-b:a', '192k', '-af', 'apad');
    else args.push('-an');
    args.push('-t', String(duration), '-movflags', '+faststart', output);
    ff = spawn('ffmpeg', args, { stdio: ['pipe', 'ignore', 'pipe'] });
    let diagnostic = '', pipeError;
    ff.stderr.on('data', chunk => { diagnostic = (diagnostic + chunk).slice(-8000); });
    ff.stdin.on('error', e => { pipeError = e; });
    ffDone = new Promise(resolve => { ff.once('error', e => resolve({ error: e.message })); ff.once('close', code => resolve({ code })); });
    for (let i = first; i < last; i++) {
      if (pipeError || ff.exitCode !== null) throw Error(`FFmpeg stopped: ${diagnostic || pipeError?.message}`);
      await frame(i / opt.fps);
      const buffer = await page.screenshot({ type: 'png' }); check();
      await new Promise((resolve, reject) => ff.stdin.write(buffer, e => e ? reject(e) : resolve()));
      if ((i - first) % (opt.fps * 5) === 0) console.error(`Rendered ${i - first + 1}/${count} frames`);
    }
    ff.stdin.end();
    const result = await ffDone;
    if (result.error || result.code !== 0) throw Error(`FFmpeg failed: ${result.error || diagnostic || result.code}`);
    const metadata = probe(output, true), video = metadata.streams.find(s => s.codec_type === 'video');
    const actualDuration = Number(video?.duration);
    if (Number(video?.nb_read_frames) !== count || !Number.isFinite(actualDuration) || Math.abs(actualDuration - duration) > 1 / opt.fps + 0.001) throw Error('ffprobe frame count/duration verification failed');
    if (opt.audio && !metadata.streams.some(s => s.codec_type === 'audio')) throw Error('Expected audio track missing');
    for (const [key, value] of Object.entries(color.output)) if (video[key] !== value) throw Error(`Export color mismatch: ${key}=${video[key]}`);
    check();
    fs.copyFileSync(output, opt.target, fs.constants.COPYFILE_EXCL);
    const imageDecodeRetries = await page.evaluate(() => window.ADU_DECODE_RETRIES || 0);
    report = { output: opt.target, frames: count, fps: opt.fps, duration, start: first / opt.fps, end: last / opt.fps, audio: !!opt.audio, imageDecodeRetries, browser: browserPath, color };
  } finally {
    if (ff && ff.exitCode === null) { ff.kill('SIGKILL'); await ffDone; }
    let shutdownForced = false, shutdownTimer;
    try {
      if (browser) {
        // Chrome helpers can retain inherited pipes after the main browser exits.
        // Playwright's process-exit handler kills only this launch's process tree
        // and removes its profile; the CLI exits after its own cleanup below.
        const closed = await Promise.race([
          browser.close().then(() => true),
          new Promise(resolve => { shutdownTimer = setTimeout(() => resolve(false), 15000); }),
        ]);
        shutdownForced = !closed;
      }
    } finally {
      clearTimeout(shutdownTimer);
      if (temporary) fs.rmSync(temporary, { recursive: true, force: true });
    }
    if (report) console.log(JSON.stringify({ ...report, browserShutdownForced: shutdownForced }));
  }
}
main().then(() => process.exit(0)).catch(error => {
  console.error(`Render failed: ${error.message}`); process.exit(1);
});

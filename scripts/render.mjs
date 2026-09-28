#!/usr/bin/env node
// Compatibility entry point. Strict exporter owns all rendering/error checks.
// [W=1920 H=1080 FPS=60] node render.mjs HTML stills NEW_DIR t1,t2 [query]
// [W=1920 H=1080 FPS=60] node render.mjs HTML video NEW.mp4 start end [query]
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const [html, mode, out, a, b, q] = process.argv.slice(2);
if (!html || !out || !['stills', 'video'].includes(mode)) {
  console.error('Usage: render.mjs HTML stills NEW_DIR t1,t2 [query] | HTML video NEW.mp4 start end [query]');
  process.exit(2);
}
const args = [fileURLToPath(new URL('./render_project.mjs', import.meta.url)), html,
  '--width', process.env.W || '1920', '--height', process.env.H || '1080', '--fps', process.env.FPS || '60'];
if (mode === 'stills') args.push('--stills-dir', out, '--times', a);
else args.push('--output', out, '--start', a, '--end', b);
const query = mode === 'stills' ? b : q;
if (query) args.push('--query', query);
const result = spawnSync(process.execPath, args, {stdio: 'inherit'});
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);

// Resolve an existing browser only. Installing a browser is an explicit setup step.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';

export function chrome(explicit = process.env.CHROME) {
  function executable(file) {
    try { fs.accessSync(file, fs.constants.X_OK); return fs.statSync(file).isFile(); } catch { return false; }
  }
  if (explicit) {
    const file = path.resolve(explicit);
    if (!executable(file)) throw Error(`CHROME/browser path is not executable: ${file}`);
    return file;
  }
  const candidates = browserCandidates();
  const names = new Set(['Google Chrome for Testing', 'Chromium', 'chrome', 'chrome.exe', 'headless_shell', 'chrome-headless-shell']);
  function search(dir, depth = 0) {
    if (!fs.existsSync(dir) || depth > 7) return [];
    let entries; try { entries = fs.readdirSync(dir, {withFileTypes: true}); } catch { return []; }
    return entries.flatMap(item => {
      const file = path.join(dir, item.name);
      return item.isDirectory() ? search(file, depth + 1) : names.has(item.name) && executable(file) ? [file] : [];
    });
  }
  const caches = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), 'Library/Caches/ms-playwright'),
    path.join(os.homedir(), '.cache/ms-playwright'), process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'ms-playwright')]
    .filter(p => p && p !== '0');
  candidates.push(...caches.flatMap(dir => search(dir)).sort((a, b) => b.localeCompare(a, undefined, {numeric: true})));
  const found = candidates.find(executable);
  if (found) return found;
  throw Error('No existing Chromium/Chrome found. Install Chrome, set CHROME to its executable, or explicitly run: npx playwright-core install chromium');
}

export function browserCandidates(platform = process.platform, env = process.env) {
  if (platform === 'win32') {
    return [env.PROGRAMFILES, env['PROGRAMFILES(X86)'], env.LOCALAPPDATA].filter(Boolean)
      .flatMap(dir => [path.join(dir, 'Google/Chrome/Application/chrome.exe'),
                      path.join(dir, 'Microsoft/Edge/Application/msedge.exe')]);
  }
  if (platform === 'darwin') return [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'];
  return ['/usr/bin/google-chrome', '/usr/bin/google-chrome-stable', '/usr/bin/chromium', '/usr/bin/chromium-browser'];
}

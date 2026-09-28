// 找本机 Chromium：优先环境变量 CHROME，其次 Playwright 缓存，最后系统 Chrome
import fs from 'fs'; import path from 'path'; import os from 'os';
export function chrome() {
  if (process.env.CHROME && fs.existsSync(process.env.CHROME)) return process.env.CHROME;
  const base = path.join(os.homedir(), 'Library/Caches/ms-playwright');
  if (fs.existsSync(base)) for (const d of fs.readdirSync(base).filter(d => /^chromium-\d+$/.test(d)).sort().reverse()) {
    for (const rel of ['chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing', 'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-linux/chrome'])
      if (fs.existsSync(path.join(base, d, rel))) return path.join(base, d, rel);
  }
  const sys = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
  if (fs.existsSync(sys)) return sys;
  throw new Error('找不到 Chromium：设置 CHROME 环境变量，或运行 npx playwright install chromium');
}

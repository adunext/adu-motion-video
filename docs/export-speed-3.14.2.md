# 3.14.2-rc.1 export speed (lossless fast PNG capture)

`scripts/render_project.mjs` now captures each exported frame through the DevTools protocol:
`Page.captureScreenshot { format: 'png', optimizeForSpeed: true }` instead of `page.screenshot({ type: 'png' })`.
It is still lossless PNG; only Chromium's zlib setting is faster. The colour pipeline (sRGB input, the analytic
BT.709 conversion, ffmpeg filters and tags), encoding settings, output signature and every other step are unchanged.
Preview stills (`--stills-dir`) keep the old call.

Verified, 2026-11-14, macOS:

- Same project, old and new script (chrome-headless-shell from the ADu Director toolchain, ffmpeg 9.0.1):
  `examples/silent-demo.html`, 8 s, 1920×1080, 30 fps, 240 frames — the two MP4 files are byte-identical
  (sha256 `2454b8751610d376…`); wall time including browser start 28 s → 21 s.
- ADu Director desktop 3.13.0-rc.2 carries the same change (its commit 9c31b2513): a full project export 905 s → 495 s,
  the film (with audio, 8062 frames) byte-identical before and after (sha256 `c9c3b68e…`); per-frame capture
  97.9 ms → 41.0 ms. A 240-frame dark-console run: 208 → 111 ms per frame, PSNR infinite.
- 245 Python regressions (with `CHROME` set to the toolchain Chromium), the output-signature schedule tests and the output-signature browser check (24 routes, 131 groups) pass on this version.

The remaining gap to the old lossy JPEG capture (about 20 ms a frame) is not taken: going back to a lossy format would
change the pixels.

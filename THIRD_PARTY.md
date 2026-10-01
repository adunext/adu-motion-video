# Provenance, distribution and dependencies

## Project source

This package contains reusable DOM/CSS/JavaScript motion-video recipes and an original Canvas2D hand-drawn continuity example, with workflow and code assistance from Claude and Codex. The public packaging adapts host-specific paths into explicit inputs, removes private profile details and media, and uses installed system fonts.

The project’s own toolkit code and documentation are licensed under the [MIT License](LICENSE), copyright 2026 阿杜Next. Third-party dependencies retain their own licenses and notices; the project license does not replace them. The README cover is supplied by the project owner and contains a visual montage; it does not bundle or grant rights to the underlying showcase works or templates. Historical video media are not included or licensed by this repository.

## Dependencies

Dependency implementations are not bundled. The package lock records Playwright Core and its Apache-2.0 metadata. Copies of the corresponding installed package's [LICENSE](third-party/playwright-core/LICENSE) and [NOTICE](third-party/playwright-core/NOTICE) are retained for reference. These apply to Playwright, not to all project files.

Acorn is installed separately under its MIT license. The package lock records its version; a copy of its [LICENSE](third-party/acorn/LICENSE) is retained. Its implementation is not bundled.

Python packages, FFmpeg, Chromium / Chrome and Apple's Vision / AppKit are separately installed tools. They retain their own licenses and distribution terms. Their code and binaries are not redistributed in this repository.

## Fonts and media

The `paper-balance@1.0.0` pack embeds unmodified WOFF2 font bytes in its CSS: Anton, Caveat, Geist and Geist Mono. These fonts are distributed under the SIL Open Font License 1.1. Their full copyright and license notices are preserved both in the CSS and as [Anton](packs/paper-balance/1.0.0/licenses/OFL-anton.txt), [Caveat](packs/paper-balance/1.0.0/licenses/OFL-caveat.txt), [Geist](packs/paper-balance/1.0.0/licenses/OFL-geist.txt) and [Geist Mono](packs/paper-balance/1.0.0/licenses/OFL-geistmono.txt) notices. The reviewed extractor retains the same notices under `adapters/paper-balance/licenses/`.

No Apple system font is copied or embedded. Chinese text still uses the user's installed PingFang stack, and the verified environment also relies on installed SF Mono. The A/B/C/D/E and legacy packs do not redistribute their source font folders. Users may add fonts that they are authorized to use and must retain the relevant notices; embedded open fonts do not establish cross-platform visual equivalence.

The tutorial diagrams, generic demo illustrations and example-frame screenshots under `assets/tutorials/` and `template/assets/` are authored for this toolkit. The Canvas2D example does not bundle p5.brush, third-party character code or footage; the p5 adaptation guide describes an interface pattern for users who supply their own licensed projects.

Apart from the owner-supplied README cover at `assets/cover.png`, no personal avatar, real voice, music track, raw footage, historical render, website screenshot or third-party showcase video is included. Relative names such as `assets/presenter.png` and `assets/app-logo.png` in the historical examples are placeholders for assets supplied by a project author. Generic labels and numbers in examples are illustrative, not measured product comparisons or general performance guarantees.

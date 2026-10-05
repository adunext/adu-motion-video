# Provenance, distribution and dependencies

## Project source

This package contains reusable DOM/CSS/JavaScript motion-video recipes and an original Canvas2D hand-drawn continuity example, with workflow and code assistance from Claude and Codex. The public packaging adapts host-specific paths into explicit inputs, removes private profile details and media, and uses installed system fonts.

The project’s own toolkit code and documentation are licensed under the [MIT License](LICENSE), copyright 2026 阿杜Next. Third-party dependencies retain their own licenses and notices; the project license does not replace them. The README cover is supplied by the project owner and contains a visual montage; it does not bundle or grant rights to the underlying showcase works or templates. Selected owner-authorized short demo exports are included for viewing; historical raw media and full source videos are not supplied as reusable project assets.

## Dependencies

Dependency implementations are not bundled. The package lock records Playwright Core and its Apache-2.0 metadata. Copies of the corresponding installed package's [LICENSE](third-party/playwright-core/LICENSE) and [NOTICE](third-party/playwright-core/NOTICE) are retained for reference. These apply to Playwright, not to all project files.

Acorn is installed separately under its MIT license. The package lock records its version; a copy of its [LICENSE](third-party/acorn/LICENSE) is retained. Its implementation is not bundled.

Python packages, FFmpeg, Chromium / Chrome and Apple's Vision / AppKit are separately installed tools. They retain their own licenses and distribution terms. Their code and binaries are not redistributed in this repository.

## Fonts and media

The `paper-balance@1.0.0` pack embeds unmodified WOFF2 font bytes in its CSS: Anton, Caveat, Geist and Geist Mono. These fonts are distributed under the SIL Open Font License 1.1. Their full copyright and license notices are preserved both in the CSS and as [Anton](packs/paper-balance/1.0.0/licenses/OFL-anton.txt), [Caveat](packs/paper-balance/1.0.0/licenses/OFL-caveat.txt), [Geist](packs/paper-balance/1.0.0/licenses/OFL-geist.txt) and [Geist Mono](packs/paper-balance/1.0.0/licenses/OFL-geistmono.txt) notices. The reviewed extractor retains the same notices under `adapters/paper-balance/licenses/`.

No Apple system font is copied or embedded. Chinese text still uses the user's installed PingFang stack, and the verified environment also relies on installed SF Mono. The A/B/C/D/E and legacy packs do not redistribute their source font folders. Users may add fonts that they are authorized to use and must retain the relevant notices; embedded open fonts do not establish cross-platform visual equivalence.

The tutorial diagrams, generic demo illustrations and example-frame screenshots under `assets/tutorials/` and `template/assets/` are authored for this toolkit. The Canvas2D example does not bundle p5.brush, third-party character code or footage; the p5 adaptation guide describes an interface pattern for users who supply their own licensed projects.

The owner-supplied README cover is retained at `assets/cover.png`, with a compressed display copy at `assets/cover.jpg`. Short MP4 demos and compressed GIF previews under `assets/demos/` show the owner's authorized template demonstrations, including the owner's talking-head image and voice. 01-A, 01-B and 02-A show reviewed new-content samples; 01-C, 01-D and 01-E show source-replay excerpts of styles whose three selected groups were separately reviewed with new-content full films for 3.2.0. These viewing exports do not provide reusable raw presenter footage, voice files, screenshots, music stems or third-party showcase assets. New productions must use their own authorized inputs. Generic labels and numbers in examples are illustrative, not measured product comparisons or general performance guarantees.

The optional [ADuDir Lottie API](references/lottie-assets.md) downloads separately hosted animation files only when requested. The external library is not bundled, and the repository's MIT license does not relicense its third-party animations. The live catalog and annotations may omit source or license details; users must retain supplied notices and establish the original animation's applicable terms before using or redistributing it.


The paper-ball-performance@1.0.0 pack and its retained candidate embed the same reviewed OFL WOFF2 bytes and complete notices. It does not include YouSheBiaoTiHei/YSBT.ttf. Its manifest requires an explicitly supplied font with the reviewed hash; the resulting owner's project records and copies that input. The official [YouShe page](https://www.uisdc.com/uisdc-first-free-font) describes free commercial use, but this pack does not infer a font redistribution or application embedding grant from that description. PingFang SC and Hannotate SC remain system dependencies.

The 02-B GIF and silent MP4 are cropped stage-only previews derived from the accepted new-content sample. They exclude presenter footage, account tags, subtitles and all audio; they show only the calendar/capability/unboxing/delivery choreography, not a full-frame or reusable personal-media source.

The vivid-sticker-performance candidates include only recipe code and external-font fingerprints, not the source presenter, generated stickers, noise texture, font binaries or commercial music. The 05-A silent viewing exports use newly authored SVG illustrations from examples/vivid-sticker-preview and a synthetic presenter placeholder; these assets are toolkit examples, not the original 3D artwork or new-episode audiovisual acceptance evidence.

## 3.14 portable fallback fonts

Unmodified Noto Sans SC and Noto Sans Mono variable TTF files are bundled under assets/fonts with their complete SIL Open Font License 1.1 notices. Their source repository commit, URLs, SHA-256 and sizes are recorded in [sources.json](assets/fonts/sources.json). Both font notices accompany every newly generated portable project. No Apple font is redistributed. The current runtime treats historical source-font fingerprints as recommendations by default and validates actual substituted fonts/layout; the earlier mandatory-font descriptions above remain historical source-pack provenance.

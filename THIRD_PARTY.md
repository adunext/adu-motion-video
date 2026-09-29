# Provenance, distribution and dependencies

## Project source

This package preserves the AduNext EP02 / EP04 custom DOM/CSS/JavaScript scene approach and historical examples, with workflow and code assistance from Claude and Codex. The public packaging adapts host-specific paths into explicit inputs, removes private profile details and media, and uses installed system fonts.

The project’s own toolkit code and documentation are licensed under the [MIT License](LICENSE), copyright 2026 阿杜Next. Third-party dependencies retain their own licenses and notices; the project license does not replace them. The README cover is supplied by the project owner and contains a visual montage; it does not bundle or grant rights to the underlying showcase works or templates. Historical video media are not included or licensed by this repository.

## Dependencies

Dependency implementations are not bundled. The package lock records Playwright Core and its Apache-2.0 metadata. Copies of the corresponding installed package's [LICENSE](third-party/playwright-core/LICENSE) and [NOTICE](third-party/playwright-core/NOTICE) are retained for reference. These apply to Playwright, not to all project files.

Python packages, FFmpeg, Chromium / Chrome and Apple's Vision / AppKit are separately installed tools. They retain their own licenses and distribution terms. Their code and binaries are not redistributed in this repository.

## Fonts and media

No font binary is included because a complete redistribution basis was not present with the source font folder. No Apple system font is copied or embedded; CSS uses local system stacks. Users may add fonts that they are authorized to use and must retain the relevant notices.

Apart from the owner-supplied README cover at `assets/cover.png`, no personal avatar, real voice, music track, raw footage, historical render, website screenshot or third-party showcase video is included. Relative names such as `assets/presenter.png` and `assets/app-logo.png` in the historical examples are placeholders for assets supplied by a project author. Model names, historical figures and examples describe old source material, not verified current product comparisons or general performance guarantees.

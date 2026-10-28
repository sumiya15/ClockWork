> The interactive index now presents only the target system design. Historical static exports and validation notes below describe the earlier two-view version.

# Offline architecture presentation

Open [index.html](index.html) in Edge or Chrome. No server or internet is needed. Keep `index.html`, `presentation.css` and `presentation.js` together. The presentation never reads or writes ClockWork application storage, and it makes no network requests.

The fixed 16:9 desktop layout presents the target architecture with hover connections, a fixed explanation panel, click-to-pin, eight numbered steps, Previous/Next, keyboard navigation, fullscreen, diagram zoom and drag-to-pan. Reset affects presentation state only. Reduced-motion preferences disable highlight transitions.

For the 90-second script, 30-second version and five architecture questions, use [ARCHITECTURE_WALKTHROUGH.md](../ARCHITECTURE_WALKTHROUGH.md).

## Static exports

| View | Editable source | 3200 × 1800 PNG |
|---|---|---|
| Current prototype | [walkthrough-current.svg](../walkthrough-current.svg) | [walkthrough-current.png](../walkthrough-current.png) |
| Target architecture | [walkthrough-target.svg](../walkthrough-target.svg) | [walkthrough-target.png](../walkthrough-target.png) |

Both include a concise caption and status legend. Source content and diagrams are generated from the same `graphs` data in `presentation.js`, preventing drift between the interactive and static versions. Original architecture SVG/PNG/Mermaid files were preserved.

## Checks actually executed

Validation ran on 26 October 2026 using installed Microsoft Edge through Playwright, with **offline mode enabled** and the HTML opened using **file://**. This is a browser-functional check, not a real desktop video recording.

- Current and target views loaded without external requests or page errors.
- Hover highlighted a component and its connected arrows. Click pinned the explanation; another hover did not replace it. Unpin and Escape released it.
- All eight numbered steps, Next/Previous and keyboard arrows navigated correctly. Home/End/R and Enter-to-pin were exercised.
- All sixteen component explanation panels fit without overflowing.
- Zoom in/out, drag panning and reset worked.
- The browser's actual Fullscreen API entered and exited fullscreen from the local file. Browser policy can still vary; F11 is the documented fallback.
- No page scrolling at 1600 × 900, 1920 × 1080 and 1366 × 768.
- Reduced-motion mode removed transitions.
- Both static diagrams rendered as 3200 × 1800 PNG. Automated checks found no node-text overflow and no arrow crossing an edge-label text box.
- Both final static images and both interactive view captures were visually inspected for hierarchy, readability and clipping. An early panel overflow, long storage label and intersecting label were corrected before final validation.

Machine-readable output: [VALIDATION.json](VALIDATION.json). Preview captures: [current](interactive-current.png), [target](interactive-target.png). These are still images, not recordings.

## Reproduce checks and static exports

The presentation itself has zero dependencies. This optional validation command reuses the repository's existing Playwright installation and Edge; it does not download anything:

```powershell
cd C:\Users\sumiy\Documents\ClockWork
node docs/presentation/architecture/interactive/validate.mjs
```

The command refreshes only the new walkthrough SVG/PNG files, two interactive preview screenshots and validation JSON. It never enables video or trace recording. Existing architecture assets and videos are not output targets.

Disk space was checked before asset creation: **6,893,821,952 bytes free**. Application/backend/data/video hashes were captured before work; the final comparison is in `PRESERVATION.json`. No application source or backend code was changed. This interactive presentation visualises architecture; it does not execute the approval workflows.

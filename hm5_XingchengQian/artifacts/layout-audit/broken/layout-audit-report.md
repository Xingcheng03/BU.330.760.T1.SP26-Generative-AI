# Frontend Layout Audit Report

URL: `http://localhost:8000/broken.html`
Generated: `2026-04-27T22:07:23`

## Summary

### desktop (1440 x 900)

- Horizontal overflow: page is 384 px wider than the viewport.
- Broken images: 1 image(s) failed to load.
- Small touch targets: 1 interactive element(s) are below 44 x 44 px.
- Clipped text/content: 1 element(s) may be clipped.
- Possible overlaps: 1 pair(s) of interactive elements overlap.
- Screenshot: `artifacts\layout-audit\broken\screenshots\desktop-1440x900.png`

### mobile (390 x 844)

- Horizontal overflow: page is 1434 px wider than the viewport.
- Broken images: 1 image(s) failed to load.
- Offscreen controls: 1 visible interactive element(s) extend outside the viewport.
- Small touch targets: 1 interactive element(s) are below 44 x 44 px.
- Clipped text/content: 1 element(s) may be clipped.
- Possible overlaps: 1 pair(s) of interactive elements overlap.
- Screenshot: `artifacts\layout-audit\broken\screenshots\mobile-390x844.png`

## Details

### desktop

Offscreen controls:
- None detected.

Small touch targets:
- `button.tiny-button` text='?' rect={'x': 49, 'y': 415, 'width': 28, 'height': 24, 'left': 49, 'top': 415, 'right': 77, 'bottom': 439}

Broken images:
- `img:nth-child(7)` src='http://localhost:8000/missing-product-shot.png' rect={'x': 49, 'y': 635, 'width': 320, 'height': 180, 'left': 49, 'top': 635, 'right': 369, 'bottom': 815}

Clipped text/content:
- `div.clipped-card` text='This text is intentionally too long for the fixed-height card, so the content be' rect={'x': 49, 'y': 459, 'width': 260, 'height': 48, 'left': 49, 'top': 459, 'right': 309, 'bottom': 507}

Possible interactive overlaps:
- `button.primary` overlaps `button.secondary` by about 2592 px^2

### mobile

Offscreen controls:
- `button.offscreen-action` text='Offscreen Action' rect={'x': 903, 'y': 363, 'width': 180, 'height': 44, 'left': 903, 'top': 363, 'right': 1083, 'bottom': 407}

Small touch targets:
- `button.tiny-button` text='?' rect={'x': 49, 'y': 461, 'width': 28, 'height': 24, 'left': 49, 'top': 461, 'right': 77, 'bottom': 485}

Broken images:
- `img:nth-child(7)` src='http://localhost:8000/missing-product-shot.png' rect={'x': 49, 'y': 681, 'width': 320, 'height': 180, 'left': 49, 'top': 681, 'right': 369, 'bottom': 861}

Clipped text/content:
- `div.clipped-card` text='This text is intentionally too long for the fixed-height card, so the content be' rect={'x': 49, 'y': 505, 'width': 260, 'height': 48, 'left': 49, 'top': 505, 'right': 309, 'bottom': 553}

Possible interactive overlaps:
- `button.primary` overlaps `button.secondary` by about 2592 px^2

## Recommended Review Order

1. Fix horizontal overflow first because it usually breaks mobile layouts.
2. Fix offscreen or overlapping controls next because they block user actions.
3. Replace broken images and review clipped text.
4. Manually inspect screenshots for visual polish and intentional design choices.

## Limits

This script reports measurable rendering risks. It does not prove that a UI is beautiful, accessible, or production-ready.

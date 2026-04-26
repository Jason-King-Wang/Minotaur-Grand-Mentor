# Minotaur Grand Mentor

Minotaur Grand Mentor is an original YouTube VTuber project for a powerful, wild, cyber trading mentor character. Version 1 is a static PNGTuber MVP that can run in OBS Browser Source without a backend. Later versions can upgrade the same character direction into a Live2D avatar.

> Disclaimer: This content is for research, education, and entertainment only. It does not constitute investment advice.

## Purpose

- Build an original Minotaur VTuber identity for YouTube.
- Ship a first usable PNGTuber overlay for OBS.
- Keep character design, prompts, assets, logs, and project state in one portable repo.
- Preserve a clean upgrade path toward Live2D.

## First Version Goal

The first version should make `overlay/index.html` usable as an OBS Browser Source. Missing images must not break the overlay; it should show a Minotaur Mentor placeholder until real PNG assets are added.

## Folder Map

- `docs/` - project brief, character bible, style guide, asset spec, prompts, blueprint, OBS setup, Live2D notes, and next actions.
- `assets/reference/` - mood boards, design references, and original inspiration notes.
- `assets/avatar/pngtuber/` - PNGTuber expression files.
- `overlay/` - OBS-ready static overlay.
- `dashboard/` - static project dashboard.
- `data/` - JSON state, avatar manifest, and public JS run-log manifest.
- `records/` - timestamped Markdown execution records.
- `tools/` - standard-library Python tools.
- `tests/` - basic project file checks.

## How To Use The Overlay

Local file preview:

```powershell
Start-Process "C:\Users\User\Documents\Obsidian Vault\Minotaur-Grand-Mentor\overlay\index.html"
```

OBS or local browser source:

```text
file:///C:/Users/User/Documents/Obsidian%20Vault/Minotaur-Grand-Mentor/overlay/index.html
```

Useful URL parameters:

```text
?debug=1&threshold=0.05&scale=1.0
```

Microphone access may require OBS Browser Source permission or a local static server. The overlay is still designed to render without microphone access.

## How To Add Avatar Assets

Put PNGTuber files here:

```text
assets/avatar/pngtuber/
```

Required first-version assets:

- `idle_closed.png`
- `talk_open.png`
- `blink_closed.png`
- `happy.png`

Then run:

```powershell
python tools\validate_assets.py
```

## How To Update Records

Use the logging tool from the project root:

```powershell
python tools\log_event.py --phase "Phase 1" --status "done" --summary "Created project scaffold" --details "Initialized docs, data, overlay, dashboard folders." --next "Build overlay MVP."
```

This creates a Markdown record under `records/YYYY-MM-DD/`, appends to `data/run-log.json`, regenerates `data/run-log.js`, and updates `data/project-state.json`.

## GitHub Pages Deployment

This project is intentionally static. To publish:

1. Push the repo to GitHub.
2. Enable GitHub Pages from the repository settings.
3. Select the branch and root folder.
4. Open:
   - `dashboard/index.html` for the project dashboard.
   - `overlay/index.html` for the OBS overlay.

No API keys, tokens, personal data, or backend services are required.


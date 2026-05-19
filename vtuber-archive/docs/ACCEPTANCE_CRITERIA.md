# Acceptance Criteria

## Static Project

- Required folder structure exists.
- JSON data files parse.
- JS fallback data files exist.
- No backend is required.

## Dashboard

- Opens as a static page.
- Shows project state, task board, missing PNGTuber assets, missing Live2D assets, blocked lists, recent logs, docs links, overlay link, and disclaimer.
- Uses fallback data if JSON fetch fails.

## Overlay

- Opens as a static page.
- Uses transparent background.
- Shows placeholder when PNG assets are missing.
- Supports microphone-based talking state when permission is available.
- Supports hotkeys and debug panel.

## Scope Lock

- `.minotaur-project-root` exists.
- `SCOPE_LOCK.md` exists.
- `docs/BOTTOM_LINES.md` states Obsidian protection.
- `tools/scope_guard.py` validates the project root.

## Final State

- Engineering: done.
- Documentation: done.
- Overlay: placeholder ready.
- Dashboard: ready.
- Live2D: spec ready, waiting for final art and rigging.


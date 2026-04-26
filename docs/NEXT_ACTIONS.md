# Next Actions

This file is meant to be updated continuously by Codex and by the project owner.

## Immediate Next Steps

- Generate `idle_closed.png`.
- Generate `talk_open.png`.
- Generate `blink_closed.png`.
- Generate `happy.png`.
- Put the files into `assets/avatar/pngtuber/`.
- Run `python tools\validate_assets.py`.
- Test `overlay/index.html` in OBS Browser Source.

## Recommended Production Order

1. Use `docs/IMAGE_PROMPTS.md` to create the base design.
2. Pick one final character direction before generating expression variants.
3. Export transparent PNGs at `2048x2048` or `3000x3000`.
4. Keep horns fully visible in every export.
5. Run asset validation.
6. Open `dashboard/index.html` and confirm missing assets are cleared.
7. Open `overlay/index.html?debug=1` and confirm hotkeys and microphone status.

## Later

- Add optional expressions: `angry.png`, `thinking.png`, `gesture_point.png`, `shock.png`.
- Create a model sheet for Live2D planning.
- Define a layered PSD production checklist with the artist.
- Decide whether the future Live2D runtime should be local viewer or web viewer.


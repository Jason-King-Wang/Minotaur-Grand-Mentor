# Next Actions

This file is meant to be updated continuously by Codex and by the project owner.

## Immediate Next Steps

- Test `overlay/index.html` in OBS Browser Source.
- Confirm microphone mouth switching with `overlay/index.html?debug=1`.
- Visually review `assets/avatar/live2d/final/layers_png_same_canvas/` against `assets/avatar/live2d/final/final_front_master.png`.
- Create `assets/avatar/live2d/final/final_layered_model.psd` from reviewed same-canvas layers.
- Send `docs/LIVE2D_RIGGER_CHECKLIST.md` to the rigger.
- Keep `.moc3` / `model3.json` / rigging outputs pending until the rigger finishes them.

## Completed Art Imports

- `idle_closed.png` imported.
- `talk_open.png` imported.
- `blink_closed.png` imported.
- `happy.png` imported.
- `angry.png` imported.
- `thinking.png` imported.
- `gesture_point.png` imported.
- `shock.png` imported.
- `assets/reference/pngtuber_mvp_contact_sheet.png` archived.
- `assets/avatar/live2d/final/final_front_master.png` imported.
- Stage 06 same-canvas layer pack generated in `assets/avatar/live2d/final/layers_png_same_canvas/`.

## Recommended Production Order

1. Open `dashboard/index.html` and confirm Stage 06 shows `built_pending_visual_review`.
2. Open `overlay/index.html?debug=1` and confirm hotkeys and microphone status.
3. Review same-canvas layer alignment visually with the user or rigger.
4. Assemble the final layered PSD only after that review.
5. Send the PSD and `docs/LIVE2D_RIGGER_CHECKLIST.md` to the rigger.

## Later

- Tune `data/same-canvas-coordinate-map.json` if visual review finds alignment issues.
- Decide whether the future Live2D runtime should be local viewer or web viewer.

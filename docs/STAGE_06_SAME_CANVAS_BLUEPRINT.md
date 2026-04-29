# Stage 06 — Same Canvas Layer Pack Blueprint

## Is Stage 06 done by Codex?

Yes. Stage 06 is mainly a Codex task.

Codex should:
- collect all component PNGs,
- validate file names and transparency,
- create a 4096x4096 transparent canvas for every source layer,
- place each layer according to `data/same-canvas-coordinate-map.json`,
- output to `assets/avatar/live2d/final/layers_png_same_canvas/`,
- update manifests, dashboard, docs, and records.

## What Codex cannot guarantee alone

Codex can create the same-canvas files, but the final alignment must still be visually checked by the user/rigger. This pack is not a finished `.moc3` model and not a final PSD.

## Master canvas spec

```text
canvas_size: 4096x4096
format: RGBA transparent PNG
safe_margin: 10% to 15%
background: transparent
purpose: allow future accessories, extra hair pieces, headset, microphone, jacket variants, expression overlays
```

## Important rule

Do not treat each layer as an independently centered part in the final same-canvas output.  
Each component must be placed where it belongs relative to `final_front_master.png`.

## Output folder

```text
assets/avatar/live2d/final/layers_png_same_canvas/
```

## Codex acceptance criteria

- All output layers are 4096x4096.
- All output layers are RGBA transparent PNG.
- Missing source files are reported, not silently ignored.
- `data/live2d-component-manifest.json` is updated.
- `data/same-canvas-coordinate-map.json` is updated.
- The dashboard marks:
  - PNGTuber: usable MVP
  - Live2D source components: ready
  - Same-canvas layer pack: pending visual review
  - Final PSD: pending

## Build Result

- Source PNG validation: 65 files exist and are RGBA.
- Layer/avatar transparency: 57 source PNGs have transparent alpha.
- Preview contact sheets: 8 `05_preview/*contact_sheet.png` files are RGBA but intentionally opaque.
- Same-canvas output: 34 PNG layers generated in `assets/avatar/live2d/final/layers_png_same_canvas/`.
- Output validation: every generated layer is 4096x4096 RGBA transparent PNG with visible pixels.

## Remaining Boundary

This Stage 06 pack is pending user/rigger visual review. It is not `final_layered_model.psd`, not a finished Live2D model, and not a `.moc3` rig.

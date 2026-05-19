# Codex Import Task — Minotaur Grand Mentor All-in-One Asset Handoff

You are inside the `Minotaur-Grand-Mentor` project.

## Hard bottom line

Do not modify anything outside this project root.  
Do not edit unrelated Obsidian notes, daily notes, templates, attachments, settings, or other repositories.

## What this package contains

- PNGTuber assets: `assets/avatar/pngtuber/`
- Live2D core components: `assets/avatar/live2d/components/core/`
- Group 01 eyes: `assets/avatar/live2d/components/eyes/`
- Group 02 mouth: `assets/avatar/live2d/components/mouth/`
- Group 03 brow/hair: `assets/avatar/live2d/components/brow_hair/`
- Group 04 collar/neck: `assets/avatar/live2d/components/body/`
- Group 05 occlusion fill: `assets/avatar/live2d/components/occlusion_fill/`
- Stage 06 blueprint: `docs/STAGE_06_SAME_CANVAS_BLUEPRINT.md`
- Same-canvas starter map: `data/same-canvas-coordinate-map.json`
- Same-canvas builder: `tools/build_same_canvas_pack.py`

## What to do

1. Validate all PNG files.
2. Update or create the asset manifest.
3. Keep existing PNGTuber overlay working.
4. Prepare Stage 06 same-canvas output.
5. Run:

```bash
python tools/build_same_canvas_pack.py
```

6. Update dashboard and records.
7. Do not claim this is a finished Live2D model.
8. Mark `final_layered_model.psd` as pending.

## Import Status

- PNGTuber MVP and optional expression PNGs are imported.
- Live2D component PNGs are imported.
- Stage 06 same-canvas layer pack has been generated.
- `final_layered_model.psd` remains pending.
- `.moc3` remains pending and must be produced by Live2D rigging work, not by this import.

# Asset Spec

## PNGTuber MVP Required Assets

Place these files in `assets/avatar/pngtuber/`:

- `idle_closed.png`
- `talk_open.png`
- `blink_closed.png`
- `happy.png`

## Optional Assets

- `angry.png`
- `thinking.png`
- `gesture_point.png`
- `shock.png`

## PNG Requirements

- Size: `2048x2048` or `3000x3000`.
- Format: transparent PNG.
- Composition: centered.
- Horns: fully visible.
- Body: half-body or bust.
- Design: consistent character design across all expressions.
- Character: brown minotaur, huge curved horns, golden eyes, black leather jacket, gold tech lines, blue-gold trading atmosphere.

## Asset Naming Rules

- Use lowercase filenames.
- Use underscores, not spaces.
- Keep manifest paths relative to the project root.
- Do not rename files without updating `data/avatar-manifest.json`.

## Live2D Upgrade Requirements

Future Live2D production should start from a layered PSD.

Required layer groups:

- `head`
- `muzzle`
- `eye_L`
- `eye_R`
- `eyelid_L`
- `eyelid_R`
- `horn_L`
- `horn_R`
- `ear_L`
- `ear_R`
- `hair_front`
- `hair_back`
- `jacket_body`
- `jacket_trim_gold`
- `mouth_A`
- `mouth_I`
- `mouth_U`
- `mouth_E`
- `mouth_O`
- `mouth_closed`
- `teeth`
- `tongue`

Layer names should be stable, English, lowercase or camel-safe, and clear enough for a rigger to understand without guessing.


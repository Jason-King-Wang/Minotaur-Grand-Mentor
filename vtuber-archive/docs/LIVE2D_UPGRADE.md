# Live2D Upgrade

The first version is a PNGTuber MVP. Live2D is a later upgrade after the character identity, expression set, and stream use are proven.

## Upgrade Flow

1. Finalize the PNGTuber character design.
2. Create a model sheet with front, side, back, expressions, and mouth shapes.
3. Produce a layered PSD.
4. Validate layer names and separations.
5. Hand off to a rigger.
6. Test in Live2D viewer or a web viewer.
7. Update overlay architecture only after the Live2D runtime target is chosen.

## Layered PSD Checklist

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
- separated shadows and highlights where rigging needs movement

## Rigger Handoff Checklist

- Character brief.
- Style guide.
- Model sheet.
- PSD with clean layer names.
- Expression list.
- Motion list.
- Mouth shape list.
- Expected viewer/runtime.
- Notes about horns, muzzle, jacket, and gold tech-line constraints.

## Viewer Direction

Possible future directions:

- Live2D Cubism Viewer for local testing.
- Web viewer for browser overlay.
- OBS integration after runtime selection.

## What Codex Can Do

- Maintain docs, manifest, dashboard, and static overlay code.
- Generate checklists and prompts.
- Validate file presence and project state.
- Build a future web viewer scaffold after the runtime choice is made.

## What Codex Cannot Do Alone

- Guarantee high-quality character art without actual art assets.
- Rig a production Live2D model without a layered PSD and rigging workflow.
- Replace human art direction and animation review.


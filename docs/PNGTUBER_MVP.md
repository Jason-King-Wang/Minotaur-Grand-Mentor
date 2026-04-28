# PNGTuber MVP

## Purpose

The PNGTuber MVP lets Minotaur Grand Mentor appear in OBS before Live2D art and rigging are available.

## Required Images

- `assets/avatar/pngtuber/idle_closed.png`
- `assets/avatar/pngtuber/talk_open.png`
- `assets/avatar/pngtuber/blink_closed.png`
- `assets/avatar/pngtuber/happy.png`

## Behavior

- Transparent OBS overlay.
- Audio-reactive talking state.
- Random blink every few seconds.
- Light breathing animation.
- Keyboard expression switching.
- Debug panel for microphone, threshold, volume, loaded assets, and missing assets.
- CSS/SVG placeholder when PNG assets are missing.

## Test URL

```text
overlay/index.html?debug=1&threshold=0.05&scale=1.0
```

## Upgrade Path

After the PNGTuber identity is stable, commission or create a Live2D-ready model sheet and layered PSD.


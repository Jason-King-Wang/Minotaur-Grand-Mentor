# OBS Setup

## Local File Overlay

Use this path for a direct local browser preview:

```text
file:///C:/Users/User/Documents/Obsidian%20Vault/Minotaur-Grand-Mentor/overlay/index.html
```

Debug version:

```text
file:///C:/Users/User/Documents/Obsidian%20Vault/Minotaur-Grand-Mentor/overlay/index.html?debug=1&threshold=0.05&scale=1.0
```

## GitHub Pages Overlay

After deploying the repo with GitHub Pages, use:

```text
https://YOUR-USER.github.io/YOUR-REPO/overlay/index.html
```

Dashboard:

```text
https://YOUR-USER.github.io/YOUR-REPO/dashboard/index.html
```

## OBS Browser Source Settings

- Source type: Browser Source.
- Width: `1920`.
- Height: `1080`.
- FPS: `30` or `60`.
- Custom CSS: leave empty for first test.
- Shutdown source when not visible: optional.
- Refresh browser when scene becomes active: useful during iteration.

## Transparent Background

The overlay uses a transparent background by default. In OBS, make sure no extra custom CSS adds a solid background.

## Microphone Permission

The overlay uses Web Audio API microphone volume detection. Browser microphone access may not work from every `file:///` context. If microphone status shows blocked or unavailable:

- Test inside OBS Browser Source.
- Or run a simple local static server.
- Or use GitHub Pages over HTTPS.

The overlay still renders a placeholder or avatar without microphone permission.

## Hotkeys

- `1`: default idle.
- `2`: happy.
- `3`: angry.
- `4`: thinking.
- `5`: gesture point.
- `0`: reset.
- `D`: toggle debug panel.


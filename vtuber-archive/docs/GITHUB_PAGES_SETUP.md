# GitHub Pages Setup

## Publish

1. Push this repository to GitHub.
2. Open repository settings.
3. Go to Pages.
4. Select the `main` branch.
5. Select root as the source folder.
6. Save and wait for deployment.

## URLs

Dashboard:

```text
https://jason-king-wang.github.io/Minotaur-Grand-Mentor/dashboard/
```

Overlay:

```text
https://jason-king-wang.github.io/Minotaur-Grand-Mentor/overlay/
```

Debug overlay:

```text
https://jason-king-wang.github.io/Minotaur-Grand-Mentor/overlay/?debug=1&threshold=0.05&scale=1.0
```

## Fallback Notes

The dashboard tries JSON fetch first. If fetch fails, it uses `data/dashboard-data.js` and `data/run-log.js` as static fallback data.


# Project Brief

> Disclaimer: This content is for research, education, and entertainment only. It does not constitute investment advice.

## Background

Minotaur Grand Mentor is an original VTuber project for a YouTube channel. The character is a brown minotaur with huge curved horns, golden eyes, a black leather jacket, gold tech-line details, and a blue-gold trading atmosphere.

The direction combines four pillars:

- Powerful and commanding presence.
- Wild minotaur energy.
- Financial trading visual language.
- AI Agent mentor identity.

The first version is not Live2D. It is a PNGTuber MVP that can run in OBS Browser Source as a static overlay.

## Channel Use

The character can appear in YouTube videos, livestreams, educational market research segments, AI workflow explanations, trading journal reviews, and dashboard walkthroughs.

The character must be framed as a mentor for learning, discipline, thinking systems, research, and risk awareness. It should not claim to provide direct investment instructions.

## Character Use

- Host avatar for YouTube.
- PNGTuber overlay for OBS.
- Mentor persona for educational narration.
- Future Live2D candidate.
- Visual identity for dashboards and project notes.

## Version Scope

### Version 1: PNGTuber MVP

- Static overlay.
- Required PNGTuber expression assets.
- Audio-reactive mouth switching.
- Blink animation.
- Placeholder fallback for missing images.
- Dashboard and records system.

### Version 2: Improved PNGTuber

- More expressions and gestures.
- Better animation timing.
- Stream scene variations.
- Refined dashboard state tracking.
- Optional local static server workflow for microphone permissions.

### Version 3: Live2D Upgrade

- Layered PSD production.
- Rigging checklist.
- Live2D viewer or web viewer direction.
- Motion and expression inventory.

## Success Criteria

- The repo opens cleanly in Obsidian.
- `overlay/index.html` works as an OBS Browser Source.
- Missing assets display a placeholder instead of breaking the overlay.
- `dashboard/index.html` shows project state, logs, tasks, links, and asset status.
- `tools/log_event.py` creates Markdown records and updates data files.
- `tools/validate_assets.py` reports missing assets without crashing.
- Tests confirm the required project files and JSON data exist.


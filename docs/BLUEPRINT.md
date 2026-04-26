# Blueprint

This project follows an Agent teaching workflow: create context, build the knowledge base, define goals and boundaries, produce a blueprint, execute the blueprint, and log every phase.

> Disclaimer: This content is for research, education, and entertainment only. It does not constitute investment advice.

## Phase 1: Project Scaffold

- Status: done
- Output: required folder structure, docs, data, overlay, dashboard, records, tools, and tests.
- Acceptance criteria: all required files exist at the expected paths.

## Phase 2: Documentation

- Status: done
- Output: project brief, character bible, style guide, asset spec, image prompts, OBS setup, Live2D upgrade notes, next actions.
- Acceptance criteria: docs define purpose, boundaries, asset rules, prompts, and non-advice disclaimer.

## Phase 3: Logging And Data System

- Status: done
- Output: `data/avatar-manifest.json`, `data/project-state.json`, `data/run-log.json`, `data/run-log.js`.
- Acceptance criteria: JSON files parse, JS run-log exposes `window.__MINOTAUR_RUN_LOG__`, and project state tracks phase, tasks, missing assets, and notes.

## Phase 4: Tools

- Status: done
- Output: `tools/log_event.py`, `tools/validate_assets.py`, `tools/build_public_data.py`.
- Acceptance criteria: tools use only Python standard library, do not overwrite old records, and tolerate missing assets.

## Phase 5: PNGTuber Overlay

- Status: done
- Output: `overlay/index.html`, `overlay/app.js`, `overlay/styles.css`.
- Acceptance criteria: transparent OBS overlay, placeholder fallback, audio-reactive talk state, random blink, debug panel, hotkeys, and URL parameters.

## Phase 6: Dashboard

- Status: done
- Output: `dashboard/index.html`, `dashboard/dashboard.js`, `dashboard/dashboard.css`.
- Acceptance criteria: static dashboard displays project state, missing assets, tasks, logs, docs links, overlay link, checklist, and disclaimer.

## Phase 7: OBS Test

- Status: ready
- Output: OBS setup instructions and local overlay entry point.
- Acceptance criteria: user can load `overlay/index.html` in OBS Browser Source and confirm microphone permission behavior.

## Phase 8: Live2D Upgrade

- Status: future
- Output: Live2D checklist and upgrade direction.
- Acceptance criteria: PSD layer checklist and rigger handoff checklist are defined before production begins.


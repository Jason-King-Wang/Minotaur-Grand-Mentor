# CODEX

## Required Reading Before Work

Before making changes, Codex must read:

- `SCOPE_LOCK.md`
- `docs/BOTTOM_LINES.md`
- `docs/CODEX_WORK_BLUEPRINT_FULL.md`
- `docs/BLUEPRINT.md`
- `docs/NEXT_ACTIONS.md`
- `data/project-state.json`

## Required Behavior

- Keep the project usable as a static site.
- Prefer vanilla HTML, CSS, JavaScript, and Python standard library.
- Do not introduce external packages unless there is a clear reason and the reason is documented first.
- Do not use API keys, tokens, private credentials, or personal data.
- Do not delete existing records.
- Do not overwrite old record files.
- Do not hard-code assets that do not exist.
- If an avatar image is missing, use the overlay placeholder fallback.
- Keep `data/run-log.json` and `data/run-log.js` in sync.
- Keep `data/dashboard-data.js` in sync by running `tools/build_public_data.py`.
- Keep `data/project-state.json` current after every phase.
- Run `tools/scope_guard.py` when changing project files.

## Completion Checklist

After each work phase:

1. Run or manually mirror the behavior of `tools/log_event.py`.
2. Update `data/project-state.json`.
3. Regenerate public data with `tools/build_public_data.py` if run-log data changed.
4. Preserve all existing Markdown records.
5. Do not modify files outside the `Minotaur-Grand-Mentor` project root.

## Financial Content Rule

The character may discuss markets for education, research, and entertainment, but must not be written as directly providing investment advice.

Required disclaimer:

> This content is for research, education, and entertainment only. It does not constitute investment advice.

# Short Term Radar MVP

This is a standalone subproject that currently lives under the Minotaur Grand Mentor repository for execution convenience.

Work from this directory:

```powershell
cd projects\short_term_radar_mvp
```

Start here:

- [SHORT_TERM_RADAR_HANDOFF.md](SHORT_TERM_RADAR_HANDOFF.md)
- [short_term_radar/README.md](short_term_radar/README.md)

Safe upload scope:

- Include this folder: `projects/short_term_radar_mvp/`
- Do not place radar source files at repository root.
- Do not upload raw data, processed data, cache files, local config, secrets, logs, or broker runtime files.

CL6 mode behavior:

- `simple_price_volume_mode` can scan, backtest, compare baselines, and report with price/universe data only.
- `semi_full_short_term_radar` starts when revenue and surveillance slots are installed.
- `full_short_term_radar` requires the price, universe, revenue, chip, surveillance, catalyst, corporate, valuation, and calendar slots to be `installed`; partial slots cannot trigger full mode.

Scan outputs include `mode`, `score_data_coverage_ratio`, `robot_slot_coverage_ratio`, and `robot_slot_statuses`.

Official source smoke status:

- `monthly_revenue`: MOPS official request builder/parser/normalizer is wired for dry-run and small-range smoke; failed fetches degrade without writing empty processed tables.
- `institutional_trading`: TWSE T86 and TPEx 3-institution JSON parser fixtures, official dry-run, and single-date collector wiring are in place. Full historical backfill remains local-only follow-up work.
- `margin_short`: DC-bot official OpenAPI skeleton now prefers project-configured API URLs and has fixture-backed parsing/merge coverage for margin + SBL payloads. Live endpoint verification/backfill remains pending.
- `material_events`, `corporate_actions`, `valuation`, and `symbol_master`: DC-bot official OpenAPI dry-run skeletons are integrated for endpoint visibility and conservative degraded collection. Full live field mapping/backfill remains pending.

DC-bot full remaining task notes are archived under `docs/codex_short_term_radar_full_remaining_tasks_2026-05-12.md` and `docs/codex_short_term_radar_full_remaining_tasks_status_2026-05-12.md`.

Important local-only paths:

- `configs/short_term_radar/local.yaml`
- `data/raw/`
- `data/processed/`
- `data/tmp/`

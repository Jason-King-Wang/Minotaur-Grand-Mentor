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

Important local-only paths:

- `configs/short_term_radar/local.yaml`
- `data/raw/`
- `data/processed/`
- `data/tmp/`

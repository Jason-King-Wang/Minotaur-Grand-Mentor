# Short Term Radar MVP Handoff

Last updated: 2026-05-12

## CL6 Status

CL6 fixes the project boundary and cleans up the official backfill wiring. Short Term Radar is a subproject only:

```text
projects/short_term_radar_mvp/
```

The repository root remains Minotaur Grand Mentor. Radar code, configs, tests, fixtures, reports, and handoff files belong inside this subproject folder.

## Completed In CL6

- Restored repository-root scope: root README remains Minotaur Grand Mentor, and radar files live under `projects/short_term_radar_mvp/`.
- Kept radar `.gitignore` inside this project; root `.gitignore` must not contain radar-specific rules.
- Updated handoff and commands to use `projects/short_term_radar_mvp` as the working directory.
- Fixed `monthly_revenue` announce-date inference so `fetched_at` is never treated as public availability.
- Split `data.gov.tw` source metadata into `landing_url` and `download_url`; landing pages are not fetched as CSV files.
- Made `collect --write-raw` real for official MOPS monthly revenue raw HTML, and explicit-error for unsupported datasets.
- Fixed `breakout_120d_only` baseline to accept only `breakout_120d_flag = true`.
- Changed daily coverage expected dates to use processed `prices_daily` trading dates when available, with weekday fallback instead of counting weekends.
- Removed duplicate score-cap logic from the old scoring path and centralized score breakdown behavior.
- Split coverage output into `score_data_coverage_ratio` and `robot_slot_coverage_ratio`.
- Added scope guard tests so radar files do not drift back to repository root.

## Work From Here

```powershell
cd projects\short_term_radar_mvp
```

## Verification Commands

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
```

## Official Monthly Revenue

Dry-run URL generation:

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs/short_term_radar/local.yaml `
  --dataset monthly_revenue `
  --market all `
  --start-month 2021-01 `
  --end-month 2026-05 `
  --source official `
  --dry-run
```

Small normalize/validate smoke test:

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs/short_term_radar/local.yaml `
  --dataset monthly_revenue `
  --market all `
  --start-month 2026-01 `
  --end-month 2026-03 `
  --source official `
  --normalize `
  --validate
```

Raw HTML capture, when intentionally needed:

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs/short_term_radar/local.yaml `
  --dataset monthly_revenue `
  --market TWSE `
  --start-month 2026-01 `
  --end-month 2026-01 `
  --source official `
  --write-raw
```

Raw output stays local under `data/raw/` and must not be committed.

## Coverage Reports

```powershell
py -3.14 -m short_term_radar.cli.coverage `
  --config configs/short_term_radar/local.yaml `
  --start 2021-01-01 `
  --end 2026-05-11 `
  --write-reports
```

Outputs:

- `data/quality/data_coverage_report.csv`
- `data/quality/missing_dates_report.csv`
- `data/quality/freshness_report.csv`

## Backtest With Baselines

```powershell
py -3.14 -m short_term_radar.cli.backtest `
  --config configs/short_term_radar/default.yaml `
  --start 2021-05-01 `
  --end 2026-04-30 `
  --top-n 20 `
  --horizon-days 126 `
  --target-multiple 3 `
  --include-baselines `
  --random-seed 42 `
  --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv
```

## Safety

Do not commit or upload:

- `configs/short_term_radar/local.yaml`
- `.env`, tokens, credentials, or broker logs
- `data/raw/`
- `data/processed/`
- `data/tmp/`
- cache files or live downloaded datasets

Broker integrations must remain read-only. No account mutation, order placement, order modification, or order cancellation calls belong in this project.

## Remaining Work

- Institutional trading and margin/short official fetchers still need full direct endpoint parsers.
- Material events and corporate actions official fetchers still need full direct endpoint parsers.
- TPEx surveillance requires real `download_url` values before live CSV collection; dataset landing pages remain reference-only.
- Full five-year official backfill should run locally and remain outside source control.

# Short Term Radar MVP

Standalone Taiwan stock short-term radar MVP for finding candidates with possible strong 126-trading-day upside. The package is read-only for broker APIs and never places, modifies, or cancels orders.

## What Is Implemented

- Daily candidate scan with price/volume, revenue, chip, catalyst, surveillance, corporate-action, and valuation adapters.
- Graceful degradation when processed tables are missing.
- Weighted `ScoreBreakdown` in scan output: raw available normalized score, coverage-adjusted score, score cap, `score_data_coverage_ratio`, `robot_slot_coverage_ratio`, `robot_slot_statuses`, `mode`, available/degraded radars, and core-data-ready flag.
- Stage gating: missing revenue blocks S3 candidate entry; active disposition forces S5 / `avoid_chasing`.
- Monthly top-N backtest with 3x/5x forward labels.
- Baseline comparisons: radar model, deterministic random top-N, 120D breakout, volume expansion, and moving-average alignment.
- Markdown report generation with data coverage, S3/S2/S5 sections, degraded radar summary, baseline comparison, backtest metrics, and source freshness warning.
- Data-source registry, official-source dry-runs, normalizers, quality checks, and processed-table storage helpers.
- Atomic processed-table `append`, `upsert`, and `replace` merge modes with primary-key dedupe.

Run every command from the subproject root:

```powershell
cd projects\short_term_radar_mvp
```

## Config

Use env vars for local data paths:

```powershell
copy configs\short_term_radar\local.yaml.example configs\short_term_radar\local.yaml
$env:TW_RADAR_DATA_ROOT="C:\path\to\short_term_radar_data"
$env:TW_EQUITIES_DATA_PATH="C:\path\to\tw_equities"
```

`TW_EQUITIES_DATA_PATH` may point directly to a daily-price parquet file, for example `...\data\processed\prices_daily.parquet`.

Do not commit `configs/short_term_radar/local.yaml`, raw/processed data, secrets, logs, or broker runtime files.

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

Monthly revenue is gated by `announce_date <= as_of_date`. If the MOPS source does not provide an announce date, the normalizer infers `next month day 10` from `revenue_month` and marks `announce_date_inferred = true`. It never uses `fetched_at` as the public announce date.

## Official Source URLs

`data.gov.tw` dataset pages are tracked as `landing_url` only. Collectors must use `download_url` or `api_url` for direct file/API downloads; empty direct endpoints mean the source is registry/dry-run only until a real endpoint is configured.

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

## Verification

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
```

Latest verified result: `48 passed`.

## Still Pending

- Full live endpoint parsers for institutional trading, margin/short, material events, and corporate actions.
- Full five-year official backfill. Keep generated raw/processed data outside commits.
- TWSE surveillance free endpoint remains registry-only; TPEx dry-run/live skeleton exists, and TWSE e-shop is disabled by default.

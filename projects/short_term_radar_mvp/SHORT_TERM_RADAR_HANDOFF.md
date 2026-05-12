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
- Split `data.gov.tw` source metadata into `landing_url`, `download_url`, and `api_url`; landing pages are not fetched as CSV files.
- Added TWSE/TPEx OpenAPI source candidates from `radar_system_data_sources.md` for revenue, institutional trading, margin/short, material events, corporate actions, trading calendar, and valuation.
- Made `collect --write-raw` real for official MOPS monthly revenue raw HTML, and explicit-error for unsupported datasets.
- Fixed `breakout_120d_only` baseline to accept only `breakout_120d_flag = true`.
- Changed daily coverage expected dates to use processed `prices_daily` trading dates when available, with weekday fallback instead of counting weekends.
- Marked `material_events` and `corporate_actions` as event-driven in coverage reports so they do not emit daily missing rows.
- Marked surveillance as `source_missing` when no enabled direct download/API source is configured, avoiding false missing-date floods.
- Removed duplicate score-cap logic from the old scoring path and centralized score breakdown behavior.
- Split coverage output into `score_data_coverage_ratio` and `robot_slot_coverage_ratio`.
- Added scan/report `mode` and `robot_slot_statuses` fields for simple/semi/full operation.
- Added scope guard tests so radar files do not drift back to repository root.
- Added full-mode guard coverage so `full_short_term_radar` cannot be triggered by partial core slots.
- Added an injected-API, read-only Shioaji source for `surveillance_daily` and `margin_short_daily`; it normalizes `notice()`, `punish()`, `credit_enquires()`, `short_stock_sources()`, and contract balance fields without login, credentials, CA activation, or order calls.
- Hardened official MOPS monthly revenue smoke coverage for TWSE/TPEx and local/foreign request generation, degraded fetch handling, and no-empty-processed-table writes.
- Added official institutional-trading parser/collector wiring for TWSE T86 JSON and TPEx 3-institution JSON, including fixture parser tests, CLI dry-run, degraded fetch handling, and processed-table upsert coverage.

## Work From Here

```powershell
cd projects\short_term_radar_mvp
```

## Verification Commands

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
```

Latest local result:

- `py -3.14 -m pytest -q tests\short_term_radar` -> `62 passed`
- `py -3.14 -m compileall -q short_term_radar tests\short_term_radar` -> passed

The simple-mode scan/backtest/report commands also completed locally with the five-year daily price file:

```powershell
$env:TW_EQUITIES_DATA_PATH="C:\Users\User\Documents\New project 4\data\processed\prices_daily.parquet"
$env:TW_RADAR_DATA_ROOT="C:\Users\User\Documents\New project 4\data"
```

Results:

- Scan `2026-04-30`: 50 candidates.
- Backtest `2021-05-01..2026-04-30`: 1083 radar-model candidate rows.
- Baseline comparison generated for radar model, random top-N, 120D breakout, volume expansion, and MA alignment.

## Robot Slot Status

| Slot | Status | Notes |
|---|---|---|
| PRICE_SLOT | installed | Simple mode can load daily OHLCV from `TW_EQUITIES_DATA_PATH` / configured `daily_price_path`. |
| UNIVERSE_SLOT | partial | Symbol metadata can be loaded from processed `symbol_master`; price rows can still run simple mode without a full universe table. |
| REVENUE_SLOT | partial | MOPS official fetcher/parser exists and small-range smoke is wired; live five-year backfill has not been run in source control. |
| CHIP_SLOT | partial | TWSE/TPEx institutional-trading official parser/dry-run exists. Shioaji read-only margin/short availability hooks exist; full official historical backfill remains pending. |
| SURVEILLANCE_SLOT | partial | Shioaji read-only `notice()`/`punish()` hooks and TPEx skeleton exist; TWSE free endpoint remains pending. |
| CATALYST_SLOT | partial | Manual catalysts and material-event normalizer/classifier exist; live official fetcher remains pending. |
| CORPORATE_SLOT | partial | Corporate-action normalizer/adapter exists; live official fetcher remains pending. |
| FINANCIAL_SLOT | partial | Financial normalizer exists; scoring/fetcher integration remains pending. |
| VALUATION_SLOT | partial | Valuation normalizer/adapter exists; live official fetcher remains pending. |
| CALENDAR_SLOT | partial | Coverage/backtest derive trading days from `prices_daily`; a full exchange holiday calendar remains pending. |

## Operation Modes

- `simple_price_volume_mode`: price/universe path only. Scan, backtest, baseline comparison, and report can run; `core_data_ready_flag = false`; missing revenue prevents S3 candidate entry.
- `semi_full_short_term_radar`: revenue and surveillance slots are installed, allowing higher-confidence candidates if not under disposition.
- `full_short_term_radar`: price, universe, revenue, chip, surveillance, catalyst, corporate, valuation, and calendar slots are all `installed`; partial slots cannot trigger full mode.

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

## Official Institutional Trading

Dry-run single-date URL generation:

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs/short_term_radar/data_sources.example.yaml `
  --dataset institutional_trading `
  --market TWSE `
  --date 2026-04-30 `
  --source official `
  --dry-run
```

Small normalize/validate smoke test, when local config and network are available:

```powershell
py -3.14 -m short_term_radar.cli.collect `
  --config configs/short_term_radar/local.yaml `
  --dataset institutional_trading `
  --market TWSE `
  --date 2026-04-30 `
  --source official `
  --normalize `
  --validate
```

If a live endpoint is unavailable or returns no rows, collect prints a degraded message and skips processed-table writes instead of creating an empty slot artifact.

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
The Shioaji source requires an externally managed API object and intentionally does not read `.env`, login, activate CA, or construct orders.

## Remaining Work

- Institutional trading now has TWSE/TPEx official parser and single-date collect wiring; full historical backfill still needs a local run and endpoint stability review.
- Margin/short official fetchers still need full direct endpoint parsers.
- Material events and corporate actions official fetchers still need full direct endpoint parsers.
- `data_sources.example.yaml` now records direct OpenAPI candidates where known; parser/backfill work remains pending.
- TPEx surveillance requires real `download_url` values before live CSV collection; dataset landing pages remain reference-only.
- A full official TWSE/TPEX trading-calendar source is still needed; current coverage uses processed price trading days.
- Full five-year official backfill should run locally and remain outside source control.

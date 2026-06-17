# Short Term Radar MVP

Standalone MVP for a Taiwan stock short-term radar targeting candidates that may have strong 126-trading-day upside. It is read-only and does not place, modify, or cancel broker orders.

## Data

The daily price adapter reads CSV or parquet files from `data.daily_price_path`. A single file or a directory of files is supported. It auto-detects common column names and normalizes these fields:

`symbol`, `name`, `industry`, `trade_date`, `open`, `high`, `low`, `close`, `volume`, `amount`, `market`.

If `amount` is missing, the MVP uses `close * volume`.

TAIEX can be retrieved from SinoPac/Shioaji market data when a caller passes in an already logged-in API object. The broker adapter is read-only, looks for index contracts under `api.Contracts.Indexs` using `data.market_index_contract_candidates`, and calls `api.kbars(...)`. It does not handle credentials and has no order placement, modification, or cancellation methods.

## Data Source Layer

The data-source layer is scaffolded under `short_term_radar/data_sources/` and is designed to degrade gracefully when live network, credentials, paid subscriptions, or raw backfills are unavailable.

Implemented pieces:

- `configs/short_term_radar/data_sources.example.yaml`
- `configs/short_term_radar/local.yaml.example`
- Dataset registry for P0/P1 tables.
- Normalizers for symbol master, daily prices, monthly revenue, institutional trading, margin/short, surveillance, corporate actions, material events, financials, insider holding, and valuation.
- Shared Taiwan date/number parsing utilities.
- Quality checks for schema, primary-key duplicates, dates, market values, symbol/source/fetched metadata.
- Dry-run CLI commands for collect, normalize, validate, and coverage.
- Processed-data adapters that load local `data/processed/*.parquet` or `.csv` when available.
- Local existing-cache collectors for `symbol_master` and `prices_daily`.

Processed table names:

`symbol_master`, `prices_daily`, `monthly_revenue`, `institutional_trading_daily`, `margin_short_daily`, `surveillance_daily`, `corporate_actions`, `material_events`, `financial_statement_quarterly`, `insider_holding_monthly`, `valuation_daily`.

The current implementation can backfill `symbol_master` and `prices_daily` from the existing local Taiwan equities cache configured by `existing_daily_price_path`. Live public-data backfill for revenue, institutional trading, margin/short, surveillance, corporate actions, and material events is still registry/interface work only.

## Current Progress

目前做到：

- `symbol_master.parquet`: 2,119 rows, quality ok.
- `prices_daily.parquet`: 2,210,492 rows, quality ok.
- Data-source registry, normalizers, quality checks, fixtures, and dry-run CLIs are implemented.
- Processed-data adapters are wired into scan gating.
- Missing revenue caps stage to S2; active disposition forces S5 / `avoid_chasing`.
- `normalize --input` can turn a local source CSV into processed parquet.

還差：

- External official-source backfill for monthly revenue, institutional trading, margin/short, surveillance, corporate actions, material events, financials, insider holding, and valuation.
- Real processed revenue/chip/catalyst/surveillance data so scan results stop being fully degraded.
- Coverage/freshness/missing-date reports as persisted CSV outputs.

Recommended next step: implement `monthly_revenue` official-source backfill first.

## Commands

The bundled Taiwan OHLCV parquet cache is currently referenced from:

`C:\Users\User\Documents\New project 6\tw-golden-cross-star\data\tw_equities`

Use Python 3.14 on this machine because it has `pandas` and `pyarrow` installed for parquet reads.

```powershell
py -3.14 -m short_term_radar.cli.scan --config configs/short_term_radar/default.yaml --date 2026-04-30 --top 50 --output reports/short_term_radar/scan_2026-04-30.csv

py -3.14 -m short_term_radar.cli.backtest --config configs/short_term_radar/default.yaml --start 2021-05-01 --end 2026-04-30 --rebalance monthly --top-n 20 --horizon-days 126 --target-multiple 3 --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv

py -3.14 -m short_term_radar.cli.report --scan-file reports/short_term_radar/scan_2026-04-30.csv --backtest-file reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv --output reports/short_term_radar/report_2026-04-30.md
```

Data-source dry runs:

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml.example --dataset symbol_master --market all --dry-run
py -3.14 -m short_term_radar.cli.normalize --config configs/short_term_radar/local.yaml.example --dataset all --dry-run
py -3.14 -m short_term_radar.cli.validate_data --config configs/short_term_radar/local.yaml.example --dataset all --dry-run
py -3.14 -m short_term_radar.cli.coverage --config configs/short_term_radar/local.yaml.example --start 2021-01-01 --end 2026-05-11 --dry-run
```

Local existing-cache backfill:

```powershell
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml.example --dataset symbol_master --market all
py -3.14 -m short_term_radar.cli.collect --config configs/short_term_radar/local.yaml.example --dataset prices_daily --market all --start 2021-01-01 --end 2026-05-11
py -3.14 -m short_term_radar.cli.validate_data --config configs/short_term_radar/local.yaml.example --dataset symbol_master --as-of 2026-05-11
py -3.14 -m short_term_radar.cli.validate_data --config configs/short_term_radar/local.yaml.example --dataset prices_daily --as-of 2026-05-11
```

Normalize a downloaded/source CSV into processed parquet:

```powershell
py -3.14 -m short_term_radar.cli.normalize --config configs/short_term_radar/local.yaml.example --dataset monthly_revenue --input path\to\monthly_revenue.csv --market TWSE --source twse --source-url https://data.gov.tw/dataset/18420 --as-of 2026-05-11
```

## MVP Scope

- Price/volume feature calculation.
- Price-only expectation-gap proxy.
- Simple theme-group score when `industry` is available.
- Risk penalty and stage classification.
- Monthly top-N backtest using forward labels.
- Markdown report generation.

## Graceful Degradation

Revenue, chip, catalyst, surveillance, corporate-action, and valuation adapters read processed local tables when those tables exist. Missing source tables do not break scans or backtests: output risk flags mark degraded radar inputs, total score is capped when core sources are missing, missing revenue prevents `S3 candidate_entry`, and active disposition forces `S5 avoid_chasing`.

Monthly revenue features are gated by `announce_date <= as_of_date`; `revenue_month` alone is never treated as proof that data was public.

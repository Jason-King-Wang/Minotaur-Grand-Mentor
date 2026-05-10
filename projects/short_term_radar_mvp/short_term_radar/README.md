# Short Term Radar MVP

Standalone MVP for a Taiwan stock short-term radar targeting candidates that may have strong 126-trading-day upside. It is read-only and does not place, modify, or cancel broker orders.

## Data

The daily price adapter reads CSV or parquet files from `data.daily_price_path`. A single file or a directory of files is supported. It auto-detects common column names and normalizes these fields:

`symbol`, `name`, `industry`, `trade_date`, `open`, `high`, `low`, `close`, `volume`, `amount`, `market`.

If `amount` is missing, the MVP uses `close * volume`.

TAIEX can be retrieved from SinoPac/Shioaji market data when a caller passes in an already logged-in API object. The broker adapter is read-only, looks for index contracts under `api.Contracts.Indexs` using `data.market_index_contract_candidates`, and calls `api.kbars(...)`. It does not handle credentials and has no order placement, modification, or cancellation methods.

## Commands

The bundled Taiwan OHLCV parquet cache is currently referenced from:

`C:\Users\User\Documents\New project 6\tw-golden-cross-star\data\tw_equities`

Use Python 3.14 on this machine because it has `pandas` and `pyarrow` installed for parquet reads.

```powershell
py -3.14 -m short_term_radar.cli.scan --config configs/short_term_radar/default.yaml --date 2026-04-30 --top 50 --output reports/short_term_radar/scan_2026-04-30.csv

py -3.14 -m short_term_radar.cli.backtest --config configs/short_term_radar/default.yaml --start 2021-05-01 --end 2026-04-30 --rebalance monthly --top-n 20 --horizon-days 126 --target-multiple 3 --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv

py -3.14 -m short_term_radar.cli.report --scan-file reports/short_term_radar/scan_2026-04-30.csv --backtest-file reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv --output reports/short_term_radar/report_2026-04-30.md
```

## MVP Scope

- Price/volume feature calculation.
- Price-only expectation-gap proxy.
- Simple theme-group score when `industry` is available.
- Risk penalty and stage classification.
- Monthly top-N backtest using forward labels.
- Markdown report generation.

## Graceful Degradation

The revenue, chip, and catalyst adapters are placeholders in this MVP. Their scores are `null`, and total score weights are re-normalized across available radar scores. Output risk flags mark those missing radar inputs as degraded.

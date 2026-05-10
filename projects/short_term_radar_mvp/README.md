# Short Term Radar MVP V2

Standalone Taiwan stock short-term radar for research and education. It is designed to find early short-term candidates while avoiding score inflation when core data is missing.

This project is scoped to `projects/short_term_radar_mvp/` and is independent from the rest of the Minotaur repo.

## Safety

- Broker integration is read-only market data only.
- No order placement, order update, cancellation, position, balance, or account mutation APIs are exposed.
- No credentials, `.env`, logs, Discord runtime files, caches, SQLite files, or unrelated local assets are included.
- This is not investment advice.

## Config

Public config uses environment variables:

```powershell
$env:TW_EQUITIES_DATA_PATH="C:\path\to\tw_equities"
$env:TW_MONTHLY_REVENUE_PATH="C:\path\to\monthly_revenue.csv" # optional
$env:TW_CHIP_DATA_PATH="C:\path\to\chip.csv"                  # optional
$env:TW_CATALYST_PATH="C:\path\to\catalysts.yaml"             # optional
```

Use `configs/short_term_radar/local.yaml.example` as the template for an ignored `local.yaml`.

## V2 Changes

- Adds score coverage fields: `score_raw_available_norm`, `score_coverage_adjusted`, `score_cap`, `data_coverage_ratio`, `available_radars`, `degraded_radars`, and `core_data_ready_flag`.
- Caps scores when revenue/chip/catalyst are missing, so price-only candidates cannot be promoted as high-confidence core candidates.
- Blocks `S3 candidate_entry` when revenue data is missing or data coverage is low.
- Adds local CSV/Parquet revenue and chip adapters, plus CSV/YAML catalyst support.
- Renames backtest metrics to explicit max-return and close-return fields.
- Adds path-based max drawdown and 2x/3x/5x hit metrics.
- Adds baselines: random, 120D breakout, volume expansion, and MA alignment.
- Adds elastic universe filters to avoid mixing mega-cap trend names into a 3x candidate list.

## Commands

```powershell
py -3.14 -m short_term_radar.cli.scan --config configs/short_term_radar/default.yaml --date 2026-04-30 --top 50 --output reports/short_term_radar/scan_2026-04-30.csv

py -3.14 -m short_term_radar.cli.backtest --config configs/short_term_radar/default.yaml --start 2021-05-01 --end 2026-04-30 --rebalance monthly --top-n 20 --horizon-days 126 --target-multiple 3 --include-baselines true --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv

py -3.14 -m short_term_radar.cli.report --scan-file reports/short_term_radar/scan_2026-04-30.csv --backtest-file reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv --baseline-file reports/short_term_radar/baseline_comparison_2021-05-01_2026-04-30.csv --output reports/short_term_radar/report_2026-04-30.md
```

## Validation

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
```

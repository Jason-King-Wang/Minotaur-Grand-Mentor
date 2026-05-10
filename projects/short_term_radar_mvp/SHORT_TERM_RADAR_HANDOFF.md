# Short Term Radar MVP V2 Handoff

Last updated: 2026-05-11

Repository target: `Jason-King-Wang/Minotaur-Grand-Mentor`
PR branch: `codex/upload-short-term-radar`
Upload scope: `projects/short_term_radar_mvp/`

## Scope Guard

Only this folder is part of the V2 update:

```text
projects/short_term_radar_mvp/
```

Do not modify the VTuber, overlay, dashboard, docs, assets, records, obsidian, tools, or unrelated project folders in the parent repo. External local data paths are read-only inputs and must not be modified.

## What V2 Fixes

- Prevents score inflation when core radars are missing.
- Adds score coverage and confidence fields.
- Blocks `S3 candidate_entry` when revenue is missing, revenue score is weak, data coverage is low, or risk is high.
- Adds local CSV/Parquet revenue and chip adapters.
- Adds CSV/YAML catalyst adapter.
- Keeps optional data graceful: missing revenue/chip/catalyst degrades and caps the score instead of breaking scans.
- Renames backtest metrics to distinguish forward max return from close return.
- Adds path-based max drawdown, 2x/3x/5x hit rates, and time-to-hit fields.
- Adds baseline comparisons: random, 120D breakout, volume expansion, and MA alignment.
- Replaces public hard-coded local paths with environment-variable config and ignored `local.yaml`.
- Keeps the broker API adapter read-only.

## Main Files

- `short_term_radar/config.py`
- `short_term_radar/pipeline.py`
- `short_term_radar/schemas.py`
- `short_term_radar/adapters/`
- `short_term_radar/features/`
- `short_term_radar/scoring/`
- `short_term_radar/backtest/`
- `short_term_radar/cli/`
- `configs/short_term_radar/default.yaml`
- `configs/short_term_radar/local.yaml.example`
- `tests/short_term_radar/`
- `reports/short_term_radar/`

## Config

Public config expects:

```powershell
$env:TW_EQUITIES_DATA_PATH="C:\path\to\tw_equities"
$env:TW_MONTHLY_REVENUE_PATH="C:\path\to\monthly_revenue.csv" # optional
$env:TW_CHIP_DATA_PATH="C:\path\to\chip.csv"                  # optional
$env:TW_CATALYST_PATH="C:\path\to\catalysts.yaml"             # optional
```

For local use, copy `configs/short_term_radar/local.yaml.example` to `configs/short_term_radar/local.yaml`. The real `local.yaml` is ignored by git.

## Score Fields

Scan output now includes:

- `score_raw_available_norm`
- `score_coverage_adjusted`
- `score_cap`
- `score_total`
- `data_coverage_ratio`
- `available_radars`
- `degraded_radars`
- `core_data_ready_flag`
- `expectation_gap_source`

When revenue, chip, and catalyst are all missing, score is capped at 70. Missing revenue caps score at 75 and prevents `S3`.

## Stage Rules

- `S0`: no usable score.
- `S1`: observation/watch-only.
- `S2`: early watch, commonly when revenue is missing.
- `S3`: candidate entry; requires revenue score >= 60, coverage >= 0.60, breakout/volume confirmation, and low risk.
- `S4`: hold/trail or wait pullback.
- `S5`: avoid chasing.

## Backtest Outputs

- `forward_max_return`
- `forward_close_return`
- `forward_min_return_from_entry`
- `forward_path_max_drawdown`
- `hit_2x`, `hit_3x`, `hit_5x`
- `time_to_2x_days`, `time_to_3x_days`, `time_to_5x_days`

Summary outputs use explicit names such as `avg_forward_max_return`, not the ambiguous old `avg_forward_return`.

## Commands Verified

```powershell
py -3.14 -m pytest -q tests\short_term_radar
py -3.14 -m compileall -q short_term_radar tests\short_term_radar

py -3.14 -m short_term_radar.cli.scan --config configs/short_term_radar/default.yaml --date 2026-04-30 --top 50 --output reports/short_term_radar/scan_2026-04-30.csv

py -3.14 -m short_term_radar.cli.backtest --config configs/short_term_radar/default.yaml --start 2021-05-01 --end 2026-04-30 --rebalance monthly --top-n 20 --horizon-days 126 --target-multiple 3 --include-baselines true --random-trials 30 --seed 42 --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv

py -3.14 -m short_term_radar.cli.report --scan-file reports/short_term_radar/scan_2026-04-30.csv --backtest-file reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv --baseline-file reports/short_term_radar/baseline_comparison_2021-05-01_2026-04-30.csv --output reports/short_term_radar/report_2026-04-30.md
```

The validation run used `TW_EQUITIES_DATA_PATH` pointing to the existing local Taiwan OHLCV cache as a read-only input.

## Last Verified Results

```text
pytest: 25 passed
compileall: passed
scan: wrote 50 candidates
backtest: wrote summary, candidate details, baseline comparison, and baseline details
report: wrote reports/short_term_radar/report_2026-04-30.md
```

## Generated Outputs

- `reports/short_term_radar/scan_2026-04-30.csv`
- `reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv`
- `reports/short_term_radar/backtest_2021-05-01_2026-04-30_candidates.csv`
- `reports/short_term_radar/baseline_comparison_2021-05-01_2026-04-30.csv`
- `reports/short_term_radar/baseline_details_2021-05-01_2026-04-30.csv`
- `reports/short_term_radar/report_2026-04-30.md`

## Remaining Data Work

- Connect reliable public monthly revenue source.
- Connect institutional investor and margin/short historical data.
- Maintain a manual catalyst file or connect a vetted event data source.
- Verify whether the daily price source includes delisted securities to reduce survivorship bias.

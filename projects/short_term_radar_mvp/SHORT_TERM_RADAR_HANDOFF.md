# Short Term Radar MVP Handoff

Last updated: 2026-05-10

## Goal

Build the MVP from `codex_short_term_radar_spec.md`: a standalone Taiwan stock short-term radar for candidates that may have strong 126-trading-day upside. The implementation must stay independent from existing projects, be read-only for broker APIs, support daily scans, support five-year backtests, and degrade gracefully when some data sources are missing.

## Current Status

MVP success criteria are complete:

1. Daily candidate scan can run.
2. Each candidate has total score, radar sub-scores, stage, entry zone, reasons, risks, and latest price/volume metrics.
3. Five-year daily-data backtest can run.
4. Top-N 126-trading-day 3x / 5x hit-rate outputs are generated.
5. Markdown report generation works.
6. Missing data does not break the system; unavailable radars are marked as degraded and total score is re-normalized across available scores.

## Implemented Files

Core package:

- `short_term_radar/`
- `short_term_radar/adapters/`
- `short_term_radar/features/`
- `short_term_radar/scoring/`
- `short_term_radar/backtest/`
- `short_term_radar/cli/`
- `short_term_radar/utils/`

Config and tests:

- `configs/short_term_radar/default.yaml`
- `tests/short_term_radar/`
- `pytest.ini`

Generated outputs:

- `reports/short_term_radar/scan_2026-04-30.csv`
- `reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv`
- `reports/short_term_radar/backtest_2021-05-01_2026-04-30_candidates.csv`
- `reports/short_term_radar/report_2026-04-30.md`

## Data Source Currently Used

The workspace did not contain five-year daily data. The usable local cache was found here:

```text
C:\Users\User\Documents\New project 6\tw-golden-cross-star\data\tw_equities
```

`configs/short_term_radar/default.yaml` points to that cache. It contains TWSE/TPEX daily OHLCV parquet files and `reference/symbol_master.csv`.

Run with Python 3.14 on this machine because that environment has `pandas`, `pyarrow`, and `yaml`.

## Broker API Status

SinoPac/Shioaji support was added only as a read-only market-data adapter:

- File: `short_term_radar/adapters/broker_api_adapter.py`
- Test: `tests/short_term_radar/test_broker_api_adapter.py`
- It accepts an already logged-in API object from the caller.
- It does not handle credentials.
- It has no order placement, modification, cancellation, or account mutation methods.

What can come from SinoPac/Shioaji:

- TAIEX / stock K bars via `kbars`
- ticks
- snapshots
- daily quotes
- attention / disposition stock lists via `notice()` and `punish()`
- margin/short availability via `credit_enquires()`
- short stock source via `short_stock_sources()`
- scanner rankings via `scanners()`
- stock/index contract metadata

What still needs other data sources:

- monthly revenue
- financial statements
- three major institutional investor daily buy/sell
- news/social/analyst coverage
- insider holding changes
- pledge ratio
- structured catalyst event calendar

## Completed By Spec Area

Phase 1, data and price-volume radar:

- Standalone directory created.
- Daily price adapter supports CSV and parquet.
- Basic filters implemented: trading days, average amount, ETF/warrant/full-delivery style exclusions where identifiable.
- Price-volume features implemented: returns, moving averages, RS vs market, breakout flags, volume z-score, volume expansion.
- Price-volume scoring and generated reasons implemented.
- `scan` CLI implemented.

Phase 2, scoring and stage:

- Scoring engine implemented.
- Price-only expectation-gap proxy implemented.
- Stage classifier implemented: S0 to S5.
- Entry zone implemented: `watch_only`, `early_watch`, `candidate_entry`, `hold_or_trail`, `avoid_chasing`.
- Crowding/risk penalty implemented from price-volume signals.
- Scan output includes the expected complete field set.

Phase 3, backtest:

- Forward labeler implemented: forward max return, forward close return, max drawdown, hit_3x, hit_5x.
- Monthly rebalance top-N backtest implemented.
- Summary and candidate details are written.
- No-future-leakage test added.

Phase 4, extra adapters:

- Revenue, chip, and catalyst adapters exist as MVP placeholders.
- Graceful degradation is implemented for missing data.
- Manual catalysts config key exists, but full event scoring is not connected to a real event source yet.

Phase 5, report:

- Markdown report CLI implemented.
- Report includes top candidates, score breakdown, reasons, risks, backtest summary, and data degradation notes.

## Still Missing Or Degraded

These are not fully complete because the required real data source has not been connected:

- Revenue radar real monthly revenue calculations.
- Chip radar real foreign/investment-trust/dealer buy-sell and margin changes.
- Catalyst radar real future event calendar.
- Industry RS versus industry index is approximated with available industry/theme grouping, not a dedicated industry-index feed.
- Attention/disposition and margin/short data can be read from Shioaji, but the daily persistence job has not been added yet.
- TAIEX Shioaji adapter is implemented and unit-tested with a fake API, but no live API fetch was executed because this session did not use credentials.

## Verification Commands

Run tests:

```powershell
py -3.14 -m pytest -q tests\short_term_radar
```

Compile check:

```powershell
py -3.14 -m compileall -q short_term_radar tests\short_term_radar
```

Run scan:

```powershell
py -3.14 -m short_term_radar.cli.scan --config configs/short_term_radar/default.yaml --date 2026-04-30 --top 50 --output reports/short_term_radar/scan_2026-04-30.csv
```

Run backtest:

```powershell
py -3.14 -m short_term_radar.cli.backtest --config configs/short_term_radar/default.yaml --start 2021-05-01 --end 2026-04-30 --rebalance monthly --top-n 20 --horizon-days 126 --target-multiple 3 --output reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv
```

Generate report:

```powershell
py -3.14 -m short_term_radar.cli.report --scan-file reports/short_term_radar/scan_2026-04-30.csv --backtest-file reports/short_term_radar/backtest_2021-05-01_2026-04-30.csv --output reports/short_term_radar/report_2026-04-30.md
```

## Last Verified Results

```text
pytest: 7 passed
compileall: passed
scan: wrote 50 candidates
backtest: wrote summary and candidate details
report: wrote reports/short_term_radar/report_2026-04-30.md
```

## Best Next Steps

1. Add a read-only Shioaji daily collector for TAIEX, attention/disposition, credit enquiries, and short stock source, then persist those snapshots locally.
2. Add public monthly revenue ingestion and replace the revenue placeholder with real scoring.
3. Add institutional investor and margin/short historical ingestion.
4. Add a manual catalyst file and connect catalyst scoring.
5. Add a GitHub upload scope that excludes `discord-private-ai-bot/`, `discord-downloads/`, `shioaji.log`, secrets, and unrelated local artifacts.

## Safe GitHub Upload Scope

Recommended include list:

- `README.md`
- `SHORT_TERM_RADAR_HANDOFF.md`
- `.gitignore`
- `pytest.ini`
- `short_term_radar/`
- `configs/short_term_radar/`
- `tests/short_term_radar/`
- selected `reports/short_term_radar/*.csv`
- selected `reports/short_term_radar/*.md`

Recommended exclude list:

- `.env`
- `shioaji.log`
- `discord-private-ai-bot/`
- `discord-downloads/`
- `pytest-cache-files-*`
- `pytest_tmp_manual_check/`
- unrelated images and local-only artifacts

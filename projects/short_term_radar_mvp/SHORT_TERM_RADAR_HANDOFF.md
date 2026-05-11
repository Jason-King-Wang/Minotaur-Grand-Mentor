# Short Term Radar MVP Handoff

Last updated: 2026-05-11

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

The data-source layer requested by `codex_short_term_radar_data_collection_instruction.md` has also been added as a test-covered layer. It provides registry, config examples, normalizers, quality checks, dry-run CLIs, sample fixtures, processed-data adapters, and local existing-cache backfill for `symbol_master` plus `prices_daily`. Live public-data backfill for external official endpoints is intentionally not executed by default.

## Progress Snapshot

這段是目前接手時最重要的狀態摘要。

已做到：

- 價量型 MVP 已可跑 scan、backtest、report。
- 資料收集層骨架已建立：registry、config、fetcher interface、normalizer、storage、quality check、CLI。
- P0/P1 目標表 schema 與 primary key 已寫入程式。
- sample fixtures 與 data-source tests 已建立。
- `symbol_master` 已從本機既有 cache 轉成 processed parquet。
- `prices_daily` 已從本機既有 5 年日線 cache 轉成 processed parquet。
- `normalize --input` 已可把本機 CSV 正規化成 processed parquet 並立即做 quality check。
- processed adapters 已接進 scan pipeline，可讀 revenue/chip/surveillance/catalyst/corporate action/valuation processed tables。
- 缺資料會降級：缺 revenue 不能進 S3；處置中強制 S5 / avoid_chasing；核心資料缺太多會 cap score。
- broker adapter 維持 read-only，沒有下單、改單、刪單或帳戶查詢方法。

目前 processed coverage：

| Table | Status | Rows | Notes |
|---|---:|---:|---|
| `symbol_master.parquet` | done | 2,119 | 來自本機既有 `reference/symbol_master.csv`，quality ok |
| `prices_daily.parquet` | done | 2,210,492 | 來自本機既有 `daily_ohlcv/{TWSE,TPEX}/*.parquet`，quality ok |
| `monthly_revenue.parquet` | missing backfill | 0 | normalizer / adapter / no-future gating 已做，尚未接官方下載與五年回補 |
| `institutional_trading_daily.parquet` | missing backfill | 0 | normalizer / adapter 已做，尚未接 TWSE/TPEx 歷史來源 |
| `margin_short_daily.parquet` | missing backfill | 0 | normalizer / adapter 已做，尚未接 TWSE/TPEx/Shioaji read-only persistence |
| `surveillance_daily.parquet` | missing backfill | 0 | normalizer / adapter / 處置 gating 已做，尚未接注意/處置實際來源 |
| `corporate_actions.parquet` | missing backfill | 0 | normalizer / adapter 已做，尚未接官方來源 |
| `material_events.parquet` | missing backfill | 0 | normalizer / classifier / adapter 已做，尚未接 MOPS/data.gov.tw |
| `financial_statement_quarterly.parquet` | missing backfill | 0 | normalizer 已做，尚未接來源與 feature scoring |
| `insider_holding_monthly.parquet` | missing backfill | 0 | normalizer 已做，尚未接來源與 feature scoring |
| `valuation_daily.parquet` | missing backfill | 0 | normalizer / adapter 已做，尚未接來源 |

還差什麼：

- 實作官方來源下載器，而不只是 registry/dry-run。
- 回補 `monthly_revenue` 最近 5 年，這是下一個最高優先級。
- 回補法人、融資融券、注意/處置、重大訊息、除權息等 P0 表。
- 把真實 processed revenue/chip/catalyst/surveillance 資料跑進 scan，確認排名不再全是 degraded。
- 補完整 data coverage / missing dates / freshness 報表輸出成 CSV。
- 若要用券商 API，只能做 read-only daily persistence，不得登入、不存 credentials、不做帳戶/交易動作。

建議下一步順序：

1. 先做 `monthly_revenue` 官方來源 backfill。
2. 再做 `surveillance_daily` 注意/處置來源，因為它會直接影響 S3/S5 風控。
3. 接 `institutional_trading_daily` 與 `margin_short_daily`，補籌碼與擁擠度。
4. 接 `material_events` 與 `corporate_actions`，補催化劑與事件風控。
5. 最後補 P1：財報、董監持股、估值。

## Implemented Files

Core package:

- `short_term_radar/`
- `short_term_radar/adapters/`
- `short_term_radar/data_sources/`
- `short_term_radar/features/`
- `short_term_radar/scoring/`
- `short_term_radar/backtest/`
- `short_term_radar/cli/`
- `short_term_radar/utils/`

Config and tests:

- `configs/short_term_radar/default.yaml`
- `configs/short_term_radar/data_sources.example.yaml`
- `configs/short_term_radar/local.yaml.example`
- `tests/short_term_radar/`
- `tests/fixtures/`
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

## Data Source Layer Added

Implemented:

- P0/P1 dataset registry with official TWSE/TPEx/data.gov.tw/MOPS/TWSE E-Shop source metadata.
- Config loader with environment-variable expansion.
- Storage helpers for raw, processed, quality, and sample paths.
- Fetcher interfaces for HTTP, local CSV files, and read-only broker access.
- Normalizers for symbol master, daily prices, monthly revenue, institutional trading, margin/short, surveillance, corporate actions, material events, financials, insider holding, and valuation.
- Shared parsers for ROC dates, Taiwan month strings, comma numbers, Chinese unit numbers, percentages, null markers, symbols, markets, and bool flags.
- Quality checks for schemas, primary keys, future dates, market values, symbols, source URLs, and fetched timestamps.
- CLI modules: `collect`, `normalize`, `validate_data`, `coverage`.
- Processed-data adapters for revenue, chip, surveillance, catalyst, corporate action, and valuation feature inputs.
- Local existing-cache backfill for `symbol_master` from `reference/symbol_master.csv`.
- Local existing-cache backfill for `prices_daily` from `daily_ohlcv/{TWSE,TPEX}/*.parquet`.
- `normalize --input` can convert a local source CSV into a processed parquet table and immediately run quality checks.

Important behavior:

- Monthly revenue is gated by `announce_date <= as_of_date`; tests verify `revenue_month` alone cannot leak future data.
- Missing revenue prevents `S3 candidate_entry`.
- Active disposition forces `S5 avoid_chasing`.
- Missing revenue/chip/catalyst/surveillance adds degraded-data risk flags and can cap score/stage.
- Broker adapter and broker fetcher remain read-only and expose no order/account mutation methods.

Completed local backfill:

- `symbol_master`: 2119 rows written to `data/processed/symbol_master.parquet`.
- `prices_daily`: 2,210,492 rows written to `data/processed/prices_daily.parquet`.
- Quality validation for both tables passed with zero issues.

Registry/dry-run only or still requiring endpoint work:

- Live public-data download/backfill for external official endpoints is not executed by default.
- TWSE E-Shop sources may require subscription.
- Broker API collection requires caller-provided logged-in API object and remains disabled by default.
- Full five-year backfill for monthly revenue, institutional trading, margin/short, surveillance, corporate actions, and material events is still pending.

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

- Revenue, chip, catalyst, surveillance, corporate-action, and valuation adapters can read processed parquet/csv tables when present.
- Graceful degradation is implemented for missing data.
- Manual catalysts config key exists.
- Full external event backfill is not connected yet, so catalyst remains degraded until `material_events` is populated.

Phase 5, report:

- Markdown report CLI implemented.
- Report includes top candidates, score breakdown, reasons, risks, backtest summary, and data degradation notes.

## Still Missing Or Degraded

These are not fully complete because the required real data source has not been connected:

- Revenue radar real monthly revenue calculations are implemented for processed tables, but real backfill is still missing.
- Chip radar real foreign/investment-trust/dealer buy-sell and margin changes are implemented for processed tables, but real backfill is still missing.
- Catalyst radar reads processed material events and manual catalysts, but real event backfill is still missing.
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

Normalize a downloaded/source CSV:

```powershell
py -3.14 -m short_term_radar.cli.normalize --config configs/short_term_radar/local.yaml.example --dataset monthly_revenue --input path\to\monthly_revenue.csv --market TWSE --source twse --source-url https://data.gov.tw/dataset/18420 --as-of 2026-05-11
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
pytest: 21 passed
compileall: passed
scan: wrote 50 candidates
backtest: wrote summary and candidate details
report: wrote reports/short_term_radar/report_2026-04-30.md
data-source dry-run CLIs: passed
local symbol_master backfill: wrote 2119 rows, validation ok
local prices_daily backfill: wrote 2210492 rows, validation ok
normalize --input fixture check: wrote 2 monthly_revenue rows to data/tmp/normalize_check, validation ok
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
- `tests/fixtures/`
- `data/quality/.gitkeep`
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
- `data/raw/`
- `data/processed/`
- `data/cache/`
- `data/tmp/`

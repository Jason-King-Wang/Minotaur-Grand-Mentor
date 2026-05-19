# 2026-05-12 Full Remaining Tasks Status

Source attachment archived as:

```text
docs/codex_short_term_radar_full_remaining_tasks_2026-05-12.md
```

## Scope

- Work stayed under `projects/short_term_radar_mvp/`.
- Root `README.md` was not edited.
- `configs/short_term_radar/local.yaml` was not created or committed.
- No raw data, processed data, local config, secrets, broker logs, or Discord runtime files were added.

## Implemented This Pass

- Processed storage now falls back to CSV when pandas/parquet is unavailable, and `read_processed_rows()` reads that CSV fallback with typed values.
- Added `official_open_data.py` for official endpoint dry-runs and conservative collector behavior.
- Added official dry-run support in `collect` for:
  - `institutional_trading`
  - `margin_short`
  - `material_events`
  - `corporate_actions`
  - `valuation`
  - `symbol_master`
- Empty official fetches degrade cleanly and skip processed writes.
- `institutional_trading` range collect now errors explicitly: use `--date` for single-day smoke.
- Added tests for official dry-run routing and common JSON payload extraction.

## Current Source Status

| Dataset | Status |
|---|---|
| monthly_revenue | Parser, dry-run, normalize, validate, upsert path exist. Live small-smoke not run in this pass. |
| institutional_trading | Official dry-run and collector skeleton exist. Full live field mapping still needs real payload verification. |
| margin_short | Official dry-run and collector skeleton exist. Full live field mapping still needs real payload verification. |
| surveillance | TPEx/TWSE degraded dry-run exists. Direct TPEx download URLs and TWSE historical free source remain unresolved. |
| material_events | Official dry-run and collector skeleton exist. Full live field mapping still needs real payload verification. |
| corporate_actions | Official dry-run and collector skeleton exist. Full live field mapping still needs real payload verification. |
| trading_calendar | Still pending as an official source. Coverage uses prices_daily trading dates, then weekday fallback. |
| valuation/symbol_master | Official dry-run and collector skeleton exist. Full live field mapping still needs real payload verification. |

## Validation

- `py -3.11 -m pytest -q tests\short_term_radar --tb=short --basetemp pytest_tmp_py311_official`: `50 passed`
- `compileall` with Python 3.11: passed
- N2 dry-runs: passed for monthly revenue, institutional trading TWSE/TPEX, margin/short, surveillance, material events, corporate actions, and coverage.
- Scan slot verification wrote `reports/short_term_radar/scan_2026-04-30.csv`.
- Scan first row mode: `simple_price_volume_mode`
- Scan first row slot coverage: `robot_slot_coverage_ratio = 0.25`, `score_data_coverage_ratio = 0.4`
- `git diff --check -- projects/short_term_radar_mvp`: passed

## Still Missing

- Live official fetch verification for the new skeleton endpoints.
- Full field mapping for real TWSE/TPEx institutional, margin/short, material event, corporate action, valuation, and symbol master payloads.
- Official trading calendar parser/source.
- TPEx surveillance direct CSV/API URLs.
- TWSE historical surveillance free endpoint.
- Full five-year official backfill. Generated raw/processed files must stay local-only.

## Risks

- Official endpoints may change payload shape or require TLS/certificate fixes.
- Some endpoints are candidate URLs and need live confirmation before marking slots `installed`.
- Shioaji remains read-only/current-data only and must not be used for account or order operations.

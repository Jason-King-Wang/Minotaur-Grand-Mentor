# Short Term Radar MVP - Public Showcase Notes

## One-Line Summary

A Taiwan equity candidate radar that combines feature adapters, stage gating, scoring, backtesting, baseline comparison, and Markdown reporting.

## Engineering Highlights

- Modular data-source layer with fetchers, normalizers, registry, storage helpers, and quality checks.
- Graceful degradation when a data slot is missing, with explicit coverage ratios and slot-status output.
- Stage gating rules for candidate entry, including missing-revenue handling and disposition-risk handling.
- Backtest pipeline with 126-trading-day forward labels, top-N selection, 3x/5x target checks, and baseline strategies.
- Report generation that separates actionable candidate sections from degraded-data warnings.
- Tests covering scoring, price-volume features, no-future-leakage rules, broker read-only behavior, normalizers, and storage.

## Security / Public Scope

This public copy excludes local raw data, processed parquet files, broker runtime files, private configs, logs, temp folders, and caches. Config files in this folder are examples or safe defaults only.

## Good Interview Files

- `short_term_radar/pipeline.py`
- `short_term_radar/scoring/short_term_score.py`
- `short_term_radar/scoring/stage_classifier.py`
- `short_term_radar/data_sources/`
- `short_term_radar/backtest/`
- `tests/short_term_radar/`
- `reports/short_term_radar/report_2026-04-30.md`

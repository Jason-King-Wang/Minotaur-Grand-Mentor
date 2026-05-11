from __future__ import annotations

from pathlib import Path
from typing import Any

from short_term_radar.adapters.daily_price_adapter import DailyPriceAdapter
from short_term_radar.backtest.labeler import forward_label
from short_term_radar.backtest.metrics import summarize_backtest
from short_term_radar.pipeline import scan_candidates
from short_term_radar.utils.calendar import monthly_rebalance_dates
from short_term_radar.utils.io import write_csv


DETAIL_FIELDS = [
    "period_date",
    "rank",
    "symbol",
    "name",
    "score_total",
    "stage",
    "entry_zone",
    "forward_max_return",
    "forward_close_return",
    "forward_min_return_from_entry",
    "forward_path_max_drawdown",
    "forward_max_drawdown",
    "hit_3x",
    "hit_5x",
]


SUMMARY_FIELDS = [
    "period_start",
    "period_end",
    "top_n",
    "horizon_days",
    "target_multiple",
    "hit_rate_3x",
    "hit_rate_5x",
    "precision_at_n",
    "avg_forward_max_return",
    "median_forward_max_return",
    "max_forward_max_return",
    "avg_forward_close_return",
    "median_forward_close_return",
    "avg_forward_path_max_drawdown",
    "median_forward_path_max_drawdown",
    "profit_factor_like",
    "num_candidates",
    "num_hits",
]


def run_backtest(config: dict[str, Any], start: str, end: str, top_n: int, horizon_days: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    adapter = DailyPriceAdapter(config)
    by_symbol = adapter.load()
    trade_dates = adapter.available_trade_dates(by_symbol)
    rebalance_dates = monthly_rebalance_dates(trade_dates, start, end)
    detail_rows: list[dict[str, Any]] = []

    for period_date in rebalance_dates:
        candidates = scan_candidates(config, period_date, top_n, by_symbol)
        for candidate in candidates:
            label = forward_label(by_symbol.get(candidate["symbol"], []), candidate["trade_date"], horizon_days)
            detail_rows.append(
                {
                    "period_date": period_date,
                    "rank": candidate["rank"],
                    "symbol": candidate["symbol"],
                    "name": candidate.get("name"),
                    "score_total": candidate["score_total"],
                    "stage": candidate["stage"],
                    "entry_zone": candidate["entry_zone"],
                    **label.to_row(),
                }
            )

    target_multiple = float((config.get("backtest", {}).get("target_multiples") or [3])[0])
    summary = summarize_backtest(detail_rows, start, end, top_n, horizon_days, target_multiple)
    return summary, detail_rows


def write_backtest_outputs(
    summary_path: str | Path,
    summary: dict[str, Any],
    detail_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]] | None = None,
    baseline_detail_rows: list[dict[str, Any]] | None = None,
) -> Path | dict[str, Path]:
    summary_path = Path(summary_path)
    write_csv(summary_path, [summary], SUMMARY_FIELDS)
    detail_path = summary_path.with_name(f"{summary_path.stem}_candidates{summary_path.suffix}")
    write_csv(detail_path, detail_rows, DETAIL_FIELDS)
    if baseline_rows is None and baseline_detail_rows is None:
        return detail_path

    suffix = summary_path.suffix
    period_part = summary_path.stem.removeprefix("backtest_")
    baseline_path = summary_path.with_name(f"baseline_comparison_{period_part}{suffix}")
    baseline_details_path = summary_path.with_name(f"baseline_details_{period_part}{suffix}")
    baseline_fields = sorted({key for row in (baseline_rows or []) for key in row})
    baseline_detail_fields = sorted({key for row in (baseline_detail_rows or []) for key in row})
    write_csv(baseline_path, baseline_rows or [], baseline_fields)
    write_csv(baseline_details_path, baseline_detail_rows or [], baseline_detail_fields)
    return {
        "summary": summary_path,
        "details": detail_path,
        "baseline": baseline_path,
        "baseline_details": baseline_details_path,
    }

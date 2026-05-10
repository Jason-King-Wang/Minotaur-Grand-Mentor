from __future__ import annotations

from pathlib import Path
from typing import Any

from short_term_radar.adapters.daily_price_adapter import DailyPriceAdapter
from short_term_radar.backtest.baselines import BASELINE_STRATEGIES, select_baseline_candidates
from short_term_radar.backtest.labeler import forward_label
from short_term_radar.backtest.metrics import summarize_backtest
from short_term_radar.features.price_volume import compute_price_volume_features
from short_term_radar.pipeline import scan_candidates
from short_term_radar.utils.calendar import monthly_rebalance_dates
from short_term_radar.utils.io import write_csv


DETAIL_FIELDS = [
    "strategy_name",
    "trial",
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
    "hit_2x",
    "hit_3x",
    "hit_5x",
    "time_to_2x_days",
    "time_to_3x_days",
    "time_to_5x_days",
]


SUMMARY_FIELDS = [
    "period_start",
    "period_end",
    "strategy_name",
    "top_n",
    "horizon_days",
    "target_multiple",
    "num_candidates",
    "num_hits_2x",
    "num_hits_3x",
    "num_hits_5x",
    "hit_rate_2x",
    "hit_rate_3x",
    "hit_rate_5x",
    "precision_at_n",
    "avg_forward_max_return",
    "median_forward_max_return",
    "max_forward_max_return",
    "avg_forward_close_return",
    "median_forward_close_return",
    "avg_forward_min_return_from_entry",
    "median_forward_min_return_from_entry",
    "avg_forward_path_max_drawdown",
    "median_forward_path_max_drawdown",
    "profit_factor_like",
]


def _target_multiple(config: dict[str, Any]) -> float:
    return float((config.get("backtest", {}).get("target_multiples") or [3])[0])


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
                    "strategy_name": "radar_top_n",
                    "trial": None,
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

    target_multiple = _target_multiple(config)
    summary = summarize_backtest(detail_rows, start, end, top_n, horizon_days, target_multiple, "radar_top_n")
    return summary, detail_rows


def run_baseline_backtests(
    config: dict[str, Any],
    start: str,
    end: str,
    top_n: int,
    horizon_days: int,
    random_trials: int = 30,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    adapter = DailyPriceAdapter(config)
    by_symbol = adapter.load()
    trade_dates = adapter.available_trade_dates(by_symbol)
    rebalance_dates = monthly_rebalance_dates(trade_dates, start, end)
    target_multiple = _target_multiple(config)
    summary_rows: list[dict[str, Any]] = []
    all_detail_rows: list[dict[str, Any]] = []
    features_by_date = {
        period_date: compute_price_volume_features(by_symbol, period_date, config)
        for period_date in rebalance_dates
    }

    for strategy_name in BASELINE_STRATEGIES:
        strategy_details: list[dict[str, Any]] = []
        trials = range(random_trials) if strategy_name == "random_top_n" else range(1)
        for trial in trials:
            for period_date in rebalance_dates:
                features_by_symbol = features_by_date[period_date]
                selected = select_baseline_candidates(strategy_name, features_by_symbol, top_n, seed, trial)
                for rank, features in enumerate(selected, 1):
                    label = forward_label(by_symbol.get(features["symbol"], []), features["trade_date"], horizon_days)
                    row = {
                        "strategy_name": strategy_name,
                        "trial": trial if strategy_name == "random_top_n" else None,
                        "period_date": period_date,
                        "rank": rank,
                        "symbol": features["symbol"],
                        "name": features.get("name"),
                        "score_total": None,
                        "stage": None,
                        "entry_zone": None,
                        **label.to_row(),
                    }
                    strategy_details.append(row)
                    all_detail_rows.append(row)
        summary_rows.append(
            summarize_backtest(strategy_details, start, end, top_n, horizon_days, target_multiple, strategy_name)
        )
    return summary_rows, all_detail_rows


def write_backtest_outputs(
    summary_path: str | Path,
    summary: dict[str, Any],
    detail_rows: list[dict[str, Any]],
    baseline_summaries: list[dict[str, Any]] | None = None,
    baseline_details: list[dict[str, Any]] | None = None,
) -> dict[str, Path]:
    summary_path = Path(summary_path)
    write_csv(summary_path, [summary], SUMMARY_FIELDS)
    detail_path = summary_path.with_name(f"{summary_path.stem}_candidates{summary_path.suffix}")
    write_csv(detail_path, detail_rows, DETAIL_FIELDS)
    paths = {"summary": summary_path, "details": detail_path}
    if baseline_summaries is not None:
        baseline_path = summary_path.with_name(summary_path.name.replace("backtest_", "baseline_comparison_"))
        write_csv(baseline_path, baseline_summaries, SUMMARY_FIELDS)
        paths["baseline"] = baseline_path
    if baseline_details is not None:
        baseline_detail_path = summary_path.with_name(summary_path.name.replace("backtest_", "baseline_details_"))
        write_csv(baseline_detail_path, baseline_details, DETAIL_FIELDS)
        paths["baseline_details"] = baseline_detail_path
    return paths

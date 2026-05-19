from __future__ import annotations

import random
from typing import Any

from short_term_radar.adapters.daily_price_adapter import DailyPriceAdapter
from short_term_radar.backtest.labeler import forward_label
from short_term_radar.backtest.metrics import summarize_backtest
from short_term_radar.pipeline import scan_candidates
from short_term_radar.utils.calendar import monthly_rebalance_dates


BASELINE_STRATEGIES = [
    "radar_model",
    "random_top_n",
    "breakout_120d_only",
    "volume_expansion_only",
    "ma_alignment_only",
]


def select_baseline_candidates(
    strategy_name: str,
    candidates: list[dict[str, Any]],
    top_n: int,
    random_seed: int = 42,
    period_date: str | None = None,
) -> list[dict[str, Any]]:
    if strategy_name == "radar_model":
        return sorted(candidates, key=lambda row: float(row.get("score_total") or 0), reverse=True)[:top_n]

    if strategy_name == "random_top_n":
        pool = sorted(candidates, key=lambda row: str(row.get("symbol") or ""))
        rng = random.Random(f"{random_seed}:{period_date or ''}")
        rng.shuffle(pool)
        return pool[:top_n]

    if strategy_name == "breakout_120d_only":
        rows = [
            row
            for row in candidates
            if _truthy(row.get("breakout_120d_flag"))
        ]
        return sorted(rows, key=lambda row: (_float(row.get("volume_expansion_ratio")), _float(row.get("rs_20d"))), reverse=True)[:top_n]

    if strategy_name == "volume_expansion_only":
        rows = [
            row
            for row in candidates
            if 1.5 <= _float(row.get("volume_expansion_ratio")) <= 3.5
        ]
        return sorted(rows, key=lambda row: _float(row.get("volume_z_20")), reverse=True)[:top_n]

    if strategy_name == "ma_alignment_only":
        rows = [row for row in candidates if _truthy(row.get("ma_alignment_bull_flag"))]
        return sorted(rows, key=lambda row: _float(row.get("rs_20d")), reverse=True)[:top_n]

    raise KeyError(f"Unknown baseline strategy: {strategy_name}")


def run_baseline_comparison(
    config: dict[str, Any],
    start: str,
    end: str,
    top_n: int,
    horizon_days: int,
    random_seed: int = 42,
    strategies: list[str] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    adapter = DailyPriceAdapter(config)
    by_symbol = adapter.load()
    trade_dates = adapter.available_trade_dates(by_symbol)
    rebalance_dates = monthly_rebalance_dates(trade_dates, start, end)
    target_multiple = float((config.get("backtest", {}).get("target_multiples") or [3])[0])
    strategies = strategies or BASELINE_STRATEGIES

    detail_rows: list[dict[str, Any]] = []
    for period_date in rebalance_dates:
        universe = scan_candidates(config, period_date, None, by_symbol)
        for strategy_name in strategies:
            selected = select_baseline_candidates(strategy_name, universe, top_n, random_seed, period_date)
            for rank, candidate in enumerate(selected, 1):
                label = forward_label(by_symbol.get(candidate["symbol"], []), candidate["trade_date"], horizon_days)
                detail_rows.append(
                    {
                        "strategy_name": strategy_name,
                        "period_date": period_date,
                        "rank": rank,
                        "symbol": candidate["symbol"],
                        "name": candidate.get("name"),
                        "score_total": candidate.get("score_total"),
                        "stage": candidate.get("stage"),
                        "entry_zone": candidate.get("entry_zone"),
                        **label.to_row(),
                    }
                )

    comparison_rows: list[dict[str, Any]] = []
    for strategy_name in strategies:
        strategy_rows = [row for row in detail_rows if row["strategy_name"] == strategy_name]
        summary = summarize_backtest(strategy_rows, start, end, top_n, horizon_days, target_multiple)
        comparison_rows.append({"strategy_name": strategy_name, **summary})
    return comparison_rows, detail_rows


def _float(value: Any) -> float:
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}

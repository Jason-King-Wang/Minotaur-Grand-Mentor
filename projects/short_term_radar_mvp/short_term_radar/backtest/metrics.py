from __future__ import annotations

from statistics import median
from typing import Any


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def summarize_backtest(
    candidate_rows: list[dict[str, Any]],
    period_start: str,
    period_end: str,
    top_n: int,
    horizon_days: int,
    target_multiple: float,
) -> dict[str, Any]:
    num_candidates = len(candidate_rows)
    max_returns = [
        float(row["forward_max_return"])
        for row in candidate_rows
        if row.get("forward_max_return") is not None
    ]
    close_returns = [
        float(row["forward_close_return"])
        for row in candidate_rows
        if row.get("forward_close_return") is not None
    ]
    drawdowns = [
        float(row["forward_path_max_drawdown"] if row.get("forward_path_max_drawdown") is not None else row["forward_max_drawdown"])
        for row in candidate_rows
        if row.get("forward_path_max_drawdown") is not None or row.get("forward_max_drawdown") is not None
    ]
    hit_3x = sum(1 for row in candidate_rows if row.get("hit_3x"))
    hit_5x = sum(1 for row in candidate_rows if row.get("hit_5x"))
    num_hits = sum(1 for value in max_returns if value >= target_multiple - 1)
    gains = [value for value in close_returns if value > 0]
    losses = [-value for value in close_returns if value < 0]

    return {
        "period_start": period_start,
        "period_end": period_end,
        "top_n": top_n,
        "horizon_days": horizon_days,
        "target_multiple": target_multiple,
        "hit_rate_3x": hit_3x / num_candidates if num_candidates else 0.0,
        "hit_rate_5x": hit_5x / num_candidates if num_candidates else 0.0,
        "precision_at_n": num_hits / num_candidates if num_candidates else 0.0,
        "avg_forward_max_return": _avg(max_returns),
        "median_forward_max_return": median(max_returns) if max_returns else None,
        "max_forward_max_return": max(max_returns) if max_returns else None,
        "avg_forward_close_return": _avg(close_returns),
        "median_forward_close_return": median(close_returns) if close_returns else None,
        "avg_forward_path_max_drawdown": _avg(drawdowns),
        "median_forward_path_max_drawdown": median(drawdowns) if drawdowns else None,
        "profit_factor_like": (sum(gains) / sum(losses)) if losses else (sum(gains) if gains else 0.0),
        "num_candidates": num_candidates,
        "num_hits": num_hits,
    }

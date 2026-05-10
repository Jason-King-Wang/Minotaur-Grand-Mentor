from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def _sum_revenue(rows: list[dict[str, Any]]) -> float | None:
    values = [row.get("revenue") for row in rows if row.get("revenue") is not None]
    return sum(values) if len(values) == len(rows) and values else None


def _window_yoy(rows: list[dict[str, Any]], months: int) -> float | None:
    if len(rows) < months + 12:
        return None
    current = _sum_revenue(rows[-months:])
    previous = _sum_revenue(rows[-months - 12 : -12])
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1.0


def compute_revenue_features(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"rev_available_flag": False}
    rows = sorted(rows, key=lambda row: row["revenue_month"])
    latest = rows[-1]
    latest_yoy = latest.get("revenue_yoy")
    latest_mom = latest.get("revenue_mom")
    rev_3m_yoy = _window_yoy(rows, 3)
    rev_6m_yoy = _window_yoy(rows, 6)
    rev_12m_yoy = _window_yoy(rows, 12)
    previous_yoy = rows[-2].get("revenue_yoy") if len(rows) >= 2 else None
    revenue_values = [row.get("revenue") for row in rows if row.get("revenue") is not None]
    latest_revenue = latest.get("revenue")

    consecutive_growth = 0
    for row in reversed(rows):
        yoy = row.get("revenue_yoy")
        if yoy is None or yoy <= 0:
            break
        consecutive_growth += 1

    def is_new_high(window: int | None) -> bool:
        if latest_revenue is None or not revenue_values:
            return False
        history = revenue_values[-window:] if window else revenue_values
        return bool(history and latest_revenue >= max(history))

    acceleration = (
        rev_3m_yoy - rev_12m_yoy
        if rev_3m_yoy is not None and rev_12m_yoy is not None
        else None
    )
    return {
        "rev_1m_yoy": latest_yoy,
        "rev_1m_mom": latest_mom,
        "rev_3m_yoy": rev_3m_yoy,
        "rev_6m_yoy": rev_6m_yoy,
        "rev_12m_yoy": rev_12m_yoy,
        "rev_3m_vs_12m_acceleration": acceleration,
        "rev_turn_positive_flag": bool(latest_yoy is not None and latest_yoy > 0 and (previous_yoy or 0) <= 0),
        "rev_new_high_12m_flag": is_new_high(12),
        "rev_new_high_24m_flag": is_new_high(24),
        "rev_new_high_all_time_flag": is_new_high(None),
        "rev_consecutive_growth_months": consecutive_growth,
        "rev_available_flag": True,
        "latest_revenue_month": latest.get("revenue_month"),
        "latest_revenue_release_date": latest.get("release_date"),
    }


def score_revenue(features: dict[str, Any] | None = None) -> float | None:
    if not features or not features.get("rev_available_flag"):
        return None
    score = 0.0
    rev_3m_yoy = features.get("rev_3m_yoy")
    rev_6m_yoy = features.get("rev_6m_yoy")
    acceleration = features.get("rev_3m_vs_12m_acceleration")
    rev_1m_yoy = features.get("rev_1m_yoy")

    if rev_3m_yoy is not None and rev_3m_yoy > 0.30:
        score += 20
    if rev_3m_yoy is not None and rev_3m_yoy > 0.50:
        score += 10
    if rev_6m_yoy is not None and rev_6m_yoy > 0.20:
        score += 10
    if acceleration is not None and acceleration > 0.15:
        score += 20
    if features.get("rev_turn_positive_flag"):
        score += 15
    if features.get("rev_new_high_12m_flag"):
        score += 10
    if features.get("rev_new_high_24m_flag"):
        score += 15
    if features.get("rev_new_high_all_time_flag"):
        score += 20
    growth_months = int(features.get("rev_consecutive_growth_months") or 0)
    if growth_months >= 3:
        score += 15
    elif growth_months >= 2:
        score += 10
    if rev_1m_yoy is not None and rev_1m_yoy < -0.20:
        score -= 20
    if rev_3m_yoy is not None and rev_3m_yoy < 0:
        score -= 15
    return clip(score)

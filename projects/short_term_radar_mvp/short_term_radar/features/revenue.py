from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def compute_revenue_features(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    rows = sorted(rows, key=lambda row: str(row.get("revenue_month") or row.get("month") or ""))
    revenues = [_to_float(row.get("revenue") or row.get("revenue_current")) for row in rows]
    yoy_values = [_to_float(row.get("revenue_yoy") or row.get("revenue_yoy_pct")) for row in rows]
    last_3 = [value for value in yoy_values[-3:] if value is not None]
    last_6 = [value for value in yoy_values[-6:] if value is not None]
    latest = rows[-1]
    latest_revenue = revenues[-1] if revenues else None
    valid_revenues = [value for value in revenues[-12:] if value is not None]
    return {
        "rev_3m_yoy": sum(last_3) / len(last_3) if last_3 else None,
        "rev_6m_yoy": sum(last_6) / len(last_6) if last_6 else None,
        "rev_new_high_12m_flag": bool(latest_revenue is not None and valid_revenues and latest_revenue >= max(valid_revenues)),
        "rev_yoy_1m": _normalize_ratio(yoy_values[-1]) if yoy_values else None,
        "rev_mom_1m": _normalize_ratio(_to_float(latest.get("revenue_mom") or latest.get("revenue_mom_pct"))),
        "latest_revenue_month": latest.get("revenue_month"),
        "latest_revenue_announce_date": latest.get("release_date") or latest.get("announce_date"),
    }


def score_revenue(features: dict[str, Any] | None = None, *_args, **_kwargs) -> float | None:
    if not features:
        return None
    score = 0.0
    yoy = _pct_value(features.get("rev_yoy_1m"))
    yoy_3m = _pct_value(features.get("rev_yoy_3m") if features.get("rev_yoy_3m") is not None else features.get("rev_3m_yoy"))
    yoy_6m = _pct_value(features.get("rev_6m_yoy"))
    acceleration = features.get("rev_acceleration_3m_vs_12m")
    if acceleration is None and yoy_3m is not None and yoy_6m is not None:
        acceleration = yoy_3m - yoy_6m
    streak = features.get("rev_positive_streak_months") or 0

    if yoy is not None and yoy > 30:
        score += 25
    elif yoy is not None and yoy > 10:
        score += 15
    if yoy_3m is not None and yoy_3m > 20:
        score += 15
    if acceleration is not None and acceleration > 10:
        score += 15
    if features.get("rev_turn_positive_flag"):
        score += 15
    if features.get("rev_new_high_flag") or features.get("rev_same_month_high_flag") or features.get("rev_new_high_12m_flag"):
        score += 15
    if streak >= 3:
        score += 10
    return clip(score)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize_ratio(value: float | None) -> float | None:
    if value is None:
        return None
    return value * 100 if -1 <= value <= 1 else value


def _pct_value(value: Any) -> float | None:
    number = _to_float(value)
    return _normalize_ratio(number)

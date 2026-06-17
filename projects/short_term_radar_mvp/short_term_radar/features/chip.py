from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def compute_chip_features(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}
    rows = sorted(rows, key=lambda row: str(row.get("trade_date") or ""))
    latest = rows[-1]
    return {
        "foreign_buy_5d": _sum_last(rows, "foreign_buy", 5),
        "investment_trust_buy_5d": _sum_last(rows, "investment_trust_buy", 5),
        "dealer_buy_5d": _sum_last(rows, "dealer_buy", 5),
        "inst_buy_total_5d": _sum_last(rows, "inst_buy_total", 5),
        "margin_balance_change_20d": _delta(rows, "margin_balance", 20),
        "short_balance_change_20d": _delta(rows, "short_balance", 20),
        "borrow_balance_change_20d": _delta(rows, "borrow_balance", 20),
        "shares_outstanding": _to_float(latest.get("shares_outstanding")),
    }


def score_chip(features: dict[str, Any] | None = None, *_args, **_kwargs) -> float | None:
    if not features:
        return None
    score = 0.0
    if (features.get("foreign_buy_5d") or 0) > 0:
        score += 20
    if (features.get("investment_trust_buy_5d") or 0) > 0:
        score += 20
    if (features.get("inst_buy_total_5d") or 0) > 0:
        score += 20
    if (features.get("margin_balance_change_20d") or 0) < 0:
        score += 10
    if (features.get("investment_trust_net_5d") or 0) > 0:
        score += 20
    if (features.get("investment_trust_net_20d") or 0) > 0:
        score += 20
    if (features.get("foreign_net_5d") or 0) > 0 and (features.get("foreign_net_20d") or 0) >= 0:
        score += 20
    if (features.get("total_institutional_net_5d") or 0) > 0:
        score += 15
    if features.get("short_squeeze_candidate_flag"):
        score += 10
    if features.get("financing_overcrowded_flag"):
        score -= 25
    if (features.get("total_institutional_net_20d") or 0) < 0:
        score -= 20
    return clip(score)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_last(rows: list[dict[str, Any]], column: str, count: int) -> float | None:
    values = [_to_float(row.get(column)) for row in rows[-count:]]
    values = [value for value in values if value is not None]
    return sum(values) if values else None


def _delta(rows: list[dict[str, Any]], column: str, count: int) -> float | None:
    if len(rows) <= count:
        return None
    latest = _to_float(rows[-1].get(column))
    previous = _to_float(rows[-count - 1].get(column))
    return latest - previous if latest is not None and previous is not None else None

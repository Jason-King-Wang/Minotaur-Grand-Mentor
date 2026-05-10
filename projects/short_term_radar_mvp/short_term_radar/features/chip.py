from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def _sum(rows: list[dict[str, Any]], key: str) -> float:
    return sum(float(row.get(key) or 0.0) for row in rows)


def _change(rows: list[dict[str, Any]], key: str, window: int) -> float | None:
    if len(rows) < window + 1:
        return None
    latest = rows[-1].get(key)
    previous = rows[-window - 1].get(key)
    if latest is None or previous is None:
        return None
    return float(latest) - float(previous)


def compute_chip_features(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"chip_available_flag": False}
    rows = sorted(rows, key=lambda row: row["trade_date"])
    latest = rows[-1]
    last_5 = rows[-5:]
    last_20 = rows[-20:]
    shares = latest.get("shares_outstanding")
    inst_20 = _sum(last_20, "inst_buy_total")
    margin_change_20 = _change(rows, "margin_balance", 20)
    margin_balance = latest.get("margin_balance")

    return {
        "foreign_buy_5d": _sum(last_5, "foreign_buy"),
        "foreign_buy_20d": _sum(last_20, "foreign_buy"),
        "investment_trust_buy_5d": _sum(last_5, "investment_trust_buy"),
        "investment_trust_buy_20d": _sum(last_20, "investment_trust_buy"),
        "dealer_buy_5d": _sum(last_5, "dealer_buy"),
        "dealer_buy_20d": _sum(last_20, "dealer_buy"),
        "inst_buy_total_5d": _sum(last_5, "inst_buy_total"),
        "inst_buy_total_20d": inst_20,
        "inst_buy_intensity_20d": inst_20 / shares if shares else None,
        "margin_change_5d": _change(rows, "margin_balance", 5),
        "margin_change_20d": margin_change_20,
        "margin_surge_flag": bool(margin_change_20 is not None and margin_balance and margin_change_20 / margin_balance > 0.15),
        "short_balance_change_20d": _change(rows, "short_balance", 20),
        "borrow_balance_change_20d": _change(rows, "borrow_balance", 20),
        "margin_balance_ratio": margin_balance / shares if shares and margin_balance is not None else None,
        "chip_available_flag": True,
        "chip_data_quality_flags": [] if shares else ["shares_outstanding_missing"],
    }


def score_chip(features: dict[str, Any] | None = None) -> float | None:
    if not features or not features.get("chip_available_flag"):
        return None
    score = 40.0
    if (features.get("investment_trust_buy_5d") or 0) > 0 and (features.get("investment_trust_buy_20d") or 0) > 0:
        score += 20
    if (features.get("foreign_buy_5d") or 0) > 0 and (features.get("foreign_buy_20d") or 0) > 0:
        score += 15
    intensity = features.get("inst_buy_intensity_20d")
    if intensity is not None and intensity > 0.01:
        score += 15
    if (features.get("inst_buy_total_20d") or 0) > 0:
        score += 15
    margin_change = features.get("margin_change_20d")
    if margin_change is not None:
        if margin_change < 0:
            score += 5
        elif features.get("margin_surge_flag"):
            score -= 25
    short_change = (features.get("short_balance_change_20d") or 0) + (features.get("borrow_balance_change_20d") or 0)
    if short_change < 0:
        score += 10
    elif short_change > 0:
        score -= 10
    return clip(score)

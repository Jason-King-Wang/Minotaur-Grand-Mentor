from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def compute_catalyst_features(
    rows: list[dict[str, Any]],
    as_of_date: str,
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not rows:
        return {}
    from datetime import date

    cfg = (config or {}).get("catalyst") or {}
    lookahead_days = int(cfg.get("lookahead_days", 126))
    near_term_days = int(cfg.get("near_term_days", 45))
    as_of = date.fromisoformat(as_of_date)
    near_count = 0
    positive_count = 0
    confirmed_count = 0
    for row in rows:
        event_date = row.get("event_date")
        if not event_date:
            continue
        parsed = date.fromisoformat(str(event_date))
        days = (parsed - as_of).days
        if 0 <= days <= lookahead_days:
            if str(row.get("impact")).lower() == "positive":
                positive_count += 1
            if str(row.get("status")).lower() == "confirmed":
                confirmed_count += 1
            if days <= near_term_days:
                near_count += 1
    return {
        "near_term_catalyst_count": near_count,
        "positive_catalyst_count": positive_count,
        "confirmed_catalyst_count": confirmed_count,
    }


def score_catalyst(features: dict[str, Any] | None = None, *_args, **_kwargs) -> float | None:
    if not features:
        return None
    score = 0.0
    score += min(30, int(features.get("near_term_catalyst_count") or 0) * 20)
    score += min(30, int(features.get("positive_catalyst_count") or 0) * 20)
    score += min(20, int(features.get("confirmed_catalyst_count") or 0) * 10)
    score += min(30, int(features.get("positive_catalyst_count_30d") or 0) * 15)
    if features.get("investor_conference_flag"):
        score += 10
    if features.get("major_order_flag"):
        score += 20
    if features.get("new_product_flag"):
        score += 15
    if features.get("capacity_expansion_flag") or features.get("customer_supply_chain_flag"):
        score += 15
    score -= min(35, int(features.get("risk_event_count_30d") or 0) * 15)
    if features.get("capital_raise_risk_flag"):
        score -= 15
    if features.get("lawsuit_or_penalty_flag"):
        score -= 20
    if features.get("manual_catalyst"):
        score += 10
    return clip(score)

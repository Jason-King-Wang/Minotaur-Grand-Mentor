from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from short_term_radar.utils.math_utils import clip


def compute_catalyst_features(rows: list[dict[str, Any]], as_of_date: str, config: dict[str, Any]) -> dict[str, Any]:
    if not rows:
        return {"catalyst_available_flag": False}
    cfg = config.get("catalyst", {})
    lookahead_days = int(cfg.get("lookahead_days", 126))
    near_term_days = int(cfg.get("near_term_days", 45))
    start = date.fromisoformat(as_of_date)
    end = start + timedelta(days=lookahead_days)
    near_end = start + timedelta(days=near_term_days)
    future = []
    for row in rows:
        if (
            row.get("event_date")
            and as_of_date <= row["event_date"] <= end.isoformat()
            and row.get("status") != "cancelled"
        ):
            future.append({**row, "_days": (date.fromisoformat(row["event_date"]) - start).days})
    future.sort(key=lambda row: row["event_date"])
    next_event = future[0] if future else {}
    near_term = [row for row in future if row["event_date"] <= near_end.isoformat()]
    confirmed = [row for row in future if row.get("status") == "confirmed"]
    positive = [row for row in future if row.get("impact") == "positive"]
    negative = [row for row in future if row.get("impact") == "negative"]
    return {
        "next_catalyst_date": next_event.get("event_date"),
        "next_catalyst_days": (date.fromisoformat(next_event["event_date"]) - start).days if next_event.get("event_date") else None,
        "next_catalyst_category": next_event.get("category"),
        "next_catalyst_confidence": next_event.get("confidence"),
        "near_term_catalyst_count": len(near_term),
        "confirmed_catalyst_count": len(confirmed),
        "positive_catalyst_count": len(positive),
        "negative_catalyst_count": len(negative),
        "catalyst_available_flag": bool(future),
        "catalyst_events": future,
    }


def score_catalyst(features: dict[str, Any] | None = None) -> float | None:
    if not features or not features.get("catalyst_available_flag"):
        return None
    score = 0.0
    for event in features.get("catalyst_events") or []:
        impact = event.get("impact")
        status = event.get("status")
        category = event.get("category")
        event_days = event.get("_days")
        if impact == "positive" and status == "confirmed" and event_days is not None and event_days <= 45:
            score += 40
        elif impact == "positive" and status == "confirmed":
            score += 25
        elif impact == "positive" and status == "expected":
            score += 15
        if event_days is not None and event_days <= 45:
            score += 10
        if category in {"monthly_revenue", "earnings"} and event_days is not None and event_days <= 14:
            score += 10
        if impact == "negative":
            score -= 30
        if status == "cancelled":
            score -= 20
    return clip(score)

from __future__ import annotations

from datetime import date
from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter


class SurveillanceAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load_features(self, as_of_date: str) -> dict[str, dict[str, Any]]:
        rows = self.processed.load_table("surveillance_daily")
        result: dict[str, dict[str, Any]] = {}
        as_of = date.fromisoformat(as_of_date)
        for row in rows:
            trade_date = row.get("trade_date")
            if not trade_date or str(trade_date) > as_of_date:
                continue
            symbol = str(row.get("symbol") or "")
            if not symbol:
                continue
            feature = result.setdefault(
                symbol,
                {
                    "attention_flag": False,
                    "attention_reason": None,
                    "disposition_flag": False,
                    "disposition_active_flag": False,
                    "disposition_days_left": None,
                    "attention_count_recent": 0,
                    "surveillance_risk_score": 0.0,
                },
            )
            if _truthy(row.get("attention_flag")):
                feature["attention_flag"] = True
                feature["attention_reason"] = row.get("attention_reason")
                feature["attention_count_recent"] = int(feature.get("attention_count_recent") or 0) + 1
                feature["surveillance_risk_score"] = max(float(feature["surveillance_risk_score"]), 10.0)
            if _truthy(row.get("disposition_flag")):
                feature["disposition_flag"] = True
                start = str(row.get("disposition_start") or trade_date)
                end = str(row.get("disposition_end") or start)
                if start <= as_of_date <= end:
                    feature["disposition_active_flag"] = True
                    try:
                        feature["disposition_days_left"] = max(0, (date.fromisoformat(end) - as_of).days)
                    except ValueError:
                        feature["disposition_days_left"] = None
                    feature["surveillance_risk_score"] = max(float(feature["surveillance_risk_score"]), 40.0)
        return result


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}

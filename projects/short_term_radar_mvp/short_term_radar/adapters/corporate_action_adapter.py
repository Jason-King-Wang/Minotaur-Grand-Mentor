from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter


class CorporateActionAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load_features(self, as_of_date: str, lookahead_days: int = 14) -> dict[str, dict[str, Any]]:
        rows = self.processed.load_table("corporate_actions")
        start = date.fromisoformat(as_of_date) - timedelta(days=lookahead_days)
        end = date.fromisoformat(as_of_date) + timedelta(days=lookahead_days)
        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            action_date = row.get("action_date")
            if not action_date:
                continue
            try:
                parsed = date.fromisoformat(str(action_date))
            except ValueError:
                continue
            if not (start <= parsed <= end):
                continue
            symbol = str(row.get("symbol") or "")
            if not symbol:
                continue
            action_type = str(row.get("action_type") or "unknown")
            result[symbol] = {
                "nearby_corporate_action_flag": True,
                "ex_dividend_nearby_flag": "dividend" in action_type,
                "capital_increase_nearby_flag": action_type == "capital_increase",
                "stock_split_or_reduction_flag": action_type in {"split", "reduction"},
                "corporate_action_risk_note": action_type,
            }
        return result

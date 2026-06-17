from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter
from short_term_radar.utils.io import read_csv_records


class CatalystAdapter:
    def __init__(self, manual_catalysts=None, config: dict[str, Any] | None = None):
        if config is None and isinstance(manual_catalysts, dict) and "data" in manual_catalysts:
            config = manual_catalysts
            manual_catalysts = config.get("manual_catalysts")
        self.manual_catalysts = manual_catalysts or {}
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load(self):
        return self.manual_catalysts

    def rows_for_symbol(self, symbol: str) -> list[dict[str, Any]]:
        path = (self.config.get("data") or {}).get("catalyst_path")
        if not path:
            return []
        return [row for row in read_csv_records(path) if str(row.get("symbol") or "") == str(symbol)]

    def load_features(self, as_of_date: str) -> dict[str, dict[str, Any]]:
        rows = self.processed.load_table("material_events")
        cutoff = date.fromisoformat(as_of_date) - timedelta(days=30)
        result: dict[str, dict[str, Any]] = {}
        for row in rows:
            announce_date = row.get("announce_date")
            if not announce_date or not (cutoff.isoformat() <= str(announce_date) <= as_of_date):
                continue
            symbol = str(row.get("symbol") or "")
            if not symbol:
                continue
            feature = result.setdefault(
                symbol,
                {
                    "material_event_count_30d": 0,
                    "positive_catalyst_count_30d": 0,
                    "risk_event_count_30d": 0,
                    "investor_conference_flag": False,
                    "major_order_flag": False,
                    "new_product_flag": False,
                    "capacity_expansion_flag": False,
                    "customer_supply_chain_flag": False,
                    "capital_raise_risk_flag": False,
                    "lawsuit_or_penalty_flag": False,
                    "latest_material_event_title": None,
                    "latest_material_event_type": None,
                },
            )
            event_type = row.get("event_type") or "other"
            feature["material_event_count_30d"] += 1
            if _to_float(row.get("catalyst_score")) and _to_float(row.get("catalyst_score")) > 0:
                feature["positive_catalyst_count_30d"] += 1
            if _to_float(row.get("risk_score")) and _to_float(row.get("risk_score")) > 0:
                feature["risk_event_count_30d"] += 1
            _set_event_flags(feature, str(event_type))
            if not feature["latest_material_event_title"] or str(row["announce_date"]) >= str(feature.get("_latest_date") or ""):
                feature["_latest_date"] = str(row["announce_date"])
                feature["latest_material_event_title"] = row.get("title")
                feature["latest_material_event_type"] = event_type

        for symbol, catalysts in (self.manual_catalysts or {}).items():
            feature = result.setdefault(str(symbol), {"material_event_count_30d": 0})
            feature["manual_catalyst"] = catalysts
        for feature in result.values():
            feature.pop("_latest_date", None)
        return result


def _set_event_flags(feature: dict[str, Any], event_type: str) -> None:
    mapping = {
        "investor_conference": "investor_conference_flag",
        "major_order": "major_order_flag",
        "new_product": "new_product_flag",
        "capacity_expansion": "capacity_expansion_flag",
        "customer_supply_chain": "customer_supply_chain_flag",
        "capital_increase": "capital_raise_risk_flag",
        "lawsuit": "lawsuit_or_penalty_flag",
        "regulatory_penalty": "lawsuit_or_penalty_flag",
    }
    if event_type in mapping:
        feature[mapping[event_type]] = True


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

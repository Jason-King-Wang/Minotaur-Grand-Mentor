from __future__ import annotations

from statistics import mean
from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter
from short_term_radar.utils.io import read_csv_records


class RevenueAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load(self) -> dict[str, dict[str, Any]]:
        return {}

    def rows_until(self, symbol: str, as_of_date: str) -> list[dict[str, Any]]:
        path = (self.config.get("data") or {}).get("monthly_revenue_path")
        if not path:
            return []
        rows = [
            row
            for row in read_csv_records(path)
            if str(row.get("symbol") or "") == str(symbol)
            and _available(row, as_of_date)
        ]
        rows.sort(key=lambda row: str(row.get("revenue_month") or ""))
        return rows

    def load_features(self, as_of_date: str) -> dict[str, dict[str, Any]]:
        rows = self.processed.load_table("monthly_revenue")
        available = [row for row in rows if _available(row, as_of_date)]
        by_symbol: dict[str, list[dict[str, Any]]] = {}
        for row in available:
            by_symbol.setdefault(str(row.get("symbol")), []).append(row)

        result: dict[str, dict[str, Any]] = {}
        for symbol, symbol_rows in by_symbol.items():
            symbol_rows.sort(key=lambda row: str(row.get("revenue_month") or ""))
            latest = symbol_rows[-1]
            yoy_values = [_to_float(row.get("revenue_yoy_pct")) for row in symbol_rows if row.get("revenue_yoy_pct") is not None]
            latest_yoy = _to_float(latest.get("revenue_yoy_pct"))
            previous_yoy = _to_float(symbol_rows[-2].get("revenue_yoy_pct")) if len(symbol_rows) >= 2 else None
            last_3 = [value for value in yoy_values[-3:] if value is not None]
            last_6 = [value for value in yoy_values[-6:] if value is not None]
            prior_12 = [value for value in yoy_values[:-3][-12:] if value is not None]
            revenues = [_to_float(row.get("revenue_current")) for row in symbol_rows]
            latest_revenue = _to_float(latest.get("revenue_current"))
            same_month = str(latest.get("revenue_month") or "")[-2:]
            same_month_revenues = [
                _to_float(row.get("revenue_current"))
                for row in symbol_rows
                if str(row.get("revenue_month") or "")[-2:] == same_month
            ]
            positive_streak = 0
            for row in reversed(symbol_rows):
                yoy = _to_float(row.get("revenue_yoy_pct"))
                if yoy is not None and yoy > 0:
                    positive_streak += 1
                else:
                    break

            result[symbol] = {
                "rev_yoy_1m": latest_yoy,
                "rev_mom_1m": _to_float(latest.get("revenue_mom_pct")),
                "rev_yoy_3m": mean(last_3) if last_3 else None,
                "rev_yoy_6m": mean(last_6) if last_6 else None,
                "rev_acceleration_3m_vs_12m": (mean(last_3) - mean(prior_12)) if last_3 and prior_12 else None,
                "rev_new_high_flag": bool(latest_revenue is not None and latest_revenue >= max(v for v in revenues if v is not None)),
                "rev_same_month_high_flag": bool(
                    latest_revenue is not None and same_month_revenues and latest_revenue >= max(v for v in same_month_revenues if v is not None)
                ),
                "rev_turn_positive_flag": bool(latest_yoy is not None and latest_yoy > 0 and previous_yoy is not None and previous_yoy <= 0),
                "rev_positive_streak_months": positive_streak,
                "rev_surprise_proxy": (latest_yoy - previous_yoy) if latest_yoy is not None and previous_yoy is not None else None,
                "latest_revenue_month": latest.get("revenue_month"),
                "latest_revenue_announce_date": latest.get("announce_date"),
            }
        return result


def _available(row: dict[str, Any], as_of_date: str) -> bool:
    announce_date = row.get("announce_date") or row.get("release_date")
    return bool(announce_date and str(announce_date) <= as_of_date)


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

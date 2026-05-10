from __future__ import annotations

from typing import Any

from short_term_radar.adapters.table_utils import (
    date_text,
    month_text,
    next_month_release_date,
    number_value,
    rate_value,
    read_table,
    text_value,
)


ALIASES = {
    "symbol": ["symbol", "stock_id", "code", "ticker"],
    "revenue_month": ["revenue_month", "month", "yyyymm"],
    "revenue": ["revenue", "monthly_revenue", "net_revenue"],
    "revenue_yoy": ["revenue_yoy", "yoy", "monthly_revenue_yoy"],
    "revenue_mom": ["revenue_mom", "mom", "monthly_revenue_mom"],
    "release_date": ["release_date", "announce_date", "published_at"],
}


class RevenueAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        data_cfg = self.config.get("data", {})
        self.path = data_cfg.get("monthly_revenue_path") or data_cfg.get("revenue_path")
        self.rows_by_symbol: dict[str, list[dict[str, Any]]] = {}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for raw in read_table(self.path):
            row = self._normalize_row(raw)
            if not row.get("symbol") or not row.get("revenue_month"):
                continue
            rows_by_symbol.setdefault(row["symbol"], []).append(row)
        for rows in rows_by_symbol.values():
            rows.sort(key=lambda item: (item["revenue_month"], item.get("release_date") or ""))
        self.rows_by_symbol = rows_by_symbol
        return rows_by_symbol

    def rows_until(self, symbol: str, as_of_date: str) -> list[dict[str, Any]]:
        if not self.rows_by_symbol:
            self.load()
        rows = self.rows_by_symbol.get(str(symbol), [])
        return [row for row in rows if (row.get("release_date") or "9999-99-99") <= as_of_date]

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        revenue_month = month_text(text_value(row, ALIASES["revenue_month"]))
        release_date = date_text(text_value(row, ALIASES["release_date"])) or next_month_release_date(revenue_month)
        return {
            "symbol": text_value(row, ALIASES["symbol"]),
            "revenue_month": revenue_month,
            "revenue": number_value(row, ALIASES["revenue"]),
            "revenue_yoy": rate_value(row, ALIASES["revenue_yoy"]),
            "revenue_mom": rate_value(row, ALIASES["revenue_mom"]),
            "release_date": release_date,
        }

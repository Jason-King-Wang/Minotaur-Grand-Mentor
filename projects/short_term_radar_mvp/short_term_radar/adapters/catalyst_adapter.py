from __future__ import annotations

from typing import Any

from short_term_radar.adapters.table_utils import date_text, number_value, read_table, text_value


ALIASES = {
    "symbol": ["symbol", "stock_id", "code", "ticker"],
    "event_date": ["event_date", "date"],
    "category": ["category", "event_type", "type"],
    "confidence": ["confidence", "probability"],
    "impact": ["impact", "direction"],
    "status": ["status"],
    "notes": ["notes", "memo", "description"],
    "source": ["source"],
}


class CatalystAdapter:
    def __init__(self, config: dict[str, Any] | None = None, manual_catalysts: Any | None = None):
        self.config = config or {}
        self.path = (
            self.config.get("catalyst", {}).get("catalyst_path")
            or self.config.get("data", {}).get("catalyst_path")
        )
        self.manual_catalysts = manual_catalysts if manual_catalysts is not None else self.config.get("manual_catalysts", {})
        self.rows_by_symbol: dict[str, list[dict[str, Any]]] = {}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        rows: list[dict[str, Any]] = []
        rows.extend(read_table(self.path))
        rows.extend(self._manual_rows())
        rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for raw in rows:
            row = self._normalize_row(raw)
            if not row.get("symbol") or not row.get("event_date"):
                continue
            rows_by_symbol.setdefault(row["symbol"], []).append(row)
        for items in rows_by_symbol.values():
            items.sort(key=lambda item: item["event_date"])
        self.rows_by_symbol = rows_by_symbol
        return rows_by_symbol

    def rows_for_symbol(self, symbol: str) -> list[dict[str, Any]]:
        if not self.rows_by_symbol:
            self.load()
        return self.rows_by_symbol.get(str(symbol), [])

    def _manual_rows(self) -> list[dict[str, Any]]:
        if isinstance(self.manual_catalysts, list):
            return self.manual_catalysts
        if isinstance(self.manual_catalysts, dict):
            rows: list[dict[str, Any]] = []
            for symbol, events in self.manual_catalysts.items():
                if isinstance(events, dict):
                    events = [events]
                for event in events or []:
                    if isinstance(event, dict):
                        rows.append({"symbol": symbol, **event})
            return rows
        return []

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "symbol": text_value(row, ALIASES["symbol"]),
            "event_date": date_text(text_value(row, ALIASES["event_date"])),
            "category": text_value(row, ALIASES["category"]) or "other",
            "confidence": number_value(row, ALIASES["confidence"]),
            "impact": (text_value(row, ALIASES["impact"]) or "neutral").lower(),
            "status": (text_value(row, ALIASES["status"]) or "expected").lower(),
            "notes": text_value(row, ALIASES["notes"]),
            "source": text_value(row, ALIASES["source"]),
        }

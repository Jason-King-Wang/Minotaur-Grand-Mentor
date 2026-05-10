from __future__ import annotations

from typing import Any

from short_term_radar.adapters.table_utils import date_text, number_value, read_table, text_value


ALIASES = {
    "symbol": ["symbol", "stock_id", "code", "ticker"],
    "trade_date": ["trade_date", "date"],
    "foreign_buy": ["foreign_buy", "foreign_net_buy"],
    "investment_trust_buy": ["investment_trust_buy", "trust_buy", "it_buy"],
    "dealer_buy": ["dealer_buy", "dealer_net_buy"],
    "inst_buy_total": ["inst_buy_total", "institutional_buy", "three_major_buy"],
    "margin_balance": ["margin_balance", "margin"],
    "short_balance": ["short_balance", "short"],
    "borrow_balance": ["borrow_balance", "borrow"],
    "shares_outstanding": ["shares_outstanding", "shares"],
}


class ChipAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.path = self.config.get("data", {}).get("chip_data_path")
        self.rows_by_symbol: dict[str, list[dict[str, Any]]] = {}

    def load(self) -> dict[str, list[dict[str, Any]]]:
        rows_by_symbol: dict[str, list[dict[str, Any]]] = {}
        for raw in read_table(self.path):
            row = self._normalize_row(raw)
            if not row.get("symbol") or not row.get("trade_date"):
                continue
            rows_by_symbol.setdefault(row["symbol"], []).append(row)
        for rows in rows_by_symbol.values():
            rows.sort(key=lambda item: item["trade_date"])
        self.rows_by_symbol = rows_by_symbol
        return rows_by_symbol

    def rows_until(self, symbol: str, as_of_date: str) -> list[dict[str, Any]]:
        if not self.rows_by_symbol:
            self.load()
        rows = self.rows_by_symbol.get(str(symbol), [])
        return [row for row in rows if row.get("trade_date") <= as_of_date]

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        foreign_buy = number_value(row, ALIASES["foreign_buy"]) or 0.0
        trust_buy = number_value(row, ALIASES["investment_trust_buy"]) or 0.0
        dealer_buy = number_value(row, ALIASES["dealer_buy"]) or 0.0
        inst_total = number_value(row, ALIASES["inst_buy_total"])
        if inst_total is None:
            inst_total = foreign_buy + trust_buy + dealer_buy
        return {
            "symbol": text_value(row, ALIASES["symbol"]),
            "trade_date": date_text(text_value(row, ALIASES["trade_date"])),
            "foreign_buy": foreign_buy,
            "investment_trust_buy": trust_buy,
            "dealer_buy": dealer_buy,
            "inst_buy_total": inst_total,
            "margin_balance": number_value(row, ALIASES["margin_balance"]),
            "short_balance": number_value(row, ALIASES["short_balance"]),
            "borrow_balance": number_value(row, ALIASES["borrow_balance"]),
            "shares_outstanding": number_value(row, ALIASES["shares_outstanding"]),
        }

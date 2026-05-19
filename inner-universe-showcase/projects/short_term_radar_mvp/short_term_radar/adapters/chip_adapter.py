from __future__ import annotations

from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter
from short_term_radar.utils.io import read_csv_records


class ChipAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load(self) -> dict[str, dict[str, Any]]:
        return {}

    def rows_until(self, symbol: str, as_of_date: str) -> list[dict[str, Any]]:
        path = (self.config.get("data") or {}).get("chip_data_path")
        if not path:
            return []
        rows = [
            _normalize_chip_row(row)
            for row in read_csv_records(path)
            if str(row.get("symbol") or "") == str(symbol)
            and row.get("trade_date")
            and str(row["trade_date"]) <= as_of_date
        ]
        rows.sort(key=lambda row: str(row.get("trade_date") or ""))
        return rows

    def load_features(self, as_of_date: str) -> dict[str, dict[str, Any]]:
        institutional = _rows_until(self.processed.load_table("institutional_trading_daily"), as_of_date, "trade_date")
        margin = _rows_until(self.processed.load_table("margin_short_daily"), as_of_date, "trade_date")
        result: dict[str, dict[str, Any]] = {}

        for symbol, rows in _group_by_symbol(institutional).items():
            rows.sort(key=lambda row: str(row.get("trade_date") or ""))
            result.setdefault(symbol, {}).update(
                {
                    "foreign_net_5d": _sum_last(rows, "foreign_net", 5),
                    "foreign_net_20d": _sum_last(rows, "foreign_net", 20),
                    "investment_trust_net_5d": _sum_last(rows, "investment_trust_net", 5),
                    "investment_trust_net_20d": _sum_last(rows, "investment_trust_net", 20),
                    "dealer_net_5d": _sum_last(rows, "dealer_net", 5),
                    "total_institutional_net_5d": _sum_last(rows, "total_institutional_net", 5),
                    "total_institutional_net_20d": _sum_last(rows, "total_institutional_net", 20),
                }
            )

        for symbol, rows in _group_by_symbol(margin).items():
            rows.sort(key=lambda row: str(row.get("trade_date") or ""))
            latest = rows[-1] if rows else {}
            margin_latest = _to_float(latest.get("margin_balance"))
            margin_20 = _to_float(rows[-21].get("margin_balance")) if len(rows) > 20 else None
            result.setdefault(symbol, {}).update(
                {
                    "margin_balance_change_5d": _delta(rows, "margin_balance", 5),
                    "margin_balance_change_20d": _delta(rows, "margin_balance", 20),
                    "margin_balance_pct_change_20d": (margin_latest - margin_20) / margin_20
                    if margin_latest is not None and margin_20
                    else None,
                    "short_balance_change_5d": _delta(rows, "short_balance", 5),
                    "sbl_short_sell_ratio": None,
                    "financing_overcrowded_flag": bool(
                        margin_latest is not None and margin_20 and (margin_latest - margin_20) / margin_20 > 0.5
                    ),
                    "short_squeeze_candidate_flag": bool((_delta(rows, "short_balance", 5) or 0) > 0),
                }
            )
        return result


def _rows_until(rows: list[dict[str, Any]], as_of_date: str, date_column: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get(date_column) and str(row[date_column]) <= as_of_date]


def _normalize_chip_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(row)
    if "inst_buy_total" not in normalized:
        total = sum(
            value or 0.0
            for value in (
                _to_float(row.get("foreign_buy") or row.get("foreign_net")),
                _to_float(row.get("investment_trust_buy") or row.get("investment_trust_net")),
                _to_float(row.get("dealer_buy") or row.get("dealer_net")),
            )
        )
        normalized["inst_buy_total"] = total
    return normalized


def _group_by_symbol(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("symbol"):
            result.setdefault(str(row["symbol"]), []).append(row)
    return result


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _sum_last(rows: list[dict[str, Any]], column: str, count: int) -> float | None:
    values = [_to_float(row.get(column)) for row in rows[-count:]]
    values = [value for value in values if value is not None]
    return sum(values) if values else None


def _delta(rows: list[dict[str, Any]], column: str, count: int) -> float | None:
    if len(rows) <= count:
        return None
    latest = _to_float(rows[-1].get(column))
    previous = _to_float(rows[-count - 1].get(column))
    return latest - previous if latest is not None and previous is not None else None

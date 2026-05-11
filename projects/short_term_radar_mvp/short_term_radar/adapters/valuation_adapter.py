from __future__ import annotations

from typing import Any

from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter


class ValuationAdapter:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.processed = ProcessedDataAdapter(self.config)

    def load_features(self, as_of_date: str) -> dict[str, dict[str, Any]]:
        valuations = [
            row for row in self.processed.load_table("valuation_daily") if row.get("trade_date") and str(row["trade_date"]) <= as_of_date
        ]
        symbols = {row.get("symbol"): row for row in self.processed.load_table("symbol_master") if row.get("symbol")}
        result: dict[str, dict[str, Any]] = {}
        valuations.sort(key=lambda row: str(row.get("trade_date") or ""))
        for row in valuations:
            symbol = str(row.get("symbol") or "")
            if not symbol:
                continue
            symbol_row = symbols.get(symbol, {})
            market_cap = _to_float(row.get("market_cap"))
            issued = _to_float(symbol_row.get("issued_shares"))
            close = _to_float(row.get("close"))
            if market_cap is None and issued is not None and close is not None:
                market_cap = issued * close
            paid_in = _to_float(symbol_row.get("paid_in_capital"))
            result[symbol] = {
                "market_cap": market_cap,
                "paid_in_capital": paid_in,
                "issued_shares": issued,
                "pe": _to_float(row.get("pe")),
                "pb": _to_float(row.get("pb")),
                "dividend_yield": _to_float(row.get("dividend_yield")),
                "large_cap_flag": bool(market_cap is not None and market_cap >= 100_000_000_000),
                "small_mid_cap_flag": bool(market_cap is not None and market_cap < 50_000_000_000),
                "elasticity_bucket": _elasticity_bucket(paid_in, market_cap),
                "valuation_overheated_flag": bool((_to_float(row.get("pe")) or 0) >= 80 or (_to_float(row.get("pb")) or 0) >= 10),
            }
        return result


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _elasticity_bucket(paid_in_capital: float | None, market_cap: float | None) -> str | None:
    value = market_cap if market_cap is not None else paid_in_capital
    if value is None:
        return None
    if value < 10_000_000_000:
        return "high_elasticity"
    if value < 50_000_000_000:
        return "mid_elasticity"
    return "low_elasticity"

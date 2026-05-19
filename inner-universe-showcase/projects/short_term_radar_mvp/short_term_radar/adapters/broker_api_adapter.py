from __future__ import annotations

from datetime import date
from typing import Any

from short_term_radar.utils.math_utils import safe_float


class BrokerApiAdapter:
    """Read-only Shioaji/SinoPac market-data adapter.

    This adapter intentionally accepts an already logged-in API object from the
    caller. It never asks for credentials and has no order placement methods.
    """

    read_only = True

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}

    def resolve_index_contract(self, api: Any, candidates: list[str] | None = None):
        candidates = candidates or self.config.get("market_index_contract_candidates") or [
            "TSE.TSE001",
            "TSE001",
            "TAIEX",
        ]
        index_root = getattr(getattr(api, "Contracts", None), "Indexs", None)
        if index_root is None:
            return None

        for candidate in candidates:
            contract = self._resolve_contract_path(index_root, candidate)
            if contract is not None:
                return contract
        return None

    def fetch_index_daily_prices(
        self,
        api: Any,
        start: str,
        end: str,
        symbol: str = "TAIEX",
        candidates: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        contract = self.resolve_index_contract(api, candidates)
        if contract is None:
            raise LookupError("TAIEX index contract was not found under api.Contracts.Indexs.")

        kbars = api.kbars(contract, start=start, end=end)
        rows = self._normalize_kbars(kbars, symbol)
        rows.sort(key=lambda row: row["trade_date"])
        return rows

    def _resolve_contract_path(self, root: Any, path: str):
        current = root
        for part in path.split("."):
            next_value = None
            if hasattr(current, "get"):
                next_value = current.get(part)
            if next_value is None:
                next_value = getattr(current, part, None)
            if next_value is None:
                return None
            current = next_value
        return current

    def _normalize_kbars(self, kbars: Any, symbol: str) -> list[dict[str, Any]]:
        data = dict(kbars)
        timestamps = data.get("ts") or data.get("Time") or data.get("time") or []
        opens = data.get("Open") or data.get("open") or []
        highs = data.get("High") or data.get("high") or []
        lows = data.get("Low") or data.get("low") or []
        closes = data.get("Close") or data.get("close") or []
        volumes = data.get("Volume") or data.get("volume") or []
        amounts = data.get("Amount") or data.get("amount") or []

        rows: list[dict[str, Any]] = []
        for index, ts in enumerate(timestamps):
            trade_date = self._date_text(ts)
            close = self._at(closes, index)
            volume = self._at(volumes, index, 0.0)
            amount = self._at(amounts, index)
            if amount is None and close is not None and volume is not None:
                amount = close * volume
            rows.append(
                {
                    "symbol": symbol,
                    "name": "TAIEX",
                    "industry": "Market Index",
                    "trade_date": trade_date,
                    "open": self._at(opens, index),
                    "high": self._at(highs, index),
                    "low": self._at(lows, index),
                    "close": close,
                    "volume": volume,
                    "amount": amount,
                    "market": "INDEX",
                }
            )
        return [row for row in rows if row["trade_date"] and row["close"] is not None]

    def _at(self, values: Any, index: int, default: float | None = None) -> float | None:
        try:
            return safe_float(values[index], default)
        except (IndexError, TypeError, KeyError):
            return default

    def _date_text(self, value: Any) -> str:
        if isinstance(value, date):
            return value.isoformat()
        text = str(value)
        return text[:10]

from __future__ import annotations

from datetime import datetime
from typing import Any

from short_term_radar.adapters.broker_api_adapter import BrokerApiAdapter
from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.normalizers.margin_short import normalize_margin_short_rows
from short_term_radar.data_sources.normalizers.surveillance import normalize_surveillance_rows

FORBIDDEN_BROKER_METHODS = {
    "place_order",
    "update_order",
    "cancel_order",
    "account_balance",
    "positions",
    "realized_pnl",
    "unrealized_pnl",
    "settlements",
}


class BrokerReadonlyFetcher:
    read_only = True

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.adapter = BrokerApiAdapter(self.config)

    def assert_read_only_api(self, api: Any) -> None:
        if not self.config.get("strict_api_surface", False):
            return
        exposed = {name for name in FORBIDDEN_BROKER_METHODS if hasattr(api, name)}
        if exposed:
            raise AttributeError(f"Broker API object exposes forbidden methods: {sorted(exposed)}")

    def fetch_index_daily_prices(self, api: Any, start: str, end: str) -> FetchResult:
        self.assert_read_only_api(api)
        rows = self.adapter.fetch_index_daily_prices(api, start, end)
        return FetchResult("broker_api", "prices_daily", None, rows=rows)

    def fetch_surveillance_daily(self, api: Any, trade_date: str, market: str = "all") -> FetchResult:
        self.assert_read_only_api(api)
        raw_rows: list[dict[str, Any]] = []
        if hasattr(api, "notice"):
            raw_rows.extend(self._notice_rows(api.notice(), trade_date))
        if hasattr(api, "punish"):
            raw_rows.extend(self._punish_rows(api.punish(), trade_date))
        rows = normalize_surveillance_rows(
            raw_rows,
            market if market.lower() != "all" else "Unknown",
            "broker_api",
            "shioaji.notice|shioaji.punish",
            self._fetched_at(),
        )
        return FetchResult("broker_api", "surveillance_daily", None, rows=self._filter_market(rows, market))

    def fetch_margin_short_daily(
        self,
        api: Any,
        symbols: list[str],
        trade_date: str,
        market: str = "all",
    ) -> FetchResult:
        self.assert_read_only_api(api)
        if not symbols:
            raise ValueError("broker_api margin_short collection requires at least one symbol.")

        contract_by_symbol = {
            symbol: self.adapter.resolve_stock_contract(api, symbol, self._exchange_hint(market))
            for symbol in symbols
        }
        contracts = [contract for contract in contract_by_symbol.values() if contract is not None]
        credit_rows = self._indexed_rows(self._call_optional(api, "credit_enquires", contracts))
        short_source_rows = self._indexed_rows(self._call_optional(api, "short_stock_sources", contracts))

        raw_rows: list[dict[str, Any]] = []
        for symbol, contract in contract_by_symbol.items():
            if contract is None:
                continue
            contract_row = self._object_row(contract)
            credit = credit_rows.get(symbol, {})
            short_source = short_source_rows.get(symbol, {})
            raw_rows.append(
                {
                    "trade_date": trade_date,
                    "market": self._market_from_contract(contract, market),
                    "symbol": symbol,
                    "name": self._pick(contract_row, "name", "stock_name", "證券名稱", default=""),
                    "margin_balance": self._pick(
                        credit,
                        "margin_trading_balance",
                        "margin_balance",
                        "融資餘額",
                        default=self._pick(contract_row, "margin_trading_balance", "margin_balance", "融資餘額"),
                    ),
                    "short_balance": self._pick(
                        credit,
                        "short_selling_balance",
                        "short_balance",
                        "融券餘額",
                        default=self._pick(contract_row, "short_selling_balance", "short_balance", "融券餘額"),
                    ),
                    "sbl_balance": self._pick(
                        short_source,
                        "sbl_balance",
                        "short_stock_source_balance",
                        "available_volume",
                        "quantity",
                        "可借券股數",
                    ),
                }
            )

        rows = normalize_margin_short_rows(
            raw_rows,
            market if market.lower() != "all" else "Unknown",
            "broker_api",
            "shioaji.credit_enquires|shioaji.short_stock_sources|shioaji.Contracts.Stocks",
            self._fetched_at(),
        )
        return FetchResult("broker_api", "margin_short_daily", None, rows=self._filter_market(rows, market))

    def _notice_rows(self, payload: Any, trade_date: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in self._records(payload):
            rows.append(
                {
                    "trade_date": self._pick(row, "trade_date", "date", "公告日", "公布日期", default=trade_date),
                    "market": self._pick(row, "market", "exchange", "市場"),
                    "symbol": self._pick(row, "symbol", "code", "stock_id", "股票代號", "證券代號"),
                    "name": self._pick(row, "name", "stock_name", "股票名稱", "證券名稱"),
                    "attention_reason": self._pick(row, "attention_reason", "reason", "注意原因", "注意交易資訊"),
                    "attention_close": self._pick(row, "attention_close", "close", "收盤價"),
                    "attention_pe": self._pick(row, "attention_pe", "pe", "本益比"),
                }
            )
        return rows

    def _punish_rows(self, payload: Any, trade_date: str) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for row in self._records(payload):
            start = self._pick(row, "disposition_start", "start_date", "處置開始日")
            end = self._pick(row, "disposition_end", "end_date", "處置結束日")
            period = self._pick(row, "disposition_period", "處置起訖時間", "處置期間")
            if not period and (start or end):
                period = f"{self._range_date_text(start or end)}~{self._range_date_text(end or start)}"
            rows.append(
                {
                    "trade_date": self._pick(row, "trade_date", "announce_date", "date", "公告日", default=trade_date),
                    "market": self._pick(row, "market", "exchange", "市場"),
                    "symbol": self._pick(row, "symbol", "code", "stock_id", "股票代號", "證券代號"),
                    "name": self._pick(row, "name", "stock_name", "股票名稱", "證券名稱"),
                    "disposition_period": period,
                    "disposition_reason": self._pick(row, "disposition_reason", "reason", "處置原因", "處置說明"),
                    "disposition_measure": self._pick(row, "disposition_measure", "measure", "處置內容", "處置措施"),
                    "disposition_condition": self._pick(row, "disposition_condition", "condition", "條件"),
                }
            )
        return rows

    def _call_optional(self, api: Any, method: str, contracts: list[Any]) -> Any:
        if not contracts or not hasattr(api, method):
            return []
        return getattr(api, method)(contracts)

    def _records(self, payload: Any) -> list[dict[str, Any]]:
        if payload is None:
            return []
        if hasattr(payload, "to_dict"):
            try:
                records = payload.to_dict("records")
                if isinstance(records, list):
                    return [self._object_row(row) for row in records]
            except TypeError:
                pass
        if isinstance(payload, dict):
            values = list(payload.values())
            if values and all(isinstance(value, list) for value in values):
                max_len = max(len(value) for value in values)
                return [{key: value[index] if index < len(value) else None for key, value in payload.items()} for index in range(max_len)]
            return [payload]
        if isinstance(payload, (list, tuple, set)):
            return [self._object_row(item) for item in payload]
        return [self._object_row(payload)]

    def _object_row(self, value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if hasattr(value, "_asdict"):
            return dict(value._asdict())
        if hasattr(value, "__dict__"):
            return dict(vars(value))
        row: dict[str, Any] = {}
        for name in dir(value):
            if name.startswith("_"):
                continue
            try:
                item = getattr(value, name)
            except Exception:
                continue
            if not callable(item):
                row[name] = item
        return row

    def _indexed_rows(self, payload: Any) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        for row in self._records(payload):
            symbol = str(self._pick(row, "symbol", "code", "stock_id", "股票代號", "證券代號", default="")).strip()
            if symbol:
                rows[symbol] = row
        return rows

    def _pick(self, row: dict[str, Any], *names: str, default: Any = None) -> Any:
        lower = {str(key).lower(): key for key in row}
        for name in names:
            if name in row and row[name] is not None and row[name] != "":
                return row[name]
            key = lower.get(name.lower())
            if key is not None and row[key] is not None and row[key] != "":
                return row[key]
        return default

    def _filter_market(self, rows: list[dict[str, Any]], market: str) -> list[dict[str, Any]]:
        if market.lower() == "all":
            return rows
        normalized = "TWSE" if market.upper() in {"TWSE", "TSE"} else "TPEX" if market.upper() in {"TPEX", "OTC"} else market.upper()
        return [row for row in rows if row.get("market") in {normalized, "Unknown"}]

    def _exchange_hint(self, market: str) -> str:
        return {"TWSE": "TSE", "TSE": "TSE", "TPEX": "OTC", "OTC": "OTC"}.get(market.upper(), "")

    def _market_from_contract(self, contract: Any, fallback: str) -> str:
        exchange = str(getattr(contract, "exchange", "") or getattr(contract, "market", "") or "").upper()
        if "TSE" in exchange or "TWSE" in exchange:
            return "TWSE"
        if "OTC" in exchange or "TPEX" in exchange:
            return "TPEX"
        if fallback.upper() in {"TWSE", "TSE"}:
            return "TWSE"
        if fallback.upper() in {"TPEX", "OTC"}:
            return "TPEX"
        return "Unknown"

    def _fetched_at(self) -> str:
        return datetime.now().isoformat(timespec="seconds")

    def _range_date_text(self, value: Any) -> str:
        return str(value).replace("-", "/")

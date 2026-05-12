from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.fetchers.broker_readonly_fetcher import BrokerReadonlyFetcher

ALLOWED_READONLY_METHODS = {
    "kbars",
    "snapshots",
    "ticks",
    "daily_quotes",
    "notice",
    "punish",
    "credit_enquires",
    "short_stock_sources",
    "scanners",
}

FORBIDDEN_ORDER_OR_ACCOUNT_METHODS = {
    "place_order",
    "update_order",
    "cancel_order",
    "account_balance",
    "positions",
    "realized_pnl",
    "unrealized_pnl",
    "settlements",
}


class BrokerReadonlySource:
    """Read-only broker source that requires an externally managed API object."""

    def __init__(self, config: dict[str, Any] | None = None, api: Any | None = None):
        self.config = config or {}
        self.api = api
        self.fetcher = BrokerReadonlyFetcher(self.config)

    def collect_surveillance_daily(
        self,
        trade_date: str,
        market: str = "all",
        api: Any | None = None,
    ) -> list[dict[str, Any]]:
        return self.fetcher.fetch_surveillance_daily(self._api(api), trade_date, market).rows

    def collect_margin_short_daily(
        self,
        symbols: list[str],
        trade_date: str,
        market: str = "all",
        api: Any | None = None,
    ) -> list[dict[str, Any]]:
        return self.fetcher.fetch_margin_short_daily(self._api(api), symbols, trade_date, market).rows

    def _api(self, api: Any | None) -> Any:
        selected = api or self.api
        if selected is None:
            raise ValueError("BrokerReadonlySource requires an externally managed read-only API object.")
        return selected

from __future__ import annotations

from typing import Any

from short_term_radar.adapters.broker_api_adapter import BrokerApiAdapter
from short_term_radar.data_sources.base import FetchResult

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
        exposed = {name for name in FORBIDDEN_BROKER_METHODS if hasattr(api, name)}
        if exposed:
            raise AttributeError(f"Broker API object exposes forbidden methods: {sorted(exposed)}")

    def fetch_index_daily_prices(self, api: Any, start: str, end: str) -> FetchResult:
        self.assert_read_only_api(api)
        rows = self.adapter.fetch_index_daily_prices(api, start, end)
        return FetchResult("broker_api", "prices_daily", None, rows=rows)

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.fetchers.tpex_institutional_trading_fetcher import TpexInstitutionalTradingFetcher
from short_term_radar.data_sources.fetchers.twse_institutional_trading_fetcher import (
    TwseInstitutionalTradingFetcher,
    normalize_trade_date,
)
from short_term_radar.data_sources.normalizers.institutional_trading import normalize_institutional_trading_rows


@dataclass(frozen=True)
class InstitutionalTradingRequest:
    market: str
    trade_date: str
    api_url: str | None
    enabled: bool
    note: str | None = None


@dataclass(frozen=True)
class InstitutionalTradingCollectResult:
    requests: list[InstitutionalTradingRequest]
    rows: list[dict[str, Any]]
    degraded: list[str]


class InstitutionalTradingOfficialSource:
    def __init__(
        self,
        config: dict[str, Any] | None = None,
        twse_fetcher: TwseInstitutionalTradingFetcher | None = None,
        tpex_fetcher: TpexInstitutionalTradingFetcher | None = None,
    ):
        self.config = config or {}
        self.twse_fetcher = twse_fetcher or TwseInstitutionalTradingFetcher(self.config)
        self.tpex_fetcher = tpex_fetcher or TpexInstitutionalTradingFetcher(self.config)

    def build_requests(self, market: str, trade_date: str) -> list[InstitutionalTradingRequest]:
        normalized_date = normalize_trade_date(trade_date)
        markets = ["TWSE", "TPEX"] if market.lower() == "all" else [market.upper()]
        return [self._build_request(item_market, normalized_date) for item_market in markets]

    def collect(self, market: str, trade_date: str) -> InstitutionalTradingCollectResult:
        requests = self.build_requests(market, trade_date)
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rows: list[dict[str, Any]] = []
        degraded: list[str] = []
        for request in requests:
            if not request.enabled or not request.api_url:
                degraded.append(request.note or f"{request.market} institutional_trading official source disabled")
                continue
            result = self._fetch(request)
            if result.degraded:
                degraded.append(f"{request.api_url}: {result.message or 'unavailable'}")
                continue
            normalized_rows = normalize_institutional_trading_rows(
                result.rows,
                request.market,
                result.source,
                request.api_url,
                fetched_at,
            )
            matching_rows = [row for row in normalized_rows if row.get("trade_date") == request.trade_date]
            if result.rows and not matching_rows:
                degraded.append(f"{request.market}: no rows matched requested trade_date {request.trade_date}")
                continue
            rows.extend(matching_rows)
        return InstitutionalTradingCollectResult(requests, rows, degraded)

    def _build_request(self, market: str, trade_date: str) -> InstitutionalTradingRequest:
        source_key = "twse" if market == "TWSE" else "tpex"
        source_cfg = ((self.config.get("sources") or {}).get(source_key) or {})
        dataset_cfg = ((source_cfg.get("datasets") or {}).get("institutional_trading") or {})
        api_url_template = dataset_cfg.get("api_url")
        enabled = bool(source_cfg.get("enabled", False)) and bool(api_url_template)
        note = None if enabled else f"{market} institutional_trading official api_url is disabled or missing"
        api_url = None
        if api_url_template:
            api_url = (
                self.twse_fetcher.build_url(api_url_template, trade_date)
                if market == "TWSE"
                else str(api_url_template)
            )
        return InstitutionalTradingRequest(market, trade_date, api_url, enabled, note)

    def _fetch(self, request: InstitutionalTradingRequest) -> FetchResult:
        if not request.api_url:
            return FetchResult("official", "institutional_trading", None, degraded=True, message="api_url missing")
        if request.market == "TWSE":
            return self.twse_fetcher.fetch_url(request.api_url, request.trade_date)
        return self.tpex_fetcher.fetch_url(request.api_url, request.trade_date)

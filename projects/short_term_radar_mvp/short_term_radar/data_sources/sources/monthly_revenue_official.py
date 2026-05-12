from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from short_term_radar.data_sources.fetchers.mops_monthly_revenue_fetcher import (
    MopsMonthlyRevenueFetcher,
    MonthlyRevenueUrl,
    iter_revenue_months,
)
from short_term_radar.data_sources.normalizers.monthly_revenue import normalize_monthly_revenue_rows


@dataclass(frozen=True)
class MonthlyRevenueCollectResult:
    requests: list[MonthlyRevenueUrl]
    rows: list[dict[str, Any]]
    degraded: list[str]
    raw_documents: list[dict[str, str]]


class MonthlyRevenueOfficialSource:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.fetcher = MopsMonthlyRevenueFetcher(self.config)

    def build_requests(
        self,
        market: str,
        start_month: str,
        end_month: str,
        company_type: str = "all",
    ) -> list[MonthlyRevenueUrl]:
        markets = ["TWSE", "TPEX"] if market.lower() == "all" else [market.upper()]
        company_types = ["local", "foreign"] if company_type == "all" else [company_type]
        requests: list[MonthlyRevenueUrl] = []
        for revenue_month in iter_revenue_months(start_month, end_month):
            for item_market in markets:
                for item_company_type in company_types:
                    requests.append(self.fetcher.build_url(item_market, revenue_month, item_company_type))
        return requests

    def collect(
        self,
        market: str,
        start_month: str,
        end_month: str,
        company_type: str = "all",
    ) -> MonthlyRevenueCollectResult:
        requests = self.build_requests(market, start_month, end_month, company_type)
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        normalized_rows: list[dict[str, Any]] = []
        degraded: list[str] = []
        raw_documents: list[dict[str, str]] = []
        for request in requests:
            result = self.fetcher.fetch_month(request.market, request.revenue_month, request.company_type)
            if result.degraded:
                degraded.append(f"{request.url}: {result.message or 'unavailable'}")
                continue
            if result.raw_text is not None:
                raw_documents.append(
                    {
                        "market": request.market,
                        "revenue_month": request.revenue_month,
                        "company_type": request.company_type,
                        "url": request.url,
                        "raw_text": result.raw_text,
                    }
                )
            normalized_rows.extend(
                normalize_monthly_revenue_rows(
                    result.rows,
                    request.market,
                    "official_mops",
                    request.url,
                    fetched_at,
                )
            )
        return MonthlyRevenueCollectResult(requests, normalized_rows, degraded, raw_documents)

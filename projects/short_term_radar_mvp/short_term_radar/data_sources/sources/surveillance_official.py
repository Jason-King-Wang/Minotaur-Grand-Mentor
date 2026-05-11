from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from short_term_radar.data_sources.fetchers.http_fetcher import HttpFetcher
from short_term_radar.data_sources.normalizers.surveillance import normalize_surveillance_rows


@dataclass(frozen=True)
class SurveillanceRequest:
    market: str
    kind: str
    download_url: str | None
    enabled: bool
    landing_url: str | None = None
    note: str | None = None


class SurveillanceOfficialSource:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.fetcher = HttpFetcher(self.config)

    def build_requests(self, market: str = "all") -> list[SurveillanceRequest]:
        markets = ["TWSE", "TPEX"] if market.lower() == "all" else [market.upper()]
        requests: list[SurveillanceRequest] = []
        for item_market in markets:
            if item_market == "TWSE":
                requests.append(
                    SurveillanceRequest(
                        "TWSE",
                        "attention_disposition",
                        None,
                        False,
                        "twse_eshop_disabled",
                        "TWSE attention/disposition free endpoint is registry-only; e-shop remains disabled by default.",
                    )
                )
                continue
            datasets = ((self.config.get("sources") or {}).get("tpex") or {}).get("datasets") or {}
            for kind in ["attention", "disposition"]:
                dataset = datasets.get(kind) or {}
                download_url = dataset.get("download_url")
                landing_url = dataset.get("landing_url") or dataset.get("url") or f"https://data.gov.tw/dataset/{'11395' if kind == 'attention' else '11396'}"
                requests.append(
                    SurveillanceRequest(
                        "TPEX",
                        kind,
                        download_url,
                        bool(download_url),
                        landing_url,
                        None if download_url else "download_url is not configured; data.gov landing_url is not fetchable as CSV.",
                    )
                )
        return requests

    def collect(self, market: str = "all") -> tuple[list[dict[str, Any]], list[str]]:
        rows: list[dict[str, Any]] = []
        degraded: list[str] = []
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for request in self.build_requests(market):
            if not request.enabled:
                degraded.append(request.note or f"{request.market} {request.kind} disabled")
                continue
            if not request.download_url:
                degraded.append(f"{request.market} {request.kind}: download_url not configured")
                continue
            result = self.fetcher.fetch_text(request.download_url, "official", "surveillance")
            if result.degraded or not result.raw_text:
                degraded.append(f"{request.download_url}: {result.message or 'unavailable'}")
                continue
            raw_rows = _parse_csv_text(result.raw_text)
            if not raw_rows:
                degraded.append(f"{request.download_url}: no CSV rows parsed")
                continue
            rows.extend(normalize_surveillance_rows(raw_rows, request.market, "official", request.download_url, fetched_at))
        return rows, degraded


def _parse_csv_text(text: str) -> list[dict[str, str]]:
    sample = text.lstrip("\ufeff\r\n ")
    if sample.startswith("<"):
        return []
    return list(csv.DictReader(io.StringIO(sample)))

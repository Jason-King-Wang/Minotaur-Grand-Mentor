from __future__ import annotations

import json
from typing import Any

from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.fetchers.http_fetcher import HttpFetcher
from short_term_radar.data_sources.fetchers.twse_institutional_trading_fetcher import (
    canonicalize_institutional_mapping,
    normalize_trade_date,
)


class TpexInstitutionalTradingFetcher:
    def __init__(self, config: dict[str, Any] | None = None):
        self.http = HttpFetcher(config or {})

    def fetch_url(self, url: str, trade_date: str) -> FetchResult:
        result = self.http.fetch_text(url, "official_tpex", "institutional_trading")
        if result.degraded or not result.raw_text:
            return result
        try:
            payload = json.loads(result.raw_text.lstrip("\ufeff"))
        except json.JSONDecodeError as exc:
            return FetchResult(
                "official_tpex",
                "institutional_trading",
                url,
                raw_text=result.raw_text,
                degraded=True,
                message=f"invalid JSON: {exc}",
            )
        rows = parse_tpex_3insti_payload(payload, trade_date)
        if not rows:
            return FetchResult(
                "official_tpex",
                "institutional_trading",
                url,
                raw_text=result.raw_text,
                degraded=True,
                message="no TPEx institutional trading rows parsed",
            )
        return FetchResult("official_tpex", "institutional_trading", url, rows=rows, raw_text=result.raw_text)


def parse_tpex_3insti_payload(payload: Any, trade_date: str) -> list[dict[str, Any]]:
    records = _records_from_payload(payload)
    fallback_date = normalize_trade_date(trade_date)
    rows: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        row = canonicalize_institutional_mapping(record, "TPEX", fallback_date)
        if row.get("symbol"):
            rows.append(row)
    return rows


def _records_from_payload(payload: Any) -> list[Any]:
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "tables", "rows", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]
    return []

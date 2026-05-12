from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from short_term_radar.data_sources.fetchers.http_fetcher import HttpFetcher
from short_term_radar.data_sources.normalizers.common import parse_tw_date
from short_term_radar.data_sources.normalizers.corporate_actions import normalize_corporate_action_rows
from short_term_radar.data_sources.normalizers.institutional_trading import normalize_institutional_trading_rows
from short_term_radar.data_sources.normalizers.margin_short import normalize_margin_short_rows
from short_term_radar.data_sources.normalizers.material_events import normalize_material_event_rows
from short_term_radar.data_sources.normalizers.symbol_master import normalize_symbol_master_rows
from short_term_radar.data_sources.normalizers.valuation import normalize_valuation_rows


@dataclass(frozen=True)
class OfficialRequest:
    dataset: str
    market: str
    endpoint_name: str
    url: str
    date: str | None = None


@dataclass(frozen=True)
class OfficialCollectResult:
    requests: list[OfficialRequest]
    rows: list[dict[str, Any]]
    degraded: list[str]


Normalizer = Callable[[list[dict[str, Any]], str, str, str, Any], list[dict[str, Any]]]


ENDPOINTS: dict[str, dict[str, list[tuple[str, str]]]] = {
    "institutional_trading": {
        "TWSE": [("twse_t86", "https://www.twse.com.tw/rwd/zh/fund/T86?date={date}&selectType=ALLBUT0999&response=json")],
        "TPEX": [("tpex_3insti", "https://www.tpex.org.tw/openapi/v1/tpex_3insti_daily_trading")],
    },
    "margin_short": {
        "TWSE": [
            ("twse_margin", "https://openapi.twse.com.tw/v1/exchangeReport/MI_MARGN"),
            ("twse_sbl", "https://openapi.twse.com.tw/v1/SBL/TWT96U"),
        ],
        "TPEX": [
            ("tpex_margin", "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_margin_balance"),
            ("tpex_sbl", "https://www.tpex.org.tw/openapi/v1/tpex_margin_sbl"),
        ],
    },
    "material_events": {
        "TWSE": [("twse_t187ap04", "https://openapi.twse.com.tw/v1/opendata/t187ap04_L")],
        "TPEX": [("tpex_t187ap04", "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O")],
    },
    "corporate_actions": {
        "TWSE": [
            ("twse_twt48u", "https://openapi.twse.com.tw/v1/exchangeReport/TWT48U_ALL"),
            ("twse_t187ap45", "https://openapi.twse.com.tw/v1/opendata/t187ap45_L"),
        ],
        "TPEX": [
            ("tpex_exright_prepost", "https://www.tpex.org.tw/openapi/v1/tpex_exright_prepost"),
            ("tpex_exright_daily", "https://www.tpex.org.tw/openapi/v1/tpex_exright_daily"),
        ],
    },
    "valuation": {
        "TWSE": [
            ("twse_bwibbu", "https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_d"),
            ("twse_company_profile", "https://openapi.twse.com.tw/v1/opendata/t187ap03_L"),
        ],
        "TPEX": [
            ("tpex_peratio", "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis"),
            ("tpex_market_value", "https://www.tpex.org.tw/openapi/v1/tpex_daily_market_value"),
        ],
    },
    "symbol_master": {
        "TWSE": [("twse_company_profile", "https://openapi.twse.com.tw/v1/opendata/t187ap03_L")],
        "TPEX": [("tpex_company_profile", "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O")],
    },
}


NORMALIZERS: dict[str, Normalizer] = {
    "institutional_trading": normalize_institutional_trading_rows,
    "margin_short": normalize_margin_short_rows,
    "material_events": normalize_material_event_rows,
    "corporate_actions": normalize_corporate_action_rows,
    "valuation": normalize_valuation_rows,
    "symbol_master": normalize_symbol_master_rows,
}


class OfficialOpenDataSource:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.fetcher = HttpFetcher(self.config)

    @staticmethod
    def supported_datasets() -> set[str]:
        return set(ENDPOINTS)

    def build_requests(self, dataset: str, market: str = "all", date: str | None = None) -> list[OfficialRequest]:
        if dataset not in ENDPOINTS:
            raise KeyError(f"Unsupported official dataset: {dataset}")
        markets = ["TWSE", "TPEX"] if market.lower() == "all" else [market.upper()]
        requests: list[OfficialRequest] = []
        for item_market in markets:
            for endpoint_name, url in ENDPOINTS[dataset].get(item_market, []):
                requests.append(OfficialRequest(dataset, item_market, endpoint_name, _render_url(url, date), date))
        return requests

    def collect(self, dataset: str, market: str = "all", date: str | None = None) -> OfficialCollectResult:
        requests = self.build_requests(dataset, market, date)
        fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        rows: list[dict[str, Any]] = []
        degraded: list[str] = []
        normalizer = NORMALIZERS[dataset]
        for request in requests:
            result = self.fetcher.fetch_text(request.url, request.endpoint_name, dataset)
            if result.degraded or not result.raw_text:
                degraded.append(f"{request.url}: {result.message or 'unavailable'}")
                continue
            raw_rows = extract_rows(result.raw_text)
            if not raw_rows:
                degraded.append(f"{request.url}: no parseable rows")
                continue
            contextual_rows = [_with_request_context(row, request) for row in raw_rows]
            normalized = normalizer(contextual_rows, request.market, request.endpoint_name, request.url, fetched_at)
            rows.extend(normalized)
        if dataset == "margin_short":
            rows = _merge_by_key(rows, ("trade_date", "market", "symbol"))
        return OfficialCollectResult(requests, rows, degraded)


def extract_rows(text: str) -> list[dict[str, Any]]:
    sample = text.lstrip("\ufeff\r\n ")
    if not sample:
        return []
    if sample.startswith("<"):
        return []
    if sample[0] in "[{":
        try:
            payload = json.loads(sample)
        except json.JSONDecodeError:
            return []
        return _records_from_payload(payload)
    return list(csv.DictReader(io.StringIO(sample)))


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [_row_from_any(item) for item in payload if _row_from_any(item)]
    if isinstance(payload, dict):
        for key in ("data", "aaData", "rows", "result", "items"):
            rows = _records_from_payload(payload.get(key))
            if rows:
                return rows
        tables = payload.get("tables")
        if isinstance(tables, list):
            rows: list[dict[str, Any]] = []
            for table in tables:
                rows.extend(_records_from_payload(table))
            return rows
        row = _row_from_any(payload)
        return [row] if row else []
    return []


def _row_from_any(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return {str(index): item for index, item in enumerate(value)}
    return {}


def _with_request_context(row: dict[str, Any], request: OfficialRequest) -> dict[str, Any]:
    contextual = dict(row)
    contextual.setdefault("market", request.market)
    if request.date:
        contextual.setdefault("trade_date", request.date)
        contextual.setdefault("action_date", request.date)
    return contextual


def _merge_by_key(rows: list[dict[str, Any]], key_columns: tuple[str, ...]) -> list[dict[str, Any]]:
    merged: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(row.get(column) for column in key_columns)
        current = merged.setdefault(key, {})
        for column, value in row.items():
            if value is not None or column not in current:
                current[column] = value
    return list(merged.values())


def _render_url(url: str, date: str | None) -> str:
    if "{date}" not in url:
        return url
    if not date:
        return url
    parsed = parse_tw_date(date)
    return url.format(date=parsed.strftime("%Y%m%d") if parsed else date)

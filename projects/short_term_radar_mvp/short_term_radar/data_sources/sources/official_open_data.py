from __future__ import annotations

import csv
import io
import json
import re
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
from short_term_radar.data_sources.registry import DATASET_REGISTRY


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
            for endpoint_name, url in self._endpoint_specs(dataset, item_market):
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

    def _endpoint_specs(self, dataset: str, market: str) -> list[tuple[str, str]]:
        default_specs = ENDPOINTS[dataset].get(market, [])
        source_cfg = _source_config_for_market(self.config, market)
        if source_cfg is None:
            return default_specs
        if source_cfg.get("enabled") is False:
            return []

        dataset_cfg = _dataset_config(source_cfg, dataset)
        urls = _configured_api_urls(dataset_cfg)
        if not urls:
            return default_specs

        default_names_by_url = {url: name for name, url in default_specs}
        return [
            (
                default_names_by_url.get(url) or _configured_endpoint_name(market, dataset, index),
                url,
            )
            for index, url in enumerate(urls)
        ]


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
        rows = _records_from_field_payload(payload)
        if rows:
            return rows
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


def _records_from_field_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    fields = _field_names(payload.get("fields") or payload.get("columns"))
    if not fields:
        return []
    for key in ("data", "aaData", "rows"):
        table_rows = payload.get(key)
        if isinstance(table_rows, list):
            rows = [_row_from_fields(fields, item) for item in table_rows]
            return [row for row in rows if row]
    return []


def _field_names(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    names: list[str] = []
    for item in value:
        if isinstance(item, dict):
            name = item.get("name") or item.get("title") or item.get("text") or item.get("key")
        else:
            name = item
        if name is None:
            return []
        names.append(str(name))
    return names


def _row_from_fields(fields: list[str], value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if not isinstance(value, list):
        return {}
    row = {fields[index] if index < len(fields) else str(index): item for index, item in enumerate(value)}
    return row


def _row_from_any(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, list):
        return {str(index): item for index, item in enumerate(value)}
    return {}


def _with_request_context(row: dict[str, Any], request: OfficialRequest) -> dict[str, Any]:
    contextual = _augment_official_row(row, request)
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


def _source_config_for_market(config: dict[str, Any], market: str) -> dict[str, Any] | None:
    source_key = "twse" if market == "TWSE" else "tpex" if market == "TPEX" else ""
    if not source_key:
        return None
    sources = config.get("sources") or {}
    return sources.get(source_key)


def _dataset_config(source_cfg: dict[str, Any], dataset: str) -> dict[str, Any]:
    datasets = source_cfg.get("datasets") or {}
    processed_table = DATASET_REGISTRY[dataset].processed_table if dataset in DATASET_REGISTRY else dataset
    return datasets.get(dataset) or datasets.get(processed_table) or {}


def _configured_api_urls(dataset_cfg: dict[str, Any]) -> list[str]:
    urls: list[str] = []
    api_url = dataset_cfg.get("api_url")
    if api_url:
        urls.append(str(api_url))
    supplemental_urls = dataset_cfg.get("supplemental_api_urls") or []
    urls.extend(str(url) for url in supplemental_urls if url)
    return urls


def _configured_endpoint_name(market: str, dataset: str, index: int) -> str:
    source_key = "twse" if market == "TWSE" else "tpex" if market == "TPEX" else market.lower()
    suffix = "" if index == 0 else f"_supplemental_{index}"
    return f"{source_key}_{dataset}{suffix}"


def _augment_official_row(row: dict[str, Any], request: OfficialRequest) -> dict[str, Any]:
    contextual = dict(row)
    if request.dataset == "margin_short":
        _augment_margin_short_row(contextual)
    return contextual


def _augment_margin_short_row(row: dict[str, Any]) -> None:
    for target, aliases in _MARGIN_SHORT_ALIASES.items():
        _set_canonical_value(row, target, aliases)


def _set_canonical_value(row: dict[str, Any], target: str, aliases: tuple[str, ...]) -> None:
    if _has_value(row.get(target)):
        return
    value = _first_by_alias(row, aliases)
    if _has_value(value):
        row[target] = value


def _first_by_alias(row: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        value = row.get(alias)
        if _has_value(value):
            return value

    compact_row = [(_compact_header(key), value) for key, value in row.items()]
    for alias in aliases:
        compact_alias = _compact_header(alias)
        for key, value in compact_row:
            if (key == compact_alias or key.startswith(compact_alias) or compact_alias in key) and _has_value(value):
                return value
    return None


def _compact_header(value: Any) -> str:
    return re.sub(r"[\s:_\-/()（）]+", "", str(value)).lower()


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in {"", "-", "--", "---", "N/A", "NA", "null", "None"}
    return True


DATE = "\u65e5\u671f"
DATA_DATE = "\u8cc7\u6599\u65e5\u671f"
STOCK = "\u80a1\u7968"
SECURITY = "\u8b49\u5238"
CODE = "\u4ee3\u865f"
NAME = "\u540d\u7a31"
STOCK_NAME = STOCK + "\u540d\u7a31"
MARGIN = "\u878d\u8cc7"
SHORT = "\u878d\u5238"
SBL = "\u501f\u5238"
BUY = "\u8cb7\u9032"
SELL = "\u8ce3\u51fa"
CASH_REPAY = "\u73fe\u91d1\u511f\u9084"
CASH_REPAY_SHORT = "\u73fe\u511f"
SECURITY_REPAY = "\u73fe\u5238\u511f\u9084"
BALANCE = "\u9918\u984d"
PREV = "\u524d\u65e5"
TODAY = "\u4eca\u65e5"
LIMIT = "\u9650\u984d"
DEAL = "\u6210\u4ea4"
QUANTITY = "\u6578\u91cf"

_MARGIN_SHORT_ALIASES: dict[str, tuple[str, ...]] = {
    "trade_date": ("trade_date", DATE, DATA_DATE),
    "symbol": ("symbol", STOCK + CODE, SECURITY + CODE, CODE),
    "name": ("name", STOCK_NAME, NAME),
    "margin_buy": ("margin_buy", MARGIN + BUY),
    "margin_sell": ("margin_sell", MARGIN + SELL),
    "margin_redeem": ("margin_redeem", MARGIN + CASH_REPAY, MARGIN + CASH_REPAY_SHORT),
    "margin_balance": ("margin_balance", MARGIN + TODAY + BALANCE, MARGIN + BALANCE),
    "margin_balance_prev": ("margin_balance_prev", MARGIN + PREV + BALANCE),
    "short_sell": ("short_sell", SHORT + SELL),
    "short_cover": ("short_cover", SHORT + BUY),
    "short_redeem": ("short_redeem", SHORT + SECURITY_REPAY, SHORT + CASH_REPAY_SHORT),
    "short_balance": ("short_balance", SHORT + TODAY + BALANCE, SHORT + BALANCE),
    "short_balance_prev": ("short_balance_prev", SHORT + PREV + BALANCE),
    "sbl_short_sell_volume": ("sbl_short_sell_volume", SBL + SELL + DEAL + QUANTITY),
    "sbl_balance": ("sbl_balance", SBL + BALANCE),
    "sbl_short_sell_balance": ("sbl_short_sell_balance", SBL + SELL + BALANCE),
    "margin_limit_code": ("margin_limit_code", MARGIN + LIMIT),
    "short_limit_code": ("short_limit_code", SHORT + LIMIT),
}

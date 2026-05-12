from __future__ import annotations

import json
from typing import Any

from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.fetchers.http_fetcher import HttpFetcher
from short_term_radar.data_sources.normalizers.common import parse_number_zh_tw, parse_tw_date


BUY = "\u8cb7\u9032"
SELL = "\u8ce3\u51fa"
NET = "\u8cb7\u8ce3\u8d85"
SECURITIES_CODE = "\u8b49\u5238\u4ee3\u865f"
SECURITIES_NAME = "\u8b49\u5238\u540d\u7a31"
CODE = "\u4ee3\u865f"
NAME = "\u540d\u7a31"
TRADE_DATE = "\u65e5\u671f"
FOREIGN_MAIN = "\u5916\u9678\u8cc7"
FOREIGN_ALT = "\u5916\u8cc7\u53ca\u9678\u8cc7"
FOREIGN_GENERIC = "\u5916\u8cc7"
INVESTMENT_TRUST = "\u6295\u4fe1"
DEALER = "\u81ea\u71df\u5546"
SELF_DEALING = "\u81ea\u884c\u8cb7\u8ce3"
HEDGE = "\u907f\u96aa"
TOTAL_INSTITUTIONAL = "\u4e09\u5927\u6cd5\u4eba"


class TwseInstitutionalTradingFetcher:
    def __init__(self, config: dict[str, Any] | None = None):
        self.http = HttpFetcher(config or {})

    def build_url(self, api_url_template: str, trade_date: str) -> str:
        return api_url_template.format(date=compact_trade_date(trade_date))

    def fetch_url(self, url: str, trade_date: str) -> FetchResult:
        result = self.http.fetch_text(url, "official_twse", "institutional_trading")
        if result.degraded or not result.raw_text:
            return result
        try:
            payload = json.loads(result.raw_text.lstrip("\ufeff"))
        except json.JSONDecodeError as exc:
            return FetchResult(
                "official_twse",
                "institutional_trading",
                url,
                raw_text=result.raw_text,
                degraded=True,
                message=f"invalid JSON: {exc}",
            )
        rows = parse_twse_t86_payload(payload, trade_date)
        if not rows:
            return FetchResult(
                "official_twse",
                "institutional_trading",
                url,
                raw_text=result.raw_text,
                degraded=True,
                message="no TWSE T86 rows parsed",
            )
        return FetchResult("official_twse", "institutional_trading", url, rows=rows, raw_text=result.raw_text)


def parse_twse_t86_payload(payload: Any, trade_date: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []

    payload_date = normalize_trade_date(payload.get("date") or trade_date)
    fields = [str(field) for field in payload.get("fields") or []]
    data = payload.get("data") or payload.get("aaData") or []
    rows: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            row = canonicalize_institutional_mapping(item, "TWSE", payload_date)
        elif isinstance(item, (list, tuple)):
            row = _canonicalize_twse_cells(fields, list(item), payload_date)
        else:
            continue
        if row.get("symbol"):
            rows.append(row)
    return rows


def canonicalize_institutional_mapping(mapping: dict[str, Any], market: str, fallback_trade_date: str) -> dict[str, Any]:
    trade_date = normalize_trade_date(_first_exact(mapping, "trade_date", "date", TRADE_DATE) or fallback_trade_date)
    dealer_self_buy = _value_by_terms(mapping, ((DEALER,), (SELF_DEALING,), (BUY,)))
    dealer_self_sell = _value_by_terms(mapping, ((DEALER,), (SELF_DEALING,), (SELL,)))
    dealer_self_net = _value_by_terms(mapping, ((DEALER,), (SELF_DEALING,), (NET,)))
    dealer_hedge_buy = _value_by_terms(mapping, ((DEALER,), (HEDGE,), (BUY,)))
    dealer_hedge_sell = _value_by_terms(mapping, ((DEALER,), (HEDGE,), (SELL,)))
    dealer_hedge_net = _value_by_terms(mapping, ((DEALER,), (HEDGE,), (NET,)))
    dealer_buy = _first_not_none(
        _value_by_terms(
            mapping,
            ((DEALER,), (BUY,)),
            excludes=(SELF_DEALING, HEDGE, FOREIGN_ALT, FOREIGN_MAIN, FOREIGN_GENERIC),
        ),
        _sum_values(dealer_self_buy, dealer_hedge_buy),
    )
    dealer_sell = _first_not_none(
        _value_by_terms(
            mapping,
            ((DEALER,), (SELL,)),
            excludes=(SELF_DEALING, HEDGE, FOREIGN_ALT, FOREIGN_MAIN, FOREIGN_GENERIC),
        ),
        _sum_values(dealer_self_sell, dealer_hedge_sell),
    )
    dealer_net = _first_not_none(
        _value_by_terms(
            mapping,
            ((DEALER,), (NET,)),
            excludes=(SELF_DEALING, HEDGE, FOREIGN_ALT, FOREIGN_MAIN, FOREIGN_GENERIC),
        ),
        _sum_values(dealer_self_net, dealer_hedge_net),
    )
    return {
        "trade_date": trade_date,
        "market": market,
        "symbol": _first_exact(mapping, "symbol", "stock_id", "code", SECURITIES_CODE, CODE),
        "name": _first_exact(mapping, "name", "stock_name", SECURITIES_NAME, NAME),
        "foreign_buy": _value_by_terms(mapping, ((FOREIGN_MAIN, FOREIGN_ALT), (BUY,))),
        "foreign_sell": _value_by_terms(mapping, ((FOREIGN_MAIN, FOREIGN_ALT), (SELL,))),
        "foreign_net": _value_by_terms(mapping, ((FOREIGN_MAIN, FOREIGN_ALT), (NET,))),
        "investment_trust_buy": _value_by_terms(mapping, ((INVESTMENT_TRUST,), (BUY,))),
        "investment_trust_sell": _value_by_terms(mapping, ((INVESTMENT_TRUST,), (SELL,))),
        "investment_trust_net": _value_by_terms(mapping, ((INVESTMENT_TRUST,), (NET,))),
        "dealer_buy": dealer_buy,
        "dealer_sell": dealer_sell,
        "dealer_net": dealer_net,
        "dealer_self_buy": dealer_self_buy,
        "dealer_self_sell": dealer_self_sell,
        "dealer_self_net": dealer_self_net,
        "dealer_hedge_buy": dealer_hedge_buy,
        "dealer_hedge_sell": dealer_hedge_sell,
        "dealer_hedge_net": dealer_hedge_net,
        "total_institutional_net": _value_by_terms(mapping, ((TOTAL_INSTITUTIONAL,), (NET,))),
    }


def normalize_trade_date(value: Any) -> str:
    parsed = parse_tw_date(value)
    if parsed is None:
        raise ValueError(f"Bad institutional trading date: {value}")
    return parsed.isoformat()


def compact_trade_date(value: Any) -> str:
    parsed = parse_tw_date(value)
    if parsed is None:
        raise ValueError(f"Bad institutional trading date: {value}")
    return parsed.strftime("%Y%m%d")


def _canonicalize_twse_cells(fields: list[str], cells: list[Any], trade_date: str) -> dict[str, Any]:
    if fields:
        mapping = {fields[index]: cells[index] for index in range(min(len(fields), len(cells)))}
        return canonicalize_institutional_mapping(mapping, "TWSE", trade_date)

    values = [*cells, *([None] * max(0, 19 - len(cells)))]
    dealer_self_buy = values[12]
    dealer_self_sell = values[13]
    dealer_self_net = values[14]
    dealer_hedge_buy = values[15]
    dealer_hedge_sell = values[16]
    dealer_hedge_net = values[17]
    return {
        "trade_date": trade_date,
        "market": "TWSE",
        "symbol": values[0],
        "name": values[1],
        "foreign_buy": values[2],
        "foreign_sell": values[3],
        "foreign_net": values[4],
        "investment_trust_buy": values[8],
        "investment_trust_sell": values[9],
        "investment_trust_net": values[10],
        "dealer_buy": _sum_values(dealer_self_buy, dealer_hedge_buy),
        "dealer_sell": _sum_values(dealer_self_sell, dealer_hedge_sell),
        "dealer_net": values[11] or _sum_values(dealer_self_net, dealer_hedge_net),
        "dealer_self_buy": dealer_self_buy,
        "dealer_self_sell": dealer_self_sell,
        "dealer_self_net": dealer_self_net,
        "dealer_hedge_buy": dealer_hedge_buy,
        "dealer_hedge_sell": dealer_hedge_sell,
        "dealer_hedge_net": dealer_hedge_net,
        "total_institutional_net": values[18],
    }


def _first_exact(mapping: dict[str, Any], *aliases: str) -> Any:
    cleaned = {_clean_header(key): value for key, value in mapping.items()}
    for alias in aliases:
        value = cleaned.get(_clean_header(alias))
        if value is not None and value != "":
            return value
    return None


def _value_by_terms(
    mapping: dict[str, Any],
    include_groups: tuple[tuple[str, ...], ...],
    excludes: tuple[str, ...] = (),
) -> Any:
    for key, value in mapping.items():
        header = _clean_header(key)
        if not header:
            continue
        if any(_clean_header(term) in header for term in excludes):
            continue
        if all(any(_clean_header(term) in header for term in group) for group in include_groups):
            return value
    return None


def _clean_header(value: Any) -> str:
    return str(value).strip().replace(" ", "").replace("\u3000", "").replace("-", "")


def _sum_values(*values: Any) -> float | None:
    parsed = [parse_number_zh_tw(value) for value in values]
    available = [value for value in parsed if value is not None]
    if not available:
        return None
    return float(sum(available))


def _first_not_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None

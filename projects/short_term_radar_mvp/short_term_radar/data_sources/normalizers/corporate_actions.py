from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
)


def normalize_corporate_action_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        action_type = _classify_action(row)
        normalized.append(
            {
                "action_date": iso_date(first_value(row, "除權息日期", "停止過戶起始日期", "日期", "action_date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "股票代號", "證券代號", "代號", "symbol")),
                "name": first_value(row, "股票名稱", "證券名稱", "名稱", "name"),
                "action_type": action_type,
                "cash_dividend": parse_number_zh_tw(first_value(row, "現金股利", "cash_dividend")),
                "stock_dividend_ratio": parse_number_zh_tw(first_value(row, "股票股利", "stock_dividend_ratio")),
                "capital_increase_ratio": parse_number_zh_tw(first_value(row, "增資配股率", "capital_increase_ratio")),
                "subscription_price": parse_number_zh_tw(first_value(row, "承銷價", "認購價", "subscription_price")),
                "reference_price": parse_number_zh_tw(first_value(row, "除權息參考價", "reference_price")),
                "previous_close": parse_number_zh_tw(first_value(row, "前日收盤價", "previous_close")),
                "right_value": parse_number_zh_tw(first_value(row, "權值", "right_value")),
                "interest_value": parse_number_zh_tw(first_value(row, "息值", "interest_value")),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["action_date"] and row["symbol"]]


def _classify_action(row: dict[str, Any]) -> str:
    text = " ".join(str(value) for value in row.values())
    if "減資" in text:
        return "reduction"
    if "增資" in text:
        return "capital_increase"
    if "除權" in text and "除息" in text:
        return "ex_right_dividend"
    if "除權" in text:
        return "ex_right"
    if "除息" in text or "現金股利" in text:
        return "ex_dividend"
    if "分割" in text:
        return "split"
    return "unknown"

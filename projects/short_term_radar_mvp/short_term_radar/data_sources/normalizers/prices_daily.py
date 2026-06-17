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


def normalize_prices_daily_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized.append(
            {
                "trade_date": iso_date(first_value(row, "日期", "資料日期", "trade_date", "date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "證券代號", "股票代號", "代號", "symbol", "stock_id")),
                "name": first_value(row, "證券名稱", "名稱", "name"),
                "open": parse_number_zh_tw(first_value(row, "開盤價", "開盤", "open")),
                "high": parse_number_zh_tw(first_value(row, "最高價", "最高", "high")),
                "low": parse_number_zh_tw(first_value(row, "最低價", "最低", "low")),
                "close": parse_number_zh_tw(first_value(row, "收盤價", "收盤", "close")),
                "change": parse_number_zh_tw(first_value(row, "漲跌價差", "漲跌", "change")),
                "volume": parse_number_zh_tw(first_value(row, "成交股數", "成交股數 ", "volume")),
                "amount": parse_number_zh_tw(first_value(row, "成交金額", "amount")),
                "transactions": parse_number_zh_tw(first_value(row, "成交筆數", "transactions")),
                "issued_shares": parse_number_zh_tw(first_value(row, "發行股數", "issued_shares")),
                "next_limit_up": parse_number_zh_tw(first_value(row, "次日漲停價", "next_limit_up")),
                "next_limit_down": parse_number_zh_tw(first_value(row, "次日跌停價", "next_limit_down")),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["trade_date"] and row["symbol"]]

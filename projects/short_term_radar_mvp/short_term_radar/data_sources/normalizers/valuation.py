from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
    parse_percent,
)


def normalize_valuation_rows(
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
                "trade_date": iso_date(first_value(row, "資料日期", "日期", "trade_date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "股票代號", "證券代號", "代號", "symbol")),
                "name": first_value(row, "名稱", "證券名稱", "name"),
                "close": parse_number_zh_tw(first_value(row, "收盤價", "close")),
                "pe": parse_number_zh_tw(first_value(row, "本益比", "pe")),
                "pb": parse_number_zh_tw(first_value(row, "股價淨值比", "pb")),
                "dividend_yield": parse_percent(first_value(row, "殖利率", "dividend_yield")),
                "dividend_per_share": parse_number_zh_tw(first_value(row, "每股股利", "dividend_per_share")),
                "financial_year_quarter": first_value(row, "財報年/季", "financial_year_quarter"),
                "market_cap": parse_number_zh_tw(first_value(row, "市值", "market_cap")),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["trade_date"] and row["symbol"]]

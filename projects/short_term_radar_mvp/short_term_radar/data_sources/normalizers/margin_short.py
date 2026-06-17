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


def normalize_margin_short_rows(
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
                "trade_date": iso_date(first_value(row, "日期", "資料日期", "trade_date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "證券代號", "股票代號", "代號", "symbol")),
                "name": first_value(row, "證券名稱", "名稱", "name"),
                "margin_buy": parse_number_zh_tw(first_value(row, "今日融資買進", "融資買進", "margin_buy")),
                "margin_sell": parse_number_zh_tw(first_value(row, "今日融資賣出", "融資賣出", "margin_sell")),
                "margin_redeem": parse_number_zh_tw(first_value(row, "今日現金償還", "現金償還", "margin_redeem")),
                "margin_balance": parse_number_zh_tw(first_value(row, "今日融資餘額", "融資餘額", "margin_balance")),
                "margin_balance_prev": parse_number_zh_tw(first_value(row, "昨日融資餘額", "margin_balance_prev")),
                "short_sell": parse_number_zh_tw(first_value(row, "今日融券賣出", "融券賣出", "short_sell")),
                "short_cover": parse_number_zh_tw(first_value(row, "今日融券買進", "融券買進", "short_cover")),
                "short_redeem": parse_number_zh_tw(first_value(row, "今日現券償還", "現券償還", "short_redeem")),
                "short_balance": parse_number_zh_tw(first_value(row, "今日融券餘額", "融券餘額", "short_balance")),
                "short_balance_prev": parse_number_zh_tw(first_value(row, "昨日融券餘額", "short_balance_prev")),
                "short_margin_ratio": parse_percent(first_value(row, "券資比", "short_margin_ratio")),
                "sbl_short_sell_volume": parse_number_zh_tw(first_value(row, "借券賣出股數", "sbl_short_sell_volume")),
                "sbl_balance": parse_number_zh_tw(first_value(row, "借券餘額", "sbl_balance")),
                "sbl_short_sell_balance": parse_number_zh_tw(first_value(row, "借券賣出餘額", "sbl_short_sell_balance")),
                "margin_limit_code": first_value(row, "融資限制碼", "margin_limit_code"),
                "short_limit_code": first_value(row, "融券限制碼", "short_limit_code"),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["trade_date"] and row["symbol"]]

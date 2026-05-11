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


def normalize_symbol_master_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    market_value = normalize_market(market)
    for row in rows:
        symbol = normalize_symbol(first_value(row, "公司代號", "股票代號", "證券代號", "代號", "symbol", "stock_id"))
        name = first_value(row, "公司名稱", "證券名稱", "名稱", "name", "stock_name") or ""
        short_name = first_value(row, "公司簡稱", "簡稱", "short_name", "stock_name")
        listing_date = first_value(row, "上市日期", "上櫃日期", "掛牌日期", "listing_date", "listed_date")
        text_blob = " ".join(str(value) for value in row.values())
        instrument_type = str(first_value(row, "instrument_type") or "").upper()
        normalized.append(
            {
                "symbol": symbol,
                "name": str(name),
                "short_name": str(short_name) if short_name is not None else None,
                "market": normalize_market(first_value(row, "市場", "market") or market_value),
                "industry": first_value(row, "產業別", "industry"),
                "listing_date": iso_date(listing_date),
                "established_date": iso_date(first_value(row, "成立日期", "established_date")),
                "paid_in_capital": parse_number_zh_tw(first_value(row, "實收資本額", "paid_in_capital")),
                "issued_shares": parse_number_zh_tw(
                    first_value(row, "已發行普通股數或TDR原股發行股數", "已發行普通股數", "issued_shares")
                ),
                "par_value": first_value(row, "普通股每股面額", "par_value"),
                "foreign_registration_country": first_value(row, "外國企業註冊地國", "foreign_registration_country"),
                "is_ky": "-KY" in str(short_name or name).upper(),
                "is_etf": "ETF" in text_blob.upper() or instrument_type == "ETF",
                "is_warrant": "權證" in text_blob or instrument_type == "WARRANT",
                "is_etn": "ETN" in text_blob.upper() or instrument_type == "ETN",
                "is_tdr": "TDR" in text_blob.upper() or instrument_type == "TDR",
                "is_common_stock": instrument_type in {"COMMON_STOCK", "STOCK"}
                or not any(token in text_blob.upper() for token in ["ETF", "ETN", "TDR"])
                and "權證" not in text_blob,
                "is_full_delivery": None,
                "is_attention": None,
                "is_disposition": None,
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["symbol"]]

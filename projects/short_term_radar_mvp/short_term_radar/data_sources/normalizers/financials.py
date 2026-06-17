from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
    safe_int,
)


def normalize_financial_statement_rows(
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
                "year": safe_int(first_value(row, "年度", "year")),
                "quarter": safe_int(first_value(row, "季別", "quarter")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "公司代號", "股票代號", "symbol")),
                "name": first_value(row, "公司名稱", "name") or "",
                "industry_type": first_value(row, "業別", "industry_type"),
                "announce_date": iso_date(first_value(row, "公告日期", "announce_date")),
                "revenue": parse_number_zh_tw(first_value(row, "營業收入", "revenue")),
                "cost": parse_number_zh_tw(first_value(row, "營業成本", "cost")),
                "gross_profit": parse_number_zh_tw(first_value(row, "營業毛利", "gross_profit")),
                "gross_margin": parse_number_zh_tw(first_value(row, "毛利率", "gross_margin")),
                "operating_expense": parse_number_zh_tw(first_value(row, "營業費用", "operating_expense")),
                "operating_profit": parse_number_zh_tw(first_value(row, "營業利益", "operating_profit")),
                "operating_margin": parse_number_zh_tw(first_value(row, "營益率", "operating_margin")),
                "pretax_income": parse_number_zh_tw(first_value(row, "稅前淨利", "pretax_income")),
                "net_income": parse_number_zh_tw(first_value(row, "本期淨利", "net_income")),
                "eps": parse_number_zh_tw(first_value(row, "每股盈餘", "eps")),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["year"] and row["quarter"] and row["symbol"]]

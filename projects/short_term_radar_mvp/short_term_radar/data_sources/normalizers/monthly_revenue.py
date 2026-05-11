from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    next_month_day_10,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
    parse_percent,
    parse_tw_month,
)


def normalize_monthly_revenue_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    fetched_text = fetched_at_text(fetched_at)
    for row in rows:
        revenue_month = parse_tw_month(first_value(row, "資料年月", "營收年月", "revenue_month"))
        announce_date = iso_date(first_value(row, "出表日期", "公告日期", "announce_date"))
        announce_date_source = first_value(row, "announce_date_source")
        announce_date_inferred = False
        if not announce_date:
            announce_date = next_month_day_10(revenue_month)
            announce_date_inferred = bool(announce_date)
            announce_date_source = "inferred_next_month_day_10" if announce_date_inferred else announce_date_source
        elif not announce_date_source:
            announce_date_source = "official" if source == "official_mops" else "manual"
        normalized.append(
            {
                "revenue_month": revenue_month,
                "announce_date": announce_date,
                "announce_date_source": announce_date_source,
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "公司代號", "股票代號", "證券代號", "symbol")),
                "name": first_value(row, "公司名稱", "證券名稱", "name") or "",
                "industry": first_value(row, "產業別", "industry"),
                "revenue_current": parse_number_zh_tw(first_value(row, "營業收入-當月營收", "當月營收", "revenue_current")),
                "revenue_previous_month": parse_number_zh_tw(
                    first_value(row, "營業收入-上月營收", "上月營收", "revenue_previous_month")
                ),
                "revenue_last_year_same_month": parse_number_zh_tw(
                    first_value(row, "營業收入-去年當月營收", "去年當月營收", "revenue_last_year_same_month")
                ),
                "revenue_mom_pct": parse_percent(
                    first_value(row, "營業收入-上月比較增減(%)", "上月比較增減(%)", "revenue_mom_pct")
                ),
                "revenue_yoy_pct": parse_percent(
                    first_value(row, "營業收入-去年同月增減(%)", "去年同月增減(%)", "revenue_yoy_pct")
                ),
                "cumulative_revenue_current": parse_number_zh_tw(
                    first_value(row, "累計營業收入-當月累計營收", "當月累計營收", "cumulative_revenue_current")
                ),
                "cumulative_revenue_last_year": parse_number_zh_tw(
                    first_value(row, "累計營業收入-去年累計營收", "去年累計營收", "cumulative_revenue_last_year")
                ),
                "cumulative_yoy_pct": parse_percent(
                    first_value(row, "累計營業收入-前期比較增減(%)", "前期比較增減(%)", "cumulative_yoy_pct")
                ),
                "note": first_value(row, "備註", "note"),
                "announce_date_inferred": bool(row.get("announce_date_inferred", announce_date_inferred)),
                "company_type": first_value(row, "company_type"),
                "raw_market_section": first_value(row, "raw_market_section"),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_text,
            }
        )
    return [row for row in normalized if row["revenue_month"] and row["symbol"]]


def filter_available_revenue(rows: list[dict[str, Any]], as_of_date: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("announce_date") and str(row["announce_date"]) <= as_of_date]

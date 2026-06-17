from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
    parse_percent,
    parse_tw_month,
)


def normalize_insider_holding_rows(
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
                "data_month": parse_tw_month(first_value(row, "資料年月", "data_month")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "公司代號", "股票代號", "symbol")),
                "name": first_value(row, "公司名稱", "name") or "",
                "title": first_value(row, "職稱", "title"),
                "insider_name": first_value(row, "姓名", "insider_name"),
                "shares_at_election": parse_number_zh_tw(first_value(row, "選任時持股", "shares_at_election")),
                "current_holding": parse_number_zh_tw(first_value(row, "目前持股", "current_holding")),
                "pledged_shares": parse_number_zh_tw(first_value(row, "設質股數", "pledged_shares")),
                "pledge_ratio": parse_percent(first_value(row, "設質比率", "pledge_ratio")),
                "related_party_holding": parse_number_zh_tw(first_value(row, "關係人持股", "related_party_holding")),
                "related_party_pledged_shares": parse_number_zh_tw(
                    first_value(row, "關係人設質股數", "related_party_pledged_shares")
                ),
                "related_party_pledge_ratio": parse_percent(
                    first_value(row, "關係人設質比率", "related_party_pledge_ratio")
                ),
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["data_month"] and row["symbol"]]

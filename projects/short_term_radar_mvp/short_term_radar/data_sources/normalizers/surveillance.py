from __future__ import annotations

import re
from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
    parse_number_zh_tw,
)


def normalize_surveillance_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        range_text = first_value(row, "處置起訖時間", "處置期間", "disposition_period")
        start, end = _parse_date_range(range_text)
        disposition_flag = bool(range_text or first_value(row, "處置原因", "處置內容", "disposition_reason"))
        attention_reason = first_value(row, "注意交易資訊", "注意原因", "attention_reason")
        normalized.append(
            {
                "trade_date": iso_date(first_value(row, "公告日期", "公布日期", "日期", "trade_date")),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "證券代號", "股票代號", "代號", "symbol")),
                "name": first_value(row, "證券名稱", "名稱", "name"),
                "attention_flag": bool(attention_reason) and not disposition_flag,
                "attention_reason": attention_reason,
                "attention_close": parse_number_zh_tw(first_value(row, "收盤價", "attention_close")),
                "attention_pe": parse_number_zh_tw(first_value(row, "本益比", "attention_pe")),
                "disposition_flag": disposition_flag,
                "disposition_start": start,
                "disposition_end": end,
                "disposition_condition": first_value(row, "條件", "disposition_condition"),
                "disposition_reason": first_value(row, "處置原因", "disposition_reason") or attention_reason,
                "disposition_measure": first_value(row, "處置內容", "處置措施", "disposition_measure"),
                "attention_count_recent": None,
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["trade_date"] and row["symbol"]]


def _parse_date_range(value: Any) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    parts = re.split(r"[~～至起迄-]+", str(value))
    dates = [iso_date(part.strip()) for part in parts if iso_date(part.strip())]
    if not dates:
        return None, None
    if len(dates) == 1:
        return dates[0], dates[0]
    return dates[0], dates[-1]


def is_active_disposition(row: dict[str, Any], as_of_date: str) -> bool:
    if not row.get("disposition_flag"):
        return False
    start = row.get("disposition_start") or row.get("trade_date")
    end = row.get("disposition_end") or start
    return bool(start and end and str(start) <= as_of_date <= str(end))

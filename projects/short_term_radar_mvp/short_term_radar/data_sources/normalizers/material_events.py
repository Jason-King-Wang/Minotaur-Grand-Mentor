from __future__ import annotations

from typing import Any

from short_term_radar.data_sources.normalizers.common import (
    fetched_at_text,
    first_value,
    iso_date,
    normalize_market,
    normalize_symbol,
)

POSITIVE_EVENT_TYPES = {
    "investor_conference",
    "monthly_revenue",
    "earnings_release",
    "major_order",
    "new_product",
    "capacity_expansion",
    "customer_supply_chain",
    "strategic_alliance",
    "merger_acquisition",
    "share_buyback",
    "dividend",
}

RISK_EVENT_TYPES = {
    "capital_increase",
    "lawsuit",
    "production_halt",
    "regulatory_penalty",
    "financial_warning",
}

KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("investor_conference", ("法說", "法人說明", "業績發表")),
    ("monthly_revenue", ("月營收", "營收")),
    ("earnings_release", ("財報", "獲利", "每股盈餘", "EPS")),
    ("major_order", ("大單", "訂單", "合約", "標案")),
    ("new_product", ("新產品", "量產", "新品")),
    ("capacity_expansion", ("擴產", "產能", "新廠")),
    ("customer_supply_chain", ("供應鏈", "客戶", "認證")),
    ("strategic_alliance", ("策略聯盟", "合作", "合資")),
    ("merger_acquisition", ("併購", "收購", "合併")),
    ("capital_increase", ("現金增資", "私募", "發行新股")),
    ("share_buyback", ("庫藏股", "買回股份")),
    ("dividend", ("股利", "配息", "配股")),
    ("lawsuit", ("訴訟", "仲裁")),
    ("production_halt", ("停工", "停產", "火災")),
    ("regulatory_penalty", ("裁罰", "罰鍰", "處分")),
    ("financial_warning", ("虧損", "減損", "債務", "跳票", "警示")),
]


def classify_material_event(title: str, description: str | None = None) -> str:
    text = f"{title or ''} {description or ''}".upper()
    for event_type, keywords in KEYWORDS:
        if any(keyword.upper() in text for keyword in keywords):
            return event_type
    return "other"


def normalize_material_event_rows(
    rows: list[dict[str, Any]],
    market: str,
    source: str,
    source_url: str,
    fetched_at: Any = None,
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        title = str(first_value(row, "主旨", "標題", "title") or "")
        description = first_value(row, "說明", "內容", "description")
        event_type = classify_material_event(title, str(description or ""))
        normalized.append(
            {
                "announce_date": iso_date(first_value(row, "公告日期", "發言日期", "announce_date")),
                "announce_time": first_value(row, "公告時間", "發言時間", "announce_time"),
                "market": normalize_market(first_value(row, "市場", "market") or market),
                "symbol": normalize_symbol(first_value(row, "公司代號", "股票代號", "證券代號", "symbol")),
                "name": first_value(row, "公司名稱", "證券名稱", "name") or "",
                "title": title,
                "rule_clause": first_value(row, "法條款", "rule_clause"),
                "event_date": iso_date(first_value(row, "事件日期", "event_date")),
                "description": description,
                "event_type": event_type,
                "catalyst_score": 10.0 if event_type in POSITIVE_EVENT_TYPES else 0.0,
                "risk_score": 10.0 if event_type in RISK_EVENT_TYPES else 0.0,
                "source": source,
                "source_url": source_url,
                "fetched_at": fetched_at_text(fetched_at),
            }
        )
    return [row for row in normalized if row["announce_date"] and row["symbol"] and row["title"]]

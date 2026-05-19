from __future__ import annotations

TPEX_DATASETS = {
    "prices_daily": "https://data.gov.tw/dataset/11371",
    "symbol_master": "https://data.gov.tw/dataset/25036",
    "monthly_revenue": "https://data.gov.tw/dataset/56510",
    "material_events": "https://data.gov.tw/dataset/18418",
    "attention": "https://data.gov.tw/dataset/11395",
    "disposition": "https://data.gov.tw/dataset/11396",
    "corporate_actions": "https://data.gov.tw/dataset/11633",
    "insider_holding": "https://data.gov.tw/dataset/22812",
    "valuation": "https://data.gov.tw/dataset/11373",
}


def source_url(dataset: str) -> str | None:
    return TPEX_DATASETS.get(dataset)

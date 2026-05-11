from __future__ import annotations

TWSE_DATASETS = {
    "prices_daily": "https://data.gov.tw/dataset/11549",
    "symbol_master": "https://data.gov.tw/dataset/18419",
    "monthly_revenue": "https://data.gov.tw/dataset/18420",
    "material_events": "https://data.gov.tw/en/datasets/18415",
    "corporate_actions": "https://data.gov.tw/dataset/89748",
    "insider_holding": "https://data.gov.tw/dataset/22811",
    "valuation": "https://data.gov.tw/dataset/11764",
}


def source_url(dataset: str) -> str | None:
    return TWSE_DATASETS.get(dataset)

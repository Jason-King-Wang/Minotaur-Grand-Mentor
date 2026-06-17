from __future__ import annotations

MOPS_DATASETS = {
    "material_events": "https://mops.twse.com.tw",
    "financial_statement": "https://mops.twse.com.tw",
}


def source_url(dataset: str) -> str | None:
    return MOPS_DATASETS.get(dataset)

from __future__ import annotations

TWSE_ESHOP_DATASETS = {
    "institutional_trading": "https://eshop.twse.com.tw/zh/product/detail/010ebd2cdb854169bb8707378f75b12a",
    "margin_short": "https://eshop.twse.com.tw/zh/product/detail/388dd3a09824427d8c01a9d2b21e820b",
    "surveillance": "https://eshop.twse.com.tw/zh/product/detail/ac35dc52883d42c1a2eeacfa332f7e7f",
}


def source_url(dataset: str) -> str | None:
    return TWSE_ESHOP_DATASETS.get(dataset)

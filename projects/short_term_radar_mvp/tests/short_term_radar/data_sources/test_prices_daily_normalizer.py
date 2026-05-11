from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.prices_daily import normalize_prices_daily_rows


def test_prices_daily_normalizer_handles_commas_and_roc_dates():
    rows = LocalFileFetcher().fetch_csv(Path("tests/fixtures/twse_prices_daily_sample.csv"), "twse", "prices_daily").rows

    normalized = normalize_prices_daily_rows(rows, "TWSE", "twse", "https://data.gov.tw/dataset/11549", "2026-05-11T00:00:00")

    assert normalized[0]["trade_date"] == "2026-05-11"
    assert normalized[0]["volume"] == 10000
    assert normalized[0]["close"] == 905

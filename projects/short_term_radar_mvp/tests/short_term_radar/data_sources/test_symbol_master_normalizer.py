from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.symbol_master import normalize_symbol_master_rows


def test_symbol_master_normalizer_handles_twse_fields():
    fixture = Path("tests/fixtures/twse_symbol_master_sample.csv")
    rows = LocalFileFetcher().fetch_csv(fixture, "twse", "symbol_master").rows

    normalized = normalize_symbol_master_rows(rows, "TWSE", "twse", "https://data.gov.tw/dataset/18419", "2026-05-11T00:00:00")

    assert normalized[0]["symbol"] == "2330"
    assert normalized[0]["market"] == "TWSE"
    assert normalized[0]["listing_date"] == "1994-09-05"
    assert normalized[0]["issued_shares"] == 25_930_380_580

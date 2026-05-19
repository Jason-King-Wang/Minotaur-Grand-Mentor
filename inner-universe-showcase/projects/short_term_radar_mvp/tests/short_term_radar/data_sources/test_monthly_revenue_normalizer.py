from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.monthly_revenue import normalize_monthly_revenue_rows


def test_monthly_revenue_normalizer_sets_announce_date_and_month():
    rows = LocalFileFetcher().fetch_csv(Path("tests/fixtures/twse_monthly_revenue_sample.csv"), "twse", "monthly_revenue").rows

    normalized = normalize_monthly_revenue_rows(rows, "TWSE", "twse", "https://data.gov.tw/dataset/18420", "2026-05-11T00:00:00")

    assert normalized[0]["revenue_month"] == "202604"
    assert normalized[0]["announce_date"] == "2026-05-10"
    assert normalized[0]["revenue_yoy_pct"] == 31.12

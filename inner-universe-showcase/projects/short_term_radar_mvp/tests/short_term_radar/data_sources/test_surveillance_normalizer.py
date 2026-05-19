from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.surveillance import is_active_disposition, normalize_surveillance_rows


def test_surveillance_normalizer_marks_active_disposition():
    rows = LocalFileFetcher().fetch_csv(Path("tests/fixtures/tpex_disposition_sample.csv"), "tpex", "surveillance").rows

    normalized = normalize_surveillance_rows(rows, "TPEX", "tpex", "https://data.gov.tw/dataset/11396", "2026-05-11T00:00:00")

    assert normalized[0]["disposition_flag"] is True
    assert normalized[0]["disposition_start"] == "2026-05-12"
    assert is_active_disposition(normalized[0], "2026-05-15") is True

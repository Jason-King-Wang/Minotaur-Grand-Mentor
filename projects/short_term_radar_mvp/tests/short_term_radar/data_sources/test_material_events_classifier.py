from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.local_file_fetcher import LocalFileFetcher
from short_term_radar.data_sources.normalizers.material_events import classify_material_event, normalize_material_event_rows


def test_material_events_classifier_positive_and_risk():
    assert classify_material_event("公告取得AI大單") == "major_order"
    assert classify_material_event("公告重大訴訟") == "lawsuit"

    rows = LocalFileFetcher().fetch_csv(Path("tests/fixtures/material_events_sample.csv"), "twse", "material_events").rows
    normalized = normalize_material_event_rows(rows, "TWSE", "twse", "https://data.gov.tw/en/datasets/18415", "2026-05-11T00:00:00")

    assert normalized[0]["event_type"] == "major_order"
    assert normalized[1]["risk_score"] == 10.0

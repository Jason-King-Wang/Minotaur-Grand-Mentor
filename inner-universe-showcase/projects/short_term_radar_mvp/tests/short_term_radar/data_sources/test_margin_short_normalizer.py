from __future__ import annotations

from short_term_radar.data_sources.normalizers.margin_short import normalize_margin_short_rows


def test_margin_short_normalizer_maps_balances():
    rows = [{"日期": "115/05/11", "證券代號": "2330", "今日融資餘額": "10,000", "今日融券餘額": "--"}]

    normalized = normalize_margin_short_rows(rows, "TWSE", "twse", "https://example.test", "2026-05-11T00:00:00")

    assert normalized[0]["margin_balance"] == 10000
    assert normalized[0]["short_balance"] is None

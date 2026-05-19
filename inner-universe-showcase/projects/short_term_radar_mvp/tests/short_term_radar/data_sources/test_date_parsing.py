from __future__ import annotations

from datetime import date

from short_term_radar.data_sources.normalizers.common import parse_tw_date, parse_tw_month


def test_roc_year_to_ad_date():
    assert parse_tw_date("115/05/11") == date(2026, 5, 11)
    assert parse_tw_date("民國83年09月05日") == date(1994, 9, 5)
    assert parse_tw_month("115/04") == "202604"

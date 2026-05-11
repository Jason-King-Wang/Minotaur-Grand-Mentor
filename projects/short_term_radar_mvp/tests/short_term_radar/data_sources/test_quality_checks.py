from __future__ import annotations

from short_term_radar.data_sources.quality import validate_rows


def test_quality_report_detects_duplicate_primary_keys():
    row = {
        "trade_date": "2026-05-11",
        "market": "TWSE",
        "symbol": "2330",
        "name": "台積電",
        "open": 900,
        "high": 910,
        "low": 895,
        "close": 905,
        "change": 5,
        "volume": 1000,
        "amount": 905000,
        "transactions": 10,
        "issued_shares": None,
        "next_limit_up": None,
        "next_limit_down": None,
        "source": "twse",
        "source_url": "https://example.test",
        "fetched_at": "2026-05-11T00:00:00",
    }

    report = validate_rows("prices_daily", [row, row.copy()])

    assert report.ok is False
    assert any(issue.check == "primary key uniqueness" for issue in report.issues)

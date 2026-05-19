from __future__ import annotations

from short_term_radar.adapters.revenue_adapter import RevenueAdapter


def test_revenue_adapter_uses_announce_date_not_revenue_month():
    adapter = RevenueAdapter({})
    adapter.processed.load_table = lambda _table: [
        {
            "revenue_month": "202604",
            "announce_date": "2026-05-10",
            "market": "TWSE",
            "symbol": "2330",
            "revenue_current": "100",
            "revenue_yoy_pct": "-5",
            "revenue_mom_pct": "1",
        },
        {
            "revenue_month": "202605",
            "announce_date": "2026-06-10",
            "market": "TWSE",
            "symbol": "2330",
            "revenue_current": "1000",
            "revenue_yoy_pct": "100",
            "revenue_mom_pct": "900",
        },
    ]

    features = adapter.load_features("2026-05-11")

    assert features["2330"]["latest_revenue_month"] == "202604"
    assert features["2330"]["rev_yoy_1m"] == -5

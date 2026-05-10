from __future__ import annotations

from short_term_radar.adapters.revenue_adapter import RevenueAdapter


def test_revenue_adapter_filters_by_release_date(tmp_path):
    path = tmp_path / "revenue.csv"
    path.write_text(
        "symbol,revenue_month,revenue,release_date\n"
        "1234,2026-03,100,2026-04-10\n"
        "1234,2026-04,200,2026-05-10\n",
        encoding="utf-8",
    )
    adapter = RevenueAdapter({"data": {"monthly_revenue_path": str(path)}})

    rows = adapter.rows_until("1234", "2026-04-30")

    assert len(rows) == 1
    assert rows[0]["revenue_month"] == "2026-03"

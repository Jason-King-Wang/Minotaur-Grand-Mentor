from __future__ import annotations

from pathlib import Path

from short_term_radar.data_sources.fetchers.mops_monthly_revenue_fetcher import (
    MopsMonthlyRevenueFetcher,
    parse_mops_monthly_revenue_html,
)
from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.normalizers.monthly_revenue import normalize_monthly_revenue_rows
from short_term_radar.data_sources.sources.monthly_revenue_official import MonthlyRevenueOfficialSource


def test_mops_monthly_revenue_url_uses_roc_year_and_company_type():
    request = MopsMonthlyRevenueFetcher().build_url("TWSE", "2026-04", "foreign")

    assert request.revenue_month == "202604"
    assert request.url.endswith("/sii/t21sc03_115_4_1.html")


def test_monthly_revenue_official_requests_cover_market_and_company_types():
    source = MonthlyRevenueOfficialSource({})

    requests = source.build_requests("all", "2026-04", "2026-04")
    urls = {request.url for request in requests}

    assert len(requests) == 4
    assert any("/sii/t21sc03_115_4_0.html" in url for url in urls)
    assert any("/sii/t21sc03_115_4_1.html" in url for url in urls)
    assert any("/otc/t21sc03_115_4_0.html" in url for url in urls)
    assert any("/otc/t21sc03_115_4_1.html" in url for url in urls)


def test_mops_monthly_revenue_fixture_parser_normalizes_rows():
    html = Path("tests/fixtures/mops_monthly_revenue_sii_sample.html").read_text(encoding="utf-8")
    raw_rows = parse_mops_monthly_revenue_html(html, "TWSE", "202604", "local")
    normalized = normalize_monthly_revenue_rows(raw_rows, "TWSE", "official_mops", "fixture", "2026-05-11T00:00:00")

    assert normalized[0]["symbol"] == "2330"
    assert normalized[0]["announce_date"] == "2026-05-10"
    assert normalized[0]["announce_date_inferred"] is True
    assert normalized[0]["announce_date_source"] == "inferred_next_month_day_10"
    assert normalized[0]["company_type"] == "local"
    assert normalized[0]["revenue_yoy_pct"] == 31.12


def test_monthly_revenue_without_month_does_not_fall_back_to_fetched_at():
    normalized = normalize_monthly_revenue_rows(
        [{"symbol": "2330", "name": "TSMC", "revenue_current": "100"}],
        "TWSE",
        "official_mops",
        "fixture",
        "2026-05-11T00:00:00",
    )

    assert normalized == []


def test_monthly_revenue_official_degraded_fetch_does_not_crash():
    source = MonthlyRevenueOfficialSource({})
    source.fetcher.fetch_month = lambda market, revenue_month, company_type: FetchResult(
        "mops",
        "monthly_revenue",
        "https://example.test",
        degraded=True,
        message=f"{market}-{revenue_month}-{company_type} blocked",
    )

    result = source.collect("TWSE", "2026-04", "2026-04")

    assert result.rows == []
    assert len(result.degraded) == 2
    assert "blocked" in result.degraded[0]

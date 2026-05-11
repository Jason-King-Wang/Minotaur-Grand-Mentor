from __future__ import annotations

from short_term_radar.cli.coverage import generate_coverage_reports
from short_term_radar.data_sources.storage import merge_processed_rows


def test_coverage_report_detects_missing_months(tmp_path):
    config = {"data_root": str(tmp_path)}
    merge_processed_rows(
        config,
        "monthly_revenue",
        [
            {
                "revenue_month": "202601",
                "announce_date": "2026-02-10",
                "market": "TWSE",
                "symbol": "2330",
                "source": "fixture",
                "source_url": "fixture",
                "fetched_at": "2026-02-10T00:00:00",
            },
            {
                "revenue_month": "202603",
                "announce_date": "2026-04-10",
                "market": "TWSE",
                "symbol": "2330",
                "source": "fixture",
                "source_url": "fixture",
                "fetched_at": "2026-04-10T00:00:00",
            },
        ],
    )

    reports = generate_coverage_reports(config, "2026-01-01", "2026-03-31")
    revenue_coverage = next(row for row in reports["coverage"] if row["dataset"] == "monthly_revenue" and row["market"] == "TWSE")

    assert revenue_coverage["expected_count"] == 3
    assert revenue_coverage["actual_count"] == 2
    assert any(row["dataset"] == "monthly_revenue" and row["missing_date_or_month"] == "202602" for row in reports["missing"])


def test_freshness_report_flags_stale_monthly_revenue(tmp_path):
    config = {"data_root": str(tmp_path)}
    merge_processed_rows(
        config,
        "monthly_revenue",
        [
            {
                "revenue_month": "202601",
                "announce_date": "2026-02-10",
                "market": "TWSE",
                "symbol": "2330",
                "source": "fixture",
                "source_url": "fixture",
                "fetched_at": "2026-02-10T00:00:00",
            }
        ],
    )

    reports = generate_coverage_reports(config, "2026-01-01", "2026-03-31")
    freshness = next(row for row in reports["freshness"] if row["dataset"] == "monthly_revenue" and row["market"] == "TWSE")

    assert freshness["freshness_status"] == "stale"
    assert freshness["lag_days"] > 0


def test_daily_coverage_uses_trading_dates_not_weekends(tmp_path):
    config = {"data_root": str(tmp_path)}
    merge_processed_rows(
        config,
        "prices_daily",
        [
            {"trade_date": "2026-01-02", "market": "TWSE", "symbol": "2330", "source": "fixture", "source_url": "fixture", "fetched_at": "2026-01-02T00:00:00"},
            {"trade_date": "2026-01-05", "market": "TWSE", "symbol": "2330", "source": "fixture", "source_url": "fixture", "fetched_at": "2026-01-05T00:00:00"},
        ],
    )

    reports = generate_coverage_reports(config, "2026-01-02", "2026-01-05")
    prices_coverage = next(row for row in reports["coverage"] if row["dataset"] == "prices_daily" and row["market"] == "TWSE")

    assert prices_coverage["expected_count"] == 2
    assert not any(row["missing_date_or_month"] in {"2026-01-03", "2026-01-04"} for row in reports["missing"])


def test_event_driven_datasets_do_not_emit_daily_missing_rows(tmp_path):
    config = {"data_root": str(tmp_path)}

    reports = generate_coverage_reports(config, "2026-01-02", "2026-01-05")

    assert not any(row["dataset"] in {"material_events", "corporate_actions"} for row in reports["missing"])
    material = next(row for row in reports["coverage"] if row["dataset"] == "material_events" and row["market"] == "TWSE")
    assert material["expected_count"] == 0
    assert material["missing_count"] == 0


def test_surveillance_without_enabled_download_source_is_source_missing_not_daily_missing(tmp_path):
    config = {
        "data_root": str(tmp_path),
        "sources": {
            "tpex": {
                "enabled": True,
                "datasets": {
                    "attention": {"landing_url": "https://data.gov.tw/dataset/11395", "download_url": ""},
                    "disposition": {"landing_url": "https://data.gov.tw/dataset/11396", "download_url": ""},
                },
            }
        },
    }
    merge_processed_rows(
        config,
        "prices_daily",
        [
            {"trade_date": "2026-01-02", "market": "TPEX", "symbol": "3088", "source": "fixture", "source_url": "fixture", "fetched_at": "2026-01-02T00:00:00"},
            {"trade_date": "2026-01-05", "market": "TPEX", "symbol": "3088", "source": "fixture", "source_url": "fixture", "fetched_at": "2026-01-05T00:00:00"},
        ],
    )

    reports = generate_coverage_reports(config, "2026-01-02", "2026-01-05")
    surveillance = next(row for row in reports["coverage"] if row["dataset"] == "surveillance" and row["market"] == "TPEX")
    freshness = next(row for row in reports["freshness"] if row["dataset"] == "surveillance" and row["market"] == "TPEX")

    assert surveillance["source"] == "source_missing"
    assert surveillance["missing_count"] == 0
    assert freshness["freshness_status"] == "source_missing"

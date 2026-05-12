from __future__ import annotations

from short_term_radar.data_sources.storage import merge_processed_rows, read_processed_rows


def test_merge_processed_rows_upserts_by_primary_key(tmp_path):
    config = {"data_root": str(tmp_path)}
    old = {
        "revenue_month": "202604",
        "market": "TWSE",
        "symbol": "2330",
        "announce_date": "2026-05-10",
        "revenue_current": 100,
        "source": "fixture",
        "source_url": "old",
        "fetched_at": "2026-05-10T00:00:00",
    }
    newer = {**old, "revenue_current": 200, "source_url": "new", "fetched_at": "2026-05-11T00:00:00"}
    extra = {**old, "symbol": "2317", "revenue_current": 300}

    first = merge_processed_rows(config, "monthly_revenue", [old], mode="upsert")
    second = merge_processed_rows(config, "monthly_revenue", [newer, extra], mode="upsert")
    rows = read_processed_rows(config, "monthly_revenue")

    assert first["inserted_rows"] == 1
    assert second["updated_rows"] == 1
    assert second["inserted_rows"] == 1
    assert len(rows) == 2
    assert next(row for row in rows if row["symbol"] == "2330")["revenue_current"] == 200


def test_merge_processed_rows_append_dedupes_primary_key(tmp_path):
    config = {"data_root": str(tmp_path)}
    row = {
        "trade_date": "2026-05-11",
        "market": "TPEX",
        "symbol": "6488",
        "attention_flag": True,
        "disposition_flag": False,
        "source": "fixture",
        "source_url": "fixture",
        "fetched_at": "2026-05-11T00:00:00",
    }

    merge_processed_rows(config, "surveillance", [row], mode="append")
    result = merge_processed_rows(config, "surveillance", [row], mode="append")

    assert result["merged_rows"] == 1
    assert result["duplicate_rows_removed"] == 1


def test_merge_processed_rows_upserts_institutional_trading_by_primary_key(tmp_path):
    config = {"data_root": str(tmp_path)}
    old = {
        "trade_date": "2026-04-30",
        "market": "TWSE",
        "symbol": "2330",
        "foreign_net": 100,
        "source": "fixture",
        "source_url": "old",
        "fetched_at": "2026-05-10T00:00:00",
    }
    newer = {**old, "foreign_net": 200, "source_url": "new", "fetched_at": "2026-05-11T00:00:00"}

    merge_processed_rows(config, "institutional_trading", [old], mode="upsert")
    result = merge_processed_rows(config, "institutional_trading", [newer], mode="upsert")
    rows = read_processed_rows(config, "institutional_trading")

    assert result["updated_rows"] == 1
    assert len(rows) == 1
    assert rows[0]["foreign_net"] == 200

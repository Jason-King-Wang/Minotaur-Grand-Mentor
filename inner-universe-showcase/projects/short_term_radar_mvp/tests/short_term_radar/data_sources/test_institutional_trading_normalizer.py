from __future__ import annotations

from short_term_radar.data_sources.normalizers.institutional_trading import normalize_institutional_trading_rows


def test_institutional_trading_normalizer_derives_net():
    rows = [
        {
            "日期": "115/05/11",
            "證券代號": "2330",
            "證券名稱": "台積電",
            "外陸資買進股數": "2,000",
            "外陸資賣出股數": "500",
            "投信買進股數": "100",
            "投信賣出股數": "50",
            "自營商買進股數": "80",
            "自營商賣出股數": "100",
        }
    ]

    normalized = normalize_institutional_trading_rows(rows, "TWSE", "twse", "https://example.test", "2026-05-11T00:00:00")

    assert normalized[0]["foreign_net"] == 1500
    assert normalized[0]["total_institutional_net"] == 1530

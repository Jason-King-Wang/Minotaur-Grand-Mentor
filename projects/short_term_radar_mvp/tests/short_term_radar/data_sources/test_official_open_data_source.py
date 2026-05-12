from __future__ import annotations

import json

from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.sources.official_open_data import OfficialOpenDataSource, extract_rows


class FakeFetcher:
    def __init__(self, payloads: dict[str, str | None]):
        self.payloads = payloads

    def fetch_text(self, url: str, source: str, dataset: str) -> FetchResult:
        raw_text = self.payloads.get(url)
        if raw_text is None:
            return FetchResult(source, dataset, url, degraded=True, message="missing fixture")
        return FetchResult(source, dataset, url, raw_text=raw_text)


def test_official_open_data_extracts_common_payload_shapes():
    assert extract_rows('[{"symbol": "2330"}]') == [{"symbol": "2330"}]
    assert extract_rows('{"aaData": [{"symbol": "2317"}]}') == [{"symbol": "2317"}]
    assert extract_rows('{"tables": [{"data": [{"symbol": "2454"}]}]}') == [{"symbol": "2454"}]


def test_official_open_data_extracts_twse_field_data_payload():
    rows = extract_rows('{"fields": ["symbol", "name"], "data": [["2330", "TSMC"]]}')

    assert rows == [{"symbol": "2330", "name": "TSMC"}]


def test_official_open_data_builds_margin_requests_for_both_markets():
    requests = OfficialOpenDataSource().build_requests("margin_short", "all", "2026-04-30")

    endpoint_names = {request.endpoint_name for request in requests}

    assert {"twse_margin", "twse_sbl", "tpex_margin", "tpex_sbl"}.issubset(endpoint_names)
    assert all(request.date == "2026-04-30" for request in requests)


def test_official_open_data_uses_configured_api_and_supplemental_urls():
    config = {
        "sources": {
            "twse": {
                "enabled": True,
                "datasets": {
                    "margin_short": {
                        "api_url": "https://example.test/margin",
                        "supplemental_api_urls": ["https://example.test/sbl"],
                    }
                },
            }
        }
    }

    requests = OfficialOpenDataSource(config).build_requests("margin_short", "TWSE", "2026-04-30")

    assert [request.url for request in requests] == ["https://example.test/margin", "https://example.test/sbl"]
    assert [request.endpoint_name for request in requests] == ["twse_margin_short", "twse_margin_short_supplemental_1"]


def test_official_margin_short_collect_normalizes_and_merges_rows():
    margin_url = "https://example.test/margin"
    sbl_url = "https://example.test/sbl"
    config = {
        "sources": {
            "twse": {
                "enabled": True,
                "datasets": {
                    "margin_short": {
                        "api_url": margin_url,
                        "supplemental_api_urls": [sbl_url],
                    }
                },
            }
        }
    }
    margin_payload = {
        "fields": [
            "\u80a1\u7968\u4ee3\u865f",
            "\u80a1\u7968\u540d\u7a31",
            "\u878d\u8cc7\u8cb7\u9032",
            "\u878d\u8cc7\u8ce3\u51fa",
            "\u878d\u8cc7\u73fe\u91d1\u511f\u9084",
            "\u878d\u8cc7\u524d\u65e5\u9918\u984d",
            "\u878d\u8cc7\u4eca\u65e5\u9918\u984d",
            "\u878d\u5238\u8ce3\u51fa",
            "\u878d\u5238\u8cb7\u9032",
            "\u878d\u5238\u73fe\u5238\u511f\u9084",
            "\u878d\u5238\u524d\u65e5\u9918\u984d",
            "\u878d\u5238\u4eca\u65e5\u9918\u984d",
        ],
        "data": [["2330", "TSMC", "1,000", "200", "10", "900", "1,690", "50", "20", "5", "100", "125"]],
    }
    sbl_payload = [
        {
            "\u80a1\u7968\u4ee3\u865f": "2330",
            "\u80a1\u7968\u540d\u7a31": "TSMC",
            "\u501f\u5238\u8ce3\u51fa\u6210\u4ea4\u6578\u91cf": "80",
            "\u501f\u5238\u9918\u984d": "500",
            "\u501f\u5238\u8ce3\u51fa\u9918\u984d": "120",
        }
    ]
    source = OfficialOpenDataSource(config)
    source.fetcher = FakeFetcher({margin_url: json.dumps(margin_payload), sbl_url: json.dumps(sbl_payload)})

    result = source.collect("margin_short", "TWSE", "2026-04-30")

    assert result.degraded == []
    assert len(result.rows) == 1
    row = result.rows[0]
    assert row["trade_date"] == "2026-04-30"
    assert row["market"] == "TWSE"
    assert row["symbol"] == "2330"
    assert row["margin_buy"] == 1000
    assert row["margin_balance"] == 1690
    assert row["short_sell"] == 50
    assert row["short_balance"] == 125
    assert row["sbl_short_sell_volume"] == 80
    assert row["sbl_balance"] == 500
    assert row["sbl_short_sell_balance"] == 120


def test_official_open_data_collect_reports_degraded_source():
    source = OfficialOpenDataSource(
        {
            "sources": {
                "twse": {
                    "enabled": True,
                    "datasets": {"margin_short": {"api_url": "https://example.test/missing"}},
                }
            }
        }
    )
    source.fetcher = FakeFetcher({})

    result = source.collect("margin_short", "TWSE", "2026-04-30")

    assert result.rows == []
    assert result.degraded == ["https://example.test/missing: missing fixture"]

from __future__ import annotations

import json
from pathlib import Path

from short_term_radar.data_sources.base import FetchResult
from short_term_radar.data_sources.fetchers.tpex_institutional_trading_fetcher import parse_tpex_3insti_payload
from short_term_radar.data_sources.fetchers.twse_institutional_trading_fetcher import parse_twse_t86_payload
from short_term_radar.data_sources.normalizers.institutional_trading import normalize_institutional_trading_rows
from short_term_radar.data_sources.sources.institutional_trading_official import InstitutionalTradingOfficialSource


def test_twse_t86_json_parser_normalizes_fixture_payload():
    payload = json.loads(Path("tests/fixtures/twse_t86_sample.json").read_text(encoding="utf-8"))

    rows = parse_twse_t86_payload(payload, "2026-04-30")
    normalized = normalize_institutional_trading_rows(
        rows,
        "TWSE",
        "official_twse",
        "https://example.test/t86",
        "2026-05-12T00:00:00",
    )

    assert normalized[0]["trade_date"] == "2026-04-30"
    assert normalized[0]["market"] == "TWSE"
    assert normalized[0]["symbol"] == "2330"
    assert normalized[0]["foreign_net"] == 1500
    assert normalized[0]["dealer_buy"] == 90
    assert normalized[0]["dealer_net"] == -5
    assert normalized[0]["total_institutional_net"] == 1545
    assert normalized[0]["source_url"] == "https://example.test/t86"


def test_tpex_3insti_json_parser_normalizes_fixture_payload():
    payload = json.loads(Path("tests/fixtures/tpex_3insti_sample.json").read_text(encoding="utf-8"))

    rows = parse_tpex_3insti_payload(payload, "2026-04-30")
    normalized = normalize_institutional_trading_rows(
        rows,
        "TPEX",
        "official_tpex",
        "https://example.test/tpex",
        "2026-05-12T00:00:00",
    )

    assert normalized[0]["trade_date"] == "2026-04-30"
    assert normalized[0]["market"] == "TPEX"
    assert normalized[0]["symbol"] == "6488"
    assert normalized[0]["foreign_buy"] == 1000
    assert normalized[0]["investment_trust_net"] == -100
    assert normalized[0]["dealer_net"] == 30
    assert normalized[0]["total_institutional_net"] == 630


def test_institutional_trading_source_reports_degraded_fetch_without_crashing(tmp_path):
    class DegradedTwseFetcher:
        def build_url(self, api_url_template: str, trade_date: str) -> str:
            return api_url_template.format(date="20260430")

        def fetch_url(self, url: str, trade_date: str) -> FetchResult:
            return FetchResult("official_twse", "institutional_trading", url, degraded=True, message="blocked")

    config = {
        "data_root": str(tmp_path),
        "sources": {
            "twse": {
                "enabled": True,
                "datasets": {
                    "institutional_trading": {
                        "api_url": "https://example.test/T86?date={date}&response=json",
                    }
                },
            }
        },
    }

    result = InstitutionalTradingOfficialSource(config, twse_fetcher=DegradedTwseFetcher()).collect(
        "TWSE",
        "2026-04-30",
    )

    assert result.rows == []
    assert "blocked" in result.degraded[0]

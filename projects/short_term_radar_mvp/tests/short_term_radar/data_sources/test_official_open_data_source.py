from __future__ import annotations

from short_term_radar.data_sources.sources.official_open_data import OfficialOpenDataSource, extract_rows


def test_official_open_data_extracts_common_payload_shapes():
    assert extract_rows('[{"symbol": "2330"}]') == [{"symbol": "2330"}]
    assert extract_rows('{"aaData": [{"symbol": "2317"}]}') == [{"symbol": "2317"}]
    assert extract_rows('{"tables": [{"data": [{"symbol": "2454"}]}]}') == [{"symbol": "2454"}]


def test_official_open_data_builds_margin_requests_for_both_markets():
    requests = OfficialOpenDataSource().build_requests("margin_short", "all", "2026-04-30")

    endpoint_names = {request.endpoint_name for request in requests}

    assert {"twse_margin", "twse_sbl", "tpex_margin", "tpex_sbl"}.issubset(endpoint_names)
    assert all(request.date == "2026-04-30" for request in requests)

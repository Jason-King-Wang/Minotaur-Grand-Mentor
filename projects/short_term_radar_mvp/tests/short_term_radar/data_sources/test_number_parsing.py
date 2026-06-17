from __future__ import annotations

from short_term_radar.data_sources.normalizers.common import parse_number_zh_tw, parse_percent


def test_number_and_percent_parsing():
    assert parse_number_zh_tw("1,234") == 1234
    assert parse_number_zh_tw("--") is None
    assert parse_number_zh_tw("2.5億") == 250_000_000
    assert parse_percent("12.5%") == 12.5

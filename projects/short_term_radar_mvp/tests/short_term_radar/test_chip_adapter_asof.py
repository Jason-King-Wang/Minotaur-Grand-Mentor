from __future__ import annotations

from short_term_radar.adapters.chip_adapter import ChipAdapter


def test_chip_adapter_filters_by_trade_date(tmp_path):
    path = tmp_path / "chip.csv"
    path.write_text(
        "symbol,trade_date,foreign_buy,investment_trust_buy,dealer_buy\n"
        "1234,2026-04-29,1,2,3\n"
        "1234,2026-05-02,10,20,30\n",
        encoding="utf-8",
    )
    adapter = ChipAdapter({"data": {"chip_data_path": str(path)}})

    rows = adapter.rows_until("1234", "2026-04-30")

    assert len(rows) == 1
    assert rows[0]["inst_buy_total"] == 6

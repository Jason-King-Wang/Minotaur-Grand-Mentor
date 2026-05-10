from __future__ import annotations

from short_term_radar.adapters.catalyst_adapter import CatalystAdapter


def test_catalyst_adapter_reads_local_csv(tmp_path):
    path = tmp_path / "catalyst.csv"
    path.write_text(
        "symbol,event_date,category,confidence,impact,status\n"
        "1234,2026-05-20,earnings,0.9,positive,confirmed\n",
        encoding="utf-8",
    )

    rows = CatalystAdapter({"data": {"catalyst_path": str(path)}}).rows_for_symbol("1234")

    assert rows[0]["category"] == "earnings"
    assert rows[0]["impact"] == "positive"

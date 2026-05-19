from z3b_prime.data.loader import load_ohlcv_csv
from z3b_prime.data.resample import resample_to_1h


def test_load_ohlcv_csv_and_resample_to_1h(tmp_path):
    csv_path = tmp_path / "bars.csv"
    csv_path.write_text(
        "\n".join(
            [
                "datetime,symbol,open,high,low,close,volume",
                "2026-01-01 09:00:00,TEST,100,103,99,102,10",
                "2026-01-01 09:15:00,TEST,102,104,101,103,20",
                "2026-01-01 09:30:00,TEST,103,105,102,104,30",
                "2026-01-01 09:45:00,TEST,104,106,103,105,40",
            ]
        ),
        encoding="utf-8",
    )

    bars = load_ohlcv_csv(csv_path, timeframe="15m")
    hourly = resample_to_1h(bars)

    assert len(bars) == 4
    assert str(bars[0].close_time) == "2026-01-01 09:15:00"
    assert len(hourly) == 1
    assert hourly[0].open == 100
    assert hourly[0].high == 106
    assert hourly[0].low == 99
    assert hourly[0].close == 105
    assert hourly[0].volume == 100

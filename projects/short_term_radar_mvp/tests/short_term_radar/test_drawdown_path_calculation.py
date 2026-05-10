from __future__ import annotations

from datetime import date, timedelta

import pytest

from short_term_radar.backtest.labeler import forward_label


def test_forward_path_max_drawdown_uses_running_peak():
    closes = [100, 120, 150, 90, 180]
    start = date(2026, 1, 1)
    rows = [{"symbol": "1234", "trade_date": (start + timedelta(days=i)).isoformat(), "close": close} for i, close in enumerate(closes)]

    label = forward_label(rows, rows[0]["trade_date"], 4)

    assert label.forward_max_return == pytest.approx(0.8)
    assert label.forward_close_return == pytest.approx(0.8)
    assert label.forward_min_return_from_entry == pytest.approx(-0.1)
    assert label.forward_path_max_drawdown == pytest.approx(-0.4)

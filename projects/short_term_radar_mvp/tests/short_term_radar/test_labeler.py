from __future__ import annotations

from datetime import date, timedelta

import pytest

from short_term_radar.backtest.labeler import forward_label


def _rows(closes):
    start = date(2025, 1, 1)
    return [
        {
            "symbol": "1234",
            "trade_date": (start + timedelta(days=index)).isoformat(),
            "close": close,
        }
        for index, close in enumerate(closes)
    ]


def test_forward_labels_hit_multiples_and_returns():
    rows = _rows([10, 9, 12, 30, 50])
    label = forward_label(rows, rows[0]["trade_date"], horizon_days=4)

    assert label.hit_3x is True
    assert label.hit_5x is True
    assert label.forward_max_return == 4.0
    assert label.forward_close_return == 4.0
    assert label.forward_max_drawdown == pytest.approx(-0.1)

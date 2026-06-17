from __future__ import annotations

from short_term_radar.backtest.metrics import summarize_backtest


def test_backtest_metrics_precision_and_empty_data():
    rows = [
        {"forward_max_return": 2.1, "forward_close_return": 1.0, "forward_max_drawdown": -0.2, "hit_3x": True, "hit_5x": False},
        {"forward_max_return": 0.5, "forward_close_return": -0.1, "forward_max_drawdown": -0.4, "hit_3x": False, "hit_5x": False},
    ]
    summary = summarize_backtest(rows, "2025-01-01", "2025-12-31", 2, 126, 3)

    assert summary["hit_rate_3x"] == 0.5
    assert summary["precision_at_n"] == 0.5
    assert summary["num_candidates"] == 2

    empty = summarize_backtest([], "2025-01-01", "2025-12-31", 2, 126, 3)
    assert empty["num_candidates"] == 0
    assert empty["hit_rate_3x"] == 0.0

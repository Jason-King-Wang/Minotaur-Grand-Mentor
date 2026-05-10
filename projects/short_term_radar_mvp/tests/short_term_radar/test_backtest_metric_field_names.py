from __future__ import annotations

from short_term_radar.backtest.metrics import summarize_backtest


def test_backtest_metric_names_are_explicit():
    rows = [
        {
            "forward_max_return": 1.2,
            "forward_close_return": 0.4,
            "forward_min_return_from_entry": -0.1,
            "forward_path_max_drawdown": -0.3,
            "hit_2x": True,
            "hit_3x": False,
            "hit_5x": False,
        }
    ]

    summary = summarize_backtest(rows, "2025-01-01", "2025-12-31", 1, 126, 3)

    assert "avg_forward_max_return" in summary
    assert "avg_forward_return" not in summary
    assert "avg_forward_path_max_drawdown" in summary

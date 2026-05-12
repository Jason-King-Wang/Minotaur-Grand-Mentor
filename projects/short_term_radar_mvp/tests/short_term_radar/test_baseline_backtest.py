from __future__ import annotations

from short_term_radar.backtest.baselines import BASELINE_STRATEGIES, select_baseline_candidates


def test_random_baseline_is_deterministic():
    candidates = [{"symbol": str(symbol), "score_total": symbol} for symbol in range(10)]

    first = select_baseline_candidates("random_top_n", candidates, 4, random_seed=42, period_date="2026-05-11")
    second = select_baseline_candidates("random_top_n", candidates, 4, random_seed=42, period_date="2026-05-11")

    assert [row["symbol"] for row in first] == [row["symbol"] for row in second]


def test_breakout_baseline_uses_breakout_flag():
    candidates = [
        {"symbol": "1", "breakout_flag": True, "breakout_120d_flag": False, "volume_expansion_ratio": 3, "rs_20d": 1},
        {"symbol": "2", "breakout_120d_flag": True, "volume_expansion_ratio": 2, "rs_20d": 1},
    ]

    selected = select_baseline_candidates("breakout_120d_only", candidates, 10)

    assert [row["symbol"] for row in selected] == ["2"]


def test_volume_and_ma_baselines_filter_expected_features():
    candidates = [
        {"symbol": "1", "volume_expansion_ratio": 1.0, "volume_z_20": 9, "ma_alignment_bull_flag": False},
        {"symbol": "2", "volume_expansion_ratio": 2.0, "volume_z_20": 5, "ma_alignment_bull_flag": True, "rs_20d": 0.2},
    ]

    volume = select_baseline_candidates("volume_expansion_only", candidates, 10)
    ma = select_baseline_candidates("ma_alignment_only", candidates, 10)

    assert [row["symbol"] for row in volume] == ["2"]
    assert [row["symbol"] for row in ma] == ["2"]
    assert "radar_model" in BASELINE_STRATEGIES

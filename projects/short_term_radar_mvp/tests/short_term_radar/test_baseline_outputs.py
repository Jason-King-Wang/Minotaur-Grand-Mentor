from __future__ import annotations

from short_term_radar.backtest.baselines import select_baseline_candidates
from short_term_radar.backtest.simulator import write_backtest_outputs


def test_random_baseline_is_seed_deterministic_and_outputs_files(tmp_path):
    features = {str(i): {"symbol": str(i)} for i in range(10)}

    first = select_baseline_candidates("random_top_n", features, 3, seed=42)
    second = select_baseline_candidates("random_top_n", features, 3, seed=42)

    assert [row["symbol"] for row in first] == [row["symbol"] for row in second]

    summary = {"period_start": "2026-01-01", "period_end": "2026-12-31", "strategy_name": "radar_top_n"}
    baseline = [{"period_start": "2026-01-01", "period_end": "2026-12-31", "strategy_name": "random_top_n"}]
    paths = write_backtest_outputs(tmp_path / "backtest_2026.csv", summary, [], baseline, [])

    assert paths["baseline"].name == "baseline_comparison_2026.csv"
    assert paths["baseline_details"].name == "baseline_details_2026.csv"

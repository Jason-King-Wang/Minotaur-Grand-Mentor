from __future__ import annotations

from short_term_radar.cli.report import generate_report
from short_term_radar.utils.io import write_csv


def test_report_contains_cl6_sections(tmp_path):
    scan_file = tmp_path / "scan.csv"
    backtest_file = tmp_path / "backtest.csv"
    baseline_file = tmp_path / "baseline.csv"
    output = tmp_path / "report.md"
    write_csv(
        scan_file,
        [
            {
                "rank": 1,
                "symbol": "2330",
                "name": "TSMC",
                "score_total": 80,
                "score_raw_available_norm": 90,
                "score_coverage_adjusted": 80,
                "score_cap": 100,
                "stage": "S3",
                "entry_zone": "candidate_entry",
                "mode": "full_short_term_radar",
                "score_data_coverage_ratio": 1,
                "robot_slot_coverage_ratio": 1,
                "robot_slot_statuses": {"PRICE_SLOT": "installed", "REVENUE_SLOT": "installed"},
                "core_data_ready_flag": True,
                "degraded_radars": [],
            }
        ],
        [
            "rank",
            "symbol",
            "name",
            "score_total",
            "score_raw_available_norm",
            "score_coverage_adjusted",
            "score_cap",
            "stage",
            "entry_zone",
            "mode",
            "score_data_coverage_ratio",
            "robot_slot_coverage_ratio",
            "robot_slot_statuses",
            "core_data_ready_flag",
            "degraded_radars",
        ],
    )
    write_csv(backtest_file, [{"horizon_days": 126, "top_n": 20, "hit_rate_3x": 0.1, "hit_rate_5x": 0, "precision_at_n": 0.1}], ["horizon_days", "top_n", "hit_rate_3x", "hit_rate_5x", "precision_at_n"])
    write_csv(baseline_file, [{"strategy_name": "radar_model", "hit_rate_3x": 0.1, "hit_rate_5x": 0, "precision_at_n": 0.1, "avg_forward_max_return": 1.2, "num_candidates": 20}], ["strategy_name", "hit_rate_3x", "hit_rate_5x", "precision_at_n", "avg_forward_max_return", "num_candidates"])

    generate_report(str(scan_file), str(backtest_file), str(output), str(baseline_file))

    text = output.read_text(encoding="utf-8")
    assert "## Data Coverage Summary" in text
    assert "## Radar Mode Summary" in text
    assert "## Robot Slot Status" in text
    assert "## Top S3 Candidate Entry" in text
    assert "## Avoid Chasing / S5" in text
    assert "## Baseline Comparison" in text
    assert "## Source Freshness Warning" in text

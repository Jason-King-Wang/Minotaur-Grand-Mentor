from __future__ import annotations

from short_term_radar.features.crowding_risk import degradation_risk_flags
from short_term_radar.scoring.short_term_score import calculate_score_breakdown


WEIGHTS = {
    "revenue": 0.25,
    "expectation_gap": 0.20,
    "price_volume": 0.20,
    "theme_group": 0.15,
    "chip": 0.10,
    "catalyst": 0.10,
}


def test_all_core_radars_missing_caps_score_at_70():
    scores = {"revenue": None, "expectation_gap": 100, "price_volume": 100, "theme_group": 100, "chip": None, "catalyst": None}
    breakdown = calculate_score_breakdown(scores, WEIGHTS, 0)

    assert breakdown.score_cap == 70
    assert breakdown.score_total <= 70
    assert breakdown.core_data_ready_flag is False


def test_missing_revenue_caps_score_at_75():
    scores = {"revenue": None, "expectation_gap": 100, "price_volume": 100, "theme_group": 100, "chip": 100, "catalyst": 100}
    breakdown = calculate_score_breakdown(scores, WEIGHTS, 0)

    assert breakdown.score_cap == 75
    assert breakdown.score_total <= 75
    assert "revenue" in breakdown.degraded_radars


def test_data_coverage_ratio_and_risk_flags_are_reported():
    scores = {"revenue": None, "expectation_gap": 80, "price_volume": 70, "theme_group": None, "chip": None, "catalyst": None}
    breakdown = calculate_score_breakdown(scores, WEIGHTS, 0)
    flags = degradation_risk_flags(breakdown.degraded_radars, breakdown.data_coverage_ratio)

    assert 0 < breakdown.data_coverage_ratio < 1
    assert any("revenue data missing" in flag for flag in flags)

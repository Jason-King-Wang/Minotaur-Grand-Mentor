from __future__ import annotations

from short_term_radar.features.crowding_risk import risk_penalty
from short_term_radar.scoring.short_term_score import normalized_score


def test_score_renormalizes_missing_data_and_subtracts_risk():
    scores = {
        "revenue": None,
        "expectation_gap": 80,
        "price_volume": 60,
        "theme_group": None,
    }
    weights = {"revenue": 0.25, "expectation_gap": 0.20, "price_volume": 0.20, "theme_group": 0.15}

    assert normalized_score(scores, weights, risk_penalty=10) == 60


def test_risk_penalty_flags_overheated_stock():
    penalty, flags = risk_penalty({"ret_20d": 0.9, "ret_60d": 1.6, "volume_z_20": 4.5}, 40)

    assert penalty == 40
    assert any("20 日" in flag for flag in flags)
    assert any("60 日" in flag for flag in flags)

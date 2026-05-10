from __future__ import annotations

from short_term_radar.features.catalyst import compute_catalyst_features, score_catalyst


def test_catalyst_scoring_rewards_confirmed_near_term_positive_event():
    rows = [
        {
            "symbol": "1234",
            "event_date": "2026-05-20",
            "category": "earnings",
            "confidence": 0.9,
            "impact": "positive",
            "status": "confirmed",
        }
    ]

    features = compute_catalyst_features(rows, "2026-05-01", {"catalyst": {"lookahead_days": 126, "near_term_days": 45}})

    assert features["near_term_catalyst_count"] == 1
    assert score_catalyst(features) >= 50

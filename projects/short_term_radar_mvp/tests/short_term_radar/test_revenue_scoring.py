from __future__ import annotations

from short_term_radar.features.revenue import compute_revenue_features, score_revenue


def test_revenue_scoring_acceleration_and_new_highs():
    rows = []
    for index in range(24):
        year = 2024 + (index // 12)
        month = index % 12 + 1
        revenue = 100 + index * 2
        if index >= 21:
            revenue += 80
        rows.append(
            {
                "symbol": "1234",
                "revenue_month": f"{year}-{month:02d}",
                "revenue": revenue,
                "revenue_yoy": 0.4 if index >= 21 else 0.1,
                "revenue_mom": 0.05,
                "release_date": f"{year}-{month:02d}-10",
            }
        )

    features = compute_revenue_features(rows)

    assert features["rev_3m_yoy"] is not None
    assert features["rev_new_high_12m_flag"] is True
    assert score_revenue(features) >= 60

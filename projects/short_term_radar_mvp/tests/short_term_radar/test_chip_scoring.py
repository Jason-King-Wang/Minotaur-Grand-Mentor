from __future__ import annotations

from datetime import date, timedelta

from short_term_radar.features.chip import compute_chip_features, score_chip


def test_chip_scoring_rewards_accumulation_and_margin_decline():
    start = date(2026, 1, 1)
    rows = []
    for index in range(25):
        rows.append(
            {
                "symbol": "1234",
                "trade_date": (start + timedelta(days=index)).isoformat(),
                "foreign_buy": 100,
                "investment_trust_buy": 200,
                "dealer_buy": 10,
                "inst_buy_total": 310,
                "margin_balance": 1000 - index,
                "short_balance": 500 - index,
                "borrow_balance": 300 - index,
                "shares_outstanding": 10000,
            }
        )

    features = compute_chip_features(rows)

    assert features["foreign_buy_5d"] > 0
    assert score_chip(features) >= 60

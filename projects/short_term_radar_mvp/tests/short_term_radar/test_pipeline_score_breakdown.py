from __future__ import annotations

from short_term_radar.pipeline import _radar_mode, scan_candidates
from short_term_radar.scoring.short_term_score import calculate_score_breakdown


FULL_MODE_CORE_SLOTS = [
    "PRICE_SLOT",
    "UNIVERSE_SLOT",
    "REVENUE_SLOT",
    "CHIP_SLOT",
    "SURVEILLANCE_SLOT",
    "CATALYST_SLOT",
    "CORPORATE_SLOT",
    "VALUATION_SLOT",
    "CALENDAR_SLOT",
]


def test_score_breakdown_splits_score_and_robot_slot_coverage():
    scores = {"revenue": None, "price_volume": 80.0, "chip": 40.0, "catalyst": 60.0}
    weights = {"revenue": 0.5, "price_volume": 0.25, "chip": 0.15, "catalyst": 0.10}

    breakdown = calculate_score_breakdown(scores, weights, risk_penalty=0, degraded_radars=["revenue", "surveillance"])

    assert breakdown.score_data_coverage_ratio == 0.5
    assert breakdown.robot_slot_coverage_ratio == 0.5
    assert breakdown.score_cap == 75.0
    assert breakdown.core_data_ready_flag is False


def test_scan_output_contains_score_breakdown_fields(tmp_path):
    config = {
        "data_root": str(tmp_path),
        "data": {"market_index_symbol": "TAIEX"},
        "filters": {
            "min_trading_days": 3,
            "min_avg_amount_20d": 0,
            "exclude_full_delivery": True,
            "exclude_etf": False,
            "exclude_warrant": True,
        },
        "scoring": {
            "weights": {
                "revenue": 0.25,
                "expectation_gap": 0.20,
                "price_volume": 0.20,
                "theme_group": 0.15,
                "chip": 0.10,
                "catalyst": 0.10,
            },
            "risk_penalty_max": 40,
        },
        "price_volume": {
            "ma_windows": [2, 3],
            "rs_windows": [2],
            "breakout_windows": [2],
            "volume_z_window": 3,
            "breakout_volume_min_ratio": 1.0,
            "breakout_volume_max_ratio": 5.0,
        },
        "expectation_gap": {
            "early_ret_20d_max": 0.35,
            "early_ret_60d_max": 0.80,
            "overheated_ret_20d": 0.80,
            "overheated_ret_60d": 1.50,
            "overheated_volume_z": 4.0,
        },
        "manual_catalysts": {},
    }
    rows = [
        {"symbol": "TAIEX", "trade_date": "2026-05-08", "close": 100, "high": 100, "low": 100, "open": 100, "volume": 1, "amount": 1},
        {"symbol": "TAIEX", "trade_date": "2026-05-09", "close": 101, "high": 101, "low": 100, "open": 100, "volume": 1, "amount": 1},
        {"symbol": "TAIEX", "trade_date": "2026-05-10", "close": 102, "high": 102, "low": 101, "open": 101, "volume": 1, "amount": 1},
        {"symbol": "TAIEX", "trade_date": "2026-05-11", "close": 103, "high": 103, "low": 102, "open": 102, "volume": 1, "amount": 1},
    ]
    stock_rows = [
        {**row, "symbol": "2330", "name": "TSMC", "amount": 10_000_000, "volume": 1000 + index * 100}
        for index, row in enumerate(rows)
    ]

    output = scan_candidates(config, "2026-05-11", by_symbol={"TAIEX": rows, "2330": stock_rows})

    assert output
    assert "score_raw_available_norm" in output[0]
    assert "score_coverage_adjusted" in output[0]
    assert "score_cap" in output[0]
    assert output[0]["mode"] == "simple_price_volume_mode"
    assert "score_data_coverage_ratio" in output[0]
    assert "robot_slot_coverage_ratio" in output[0]
    assert "robot_slot_statuses" in output[0]
    assert "degraded_radars" in output[0]
    assert output[0]["core_data_ready_flag"] is False
    assert "data_coverage_ratio" not in output[0]


def test_full_radar_mode_requires_installed_core_slots():
    installed_statuses = {slot: "installed" for slot in FULL_MODE_CORE_SLOTS}

    assert _radar_mode(installed_statuses) == "full_short_term_radar"

    for partial_slot in FULL_MODE_CORE_SLOTS:
        partial_statuses = dict(installed_statuses)
        partial_statuses[partial_slot] = "partial"

        assert _radar_mode(partial_statuses) != "full_short_term_radar"

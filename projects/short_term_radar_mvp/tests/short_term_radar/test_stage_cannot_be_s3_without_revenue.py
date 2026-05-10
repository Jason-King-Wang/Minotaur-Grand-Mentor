from __future__ import annotations

from short_term_radar.schemas import ScoreBreakdown
from short_term_radar.scoring.stage_classifier import classify_stage


FEATURES = {"ret_20d": 0.2, "ret_60d": 0.5, "breakout_flag": True, "volume_expansion_ratio": 1.5}


def _score(**kwargs):
    defaults = {
        "score_raw_available_norm": 90,
        "score_coverage_adjusted": 90,
        "score_cap": 100,
        "score_total": 90,
        "data_coverage_ratio": 1,
        "available_radars": [],
        "degraded_radars": [],
        "core_data_ready_flag": True,
    }
    defaults.update(kwargs)
    return ScoreBreakdown(**defaults)


def test_missing_revenue_blocks_s3():
    stage, zone = classify_stage(FEATURES, _score(degraded_radars=["revenue"]), 0, None, {})

    assert stage != "S3"
    assert zone == "early_watch"


def test_low_coverage_blocks_s3():
    stage, _ = classify_stage(FEATURES, _score(data_coverage_ratio=0.5), 0, 80, {})

    assert stage != "S3"


def test_high_risk_forces_s5():
    stage, zone = classify_stage(FEATURES, _score(), 25, 80, {})

    assert stage == "S5"
    assert zone == "avoid_chasing"


def test_high_score_revenue_breakout_volume_allows_s3():
    stage, zone = classify_stage(FEATURES, _score(), 0, 80, {})

    assert stage == "S3"
    assert zone == "candidate_entry"

from __future__ import annotations

from short_term_radar.scoring.stage_classifier import apply_data_gating


def test_missing_revenue_caps_stage_to_s2():
    stage, zone, risks = apply_data_gating("S3", "candidate_entry", {}, ["revenue"])

    assert (stage, zone) == ("S2", "early_watch")
    assert any("revenue 缺資料" in risk for risk in risks)

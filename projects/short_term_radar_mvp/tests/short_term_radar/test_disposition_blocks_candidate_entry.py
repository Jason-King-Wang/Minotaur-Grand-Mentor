from __future__ import annotations

from short_term_radar.scoring.stage_classifier import apply_data_gating


def test_active_disposition_blocks_candidate_entry():
    stage, zone, risks = apply_data_gating("S3", "candidate_entry", {"disposition_active_flag": True}, [])

    assert (stage, zone) == ("S5", "avoid_chasing")
    assert any("處置中" in risk for risk in risks)

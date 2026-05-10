from __future__ import annotations

from typing import Any

from short_term_radar.schemas import ScoreBreakdown


def classify_stage(
    features: dict[str, Any],
    score: ScoreBreakdown | float,
    risk_penalty: float,
    revenue_score: float | None = None,
    config: dict[str, Any] | None = None,
) -> tuple[str, str]:
    score_total = score.score_total if isinstance(score, ScoreBreakdown) else float(score)
    data_coverage_ratio = score.data_coverage_ratio if isinstance(score, ScoreBreakdown) else 1.0
    degraded = set(score.degraded_radars if isinstance(score, ScoreBreakdown) else [])
    cfg = (config or {}).get("expectation_gap", {})
    overheated_ret_20d = float(cfg.get("overheated_ret_20d", 0.80))
    overheated_ret_60d = float(cfg.get("overheated_ret_60d", 1.50))
    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    breakout = features.get("breakout_flag") or features.get("breakout_with_volume_flag")
    volume_ratio = features.get("volume_expansion_ratio") or 0.0

    if score_total <= 0:
        return "S0", "watch_only"
    if risk_penalty >= 25 or ret_20 > overheated_ret_20d or ret_60 > overheated_ret_60d:
        return "S5", "avoid_chasing"
    if "revenue" in degraded or revenue_score is None:
        return ("S2", "early_watch") if score_total >= 50 else ("S1", "new_observation")
    if revenue_score < 60:
        return ("S2", "early_watch") if score_total >= 50 else ("S1", "new_observation")
    if data_coverage_ratio < 0.60:
        return ("S2", "early_watch") if score_total >= 50 else ("S1", "watch_only")
    if score_total >= 75 and revenue_score >= 60 and breakout and volume_ratio >= 1.2 and risk_penalty < 25:
        return "S3", "candidate_entry"
    if score_total >= 65 and (breakout or ret_20 > 0.15):
        return "S4", "wait_pullback" if ret_20 > 0.35 else "hold_or_trail"
    if score_total >= 50 and (ret_20 > 0 or volume_ratio >= 1.1):
        return "S2", "early_watch"
    return "S1", "new_observation"

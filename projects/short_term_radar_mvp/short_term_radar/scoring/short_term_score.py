from __future__ import annotations

from short_term_radar.schemas import ScoreBreakdown
from short_term_radar.utils.math_utils import clip


CORE_RADARS = ("revenue", "chip", "catalyst")


def calculate_score_breakdown(
    scores: dict[str, float | None],
    weights: dict[str, float],
    risk_penalty: float,
    degraded_radars: list[str] | None = None,
) -> ScoreBreakdown:
    degraded_set = set(degraded_radars or [])
    available = {key: value for key, value in scores.items() if value is not None and key in weights}
    total_weight = sum(float(weight) for weight in weights.values() if weight is not None)
    if not available or total_weight <= 0:
        return ScoreBreakdown(
            score_raw_available_norm=0.0,
            score_coverage_adjusted=0.0,
            score_cap=0.0,
            score_total=0.0,
            data_coverage_ratio=0.0,
            available_radars=[],
            degraded_radars=sorted(degraded_set or set(scores)),
            core_data_ready_flag=False,
        )

    available_weight = sum(float(weights[key]) for key in available)
    if available_weight <= 0:
        return ScoreBreakdown(
            score_raw_available_norm=0.0,
            score_coverage_adjusted=0.0,
            score_cap=0.0,
            score_total=0.0,
            data_coverage_ratio=0.0,
            available_radars=[],
            degraded_radars=sorted(degraded_set or set(scores)),
            core_data_ready_flag=False,
        )

    for key in weights:
        if key not in available:
            degraded_set.add(key)

    score_raw_available_norm = sum(float(value) * float(weights[key]) for key, value in available.items()) / available_weight
    data_coverage_ratio = available_weight / total_weight
    score_coverage_adjusted = score_raw_available_norm * data_coverage_ratio

    score_cap = 100.0
    core_missing = {radar for radar in CORE_RADARS if radar in degraded_set or scores.get(radar) is None}
    if core_missing == set(CORE_RADARS):
        score_cap = min(score_cap, 70.0)
    if "revenue" in core_missing:
        score_cap = min(score_cap, 75.0)
    if data_coverage_ratio < 0.60:
        score_cap = min(score_cap, 70.0)
    if data_coverage_ratio < 0.40:
        score_cap = min(score_cap, 55.0)

    score_total = clip(min(score_cap, score_coverage_adjusted - float(risk_penalty)))
    return ScoreBreakdown(
        score_raw_available_norm=clip(score_raw_available_norm),
        score_coverage_adjusted=clip(score_coverage_adjusted),
        score_cap=score_cap,
        score_total=score_total,
        data_coverage_ratio=max(0.0, min(1.0, data_coverage_ratio)),
        available_radars=sorted(available),
        degraded_radars=sorted(degraded_set),
        core_data_ready_flag=not core_missing,
    )


def normalized_score(scores: dict[str, float | None], weights: dict[str, float], risk_penalty: float) -> float:
    return calculate_score_breakdown(scores, weights, risk_penalty).score_total

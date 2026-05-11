from __future__ import annotations

from short_term_radar.utils.math_utils import clip
from short_term_radar.schemas import ScoreBreakdown


def normalized_score(scores: dict[str, float | None], weights: dict[str, float], risk_penalty: float) -> float:
    available = {key: value for key, value in scores.items() if value is not None and key in weights}
    if not available:
        return 0.0

    total_weight = sum(weights[key] for key in available)
    if total_weight <= 0:
        return 0.0

    weighted = sum(float(value) * weights[key] for key, value in available.items()) / total_weight
    return clip(weighted - risk_penalty)


def apply_score_caps(score: float, missing_radars: list[str]) -> float:
    cap = 100.0
    if all(item in missing_radars for item in ["revenue", "chip", "catalyst"]):
        cap = min(cap, 70.0)
    elif "revenue" in missing_radars:
        cap = min(cap, 75.0)
    if "surveillance" in missing_radars:
        cap = min(cap, 80.0)
    return min(score, cap)


def calculate_score_breakdown(
    scores: dict[str, float | None],
    weights: dict[str, float],
    risk_penalty: float,
) -> ScoreBreakdown:
    available_radars = [key for key, value in scores.items() if value is not None and key in weights]
    degraded_radars = [key for key, value in scores.items() if value is None and key in weights]
    raw = normalized_score(scores, weights, 0)
    data_coverage_ratio = len(available_radars) / len([key for key in scores if key in weights]) if weights else 0.0
    coverage_adjusted = clip(raw * data_coverage_ratio - risk_penalty)
    score_cap = _score_cap(degraded_radars)
    total = min(coverage_adjusted, score_cap)
    core_data_ready = not any(item in degraded_radars for item in ["revenue", "chip", "catalyst"])
    return ScoreBreakdown(
        score_raw_available_norm=round(raw, 4),
        score_coverage_adjusted=round(coverage_adjusted, 4),
        score_cap=score_cap,
        score_total=round(total, 4),
        data_coverage_ratio=round(data_coverage_ratio, 4),
        available_radars=available_radars,
        degraded_radars=degraded_radars,
        core_data_ready_flag=core_data_ready,
    )


def _score_cap(degraded_radars: list[str]) -> float:
    cap = 100.0
    if all(item in degraded_radars for item in ["revenue", "chip", "catalyst"]):
        cap = min(cap, 70.0)
    elif "revenue" in degraded_radars:
        cap = min(cap, 75.0)
    if "surveillance" in degraded_radars:
        cap = min(cap, 80.0)
    return cap

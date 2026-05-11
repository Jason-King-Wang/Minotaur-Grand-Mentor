from __future__ import annotations

from short_term_radar.utils.math_utils import clip
from short_term_radar.schemas import ScoreBreakdown


def normalized_score(scores: dict[str, float | None], weights: dict[str, float], risk_penalty: float) -> float:
    return clip(_weighted_available_score(scores, weights) - risk_penalty)


def calculate_score_breakdown(
    scores: dict[str, float | None],
    weights: dict[str, float],
    risk_penalty: float,
    degraded_radars: list[str] | None = None,
) -> ScoreBreakdown:
    available_radars = [key for key, value in scores.items() if value is not None and key in weights]
    score_degraded = [key for key, value in scores.items() if value is None and key in weights]
    degraded = _unique(score_degraded + (degraded_radars or []))
    raw = _weighted_available_score(scores, weights)
    total_weight = sum(float(value) for key, value in weights.items() if key in scores)
    available_weight = sum(float(weights[key]) for key in available_radars)
    score_data_coverage_ratio = available_weight / total_weight if total_weight > 0 else 0.0
    robot_slot_coverage_ratio = _robot_slot_coverage_ratio(degraded)
    coverage_adjusted = clip(raw * score_data_coverage_ratio - risk_penalty)
    score_cap = _score_cap(degraded)
    total = min(coverage_adjusted, score_cap)
    core_data_ready = not any(item in degraded for item in ["revenue", "chip", "catalyst"])
    return ScoreBreakdown(
        score_raw_available_norm=round(raw, 4),
        score_coverage_adjusted=round(coverage_adjusted, 4),
        score_cap=score_cap,
        score_total=round(total, 4),
        score_data_coverage_ratio=round(score_data_coverage_ratio, 4),
        robot_slot_coverage_ratio=round(robot_slot_coverage_ratio, 4),
        available_radars=available_radars,
        degraded_radars=degraded,
        core_data_ready_flag=core_data_ready,
    )


def _weighted_available_score(scores: dict[str, float | None], weights: dict[str, float]) -> float:
    available = {key: value for key, value in scores.items() if value is not None and key in weights}
    if not available:
        return 0.0
    total_weight = sum(weights[key] for key in available)
    if total_weight <= 0:
        return 0.0
    return sum(float(value) * weights[key] for key, value in available.items()) / total_weight


def _score_cap(degraded_radars: list[str]) -> float:
    cap = 100.0
    if all(item in degraded_radars for item in ["revenue", "chip", "catalyst"]):
        cap = min(cap, 70.0)
    elif "revenue" in degraded_radars:
        cap = min(cap, 75.0)
    if "surveillance" in degraded_radars:
        cap = min(cap, 80.0)
    return cap


def _robot_slot_coverage_ratio(degraded_radars: list[str]) -> float:
    slots = ["revenue", "chip", "catalyst", "surveillance"]
    available = [slot for slot in slots if slot not in degraded_radars]
    return len(available) / len(slots)


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

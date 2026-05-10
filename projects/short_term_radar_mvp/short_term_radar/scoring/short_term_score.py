from __future__ import annotations

from short_term_radar.utils.math_utils import clip


def normalized_score(scores: dict[str, float | None], weights: dict[str, float], risk_penalty: float) -> float:
    available = {key: value for key, value in scores.items() if value is not None and key in weights}
    if not available:
        return 0.0

    total_weight = sum(weights[key] for key in available)
    if total_weight <= 0:
        return 0.0

    weighted = sum(float(value) * weights[key] for key, value in available.items()) / total_weight
    return clip(weighted - risk_penalty)

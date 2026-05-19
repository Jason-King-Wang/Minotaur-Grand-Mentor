from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def score_expectation_gap(features: dict[str, Any], config: dict[str, Any]) -> float:
    cfg = config["expectation_gap"]
    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    volume_z = features.get("volume_z_20") or 0.0
    score = 45.0

    if features.get("breakout_flag") or features.get("above_ma20_flag"):
        score += 20
    if 0 <= ret_20 <= float(cfg["early_ret_20d_max"]):
        score += 15
    if 0 <= ret_60 <= float(cfg["early_ret_60d_max"]):
        score += 10
    if -0.5 <= volume_z <= 3.0:
        score += 10
    if ret_20 >= float(cfg["overheated_ret_20d"]):
        score -= 25
    if ret_60 >= float(cfg["overheated_ret_60d"]):
        score -= 25
    if volume_z >= float(cfg["overheated_volume_z"]):
        score -= 15
    return clip(score)

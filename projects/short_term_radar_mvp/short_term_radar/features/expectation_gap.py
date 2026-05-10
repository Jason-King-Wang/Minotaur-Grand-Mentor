from __future__ import annotations

from typing import Any

from short_term_radar.utils.math_utils import clip


def enrich_expectation_gap_features(features: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    volume_z = features.get("volume_z_20") or 0.0
    features.update(
        {
            "price_reacted_20d": ret_20,
            "price_reacted_60d": ret_60,
            "not_overreacted_flag": bool(ret_20 <= config["expectation_gap"].get("overheated_ret_20d", 0.80)),
            "quiet_accumulation_flag": bool(features.get("above_ma20_flag") and 0 <= ret_20 <= 0.35 and volume_z <= 3.0),
            "breakout_after_base_flag": bool(features.get("breakout_flag") and ret_60 <= 0.80),
            "base_length_days": None,
            "base_tightness": None,
            "news_heat_score": None,
            "social_heat_score": None,
            "analyst_coverage_count": None,
            "expectation_data_available_flag": False,
            "expectation_gap_source": "price_only",
        }
    )
    return features


def score_expectation_gap(features: dict[str, Any], config: dict[str, Any]) -> float:
    enrich_expectation_gap_features(features, config)
    cfg = config["expectation_gap"]
    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    volume_z = features.get("volume_z_20") or 0.0
    score = 40.0

    if features.get("breakout_flag") or features.get("above_ma20_flag"):
        score += 15
    if 0 <= ret_20 <= float(cfg["early_ret_20d_max"]):
        score += 15
    if 0 <= ret_60 <= float(cfg["early_ret_60d_max"]):
        score += 10
    if features.get("quiet_accumulation_flag"):
        score += 10
    if features.get("breakout_after_base_flag"):
        score += 15
    if ret_20 >= float(cfg["overheated_ret_20d"]):
        score -= 25
    if ret_60 >= float(cfg["overheated_ret_60d"]):
        score -= 25
    if volume_z >= float(cfg["overheated_volume_z"]):
        score -= 15
    if ret_20 < -0.20:
        score -= 20
    return clip(score)

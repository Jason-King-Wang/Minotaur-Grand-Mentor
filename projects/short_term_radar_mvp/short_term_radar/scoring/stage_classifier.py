from __future__ import annotations

from typing import Any


def classify_stage(features: dict[str, Any], score_total: float, risk_penalty: float) -> tuple[str, str]:
    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    breakout = features.get("breakout_flag")
    volume_ratio = features.get("volume_expansion_ratio") or 0.0

    if score_total <= 0:
        return "S0", "watch_only"
    if risk_penalty >= 25 or ret_20 > 0.80 or ret_60 > 1.50:
        return "S5", "avoid_chasing"
    if score_total >= 75 and breakout and volume_ratio >= 1.2:
        return "S3", "candidate_entry"
    if score_total >= 65 and (breakout or ret_20 > 0.15):
        return "S4", "hold_or_trail"
    if score_total >= 50 and (ret_20 > 0 or volume_ratio >= 1.1):
        return "S2", "early_watch"
    return "S1", "watch_only"

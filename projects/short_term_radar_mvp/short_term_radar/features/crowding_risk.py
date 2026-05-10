from __future__ import annotations

from typing import Any


def risk_penalty(features: dict[str, Any], max_penalty: float = 40.0) -> tuple[float, list[str]]:
    penalty = 0.0
    flags: list[str] = []

    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    volume_z = features.get("volume_z_20") or 0.0
    upper_shadow = features.get("upper_shadow_ratio") or 0.0

    if ret_20 > 0.80:
        penalty += 15
        flags.append("20D return is overheated")
    elif ret_20 > 0.50:
        penalty += 8
        flags.append("20D return is extended")

    if ret_60 > 1.50:
        penalty += 20
        flags.append("60D return is overheated")
    elif ret_60 > 1.00:
        penalty += 10
        flags.append("60D return is extended")

    if volume_z > 4:
        penalty += 15
        flags.append(f"volume z-score is elevated: {volume_z:.1f}")

    if upper_shadow > 0.45:
        penalty += 10
        flags.append("large upper shadow suggests chase risk")

    return min(max_penalty, penalty), flags


def degradation_risk_flags(degraded_radars: list[str], data_coverage_ratio: float) -> list[str]:
    flags: list[str] = []
    if "revenue" in degraded_radars:
        flags.append("revenue data missing; core score is capped and S3 is blocked")
    if "chip" in degraded_radars:
        flags.append("chip data missing; institutional and margin signals unavailable")
    if "catalyst" in degraded_radars:
        flags.append("catalyst data missing; event timing confidence unavailable")
    if data_coverage_ratio < 0.60:
        flags.append("data coverage below 60%; ranking confidence is low")
    return flags

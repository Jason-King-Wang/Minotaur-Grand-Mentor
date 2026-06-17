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
        flags.append("近 20 日漲幅過大，追高風險升高")
    elif ret_20 > 0.50:
        penalty += 8
        flags.append("近 20 日漲幅偏高")

    if ret_60 > 1.50:
        penalty += 20
        flags.append("近 60 日漲幅過熱")
    elif ret_60 > 1.00:
        penalty += 10
        flags.append("近 60 日漲幅偏高")

    if volume_z > 4:
        penalty += 15
        flags.append(f"成交量 z-score {volume_z:.1f}，短線擁擠")

    if upper_shadow > 0.45:
        penalty += 10
        flags.append("爆量長上影或上檔賣壓偏重")

    if features.get("attention_flag"):
        penalty += 10
        flags.append("注意股，短線風險升高")

    if features.get("disposition_active_flag"):
        penalty = max(penalty, max_penalty)
        flags.append("處置中，禁止候選進場")

    if features.get("financing_overcrowded_flag"):
        penalty += 10
        flags.append("融資增幅偏高，籌碼擁擠")

    if features.get("valuation_overheated_flag"):
        penalty += 8
        flags.append("估值偏熱")

    return min(max_penalty, penalty), flags


def degradation_risk_flags(degraded_radars: list[str], data_coverage_ratio: float) -> list[str]:
    labels = {
        "revenue": "revenue data missing; fundamental turn is unverified",
        "chip": "chip data missing; institutional flow is unverified",
        "catalyst": "catalyst data missing; re-rating driver is unverified",
        "surveillance": "surveillance data missing; attention/disposition risk is unverified",
    }
    flags = [labels.get(item, f"{item} data missing") for item in degraded_radars]
    if data_coverage_ratio < 0.5:
        flags.append("data coverage below 50%; radar is heavily degraded")
    return flags

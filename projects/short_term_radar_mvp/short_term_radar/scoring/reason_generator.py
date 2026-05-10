from __future__ import annotations

from typing import Any


def generate_reasons(
    features: dict[str, Any], scores: dict[str, float | None], degraded: list[str]
) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    risks: list[str] = []

    if features.get("breakout_120d_flag"):
        reasons.append("120D breakout")
    elif features.get("breakout_60d_flag"):
        reasons.append("60D breakout")

    ratio = features.get("volume_expansion_ratio")
    if ratio is not None and 1.2 <= ratio <= 3.5:
        reasons.append(f"volume expansion {ratio:.1f}x 20D average")

    rs_20 = features.get("rs_20d")
    if rs_20 is not None and rs_20 > 0:
        reasons.append("20D relative strength is positive")

    rs_60 = features.get("rs_60d")
    if rs_60 is not None and rs_60 > 0:
        reasons.append("60D relative strength is positive")

    if scores.get("revenue") is not None and scores["revenue"] >= 60:
        reasons.append("revenue radar supports momentum")

    if features.get("ma_alignment_bull_flag"):
        reasons.append("moving averages are bull aligned")
    elif features.get("above_ma20_flag") and features.get("above_ma60_flag"):
        reasons.append("price is above MA20 and MA60")

    if scores.get("expectation_gap") is not None and scores["expectation_gap"] >= 70:
        reasons.append("price-only expectation gap proxy is constructive")

    if scores.get("chip") is not None and scores["chip"] >= 60:
        reasons.append("chip radar shows net accumulation")

    if scores.get("catalyst") is not None and scores["catalyst"] >= 40:
        reasons.append("near-term catalyst is present")

    for item in degraded:
        risks.append(f"{item} radar degraded")

    if not reasons:
        reasons.append("limited but improving price-volume evidence")
    return reasons, risks

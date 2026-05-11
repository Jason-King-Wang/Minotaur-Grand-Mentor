from __future__ import annotations

from typing import Any


def generate_reasons(
    features: dict[str, Any], scores: dict[str, float | None], degraded: list[str]
) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    risks: list[str] = []

    if features.get("breakout_120d_flag"):
        reasons.append("突破 120 日整理區")
    elif features.get("breakout_60d_flag"):
        reasons.append("突破 60 日整理區")

    ratio = features.get("volume_expansion_ratio")
    if ratio is not None and 1.2 <= ratio <= 3.5:
        reasons.append(f"成交量為 20 日均量 {ratio:.1f} 倍，屬於有效放量區")

    rs_20 = features.get("rs_20d")
    if rs_20 is not None and rs_20 > 0:
        reasons.append("近 20 日相對強於大盤")

    rs_60 = features.get("rs_60d")
    if rs_60 is not None and rs_60 > 0:
        reasons.append("近 60 日相對強於大盤")

    if features.get("ma_alignment_bull_flag"):
        reasons.append("均線結構轉為多頭排列")
    elif features.get("above_ma20_flag") and features.get("above_ma60_flag"):
        reasons.append("站上 20 日與 60 日均線")

    if scores.get("expectation_gap") is not None and scores["expectation_gap"] >= 70:
        reasons.append("價量轉強但尚未完全過熱，預期差仍可接受")

    for item in degraded:
        risks.append(f"{item} 缺資料，雷達降級")

    if not reasons:
        reasons.append("通過基本流動性與資料完整性篩選")
    return reasons, risks

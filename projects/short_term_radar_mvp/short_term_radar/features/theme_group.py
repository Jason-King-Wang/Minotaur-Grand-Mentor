from __future__ import annotations

from collections import defaultdict
from typing import Any

from short_term_radar.utils.math_utils import clip, mean


def score_theme_groups(features_by_symbol: dict[str, dict[str, Any]]) -> dict[str, float | None]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for features in features_by_symbol.values():
        industry = features.get("industry")
        if industry:
            grouped[industry].append(features)

    industry_scores: dict[str, float] = {}
    for industry, items in grouped.items():
        if len(items) < 2:
            continue
        avg_ret_20 = mean([item.get("ret_20d") for item in items]) or 0.0
        breakout_count = sum(1 for item in items if item.get("breakout_flag"))
        new_high_score = min(30, breakout_count * 8)
        industry_scores[industry] = clip(45 + avg_ret_20 * 80 + new_high_score)

    return {
        symbol: industry_scores.get(features.get("industry"))
        for symbol, features in features_by_symbol.items()
    }

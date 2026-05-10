from __future__ import annotations

from collections import defaultdict
from typing import Any

from short_term_radar.utils.math_utils import clip, mean


def _themes_for(symbol: str, features: dict[str, Any], config: dict[str, Any]) -> list[str]:
    mapping = config.get("theme_mapping") or {}
    mapped = mapping.get(symbol)
    if isinstance(mapped, str):
        return [mapped]
    if isinstance(mapped, list) and mapped:
        return [str(item) for item in mapped]
    industry = features.get("industry")
    return [industry] if industry else []


def score_theme_groups(features_by_symbol: dict[str, dict[str, Any]], config: dict[str, Any] | None = None) -> dict[str, float | None]:
    config = config or {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    symbol_themes: dict[str, list[str]] = {}
    for symbol, features in features_by_symbol.items():
        themes = _themes_for(symbol, features, config)
        symbol_themes[symbol] = themes
        for theme in themes:
            grouped[theme].append(features)

    theme_stats: dict[str, dict[str, Any]] = {}
    for theme, items in grouped.items():
        if len(items) < 2:
            continue
        avg_ret_20 = mean([item.get("ret_20d") for item in items]) or 0.0
        avg_rs_20 = mean([item.get("rs_20d") for item in items]) or 0.0
        breakout_count = sum(1 for item in items if item.get("breakout_flag"))
        above_ma20_count = sum(1 for item in items if item.get("above_ma20_flag"))
        breakout_ratio = breakout_count / len(items)
        above_ma20_ratio = above_ma20_count / len(items)
        volume_avg = mean([item.get("volume_expansion_ratio") for item in items]) or 0.0
        leaders = sorted(items, key=lambda item: item.get("rs_20d") or -999, reverse=True)
        theme_stats[theme] = {
            "theme_avg_ret_20d": avg_ret_20,
            "theme_avg_rs_20d": avg_rs_20,
            "theme_breakout_count": breakout_count,
            "theme_breakout_ratio": breakout_ratio,
            "theme_above_ma20_ratio": above_ma20_ratio,
            "theme_volume_expansion_ratio_avg": volume_avg,
            "leader_symbols": [item.get("symbol") for item in leaders[:3]],
        }

    scores: dict[str, float | None] = {}
    for symbol, features in features_by_symbol.items():
        themes = symbol_themes.get(symbol) or []
        best_theme = None
        best_score = None
        for theme in themes:
            stats = theme_stats.get(theme)
            if not stats:
                continue
            score = 40.0
            if stats["theme_breakout_count"] >= 3:
                score += 10
            if stats["theme_breakout_ratio"] > 0.20:
                score += 15
            if stats["theme_avg_rs_20d"] > 0:
                score += 15
            if symbol in stats["leader_symbols"]:
                score += 15
            if stats["theme_above_ma20_ratio"] > 0.60:
                score += 10
            if stats["theme_avg_ret_20d"] < -0.10:
                score -= 15
            score = clip(score)
            if best_score is None or score > best_score:
                best_theme = theme
                best_score = score
        if best_theme and best_score is not None:
            stats = theme_stats[best_theme]
            features.update(stats)
            features["theme"] = best_theme
            features["theme_available_flag"] = True
            features["theme_leader_score"] = 15 if symbol in stats["leader_symbols"] else 0
            features["theme_rank"] = (stats["leader_symbols"].index(symbol) + 1) if symbol in stats["leader_symbols"] else None
        else:
            features["theme_available_flag"] = False
        scores[symbol] = best_score
    return scores

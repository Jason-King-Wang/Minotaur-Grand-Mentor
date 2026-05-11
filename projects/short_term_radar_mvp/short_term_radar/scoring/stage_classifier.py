from __future__ import annotations

from typing import Any

from short_term_radar.schemas import ScoreBreakdown


def classify_stage(
    features: dict[str, Any],
    score_total: float | ScoreBreakdown,
    risk_penalty: float,
    min_data_coverage_for_s3: float | None = None,
    _config: dict[str, Any] | None = None,
) -> tuple[str, str]:
    breakdown = score_total if isinstance(score_total, ScoreBreakdown) else None
    if breakdown is not None:
        score_value = breakdown.score_total
        if "revenue" in breakdown.degraded_radars:
            return "S2", "early_watch"
        min_coverage = _normalize_coverage_threshold(min_data_coverage_for_s3)
        if min_coverage is not None and breakdown.data_coverage_ratio < min_coverage:
            return "S2", "early_watch"
    else:
        score_value = float(score_total)

    ret_20 = features.get("ret_20d") or 0.0
    ret_60 = features.get("ret_60d") or 0.0
    breakout = features.get("breakout_flag")
    volume_ratio = features.get("volume_expansion_ratio") or 0.0

    if score_value <= 0:
        return "S0", "watch_only"
    if risk_penalty >= 25 or ret_20 > 0.80 or ret_60 > 1.50:
        return "S5", "avoid_chasing"
    if score_value >= 75 and breakout and volume_ratio >= 1.2:
        return "S3", "candidate_entry"
    if score_value >= 65 and (breakout or ret_20 > 0.15):
        return "S4", "hold_or_trail"
    if score_value >= 50 and (ret_20 > 0 or volume_ratio >= 1.1):
        return "S2", "early_watch"
    return "S1", "watch_only"


def _normalize_coverage_threshold(value: float | None) -> float | None:
    if value is None:
        return None
    return value / 100 if value > 1 else value


def apply_data_gating(
    stage: str,
    entry_zone: str,
    features: dict[str, Any],
    missing_radars: list[str],
) -> tuple[str, str, list[str]]:
    risk_flags: list[str] = []

    if features.get("disposition_active_flag"):
        return "S5", "avoid_chasing", ["處置中，禁止 candidate_entry"]

    if "surveillance" in missing_radars:
        risk_flags.append("surveillance 缺資料，注意/處置風險未驗證")
    if "revenue" in missing_radars:
        risk_flags.append("revenue 缺資料，基本面未驗證")
        if stage in {"S3", "S4"}:
            stage, entry_zone = "S2", "early_watch"
    if "chip" in missing_radars:
        risk_flags.append("chip 缺資料，籌碼未驗證")
    if "catalyst" in missing_radars:
        risk_flags.append("catalyst 缺資料，缺少 1-6 個月重估催化劑")

    if "catalyst" in missing_radars and stage == "S3":
        stage, entry_zone = "S2", "early_watch"
    return stage, entry_zone, risk_flags

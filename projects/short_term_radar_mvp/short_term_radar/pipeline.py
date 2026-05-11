from __future__ import annotations

from datetime import datetime
from typing import Any

from short_term_radar.adapters.catalyst_adapter import CatalystAdapter
from short_term_radar.adapters.chip_adapter import ChipAdapter
from short_term_radar.adapters.corporate_action_adapter import CorporateActionAdapter
from short_term_radar.adapters.processed_data_adapter import ProcessedDataAdapter
from short_term_radar.adapters.revenue_adapter import RevenueAdapter
from short_term_radar.adapters.surveillance_adapter import SurveillanceAdapter
from short_term_radar.adapters.valuation_adapter import ValuationAdapter
from short_term_radar.data_loader import load_daily_prices
from short_term_radar.features.catalyst import score_catalyst
from short_term_radar.features.chip import score_chip
from short_term_radar.features.crowding_risk import risk_penalty
from short_term_radar.features.expectation_gap import score_expectation_gap
from short_term_radar.features.price_volume import compute_price_volume_features, score_price_volume
from short_term_radar.features.revenue import score_revenue
from short_term_radar.features.theme_group import score_theme_groups
from short_term_radar.schemas import RadarCandidate
from short_term_radar.scoring.reason_generator import generate_reasons
from short_term_radar.scoring.short_term_score import calculate_score_breakdown
from short_term_radar.scoring.stage_classifier import apply_data_gating, classify_stage


SCAN_FIELDS = [
    "rank",
    "symbol",
    "name",
    "industry",
    "score_total",
    "score_revenue",
    "score_expectation_gap",
    "score_price_volume",
    "score_theme_group",
    "score_chip",
    "score_catalyst",
    "risk_penalty",
    "score_raw_available_norm",
    "score_coverage_adjusted",
    "score_cap",
    "stage",
    "entry_zone",
    "reasons",
    "risk_flags",
    "last_close",
    "ret_20d",
    "ret_60d",
    "volume_z_20",
    "volume_expansion_ratio",
    "rs_20d",
    "rs_60d",
    "breakout_flag",
    "breakout_120d_flag",
    "ma_alignment_bull_flag",
    "score_data_coverage_ratio",
    "robot_slot_coverage_ratio",
    "available_radars",
    "degraded_radars",
    "core_data_ready_flag",
    "created_at",
]


def scan_candidates(
    config: dict[str, Any],
    as_of_date: str,
    top: int | None = None,
    by_symbol: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    by_symbol = by_symbol if by_symbol is not None else load_daily_prices(config)
    features_by_symbol = compute_price_volume_features(by_symbol, as_of_date, config)
    theme_scores = score_theme_groups(features_by_symbol)
    processed = ProcessedDataAdapter(config)
    revenue_features = RevenueAdapter(config).load_features(as_of_date)
    chip_features = ChipAdapter(config).load_features(as_of_date)
    catalyst_features = CatalystAdapter(config.get("manual_catalysts"), config).load_features(as_of_date)
    surveillance_features = SurveillanceAdapter(config).load_features(as_of_date)
    corporate_action_features = CorporateActionAdapter(config).load_features(as_of_date)
    valuation_features = ValuationAdapter(config).load_features(as_of_date)
    source_available = {
        "revenue": processed.table_exists("monthly_revenue"),
        "chip": processed.table_exists("institutional_trading_daily")
        or processed.table_exists("margin_short_daily"),
        "catalyst": processed.table_exists("material_events") or bool(config.get("manual_catalysts")),
        "surveillance": processed.table_exists("surveillance_daily"),
    }
    weights = config["scoring"]["weights"]
    max_penalty = float(config["scoring"].get("risk_penalty_max", 40))
    created_at = datetime.now().isoformat(timespec="seconds")
    candidates: list[RadarCandidate] = []

    for symbol, features in features_by_symbol.items():
        enriched = {
            **features,
            **(revenue_features.get(symbol) or {}),
            **(chip_features.get(symbol) or {}),
            **(catalyst_features.get(symbol) or {}),
            **(surveillance_features.get(symbol) or {}),
            **(corporate_action_features.get(symbol) or {}),
            **(valuation_features.get(symbol) or {}),
        }
        scores = {
            "revenue": score_revenue(revenue_features.get(symbol)),
            "expectation_gap": score_expectation_gap(enriched, config),
            "price_volume": score_price_volume(enriched),
            "theme_group": theme_scores.get(symbol),
            "chip": score_chip(chip_features.get(symbol)),
            "catalyst": score_catalyst(catalyst_features.get(symbol)),
        }
        missing_radars = _missing_radars(
            symbol,
            source_available,
            revenue_features,
            chip_features,
            catalyst_features,
            surveillance_features,
        )
        degraded = [key for key, value in scores.items() if value is None and key in {"revenue", "chip", "catalyst"}]
        if "surveillance" in missing_radars:
            degraded.append("surveillance")
        penalty, risk_flags = risk_penalty(enriched, max_penalty)
        breakdown = calculate_score_breakdown(scores, weights, penalty, degraded)
        total = breakdown.score_total
        stage, entry_zone = classify_stage(
            enriched,
            breakdown,
            penalty,
            config.get("scoring", {}).get("min_data_coverage_for_s3"),
        )
        stage, entry_zone, gating_risks = apply_data_gating(stage, entry_zone, enriched, missing_radars)
        reasons, generated_risks = generate_reasons(enriched, scores, [])
        candidates.append(
            RadarCandidate(
                symbol=symbol,
                name=enriched.get("name"),
                industry=enriched.get("industry"),
                trade_date=enriched.get("trade_date") or as_of_date,
                score_total=round(total, 4),
                score_revenue=scores["revenue"],
                score_expectation_gap=round(scores["expectation_gap"], 4)
                if scores["expectation_gap"] is not None
                else None,
                score_price_volume=round(scores["price_volume"], 4)
                if scores["price_volume"] is not None
                else None,
                score_theme_group=round(scores["theme_group"], 4)
                if scores["theme_group"] is not None
                else None,
                score_chip=scores["chip"],
                score_catalyst=scores["catalyst"],
                risk_penalty=round(penalty, 4),
                stage=stage,
                entry_zone=entry_zone,
                score_raw_available_norm=breakdown.score_raw_available_norm,
                score_coverage_adjusted=breakdown.score_coverage_adjusted,
                score_cap=breakdown.score_cap,
                reasons=reasons,
                risk_flags=_unique(risk_flags + gating_risks + generated_risks),
                last_close=enriched.get("last_close"),
                ret_20d=enriched.get("ret_20d"),
                ret_60d=enriched.get("ret_60d"),
                volume_z_20=enriched.get("volume_z_20"),
                volume_expansion_ratio=enriched.get("volume_expansion_ratio"),
                rs_20d=enriched.get("rs_20d"),
                rs_60d=enriched.get("rs_60d"),
                breakout_flag=enriched.get("breakout_flag", False),
                breakout_120d_flag=enriched.get("breakout_120d_flag", False),
                ma_alignment_bull_flag=enriched.get("ma_alignment_bull_flag", False),
                score_data_coverage_ratio=breakdown.score_data_coverage_ratio,
                robot_slot_coverage_ratio=breakdown.robot_slot_coverage_ratio,
                available_radars=breakdown.available_radars,
                degraded_radars=breakdown.degraded_radars,
                core_data_ready_flag=breakdown.core_data_ready_flag,
                created_at=created_at,
            )
        )

    candidates.sort(key=lambda item: item.score_total, reverse=True)
    if top:
        candidates = candidates[:top]

    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, 1):
        row = candidate.to_row()
        row["rank"] = rank
        rows.append(row)
    return rows


def _missing_radars(
    symbol: str,
    source_available: dict[str, bool],
    revenue_features: dict[str, dict[str, Any]],
    chip_features: dict[str, dict[str, Any]],
    catalyst_features: dict[str, dict[str, Any]],
    surveillance_features: dict[str, dict[str, Any]],
) -> list[str]:
    missing: list[str] = []
    if not source_available["revenue"] or symbol not in revenue_features:
        missing.append("revenue")
    if not source_available["chip"] or symbol not in chip_features:
        missing.append("chip")
    if not source_available["catalyst"] or symbol not in catalyst_features:
        missing.append("catalyst")
    if not source_available["surveillance"]:
        missing.append("surveillance")
    return missing


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

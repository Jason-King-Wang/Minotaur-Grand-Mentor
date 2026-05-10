from __future__ import annotations

from datetime import datetime
from typing import Any

from short_term_radar.adapters.catalyst_adapter import CatalystAdapter
from short_term_radar.adapters.chip_adapter import ChipAdapter
from short_term_radar.adapters.revenue_adapter import RevenueAdapter
from short_term_radar.data_loader import load_daily_prices
from short_term_radar.features.catalyst import compute_catalyst_features, score_catalyst
from short_term_radar.features.chip import compute_chip_features, score_chip
from short_term_radar.features.crowding_risk import degradation_risk_flags, risk_penalty
from short_term_radar.features.expectation_gap import score_expectation_gap
from short_term_radar.features.price_volume import compute_price_volume_features, score_price_volume
from short_term_radar.features.revenue import compute_revenue_features, score_revenue
from short_term_radar.features.theme_group import score_theme_groups
from short_term_radar.schemas import RadarCandidate
from short_term_radar.scoring.reason_generator import generate_reasons
from short_term_radar.scoring.short_term_score import calculate_score_breakdown
from short_term_radar.scoring.stage_classifier import classify_stage


SCAN_FIELDS = [
    "rank",
    "symbol",
    "name",
    "industry",
    "universe_mode",
    "score_total",
    "score_raw_available_norm",
    "score_coverage_adjusted",
    "score_cap",
    "data_coverage_ratio",
    "available_radars",
    "degraded_radars",
    "core_data_ready_flag",
    "score_revenue",
    "score_expectation_gap",
    "expectation_gap_source",
    "score_price_volume",
    "score_theme_group",
    "score_chip",
    "score_catalyst",
    "risk_penalty",
    "stage",
    "entry_zone",
    "reasons",
    "risk_flags",
    "last_close",
    "avg_amount_20",
    "ret_20d",
    "ret_60d",
    "ret_120d",
    "volume_z_20",
    "volume_expansion_ratio",
    "rs_20d",
    "rs_60d",
    "breakout_flag",
    "breakout_60d_flag",
    "breakout_120d_flag",
    "rev_1m_yoy",
    "rev_3m_yoy",
    "rev_6m_yoy",
    "rev_3m_vs_12m_acceleration",
    "latest_revenue_month",
    "latest_revenue_release_date",
    "foreign_buy_5d",
    "investment_trust_buy_5d",
    "inst_buy_total_20d",
    "margin_change_20d",
    "next_catalyst_date",
    "next_catalyst_category",
    "data_quality_flags",
    "survivorship_bias_warning",
    "price_data_source",
    "revenue_data_source",
    "chip_data_source",
    "created_at",
]


def _round(value: Any, digits: int = 4) -> Any:
    return round(value, digits) if isinstance(value, (int, float)) else value


def _optional_data_adapters(config: dict[str, Any]) -> tuple[RevenueAdapter, ChipAdapter, CatalystAdapter]:
    revenue_adapter = RevenueAdapter(config)
    chip_adapter = ChipAdapter(config)
    catalyst_adapter = CatalystAdapter(config)
    revenue_adapter.load()
    chip_adapter.load()
    catalyst_adapter.load()
    return revenue_adapter, chip_adapter, catalyst_adapter


def scan_candidates(
    config: dict[str, Any],
    as_of_date: str,
    top: int | None = None,
    by_symbol: dict[str, list[dict[str, Any]]] | None = None,
    min_coverage: float = 0.0,
    stage_filter: set[str] | None = None,
    include_degraded: bool = True,
) -> list[dict[str, Any]]:
    by_symbol = by_symbol if by_symbol is not None else load_daily_prices(config)
    features_by_symbol = compute_price_volume_features(by_symbol, as_of_date, config)
    theme_scores = score_theme_groups(features_by_symbol, config)
    revenue_adapter, chip_adapter, catalyst_adapter = _optional_data_adapters(config)
    weights = config["scoring"]["weights"]
    max_penalty = float(config["scoring"].get("risk_penalty_max", 40))
    created_at = datetime.now().isoformat(timespec="seconds")
    candidates: list[RadarCandidate] = []

    for symbol, features in features_by_symbol.items():
        revenue_features = compute_revenue_features(revenue_adapter.rows_until(symbol, as_of_date))
        chip_features = compute_chip_features(chip_adapter.rows_until(symbol, as_of_date))
        catalyst_features = compute_catalyst_features(catalyst_adapter.rows_for_symbol(symbol), as_of_date, config)
        features.update(revenue_features)
        features.update(chip_features)
        features.update(catalyst_features)

        scores = {
            "revenue": score_revenue(revenue_features),
            "expectation_gap": score_expectation_gap(features, config),
            "price_volume": score_price_volume(features),
            "theme_group": theme_scores.get(symbol),
            "chip": score_chip(chip_features),
            "catalyst": score_catalyst(catalyst_features),
        }
        degraded = [key for key, value in scores.items() if value is None]
        penalty, risk_flags = risk_penalty(features, max_penalty)
        breakdown = calculate_score_breakdown(scores, weights, penalty, degraded)
        if breakdown.data_coverage_ratio < min_coverage:
            continue
        if not include_degraded and breakdown.degraded_radars:
            continue

        stage, entry_zone = classify_stage(features, breakdown, penalty, scores["revenue"], config)
        if stage_filter and stage not in stage_filter:
            continue
        reasons, generated_risks = generate_reasons(features, scores, breakdown.degraded_radars)
        all_risks = risk_flags + generated_risks + degradation_risk_flags(
            breakdown.degraded_radars, breakdown.data_coverage_ratio
        )
        data_quality_flags = list(features.get("data_quality_flags") or [])
        data_quality_flags.extend(chip_features.get("chip_data_quality_flags") or [])

        candidates.append(
            RadarCandidate(
                rank=None,
                symbol=symbol,
                name=features.get("name"),
                industry=features.get("industry"),
                trade_date=features.get("trade_date") or as_of_date,
                universe_mode=features.get("universe_mode") or config.get("universe", {}).get("mode", "elastic"),
                score_total=_round(breakdown.score_total),
                score_raw_available_norm=_round(breakdown.score_raw_available_norm),
                score_coverage_adjusted=_round(breakdown.score_coverage_adjusted),
                score_cap=_round(breakdown.score_cap),
                data_coverage_ratio=_round(breakdown.data_coverage_ratio),
                available_radars=breakdown.available_radars,
                degraded_radars=breakdown.degraded_radars,
                core_data_ready_flag=breakdown.core_data_ready_flag,
                score_revenue=_round(scores["revenue"]),
                score_expectation_gap=_round(scores["expectation_gap"]),
                expectation_gap_source=features.get("expectation_gap_source", "price_only"),
                score_price_volume=_round(scores["price_volume"]),
                score_theme_group=_round(scores["theme_group"]),
                score_chip=_round(scores["chip"]),
                score_catalyst=_round(scores["catalyst"]),
                risk_penalty=_round(penalty),
                stage=stage,
                entry_zone=entry_zone,
                reasons=reasons,
                risk_flags=all_risks,
                last_close=features.get("last_close"),
                avg_amount_20=features.get("avg_amount_20"),
                ret_20d=features.get("ret_20d"),
                ret_60d=features.get("ret_60d"),
                ret_120d=features.get("ret_120d"),
                volume_z_20=features.get("volume_z_20"),
                volume_expansion_ratio=features.get("volume_expansion_ratio"),
                rs_20d=features.get("rs_20d"),
                rs_60d=features.get("rs_60d"),
                breakout_flag=features.get("breakout_flag", False),
                breakout_60d_flag=features.get("breakout_60d_flag", False),
                breakout_120d_flag=features.get("breakout_120d_flag", False),
                rev_1m_yoy=features.get("rev_1m_yoy"),
                rev_3m_yoy=features.get("rev_3m_yoy"),
                rev_6m_yoy=features.get("rev_6m_yoy"),
                rev_3m_vs_12m_acceleration=features.get("rev_3m_vs_12m_acceleration"),
                latest_revenue_month=features.get("latest_revenue_month"),
                latest_revenue_release_date=features.get("latest_revenue_release_date"),
                foreign_buy_5d=features.get("foreign_buy_5d"),
                investment_trust_buy_5d=features.get("investment_trust_buy_5d"),
                inst_buy_total_20d=features.get("inst_buy_total_20d"),
                margin_change_20d=features.get("margin_change_20d"),
                next_catalyst_date=features.get("next_catalyst_date"),
                next_catalyst_category=features.get("next_catalyst_category"),
                excluded_by_universe_flag=features.get("excluded_by_universe_flag", False),
                market_cap=features.get("market_cap"),
                share_capital=features.get("share_capital"),
                data_quality_flags=data_quality_flags,
                survivorship_bias_warning=features.get("survivorship_bias_warning"),
                has_delisted_data_flag=features.get("has_delisted_data_flag"),
                price_data_source=features.get("price_data_source"),
                revenue_data_source=config.get("data", {}).get("revenue_data_source"),
                chip_data_source=config.get("data", {}).get("chip_data_source"),
                created_at=created_at,
            )
        )

    candidates.sort(key=lambda item: item.score_total, reverse=True)
    if top:
        candidates = candidates[:top]

    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(candidates, 1):
        candidate.rank = rank
        rows.append(candidate.to_row())
    return rows

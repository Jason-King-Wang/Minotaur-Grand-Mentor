from __future__ import annotations

from datetime import datetime
from typing import Any

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
from short_term_radar.scoring.short_term_score import normalized_score
from short_term_radar.scoring.stage_classifier import classify_stage


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
    "stage",
    "entry_zone",
    "reasons",
    "risk_flags",
    "last_close",
    "ret_20d",
    "ret_60d",
    "volume_z_20",
    "rs_20d",
    "rs_60d",
    "breakout_flag",
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
    weights = config["scoring"]["weights"]
    max_penalty = float(config["scoring"].get("risk_penalty_max", 40))
    created_at = datetime.now().isoformat(timespec="seconds")
    candidates: list[RadarCandidate] = []

    for symbol, features in features_by_symbol.items():
        scores = {
            "revenue": score_revenue(),
            "expectation_gap": score_expectation_gap(features, config),
            "price_volume": score_price_volume(features),
            "theme_group": theme_scores.get(symbol),
            "chip": score_chip(),
            "catalyst": score_catalyst(),
        }
        degraded = [key for key, value in scores.items() if value is None]
        penalty, risk_flags = risk_penalty(features, max_penalty)
        total = normalized_score(scores, weights, penalty)
        stage, entry_zone = classify_stage(features, total, penalty)
        reasons, generated_risks = generate_reasons(features, scores, degraded)
        candidates.append(
            RadarCandidate(
                symbol=symbol,
                name=features.get("name"),
                industry=features.get("industry"),
                trade_date=features.get("trade_date") or as_of_date,
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
                reasons=reasons,
                risk_flags=risk_flags + generated_risks,
                last_close=features.get("last_close"),
                ret_20d=features.get("ret_20d"),
                ret_60d=features.get("ret_60d"),
                volume_z_20=features.get("volume_z_20"),
                rs_20d=features.get("rs_20d"),
                rs_60d=features.get("rs_60d"),
                breakout_flag=features.get("breakout_flag", False),
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

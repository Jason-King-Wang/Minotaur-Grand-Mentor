from __future__ import annotations

import random
from typing import Any


BASELINE_STRATEGIES = [
    "random_top_n",
    "breakout_120d_only",
    "volume_expansion_only",
    "ma_alignment_only",
]


def select_baseline_candidates(
    strategy_name: str,
    features_by_symbol: dict[str, dict[str, Any]],
    top_n: int,
    seed: int = 42,
    trial: int = 0,
) -> list[dict[str, Any]]:
    rows = list(features_by_symbol.values())
    if strategy_name == "random_top_n":
        rng = random.Random(seed + trial)
        shuffled = rows[:]
        rng.shuffle(shuffled)
        return shuffled[:top_n]
    if strategy_name == "breakout_120d_only":
        rows = [row for row in rows if row.get("breakout_120d_flag")]
        return sorted(
            rows,
            key=lambda row: (
                row.get("rs_20d") or -999,
                row.get("volume_expansion_ratio") or 0,
                -(row.get("ret_20d") or 0),
            ),
            reverse=True,
        )[:top_n]
    if strategy_name == "volume_expansion_only":
        rows = [
            row
            for row in rows
            if row.get("above_ma20_flag")
            and row.get("volume_expansion_ratio") is not None
            and 1.2 <= row["volume_expansion_ratio"] <= 3.5
        ]
        return sorted(
            rows,
            key=lambda row: (row.get("volume_expansion_ratio") or 0, row.get("rs_20d") or -999),
            reverse=True,
        )[:top_n]
    if strategy_name == "ma_alignment_only":
        rows = [
            row
            for row in rows
            if row.get("ma_alignment_bull_flag") and row.get("above_ma20_flag") and row.get("above_ma60_flag")
        ]
        return sorted(rows, key=lambda row: row.get("rs_60d") or -999, reverse=True)[:top_n]
    raise ValueError(f"Unknown baseline strategy: {strategy_name}")

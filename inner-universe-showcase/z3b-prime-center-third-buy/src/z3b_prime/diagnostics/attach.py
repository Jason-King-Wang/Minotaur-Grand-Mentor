from __future__ import annotations

from z3b_prime.config import MacdConfig
from z3b_prime.diagnostics.macd_zero_axis import classify_zero_axis
from z3b_prime.indicators.macd import macd
from z3b_prime.models import Bar, Center


def attach_macd_zero_axis_diagnostics(
    centers: list[Center],
    bars: list[Bar],
    config: MacdConfig,
) -> None:
    values = macd([bar.close for bar in bars], config.fast, config.slow, config.signal)
    for center in centers:
        segment = values[center.start_index : center.end_index + 1]
        center.macd_level_diag = classify_zero_axis(
            [item["dif"] for item in segment],
            [item["dea"] for item in segment],
        )

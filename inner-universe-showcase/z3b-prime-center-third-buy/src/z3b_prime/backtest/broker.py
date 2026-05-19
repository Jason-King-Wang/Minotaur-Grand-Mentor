from __future__ import annotations

from z3b_prime import reason_codes
from z3b_prime.models import Bar


def next_bar_open(bar: Bar) -> float:
    return bar.open


def stop_take_exit_reason(bar: Bar, stop_loss: float, take_profit: float) -> str | None:
    stop_hit = bar.low <= stop_loss
    target_hit = bar.high >= take_profit
    if stop_hit:
        return reason_codes.AMBIGUOUS_BAR_STOP_FIRST if target_hit else "STOP_LOSS"
    if target_hit:
        return "TAKE_PROFIT"
    return None

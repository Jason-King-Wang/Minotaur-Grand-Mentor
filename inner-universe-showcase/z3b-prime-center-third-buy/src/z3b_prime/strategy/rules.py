from __future__ import annotations

from z3b_prime import reason_codes
from z3b_prime.models import Bar, Center, Leg, SwingPoint, TradeSignal


def has_upward_leave(bar_1h: Bar, center: Center) -> bool:
    return bar_1h.close > center.upper


def pullback_holds_center_upper(bar_1h: Bar, center: Center) -> bool:
    return bar_1h.low >= center.upper


def a_b_goes_to_bA_path(a_leg: Leg, b_leg: Leg) -> bool:
    return b_leg.length > a_leg.length


def a_b_direct_entry_allowed_v1_1(a_leg: Leg, b_leg: Leg) -> bool:
    return False


def bA_is_smaller_than_A(
    center_A: Center,
    center_bA: Center,
    max_range_ratio: float = 0.8,
    max_duration_ratio: float = 0.8,
    max_score_ratio: float = 0.8,
) -> bool:
    if center_A.id == center_bA.id:
        return False
    if center_A.range <= 0 or center_A.duration_bars <= 0 or center_A.score <= 0:
        return center_bA.range < center_A.range
    return (
        center_bA.range <= center_A.range * max_range_ratio
        and center_bA.duration_bars <= center_A.duration_bars * max_duration_ratio
        and center_bA.score <= center_A.score * max_score_ratio
    )


def bb_less_than_ba(ba_leg: Leg, bb_leg: Leg) -> bool:
    return bb_leg.length < ba_leg.length


def bb_low_holds_ba_low(ba_leg: Leg, bb_leg: Leg) -> bool:
    return bb_leg.end_price >= ba_leg.end_price


def isolated_lows_hold(first_low: SwingPoint, second_low: SwingPoint) -> bool:
    if first_low.kind != "low" or second_low.kind != "low":
        raise ValueError("isolated lows must be low swing points")
    return second_low.price >= first_low.price


def is_bullish_trend_k(
    bar: Bar,
    terminal_center: Center,
    body_ratio_of_ba_range: float = 0.25,
    min_body_range_ratio: float = 0.60,
    max_upper_wick_ratio: float = 0.20,
    min_close_position: float = 0.75,
    local_resistance: float | None = None,
    require_close_above_local_resistance: bool = False,
) -> bool:
    body = bar.close - bar.open
    full_range = bar.high - bar.low
    if body <= 0 or full_range <= 0:
        return False
    upper_wick = bar.high - bar.close
    close_position = (bar.close - bar.low) / full_range
    if body / full_range < min_body_range_ratio:
        return False
    if upper_wick / full_range > max_upper_wick_ratio:
        return False
    if close_position < min_close_position:
        return False
    if body < body_ratio_of_ba_range * terminal_center.range:
        return False
    if require_close_above_local_resistance and local_resistance is not None:
        return bar.close > local_resistance
    return True


def build_long_signal(
    *,
    strategy_id: str,
    symbol: str,
    bullish_k: Bar,
    next_bar: Bar,
    target_high_1h: float,
    stop_loss: float | None = None,
    metadata: dict | None = None,
) -> TradeSignal:
    entry_price = next_bar.open
    stop_loss = bullish_k.low if stop_loss is None else stop_loss
    take_profit = target_high_1h

    if entry_price <= stop_loss:
        raise ValueError(reason_codes.INVALID_RISK_ENTRY_LE_STOP)
    if take_profit <= entry_price:
        raise ValueError(reason_codes.INVALID_TARGET_LE_ENTRY)

    rr = (take_profit - entry_price) / (entry_price - stop_loss)
    return TradeSignal(
        strategy_id=strategy_id,
        symbol=symbol,
        signal_time=bullish_k.close_time,
        entry_time=next_bar.time,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        rr=rr,
        reason_code=reason_codes.VALID_LONG_SIGNAL,
        metadata=metadata or {},
    )

from __future__ import annotations

from dataclasses import dataclass

from z3b_prime import reason_codes
from z3b_prime.config import StrategyConfig
from z3b_prime.diagnostics.attach import attach_macd_zero_axis_diagnostics
from z3b_prime.market_structure.centers import detect_price_centers
from z3b_prime.market_structure.legs import (
    build_a_leg_and_b_start,
    build_ba_bb_legs_from_b_start,
    find_isolated_lows,
)
from z3b_prime.market_structure.swings import detect_swings
from z3b_prime.models import Bar, Center, SignalEvent, SwingPoint, TradeSignal
from z3b_prime.strategy import rules
from z3b_prime.strategy.state_machine import State, Z3BPrimeStateMachine


@dataclass
class StrategyRunResult:
    signals: list[TradeSignal]
    signal_log: list[SignalEvent]
    swings_1h: list[SwingPoint]
    swings_15m: list[SwingPoint]
    centers_1h: list[Center]
    centers_15m: list[Center]


@dataclass(frozen=True)
class OneHourThirdBuySetup:
    center: Center
    prior_breakout_high: SwingPoint
    center_down_break_index: int
    previous_high: SwingPoint
    pullback_low_before_breakout: SwingPoint
    breakout_high: SwingPoint
    third_buy_low: SwingPoint
    segment_start_time: object
    target_high_1h: float


def run_strategy(
    symbol: str,
    bars_1h: list[Bar],
    bars_15m: list[Bar],
    config: StrategyConfig,
    stop_after_first_signal: bool = True,
) -> StrategyRunResult:
    bars_1h = sorted(bars_1h, key=lambda bar: bar.time)
    bars_15m = sorted(bars_15m, key=lambda bar: bar.time)
    events: list[SignalEvent] = []
    signals: list[TradeSignal] = []

    swings_1h = detect_swings(
        bars_1h,
        config.swing.left_bars,
        config.swing.right_bars,
    )
    swings_15m = detect_swings(
        bars_15m,
        config.swing.left_bars,
        config.swing.right_bars,
    )
    centers_1h = detect_price_centers(
        bars_1h,
        swings_1h,
        config.center_detection.min_center_swings,
        config.center_detection.min_center_bars,
        config.center_detection.min_midline_crosses,
    )
    centers_15m = detect_price_centers(
        bars_15m,
        swings_15m,
        config.center_detection.min_center_swings,
        config.center_detection.min_center_bars,
        config.center_detection.min_midline_crosses,
    )
    attach_macd_zero_axis_diagnostics(centers_1h, bars_1h, config.macd)
    attach_macd_zero_axis_diagnostics(centers_15m, bars_15m, config.macd)

    if not centers_1h:
        log_event(events, config, symbol, bars_1h[-1], State.WAIT_1H_CENTER, reason_codes.NO_1H_CENTER)

    for center_1h in sorted(centers_1h, key=lambda center: center.end_index):
        machine = Z3BPrimeStateMachine()
        machine.transition(State.WAIT_1H_UPWARD_LEAVE)
        machine.transition(State.WAIT_1H_STRUCTURE_BREAK)
        machine.transition(State.WAIT_1H_PULLBACK_3BUY)
        setup = find_user_1h_third_buy_setup(bars_1h, swings_1h, center_1h)
        if setup is None:
            log_event(
                events,
                config,
                symbol,
                bars_1h[center_1h.end_index],
                machine.state,
                reason_codes.NO_1H_PULLBACK_3BUY,
                {"center_id": center_1h.id},
            )
            continue

        machine.transition(State.WAIT_15M_CENTER_A)
        segment_start = setup.segment_start_time
        segment_end = bars_15m[-1].close_time
        signal = evaluate_15m_entry_path(
            symbol=symbol,
            bars_15m=bars_15m,
            swings_15m=swings_15m,
            centers_15m=centers_15m,
            center_1h=center_1h,
            target_high_1h=setup.target_high_1h,
            segment_start=segment_start,
            segment_end=segment_end,
            config=config,
            events=events,
            machine=machine,
        )
        if signal is not None:
            signals.append(signal)
            machine.transition(State.IN_POSITION)
            if stop_after_first_signal:
                break

    return StrategyRunResult(
        signals=signals,
        signal_log=events,
        swings_1h=swings_1h,
        swings_15m=swings_15m,
        centers_1h=centers_1h,
        centers_15m=centers_15m,
    )


def find_upward_leave_index(bars: list[Bar], center: Center) -> int | None:
    for index in range(center.end_index + 1, len(bars)):
        if rules.has_upward_leave(bars[index], center):
            return index
    return None


def find_structure_break_index(
    bars: list[Bar],
    swings: list[SwingPoint],
    center: Center,
    start_index: int,
) -> int | None:
    prior_highs = [
        swing
        for swing in swings
        if swing.kind == "high"
        and swing.bar_index < start_index
        and swing.confirmed_time <= bars[start_index].close_time
    ]
    threshold = max((swing.price for swing in prior_highs), default=center.upper)
    for index in range(start_index, len(bars)):
        if bars[index].close > threshold:
            return index
    return None


def find_user_1h_third_buy_setup(
    bars: list[Bar],
    swings: list[SwingPoint],
    center: Center,
) -> OneHourThirdBuySetup | None:
    center_high = center.box_high if center.box_high is not None else center.upper
    prior_breakout_high = latest_breakout_high_before_center(swings, center.start_index)
    if prior_breakout_high is None:
        return None

    down_break_index = find_center_down_break_index(bars, swings, center)
    if down_break_index is None:
        return None

    previous_high = first_high_after_center_not_above_center_high(
        swings,
        down_break_index,
        center_high,
    )
    if previous_high is None:
        return None

    pullback_low = first_swing_after(swings, "low", previous_high.bar_index)
    if pullback_low is None:
        return None

    breakout_high = first_breakout_high_after_low(
        swings,
        start_index=pullback_low.bar_index,
        threshold=previous_high.price,
    )
    if breakout_high is None:
        return None

    third_buy_low = first_swing_after(swings, "low", breakout_high.bar_index)
    if third_buy_low is None:
        return None

    return OneHourThirdBuySetup(
        center=center,
        prior_breakout_high=prior_breakout_high,
        center_down_break_index=down_break_index,
        previous_high=previous_high,
        pullback_low_before_breakout=pullback_low,
        breakout_high=breakout_high,
        third_buy_low=third_buy_low,
        segment_start_time=breakout_high.time,
        target_high_1h=breakout_high.price,
    )


def latest_breakout_high_before_center(
    swings: list[SwingPoint],
    center_start_index: int,
) -> SwingPoint | None:
    highest_so_far: float | None = None
    latest_breakout: SwingPoint | None = None
    for swing in swings:
        if swing.bar_index >= center_start_index:
            break
        if swing.kind != "high":
            continue
        if highest_so_far is not None and swing.price > highest_so_far:
            latest_breakout = swing
        highest_so_far = swing.price if highest_so_far is None else max(highest_so_far, swing.price)
    return latest_breakout


def find_center_down_break_index(
    bars: list[Bar],
    swings: list[SwingPoint],
    center: Center,
) -> int | None:
    center_low = center.box_low if center.box_low is not None else center.lower
    close_break_index = None
    for index in range(center.end_index + 1, len(bars)):
        if bars[index].close < center_low:
            close_break_index = index
            break
    if close_break_index is None:
        return None

    for swing in swings:
        if swing.kind != "low" or swing.bar_index < close_break_index:
            continue
        if swing.price < center_low:
            return swing.bar_index
    return None


def first_high_after_center_not_above_center_high(
    swings: list[SwingPoint],
    center_end_index: int,
    center_high: float,
) -> SwingPoint | None:
    for swing in swings:
        if swing.bar_index <= center_end_index or swing.kind != "high":
            continue
        if swing.price <= center_high:
            return swing
    return None


def first_breakout_high_after_low(
    swings: list[SwingPoint],
    start_index: int,
    threshold: float,
) -> SwingPoint | None:
    for swing in swings:
        if swing.bar_index <= start_index or swing.kind != "high":
            continue
        if swing.price > threshold:
            return swing
    return None


def first_swing_after(
    swings: list[SwingPoint],
    kind: str,
    start_index: int,
) -> SwingPoint | None:
    for swing in swings:
        if swing.bar_index > start_index and swing.kind == kind:
            return swing
    return None


def find_pullback_3buy_index(
    bars: list[Bar],
    center: Center,
    start_index: int,
) -> tuple[int, float] | None:
    impulse_high = bars[start_index].high
    for index in range(start_index + 1, len(bars)):
        bar = bars[index]
        if bar.low < center.upper:
            return None
        if bar.high > impulse_high:
            impulse_high = bar.high
            continue
        if rules.pullback_holds_center_upper(bar, center) and bar.close < impulse_high:
            return index, impulse_high
    return None


def evaluate_15m_entry_path(
    *,
    symbol: str,
    bars_15m: list[Bar],
    swings_15m: list[SwingPoint],
    centers_15m: list[Center],
    center_1h: Center,
    target_high_1h: float,
    segment_start,
    segment_end,
    config: StrategyConfig,
    events: list[SignalEvent],
    machine: Z3BPrimeStateMachine,
) -> TradeSignal | None:
    a_cache = {}
    ba_bb_cache = {}
    center_A_candidates = [
        center
        for center in centers_15m
        if center.start_time >= segment_start and center.start_time <= segment_end
    ]
    if not center_A_candidates:
        log_event(
            events,
            config,
            symbol,
            bars_15m[-1],
            machine.state,
            reason_codes.NO_15M_CENTER_A,
        )
        return None

    for center_A in sorted(center_A_candidates, key=lambda center: (center.end_index, -center.score)):
        machine.state = State.WAIT_15M_AB_COMPARE
        if center_A.id not in a_cache:
            a_cache[center_A.id] = build_a_leg_and_b_start(center_A, swings_15m)
        a_and_b_start = a_cache[center_A.id]
        if a_and_b_start is None:
            log_event(
                events,
                config,
                symbol,
                bar_at_or_last(bars_15m, center_A.end_index),
                machine.state,
                reason_codes.NO_AB_LEGS,
                {"center_A": center_A.id},
            )
            continue
        a_leg, b_start_high = a_and_b_start

        machine.state = State.WAIT_15M_BA_CENTER
        bA_candidates = [
            center
            for center in centers_15m
            if center.id != center_A.id
            and center.start_index >= center_A.end_index
            and center.end_index > center_A.end_index
            and center.start_index > b_start_high.bar_index
        ]
        if not bA_candidates:
            log_event(
                events,
                config,
                symbol,
                bar_at_or_last(bars_15m, center_A.end_index),
                machine.state,
                reason_codes.NO_BA_CENTER,
            )
            continue

        for center_bA in sorted(bA_candidates, key=lambda center: (center.end_index, center.range)):
            if not rules.bA_is_smaller_than_A(center_A, center_bA):
                log_event(
                    events,
                    config,
                    symbol,
                    bar_at_or_last(bars_15m, center_bA.end_index),
                    machine.state,
                    reason_codes.NO_SMALLER_BA_CENTER,
                    {"center_A_range": center_A.range, "center_bA_range": center_bA.range},
                )
                continue

            machine.state = State.WAIT_15M_BA_BB_COMPARE
            if center_bA.id not in ba_bb_cache:
                ba_bb_cache[center_bA.id] = build_ba_bb_legs_from_b_start(
                    center_bA,
                    swings_15m,
                    b_start_high,
                )
            ba_bb = ba_bb_cache[center_bA.id]
            if ba_bb is None:
                log_event(
                    events,
                    config,
                    symbol,
                    bar_at_or_last(bars_15m, center_bA.end_index),
                    machine.state,
                    reason_codes.NO_BA_BB_LEGS,
                )
                continue
            ba_leg, bb_leg = ba_bb
            b_length = b_start_high.price - bb_leg.end_price
            if b_length <= a_leg.length:
                log_event(
                    events,
                    config,
                    symbol,
                    bar_at_or_last(bars_15m, center_bA.end_index),
                    machine.state,
                    reason_codes.B_EQUAL_A_NOT_CLEAR,
                    {"a_length": a_leg.length, "b_length": b_length},
                )
                continue
            if not rules.bb_less_than_ba(ba_leg, bb_leg):
                log_event(
                    events,
                    config,
                    symbol,
                    bar_at_or_last(bars_15m, center_bA.end_index),
                    machine.state,
                    reason_codes.BB_NOT_LESS_THAN_BA,
                    {"ba_length": ba_leg.length, "bb_length": bb_leg.length},
                )
                continue
            if not rules.bb_low_holds_ba_low(ba_leg, bb_leg):
                log_event(
                    events,
                    config,
                    symbol,
                    bar_at_or_last(bars_15m, center_bA.end_index),
                    machine.state,
                    reason_codes.SECOND_LOW_BROKE_FIRST_LOW,
                    {"ba_low": ba_leg.end_price, "bb_low": bb_leg.end_price},
                )
                continue

            machine.transition(State.WAIT_15M_ISOLATED_LOWS_AND_GOLDEN_K)
            machine.transition(State.WAIT_15M_BULLISH_TREND_K)
            signal = find_bullish_signal(
                bars_15m=bars_15m,
                swings_15m=swings_15m,
                start_index=max(center_bA.end_index + 1, (bb_leg.end_index or 0) + 1),
                center_1h=center_1h,
                center_A=center_A,
                terminal_center=center_bA,
                a_length=a_leg.length,
                b_length=b_length,
                ba_length=ba_leg.length,
                bb_length=bb_leg.length,
                iso_low_1=ba_leg.end_price,
                iso_low_2=bb_leg.end_price,
                iso_low_2_index=bb_leg.end_index or center_bA.end_index,
                golden_k=bars_15m[bb_leg.end_index or center_bA.end_index],
                target_high_1h=target_high_1h,
                path_name="nested_bA_user_spec",
                config=config,
            )
            if signal is not None:
                return signal
            log_event(
                events,
                config,
                symbol,
                bar_at_or_last(bars_15m, center_bA.end_index),
                machine.state,
                reason_codes.NO_BULLISH_TREND_K,
            )
    return None


def confirm_two_lows_and_bullish_k(
    symbol: str,
    bars_15m: list[Bar],
    swings_15m: list[SwingPoint],
    center_1h: Center,
    center_A: Center,
    terminal_center: Center,
    target_high_1h: float,
    a_length: float,
    b_length: float,
    ba_length: float | None,
    bb_length: float | None,
    path_name: str,
    config: StrategyConfig,
    events: list[SignalEvent],
    machine: Z3BPrimeStateMachine,
) -> TradeSignal | None:
    lows = find_isolated_lows(terminal_center, swings_15m)
    if lows is None:
        log_event(
            events,
            config,
            symbol,
            bar_at_or_last(bars_15m, terminal_center.end_index),
            machine.state,
            reason_codes.NO_ISOLATED_LOWS,
            {"path": path_name},
        )
        return None
    iso1, iso2 = lows
    if not rules.isolated_lows_hold(iso1, iso2):
        log_event(
            events,
            config,
            symbol,
            bar_at_or_last(bars_15m, iso2.bar_index),
            machine.state,
            reason_codes.SECOND_LOW_BROKE_FIRST_LOW,
            {"path": path_name},
        )
        return None
    golden_k = resolve_golden_k_from_iso_low_2(iso2, bars_15m)
    if golden_k is None:
        log_event(
            events,
            config,
            symbol,
            bar_at_or_last(bars_15m, iso2.bar_index),
            machine.state,
            reason_codes.NO_GOLDEN_K_FOR_SECOND_LOW,
            {"path": path_name},
        )
        return None

    machine.state = State.WAIT_15M_BULLISH_TREND_K
    return find_bullish_signal(
        bars_15m=bars_15m,
        swings_15m=swings_15m,
        start_index=max(terminal_center.end_index + 1, iso2.bar_index + 1),
        center_1h=center_1h,
        center_A=center_A,
        terminal_center=terminal_center,
        a_length=a_length,
        b_length=b_length,
        ba_length=ba_length,
        bb_length=bb_length,
        iso_low_1=iso1.price,
        iso_low_2=iso2.price,
        iso_low_2_index=iso2.bar_index,
        golden_k=golden_k,
        target_high_1h=target_high_1h,
        path_name=path_name,
        config=config,
    )


def find_bullish_signal(
    *,
    bars_15m: list[Bar],
    swings_15m: list[SwingPoint],
    start_index: int,
    center_1h: Center,
    center_A: Center,
    terminal_center: Center,
    a_length: float,
    b_length: float,
    ba_length: float | None,
    bb_length: float | None,
    iso_low_1: float,
    iso_low_2: float,
    iso_low_2_index: int,
    golden_k: Bar,
    target_high_1h: float,
    path_name: str,
    config: StrategyConfig,
) -> TradeSignal | None:
    start_index = max(start_index, golden_k.bar_index + 1 if hasattr(golden_k, "bar_index") else start_index)
    max_bars = config.entry_confirmation.bullish_k_max_bars_after_low2
    stop_index = min(len(bars_15m) - 1, iso_low_2_index + max_bars + 1)
    for index in range(start_index, stop_index):
        bar = bars_15m[index]
        if bar.close_time <= golden_k.close_time:
            continue
        local_resistance = local_resistance_before_bar(
            swings_15m,
            terminal_center,
            low_2_index=iso_low_2_index,
            bar_index=index,
            bar_time=bar.close_time,
            direct_path=path_name == "direct_A_exhaustion",
        )
        if not rules.is_bullish_trend_k(
            bar,
            terminal_center,
            config.entry_confirmation.bullish_k_body_ratio_of_ba_range,
            config.entry_confirmation.bullish_k_min_body_range_ratio,
            config.entry_confirmation.bullish_k_max_upper_wick_ratio,
            config.entry_confirmation.bullish_k_min_close_position,
            local_resistance,
            config.entry_confirmation.bullish_k_require_close_above_local_resistance,
        ):
            continue
        next_bar = bars_15m[index + 1]
        metadata = structure_metadata(
            center_1h=center_1h,
            center_A=center_A,
            terminal_center=terminal_center,
            a_length=a_length,
            b_length=b_length,
            ba_length=ba_length,
            bb_length=bb_length,
            iso_low_1=iso_low_1,
            iso_low_2=iso_low_2,
            golden_k=golden_k,
            bullish_k=bar,
            path_name=path_name,
            local_resistance=local_resistance,
        )
        try:
            return rules.build_long_signal(
                strategy_id=config.strategy_id,
                symbol=bar.symbol,
                bullish_k=bar,
                next_bar=next_bar,
                target_high_1h=target_high_1h,
                stop_loss=golden_k.low,
                metadata=metadata,
            )
        except ValueError:
            return None
    return None


def structure_metadata(
    *,
    center_1h: Center,
    center_A: Center,
    terminal_center: Center,
    a_length: float,
    b_length: float,
    ba_length: float | None,
    bb_length: float | None,
    iso_low_1: float,
    iso_low_2: float,
    golden_k: Bar,
    bullish_k: Bar,
    path_name: str,
    local_resistance: float | None,
) -> dict:
    is_nested = path_name.startswith("nested_bA")
    return {
        "entry_path": path_name,
        "center_1h_start": center_1h.start_time,
        "center_1h_end": center_1h.end_time,
        "center_1h_upper": center_1h.upper,
        "center_1h_lower": center_1h.lower,
        "center_1h_box_high": center_1h.box_high,
        "center_1h_box_low": center_1h.box_low,
        "center_1h_score": center_1h.score,
        "center_1h_macd_diag": center_1h.macd_level_diag,
        "center_A_15m_start": center_A.start_time,
        "center_A_15m_end": center_A.end_time,
        "center_A_upper": center_A.upper,
        "center_A_lower": center_A.lower,
        "center_A_box_high": center_A.box_high,
        "center_A_box_low": center_A.box_low,
        "center_A_score": center_A.score,
        "center_A_macd_diag": center_A.macd_level_diag,
        "a_length": a_length,
        "b_length": b_length,
        "center_bA_15m_start": terminal_center.start_time if is_nested else "",
        "center_bA_15m_end": terminal_center.end_time if is_nested else "",
        "center_bA_upper": terminal_center.upper if is_nested else "",
        "center_bA_lower": terminal_center.lower if is_nested else "",
        "center_bA_score": terminal_center.score if is_nested else "",
        "center_bA_macd_diag": terminal_center.macd_level_diag if is_nested else "",
        "ba_length": ba_length,
        "bb_length": bb_length,
        "iso_low_1": iso_low_1,
        "iso_low_2": iso_low_2,
        "local_resistance": local_resistance,
        "golden_k_time": golden_k.close_time,
        "golden_k_open": golden_k.open,
        "golden_k_high": golden_k.high,
        "golden_k_low": golden_k.low,
        "golden_k_close": golden_k.close,
        "bullish_k_time": bullish_k.close_time,
        "bullish_k_low": bullish_k.low,
    }


def local_resistance_before_bar(
    swings_15m: list[SwingPoint],
    terminal_center: Center,
    *,
    low_2_index: int,
    bar_index: int,
    bar_time,
    direct_path: bool,
) -> float | None:
    resistance = None if direct_path else terminal_center.upper
    for swing in swings_15m:
        if swing.kind != "high":
            continue
        if swing.bar_index <= low_2_index or swing.bar_index >= bar_index:
            continue
        if swing.confirmed_time > bar_time:
            continue
        resistance = swing.price if resistance is None else max(resistance, swing.price)
    return resistance


def resolve_golden_k_from_iso_low_2(iso_low_2: SwingPoint, bars_15m: list[Bar]) -> Bar | None:
    if iso_low_2.bar_index < 0 or iso_low_2.bar_index >= len(bars_15m):
        return None
    return bars_15m[iso_low_2.bar_index]


def log_event(
    events: list[SignalEvent],
    config: StrategyConfig,
    symbol: str,
    bar: Bar,
    state: State,
    reason_code: str,
    metadata: dict | None = None,
) -> None:
    events.append(
        SignalEvent(
            strategy_id=config.strategy_id,
            symbol=symbol,
            time=bar.close_time,
            state=state.value if isinstance(state, State) else str(state),
            reason_code=reason_code,
            metadata=metadata or {},
        )
    )


def bar_at_or_last(bars: list[Bar], index: int) -> Bar:
    index = max(0, min(index, len(bars) - 1))
    return bars[index]

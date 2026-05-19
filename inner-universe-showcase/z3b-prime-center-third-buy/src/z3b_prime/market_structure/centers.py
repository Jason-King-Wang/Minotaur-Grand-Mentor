from __future__ import annotations

from z3b_prime.models import Bar, Center, Leg, SwingPoint


def detect_price_centers(
    bars: list[Bar],
    swings: list[SwingPoint],
    min_center_swings: int = 4,
    min_center_bars: int = 5,
    min_midline_crosses: int = 2,
) -> list[Center]:
    """Detect simplified Chan-style centers with leg-overlap extension.

    Z3B-Core v2 treats center.upper/lower as the overlap zone, not the visual
    box extremes. Box extremes are still stored for charting/debug metadata.
    Once a center is active, later legs extend it while they intersect the core
    overlap zone. The core zone stays fixed; only box and right edge update.
    """
    centers: list[Center] = []
    if min_center_swings < 4:
        raise ValueError("min_center_swings should be at least 4")

    if len(swings) < min_center_swings:
        return centers

    legs = build_swing_legs(swings)
    seed_leg_count = min_center_swings - 1
    active: Center | None = None
    next_seed_start_leg = 0

    for leg_index, leg in enumerate(legs):
        if active is not None and leg_index >= next_seed_start_leg:
            if leg_intersects_center(leg, active):
                extend_center(active, leg, bars)
                continue

            complete_center(active, leg)
            centers.append(active)
            active = None
            next_seed_start_leg = leg_index

        if active is None and leg_index - seed_leg_count + 1 >= next_seed_start_leg:
            seed_legs = legs[leg_index - seed_leg_count + 1 : leg_index + 1]
            center = try_create_center_from_seed(
                bars,
                seed_legs,
                min_center_bars=min_center_bars,
                min_midline_crosses=min_midline_crosses,
            )
            if center is not None:
                active = center

    if active is not None:
        centers.append(active)
    return centers


def build_swing_legs(swings: list[SwingPoint]) -> list[Leg]:
    legs: list[Leg] = []
    for left, right in zip(swings, swings[1:]):
        if left.kind == right.kind:
            continue
        direction = "up" if right.price >= left.price else "down"
        legs.append(
            Leg(
                name=f"center-leg-{left.bar_index}-{right.bar_index}",
                start_time=left.time,
                end_time=right.time,
                start_price=left.price,
                end_price=right.price,
                direction=direction,
                length=abs(right.price - left.price),
                start_index=left.bar_index,
                end_index=right.bar_index,
                confirmed_time=right.confirmed_time,
            )
        )
    return legs


def try_create_center_from_seed(
    bars: list[Bar],
    seed_legs: list[Leg],
    min_center_bars: int,
    min_midline_crosses: int,
) -> Center | None:
    if len(seed_legs) < 3:
        return None

    start_index = seed_legs[0].start_index
    end_index = seed_legs[-1].end_index
    if start_index is None or end_index is None:
        return None

    window = bars[start_index : end_index + 1]
    if len(window) < min_center_bars:
        return None

    core = calc_center_core(seed_legs)
    if core is None:
        return None

    lower, upper = core
    mid = (upper + lower) / 2
    crosses = count_midline_crosses(window, mid)
    if crosses < min_midline_crosses:
        return None

    box_high, box_low = calc_box_from_bars_or_legs(bars, start_index, end_index, seed_legs)
    center_range = upper - lower
    duration = len(window)
    return Center(
        id=f"{bars[start_index].symbol}-{bars[start_index].timeframe}-{start_index}-{end_index}",
        symbol=bars[start_index].symbol,
        timeframe=bars[start_index].timeframe,
        start_time=bars[start_index].close_time,
        end_time=bars[end_index].close_time,
        upper=upper,
        lower=lower,
        mid=mid,
        range=center_range,
        duration_bars=duration,
        score=center_range * duration,
        start_index=start_index,
        end_index=end_index,
        confirmed_time=max(leg.confirmed_time for leg in seed_legs if leg.confirmed_time is not None),
        overlap_upper=upper,
        overlap_lower=lower,
        box_high=box_high,
        box_low=box_low,
        member_leg_count=len(seed_legs),
        state="active",
        source_type="swing_simplified",
        midline_crosses=crosses,
    )


def calc_center_core(legs: list[Leg]) -> tuple[float, float] | None:
    lower = max(min(leg.start_price, leg.end_price) for leg in legs)
    upper = min(max(leg.start_price, leg.end_price) for leg in legs)
    if lower > upper:
        return None
    return lower, upper


def leg_intersects_center(leg: Leg, center: Center) -> bool:
    leg_low = min(leg.start_price, leg.end_price)
    leg_high = max(leg.start_price, leg.end_price)
    return leg_high >= center.lower and leg_low <= center.upper


def complete_center(center: Center, leg: Leg) -> None:
    leg_low = min(leg.start_price, leg.end_price)
    leg_high = max(leg.start_price, leg.end_price)
    if leg_low > center.upper:
        center.break_dir = "up"
    elif leg_high < center.lower:
        center.break_dir = "down"
    center.state = "completed"
    center.completed_time = leg.confirmed_time


def extend_center(center: Center, leg: Leg, bars: list[Bar]) -> None:
    if leg.end_index is None:
        return
    center.end_index = leg.end_index
    center.end_time = bars[leg.end_index].close_time
    center.duration_bars = center.end_index - center.start_index + 1
    center.member_leg_count += 1
    center.extension_count += 1
    center.confirmed_time = leg.confirmed_time

    box_high, box_low = calc_box_from_bars_or_legs(
        bars,
        center.start_index,
        center.end_index,
        [leg],
        fallback_box_high=center.box_high,
        fallback_box_low=center.box_low,
    )
    center.box_high = box_high
    center.box_low = box_low
    center.midline_crosses = count_midline_crosses(
        bars[center.start_index : center.end_index + 1],
        center.mid,
    )
    center.score = center.range * center.duration_bars


def calc_box_from_bars_or_legs(
    bars: list[Bar],
    start_index: int,
    end_index: int,
    legs: list[Leg],
    fallback_box_high: float | None = None,
    fallback_box_low: float | None = None,
) -> tuple[float, float]:
    window = bars[start_index : end_index + 1]
    if window:
        return max(bar.high for bar in window), min(bar.low for bar in window)

    leg_high = max(max(leg.start_price, leg.end_price) for leg in legs)
    leg_low = min(min(leg.start_price, leg.end_price) for leg in legs)
    if fallback_box_high is not None:
        leg_high = max(fallback_box_high, leg_high)
    if fallback_box_low is not None:
        leg_low = min(fallback_box_low, leg_low)
    return leg_high, leg_low


def is_alternating(swings: list[SwingPoint]) -> bool:
    return all(prev.kind != curr.kind for prev, curr in zip(swings, swings[1:]))


def count_midline_crosses(bars: list[Bar], mid: float) -> int:
    signs: list[int] = []
    for bar in bars:
        if bar.close > mid:
            signs.append(1)
        elif bar.close < mid:
            signs.append(-1)
        else:
            signs.append(0)

    compact = [sign for sign in signs if sign != 0]
    return sum(1 for prev, curr in zip(compact, compact[1:]) if prev != curr)


def select_main_center(centers: list[Center]) -> Center | None:
    if not centers:
        return None
    return sorted(centers, key=lambda center: (center.score, center.end_time))[-1]

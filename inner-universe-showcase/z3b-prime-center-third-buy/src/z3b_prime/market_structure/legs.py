from __future__ import annotations

from z3b_prime.models import Leg, SwingPoint


def down_leg(name: str, start_high: SwingPoint, end_low: SwingPoint) -> Leg:
    if start_high.kind != "high" or end_low.kind != "low":
        raise ValueError("down_leg requires a high swing followed by a low swing")
    if end_low.bar_index <= start_high.bar_index:
        raise ValueError("end_low must come after start_high")
    if end_low.price >= start_high.price:
        raise ValueError("down_leg requires a lower low than the starting high")
    return Leg(
        name=name,
        start_time=start_high.time,
        end_time=end_low.time,
        start_price=start_high.price,
        end_price=end_low.price,
        direction="down",
        length=start_high.price - end_low.price,
        start_index=start_high.bar_index,
        end_index=end_low.bar_index,
    )


def first_down_leg_after(swings: list[SwingPoint], start_index: int, name: str) -> Leg | None:
    for high, low in zip(swings, swings[1:]):
        if high.bar_index < start_index:
            continue
        if high.kind == "high" and low.kind == "low":
            try:
                return down_leg(name, high, low)
            except ValueError:
                continue
    return None


def build_ab_legs(center, swings: list[SwingPoint]) -> tuple[Leg, Leg] | None:
    high_before = latest_swing(swings, "high", before_index=center.start_index)
    if high_before is None:
        high_before = first_swing(
            swings, "high", start_index=center.start_index, end_index=center.end_index
        )
    if high_before is None:
        return None

    low_inside = first_swing(
        swings,
        "low",
        start_index=high_before.bar_index + 1,
        end_index=center.end_index,
    )
    high_inside = latest_swing(
        swings,
        "high",
        start_index=(low_inside.bar_index + 1 if low_inside else center.start_index),
        end_index=center.end_index,
    )
    low_after = first_swing(
        swings,
        "low",
        start_index=(high_inside.bar_index + 1 if high_inside else center.end_index + 1),
    )

    if not all([high_before, low_inside, high_inside, low_after]):
        return None
    try:
        return down_leg("a", high_before, low_inside), down_leg("b", high_inside, low_after)
    except ValueError:
        return None


def build_a_leg_and_b_start(
    center,
    swings: list[SwingPoint],
) -> tuple[Leg, SwingPoint] | None:
    """Build user-spec A-front pullback and locate the start high of b."""
    high_before = latest_swing(swings, "high", before_index=center.start_index)
    if high_before is None:
        high_before = first_swing(
            swings, "high", start_index=center.start_index, end_index=center.end_index
        )
    if high_before is None:
        return None

    low_inside = first_swing(
        swings,
        "low",
        start_index=high_before.bar_index + 1,
        end_index=center.end_index,
    )
    if low_inside is None:
        return None

    high_inside = highest_swing(
        swings,
        start_index=low_inside.bar_index + 1,
        end_index=center.end_index,
    )
    if high_inside is None:
        return None

    try:
        return down_leg("a", high_before, low_inside), high_inside
    except ValueError:
        return None


def build_ba_bb_legs(center, swings: list[SwingPoint]) -> tuple[Leg, Leg] | None:
    high_before = latest_swing(swings, "high", before_index=center.start_index)
    if high_before is None:
        high_before = first_swing(
            swings, "high", start_index=center.start_index, end_index=center.end_index
        )
    if high_before is None:
        return None

    low_inside = first_swing(
        swings,
        "low",
        start_index=high_before.bar_index + 1,
        end_index=center.end_index,
    )
    high_inside = latest_swing(
        swings,
        "high",
        start_index=(low_inside.bar_index + 1 if low_inside else center.start_index),
        end_index=center.end_index,
    )
    low_after = first_swing(
        swings,
        "low",
        start_index=(high_inside.bar_index + 1 if high_inside else center.end_index + 1),
    )

    if not all([high_before, low_inside, high_inside, low_after]):
        return None
    try:
        return down_leg("b-a", high_before, low_inside), down_leg("b-b", high_inside, low_after)
    except ValueError:
        return None


def build_ba_bb_legs_from_b_start(
    center,
    swings: list[SwingPoint],
    b_start_high: SwingPoint,
) -> tuple[Leg, Leg] | None:
    """Build b-a and b-b according to the user's b-tail b-A definition."""
    low_before_ba = lowest_swing(
        swings,
        start_index=b_start_high.bar_index + 1,
        end_index=center.start_index - 1,
    )
    high_inside_ba = highest_swing(
        swings,
        start_index=center.start_index,
        end_index=center.end_index,
    )
    if low_before_ba is None or high_inside_ba is None:
        return None

    low_after_ba = first_swing(
        swings,
        "low",
        start_index=max(high_inside_ba.bar_index + 1, center.end_index + 1),
    )
    if low_after_ba is None:
        return None

    try:
        ba_leg = down_leg("b-a", b_start_high, low_before_ba)
        bb_leg = down_leg("b-b", high_inside_ba, low_after_ba)
    except ValueError:
        return None
    return ba_leg, bb_leg


def find_isolated_lows(center, swings: list[SwingPoint]) -> tuple[SwingPoint, SwingPoint] | None:
    first_low = lowest_swing(
        swings, start_index=max(0, center.start_index - 1), end_index=center.end_index
    )
    second_low = first_swing(swings, "low", start_index=center.end_index + 1)
    if first_low is None or second_low is None:
        return None
    return first_low, second_low


def first_swing(
    swings: list[SwingPoint],
    kind: str,
    start_index: int = 0,
    end_index: int | None = None,
) -> SwingPoint | None:
    for swing in swings:
        if swing.kind != kind or swing.bar_index < start_index:
            continue
        if end_index is not None and swing.bar_index > end_index:
            break
        return swing
    return None


def latest_swing(
    swings: list[SwingPoint],
    kind: str,
    before_index: int | None = None,
    start_index: int | None = None,
    end_index: int | None = None,
) -> SwingPoint | None:
    latest: SwingPoint | None = None
    for swing in swings:
        if swing.kind != kind:
            continue
        if before_index is not None and swing.bar_index >= before_index:
            break
        if start_index is not None and swing.bar_index < start_index:
            continue
        if end_index is not None and swing.bar_index > end_index:
            break
        latest = swing
    return latest


def lowest_swing(
    swings: list[SwingPoint],
    start_index: int,
    end_index: int,
) -> SwingPoint | None:
    lowest: SwingPoint | None = None
    for swing in swings:
        if swing.bar_index < start_index:
            continue
        if swing.bar_index > end_index:
            break
        if swing.kind != "low":
            continue
        if lowest is None or (swing.price, swing.bar_index) < (lowest.price, lowest.bar_index):
            lowest = swing
    return lowest


def highest_swing(
    swings: list[SwingPoint],
    start_index: int,
    end_index: int,
) -> SwingPoint | None:
    highest: SwingPoint | None = None
    for swing in swings:
        if swing.bar_index < start_index:
            continue
        if swing.bar_index > end_index:
            break
        if swing.kind != "high":
            continue
        if highest is None or (swing.price, -swing.bar_index) > (
            highest.price,
            -highest.bar_index,
        ):
            highest = swing
    return highest

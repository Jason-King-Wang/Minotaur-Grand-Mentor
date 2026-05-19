from __future__ import annotations

from z3b_prime.models import Bar, SwingPoint


def detect_swings(
    bars: list[Bar],
    left_bars: int = 2,
    right_bars: int = 2,
) -> list[SwingPoint]:
    raw: list[SwingPoint] = []
    if left_bars < 1 or right_bars < 1:
        raise ValueError("left_bars and right_bars must be positive")

    for index in range(left_bars, len(bars) - right_bars):
        window = bars[index - left_bars : index + right_bars + 1]
        current = bars[index]
        confirmed_time = bars[index + right_bars].close_time

        if current.high == max(bar.high for bar in window):
            raw.append(
                SwingPoint(
                    symbol=current.symbol,
                    timeframe=current.timeframe,
                    time=current.close_time,
                    confirmed_time=confirmed_time,
                    kind="high",
                    price=current.high,
                    bar_index=index,
                )
            )
        if current.low == min(bar.low for bar in window):
            raw.append(
                SwingPoint(
                    symbol=current.symbol,
                    timeframe=current.timeframe,
                    time=current.close_time,
                    confirmed_time=confirmed_time,
                    kind="low",
                    price=current.low,
                    bar_index=index,
                )
            )
    return compress_to_alternating_swings(raw)


def compress_to_alternating_swings(swings: list[SwingPoint]) -> list[SwingPoint]:
    ordered = sorted(swings, key=lambda point: (point.bar_index, point.kind))
    compressed: list[SwingPoint] = []
    for point in ordered:
        if not compressed or compressed[-1].kind != point.kind:
            compressed.append(point)
            continue

        prev = compressed[-1]
        keep_new = (
            point.kind == "high"
            and point.price > prev.price
            or point.kind == "low"
            and point.price < prev.price
        )
        if keep_new:
            compressed[-1] = point
    return compressed


def available_swings(swings: list[SwingPoint], as_of_time) -> list[SwingPoint]:
    return [point for point in swings if point.confirmed_time <= as_of_time]

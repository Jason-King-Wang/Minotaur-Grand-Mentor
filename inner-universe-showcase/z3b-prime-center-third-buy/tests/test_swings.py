from datetime import timedelta

from z3b_prime.market_structure.swings import available_swings, detect_swings


def test_swing_confirmation_delay(make_bars):
    bars = make_bars(
        [
            (10, 11, 9, 10),
            (10, 12, 9, 11),
            (11, 15, 10, 14),
            (14, 13, 8, 9),
            (9, 11, 7, 10),
        ]
    )

    swings = detect_swings(bars, left_bars=1, right_bars=1)
    high = next(point for point in swings if point.kind == "high")

    assert high.bar_index == 2
    assert high.confirmed_time == bars[3].close_time


def test_no_lookahead_swing_not_available_before_confirmed_time(make_bars):
    bars = make_bars(
        [
            (10, 11, 9, 10),
            (10, 12, 9, 11),
            (11, 15, 10, 14),
            (14, 13, 8, 9),
            (9, 11, 7, 10),
        ]
    )

    swings = detect_swings(bars, left_bars=1, right_bars=1)
    high = next(point for point in swings if point.kind == "high")

    assert high not in available_swings(swings, high.confirmed_time - timedelta(seconds=1))
    assert high in available_swings(swings, high.confirmed_time)

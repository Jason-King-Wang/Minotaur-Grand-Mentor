from z3b_prime.strategy.z3b_prime import find_user_1h_third_buy_setup


def test_user_spec_1h_gate_requires_prior_breakout_and_down_broken_center(
    make_bars,
    center,
    swing,
):
    bars = make_bars(
        [
            (98, 100, 95, 99),
            (99, 112, 98, 111),
            (111, 108, 92, 96),
            (96, 107, 91, 103),
            (103, 109, 93, 96),
            (96, 97, 88, 89),
            (89, 108, 88, 106),
            (106, 107, 94, 96),
            (96, 111, 95, 110),
            (110, 111, 100, 102),
        ],
        timeframe="1h",
    )
    center_1h = center("Z", upper=105, lower=95, start_index=2, end_index=4)
    center_1h.box_high = 110
    center_1h.box_low = 90
    swings = [
        swing("high", 100, 0),
        swing("high", 112, 1),
        swing("low", 91, 3),
        swing("low", 88, 5),
        swing("high", 108, 6),
        swing("low", 94, 7),
        swing("high", 111, 8),
        swing("low", 100, 9),
    ]

    setup = find_user_1h_third_buy_setup(bars, swings, center_1h)

    assert setup is not None
    assert setup.prior_breakout_high.price == 112
    assert setup.center_down_break_index == 5
    assert setup.previous_high.price == 108
    assert setup.breakout_high.price == 111
    assert setup.third_buy_low.price == 100


def test_user_spec_1h_gate_rejects_without_down_break(make_bars, center, swing):
    bars = make_bars(
        [
            (98, 100, 95, 99),
            (99, 112, 98, 111),
            (111, 108, 92, 96),
            (96, 107, 91, 103),
            (103, 109, 93, 96),
            (96, 97, 90, 91),
            (91, 108, 90, 106),
            (106, 107, 94, 96),
            (96, 111, 95, 110),
            (110, 111, 100, 102),
        ],
        timeframe="1h",
    )
    center_1h = center("Z", upper=105, lower=95, start_index=2, end_index=4)
    center_1h.box_high = 110
    center_1h.box_low = 90
    swings = [
        swing("high", 100, 0),
        swing("high", 112, 1),
        swing("low", 91, 3),
        swing("low", 90, 5),
        swing("high", 108, 6),
        swing("low", 94, 7),
        swing("high", 111, 8),
        swing("low", 100, 9),
    ]

    assert find_user_1h_third_buy_setup(bars, swings, center_1h) is None


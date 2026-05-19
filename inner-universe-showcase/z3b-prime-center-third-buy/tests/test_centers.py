from z3b_prime.market_structure.centers import detect_price_centers


def test_center_edges_use_leg_overlap_not_box_extremes(make_bars, swing):
    bars = make_bars(
        [
            (100, 106, 98, 104),
            (104, 112, 101, 102),
            (102, 109, 97, 108),
            (108, 111, 99, 100),
            (100, 110, 96, 107),
        ]
    )
    swings = [
        swing("low", 98, 0),
        swing("high", 112, 1),
        swing("low", 97, 2),
        swing("high", 111, 3),
    ]

    centers = detect_price_centers(bars, swings, 4, 4, 1)

    assert centers[0].upper == 111
    assert centers[0].lower == 98
    assert centers[0].box_high == 112
    assert centers[0].box_low == 97


def test_center_candidate_requires_alternating_swings(make_bars, swing):
    bars = make_bars(
        [
            (100, 106, 98, 104),
            (104, 112, 101, 102),
            (102, 109, 97, 108),
            (108, 111, 99, 100),
            (100, 110, 96, 107),
        ]
    )
    swings = [
        swing("low", 98, 0),
        swing("low", 97, 1),
        swing("high", 112, 2),
        swing("low", 96, 3),
    ]

    assert detect_price_centers(bars, swings, 4, 4, 1) == []


def test_simplified_center_extends_when_new_leg_touches_core(make_bars, swing):
    bars = make_bars(
        [
            (100, 106, 99, 101),
            (101, 110, 102, 109),
            (109, 108, 104, 105),
            (105, 112, 106, 111),
            (111, 116, 108, 110),
        ]
    )
    swings = [
        swing("low", 100, 0),
        swing("high", 110, 1),
        swing("low", 104, 2),
        swing("high", 112, 3),
        swing("low", 108, 4),
    ]

    centers = detect_price_centers(bars, swings, 4, 4, 0)

    assert len(centers) == 1
    assert centers[0].state == "active"
    assert centers[0].upper == 110
    assert centers[0].lower == 104
    assert centers[0].end_index == 4
    assert centers[0].box_high == 116
    assert centers[0].member_leg_count == 4
    assert centers[0].extension_count == 1


def test_simplified_center_completes_when_new_leg_breaks_up(make_bars, swing):
    bars = make_bars(
        [
            (100, 106, 99, 101),
            (101, 110, 102, 109),
            (109, 108, 104, 105),
            (105, 112, 106, 111),
            (111, 118, 111, 117),
        ]
    )
    swings = [
        swing("low", 100, 0),
        swing("high", 110, 1),
        swing("low", 104, 2),
        swing("high", 112, 3),
        swing("low", 111, 4),
    ]

    centers = detect_price_centers(bars, swings, 4, 4, 0)

    assert len(centers) == 1
    assert centers[0].state == "completed"
    assert centers[0].break_dir == "up"
    assert centers[0].upper == 110
    assert centers[0].lower == 104
    assert centers[0].end_index == 3
    assert centers[0].completed_time == swings[-1].confirmed_time


def test_simplified_center_completes_when_new_leg_breaks_down(make_bars, swing):
    bars = make_bars(
        [
            (110, 112, 108, 111),
            (111, 109, 105, 106),
            (106, 110, 106, 109),
            (109, 108, 100, 101),
            (101, 103, 99, 102),
        ]
    )
    swings = [
        swing("high", 112, 0),
        swing("low", 105, 1),
        swing("high", 110, 2),
        swing("low", 100, 3),
        swing("high", 103, 4),
    ]

    centers = detect_price_centers(bars, swings, 4, 4, 0)

    assert len(centers) == 1
    assert centers[0].state == "completed"
    assert centers[0].break_dir == "down"
    assert centers[0].end_index == 3

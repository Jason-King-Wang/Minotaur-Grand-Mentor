from z3b_prime.chanlun_core import CenterEngine, Direction, TrendUnit
from z3b_prime.chanlun_core.persistence import center_event_to_dict


def make_unit(seq: int, low: float, high: float) -> TrendUnit:
    start_ts = seq * 1000
    end_ts = start_ts + 900
    return TrendUnit(
        symbol="2330",
        level="15m",
        seq=seq,
        start_ts=start_ts,
        end_ts=end_ts,
        direction=Direction.UP,
        low=low,
        high=high,
        confirmed_at=end_ts + 60,
    )


def test_center_event_to_dict_uses_plain_enum_values():
    engine = CenterEngine("2330", "1h", "15m", min_units=3)
    engine.on_child_unit(make_unit(1, 96, 104))
    engine.on_child_unit(make_unit(2, 98, 105))
    event = engine.on_child_unit(make_unit(3, 97, 102))[0]

    row = center_event_to_dict(event)

    assert row["event_type"] == "center_started"
    assert row["center"]["state"] == "active"
    assert row["center"]["units"][0]["direction"] == "up"

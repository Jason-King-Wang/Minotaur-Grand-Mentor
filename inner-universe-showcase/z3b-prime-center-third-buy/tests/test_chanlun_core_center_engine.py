import pytest

from z3b_prime.chanlun_core import (
    CenterEngine,
    CenterEventType,
    Direction,
    TrendUnit,
    UpdateMode,
)


def make_unit(
    seq: int,
    low: float,
    high: float,
    level: str = "15m",
    symbol: str = "2330",
    direction: Direction = Direction.UP,
) -> TrendUnit:
    start_ts = seq * 1000
    end_ts = start_ts + 900
    confirmed_at = end_ts + 60
    return TrendUnit(
        symbol=symbol,
        level=level,
        seq=seq,
        start_ts=start_ts,
        end_ts=end_ts,
        direction=direction,
        low=low,
        high=high,
        confirmed_at=confirmed_at,
    )


def test_three_overlapping_units_start_center():
    engine = CenterEngine("2330", "1h", "15m", min_units=3)

    assert engine.on_child_unit(make_unit(1, 96, 104)) == []
    assert engine.on_child_unit(make_unit(2, 98, 105)) == []
    events = engine.on_child_unit(make_unit(3, 97, 102))

    assert len(events) == 1
    assert events[0].event_type == CenterEventType.STARTED
    assert events[0].center.zd == 98
    assert events[0].center.zg == 102
    assert events[0].center.confirmed_at == make_unit(3, 97, 102).confirmed_at
    assert [unit.seq for unit in events[0].center.units] == [1, 2, 3]


def test_active_center_extends_in_fixed_mode():
    engine = CenterEngine("2330", "1h", "15m", min_units=3, update_mode=UpdateMode.FIXED)
    for unit in [make_unit(1, 96, 104), make_unit(2, 98, 105), make_unit(3, 97, 102)]:
        engine.on_child_unit(unit)

    events = engine.on_child_unit(make_unit(4, 99, 103))

    assert len(events) == 1
    assert events[0].event_type == CenterEventType.EXTENDED
    assert events[0].center.zd == 98
    assert events[0].center.zg == 102
    assert [unit.seq for unit in events[0].center.units] == [1, 2, 3, 4]


def test_active_center_extends_in_shrink_mode():
    engine = CenterEngine("2330", "1h", "15m", min_units=3, update_mode=UpdateMode.SHRINK)
    for unit in [make_unit(1, 96, 104), make_unit(2, 98, 105), make_unit(3, 97, 102)]:
        engine.on_child_unit(unit)

    events = engine.on_child_unit(make_unit(4, 99, 103))

    assert events[0].center.zd == 99
    assert events[0].center.zg == 102


def test_active_center_completes_up():
    engine = CenterEngine("2330", "1h", "15m", min_units=3)
    for unit in [make_unit(1, 96, 104), make_unit(2, 98, 105), make_unit(3, 97, 102)]:
        engine.on_child_unit(unit)

    events = engine.on_child_unit(make_unit(4, 103, 110))

    assert len(events) == 1
    assert events[0].event_type == CenterEventType.COMPLETED
    assert events[0].center.break_dir == Direction.UP
    assert engine.active is None
    assert len(engine.completed) == 1


def test_active_center_completes_down():
    engine = CenterEngine("2330", "1h", "15m", min_units=3)
    for unit in [make_unit(1, 96, 104), make_unit(2, 98, 105), make_unit(3, 97, 102)]:
        engine.on_child_unit(unit)

    events = engine.on_child_unit(make_unit(4, 90, 97))

    assert events[0].event_type == CenterEventType.COMPLETED
    assert events[0].center.break_dir == Direction.DOWN
    assert engine.active is None


def test_wrong_child_level_rejected():
    engine = CenterEngine("2330", "1h", "15m")

    with pytest.raises(ValueError, match="Expected child_level"):
        engine.on_child_unit(make_unit(1, 96, 104, level="5m"))


def test_duplicate_seq_rejected():
    engine = CenterEngine("2330", "1h", "15m")
    engine.on_child_unit(make_unit(1, 96, 104))

    with pytest.raises(ValueError, match="Duplicated unit seq"):
        engine.on_child_unit(make_unit(1, 97, 105))


def test_reverse_seq_rejected():
    engine = CenterEngine("2330", "1h", "15m")
    engine.on_child_unit(make_unit(2, 96, 104))

    with pytest.raises(ValueError, match="strictly increasing"):
        engine.on_child_unit(make_unit(1, 97, 105))


def test_confirmed_at_cannot_be_before_end_ts():
    with pytest.raises(ValueError, match="avoid look-ahead"):
        TrendUnit(
            symbol="2330",
            level="15m",
            seq=1,
            start_ts=1000,
            end_ts=1900,
            direction=Direction.UP,
            low=96,
            high=104,
            confirmed_at=1800,
        )


def test_event_snapshot_does_not_share_unit_list_with_active_center():
    engine = CenterEngine("2330", "1h", "15m", min_units=3)
    engine.on_child_unit(make_unit(1, 96, 104))
    engine.on_child_unit(make_unit(2, 98, 105))
    started = engine.on_child_unit(make_unit(3, 97, 102))[0]
    extended = engine.on_child_unit(make_unit(4, 99, 103))[0]

    assert [unit.seq for unit in started.center.units] == [1, 2, 3]
    assert [unit.seq for unit in extended.center.units] == [1, 2, 3, 4]

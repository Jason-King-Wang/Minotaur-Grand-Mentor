from z3b_prime.chanlun_core import CenterEngine, CenterEventType, Direction, MultiLevelCenterRouter, TrendUnit


def make_unit(seq: int, low: float, high: float, level: str) -> TrendUnit:
    start_ts = seq * 1000
    end_ts = start_ts + 900
    return TrendUnit(
        symbol="2330",
        level=level,
        seq=seq,
        start_ts=start_ts,
        end_ts=end_ts,
        direction=Direction.UP,
        low=low,
        high=high,
        confirmed_at=end_ts + 60,
    )


def test_router_sends_5m_units_only_to_15m_engine():
    engine_15m = CenterEngine("2330", "15m", "5m", min_units=3)
    engine_1h = CenterEngine("2330", "1h", "15m", min_units=3)
    router = MultiLevelCenterRouter([engine_15m, engine_1h])

    router.on_trend_unit_confirmed(make_unit(1, 96, 104, "5m"))
    router.on_trend_unit_confirmed(make_unit(2, 98, 105, "5m"))
    events = router.on_trend_unit_confirmed(make_unit(3, 97, 102, "5m"))

    assert len(events) == 1
    assert events[0].event_type == CenterEventType.STARTED
    assert events[0].center.level == "15m"
    assert engine_15m.active is not None
    assert engine_1h.active is None
    assert engine_1h.units == []


def test_router_sends_15m_units_to_1h_engine():
    engine_15m = CenterEngine("2330", "15m", "5m", min_units=3)
    engine_1h = CenterEngine("2330", "1h", "15m", min_units=3)
    router = MultiLevelCenterRouter([engine_15m, engine_1h])

    router.on_trend_unit_confirmed(make_unit(1, 96, 104, "15m"))
    router.on_trend_unit_confirmed(make_unit(2, 98, 105, "15m"))
    events = router.on_trend_unit_confirmed(make_unit(3, 97, 102, "15m"))

    assert len(events) == 1
    assert events[0].center.level == "1h"
    assert engine_15m.units == []
    assert engine_1h.active is not None

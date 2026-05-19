from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from z3b_prime.models import Bar, Center, SwingPoint


@pytest.fixture
def make_bars():
    def _make_bars(values, symbol="TEST", timeframe="15m"):
        base = datetime(2026, 1, 1, 9, 0)
        bars = []
        for idx, (open_, high, low, close) in enumerate(values):
            time = base + timedelta(minutes=15 * idx)
            bars.append(
                Bar(
                    symbol=symbol,
                    timeframe=timeframe,
                    time=time,
                    close_time=time + timedelta(minutes=15),
                    open=open_,
                    high=high,
                    low=low,
                    close=close,
                )
            )
        return bars

    return _make_bars


@pytest.fixture
def center():
    def _center(id_="C", upper=110, lower=100, start_index=0, end_index=4):
        start = datetime(2026, 1, 1, 9, 0)
        return Center(
            id=id_,
            symbol="TEST",
            timeframe="15m",
            start_time=start,
            end_time=start + timedelta(minutes=15 * end_index),
            upper=upper,
            lower=lower,
            mid=(upper + lower) / 2,
            range=upper - lower,
            duration_bars=end_index - start_index + 1,
            score=(upper - lower) * (end_index - start_index + 1),
            start_index=start_index,
            end_index=end_index,
        )

    return _center


@pytest.fixture
def swing():
    def _swing(kind, price, index):
        base = datetime(2026, 1, 1, 9, 0)
        time = base + timedelta(minutes=15 * index)
        return SwingPoint(
            symbol="TEST",
            timeframe="15m",
            time=time,
            confirmed_time=time + timedelta(minutes=30),
            kind=kind,
            price=price,
            bar_index=index,
        )

    return _swing


@pytest.fixture
def synthetic_z3b_bars():
    base = datetime(2026, 1, 1, 9, 0)

    def _bar(timeframe, idx, open_, high, low, close, minutes):
        time = base + timedelta(minutes=minutes * idx)
        return Bar(
            symbol="TEST",
            timeframe=timeframe,
            time=time,
            close_time=time + timedelta(minutes=minutes),
            open=open_,
            high=high,
            low=low,
            close=close,
        )

    bars_1h = [
        _bar("1h", 0, 105, 108, 100, 104, 60),
        _bar("1h", 1, 104, 112, 102, 110, 60),
        _bar("1h", 2, 110, 109, 99, 101, 60),
        _bar("1h", 3, 101, 113, 103, 111, 60),
        _bar("1h", 4, 111, 108, 100, 102, 60),
        _bar("1h", 5, 102, 110, 101, 107, 60),
        _bar("1h", 6, 107, 118, 106, 116, 60),
        _bar("1h", 7, 116, 130, 115, 128, 60),
        _bar("1h", 8, 128, 129, 114, 116, 60),
    ]

    start = base + timedelta(hours=6)
    values_15m = [
        (116, 120, 115, 116),
        (116, 130, 122, 129),
        (129, 126, 120, 121),
        (121, 128, 121, 127),
        (127, 123, 112, 113),
        (113, 120, 113, 119),
        (119, 118, 110, 111),
        (111, 116, 111, 115),
        (115, 114, 113, 113.5),
        (113.5, 117, 113, 116),
        (116, 115, 112.5, 113),
        (113, 122, 114, 121),
        (121, 124, 120, 123),
        (123, 132, 122, 131),
    ]
    bars_15m = []
    for idx, (open_, high, low, close) in enumerate(values_15m):
        time = start + timedelta(minutes=15 * idx)
        bars_15m.append(
            Bar(
                symbol="TEST",
                timeframe="15m",
                time=time,
                close_time=time + timedelta(minutes=15),
                open=open_,
                high=high,
                low=low,
                close=close,
            )
        )
    return bars_1h, bars_15m

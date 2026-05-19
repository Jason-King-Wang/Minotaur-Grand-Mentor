from __future__ import annotations

import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from z3b_prime.models import Bar


TIME_COLUMNS = ("datetime", "date", "time", "timestamp")


def load_ohlcv_csv(
    path: str | Path,
    *,
    symbol: str | None = None,
    timeframe: str = "15m",
) -> list[Bar]:
    rows = list(_read_rows(path))
    bars: list[Bar] = []
    for row in rows:
        normalized = {key.strip().lower(): value for key, value in row.items()}
        time_key = next((key for key in TIME_COLUMNS if key in normalized), None)
        if time_key is None:
            raise ValueError(f"CSV must include one of: {', '.join(TIME_COLUMNS)}")

        bar_symbol = symbol or normalized.get("symbol") or "UNKNOWN"
        bar_time = parse_datetime(normalized[time_key])
        close_time = (
            parse_datetime(normalized["close_time"])
            if normalized.get("close_time")
            else bar_time + timeframe_delta(timeframe)
        )
        bars.append(
            Bar(
                symbol=bar_symbol,
                timeframe=timeframe,
                time=bar_time,
                close_time=close_time,
                open=float(normalized["open"]),
                high=float(normalized["high"]),
                low=float(normalized["low"]),
                close=float(normalized["close"]),
                volume=float(normalized.get("volume") or 0),
            )
        )
    return sorted(bars, key=lambda bar: bar.time)


def parse_datetime(value: str) -> datetime:
    value = value.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    return datetime.fromisoformat(value)


def timeframe_delta(timeframe: str) -> timedelta:
    value = timeframe.strip().lower()
    if value.endswith("m"):
        return timedelta(minutes=int(value[:-1]))
    if value.endswith("h"):
        return timedelta(hours=int(value[:-1]))
    if value.endswith("d"):
        return timedelta(days=int(value[:-1]))
    return timedelta(0)


def _read_rows(path: str | Path) -> Iterable[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)

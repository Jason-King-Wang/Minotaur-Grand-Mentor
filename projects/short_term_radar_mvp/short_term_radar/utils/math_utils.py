from __future__ import annotations

from math import isnan, sqrt
from typing import Iterable


def safe_float(value, default: float | None = None) -> float | None:
    if value is None:
        return default
    text = str(value).replace(",", "").strip()
    if text == "":
        return default
    try:
        parsed = float(text)
        return default if isnan(parsed) else parsed
    except ValueError:
        return default


def clip(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def mean(values: Iterable[float]) -> float | None:
    items = [v for v in values if v is not None]
    if not items:
        return None
    return sum(items) / len(items)


def stddev(values: Iterable[float]) -> float | None:
    items = [v for v in values if v is not None]
    if len(items) < 2:
        return None
    avg = sum(items) / len(items)
    return sqrt(sum((v - avg) ** 2 for v in items) / (len(items) - 1))


def pct_change(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    return current / previous - 1.0


def z_score(value: float | None, values: list[float]) -> float | None:
    if value is None:
        return None
    avg = mean(values)
    sd = stddev(values)
    if avg is None or not sd:
        return 0.0
    return (value - avg) / sd

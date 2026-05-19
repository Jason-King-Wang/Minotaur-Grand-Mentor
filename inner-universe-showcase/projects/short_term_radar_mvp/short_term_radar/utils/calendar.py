from __future__ import annotations

from datetime import date


def parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def monthly_rebalance_dates(trade_dates: list[str], start: str, end: str) -> list[str]:
    start_date = parse_date(start)
    end_date = parse_date(end)
    result: list[str] = []
    seen_months: set[tuple[int, int]] = set()

    for trade_date in sorted({d for d in trade_dates if d}):
        current = parse_date(trade_date)
        if current < start_date or current > end_date:
            continue
        key = (current.year, current.month)
        if key not in seen_months:
            seen_months.add(key)
            result.append(trade_date)
    return result

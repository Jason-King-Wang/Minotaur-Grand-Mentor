from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from z3b_prime.models import Bar


def resample_to_1h(bars: list[Bar]) -> list[Bar]:
    grouped: dict[datetime, list[Bar]] = defaultdict(list)
    for bar in bars:
        grouped[floor_hour(bar.time)].append(bar)

    output: list[Bar] = []
    for bucket in sorted(grouped):
        rows = sorted(grouped[bucket], key=lambda item: item.time)
        first = rows[0]
        last = rows[-1]
        output.append(
            Bar(
                symbol=first.symbol,
                timeframe="1h",
                time=bucket,
                close_time=bucket + timedelta(hours=1),
                open=first.open,
                high=max(row.high for row in rows),
                low=min(row.low for row in rows),
                close=last.close,
                volume=sum(row.volume for row in rows),
            )
        )
    return output


def floor_hour(value: datetime) -> datetime:
    return value.replace(minute=0, second=0, microsecond=0)

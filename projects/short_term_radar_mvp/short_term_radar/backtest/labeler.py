from __future__ import annotations

from typing import Any

from short_term_radar.schemas import ForwardLabel


def forward_label(
    rows: list[dict[str, Any]], trade_date: str, horizon_days: int = 126
) -> ForwardLabel:
    anchor_index = None
    for index, row in enumerate(rows):
        if row["trade_date"] == trade_date:
            anchor_index = index
            break

    if anchor_index is None or rows[anchor_index].get("close") in (None, 0):
        symbol = rows[0]["symbol"] if rows else ""
        return ForwardLabel(symbol, trade_date, None, None, None, False, False)

    anchor = rows[anchor_index]
    future = rows[anchor_index + 1 : anchor_index + 1 + horizon_days]
    if not future:
        return ForwardLabel(anchor["symbol"], trade_date, None, None, None, False, False)

    start_close = anchor["close"]
    closes = [row["close"] for row in future if row.get("close") is not None]
    if not closes:
        return ForwardLabel(anchor["symbol"], trade_date, None, None, None, False, False)

    max_close = max(closes)
    end_close = closes[-1]
    min_return = min(close / start_close - 1 for close in closes)
    return ForwardLabel(
        symbol=anchor["symbol"],
        trade_date=trade_date,
        forward_max_return=max_close / start_close - 1,
        forward_close_return=end_close / start_close - 1,
        forward_max_drawdown=min_return,
        hit_3x=max_close >= start_close * 3,
        hit_5x=max_close >= start_close * 5,
    )

from __future__ import annotations

from typing import Any

from short_term_radar.schemas import ForwardLabel


def _empty_label(symbol: str, trade_date: str) -> ForwardLabel:
    return ForwardLabel(
        symbol=symbol,
        trade_date=trade_date,
        forward_max_return=None,
        forward_close_return=None,
        forward_min_return_from_entry=None,
        forward_path_max_drawdown=None,
        hit_3x=False,
        hit_5x=False,
    )


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
        return _empty_label(symbol, trade_date)

    anchor = rows[anchor_index]
    future = rows[anchor_index + 1 : anchor_index + 1 + horizon_days]
    if not future:
        return _empty_label(anchor["symbol"], trade_date)

    start_close = anchor["close"]
    closes = [row["close"] for row in future if row.get("close") is not None]
    if not closes:
        return _empty_label(anchor["symbol"], trade_date)

    max_close = max(closes)
    end_close = closes[-1]
    min_return_from_entry = min(close / start_close - 1 for close in closes)
    running_peak = start_close
    path_max_drawdown = 0.0
    for close in closes:
        running_peak = max(running_peak, close)
        path_max_drawdown = min(path_max_drawdown, close / running_peak - 1)

    return ForwardLabel(
        symbol=anchor["symbol"],
        trade_date=trade_date,
        forward_max_return=max_close / start_close - 1,
        forward_close_return=end_close / start_close - 1,
        forward_min_return_from_entry=min_return_from_entry,
        forward_path_max_drawdown=path_max_drawdown,
        hit_3x=max_close >= start_close * 3,
        hit_5x=max_close >= start_close * 5,
    )

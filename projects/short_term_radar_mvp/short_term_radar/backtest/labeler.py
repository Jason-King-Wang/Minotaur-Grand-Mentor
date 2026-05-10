from __future__ import annotations

from typing import Any

from short_term_radar.schemas import ForwardLabel


def _empty_label(symbol: str, trade_date: str) -> ForwardLabel:
    return ForwardLabel(symbol, trade_date, None, None, None, None, False, False, False)


def _time_to_multiple(closes: list[float], start_close: float, multiple: float) -> int | None:
    target = start_close * multiple
    for index, close in enumerate(closes, 1):
        if close >= target:
            return index
    return None


def _path_max_drawdown(closes: list[float], start_close: float) -> float:
    peak = start_close
    max_drawdown = 0.0
    for close in closes:
        peak = max(peak, close)
        drawdown = close / peak - 1.0
        max_drawdown = min(max_drawdown, drawdown)
    return max_drawdown


def forward_label(
    rows: list[dict[str, Any]], trade_date: str, horizon_days: int = 126
) -> ForwardLabel:
    anchor_index = None
    for index, row in enumerate(rows):
        if row["trade_date"] == trade_date:
            anchor_index = index
            break

    symbol = rows[0]["symbol"] if rows else ""
    if anchor_index is None or rows[anchor_index].get("close") in (None, 0):
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
    return ForwardLabel(
        symbol=anchor["symbol"],
        trade_date=trade_date,
        forward_max_return=max_close / start_close - 1,
        forward_close_return=end_close / start_close - 1,
        forward_min_return_from_entry=min(close / start_close - 1 for close in closes),
        forward_path_max_drawdown=_path_max_drawdown(closes, start_close),
        hit_2x=max_close >= start_close * 2,
        hit_3x=max_close >= start_close * 3,
        hit_5x=max_close >= start_close * 5,
        time_to_2x_days=_time_to_multiple(closes, start_close, 2),
        time_to_3x_days=_time_to_multiple(closes, start_close, 3),
        time_to_5x_days=_time_to_multiple(closes, start_close, 5),
    )
